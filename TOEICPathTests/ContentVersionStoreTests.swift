import XCTest
import CryptoKit
@testable import TOEICPath

final class ContentVersionStoreTests: XCTestCase {
    @MainActor
    func testFirstFiveUntouchedExportsAllowReadingAndKeepListeningPreviewOnly() throws {
        let root = temporaryDirectory(name: "five-batch-material-boundary")
        let contentRoot = root.appending(path: "content", directoryHint: .isDirectory)
        let store = ContentVersionStore(rootURL: contentRoot)
        let exports = repositoryRoot.appending(path: "exports")
        for number in 1...5 {
            _ = try store.install(from: exports.appending(path: String(format: "batch-ag-%04d", number)))
        }

        let model = AppModel(
            store: LocalProfileStore(fileURL: root.appending(path: "profile.json")),
            contentStore: store,
            backend: LocalBackendClient(hub: LocalBackendHub(storeURL: root.appending(path: "backend.json")))
        )
        let reading = ContentEligibility.formalGroups(in: model.package.groups, for: .training)
            .filter { $0.part.section == .reading }
        let listening = model.package.groups
            .filter { $0.part.section == .listening && ContentEligibility.hasApprovedMetadata($0, for: .training) }

        XCTAssertEqual(reading.flatMap(\.items).count, 51)
        XCTAssertEqual(listening.flatMap(\.items).count, 49)
        XCTAssertTrue(listening.allSatisfy { !ContentEligibility.isFormallyEligible($0, for: .training) })
        XCTAssertTrue(reading.allSatisfy { model.materialAvailability(for: $0) == .complete })
        XCTAssertTrue(listening.allSatisfy {
            if case .previewOnly = model.materialAvailability(for: $0) { return true }
            return false
        })

        for group in reading {
            XCTAssertNoThrow(try model.beginSession(groups: [group], mode: .practice))
            model.abortActiveSession()
        }
        for group in listening {
            XCTAssertThrowsError(try model.beginSession(groups: [group], mode: .practice))
        }
    }

    func testSevenUntouchedExportsResolveExactCatalogPersistReimportAndRollback() throws {
        let root = temporaryDirectory(name: "store")
        let store = ContentVersionStore(rootURL: root)
        let exports = repositoryRoot.appending(path: "exports")
        var installed: InstalledContentBatch?
        for number in 1...7 {
            installed = try store.install(from: exports.appending(path: String(format: "batch-ag-%04d", number)))
        }

        let package = try XCTUnwrap(installed?.package)
        XCTAssertEqual(installed?.activeBatchIDs.count, 7)
        XCTAssertEqual(package.groups.count, 51)
        XCTAssertEqual(package.groups.flatMap(\.items).count, 100)
        XCTAssertEqual(Set(package.groups.flatMap { $0.items.map(\.id) }).count, 100)
        let expectedItemsByPart: [TOEICPart: Int] = [
            .part1: 3, .part2: 13, .part3: 18, .part4: 15, .part5: 15, .part6: 8, .part7: 28
        ]
        for part in TOEICPart.allCases {
            XCTAssertEqual(package.groups.filter { $0.part == part }.flatMap(\.items).count, expectedItemsByPart[part])
        }
        let listeningGroups = package.groups.filter { $0.part.section == .listening }
        XCTAssertEqual(listeningGroups.count, 27)
        XCTAssertTrue(listeningGroups.allSatisfy { $0.version == 2 && $0.audioAssetID != nil })
        XCTAssertTrue(package.groups.allSatisfy {
            $0.purpose == .training && $0.contentStatus == .aiChecked && !$0.fixture
        })
        XCTAssertEqual(package.assets.count, 30)
        XCTAssertEqual(package.assets.filter { $0.kind == .audio }.count, 27)
        XCTAssertEqual(package.assets.filter { $0.kind == .image }.count, 3)
        let partOne = try XCTUnwrap(package.groups.first { $0.id == "ag-g-p1-000001" })
        XCTAssertTrue(try XCTUnwrap(partOne.items.first?.transcript).hasPrefix("A. She is looking through a microscope."))
        XCTAssertTrue(try XCTUnwrap(partOne.items.first?.transcript).contains("D. She is putting on a laboratory coat."))
        let partTwo = try XCTUnwrap(package.groups.first { $0.id == "ag-g-p2-000001" })
        XCTAssertTrue(try XCTUnwrap(partTwo.items.first?.transcript).hasPrefix("Question:"))
        XCTAssertTrue(try XCTUnwrap(partTwo.items.first?.transcript).contains("A. In the top tray"))
        for asset in package.assets {
            XCTAssertTrue(asset.id.contains("::"), "asset IDs must retain their source-batch namespace")
            XCTAssertTrue(asset.path.hasPrefix(root.path), "installed assets must point into the version store")
            XCTAssertTrue(FileManager.default.fileExists(atPath: asset.path))
            let expectedHash = try XCTUnwrap(asset.checksumSHA256)
            XCTAssertEqual(sha256(try Data(contentsOf: URL(fileURLWithPath: asset.path))), expectedHash)
        }

        let reopened = ContentVersionStore(rootURL: root)
        let reopenedPackage = try XCTUnwrap(reopened.activePackage())
        XCTAssertEqual(reopenedPackage.groups.count, 51)
        XCTAssertEqual(reopenedPackage.groups.flatMap(\.items).count, 100)
        XCTAssertEqual(reopenedPackage.assets.count, 30)
        let repeated = try reopened.install(from: exports.appending(path: "batch-ag-0001"))
        XCTAssertTrue(repeated.wasAlreadyInstalled)
        XCTAssertEqual(repeated.activeBatchIDs.count, 7)
        XCTAssertEqual(repeated.package.groups.count, 51)
        XCTAssertEqual(repeated.package.groups.flatMap(\.items).count, 100)

        let stateBefore = try Data(contentsOf: root.appending(path: "state.json"))
        let broken = temporaryDirectory(name: "invalid-batch")
        try FileManager.default.copyItem(
            at: exports.appending(path: "batch-ag-0005/groups.jsonl"),
            to: broken.appending(path: "groups.jsonl")
        )
        for path in ["manifest.json", "reviews.jsonl"] {
            try FileManager.default.copyItem(at: exports.appending(path: "batch-ag-0005/\(path)"), to: broken.appending(path: path))
        }
        try FileManager.default.createDirectory(at: broken.appending(path: "reports"), withIntermediateDirectories: true)
        for path in ["blind-solve.json", "summary.md", "validation.json"] {
            try FileManager.default.copyItem(at: exports.appending(path: "batch-ag-0005/reports/\(path)"), to: broken.appending(path: "reports/\(path)"))
        }
        var corruptGroups = try Data(contentsOf: broken.appending(path: "groups.jsonl"))
        corruptGroups.append(0x20)
        try corruptGroups.write(to: broken.appending(path: "groups.jsonl"))
        XCTAssertThrowsError(try reopened.install(from: broken))
        XCTAssertEqual(try Data(contentsOf: root.appending(path: "state.json")), stateBefore)
        XCTAssertEqual(try reopened.activePackage()?.groups.count, 51)
        XCTAssertEqual(try reopened.activePackage()?.groups.flatMap(\.items).count, 100)
    }

    @MainActor
    func testRevisionBatches0011Through0015UpgradeInPlaceAndMergeWithSeedCatalog() throws {
        let root = temporaryDirectory(name: "revision-batches")
        let store = ContentVersionStore(rootURL: root)
        let exports = repositoryRoot.appending(path: "exports")
        for number in 1...7 {
            _ = try store.install(from: exports.appending(path: String(format: "batch-ag-%04d", number)))
        }

        var latest: InstalledContentBatch?
        for number in 11...13 {
            latest = try store.install(from: exports.appending(path: String(format: "batch-ag-%04d", number)))
        }
        let itemIDsBeforeRevision = Set(try XCTUnwrap(latest?.package).groups.flatMap { $0.items.map(\.id) })
        XCTAssertEqual(itemIDsBeforeRevision.count, 177)

        for number in 14...15 {
            let batchURL = exports.appending(path: String(format: "batch-ag-%04d", number))
            let imported = try ContentBatchImporter.loadAndValidate(directory: batchURL)
            assertEvidenceQuotesResolve(in: imported.groups)
            latest = try store.install(from: batchURL)
        }

        let package = try XCTUnwrap(latest?.package)
        XCTAssertEqual(latest?.activeBatchIDs.count, 12)
        XCTAssertEqual(package.groups.count, 106)
        XCTAssertEqual(package.groups.flatMap(\.items).count, 177)
        XCTAssertEqual(Set(package.groups.map(\.id)).count, 106)
        XCTAssertEqual(Set(package.groups.flatMap { $0.items.map(\.id) }).count, 177)
        XCTAssertEqual(Set(package.groups.flatMap { $0.items.map(\.id) }), itemIDsBeforeRevision)
        XCTAssertEqual(package.groups.filter { $0.purpose == .training }.flatMap(\.items).count, 129)
        XCTAssertEqual(package.groups.filter { $0.purpose == .diagnostic }.flatMap(\.items).count, 24)
        XCTAssertEqual(package.groups.filter { $0.purpose == .battle }.flatMap(\.items).count, 24)
        let diagnosticRevisionIDs = (301...304).map { String(format: "ag-g-p2-%06d", $0) }
        let battleRevisionIDs = (401...406).map { String(format: "ag-g-p2-%06d", $0) }
        for groupID in diagnosticRevisionIDs {
            let group = try XCTUnwrap(package.groups.first { $0.id == groupID })
            XCTAssertEqual(group.version, 3)
            XCTAssertEqual(group.sourceBatchID, "batch-ag-0014")
        }
        for groupID in battleRevisionIDs {
            let group = try XCTUnwrap(package.groups.first { $0.id == groupID })
            XCTAssertEqual(group.version, 3)
            XCTAssertEqual(group.sourceBatchID, "batch-ag-0015")
        }
        let model = AppModel(
            store: LocalProfileStore(fileURL: root.appending(path: "profile.json")),
            contentStore: store,
            backend: LocalBackendClient(hub: LocalBackendHub(storeURL: root.appending(path: "backend.json")))
        )
        let completeItems = package.groups.filter { model.materialAvailability(for: $0) == .complete }.flatMap(\.items).count
        let previewItems = package.groups.filter {
            if case .previewOnly = model.materialAvailability(for: $0) { return true }
            return false
        }.flatMap(\.items).count
        XCTAssertEqual(completeItems, 177)
        XCTAssertEqual(previewItems, 0)

        let reopened = ContentVersionStore(rootURL: root)
        let reopenedPackage = try XCTUnwrap(reopened.activePackage())
        XCTAssertEqual(reopenedPackage.groups.flatMap(\.items).count, 177)
        for batchID in ["batch-ag-0011", "batch-ag-0014", "batch-ag-0015"] {
            let repeated = try reopened.install(from: exports.appending(path: batchID))
            XCTAssertTrue(repeated.wasAlreadyInstalled)
            XCTAssertEqual(repeated.package.groups.flatMap(\.items).count, 177)
        }
    }

    func testHigherGroupVersionReplacesOnlyThatGroup() throws {
        let old = runtimeGroup(id: "same", version: 1, batch: "batch-1")
        let unrelated = runtimeGroup(id: "other", version: 1, batch: "batch-1")
        let updated = runtimeGroup(id: "same", version: 2, batch: "batch-2")
        let first = runtimePackage(id: "batch-1", groups: [old, unrelated])
        let second = runtimePackage(id: "batch-2", groups: [updated])
        let merged = try XCTUnwrap(ContentVersionStore.mergePackages([first, second]))
        XCTAssertEqual(merged.groups.count, 2)
        XCTAssertEqual(merged.groups.first { $0.id == "same" }?.version, 2)
        XCTAssertEqual(merged.groups.first { $0.id == "same" }?.sourceBatchID, "batch-2")
        XCTAssertNotNil(merged.groups.first { $0.id == "other" })
    }

    func testSameGroupVersionWithDifferentHashIsRejected() {
        let group = makeGroup(id: "cx-g-p5-0001", itemID: "cx-i-p5-0001", family: "family-a", pool: .training)
        let existing = ContentImportIndex(groups: [.init(
            groupID: group.groupID, version: group.version, contentHash: "different",
            batchID: "older-batch", familyID: group.familyID, pool: group.pool,
            itemIDs: group.items.map(\.itemID)
        )])
        XCTAssertThrowsError(try ContentVersionStore().validateCrossBatch([group], existing: existing)) { error in
            guard case ContentVersionStore.StoreError.sameVersionDifferentContent = error else {
                return XCTFail("unexpected error: \(error)")
            }
        }
    }

    func testItemIDCannotMoveToAnotherGroup() {
        let group = makeGroup(id: "cx-g-p5-new", itemID: "shared-item", family: "family-new", pool: .training)
        let existing = ContentImportIndex(groups: [.init(
            groupID: "cx-g-p5-old", version: 1, contentHash: "hash", batchID: "older-batch",
            familyID: "family-old", pool: .training, itemIDs: ["shared-item"]
        )])
        XCTAssertThrowsError(try ContentVersionStore().validateCrossBatch([group], existing: existing)) { error in
            guard case ContentVersionStore.StoreError.itemIDConflict("shared-item") = error else {
                return XCTFail("unexpected error: \(error)")
            }
        }
    }

    func testFamilyCannotCrossPoolsAcrossBatches() {
        let group = makeGroup(id: "cx-g-p5-new", itemID: "new-item", family: "same-family", pool: .battle)
        let existing = ContentImportIndex(groups: [.init(
            groupID: "cx-g-p5-old", version: 1, contentHash: "hash", batchID: "older-batch",
            familyID: "same-family", pool: .training, itemIDs: ["old-item"]
        )])
        XCTAssertThrowsError(try ContentVersionStore().validateCrossBatch([group], existing: existing)) { error in
            guard case ContentVersionStore.StoreError.familyPoolConflict = error else {
                return XCTFail("unexpected error: \(error)")
            }
        }
    }

    private func makeGroup(id: String, itemID: String, family: String, pool: BatchPool) -> BatchGroup {
        let choices = ["A", "B", "C", "D"].map { BatchChoice(id: $0, textEN: $0) }
        return BatchGroup(
            schemaVersion: "1.0.0", groupID: id, version: 1, familyID: family, pool: pool, fixture: true,
            part: 5, layout: .sentence, scenario: "office_reporting",
            difficulty: .init(level: "D2", rationaleZH: "測試", basis: "editorial"), contentStatus: .aiChecked,
            stimulus: .init(documents: [], speakers: [], audioScript: []), assets: [],
            items: [.init(
                itemID: itemID, promptEN: "The report is _____ complete.", choices: choices,
                answerChoiceID: "A", skillTags: ["word_form"],
                evidence: [.init(sourceType: "item_prompt", sourceID: itemID, quoteEN: "is _____ complete", reasoningZH: "測試")],
                explanationZH: "測試", distractorNotes: [
                    .init(choiceID: "B", reasonZH: "測試"), .init(choiceID: "C", reasonZH: "測試"),
                    .init(choiceID: "D", reasonZH: "測試")
                ], vocabulary: [], estimatedTimeSec: 20
            )],
            provenance: .init(origin: "original", authorTool: "tests", authorModel: "none", createdAt: .now, rightsNoteZH: "測試"),
            reviewRefs: ["review-\(id)"]
        )
    }

    private var repositoryRoot: URL {
        URL(fileURLWithPath: #filePath).deletingLastPathComponent().deletingLastPathComponent()
    }

    private func temporaryDirectory(name: String) -> URL {
        let url = FileManager.default.temporaryDirectory.appending(path: "TOEICPathTests-\(name)-\(UUID().uuidString)", directoryHint: .isDirectory)
        try! FileManager.default.createDirectory(at: url, withIntermediateDirectories: true)
        addTeardownBlock { try? FileManager.default.removeItem(at: url) }
        return url
    }

    private func assertEvidenceQuotesResolve(
        in groups: [BatchGroup],
        file: StaticString = #filePath,
        line: UInt = #line
    ) {
        for group in groups {
            let segmentText = Dictionary(
                group.stimulus.audioScript.map { ($0.segmentID, $0.textEN) },
                uniquingKeysWith: { first, _ in first }
            )
            let blockText = Dictionary(
                group.stimulus.documents.flatMap { document in
                    document.blocks.map { block in
                        let text = block.textEN ?? ((block.columns.map { [$0] } ?? []) + (block.rows ?? []))
                            .map { $0.joined(separator: " | ") }
                            .joined(separator: "\n")
                        return (block.blockID, text)
                    }
                },
                uniquingKeysWith: { first, _ in first }
            )
            for item in group.items {
                for evidence in item.evidence where evidence.sourceType != "asset" {
                    let source: String? = switch evidence.sourceType {
                    case "audio_segment": segmentText[evidence.sourceID]
                    case "document_block": blockText[evidence.sourceID]
                    case "item_prompt" where evidence.sourceID == item.itemID: item.promptEN
                    default: nil
                    }
                    let normalizedQuote = evidence.quoteEN.split(whereSeparator: \.isWhitespace).joined(separator: " ")
                    let normalizedSource = source?.split(whereSeparator: \.isWhitespace).joined(separator: " ")
                    XCTAssertFalse(normalizedQuote.isEmpty, "\(group.groupID)/\(item.itemID) quote is empty", file: file, line: line)
                    XCTAssertNotNil(source, "\(group.groupID)/\(item.itemID) source \(evidence.sourceID) is missing", file: file, line: line)
                    XCTAssertTrue(
                        normalizedSource?.contains(normalizedQuote) == true,
                        "\(group.groupID)/\(item.itemID) quote is not present in \(evidence.sourceID)",
                        file: file,
                        line: line
                    )
                }
            }
        }
    }

    private func runtimeGroup(id: String, version: Int, batch: String) -> QuestionGroup {
        let source = SampleContent.groups.first { $0.part == .part5 }!
        return QuestionGroup(
            id: id, version: version, sourceBatchID: batch, familyID: "family-\(id)", part: .part5,
            difficulty: .d2, scenario: "test", documents: [], items: source.items,
            audioAssetID: nil, timeLimitSeconds: nil, tags: ["training"]
        )
    }

    private func runtimePackage(id: String, groups: [QuestionGroup]) -> ContentPackage {
        ContentPackage(
            manifest: .init(schemaVersion: 1, packageID: id, contentVersion: id, locale: "en", createdAt: .now,
                            generator: "tests", generatorVersion: "1", license: "tests"),
            assets: [], groups: groups
        )
    }

    private func sha256(_ data: Data) -> String {
        SHA256.hash(data: data).map { String(format: "%02x", $0) }.joined()
    }
}
