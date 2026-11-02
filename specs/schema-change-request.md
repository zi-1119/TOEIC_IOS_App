# Schema 對齊與變更請求紀錄（Schema Change Request & Alignment Log）

更新日期：2026-10-28  
目前生效基礎契約：
- [specs/content-contract-v1.md](file:///Users/ziii/Desktop/TOEIC_IOS_App/specs/content-contract-v1.md)（`schema_version: "1.0.0"`, SHA-256: `f3aee0f0ae02ae4b69bc066deb4be83acd72c687b121b72d0331f4f7567a28c1`）
- [specs/validation-report-v1.md](file:///Users/ziii/Desktop/TOEIC_IOS_App/specs/validation-report-v1.md)（`report_version: "1.0.0"`, SHA-256: `8c64b71847e83f5179e3c3fa605af14312b1a058418ca8e0b4af044d2da22ccc`）

模考附加契約對齊基準：
- [specs/mock-form-contract-v1.md](file:///Users/ziii/Desktop/TOEIC_IOS_App/specs/mock-form-contract-v1.md)（`form_schema_version: "1.0.0"`, SHA-256: `0588948a0b61cb43ed9e64abd8b12d35740560108790869f91c11920873a8f6f`）
- Antigravity 正式對齊狀態檔：[handoff/2026-10-28/antigravity-contract-status.md](file:///Users/ziii/Desktop/TOEIC_IOS_App/handoff/2026-10-28/antigravity-contract-status.md)

---

## 1. 基礎契約遵循聲明

Antigravity 題庫工作區完全依照 `TOEIC Content Contract 1.0.0` 與 `Validation Report 1.0.0` 建立 JSON Schema、驗證工具與匯出批次包（`exports/batch-ag-XXXX/`），**未單方新增、刪除或修改任何交換欄位或 enum**。

---

## 2. 模考附加契約（`Mock Form Additive Contract 1.0.0`）對齊與算術修正

### A. 廢止舊提案秒數欄位、全面對齊新版毫秒規格
[specs/schema-change-request-mock-forms.md](file:///Users/ziii/Desktop/TOEIC_IOS_App/specs/schema-change-request-mock-forms.md) 為舊版過渡提案，已不再作為現行依據。Antigravity 已建立對應新版 [specs/mock-form-contract-v1.md](file:///Users/ziii/Desktop/TOEIC_IOS_App/specs/mock-form-contract-v1.md) 之 JSON Schema（[specs/mock-forms.schema.json](file:///Users/ziii/Desktop/TOEIC_IOS_App/specs/mock-forms.schema.json)），對齊重點如下：
1. **檔案位置與雜湊登錄**：
   - 組卷描述檔：`reports/mock-forms.json`（列入 `manifest.json.files`）。
   - 整卷時間軸音檔：`assets/mock/<form_id>/timeline.m4a`（列入 `reports/mock-forms.json` 頂層 `assets` 陣列，且獨立列入 `manifest.json.files`，`kind: "mock_audio_timeline"`）。
2. **避免自我雜湊循環之兩階段批次結構**：
   - 模考題組與單題素材先封裝為不可變**題組來源批次**（如 `batch-ag-mock-01-source`），取得確定之 `manifest_sha256`；
   - 組卷報表 `reports/mock-forms.json` 與整卷時間軸音檔封裝於**組卷批次**（如 `batch-ag-mock-01-form`），其 `content_set.required_batches` 僅引用前置來源批次之 `{batch_id, manifest_sha256}`，不引用組卷批次自身，徹底消除循環雜湊。
3. **精確題組版本參照與毫秒事件時間軸**：
   - `forms[].group_refs`：每筆為 `{group_id, version, source_batch_id}`，展開順序完全等於 `ordered_item_ids`（200 題 = `listening_item_ids` 100 題 + `reading_item_ids` 100 題）。
   - `forms[].listening_timeline`：包含 `asset_id`、`duration_ms` 與嚴格遞增 `sequence` 之毫秒級 `events`（`directions`, `item_unlock`, `stimulus`, `response_options`, `response_window`, `pause`）。
   - `forms[].reading_time_limit_ms`：固定為 `4500000`（75 分鐘）。

### B. 完整題組算術修正（54 聽力 + 49 閱讀 = 103 組，動態推導不硬編碼常數）
先前報告曾誤將單卷題組總數寫為「93 組（54 聽力 + 39 閱讀）」。依目前藍圖配額重新核算：
- **Listening（100 題）**：
  - Part 1：6 組（6 題）
  - Part 2：25 組（25 題）
  - Part 3：13 組（39 題，每組 3 題）
  - Part 4：10 組（30 題，每組 3 題）
  - **聽力小計**：`6 + 25 + 13 + 10 = 54 組（100 題）`
- **Reading（100 題）**：
  - Part 5：30 組（30 題，每組 1 題）
  - Part 6：4 組（16 題，每組 4 題）
  - Part 7 單篇（`single_passage`，每組 2–4 題，共 29 題）：以現行藍圖（3 題 × 9 組 + 2 題 × 1 組，或 4 題 × 2 組 + 3 題 × 5 組 + 2 題 × 3 組）配置為 **10 組（29 題）**
  - Part 7 多篇（`double_passage` + `triple_passage`，每組 5 題，共 25 題）：固定為 **5 組（25 題）**
  - **閱讀小計**：`30 + 4 + 10 + 5 = 49 組（100 題）`
- **全卷合計**：依現行藍圖為 **`54 + 49 = 103 個完整題組（200 題）`**。
- **動態驗證原則**：由於 Part 7 單篇每組可為 2–4 題，合法試卷之單篇組數可介於 8–14 組（全卷總組數對應介於 101–107 組）。因此生成與驗證工具均以「完整題組不拆分、展開小題數符合 Part 1–7 `6/25/39/30/30/16/54` 及 Part 7 `29 單篇 + 25 多篇`」動態推導，絕不硬編碼固定總組數常數。
