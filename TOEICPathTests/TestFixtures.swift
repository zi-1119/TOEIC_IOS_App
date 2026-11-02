import Foundation
@testable import TOEICPath

enum TestFixtures {
    static func formalGroup(
        id: String,
        familyID: String? = nil,
        part: TOEICPart,
        purpose: ContentPurpose,
        difficulty: Difficulty = .d2,
        itemCount: Int = 1,
        version: Int = 1,
        sourceBatchID: String = "test-batch"
    ) -> QuestionGroup {
        let seed = SampleContent.groups.last!.items.first!
        let audioID = part.section == .listening ? "test-audio" : nil
        let items = (0..<itemCount).map { index in
            QuestionItem(
                id: "\(id)-item-\(index)",
                prompt: seed.prompt,
                options: seed.options,
                correctOptionID: seed.correctOptionID,
                explanation: seed.explanation,
                skills: seed.skills,
                transcript: part.section == .listening ? "Test transcript" : nil,
                imageAssetID: part == .part1 ? "test-image" : nil,
                audioAssetID: audioID
            )
        }
        return QuestionGroup(
            id: id,
            version: version,
            sourceBatchID: sourceBatchID,
            familyID: familyID ?? "family-\(id)",
            part: part,
            difficulty: difficulty,
            scenario: "Test \(id)",
            documents: part.rawValue >= 6 ? SampleContent.groups.last!.documents : [],
            items: items,
            audioAssetID: audioID,
            timeLimitSeconds: nil,
            tags: [],
            purpose: purpose,
            contentStatus: .aiChecked,
            fixture: false
        )
    }
}
