import Foundation

/// Presentation only: keep content IDs intact in the imported source package.
enum QuestionDisplayText {
    static func render(_ text: String, itemIDs: [String]) -> String {
        var result = text
        for (index, id) in itemIDs.enumerated() {
            result = result.replacingOccurrences(of: "[[blank:\(id)]]", with: "(\(index + 1)) ____")
        }
        return result.replacingOccurrences(
            of: #"\[\[blank:[^\]]+\]\]"#, with: "____", options: .regularExpression
        )
    }
}

enum TOEICSection: String, Codable, CaseIterable, Sendable {
    case listening
    case reading

    var title: String { self == .listening ? "聽力" : "閱讀" }
}

enum TOEICPart: Int, Codable, CaseIterable, Identifiable, Sendable {
    case part1 = 1, part2, part3, part4, part5, part6, part7

    var id: Int { rawValue }
    var section: TOEICSection { rawValue <= 4 ? .listening : .reading }
    var shortTitle: String { "Part \(rawValue)" }

    var title: String {
        switch self {
        case .part1: "照片描述"
        case .part2: "應答問題"
        case .part3: "簡短對話"
        case .part4: "簡短獨白"
        case .part5: "句子填空"
        case .part6: "段落填空"
        case .part7: "閱讀理解"
        }
    }

    var symbol: String {
        switch self {
        case .part1: "photo"
        case .part2: "ear"
        case .part3: "person.2.wave.2"
        case .part4: "waveform"
        case .part5: "textformat.abc"
        case .part6: "doc.text"
        case .part7: "doc.on.doc"
        }
    }
}

enum Difficulty: Int, Codable, CaseIterable, Comparable, Sendable {
    case d1 = 1, d2, d3, d4, d5

    static func < (lhs: Difficulty, rhs: Difficulty) -> Bool { lhs.rawValue < rhs.rawValue }
    var label: String { "D\(rawValue)" }
}

enum ContentPurpose: String, Codable, CaseIterable, Sendable {
    case training, battle, diagnostic, mock
}

enum RuntimeContentStatus: String, Codable, Sendable {
    case draft
    case aiChecked = "ai_checked"
    case humanReviewed = "human_reviewed"
    case quarantined
    case retired

    var isApprovedForFormalUse: Bool {
        self == .aiChecked || self == .humanReviewed
    }
}

struct AnswerOption: Identifiable, Codable, Hashable, Sendable {
    let id: String
    let text: String
}

struct Explanation: Codable, Hashable, Sendable {
    let evidence: String
    let zhTW: String
    let optionNotes: [String: String]
    let translation: String?
    let vocabulary: [VocabularyItem]
    let takeaway: String?
}

struct VocabularyItem: Identifiable, Codable, Hashable, Sendable {
    let term: String
    let meaning: String
    let note: String?
    var id: String { term }
}

struct ContentAsset: Identifiable, Codable, Hashable, Sendable {
    enum Kind: String, Codable, Sendable { case audio, image }
    let id: String
    let kind: Kind
    let path: String
    let checksumSHA256: String?
    let durationMilliseconds: Int?
}

struct QuestionItem: Identifiable, Codable, Hashable, Sendable {
    let id: String
    let prompt: String?
    let options: [AnswerOption]
    let correctOptionID: String
    let explanation: Explanation
    let skills: [String]
    let transcript: String?
    let imageAssetID: String?
    let audioAssetID: String?
}

struct StimulusDocument: Identifiable, Codable, Hashable, Sendable {
    enum Kind: String, Codable, Sendable { case text, email, notice, article, chat, table, form }
    let id: String
    let kind: Kind
    let title: String?
    let body: String
    let accessibilityLabel: String?
}

struct AudioSegment: Identifiable, Codable, Hashable, Sendable {
    let id: String
    let text: String
    let startMilliseconds: Int
    let endMilliseconds: Int
}

struct QuestionGroup: Identifiable, Codable, Hashable, Sendable {
    let id: String
    let version: Int
    let sourceBatchID: String
    let familyID: String
    let part: TOEICPart
    let difficulty: Difficulty
    let scenario: String
    let documents: [StimulusDocument]
    let items: [QuestionItem]
    let audioAssetID: String?
    let audioSegments: [AudioSegment]
    let timeLimitSeconds: Int?
    let tags: [String]
    let purpose: ContentPurpose?
    let contentStatus: RuntimeContentStatus?
    let fixture: Bool

    init(
        id: String, version: Int = 1, sourceBatchID: String = "bundled",
        familyID: String, part: TOEICPart, difficulty: Difficulty, scenario: String,
        documents: [StimulusDocument], items: [QuestionItem], audioAssetID: String?,
        audioSegments: [AudioSegment] = [], timeLimitSeconds: Int?, tags: [String],
        purpose: ContentPurpose? = nil, contentStatus: RuntimeContentStatus? = nil,
        fixture: Bool = true
    ) {
        self.id = id
        self.version = version
        self.sourceBatchID = sourceBatchID
        self.familyID = familyID
        self.part = part
        self.difficulty = difficulty
        self.scenario = scenario
        self.documents = documents
        self.items = items
        self.audioAssetID = audioAssetID
        self.audioSegments = audioSegments
        self.timeLimitSeconds = timeLimitSeconds
        self.tags = tags
        self.purpose = purpose
        self.contentStatus = contentStatus
        self.fixture = fixture
    }

    private enum CodingKeys: String, CodingKey {
        case id, version, sourceBatchID, familyID, part, difficulty, scenario, documents, items
        case audioAssetID, audioSegments, timeLimitSeconds, tags, purpose, contentStatus, fixture
    }

    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        id = try container.decode(String.self, forKey: .id)
        version = try container.decodeIfPresent(Int.self, forKey: .version) ?? 1
        sourceBatchID = try container.decodeIfPresent(String.self, forKey: .sourceBatchID) ?? "legacy"
        familyID = try container.decode(String.self, forKey: .familyID)
        part = try container.decode(TOEICPart.self, forKey: .part)
        difficulty = try container.decode(Difficulty.self, forKey: .difficulty)
        scenario = try container.decode(String.self, forKey: .scenario)
        documents = try container.decodeIfPresent([StimulusDocument].self, forKey: .documents) ?? []
        items = try container.decode([QuestionItem].self, forKey: .items)
        audioAssetID = try container.decodeIfPresent(String.self, forKey: .audioAssetID)
        audioSegments = try container.decodeIfPresent([AudioSegment].self, forKey: .audioSegments) ?? []
        timeLimitSeconds = try container.decodeIfPresent(Int.self, forKey: .timeLimitSeconds)
        tags = try container.decodeIfPresent([String].self, forKey: .tags) ?? []
        purpose = try container.decodeIfPresent(ContentPurpose.self, forKey: .purpose)
        contentStatus = try container.decodeIfPresent(RuntimeContentStatus.self, forKey: .contentStatus)
        fixture = try container.decodeIfPresent(Bool.self, forKey: .fixture) ?? true
    }
}

struct ContentManifest: Codable, Hashable, Sendable {
    let schemaVersion: Int
    let packageID: String
    let contentVersion: String
    let locale: String
    let createdAt: Date
    let generator: String
    let generatorVersion: String
    let license: String
}

struct ContentPackage: Codable, Hashable, Sendable {
    let manifest: ContentManifest
    let assets: [ContentAsset]
    let groups: [QuestionGroup]
}

enum SessionMode: String, Codable, Sendable {
    case practice, diagnostic, mockExam, review, battle
}

enum QuickTestFocus: String, Codable, CaseIterable, Identifiable, Sendable {
    case reading
    case listening
    case mixed

    var id: String { rawValue }
    var title: String {
        switch self {
        case .reading: "閱讀"
        case .listening: "聽力"
        case .mixed: "混合"
        }
    }
}

enum QuickTestLevel: String, Codable, CaseIterable, Identifiable, Sendable {
    case foundation
    case challenge

    var id: String { rawValue }
    var title: String { self == .foundation ? "基礎" : "挑戰" }
    var targetDifficulty: Difficulty { self == .foundation ? .d2 : .d4 }
}

struct AnswerCondition: Codable, Hashable, Sendable {
    var playbackRate: Double = 1
    var replayCount: Int = 0
    var transcriptShown = false
    var sentenceModeUsed = false
    var voiceOverRunning = false
    var interrupted = false
    var appBackgrounded = false
    /// Captured when listening playback starts; diagnostic evidence only and does not affect scoring.
    var audioOutputRoute: String?
    var audioSessionSampleRate: Double?

    var isStandard: Bool {
        playbackRate == 1 && replayCount == 0 && !transcriptShown && !sentenceModeUsed
            && !voiceOverRunning && !interrupted && !appBackgrounded
    }
}

struct ItemResponse: Identifiable, Codable, Hashable, Sendable {
    let id: UUID
    let sessionID: UUID
    let groupID: String
    let groupVersion: Int?
    let sourceBatchID: String?
    let itemID: String
    let part: TOEICPart
    let difficulty: Difficulty
    let familyID: String
    let selectedOptionID: String?
    let isCorrect: Bool
    let answeredAt: Date
    let elapsedMilliseconds: Int
    let condition: AnswerCondition

    init(
        id: UUID, sessionID: UUID, groupID: String, groupVersion: Int? = nil, sourceBatchID: String? = nil,
        itemID: String, part: TOEICPart, difficulty: Difficulty, familyID: String,
        selectedOptionID: String?, isCorrect: Bool, answeredAt: Date,
        elapsedMilliseconds: Int, condition: AnswerCondition
    ) {
        self.id = id
        self.sessionID = sessionID
        self.groupID = groupID
        self.groupVersion = groupVersion
        self.sourceBatchID = sourceBatchID
        self.itemID = itemID
        self.part = part
        self.difficulty = difficulty
        self.familyID = familyID
        self.selectedOptionID = selectedOptionID
        self.isCorrect = isCorrect
        self.answeredAt = answeredAt
        self.elapsedMilliseconds = elapsedMilliseconds
        self.condition = condition
    }
}

struct LearningSession: Identifiable, Codable, Hashable, Sendable {
    let id: UUID
    let mode: SessionMode
    let contentVersion: String
    let startedAt: Date
    var completedAt: Date?
    var groupIDs: [String]
    var responses: [ItemResponse]
    var ruleVersion: String?
    var selectionReasons: [String: String]
}

struct UserPreferences: Codable, Hashable, Sendable {
    var dailyMinutes = 20
    var target: String = "穩定提升聽讀能力"
    var examDate: Date?
    var notificationsEnabled = true
    var messagePreviewEnabled = false
    var hasCompletedOnboarding = false
    var quickTestFocus: QuickTestFocus = .reading
    var quickTestLevel: QuickTestLevel = .foundation

    init(
        dailyMinutes: Int = 20,
        target: String = "穩定提升聽讀能力",
        examDate: Date? = nil,
        notificationsEnabled: Bool = true,
        messagePreviewEnabled: Bool = false,
        hasCompletedOnboarding: Bool = false,
        quickTestFocus: QuickTestFocus = .reading,
        quickTestLevel: QuickTestLevel = .foundation
    ) {
        self.dailyMinutes = dailyMinutes
        self.target = target
        self.examDate = examDate
        self.notificationsEnabled = notificationsEnabled
        self.messagePreviewEnabled = messagePreviewEnabled
        self.hasCompletedOnboarding = hasCompletedOnboarding
        self.quickTestFocus = quickTestFocus
        self.quickTestLevel = quickTestLevel
    }

    private enum CodingKeys: String, CodingKey {
        case dailyMinutes, target, examDate, notificationsEnabled, messagePreviewEnabled
        case hasCompletedOnboarding, quickTestFocus, quickTestLevel
    }

    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        dailyMinutes = try container.decodeIfPresent(Int.self, forKey: .dailyMinutes) ?? 20
        target = try container.decodeIfPresent(String.self, forKey: .target) ?? "穩定提升聽讀能力"
        examDate = try container.decodeIfPresent(Date.self, forKey: .examDate)
        notificationsEnabled = try container.decodeIfPresent(Bool.self, forKey: .notificationsEnabled) ?? true
        messagePreviewEnabled = try container.decodeIfPresent(Bool.self, forKey: .messagePreviewEnabled) ?? false
        hasCompletedOnboarding = try container.decodeIfPresent(Bool.self, forKey: .hasCompletedOnboarding) ?? false
        quickTestFocus = try container.decodeIfPresent(QuickTestFocus.self, forKey: .quickTestFocus) ?? .reading
        quickTestLevel = try container.decodeIfPresent(QuickTestLevel.self, forKey: .quickTestLevel) ?? .foundation
    }

    func encode(to encoder: Encoder) throws {
        var container = encoder.container(keyedBy: CodingKeys.self)
        try container.encode(dailyMinutes, forKey: .dailyMinutes)
        try container.encode(target, forKey: .target)
        try container.encodeIfPresent(examDate, forKey: .examDate)
        try container.encode(notificationsEnabled, forKey: .notificationsEnabled)
        try container.encode(messagePreviewEnabled, forKey: .messagePreviewEnabled)
        try container.encode(hasCompletedOnboarding, forKey: .hasCompletedOnboarding)
        try container.encode(quickTestFocus, forKey: .quickTestFocus)
        try container.encode(quickTestLevel, forKey: .quickTestLevel)
    }
}

struct ReviewState: Codable, Hashable, Sendable {
    let itemID: String
    var repetitions: Int
    var masteryEvidence: Int
    var lastFamilyID: String?
    var lastReviewedAt: Date
    var nextReviewAt: Date
}

struct ContentExposure: Codable, Hashable, Sendable {
    let groupID: String
    var familyIDs: Set<String>
    var versions: Set<Int>
    var sourceBatchIDs: Set<String>
    var itemIDs: Set<String>
    var modes: Set<SessionMode>
    var firstExposedAt: Date
    var lastExposedAt: Date
    var presentationCount: Int
}

struct LocalProfile: Codable, Hashable, Sendable {
    var preferences = UserPreferences()
    var sessions: [LearningSession] = []
    var dueItemIDs: [String] = []
    var hiddenConversationIDs: Set<UUID> = []
    var reviewStates: [String: ReviewState] = [:]
    var activeMockExam: MockExamRuntime?
    var exposures: [String: ContentExposure] = [:]

    init(
        preferences: UserPreferences = UserPreferences(),
        sessions: [LearningSession] = [],
        dueItemIDs: [String] = [],
        hiddenConversationIDs: Set<UUID> = [],
        reviewStates: [String: ReviewState] = [:],
        activeMockExam: MockExamRuntime? = nil,
        exposures: [String: ContentExposure] = [:]
    ) {
        self.preferences = preferences
        self.sessions = sessions
        self.dueItemIDs = dueItemIDs
        self.hiddenConversationIDs = hiddenConversationIDs
        self.reviewStates = reviewStates
        self.activeMockExam = activeMockExam
        self.exposures = exposures
    }

    private enum CodingKeys: String, CodingKey {
        case preferences, sessions, dueItemIDs, hiddenConversationIDs, reviewStates, activeMockExam, exposures
    }

    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        preferences = try container.decodeIfPresent(UserPreferences.self, forKey: .preferences) ?? UserPreferences()
        sessions = try container.decodeIfPresent([LearningSession].self, forKey: .sessions) ?? []
        dueItemIDs = try container.decodeIfPresent([String].self, forKey: .dueItemIDs) ?? []
        hiddenConversationIDs = try container.decodeIfPresent(Set<UUID>.self, forKey: .hiddenConversationIDs) ?? []
        reviewStates = try container.decodeIfPresent([String: ReviewState].self, forKey: .reviewStates) ?? [:]
        activeMockExam = try container.decodeIfPresent(MockExamRuntime.self, forKey: .activeMockExam)
        if let decoded = try container.decodeIfPresent([String: ContentExposure].self, forKey: .exposures) {
            exposures = decoded
        } else {
            exposures = Self.migratedExposures(from: sessions)
        }
    }

    private static func migratedExposures(from sessions: [LearningSession]) -> [String: ContentExposure] {
        var result: [String: ContentExposure] = [:]
        for session in sessions {
            for response in session.responses {
                var exposure = result[response.groupID] ?? ContentExposure(
                    groupID: response.groupID,
                    familyIDs: [],
                    versions: [],
                    sourceBatchIDs: [],
                    itemIDs: [],
                    modes: [],
                    firstExposedAt: response.answeredAt,
                    lastExposedAt: response.answeredAt,
                    presentationCount: 0
                )
                exposure.familyIDs.insert(response.familyID)
                if let version = response.groupVersion { exposure.versions.insert(version) }
                if let batchID = response.sourceBatchID { exposure.sourceBatchIDs.insert(batchID) }
                exposure.itemIDs.insert(response.itemID)
                exposure.modes.insert(session.mode)
                exposure.firstExposedAt = min(exposure.firstExposedAt, response.answeredAt)
                exposure.lastExposedAt = max(exposure.lastExposedAt, response.answeredAt)
                exposure.presentationCount += 1
                result[response.groupID] = exposure
            }
        }
        return result
    }
}

extension LocalProfile {
    mutating func recordExposure(group: QuestionGroup, itemID: String, mode: SessionMode, now: Date = .now) {
        var exposure = exposures[group.id] ?? ContentExposure(
            groupID: group.id,
            familyIDs: [],
            versions: [],
            sourceBatchIDs: [],
            itemIDs: [],
            modes: [],
            firstExposedAt: now,
            lastExposedAt: now,
            presentationCount: 0
        )
        exposure.familyIDs.insert(group.familyID)
        exposure.versions.insert(group.version)
        exposure.sourceBatchIDs.insert(group.sourceBatchID)
        exposure.itemIDs.insert(itemID)
        exposure.modes.insert(mode)
        exposure.firstExposedAt = min(exposure.firstExposedAt, now)
        exposure.lastExposedAt = max(exposure.lastExposedAt, now)
        exposure.presentationCount += 1
        exposures[group.id] = exposure
    }
}
