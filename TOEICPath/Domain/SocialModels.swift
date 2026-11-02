import Foundation

enum DeliveryState: String, Codable, Sendable { case sending, sent, failed }

struct FriendSummary: Identifiable, Codable, Hashable, Sendable {
    let id: UUID
    var displayName: String
    var handle: String
    var isBlocked: Bool
    var unreadCount: Int
}

struct ChatMessage: Identifiable, Codable, Hashable, Sendable {
    let id: UUID
    let clientMessageID: UUID
    let conversationID: UUID
    let senderID: UUID
    let body: String
    let createdAt: Date
    var delivery: DeliveryState
}

enum MatchState: String, Codable, CaseIterable, Sendable {
    case invited, accepted, preparing, active, settling, completed
    case expired, declined, cancelled, invalid, forfeited

    var isTerminal: Bool {
        [.completed, .expired, .declined, .cancelled, .invalid, .forfeited].contains(self)
    }
}

enum ParticipantState: String, Codable, Sendable {
    case invited, accepted, ready, active, submitted, timedOut, forfeited, completed
}

struct MatchParticipant: Identifiable, Codable, Hashable, Sendable {
    let id: UUID
    var state: ParticipantState
    var progress: Int
    var serverScore: Int?
}

struct BattleMatch: Identifiable, Codable, Hashable, Sendable {
    let id: UUID
    let requestID: UUID
    var state: MatchState
    let contentVersion: String
    let groupIDs: [String]
    let orderedItemIDs: [String]
    let invitationExpiresAt: Date
    var startsAt: Date?
    var deadline: Date?
    var participants: [MatchParticipant]
    var winnerID: UUID?
    var isReviewRematch: Bool
}

/// Server-projected battle content. It intentionally has no correct answer,
/// explanation, evidence, or private authoring metadata.
struct BattleQuestion: Identifiable, Codable, Hashable, Sendable {
    let id: String
    let groupID: String
    let prompt: String?
    let options: [AnswerOption]
    let assetChecksums: [String: String]
}

enum BattleStateMachine {
    static let allowedTransitions: [MatchState: Set<MatchState>] = [
        .invited: [.accepted, .declined, .cancelled, .expired],
        .accepted: [.preparing, .cancelled, .invalid],
        .preparing: [.active, .cancelled, .invalid],
        .active: [.settling, .forfeited, .invalid],
        .settling: [.completed, .invalid],
        .completed: [], .expired: [], .declined: [], .cancelled: [], .invalid: [], .forfeited: []
    ]

    static func canTransition(from: MatchState, to: MatchState) -> Bool {
        allowedTransitions[from]?.contains(to) == true
    }
}
