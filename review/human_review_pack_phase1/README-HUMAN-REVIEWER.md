# 第一階段 100 題真人審閱與聽審操作包（Human Reviewer & Audio QA Package）

- **建立時間（UTC）**：`2026-10-28T08:29:13Z`
- **目前真人審閱狀態**：`human_reviewed = 0 / 100`（全數候選題目前皆為 `ai_checked`，絕不預填或代填真人通過紀錄）
- **優先抽樣審閱範圍（`priority-sample-review-sheet.md`）**：共 **27 個題組 / 53 道小題**（佔總數 100 題之 53%；**注意：抽審僅代表抽樣覆核，未審畢全量 51 組 100 題前不可改稱全量人工完審**）。
  - 涵蓋 **Part 1–7 全部七大題型**；
  - 涵蓋 **D1–D5 全部五個難度等級**（含全數 16 道 D5 高難度題）；
  - 涵蓋 **全部 3 張 Part 1 照片**（`ag-ast-p1-000001..000003-image.jpg`）；
  - 涵蓋 **四種聽力可播放樣本（`batch-ag-0006`）** 與 **全部 8 組含 `ca` 北美語音替代之聽力題組**。

## 檔案結構說明

1. `priority-sample-review-sheet.md`：優先抽審題組之完整題幹、文章／音訊逐字稿、實體圖片與音檔路徑、選項、預設答案、解析、專項審核疑點與勾選欄。
2. `full-100-items-checklist.md`：全部 51 組 100 題之完整審閱簽核總表。
3. `human-review-response-template.jsonl`：供審閱者填寫後匯回之標準 `reviews.jsonl` 模板（目前 `verdict` 預設為 `"pending"`，`reviewer_name` 為 `"PENDING_HUMAN_REVIEWER"`）。

## 審閱與聽審標準清單（Checklist for Human Reviewers）

1. **唯一最佳答案（Single Best Answer）**：在不看解析的情況下先自行作答，確認正解唯一且無第二個可爭辯之選項。
2. **英語自然度與職場真實性（Naturalness）**：確認題幹、對話、文章符合自然當代商務／日常英語，無中式英文或生硬句構。
3. **Part 1 照片與選項一致性（Photo Verification）**：打開對應 `.jpg` 檔案，確認正解描述之動作或狀態在畫面中清晰可見，且三個干擾項確定與畫面不符。
4. **Part 1–4 音檔實際聽審（Audio Listening QA）**：播放對應 `.m4a` 音檔，確認：
   - 發音清晰、數字／日期／專有名詞朗讀無誤；
   - 多人對話角色音色區分明顯、句間停頓自然；
   - `segment_times` 時間碼與實際發聲起訖吻合。
