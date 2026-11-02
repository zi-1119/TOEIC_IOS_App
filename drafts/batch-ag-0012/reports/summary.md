# 批次摘要報告：`batch-ag-0012`（Supersedes `batch-ag-0009` `v1` -> `v2`）

- **用途池（Pool）**：`diagnostic`
- **版本狀態**：`version=2`（不可變修訂包，正式取代因巢狀 Schema 缺失被匯入器拒絕之 `batch-ag-0009` `v1`）
- **批次定位**：修正 `batch-ag-0009` 之巢狀 Schema 缺失並升版為 `version=2`（`pool="diagnostic"`，涵蓋 Part 1–7 共 14 組 24 題，含 1 張 Part 1 實景圖與 8 個 `.m4a` 音檔，全部 `status="ready"`）。
- **題組數（Groups）**：14
- **可評分小題數（Items）**：24
- **內容審核狀態**：`ai_checked`（0 題宣稱 `human_reviewed`）
- **媒體就緒狀態**：本批內所有宣告之音訊／圖片素材均為 `status="ready"`（0 個 `planned` 缺項）

## 題型與題數分布

| 題型 | 用途池 | 題組數 | 小題數 |
|---|---|---:|---:|
| Part 1 | `diagnostic` | 1 | 1 |
| Part 2 | `diagnostic` | 4 | 4 |
| Part 3 | `diagnostic` | 2 | 6 |
| Part 4 | `diagnostic` | 1 | 3 |
| Part 5 | `diagnostic` | 4 | 4 |
| Part 6 | `diagnostic` | 1 | 4 |
| Part 7 | `diagnostic` | 1 | 2 |
| **合計** | **`diagnostic`** | **14** | **24** |

## 版本修訂清單（`v1` `batch-ag-0009` → `v2` `batch-ag-0012`）

1. **保留原 ID 與家族**：所有 `group_id`、`item_id`、`family_id`、`pool`、題幹、選項、正解及已驗收媒體檔案 100% 保持不變，`version` 由 `1` 遞增為 `2`。
2. **補齊 `evidence.reasoning_zh`**：為全部小題之每一筆 `evidence` 補齊具體中文佐證推理說明。
3. **修正 `vocabulary` 結構**：由舊欄位 `surface`/`pos`/`note_zh`（及 `ag-i-p7-000009-1` 之陣列誤植）全面轉為符合 `specs/group.schema.json` 之 `term_en`、`meaning_zh` 與完整商務英文例句 `example_en`。
4. **修正 `stimulus.documents` 欄位**：由 `doc_id`/`doc_type` 修正為契約定義之 `document_id`/`genre`。
5. **移除未宣告額外欄位**：移除 `distractor_notes.trap_type` 與 `provenance.prompt_hash`（符合 `additionalProperties: false`）。
6. **修正 `reviews.jsonl` 結構**：於每筆 `findings` 補齊必填欄位 `"item_id": null`，並將 `group_version` 更新為 `2`。
