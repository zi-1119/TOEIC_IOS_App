# 配額進度、去重與品質總報告（Quota & Quality Summary）

更新時間（UTC）：`2026-10-28T08:46:33Z`

## 1. 核心驗收指標（AI 審核、人工審核、盲解模式、素材就緒、難度校準與未發布草稿嚴格分開統計）

| 指標名稱 | 數量 | 統計與邊界說明 |
|---|---:|---|
| **AI 審核合格候選小題數（`accepted_candidate_count`, `ai_checked`）** | **177 題** | 106 個不重複題組：`training` **129** 題（71 組）、`diagnostic` **24** 題（14 組）、`battle` **24** 題（21 組）、`mock` **0** 題 |
| **人工審核完成小題數（`fully_reviewed_count`, `human_reviewed`）** | **0 題** | 0 題；未經真人審閱前絕不標記為 `human_reviewed` |
| **獨立盲解 — 純閱讀盲解（Part 5–7）** | **108 題** | 100% 由獨立上下文子代理盲解通過並留存輸入／輸出證據 |
| **獨立盲解 — 聽力逐字稿盲解（Part 2–4）** | **65 題** | 100% 由獨立上下文子代理依 `audio_script` + 圖表盲解通過 |
| **獨立盲解 — Part 1 實體圖片視覺盲解（Part 1）** | **4 題** | 4 張 1200×896 照片均由獨立子代理實際讀取圖片盲解通過 |
| **獨立盲解 — 純聽音盲解（Audio-Only Blind Solve）** | **0 / 69 題 (`not_run`)** | 誠實標示 `not_run`；待真人試聽或多模態純音訊盲解工具驗收 |
| **累計素材就緒總小題數（合併 v2 後 `media_ready_item_count`）** | **177 / 177 題** | 匯入 `batch-ag-0001..0010` 後，全數 4 張圖片與 41 個音檔皆為 `status=ready` |
| **統計難度校準完成小題數（`calibrated_item_count`）** | **0 題** | 0 題；全部題組均為 `basis="editorial"` 編輯預估難度 |
| **未發布模考草稿（`unreleased_mock_draft_count`）** | **2 題** | 存放於 `drafts/mock-form-01-unreleased/`（`pool="mock"`），**分開記錄，不計入已發布合格題** |

---

## 2. 已匯出不可變批次一覽（`exports/batch-ag-0001` 至 `0010`）

| Batch ID | Pool | 版本 | 題組數 | 小題數 | Ready 素材數 | Planned 素材數 | Validation 檢查計數 | Overall Result |
|---|---|---|---:|---:|---:|---:|---|---|
| `batch-ag-0001` | `training` | v1 | 20 | 20 | 0 | 8 | pass:11 / warn:1 / fail:0 / not_run:1 | `incomplete` |
| `batch-ag-0002` | `training` | v1 | 13 | 19 | 0 | 11 | pass:11 / warn:2 / fail:0 / not_run:1 | `incomplete` |
| `batch-ag-0003` | `training` | v1 | 6 | 18 | 0 | 6 | pass:11 / warn:1 / fail:0 / not_run:1 | `incomplete` |
| `batch-ag-0004` | `training` | v1 | 5 | 15 | 0 | 5 | pass:11 / warn:1 / fail:0 / not_run:1 | `incomplete` |
| `batch-ag-0005` | `training` | v1 | 7 | 28 | 0 | 0 | pass:12 / warn:0 / fail:0 / not_run:1 | `incomplete` |
| `batch-ag-0006` | `training` | v2 | 4 | 8 | 5 | 0 | pass:12 / warn:0 / fail:0 / not_run:1 | `incomplete` |
| `batch-ag-0007` | `training` | v2 | 23 | 41 | 25 | 0 | pass:12 / warn:0 / fail:0 / not_run:1 | `incomplete` |
| `batch-ag-0008` | `training` | v1 | 20 | 29 | 0 | 0 | pass:12 / warn:0 / fail:0 / not_run:1 | `incomplete` |
| `batch-ag-0009` | `diagnostic` | v1 | 14 | 24 | 9 | 0 | pass:12 / warn:0 / fail:0 / not_run:1 | `incomplete` |
| `batch-ag-0010` | `battle` | v1 | 21 | 24 | 6 | 0 | pass:12 / warn:0 / fail:0 / not_run:1 | `incomplete` |

---

## 3. 第一階段 100 題 → 第二階段 400 題（`pool=training`）配額推進表

| 題型 | Phase 1 基線 | **目前已匯出 `training` 累計** | 400 題階段目標累計 | **距離 400 題剩餘需新增配額** |
|---|---:|---:|---:|---:|
| Part 1 | 3 | **3** | 12 | **+9** |
| Part 2 | 13 | **13** | 50 | **+37** |
| Part 3 | 18 | **18** | 78 | **+60** |
| Part 4 | 15 | **15** | 60 | **+45** |
| Part 5 | 15 | **31** | 60 | **+29** |
| Part 6 | 8 | **16** | 32 | **+16** |
| Part 7 | 28 | **33** | 108 | **+75** |
| **合計** | **100 題** | **129 題** | **400 題** | **+271 題** |

---

## 4. 長期 4,800 題（Part × Pool）總配額執行進度

| 題型 | training | battle | diagnostic | mock | 累計合格 ／ 總配額 | 距離 4,800 剩餘配額 |
|---|---:|---:|---:|---:|---:|---:|
| Part 1 | 3 / 90 | 0 / 18 | 1 / 12 | 0 / 24 | **4 / 144** | 140 |
| Part 2 | 13 / 375 | 6 / 75 | 4 / 50 | 0 / 100 | **23 / 600** | 577 |
| Part 3 | 18 / 585 | 0 / 117 | 6 / 78 | 0 / 156 | **24 / 936** | 912 |
| Part 4 | 15 / 450 | 0 / 90 | 3 / 60 | 0 / 120 | **18 / 720** | 702 |
| Part 5 | 31 / 450 | 14 / 90 | 4 / 60 | 0 / 120 | **49 / 720** | 671 |
| Part 6 | 16 / 240 | 4 / 48 | 4 / 32 | 0 / 64 | **24 / 384** | 360 |
| Part 7 | 33 / 810 | 0 / 162 | 2 / 108 | 0 / 216 | **35 / 1296** | 1261 |
| **合計** | **129 / 3,000** | **24 / 600** | **24 / 400** | **0 / 800** | **177 / 4,800** | **4623** |

---

## 5. 全域 177 題難度分布（Editorial Difficulty）

| 難度等級 | 小題數 | 佔比 |
|---|---:|---:|
| D1 | 14 | 7.9% |
| D2 | 30 | 16.9% |
| D3 | 55 | 31.1% |
| D4 | 56 | 31.6% |
| D5 | 22 | 12.4% |

---

## 6. 本專案定義的 22 項能力標籤（Project-Defined Skill Taxonomy）覆蓋統計

目前已匯出 177 題 100% 覆蓋契約 H 節所列、**本專案定義的 22 項能力標籤**（非 ETS 官方認證標籤）：

| Skill Tag | 覆蓋題次 |
|---|---:|
| `chronology` | 7 |
| `conditions_exceptions` | 12 |
| `connector_clause` | 40 |
| `cross_document` | 9 |
| `direct_response` | 11 |
| `explicit_detail` | 47 |
| `graphic_integration` | 5 |
| `indirect_response` | 12 |
| `inference` | 7 |
| `main_idea_purpose` | 8 |
| `next_action` | 13 |
| `paraphrase` | 38 |
| `photo_action` | 3 |
| `photo_state_location` | 2 |
| `preposition_collocation` | 20 |
| `question_function` | 23 |
| `reference_cohesion` | 18 |
| `sentence_insertion` | 8 |
| `speaker_intent` | 8 |
| `verb_form_agreement` | 16 |
| `vocabulary_in_context` | 18 |
| `word_form` | 14 |

---

## 7. 去重、版本升級與家族隔離驗證結果

- **跨版本唯一性**：106 個獨立 `group_id`、177 個獨立 `item_id`。
- **完全相同與正規化文字去重**：106 個獨立題組跨批次比對 **0 重複**。
- **同題型跨家族 n-gram 餘弦相似度檢查**：全部獨立題組兩兩比對均低於 0.82 警戒閾值（**0 近似警告**）。
- **家族（`family_id`）跨用途池隔離**：106 個已匯出獨立 `family_id`（`training`: 71、`diagnostic`: 14、`battle`: 21），跨池衝突數為 **0**。
