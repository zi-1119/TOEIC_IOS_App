import Foundation

actor NetworkBackendClient: AppBackendService {
    private struct VerifyResponse: Decodable { let identity: AuthIdentity; let accessToken: String }
    private struct InviteResponse: Decodable { let url: URL }
    private struct ConversationResponse: Decodable { let conversationID: UUID }
    private struct APIErrorBody: Decodable { let error: String; let message: String? }
    private struct EmptyResponse: Decodable { }

    private let configuration: ServerConfiguration
    private let session: URLSession
    private var accessToken: String?
    private(set) var identity: AuthIdentity?

    init(configuration: ServerConfiguration, session: URLSession = .shared) {
        self.configuration = configuration
        self.session = session
    }

    func requestEmailCode(email: String) async throws {
        _ = try await send(EmptyResponse.self, method: "POST", path: "/v1/auth/request-code", body: ["email": email])
    }

    func verifyEmailCode(email: String, code: String) async throws -> AuthIdentity {
        let response = try await send(
            VerifyResponse.self, method: "POST", path: "/v1/auth/verify",
            body: ["email": email, "code": code]
        )
        accessToken = response.accessToken
        identity = response.identity
        return response.identity
    }

    func signOut() async {
        if accessToken != nil { _ = try? await send(EmptyResponse.self, method: "POST", path: "/v1/auth/sign-out") }
        accessToken = nil
        identity = nil
    }

    func mergeLocalProfile(_ profile: LocalProfile, into identity: AuthIdentity, requestID: UUID) async throws {
        guard self.identity?.userID == identity.userID else { throw NetworkBackendError.notAuthenticated }
        let payload = ProfileMergeRequest(requestID: requestID, profile: profile)
        _ = try await send(EmptyResponse.self, method: "POST", path: "/v1/profile/merge", encodableBody: payload)
    }

    func configureBattleItems(_ items: [LocalBattleItem]) async throws {
        let safeItems = items.map {
            BattleCatalogCheckItem(groupID: $0.groupID, itemID: $0.itemID, contentVersion: $0.contentVersion, purpose: $0.purpose)
        }
        _ = try await send(
            EmptyResponse.self, method: "POST", path: "/v1/battles/catalog/check",
            encodableBody: BattleCatalogCheckRequest(items: safeItems)
        )
    }

    func createInvite(requestID: UUID) async throws -> URL {
        try await send(InviteResponse.self, method: "POST", path: "/v1/friends/invites", body: ["requestID": requestID.uuidString]).url
    }

    func acceptInvite(code: String, requestID: UUID) async throws -> FriendSummary {
        try await send(
            FriendSummary.self, method: "POST", path: "/v1/friends/accept",
            body: ["code": code, "requestID": requestID.uuidString]
        )
    }

    func listFriends() async throws -> [FriendSummary] {
        try await send([FriendSummary].self, method: "GET", path: "/v1/friends")
    }

    func conversationID(with friendID: UUID) async throws -> UUID {
        try await send(ConversationResponse.self, method: "GET", path: "/v1/conversations/with/\(friendID.uuidString)").conversationID
    }

    func sendMessage(conversationID: UUID, clientMessageID: UUID, body: String) async throws -> ChatMessage {
        try await send(
            ChatMessage.self, method: "POST", path: "/v1/conversations/\(conversationID.uuidString)/messages",
            body: ["clientMessageID": clientMessageID.uuidString, "body": body]
        )
    }

    func messages(conversationID: UUID, after: Date?) async throws -> [ChatMessage] {
        var components = URLComponents()
        components.queryItems = [URLQueryItem(name: "limit", value: "100")]
        if let after { components.queryItems?.append(.init(name: "after", value: ISO8601DateFormatter().string(from: after))) }
        return try await send(
            [ChatMessage].self, method: "GET",
            path: "/v1/conversations/\(conversationID.uuidString)/messages\(components.percentEncodedQuery.map { "?\($0)" } ?? "")"
        )
    }

    func removeFriend(userID: UUID, requestID: UUID) async throws {
        _ = try await send(
            EmptyResponse.self, method: "DELETE", path: "/v1/friends/\(userID.uuidString)",
            body: ["requestID": requestID.uuidString]
        )
    }

    func setBlocked(userID: UUID, blocked: Bool, requestID: UUID) async throws {
        _ = try await send(
            EmptyResponse.self, method: "POST", path: "/v1/friends/\(userID.uuidString)/block",
            encodableBody: BlockRequest(blocked: blocked, requestID: requestID)
        )
    }

    func listMatches() async throws -> [BattleMatch] {
        try await send([BattleMatch].self, method: "GET", path: "/v1/battles")
    }

    func battleQuestions(matchID: UUID) async throws -> [BattleQuestion] {
        try await send([BattleQuestion].self, method: "GET", path: "/v1/battles/\(matchID.uuidString)/questions")
    }

    func createChallenge(opponentID: UUID, groupIDs: [String], requestID: UUID) async throws -> BattleMatch {
        try await send(
            BattleMatch.self, method: "POST", path: "/v1/battles",
            encodableBody: CreateBattleRequest(opponentID: opponentID, groupIDs: groupIDs, requestID: requestID)
        )
    }

    func accept(matchID: UUID, requestID: UUID) async throws -> BattleMatch {
        try await battleAction(matchID: matchID, action: "accept", requestID: requestID)
    }

    func ready(matchID: UUID, assetChecksums: [String: String], requestID: UUID) async throws -> BattleMatch {
        try await send(
            BattleMatch.self, method: "POST", path: "/v1/battles/\(matchID.uuidString)/ready",
            encodableBody: ReadyBattleRequest(requestID: requestID, assetChecksums: assetChecksums)
        )
    }

    func submitAnswer(matchID: UUID, itemID: String, optionID: String, requestID: UUID) async throws {
        _ = try await send(
            EmptyResponse.self, method: "POST", path: "/v1/battles/\(matchID.uuidString)/answers",
            encodableBody: BattleAnswerRequest(itemID: itemID, optionID: optionID, requestID: requestID)
        )
    }

    func submitMatch(matchID: UUID, requestID: UUID) async throws -> BattleMatch {
        try await battleAction(matchID: matchID, action: "submit", requestID: requestID)
    }

    func refresh(matchID: UUID) async throws -> BattleMatch {
        try await send(BattleMatch.self, method: "GET", path: "/v1/battles/\(matchID.uuidString)")
    }

    func report(groupID: String, itemID: String?, category: String, details: String, requestID: UUID) async throws {
        _ = try await send(
            EmptyResponse.self, method: "POST", path: "/v1/content/issues",
            encodableBody: ContentIssueRequest(groupID: groupID, itemID: itemID, category: category, details: details, requestID: requestID)
        )
    }

    private func battleAction(matchID: UUID, action: String, requestID: UUID) async throws -> BattleMatch {
        try await send(
            BattleMatch.self, method: "POST", path: "/v1/battles/\(matchID.uuidString)/\(action)",
            body: ["requestID": requestID.uuidString]
        )
    }

    private func send<Response: Decodable>(
        _ responseType: Response.Type,
        method: String,
        path: String,
        body: [String: String]? = nil
    ) async throws -> Response {
        let data = try body.map { try JSONSerialization.data(withJSONObject: $0, options: [.sortedKeys]) }
        return try await sendData(responseType, method: method, path: path, bodyData: data)
    }

    private func send<Response: Decodable, Body: Encodable>(
        _ responseType: Response.Type,
        method: String,
        path: String,
        encodableBody: Body
    ) async throws -> Response {
        return try await sendData(responseType, method: method, path: path, bodyData: try Self.makeEncoder().encode(encodableBody))
    }

    private func sendData<Response: Decodable>(
        _ responseType: Response.Type,
        method: String,
        path: String,
        bodyData: Data? = nil
    ) async throws -> Response {
        guard let url = URL(string: path, relativeTo: configuration.baseURL) else { throw NetworkBackendError.invalidURL }
        var request = URLRequest(url: url)
        request.httpMethod = method
        request.httpBody = bodyData
        request.setValue("application/json", forHTTPHeaderField: "Accept")
        request.setValue(configuration.publicClientID, forHTTPHeaderField: "X-Public-Client-ID")
        if bodyData != nil { request.setValue("application/json", forHTTPHeaderField: "Content-Type") }
        if let accessToken { request.setValue("Bearer \(accessToken)", forHTTPHeaderField: "Authorization") }
        let (data, response) = try await session.data(for: request)
        guard let http = response as? HTTPURLResponse else { throw NetworkBackendError.invalidResponse }
        guard (200..<300).contains(http.statusCode) else {
            let api = try? Self.makeDecoder().decode(APIErrorBody.self, from: data)
            throw NetworkBackendError.server(status: http.statusCode, code: api?.error ?? "unknown", message: api?.message)
        }
        if responseType == EmptyResponse.self, data.isEmpty || data == Data("{}".utf8) {
            return EmptyResponse() as! Response
        }
        return try Self.makeDecoder().decode(responseType, from: data)
    }

    private static func makeEncoder() -> JSONEncoder {
        let value = JSONEncoder(); value.dateEncodingStrategy = .iso8601; return value
    }
    private static func makeDecoder() -> JSONDecoder {
        let value = JSONDecoder(); value.dateDecodingStrategy = .iso8601; return value
    }
}

private struct ProfileMergeRequest: Encodable { let requestID: UUID; let profile: LocalProfile }
private struct BattleCatalogCheckRequest: Encodable { let items: [BattleCatalogCheckItem] }
private struct BattleCatalogCheckItem: Encodable {
    let groupID: String; let itemID: String; let contentVersion: String; let purpose: ContentPurpose?
}
private struct BlockRequest: Encodable { let blocked: Bool; let requestID: UUID }
private struct CreateBattleRequest: Encodable { let opponentID: UUID; let groupIDs: [String]; let requestID: UUID }
private struct ReadyBattleRequest: Encodable { let requestID: UUID; let assetChecksums: [String: String] }
private struct BattleAnswerRequest: Encodable { let itemID: String; let optionID: String; let requestID: UUID }
private struct ContentIssueRequest: Encodable {
    let groupID: String; let itemID: String?; let category: String; let details: String; let requestID: UUID
}

enum NetworkBackendError: LocalizedError {
    case invalidURL, invalidResponse, notAuthenticated
    case server(status: Int, code: String, message: String?)

    var errorDescription: String? {
        switch self {
        case .invalidURL: "後端 URL 無效。"
        case .invalidResponse: "後端回應格式無效。"
        case .notAuthenticated: "請先登入。"
        case let .server(status, code, message): "後端錯誤 \(status) / \(code)：\(message ?? "未提供細節")"
        }
    }
}
