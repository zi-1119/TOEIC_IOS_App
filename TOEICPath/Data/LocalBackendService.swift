import Foundation

struct LocalBattleItem: Codable, Hashable, Sendable {
    let groupID: String
    let itemID: String
    let correctOptionID: String
    let contentVersion: String
    let purpose: ContentPurpose?
    let prompt: String?
    let options: [AnswerOption]
    let assetChecksums: [String: String]

    init(
        groupID: String,
        itemID: String,
        correctOptionID: String,
        contentVersion: String,
        purpose: ContentPurpose? = nil,
        prompt: String? = nil,
        options: [AnswerOption] = [],
        assetChecksums: [String: String] = [:]
    ) {
        self.groupID = groupID
        self.itemID = itemID
        self.correctOptionID = correctOptionID
        self.contentVersion = contentVersion
        self.purpose = purpose
        self.prompt = prompt
        self.options = options
        self.assetChecksums = assetChecksums
    }

    private enum CodingKeys: String, CodingKey {
        case groupID, itemID, correctOptionID, contentVersion, purpose, prompt, options, assetChecksums
    }

    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        groupID = try container.decode(String.self, forKey: .groupID)
        itemID = try container.decode(String.self, forKey: .itemID)
        correctOptionID = try container.decode(String.self, forKey: .correctOptionID)
        contentVersion = try container.decode(String.self, forKey: .contentVersion)
        purpose = try container.decodeIfPresent(ContentPurpose.self, forKey: .purpose)
        prompt = try container.decodeIfPresent(String.self, forKey: .prompt)
        options = try container.decodeIfPresent([AnswerOption].self, forKey: .options) ?? []
        assetChecksums = try container.decodeIfPresent([String: String].self, forKey: .assetChecksums) ?? [:]
    }

    var clientQuestion: BattleQuestion {
        BattleQuestion(id: itemID, groupID: groupID, prompt: prompt, options: options, assetChecksums: assetChecksums)
    }
}

actor LocalBackendHub {
    static let verificationCode = "246810"

    private struct Invite: Codable, Hashable {
        let code: String
        let inviterID: UUID
        let requestID: UUID
        let expiresAt: Date
        var acceptedBy: UUID?
    }

    private struct Friendship: Codable, Hashable {
        let id: UUID
        let firstID: UUID
        let secondID: UUID
        var accepted: Bool
        var removed: Bool
    }

    private struct Conversation: Codable, Hashable {
        let id: UUID
        let friendshipID: UUID
        let firstID: UUID
        let secondID: UUID
    }

    private struct Block: Codable, Hashable { let blockerID: UUID; let blockedID: UUID }
    private struct ProfileEntry: Codable, Hashable { let userID: UUID; var profile: LocalProfile; var requestIDs: Set<UUID> }
    private struct BattleAnswer: Codable, Hashable {
        let matchID: UUID; let userID: UUID; let itemID: String; let optionID: String; let requestID: UUID
    }
    private struct Issue: Codable, Hashable {
        let reporterID: UUID; let requestID: UUID; let groupID: String; let itemID: String?; let category: String; let details: String
    }
    private struct State: Codable {
        var users: [AuthIdentity] = []
        var requestedEmails: Set<String> = []
        var invites: [Invite] = []
        var friendships: [Friendship] = []
        var conversations: [Conversation] = []
        var blocks: [Block] = []
        var messages: [ChatMessage] = []
        var profiles: [ProfileEntry] = []
        var matches: [BattleMatch] = []
        var answers: [BattleAnswer] = []
        var battleItems: [LocalBattleItem] = []
        var battleOperationIDs: Set<UUID>? = []
        var issues: [Issue] = []
    }

    private let storeURL: URL
    private let loadFailure: String?
    private var state: State

    init(storeURL: URL? = nil) {
        let resolved = storeURL ?? FileManager.default.urls(for: .applicationSupportDirectory, in: .userDomainMask)[0]
            .appending(path: "TOEICPath/LocalBackend/state.json")
        self.storeURL = resolved
        let decoder = JSONDecoder()
        decoder.dateDecodingStrategy = .iso8601
        if FileManager.default.fileExists(atPath: resolved.path) {
            do {
                self.state = try decoder.decode(State.self, from: Data(contentsOf: resolved))
                self.loadFailure = nil
            } catch {
                self.state = State()
                self.loadFailure = error.localizedDescription
            }
        } else {
            self.state = State()
            self.loadFailure = nil
        }
    }

    func makeClient() -> LocalBackendClient { LocalBackendClient(hub: self) }

    func registerBattleItems(_ items: [LocalBattleItem]) throws {
        try ensureStorageReadable()
        guard !items.isEmpty, items.allSatisfy({
            $0.purpose == .battle &&
            $0.prompt?.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty == false &&
            $0.options.count >= 2 &&
            Set($0.options.map(\.id)).count == $0.options.count
        }) else {
            throw LocalBackendError.invalidBattleContent
        }
        for item in items {
            if let existing = state.battleItems.first(where: { $0.contentVersion == item.contentVersion && $0.itemID == item.itemID }) {
                guard existing == item else { throw LocalBackendError.invalidBattleContent }
            } else {
                state.battleItems.append(item)
            }
        }
        try persist()
    }

    fileprivate func requestCode(email: String) throws {
        try ensureStorageReadable()
        let normalized = try normalize(email)
        state.requestedEmails.insert(normalized)
        try persist()
    }

    fileprivate func verify(email: String, code: String) throws -> AuthIdentity {
        try ensureStorageReadable()
        let normalized = try normalize(email)
        guard state.requestedEmails.contains(normalized), code == Self.verificationCode else { throw LocalBackendError.invalidCode }
        if let existing = state.users.first(where: { $0.email == normalized }) { return existing }
        let stem = normalized.split(separator: "@").first.map(String.init) ?? "Learner"
        let identity = AuthIdentity(userID: UUID(), email: normalized, displayName: stem)
        state.users.append(identity)
        try persist()
        return identity
    }

    fileprivate func merge(profile: LocalProfile, actorID: UUID, requestID: UUID) throws {
        try requireUser(actorID)
        if let index = state.profiles.firstIndex(where: { $0.userID == actorID }) {
            guard !state.profiles[index].requestIDs.contains(requestID) else { return }
            let existingIDs = Set(state.profiles[index].profile.sessions.map(\.id))
            state.profiles[index].profile.sessions.append(contentsOf: profile.sessions.filter { !existingIDs.contains($0.id) })
            state.profiles[index].profile.dueItemIDs = Array(Set(state.profiles[index].profile.dueItemIDs + profile.dueItemIDs)).sorted()
            for (groupID, incoming) in profile.exposures {
                guard var existing = state.profiles[index].profile.exposures[groupID] else {
                    state.profiles[index].profile.exposures[groupID] = incoming
                    continue
                }
                existing.familyIDs.formUnion(incoming.familyIDs)
                existing.versions.formUnion(incoming.versions)
                existing.sourceBatchIDs.formUnion(incoming.sourceBatchIDs)
                existing.itemIDs.formUnion(incoming.itemIDs)
                existing.modes.formUnion(incoming.modes)
                existing.firstExposedAt = min(existing.firstExposedAt, incoming.firstExposedAt)
                existing.lastExposedAt = max(existing.lastExposedAt, incoming.lastExposedAt)
                existing.presentationCount += incoming.presentationCount
                state.profiles[index].profile.exposures[groupID] = existing
            }
            state.profiles[index].requestIDs.insert(requestID)
        } else {
            state.profiles.append(.init(userID: actorID, profile: profile, requestIDs: [requestID]))
        }
        try persist()
    }

    fileprivate func createInvite(actorID: UUID, requestID: UUID) throws -> URL {
        try requireUser(actorID)
        if let existing = state.invites.first(where: { $0.inviterID == actorID && $0.requestID == requestID }) {
            return inviteURL(existing.code)
        }
        let invite = Invite(code: UUID().uuidString.replacingOccurrences(of: "-", with: "").lowercased(), inviterID: actorID,
                            requestID: requestID, expiresAt: .now.addingTimeInterval(86_400), acceptedBy: nil)
        state.invites.append(invite)
        try persist()
        return inviteURL(invite.code)
    }

    fileprivate func acceptInvite(code: String, actorID: UUID) throws -> FriendSummary {
        try requireUser(actorID)
        guard let inviteIndex = state.invites.firstIndex(where: { $0.code == code }) else { throw LocalBackendError.inviteNotFound }
        let invite = state.invites[inviteIndex]
        guard invite.expiresAt > .now else { throw LocalBackendError.inviteExpired }
        guard invite.inviterID != actorID else { throw LocalBackendError.cannotInviteSelf }
        guard !isBlocked(invite.inviterID, actorID) else { throw LocalBackendError.blocked }
        if let existing = friendship(invite.inviterID, actorID), existing.accepted, !existing.removed {
            return try friendSummary(userID: invite.inviterID, viewerID: actorID)
        }
        let friendship = Friendship(id: UUID(), firstID: invite.inviterID, secondID: actorID, accepted: true, removed: false)
        state.friendships.removeAll { pairMatches($0.firstID, $0.secondID, invite.inviterID, actorID) }
        state.friendships.append(friendship)
        state.conversations.append(.init(id: UUID(), friendshipID: friendship.id, firstID: invite.inviterID, secondID: actorID))
        state.invites[inviteIndex].acceptedBy = actorID
        try persist()
        return try friendSummary(userID: invite.inviterID, viewerID: actorID)
    }

    fileprivate func listFriends(actorID: UUID) throws -> [FriendSummary] {
        try requireUser(actorID)
        return try state.friendships.filter { $0.accepted && !$0.removed && ($0.firstID == actorID || $0.secondID == actorID) }
            .compactMap { relation -> FriendSummary? in
                let other = relation.firstID == actorID ? relation.secondID : relation.firstID
                guard !isBlocked(actorID, other) else { return nil }
                return try friendSummary(userID: other, viewerID: actorID)
            }.sorted { $0.displayName < $1.displayName }
    }

    fileprivate func conversationID(actorID: UUID, friendID: UUID) throws -> UUID {
        try requireMessagingAccess(actorID, friendID, allowRemoved: true)
        guard let conversation = state.conversations.first(where: { pairMatches($0.firstID, $0.secondID, actorID, friendID) }) else {
            throw LocalBackendError.conversationNotFound
        }
        return conversation.id
    }

    fileprivate func sendMessage(actorID: UUID, conversationID: UUID, clientMessageID: UUID, body: String) throws -> ChatMessage {
        let normalizedBody = body.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !normalizedBody.isEmpty, normalizedBody.count <= 4_000 else { throw LocalBackendError.invalidMessage }
        guard let conversation = state.conversations.first(where: { $0.id == conversationID }) else { throw LocalBackendError.conversationNotFound }
        guard conversation.firstID == actorID || conversation.secondID == actorID else { throw LocalBackendError.forbidden }
        let other = conversation.firstID == actorID ? conversation.secondID : conversation.firstID
        try requireMessagingAccess(actorID, other, allowRemoved: false)
        if let duplicate = state.messages.first(where: { $0.senderID == actorID && $0.clientMessageID == clientMessageID }) { return duplicate }
        let message = ChatMessage(id: UUID(), clientMessageID: clientMessageID, conversationID: conversationID,
                                  senderID: actorID, body: normalizedBody, createdAt: .now, delivery: .sent)
        state.messages.append(message)
        try persist()
        return message
    }

    fileprivate func messages(actorID: UUID, conversationID: UUID, after: Date?) throws -> [ChatMessage] {
        guard let conversation = state.conversations.first(where: { $0.id == conversationID }) else { throw LocalBackendError.conversationNotFound }
        guard conversation.firstID == actorID || conversation.secondID == actorID else { throw LocalBackendError.forbidden }
        let other = conversation.firstID == actorID ? conversation.secondID : conversation.firstID
        guard !isBlocked(actorID, other) else { throw LocalBackendError.blocked }
        return state.messages.filter { $0.conversationID == conversationID && (after == nil || $0.createdAt > after!) }
            .sorted { $0.createdAt < $1.createdAt }
    }

    fileprivate func removeFriend(actorID: UUID, userID: UUID) throws {
        guard let index = state.friendships.firstIndex(where: { pairMatches($0.firstID, $0.secondID, actorID, userID) }) else { return }
        state.friendships[index].removed = true
        try persist()
    }

    fileprivate func setBlocked(actorID: UUID, userID: UUID, blocked: Bool) throws {
        try requireUser(actorID); try requireUser(userID)
        state.blocks.removeAll { $0.blockerID == actorID && $0.blockedID == userID }
        if blocked { state.blocks.append(.init(blockerID: actorID, blockedID: userID)) }
        try persist()
    }

    fileprivate func createChallenge(actorID: UUID, opponentID: UUID, groupIDs: [String], requestID: UUID) throws -> BattleMatch {
        try reconcileMatches()
        try requireMessagingAccess(actorID, opponentID, allowRemoved: false)
        if let duplicate = state.matches.first(where: { $0.participants.contains(where: { $0.id == actorID }) && $0.requestID == requestID }) { return duplicate }
        let candidateVersions = state.battleItems.reversed().map(\.contentVersion).reduce(into: [String]()) {
            if !$0.contains($1) { $0.append($1) }
        }
        guard let contentVersion = candidateVersions.first(where: { version in
            Set(state.battleItems.filter { $0.contentVersion == version }.map(\.groupID)).isSuperset(of: groupIDs)
        }) else { throw LocalBackendError.invalidBattleContent }
        let items = groupIDs.flatMap { groupID in
            state.battleItems.filter { $0.contentVersion == contentVersion && $0.groupID == groupID }
        }
        guard !items.isEmpty, items.allSatisfy({
            $0.purpose == .battle &&
            $0.prompt?.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty == false &&
            $0.options.count >= 2
        }) else { throw LocalBackendError.invalidBattleContent }
        let match = BattleMatch(
            id: UUID(), requestID: requestID, state: .invited, contentVersion: contentVersion,
            groupIDs: groupIDs, orderedItemIDs: items.map(\.itemID), invitationExpiresAt: .now.addingTimeInterval(86_400),
            startsAt: nil, deadline: nil,
            participants: [.init(id: actorID, state: .accepted, progress: 0, serverScore: nil),
                           .init(id: opponentID, state: .invited, progress: 0, serverScore: nil)],
            winnerID: nil, isReviewRematch: false
        )
        state.matches.append(match)
        try persist()
        return visibleMatch(match, actorID: actorID)
    }

    fileprivate func listMatches(actorID: UUID) throws -> [BattleMatch] {
        try requireUser(actorID)
        try reconcileMatches()
        return state.matches.filter { $0.participants.contains(where: { $0.id == actorID }) }
            .sorted { $0.invitationExpiresAt > $1.invitationExpiresAt }
            .map { visibleMatch($0, actorID: actorID) }
    }

    fileprivate func battleQuestions(actorID: UUID, matchID: UUID) throws -> [BattleQuestion] {
        let index = try participantMatchIndex(actorID, matchID)
        let match = state.matches[index]
        let items = Dictionary(uniqueKeysWithValues: state.battleItems
            .filter { $0.contentVersion == match.contentVersion && match.orderedItemIDs.contains($0.itemID) }
            .map { ($0.itemID, $0.clientQuestion) })
        guard items.count == match.orderedItemIDs.count else { throw LocalBackendError.invalidBattleContent }
        return match.orderedItemIDs.compactMap { items[$0] }
    }

    fileprivate func acceptMatch(actorID: UUID, matchID: UUID, requestID: UUID) throws -> BattleMatch {
        try reconcileMatches()
        let index = try participantMatchIndex(actorID, matchID)
        if state.battleOperationIDs?.contains(requestID) == true { return visibleMatch(state.matches[index], actorID: actorID) }
        guard state.matches[index].state == .invited else { throw LocalBackendError.invalidTransition }
        state.matches[index].state = .accepted
        if let participant = state.matches[index].participants.firstIndex(where: { $0.id == actorID }) {
            state.matches[index].participants[participant].state = .accepted
        }
        rememberBattleOperation(requestID)
        try persist()
        return visibleMatch(state.matches[index], actorID: actorID)
    }

    fileprivate func ready(actorID: UUID, matchID: UUID, assetChecksums: [String: String], requestID: UUID) throws -> BattleMatch {
        try reconcileMatches()
        let index = try participantMatchIndex(actorID, matchID)
        if state.battleOperationIDs?.contains(requestID) == true { return visibleMatch(state.matches[index], actorID: actorID) }
        guard state.matches[index].state == .accepted || state.matches[index].state == .preparing else { throw LocalBackendError.invalidTransition }
        let itemIDs = Set(state.matches[index].orderedItemIDs)
        let requiredAssets = state.battleItems
            .filter { $0.contentVersion == state.matches[index].contentVersion && itemIDs.contains($0.itemID) }
            .reduce(into: [String: String]()) { result, item in
                for (assetID, checksum) in item.assetChecksums { result[assetID] = checksum }
            }
        guard requiredAssets == assetChecksums else { throw LocalBackendError.battleAssetMismatch }
        state.matches[index].state = .preparing
        if let participant = state.matches[index].participants.firstIndex(where: { $0.id == actorID }) {
            state.matches[index].participants[participant].state = .ready
        }
        if state.matches[index].participants.allSatisfy({ $0.state == .ready }) {
            let now = Date.now
            state.matches[index].state = .active
            state.matches[index].startsAt = now
            state.matches[index].deadline = now.addingTimeInterval(600)
            for participant in state.matches[index].participants.indices { state.matches[index].participants[participant].state = .active }
        }
        rememberBattleOperation(requestID)
        try persist()
        return visibleMatch(state.matches[index], actorID: actorID)
    }

    fileprivate func submitAnswer(actorID: UUID, matchID: UUID, itemID: String, optionID: String, requestID: UUID) throws {
        try reconcileMatches()
        let index = try participantMatchIndex(actorID, matchID)
        if let accepted = state.answers.first(where: { $0.userID == actorID && $0.requestID == requestID }) {
            guard accepted.matchID == matchID, accepted.itemID == itemID, accepted.optionID == optionID else {
                throw LocalBackendError.idempotencyConflict
            }
            return
        }
        guard state.matches[index].state == .active, (state.matches[index].deadline ?? .distantPast) >= .now else { throw LocalBackendError.answerWindowClosed }
        guard state.matches[index].participants.first(where: { $0.id == actorID })?.state == .active else {
            throw LocalBackendError.answerWindowClosed
        }
        guard state.matches[index].orderedItemIDs.contains(itemID) else { throw LocalBackendError.invalidBattleContent }
        guard !state.answers.contains(where: { $0.matchID == matchID && $0.userID == actorID && $0.itemID == itemID }) else { throw LocalBackendError.answerAlreadyAccepted }
        state.answers.append(.init(matchID: matchID, userID: actorID, itemID: itemID, optionID: optionID, requestID: requestID))
        if let participant = state.matches[index].participants.firstIndex(where: { $0.id == actorID }) {
            state.matches[index].participants[participant].progress += 1
        }
        try persist()
    }

    fileprivate func submitMatch(actorID: UUID, matchID: UUID, requestID: UUID) throws -> BattleMatch {
        try reconcileMatches()
        let index = try participantMatchIndex(actorID, matchID)
        if state.battleOperationIDs?.contains(requestID) == true { return visibleMatch(state.matches[index], actorID: actorID) }
        guard state.matches[index].state == .active else { throw LocalBackendError.invalidTransition }
        if let participant = state.matches[index].participants.firstIndex(where: { $0.id == actorID }) {
            state.matches[index].participants[participant].state = .submitted
        }
        if state.matches[index].participants.allSatisfy({ $0.state == .submitted }) { settleMatch(index) }
        rememberBattleOperation(requestID)
        try persist()
        return visibleMatch(state.matches[index], actorID: actorID)
    }

    fileprivate func refreshMatch(actorID: UUID, matchID: UUID) throws -> BattleMatch {
        try reconcileMatches()
        let index = try participantMatchIndex(actorID, matchID)
        return visibleMatch(state.matches[index], actorID: actorID)
    }

    fileprivate func reportIssue(actorID: UUID, groupID: String, itemID: String?, category: String, details: String, requestID: UUID) throws {
        try requireUser(actorID)
        guard !details.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty else { throw LocalBackendError.invalidIssue }
        guard !state.issues.contains(where: { $0.reporterID == actorID && $0.requestID == requestID }) else { return }
        state.issues.append(.init(reporterID: actorID, requestID: requestID, groupID: groupID, itemID: itemID, category: category, details: details))
        try persist()
    }

    private func settleMatch(_ index: Int) {
        state.matches[index].state = .settling
        let matchID = state.matches[index].id
        let keys = Dictionary(uniqueKeysWithValues: state.battleItems
            .filter { $0.contentVersion == state.matches[index].contentVersion && state.matches[index].orderedItemIDs.contains($0.itemID) }
            .map { ($0.itemID, $0.correctOptionID) })
        for participant in state.matches[index].participants.indices {
            let userID = state.matches[index].participants[participant].id
            let score = state.answers.filter { $0.matchID == matchID && $0.userID == userID && keys[$0.itemID] == $0.optionID }.count * 100
            state.matches[index].participants[participant].serverScore = score
            state.matches[index].participants[participant].state = .completed
        }
        let scores = state.matches[index].participants.compactMap { participant in participant.serverScore.map { (participant.id, $0) } }
        if scores.count == 2, scores[0].1 != scores[1].1 { state.matches[index].winnerID = scores.max(by: { $0.1 < $1.1 })?.0 }
        state.matches[index].state = .completed
    }

    /// Local recovery scanner. Production uses the same rules from a durable scheduled worker.
    private func reconcileMatches(now: Date = .now) throws {
        var changed = false
        for index in state.matches.indices {
            if state.matches[index].state == .invited, state.matches[index].invitationExpiresAt <= now {
                state.matches[index].state = .expired
                for participant in state.matches[index].participants.indices
                where state.matches[index].participants[participant].state == .invited {
                    state.matches[index].participants[participant].state = .timedOut
                }
                changed = true
            } else if state.matches[index].state == .active,
                      let deadline = state.matches[index].deadline, deadline <= now {
                for participant in state.matches[index].participants.indices
                where state.matches[index].participants[participant].state != .submitted {
                    state.matches[index].participants[participant].state = .timedOut
                }
                settleMatch(index)
                changed = true
            }
        }
        if changed { try persist() }
    }

    private func rememberBattleOperation(_ requestID: UUID) {
        if state.battleOperationIDs == nil { state.battleOperationIDs = [] }
        state.battleOperationIDs?.insert(requestID)
    }

    private func visibleMatch(_ match: BattleMatch, actorID: UUID) -> BattleMatch {
        guard match.state != .completed else { return match }
        var hidden = match
        hidden.winnerID = nil
        hidden.participants = hidden.participants.map {
            .init(id: $0.id, state: $0.state, progress: $0.progress, serverScore: $0.id == actorID ? nil : nil)
        }
        return hidden
    }

    private func participantMatchIndex(_ actorID: UUID, _ matchID: UUID) throws -> Int {
        guard let index = state.matches.firstIndex(where: { $0.id == matchID && $0.participants.contains(where: { $0.id == actorID }) }) else {
            throw LocalBackendError.forbidden
        }
        return index
    }

    private func requireMessagingAccess(_ actorID: UUID, _ otherID: UUID, allowRemoved: Bool) throws {
        try requireUser(actorID); try requireUser(otherID)
        guard !isBlocked(actorID, otherID) else { throw LocalBackendError.blocked }
        guard let relation = friendship(actorID, otherID), relation.accepted, allowRemoved || !relation.removed else { throw LocalBackendError.notFriends }
    }

    private func friendSummary(userID: UUID, viewerID: UUID) throws -> FriendSummary {
        guard let identity = state.users.first(where: { $0.userID == userID }) else { throw LocalBackendError.userNotFound }
        let conversation = state.conversations.first { pairMatches($0.firstID, $0.secondID, userID, viewerID) }
        let unread = conversation.map { conversation in state.messages.filter { $0.conversationID == conversation.id && $0.senderID == userID }.count } ?? 0
        return .init(id: userID, displayName: identity.displayName, handle: "@\(identity.email.split(separator: "@").first ?? "learner")",
                     isBlocked: isBlocked(viewerID, userID), unreadCount: unread)
    }

    private func friendship(_ first: UUID, _ second: UUID) -> Friendship? {
        state.friendships.first { pairMatches($0.firstID, $0.secondID, first, second) }
    }

    private func isBlocked(_ first: UUID, _ second: UUID) -> Bool {
        state.blocks.contains { ($0.blockerID == first && $0.blockedID == second) || ($0.blockerID == second && $0.blockedID == first) }
    }

    private func pairMatches(_ a: UUID, _ b: UUID, _ first: UUID, _ second: UUID) -> Bool {
        (a == first && b == second) || (a == second && b == first)
    }

    private func requireUser(_ id: UUID) throws {
        try ensureStorageReadable()
        guard state.users.contains(where: { $0.userID == id }) else { throw LocalBackendError.userNotFound }
    }

    private func ensureStorageReadable() throws {
        if let loadFailure { throw LocalBackendError.corruptState(loadFailure) }
    }

    private func normalize(_ email: String) throws -> String {
        let normalized = email.trimmingCharacters(in: .whitespacesAndNewlines).lowercased()
        guard normalized.contains("@"), normalized.count <= 254 else { throw LocalBackendError.invalidEmail }
        return normalized
    }

    private func inviteURL(_ code: String) -> URL { URL(string: "toeicpath://invite/\(code)")! }

    private func persist() throws {
        try FileManager.default.createDirectory(at: storeURL.deletingLastPathComponent(), withIntermediateDirectories: true)
        let encoder = JSONEncoder()
        encoder.dateEncodingStrategy = .iso8601
        encoder.outputFormatting = [.sortedKeys]
        try encoder.encode(state).write(to: storeURL, options: .atomic)
    }
}

actor LocalBackendClient: AppBackendService {
    private let hub: LocalBackendHub
    private(set) var identity: AuthIdentity?

    init(hub: LocalBackendHub) { self.hub = hub }

    func configureBattleItems(_ items: [LocalBattleItem]) async throws { try await hub.registerBattleItems(items) }
    func signOut() { identity = nil }

    func requestEmailCode(email: String) async throws { try await hub.requestCode(email: email) }
    func verifyEmailCode(email: String, code: String) async throws -> AuthIdentity {
        let value = try await hub.verify(email: email, code: code)
        identity = value
        return value
    }
    func mergeLocalProfile(_ profile: LocalProfile, into identity: AuthIdentity, requestID: UUID) async throws {
        guard try actorID() == identity.userID else { throw LocalBackendError.forbidden }
        try await hub.merge(profile: profile, actorID: identity.userID, requestID: requestID)
    }
    func createInvite(requestID: UUID) async throws -> URL { try await hub.createInvite(actorID: try actorID(), requestID: requestID) }
    func acceptInvite(code: String, requestID _: UUID) async throws -> FriendSummary { try await hub.acceptInvite(code: code, actorID: try actorID()) }
    func listFriends() async throws -> [FriendSummary] { try await hub.listFriends(actorID: try actorID()) }
    func conversationID(with friendID: UUID) async throws -> UUID { try await hub.conversationID(actorID: try actorID(), friendID: friendID) }
    func sendMessage(conversationID: UUID, clientMessageID: UUID, body: String) async throws -> ChatMessage {
        try await hub.sendMessage(actorID: try actorID(), conversationID: conversationID, clientMessageID: clientMessageID, body: body)
    }
    func messages(conversationID: UUID, after: Date?) async throws -> [ChatMessage] {
        try await hub.messages(actorID: try actorID(), conversationID: conversationID, after: after)
    }
    func removeFriend(userID: UUID, requestID _: UUID) async throws { try await hub.removeFriend(actorID: try actorID(), userID: userID) }
    func setBlocked(userID: UUID, blocked: Bool, requestID _: UUID) async throws { try await hub.setBlocked(actorID: try actorID(), userID: userID, blocked: blocked) }
    func createChallenge(opponentID: UUID, groupIDs: [String], requestID: UUID) async throws -> BattleMatch {
        try await hub.createChallenge(actorID: try actorID(), opponentID: opponentID, groupIDs: groupIDs, requestID: requestID)
    }
    func listMatches() async throws -> [BattleMatch] { try await hub.listMatches(actorID: try actorID()) }
    func battleQuestions(matchID: UUID) async throws -> [BattleQuestion] {
        try await hub.battleQuestions(actorID: try actorID(), matchID: matchID)
    }
    func accept(matchID: UUID, requestID: UUID) async throws -> BattleMatch {
        try await hub.acceptMatch(actorID: try actorID(), matchID: matchID, requestID: requestID)
    }
    func ready(matchID: UUID, assetChecksums: [String: String], requestID: UUID) async throws -> BattleMatch {
        try await hub.ready(actorID: try actorID(), matchID: matchID, assetChecksums: assetChecksums, requestID: requestID)
    }
    func submitAnswer(matchID: UUID, itemID: String, optionID: String, requestID: UUID) async throws {
        try await hub.submitAnswer(actorID: try actorID(), matchID: matchID, itemID: itemID, optionID: optionID, requestID: requestID)
    }
    func submitMatch(matchID: UUID, requestID: UUID) async throws -> BattleMatch {
        try await hub.submitMatch(actorID: try actorID(), matchID: matchID, requestID: requestID)
    }
    func refresh(matchID: UUID) async throws -> BattleMatch { try await hub.refreshMatch(actorID: try actorID(), matchID: matchID) }
    func report(groupID: String, itemID: String?, category: String, details: String, requestID: UUID) async throws {
        try await hub.reportIssue(actorID: try actorID(), groupID: groupID, itemID: itemID, category: category, details: details, requestID: requestID)
    }

    private func actorID() throws -> UUID {
        guard let identity else { throw LocalBackendError.notAuthenticated }
        return identity.userID
    }
}

enum LocalBackendError: LocalizedError {
    case invalidEmail, invalidCode, notAuthenticated, userNotFound, inviteNotFound, inviteExpired, cannotInviteSelf
    case blocked, notFriends, conversationNotFound, forbidden, invalidMessage, invalidBattleContent
    case invalidTransition, answerWindowClosed, answerAlreadyAccepted, idempotencyConflict, battleAssetMismatch, invalidIssue, corruptState(String)

    var errorDescription: String? {
        switch self {
        case .invalidEmail: "Email 格式不正確。"
        case .invalidCode: "驗證碼錯誤或尚未要求驗證碼。"
        case .notAuthenticated: "請先登入。"
        case .userNotFound: "找不到帳號。"
        case .inviteNotFound: "邀請碼不存在。"
        case .inviteExpired: "邀請已過期。"
        case .cannotInviteSelf: "不能接受自己的邀請。"
        case .blocked: "任一方封鎖後，伺服器拒絕這項操作。"
        case .notFriends: "目前不是可互動的好友。"
        case .conversationNotFound: "找不到對話。"
        case .forbidden: "沒有權限執行這項操作。"
        case .invalidMessage: "訊息必須為 1–4000 個字元。"
        case .invalidBattleContent: "對戰題目或版本無效。"
        case .invalidTransition: "目前對戰狀態不允許這項操作。"
        case .answerWindowClosed: "伺服器已關閉作答時窗。"
        case .answerAlreadyAccepted: "這題已有伺服器接受的答案。"
        case .idempotencyConflict: "相同請求 ID 已用於不同作答資料。"
        case .battleAssetMismatch: "對戰所需素材缺少或雜湊不一致，不能開始。"
        case .invalidIssue: "問題回報內容不可為空。"
        case .corruptState(let detail): "本機服務資料無法解碼，為避免覆寫已停止操作：\(detail)"
        }
    }
}
