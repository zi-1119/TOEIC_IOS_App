# 人工審閱與後續驗收待辦佇列（REVIEW_QUEUE.md）

更新時間（UTC）：`2026-10-28T08:46:33Z`

- **AI 審查與結構驗證合格小題數（`accepted_candidate_count`, `content_status=ai_checked`）**：**177** 題（106 個獨立題組：`training` 129 題、`diagnostic` 24 題、`battle` 24 題、`mock` 0 題）
- **真人命題專家審閱完成小題數（`fully_reviewed_count`, `content_status=human_reviewed`）**：**0** 題
- **獨立上下文盲解通過小題數（`blind=true`）**：**177 / 177** 題
  - 純閱讀盲解（Part 5–7）：**108** 題
  - 聽力逐字稿盲解（Part 2–4）：**65** 題
  - Part 1 實體照片視覺盲解（Part 1）：**4** 題
  - 純聽音盲解（不看逐字稿）：**0** 題（`not_run`）
- **優先真人審閱與試聽樣本包**：已建立於 [review/human_review_pack_phase1/](file:///Users/ziii/Desktop/TOEIC_IOS_App/review/human_review_pack_phase1/README-HUMAN-REVIEWER.md)（涵蓋 27 組優先抽樣／53 題 + 全量 100 題檢核表 + JSONL 回填模板）

## 待人工審閱題組清單（共 106 組 177 題）

| 最新所在批次 (版本) | Pool | Group ID | 題型 (Layout) | 小題數 | 難度 | 目前狀態 | 待辦人工審核項目 |
|---|---|---|---|---:|---|---|---|
| `batch-ag-0006` (v2) | `training` | `ag-g-p2-000001` | Part 2 (question_response) | 1 | D1 | `ai_checked` | 已完成獨立盲解；待真人命題複核與音圖最終審閱 |
| `batch-ag-0007` (v2) | `training` | `ag-g-p2-000002` | Part 2 (question_response) | 1 | D2 | `ai_checked` | 已完成獨立盲解；待真人命題複核與音圖最終審閱 |
| `batch-ag-0007` (v2) | `training` | `ag-g-p2-000003` | Part 2 (question_response) | 1 | D3 | `ai_checked` | 已完成獨立盲解與音檔合成；待真人命題複核、試聽及 ca 口音替換驗收 |
| `batch-ag-0007` (v2) | `training` | `ag-g-p2-000004` | Part 2 (question_response) | 1 | D2 | `ai_checked` | 已完成獨立盲解；待真人命題複核與音圖最終審閱 |
| `batch-ag-0007` (v2) | `training` | `ag-g-p2-000005` | Part 2 (question_response) | 1 | D3 | `ai_checked` | 已完成獨立盲解；待真人命題複核與音圖最終審閱 |
| `batch-ag-0007` (v2) | `training` | `ag-g-p2-000006` | Part 2 (question_response) | 1 | D2 | `ai_checked` | 已完成獨立盲解與音檔合成；待真人命題複核、試聽及 ca 口音替換驗收 |
| `batch-ag-0007` (v2) | `training` | `ag-g-p2-000007` | Part 2 (question_response) | 1 | D4 | `ai_checked` | 已完成獨立盲解；待真人命題複核與音圖最終審閱 |
| `batch-ag-0007` (v2) | `training` | `ag-g-p2-000008` | Part 2 (question_response) | 1 | D5 | `ai_checked` | 已完成獨立盲解與音檔合成；待真人命題複核、試聽及 ca 口音替換驗收 |
| `batch-ag-0001` (v1) | `training` | `ag-g-p5-000001` | Part 5 (sentence) | 1 | D1 | `ai_checked` | 已完成獨立盲解；待真人命題複核與音圖最終審閱 |
| `batch-ag-0001` (v1) | `training` | `ag-g-p5-000002` | Part 5 (sentence) | 1 | D2 | `ai_checked` | 已完成獨立盲解；待真人命題複核與音圖最終審閱 |
| `batch-ag-0001` (v1) | `training` | `ag-g-p5-000003` | Part 5 (sentence) | 1 | D2 | `ai_checked` | 已完成獨立盲解；待真人命題複核與音圖最終審閱 |
| `batch-ag-0001` (v1) | `training` | `ag-g-p5-000004` | Part 5 (sentence) | 1 | D3 | `ai_checked` | 已完成獨立盲解；待真人命題複核與音圖最終審閱 |
| `batch-ag-0001` (v1) | `training` | `ag-g-p5-000005` | Part 5 (sentence) | 1 | D2 | `ai_checked` | 已完成獨立盲解；待真人命題複核與音圖最終審閱 |
| `batch-ag-0001` (v1) | `training` | `ag-g-p5-000006` | Part 5 (sentence) | 1 | D1 | `ai_checked` | 已完成獨立盲解；待真人命題複核與音圖最終審閱 |
| `batch-ag-0001` (v1) | `training` | `ag-g-p5-000007` | Part 5 (sentence) | 1 | D4 | `ai_checked` | 已完成獨立盲解；待真人命題複核與音圖最終審閱 |
| `batch-ag-0001` (v1) | `training` | `ag-g-p5-000008` | Part 5 (sentence) | 1 | D3 | `ai_checked` | 已完成獨立盲解；待真人命題複核與音圖最終審閱 |
| `batch-ag-0001` (v1) | `training` | `ag-g-p5-000009` | Part 5 (sentence) | 1 | D4 | `ai_checked` | 已完成獨立盲解；待真人命題複核與音圖最終審閱 |
| `batch-ag-0001` (v1) | `training` | `ag-g-p5-000010` | Part 5 (sentence) | 1 | D3 | `ai_checked` | 已完成獨立盲解；待真人命題複核與音圖最終審閱 |
| `batch-ag-0001` (v1) | `training` | `ag-g-p5-000011` | Part 5 (sentence) | 1 | D5 | `ai_checked` | 已完成獨立盲解；待真人命題複核與音圖最終審閱 |
| `batch-ag-0001` (v1) | `training` | `ag-g-p5-000012` | Part 5 (sentence) | 1 | D5 | `ai_checked` | 已完成獨立盲解；待真人命題複核與音圖最終審閱 |
| `batch-ag-0006` (v2) | `training` | `ag-g-p1-000001` | Part 1 (photo) | 1 | D1 | `ai_checked` | 已完成獨立盲解；待真人命題複核與音圖最終審閱 |
| `batch-ag-0007` (v2) | `training` | `ag-g-p1-000002` | Part 1 (photo) | 1 | D3 | `ai_checked` | 已完成獨立盲解；待真人命題複核與音圖最終審閱 |
| `batch-ag-0007` (v2) | `training` | `ag-g-p1-000003` | Part 1 (photo) | 1 | D4 | `ai_checked` | 已完成獨立盲解；待真人命題複核與音圖最終審閱 |
| `batch-ag-0007` (v2) | `training` | `ag-g-p2-000009` | Part 2 (question_response) | 1 | D1 | `ai_checked` | 已完成獨立盲解；待真人命題複核與音圖最終審閱 |
| `batch-ag-0007` (v2) | `training` | `ag-g-p2-000010` | Part 2 (question_response) | 1 | D2 | `ai_checked` | 已完成獨立盲解；待真人命題複核與音圖最終審閱 |
| `batch-ag-0007` (v2) | `training` | `ag-g-p2-000011` | Part 2 (question_response) | 1 | D3 | `ai_checked` | 已完成獨立盲解與音檔合成；待真人命題複核、試聽及 ca 口音替換驗收 |
| `batch-ag-0007` (v2) | `training` | `ag-g-p2-000012` | Part 2 (question_response) | 1 | D4 | `ai_checked` | 已完成獨立盲解與音檔合成；待真人命題複核、試聽及 ca 口音替換驗收 |
| `batch-ag-0007` (v2) | `training` | `ag-g-p2-000013` | Part 2 (question_response) | 1 | D5 | `ai_checked` | 已完成獨立盲解；待真人命題複核與音圖最終審閱 |
| `batch-ag-0002` (v1) | `training` | `ag-g-p5-000013` | Part 5 (sentence) | 1 | D2 | `ai_checked` | 已完成獨立盲解；待真人命題複核與音圖最終審閱 |
| `batch-ag-0002` (v1) | `training` | `ag-g-p5-000014` | Part 5 (sentence) | 1 | D4 | `ai_checked` | 已完成獨立盲解；待真人命題複核與音圖最終審閱 |
| `batch-ag-0002` (v1) | `training` | `ag-g-p5-000015` | Part 5 (sentence) | 1 | D5 | `ai_checked` | 已完成獨立盲解；待真人命題複核與音圖最終審閱 |
| `batch-ag-0002` (v1) | `training` | `ag-g-p6-000001` | Part 6 (text_completion) | 4 | D3 | `ai_checked` | 已完成獨立盲解；待真人命題複核與音圖最終審閱 |
| `batch-ag-0002` (v1) | `training` | `ag-g-p6-000002` | Part 6 (text_completion) | 4 | D4 | `ai_checked` | 已完成獨立盲解；待真人命題複核與音圖最終審閱 |
| `batch-ag-0006` (v2) | `training` | `ag-g-p3-000001` | Part 3 (conversation) | 3 | D2 | `ai_checked` | 已完成獨立盲解；待真人命題複核與音圖最終審閱 |
| `batch-ag-0007` (v2) | `training` | `ag-g-p3-000002` | Part 3 (conversation) | 3 | D3 | `ai_checked` | 已完成獨立盲解與音檔合成；待真人命題複核、試聽及 ca 口音替換驗收 |
| `batch-ag-0007` (v2) | `training` | `ag-g-p3-000003` | Part 3 (conversation) | 3 | D4 | `ai_checked` | 已完成獨立盲解；待真人命題複核與音圖最終審閱 |
| `batch-ag-0007` (v2) | `training` | `ag-g-p3-000004` | Part 3 (conversation) | 3 | D3 | `ai_checked` | 已完成獨立盲解；待真人命題複核與音圖最終審閱 |
| `batch-ag-0007` (v2) | `training` | `ag-g-p3-000005` | Part 3 (conversation) | 3 | D4 | `ai_checked` | 已完成獨立盲解與音檔合成；待真人命題複核、試聽及 ca 口音替換驗收 |
| `batch-ag-0007` (v2) | `training` | `ag-g-p3-000006` | Part 3 (conversation) | 3 | D5 | `ai_checked` | 已完成獨立盲解；待真人命題複核與音圖最終審閱 |
| `batch-ag-0006` (v2) | `training` | `ag-g-p4-000001` | Part 4 (talk) | 3 | D2 | `ai_checked` | 已完成獨立盲解；待真人命題複核與音圖最終審閱 |
| `batch-ag-0007` (v2) | `training` | `ag-g-p4-000002` | Part 4 (talk) | 3 | D3 | `ai_checked` | 已完成獨立盲解；待真人命題複核與音圖最終審閱 |
| `batch-ag-0007` (v2) | `training` | `ag-g-p4-000003` | Part 4 (talk) | 3 | D4 | `ai_checked` | 已完成獨立盲解；待真人命題複核與音圖最終審閱 |
| `batch-ag-0007` (v2) | `training` | `ag-g-p4-000004` | Part 4 (talk) | 3 | D3 | `ai_checked` | 已完成獨立盲解與音檔合成；待真人命題複核、試聽及 ca 口音替換驗收 |
| `batch-ag-0007` (v2) | `training` | `ag-g-p4-000005` | Part 4 (talk) | 3 | D5 | `ai_checked` | 已完成獨立盲解；待真人命題複核與音圖最終審閱 |
| `batch-ag-0005` (v1) | `training` | `ag-g-p7-000001` | Part 7 (single_passage) | 3 | D1 | `ai_checked` | 已完成獨立盲解；待真人命題複核與音圖最終審閱 |
| `batch-ag-0005` (v1) | `training` | `ag-g-p7-000002` | Part 7 (single_passage) | 3 | D2 | `ai_checked` | 已完成獨立盲解；待真人命題複核與音圖最終審閱 |
| `batch-ag-0005` (v1) | `training` | `ag-g-p7-000003` | Part 7 (single_passage) | 3 | D3 | `ai_checked` | 已完成獨立盲解；待真人命題複核與音圖最終審閱 |
| `batch-ag-0005` (v1) | `training` | `ag-g-p7-000004` | Part 7 (single_passage) | 4 | D4 | `ai_checked` | 已完成獨立盲解；待真人命題複核與音圖最終審閱 |
| `batch-ag-0005` (v1) | `training` | `ag-g-p7-000005` | Part 7 (double_passage) | 5 | D4 | `ai_checked` | 已完成獨立盲解；待真人命題複核與音圖最終審閱 |
| `batch-ag-0005` (v1) | `training` | `ag-g-p7-000006` | Part 7 (double_passage) | 5 | D4 | `ai_checked` | 已完成獨立盲解；待真人命題複核與音圖最終審閱 |
| `batch-ag-0005` (v1) | `training` | `ag-g-p7-000007` | Part 7 (triple_passage) | 5 | D5 | `ai_checked` | 已完成獨立盲解；待真人命題複核與音圖最終審閱 |
| `batch-ag-0008` (v1) | `training` | `ag-g-p5-000016` | Part 5 (sentence) | 1 | D1 | `ai_checked` | 已完成獨立盲解；待真人命題複核與音圖最終審閱 |
| `batch-ag-0008` (v1) | `training` | `ag-g-p5-000017` | Part 5 (sentence) | 1 | D2 | `ai_checked` | 已完成獨立盲解；待真人命題複核與音圖最終審閱 |
| `batch-ag-0008` (v1) | `training` | `ag-g-p5-000018` | Part 5 (sentence) | 1 | D2 | `ai_checked` | 已完成獨立盲解；待真人命題複核與音圖最終審閱 |
| `batch-ag-0008` (v1) | `training` | `ag-g-p5-000019` | Part 5 (sentence) | 1 | D2 | `ai_checked` | 已完成獨立盲解；待真人命題複核與音圖最終審閱 |
| `batch-ag-0008` (v1) | `training` | `ag-g-p5-000020` | Part 5 (sentence) | 1 | D3 | `ai_checked` | 已完成獨立盲解；待真人命題複核與音圖最終審閱 |
| `batch-ag-0008` (v1) | `training` | `ag-g-p5-000021` | Part 5 (sentence) | 1 | D3 | `ai_checked` | 已完成獨立盲解；待真人命題複核與音圖最終審閱 |
| `batch-ag-0008` (v1) | `training` | `ag-g-p5-000022` | Part 5 (sentence) | 1 | D3 | `ai_checked` | 已完成獨立盲解；待真人命題複核與音圖最終審閱 |
| `batch-ag-0008` (v1) | `training` | `ag-g-p5-000023` | Part 5 (sentence) | 1 | D3 | `ai_checked` | 已完成獨立盲解；待真人命題複核與音圖最終審閱 |
| `batch-ag-0008` (v1) | `training` | `ag-g-p5-000024` | Part 5 (sentence) | 1 | D3 | `ai_checked` | 已完成獨立盲解；待真人命題複核與音圖最終審閱 |
| `batch-ag-0008` (v1) | `training` | `ag-g-p5-000025` | Part 5 (sentence) | 1 | D4 | `ai_checked` | 已完成獨立盲解；待真人命題複核與音圖最終審閱 |
| `batch-ag-0008` (v1) | `training` | `ag-g-p5-000026` | Part 5 (sentence) | 1 | D4 | `ai_checked` | 已完成獨立盲解；待真人命題複核與音圖最終審閱 |
| `batch-ag-0008` (v1) | `training` | `ag-g-p5-000027` | Part 5 (sentence) | 1 | D4 | `ai_checked` | 已完成獨立盲解；待真人命題複核與音圖最終審閱 |
| `batch-ag-0008` (v1) | `training` | `ag-g-p5-000028` | Part 5 (sentence) | 1 | D4 | `ai_checked` | 已完成獨立盲解；待真人命題複核與音圖最終審閱 |
| `batch-ag-0008` (v1) | `training` | `ag-g-p5-000029` | Part 5 (sentence) | 1 | D4 | `ai_checked` | 已完成獨立盲解；待真人命題複核與音圖最終審閱 |
| `batch-ag-0008` (v1) | `training` | `ag-g-p5-000030` | Part 5 (sentence) | 1 | D5 | `ai_checked` | 已完成獨立盲解；待真人命題複核與音圖最終審閱 |
| `batch-ag-0008` (v1) | `training` | `ag-g-p5-000031` | Part 5 (sentence) | 1 | D5 | `ai_checked` | 已完成獨立盲解；待真人命題複核與音圖最終審閱 |
| `batch-ag-0008` (v1) | `training` | `ag-g-p6-000003` | Part 6 (text_completion) | 4 | D3 | `ai_checked` | 已完成獨立盲解；待真人命題複核與音圖最終審閱 |
| `batch-ag-0008` (v1) | `training` | `ag-g-p6-000004` | Part 6 (text_completion) | 4 | D4 | `ai_checked` | 已完成獨立盲解；待真人命題複核與音圖最終審閱 |
| `batch-ag-0008` (v1) | `training` | `ag-g-p7-000008` | Part 7 (single_passage) | 2 | D2 | `ai_checked` | 已完成獨立盲解；待真人命題複核與音圖最終審閱 |
| `batch-ag-0008` (v1) | `training` | `ag-g-p7-000009` | Part 7 (single_passage) | 3 | D4 | `ai_checked` | 已完成獨立盲解；待真人命題複核與音圖最終審閱 |
| `batch-ag-0009` (v1) | `diagnostic` | `ag-g-p1-000301` | Part 1 (photo) | 1 | D2 | `ai_checked` | 已完成獨立盲解；待真人命題複核與音圖最終審閱 |
| `batch-ag-0009` (v1) | `diagnostic` | `ag-g-p2-000301` | Part 2 (question_response) | 1 | D1 | `ai_checked` | 已完成獨立盲解；待真人命題複核與音圖最終審閱 |
| `batch-ag-0009` (v1) | `diagnostic` | `ag-g-p2-000302` | Part 2 (question_response) | 1 | D2 | `ai_checked` | 已完成獨立盲解；待真人命題複核與音圖最終審閱 |
| `batch-ag-0009` (v1) | `diagnostic` | `ag-g-p2-000303` | Part 2 (question_response) | 1 | D3 | `ai_checked` | 已完成獨立盲解；待真人命題複核與音圖最終審閱 |
| `batch-ag-0009` (v1) | `diagnostic` | `ag-g-p2-000304` | Part 2 (question_response) | 1 | D4 | `ai_checked` | 已完成獨立盲解；待真人命題複核與音圖最終審閱 |
| `batch-ag-0009` (v1) | `diagnostic` | `ag-g-p3-000301` | Part 3 (conversation) | 3 | D3 | `ai_checked` | 已完成獨立盲解；待真人命題複核與音圖最終審閱 |
| `batch-ag-0009` (v1) | `diagnostic` | `ag-g-p3-000302` | Part 3 (conversation) | 3 | D4 | `ai_checked` | 已完成獨立盲解；待真人命題複核與音圖最終審閱 |
| `batch-ag-0009` (v1) | `diagnostic` | `ag-g-p4-000301` | Part 4 (talk) | 3 | D4 | `ai_checked` | 已完成獨立盲解；待真人命題複核與音圖最終審閱 |
| `batch-ag-0009` (v1) | `diagnostic` | `ag-g-p5-000301` | Part 5 (sentence) | 1 | D1 | `ai_checked` | 已完成獨立盲解；待真人命題複核與音圖最終審閱 |
| `batch-ag-0009` (v1) | `diagnostic` | `ag-g-p5-000302` | Part 5 (sentence) | 1 | D2 | `ai_checked` | 已完成獨立盲解；待真人命題複核與音圖最終審閱 |
| `batch-ag-0009` (v1) | `diagnostic` | `ag-g-p5-000303` | Part 5 (sentence) | 1 | D3 | `ai_checked` | 已完成獨立盲解；待真人命題複核與音圖最終審閱 |
| `batch-ag-0009` (v1) | `diagnostic` | `ag-g-p5-000304` | Part 5 (sentence) | 1 | D5 | `ai_checked` | 已完成獨立盲解；待真人命題複核與音圖最終審閱 |
| `batch-ag-0009` (v1) | `diagnostic` | `ag-g-p6-000301` | Part 6 (text_completion) | 4 | D3 | `ai_checked` | 已完成獨立盲解；待真人命題複核與音圖最終審閱 |
| `batch-ag-0009` (v1) | `diagnostic` | `ag-g-p7-000301` | Part 7 (single_passage) | 2 | D3 | `ai_checked` | 已完成獨立盲解；待真人命題複核與音圖最終審閱 |
| `batch-ag-0010` (v1) | `battle` | `ag-g-p2-000401` | Part 2 (question_response) | 1 | D1 | `ai_checked` | 已完成獨立盲解；待真人命題複核與音圖最終審閱 |
| `batch-ag-0010` (v1) | `battle` | `ag-g-p2-000402` | Part 2 (question_response) | 1 | D2 | `ai_checked` | 已完成獨立盲解；待真人命題複核與音圖最終審閱 |
| `batch-ag-0010` (v1) | `battle` | `ag-g-p2-000403` | Part 2 (question_response) | 1 | D2 | `ai_checked` | 已完成獨立盲解；待真人命題複核與音圖最終審閱 |
| `batch-ag-0010` (v1) | `battle` | `ag-g-p2-000404` | Part 2 (question_response) | 1 | D3 | `ai_checked` | 已完成獨立盲解；待真人命題複核與音圖最終審閱 |
| `batch-ag-0010` (v1) | `battle` | `ag-g-p2-000405` | Part 2 (question_response) | 1 | D4 | `ai_checked` | 已完成獨立盲解；待真人命題複核與音圖最終審閱 |
| `batch-ag-0010` (v1) | `battle` | `ag-g-p2-000406` | Part 2 (question_response) | 1 | D5 | `ai_checked` | 已完成獨立盲解；待真人命題複核與音圖最終審閱 |
| `batch-ag-0010` (v1) | `battle` | `ag-g-p5-000401` | Part 5 (sentence) | 1 | D1 | `ai_checked` | 已完成獨立盲解；待真人命題複核與音圖最終審閱 |
| `batch-ag-0010` (v1) | `battle` | `ag-g-p5-000402` | Part 5 (sentence) | 1 | D1 | `ai_checked` | 已完成獨立盲解；待真人命題複核與音圖最終審閱 |
| `batch-ag-0010` (v1) | `battle` | `ag-g-p5-000403` | Part 5 (sentence) | 1 | D2 | `ai_checked` | 已完成獨立盲解；待真人命題複核與音圖最終審閱 |
| `batch-ag-0010` (v1) | `battle` | `ag-g-p5-000404` | Part 5 (sentence) | 1 | D2 | `ai_checked` | 已完成獨立盲解；待真人命題複核與音圖最終審閱 |
| `batch-ag-0010` (v1) | `battle` | `ag-g-p5-000405` | Part 5 (sentence) | 1 | D2 | `ai_checked` | 已完成獨立盲解；待真人命題複核與音圖最終審閱 |
| `batch-ag-0010` (v1) | `battle` | `ag-g-p5-000406` | Part 5 (sentence) | 1 | D3 | `ai_checked` | 已完成獨立盲解；待真人命題複核與音圖最終審閱 |
| `batch-ag-0010` (v1) | `battle` | `ag-g-p5-000407` | Part 5 (sentence) | 1 | D3 | `ai_checked` | 已完成獨立盲解；待真人命題複核與音圖最終審閱 |
| `batch-ag-0010` (v1) | `battle` | `ag-g-p5-000408` | Part 5 (sentence) | 1 | D3 | `ai_checked` | 已完成獨立盲解；待真人命題複核與音圖最終審閱 |
| `batch-ag-0010` (v1) | `battle` | `ag-g-p5-000409` | Part 5 (sentence) | 1 | D3 | `ai_checked` | 已完成獨立盲解；待真人命題複核與音圖最終審閱 |
| `batch-ag-0010` (v1) | `battle` | `ag-g-p5-000410` | Part 5 (sentence) | 1 | D4 | `ai_checked` | 已完成獨立盲解；待真人命題複核與音圖最終審閱 |
| `batch-ag-0010` (v1) | `battle` | `ag-g-p5-000411` | Part 5 (sentence) | 1 | D4 | `ai_checked` | 已完成獨立盲解；待真人命題複核與音圖最終審閱 |
| `batch-ag-0010` (v1) | `battle` | `ag-g-p5-000412` | Part 5 (sentence) | 1 | D4 | `ai_checked` | 已完成獨立盲解；待真人命題複核與音圖最終審閱 |
| `batch-ag-0010` (v1) | `battle` | `ag-g-p5-000413` | Part 5 (sentence) | 1 | D5 | `ai_checked` | 已完成獨立盲解；待真人命題複核與音圖最終審閱 |
| `batch-ag-0010` (v1) | `battle` | `ag-g-p5-000414` | Part 5 (sentence) | 1 | D5 | `ai_checked` | 已完成獨立盲解；待真人命題複核與音圖最終審閱 |
| `batch-ag-0010` (v1) | `battle` | `ag-g-p6-000401` | Part 6 (text_completion) | 4 | D3 | `ai_checked` | 已完成獨立盲解；待真人命題複核與音圖最終審閱 |
