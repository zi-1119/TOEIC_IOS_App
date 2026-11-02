import XCTest
@testable import TOEICPath

final class ExamAndBattleTests: XCTestCase {
    func testOfficialBlueprintTotalsTwoHundred() {
        XCTAssertEqual(MockExamBlueprint.standard.totalItems, 200)
        XCTAssertEqual(MockExamBlueprint.standard.counts.filter { $0.key.section == .listening }.values.reduce(0, +), 100)
        XCTAssertEqual(MockExamBlueprint.standard.counts.filter { $0.key.section == .reading }.values.reduce(0, +), 100)
    }

    func testPreviewBankReportsShortagesInsteadOfStartingFakeExam() {
        let assembly = MockExamEngine.assemble(from: SampleContent.groups)
        XCTAssertFalse(assembly.isReady)
        XCTAssertFalse(assembly.shortages.isEmpty)
    }

    func testAssemblyFindsExactCombinationInsteadOfGreedyDeadEnd() {
        let source = SampleContent.groups.last!
        func resized(_ id: String, family: String, count: Int) -> QuestionGroup {
            let seed = source.items.first!
            let items = (0..<count).map { index in
                QuestionItem(id: "\(id)-\(index)", prompt: seed.prompt, options: seed.options, correctOptionID: seed.correctOptionID,
                             explanation: seed.explanation, skills: seed.skills, transcript: nil, imageAssetID: nil, audioAssetID: nil)
            }
            return QuestionGroup(id: id, familyID: family, part: .part7, difficulty: .d2, scenario: id,
                                 documents: source.documents, items: items, audioAssetID: nil, timeLimitSeconds: nil, tags: [],
                                 purpose: .mock, contentStatus: .humanReviewed, fixture: false)
        }
        let groups = [resized("a-four", family: "f1", count: 4), resized("b-three", family: "f2", count: 3), resized("c-two", family: "f3", count: 2)]
        let blueprint = MockExamBlueprint(counts: [.part7: 5], readingTimeLimitSeconds: 60, listeningExpectedSeconds: 60)
        let assembly = MockExamEngine.assemble(from: groups, blueprint: blueprint)
        XCTAssertEqual(assembly.groups.flatMap(\.items).count, 5)
        XCTAssertTrue(assembly.shortages.isEmpty)
    }

    func testMockAssemblyNeverConsumesTrainingPool() {
        let training = TestFixtures.formalGroup(id: "training", part: .part7, purpose: .training, itemCount: 5)
        let blueprint = MockExamBlueprint(counts: [.part7: 5], readingTimeLimitSeconds: 60, listeningExpectedSeconds: 60)
        let assembly = MockExamEngine.assemble(from: [training], blueprint: blueprint)
        XCTAssertTrue(assembly.groups.isEmpty)
        XCTAssertEqual(assembly.shortages[.part7], 5)
    }

    func testBattleHappyPathAndTerminalStates() {
        let path: [MatchState] = [.invited, .accepted, .preparing, .active, .settling, .completed]
        for pair in zip(path, path.dropFirst()) {
            XCTAssertTrue(BattleStateMachine.canTransition(from: pair.0, to: pair.1))
        }
        XCTAssertFalse(BattleStateMachine.canTransition(from: .completed, to: .active))
        XCTAssertFalse(BattleStateMachine.canTransition(from: .invited, to: .completed))
    }
}
