# 第二輪 App × Antigravity 驗收 — 2026-10-29

## 結論

有實質進展，但不能驗收為全部完成。上輪用途池與單 Part 選題問題已有實作及測試修正，新增 HTTP 後端可在本機經網路測試；然而新增三批題庫全部無法被 App 匯入，且新後端存在已交卷仍能補答計分的缺陷。完整 iOS build、實機與正式模考仍未通過／未交付。

本輪未修改 App、後端、題庫、規格或對方交付文件。僅新增本稽核目錄的紀錄與獨立診斷程式，執行測試產生快取／建置結果，臨時題庫與測試資料庫已清理；未公開部署、發信或跨對話派送。

## 實際驗證結果

| 項目 | 本輪結果 |
|---|---|
| SwiftPM 全測試 | **55 tests，0 failures**；包含兩個 HTTP process/client 整合案例 |
| 完整 generic iOS xcodebuild | **exit 70**；iOS 26.2 destination component 不可用，尚未進入編譯 |
| 真實批次 0001–0007 匯入 | **通過**，51 題組、100 唯一小題、30 素材 |
| 真實批次 0008／0009／0010 匯入 | **三批皆失敗**，每批第一行 evidence 缺 reasoning_zh |
| 新包失敗後的狀態 | state.json 保持原樣；重開仍 100 題，重匯 0007 不增題 |
| 獨立 JSON Schema 全量驗證 | 0001–0007 無錯；0008=269、0009=212、0010=210 個 schema violations |
| 97 筆 manifest 檔案雜湊 | 全吻合；不代表 schema 或語意驗收通過 |
| 生產端實體資料統計 | 106 題組、177 題：training129、diagnostic24、battle24、mock0 |
| 素材技術檢查 | 41 音檔 ffprobe 可解析、4 圖片；無跨池 family ID 衝突 |
| 實際 App 核心成功啟用題庫 | training100；diagnostic0、battle0、mock0；Part5 picker 為15個未見題組 |
| 獨立 HTTP 交卷後補答探針 | **重現缺陷**：submitted 之後的新答案仍回 HTTP200，結算納入補答 |

691 個 schema violations 是巢狀欄位層級的錯誤數，不是 691 題。新三包合計 55 題組／77 題，55 題組全有違規，77 題全缺至少一筆 evidence.reasoning_zh。

## 1. 高優先：新 77 題均不能匯入，生產端結構檢查誤判通過

### 重現

診斷程式 `ten-batch-audit.swift` 連結本輪已編譯的真正 App 核心模組；把 0001–0010 依次安裝至新暫存 ContentVersionStore。0008、0009、0010 各自皆拋出：

```text
invalidJSONL(path: "groups.jsonl", line: 1,
  underlying: Swift.DecodingError.keyNotFound("reasoning_zh", ...))
```

個別包失敗後繼續驗證其他包，不因第一包錯誤就把後兩包假定失敗。每次失敗均確認 atomic state preserved=true。

### 獨立 schema 驗證確認的問題

直接使用現有 `specs/group.schema.json` 與 `jsonschema.Draft202012Validator`：

- evidence 缺必填 `reasoning_zh`。
- vocabulary 使用 `surface`／`pos`／`note_zh`，卻缺契約要求的 `term_en`／`example_en`。
- document 使用 `doc_id`／`doc_type`，卻缺 `document_id`／`genre`。
- distractor_notes 多出未允許的 `trap_type`。
- provenance 多出未允許的 `prompt_hash`。
- 0008 另有一筆 vocabulary 為陣列而非 object。

`scripts/generate_batches_0008_to_0010.py:56`、`:60`、`:105` 可直接看到產生不相容欄位的 helper 與 evidence。這些不是新模考契約變動造成，而是原 Content Contract 1.0.0 的既有必填欄位。

`scripts/validate_and_package.py:251` 的 schema 檢查只核對 item 頂層 keys／skill tags，沒有用完整 JSON Schema 驗證巢狀結構。新三包 `reports/validation.json` 因而錯誤記錄 `structure-001 = pass / struct_json_schema_valid`。檔案 hash、AI 盲解及 reports 中的 pass 均不能抵銷此失敗。

### 修正與驗收要求

Antigravity 應先修生成器與完整巢狀 schema 驗證，加入上述負向案例；補上有實際意義的證據推理與例句，不能只填空字串／佔位文字。依不可變發布規則產生修訂版包，保留題目身份與提高版本，修訂不再計為新增題。Codex 不應以將必要欄位設 optional 或放寬契約掩蓋錯誤。

新版必須同時通過生產端 schema 與 App 真實 importer，再把可用總數更新為 177（或實際修訂後數量）。原有55測試沒有覆蓋0008–0010，須補入真實新包接收回歸。

## 2. 高優先：對戰交卷後仍能補答並計分

來源：`Backend/local_server.py:428`。

答案 endpoint 只檢查整場 state=active 與 deadline，沒有檢查本人的 participant state 是否已 submitted。因此當另一人還沒交卷，已交卷者仍能提交之前未作答的題。

`backend-submit-probe.py` 在 127.0.0.1、獨立暫存 SQLite 與假帳號下執行：

1. 建立兩小題的測試對戰；兩人 ready。
2. Alice 答第一題並交卷，回傳 participant state=submitted。
3. Alice 再補答第二題，伺服器回 HTTP200。
4. Bob 交卷後，Alice 得 200 分（每題100），包含交卷後那題。

這不是推測，也不是修改正式資料取得的結果。應在伺服器阻擋 submitted／timedOut 等終結 participant 的新答案；已接受請求的冪等重試須與新作答分開處理。補負向網路測試，確認提交後、逾時後、重啟後不再收新答案。

## 3. 對戰客戶端仍依賴含答案題庫；素材一致性尚未落實

來源檢查（不是完整滲透測試）：

- `AppModel.swift:263` 從本機 QuestionItem 讀取 correctOptionID 建構對戰描述。
- `AppModel.swift:311` 的對戰顯示仍從本機 package 取得完整 QuestionItem；其模型含正解與解析。NetworkBackendClient 雖移除「上傳的正解」，不能因此宣稱「正解只存在伺服器」。目前尚未完成不含答案的競技供題模型／下載流程。
- `NetworkBackendClient.ready` 送 assetChecksums，但 `Backend/local_server.py:417` 的 ready handler 未使用或核對它。這對目前純文字 Part5 的影響較小，但不能宣稱音圖對戰雙方素材一致性已驗收。
- client 以整個本機合併 package 的 contentVersion 比對 battle，仍需確認真實專用題庫發版／不同裝置安裝其他 training 包時的版本策略。

正式跨手機前應分開私人製作包、練習包與無答案競技 payload；服務端鎖定對戰內容版本、題序與必要素材，客戶端實際核對素材後 ready，不能僅靠 UI 不顯示答案。

## 4. 已修正／有實質進展的項目

- ContentEligibility 集中用途、fixture、內容狀態與素材引用資格。
- DiagnosticRouter 已移除 training fallback；DailyPlanner 限 training；App session 邊界與對戰 Part5 選題也檢查用途。
- PartPracticePickerView 提供未曝光／複習題組列表，已不再固定只開第一組。
- 曝光紀錄增加 family/version/session 歷史，展示時寫入；已有跨重啟／升版測試。此次未做真機完整生命週期 QA。
- 七批基線新增 namespace、hash、重開與回滾測試。
- 已有獨立 Python/SQLite HTTP server、Swift URLSession client，並真正跑過兩client＋outsider權限、聊天持久化與去重、重啟恢復、伺服器結算、無client在線的deadline worker測試。
- Antigravity 修正模考藍圖 54+49=103 題組，建立人工抽審包，並清楚區分文字／圖片盲解與純聽音盲解。新三包的語意原創性與完整音質未在本輪逐題重審。

## 5. 仍未完成或未驗收

- **模考契約仍未雙邊接受同一版本**：磁碟現值與 Codex 接受值為 `f8d3e70867c256f95384c9c490735afcbebadbed91728f86450e262b28ae650e`；Antigravity 接受的是舊 `0588948a0b61cb43ed9e64abd8b12d35740560108790869f91c11920873a8f6f`。
- **正式 mock=0**，未發布草稿只有2題；藍圖不是200題實際卷，沒有整卷音訊可做長時間實播驗收。
- **題庫擴充未達400/4800目標**：檔案有177題候選，成功接收仍100；training候選129，不是400。
- **品質狀態**：177題檔案皆 ai_checked；human_reviewed=0、calibrated=0；對方聲明純聽音盲解仍0/69。不能據此宣稱可精準預估多益分數。
- **完整 iOS build仍失敗**：destination iOS26.2 component。未把核心測試當成App可安裝運作；本輪未重跑 whole-source typecheck、未操作模擬器／iPhone。
- **後端不是正式部署**：目前可驗證本機HTTP參考實作。production OTP、HTTPS部署與權限／維運、realtime、APNs及雙實體手機端到端尚未完成。App 安裝方式不在本輪範圍。
- 雙方交付文件互有過時狀態：Codex仍描述專用池0／舊100題；Antigravity仍說Codex status尚未建立。應以真實共同接收測試結果更新，不能只互相引用舊報告。

## 6. 下一輪最小閉環

1. **Antigravity**：優先修新三包格式與驗證器假陽性，按不可變規則交修訂包，先暫停擴量以免複製錯誤。
2. **Codex**：修已交卷補答與競技答案隔離；將修訂後真實新包加入接收測試；列明來源包／server catalog／client payload之版本關係。
3. **共同**：接受同一模考契約 hash，明列 human-reviewed 正式門檻與候選預覽界線，不能偽造人工狀態。
4. **環境／實機**：解決Xcode platform component後重跑完整build，才進一步作iPhone UI／音訊／雙手機驗收。

本輪判定：**上輪部分修正可接受；新題庫交接與對戰完整性不通過；產品整體未完成。**
