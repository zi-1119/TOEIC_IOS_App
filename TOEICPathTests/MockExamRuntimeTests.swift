import XCTest
@testable import TOEICPath

final class MockExamRuntimeTests: XCTestCase {
    func testListeningTimelineUnlocksItemsWithoutPausingDeadline() throws {
        let start = Date(timeIntervalSince1970: 1_800_000_000)
        var runtime = MockExamRuntime(form: makeForm(), now: start)
        try runtime.start(now: start)
        XCTAssertEqual(runtime.phase, .listening)
        XCTAssertEqual(runtime.availableItemIDs(at: start), ["L0"])
        XCTAssertThrowsError(try runtime.select(optionID: "A", for: "L1", now: start))

        try runtime.select(optionID: "B", for: "L1", now: start.addingTimeInterval(10))
        runtime.beginInterruption(.background, now: start.addingTimeInterval(20))
        runtime.endInterruption(.background, now: start.addingTimeInterval(40))
        XCTAssertEqual(runtime.remainingSeconds(at: start.addingTimeInterval(40)), 2_660)

        runtime.updateForTime(start.addingTimeInterval(2_700))
        XCTAssertEqual(runtime.phase, .sectionBreak)
        XCTAssertEqual(runtime.selectedOptionIDs["L1"], "B")
    }

    func testReadingExpiresAtOriginalDeadlineAcrossRestore() throws {
        let start = Date(timeIntervalSince1970: 1_800_000_000)
        var runtime = MockExamRuntime(form: makeForm(), now: start)
        try runtime.start(now: start)
        runtime.updateForTime(start.addingTimeInterval(2_700))
        try runtime.beginReading(now: start.addingTimeInterval(2_710))
        try runtime.select(optionID: "C", for: "R99", now: start.addingTimeInterval(2_720))

        let data = try JSONEncoder().encode(LocalProfile(activeMockExam: runtime))
        var restored = try JSONDecoder().decode(LocalProfile.self, from: data).activeMockExam!
        restored.updateForTime(start.addingTimeInterval(2_710 + 4_500))
        XCTAssertEqual(restored.phase, .expired)
        XCTAssertEqual(restored.selectedOptionIDs["R99"], "C")
        try restored.submit(now: start.addingTimeInterval(2_710 + 4_501))
        XCTAssertEqual(restored.phase, .submitted)
    }

    func testFormRejectsMissingAuthoritativeAudioTimeline() {
        let form = MockExamForm(
            id: "bad", contentVersion: "v1", orderedGroupIDs: [], orderedItemIDs: [],
            listeningItemIDs: [], readingItemIDs: [], listeningUnlockOffsetsSeconds: [:],
            listeningDurationSeconds: 0, readingTimeLimitSeconds: 4_500, audioTimelineAssetIDs: []
        )
        XCTAssertFalse(form.validationIssues().isEmpty)
        var runtime = MockExamRuntime(form: form)
        XCTAssertThrowsError(try runtime.start())
    }

    func testOpenBackgroundInterruptionIsNotDuplicated() throws {
        let start = Date(timeIntervalSince1970: 1_800_000_000)
        var runtime = MockExamRuntime(form: makeForm(), now: start)
        try runtime.start(now: start)
        runtime.beginInterruption(.background, now: start.addingTimeInterval(2))
        runtime.beginInterruption(.background, now: start.addingTimeInterval(3))
        XCTAssertEqual(runtime.interruptions.count, 1)
        runtime.endInterruption(.background, now: start.addingTimeInterval(4))
        XCTAssertEqual(runtime.interruptions.first?.endedAt, start.addingTimeInterval(4))
    }

    func testFormRejectsMissingRuntimeGroups() {
        let issues = makeForm().contentValidationIssues(groups: [])
        XCTAssertTrue(issues.contains { $0.contains("找不到題組") })
        XCTAssertTrue(issues.contains { $0.contains("題組展開後") })
    }

    private func makeForm() -> MockExamForm {
        let listening = (0..<100).map { "L\($0)" }
        let reading = (0..<100).map { "R\($0)" }
        return .init(
            id: "mock-form-1", contentVersion: "v1", orderedGroupIDs: (1...7).map { "G\($0)" },
            orderedItemIDs: listening + reading, listeningItemIDs: listening, readingItemIDs: reading,
            listeningUnlockOffsetsSeconds: Dictionary(uniqueKeysWithValues: listening.enumerated().map { ($0.element, $0.offset * 10) }),
            listeningDurationSeconds: 2_700, readingTimeLimitSeconds: 4_500,
            audioTimelineAssetIDs: ["timeline-audio"]
        )
    }
}
