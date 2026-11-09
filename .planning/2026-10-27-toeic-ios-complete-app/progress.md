# Progress Log

## Session: 2026-10-27

### Current Status
- **Phase:** 10 - Evidence-Based Documentation; phases 7–9 retain explicit external/integration blockers
- **Started:** 2026-10-27

### Actions Taken
- Read the complete file-planning skill instructions and initialized a scoped plan.
- Inspected the workspace, applicable instructions, Git state, and Apple toolchain.
- Confirmed the directory is empty and documented the requirements and architecture boundaries.
- Created the SwiftUI app, app/test targets, local store, domain models, import validator, learning engines, service boundaries, seven-Part preview bank, and four-tab feature UI.
- Added Antigravity content contract, backend trust-boundary contract, PostgreSQL reference migration, README, Package.swift core harness, and git ignores.
- Fixed first-play vs. replay condition tracking, made review launch real due groups, and made mock assembly use exact subset selection rather than a greedy count.
- Detected the newly present authoritative `specs/` contract, removed the conflicting draft, implemented the 1.0.0 batch wire model/import validator, and changed the UI importer from single JSON to a security-scoped batch directory.
- Implemented live diagnostic group routing across listening and reading, with whole-group/family de-duplication, Part coverage, evidence sufficiency, and persisted selection reasons.
- Implemented the resumable 200-question mock runtime: fixed listening timeline, 75-minute reading deadline, answer grid, background/interruption recording, immutable deadlines, delayed reveal, and local submission persistence.
- Added strict mock-form/runtime-content validation and documented the additive mock-form contract request without changing the authoritative Content Contract 1.0.0.
- Added app-owned staging/version directories, atomic active-version selection, startup restoration, cross-batch group/version hash checks, global item ownership, family pool enforcement, full file inventory checks, and symlink/path defenses.
- Fixed mock submission teardown so leaving the submitted screen cannot resurrect a completed runtime, and de-duplicated inactive/background interruption events.
- Replaced the practice audio placeholder with real imported-asset playback, 0.8× assistance, contract-provided segment playback, local Part 1 image rendering, and material-missing/interruption condition tracking. Part 1–2 prompt/choice text is now withheld before submission, including from VoiceOver labels.
- Replaced the single active pointer with atomic `state.json`, merged all active immutable batches, namespaced runtime assets by source batch, and preserved group/source versions in responses.
- Ran untouched batches `batch-ag-0001` through `0005`: 100 accumulated items survive store reconstruction; re-import stays at 100; failed hash validation leaves state and the 100-item package unchanged; higher group versions replace only that group.
- Added `specs/mock-form-contract-v1.md` with exact group version references, whole-form asset registration, event timeline, fixed resume anchors, integrity validation, and failure semantics. It is explicitly an alignment baseline, not yet an accepted Content Contract feature.
- Implemented a persistent local backend and connected iOS sign-in, invite, friend, block/remove, durable chat, retry, and battle creation flows. Removed static demo friends/matches.
- Added two-account plus outsider integration tests for stable identity, profile merge boundary, message deduplication, block/remove authorization, retained history, server-owned deadlines, answer deduplication, scoring, winner, and outsider denial.
- Captured the current full Xcode build failure with environment/platform evidence in `artifacts/build/xcodebuild-diagnosis-2026-10-27.md` and documented cloud deployment settings in `Docs/backend-deployment.md`.

### Test Results
| Test | Expected | Actual | Status |
|------|----------|--------|--------|
| Xcode availability | Apple build toolchain installed | Xcode 26.3 / Swift 6.2.4 | pass |
| Existing-project preservation | Identify existing work before writes | No project files found | pass |
| Generic iOS compile | Swift sources and project compile without signing | `BUILD SUCCEEDED` | pass |
| Xcode test-target compile | App and XCTest sources compile | `TEST BUILD SUCCEEDED` | pass |
| Portable core unit tests | All core rules execute successfully | 14 tests, 0 failures | pass |
| Authoritative batch contract | Valid fixture passes; cross-pool family rejected | 2 focused tests pass | pass |
| Preview content validation | No blocking structural issues | 0 blocking errors | pass |
| Portable core unit tests after continuation | Diagnostic, mock runtime, import index, content, review, and battle rules | 25 tests, 0 failures | pass |
| Whole iOS source type check | Every SwiftUI/App source checks against iPhoneOS SDK | clean `swiftc -typecheck` | pass |
| Current generic Xcode build retry | Xcode destination registry recognizes installed iOS platform | Xcode reports iOS 26.2 platform unavailable before compilation | blocked by local Xcode platform registration |
| Five untouched Antigravity packages | 5 active batches, 100 items, restart/idempotency/rollback | 49 listening preview + 51 reading, all persistence assertions pass | pass |
| Portable core suite after multi-batch work | All core and integration tests | 27 tests, 0 failures | pass |
| Local backend two-account suite | Auth/social/chat/battle authorization and persistence | 2 integration tests pass | pass |
| Final portable suite this round | Content, learning, mock, backend, battle, corrupt-state refusal | 30 tests, 0 failures | pass |
| Full iOS source type check after iOS/backend integration | All Swift app sources | clean | pass, secondary evidence only |
| Full unsigned generic-device Xcode build | Compile/link/package app | exit 70 before compilation; matching iOS 26.2 component unavailable | blocked, evidence preserved |

### Errors
| Error | Resolution |
|-------|------------|
| Project generator unavailable | Use a self-contained explicit Xcode project. |
| Empty Asset Catalog could not compile because CoreSimulatorService is unavailable | Removed placeholder catalog; app has no final icon until real branding asset is supplied. |
| Observation macro plugin returned malformed response under sandbox | Used Combine `ObservableObject`, which compiled successfully. |
| SwiftPM's nested sandbox was denied | Ran the same local tests with approved sandbox escalation; no network access was needed. |
| Xcode destination registry later reported iOS 26.2 unavailable despite the SDK being present | Did not misreport a fresh Xcode build; verified this continuation with 24 SwiftPM tests and full iPhoneOS SDK type checking. |
| First untouched Antigravity import failed decoding `manifest.producer` as an object | `manifest.schema.json` requires a string; changed the wire type to decode the normative string while retaining object decode compatibility for earlier Codex fixtures. Original exports remain unchanged. |
| Second untouched import attempt misclassified files under `/tmp` as undeclared nested paths | `/tmp` resolves to `/private/tmp` on macOS; canonicalized the inventory root before deriving relative paths without weakening package symlink checks. |
| First two-account restart test produced a different stable identity | Local backend encoded ISO-8601 dates but decoded with Foundation's default date strategy, causing the whole state to fall back empty. Unified the decoding strategy and retained the restart assertion. |
| A stale-text audit command had an unmatched shell quote | Re-ran the read-only search with a single-quoted pattern; no project data was changed. |

## Session: 2026-10-28

### Actions Taken
- Implemented the additive mock-form wire model and connected optional `reports/mock-forms.json` decoding to batch import.
- Added cross-batch resolution by exact group ID/version/source batch, required manifest-hash checks, whole-form asset registration, official 200-item/Part/Part 7 validation, event overlap/unlock checks, and Part 1–2 response-audio requirements.
- Preserved listening timeline values in milliseconds through the runtime instead of truncating them to whole seconds.
- Changed content activation to reconstruct and validate the complete candidate catalog before atomically writing `state.json`, closing a rollback window where state could have pointed at a removed destination.
- Loaded resolved formal forms into `AppModel`; the UI only exposes a form when its exact groups and timeline checksum resolve.
- Connected the local battle UI through listing, acceptance, ready handshake, question answering, submission, waiting, and authoritative result reveal.
- Added request-ID replay protection for accept/ready/submit, a persistent expiry/deadline recovery scan, match listing, and a local account switch for two-account manual testing.
- Re-ran the real generic-device Xcode build after destinations reappeared; it still exited 70 before compilation with the same missing iOS 26.2 component error.
- Updated implementation, deployment, contract, build-evidence, README, findings, and plan documents to distinguish delivered code from external and device acceptance work.

### Verification
| Test | Actual | Status |
|------|--------|--------|
| Portable core suite | 32 tests, 0 failures | pass |
| Additive mock-form resolver | Valid 200-item form resolves; missing required batch rejects catalog | pass |
| Untouched Antigravity imports | 5 batches / 100 items / restart / idempotency / rollback | pass |
| Local battle service | Two accounts, outsider denial, mutation replay, answer dedup, server settlement | pass |
| Whole iOS source type check | All Swift sources clean against iPhoneOS 26.2 SDK | pass, secondary evidence only |
| Full generic-device Xcode build | exit 70 before compilation; iOS 26.2 component still ineligible | blocked, evidence preserved |

## Session: 2026-10-28 Integration Audit Remediation

### Intake
- Re-read the complete planning skill and restored the active plan, findings, and progress files.
- Read `handoff/2026-10-28/01-codex-next-round.md` through `END-CODEX-HANDOFF-2026-10-28`.
- Added phases 11–14 for pool/exposure/Part selection, seven-batch and mock regression, cross-process network backend, and evidence-based delivery.
## 2026-10-28 implementation continuation

- Added explicit runtime `ContentPurpose`, `RuntimeContentStatus`, and `fixture` metadata with backward-safe decoding; imported batches now preserve all three fields.
- Added central formal eligibility checks and removed cross-pool fallback from diagnostic, daily training, Part practice selection, mock assembly, and local battle configuration.
- Added persisted per-group exposure history with item IDs, family IDs, versions, source batches, modes, timestamps, and presentation count. Legacy profiles migrate only definite submitted responses.
- Updated the practice UI to select a Part first, list unseen complete training groups before explicitly labeled review groups, and keep incomplete material in a non-formal preview section.
- Session start now validates purpose, approval, fixture status, and actual local listening material. A presented item records exposure immediately, including when the user exits without submitting.
- Added initial regression tests for empty diagnostic pools, historical exclusion, daily/mock/battle isolation, Part new-versus-review ordering, and exposure restart/version persistence.
- First post-change `swift test` built successfully but failed expected stale tests that still treated bundled fixtures as formal content; those tests have now been converted to explicit purpose fixtures. A clean rerun is still pending.

### Completed implementation and verification

- Ran the immutable seven-batch test without modifying exports: 7 active batches, 51 groups, 100 unique items, Part counts 3/13/18/15/15/8/28, 27 listening groups at v2, and 30 hash-verified installed assets. Restart, re-import, update selection, and failed-install rollback pass.
- Clarified the mock form package topology to source batches → separate form package, prohibited owner self-reference, required formal mock metadata, added AVFoundation decoded-duration probing, and added the required negative contract cases.
- Read the newly created Antigravity contract status. It accepted the former hash `058894...`; the clarified Codex document is now `f8d3e7...`, so shared acceptance is pending re-acceptance.
- Added `AppBackendService`, `NetworkBackendClient`, dynamic iOS composition, and `Backend/local_server.py` with SQLite persistence, bearer sessions, friend/chat authorization, server-owned battle catalog/scoring, and a continuously running deadline worker.
- Executed two independent Swift clients against a separate HTTP process plus an outsider account. Social persistence survived a process restart; the worker settled an active match after both clients signed out.
- Exact required SwiftPM command first passed 49 tests before the final boundary/mixed-pool additions, then passed 54 tests, and the final complete rerun with the explicit five-batch material boundary passed 55 tests with 0 failures.
- Exact full xcodebuild command exited 70 before compilation because Xcode still marks iOS 26.2 unavailable. Captured current evidence in `artifacts/build/xcodebuild-diagnosis-2026-10-29.md`.

### Final verification and delivery — 2026-10-29

- Exact requested SwiftPM suite: 55 tests, 0 failures. The added untouched 0001–0005 regression proves 51 reading items can start formal practice while all 49 listening items remain preview-only and are rejected by the session boundary until ready media exists.
- Whole iOS source type check against the iPhoneOS 26.2 SDK: exit 0 with no warnings after correcting the two warnings found on the prior run. This remains supplemental evidence only.
- `python3 -m py_compile Backend/local_server.py`: exit 0.
- Contract hashes rechecked: mock form `f8d3e70867c256f95384c9c490735afcbebadbed91728f86450e262b28ae650e`, content `f3aee0f0ae02ae4b69bc066deb4be83acd72c687b121b72d0331f4f7567a28c1`, validation `8c64b71847e83f5179e3c3fa605af14312b1a058418ca8e0b4af044d2da22ccc`.
- Full unsigned `xcodebuild`: still exit 70 before compilation because the iOS 26.2 platform component is not installed/eligible. No UI simulator or physical-device result is inferred from SwiftPM/typecheck.
- Final handoff written to `handoff/2026-10-28/codex-delivery.md`; original Antigravity exports and counterpart status/delivery documents remain unchanged.

## Session: 2026-10-29 Installed-App MVP

- Read `handoff/2026-10-29-mvp/01-codex-mvp.md` and the complete `.planning/2026-10-29-integration-audit/audit-report.md`.
- Confirmed the installed-App empty-shell root cause: the App target has an empty resource phase and `AppModel` falls back to `SampleContent` when Application Support has no active batches.
- Confirmed current signing values before edits: team `VJ3Y39FF2P`, bundle ID `com.local.TOEICPath`.
- Started Phase 15 for portable seed resources, validated asynchronous bootstrap, UI recovery states, built-App verification, and device handoff; Phase 16 tracks corrected 0008–0010 intake and battle integrity separately.
- Copied the untouched 74 files from batches 0001–0007 into an explicit 8.9 MB `SeedContent` folder resource and verified every copied directory is byte-identical with `diff -qr`.
- Added a candidate-state atomic multi-batch install path and asynchronous bootstrap UI. The first SwiftPM compile rejected sending an unmarked store value across actors; the second confirmed `FileManager` itself is non-Sendable. The bootstrap actor now receives only the Sendable storage URL and constructs its own store internally, while manual imports are rejected during the seed transaction.
- The first built-resource override test compile needed an explicit `return` in its multi-branch `seedRoot` getter; corrected before rerunning the built `.app` importer test.

### Completed implementation and verification

- Added `SeedContent/batch-ag-0001...0007` to the App resource phase without editing the Antigravity exports, signing team, bundle identifier, or profile storage.
- Added asynchronous startup bootstrap, atomic seven-batch activation, loading/failure/retry UI, profile preservation, no-downgrade behavior, and same-Part “下一組” practice continuation.
- Added four seed bootstrap tests covering empty install, restart/idempotency, installed-empty upgrade/profile retention, failed-transaction rollback, actual media bytes, and newer-version preservation.
- Added answer-free battle question transport, frozen match payload/assets, actual local SHA-256 readiness verification, and submitted/timed-out answer replay semantics to the local and HTTP services.
- Added local and HTTP negative cases for exact asset requirements and post-submit/post-timeout answer acceptance boundaries.

### Final verification — 2026-10-29

| Verification | Actual | Status |
|---|---|---|
| Full SwiftPM suite | 63 tests, 0 failures | pass |
| Python HTTP syntax | `python3 -m py_compile Backend/local_server.py`, exit 0 | pass |
| Full unsigned iPhoneOS build | `** BUILD SUCCEEDED **` | pass |
| Built App resources | 74 files, 7 manifests, 30 media, 8.9 MB; source diff clean | pass |
| Built App importer | 4 seed tests using `.app/SeedContent`, 0 failures | pass |
| Signing preservation | Team `VJ3Y39FF2P`, Bundle ID `com.local.TOEICPath` | pass |
| Physical iPhone five-minute checklist | Not executed by Codex | not_run |
| Corrected immutable 0008–0010 intake | No replacement delivery present | blocked_external |

- Delivery updated at `handoff/2026-10-29-mvp/codex-mvp-delivery.md`.
- Current build-success evidence is `artifacts/build/xcodebuild-success-2026-10-29.md`; older exit-70 diagnosis artifacts are retained unchanged.

### Physical-device feedback follow-up

- Recorded Part 1 `research_laboratory` audio quality as `not_passed` after direct user feedback.
- Confirmed the current source format/bitrate and missing spoken A–D labels without modifying the immutable seed/export packages.
- Improved Part 1/2 standard-condition guidance, assisted transcript behavior/recording, semantic sentence playback labels, and 1× AVAudioPlayer configuration.
- Generated a clearly non-production local A/B sample and requested an immutable v3 media revision plus human headphone/audio-only review from the Antigravity workflow; no paid service was purchased or invoked.
- Antigravity's prior run is terminated by a network issue and its UI retains an unsent attachment draft. No retry/send action was taken, so the immutable media replacement remains an external blocker rather than active verified work.
- Inventoried all 27 bundled audio files. They share AAC mono/22.05 kHz and one synthesis pipeline, but vary by voice, actual bitrate (about 37.6–61.8 kbps), and mean volume (about -21.5 to -16.3 dB); no cause is claimed without a named clear sample.
- Added playback-start output route and AVAudioSession sample-rate capture to persisted answer conditions plus a user-readable route caption. Focused diagnostic tests and the complete unsigned iPhoneOS build pass.
- A full-suite rerun exposed an intermittent XCTest teardown hang in `Process.waitUntilExit()` after the Python server had already disappeared. Replaced the unbounded wait with a bounded terminate/poll and SIGKILL fallback in the test harness; the 5 HTTP integration tests and final 63-test suite then completed with 0 failures.
- Recorded the physical-device shortlist result: the user judged the third sample (`ag-g-p1-000003`, Karen en_AU) clearest on the iPhone speaker.
- Generated two comparison-only Karen files from the original muddy group's statements, one preserving unlabeled statements and one speaking A–D. Captured hashes, durations and segment timings; exports, SeedContent, signing and user data remain unchanged. Device A/B acceptance is still pending, so no production replacement is claimed.
- Implemented an optional, default-off Part 1/2 label-gap synthesis control plus a reproducible comparison builder. Generated and measured the user's requested Karen/A–D/short-gap candidate: 15.556 s, SHA-256 `1eae239a...`, with four detected encoded gaps of about 357–359 ms. Python compilation passed; no iOS source, seed, signing or user data changed.

## Session: 2026-10-30 Simple Quick Test

- Received the explicit implementation handoff for a one-tap, approximately ten-item training quiz and kept audio-candidate acceptance separate from this UI work.
- Re-read the complete `planning-with-files-zht` skill, restored the active plan/findings/progress, ran session catch-up, and confirmed there is no project-local `AGENTS.md`.
- Added Phase 17 for training-only assembly, delayed reveal, simplified UI, persistence, verification, and delivery evidence.
- Added backward-compatible persisted quick-test focus/level preferences, a whole-group training-only assembler, delayed result scoring, and AppModel composition that excludes unresolved material.
- Reworked the Today screen around one prominent `開始測驗` action with compact reading/listening/mixed and editorial-level controls; retained Part practice as a secondary route.
- Extended `SessionView` with a quick-test presentation: no per-item reveal, simplified metadata, bottom-safe-area next/submit action, compact primary audio playback with assisted tools in a disclosure, and end-of-test score/time/per-item evidence review.
- The first attempt to replace `TodayView.swift` used delete/add operations for one path in a single patch and was rejected before changing the file. Reapplied the same change as two controlled `apply_patch` operations.
- Added six quick-test regression tests for purpose/material isolation, whole-group count reduction, family de-duplication/unseen priority, delayed scoring, persistence/reselection, and legacy preference decoding.
- Full portable suite after the first implementation pass: 69 tests, 0 failures. This does not yet count as an iOS UI build; full `xcodebuild` is next.
- First full unsigned iPhoneOS build reached compilation but failed with exit 65 at `SessionView.swift:751`: the existing mode-title switch needed an explicit return after the new quick-test early branch. Preserved the exact error in progress and applied the targeted source fix; a clean full rerun remains required.
- The corrected second unsigned iPhoneOS build succeeded. A separate iOS 26.3 Simulator build also succeeded and the fresh-launch onboarding plus new home screen rendered correctly with the default 10-item reading selection.
- First Simulator tap on `開始測驗` exposed a SwiftUI launch-state race: the cover received an empty array although the home card showed 10, yielding `1 / 0` and `無法開始作答`. Replaced the separate array and presentation boolean with an identifiable launch value carrying the frozen groups; simulator and device builds must be rerun.
- Applied the selected option-row visual refinement: increased the A–D marker-to-copy gap from 12pt to 18pt and the marker frame from 28pt to 30pt in training/quick test, with the same rhythm in mock exams, battles, and result review. The iOS Simulator `xcodebuild` completed with `** BUILD SUCCEEDED **`.

### 2026-10-31 quick-test integration follow-up

- Added accessibility-size layouts for the Today controls and summary metrics, and for the quick-test result metrics. Simulator verification completed for the maximum Dynamic Type home, listening flow, and result screen; the final maximum-size Part 6 passage check was not run because the Mac locked.
- Made saved mistakes visible before their review due date, separated saved and due counts, grouped them by user-facing Part names, and made full-group expansion explicit before starting review. Simulator restart preserved 31 saved mistakes and full-group review truthfully expanded to 36 items.
- Added real-seed listening/mixed quick-test regressions, a wrong-answer persistence/reopen regression, and a real `ContentVersionStore` intake test for immutable exports 0011–0015. The intake merged with the seven seeded batches to 177 unique items, applied the ten v3 Part 2 replacements from 0014/0015 without changing the item-ID set, verified each revised evidence quote against its referenced audio segment, stayed idempotent across reopen/re-import, and kept all 177 materials complete; it did not modify exports or bundle the new batches.
- Re-ran the complete SwiftPM suite: 75 tests, 0 failures. Re-ran the full unsigned generic iPhoneOS and iPhone 17 Pro Simulator builds: both `BUILD SUCCEEDED`. Re-ran six bootstrap tests against the built `.app/SeedContent`: 6 tests, 0 failures.
- Preserved Team `VJ3Y39FF2P`, bundle `com.local.TOEICPath`, the built-in 100-item SeedContent, and user profile storage. Physical iPhone/VoiceOver acceptance and Antigravity/human audio acceptance remain external acceptance work.

## Session: 2026-11-09 Offline Audio Preview

- Restored the active plan and read the latest 11/9 coordination boundary plus the existing audio-label and quick-test deliveries.
- Added Phase 18 for an isolated, offline five-pair A/B preview. No App code or resources have been changed yet.
- Confirmed the source catalog has five pairs / ten files and independently matched all ten declared SHA-256 hashes before copying anything.
- Selected the existing `我的 → 題庫與下載` section as the secondary entry; Today and formal `SeedContent` remain outside this change.
- Added a typed five-pair catalog, a secondary `我的 → 音質試聽` page, serialized A/B playback, explicit candidate labeling, visible playback errors, background/leave stop behavior, and 18pt marker-to-copy spacing.
- Added three resource/catalog tests; targeted run passed 3 tests with 0 failures.
- Full unsigned generic iPhoneOS build succeeded. The built `.app` contains all ten expected audio files with matching SHA-256 values, while formal SeedContent remains unchanged at 74 files.
- The iPhone 17 Pro Simulator build succeeded. UI QA reached `我的 → 音質試聽`, confirmed A playing, then B playing with A no longer selected, and confirmed re-entering after navigation showed neither track playing.
- Maximum Dynamic Type QA reached the scrollable A/B rows with separated 18pt markers, readable titles/details, and full-size play targets; the Simulator content size was restored to Large afterward.
- Full SwiftPM regression suite passed 78 tests with 0 failures. Physical iPhone speaker judgment and VoiceOver traversal were not executed and remain pending.

