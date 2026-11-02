import XCTest
@testable import TOEICPath

final class ReviewSchedulerTests: XCTestCase {
    func testIncorrectAnswerReturnsNextDayAndResetsRepetition() {
        let now = Date(timeIntervalSince1970: 1_800_000_000)
        let previous = ReviewState(itemID: "q", repetitions: 4, masteryEvidence: 2, lastFamilyID: "old", lastReviewedAt: now, nextReviewAt: now)
        let state = ReviewScheduler.updatedState(for: response(correct: false, family: "new"), previous: previous, now: now)
        XCTAssertEqual(state.repetitions, 0)
        XCTAssertEqual(state.masteryEvidence, 2)
        XCTAssertEqual(state.nextReviewAt.timeIntervalSince(now), 86_400, accuracy: 1)
    }

    func testNewFamilyStandardSuccessAddsTransferEvidence() {
        let now = Date(timeIntervalSince1970: 1_800_000_000)
        let previous = ReviewState(itemID: "q", repetitions: 1, masteryEvidence: 0, lastFamilyID: "old", lastReviewedAt: now, nextReviewAt: now)
        let state = ReviewScheduler.updatedState(for: response(correct: true, family: "new"), previous: previous, now: now)
        XCTAssertEqual(state.repetitions, 2)
        XCTAssertEqual(state.masteryEvidence, 1)
        XCTAssertEqual(state.nextReviewAt.timeIntervalSince(now), 3 * 86_400, accuracy: 1)
    }

    func testDailyPlanPreservesCompleteGroupsAndPrioritizesDueReview() {
        let dueGroup = TestFixtures.formalGroup(id: "due-reading", part: .part7, purpose: .training, itemCount: 2)
        let other = TestFixtures.formalGroup(id: "other-reading", part: .part5, purpose: .training)
        let dueItem = dueGroup.items.first!.id
        let now = Date(timeIntervalSince1970: 1_800_000_000)
        var profile = LocalProfile()
        profile.preferences.dailyMinutes = 10
        profile.reviewStates[dueItem] = ReviewState(itemID: dueItem, repetitions: 1, masteryEvidence: 0, lastFamilyID: nil, lastReviewedAt: now, nextReviewAt: now)
        let plan = DailyPlanner.makePlan(groups: [other, dueGroup], profile: profile, now: now)
        XCTAssertEqual(plan.groups.first?.part, .part7)
        XCTAssertEqual(plan.groups.first?.items.count, dueGroup.items.count)
        XCTAssertTrue(plan.reasons[plan.groups.first!.id]?.contains("到期複習") == true)
    }

    func testDailyPlanNeverSelectsMockDiagnosticBattleOrFixtureContent() {
        let training = TestFixtures.formalGroup(id: "training", part: .part5, purpose: .training)
        let mock = TestFixtures.formalGroup(id: "mock", part: .part5, purpose: .mock)
        let diagnostic = TestFixtures.formalGroup(id: "diagnostic", part: .part5, purpose: .diagnostic)
        let battle = TestFixtures.formalGroup(id: "battle", part: .part5, purpose: .battle)
        let fixture = QuestionGroup(
            id: "fixture", familyID: "fixture-family", part: .part5, difficulty: .d2, scenario: "fixture",
            documents: [], items: training.items, audioAssetID: nil, timeLimitSeconds: nil, tags: [],
            purpose: .training, contentStatus: .humanReviewed, fixture: true
        )
        let plan = DailyPlanner.makePlan(groups: [mock, diagnostic, battle, fixture, training], profile: LocalProfile())
        XCTAssertEqual(plan.groups.map(\.id), ["training"])
    }

    func testPartSelectorPrioritizesUnexposedAndKeepsReviewExplicit() {
        let seen = TestFixtures.formalGroup(id: "seen", familyID: "seen-family", part: .part5, purpose: .training)
        let fresh = TestFixtures.formalGroup(id: "fresh", familyID: "fresh-family", part: .part5, purpose: .training)
        var profile = LocalProfile()
        profile.exposures[seen.id] = ContentExposure(
            groupID: seen.id, familyIDs: [seen.familyID], versions: [seen.version], sourceBatchIDs: [seen.sourceBatchID],
            itemIDs: [seen.items[0].id], modes: [.practice], firstExposedAt: .now, lastExposedAt: .now, presentationCount: 1
        )
        let selection = PartPracticeSelector.select(part: .part5, from: [seen, fresh], profile: profile)
        XCTAssertEqual(selection.newGroups.map(\.id), ["fresh"])
        XCTAssertEqual(selection.reviewGroups.map(\.id), ["seen"])
    }

    private func response(correct: Bool, family: String) -> ItemResponse {
        .init(id: UUID(), sessionID: UUID(), groupID: family, itemID: "q", part: .part5, difficulty: .d2,
              familyID: family, selectedOptionID: "A", isCorrect: correct, answeredAt: .now,
              elapsedMilliseconds: 100, condition: AnswerCondition())
    }
}
