import XCTest
@testable import TOEICPath

final class ContentBatchImporterTests: XCTestCase {
    func testValidContractFixturePassesStructuralValidation() {
        let group = makeGroup(id: "cx-g-p5-0001", family: "family-a", pool: .training)
        let review = makeReview(group: group)
        let manifest = makeManifest(groups: [group])
        let result = ContentBatchImporter.validate(manifest: manifest, groups: [group], reviews: [review], report: makeReport(batchID: manifest.batchID))
        XCTAssertTrue(result.errors.isEmpty, result.errors.map(\.message).joined(separator: "\n"))
    }

    func testFamilyCannotCrossPurposePools() {
        let first = makeGroup(id: "cx-g-p5-0001", family: "family-a", pool: .training)
        let second = makeGroup(id: "cx-g-p5-0002", family: "family-a", pool: .battle)
        let reviews = [makeReview(group: first), makeReview(group: second)]
        let manifest = makeManifest(groups: [first, second])
        let result = ContentBatchImporter.validate(manifest: manifest, groups: [first, second], reviews: reviews, report: makeReport(batchID: manifest.batchID))
        XCTAssertTrue(result.errors.contains { $0.message.contains("跨用途池") })
    }

    private func makeManifest(groups: [BatchGroup]) -> BatchManifest {
        .init(schemaVersion: "1.0.0", batchID: "batch-test", createdAt: .now,
              producer: .init(tool: "test", model: "none"), groupCount: groups.count,
              itemCount: groups.flatMap(\.items).count, files: [])
    }

    private func makeGroup(id: String, family: String, pool: BatchPool) -> BatchGroup {
        let itemID = "\(id)-q1"
        let choices = ["A", "B", "C", "D"].map { BatchChoice(id: $0, textEN: $0) }
        let item = BatchItem(
            itemID: itemID, promptEN: "The report is _____ complete.", choices: choices,
            answerChoiceID: "A", skillTags: ["word_form"],
            evidence: [.init(sourceType: "item_prompt", sourceID: itemID, quoteEN: "is _____ complete", reasoningZH: "此處需要副詞。")],
            explanationZH: "A 是唯一符合句構的選項。",
            distractorNotes: [
                .init(choiceID: "B", reasonZH: "詞性不符"), .init(choiceID: "C", reasonZH: "詞性不符"), .init(choiceID: "D", reasonZH: "詞性不符")
            ], vocabulary: [], estimatedTimeSec: 25
        )
        return BatchGroup(
            schemaVersion: "1.0.0", groupID: id, version: 1, familyID: family, pool: pool, fixture: true,
            part: 5, layout: .sentence, scenario: "office_reporting",
            difficulty: .init(level: "D2", rationaleZH: "常見詞性辨識", basis: "editorial"), contentStatus: .aiChecked,
            stimulus: .init(documents: [], speakers: [], audioScript: []), assets: [], items: [item],
            provenance: .init(origin: "original", authorTool: "test", authorModel: "none", createdAt: .now, rightsNoteZH: "測試 fixture"),
            reviewRefs: ["review-\(id)"]
        )
    }

    private func makeReview(group: BatchGroup) -> BatchReview {
        .init(reviewID: "review-\(group.groupID)", groupID: group.groupID, groupVersion: group.version,
              itemIDs: group.items.map(\.itemID), reviewerKind: "program", reviewerName: "tests", reviewerModel: nil,
              reviewedAt: .now, blind: false, verdict: "pass", findings: [])
    }

    private func makeReport(batchID: String) -> BatchValidationReport {
        let categories = ["structure", "references", "uniqueness", "assets", "review_integrity", "content_quality", "package"]
        let checks = categories.enumerated().map { index, category in
            BatchValidationReport.Check(checkID: "\(category)-\(index)", category: category,
                                        target: .init(path: "groups.jsonl", groupID: nil, itemID: nil), status: "pass",
                                        code: "fixture", messageZH: "測試", evidencePaths: [])
        }
        return .init(reportVersion: "1.0.0", contentSchemaVersion: "1.0.0", batchID: batchID, generatedAt: .now,
              validator: .init(name: "tests", version: "1"), profile: "authoring",
              checks: checks, counts: .init(pass: checks.count, warning: 0, fail: 0, notRun: 0), overallResult: "pass")
    }
}
