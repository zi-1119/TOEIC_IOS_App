# 完整模考組卷清單與用途池家族隔離報告

更新時間（UTC）：`2026-10-28T08:40:00Z`

---

## 1. 用途池家族隔離（Family Pool Isolation）驗證

- 依契約 A 節規定：「題組與同一家族不得跨用途池。不能從使用者練習過的 `training` 題直接搬到 `mock`。診斷與完整模考也分開。」
- 目前全域已匯出索引（[global-index.json](file:///Users/ziii/Desktop/TOEIC_IOS_App/reports/global-index.json)）共登錄 **106** 個已匯出獨立 `family_id`（另含未發布草稿區 `drafts/mock-form-01-unreleased/` 2 個獨立 `mock` 家族）：
  - `training` 池專用家族：**71** 個（涵蓋 `batch-ag-0001`..`0005` 不可變基線、`batch-ag-0006`..`0007` v2 媒體升級批次，以及 `batch-ag-0008` 新增 20 個閱讀題組家族）
  - `diagnostic` 池專用家族：**14** 個（涵蓋 `batch-ag-0009` Part 1–7 共 14 組 24 題，家族前綴 `ag-fam-diag-*`）
  - `battle` 池專用家族：**21** 個（涵蓋 `batch-ag-0010` Part 2/5/6 共 21 組 24 題，家族前綴 `ag-fam-btl-*`）
  - `mock` 池已匯出專用家族：**0** 個（藍圖與未發布草稿 `ag-fam-mock-*` 保存在 [mock-form-01-blueprint.json](file:///Users/ziii/Desktop/TOEIC_IOS_App/blueprints/mock-form-01-blueprint.json) 與 `drafts/mock-form-01-unreleased/`，不計入已匯出題數）
  - **跨池共用家族衝突數：0 個（PASS）**

---

## 2. 對齊 `specs/mock-form-contract-v1.md`（1.0.0）之題庫端組卷與音訊時間軸規格

- **規範文件**：[mock-form-contract-v1.md](file:///Users/ziii/Desktop/TOEIC_IOS_App/specs/mock-form-contract-v1.md)（SHA-256：`0588948a0b61cb43ed9e64abd8b12d35740560108790869f91c11920873a8f6f`）
- **題庫端狀態報告**：[antigravity-contract-status.md](file:///Users/ziii/Desktop/TOEIC_IOS_App/handoff/2026-10-28/antigravity-contract-status.md)
- **JSON Schema 驗證檔**：[mock-forms.schema.json](file:///Users/ziii/Desktop/TOEIC_IOS_App/specs/mock-forms.schema.json)
- **核心設計對齊**：
  1. **毫秒級時間軸（Millisecond Precision）**：全面採用 `specs/mock-form-contract-v1.md` 定義之毫秒欄位（`reading_time_limit_ms: 4500000`、`listening_timeline.timeline_asset.duration_ms`、`listening_timeline.events[].start_ms` / `end_ms`），不再使用早期草案中的秒數欄位。
  2. **題組與題數算術修正（Complete Groups Without Splitting）**：
     - 聽力（100 題）：Part 1（6 組 6 題）+ Part 2（25 組 25 題）+ Part 3（13 組 39 題）+ Part 4（10 組 30 題）= **54 個完整題組（100 道小題）**
     - 閱讀（100 題）：Part 5（30 組 30 題）+ Part 6（4 組 16 題）+ Part 7 單篇（10 組 29 題：2 題組 × 3 + 3 題組 × 5 + 4 題組 × 2）+ Part 7 雙／三篇（5 組 25 題：雙篇 × 3 + 三篇 × 2）= **49 個完整題組（100 道小題）**
     - 全卷總計：**54 + 49 = 103 個完整題組（200 道小題）**。題組數由 `content_set.group_refs` 依完整題組動態推導，絕不硬編碼錯誤的 `93` 或 `39`。
  3. **雙批次無循環封裝架構（Two-Batch Acyclic Packaging）**：
     - 題組來源批次（如 `batch-ag-mock-01-source`）：封裝 200 道 `pool="mock"` 題組與單題媒體資產，產出固定 `manifest.json` SHA-256。
     - 模考組卷批次（如 `batch-ag-mock-01-form`）：於 `reports/mock-forms.json` 的 `content_set.required_batches` 引用來源批次之 `manifest_sha256`，並附帶整卷合成聽力時間軸音檔 `assets/mock/<form_id>/timeline.m4a`。
  4. **真人聽審發布關卡**：依 `specs/mock-form-contract-v1.md` 第 8 節及 `MockFormContract.swift` 規定，正式模考時間軸音檔 `review_state` 須達 `"human_reviewed"` 方可在生產環境開放作答；未完成真人聽審與滿 200 題前，不匯出偽稱可用的半成品模考卷。

---

## 3. 四份完整模考（Mock Forms 01–04）固定組卷配額與保留 ID 區間

每份完整模考固定為 **200 道小題**（依本專案 Part 7 單篇 10 組配置為 **103 個完整題組**：聽力 54 組 100 題、閱讀 49 組 100 題），各卷獨立命題、固定 `form_id` 與 `group_id` 順序，絕不挪用 `training`、`battle` 或 `diagnostic` 池題組：

| Form ID | Pool | Part 1 (6組6題) | Part 2 (25組25題) | Part 3 (13組39題) | Part 4 (10組30題) | Part 5 (30組30題) | Part 6 (4組16題) | Part 7 單篇 (10組29題) | Part 7 多篇 (5組25題) | 合成時間軸音訊路徑 | 狀態 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `mock-form-01` | `mock` | `ag-g-p1-000121`..`000126` | `ag-g-p2-000501`..`000525` | `ag-g-p3-000261`..`000273` | `ag-g-p4-000201`..`000210` | `ag-g-p5-000601`..`000630` | `ag-g-p6-000081`..`000084` | `ag-g-p7-000221`..`000230` | `ag-g-p7-000231`..`000235` (雙篇×3 + 三篇×2) | `assets/mock/mock-form-01/timeline.m4a` | `blueprint_ready` |
| `mock-form-02` | `mock` | `ag-g-p1-000127`..`000132` | `ag-g-p2-000526`..`000550` | `ag-g-p3-000274`..`000286` | `ag-g-p4-000211`..`000220` | `ag-g-p5-000631`..`000660` | `ag-g-p6-000085`..`000088` | `ag-g-p7-000236`..`000245` | `ag-g-p7-000246`..`000250` (雙篇×3 + 三篇×2) | `assets/mock/mock-form-02/timeline.m4a` | `planned` |
| `mock-form-03` | `mock` | `ag-g-p1-000133`..`000138` | `ag-g-p2-000551`..`000575` | `ag-g-p3-000287`..`000299` | `ag-g-p4-000221`..`000230` | `ag-g-p5-000661`..`000690` | `ag-g-p6-000089`..`000092` | `ag-g-p7-000251`..`000260` | `ag-g-p7-000261`..`000265` (雙篇×3 + 三篇×2) | `assets/mock/mock-form-03/timeline.m4a` | `planned` |
| `mock-form-04` | `mock` | `ag-g-p1-000139`..`000144` | `ag-g-p2-000576`..`000600` | `ag-g-p3-000300`..`000312` | `ag-g-p4-000231`..`000240` | `ag-g-p5-000691`..`000720` | `ag-g-p6-000093`..`000096` | `ag-g-p7-000266`..`000275` | `ag-g-p7-000276`..`000280` (雙篇×3 + 三篇×2) | `assets/mock/mock-form-04/timeline.m4a` | `planned` |
