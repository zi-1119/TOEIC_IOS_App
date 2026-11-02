import Foundation
import Darwin
import XCTest
@testable import TOEICPath

final class NetworkBackendIntegrationTests: XCTestCase {
    func testTwoIndependentHTTPClientsPersistChatDedupAndPermissionsAcrossRestart() async throws {
        let fixture = try makeServerFixture(name: "social")
        var server = try startServer(fixture: fixture)
        let alice = NetworkBackendClient(configuration: server.configuration)
        let bob = NetworkBackendClient(configuration: server.configuration)
        let eve = NetworkBackendClient(configuration: server.configuration)
        let aliceIdentity = try await signIn(alice, email: "alice@example.test")
        let bobIdentity = try await signIn(bob, email: "bob@example.test")
        _ = try await signIn(eve, email: "eve@example.test")

        let invite = try await alice.createInvite(requestID: UUID())
        _ = try await bob.acceptInvite(code: try XCTUnwrap(invite.pathComponents.last), requestID: UUID())
        let aliceFriends = try await alice.listFriends()
        let bobFriends = try await bob.listFriends()
        XCTAssertEqual(aliceFriends.map(\.id), [bobIdentity.userID])
        XCTAssertEqual(bobFriends.map(\.id), [aliceIdentity.userID])

        let aliceConversation = try await alice.conversationID(with: bobIdentity.userID)
        let bobConversation = try await bob.conversationID(with: aliceIdentity.userID)
        XCTAssertEqual(aliceConversation, bobConversation)
        let clientMessageID = UUID()
        let first = try await alice.sendMessage(conversationID: aliceConversation, clientMessageID: clientMessageID, body: "Network hello")
        let duplicate = try await alice.sendMessage(conversationID: aliceConversation, clientMessageID: clientMessageID, body: "Network hello")
        XCTAssertEqual(first.id, duplicate.id)
        let initialMessages = try await bob.messages(conversationID: bobConversation, after: nil)
        XCTAssertEqual(initialMessages.count, 1)

        try await alice.setBlocked(userID: bobIdentity.userID, blocked: true, requestID: UUID())
        await XCTAssertThrowsNetworkError { try await bob.sendMessage(conversationID: bobConversation, clientMessageID: UUID(), body: "blocked") }
        await XCTAssertThrowsNetworkError { try await eve.conversationID(with: aliceIdentity.userID) }
        try await alice.setBlocked(userID: bobIdentity.userID, blocked: false, requestID: UUID())
        try await alice.removeFriend(userID: bobIdentity.userID, requestID: UUID())
        await XCTAssertThrowsNetworkError { try await bob.sendMessage(conversationID: bobConversation, clientMessageID: UUID(), body: "removed") }
        let retainedMessages = try await bob.messages(conversationID: bobConversation, after: nil)
        XCTAssertEqual(retainedMessages.count, 1)

        server.stop()
        server = try startServer(fixture: fixture)
        let reopenedAlice = NetworkBackendClient(configuration: server.configuration)
        let reopenedIdentity = try await signIn(reopenedAlice, email: "alice@example.test")
        XCTAssertEqual(reopenedIdentity.userID, aliceIdentity.userID)
        let reopenedFriends = try await reopenedAlice.listFriends()
        XCTAssertTrue(reopenedFriends.isEmpty)
    }

    func testHTTPBattleIsServerScoredAndDurableWorkerSettlesWithoutClients() async throws {
        let fixture = try makeServerFixture(name: "battle")
        let server = try startServer(fixture: fixture, battleSeconds: 1)
        let alice = NetworkBackendClient(configuration: server.configuration)
        let bob = NetworkBackendClient(configuration: server.configuration)
        let eve = NetworkBackendClient(configuration: server.configuration)
        let aliceIdentity = try await signIn(alice, email: "battle-alice@example.test")
        let bobIdentity = try await signIn(bob, email: "battle-bob@example.test")
        _ = try await signIn(eve, email: "battle-eve@example.test")
        let invite = try await alice.createInvite(requestID: UUID())
        _ = try await bob.acceptInvite(code: try XCTUnwrap(invite.pathComponents.last), requestID: UUID())

        try await alice.configureBattleItems(safeBattleDescriptors)
        try await bob.configureBattleItems(safeBattleDescriptors)
        let match = try await alice.createChallenge(opponentID: bobIdentity.userID, groupIDs: ["battle-group"], requestID: UUID())
        _ = try await bob.accept(matchID: match.id, requestID: UUID())
        let questions = try await alice.battleQuestions(matchID: match.id)
        XCTAssertEqual(questions.map(\.id), ["battle-item", "battle-item-2"])
        XCTAssertEqual(questions.first?.prompt, "The report is ___ for review.")
        XCTAssertEqual(questions.first?.options.map(\.id), ["A", "B", "C", "D"])
        _ = try await alice.ready(matchID: match.id, assetChecksums: [:], requestID: UUID())
        let active = try await bob.ready(matchID: match.id, assetChecksums: [:], requestID: UUID())
        XCTAssertEqual(active.state, .active)
        let answerRequest = UUID()
        try await alice.submitAnswer(matchID: match.id, itemID: "battle-item", optionID: "B", requestID: answerRequest)
        try await alice.submitAnswer(matchID: match.id, itemID: "battle-item", optionID: "B", requestID: answerRequest)
        try await bob.submitAnswer(matchID: match.id, itemID: "battle-item", optionID: "A", requestID: UUID())
        _ = try await alice.submitMatch(matchID: match.id, requestID: UUID())
        let completed = try await bob.submitMatch(matchID: match.id, requestID: UUID())
        XCTAssertEqual(completed.state, .completed)
        XCTAssertEqual(completed.winnerID, aliceIdentity.userID)
        XCTAssertEqual(completed.participants.first { $0.id == aliceIdentity.userID }?.serverScore, 100)
        XCTAssertEqual(completed.participants.first { $0.id == bobIdentity.userID }?.serverScore, 0)
        await XCTAssertThrowsNetworkError { try await eve.refresh(matchID: match.id) }

        let timeoutMatch = try await alice.createChallenge(opponentID: bobIdentity.userID, groupIDs: ["battle-group"], requestID: UUID())
        _ = try await bob.accept(matchID: timeoutMatch.id, requestID: UUID())
        _ = try await alice.ready(matchID: timeoutMatch.id, assetChecksums: [:], requestID: UUID())
        _ = try await bob.ready(matchID: timeoutMatch.id, assetChecksums: [:], requestID: UUID())
        await alice.signOut()
        await bob.signOut()
        try await Task.sleep(for: .seconds(2))

        let reconnectedAlice = NetworkBackendClient(configuration: server.configuration)
        _ = try await signIn(reconnectedAlice, email: "battle-alice@example.test")
        let settledWithoutClients = try await reconnectedAlice.refresh(matchID: timeoutMatch.id)
        XCTAssertEqual(settledWithoutClients.state, .completed)
        XCTAssertTrue(settledWithoutClients.participants.allSatisfy { $0.state == .timedOut })
    }

    func testHTTPRejectsNewAnswersAfterSubmitButAllowsExactReplayAcrossRestart() async throws {
        let fixture = try makeServerFixture(name: "post-submit")
        var server = try startServer(fixture: fixture)
        let alice = NetworkBackendClient(configuration: server.configuration)
        let bob = NetworkBackendClient(configuration: server.configuration)
        let aliceIdentity = try await signIn(alice, email: "submit-alice@example.test")
        let bobIdentity = try await signIn(bob, email: "submit-bob@example.test")
        let invite = try await alice.createInvite(requestID: UUID())
        _ = try await bob.acceptInvite(code: try XCTUnwrap(invite.pathComponents.last), requestID: UUID())
        try await alice.configureBattleItems(safeBattleDescriptors)
        let match = try await alice.createChallenge(opponentID: bobIdentity.userID, groupIDs: ["battle-group"], requestID: UUID())
        _ = try await bob.accept(matchID: match.id, requestID: UUID())
        _ = try await alice.ready(matchID: match.id, assetChecksums: [:], requestID: UUID())
        _ = try await bob.ready(matchID: match.id, assetChecksums: [:], requestID: UUID())

        let acceptedRequestID = UUID()
        try await alice.submitAnswer(matchID: match.id, itemID: "battle-item", optionID: "B", requestID: acceptedRequestID)
        _ = try await alice.submitMatch(matchID: match.id, requestID: UUID())
        try await alice.submitAnswer(matchID: match.id, itemID: "battle-item", optionID: "B", requestID: acceptedRequestID)
        await XCTAssertThrowsNetworkError {
            try await alice.submitAnswer(matchID: match.id, itemID: "battle-item-2", optionID: "C", requestID: UUID())
        }

        server.stop()
        server = try startServer(fixture: fixture)
        let reopenedAlice = NetworkBackendClient(configuration: server.configuration)
        let reopenedBob = NetworkBackendClient(configuration: server.configuration)
        let reopenedIdentity = try await signIn(reopenedAlice, email: "submit-alice@example.test")
        _ = try await signIn(reopenedBob, email: "submit-bob@example.test")
        XCTAssertEqual(reopenedIdentity.userID, aliceIdentity.userID)
        try await reopenedAlice.submitAnswer(matchID: match.id, itemID: "battle-item", optionID: "B", requestID: acceptedRequestID)
        await XCTAssertThrowsNetworkError {
            try await reopenedAlice.submitAnswer(matchID: match.id, itemID: "battle-item-2", optionID: "C", requestID: UUID())
        }
        let completed = try await reopenedBob.submitMatch(matchID: match.id, requestID: UUID())
        XCTAssertEqual(completed.state, .completed)
        XCTAssertEqual(completed.participants.first { $0.id == aliceIdentity.userID }?.serverScore, 100)
    }

    func testHTTPRejectsNewAnswersAfterTimeoutButAllowsAcceptedReplayAfterRestart() async throws {
        let fixture = try makeServerFixture(name: "post-timeout")
        var server = try startServer(fixture: fixture, battleSeconds: 1)
        let alice = NetworkBackendClient(configuration: server.configuration)
        let bob = NetworkBackendClient(configuration: server.configuration)
        let aliceIdentity = try await signIn(alice, email: "timeout-alice@example.test")
        let bobIdentity = try await signIn(bob, email: "timeout-bob@example.test")
        let invite = try await alice.createInvite(requestID: UUID())
        _ = try await bob.acceptInvite(code: try XCTUnwrap(invite.pathComponents.last), requestID: UUID())
        try await alice.configureBattleItems(safeBattleDescriptors)
        let match = try await alice.createChallenge(opponentID: bobIdentity.userID, groupIDs: ["battle-group"], requestID: UUID())
        _ = try await bob.accept(matchID: match.id, requestID: UUID())
        _ = try await alice.ready(matchID: match.id, assetChecksums: [:], requestID: UUID())
        _ = try await bob.ready(matchID: match.id, assetChecksums: [:], requestID: UUID())
        let acceptedRequestID = UUID()
        try await alice.submitAnswer(matchID: match.id, itemID: "battle-item", optionID: "B", requestID: acceptedRequestID)
        try await Task.sleep(for: .seconds(2))
        let timedOut = try await alice.refresh(matchID: match.id)
        XCTAssertEqual(timedOut.state, .completed)

        server.stop()
        server = try startServer(fixture: fixture, battleSeconds: 1)
        let reopenedAlice = NetworkBackendClient(configuration: server.configuration)
        let reopenedIdentity = try await signIn(reopenedAlice, email: "timeout-alice@example.test")
        XCTAssertEqual(reopenedIdentity.userID, aliceIdentity.userID)
        try await reopenedAlice.submitAnswer(matchID: match.id, itemID: "battle-item", optionID: "B", requestID: acceptedRequestID)
        await XCTAssertThrowsNetworkError {
            try await reopenedAlice.submitAnswer(matchID: match.id, itemID: "battle-item-2", optionID: "C", requestID: UUID())
        }
        let settled = try await reopenedAlice.refresh(matchID: match.id)
        XCTAssertEqual(settled.participants.first { $0.id == aliceIdentity.userID }?.state, .timedOut)
    }

    func testHTTPBattleFreezesAnswerFreePayloadAndRequiresExactAssets() async throws {
        let fixture = try makeServerFixture(name: "frozen-assets", assetChecksums: ["audio-1": "abc123"])
        let server = try startServer(fixture: fixture)
        let alice = NetworkBackendClient(configuration: server.configuration)
        let bob = NetworkBackendClient(configuration: server.configuration)
        _ = try await signIn(alice, email: "asset-alice@example.test")
        let bobIdentity = try await signIn(bob, email: "asset-bob@example.test")
        let invite = try await alice.createInvite(requestID: UUID())
        _ = try await bob.acceptInvite(code: try XCTUnwrap(invite.pathComponents.last), requestID: UUID())
        let match = try await alice.createChallenge(opponentID: bobIdentity.userID, groupIDs: ["battle-group"], requestID: UUID())
        _ = try await bob.accept(matchID: match.id, requestID: UUID())

        let questions = try await alice.battleQuestions(matchID: match.id)
        XCTAssertEqual(questions.first?.assetChecksums, ["audio-1": "abc123"])
        await XCTAssertThrowsNetworkError {
            try await alice.ready(matchID: match.id, assetChecksums: [:], requestID: UUID())
        }
        let preparing = try await alice.ready(matchID: match.id, assetChecksums: ["audio-1": "abc123"], requestID: UUID())
        XCTAssertEqual(preparing.state, .preparing)
    }

    private func signIn(_ client: NetworkBackendClient, email: String) async throws -> AuthIdentity {
        try await client.requestEmailCode(email: email)
        return try await client.verifyEmailCode(email: email, code: "246810")
    }

    private func makeServerFixture(name: String, assetChecksums: [String: String] = [:]) throws -> ServerFixture {
        let directory = FileManager.default.temporaryDirectory
            .appending(path: "TOEICPathNetworkTests-\(name)-\(UUID().uuidString)", directoryHint: .isDirectory)
        try FileManager.default.createDirectory(at: directory, withIntermediateDirectories: true)
        addTeardownBlock { try? FileManager.default.removeItem(at: directory) }
        let catalogURL = directory.appending(path: "catalog.json")
        let catalog: [[String: Any]] = [
            [
                "contentVersion": "battle-v1", "groupID": "battle-group", "itemID": "battle-item",
                "ordinal": 0, "correctOptionID": "B", "purpose": "battle",
                "prompt": "The report is ___ for review.",
                "options": [["id": "A", "text": "readying"], ["id": "B", "text": "ready"],
                            ["id": "C", "text": "readily"], ["id": "D", "text": "readiness"]],
                "assetChecksums": assetChecksums
            ],
            [
                "contentVersion": "battle-v1", "groupID": "battle-group", "itemID": "battle-item-2",
                "ordinal": 1, "correctOptionID": "C", "purpose": "battle",
                "prompt": "Please submit the form ___ Friday.",
                "options": [["id": "A", "text": "at"], ["id": "B", "text": "from"],
                            ["id": "C", "text": "by"], ["id": "D", "text": "with"]],
                "assetChecksums": assetChecksums
            ]
        ]
        try JSONSerialization.data(withJSONObject: catalog, options: [.prettyPrinted, .sortedKeys]).write(to: catalogURL)
        return ServerFixture(directory: directory, stateURL: directory.appending(path: "state.sqlite"), catalogURL: catalogURL)
    }

    private func startServer(fixture: ServerFixture, battleSeconds: Int = 600) throws -> ServerProcess {
        let process = Process()
        let stdout = Pipe()
        let stderr = Pipe()
        process.executableURL = URL(fileURLWithPath: "/usr/bin/python3")
        process.arguments = [
            repositoryRoot.appending(path: "Backend/local_server.py").path,
            "--state", fixture.stateURL.path,
            "--catalog", fixture.catalogURL.path,
            "--public-client-id", "toeicpath-tests",
            "--battle-seconds", "\(battleSeconds)",
            "--test-mode"
        ]
        process.standardOutput = stdout
        process.standardError = stderr
        try process.run()
        let line = try readLine(from: stdout.fileHandleForReading)
        guard let data = line.data(using: .utf8),
              let object = try JSONSerialization.jsonObject(with: data) as? [String: Any],
              let port = object["port"] as? Int else {
            process.terminate()
            let errorText = String(data: stderr.fileHandleForReading.availableData, encoding: .utf8) ?? ""
            throw NSError(domain: "NetworkBackendIntegrationTests", code: 1, userInfo: [NSLocalizedDescriptionKey: "Server did not start: \(line) \(errorText)"])
        }
        let value = ServerProcess(
            process: process,
            configuration: ServerConfiguration(baseURL: URL(string: "http://127.0.0.1:\(port)/")!, publicClientID: "toeicpath-tests")
        )
        addTeardownBlock { value.stop() }
        return value
    }

    private func readLine(from handle: FileHandle) throws -> String {
        var data = Data()
        while true {
            guard let byte = try handle.read(upToCount: 1), !byte.isEmpty else { break }
            if byte[0] == 0x0A { break }
            data.append(byte)
        }
        return String(decoding: data, as: UTF8.self)
    }

    private var repositoryRoot: URL {
        URL(fileURLWithPath: #filePath).deletingLastPathComponent().deletingLastPathComponent()
    }

    private var safeBattleDescriptors: [LocalBattleItem] {
        [
            .init(groupID: "battle-group", itemID: "battle-item", correctOptionID: "not-sent-by-network-client", contentVersion: "battle-v1", purpose: .battle),
            .init(groupID: "battle-group", itemID: "battle-item-2", correctOptionID: "not-sent-by-network-client", contentVersion: "battle-v1", purpose: .battle)
        ]
    }
}

private struct ServerFixture {
    let directory: URL
    let stateURL: URL
    let catalogURL: URL
}

private final class ServerProcess: @unchecked Sendable {
    let process: Process
    let configuration: ServerConfiguration
    init(process: Process, configuration: ServerConfiguration) {
        self.process = process
        self.configuration = configuration
    }
    func stop() {
        guard process.isRunning else { return }
        let processID = process.processIdentifier
        process.terminate()
        let deadline = Date.now.addingTimeInterval(2)
        while process.isRunning, Date.now < deadline {
            RunLoop.current.run(until: Date.now.addingTimeInterval(0.02))
        }
        if process.isRunning {
            _ = Darwin.kill(processID, SIGKILL)
        }
    }
}

private func XCTAssertThrowsNetworkError<T>(
    _ expression: () async throws -> T,
    file: StaticString = #filePath,
    line: UInt = #line
) async {
    do {
        _ = try await expression()
        XCTFail("Expected network request to fail", file: file, line: line)
    } catch { }
}
