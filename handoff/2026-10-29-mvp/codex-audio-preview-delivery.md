# Codex Offline Audio Preview Delivery — 2026-11-09

## Outcome

The App now contains an offline, five-pair A/B audio-quality preview at:

`我的 → 題庫與下載 → 音質試聽`

This is a secondary review tool. It does not alter the one-tap Today test, practice scoring, exposure history, or the formal content catalog.

## Implemented

- Bundled the existing ten immutable `.m4a` comparison files as a separate top-level `AudioPreview` folder resource.
- Kept `AudioPreview` outside `SeedContent`; candidate B is labeled `尚未採用` in the UI and is not a formal content replacement.
- Added a typed five-pair catalog with the source SHA-256 for every A and B file.
- Added a SwiftUI preview page with five samples, descriptive Part/context text, and A/B playback rows.
- Applied 18pt spacing between each A/B marker and its option content, matching the current answer-choice rhythm.
- Starting another file first stops the current player. Tapping the active row stops it. Leaving the page or moving the App out of the active scene also stops playback.
- Missing or unplayable files produce a visible red error row instead of silently failing.
- Playback controls have at least a 56pt row height, Dynamic Type support, and explicit VoiceOver labels/state.

## Preserved boundaries

- Signing remains `DEVELOPMENT_TEAM = VJ3Y39FF2P` and `PRODUCT_BUNDLE_IDENTIFIER = com.local.TOEICPath`.
- The formal built-in seed remains seven batches, 51 groups, 100 unique items, 30 formal media assets, and 74 bundled seed files.
- Existing profile/application-support data is not migrated, reset, or written by this feature.
- No Antigravity export, audio source file, seed batch, coordinator file, or synthesis pipeline was modified by this implementation.

## Executed verification

| Verification | Result |
|---|---|
| Source pack SHA-256 audit | 10 / 10 match `listening-pack.json` |
| Targeted `AudioPreviewCatalogTests` | 3 tests, 0 failures |
| Complete SwiftPM regression suite | 78 tests, 0 failures |
| Unsigned generic iPhoneOS `xcodebuild` | `BUILD SUCCEEDED` |
| iPhone 17 Pro Simulator `xcodebuild` | `BUILD SUCCEEDED` |
| Built `.app/AudioPreview` inventory | 10 files; all 10 hashes match catalog |
| Built `.app/SeedContent` inventory | 74 files, unchanged |
| Simulator navigation | `我的 → 音質試聽` reached |
| Simulator playback switching | A playing → B playing; A returned to idle |
| Simulator leave/re-enter | both rows returned to idle |
| Maximum Dynamic Type | rows scrollable, readable, and actionable; restored to Large afterward |

Build/test evidence:

- `artifacts/build/xcodebuild-audio-preview-2026-11-09.log`
- `artifacts/build/xcodebuild-audio-preview-simulator-2026-11-09.log`
- `artifacts/build/swift-test-audio-preview-2026-11-09.log`

收尾時為避免在工作區留下大型未追蹤 DerivedData，已將本輪兩個建置目錄搬至 `/tmp/toeic-audio-preview-derived.qMkazm/`：generic-device 產物位於 `device/Build/Products/Debug-iphoneos/TOEICPath.app`，Simulator 產物位於 `simulator/Build/Products/Debug-iphonesimulator/TOEICPath.app`。兩個 `.app` 在交付補記時仍存在；這是暫存位置，永久驗證證據以以上三份 log 為準。

## Pending physical-device acceptance

- Listen to all five A/B pairs on the iPhone built-in speaker at a fixed volume and decide whether candidate B is actually preferable.
- Confirm the spoken A–D / A–C labels and short label-to-copy interval feel natural.
- Run a hands-on VoiceOver traversal and audio-interruption check.

These items are deliberately not marked passed. Candidate B remains comparison-only until the physical listening decision and a separately reviewed immutable production batch are available.
