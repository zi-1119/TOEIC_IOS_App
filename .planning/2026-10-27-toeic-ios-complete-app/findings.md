# Findings & Decisions

## Repository and Toolchain
- `/Users/ziii/Desktop/TOEIC_IOS_App` was empty at discovery time.
- No project-local `AGENTS.md` exists; the only discovered file was in an unrelated sibling repository and is not applicable.
- Xcode 26.3 and Swift 6.2.4 are installed.
- XcodeGen and Tuist are not installed, so the project must not depend on either.
- During final inventory, another workspace/user process added authoritative `specs/content-contract-v1.md`, `specs/validation-report-v1.md`, and Antigravity instructions. These are preserved and now supersede the initial single-JSON draft.

## Product Constraints That Must Remain Visible in Code
- UI and explanations are Traditional Chinese; question/audio content is English.
- Practice, diagnosis, and mock exams are distinct modes with distinct answer/review behavior.
- Listening and reading evidence are separated. Training performance is not multiplied into a fake 990 score.
- Part 1 and Part 2 must not expose the audio script during standard conditions.
- Assistance usage changes the recorded answer condition and is separated from standard evidence.
- Diagnostic selection must preserve complete groups and audit rule version, reason, exposure, family, and conditions.
- Battle questions, ordering, assets, version, and deadline must be identical; score and winner are server-owned.
- Private learning details remain private by default; notification previews do not include message body by default.
- Offline practice is a first-class path and sign-in is deferred until sync/social use.

## Architecture Direction
- `App`: composition root, navigation, accessibility-aware theme.
- `Domain`: content, attempts, learning profile, diagnostic, mock exam, social, battle.
- `Data`: bundled content, JSON importer/validator, Codable offline store, repository protocols.
- `Features`: onboarding, today, practice, session, report, friends, profile, content review.
- `BackendContract`: production API DTOs and a documented server state machine; demo implementations remain visibly demo data.

## External Inputs Still Needed for Production Network Features
- Backend provider/project URL and public client configuration.
- Email OTP provider configuration and server database deployment.
- APNs entitlement/certificate or token setup.
- Production question/audio/image packages from Antigravity.

## Accuracy and Content Note
- Bundled sample content is for exercising every UI and import path, not a calibrated or officially licensed TOEIC item bank.
- The app must label data sufficiency and never present unvalidated score estimates or confidence intervals.

## Implemented in This Session
- Native Xcode app and portable SwiftPM core test harness, with no third-party runtime dependencies.
- Onboarding, four tabs, local practice, delayed-reveal modes, answer conditions, evidence-first explanation UI, empty/error/shortage states, and local persistence.
- Deterministic Content Contract 1.0.0 batch-directory importer: snake-case wire models, JSONL, manifest counts/file inventory/SHA-256, path and symlink defenses, Part shapes, source references, review integrity, report derivation, and runtime projection.
- Rule-based diagnostic decision engine, daily whole-group planner, spaced review scheduler, exact-count mock-exam assembler, and battle transition engine.
- Server service protocols plus a PostgreSQL reference schema for identities, idempotency, friendships, blocks, durable chat, attempts, battles, unique answers, deadlines, and content reports.
- iOS 26 native glass effect behind availability and Reduce Transparency fallback.
- Dynamic diagnostic routing now selects one complete group at a time, balances listening/reading, fills Part deficits, avoids repeated families, and stores the exact rule/reason used.
- The mock runtime requires exactly 200 version-matched items, official Part counts, a non-repeated family set, and one composited verified audio timeline; it preserves original section deadlines across backgrounding and relaunch.
- Content packages now install through app-owned staging into immutable version directories. The active package is restored on launch, and a persistent index rejects same-ID/same-version mutations, item ID reassignment, and family movement across purpose pools.
- Training playback now uses verified local assets rather than a UI-only control. Contract segment timings feed逐句 playback; slow speed, replay, transcript, VoiceOver, backgrounding, missing audio, and missing Part 1 images all prevent the result from entering standard-condition evidence.

## Explicitly Incomplete
- Seven-batch media upgrades now resolve 27 audio and 3 image assets, but incomplete/older listening records still remain preview-only and the UI intentionally reports missing material rather than counting them as formal evidence.
- The App implements the current mock-form decoder and validator, but there is no real 200-item form package or verified composited timeline asset. The current Codex contract hash also still needs Antigravity re-acceptance.
- The in-process service, full local battle UI, and independent HTTP/SQLite vertical slice are executable. Production cross-device use still requires a hardened HTTPS deployment, production auth, PostgreSQL API implementation, realtime, and APNs.
- Simulator visual QA could not run because CoreSimulatorService is unavailable to the execution environment.
- Final VoiceOver, largest Dynamic Type, Reduce Motion, and physical-device audio interruption QA remains outstanding.
- The detailed additive baseline now exists and decoder/validator integration is complete, but the App intentionally does not claim a usable formal mock until producer acceptance, exact form packages, decoded-media duration/device checks, and composited audio arrive.
- Local auth/social/chat/battle behavior is executable and tested both in-process and across an independent HTTP process. This is not yet a public multi-device deployment; production HTTP hardening/realtime/APNs remain incomplete.
- Current `xcodebuild` cannot reach compilation because Xcode 26.3 marks the iOS 26.2 generic destination ineligible. The built-in SDK exists, but the matching platform component/runtime is not registered; only iOS 18.6 Simulator runtime is installed.

## Historical Continuation Audit: Five-Batch Inputs (superseded by seven-batch verification)
- The untouched export set exists at `exports/batch-ag-0001` through `batch-ag-0005` and declares 100 items total across 51 groups (20 + 19 + 18 + 15 + 28 items).
- Each export manifest declares five non-manifest files. No audio or image binary is present in the directory inventory, so listening/photo material cannot be treated as complete even when question records are structurally importable.
- The original store used one `active.json` pointer; it has been replaced with atomic multi-batch `state.json`, and the untouched five-batch restart/idempotency/rollback behavior now passes integration tests.
- The backend reference is under `backend/` rather than a `BackendContract/` directory; current iOS service boundaries are in `TOEICPath/Data/ServiceContracts.swift`.
- Exported item distribution is exactly 49 listening items (Part 1: 3, Part 2: 13, Part 3: 18, Part 4: 15) and 51 reading items (Part 5: 15, Part 6: 8, Part 7: 28). All 30 declared listening/photo assets are `planned`; no ready binary asset exists.
- All five reports are `profile=authoring`, `overall_result=incomplete`. The current contract validator permits an authoring incomplete batch when there is no fail, while emitting missing-material warnings. The UI must therefore distinguish structural preview import from complete listening availability.
- Multi-batch merge design: store one atomic `state.json` containing both the immutable cross-batch index and ordered active batch IDs; load every active immutable directory; select the highest group version per permanent group ID; namespace runtime asset IDs by source batch; retain group version/source batch in runtime and responses.
- Existing PostgreSQL SQL still needs a deployed API. A later implementation added a separate Python/SQLite HTTP service and Swift network client with two-account plus outsider integration coverage; it does not replace the production PostgreSQL deployment requirement.

## 2026-10-28 Handoff Intake
- Fully read `handoff/2026-10-28/01-codex-next-round.md` through the literal `END-CODEX-HANDOFF-2026-10-28` marker.
- Required priority is runtime-enforced purpose-pool isolation, presentation-time exposure persistence, and usable single-Part selection before contract/backend follow-up.
- The handoff reports a newer seven-batch snapshot (0001–0007, 51 groups, 100 unique items, 27 listening groups at v2, 30 resolvable assets) that must be revalidated rather than assumed from the prior five-batch tests.
- Formal diagnostic, battle, and mock pools are reportedly empty; no fallback to training is permitted for formal modes.
- Cross-device claims require a real network boundary and two independent clients; the shared local actor remains a test double only.
- Final output must include exact contract SHA-256 and counterpart acceptance status, and distinguish build/UI/device/cross-process/two-phone evidence.
- Integration audit reproduced three concrete leaks: DiagnosticRouter falls back to all groups, DailyPlanner scores mock groups, and AppModel battle creation uses the first Part 5 groups without a battle-pool filter.
- The audit independently observed seven-batch resolution at 51 groups / 100 items with 27 listening v2 groups and 30 ready assets; existing committed XCTest coverage and README still describe only five batches and missing media, so both are stale until rerun in this implementation session.
- The current mock additive contract and Antigravity assembly report disagree on milliseconds/exact refs and even the derived group count (the documented quotas total 103 groups, not 93).
- Core XCTest success is not UI, full Xcode build, device, or network evidence. At intake the audit had not rerun the whole-source typecheck; the final 2026-10-29 rerun later passed cleanly as supplemental evidence only.
- Content Contract 1.0.0 makes pool and fixture explicit; content_status is not release permission. Used questions may be reviewed but cannot be counted as fresh ability evidence, and exposure history must survive version changes.
- Release listening eligibility requires ready audio for Parts 1–4 and ready images for Part 1; authoring/incomplete packages may import for private preview but cannot silently become formal content.
- Validation Report 1.0.0 explicitly permits `final_manifest_pending` authoring reports when receiver-side manifest verification is external; this does not waive other not_run or semantic-review limitations.
- The new mock contract is millisecond-based and exact-versioned; the old schema-change request is seconds/ordered-group-ID based and is explicitly superseded.
- The current new-contract example places `mock-forms.json` and timeline inside a batch while allowing `required_batches` to name that same batch's manifest hash. Because the manifest hashes the report and the report would contain the manifest hash, this creates a self-hash cycle. The contract needs an explicit acyclic release topology (source content batches first, separate form package referencing only those source manifests).
- Runtime media duration must be checked against iOS-decoded duration within the stated tolerance; metadata equality alone is insufficient, especially given observed AAC container padding.
- Antigravity reports all 100 unique items as training/ai_checked, 0 human-reviewed and 0 calibrated; batches 0006–0007 are v2 media upgrades with 3 images and 27 m4a files, not 49 new questions.
- The Antigravity mock report still targets the superseded seconds schema and says 93 groups even though its own fixed rows total 103 groups. It is planning evidence only, not an importable form.
- `handoff/2026-10-28/antigravity-contract-status.md` was missing at intake and appeared later. It accepts the former `058894...` hash; the current `f8d3e7...` document still requires explicit re-acceptance.
- The Antigravity handoff confirms Codex is the sole editor of the mock spec this round and requires an acyclic source-package → separate form-package dependency structure.
## 2026-10-28 handoff implementation findings

- `DiagnosticRouter` currently falls back to the entire bank when no diagnostic pool exists. This violates strict purpose isolation and can consume training or mock content.
- `DailyPlanner` currently scores every group in the package, so mock content can enter daily training.
- `AppModel.createLocalBattle` currently takes the first ten Part 5 groups without requiring the battle pool.
- Runtime `QuestionGroup` loses the imported group's `content_status` and `fixture` fields; only pool/layout strings survive in `tags`. Formal eligibility therefore cannot be enforced safely at the service boundary.
- `LocalProfile` has no exposure ledger. Only submitted responses are persisted, so viewing a question and exiting allows it to be selected as unseen again after restart.
- The Part practice UI directly chooses the first matching group, causing repeated selection and providing no explicit new-versus-review choice.
- The immutable seven-batch corpus resolves to 51 groups and 100 unique items; batches 0006/0007 upgrade the listening media versions rather than add questions. These counts still require committed XCTest verification in this round.
- Current mock-form spec uses millisecond timelines and exact group/item version references. The older report still describes seconds/group IDs and must be brought into alignment without claiming formal mock readiness.
- A mock-form package cannot self-reference a manifest hash when that manifest hashes the report itself. The contract needs an acyclic split: source content batches are published first; a separate form package references those immutable source manifest hashes.
- No counterpart contract-status handoff file exists yet, so cross-workspace acceptance remains pending even after local schema/tests are aligned.

## 2026-10-29 verified updates

- The previous "counterpart status missing" note is superseded: Antigravity created `handoff/2026-10-28/antigravity-contract-status.md` and accepted mock-contract hash `0588948a...`. Codex subsequently incorporated its acyclic packaging and AVFoundation-duration clarifications, producing hash `f8d3e708...`; exact-hash shared acceptance is therefore still pending.
- `AVAudioFile.length / processingFormat.sampleRate` is the implemented Apple-decoder duration probe. The formal contract keeps the `<= 100 ms` threshold; Antigravity intends to generate within 5 ms of this API and correctly treats ffprobe container padding as separate evidence.
- The seven immutable exports now have committed regression evidence, not just an audit observation: every installed asset path exists and its bytes match the manifest hash.
- Cross-process networking is now proven locally through URLSession → HTTP → SQLite, including process restart and a deadline worker that settles while clients are signed out. This is not evidence of TLS, public deployment, realtime delivery, APNs, or two physical phones.
- The full build blocker remains Xcode component eligibility, exit 70 before compilation. Whole-source iPhoneOS type checking is supplemental only.

## 2026-10-29 Installed-App MVP Intake

- The user has now installed and opened the App on an iPhone, superseding any inference that an installable App does not exist; this does not prove feature-level acceptance.
- `AppModel.init` reads only the Application Support `ContentVersionStore`. When no active catalog exists it falls back to `SampleContent`; no validated exports are currently bundled or bootstrapped.
- The Xcode resource phase is empty. The user's current signing settings are `DEVELOPMENT_TEAM = VJ3Y39FF2P` and `PRODUCT_BUNDLE_IDENTIFIER = com.local.TOEICPath`; both must be preserved.
- The validated seed is the immutable 0001–0007 set: 51 groups, 100 unique training items, and 30 media assets. Startup must install each batch through `ContentVersionStore.install`, not deserialize a bypass package.
- Audit evidence shows 0008–0010 are contract-invalid and must remain excluded until Antigravity republishes corrected immutable versions.
- The startup bootstrap must cover both first install and an already-installed App whose content store is empty, without deleting or replacing the user's profile or newer imported group versions.

## 2026-10-29 Installed-App MVP Results

- The explicit `SeedContent` folder resource contains byte-identical copies of immutable batches 0001–0007: 74 files, 7 manifests, 51 active groups, 100 unique training items, 27 audio files, and 3 images.
- A single multi-batch transaction now validates every seed package with the real importer, constructs the complete candidate catalog, moves immutable versions, and writes active state only after all steps succeed. A corrupted seventh package leaves the prior state and catalog unchanged.
- Bootstrap is idempotent across restart and does not reset the independent profile store. Tests preserve onboarding, target, due-item state, and a preinstalled synthetic v3 group.
- The current Xcode platform is now usable: the exact generic iPhoneOS build compiles, links, and packages successfully. Earlier exit-70 files remain historical evidence rather than current status.
- Built-App verification is not source-only: the `.app/SeedContent` bytes match the project resource and the bootstrap tests pass when pointed directly at that built directory.
- The battle client now consumes a dedicated `BattleQuestion` projection without correct answer, evidence, or explanation. The server freezes that projection and required assets at match creation; ready accepts only an exact checksum map, and iOS hashes actual local bytes before sending it.
- Both local and HTTP services allow exact replay of an already accepted answer request after submit/timeout/restart, while rejecting new answers and request-ID/data conflicts.
- Antigravity has provided the seed index but no immutable corrected replacement packages or final delivery for 0008–0010. Those original invalid exports remain excluded and unchanged.

## 2026-10-29 Part 1 device feedback

- The first physical-device learning-flow check reached `ag-g-p1-000001`, proving the bundled photo/audio path is reachable, but the user rated the audio muddy. Perceptual audio acceptance is therefore `not_passed`, despite earlier file/hash/waveform checks.
- The bundled file is AAC mono at 22,050 Hz and about 37.6 kbps. Its four segments contain the statements in A→D order but do not audibly announce the letters. Neither fact alone proves the reported muddiness, and upsampling/gain changes are not valid evidence of improvement.
- `PracticeAudioPlayer` stops the existing player before every new playback, so no overlapping player path was found. Normal 1× playback previously enabled AVAudioPlayer rate processing unnecessarily; it now remains disabled unless the learner selects 0.8×.
- The sentence control displayed the next index immediately after starting a segment. The UI now distinguishes the next segment from the currently/previously played semantic label (`選項 A`, `問句`, etc.).
- Training/review now offers an explicit assisted transcript rather than a silently disabled button. Any use is persisted as a non-standard condition even if the transcript is hidden again before submission. Diagnostic/mock/battle locking remains explicit.
- On 2026-10-30 the user selected the third bundled Part 1 comparison, `ag-g-p1-000003` with Karen en_AU, as clearest on the iPhone built-in speaker. This supports Karen as the next controlled voice direction, but the comparison does not isolate codec bitrate, loudness, sample rate, or content as a causal variable.
- Two non-seed control artifacts now reuse the `ag-g-p1-000001` statements and existing pipeline: a Karen version without labels (`8b0b691f...`, 12.777 s) and a Karen version with spoken A–D labels (`a7e99669...`, 13.508 s). A same-device/same-volume user choice is required before requesting an immutable v3 production package.
- The user selected the spoken-label direction but requested a short label-to-statement gap. Synthesizing letters as standalone utterances made Karen unnaturally elongate them; keeping one utterance with a requested 400 ms macOS silence control produced four measured encoded gaps of about 357–359 ms. The resulting comparison artifact is `candidate-karen-labels-400ms-gap.m4a` (`1eae239a...`, 15.556 s) and still requires device acceptance.

## 2026-10-30 simple quick-test findings

- The existing `SessionView` already owns exposure-on-presentation, answer-condition capture, exit confirmation, delayed-reveal behavior for non-practice modes, and idempotent `AppModel.finishSession`; extending its presentation style is safer than introducing a second attempt recorder.
- `UserPreferences` previously relied on synthesized decoding. Adding non-optional quick-test preferences required an explicit backward-compatible decoder so existing on-device profiles default to reading/foundation without being discarded.
- A training quick test can preserve complete groups and reach the largest item count at or below ten with a bounded subset DP. The selection ranking prioritizes unseen families, Part/section coverage, and proximity to the selected editorial difficulty while never crossing purpose pools or repeating a family.
- The current immutable seed has enough complete reading content for the default one-tap path. Listening remains selectable only for groups whose installed media resolves; missing-material IDs are excluded before assembly.

