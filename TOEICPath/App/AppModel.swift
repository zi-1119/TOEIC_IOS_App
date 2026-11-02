import Foundation
import Combine
import CryptoKit

@MainActor
final class AppModel: ObservableObject {
    enum Connectivity { case online, offline }
    enum ContentBootstrapState: Equatable {
        case idle
        case loading
        case ready(itemCount: Int)
        case failed(String)
    }
    enum MaterialAvailability: Equatable {
        case complete
        case previewOnly(String)
    }
    enum SessionStartError: LocalizedError, Equatable {
        case emptySelection
        case wrongPurpose(groupID: String, expected: ContentPurpose)
        case unapproved(groupID: String)
        case missingMaterial(groupID: String, reason: String)

        var errorDescription: String? {
            switch self {
            case .emptySelection: "目前沒有可正式作答的完整題組。"
            case let .wrongPurpose(groupID, expected): "題組 \(groupID) 不屬於 \(expected.rawValue) 用途池。"
            case let .unapproved(groupID): "題組 \(groupID) 尚未通過正式使用條件。"
            case let .missingMaterial(groupID, reason): "題組 \(groupID) 素材不完整：\(reason)。"
            }
        }
    }
    enum MockStartError: LocalizedError {
        case unresolvedForm
        case invalidForm([String])
        case missingTimeline

        var errorDescription: String? {
            switch self {
            case .unresolvedForm: "這份模考未由目前啟用批次的精確版本解析，不能開始。"
            case .invalidForm(let issues): "模考表單未通過：\(issues.joined(separator: "；"))"
            case .missingTimeline: "整卷聽力音檔遺失或無法讀取，不能開始正式模考。"
            }
        }
    }

    @Published private(set) var package: ContentPackage
    @Published var profile: LocalProfile
    @Published var connectivity: Connectivity = .online
    @Published var selectedTab = 0
    @Published var activeSession: LearningSession?
    @Published var lastSaveError: String?
    @Published var friends: [FriendSummary] = []
    @Published var matches: [BattleMatch] = []
    @Published private(set) var battleQuestionsByMatch: [UUID: [BattleQuestion]] = [:]
    @Published var identity: AuthIdentity?
    @Published var socialError: String?
    @Published var mockExamForm: MockExamForm?
    @Published private(set) var resolvedMockForms: [ResolvedMockExamForm]
    @Published private(set) var contentBootstrapState: ContentBootstrapState

    private let store: LocalProfileStore
    private let contentStore: ContentVersionStore
    private let bundledSeedRootURL: URL?
    private let bundledContentBootstrapper: BundledContentBootstrapper
    private let backend: any AppBackendService
    let usesNetworkBackend: Bool

    init(
        store: LocalProfileStore = LocalProfileStore(),
        package: ContentPackage = SampleContent.package,
        contentStore: ContentVersionStore = ContentVersionStore(),
        bundledSeedRootURL: URL? = BundledSeedContent.rootURL(),
        backend: any AppBackendService = LocalBackendClient(hub: LocalBackendHub())
    ) {
        let activeCatalog = try? contentStore.activeCatalog()
        self.store = store
        self.contentStore = contentStore
        self.bundledSeedRootURL = bundledSeedRootURL
        self.bundledContentBootstrapper = BundledContentBootstrapper(rootURL: contentStore.storageRootURL)
        self.backend = backend
        self.usesNetworkBackend = backend is NetworkBackendClient
        self.package = activeCatalog?.package ?? package
        self.profile = store.load()
        self.resolvedMockForms = activeCatalog?.mockForms ?? []
        self.mockExamForm = activeCatalog?.mockForms.first?.form
        self.contentBootstrapState = activeCatalog.map { .ready(itemCount: $0.package.groups.flatMap(\.items).count) } ?? .idle
    }

    var validationReport: ContentValidationReport { ContentValidator.validate(package) }
    var completedResponses: [ItemResponse] { profile.sessions.flatMap(\.responses) }
    var standardResponses: [ItemResponse] { completedResponses.filter(\.condition.isStandard) }
    var dueReviewCount: Int { profile.reviewStates.values.filter { $0.nextReviewAt <= .now }.count }
    var activeBatchCount: Int { Set(package.groups.map(\.sourceBatchID).filter { $0 != "bundled" }).count }
    var exposedFamilyIDs: Set<String> { Set(profile.exposures.values.flatMap(\.familyIDs)) }

    func materialAvailability(for group: QuestionGroup) -> MaterialAvailability {
        guard group.part.section == .listening else { return .complete }
        let hasAudio = group.items.allSatisfy { assetURL(for: $0.audioAssetID ?? group.audioAssetID) != nil }
        guard hasAudio else { return .previewOnly("缺少 ready 音訊") }
        if group.part == .part1 {
            let hasImages = group.items.allSatisfy { assetURL(for: $0.imageAssetID) != nil }
            guard hasImages else { return .previewOnly("缺少 ready 照片") }
        }
        return .complete
    }

    func completeOnboarding(minutes: Int, target: String, examDate: Date?) {
        profile.preferences.dailyMinutes = minutes
        profile.preferences.target = target
        profile.preferences.examDate = examDate
        profile.preferences.hasCompletedOnboarding = true
        persist()
    }

    func updateQuickTestPreferences(focus: QuickTestFocus, level: QuickTestLevel) {
        guard profile.preferences.quickTestFocus != focus || profile.preferences.quickTestLevel != level else { return }
        profile.preferences.quickTestFocus = focus
        profile.preferences.quickTestLevel = level
        persist()
    }

    func quickTestAssembly(
        focus: QuickTestFocus? = nil,
        level: QuickTestLevel? = nil,
        targetItemCount: Int = 10
    ) -> QuickTestAssembly {
        let selectedFocus = focus ?? profile.preferences.quickTestFocus
        let selectedLevel = level ?? profile.preferences.quickTestLevel
        let completeGroupIDs = Set(package.groups.compactMap { group in
            materialAvailability(for: group) == .complete ? group.id : nil
        })
        return QuickTestAssembler.assemble(
            from: package.groups,
            focus: selectedFocus,
            level: selectedLevel,
            profile: profile,
            materialCompleteGroupIDs: completeGroupIDs,
            targetItemCount: targetItemCount
        )
    }

    func beginSession(groups: [QuestionGroup], mode: SessionMode) throws {
        guard !groups.isEmpty else { throw SessionStartError.emptySelection }
        let expectedPurpose: ContentPurpose
        switch mode {
        case .practice, .review: expectedPurpose = .training
        case .diagnostic: expectedPurpose = .diagnostic
        case .mockExam: expectedPurpose = .mock
        case .battle: expectedPurpose = .battle
        }
        for group in groups {
            guard group.purpose == expectedPurpose else {
                throw SessionStartError.wrongPurpose(groupID: group.id, expected: expectedPurpose)
            }
            guard ContentEligibility.isFormallyEligible(group, for: expectedPurpose) else {
                throw SessionStartError.unapproved(groupID: group.id)
            }
            if case let .previewOnly(reason) = materialAvailability(for: group) {
                throw SessionStartError.missingMaterial(groupID: group.id, reason: reason)
            }
        }
        activeSession = LearningSession(
            id: UUID(), mode: mode, contentVersion: package.manifest.contentVersion,
            startedAt: .now, completedAt: nil, groupIDs: groups.map(\.id), responses: [],
            ruleVersion: mode == .diagnostic ? DiagnosticRule.initial.version : nil,
            selectionReasons: Dictionary(uniqueKeysWithValues: groups.map { ($0.id, selectionReason(for: $0, mode: mode)) })
        )
    }

    func finishSession(responses: [ItemResponse]) {
        guard var session = activeSession else { return }
        session.responses = responses
        session.completedAt = .now
        profile.sessions.append(session)
        if session.mode == .practice || session.mode == .review {
            let incorrect = responses.filter { !$0.isCorrect }.map(\.itemID)
            profile.dueItemIDs = Array(Set(profile.dueItemIDs + incorrect)).sorted()
            for response in responses {
                profile.reviewStates[response.itemID] = ReviewScheduler.updatedState(
                    for: response, previous: profile.reviewStates[response.itemID]
                )
            }
        }
        activeSession = nil
        persist()
    }

    func recordExposure(group: QuestionGroup, itemID: String, mode: SessionMode, now: Date = .now) {
        profile.recordExposure(group: group, itemID: itemID, mode: mode, now: now)
        persist()
    }

    func abortActiveSession() {
        activeSession = nil
    }

    func appendDiagnosticGroup(_ group: QuestionGroup, reason: String) {
        guard var session = activeSession, session.mode == .diagnostic,
              !session.groupIDs.contains(group.id) else { return }
        session.groupIDs.append(group.id)
        session.selectionReasons[group.id] = reason
        activeSession = session
    }

    func importBatchDirectory(_ url: URL) throws {
        guard contentBootstrapState != .loading else { throw BundledSeedError.installInProgress }
        let installed = try contentStore.install(from: url)
        package = installed.package
        resolvedMockForms = installed.mockForms
        mockExamForm = installed.mockForms.first?.form
    }

    func bootstrapBundledContent() async {
        guard contentBootstrapState != .loading else { return }
        contentBootstrapState = .loading
        guard let bundledSeedRootURL else {
            contentBootstrapState = .failed(BundledSeedError.missingResource.localizedDescription)
            return
        }
        do {
            let catalog = try await bundledContentBootstrapper.install(rootURL: bundledSeedRootURL)
            package = catalog.package
            resolvedMockForms = catalog.mockForms
            mockExamForm = catalog.mockForms.first?.form
            contentBootstrapState = .ready(itemCount: catalog.package.groups.flatMap(\.items).count)
        } catch {
            contentBootstrapState = .failed(error.localizedDescription)
        }
    }

    func persist() {
        do { try store.save(profile); lastSaveError = nil }
        catch { lastSaveError = error.localizedDescription }
    }

    func startMockExam(form: MockExamForm, now: Date = .now) throws {
        guard let resolved = resolvedMockForms.first(where: {
            $0.form.id == form.id && $0.form.revision == form.revision && $0.form == form
        }) else { throw MockStartError.unresolvedForm }
        var issues = form.validationIssues() + form.contentValidationIssues(groups: resolved.groups)
        if resolved.groups.contains(where: { !ContentEligibility.isFormallyEligible($0, for: .mock) }) {
            issues.append("含有非正式 mock 用途題組")
        }
        guard issues.isEmpty else { throw MockStartError.invalidForm(issues) }
        guard mockAudioURL(for: form) != nil else { throw MockStartError.missingTimeline }
        var runtime = MockExamRuntime(form: form, now: now)
        try runtime.start(now: now)
        profile.activeMockExam = runtime
        persist()
    }

    func saveMockExam(_ runtime: MockExamRuntime) {
        profile.activeMockExam = runtime
        persist()
    }

    func clearMockExam() {
        profile.activeMockExam = nil
        persist()
    }

    func requestLocalSignInCode(email: String) async throws {
        try await backend.requestEmailCode(email: email)
    }

    func verifyLocalSignIn(email: String, code: String) async throws {
        let signedIn = try await backend.verifyEmailCode(email: email, code: code)
        identity = signedIn
        try await backend.mergeLocalProfile(profile, into: signedIn, requestID: UUID())
        try await refreshFriends()
        try await refreshMatches()
    }

    func signOutLocalAccount() async {
        await backend.signOut()
        identity = nil
        friends = []
        matches = []
        battleQuestionsByMatch = [:]
    }

    func refreshFriends() async throws {
        guard identity != nil else { friends = []; return }
        friends = try await backend.listFriends()
        socialError = nil
    }

    func createFriendInvite() async throws -> URL {
        try await backend.createInvite(requestID: UUID())
    }

    func acceptFriendInvite(code: String) async throws {
        _ = try await backend.acceptInvite(code: code, requestID: UUID())
        try await refreshFriends()
    }

    func setBlocked(friendID: UUID, blocked: Bool) async throws {
        try await backend.setBlocked(userID: friendID, blocked: blocked, requestID: UUID())
        try await refreshFriends()
    }

    func removeFriend(friendID: UUID) async throws {
        try await backend.removeFriend(userID: friendID, requestID: UUID())
        try await refreshFriends()
    }

    func conversationID(with friendID: UUID) async throws -> UUID {
        try await backend.conversationID(with: friendID)
    }

    func messages(conversationID: UUID, after: Date? = nil) async throws -> [ChatMessage] {
        try await backend.messages(conversationID: conversationID, after: after)
    }

    func sendMessage(conversationID: UUID, clientMessageID: UUID, body: String) async throws -> ChatMessage {
        try await backend.sendMessage(conversationID: conversationID, clientMessageID: clientMessageID, body: body)
    }

    func createLocalBattle(opponentID: UUID) async throws {
        let groups = ContentEligibility.formalGroups(in: package.groups, for: .battle)
            .filter { $0.part == .part5 && materialAvailability(for: $0) == .complete }
        let selectedGroups = Array(groups.prefix(10))
        guard !selectedGroups.isEmpty else { throw LocalBackendError.invalidBattleContent }
        let items = selectedGroups.flatMap { group in
            group.items.map { LocalBattleItem(groupID: group.id, itemID: $0.id, correctOptionID: $0.correctOptionID,
                                               contentVersion: package.manifest.contentVersion, purpose: .battle,
                                               prompt: $0.prompt, options: $0.options,
                                               assetChecksums: battleAssetChecksums(group: group, item: $0)) }
        }
        try await backend.configureBattleItems(items)
        let match = try await backend.createChallenge(opponentID: opponentID, groupIDs: selectedGroups.map(\.id), requestID: UUID())
        upsertMatch(match)
        try await loadBattleQuestions(for: match)
    }

    func refreshMatches() async throws {
        guard identity != nil else { matches = []; battleQuestionsByMatch = [:]; return }
        matches = try await backend.listMatches()
        battleQuestionsByMatch = battleQuestionsByMatch.filter { id, _ in matches.contains { $0.id == id } }
        for match in matches { try await loadBattleQuestions(for: match) }
    }

    func acceptBattle(_ matchID: UUID) async throws {
        let match = try await backend.accept(matchID: matchID, requestID: UUID())
        upsertMatch(match)
        try await loadBattleQuestions(for: match)
    }

    func markBattleReady(_ matchID: UUID) async throws {
        guard let match = matches.first(where: { $0.id == matchID }) else { throw LocalBackendError.forbidden }
        try await loadBattleQuestions(for: match)
        let expected = battleQuestions(for: match).reduce(into: [String: String]()) { result, question in
            for (assetID, checksum) in question.assetChecksums { result[assetID] = checksum.lowercased() }
        }
        var checksums: [String: String] = [:]
        for (assetID, expectedChecksum) in expected {
            guard let url = assetURL(for: assetID),
                  let data = try? Data(contentsOf: url),
                  Self.sha256(data) == expectedChecksum else { throw LocalBackendError.battleAssetMismatch }
            checksums[assetID] = expectedChecksum
        }
        upsertMatch(try await backend.ready(matchID: matchID, assetChecksums: checksums, requestID: UUID()))
    }

    func submitBattleAnswer(matchID: UUID, itemID: String, optionID: String, requestID: UUID) async throws {
        try await backend.submitAnswer(matchID: matchID, itemID: itemID, optionID: optionID, requestID: requestID)
        upsertMatch(try await backend.refresh(matchID: matchID))
    }

    func submitBattle(_ matchID: UUID) async throws {
        upsertMatch(try await backend.submitMatch(matchID: matchID, requestID: UUID()))
    }

    func refreshBattle(_ matchID: UUID) async throws {
        let match = try await backend.refresh(matchID: matchID)
        upsertMatch(match)
        try await loadBattleQuestions(for: match)
    }

    func battleGroups(for match: BattleMatch) -> [QuestionGroup] {
        guard match.contentVersion == package.manifest.contentVersion else { return [] }
        let byID = Dictionary(uniqueKeysWithValues: package.groups.map { ($0.id, $0) })
        return match.groupIDs.compactMap { byID[$0] }
    }

    func battleQuestions(for match: BattleMatch) -> [BattleQuestion] {
        battleQuestionsByMatch[match.id] ?? []
    }

    func battleItem(_ itemID: String, in match: BattleMatch) -> BattleQuestion? {
        battleQuestions(for: match).first { $0.id == itemID }
    }

    private func loadBattleQuestions(for match: BattleMatch) async throws {
        let questions = try await backend.battleQuestions(matchID: match.id)
        guard questions.map(\.id) == match.orderedItemIDs,
              questions.allSatisfy({ match.groupIDs.contains($0.groupID) }) else {
            throw LocalBackendError.invalidBattleContent
        }
        battleQuestionsByMatch[match.id] = questions
    }

    private func battleAssetChecksums(group: QuestionGroup, item: QuestionItem) -> [String: String] {
        let ids = Set([group.audioAssetID, item.audioAssetID, item.imageAssetID].compactMap { $0 })
        return Dictionary(uniqueKeysWithValues: ids.compactMap { id in
            package.assets.first(where: { $0.id == id })?.checksumSHA256.map { (id, $0.lowercased()) }
        })
    }

    private static func sha256(_ data: Data) -> String {
        SHA256.hash(data: data).map { String(format: "%02x", $0) }.joined()
    }

    private func upsertMatch(_ match: BattleMatch) {
        if let index = matches.firstIndex(where: { $0.id == match.id }) { matches[index] = match }
        else { matches.insert(match, at: 0) }
    }

    func mockAudioURL(for form: MockExamForm) -> URL? {
        guard form.audioTimelineAssetIDs.count == 1,
              let asset = package.assets.first(where: { $0.id == form.audioTimelineAssetIDs[0] }) else { return nil }
        return assetURL(asset)
    }

    func mockGroups(for form: MockExamForm) -> [QuestionGroup] {
        resolvedMockForms.first { $0.form.id == form.id && $0.form.revision == form.revision }?.groups ?? []
    }

    func assetURL(for assetID: String?) -> URL? {
        guard let assetID, let asset = package.assets.first(where: { $0.id == assetID }) else { return nil }
        return assetURL(asset)
    }

    private func assetURL(_ asset: ContentAsset) -> URL? {
        if asset.path.hasPrefix("/") {
            let url = URL(fileURLWithPath: asset.path)
            return FileManager.default.fileExists(atPath: url.path) ? url : nil
        }
        if let encoded = asset.path.addingPercentEncoding(withAllowedCharacters: .urlPathAllowed),
           let url = URL(string: encoded), url.isFileURL,
           FileManager.default.fileExists(atPath: url.path) { return url }
        return Bundle.main.url(forResource: asset.path, withExtension: nil)
    }

    func finalizeMockExam(_ runtime: MockExamRuntime, groups: [QuestionGroup], now: Date = .now) {
        let entries = groups.flatMap { group in group.items.map { (group, $0) } }
        let startedAt = runtime.answerRecords.values.map(\.firstAnsweredAt).min() ?? now
        let interrupted = !runtime.interruptions.isEmpty
        let backgrounded = runtime.interruptions.contains { $0.kind == .background }
        let responses = entries.map { group, item -> ItemResponse in
            let record = runtime.answerRecords[item.id]
            var condition = record?.condition ?? AnswerCondition()
            condition.interrupted = interrupted
            condition.appBackgrounded = backgrounded
            return ItemResponse(
                id: UUID(), sessionID: runtime.sessionID, groupID: group.id, groupVersion: group.version,
                sourceBatchID: group.sourceBatchID, itemID: item.id,
                part: group.part, difficulty: group.difficulty, familyID: group.familyID,
                selectedOptionID: record?.selectedOptionID,
                isCorrect: record?.selectedOptionID == item.correctOptionID,
                answeredAt: record?.lastChangedAt ?? now,
                elapsedMilliseconds: record?.elapsedSectionMilliseconds ?? 0,
                condition: condition
            )
        }
        profile.sessions.append(.init(
            id: runtime.sessionID, mode: .mockExam, contentVersion: runtime.form.contentVersion,
            startedAt: startedAt, completedAt: now, groupIDs: runtime.form.orderedGroupIDs,
            responses: responses, ruleVersion: nil, selectionReasons: [:]
        ))
        profile.activeMockExam = nil
        persist()
    }

    private func selectionReason(for group: QuestionGroup, mode: SessionMode) -> String {
        switch mode {
        case .diagnostic: "診斷暖身：涵蓋 \(group.part.shortTitle)，從 \(group.difficulty.label) 收集完整題組證據。"
        case .review: "到期複習或錯題重做。"
        case .practice: "依練習入口選擇的完整題組。"
        case .mockExam: "固定規格模考題組。"
        case .battle: "由伺服器鎖定版本與順序的同卷題組。"
        }
    }

}
