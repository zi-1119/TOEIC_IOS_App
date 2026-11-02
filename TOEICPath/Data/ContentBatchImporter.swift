import CryptoKit
import Foundation

enum ContentBatchImporter {
    static let schemaVersion = "1.0.0"
    static let allowedSkills: Set<String> = [
        "photo_action", "photo_state_location", "question_function", "direct_response", "indirect_response",
        "main_idea_purpose", "explicit_detail", "paraphrase", "speaker_intent", "next_action", "inference",
        "graphic_integration", "word_form", "verb_form_agreement", "preposition_collocation", "connector_clause",
        "vocabulary_in_context", "reference_cohesion", "sentence_insertion", "cross_document", "conditions_exceptions", "chronology"
    ]

    static func loadAndValidate(directory: URL, fileManager: FileManager = .default) throws -> ImportedContentBatch {
        let decoder = JSONDecoder()
        decoder.dateDecodingStrategy = .iso8601
        let manifestURL = directory.appending(path: "manifest.json")
        let manifest = try decoder.decode(BatchManifest.self, from: Data(contentsOf: manifestURL))

        var packageIssues = verifyFiles(directory: directory, manifest: manifest, fileManager: fileManager)
        let groups: [BatchGroup] = try decodeJSONL(directory.appending(path: "groups.jsonl"), decoder: decoder)
        let reviews: [BatchReview] = try decodeJSONL(directory.appending(path: "reviews.jsonl"), decoder: decoder)
        let report = try decoder.decode(BatchValidationReport.self, from: Data(contentsOf: directory.appending(path: "reports/validation.json")))
        let mockFormsURL = directory.appending(path: "reports/mock-forms.json")
        let mockFormReport = fileManager.fileExists(atPath: mockFormsURL.path)
            ? try decoder.decode(BatchMockFormReport.self, from: Data(contentsOf: mockFormsURL))
            : nil
        packageIssues.append(contentsOf: validate(manifest: manifest, groups: groups, reviews: reviews, report: report).issues)
        if mockFormReport != nil && !manifest.files.contains(where: { $0.path == "reports/mock-forms.json" }) {
            packageIssues.append(.init(severity: .error, path: "reports/mock-forms.json", message: "模考組卷報表必須登錄於 manifest.files"))
        }
        let combined = ContentValidationReport(issues: packageIssues)
        guard combined.isImportable else { throw ImportFailure.validation(combined) }
        return ImportedContentBatch(
            manifest: manifest, groups: groups, reviews: reviews, validationReport: report,
            mockFormReport: mockFormReport, issues: combined
        )
    }

    static func validate(
        manifest: BatchManifest,
        groups: [BatchGroup],
        reviews: [BatchReview],
        report: BatchValidationReport
    ) -> ContentValidationReport {
        var issues: [ValidationIssue] = []
        func issue(_ severity: ValidationIssue.Severity, _ path: String, _ message: String) {
            issues.append(.init(severity: severity, path: path, message: message))
        }

        if manifest.schemaVersion != schemaVersion { issue(.error, "manifest.schema_version", "只支援共用契約 \(schemaVersion)") }
        if !isSafeIdentifier(manifest.batchID) { issue(.error, "manifest.batch_id", "batch_id 只能使用英數、點、底線與連字號，且不可為路徑") }
        if manifest.groupCount != groups.count { issue(.error, "manifest.group_count", "宣告 \(manifest.groupCount)，實際 \(groups.count)") }
        let itemCount = groups.reduce(0) { $0 + $1.items.count }
        if manifest.itemCount != itemCount { issue(.error, "manifest.item_count", "宣告 \(manifest.itemCount)，實際 \(itemCount)") }

        duplicates(groups.map(\.groupID)).forEach { issue(.error, "groups.jsonl", "重複 group_id：\($0)") }
        duplicates(groups.flatMap { $0.items.map(\.itemID) }).forEach { issue(.error, "groups.jsonl", "重複 item_id：\($0)") }
        duplicates(reviews.map(\.reviewID)).forEach { issue(.error, "reviews.jsonl", "重複 review_id：\($0)") }
        let reviewsByID = Dictionary(reviews.map { ($0.reviewID, $0) }, uniquingKeysWith: { first, _ in first })
        let familyPools = Dictionary(grouping: groups, by: \.familyID)
        for (family, members) in familyPools where Set(members.map(\.pool)).count > 1 {
            issue(.error, "groups.jsonl", "family \(family) 跨用途池")
        }

        for (index, group) in groups.enumerated() {
            let path = "groups.jsonl:\(index + 1)"
            if group.schemaVersion != schemaVersion { issue(.error, path, "schema_version 必須為 \(schemaVersion)") }
            if group.version < 1 { issue(.error, path, "version 必須為正整數") }
            if group.fixture && !group.groupID.hasPrefix("cx-") { issue(.error, path, "Codex fixture group_id 必須使用 cx- 前綴") }
            if !(1...7).contains(group.part) { issue(.error, path, "part 必須為 1–7") }
            if group.scenario.isEmpty || group.familyID.isEmpty || group.items.isEmpty { issue(.error, path, "scenario、family_id 與 items 不可為空") }
            if !["D1", "D2", "D3", "D4", "D5"].contains(group.difficulty.level) || group.difficulty.basis != "editorial" {
                issue(.error, path, "difficulty 必須為 D1–D5 且 basis=editorial")
            }
            validateShape(group, path: path, reportProfile: report.profile, issue: issue)

            let speakerIDs = Set(group.stimulus.speakers.map(\.speakerID))
            let segmentIDs = Set(group.stimulus.audioScript.map(\.segmentID))
            duplicates(Array(speakerIDs)).forEach { _ in }
            for segment in group.stimulus.audioScript where !speakerIDs.contains(segment.speakerID) {
                issue(.error, path, "audio segment \(segment.segmentID) 指向不存在的 speaker")
            }
            let blockIDs = Set(group.stimulus.documents.flatMap { $0.blocks.map(\.blockID) })
            let assetIDs = Set(group.assets.map(\.assetID))

            for document in group.stimulus.documents {
                for block in document.blocks {
                    if block.type == "table" {
                        guard let columns = block.columns, !columns.isEmpty, let rows = block.rows,
                              rows.allSatisfy({ $0.count == columns.count }) else {
                            issue(.error, path, "table block \(block.blockID) 的列數與欄數不一致"); continue
                        }
                    } else if block.type != "text" || block.textEN == nil {
                        issue(.error, path, "block \(block.blockID) 必須是合法 text 或 table")
                    }
                }
            }

            for asset in group.assets {
                validateAsset(asset, segmentIDs: segmentIDs, path: path, issue: issue)
            }
            for item in group.items {
                let itemPath = "\(path)/\(item.itemID)"
                let choiceIDs = item.choices.map(\.id)
                let expected = group.part == 2 ? 3 : 4
                if choiceIDs.count != expected || Set(choiceIDs).count != expected { issue(.error, itemPath, "選項必須為 \(expected) 個且 ID 唯一") }
                if !Set(choiceIDs).contains(item.answerChoiceID) { issue(.error, itemPath, "answer_choice_id 不在 choices") }
                if item.skillTags.isEmpty || !Set(item.skillTags).isSubset(of: allowedSkills) { issue(.error, itemPath, "skill_tags 為空或含契約外標籤") }
                if item.evidence.isEmpty || item.explanationZH.isEmpty { issue(.error, itemPath, "evidence 與 explanation_zh 不可為空") }
                let wrongIDs = Set(choiceIDs.filter { $0 != item.answerChoiceID })
                if Set(item.distractorNotes.map(\.choiceID)) != wrongIDs { issue(.error, itemPath, "每個錯誤選項必須恰有一筆 distractor note") }
                for evidence in item.evidence {
                    let valid: Bool
                    switch evidence.sourceType {
                    case "document_block": valid = blockIDs.contains(evidence.sourceID)
                    case "audio_segment": valid = segmentIDs.contains(evidence.sourceID)
                    case "asset": valid = assetIDs.contains(evidence.sourceID)
                    case "item_prompt": valid = evidence.sourceID == item.itemID
                    default: valid = false
                    }
                    if !valid { issue(.error, itemPath, "evidence 指向不存在或不合法的來源 \(evidence.sourceID)") }
                }
                if group.part == 6 {
                    let marker = "[[blank:\(item.itemID)]]"
                    let occurrences = group.stimulus.documents.flatMap(\.blocks).compactMap(\.textEN).reduce(0) { $0 + $1.components(separatedBy: marker).count - 1 }
                    if occurrences != 1 { issue(.error, itemPath, "Part 6 每題必須恰有一個對應 blank marker") }
                }
            }
            for ref in group.reviewRefs {
                guard let review = reviewsByID[ref] else { issue(.error, path, "review_ref \(ref) 不存在"); continue }
                if review.groupID != group.groupID || review.groupVersion != group.version { issue(.error, path, "review_ref \(ref) 的題組或版本不符") }
                if Set(review.itemIDs) != Set(group.items.map(\.itemID)) { issue(.error, path, "review_ref \(ref) 的 item_ids 不完整") }
            }
            let referencedReviews = group.reviewRefs.compactMap { reviewsByID[$0] }
            if group.contentStatus == .humanReviewed && !referencedReviews.contains(where: { $0.reviewerKind == "human" && $0.verdict == "pass" }) {
                issue(.error, path, "human_reviewed 缺少實際 human pass 紀錄")
            }
            if group.contentStatus == .aiChecked && !referencedReviews.contains(where: { $0.reviewerKind == "ai" && $0.verdict == "pass" }) {
                issue(.warning, path, "ai_checked 未連結 AI pass 紀錄")
            }
        }

        validateReport(report, manifest: manifest, issue: issue)
        return ContentValidationReport(issues: issues)
    }

    private static func validateShape(
        _ group: BatchGroup,
        path: String,
        reportProfile: String,
        issue: (ValidationIssue.Severity, String, String) -> Void
    ) {
        let expectedLayout: BatchLayout? = switch group.part {
        case 1: .photo; case 2: .questionResponse; case 3: .conversation; case 4: .talk
        case 5: .sentence; case 6: .textCompletion; case 7: nil; default: nil
        }
        if let expectedLayout, group.layout != expectedLayout { issue(.error, path, "Part \(group.part) layout 必須是 \(expectedLayout.rawValue)") }
        let expectedItems: Int? = switch group.part { case 1, 2, 5: 1; case 3, 4: 3; case 6: 4; default: nil }
        if let expectedItems, group.items.count != expectedItems { issue(.error, path, "Part \(group.part) 必須有 \(expectedItems) 題") }
        if group.part == 7 {
            let documentCount = group.stimulus.documents.count
            let valid = switch group.layout {
            case .singlePassage: documentCount == 1 && (2...4).contains(group.items.count)
            case .doublePassage: documentCount == 2 && group.items.count == 5
            case .triplePassage: documentCount == 3 && group.items.count == 5
            default: false
            }
            if !valid { issue(.error, path, "Part 7 的 layout、文件數與題數不符") }
        }
        if group.part == 3 && Set(group.stimulus.speakers.map(\.role)).count < 2 { issue(.error, path, "Part 3 至少需要兩位對話角色") }
        let readyKinds = Set(group.assets.filter { $0.status == .ready }.map(\.kind))
        if reportProfile == "release" {
            if (1...4).contains(group.part) && !readyKinds.contains("audio") { issue(.error, path, "release 聽力題缺 ready 音訊") }
            if group.part == 1 && !readyKinds.contains("image") { issue(.error, path, "release Part 1 缺 ready 圖片") }
        } else {
            if (1...4).contains(group.part) && !readyKinds.contains("audio") { issue(.warning, path, "authoring 聽力題尚缺 ready 音訊") }
            if group.part == 1 && !readyKinds.contains("image") { issue(.warning, path, "authoring Part 1 尚缺 ready 圖片") }
        }
    }

    private static func validateAsset(
        _ asset: BatchAsset,
        segmentIDs: Set<String>,
        path: String,
        issue: (ValidationIssue.Severity, String, String) -> Void
    ) {
        if asset.status == .planned {
            if asset.path != nil || asset.sha256 != nil || asset.durationMS != nil { issue(.error, path, "planned asset 的 path/hash/duration 必須為 null") }
        } else {
            if asset.path == nil || asset.sha256 == nil || asset.mimeType == nil { issue(.error, path, "ready asset 缺 path/hash/mime_type") }
            if asset.kind == "audio" && (asset.durationMS ?? 0) <= 0 { issue(.error, path, "ready audio 必須有正 duration_ms") }
        }
        for timing in asset.segmentTimes {
            if !segmentIDs.contains(timing.segmentID) || timing.startMS < 0 || timing.endMS <= timing.startMS || (asset.durationMS.map { timing.endMS > $0 } ?? true) {
                issue(.error, path, "segment time \(timing.segmentID) 無效")
            }
        }
    }

    private static func validateReport(
        _ report: BatchValidationReport,
        manifest: BatchManifest,
        issue: (ValidationIssue.Severity, String, String) -> Void
    ) {
        let path = "reports/validation.json"
        if report.reportVersion != schemaVersion || report.contentSchemaVersion != schemaVersion || report.batchID != manifest.batchID {
            issue(.error, path, "validation report 版本或 batch_id 不符")
        }
        if !["authoring", "release"].contains(report.profile) || report.checks.isEmpty { issue(.error, path, "profile 或 checks 無效") }
        if Set(report.checks.map(\.checkID)).count != report.checks.count { issue(.error, path, "check_id 重複") }
        let requiredCategories: Set<String> = ["structure", "references", "uniqueness", "assets", "review_integrity", "content_quality", "package"]
        if !requiredCategories.isSubset(of: Set(report.checks.map(\.category))) { issue(.error, path, "checks 未涵蓋所有必要檢查類別") }
        let actual = (
            report.checks.filter { $0.status == "pass" }.count,
            report.checks.filter { $0.status == "warning" }.count,
            report.checks.filter { $0.status == "fail" }.count,
            report.checks.filter { $0.status == "not_run" }.count
        )
        if actual != (report.counts.pass, report.counts.warning, report.counts.fail, report.counts.notRun) { issue(.error, path, "counts 與 checks 不一致") }
        let derived = actual.2 > 0 ? "fail" : actual.3 > 0 ? "incomplete" : actual.1 > 0 ? "warning" : "pass"
        if report.overallResult != derived { issue(.error, path, "overall_result 應為 \(derived)") }
        if report.overallResult == "fail" { issue(.error, path, "含 fail 的批次不可啟用") }
        if report.profile == "release" && report.overallResult != "pass" { issue(.error, path, "release 匯入必須為 pass") }
    }

    private static func verifyFiles(directory: URL, manifest: BatchManifest, fileManager: FileManager) -> [ValidationIssue] {
        var issues: [ValidationIssue] = []
        let declaredPaths = manifest.files.map(\.path)
        for duplicate in duplicates(declaredPaths) { issues.append(.init(severity: .error, path: "manifest.files", message: "重複路徑 \(duplicate)")) }
        for entry in manifest.files {
            guard isSafeRelativePath(entry.path) else { issues.append(.init(severity: .error, path: "manifest.files", message: "不安全路徑 \(entry.path)")); continue }
            let url = directory.appending(path: entry.path)
            let rootPath = directory.resolvingSymlinksInPath().standardizedFileURL.path + "/"
            let resolvedPath = url.resolvingSymlinksInPath().standardizedFileURL.path
            guard resolvedPath.hasPrefix(rootPath) else { issues.append(.init(severity: .error, path: entry.path, message: "解析後路徑越界")); continue }
            guard fileManager.fileExists(atPath: url.path) else { issues.append(.init(severity: .error, path: entry.path, message: "manifest 檔案不存在")); continue }
            if (try? url.resourceValues(forKeys: [.isSymbolicLinkKey]).isSymbolicLink) == true { issues.append(.init(severity: .error, path: entry.path, message: "不允許 symlink")); continue }
            guard let data = try? Data(contentsOf: url) else { issues.append(.init(severity: .error, path: entry.path, message: "無法讀取檔案")); continue }
            let digest = SHA256.hash(data: data).map { String(format: "%02x", $0) }.joined()
            if digest != entry.sha256.lowercased() { issues.append(.init(severity: .error, path: entry.path, message: "SHA-256 不符")) }
        }
        if declaredPaths.contains("manifest.json") { issues.append(.init(severity: .error, path: "manifest.files", message: "files 不得列 manifest 自身")) }
        let inventoryRoot = directory.resolvingSymlinksInPath().standardizedFileURL
        if let enumerator = fileManager.enumerator(at: inventoryRoot, includingPropertiesForKeys: [.isRegularFileKey, .isSymbolicLinkKey]) {
            let actualPaths = Set(enumerator.compactMap { element -> String? in
                guard let url = element as? URL else { return nil }
                let values = try? url.resourceValues(forKeys: [.isRegularFileKey, .isSymbolicLinkKey])
                let relative = String(url.standardizedFileURL.path.dropFirst(inventoryRoot.path.count + 1))
                if values?.isSymbolicLink == true {
                    issues.append(.init(severity: .error, path: relative, message: "包內不允許 symlink"))
                    return nil
                }
                guard values?.isRegularFile == true else { return nil }
                return relative == "manifest.json" ? nil : relative
            })
            let declared = Set(declaredPaths)
            for path in actualPaths.subtracting(declared).sorted() { issues.append(.init(severity: .error, path: path, message: "檔案未列入 manifest")) }
            for path in declared.subtracting(actualPaths).sorted() { issues.append(.init(severity: .error, path: path, message: "manifest 列出但包內無一般檔案")) }
        }
        return issues
    }

    private static func decodeJSONL<T: Decodable>(_ url: URL, decoder: JSONDecoder) throws -> [T] {
        let text = try String(contentsOf: url, encoding: .utf8)
        return try text.split(whereSeparator: \.isNewline).enumerated().map { index, line in
            do { return try decoder.decode(T.self, from: Data(line.utf8)) }
            catch { throw ImportFailure.invalidJSONL(path: url.lastPathComponent, line: index + 1, underlying: error) }
        }
    }

    private static func isSafeRelativePath(_ path: String) -> Bool {
        guard !path.isEmpty, !path.hasPrefix("/"), !path.contains("\\") else { return false }
        let components = path.split(separator: "/", omittingEmptySubsequences: false)
        return components.allSatisfy { !$0.isEmpty && $0 != "." && $0 != ".." }
    }

    private static func isSafeIdentifier(_ value: String) -> Bool {
        guard !value.isEmpty, value.count <= 128, value != ".", value != ".." else { return false }
        return value.unicodeScalars.allSatisfy {
            CharacterSet.alphanumerics.contains($0) || $0 == "." || $0 == "_" || $0 == "-"
        }
    }

    private static func duplicates(_ values: [String]) -> [String] {
        var seen = Set<String>(), duplicates = Set<String>()
        for value in values where !seen.insert(value).inserted { duplicates.insert(value) }
        return duplicates.sorted()
    }

    enum ImportFailure: LocalizedError {
        case invalidJSONL(path: String, line: Int, underlying: Error)
        case validation(ContentValidationReport)
        var errorDescription: String? {
            switch self {
            case .invalidJSONL(let path, let line, let error): "\(path) 第 \(line) 行不是合法契約資料：\(error.localizedDescription)"
            case .validation(let report): "批次驗證失敗：\n" + report.errors.prefix(10).map { "\($0.path)：\($0.message)" }.joined(separator: "\n")
            }
        }
    }
}
