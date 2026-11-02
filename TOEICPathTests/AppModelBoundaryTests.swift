import XCTest
@testable import TOEICPath

@MainActor
final class AppModelBoundaryTests: XCTestCase {
    func testSessionBoundaryRejectsWrongPurposeFixtureAndMissingMaterial() throws {
        let training = TestFixtures.formalGroup(id: "training", part: .part5, purpose: .training)
        let diagnostic = TestFixtures.formalGroup(id: "diagnostic", part: .part5, purpose: .diagnostic)
        let missingAudio = QuestionGroup(
            id: "missing-audio", familyID: "missing-audio-family", part: .part3, difficulty: .d2,
            scenario: "missing", documents: [], items: training.items, audioAssetID: nil,
            timeLimitSeconds: nil, tags: [], purpose: .training, contentStatus: .aiChecked, fixture: false
        )
        let fixture = QuestionGroup(
            id: "fixture", familyID: "fixture-family", part: .part5, difficulty: .d2,
            scenario: "fixture", documents: [], items: training.items, audioAssetID: nil,
            timeLimitSeconds: nil, tags: [], purpose: .training, contentStatus: .humanReviewed, fixture: true
        )
        let model = makeModel(groups: [training, diagnostic, missingAudio, fixture])
        XCTAssertNoThrow(try model.beginSession(groups: [training], mode: .practice))
        model.abortActiveSession()
        XCTAssertThrowsError(try model.beginSession(groups: [training], mode: .diagnostic))
        XCTAssertThrowsError(try model.beginSession(groups: [fixture], mode: .practice))
        XCTAssertThrowsError(try model.beginSession(groups: [missingAudio], mode: .practice))
        XCTAssertThrowsError(try model.beginSession(groups: [], mode: .practice))
    }

    func testBattleBoundaryDoesNotFallbackToTrainingPartFive() async {
        let training = TestFixtures.formalGroup(id: "training", part: .part5, purpose: .training)
        let model = makeModel(groups: [training])
        do {
            try await model.createLocalBattle(opponentID: UUID())
            XCTFail("Expected battle pool shortage")
        } catch { }
    }

    func testMockBoundaryRejectsUnresolvedRuntimeForm() {
        let model = makeModel(groups: [])
        let form = MockExamForm(
            id: "unresolved", contentVersion: "v1", orderedGroupIDs: [], orderedItemIDs: [],
            listeningItemIDs: [], readingItemIDs: [], listeningUnlockOffsetsSeconds: [:],
            listeningDurationSeconds: 1, readingTimeLimitSeconds: 4_500,
            audioTimelineAssetIDs: ["missing"]
        )
        XCTAssertThrowsError(try model.startMockExam(form: form))
    }

    private func makeModel(groups: [QuestionGroup]) -> AppModel {
        let directory = FileManager.default.temporaryDirectory
            .appending(path: "TOEICPathAppModelTests-\(UUID().uuidString)", directoryHint: .isDirectory)
        try! FileManager.default.createDirectory(at: directory, withIntermediateDirectories: true)
        addTeardownBlock { try? FileManager.default.removeItem(at: directory) }
        let package = ContentPackage(
            manifest: .init(
                schemaVersion: 1, packageID: "tests", contentVersion: "tests", locale: "en",
                createdAt: .now, generator: "tests", generatorVersion: "1", license: "tests"
            ),
            assets: [], groups: groups
        )
        return AppModel(
            store: LocalProfileStore(fileURL: directory.appending(path: "profile.json")),
            package: package,
            contentStore: ContentVersionStore(rootURL: directory.appending(path: "content")),
            backend: LocalBackendClient(hub: LocalBackendHub(storeURL: directory.appending(path: "backend.json")))
        )
    }
}
