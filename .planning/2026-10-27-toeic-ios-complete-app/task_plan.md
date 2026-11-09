# Task Plan: TOEIC Native iOS App

## Goal
Deliver a maintainable native SwiftUI iPhone app foundation that already supports real offline TOEIC practice flows and content validation, while preserving clear seams for the authenticated backend, social features, and battle settlement service.

## Current Phase
Phase 18 (offline audio quality preview)

## Phases

### Phase 1: Requirements & Discovery
- [x] Confirm repository state and instructions
- [x] Capture product, learning, accessibility, privacy, and integrity constraints
- [x] Confirm available Apple toolchain
- **Status:** complete

### Phase 2: Architecture & Project Bootstrap
- [x] Create the Xcode project and source/test targets without external dependencies
- [x] Define domain models, persistence boundaries, service protocols, and app state
- [x] Define the versioned content-package contract and importer validation rules
- **Status:** complete

### Phase 3: Offline Learning Vertical Slice
- [x] Implement onboarding and the four-tab shell
- [x] Implement Part 1–7 catalog, standard practice session, answer review, and accessibility conditions
- [x] Implement rule-based diagnostic routing with audit reasons and evidence sufficiency
- [x] Implement daily plan, mistakes, spaced review, progress, and a 200-question mock-test assembly engine
- [x] Add timed mock runtime, authoritative listening timeline, section review grid, and interruption restoration
- [x] Add an app-owned staged content version store with cross-batch conflict checks and active-version restoration
- **Status:** complete

### Phase 4: Social, Sync, and Battle Contracts
- [x] Implement signed-out/local-first UX and account merge boundary protocols
- [x] Implement friend/chat/battle state models and clearly labeled preview flows
- [x] Document server-enforced authorization, idempotency, deadlines, transitions, and settlement schema
- [x] Add production API configuration seams without committing secrets
- [ ] Deploy and connect auth, sync, chat, battle worker, realtime events, and push notifications
- **Status:** pending

### Phase 5: Verification & Delivery
- [x] Build for a generic iOS device target without signing
- [x] Run unit tests for content validation, diagnostic rules, review scheduling, mock tests, and battle transitions
- [ ] Audit accessibility labels, states, and representative Dynamic Type layouts
- [x] Update README, findings, and progress with exact supported vs. deferred capabilities
- **Status:** pending

### Phase 6: Multi-Batch Content Activation
- [x] Replace the single active-batch pointer with an atomic multi-batch activation catalog
- [x] Merge latest group versions without losing per-batch asset roots or unrelated batches
- [x] Prove idempotent re-import, update preservation, restart restoration, and rollback on failure
- [x] Execute untouched `exports/batch-ag-0001` through `batch-ag-0005` as integration fixtures
- **Status:** complete

### Phase 7: Mock Form Contract 1.0
- [x] Promote the proposal into a normative additive specification with group versions and asset registration
- [x] Define listening timeline events, resume anchors, integrity checks, and failure semantics
- [x] Align App decoding/validation with the additive file, including exact cross-batch resolution and millisecond timelines
- **Status:** complete; producer acceptance and real form/audio delivery remain external inputs

### Phase 8: Local Backend Integration
- [x] Implement persistent local auth, friendship/block, durable chat, sync, and server-authoritative battle services
- [x] Connect iOS friend/chat state and battle creation to the service rather than static demo arrays
- [x] Connect local battle listing, acceptance, asset-ready handshake, answer submission, waiting, recovery refresh, and result UI
- [x] Add two-account authorization, deduplication, visibility, and settlement integration tests
- [x] Document cloud deployment variables, credentials, workers, realtime, and APNs inputs
- [x] Add a replaceable Swift HTTP client and an independently executable local HTTP/SQLite vertical slice
- [ ] Deploy a hardened public API, realtime transport, production OTP, and APNs after credentials are supplied
- **Status:** in_progress; local and cross-process HTTP complete, public deployment pending

### Phase 9: Xcode Build Diagnosis
- [x] Capture full `xcodebuild` command, environment, destinations, SDK/platform inventory, and error log
- [x] Identify project error versus Xcode platform registration error and apply safe project fixes if applicable
- [x] Run a full unsigned generic-device build when the platform becomes available
- **Status:** complete; historical exit-70 evidence preserved, 2026-10-29 current build succeeds

### Phase 10: Evidence-Based Documentation
- [x] Separate implemented, executed verification, blocked external integration, and pending device acceptance
- [x] Remove stale claims and preserve raw validation/build evidence paths
- **Status:** complete

### Phase 11: Pool Isolation, Exposure, and Part Selection
- [x] Enforce training / diagnostic / battle / mock eligibility at engines, session start, and service boundaries
- [x] Persist exposure on presentation across exits, restarts, and group-version updates; migrate certain legacy responses
- [x] Replace first-group Part launch with unpracticed-first selection plus explicit review
- [x] Add mixed-pool, empty-pool, fixture, missing-material, all-exposed, exit, restart, update, and mock-leak regression tests
- **Status:** complete

### Phase 12: Seven-Batch and Mock-Contract Regression
- [x] Execute untouched batch 0001–0007 regression with versions, assets, namespaces, hashes, restart, idempotency, and rollback
- [x] Separate immutable 100-item baseline assertions from future additive catalog tests
- [x] Add required negative mock-form contract cases and record exact accepted hash/status
- **Status:** complete; counterpart re-acceptance of the new hash remains external

### Phase 13: Cross-Process Local Network Backend
- [x] Make AppModel depend on replaceable service composition rather than a concrete local client
- [x] Implement independently launchable local HTTP service and Swift network client for minimum auth/social/chat/battle flow
- [x] Run two independent network clients plus outsider authorization tests, including durable deadline settlement while clients are closed
- **Status:** complete for local cross-process execution; public deployment and two-phone acceptance remain pending

### Phase 14: Audit Verification and Delivery
- [x] Run the exact requested SwiftPM and full xcodebuild commands with preserved exit evidence
- [x] Record UI/device/simulator/network/two-phone status as pass, fail, or not_run without inference
- [x] Update README, contract status, planning evidence, and codex-delivery handoff
- **Status:** complete; historical blocker evidence retained and later superseded by the successful Phase 15 build

### Phase 15: Installed-App Offline MVP Seed Bootstrap
- [x] Bundle untouched validated batches 0001–0007 and media as portable App resources
- [x] Add asynchronous, retryable, idempotent startup installation through the existing validated staging/store path
- [x] Preserve profile data, existing batches, and newer group versions while recovering an empty installed store
- [x] Expose loading/failure/retry and truthful unavailable-feature states in the UI
- [x] Prove built `.app` resource presence plus empty/upgrade/restart/no-downgrade/profile/rollback/media scenarios
- [x] Deliver `handoff/2026-10-29-mvp/codex-mvp-delivery.md` with a five-minute device checklist
- **Status:** complete in code and automated verification; physical-device checklist remains not_run

### Phase 16: Revised Content Intake and Battle Integrity
- [ ] Accept only corrected immutable 0008–0010 packages through the unchanged contract and add real-package regression
- [x] Reject post-submit/post-timeout answers while preserving replay of already accepted request IDs
- [x] Separate server-owned battle catalog from answer-free client payload and verify ready asset/version checks
- [x] Document deployment authorization and avoid claiming cross-phone availability before deployment
- **Status:** Codex backend integrity complete; corrected immutable 0008–0010 packages not delivered and remain excluded

### Phase 17: Simple Quick Test
- [ ] Add a persisted reading/listening/mixed preference and one-tap home start, defaulting to a short reading test
- [ ] Assemble about ten items from complete approved non-fixture training groups, preserving whole groups and unseen-family priority
- [ ] Implement delayed-reveal test flow, fixed ordering, leave confirmation, idempotent submission, result summary, and per-item review
- [ ] Keep engineering metadata and secondary listening tools out of the main answer path while preserving condition evidence
- [ ] Add assembly/state/persistence regression tests, run the full core suite and unsigned iPhoneOS build, and write the simple-test delivery handoff
- **Status:** in_progress

### Phase 18: Offline Audio Quality Preview
- [x] Copy the immutable five A/B audio pairs into an App-only preview resource namespace with verified hashes
- [x] Add a minimal secondary-entry SwiftUI preview that serializes playback, stops on leave, and reports missing files
- [x] Preserve candidate/formal-content separation, signing, profile data, item counts, pools, and one-tap Today flow
- [x] Add targeted resource/catalog tests, run a full unsigned iPhoneOS build, and perform representative Simulator UI verification
- [x] Deliver `handoff/2026-10-29-mvp/codex-audio-preview-delivery.md` with exact device path and pending human checks
- **Status:** complete in code/build/Simulator verification; physical iPhone audio judgment and VoiceOver acceptance remain pending

## Decisions Made
| Decision | Rationale |
|----------|-----------|
| Minimum iOS 18; availability-gated iOS 26 effects | Matches request while preserving correct fallback behavior. |
| SwiftUI + Observation + Codable file persistence | Native, testable, offline-first, and does not require third-party packages. |
| Repository protocols separate UI from local/demo and future remote implementations | Allows useful unsigned practice now and later server authority without rewriting views. |
| Authoritative Content Contract 1.0.0 batch directory is the only external import format | Keeps Codex and Antigravity aligned; runtime models are an internal projection only. |
| Rule-based D1–D5 routing is explicitly labeled as a product rule | Avoids false psychometric claims and keeps thresholds testable/configurable. |
| Social and battle clients never authoritatively write score or winner | Preserves server authority and prevents accidental insecure architecture. |
| Mock exams require a version-matched form and one verified composited audio timeline | Prevents a fake 45-minute timer from replacing actual listening conditions. |
| Imported packages move through app-owned staging and an immutable version directory | Makes restart recovery and cross-batch identity enforcement possible. |
| The quick test is a training-only delayed-reveal session, not a diagnostic, mock exam, or TOEIC score estimate | Keeps the one-tap experience simple without weakening content-pool or reporting integrity. |

## Errors Encountered
| Error | Resolution |
|-------|------------|
| No existing project or generator installed | Create a small explicit `.xcodeproj` and native source tree. |
| Simulator/asset tools cannot access CoreSimulatorService in this environment | Removed the empty placeholder asset catalog, built with generic iOS device SDK, and ran portable core tests through SwiftPM. |
| Observation macro plugin was blocked by the execution sandbox | Replaced macro-based observation with standard `ObservableObject` / Combine. |
| Xcode later stopped registering the installed iOS 26.2 platform even though the SDK remains readable | Preserved each exit-70 retry as current evidence; direct iPhoneOS SDK type checking and SwiftPM tests are labeled supplemental and do not count as a successful full build. |
| First Phase 17 iPhoneOS build failed at `SessionView.swift:751` because adding an early quick-test branch disabled the implicit return of the following switch | Changed the getter to an explicit `return switch`; full build must be rerun before claiming success. |
| First Simulator launch showed the home card's correct `10 題`, but opening the boolean full-screen cover passed an earlier empty groups state and produced `1 / 0` / no session | Replaced separate array-plus-boolean state with one identifiable launch value that carries the frozen group list into the cover. |

## Scope Note
This is a multi-session product build. A real multi-user deployment additionally requires a selected backend project, credentials, push entitlement, and server deployment. Those are integration inputs, not reasons to block the offline learning application or server contract work.
