# Backend Implementation and Deployment Boundary

## Implemented and executed locally

There are two local implementations behind the same `AppBackendService` boundary:

- `LocalBackendHub` / `LocalBackendClient` is the in-process, atomic-JSON test substitute used when no server configuration exists.
- `Backend/local_server.py` is an independently started HTTP process with SQLite persistence, bearer sessions, per-request authorization, and a deadline worker. `NetworkBackendClient` is the Swift URLSession client used by the App whenever `SERVER_BASE_URL` and `SERVER_PUBLIC_CLIENT_ID` are present.

Implemented behaviors:

- stable email identity with a local development OTP;
- idempotent local-profile merge by request ID;
- expiring invite creation and bilateral friendship acceptance;
- friend removal with history retention;
- symmetric enforcement of either user's block for friend visibility, message reads/writes, invites, and battles;
- durable messages with `(sender_id, client_message_id)` deduplication and reload from persisted state;
- server-owned battle start/deadline, first-answer acceptance, progress, score, tie, winner, and settlement;
- persistent recovery scans for expired invitations and active-match deadlines, plus request-ID replay protection for accept/ready/submit mutations;
- issue-report and mutation request deduplication;
- atomic JSON persistence and refusal to operate if an existing state file cannot be decoded.

The XCTest integration suite covers both the actor substitute and the real HTTP boundary. The HTTP suite starts a separate server process, connects two independent Swift clients plus an unauthorized third account, restarts the service against the same SQLite file, and verifies stable identity, message deduplication, block/remove permissions, retained history, answer deduplication, hidden pre-settlement scores, authoritative settlement, outsider denial, and deadline settlement after both clients sign out.

The iOS Friends tab is connected to this service for sign-in, profile merge, invites, friend refresh, durable conversations, sending/failure/retry, remove, block, and the full local battle path: list/accept, asset-ready handshake, server-accepted answers, submit/wait, and authoritative result reveal. A labeled local account switch supports two-account manual testing without deleting persisted service data.

## Run the cross-process local service

The battle catalog is trusted server input and must not be downloaded from or authored by the mobile client. Supply a private JSON file outside version control:

```json
[
  {
    "contentVersion": "catalog-version",
    "groupID": "battle-group-id",
    "itemID": "battle-item-id",
    "ordinal": 0,
    "correctOptionID": "B",
    "purpose": "battle"
  }
]
```

Start the test-only service:

```bash
python3 Backend/local_server.py \
  --state /absolute/private/path/toeicpath.sqlite \
  --catalog /absolute/private/path/battle-catalog.json \
  --host 127.0.0.1 --port 8080 \
  --public-client-id toeicpath-local \
  --test-mode
```

`--test-mode` is the only mode that enables fixed OTP `246810`. Without it, OTP requests return `email_provider_not_configured`; this prevents accidentally exposing the fixed code on a network deployment.

Configure the generated iOS Info.plist through public build settings:

```bash
xcodebuild ... \
  SERVER_BASE_URL='https://your-api.example/' \
  SERVER_PUBLIC_CLIENT_ID='your-public-client-id'
```

If either setting is absent or empty, the App deliberately falls back to the in-process local service. A physical iPhone should use a trusted HTTPS endpoint. Plain HTTP on a Mac LAN is not enabled as a broad ATS exception; use a trusted local reverse proxy if testing a physical device.

## Local-development limitations

- OTP is the visibly labeled fixed code `246810`; it must never be enabled in a network deployment.
- The HTTP reference service uses SQLite and bearer-token hashes, but no TLS endpoint, encryption-at-rest policy, key rotation, rate limiting, email provider, or account-recovery workflow.
- The in-process fallback still uses a local atomic JSON file and is not a multi-device service.
- There is no APNs delivery, external realtime transport, abuse throttling, email delivery, or cloud account recovery.
- HTTP message recovery is durable polling with an `after` cursor and limit, not websocket/SSE realtime. Read receipts and unread cursor persistence remain incomplete.
- The Python service is suitable for deterministic cross-process integration tests and local product wiring, not direct Internet exposure.
- Messages are not end-to-end encrypted.

## Production processes required

1. **API service** — verifies OTP/session tokens, sets the actor identity, enforces authorization, records idempotency keys, and exposes sync/social/chat/battle/content endpoints.
2. **PostgreSQL 16** — apply `backend/migrations/0001_core.sql`; use separate migration and runtime roles. The public/mobile role must not connect directly with table-write privileges.
3. **Deadline worker** — durably scans invitation and active-match deadlines, calls settlement in a transaction, and is safe to retry after restart.
4. **Realtime gateway** — emits lightweight row-change hints only. Every reconnect queries durable messages/matches by cursor.
5. **OTP provider adapter** — sends short-lived, single-use codes with rate limiting and normalized email identities.
6. **APNs worker** — uses token-based APNs credentials; message bodies are omitted unless the recipient explicitly enables previews.
7. **Content origin** — serves immutable manifests and signed asset URLs. Private authoring packages containing answer keys are never delivered directly.

## Required server configuration

Secrets belong in the deployment secret manager, never in the repository or iOS bundle.

| Setting | Used by | Secret |
|---|---|---|
| `DATABASE_URL` | API and worker PostgreSQL connection | yes |
| `DATABASE_MIGRATION_URL` | migration role | yes |
| `AUTH_TOKEN_SIGNING_KEY` | session token signing/verification | yes |
| `AUTH_TOKEN_ISSUER` / `AUTH_TOKEN_AUDIENCE` | token validation | no |
| `OTP_PROVIDER` | adapter selection | no |
| `OTP_API_KEY`, `OTP_FROM_ADDRESS` | email delivery | yes |
| `PUBLIC_API_BASE_URL` | canonical API origin | no |
| `REALTIME_PUBLIC_URL` | websocket/SSE origin | no |
| `CONTENT_SIGNING_KEY` | signed media URLs | yes |
| `APNS_TEAM_ID`, `APNS_KEY_ID`, `APNS_TOPIC` | APNs routing | mixed |
| `APNS_PRIVATE_KEY` | APNs authentication | yes |
| `DEADLINE_SCAN_INTERVAL_SECONDS` | durable worker cadence | no |
| `INVITE_TTL_SECONDS` | invite policy, initially 86400 | no |

## Required iOS public configuration

Only public values may be placed in generated Info.plist/build configuration:

- `SERVER_BASE_URL`
- `SERVER_PUBLIC_CLIENT_ID`
- optional `REALTIME_BASE_URL`
- Associated Domains/universal-link domain for friend invites
- Push Notifications capability and production bundle identifier

`ServerConfiguration.fromBundle` reads the first two values and the App composition root creates `NetworkBackendClient`. The local server implements the minimum HTTP vertical slice, but a hardened public deployment (or a port of the API to the PostgreSQL schema) is still required before Internet exposure.

## Deployment acceptance checks

- Run migrations against a disposable database, then test least-privilege roles.
- Execute the same two-account authorization suite against the HTTP API.
- Kill/restart the API, worker, and realtime gateway during an active match; deadlines and accepted answers must survive.
- Replay every mutation request ID and verify identical results without duplicated rows.
- Confirm blocked users cannot read, write, invite, battle, or subscribe.
- Confirm pre-settlement payloads contain neither correct answers nor opponent score.
- Confirm push payloads omit message body by default.
- Run account deletion/retention policy tests after the policy is finalized.
