import XCTest
@testable import TOEICPath

final class MockFormContractTests: XCTestCase {
    func testValidAdditiveReportResolvesExactTwoHundredItemForm() throws {
        let fixture = makeFixture()
        let resolved = try MockFormContractResolver.resolve(fixture.contexts, mediaDurationProbe: { _ in 300_000 })

        let form = try XCTUnwrap(resolved.first)
        XCTAssertEqual(resolved.count, 1)
        XCTAssertEqual(form.form.orderedItemIDs.count, 200)
        XCTAssertEqual(form.form.listeningItemIDs.count, 100)
        XCTAssertEqual(form.form.readingItemIDs.count, 100)
        XCTAssertEqual(form.form.revision, 3)
        XCTAssertEqual(form.form.groupReferences.count, fixture.groups.count)
        XCTAssertEqual(form.form.audioTimelineAssetIDs, ["batch-form::timeline-1"])
        XCTAssertEqual(form.groups.flatMap(\.items).count, 200)
        XCTAssertTrue(form.form.validationIssues().isEmpty)
        XCTAssertTrue(form.form.contentValidationIssues(groups: form.groups).isEmpty)
    }

    func testMissingRequiredBatchRejectsEntireMockCatalog() {
        let fixture = makeFixture(requiredBatchID: "not-installed")
        XCTAssertThrowsError(try MockFormContractResolver.resolve(fixture.contexts, mediaDurationProbe: { _ in 300_000 })) { error in
            guard case MockFormContractError.invalid(let failures) = error else {
                return XCTFail("unexpected error: \(error)")
            }
            XCTAssertTrue(failures.contains { $0.contains("缺少必要批次 not-installed") })
        }
    }

    func testFormPackageCannotSelfReferenceItsOwnManifestHash() {
        let fixture = makeFixture(requiredBatchID: "batch-form")
        XCTAssertThrowsError(try MockFormContractResolver.resolve(fixture.contexts, mediaDurationProbe: { _ in 300_000 })) { error in
            guard case MockFormContractError.invalid(let failures) = error else {
                return XCTFail("unexpected error: \(error)")
            }
            XCTAssertTrue(failures.contains { $0.contains("不得在 required_batches 自我引用") })
        }
    }

    func testDecodedTimelineDurationMustMatchWithinOneHundredMilliseconds() {
        let fixture = makeFixture()
        XCTAssertThrowsError(try MockFormContractResolver.resolve(fixture.contexts, mediaDurationProbe: { _ in 300_101 })) { error in
            guard case MockFormContractError.invalid(let failures) = error else {
                return XCTFail("unexpected error: \(error)")
            }
            XCTAssertTrue(failures.contains { $0.contains("相差超過 100 毫秒") })
        }
    }

    func testFormalFormRejectsFixtureOrNonReviewedMockGroups() {
        for (fixtureFlag, status) in [(true, BatchContentStatus.humanReviewed), (false, .aiChecked)] {
            let fixture = makeFixture(groupFixture: fixtureFlag, groupStatus: status)
            XCTAssertThrowsError(try MockFormContractResolver.resolve(fixture.contexts, mediaDurationProbe: { _ in 300_000 })) { error in
                guard case MockFormContractError.invalid(let failures) = error else {
                    return XCTFail("unexpected error: \(error)")
                }
                XCTAssertTrue(failures.contains { $0.contains("fixture=false 且 human_reviewed") })
            }
        }
    }

    func testWrongGroupVersionAndManifestHashAreRejected() {
        let wrongVersion = makeFixture(groupVersionOffset: 1)
        XCTAssertThrowsError(try MockFormContractResolver.resolve(wrongVersion.contexts, mediaDurationProbe: { _ in 300_000 })) { error in
            guard case MockFormContractError.invalid(let failures) = error else { return XCTFail("unexpected error: \(error)") }
            XCTAssertTrue(failures.contains { $0.contains("找不到題組") })
        }
        let wrongHash = makeFixture(requiredManifestHash: String(repeating: "d", count: 64))
        XCTAssertThrowsError(try MockFormContractResolver.resolve(wrongHash.contexts, mediaDurationProbe: { _ in 300_000 })) { error in
            guard case MockFormContractError.invalid(let failures) = error else { return XCTFail("unexpected error: \(error)") }
            XCTAssertTrue(failures.contains { $0.contains("manifest 雜湊不符") })
        }
    }

    func testSecondBasedReadingLimitAndMissingAudioAreRejected() {
        let secondsMistake = makeFixture(readingTimeLimitMS: 4_500)
        XCTAssertThrowsError(try MockFormContractResolver.resolve(secondsMistake.contexts, mediaDurationProbe: { _ in 300_000 }))
        let fixture = makeFixture()
        XCTAssertThrowsError(try MockFormContractResolver.resolve(fixture.contexts, mediaDurationProbe: { _ in
            throw CocoaError(.fileReadNoSuchFile)
        })) { error in
            guard case MockFormContractError.invalid(let failures) = error else { return XCTFail("unexpected error: \(error)") }
            XCTAssertTrue(failures.contains { $0.contains("整卷音檔無法解碼") })
        }
    }

    func testUnlockAndTimelineFailuresAreRejected() {
        for mutation in [TimelineMutation.missingUnlock, .duplicateUnlock, .backwardUnlock, .outOfBounds] {
            let fixture = makeFixture(timelineMutation: mutation)
            XCTAssertThrowsError(try MockFormContractResolver.resolve(fixture.contexts, mediaDurationProbe: { _ in 300_000 }), "mutation \(mutation) must fail")
        }
    }

    func testTimelineAssetMustBeInsideItsFormDirectory() {
        let fixture = makeFixture(assetPath: "assets/mock/another-form/timeline.m4a")
        XCTAssertThrowsError(try MockFormContractResolver.resolve(fixture.contexts, mediaDurationProbe: { _ in 300_000 })) { error in
            guard case MockFormContractError.invalid(let failures) = error else { return XCTFail("unexpected error: \(error)") }
            XCTAssertTrue(failures.contains { $0.contains("assets/mock/form-1/") })
        }
    }

    private func makeFixture(
        requiredBatchID: String = "batch-source",
        requiredManifestHash: String = String(repeating: "a", count: 64),
        groupFixture: Bool = false,
        groupStatus: BatchContentStatus = .humanReviewed,
        groupVersionOffset: Int = 0,
        readingTimeLimitMS: Int = 4_500_000,
        assetPath: String = "assets/mock/form-1/timeline.m4a",
        timelineMutation: TimelineMutation = .none
    ) -> (contexts: [MockFormContractResolver.BatchContext], groups: [BatchGroup]) {
        var groups: [BatchGroup] = []
        func append(part: Int, layout: BatchLayout, itemCounts: [Int]) {
            for count in itemCounts {
                let ordinal = groups.filter { $0.part == part }.count + 1
                groups.append(makeGroup(
                    part: part, layout: layout, ordinal: ordinal, itemCount: count,
                    fixture: groupFixture, status: groupStatus
                ))
            }
        }
        append(part: 1, layout: .photo, itemCounts: Array(repeating: 1, count: 6))
        append(part: 2, layout: .questionResponse, itemCounts: Array(repeating: 1, count: 25))
        append(part: 3, layout: .conversation, itemCounts: Array(repeating: 3, count: 13))
        append(part: 4, layout: .talk, itemCounts: Array(repeating: 3, count: 10))
        append(part: 5, layout: .sentence, itemCounts: Array(repeating: 1, count: 30))
        append(part: 6, layout: .textCompletion, itemCounts: Array(repeating: 4, count: 4))
        append(part: 7, layout: .singlePassage, itemCounts: Array(repeating: 3, count: 9) + [2])
        append(part: 7, layout: .doublePassage, itemCounts: Array(repeating: 5, count: 5))

        let allIDs = groups.flatMap { $0.items.map(\.itemID) }
        let listeningIDs = groups.filter { $0.part <= 4 }.flatMap { $0.items.map(\.itemID) }
        let readingIDs = groups.filter { $0.part >= 5 }.flatMap { $0.items.map(\.itemID) }
        XCTAssertEqual(allIDs.count, 200)
        XCTAssertEqual(listeningIDs.count, 100)
        XCTAssertEqual(readingIDs.count, 100)

        var events: [BatchMockFormReport.Timeline.Event] = [
            .init(sequence: 0, kind: .directions, startMS: 0, endMS: 50, itemIDs: [])
        ]
        var sequence = 1
        let partByItem = Dictionary(uniqueKeysWithValues: groups.flatMap { group in
            group.items.map { ($0.itemID, group.part) }
        })
        for (index, itemID) in listeningIDs.enumerated() {
            let base = 100 + index * 3_000
            events.append(.init(sequence: sequence, kind: .itemUnlock, startMS: base, endMS: base, itemIDs: [itemID]))
            sequence += 1
            events.append(.init(sequence: sequence, kind: .stimulus, startMS: base + 100, endMS: base + 800, itemIDs: [itemID]))
            sequence += 1
            if partByItem[itemID] == 1 || partByItem[itemID] == 2 {
                events.append(.init(sequence: sequence, kind: .responseOptions, startMS: base + 800, endMS: base + 1_600, itemIDs: [itemID]))
                sequence += 1
            }
            events.append(.init(sequence: sequence, kind: .responseWindow, startMS: base + 1_600, endMS: base + 2_500, itemIDs: [itemID]))
            sequence += 1
        }
        switch timelineMutation {
        case .none:
            break
        case .missingUnlock:
            if let index = events.lastIndex(where: { $0.kind == .itemUnlock }) { events.remove(at: index) }
        case .duplicateUnlock:
            let last = listeningIDs.last!
            events.append(.init(sequence: sequence, kind: .itemUnlock, startMS: 299_999, endMS: 299_999, itemIDs: [last]))
        case .backwardUnlock:
            if let index = events.firstIndex(where: { $0.kind == .itemUnlock }) {
                let event = events[index]
                events[index] = .init(sequence: event.sequence, kind: event.kind, startMS: 299_999, endMS: 299_999, itemIDs: event.itemIDs)
            }
        case .outOfBounds:
            if let index = events.lastIndex(where: { $0.kind == .responseWindow }) {
                let event = events[index]
                events[index] = .init(sequence: event.sequence, kind: event.kind, startMS: event.startMS, endMS: 300_001, itemIDs: event.itemIDs)
            }
        }

        let manifestHash = String(repeating: "a", count: 64)
        let assetHash = String(repeating: "b", count: 64)
        let asset = BatchMockFormReport.Asset(
            assetID: "timeline-1", kind: "mock_audio_timeline", path: assetPath,
            sha256: assetHash, mimeType: "audio/mp4", durationMS: 300_000, reviewState: .humanReviewed
        )
        let report = BatchMockFormReport(
            formSchemaVersion: "1.0.0", contentSchemaVersion: "1.0.0",
            contentSet: .init(
                contentSetID: "set-1",
                requiredBatches: [.init(batchID: requiredBatchID, manifestSHA256: requiredManifestHash)]
            ),
            assets: [asset],
            forms: [.init(
                formID: "form-1", revision: 3,
                groupRefs: groups.map { .init(groupID: $0.groupID, version: $0.version + groupVersionOffset, sourceBatchID: "batch-source") },
                orderedItemIDs: allIDs, listeningItemIDs: listeningIDs, readingItemIDs: readingIDs,
                listeningTimeline: .init(assetID: asset.assetID, durationMS: asset.durationMS, events: events),
                readingTimeLimitMS: readingTimeLimitMS
            )]
        )
        let sourceManifest = BatchManifest(
            schemaVersion: "1.0.0", batchID: "batch-source", createdAt: .now,
            producer: .init(tool: "tests", model: "none"), groupCount: groups.count, itemCount: allIDs.count,
            files: []
        )
        let formManifest = BatchManifest(
            schemaVersion: "1.0.0", batchID: "batch-form", createdAt: .now,
            producer: .init(tool: "tests", model: "none"), groupCount: 0, itemCount: 0,
            files: [.init(path: asset.path, sha256: assetHash)]
        )
        let sourceContext = MockFormContractResolver.BatchContext(
            manifest: sourceManifest, manifestSHA256: manifestHash, groups: groups, report: nil,
            rootURL: URL(fileURLWithPath: "/tmp/mock-source-fixture")
        )
        let formContext = MockFormContractResolver.BatchContext(
            manifest: formManifest, manifestSHA256: String(repeating: "c", count: 64), groups: [], report: report,
            rootURL: URL(fileURLWithPath: "/tmp/mock-form-fixture")
        )
        return ([sourceContext, formContext], groups)
    }

    private enum TimelineMutation {
        case none, missingUnlock, duplicateUnlock, backwardUnlock, outOfBounds
    }

    private func makeGroup(
        part: Int, layout: BatchLayout, ordinal: Int, itemCount: Int,
        fixture: Bool, status: BatchContentStatus
    ) -> BatchGroup {
        let groupID = "mock-p\(part)-g\(ordinal)"
        let items = (1...itemCount).map { index -> BatchItem in
            let itemID = "mock-p\(part)-g\(ordinal)-i\(index)"
            return .init(
                itemID: itemID, promptEN: "Question", choices: ["A", "B", "C", "D"].map { .init(id: $0, textEN: $0) },
                answerChoiceID: "A", skillTags: ["explicit_detail"],
                evidence: [.init(sourceType: "item_prompt", sourceID: itemID, quoteEN: "Question", reasoningZH: "測試")],
                explanationZH: "測試", distractorNotes: ["B", "C", "D"].map { .init(choiceID: $0, reasonZH: "測試") },
                vocabulary: [], estimatedTimeSec: 20
            )
        }
        return BatchGroup(
            schemaVersion: "1.0.0", groupID: groupID, version: 1, familyID: "family-\(groupID)", pool: .mock,
            fixture: fixture, part: part, layout: layout, scenario: "mock",
            difficulty: .init(level: "D3", rationaleZH: "測試", basis: "editorial"), contentStatus: status,
            stimulus: .init(documents: [], speakers: [], audioScript: []), assets: [], items: items,
            provenance: .init(origin: "original", authorTool: "tests", authorModel: "none", createdAt: .now, rightsNoteZH: "測試"),
            reviewRefs: []
        )
    }
}
