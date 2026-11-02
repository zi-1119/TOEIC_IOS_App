# 批次變更清單（Changelog）— `batch-ag-0006`

- **批次標題**：第一階段聽力四題型可播放樣本包（Part 1–4 各一完整題組，v2 實體音圖就緒）
- **建立時間**：`2026-10-27T16:07:23Z`
- **升級題組數**：4 組（共 8 道可評分小題）
- **版本原則**：保留原 `group_id`、`item_id` 與 `family_id`，`version` 由 `1` 遞增為 `2`；原始 `exports/batch-ag-0001` 至 `0005` 維持不可變。

## 逐題組變更明細

| 題組 ID | Part | 原批次 (v1) | 新版本 | 小題 ID | 素材與審查變更說明 |
|---|---:|---|---|---|---|
| `ag-g-p1-000001` | Part 1 | `batch-ag-0002` | `v2` | `ag-i-p1-000001-1` | 圖片 `ag-ast-p1-000001-image`: `planned` -> `ready` (`assets/ag-ast-p1-000001-image.jpg`, sha256=`70bbdf4c595f...`)<br>音訊 `ag-ast-p1-000001-audio`: `planned` -> `ready` (`assets/ag-ast-p1-000001-audio.m4a`, 15017 ms, 4 段時間碼, sha256=`684cd4b76474...`)<br>審查：補齊真實照片後完成獨立視覺盲解（`blind: false -> true`） |
| `ag-g-p2-000001` | Part 2 | `batch-ag-0001` | `v2` | `ag-i-p2-000001-1` | 音訊 `ag-ast-p2-000001-audio`: `planned` -> `ready` (`assets/ag-ast-p2-000001-audio.m4a`, 12974 ms, 4 段時間碼, sha256=`b878ab1d5df7...`) |
| `ag-g-p3-000001` | Part 3 | `batch-ag-0003` | `v2` | `ag-i-p3-000001-1`, `ag-i-p3-000001-2`, `ag-i-p3-000001-3` | 音訊 `ag-ast-p3-000001-audio`: `planned` -> `ready` (`assets/ag-ast-p3-000001-audio.m4a`, 64308 ms, 9 段時間碼, sha256=`7a8ddb3b6b03...`) |
| `ag-g-p4-000001` | Part 4 | `batch-ag-0004` | `v2` | `ag-i-p4-000001-1`, `ag-i-p4-000001-2`, `ag-i-p4-000001-3` | 音訊 `ag-ast-p4-000001-audio`: `planned` -> `ready` (`assets/ag-ast-p4-000001-audio.m4a`, 60672 ms, 6 段時間碼, sha256=`d962cacb040a...`) |
