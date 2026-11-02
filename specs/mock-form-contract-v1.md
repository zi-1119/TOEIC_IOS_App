# Mock Form Additive Contract 1.0.0

Status: Codex implementation baseline, revision 2026-10-28; awaiting Antigravity acceptance of the exact file hash. It is not part of Content Contract 1.0.0 until both producers record acceptance of the same hash.

This document defines the missing machine-readable boundary for a fixed 200-item TOEIC Listening & Reading form. A runtime implementation alone is not evidence that a usable form exists. A form is usable only after this file, every referenced group version, and the composited timeline asset pass validation together.

## Package location and manifest registration

- File: `reports/mock-forms.json`.
- The file must appear in `manifest.json.files` with its SHA-256.
- Every timeline binary must live under `assets/mock/<form_id>/` and independently appear in `manifest.json.files` with its SHA-256.
- Timeline assets are registered in the top-level `assets` array inside `reports/mock-forms.json`. They are not duplicated into an arbitrary question group's `assets` array because they belong to the whole form.
- Paths are relative package paths and inherit all traversal, symlink, inventory, and checksum rules from Content Contract 1.0.0.

## Acyclic package dependency

The content sources and form definition are separate immutable packages:

1. Publish one or more **source content batches** first. They contain the `pool=mock`, `fixture=false`, `human_reviewed` groups and their group-level assets. Their final `manifest.json` bytes can now be hashed.
2. Publish a later **form package** containing an empty-but-registered `groups.jsonl`, the normal required reports, `reports/mock-forms.json`, and the whole-form audio under `assets/mock/<form_id>/`.
3. `content_set.required_batches` in the form package lists every source content batch used by `group_refs`, with the SHA-256 of each already-final source `manifest.json`.
4. The form package must not list its own batch ID in `required_batches`. Its manifest hashes `reports/mock-forms.json`, while that report references only earlier source-manifest hashes. This ordering makes every hash computable and prevents a manifest/report self-hash cycle.

Every `group_ref.source_batch_id` must appear exactly once in `required_batches`. A form package may define multiple forms and timeline assets, but each timeline asset remains owned and namespaced by the form package.

## Wire format

All durations and offsets use integer milliseconds.

```json
{
  "form_schema_version": "1.0.0",
  "content_schema_version": "1.0.0",
  "content_set": {
    "content_set_id": "mock-release-2026-01",
    "required_batches": [
      {"batch_id": "batch-mock-01", "manifest_sha256": "64 lowercase hex"}
    ]
  },
  "assets": [
    {
      "asset_id": "mock-form-01-timeline",
      "kind": "mock_audio_timeline",
      "path": "assets/mock/mock-form-01/timeline.m4a",
      "sha256": "64 lowercase hex",
      "mime_type": "audio/mp4",
      "duration_ms": 2704000,
      "review_state": "human_reviewed"
    }
  ],
  "forms": [
    {
      "form_id": "mock-form-01",
      "revision": 1,
      "group_refs": [
        {"group_id": "ag-g-p1-000001", "version": 2, "source_batch_id": "batch-mock-01"}
      ],
      "ordered_item_ids": ["200 permanent item IDs"],
      "listening_item_ids": ["100 permanent item IDs"],
      "reading_item_ids": ["100 permanent item IDs"],
      "listening_timeline": {
        "asset_id": "mock-form-01-timeline",
        "duration_ms": 2704000,
        "events": [
          {
            "sequence": 0,
            "kind": "directions",
            "start_ms": 0,
            "end_ms": 32000,
            "item_ids": []
          },
          {
            "sequence": 1,
            "kind": "item_unlock",
            "start_ms": 32000,
            "end_ms": 32000,
            "item_ids": ["ag-i-p1-000001"]
          },
          {
            "sequence": 2,
            "kind": "stimulus",
            "start_ms": 32000,
            "end_ms": 39000,
            "item_ids": ["ag-i-p1-000001"]
          },
          {
            "sequence": 3,
            "kind": "response_window",
            "start_ms": 39000,
            "end_ms": 44000,
            "item_ids": ["ag-i-p1-000001"]
          }
        ]
      },
      "reading_time_limit_ms": 4500000
    }
  ]
}
```

Allowed event kinds are `directions`, `item_unlock`, `stimulus`, `response_options`, `response_window`, and `pause`. `item_unlock` is a zero-duration event; all other events have `end_ms > start_ms`.

## Identity and version rules

- `form_id + revision` is immutable. Any change to ordering, a group version, timing, audio bytes, or timeline event requires a higher revision.
- Each `group_ref` includes the permanent `group_id`, exact positive `version`, and immutable source batch. Resolution by ID alone is forbidden.
- `ordered_item_ids` must exactly equal the item order obtained by expanding `group_refs`; a group may not be split.
- A multi-batch active catalog may contain newer training versions, but the form resolves only the exact versions named in `group_refs`.
- Every `required_batches` entry is verified against the installed manifest bytes. Missing or different batches make the form unavailable rather than silently substituting content.
- Four released forms may not share group IDs or family IDs with one another, training, diagnostic, or battle pools.
- Every resolved group is `pool=mock`, `fixture=false`, and `content_status=human_reviewed`. Draft, AI-only, quarantined, retired, unknown, or fixture groups cannot activate a formal form.

## Form validation

- Exactly 200 unique items with official counts 6 / 25 / 39 / 30 / 30 / 16 / 54.
- Exactly 100 listening items followed by exactly 100 reading items.
- Part 7 includes 29 single-passage questions and 25 multiple-passage questions, preserving complete groups.
- Exactly one registered `mock_audio_timeline` asset is referenced per form in version 1.0.0.
- Asset `duration_ms`, iOS-decoded media duration, and timeline `duration_ms` must agree within 100 ms. Container metadata from another decoder is supporting evidence, not a substitute for the iOS decode check.
- Timeline events are sorted by `sequence`; times are nonnegative and inside the asset duration. Non-pause audio events may not overlap.
- Each listening item has exactly one `item_unlock`. Unlock order follows `listening_item_ids` and never exposes a future item early.
- The timeline includes directions, stimuli, spoken response options where the Part requires them, and authored response windows/pauses. Duration is derived from the verified asset, never filled from a 45-minute target.
- `reading_time_limit_ms` is exactly 4,500,000.
- The report, group files, manifest, and every referenced asset must pass as one staged transaction before activation.

## Playback and restoration rules

On first start the client persists `form_id`, `revision`, resolved group versions, timeline asset checksum, attempt ID, wall-clock section start, monotonic playback position, and fixed listening deadline. The deadline is `section_start + duration_ms` and is never recreated on resume.

While foregrounded, the visible item set is derived from passed `item_unlock` events. Seeking forward, user scrubbing, pause, and playback-rate controls are disabled. Backgrounding, route changes, media-service reset, calls, and audio interruptions are recorded with begin/end times.

After relaunch or foreground return:

1. Revalidate the same form revision, exact group versions, and local asset checksum.
2. Compute expected position from the original wall-clock section start.
3. Seek the same composited asset to that position; never restart the section or extend its deadline.
4. Replay no missed answer window. Previously accepted selections remain available.
5. If the deadline passed, enter the section break immediately.

If the asset is absent, corrupt, replaced, or cannot resume consistently, the attempt is not called a completed standard mock. Preserve accepted answers and mark the attempt `invalid_material`, `invalid_audio`, or `service_interruption` for later policy handling. User exit remains distinct from service failure.

Reading starts only after the listening section reaches its fixed deadline or a server-authorized invalidation. Its 75-minute deadline is likewise persisted and never reset.

## Delivery and answer security

The authoring package may contain answers and explanations. A learner delivery projection must omit correct answers, distractor analysis, evidence, and locked transcripts until final submission. The server freezes form revision, ordered IDs, group versions, asset checksum, start, and deadlines for battles or remotely synchronized mock attempts. The client never authors an authoritative score.

## Current implementation status

The iOS runtime enforces a single composited asset, immutable section deadlines, millisecond item unlock offsets, delayed reveal, interruption records, and resume seeking. The importer decodes this additive report, rejects self-referential form packages, verifies required source-manifest hashes, resolves exact group versions across active batches, requires formal mock group status, validates official counts/timeline events, probes decoded audio duration, and registers the whole-form asset under its immutable form-package namespace. XCTest covers missing source packages, wrong versions/hashes, seconds-versus-milliseconds mistakes, missing/unreadable audio, decoded-duration mismatch, duplicate/missing/backward/out-of-range unlocks, and misplaced assets. No accepted package currently implements the report or supplies a verified composited audio file, so complete mock exams remain unavailable. Long-duration playback and interruption behavior still require simulator/device acceptance.
