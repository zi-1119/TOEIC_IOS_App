import XCTest
@testable import TOEICPath

final class LocalBackendIntegrationTests: XCTestCase {
    func testCorruptPersistentStateIsNotSilentlyOverwritten() async throws {
        let url = temporaryStateURL(name: "corrupt")
        try Data("not-json".utf8).write(to: url)
        let hub = LocalBackendHub(storeURL: url)
        let client = await hub.makeClient()
        await XCTAssertThrowsErrorAsync { try await client.requestEmailCode(email: "alice@example.test") }
        XCTAssertEqual(try Data(contentsOf: url), Data("not-json".utf8))
    }

    func testTwoAccountsFriendChatDedupBlockAndRemovalPermissionsPersist() async throws {
        let storeURL = temporaryStateURL(name: "social")
        let hub = LocalBackendHub(storeURL: storeURL)
        let alice = await hub.makeClient()
        let bob = await hub.makeClient()
        let aliceIdentity = try await signIn(alice, email: "alice@example.test")
        let bobIdentity = try await signIn(bob, email: "bob@example.test")

        let invite = try await alice.createInvite(requestID: UUID())
        let code = try XCTUnwrap(invite.pathComponents.last)
        _ = try await bob.acceptInvite(code: code, requestID: UUID())
        let aliceFriends = try await alice.listFriends()
        let bobFriends = try await bob.listFriends()
        XCTAssertEqual(aliceFriends.map(\.id), [bobIdentity.userID])
        XCTAssertEqual(bobFriends.map(\.id), [aliceIdentity.userID])

        let aliceConversation = try await alice.conversationID(with: bobIdentity.userID)
        let bobConversation = try await bob.conversationID(with: aliceIdentity.userID)
        XCTAssertEqual(aliceConversation, bobConversation)
        let clientMessageID = UUID()
        let first = try await alice.sendMessage(conversationID: aliceConversation, clientMessageID: clientMessageID, body: "Ready to study?")
        let duplicate = try await alice.sendMessage(conversationID: aliceConversation, clientMessageID: clientMessageID, body: "Ready to study?")
        XCTAssertEqual(first.id, duplicate.id)
        let initialMessages = try await bob.messages(conversationID: bobConversation, after: nil)
        XCTAssertEqual(initialMessages.count, 1)

        try await alice.setBlocked(userID: bobIdentity.userID, blocked: true, requestID: UUID())
        await XCTAssertThrowsErrorAsync { try await bob.sendMessage(conversationID: bobConversation, clientMessageID: UUID(), body: "blocked") }
        await XCTAssertThrowsErrorAsync { try await bob.messages(conversationID: bobConversation, after: nil) }
        try await alice.setBlocked(userID: bobIdentity.userID, blocked: false, requestID: UUID())
        try await alice.removeFriend(userID: bobIdentity.userID, requestID: UUID())
        await XCTAssertThrowsErrorAsync { try await bob.sendMessage(conversationID: bobConversation, clientMessageID: UUID(), body: "removed") }
        let retainedMessages = try await bob.messages(conversationID: bobConversation, after: nil)
        XCTAssertEqual(retainedMessages.count, 1, "history remains readable after removal")

        let reopenedHub = LocalBackendHub(storeURL: storeURL)
        let reopenedAlice = await reopenedHub.makeClient()
        let reopenedIdentity = try await signIn(reopenedAlice, email: "alice@example.test")
        XCTAssertEqual(reopenedIdentity.userID, aliceIdentity.userID, "auth identity must remain stable")
        let reopenedFriends = try await reopenedAlice.listFriends()
        XCTAssertTrue(reopenedFriends.isEmpty)
    }

    func testServerAuthoritativeBattleSettlementAndAnswerDedup() async throws {
        let hub = LocalBackendHub(storeURL: temporaryStateURL(name: "battle"))
        try await hub.registerBattleItems([battleItem(groupID: "g-p5", itemID: "i-p5", answer: "B", version: "v1")])
        let alice = await hub.makeClient()
        let bob = await hub.makeClient()
        let outsider = await hub.makeClient()
        let aliceID = try await signIn(alice, email: "alice@example.test")
        let bobID = try await signIn(bob, email: "bob@example.test")
        _ = try await signIn(outsider, email: "eve@example.test")
        let invite = try await alice.createInvite(requestID: UUID())
        _ = try await bob.acceptInvite(code: try XCTUnwrap(invite.pathComponents.last), requestID: UUID())

        let match = try await alice.createChallenge(opponentID: bobID.userID, groupIDs: ["g-p5"], requestID: UUID())
        let questions = try await alice.battleQuestions(matchID: match.id)
        XCTAssertEqual(questions.map(\.id), ["i-p5"])
        XCTAssertEqual(questions.first?.options.count, 4)
        let listedMatches = try await bob.listMatches()
        XCTAssertEqual(listedMatches.map(\.id), [match.id])
        let acceptRequest = UUID()
        _ = try await bob.accept(matchID: match.id, requestID: acceptRequest)
        let repeatedAccept = try await bob.accept(matchID: match.id, requestID: acceptRequest)
        XCTAssertEqual(repeatedAccept.state, .accepted)
        let readyRequest = UUID()
        let preparing = try await alice.ready(matchID: match.id, assetChecksums: [:], requestID: readyRequest)
        XCTAssertEqual(preparing.state, .preparing)
        let repeatedReady = try await alice.ready(matchID: match.id, assetChecksums: [:], requestID: readyRequest)
        XCTAssertEqual(repeatedReady.state, .preparing)
        let active = try await bob.ready(matchID: match.id, assetChecksums: [:], requestID: UUID())
        XCTAssertEqual(active.state, .active)
        XCTAssertNotNil(active.deadline)

        try await hub.registerBattleItems([battleItem(groupID: "g-new", itemID: "i-new", answer: "C", version: "v2")])

        let answerRequest = UUID()
        try await alice.submitAnswer(matchID: match.id, itemID: "i-p5", optionID: "B", requestID: answerRequest)
        try await alice.submitAnswer(matchID: match.id, itemID: "i-p5", optionID: "B", requestID: answerRequest)
        try await bob.submitAnswer(matchID: match.id, itemID: "i-p5", optionID: "A", requestID: UUID())
        let submitRequest = UUID()
        _ = try await alice.submitMatch(matchID: match.id, requestID: submitRequest)
        try await alice.submitAnswer(matchID: match.id, itemID: "i-p5", optionID: "B", requestID: answerRequest)
        await XCTAssertThrowsErrorAsync {
            try await alice.submitAnswer(matchID: match.id, itemID: "i-p5", optionID: "A", requestID: UUID())
        }
        let completed = try await bob.submitMatch(matchID: match.id, requestID: UUID())
        let repeatedSubmit = try await alice.submitMatch(matchID: match.id, requestID: submitRequest)
        XCTAssertEqual(repeatedSubmit.state, .completed)
        XCTAssertEqual(completed.state, .completed)
        XCTAssertEqual(completed.winnerID, aliceID.userID)
        XCTAssertEqual(completed.participants.first { $0.id == aliceID.userID }?.serverScore, 100)
        XCTAssertEqual(completed.participants.first { $0.id == bobID.userID }?.serverScore, 0)
        await XCTAssertThrowsErrorAsync { try await outsider.refresh(matchID: match.id) }
    }

    func testBackendRejectsTrainingContentRegisteredAsBattle() async throws {
        let hub = LocalBackendHub(storeURL: temporaryStateURL(name: "wrong-purpose"))
        await XCTAssertThrowsErrorAsync {
            try await hub.registerBattleItems([
                .init(groupID: "training", itemID: "training-item", correctOptionID: "A", contentVersion: "v1", purpose: .training,
                      prompt: "Prompt", options: [.init(id: "A", text: "A"), .init(id: "B", text: "B")])
            ])
        }
    }

    func testBattleReadyRequiresExactFrozenAssetChecksums() async throws {
        let hub = LocalBackendHub(storeURL: temporaryStateURL(name: "assets"))
        try await hub.registerBattleItems([
            .init(groupID: "g-audio", itemID: "i-audio", correctOptionID: "A", contentVersion: "v1", purpose: .battle,
                  prompt: "Listen and choose.", options: [.init(id: "A", text: "A"), .init(id: "B", text: "B")],
                  assetChecksums: ["audio-1": "abc123"])
        ])
        let alice = await hub.makeClient()
        let bob = await hub.makeClient()
        _ = try await signIn(alice, email: "asset-alice@example.test")
        let bobID = try await signIn(bob, email: "asset-bob@example.test")
        let invite = try await alice.createInvite(requestID: UUID())
        _ = try await bob.acceptInvite(code: try XCTUnwrap(invite.pathComponents.last), requestID: UUID())
        let match = try await alice.createChallenge(opponentID: bobID.userID, groupIDs: ["g-audio"], requestID: UUID())
        _ = try await bob.accept(matchID: match.id, requestID: UUID())

        await XCTAssertThrowsErrorAsync {
            try await alice.ready(matchID: match.id, assetChecksums: [:], requestID: UUID())
        }
        let preparing = try await alice.ready(matchID: match.id, assetChecksums: ["audio-1": "abc123"], requestID: UUID())
        XCTAssertEqual(preparing.state, .preparing)
    }

    private func battleItem(groupID: String, itemID: String, answer: String, version: String) -> LocalBattleItem {
        .init(groupID: groupID, itemID: itemID, correctOptionID: answer, contentVersion: version, purpose: .battle,
              prompt: "The report is ___ for review.",
              options: [.init(id: "A", text: "readying"), .init(id: "B", text: "ready"),
                        .init(id: "C", text: "readily"), .init(id: "D", text: "readiness")])
    }

    private func signIn(_ client: LocalBackendClient, email: String) async throws -> AuthIdentity {
        try await client.requestEmailCode(email: email)
        return try await client.verifyEmailCode(email: email, code: LocalBackendHub.verificationCode)
    }

    private func temporaryStateURL(name: String) -> URL {
        let directory = FileManager.default.temporaryDirectory.appending(path: "TOEICPathBackendTests-\(name)-\(UUID().uuidString)")
        try! FileManager.default.createDirectory(at: directory, withIntermediateDirectories: true)
        addTeardownBlock { try? FileManager.default.removeItem(at: directory) }
        return directory.appending(path: "state.json")
    }
}

private func XCTAssertThrowsErrorAsync<T>(
    _ expression: () async throws -> T,
    file: StaticString = #filePath,
    line: UInt = #line
) async {
    do {
        _ = try await expression()
        XCTFail("Expected error", file: file, line: line)
    } catch { }
}
