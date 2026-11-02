import XCTest
@testable import TOEICPath

final class ExposurePersistenceTests: XCTestCase {
    func testPresentedItemPersistsAcrossRestartAndTracksLaterVersion() throws {
        let directory = FileManager.default.temporaryDirectory
            .appending(path: "TOEICPathExposureTests-\(UUID().uuidString)", directoryHint: .isDirectory)
        let fileURL = directory.appending(path: "profile.json")
        addTeardownBlock { try? FileManager.default.removeItem(at: directory) }
        let store = LocalProfileStore(fileURL: fileURL)
        let first = TestFixtures.formalGroup(
            id: "stable-group", familyID: "stable-family", part: .part5, purpose: .training,
            version: 1, sourceBatchID: "batch-v1"
        )
        var profile = LocalProfile()
        profile.recordExposure(group: first, itemID: first.items[0].id, mode: .practice, now: Date(timeIntervalSince1970: 100))
        try store.save(profile)

        var reopened = store.load()
        XCTAssertEqual(reopened.exposures[first.id]?.itemIDs, Set([first.items[0].id]))
        XCTAssertEqual(reopened.exposures[first.id]?.versions, Set([1]))
        XCTAssertEqual(reopened.exposures[first.id]?.presentationCount, 1)

        let updated = TestFixtures.formalGroup(
            id: "stable-group", familyID: "stable-family", part: .part5, purpose: .training,
            version: 2, sourceBatchID: "batch-v2"
        )
        reopened.recordExposure(group: updated, itemID: updated.items[0].id, mode: .review, now: Date(timeIntervalSince1970: 200))
        XCTAssertEqual(reopened.exposures[first.id]?.versions, Set([1, 2]))
        XCTAssertEqual(reopened.exposures[first.id]?.sourceBatchIDs, Set(["batch-v1", "batch-v2"]))
        XCTAssertEqual(reopened.exposures[first.id]?.modes, Set([.practice, .review]))
        XCTAssertEqual(reopened.exposures[first.id]?.presentationCount, 2)
    }

    func testLegacyProfileMigratesOnlySubmittedResponsesIntoExposureHistory() throws {
        let group = TestFixtures.formalGroup(id: "answered", part: .part5, purpose: .training)
        let sessionID = UUID()
        let response = ItemResponse(
            id: UUID(), sessionID: sessionID, groupID: group.id, groupVersion: group.version,
            sourceBatchID: group.sourceBatchID, itemID: group.items[0].id, part: group.part,
            difficulty: group.difficulty, familyID: group.familyID, selectedOptionID: "A", isCorrect: true,
            answeredAt: Date(timeIntervalSince1970: 100), elapsedMilliseconds: 500, condition: AnswerCondition()
        )
        let legacy = LegacyProfile(
            preferences: UserPreferences(),
            sessions: [LearningSession(
                id: sessionID, mode: .practice, contentVersion: "v1", startedAt: Date(timeIntervalSince1970: 90),
                completedAt: Date(timeIntervalSince1970: 100), groupIDs: [group.id, "viewed-but-unanswered"],
                responses: [response], ruleVersion: nil, selectionReasons: [:]
            )],
            dueItemIDs: [], hiddenConversationIDs: [], reviewStates: [:], activeMockExam: nil
        )
        let data = try JSONEncoder().encode(legacy)
        let migrated = try JSONDecoder().decode(LocalProfile.self, from: data)
        XCTAssertNotNil(migrated.exposures[group.id])
        XCTAssertNil(migrated.exposures["viewed-but-unanswered"])
    }

    private struct LegacyProfile: Codable {
        let preferences: UserPreferences
        let sessions: [LearningSession]
        let dueItemIDs: [String]
        let hiddenConversationIDs: Set<UUID>
        let reviewStates: [String: ReviewState]
        let activeMockExam: MockExamRuntime?
    }
}
