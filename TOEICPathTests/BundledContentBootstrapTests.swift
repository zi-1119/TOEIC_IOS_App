import CryptoKit
import XCTest
@testable import TOEICPath

final class BundledContentBootstrapTests: XCTestCase {
    func testEmptyStoreInstallsSevenSeedBatchesIdempotentlyWithOfflineMedia() async throws {
        let root = temporaryDirectory(name: "empty-seed")
        let contentRoot = root.appending(path: "Content", directoryHint: .isDirectory)
        let bootstrapper = BundledContentBootstrapper(rootURL: contentRoot)

        let first = try await bootstrapper.install(rootURL: seedRoot)
        XCTAssertEqual(first.package.groups.count, 51)
        XCTAssertEqual(first.package.groups.flatMap(\.items).count, 100)
        XCTAssertEqual(first.package.assets.count, 30)
        XCTAssertTrue(first.package.groups.allSatisfy {
            $0.purpose == .training && $0.contentStatus == .aiChecked && !$0.fixture
        })
        for asset in first.package.assets {
            let url = URL(fileURLWithPath: asset.path)
            XCTAssertTrue(url.path.hasPrefix(contentRoot.path))
            XCTAssertTrue(FileManager.default.fileExists(atPath: url.path))
            XCTAssertEqual(sha256(try Data(contentsOf: url)), asset.checksumSHA256)
        }

        let store = ContentVersionStore(rootURL: contentRoot)
        XCTAssertEqual(try store.activeBatchIDs(), BundledSeedContent.batchDirectoryNames)
        let stateBefore = try Data(contentsOf: contentRoot.appending(path: "state.json"))
        let second = try await bootstrapper.install(rootURL: seedRoot)
        XCTAssertEqual(second.package.groups.flatMap(\.items).count, 100)
        XCTAssertEqual(try Data(contentsOf: contentRoot.appending(path: "state.json")), stateBefore)
        XCTAssertEqual(try ContentVersionStore(rootURL: contentRoot).activePackage()?.groups.flatMap(\.items).count, 100)
    }

    @MainActor
    func testInstalledEmptyAppBootstrapPreservesProfileAndSurvivesRestart() async throws {
        let root = temporaryDirectory(name: "profile-upgrade")
        let profileURL = root.appending(path: "profile.json")
        let profileStore = LocalProfileStore(fileURL: profileURL)
        var expectedProfile = LocalProfile()
        expectedProfile.preferences.hasCompletedOnboarding = true
        expectedProfile.preferences.target = "保留我的目標"
        expectedProfile.dueItemIDs = ["existing-due-item"]
        try profileStore.save(expectedProfile)

        let contentStore = ContentVersionStore(rootURL: root.appending(path: "Content"))
        let model = AppModel(
            store: profileStore,
            contentStore: contentStore,
            bundledSeedRootURL: seedRoot,
            backend: LocalBackendClient(hub: LocalBackendHub(storeURL: root.appending(path: "backend.json")))
        )
        XCTAssertEqual(model.contentBootstrapState, .idle)
        await model.bootstrapBundledContent()
        XCTAssertEqual(model.contentBootstrapState, .ready(itemCount: 100))
        XCTAssertEqual(model.profile, expectedProfile)
        XCTAssertEqual(model.package.groups.flatMap(\.items).count, 100)

        let reopened = AppModel(
            store: profileStore,
            contentStore: ContentVersionStore(rootURL: root.appending(path: "Content")),
            bundledSeedRootURL: seedRoot,
            backend: LocalBackendClient(hub: LocalBackendHub(storeURL: root.appending(path: "backend.json")))
        )
        XCTAssertEqual(reopened.profile, expectedProfile)
        XCTAssertEqual(reopened.package.groups.flatMap(\.items).count, 100)
        XCTAssertEqual(reopened.contentBootstrapState, .ready(itemCount: 100))
    }

    func testAtomicSeedFailureLeavesExistingCatalogUntouched() throws {
        let root = temporaryDirectory(name: "rollback")
        let store = ContentVersionStore(rootURL: root.appending(path: "Content"))
        _ = try store.install(from: seedRoot.appending(path: "batch-ag-0001"))
        let stateURL = store.storageRootURL.appending(path: "state.json")
        let stateBefore = try Data(contentsOf: stateURL)
        let packageBefore = try XCTUnwrap(store.activePackage())

        let broken = root.appending(path: "batch-ag-0007", directoryHint: .isDirectory)
        try FileManager.default.copyItem(at: seedRoot.appending(path: "batch-ag-0007"), to: broken)
        let groupsURL = broken.appending(path: "groups.jsonl")
        var corrupt = try Data(contentsOf: groupsURL)
        corrupt.append(0x20)
        try corrupt.write(to: groupsURL)
        let sources = (1...6).map { seedRoot.appending(path: String(format: "batch-ag-%04d", $0)) } + [broken]

        XCTAssertThrowsError(try store.installAtomically(from: sources))
        XCTAssertEqual(try Data(contentsOf: stateURL), stateBefore)
        XCTAssertEqual(try store.activePackage(), packageBefore)
        XCTAssertEqual(try store.activeBatchIDs(), ["batch-ag-0001"])
    }

    func testSeedBootstrapDoesNotDowngradeNewerInstalledGroupVersions() async throws {
        let root = temporaryDirectory(name: "no-downgrade")
        let contentRoot = root.appending(path: "Content")
        let bootstrapper = BundledContentBootstrapper(rootURL: contentRoot)
        _ = try await bootstrapper.install(rootURL: seedRoot)

        let future = root.appending(path: "future-batch", directoryHint: .isDirectory)
        try FileManager.default.copyItem(at: seedRoot.appending(path: "batch-ag-0007"), to: future)
        try rewriteJSONL(future.appending(path: "groups.jsonl")) { $0["version"] = 3 }
        try rewriteJSONL(future.appending(path: "reviews.jsonl")) { $0["group_version"] = 3 }
        try mutateJSONObject(future.appending(path: "reports/validation.json")) { $0["batch_id"] = "test-future-listening-v3" }
        try mutateJSONObject(future.appending(path: "manifest.json")) { manifest in
            manifest["batch_id"] = "test-future-listening-v3"
            var files = manifest["files"] as! [[String: Any]]
            for index in files.indices {
                let path = files[index]["path"] as! String
                files[index]["sha256"] = try! sha256(Data(contentsOf: future.appending(path: path)))
            }
            manifest["files"] = files
        }

        let futureBatch = try ContentBatchImporter.loadAndValidate(directory: future)
        let upgradedGroupID = try XCTUnwrap(futureBatch.groups.first?.groupID)
        let store = ContentVersionStore(rootURL: contentRoot)
        _ = try store.install(from: future)
        XCTAssertEqual(try store.activePackage()?.groups.first { $0.id == upgradedGroupID }?.version, 3)

        let afterSeedRetry = try await bootstrapper.install(rootURL: seedRoot)
        let upgraded = try XCTUnwrap(afterSeedRetry.package.groups.first { $0.id == upgradedGroupID })
        XCTAssertEqual(upgraded.version, 3)
        XCTAssertEqual(upgraded.sourceBatchID, "test-future-listening-v3")
        XCTAssertEqual(afterSeedRetry.package.groups.flatMap(\.items).count, 100)
    }

    @MainActor
    func testRealSeedBuildsDefaultTenItemReadingQuickTest() async throws {
        let root = temporaryDirectory(name: "real-seed-quick-test")
        let contentRoot = root.appending(path: "Content")
        _ = try await BundledContentBootstrapper(rootURL: contentRoot).install(rootURL: seedRoot)
        let model = AppModel(
            store: LocalProfileStore(fileURL: root.appending(path: "profile.json")),
            contentStore: ContentVersionStore(rootURL: contentRoot),
            bundledSeedRootURL: seedRoot,
            backend: LocalBackendClient(hub: LocalBackendHub(storeURL: root.appending(path: "backend.json")))
        )

        let assembly = model.quickTestAssembly()
        XCTAssertEqual(model.profile.preferences.quickTestFocus, .reading)
        XCTAssertEqual(assembly.actualItemCount, 10)
        XCTAssertTrue(assembly.isExactTarget)
        XCTAssertEqual(Set(assembly.groups.map(\.familyID)).count, assembly.groups.count)
        XCTAssertTrue(assembly.groups.allSatisfy {
            $0.part.section == .reading
                && $0.purpose == .training
                && $0.contentStatus?.isApprovedForFormalUse == true
                && !$0.fixture
                && model.materialAvailability(for: $0) == .complete
        })
    }

    @MainActor
    func testRealSeedBuildsMaterialCompleteListeningAndMixedQuickTests() async throws {
        let root = temporaryDirectory(name: "real-seed-quick-test-focuses")
        let contentRoot = root.appending(path: "Content")
        _ = try await BundledContentBootstrapper(rootURL: contentRoot).install(rootURL: seedRoot)
        let model = AppModel(
            store: LocalProfileStore(fileURL: root.appending(path: "profile.json")),
            contentStore: ContentVersionStore(rootURL: contentRoot),
            bundledSeedRootURL: seedRoot,
            backend: LocalBackendClient(hub: LocalBackendHub(storeURL: root.appending(path: "backend.json")))
        )

        for focus in [QuickTestFocus.listening, .mixed] {
            let assembly = model.quickTestAssembly(focus: focus, level: .foundation)
            XCTAssertEqual(assembly.actualItemCount, 10, "\(focus.rawValue) should assemble the advertised item count")
            XCTAssertEqual(Set(assembly.groups.map(\.familyID)).count, assembly.groups.count)
            XCTAssertTrue(assembly.groups.allSatisfy {
                $0.purpose == .training
                    && $0.contentStatus?.isApprovedForFormalUse == true
                    && !$0.fixture
                    && model.materialAvailability(for: $0) == .complete
            })
            if focus == .listening {
                XCTAssertTrue(assembly.groups.allSatisfy { $0.part.section == .listening })
            } else {
                XCTAssertEqual(Set(assembly.groups.map { $0.part.section }), [.listening, .reading])
            }
        }
    }

    private var seedRoot: URL {
        if let override = ProcessInfo.processInfo.environment["TOEICPATH_SEED_ROOT"], !override.isEmpty {
            return URL(fileURLWithPath: override, isDirectory: true)
        }
        return URL(fileURLWithPath: #filePath).deletingLastPathComponent().deletingLastPathComponent()
            .appending(path: "SeedContent", directoryHint: .isDirectory)
    }

    private func temporaryDirectory(name: String) -> URL {
        let url = FileManager.default.temporaryDirectory
            .appending(path: "TOEICPathSeedTests-\(name)-\(UUID().uuidString)", directoryHint: .isDirectory)
        try! FileManager.default.createDirectory(at: url, withIntermediateDirectories: true)
        addTeardownBlock { try? FileManager.default.removeItem(at: url) }
        return url
    }

    private func rewriteJSONL(_ url: URL, mutation: (inout [String: Any]) -> Void) throws {
        let lines = try String(contentsOf: url, encoding: .utf8).split(whereSeparator: \.isNewline)
        let rewritten = try lines.map { line -> String in
            var object = try JSONSerialization.jsonObject(with: Data(line.utf8)) as! [String: Any]
            mutation(&object)
            let data = try JSONSerialization.data(withJSONObject: object, options: [.sortedKeys])
            return String(decoding: data, as: UTF8.self)
        }.joined(separator: "\n") + "\n"
        try Data(rewritten.utf8).write(to: url)
    }

    private func mutateJSONObject(_ url: URL, mutation: (inout [String: Any]) -> Void) throws {
        var object = try JSONSerialization.jsonObject(with: Data(contentsOf: url)) as! [String: Any]
        mutation(&object)
        try JSONSerialization.data(withJSONObject: object, options: [.prettyPrinted, .sortedKeys])
            .write(to: url)
    }

    private func sha256(_ data: Data) -> String {
        SHA256.hash(data: data).map { String(format: "%02x", $0) }.joined()
    }
}
