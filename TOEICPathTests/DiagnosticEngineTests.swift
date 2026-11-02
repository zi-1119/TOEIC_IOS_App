import XCTest
@testable import TOEICPath

final class DiagnosticEngineTests: XCTestCase {
    func testVoiceOverAndBackgroundConditionsAreNotStandardEvidence() {
        XCTAssertFalse(AnswerCondition(voiceOverRunning: true).isStandard)
        XCTAssertFalse(AnswerCondition(appBackgrounded: true).isStandard)
        XCTAssertTrue(AnswerCondition(audioOutputRoute: "Speaker", audioSessionSampleRate: 48_000).isStandard)
    }
    func testDoesNotMoveOnSingleGroup() {
        let response = makeResponse(group: "g1", correct: true)
        let decision = DiagnosticEngine.decide(current: .d2, responses: [response], shortForm: false)
        XCTAssertEqual(decision.action, .insufficientEvidence)
        XCTAssertEqual(decision.nextDifficulty, .d2)
    }

    func testPromotesAfterIndependentStableEvidence() {
        let responses = [makeResponse(group: "g1", correct: true), makeResponse(group: "g2", correct: true)]
        let decision = DiagnosticEngine.decide(current: .d2, responses: responses, shortForm: false)
        XCTAssertEqual(decision.action, .promote)
        XCTAssertEqual(decision.nextDifficulty, .d3)
        XCTAssertEqual(decision.ruleVersion, DiagnosticRule.initial.version)
    }

    func testAssistedResponseDoesNotCountAsStandardEvidence() {
        var assisted = makeResponse(group: "g2", correct: true).condition
        assisted.transcriptShown = true
        let base = makeResponse(group: "g2", correct: true)
        let modified = ItemResponse(
            id: base.id, sessionID: base.sessionID, groupID: base.groupID, itemID: base.itemID, part: base.part,
            difficulty: base.difficulty, familyID: base.familyID, selectedOptionID: base.selectedOptionID,
            isCorrect: base.isCorrect, answeredAt: base.answeredAt, elapsedMilliseconds: base.elapsedMilliseconds,
            condition: assisted
        )
        let decision = DiagnosticEngine.decide(current: .d2, responses: [makeResponse(group: "g1", correct: true), modified], shortForm: false)
        XCTAssertEqual(decision.action, .insufficientEvidence)
    }

    func testRouterBalancesListeningAndReadingAndDoesNotReuseFamilies() {
        let groups = [
            TestFixtures.formalGroup(id: "diagnostic-listening", part: .part3, purpose: .diagnostic, itemCount: 3),
            TestFixtures.formalGroup(id: "diagnostic-reading", part: .part5, purpose: .diagnostic, itemCount: 3)
        ]
        let first = DiagnosticRouter.nextGroup(from: groups, selectedGroups: [], responses: [])
        XCTAssertEqual(first?.group.part.section, .listening)
        guard let first else { return }
        let second = DiagnosticRouter.nextGroup(from: groups, selectedGroups: [first.group], responses: [])
        XCTAssertEqual(second?.group.part.section, .reading)
        XCTAssertNotEqual(second?.group.familyID, first.group.familyID)
        XCTAssertTrue(second?.reason.contains("完整題組覆蓋") == true)
    }

    func testRouterNeverFallsBackToTrainingWhenDiagnosticPoolIsEmpty() {
        let training = TestFixtures.formalGroup(id: "training-only", part: .part5, purpose: .training)
        XCTAssertNil(DiagnosticRouter.nextGroup(from: [training], selectedGroups: [], responses: []))
    }

    func testRouterSelectsOnlyDiagnosticFromMixedFourPoolBank() {
        let groups = [
            TestFixtures.formalGroup(id: "training", part: .part3, purpose: .training),
            TestFixtures.formalGroup(id: "battle", part: .part3, purpose: .battle),
            TestFixtures.formalGroup(id: "mock", part: .part3, purpose: .mock),
            TestFixtures.formalGroup(id: "diagnostic", part: .part3, purpose: .diagnostic)
        ]
        XCTAssertEqual(DiagnosticRouter.nextGroup(from: groups, selectedGroups: [], responses: [])?.group.id, "diagnostic")
    }

    func testRouterRejectsAllFixtureBankAndStopsWhenAllFamiliesWereExposed() {
        let formal = TestFixtures.formalGroup(id: "formal", part: .part3, purpose: .diagnostic)
        let fixture = QuestionGroup(
            id: "fixture", familyID: "fixture-family", part: .part3, difficulty: .d2,
            scenario: "fixture", documents: formal.documents, items: formal.items,
            audioAssetID: formal.audioAssetID, timeLimitSeconds: nil, tags: [],
            purpose: .diagnostic, contentStatus: .humanReviewed, fixture: true
        )
        XCTAssertNil(DiagnosticRouter.nextGroup(from: [fixture], selectedGroups: [], responses: []))
        XCTAssertNil(DiagnosticRouter.nextGroup(
            from: [formal], selectedGroups: [], responses: [], exposedFamilyIDs: [formal.familyID]
        ))
    }

    func testRouterExcludesHistoricallyExposedFamily() {
        let exposed = TestFixtures.formalGroup(id: "seen", familyID: "seen-family", part: .part3, purpose: .diagnostic)
        let fresh = TestFixtures.formalGroup(id: "fresh", familyID: "fresh-family", part: .part3, purpose: .diagnostic)
        let selection = DiagnosticRouter.nextGroup(
            from: [exposed, fresh], selectedGroups: [], responses: [], exposedFamilyIDs: ["seen-family"]
        )
        XCTAssertEqual(selection?.group.id, "fresh")
    }

    func testPreviewDiagnosticSummaryReportsInsufficientEvidence() {
        let summary = DiagnosticRouter.summary(selectedGroups: SampleContent.groups, responses: [])
        XCTAssertFalse(summary.hasTargetEvidence)
        XCTAssertFalse(summary.uncoveredParts.isEmpty)
        XCTAssertTrue(summary.message.contains("不足"))
    }

    private func makeResponse(group: String, correct: Bool) -> ItemResponse {
        .init(id: UUID(), sessionID: UUID(), groupID: group, itemID: UUID().uuidString, part: .part3,
              difficulty: .d2, familyID: group, selectedOptionID: "A", isCorrect: correct,
              answeredAt: .now, elapsedMilliseconds: 1000, condition: AnswerCondition())
    }
}
