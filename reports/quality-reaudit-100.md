# 現有 100 題逐題品質補驗與盲解模態追溯報告（Traceable 100-Item Quality & Blind-Solve Audit）

- **補驗時間（UTC）**：`2026-10-28T08:29:13Z`
- **涵蓋範圍**：`exports/batch-ag-0001` 至 `0007` 按最高題組版本合併後之 **51 個唯一題組、100 道唯一可評分小題**（`pool=training`, `content_status=ai_checked`）。
- **嚴格邊界聲明**：
  1. **Editorial Difficulty**：D1–D5 分布為 **D1: 8、D2: 17、D3: 26、D4: 33、D5: 16**，全數為 `basis="editorial"` 編輯預估難度，**尚未經真人施測與心理計量校準（`calibrated=0`）**。
  2. **盲解模態誠實區分**：
     - **純閱讀題獨立文字盲解（Part 5–7）**：**51 / 51 題通過**（`blind=true`）。
     - **聽力題獨立逐字稿盲解（Part 2–4）**：**46 / 46 題通過**（`blind=true`，子代理係讀取移除答案之 `audio_script` 逐字稿解題，**非聽取音檔波形解題**）。
     - **Part 1 真實圖片視覺盲解（v2 補圖後）**：**3 / 3 題通過**（`blind=true`，子代理於 v2 直接檢視 1200×896 JPEG 照片與四個英文選項作答；v1 無圖時誠實標記 `blind=false`）。
     - **純聽音檔不看稿盲解（Audio-Only Blind Solve）**：**`not_run`（0 / 49 題）**。
     - **真人命題審閱與實際聽審（`human_reviewed`）**：**`not_run`（0 / 100 題）**。已建立可操作之真人審閱包於 `review/human_review_pack_phase1/`。

---

## 一、語意與題型專項檢查結果（Semantic & Part-Specific Quality Gates）

| 專項檢查項目 | 檢查結果 | 涵蓋題數 | 具體核驗內容 |
|---|---|---:|---|
| Part 2 間接回應唯一性檢查 | **通過** | 6 題 | 逐題確認含 `indirect_response` 標籤之小題，其餘兩個干擾選項皆因疑問詞不合、時態衝突或諧音誤導而明確不合理，無兩項皆通之情形 |
| Part 3 / Part 4 聽力證據支撐檢查 | **通過** | 33 題 | 全部 33 道小題之 `evidence` 均精確引用對應 `audio_segment`（圖表整合題同時引用 `document_block` 表格列），無超出對白之臆測題 |
| Part 6 句子插入篇章邏輯檢查 | **通過** | 2 題 | 2 組 Part 6 各含 1 道完整句插入題（`ag-i-p6-000001-3`, `ag-i-p6-000002-3`），均透過前後句代名詞與因果轉折確立唯一可插入句 |
| Part 7 多篇跨文件整合檢查 | **通過** | 3 組 (15 題) | 2 組雙篇與 1 組三篇均包含必須同時比對兩份以上文件（如報價單對照修訂信、保固條款對照報修單、時程表對照場地變更信）始能作答之跨文件題 |
| D4 / D5 高難度命題合理性檢查 | **通過** | 49 題 (D4:33, D5:16) | 難度均來自同義改寫、多條件排除、語用意圖或跨段整合，無罕見專業術語、病句或漏資訊 |
| 正解位置分布與形式線索檢查 | **通過** | 100 題 | 如下表所示，各選項分布自然均衡，且正確選項無固定最長或最短之表面形式線索 |

### 各 Part 正解位置（A / B / C / D）分布表

| Part | A | B | C | D | 總題數 |
|---|---:|---:|---:|---:|---:|
| Part 1 | 1 | 1 | 1 | 0 | 3 |
| Part 2 | 7 | 4 | 2 | — | 13 |
| Part 3 | 1 | 12 | 4 | 1 | 18 |
| Part 4 | 0 | 6 | 8 | 1 | 15 |
| Part 5 | 5 | 4 | 5 | 1 | 15 |
| Part 6 | 4 | 3 | 1 | 0 | 8 |
| Part 7 | 8 | 12 | 7 | 1 | 28 |

---

## 二、100 題逐題證據、盲解模態與審閱狀態追溯表

| 最新批次 (版本) | 題組 ID | 小題 ID | Part | 難度 | 正解 | 證據來源 (`source_type:source_id`) | AI 盲解模態與結果 | 聽音檔盲解 | 真人審閱 |
|---|---|---|---:|---|---|---|---|:---:|:---:|
| `batch-ag-0006` (v2) | `ag-g-p2-000001` | `ag-i-p2-000001-1` | Part 2 | D1 | **A** | `audio_segment:ag-g-p2-000001-seg-q, audio_segment:ag-g-p2-000001-seg-a` | transcript_text_isolated_subagent (blind=true) (`A == A`) | `not_run (未僅憑音檔盲解)` | `pending (human_reviewed=0)` |
| `batch-ag-0007` (v2) | `ag-g-p2-000002` | `ag-i-p2-000002-1` | Part 2 | D2 | **B** | `audio_segment:ag-g-p2-000002-seg-q, audio_segment:ag-g-p2-000002-seg-b` | transcript_text_isolated_subagent (blind=true) (`B == B`) | `not_run (未僅憑音檔盲解)` | `pending (human_reviewed=0)` |
| `batch-ag-0007` (v2) | `ag-g-p2-000003` | `ag-i-p2-000003-1` | Part 2 | D3 | **C** | `audio_segment:ag-g-p2-000003-seg-q, audio_segment:ag-g-p2-000003-seg-c` | transcript_text_isolated_subagent (blind=true) (`C == C`) | `not_run (未僅憑音檔盲解)` | `pending (human_reviewed=0)` |
| `batch-ag-0007` (v2) | `ag-g-p2-000004` | `ag-i-p2-000004-1` | Part 2 | D2 | **A** | `audio_segment:ag-g-p2-000004-seg-q, audio_segment:ag-g-p2-000004-seg-a` | transcript_text_isolated_subagent (blind=true) (`A == A`) | `not_run (未僅憑音檔盲解)` | `pending (human_reviewed=0)` |
| `batch-ag-0007` (v2) | `ag-g-p2-000005` | `ag-i-p2-000005-1` | Part 2 | D3 | **A** | `audio_segment:ag-g-p2-000005-seg-q, audio_segment:ag-g-p2-000005-seg-a` | transcript_text_isolated_subagent (blind=true) (`A == A`) | `not_run (未僅憑音檔盲解)` | `pending (human_reviewed=0)` |
| `batch-ag-0007` (v2) | `ag-g-p2-000006` | `ag-i-p2-000006-1` | Part 2 | D2 | **A** | `audio_segment:ag-g-p2-000006-seg-q, audio_segment:ag-g-p2-000006-seg-a` | transcript_text_isolated_subagent (blind=true) (`A == A`) | `not_run (未僅憑音檔盲解)` | `pending (human_reviewed=0)` |
| `batch-ag-0007` (v2) | `ag-g-p2-000007` | `ag-i-p2-000007-1` | Part 2 | D4 | **B** | `audio_segment:ag-g-p2-000007-seg-q, audio_segment:ag-g-p2-000007-seg-b` | transcript_text_isolated_subagent (blind=true) (`B == B`) | `not_run (未僅憑音檔盲解)` | `pending (human_reviewed=0)` |
| `batch-ag-0007` (v2) | `ag-g-p2-000008` | `ag-i-p2-000008-1` | Part 2 | D5 | **C** | `audio_segment:ag-g-p2-000008-seg-q, audio_segment:ag-g-p2-000008-seg-c` | transcript_text_isolated_subagent (blind=true) (`C == C`) | `not_run (未僅憑音檔盲解)` | `pending (human_reviewed=0)` |
| `batch-ag-0001` (v1) | `ag-g-p5-000001` | `ag-i-p5-000001-1` | Part 5 | D1 | **B** | `item_prompt:ag-i-p5-000001-1` | reading_stimulus_isolated_subagent (blind=true) (`B == B`) | `not_applicable (純閱讀題)` | `pending (human_reviewed=0)` |
| `batch-ag-0001` (v1) | `ag-g-p5-000002` | `ag-i-p5-000002-1` | Part 5 | D2 | **C** | `item_prompt:ag-i-p5-000002-1` | reading_stimulus_isolated_subagent (blind=true) (`C == C`) | `not_applicable (純閱讀題)` | `pending (human_reviewed=0)` |
| `batch-ag-0001` (v1) | `ag-g-p5-000003` | `ag-i-p5-000003-1` | Part 5 | D2 | **A** | `item_prompt:ag-i-p5-000003-1` | reading_stimulus_isolated_subagent (blind=true) (`A == A`) | `not_applicable (純閱讀題)` | `pending (human_reviewed=0)` |
| `batch-ag-0001` (v1) | `ag-g-p5-000004` | `ag-i-p5-000004-1` | Part 5 | D3 | **B** | `item_prompt:ag-i-p5-000004-1` | reading_stimulus_isolated_subagent (blind=true) (`B == B`) | `not_applicable (純閱讀題)` | `pending (human_reviewed=0)` |
| `batch-ag-0001` (v1) | `ag-g-p5-000005` | `ag-i-p5-000005-1` | Part 5 | D2 | **B** | `item_prompt:ag-i-p5-000005-1` | reading_stimulus_isolated_subagent (blind=true) (`B == B`) | `not_applicable (純閱讀題)` | `pending (human_reviewed=0)` |
| `batch-ag-0001` (v1) | `ag-g-p5-000006` | `ag-i-p5-000006-1` | Part 5 | D1 | **D** | `item_prompt:ag-i-p5-000006-1` | reading_stimulus_isolated_subagent (blind=true) (`D == D`) | `not_applicable (純閱讀題)` | `pending (human_reviewed=0)` |
| `batch-ag-0001` (v1) | `ag-g-p5-000007` | `ag-i-p5-000007-1` | Part 5 | D4 | **C** | `item_prompt:ag-i-p5-000007-1` | reading_stimulus_isolated_subagent (blind=true) (`C == C`) | `not_applicable (純閱讀題)` | `pending (human_reviewed=0)` |
| `batch-ag-0001` (v1) | `ag-g-p5-000008` | `ag-i-p5-000008-1` | Part 5 | D3 | **C** | `item_prompt:ag-i-p5-000008-1` | reading_stimulus_isolated_subagent (blind=true) (`C == C`) | `not_applicable (純閱讀題)` | `pending (human_reviewed=0)` |
| `batch-ag-0001` (v1) | `ag-g-p5-000009` | `ag-i-p5-000009-1` | Part 5 | D4 | **A** | `item_prompt:ag-i-p5-000009-1` | reading_stimulus_isolated_subagent (blind=true) (`A == A`) | `not_applicable (純閱讀題)` | `pending (human_reviewed=0)` |
| `batch-ag-0001` (v1) | `ag-g-p5-000010` | `ag-i-p5-000010-1` | Part 5 | D3 | **A** | `item_prompt:ag-i-p5-000010-1` | reading_stimulus_isolated_subagent (blind=true) (`A == A`) | `not_applicable (純閱讀題)` | `pending (human_reviewed=0)` |
| `batch-ag-0001` (v1) | `ag-g-p5-000011` | `ag-i-p5-000011-1` | Part 5 | D5 | **C** | `item_prompt:ag-i-p5-000011-1` | reading_stimulus_isolated_subagent (blind=true) (`C == C`) | `not_applicable (純閱讀題)` | `pending (human_reviewed=0)` |
| `batch-ag-0001` (v1) | `ag-g-p5-000012` | `ag-i-p5-000012-1` | Part 5 | D5 | **A** | `item_prompt:ag-i-p5-000012-1` | reading_stimulus_isolated_subagent (blind=true) (`A == A`) | `not_applicable (純閱讀題)` | `pending (human_reviewed=0)` |
| `batch-ag-0006` (v2) | `ag-g-p1-000001` | `ag-i-p1-000001-1` | Part 1 | D1 | **A** | `asset:ag-ast-p1-000001-image, audio_segment:ag-g-p1-000001-seg-a` | real_photo_visual_plus_choice_text (v2 blind=true; v1 was blind=false) (`A == A`) | `not_run (未僅憑音檔盲解)` | `pending (human_reviewed=0)` |
| `batch-ag-0007` (v2) | `ag-g-p1-000002` | `ag-i-p1-000002-1` | Part 1 | D3 | **C** | `asset:ag-ast-p1-000002-image, audio_segment:ag-g-p1-000002-seg-c` | real_photo_visual_plus_choice_text (v2 blind=true; v1 was blind=false) (`C == C`) | `not_run (未僅憑音檔盲解)` | `pending (human_reviewed=0)` |
| `batch-ag-0007` (v2) | `ag-g-p1-000003` | `ag-i-p1-000003-1` | Part 1 | D4 | **B** | `asset:ag-ast-p1-000003-image, audio_segment:ag-g-p1-000003-seg-b` | real_photo_visual_plus_choice_text (v2 blind=true; v1 was blind=false) (`B == B`) | `not_run (未僅憑音檔盲解)` | `pending (human_reviewed=0)` |
| `batch-ag-0007` (v2) | `ag-g-p2-000009` | `ag-i-p2-000009-1` | Part 2 | D1 | **A** | `audio_segment:ag-g-p2-000009-seg-q, audio_segment:ag-g-p2-000009-seg-a` | transcript_text_isolated_subagent (blind=true) (`A == A`) | `not_run (未僅憑音檔盲解)` | `pending (human_reviewed=0)` |
| `batch-ag-0007` (v2) | `ag-g-p2-000010` | `ag-i-p2-000010-1` | Part 2 | D2 | **A** | `audio_segment:ag-g-p2-000010-seg-q, audio_segment:ag-g-p2-000010-seg-a` | transcript_text_isolated_subagent (blind=true) (`A == A`) | `not_run (未僅憑音檔盲解)` | `pending (human_reviewed=0)` |
| `batch-ag-0007` (v2) | `ag-g-p2-000011` | `ag-i-p2-000011-1` | Part 2 | D3 | **B** | `audio_segment:ag-g-p2-000011-seg-q, audio_segment:ag-g-p2-000011-seg-b` | transcript_text_isolated_subagent (blind=true) (`B == B`) | `not_run (未僅憑音檔盲解)` | `pending (human_reviewed=0)` |
| `batch-ag-0007` (v2) | `ag-g-p2-000012` | `ag-i-p2-000012-1` | Part 2 | D4 | **A** | `audio_segment:ag-g-p2-000012-seg-q, audio_segment:ag-g-p2-000012-seg-a` | transcript_text_isolated_subagent (blind=true) (`A == A`) | `not_run (未僅憑音檔盲解)` | `pending (human_reviewed=0)` |
| `batch-ag-0007` (v2) | `ag-g-p2-000013` | `ag-i-p2-000013-1` | Part 2 | D5 | **B** | `audio_segment:ag-g-p2-000013-seg-q, audio_segment:ag-g-p2-000013-seg-b` | transcript_text_isolated_subagent (blind=true) (`B == B`) | `not_run (未僅憑音檔盲解)` | `pending (human_reviewed=0)` |
| `batch-ag-0002` (v1) | `ag-g-p5-000013` | `ag-i-p5-000013-1` | Part 5 | D2 | **C** | `item_prompt:ag-i-p5-000013-1` | reading_stimulus_isolated_subagent (blind=true) (`C == C`) | `not_applicable (純閱讀題)` | `pending (human_reviewed=0)` |
| `batch-ag-0002` (v1) | `ag-g-p5-000014` | `ag-i-p5-000014-1` | Part 5 | D4 | **A** | `item_prompt:ag-i-p5-000014-1` | reading_stimulus_isolated_subagent (blind=true) (`A == A`) | `not_applicable (純閱讀題)` | `pending (human_reviewed=0)` |
| `batch-ag-0002` (v1) | `ag-g-p5-000015` | `ag-i-p5-000015-1` | Part 5 | D5 | **B** | `item_prompt:ag-i-p5-000015-1` | reading_stimulus_isolated_subagent (blind=true) (`B == B`) | `not_applicable (純閱讀題)` | `pending (human_reviewed=0)` |
| `batch-ag-0002` (v1) | `ag-g-p6-000001` | `ag-i-p6-000001-1` | Part 6 | D3 | **B** | `document_block:ag-blk-p6-000001-1` | reading_stimulus_isolated_subagent (blind=true) (`B == B`) | `not_applicable (純閱讀題)` | `pending (human_reviewed=0)` |
| `batch-ag-0002` (v1) | `ag-g-p6-000001` | `ag-i-p6-000001-2` | Part 6 | D3 | **A** | `document_block:ag-blk-p6-000001-1` | reading_stimulus_isolated_subagent (blind=true) (`A == A`) | `not_applicable (純閱讀題)` | `pending (human_reviewed=0)` |
| `batch-ag-0002` (v1) | `ag-g-p6-000001` | `ag-i-p6-000001-3` | Part 6 | D3 | **B** | `document_block:ag-blk-p6-000001-1` | reading_stimulus_isolated_subagent (blind=true) (`B == B`) | `not_applicable (純閱讀題)` | `pending (human_reviewed=0)` |
| `batch-ag-0002` (v1) | `ag-g-p6-000001` | `ag-i-p6-000001-4` | Part 6 | D3 | **A** | `document_block:ag-blk-p6-000001-1` | reading_stimulus_isolated_subagent (blind=true) (`A == A`) | `not_applicable (純閱讀題)` | `pending (human_reviewed=0)` |
| `batch-ag-0002` (v1) | `ag-g-p6-000002` | `ag-i-p6-000002-1` | Part 6 | D4 | **B** | `document_block:ag-blk-p6-000002-1` | reading_stimulus_isolated_subagent (blind=true) (`B == B`) | `not_applicable (純閱讀題)` | `pending (human_reviewed=0)` |
| `batch-ag-0002` (v1) | `ag-g-p6-000002` | `ag-i-p6-000002-2` | Part 6 | D4 | **A** | `document_block:ag-blk-p6-000002-1` | reading_stimulus_isolated_subagent (blind=true) (`A == A`) | `not_applicable (純閱讀題)` | `pending (human_reviewed=0)` |
| `batch-ag-0002` (v1) | `ag-g-p6-000002` | `ag-i-p6-000002-3` | Part 6 | D4 | **A** | `document_block:ag-blk-p6-000002-1` | reading_stimulus_isolated_subagent (blind=true) (`A == A`) | `not_applicable (純閱讀題)` | `pending (human_reviewed=0)` |
| `batch-ag-0002` (v1) | `ag-g-p6-000002` | `ag-i-p6-000002-4` | Part 6 | D4 | **C** | `document_block:ag-blk-p6-000002-1` | reading_stimulus_isolated_subagent (blind=true) (`C == C`) | `not_applicable (純閱讀題)` | `pending (human_reviewed=0)` |
| `batch-ag-0006` (v2) | `ag-g-p3-000001` | `ag-i-p3-000001-1` | Part 3 | D2 | **B** | `audio_segment:ag-g-p3-000001-seg-3` | transcript_text_isolated_subagent (blind=true) (`B == B`) | `not_run (未僅憑音檔盲解)` | `pending (human_reviewed=0)` |
| `batch-ag-0006` (v2) | `ag-g-p3-000001` | `ag-i-p3-000001-2` | Part 3 | D2 | **C** | `audio_segment:ag-g-p3-000001-seg-5` | transcript_text_isolated_subagent (blind=true) (`C == C`) | `not_run (未僅憑音檔盲解)` | `pending (human_reviewed=0)` |
| `batch-ag-0006` (v2) | `ag-g-p3-000001` | `ag-i-p3-000001-3` | Part 3 | D2 | **B** | `audio_segment:ag-g-p3-000001-seg-6` | transcript_text_isolated_subagent (blind=true) (`B == B`) | `not_run (未僅憑音檔盲解)` | `pending (human_reviewed=0)` |
| `batch-ag-0007` (v2) | `ag-g-p3-000002` | `ag-i-p3-000002-1` | Part 3 | D3 | **B** | `audio_segment:ag-g-p3-000002-seg-1` | transcript_text_isolated_subagent (blind=true) (`B == B`) | `not_run (未僅憑音檔盲解)` | `pending (human_reviewed=0)` |
| `batch-ag-0007` (v2) | `ag-g-p3-000002` | `ag-i-p3-000002-2` | Part 3 | D3 | **C** | `audio_segment:ag-g-p3-000002-seg-2` | transcript_text_isolated_subagent (blind=true) (`C == C`) | `not_run (未僅憑音檔盲解)` | `pending (human_reviewed=0)` |
| `batch-ag-0007` (v2) | `ag-g-p3-000002` | `ag-i-p3-000002-3` | Part 3 | D3 | **B** | `audio_segment:ag-g-p3-000002-seg-4, audio_segment:ag-g-p3-000002-seg-5` | transcript_text_isolated_subagent (blind=true) (`B == B`) | `not_run (未僅憑音檔盲解)` | `pending (human_reviewed=0)` |
| `batch-ag-0007` (v2) | `ag-g-p3-000003` | `ag-i-p3-000003-1` | Part 3 | D4 | **B** | `audio_segment:ag-g-p3-000003-seg-1` | transcript_text_isolated_subagent (blind=true) (`B == B`) | `not_run (未僅憑音檔盲解)` | `pending (human_reviewed=0)` |
| `batch-ag-0007` (v2) | `ag-g-p3-000003` | `ag-i-p3-000003-2` | Part 3 | D4 | **A** | `audio_segment:ag-g-p3-000003-seg-2, audio_segment:ag-g-p3-000003-seg-3` | transcript_text_isolated_subagent (blind=true) (`A == A`) | `not_run (未僅憑音檔盲解)` | `pending (human_reviewed=0)` |
| `batch-ag-0007` (v2) | `ag-g-p3-000003` | `ag-i-p3-000003-3` | Part 3 | D4 | **B** | `audio_segment:ag-g-p3-000003-seg-6` | transcript_text_isolated_subagent (blind=true) (`B == B`) | `not_run (未僅憑音檔盲解)` | `pending (human_reviewed=0)` |
| `batch-ag-0007` (v2) | `ag-g-p3-000004` | `ag-i-p3-000004-1` | Part 3 | D3 | **B** | `audio_segment:ag-g-p3-000004-seg-1, audio_segment:ag-g-p3-000004-seg-2` | transcript_text_isolated_subagent (blind=true) (`B == B`) | `not_run (未僅憑音檔盲解)` | `pending (human_reviewed=0)` |
| `batch-ag-0007` (v2) | `ag-g-p3-000004` | `ag-i-p3-000004-2` | Part 3 | D3 | **C** | `audio_segment:ag-g-p3-000004-seg-2` | transcript_text_isolated_subagent (blind=true) (`C == C`) | `not_run (未僅憑音檔盲解)` | `pending (human_reviewed=0)` |
| `batch-ag-0007` (v2) | `ag-g-p3-000004` | `ag-i-p3-000004-3` | Part 3 | D3 | **B** | `audio_segment:ag-g-p3-000004-seg-3, audio_segment:ag-g-p3-000004-seg-5` | transcript_text_isolated_subagent (blind=true) (`B == B`) | `not_run (未僅憑音檔盲解)` | `pending (human_reviewed=0)` |
| `batch-ag-0007` (v2) | `ag-g-p3-000005` | `ag-i-p3-000005-1` | Part 3 | D4 | **B** | `audio_segment:ag-g-p3-000005-seg-1` | transcript_text_isolated_subagent (blind=true) (`B == B`) | `not_run (未僅憑音檔盲解)` | `pending (human_reviewed=0)` |
| `batch-ag-0007` (v2) | `ag-g-p3-000005` | `ag-i-p3-000005-2` | Part 3 | D4 | **C** | `audio_segment:ag-g-p3-000005-seg-2, document_block:ag-blk-p3-000005-1` | transcript_text_isolated_subagent (blind=true) (`C == C`) | `not_run (未僅憑音檔盲解)` | `pending (human_reviewed=0)` |
| `batch-ag-0007` (v2) | `ag-g-p3-000005` | `ag-i-p3-000005-3` | Part 3 | D4 | **B** | `audio_segment:ag-g-p3-000005-seg-4` | transcript_text_isolated_subagent (blind=true) (`B == B`) | `not_run (未僅憑音檔盲解)` | `pending (human_reviewed=0)` |
| `batch-ag-0007` (v2) | `ag-g-p3-000006` | `ag-i-p3-000006-1` | Part 3 | D5 | **B** | `audio_segment:ag-g-p3-000006-seg-1` | transcript_text_isolated_subagent (blind=true) (`B == B`) | `not_run (未僅憑音檔盲解)` | `pending (human_reviewed=0)` |
| `batch-ag-0007` (v2) | `ag-g-p3-000006` | `ag-i-p3-000006-2` | Part 3 | D5 | **B** | `audio_segment:ag-g-p3-000006-seg-3` | transcript_text_isolated_subagent (blind=true) (`B == B`) | `not_run (未僅憑音檔盲解)` | `pending (human_reviewed=0)` |
| `batch-ag-0007` (v2) | `ag-g-p3-000006` | `ag-i-p3-000006-3` | Part 3 | D5 | **D** | `audio_segment:ag-g-p3-000006-seg-4, document_block:ag-blk-p3-000006-1` | transcript_text_isolated_subagent (blind=true) (`D == D`) | `not_run (未僅憑音檔盲解)` | `pending (human_reviewed=0)` |
| `batch-ag-0006` (v2) | `ag-g-p4-000001` | `ag-i-p4-000001-1` | Part 4 | D2 | **C** | `audio_segment:ag-g-p4-000001-seg-1` | transcript_text_isolated_subagent (blind=true) (`C == C`) | `not_run (未僅憑音檔盲解)` | `pending (human_reviewed=0)` |
| `batch-ag-0006` (v2) | `ag-g-p4-000001` | `ag-i-p4-000001-2` | Part 4 | D2 | **C** | `audio_segment:ag-g-p4-000001-seg-2` | transcript_text_isolated_subagent (blind=true) (`C == C`) | `not_run (未僅憑音檔盲解)` | `pending (human_reviewed=0)` |
| `batch-ag-0006` (v2) | `ag-g-p4-000001` | `ag-i-p4-000001-3` | Part 4 | D2 | **B** | `audio_segment:ag-g-p4-000001-seg-3` | transcript_text_isolated_subagent (blind=true) (`B == B`) | `not_run (未僅憑音檔盲解)` | `pending (human_reviewed=0)` |
| `batch-ag-0007` (v2) | `ag-g-p4-000002` | `ag-i-p4-000002-1` | Part 4 | D3 | **B** | `audio_segment:ag-g-p4-000002-seg-1` | transcript_text_isolated_subagent (blind=true) (`B == B`) | `not_run (未僅憑音檔盲解)` | `pending (human_reviewed=0)` |
| `batch-ag-0007` (v2) | `ag-g-p4-000002` | `ag-i-p4-000002-2` | Part 4 | D3 | **C** | `audio_segment:ag-g-p4-000002-seg-2` | transcript_text_isolated_subagent (blind=true) (`C == C`) | `not_run (未僅憑音檔盲解)` | `pending (human_reviewed=0)` |
| `batch-ag-0007` (v2) | `ag-g-p4-000002` | `ag-i-p4-000002-3` | Part 4 | D3 | **B** | `audio_segment:ag-g-p4-000002-seg-3` | transcript_text_isolated_subagent (blind=true) (`B == B`) | `not_run (未僅憑音檔盲解)` | `pending (human_reviewed=0)` |
| `batch-ag-0007` (v2) | `ag-g-p4-000003` | `ag-i-p4-000003-1` | Part 4 | D4 | **B** | `audio_segment:ag-g-p4-000003-seg-2` | transcript_text_isolated_subagent (blind=true) (`B == B`) | `not_run (未僅憑音檔盲解)` | `pending (human_reviewed=0)` |
| `batch-ag-0007` (v2) | `ag-g-p4-000003` | `ag-i-p4-000003-2` | Part 4 | D4 | **C** | `audio_segment:ag-g-p4-000003-seg-2, audio_segment:ag-g-p4-000003-seg-3` | transcript_text_isolated_subagent (blind=true) (`C == C`) | `not_run (未僅憑音檔盲解)` | `pending (human_reviewed=0)` |
| `batch-ag-0007` (v2) | `ag-g-p4-000003` | `ag-i-p4-000003-3` | Part 4 | D4 | **C** | `audio_segment:ag-g-p4-000003-seg-3` | transcript_text_isolated_subagent (blind=true) (`C == C`) | `not_run (未僅憑音檔盲解)` | `pending (human_reviewed=0)` |
| `batch-ag-0007` (v2) | `ag-g-p4-000004` | `ag-i-p4-000004-1` | Part 4 | D3 | **C** | `audio_segment:ag-g-p4-000004-seg-1` | transcript_text_isolated_subagent (blind=true) (`C == C`) | `not_run (未僅憑音檔盲解)` | `pending (human_reviewed=0)` |
| `batch-ag-0007` (v2) | `ag-g-p4-000004` | `ag-i-p4-000004-2` | Part 4 | D3 | **B** | `audio_segment:ag-g-p4-000004-seg-3` | transcript_text_isolated_subagent (blind=true) (`B == B`) | `not_run (未僅憑音檔盲解)` | `pending (human_reviewed=0)` |
| `batch-ag-0007` (v2) | `ag-g-p4-000004` | `ag-i-p4-000004-3` | Part 4 | D3 | **C** | `audio_segment:ag-g-p4-000004-seg-3` | transcript_text_isolated_subagent (blind=true) (`C == C`) | `not_run (未僅憑音檔盲解)` | `pending (human_reviewed=0)` |
| `batch-ag-0007` (v2) | `ag-g-p4-000005` | `ag-i-p4-000005-1` | Part 4 | D5 | **B** | `audio_segment:ag-g-p4-000005-seg-2, document_block:ag-blk-p4-000005-1` | transcript_text_isolated_subagent (blind=true) (`B == B`) | `not_run (未僅憑音檔盲解)` | `pending (human_reviewed=0)` |
| `batch-ag-0007` (v2) | `ag-g-p4-000005` | `ag-i-p4-000005-2` | Part 4 | D5 | **C** | `audio_segment:ag-g-p4-000005-seg-3` | transcript_text_isolated_subagent (blind=true) (`C == C`) | `not_run (未僅憑音檔盲解)` | `pending (human_reviewed=0)` |
| `batch-ag-0007` (v2) | `ag-g-p4-000005` | `ag-i-p4-000005-3` | Part 4 | D5 | **D** | `audio_segment:ag-g-p4-000005-seg-3, document_block:ag-blk-p4-000005-1` | transcript_text_isolated_subagent (blind=true) (`D == D`) | `not_run (未僅憑音檔盲解)` | `pending (human_reviewed=0)` |
| `batch-ag-0005` (v1) | `ag-g-p7-000001` | `ag-i-p7-000001-1` | Part 7 | D1 | **B** | `document_block:ag-blk-p7-000001-1` | reading_stimulus_isolated_subagent (blind=true) (`B == B`) | `not_applicable (純閱讀題)` | `pending (human_reviewed=0)` |
| `batch-ag-0005` (v1) | `ag-g-p7-000001` | `ag-i-p7-000001-2` | Part 7 | D1 | **C** | `document_block:ag-blk-p7-000001-1` | reading_stimulus_isolated_subagent (blind=true) (`C == C`) | `not_applicable (純閱讀題)` | `pending (human_reviewed=0)` |
| `batch-ag-0005` (v1) | `ag-g-p7-000001` | `ag-i-p7-000001-3` | Part 7 | D1 | **B** | `document_block:ag-blk-p7-000001-1` | reading_stimulus_isolated_subagent (blind=true) (`B == B`) | `not_applicable (純閱讀題)` | `pending (human_reviewed=0)` |
| `batch-ag-0005` (v1) | `ag-g-p7-000002` | `ag-i-p7-000002-1` | Part 7 | D2 | **A** | `document_block:ag-blk-p7-000002-1` | reading_stimulus_isolated_subagent (blind=true) (`A == A`) | `not_applicable (純閱讀題)` | `pending (human_reviewed=0)` |
| `batch-ag-0005` (v1) | `ag-g-p7-000002` | `ag-i-p7-000002-2` | Part 7 | D2 | **B** | `document_block:ag-blk-p7-000002-1` | reading_stimulus_isolated_subagent (blind=true) (`B == B`) | `not_applicable (純閱讀題)` | `pending (human_reviewed=0)` |
| `batch-ag-0005` (v1) | `ag-g-p7-000002` | `ag-i-p7-000002-3` | Part 7 | D2 | **C** | `document_block:ag-blk-p7-000002-1` | reading_stimulus_isolated_subagent (blind=true) (`C == C`) | `not_applicable (純閱讀題)` | `pending (human_reviewed=0)` |
| `batch-ag-0005` (v1) | `ag-g-p7-000003` | `ag-i-p7-000003-1` | Part 7 | D3 | **B** | `document_block:ag-blk-p7-000003-1` | reading_stimulus_isolated_subagent (blind=true) (`B == B`) | `not_applicable (純閱讀題)` | `pending (human_reviewed=0)` |
| `batch-ag-0005` (v1) | `ag-g-p7-000003` | `ag-i-p7-000003-2` | Part 7 | D3 | **A** | `document_block:ag-blk-p7-000003-1` | reading_stimulus_isolated_subagent (blind=true) (`A == A`) | `not_applicable (純閱讀題)` | `pending (human_reviewed=0)` |
| `batch-ag-0005` (v1) | `ag-g-p7-000003` | `ag-i-p7-000003-3` | Part 7 | D3 | **B** | `document_block:ag-blk-p7-000003-1` | reading_stimulus_isolated_subagent (blind=true) (`B == B`) | `not_applicable (純閱讀題)` | `pending (human_reviewed=0)` |
| `batch-ag-0005` (v1) | `ag-g-p7-000004` | `ag-i-p7-000004-1` | Part 7 | D4 | **B** | `document_block:ag-blk-p7-000004-1` | reading_stimulus_isolated_subagent (blind=true) (`B == B`) | `not_applicable (純閱讀題)` | `pending (human_reviewed=0)` |
| `batch-ag-0005` (v1) | `ag-g-p7-000004` | `ag-i-p7-000004-2` | Part 7 | D4 | **B** | `document_block:ag-blk-p7-000004-1` | reading_stimulus_isolated_subagent (blind=true) (`B == B`) | `not_applicable (純閱讀題)` | `pending (human_reviewed=0)` |
| `batch-ag-0005` (v1) | `ag-g-p7-000004` | `ag-i-p7-000004-3` | Part 7 | D4 | **B** | `document_block:ag-blk-p7-000004-1` | reading_stimulus_isolated_subagent (blind=true) (`B == B`) | `not_applicable (純閱讀題)` | `pending (human_reviewed=0)` |
| `batch-ag-0005` (v1) | `ag-g-p7-000004` | `ag-i-p7-000004-4` | Part 7 | D4 | **C** | `document_block:ag-blk-p7-000004-1` | reading_stimulus_isolated_subagent (blind=true) (`C == C`) | `not_applicable (純閱讀題)` | `pending (human_reviewed=0)` |
| `batch-ag-0005` (v1) | `ag-g-p7-000005` | `ag-i-p7-000005-1` | Part 7 | D4 | **C** | `document_block:ag-blk-p7-000005-1` | reading_stimulus_isolated_subagent (blind=true) (`C == C`) | `not_applicable (純閱讀題)` | `pending (human_reviewed=0)` |
| `batch-ag-0005` (v1) | `ag-g-p7-000005` | `ag-i-p7-000005-2` | Part 7 | D4 | **C** | `document_block:ag-blk-p7-000005-2, document_block:ag-blk-p7-000005-1` | reading_stimulus_isolated_subagent (blind=true) (`C == C`) | `not_applicable (純閱讀題)` | `pending (human_reviewed=0)` |
| `batch-ag-0005` (v1) | `ag-g-p7-000005` | `ag-i-p7-000005-3` | Part 7 | D4 | **B** | `document_block:ag-blk-p7-000005-3` | reading_stimulus_isolated_subagent (blind=true) (`B == B`) | `not_applicable (純閱讀題)` | `pending (human_reviewed=0)` |
| `batch-ag-0005` (v1) | `ag-g-p7-000005` | `ag-i-p7-000005-4` | Part 7 | D4 | **D** | `document_block:ag-blk-p7-000005-1, document_block:ag-blk-p7-000005-3` | reading_stimulus_isolated_subagent (blind=true) (`D == D`) | `not_applicable (純閱讀題)` | `pending (human_reviewed=0)` |
| `batch-ag-0005` (v1) | `ag-g-p7-000005` | `ag-i-p7-000005-5` | Part 7 | D4 | **A** | `document_block:ag-blk-p7-000005-1, document_block:ag-blk-p7-000005-3` | reading_stimulus_isolated_subagent (blind=true) (`A == A`) | `not_applicable (純閱讀題)` | `pending (human_reviewed=0)` |
| `batch-ag-0005` (v1) | `ag-g-p7-000006` | `ag-i-p7-000006-1` | Part 7 | D4 | **C** | `document_block:ag-blk-p7-000006-1` | reading_stimulus_isolated_subagent (blind=true) (`C == C`) | `not_applicable (純閱讀題)` | `pending (human_reviewed=0)` |
| `batch-ag-0005` (v1) | `ag-g-p7-000006` | `ag-i-p7-000006-2` | Part 7 | D4 | **B** | `document_block:ag-blk-p7-000006-1, document_block:ag-blk-p7-000006-3` | reading_stimulus_isolated_subagent (blind=true) (`B == B`) | `not_applicable (純閱讀題)` | `pending (human_reviewed=0)` |
| `batch-ag-0005` (v1) | `ag-g-p7-000006` | `ag-i-p7-000006-3` | Part 7 | D4 | **A** | `document_block:ag-blk-p7-000006-1, document_block:ag-blk-p7-000006-2` | reading_stimulus_isolated_subagent (blind=true) (`A == A`) | `not_applicable (純閱讀題)` | `pending (human_reviewed=0)` |
| `batch-ag-0005` (v1) | `ag-g-p7-000006` | `ag-i-p7-000006-4` | Part 7 | D4 | **C** | `document_block:ag-blk-p7-000006-1, document_block:ag-blk-p7-000006-3` | reading_stimulus_isolated_subagent (blind=true) (`C == C`) | `not_applicable (純閱讀題)` | `pending (human_reviewed=0)` |
| `batch-ag-0005` (v1) | `ag-g-p7-000006` | `ag-i-p7-000006-5` | Part 7 | D4 | **A** | `document_block:ag-blk-p7-000006-1` | reading_stimulus_isolated_subagent (blind=true) (`A == A`) | `not_applicable (純閱讀題)` | `pending (human_reviewed=0)` |
| `batch-ag-0005` (v1) | `ag-g-p7-000007` | `ag-i-p7-000007-1` | Part 7 | D5 | **B** | `document_block:ag-blk-p7-000007-3, document_block:ag-blk-p7-000007-4, document_block:ag-blk-p7-000007-1` | reading_stimulus_isolated_subagent (blind=true) (`B == B`) | `not_applicable (純閱讀題)` | `pending (human_reviewed=0)` |
| `batch-ag-0005` (v1) | `ag-g-p7-000007` | `ag-i-p7-000007-2` | Part 7 | D5 | **A** | `document_block:ag-blk-p7-000007-2, document_block:ag-blk-p7-000007-3` | reading_stimulus_isolated_subagent (blind=true) (`A == A`) | `not_applicable (純閱讀題)` | `pending (human_reviewed=0)` |
| `batch-ag-0005` (v1) | `ag-g-p7-000007` | `ag-i-p7-000007-3` | Part 7 | D5 | **B** | `document_block:ag-blk-p7-000007-2, document_block:ag-blk-p7-000007-3` | reading_stimulus_isolated_subagent (blind=true) (`B == B`) | `not_applicable (純閱讀題)` | `pending (human_reviewed=0)` |
| `batch-ag-0005` (v1) | `ag-g-p7-000007` | `ag-i-p7-000007-4` | Part 7 | D5 | **A** | `document_block:ag-blk-p7-000007-4` | reading_stimulus_isolated_subagent (blind=true) (`A == A`) | `not_applicable (純閱讀題)` | `pending (human_reviewed=0)` |
| `batch-ag-0005` (v1) | `ag-g-p7-000007` | `ag-i-p7-000007-5` | Part 7 | D5 | **A** | `document_block:ag-blk-p7-000007-4` | reading_stimulus_isolated_subagent (blind=true) (`A == A`) | `not_applicable (純閱讀題)` | `pending (human_reviewed=0)` |
