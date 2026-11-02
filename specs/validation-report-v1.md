# Validation Report 1.0.0 補充規範

日期：2026-10-27。這是對原本未明確定義之 reports/validation.json 的新增規範，不是恢復的舊文。它不更改 Content Contract 1.0.0 的題組、素材、reviews 或 manifest 欄位，報告使用獨立 report_version。

## 檔案與欄位

每個批次的 reports/validation.json 是一個 UTF-8 JSON object，禁止註解與 NaN。以下欄位必填：

| 欄位 | 型別與用途 |
|---|---|
| report_version | 固定字串 1.0.0 |
| content_schema_version | 固定字串 1.0.0 |
| batch_id | 與 manifest 的 batch_id 相同 |
| generated_at | 實際產生時間，ISO 8601 UTC |
| validator | object，必填 name、version，兩者為非空字串；記錄實際執行工具 |
| profile | authoring / release，含義如下 |
| checks | 非空檢查陣列，格式如下 |
| counts | object，必填 pass、warning、fail、not_run，值為非負整數，與 checks 各狀態計數完全相符 |
| overall_result | pass / warning / fail / incomplete，依下述規則機械推導 |

每個 checks 元素必填：

- check_id：本報告內唯一字串，可用檢查名稱加流水號。
- category：structure / references / uniqueness / assets / review_integrity / content_quality / package。
- target：object，必填 path、group_id、item_id，各值為字串或 null；path 若有值必須為包內相對路徑。
- status：pass / warning / fail / not_run。
- code：非空、穩定的工具自訂診斷代碼，定義保存在工具文件，不能以變動的自然語句充當代碼。
- message_zh：此次實際結果與必要上下文；未執行要寫原因。
- evidence_paths：字串陣列，可為空；非空時必須指向包內實際存在的相對檔案，不複製秘密或個人資料。

overall_result 規則依優先序：有 fail → fail；否則有 not_run → incomplete；否則有 warning → warning；其餘全部 pass → pass。counts 只統計檢查筆數，不代表通過的題目數。

## profile 與檢查範圍

authoring 用於候選草稿交接：合法的 planned 素材可以保留，但缺少完整聽力／圖片時要有 warning；不得假稱素材完成。release 檢查準備發布所需內容，缺必要 ready 素材或既定發布審核證據為 fail。release 的報告 pass 仍不等於題目已心理計量校準或可精準預測多益分數。

每份報告至少覆蓋以下檢查族；若未做，保留 not_run 與原因，不要刪掉該檢查：

1. JSON／schema、必填欄位及 enum。
2. Part 題組／選項／文件結構、答案引用、blank 及表格形狀。
3. evidence、speaker、review_refs 及音訊時間碼引用。
4. ID／版本／family 的本批衝突及跨批衝突；沒有歷史索引時跨批項目列 not_run。
5. 完全相同、正規化近似與語意／家族重複；未執行語意檢查時不得以文字去重代替 pass。
6. 素材狀態、檔案存在、路徑安全、格式與音訊時間範圍。
7. reviews 狀態／證據一致性，沒有實際盲解／人工審查不得聲稱做過。
8. 題目語意、唯一答案與英文品質審查的實際覆蓋。只跑 schema 不足以將此項標 pass。
9. 組包前的檔案清單與數量；交接後另由接收端驗證最終 manifest/hash。

pass 僅表示該項檢查在標明的方法與範圍內通過，不等於語意真理。自動檢查不證明不存在歧義；模型／人工審閱細節放 reviews.jsonl 及其證據檔。

## 打包順序與自我雜湊問題

1. 完成 groups、reviews、素材、盲解證據及其他報告。
2. 執行內容檢查，寫出 validation.json；此時若最終 manifest 尚未建立，該項結果必須 not_run，code 可用 final_manifest_pending。
3. 依實際所有檔案產生 manifest，包含 validation.json 的最終 SHA256，但不包含 manifest 自身。
4. 接收端重新核對 manifest/hash／數量，將接收驗證結果寫在批次目錄之外，例如接收專案的 import-reports 目錄。
5. 不在 manifest 產生後修改包內 validation.json；需要修改則重建整包與雜湊。

候選包因 final_manifest_pending 而 overall_result=incomplete 並非自動拒絕；接收端以獨立檢查補足這項結果。其他 not_run 需逐項說明，是否允許私有預覽與是否可發布分開決定，不能只判斷單一 overall_result 字串。

## 最小結構示例

以下只是格式示例，並非真實驗證紀錄；實際報告必須列出上面所有檢查族。

```json
{
  "report_version": "1.0.0",
  "content_schema_version": "1.0.0",
  "batch_id": "batch-ag-example",
  "generated_at": "2026-10-27T00:00:00Z",
  "validator": {"name": "example-validator", "version": "0.1.0"},
  "profile": "authoring",
  "checks": [
    {
      "check_id": "package-001",
      "category": "package",
      "target": {"path": "manifest.json", "group_id": null, "item_id": null},
      "status": "not_run",
      "code": "final_manifest_pending",
      "message_zh": "格式示例：最終 manifest 將在報告保存後產生，接收端須另行驗證。",
      "evidence_paths": []
    }
  ],
  "counts": {"pass": 0, "warning": 0, "fail": 0, "not_run": 1},
  "overall_result": "incomplete"
}
```
