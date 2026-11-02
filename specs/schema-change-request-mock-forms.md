# Schema Change Request: Mock Form and Listening Timeline

Status: superseded; retained only as change history｜2026-10-28

Do not implement the JSON example or seconds-based fields formerly described here. The only current candidate is `specs/mock-form-contract-v1.md`, which uses exact `group_refs`, source manifest hashes, millisecond fields, authored timeline events, decoded-media duration checks, and an acyclic source-batch → form-package dependency. It remains pending until both workspaces record acceptance of the same document SHA-256.

## Problem

Content Contract 1.0.0 requires four immutable 200-item mock forms and says the listening timeline must include directions, speech, and pauses. It does not define the filename or machine-readable schema for each form's ordered groups/items, audio timeline assets, per-item unlock points, or total verified playback duration.

The App must not infer a listening timeline by evenly distributing roughly 45 minutes. Without an authoritative form record it cannot safely guarantee identical ordering/assets, prevent future-question exposure, restore an interrupted attempt to the original deadline, or distinguish a complete listening form from 100 unrelated listening items.

## Historical proposal (not accepted)

The following example is intentionally retained to explain the incompatibility. It must be rejected by the current importer because it uses ID-only references and seconds:

```json
{
  "form_schema_version": "1.0.0",
  "content_schema_version": "1.0.0",
  "forms": [
    {
      "form_id": "mock-form-01",
      "content_version": "immutable release identifier",
      "ordered_group_ids": ["..."],
      "ordered_item_ids": ["... 200 total ..."],
      "listening_item_ids": ["... 100 total ..."],
      "reading_item_ids": ["... 100 total ..."],
      "listening_unlock_offsets_sec": {"item_id": 123},
      "listening_duration_sec": 2704,
      "reading_time_limit_sec": 4500,
      "audio_timeline_asset_ids": ["one-composited-timeline-asset"]
    }
  ]
}
```

## Validation

- Each form contains exactly the official Part counts: 6 / 25 / 39 / 30 / 30 / 16 / 54.
- `ordered_item_ids` is exactly `listening_item_ids + reading_item_ids`; all IDs and group IDs belong to the same immutable mock pool/version and are unique within the form.
- Part 7 contains 29 single-passage items and 25 double/triple-passage items without splitting a group.
- Every listening item has a nondecreasing unlock offset inside the verified timeline duration.
- The first App version requires exactly one composited, `ready`, hash-verified timeline audio asset per form. Its authored schedule covers directions, question audio, response options where applicable, and pauses. A future contract may add a segment playlist only together with deterministic cross-file seek semantics.
- `listening_duration_sec` is derived from the actual verified timeline, not a target typed by the author.
- `reading_time_limit_sec` is exactly 4,500.
- Four forms do not share groups or families with training, battle, diagnostic, or one another.

## Security projection

The private batch form may reference answers through its groups, but the learner/battle delivery API returns a mode-safe projection without correct answers, explanations, evidence, or locked transcripts until submission. This proposal does not authorize shipping raw `groups.jsonl` directly to a client.

Until both workspaces approve the exact current contract hash, Codex keeps the mock runtime implemented but refuses to start a complete listening mock merely because 200 items are present. Producers must use the current millisecond contract, not this historical example.
