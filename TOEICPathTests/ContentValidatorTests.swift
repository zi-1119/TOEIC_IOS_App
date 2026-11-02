import XCTest
@testable import TOEICPath

final class ContentValidatorTests: XCTestCase {
    func testBundledPreviewHasNoBlockingValidationErrors() {
        let report = ContentValidator.validate(SampleContent.package)
        XCTAssertTrue(report.errors.isEmpty, report.errors.map(\.message).joined(separator: "\n"))
    }

    func testRejectsCorrectAnswerOutsideOptions() {
        let original = SampleContent.groups[4]
        let badItem = QuestionItem(
            id: original.items[0].id, prompt: original.items[0].prompt, options: original.items[0].options,
            correctOptionID: "Z", explanation: original.items[0].explanation, skills: [], transcript: nil,
            imageAssetID: nil, audioAssetID: nil
        )
        let badGroup = QuestionGroup(
            id: original.id, familyID: original.familyID, part: original.part, difficulty: original.difficulty,
            scenario: original.scenario, documents: original.documents, items: [badItem], audioAssetID: nil,
            timeLimitSeconds: nil, tags: []
        )
        let package = ContentPackage(manifest: SampleContent.package.manifest, assets: [], groups: [badGroup])
        XCTAssertTrue(ContentValidator.validate(package).errors.contains { $0.path.contains("correctOptionID") })
    }
}
