# Codex MVP 交付 — 2026-10-29

## P0：可上機離線練習

狀態：**程式與 built-App 自動化驗證通過；等待使用者覆蓋 Run 後做五分鐘真機驗收。**

### 內建 seed

- 來源：未修改的 `exports/batch-ag-0001` 至 `batch-ag-0007`。
- App 資源：`SeedContent/batch-ag-0001` 至 `SeedContent/batch-ag-0007`，共 74 個檔案、8.9 MB。
- 啟用結果：7 批、51 題組、100 個唯一小題，全部為 `training / ai_checked / fixture=false`。
- Part 1–7 小題數：3 / 13 / 18 / 15 / 15 / 8 / 28。
- 離線素材：27 個 m4a、3 個 jpg，共 30 個；installed asset bytes 再核對 manifest SHA-256。
- 沒有納入 0008–0010；稽核證明原版本不符合 Content Contract，修訂前不算可用 177 題。

### 啟動與資料安全

- App 啟動以非同步 actor 從 `Bundle.main/SeedContent` 讀取七包。
- 每包仍走 `ContentBatchImporter` 的 schema、manifest inventory、SHA-256、引用、review 與用途池驗證。
- `ContentVersionStore.installAtomically` 先完成整個候選 catalog，再一次寫入 active state；任一包或合併失敗會移除本次新版本並保留舊 state。
- 全新 store、已安裝但空 store 都會自動補入；重啟與重試冪等。
- profile、作答、錯題、曝光與偏好使用獨立 profile store，不會被 seed 重設。
- 已有較高 group version 時，seed 重跑仍保留較高版本，不降級。
- UI 有「正在驗證離線題庫」、具體失敗原因與「重新驗證」。

### 練習 UX

- 今天頁主要按鈕為「開始練習」。
- Part 1–7 顯示實際可練題數；未曝光完整題組優先，複習題組分開。
- 作答後立即顯示正解證據與詳解；完成題組可按「下一組」接續同 Part 未曝光題組。
- Part 1–2 作答前仍隱藏由音訊提供的文字；慢速、重播、逐句與逐字稿會記錄輔助條件。
- 模考不足頁提供「先做分項練習」。diagnostic、mock、battle 不借用 training。
- 未設定真正 network backend 時，好友頁明示「尚未部署」，不提供假登入、假好友或假跨手機連線。

### 已執行驗證

| 驗證 | 結果 |
|---|---|
| Seed 專項 XCTest | 4 tests，0 failures |
| 空 store／空殼升級 | 100 題、30 素材成功啟用 |
| 重啟／重試 | 100 題不重複，state bytes 不變 |
| profile 保留 | onboarding、目標、due item 完整保留 |
| 失敗回滾 | 壞第七包不改既有 state／catalog |
| 不降級 | 已裝 v3 後重跑 seed 仍選 v3 |
| 全 iOS 原始碼 typecheck | exit 0，無警告 |
| unsigned generic iOS build | `BUILD SUCCEEDED` |
| built `.app` 資源 | 74 檔、30 媒體、七份 manifest，與來源 `diff -qr` 相同 |
| built `.app` 真實 importer | 4 seed tests，0 failures；直接以 `.app/SeedContent` 為輸入 |

產物：`.build-device/Build/Products/Debug-iphoneos/TOEICPath.app`。該 build 使用 Bundle ID `com.local.TOEICPath`；專案的 Team `VJ3Y39FF2P` 與 Bundle ID 均保留。

### 五分鐘真機清單

1. 開啟 `/Users/ziii/Desktop/TOEIC_IOS_App/TOEICPath.xcodeproj`，選已使用的 iPhone，直接按 Run；不要刪除手機上的 App。
2. 開啟後等待「正在驗證離線題庫」消失；到「練習」確認共同啟用 7 批、51 題組、100 題。
3. Part 1 確認照片與音訊；Part 2 確認音訊且作答前不顯示台詞；各完成一組並查看詳解。
4. Part 5 完成一題後確認正誤、證據、詳解與「下一組」；Part 7 確認文章與題目可閱讀作答。
5. 強制關閉 App 再開啟；確認仍是 100 題，且「我的」作答紀錄／錯題或已看過題組仍保留。

以上真機步驟尚未由 Codex 操作，不標示為 pass。若 seed banner 顯示失敗，請保留完整訊息回報，不要刪 App 或清資料。

### 首次真機回歸（Part 1）

- `ag-g-p1-000001` 的照片與作答畫面已在 iPhone 開啟，但使用者回報音訊混濁；音質狀態為 **not_passed**，不能以檔案可解碼或波形檢查取代真人聽感。
- 原檔實測為 AAC mono 22,050 Hz、約 37.6 kbps；內容依序包含四句，但沒有實際念出 A／B／C／D。App 端不把此觀察誤判成唯一音質原因。
- 播放器每次開始前會停止原播放器，未發現 App 內重疊播放路徑；正常 1× 現在不啟用 rate processing，0.8× 才啟用。
- UI 已補 Part 1／2 標準作答說明、逐字稿鎖定原因與可選的「輔助逐字稿」；練習中開啟逐字稿會記為非標準條件。逐句控制分開標示「下一段」與「正在／剛播放」，不再用跳動數字混淆目前段落。
- 原檔與本機比較樣本記錄在 `artifacts/audio-comparison/part1-research-laboratory/`。比較樣本未放入 seed、未宣稱正式改善；正式替換需由 Antigravity 發布不可變升版並完成真人耳機聽審。
- Antigravity 原工作因 network issue 終止，且其輸入框仍有未送出的附件草稿；為避免破壞草稿，協調端沒有代按 Retry 或送出。目前沒有新修訂包正在被 Codex 接收，手機覆蓋 Run 後仍會使用原音檔，直到不可變 v3 包實際交付並驗證。
- 使用者確認重現於 iPhone 內建喇叭，且同 App 有清晰與模糊音檔。27 檔 inventory 顯示皆為同管線的 22.05 kHz mono AAC，但 voice、實際碼率與響度不同；在尚未指定一個清晰 group 前，不把任一欄位判定為原因。App 現會顯示實際輸出路由，並把播放起始時的 route/sample rate 存進作答條件供後續比對；詳細診斷見 `artifacts/audio-comparison/device-speaker-diagnosis.md`。
- 路由紀錄變更後重新執行完整 suite：63 tests、0 failures；完整 unsigned iPhoneOS build 亦為 `BUILD SUCCEEDED`。
- 2026-10-30 使用者以同一支 iPhone 內建喇叭比較三個 Part 1 樣本後，確認第三個 `ag-g-p1-000003`（Karen en_AU）最清楚。此結果把 Karen 定為下一個小批修訂的優先聲線方向，但尚不能證明碼率或音量是成因。
- 已用原 `ag-g-p1-000001` 內容與既有合成／編碼管線產生兩個本機控制樣本：Karen 無標號，以及 Karen 含可聽 A–D 標號。兩者只位於 `artifacts/audio-comparison/part1-research-laboratory/`，未寫入 `SeedContent`、未修改 exports，也未宣稱為正式替換；待同音量 iPhone 外放 A/B 選定後才交由 Antigravity 發布不可變 v3。
- 使用者選擇 Karen 含 A–D 標號的方向，並要求字母與選項內容間增加短暫停頓。新比較檔 `candidate-karen-labels-400ms-gap.m4a` 使用 400 ms speech-engine silence control；AAC 成品實測四段安靜區約 357–359 ms、總長 15.556 秒、SHA-256 `1eae239a...`。它仍未放入 seed，需真機再聽確認後才可作為 v3 節奏基準。

## P1：修訂題庫與對戰完整性

狀態：**Codex 可執行部分已完成並驗證；修訂題庫仍待 Antigravity 交付。**

- 本機 JSON 服務與 Python／SQLite HTTP 服務都在 participant 已提交或逾時後拒絕任何新答案；已由服務接受的相同 request ID／題目／選項仍可安全重送，重啟後亦同；request ID 改帶其他資料會衝突。
- 對戰建立時伺服器凍結題目順序、無答案的題幹／選項 payload 與素材 checksum。iOS 不再從完整 `QuestionItem` 讀對戰題，也不取得正解、解析或證據。
- ready 需提交與凍結需求完全一致的素材 map；iOS 會讀實際本機檔案重算 SHA-256，缺檔或不符即不上報 ready。
- 雙帳號本機服務與兩個獨立 HTTP client 的 auth、好友、持久聊天、封鎖／移除、判分、逾時 worker、重啟與上述負向案例均已執行。
- 完整 SwiftPM suite：63 tests、0 failures；Python `py_compile` 通過；完整 unsigned iPhoneOS build 為 `BUILD SUCCEEDED`。
- 截至本交付更新，Antigravity 只有 `antigravity-seed-index.md`；未提供 `antigravity-mvp-delivery.md` 或符合 unchanged Swift importer 的不可變修訂包。原 0008–0010 保持未修改、未納入、未宣稱可用。

## 目前仍不可用

- 正式 diagnostic、battle、mock 有效池仍為 0；不以 training 偷補。
- 沒有正式 200 題 form package／整卷音訊，完整模考不可開始。
- 沒有 public HTTPS backend、production OTP、realtime 或 APNs，好友手機聊天與對戰不可用。
- 不提供未校準的 TOEIC 990 預測。
