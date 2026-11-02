import Foundation

struct AuthIdentity: Codable, Hashable, Sendable {
    let userID: UUID
    let email: String
    let displayName: String
}

struct OutboxOperation: Identifiable, Codable, Hashable, Sendable {
    enum Kind: String, Codable, Sendable { case uploadSession, sendMessage, submitBattleAnswer, reportContent }
    let id: UUID
    let kind: Kind
    let idempotencyKey: UUID
    let createdAt: Date
    let payload: Data
    var attemptCount: Int
}

protocol AccountService: Sendable {
    func requestEmailCode(email: String) async throws
    func verifyEmailCode(email: String, code: String) async throws -> AuthIdentity
    func mergeLocalProfile(_ profile: LocalProfile, into identity: AuthIdentity, requestID: UUID) async throws
}

protocol SocialService: Sendable {
    func createInvite(requestID: UUID) async throws -> URL
    func acceptInvite(code: String, requestID: UUID) async throws -> FriendSummary
    func listFriends() async throws -> [FriendSummary]
    func sendMessage(conversationID: UUID, clientMessageID: UUID, body: String) async throws -> ChatMessage
    func messages(conversationID: UUID, after: Date?) async throws -> [ChatMessage]
    func removeFriend(userID: UUID, requestID: UUID) async throws
    func setBlocked(userID: UUID, blocked: Bool, requestID: UUID) async throws
}

protocol BattleService: Sendable {
    func listMatches() async throws -> [BattleMatch]
    func battleQuestions(matchID: UUID) async throws -> [BattleQuestion]
    func createChallenge(opponentID: UUID, groupIDs: [String], requestID: UUID) async throws -> BattleMatch
    func accept(matchID: UUID, requestID: UUID) async throws -> BattleMatch
    func ready(matchID: UUID, assetChecksums: [String: String], requestID: UUID) async throws -> BattleMatch
    func submitAnswer(matchID: UUID, itemID: String, optionID: String, requestID: UUID) async throws
    func submitMatch(matchID: UUID, requestID: UUID) async throws -> BattleMatch
    func refresh(matchID: UUID) async throws -> BattleMatch
}

protocol ContentIssueService: Sendable {
    func report(groupID: String, itemID: String?, category: String, details: String, requestID: UUID) async throws
}

protocol AppBackendService: AccountService, SocialService, BattleService, ContentIssueService {
    func configureBattleItems(_ items: [LocalBattleItem]) async throws
    func signOut() async
    func conversationID(with friendID: UUID) async throws -> UUID
}

struct ServerConfiguration: Sendable {
    let baseURL: URL
    let publicClientID: String

    static func fromBundle(_ bundle: Bundle = .main) -> ServerConfiguration? {
        guard let rawURL = bundle.object(forInfoDictionaryKey: "SERVER_BASE_URL") as? String,
              let url = URL(string: rawURL),
              let clientID = bundle.object(forInfoDictionaryKey: "SERVER_PUBLIC_CLIENT_ID") as? String,
              !clientID.isEmpty else { return nil }
        return .init(baseURL: url, publicClientID: clientID)
    }
}

enum BackendComposition {
    static func make(bundle: Bundle = .main) -> any AppBackendService {
        if let configuration = ServerConfiguration.fromBundle(bundle) {
            return NetworkBackendClient(configuration: configuration)
        }
        return LocalBackendClient(hub: LocalBackendHub())
    }
}
