import XCTest
@testable import TOEICPath

final class QuickTestEngineTests: XCTestCase {
    func testBlankDisplayUsesGroupOrderInBothPassageAndPromptWithoutChangingSource() {
        let passage = "Open [[blank:second-id]] then [[blank:first-id]]."
        let ids = ["first-id", "second-id"]
        XCTAssertEqual(QuestionDisplayText.render(passage, itemIDs: ids), "Open (2) ____ then (1) ____.")
        XCTAssertEqual(QuestionDisplayText.render("Fill [[blank:second-id]].", itemIDs: ids), "Fill (2) ____.")
        XCTAssertEqual(passage, "Open [[blank:second-id]] then [[blank:first-id]].")
    }

    func testBlankDisplayLeavesOrdinaryTextAndDoesNotExposeUnknownIDs() {
        XCTAssertEqual(QuestionDisplayText.render("Choose ____.", itemIDs: []), "Choose ____.")
        XCTAssertEqual(QuestionDisplayText.render("Fill [[blank:unknown]].", itemIDs: []), "Fill ____.")
    }

    func testAssemblyUsesOnlyCompleteApprovedTrainingGroupsAndKeepsWholeGroups() {
        let training = (0..<12).map {
            TestFixtures.formalGroup(id: "training-\($0)", part: .part5, purpose: .training)
        }
        let diagnostic = TestFixtures.formalGroup(id: "diagnostic", part: .part5, purpose: .diagnostic)
        let battle = TestFixtures.formalGroup(id: "battle", part: .part5, purpose: .battle)
        let mock = TestFixtures.formalGroup(id: "mock", part: .part5, purpose: .mock)
        let fixture = QuestionGroup(
            id: "fixture", familyID: "fixture-family", part: .part5, difficulty: .d2,
            scenario: "fixture", documents: [], items: training[0].items, audioAssetID: nil,
            timeLimitSeconds: nil, tags: [], purpose: .training, contentStatus: .aiChecked, fixture: true
        )
        let all = training + [diagnostic, battle, mock, fixture]
        let assembly = QuickTestAssembler.assemble(
            from: all,
            focus: .reading,
            level: .foundation,
            profile: LocalProfile(),
            materialCompleteGroupIDs: Set(all.map(\.id)),
            targetItemCount: 10
        )

        XCTAssertEqual(assembly.actualItemCount, 10)
        XCTAssertTrue(assembly.isExactTarget)
        XCTAssertEqual(Set(assembly.groups.map(\.familyID)).count, assembly.groups.count)
        XCTAssertTrue(assembly.groups.allSatisfy {
            $0.purpose == .training && !$0.fixture && $0.contentStatus?.isApprovedForFormalUse == true
        })
        XCTAssertEqual(assembly.groups.flatMap(\.items).count, assembly.actualItemCount)
    }

    func testAssemblyTruthfullyReducesCountRatherThanSplittingOrRepeatingGroups() {
        let groups = [
            TestFixtures.formalGroup(id: "four-a", part: .part6, purpose: .training, itemCount: 4),
            TestFixtures.formalGroup(id: "four-b", part: .part6, purpose: .training, itemCount: 4),
            TestFixtures.formalGroup(id: "three", part: .part7, purpose: .training, itemCount: 3),
        ]
        let assembly = QuickTestAssembler.assemble(
            from: groups,
            focus: .reading,
            level: .foundation,
            profile: LocalProfile(),
            materialCompleteGroupIDs: Set(groups.map(\.id)),
            targetItemCount: 10
        )

        XCTAssertEqual(assembly.actualItemCount, 8)
        XCTAssertFalse(assembly.isExactTarget)
        XCTAssertEqual(Set(assembly.groups.map(\.id)).count, assembly.groups.count)
        XCTAssertTrue(assembly.groups.allSatisfy { groups.contains($0) })
    }

    func testAssemblyPrioritizesUnseenFamiliesAndFiltersMissingListeningMaterial() {
        let seen = TestFixtures.formalGroup(id: "seen", part: .part2, purpose: .training)
        let ready = TestFixtures.formalGroup(id: "ready", part: .part3, purpose: .training, itemCount: 3)
        let missing = TestFixtures.formalGroup(id: "missing", part: .part4, purpose: .training, itemCount: 3)
        var profile = LocalProfile()
        profile.recordExposure(group: seen, itemID: seen.items[0].id, mode: .practice)

        let assembly = QuickTestAssembler.assemble(
            from: [seen, ready, missing],
            focus: .listening,
            level: .challenge,
            profile: profile,
            materialCompleteGroupIDs: [seen.id, ready.id],
            targetItemCount: 4
        )

        XCTAssertEqual(Set(assembly.groups.map(\.id)), Set([ready.id, seen.id]))
        XCTAssertFalse(assembly.groups.contains(where: { $0.id == missing.id }))
        XCTAssertEqual(assembly.reviewGroupIDs, [seen.id])
    }

    func testResultIsUnavailableBeforeSubmissionAndAccurateAfterSubmission() {
        let group = TestFixtures.formalGroup(id: "result", part: .part5, purpose: .training, itemCount: 2)
        let sessionID = UUID()
        let start = Date(timeIntervalSince1970: 100)
        let responses = group.items.enumerated().map { index, item in
            ItemResponse(
                id: UUID(), sessionID: sessionID, groupID: group.id, groupVersion: group.version,
                sourceBatchID: group.sourceBatchID, itemID: item.id, part: group.part,
                difficulty: group.difficulty, familyID: group.familyID,
                selectedOptionID: index == 0 ? item.correctOptionID : "wrong",
                isCorrect: index == 0, answeredAt: start.addingTimeInterval(Double(index + 1)),
                elapsedMilliseconds: 1_000, condition: AnswerCondition()
            )
        }

        XCTAssertNil(QuickTestScoring.result(
            responses: responses,
            expectedItemCount: 2,
            startedAt: start,
            submittedAt: nil
        ))
        let result = QuickTestScoring.result(
            responses: responses,
            expectedItemCount: 2,
            startedAt: start,
            submittedAt: start.addingTimeInterval(65)
        )
        XCTAssertEqual(result?.correctCount, 1)
        XCTAssertEqual(result?.totalCount, 2)
        XCTAssertEqual(result?.accuracy, 0.5)
        XCTAssertEqual(result?.elapsedSeconds, 65)
        XCTAssertEqual(result?.incorrectItemIDs, [group.items[1].id])
    }

    func testPreferenceAndExposurePersistAndNextAssemblyMovesToNewFamilies() throws {
        let directory = FileManager.default.temporaryDirectory
            .appending(path: "TOEICPathQuickTest-\(UUID().uuidString)", directoryHint: .isDirectory)
        addTeardownBlock { try? FileManager.default.removeItem(at: directory) }
        let store = LocalProfileStore(fileURL: directory.appending(path: "profile.json"))
        let groups = (0..<20).map {
            TestFixtures.formalGroup(id: "group-\($0)", part: .part5, purpose: .training)
        }
        var profile = LocalProfile()
        profile.preferences.quickTestFocus = .mixed
        profile.preferences.quickTestLevel = .challenge
        let first = QuickTestAssembler.assemble(
            from: groups,
            focus: .reading,
            level: .foundation,
            profile: profile,
            materialCompleteGroupIDs: Set(groups.map(\.id))
        )
        for group in first.groups {
            profile.recordExposure(group: group, itemID: group.items[0].id, mode: .practice)
        }
        try store.save(profile)

        let reopened = store.load()
        XCTAssertEqual(reopened.preferences.quickTestFocus, .mixed)
        XCTAssertEqual(reopened.preferences.quickTestLevel, .challenge)
        let second = QuickTestAssembler.assemble(
            from: groups,
            focus: .reading,
            level: .foundation,
            profile: reopened,
            materialCompleteGroupIDs: Set(groups.map(\.id))
        )
        XCTAssertTrue(Set(first.groups.map(\.familyID)).isDisjoint(with: Set(second.groups.map(\.familyID))))
    }

    func testLegacyPreferencesDefaultToReadingFoundation() throws {
        let legacy = Data(#"{"dailyMinutes":40,"target":"test","notificationsEnabled":true,"messagePreviewEnabled":false,"hasCompletedOnboarding":true}"#.utf8)
        let decoded = try JSONDecoder().decode(UserPreferences.self, from: legacy)
        XCTAssertEqual(decoded.quickTestFocus, .reading)
        XCTAssertEqual(decoded.quickTestLevel, .foundation)
        XCTAssertEqual(decoded.dailyMinutes, 40)
    }

    @MainActor
    func testFinishingQuickPracticePersistsMistakesBeforeTheirReviewDueDate() throws {
        let directory = FileManager.default.temporaryDirectory
            .appending(path: "TOEICPathQuickTestFinish-\(UUID().uuidString)", directoryHint: .isDirectory)
        addTeardownBlock { try? FileManager.default.removeItem(at: directory) }
        let profileURL = directory.appending(path: "profile.json")
        let store = LocalProfileStore(fileURL: profileURL)
        let group = TestFixtures.formalGroup(id: "saved-mistake", part: .part5, purpose: .training)
        let model = AppModel(
            store: store,
            contentStore: ContentVersionStore(rootURL: directory.appending(path: "Content")),
            bundledSeedRootURL: nil,
            backend: LocalBackendClient(hub: LocalBackendHub(storeURL: directory.appending(path: "backend.json")))
        )
        try model.beginSession(groups: [group], mode: .practice)
        let item = try XCTUnwrap(group.items.first)
        let response = ItemResponse(
            id: UUID(), sessionID: try XCTUnwrap(model.activeSession?.id),
            groupID: group.id, groupVersion: group.version, sourceBatchID: group.sourceBatchID,
            itemID: item.id, part: group.part, difficulty: group.difficulty, familyID: group.familyID,
            selectedOptionID: "wrong", isCorrect: false, answeredAt: .now,
            elapsedMilliseconds: 500, condition: AnswerCondition()
        )

        model.finishSession(responses: [response])
        let reopened = store.load()
        XCTAssertTrue(reopened.dueItemIDs.contains(item.id))
        XCTAssertEqual(reopened.sessions.last?.responses.first?.itemID, item.id)
        XCTAssertNotNil(reopened.reviewStates[item.id])
        XCTAssertGreaterThan(reopened.reviewStates[item.id]?.nextReviewAt ?? .distantPast, .now)
    }
}
