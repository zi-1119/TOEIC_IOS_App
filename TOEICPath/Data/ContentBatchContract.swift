import CryptoKit
import Foundation

struct BatchManifest: Codable, Hashable, Sendable {
    struct Producer: Codable, Hashable, Sendable {
        let tool: String
        let model: String

        init(tool: String, model: String) {
            self.tool = tool
            self.model = model
        }

        init(from decoder: Decoder) throws {
            if let value = try? decoder.singleValueContainer().decode(String.self) {
                let marker = " (model: "
                if let range = value.range(of: marker), value.hasSuffix(")") {
                    tool = String(value[..<range.lowerBound])
                    model = String(value[range.upperBound..<value.index(before: value.endIndex)])
                } else {
                    tool = value
                    model = "unknown"
                }
                return
            }
            let container = try decoder.container(keyedBy: CodingKeys.self)
            tool = try container.decode(String.self, forKey: .tool)
            model = try container.decode(String.self, forKey: .model)
        }

        func encode(to encoder: Encoder) throws {
            var container = encoder.singleValueContainer()
            try container.encode("\(tool) (model: \(model))")
        }

        private enum CodingKeys: String, CodingKey { case tool, model }
    }
    struct FileEntry: Codable, Hashable, Sendable {
        let path: String
        let sha256: String
    }
    let schemaVersion: String
    let batchID: String
    let createdAt: Date
    let producer: Producer
    let groupCount: Int
    let itemCount: Int
    let files: [FileEntry]
    enum CodingKeys: String, CodingKey {
        case schemaVersion = "schema_version", batchID = "batch_id", createdAt = "created_at"
        case producer, groupCount = "group_count", itemCount = "item_count", files
    }
}

enum BatchPool: String, Codable, Sendable { case training, battle, diagnostic, mock }
enum BatchLayout: String, Codable, Sendable {
    case photo, questionResponse = "question_response", conversation, talk, sentence, textCompletion = "text_completion"
    case singlePassage = "single_passage", doublePassage = "double_passage", triplePassage = "triple_passage"
}
enum BatchContentStatus: String, Codable, Sendable { case draft, aiChecked = "ai_checked", humanReviewed = "human_reviewed", quarantined, retired }
enum BatchAssetStatus: String, Codable, Sendable { case planned, ready }
enum BatchReviewState: String, Codable, Sendable { case pending, aiChecked = "ai_checked", humanReviewed = "human_reviewed" }

struct BatchDifficulty: Codable, Hashable, Sendable {
    let level: String
    let rationaleZH: String
    let basis: String
    enum CodingKeys: String, CodingKey { case level, rationaleZH = "rationale_zh", basis }
}

struct BatchBlock: Codable, Hashable, Sendable {
    let blockID: String
    let type: String
    let textEN: String?
    let columns: [String]?
    let rows: [[String]]?
    enum CodingKeys: String, CodingKey { case blockID = "block_id", type, textEN = "text_en", columns, rows }
}

struct BatchDocument: Codable, Hashable, Sendable {
    let documentID: String
    let genre: String
    let titleEN: String
    let blocks: [BatchBlock]
    enum CodingKeys: String, CodingKey { case documentID = "document_id", genre, titleEN = "title_en", blocks }
}

struct BatchSpeaker: Codable, Hashable, Sendable {
    let speakerID: String
    let role: String
    let accent: String
    enum CodingKeys: String, CodingKey { case speakerID = "speaker_id", role, accent }
}

struct BatchAudioSegment: Codable, Hashable, Sendable {
    let segmentID: String
    let speakerID: String
    let textEN: String
    enum CodingKeys: String, CodingKey { case segmentID = "segment_id", speakerID = "speaker_id", textEN = "text_en" }
}

struct BatchStimulus: Codable, Hashable, Sendable {
    let documents: [BatchDocument]
    let speakers: [BatchSpeaker]
    let audioScript: [BatchAudioSegment]
    enum CodingKeys: String, CodingKey { case documents, speakers, audioScript = "audio_script" }
}

struct BatchSegmentTime: Codable, Hashable, Sendable {
    let segmentID: String
    let startMS: Int
    let endMS: Int
    enum CodingKeys: String, CodingKey { case segmentID = "segment_id", startMS = "start_ms", endMS = "end_ms" }
}

struct BatchAsset: Codable, Hashable, Sendable {
    let assetID: String
    let kind: String
    let status: BatchAssetStatus
    let path: String?
    let sha256: String?
    let mimeType: String?
    let durationMS: Int?
    let sourceNoteZH: String
    let reviewState: BatchReviewState
    let segmentTimes: [BatchSegmentTime]
    enum CodingKeys: String, CodingKey {
        case assetID = "asset_id", kind, status, path, sha256, mimeType = "mime_type", durationMS = "duration_ms"
        case sourceNoteZH = "source_note_zh", reviewState = "review_state", segmentTimes = "segment_times"
    }
}

struct BatchChoice: Codable, Hashable, Sendable {
    let id: String
    let textEN: String
    enum CodingKeys: String, CodingKey { case id, textEN = "text_en" }
}

struct BatchEvidence: Codable, Hashable, Sendable {
    let sourceType: String
    let sourceID: String
    let quoteEN: String
    let reasoningZH: String
    enum CodingKeys: String, CodingKey {
        case sourceType = "source_type", sourceID = "source_id", quoteEN = "quote_en", reasoningZH = "reasoning_zh"
    }
}

struct BatchDistractorNote: Codable, Hashable, Sendable {
    let choiceID: String
    let reasonZH: String
    enum CodingKeys: String, CodingKey { case choiceID = "choice_id", reasonZH = "reason_zh" }
}

struct BatchVocabulary: Codable, Hashable, Sendable {
    let termEN: String
    let meaningZH: String
    let exampleEN: String
    enum CodingKeys: String, CodingKey { case termEN = "term_en", meaningZH = "meaning_zh", exampleEN = "example_en" }
}

struct BatchItem: Codable, Hashable, Sendable {
    let itemID: String
    let promptEN: String
    let choices: [BatchChoice]
    let answerChoiceID: String
    let skillTags: [String]
    let evidence: [BatchEvidence]
    let explanationZH: String
    let distractorNotes: [BatchDistractorNote]
    let vocabulary: [BatchVocabulary]
    let estimatedTimeSec: Int?
    enum CodingKeys: String, CodingKey {
        case itemID = "item_id", promptEN = "prompt_en", choices, answerChoiceID = "answer_choice_id"
        case skillTags = "skill_tags", evidence, explanationZH = "explanation_zh"
        case distractorNotes = "distractor_notes", vocabulary, estimatedTimeSec = "estimated_time_sec"
    }
}

struct BatchProvenance: Codable, Hashable, Sendable {
    let origin: String
    let authorTool: String
    let authorModel: String
    let createdAt: Date
    let rightsNoteZH: String
    enum CodingKeys: String, CodingKey {
        case origin, authorTool = "author_tool", authorModel = "author_model", createdAt = "created_at", rightsNoteZH = "rights_note_zh"
    }
}

struct BatchGroup: Codable, Hashable, Sendable {
    let schemaVersion: String
    let groupID: String
    let version: Int
    let familyID: String
    let pool: BatchPool
    let fixture: Bool
    let part: Int
    let layout: BatchLayout
    let scenario: String
    let difficulty: BatchDifficulty
    let contentStatus: BatchContentStatus
    let stimulus: BatchStimulus
    let assets: [BatchAsset]
    let items: [BatchItem]
    let provenance: BatchProvenance
    let reviewRefs: [String]
    enum CodingKeys: String, CodingKey {
        case schemaVersion = "schema_version", groupID = "group_id", version, familyID = "family_id", pool, fixture, part, layout, scenario
        case difficulty, contentStatus = "content_status", stimulus, assets, items, provenance, reviewRefs = "review_refs"
    }
}

struct BatchReview: Codable, Hashable, Sendable {
    struct Finding: Codable, Hashable, Sendable {
        let itemID: String?
        let severity: String
        let code: String
        let noteZH: String
        enum CodingKeys: String, CodingKey { case itemID = "item_id", severity, code, noteZH = "note_zh" }
    }
    let reviewID: String
    let groupID: String
    let groupVersion: Int
    let itemIDs: [String]
    let reviewerKind: String
    let reviewerName: String
    let reviewerModel: String?
    let reviewedAt: Date
    let blind: Bool
    let verdict: String
    let findings: [Finding]
    enum CodingKeys: String, CodingKey {
        case reviewID = "review_id", groupID = "group_id", groupVersion = "group_version", itemIDs = "item_ids"
        case reviewerKind = "reviewer_kind", reviewerName = "reviewer_name", reviewerModel = "reviewer_model"
        case reviewedAt = "reviewed_at", blind, verdict, findings
    }
}

struct BatchValidationReport: Codable, Hashable, Sendable {
    struct Validator: Codable, Hashable, Sendable { let name: String; let version: String }
    struct Target: Codable, Hashable, Sendable { let path: String?; let groupID: String?; let itemID: String?; enum CodingKeys: String, CodingKey { case path, groupID = "group_id", itemID = "item_id" } }
    struct Check: Codable, Hashable, Sendable {
        let checkID: String; let category: String; let target: Target; let status: String; let code: String; let messageZH: String; let evidencePaths: [String]
        enum CodingKeys: String, CodingKey { case checkID = "check_id", category, target, status, code, messageZH = "message_zh", evidencePaths = "evidence_paths" }
    }
    struct Counts: Codable, Hashable, Sendable { let pass: Int; let warning: Int; let fail: Int; let notRun: Int; enum CodingKeys: String, CodingKey { case pass, warning, fail, notRun = "not_run" } }
    let reportVersion: String; let contentSchemaVersion: String; let batchID: String; let generatedAt: Date
    let validator: Validator; let profile: String; let checks: [Check]; let counts: Counts; let overallResult: String
    enum CodingKeys: String, CodingKey {
        case reportVersion = "report_version", contentSchemaVersion = "content_schema_version", batchID = "batch_id", generatedAt = "generated_at"
        case validator, profile, checks, counts, overallResult = "overall_result"
    }
}

struct ImportedContentBatch: Sendable {
    let manifest: BatchManifest
    let groups: [BatchGroup]
    let reviews: [BatchReview]
    let validationReport: BatchValidationReport
    let mockFormReport: BatchMockFormReport?
    let issues: ContentValidationReport

    func runtimePackage(rootURL: URL? = nil) -> ContentPackage {
        var runtimeAssets = groups.flatMap(\.assets).filter { $0.status == .ready }.compactMap { asset -> ContentAsset? in
            guard let path = asset.path else { return nil }
            let runtimePath = rootURL?.appending(path: path).path ?? path
            return ContentAsset(id: "\(manifest.batchID)::\(asset.assetID)", kind: asset.kind == "audio" ? .audio : .image, path: runtimePath, checksumSHA256: asset.sha256, durationMilliseconds: asset.durationMS)
        }
        if let rootURL, let mockFormReport {
            runtimeAssets.append(contentsOf: mockFormReport.runtimeAssets(batchID: manifest.batchID, rootURL: rootURL))
        }
        return ContentPackage(
            manifest: .init(schemaVersion: 1, packageID: manifest.batchID, contentVersion: manifest.batchID, locale: "en",
                            createdAt: manifest.createdAt, generator: manifest.producer.tool, generatorVersion: manifest.producer.model,
                            license: "See per-group provenance"),
            assets: Array(Dictionary(runtimeAssets.map { ($0.id, $0) }, uniquingKeysWith: { first, _ in first }).values),
            groups: groups.compactMap { $0.runtimeGroup(batchID: manifest.batchID) }
        )
    }
}

extension BatchGroup {
    func runtimeGroup(batchID: String) -> QuestionGroup? {
        guard let runtimePart = TOEICPart(rawValue: part), let level = Int(difficulty.level.dropFirst()), let runtimeDifficulty = Difficulty(rawValue: level) else { return nil }
        let documents = stimulus.documents.map { document in
            let body = document.blocks.map { block in
                if block.type == "table", let columns = block.columns, let rows = block.rows {
                    return ([columns] + rows).map { $0.joined(separator: " | ") }.joined(separator: "\n")
                }
                return block.textEN ?? ""
            }.joined(separator: "\n\n")
            return StimulusDocument(id: document.documentID, kind: .text, title: document.titleEN.isEmpty ? nil : document.titleEN, body: body, accessibilityLabel: nil)
        }
        let transcript = stimulus.audioScript.enumerated().map { index, segment in
            switch runtimePart {
            case .part1:
                let label = String(UnicodeScalar(65 + index)!)
                return "\(label). \(segment.textEN)"
            case .part2:
                if index == 0 { return "Question: \(segment.textEN)" }
                let label = String(UnicodeScalar(64 + index)!)
                return "\(label). \(segment.textEN)"
            default:
                return segment.textEN
            }
        }.joined(separator: "\n")
        let audioAsset = assets.first(where: { $0.kind == "audio" && $0.status == .ready })
        let audioID = audioAsset.map { "\(batchID)::\($0.assetID)" }
        let scriptByID = Dictionary(uniqueKeysWithValues: stimulus.audioScript.map { ($0.segmentID, $0) })
        let audioSegments = (audioAsset?.segmentTimes ?? []).compactMap { timing -> AudioSegment? in
            guard let script = scriptByID[timing.segmentID] else { return nil }
            return .init(id: timing.segmentID, text: script.textEN, startMilliseconds: timing.startMS, endMilliseconds: timing.endMS)
        }.sorted { $0.startMilliseconds < $1.startMilliseconds }
        let imageID = assets.first(where: { $0.kind == "image" && $0.status == .ready }).map { "\(batchID)::\($0.assetID)" }
        let runtimeItems = items.map { item in
            let evidenceText = item.evidence.map { $0.quoteEN.isEmpty ? $0.reasoningZH : $0.quoteEN }.joined(separator: "\n")
            let distractors = Dictionary(uniqueKeysWithValues: item.distractorNotes.map { ($0.choiceID, $0.reasonZH) })
            return QuestionItem(
                id: item.itemID, prompt: item.promptEN.isEmpty ? nil : item.promptEN,
                options: item.choices.map { .init(id: $0.id, text: $0.textEN) }, correctOptionID: item.answerChoiceID,
                explanation: .init(evidence: evidenceText, zhTW: item.explanationZH, optionNotes: distractors, translation: nil,
                                   vocabulary: item.vocabulary.map { .init(term: $0.termEN, meaning: $0.meaningZH, note: $0.exampleEN) }, takeaway: nil),
                skills: item.skillTags, transcript: transcript.isEmpty ? nil : transcript, imageAssetID: imageID, audioAssetID: audioID
            )
        }
        return QuestionGroup(id: groupID, version: version, sourceBatchID: batchID, familyID: familyID, part: runtimePart, difficulty: runtimeDifficulty, scenario: scenario,
                             documents: documents, items: runtimeItems, audioAssetID: audioID, audioSegments: audioSegments, timeLimitSeconds: nil,
                             tags: [layout.rawValue], purpose: pool.runtimePurpose,
                             contentStatus: contentStatus.runtimeStatus, fixture: fixture)
    }
}

private extension BatchPool {
    var runtimePurpose: ContentPurpose {
        switch self {
        case .training: .training
        case .battle: .battle
        case .diagnostic: .diagnostic
        case .mock: .mock
        }
    }
}

private extension BatchContentStatus {
    var runtimeStatus: RuntimeContentStatus {
        switch self {
        case .draft: .draft
        case .aiChecked: .aiChecked
        case .humanReviewed: .humanReviewed
        case .quarantined: .quarantined
        case .retired: .retired
        }
    }
}
