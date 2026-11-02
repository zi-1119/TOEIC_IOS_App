# Content Import Implementation Notes

The authoritative exchange format is [`specs/content-contract-v1.md`](../specs/content-contract-v1.md), supplemented by [`specs/validation-report-v1.md`](../specs/validation-report-v1.md). Those files are not redefined here.

The app uses two intentionally separate models:

1. `ContentBatchContract.swift` mirrors the snake-case 1.0.0 exchange format and validates the immutable batch directory, manifest file list, SHA-256 hashes, JSONL records, review references, report counts, Part semantics, paths, IDs, pools, assets, and source evidence.
2. `ContentModels.swift` is the smaller runtime projection used after import. It contains only fields needed to render and route questions. The private authoring package, answers, evidence, and transcripts must not be sent wholesale to a battle or exam client; a production content service creates a mode-safe projection.

An import copies the selected directory into app-owned staging, checks the complete package, then atomically moves it into `Content/Versions/<batch_id>`. `state.json` atomically stores both the immutable cross-batch index and the ordered active-batch catalog. The store now reconstructs the entire candidate catalog—including optional mock-form reports—before writing `state.json`; a failed merge, mock-form validation, or state write leaves the previously active catalog unchanged.

At startup every active immutable batch is revalidated and projected. Groups merge by permanent `group_id`; the highest explicit group version is selected while unrelated groups remain active. Runtime group and response records retain `version` and `sourceBatchID`. Ready asset IDs are namespaced as `<batch_id>::<asset_id>` and their absolute paths point to that batch's immutable directory, preventing collisions or accidental path rebasing.

The former `index.json` plus single `active.json` layout is read as a one-batch legacy state. The next successful activation writes the unified state format.

Executed integration coverage imports the untouched five Antigravity exports, reconstructs the store, repeats an import, applies a higher-version merge fixture, and corrupts a staged copy to verify rollback. The source exports are never modified.

Fixture content uses the `cx-` prefix and does not count toward the 4,800-item quota. Missing planned media is allowed for authoring preview and is not represented as ready runtime media. Release validation must reject missing required ready media as defined by the authoritative contract.

For the current five exports this yields 51 fully practiceable reading items and 49 listening items with planned-but-absent material. Those listening groups remain visible as authoring previews, but missing audio/photo sets a nonstandard answer condition and cannot contribute standard listening evidence.

The additive `reports/mock-forms.json` baseline is decoded when present. Activation resolves every group by `group_id + version + source_batch_id`, verifies required batch manifest hashes, registers whole-form assets under the owning batch namespace, validates the exact 200-item expansion and official Part counts, checks the 29/25 Part 7 split, and preserves timeline offsets in milliseconds. No current Antigravity export contains this report, so decoder support does not imply that a production form or timeline audio exists.
