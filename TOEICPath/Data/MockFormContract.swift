import CryptoKit
import Foundation
import AVFoundation

struct BatchMockFormReport: Codable, Hashable, Sendable {
    struct ContentSet: Codable, Hashable, Sendable {
        struct RequiredBatch: Codable, Hashable, Sendable {
            let batchID: String
            let manifestSHA256: String

            enum CodingKeys: String, CodingKey {
                case batchID = "batch_id"
                case manifestSHA256 = "manifest_sha256"
            }
        }

        let contentSetID: String
        let requiredBatches: [RequiredBatch]

        enum CodingKeys: String, CodingKey {
            case contentSetID = "content_set_id"
            case requiredBatches = "required_batches"
        }
    }

    struct Asset: Codable, Hashable, Sendable {
        let assetID: String
        let kind: String
        let path: String
        let sha256: String
        let mimeType: String
        let durationMS: Int
        let reviewState: BatchReviewState

        enum CodingKeys: String, CodingKey {
            case assetID = "asset_id"
            case kind, path, sha256
            case mimeType = "mime_type"
            case durationMS = "duration_ms"
            case reviewState = "review_state"
        }
    }

    struct GroupReference: Codable, Hashable, Sendable {
        let groupID: String
        let version: Int
        let sourceBatchID: String

        enum CodingKeys: String, CodingKey {
            case groupID = "group_id"
            case version
            case sourceBatchID = "source_batch_id"
        }
    }

    struct Timeline: Codable, Hashable, Sendable {
        struct Event: Codable, Hashable, Sendable {
            enum Kind: String, Codable, Sendable {
                case directions
                case itemUnlock = "item_unlock"
                case stimulus
                case responseOptions = "response_options"
                case responseWindow = "response_window"
                case pause

                var carriesAudio: Bool {
                    self == .directions || self == .stimulus || self == .responseOptions
                }
            }

            let sequence: Int
            let kind: Kind
            let startMS: Int
            let endMS: Int
            let itemIDs: [String]

            enum CodingKeys: String, CodingKey {
                case sequence, kind
                case startMS = "start_ms"
                case endMS = "end_ms"
                case itemIDs = "item_ids"
            }
        }

        let assetID: String
        let durationMS: Int
        let events: [Event]

        enum CodingKeys: String, CodingKey {
            case assetID = "asset_id"
            case durationMS = "duration_ms"
            case events
        }
    }

    struct Form: Codable, Hashable, Sendable {
        let formID: String
        let revision: Int
        let groupRefs: [GroupReference]
        let orderedItemIDs: [String]
        let listeningItemIDs: [String]
        let readingItemIDs: [String]
        let listeningTimeline: Timeline
        let readingTimeLimitMS: Int

        enum CodingKeys: String, CodingKey {
            case formID = "form_id"
            case revision
            case groupRefs = "group_refs"
            case orderedItemIDs = "ordered_item_ids"
            case listeningItemIDs = "listening_item_ids"
            case readingItemIDs = "reading_item_ids"
            case listeningTimeline = "listening_timeline"
            case readingTimeLimitMS = "reading_time_limit_ms"
        }
    }

    let formSchemaVersion: String
    let contentSchemaVersion: String
    let contentSet: ContentSet
    let assets: [Asset]
    let forms: [Form]

    enum CodingKeys: String, CodingKey {
        case formSchemaVersion = "form_schema_version"
        case contentSchemaVersion = "content_schema_version"
        case contentSet = "content_set"
        case assets, forms
    }
}

struct ResolvedMockExamForm: Hashable, Sendable {
    let form: MockExamForm
    let groups: [QuestionGroup]
}

struct InstalledContentCatalog: Sendable {
    let package: ContentPackage
    let mockForms: [ResolvedMockExamForm]
}

enum MockFormContractResolver {
    typealias MediaDurationProbe = (URL) throws -> Int

    struct BatchContext: Sendable {
        let manifest: BatchManifest
        let manifestSHA256: String
        let groups: [BatchGroup]
        let report: BatchMockFormReport?
        let rootURL: URL
    }

    static func resolve(
        _ batches: [BatchContext],
        mediaDurationProbe: MediaDurationProbe = decodedAudioDurationMilliseconds(at:)
    ) throws -> [ResolvedMockExamForm] {
        let manifests = Dictionary(uniqueKeysWithValues: batches.map { ($0.manifest.batchID, $0.manifestSHA256) })
        let groupKeys = batches.flatMap { batch in
            batch.groups.map { group in
                (key: groupKey(group.groupID, group.version, batch.manifest.batchID), group: group)
            }
        }
        let groups = Dictionary(uniqueKeysWithValues: groupKeys.map { ($0.key, $0.group) })

        var failures: [String] = []
        var resolved: [ResolvedMockExamForm] = []
        var identities = Set<String>()
        var usedGroupIDs = Set<String>()
        var usedFamilyIDs = Set<String>()

        for owner in batches {
            guard let report = owner.report else { continue }
            let reportPath = "\(owner.manifest.batchID)/reports/mock-forms.json"
            if report.formSchemaVersion != "1.0.0" || report.contentSchemaVersion != ContentBatchImporter.schemaVersion {
                failures.append("\(reportPath)：版本必須為 1.0.0")
            }
            if report.contentSet.contentSetID.isEmpty || report.contentSet.requiredBatches.isEmpty {
                failures.append("\(reportPath)：content_set 與 required_batches 不可為空")
            }
            let requiredBatchIDs = report.contentSet.requiredBatches.map(\.batchID)
            if Set(requiredBatchIDs).count != requiredBatchIDs.count {
                failures.append("\(reportPath)：required_batches 不可重複")
            }
            if requiredBatchIDs.contains(owner.manifest.batchID) {
                failures.append("\(reportPath)：表單包不得在 required_batches 自我引用；請先發布來源題庫包")
            }
            for required in report.contentSet.requiredBatches {
                guard isSHA256(required.manifestSHA256) else {
                    failures.append("\(reportPath)：\(required.batchID) 的 manifest_sha256 格式無效")
                    continue
                }
                guard let installedHash = manifests[required.batchID] else {
                    failures.append("\(reportPath)：缺少必要批次 \(required.batchID)")
                    continue
                }
                if installedHash != required.manifestSHA256.lowercased() {
                    failures.append("\(reportPath)：必要批次 \(required.batchID) 的 manifest 雜湊不符")
                }
            }

            let declaredFiles = Dictionary(uniqueKeysWithValues: owner.manifest.files.map { ($0.path, $0.sha256.lowercased()) })
            let assetsByID = Dictionary(report.assets.map { ($0.assetID, $0) }, uniquingKeysWith: { first, _ in first })
            if assetsByID.count != report.assets.count {
                failures.append("\(reportPath)：asset_id 不可重複")
            }
            for asset in report.assets {
                validate(asset: asset, reportPath: reportPath, declaredFiles: declaredFiles, failures: &failures)
            }

            for wireForm in report.forms {
                let identity = "\(wireForm.formID)@\(wireForm.revision)"
                let formPath = "\(reportPath)/\(identity)"
                guard identities.insert(identity).inserted else {
                    failures.append("\(formPath)：form_id + revision 重複")
                    continue
                }
                if wireForm.formID.isEmpty || wireForm.revision < 1 {
                    failures.append("\(formPath)：form_id 不可為空且 revision 必須為正整數")
                }

                var exactGroups: [BatchGroup] = []
                for ref in wireForm.groupRefs {
                    if !requiredBatchIDs.contains(ref.sourceBatchID) {
                        failures.append("\(formPath)：題組來源批次 \(ref.sourceBatchID) 未列入 required_batches")
                    }
                    let key = groupKey(ref.groupID, ref.version, ref.sourceBatchID)
                    guard let group = groups[key] else {
                        failures.append("\(formPath)：找不到題組 \(ref.groupID) v\(ref.version) @ \(ref.sourceBatchID)")
                        continue
                    }
                    exactGroups.append(group)
                }
                guard exactGroups.count == wireForm.groupRefs.count else { continue }

                let localGroupIDs = Set(exactGroups.map(\.groupID))
                let localFamilyIDs = Set(exactGroups.map(\.familyID))
                if localGroupIDs.count != exactGroups.count || localFamilyIDs.count != exactGroups.count {
                    failures.append("\(formPath)：同一表單不可重複題組或題目家族")
                }
                if !usedGroupIDs.isDisjoint(with: localGroupIDs) || !usedFamilyIDs.isDisjoint(with: localFamilyIDs) {
                    failures.append("\(formPath)：正式表單之間不可共用題組或題目家族")
                }
                if exactGroups.contains(where: {
                    $0.pool != .mock || $0.fixture || $0.contentStatus != .humanReviewed
                }) {
                    failures.append("\(formPath)：所有題組必須是 mock pool、fixture=false 且 human_reviewed")
                }

                let expandedIDs = exactGroups.flatMap { $0.items.map(\.itemID) }
                let formIssueStart = failures.count
                validate(form: wireForm, groups: exactGroups, expandedIDs: expandedIDs, asset: assetsByID[wireForm.listeningTimeline.assetID], path: formPath, failures: &failures)
                if let timelineAsset = assetsByID[wireForm.listeningTimeline.assetID] {
                    if !timelineAsset.path.hasPrefix("assets/mock/\(wireForm.formID)/") {
                        failures.append("\(formPath)：整卷音檔必須登錄在 assets/mock/\(wireForm.formID)/")
                    }
                    do {
                        let decodedDuration = try mediaDurationProbe(owner.rootURL.appending(path: timelineAsset.path))
                        if abs(decodedDuration - timelineAsset.durationMS) > 100 {
                            failures.append("\(formPath)：解碼音檔長度與 duration_ms 相差超過 100 毫秒")
                        }
                    } catch {
                        failures.append("\(formPath)：整卷音檔無法解碼：\(error.localizedDescription)")
                    }
                }

                let runtimeGroups = zip(wireForm.groupRefs, exactGroups).compactMap { ref, group in
                    group.runtimeGroup(batchID: ref.sourceBatchID)
                }
                if runtimeGroups.count != exactGroups.count {
                    failures.append("\(formPath)：題組無法轉換成 App 執行格式")
                }
                guard failures.count == formIssueStart,
                      let timelineAsset = assetsByID[wireForm.listeningTimeline.assetID] else { continue }

                let unlockOffsetsMilliseconds = Dictionary(uniqueKeysWithValues: wireForm.listeningTimeline.events
                    .filter { $0.kind == .itemUnlock }
                    .flatMap { event in event.itemIDs.map { ($0, event.startMS) } })
                let unlockOffsetsSeconds = unlockOffsetsMilliseconds.mapValues { $0 / 1_000 }
                let groupReferences = wireForm.groupRefs.map {
                    MockExamGroupReference(groupID: $0.groupID, version: $0.version, sourceBatchID: $0.sourceBatchID)
                }
                let runtimeForm = MockExamForm(
                    id: wireForm.formID,
                    contentVersion: report.contentSet.contentSetID,
                    orderedGroupIDs: wireForm.groupRefs.map(\.groupID),
                    orderedItemIDs: wireForm.orderedItemIDs,
                    listeningItemIDs: wireForm.listeningItemIDs,
                    readingItemIDs: wireForm.readingItemIDs,
                    listeningUnlockOffsetsSeconds: unlockOffsetsSeconds,
                    listeningDurationSeconds: wireForm.listeningTimeline.durationMS / 1_000,
                    readingTimeLimitSeconds: wireForm.readingTimeLimitMS / 1_000,
                    audioTimelineAssetIDs: ["\(owner.manifest.batchID)::\(timelineAsset.assetID)"],
                    revision: wireForm.revision,
                    groupReferences: groupReferences,
                    audioTimelineChecksumSHA256: timelineAsset.sha256.lowercased(),
                    listeningUnlockOffsetsMilliseconds: unlockOffsetsMilliseconds,
                    listeningDurationMilliseconds: wireForm.listeningTimeline.durationMS
                )
                resolved.append(.init(form: runtimeForm, groups: runtimeGroups))
                usedGroupIDs.formUnion(localGroupIDs)
                usedFamilyIDs.formUnion(localFamilyIDs)
            }
        }

        guard failures.isEmpty else { throw MockFormContractError.invalid(failures) }
        return resolved.sorted { ($0.form.id, $0.form.revision) < ($1.form.id, $1.form.revision) }
    }

    private static func validate(
        asset: BatchMockFormReport.Asset,
        reportPath: String,
        declaredFiles: [String: String],
        failures: inout [String]
    ) {
        let path = "\(reportPath)/assets/\(asset.assetID)"
        if asset.assetID.isEmpty || asset.kind != "mock_audio_timeline" || asset.durationMS <= 0 {
            failures.append("\(path)：必須是具正播放長度的 mock_audio_timeline")
        }
        if !asset.path.hasPrefix("assets/mock/") || asset.path.hasPrefix("/") || asset.path.split(separator: "/").contains("..") {
            failures.append("\(path)：素材必須位於 assets/mock/<form_id>/ 且不得越界")
        }
        if !isSHA256(asset.sha256) || declaredFiles[asset.path] != asset.sha256.lowercased() {
            failures.append("\(path)：素材 SHA-256 必須與 manifest 登錄一致")
        }
        if !asset.mimeType.hasPrefix("audio/") || asset.reviewState != .humanReviewed {
            failures.append("\(path)：正式時間線必須是 human_reviewed 音訊")
        }
    }

    private static func validate(
        form: BatchMockFormReport.Form,
        groups: [BatchGroup],
        expandedIDs: [String],
        asset: BatchMockFormReport.Asset?,
        path: String,
        failures: inout [String]
    ) {
        if expandedIDs != form.orderedItemIDs {
            failures.append("\(path)：group_refs 展開順序必須完全等於 ordered_item_ids")
        }
        if form.orderedItemIDs.count != 200 || Set(form.orderedItemIDs).count != 200 {
            failures.append("\(path)：正式模考必須恰有 200 個唯一題目")
        }
        if form.listeningItemIDs.count != 100 || form.readingItemIDs.count != 100 ||
            form.orderedItemIDs != form.listeningItemIDs + form.readingItemIDs {
            failures.append("\(path)：必須先列 100 題聽力，再列 100 題閱讀")
        }
        let actualCounts = Dictionary(grouping: groups, by: \.part).mapValues { $0.flatMap(\.items).count }
        let expectedCounts = [1: 6, 2: 25, 3: 39, 4: 30, 5: 30, 6: 16, 7: 54]
        for (part, expected) in expectedCounts where actualCounts[part, default: 0] != expected {
            failures.append("\(path)：Part \(part) 必須有 \(expected) 題")
        }
        let part7 = groups.filter { $0.part == 7 }
        let singleCount = part7.filter { $0.layout == .singlePassage }.flatMap(\.items).count
        let multipleCount = part7.filter { $0.layout == .doublePassage || $0.layout == .triplePassage }.flatMap(\.items).count
        if singleCount != 29 || multipleCount != 25 {
            failures.append("\(path)：Part 7 必須是 29 題單篇與 25 題多篇")
        }
        if form.readingTimeLimitMS != 4_500_000 {
            failures.append("\(path)：閱讀時限必須是 4,500,000 毫秒")
        }
        guard let asset else {
            failures.append("\(path)：找不到 listening_timeline.asset_id")
            return
        }
        if asset.durationMS != form.listeningTimeline.durationMS {
            failures.append("\(path)：報表素材與時間線的 duration_ms 必須一致")
        }

        let timeline = form.listeningTimeline
        let sequences = timeline.events.map(\.sequence)
        if sequences != sequences.sorted() || Set(sequences).count != sequences.count {
            failures.append("\(path)：時間線 sequence 必須嚴格遞增且唯一")
        }
        for event in timeline.events {
            let validDuration = event.kind == .itemUnlock ? event.endMS == event.startMS : event.endMS > event.startMS
            if event.startMS < 0 || event.startMS >= timeline.durationMS || event.endMS > timeline.durationMS || !validDuration {
                failures.append("\(path)：時間線事件 \(event.sequence) 的時間範圍無效")
            }
            if !Set(event.itemIDs).isSubset(of: Set(form.listeningItemIDs)) {
                failures.append("\(path)：時間線事件 \(event.sequence) 指向非聽力題")
            }
        }
        let audioEvents = timeline.events.filter(\.kind.carriesAudio).sorted { $0.startMS < $1.startMS }
        for pair in zip(audioEvents, audioEvents.dropFirst()) where pair.0.endMS > pair.1.startMS {
            failures.append("\(path)：帶音訊的時間線事件不可重疊")
            break
        }
        let unlocks = timeline.events.filter { $0.kind == .itemUnlock }.flatMap { event in
            event.itemIDs.map { (id: $0, offset: event.startMS) }
        }
        if unlocks.map(\.id) != form.listeningItemIDs || Set(unlocks.map(\.id)).count != 100 {
            failures.append("\(path)：每道聽力題必須依 listening_item_ids 順序恰好解鎖一次")
        }
        if unlocks.map(\.offset) != unlocks.map(\.offset).sorted() {
            failures.append("\(path)：聽力解鎖時間不可倒退")
        }
        let partsByItem = Dictionary(uniqueKeysWithValues: groups.flatMap { group in group.items.map { ($0.itemID, group.part) } })
        if !timeline.events.contains(where: { $0.kind == .directions }) {
            failures.append("\(path)：聽力時間線必須包含 directions")
        }
        let responseWindowItems = Set(timeline.events.filter { $0.kind == .responseWindow }.flatMap(\.itemIDs))
        if !Set(form.listeningItemIDs).isSubset(of: responseWindowItems) {
            failures.append("\(path)：每道聽力題都必須有 authored response_window")
        }
        let responseOptionItems = Set(timeline.events.filter { $0.kind == .responseOptions }.flatMap(\.itemIDs))
        let needsSpokenOptions = Set(form.listeningItemIDs.filter { partsByItem[$0] == 1 || partsByItem[$0] == 2 })
        if !needsSpokenOptions.isSubset(of: responseOptionItems) {
            failures.append("\(path)：Part 1–2 每題都必須有 response_options 音訊事件")
        }
    }

    private static func groupKey(_ id: String, _ version: Int, _ batchID: String) -> String {
        "\(batchID)\u{1f}\(id)\u{1f}\(version)"
    }

    private static func isSHA256(_ value: String) -> Bool {
        value.count == 64 && value.lowercased().allSatisfy { $0.isHexDigit }
    }
}

private func decodedAudioDurationMilliseconds(at url: URL) throws -> Int {
    let file = try AVAudioFile(forReading: url)
    guard file.processingFormat.sampleRate > 0 else {
        throw MockFormMediaError.invalidSampleRate
    }
    return Int((Double(file.length) / file.processingFormat.sampleRate * 1_000).rounded())
}

private enum MockFormMediaError: LocalizedError {
    case invalidSampleRate
    var errorDescription: String? { "音訊 sample rate 無效" }
}

enum MockFormContractError: LocalizedError {
    case invalid([String])

    var errorDescription: String? {
        switch self {
        case .invalid(let failures):
            "模考組卷驗證失敗：\n" + failures.prefix(12).joined(separator: "\n")
        }
    }
}

extension BatchMockFormReport {
    func runtimeAssets(batchID: String, rootURL: URL) -> [ContentAsset] {
        assets.map {
            ContentAsset(
                id: "\(batchID)::\($0.assetID)", kind: .audio,
                path: rootURL.appending(path: $0.path).path,
                checksumSHA256: $0.sha256.lowercased(), durationMilliseconds: $0.durationMS
            )
        }
    }
}

private extension Digest {
    var mockFormHex: String { map { String(format: "%02x", $0) }.joined() }
}

func manifestSHA256(at rootURL: URL) throws -> String {
    SHA256.hash(data: try Data(contentsOf: rootURL.appending(path: "manifest.json"))).mockFormHex
}
