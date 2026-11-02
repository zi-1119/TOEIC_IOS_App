import Foundation

enum MockExamPhase: String, Codable, Sendable {
    case notStarted, listening, sectionBreak, reading, submitted, expired
}

enum MockSubmissionState: String, Codable, Sendable {
    case localOnly, submitting, confirmed, failed
}

struct MockAnswerRecord: Codable, Hashable, Sendable {
    var selectedOptionID: String
    var firstAnsweredAt: Date
    var lastChangedAt: Date
    var changeCount: Int
    var elapsedSectionMilliseconds: Int
    var condition: AnswerCondition
}

struct MockExamInterruption: Identifiable, Codable, Hashable, Sendable {
    enum Kind: String, Codable, Sendable { case background, audioInterruption, routeChange }
    let id: UUID
    let kind: Kind
    let beganAt: Date
    var endedAt: Date?
}

struct MockExamGroupReference: Codable, Hashable, Sendable {
    let groupID: String
    let version: Int
    let sourceBatchID: String
}

struct MockExamForm: Identifiable, Codable, Hashable, Sendable {
    let id: String
    let contentVersion: String
    let orderedGroupIDs: [String]
    let orderedItemIDs: [String]
    let listeningItemIDs: [String]
    let readingItemIDs: [String]
    let listeningUnlockOffsetsSeconds: [String: Int]
    let listeningDurationSeconds: Int
    let listeningUnlockOffsetsMilliseconds: [String: Int]
    let listeningDurationMilliseconds: Int
    let readingTimeLimitSeconds: Int
    let audioTimelineAssetIDs: [String]
    let revision: Int
    let groupReferences: [MockExamGroupReference]
    let audioTimelineChecksumSHA256: String?

    init(
        id: String,
        contentVersion: String,
        orderedGroupIDs: [String],
        orderedItemIDs: [String],
        listeningItemIDs: [String],
        readingItemIDs: [String],
        listeningUnlockOffsetsSeconds: [String: Int],
        listeningDurationSeconds: Int,
        readingTimeLimitSeconds: Int,
        audioTimelineAssetIDs: [String],
        revision: Int = 1,
        groupReferences: [MockExamGroupReference] = [],
        audioTimelineChecksumSHA256: String? = nil,
        listeningUnlockOffsetsMilliseconds: [String: Int]? = nil,
        listeningDurationMilliseconds: Int? = nil
    ) {
        self.id = id
        self.contentVersion = contentVersion
        self.orderedGroupIDs = orderedGroupIDs
        self.orderedItemIDs = orderedItemIDs
        self.listeningItemIDs = listeningItemIDs
        self.readingItemIDs = readingItemIDs
        self.listeningUnlockOffsetsSeconds = listeningUnlockOffsetsSeconds
        self.listeningDurationSeconds = listeningDurationSeconds
        self.listeningUnlockOffsetsMilliseconds = listeningUnlockOffsetsMilliseconds
            ?? listeningUnlockOffsetsSeconds.mapValues { $0 * 1_000 }
        self.listeningDurationMilliseconds = listeningDurationMilliseconds ?? listeningDurationSeconds * 1_000
        self.readingTimeLimitSeconds = readingTimeLimitSeconds
        self.audioTimelineAssetIDs = audioTimelineAssetIDs
        self.revision = revision
        self.groupReferences = groupReferences
        self.audioTimelineChecksumSHA256 = audioTimelineChecksumSHA256
    }

    private enum CodingKeys: String, CodingKey {
        case id, contentVersion, orderedGroupIDs, orderedItemIDs, listeningItemIDs, readingItemIDs
        case listeningUnlockOffsetsSeconds, listeningDurationSeconds, listeningUnlockOffsetsMilliseconds, listeningDurationMilliseconds
        case readingTimeLimitSeconds, audioTimelineAssetIDs
        case revision, groupReferences, audioTimelineChecksumSHA256
    }

    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        id = try container.decode(String.self, forKey: .id)
        contentVersion = try container.decode(String.self, forKey: .contentVersion)
        orderedGroupIDs = try container.decode([String].self, forKey: .orderedGroupIDs)
        orderedItemIDs = try container.decode([String].self, forKey: .orderedItemIDs)
        listeningItemIDs = try container.decode([String].self, forKey: .listeningItemIDs)
        readingItemIDs = try container.decode([String].self, forKey: .readingItemIDs)
        listeningUnlockOffsetsSeconds = try container.decode([String: Int].self, forKey: .listeningUnlockOffsetsSeconds)
        listeningDurationSeconds = try container.decode(Int.self, forKey: .listeningDurationSeconds)
        listeningUnlockOffsetsMilliseconds = try container.decodeIfPresent([String: Int].self, forKey: .listeningUnlockOffsetsMilliseconds)
            ?? listeningUnlockOffsetsSeconds.mapValues { $0 * 1_000 }
        listeningDurationMilliseconds = try container.decodeIfPresent(Int.self, forKey: .listeningDurationMilliseconds)
            ?? listeningDurationSeconds * 1_000
        readingTimeLimitSeconds = try container.decode(Int.self, forKey: .readingTimeLimitSeconds)
        audioTimelineAssetIDs = try container.decode([String].self, forKey: .audioTimelineAssetIDs)
        revision = try container.decodeIfPresent(Int.self, forKey: .revision) ?? 1
        groupReferences = try container.decodeIfPresent([MockExamGroupReference].self, forKey: .groupReferences) ?? []
        audioTimelineChecksumSHA256 = try container.decodeIfPresent(String.self, forKey: .audioTimelineChecksumSHA256)
    }

    func validationIssues() -> [String] {
        var issues: [String] = []
        if orderedItemIDs.count != MockExamBlueprint.standard.totalItems { issues.append("完整模考必須恰有 200 題") }
        if Set(orderedItemIDs).count != orderedItemIDs.count { issues.append("orderedItemIDs 不可重複") }
        if listeningItemIDs.count != 100 || readingItemIDs.count != 100 { issues.append("聽力與閱讀必須各 100 題") }
        if orderedItemIDs != listeningItemIDs + readingItemIDs { issues.append("題目順序必須先聽力、後閱讀") }
        if Set(listeningUnlockOffsetsMilliseconds.keys) != Set(listeningItemIDs) { issues.append("每道聽力題都必須有時間線解鎖點") }
        let offsets = listeningItemIDs.compactMap { listeningUnlockOffsetsMilliseconds[$0] }
        if offsets != offsets.sorted() || offsets.contains(where: { $0 < 0 || $0 > listeningDurationMilliseconds }) {
            issues.append("聽力時間線解鎖點必須遞增且位於音訊長度內")
        }
        if listeningDurationMilliseconds <= 0 || readingTimeLimitSeconds != 75 * 60 { issues.append("播放長度須為正；閱讀固定 75 分鐘") }
        if audioTimelineAssetIDs.count != 1 { issues.append("首版正式模考必須有一個已合成的固定播放時間線素材") }
        if revision < 1 { issues.append("模考 revision 必須為正整數") }
        if !groupReferences.isEmpty && groupReferences.map(\.groupID) != orderedGroupIDs {
            issues.append("題組版本參照順序必須與 orderedGroupIDs 一致")
        }
        return issues
    }

    func contentValidationIssues(groups: [QuestionGroup]) -> [String] {
        var issues: [String] = []
        if contentVersion.isEmpty { issues.append("模考表單必須指定題庫版本") }
        if Set(orderedGroupIDs).count != orderedGroupIDs.count { issues.append("orderedGroupIDs 不可重複") }

        let groupsByID = Dictionary(uniqueKeysWithValues: groups.map { ($0.id, $0) })
        let missingGroupIDs = orderedGroupIDs.filter { groupsByID[$0] == nil }
        if !missingGroupIDs.isEmpty { issues.append("找不到題組：\(missingGroupIDs.joined(separator: ", "))") }

        let resolved = orderedGroupIDs.compactMap { groupsByID[$0] }
        let resolvedItemIDs = resolved.flatMap(\.items).map(\.id)
        if resolvedItemIDs != orderedItemIDs { issues.append("題組展開後的題目與表單順序不一致") }

        let repeatedFamilies = Dictionary(grouping: resolved, by: \.familyID).filter { $0.value.count > 1 }.keys.sorted()
        if !repeatedFamilies.isEmpty { issues.append("正式模考不可重複題目家族：\(repeatedFamilies.joined(separator: ", "))") }

        if !groupReferences.isEmpty {
            for reference in groupReferences {
                guard let group = groupsByID[reference.groupID] else { continue }
                if group.version != reference.version || group.sourceBatchID != reference.sourceBatchID {
                    issues.append("題組 \(reference.groupID) 必須使用 v\(reference.version) @ \(reference.sourceBatchID)")
                }
            }
        }

        let actualCounts = Dictionary(grouping: resolved, by: \.part).mapValues { $0.flatMap(\.items).count }
        for part in TOEICPart.allCases where actualCounts[part, default: 0] != MockExamBlueprint.standard.counts[part, default: 0] {
            issues.append("\(part.shortTitle) 題數應為 \(MockExamBlueprint.standard.counts[part, default: 0])，目前為 \(actualCounts[part, default: 0])")
        }
        return issues
    }
}

struct MockExamRuntime: Codable, Hashable, Sendable {
    let sessionID: UUID
    let form: MockExamForm
    var phase: MockExamPhase
    var selectedOptionIDs: [String: String]
    var answerRecords: [String: MockAnswerRecord]
    var currentItemID: String?
    var sectionStartedAt: Date?
    var sectionDeadline: Date?
    var lastSavedAt: Date
    var interruptions: [MockExamInterruption]
    var submissionState: MockSubmissionState

    init(sessionID: UUID = UUID(), form: MockExamForm, now: Date = .now) {
        self.sessionID = sessionID
        self.form = form
        self.phase = .notStarted
        self.selectedOptionIDs = [:]
        self.answerRecords = [:]
        self.currentItemID = form.orderedItemIDs.first
        self.sectionStartedAt = nil
        self.sectionDeadline = nil
        self.lastSavedAt = now
        self.interruptions = []
        self.submissionState = .localOnly
    }

    mutating func start(now: Date = .now) throws {
        guard phase == .notStarted else { throw RuntimeError.invalidTransition }
        let issues = form.validationIssues()
        guard issues.isEmpty else { throw RuntimeError.invalidForm(issues) }
        phase = .listening
        sectionStartedAt = now
        sectionDeadline = now.addingTimeInterval(TimeInterval(form.listeningDurationMilliseconds) / 1_000)
        currentItemID = form.listeningItemIDs.first
        lastSavedAt = now
    }

    mutating func select(
        optionID: String,
        for itemID: String,
        condition: AnswerCondition = AnswerCondition(),
        now: Date = .now
    ) throws {
        updateForTime(now)
        guard phase == .listening || phase == .reading,
              availableItemIDs(at: now).contains(itemID) else { throw RuntimeError.itemUnavailable }
        selectedOptionIDs[itemID] = optionID
        let elapsed = max(0, Int(now.timeIntervalSince(sectionStartedAt ?? now) * 1_000))
        if var record = answerRecords[itemID] {
            if record.selectedOptionID != optionID { record.changeCount += 1 }
            record.selectedOptionID = optionID
            record.lastChangedAt = now
            record.elapsedSectionMilliseconds = elapsed
            record.condition = condition
            answerRecords[itemID] = record
        } else {
            answerRecords[itemID] = .init(
                selectedOptionID: optionID, firstAnsweredAt: now, lastChangedAt: now,
                changeCount: 0, elapsedSectionMilliseconds: elapsed, condition: condition
            )
        }
        lastSavedAt = now
    }

    mutating func navigate(to itemID: String, now: Date = .now) throws {
        updateForTime(now)
        guard availableItemIDs(at: now).contains(itemID) else { throw RuntimeError.itemUnavailable }
        currentItemID = itemID
        lastSavedAt = now
    }

    mutating func updateForTime(_ now: Date = .now) {
        guard let deadline = sectionDeadline, now >= deadline else { return }
        switch phase {
        case .listening:
            phase = .sectionBreak
            currentItemID = nil
            sectionStartedAt = nil
            sectionDeadline = nil
        case .reading:
            phase = .expired
            currentItemID = nil
            sectionStartedAt = nil
            sectionDeadline = nil
            submissionState = .localOnly
        default: break
        }
        lastSavedAt = now
    }

    mutating func beginReading(now: Date = .now) throws {
        guard phase == .sectionBreak else { throw RuntimeError.invalidTransition }
        phase = .reading
        sectionStartedAt = now
        sectionDeadline = now.addingTimeInterval(TimeInterval(form.readingTimeLimitSeconds))
        currentItemID = form.readingItemIDs.first
        lastSavedAt = now
    }

    mutating func submit(now: Date = .now) throws {
        updateForTime(now)
        guard phase == .reading || phase == .expired else { throw RuntimeError.invalidTransition }
        phase = .submitted
        currentItemID = nil
        sectionStartedAt = nil
        sectionDeadline = nil
        submissionState = .localOnly
        lastSavedAt = now
    }

    mutating func beginInterruption(_ kind: MockExamInterruption.Kind, now: Date = .now) {
        guard phase == .listening || phase == .reading else { return }
        guard !interruptions.contains(where: { $0.kind == kind && $0.endedAt == nil }) else { return }
        interruptions.append(.init(id: UUID(), kind: kind, beganAt: now, endedAt: nil))
        lastSavedAt = now
    }

    mutating func endInterruption(_ kind: MockExamInterruption.Kind, now: Date = .now) {
        guard let index = interruptions.lastIndex(where: { $0.kind == kind && $0.endedAt == nil }) else { return }
        interruptions[index].endedAt = now
        lastSavedAt = now
        updateForTime(now)
    }

    func availableItemIDs(at now: Date = .now) -> [String] {
        switch phase {
        case .listening:
            guard let start = sectionStartedAt else { return [] }
            let elapsed = max(0, Int(now.timeIntervalSince(start) * 1_000))
            return form.listeningItemIDs.filter { form.listeningUnlockOffsetsMilliseconds[$0, default: .max] <= elapsed }
        case .reading: return form.readingItemIDs
        default: return []
        }
    }

    func remainingSeconds(at now: Date = .now) -> Int? {
        guard let deadline = sectionDeadline else { return nil }
        return max(0, Int(ceil(deadline.timeIntervalSince(now))))
    }

    enum RuntimeError: LocalizedError {
        case invalidTransition
        case invalidForm([String])
        case itemUnavailable
        var errorDescription: String? {
            switch self {
            case .invalidTransition: "目前狀態不允許這個操作。"
            case .invalidForm(let issues): "模考表單無效：\(issues.joined(separator: "、"))"
            case .itemUnavailable: "這題尚未由聽力時間線解鎖，或不在目前區段。"
            }
        }
    }
}
