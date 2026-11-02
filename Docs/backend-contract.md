# Backend Contract and Trust Boundaries

The iOS app is offline-first, but social and competitive outcomes are server-authoritative. A production deployment must connect one stable auth identity to email OTP. Public client configuration may ship in the app; privileged keys never do.

## Required endpoints

- Auth: request and verify email OTP, return stable user identity.
- Sync: idempotently merge/upload local sessions and pull changes by cursor.
- Friends: create expiring invite/QR payload, accept, remove, block/unblock.
- Chat: persist messages keyed by `(sender_id, client_message_id)`, query by durable cursor, and emit lightweight realtime change events.
- Content: version manifest, signed media URLs, staged download, issue report.
- Battle: invite/accept/decline, asset-ready, start, answer acceptance, submit, status, and settlement.

Every mutation accepts a UUID request ID. A server idempotency record stores actor, operation, request ID, response digest, and completion. Realtime delivery is a hint only; reconnect always queries persistent rows.

## Battle invariants

The server freezes `content_version`, ordered group/item IDs, media checksums, and per-player time allowance before `active`. It prefers unseen families for both players; if unavailable, it labels the match `is_review_rematch` before acceptance.

Only these match transitions are valid:

```text
invited -> accepted | declined | cancelled | expired
accepted -> preparing | cancelled | invalid
preparing -> active | cancelled | invalid
active -> settling | forfeited | invalid
settling -> completed | invalid
```

Participant state is separate: `invited`, `accepted`, `ready`, `active`, `submitted`, `timed_out`, `forfeited`, `completed`. The server stamps start/deadline, accepts answers inside the window, and settles once. Unique keys prevent duplicate answers and settlement. A durable scheduler or recoverable database scan expires invitations and advances deadlines; an in-memory timer is never the sole authority.

Scoring is 100 for correct, 0 for wrong/unanswered, no penalty. Equal scores are ties; speed is recorded but not the default tiebreak. Clients receive only opponent progress until both players finish or the match validly ends. They never write score, winner, correct answers, or deadline.

## Chat and blocking

Friendship is mutual and unique. Removing a friend blocks new messages/invites while keeping server history readable under the documented retention policy. Local hiding deletes only that user's local display. A block is checked when reading, writing, and subscribing; UI hiding alone is insufficient. Push payloads omit message bodies unless a user explicitly enables previews.

## Account deletion policy to finalize before production

Default proposal: immediately revoke auth and social reachability; delete profile/contact fields after a recovery window; retain de-identified attempt aggregates only with explicit analytics consent; tombstone sender identity in retained conversations; retain competitive ledgers for abuse/audit for a published duration. This requires a product/legal decision before enabling production account deletion.
