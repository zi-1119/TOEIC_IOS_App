# Codex 本輪交付 — 2026-10-29

本文件只記錄已實作、已執行驗證與仍待外部條件的狀態。`exports/batch-ag-0001` 至 `batch-ag-0007` 未被修改；Antigravity 的狀態與交付文件也未被覆寫。

## 1. 已實作

### 用途池、曝光與 Part 選題

- runtime 題組保留 `purpose`、`content_status`、`fixture`，舊資料以非正式內容安全解碼。
- training、diagnostic、battle、mock 的資格規則集中於 `ContentEligibility`，並在引擎、App session 起點與服務邊界重複檢查，移除跨池補題。
- 題目一顯示即記錄 group、family、item、版本、來源批次、模式與時間；中途離開、重開及題組升版仍保留歷史曝光。
- Part 練習先顯示未曝光且素材完整的正式 training 題組；已曝光題組只在明確的複習區出現；缺素材內容只可非正式預覽。
- 診斷只用正式 diagnostic 池並排除歷史 family；正式池不足時明確阻擋，不借用 training 題。

主要程式位置：

- `TOEICPath/Domain/ContentModels.swift`
- `TOEICPath/Data/ContentBatchContract.swift`
- `TOEICPath/Data/LearningEngines.swift`
- `TOEICPath/App/AppModel.swift`
- `TOEICPath/Features/Practice/PracticeHomeView.swift`
- `TOEICPath/Features/Session/SessionView.swift`

### 七批累積與真實匯入

- 多批 active catalog、最高題組版本合併、每批素材命名空間、原子寫入、重開、重匯與失敗回滾均已落地。
- 真實測試直接讀取未修改的 batch 0001–0007。結果為 7 批、51 題組、100 個唯一小題；Part 1–7 分布為 3/13/18/15/15/8/28。
- 27 個 listening 題組解析為 v2；安裝後 27 音檔與 3 圖片均核對 namespace、路徑、存在性及實際 SHA-256。
- 另以只匯入 batch 0001–0005 的真實回歸驗證：51 題 reading 可啟動正式 training；49 題 listening 全部只出現在素材預覽，且 session 邊界拒絕正式作答。
- 現有 100 題皆為 `training / ai_checked`。51 題 reading 可進正式 training；具備素材的 listening v2 可練習。任何缺少規定音圖的舊版／不完整內容只保留非正式預覽資格，不能計入正式聽力證據。

### 模考契約與 runtime

- `specs/mock-form-contract-v1.md` 現行 SHA-256：`f8d3e70867c256f95384c9c490735afcbebadbed91728f86450e262b28ae650e`。
- 已實作精確 `group_id + version + source_batch_id`、必要來源 manifest hash、非循環來源包 → 獨立 form package 拓撲，以及 `assets/mock/<form_id>/` 整卷音檔登錄。
- 正式表單要求 200 唯一小題、官方 Part 配額、正式 `mock / fixture=false / human_reviewed` 題組、毫秒時間線、逐題 unlock、Part 1–2 directions/response window，以及 AVFoundation 解碼時長和宣告值差 `<= 100 ms`。
- 恢復只允許使用已驗證時間線的固定 anchor；缺檔、hash／版本不符、事件缺漏／重複／倒退／越界、秒毫秒誤用及音檔時長不符都會拒絕表單。
- 目前沒有實際 form package 或合格整卷音檔，因此正式完整模考是「runtime 已實作、內容不可用」，不是完成可考。

### 可執行後端與 iOS 串接

- `LocalBackendHub` 保留為裝置內替身；`Backend/local_server.py` 是獨立 process 的 Python／SQLite HTTP 服務；`NetworkBackendClient` 為 Swift URLSession client。
- 已串接 session、profile merge、好友邀請／接受／移除、封鎖、一對一持久聊天、cursor 補查與 client message 去重、內容回報及伺服器權威對戰。
- App 由 `SERVER_BASE_URL` 與 `SERVER_PUBLIC_CLIENT_ID` 選擇 network client；缺少設定時使用本機替身。
- 對戰題庫與正解只存在受信任的 server catalog。client 不傳正解，也不能寫 score／winner。服務保存答案、request ID、deadline 與結算；deadline worker 在兩個 client 都離線後仍可結算。

部署前仍需：可信 HTTPS／反向代理、production email OTP、PostgreSQL API 實作與最小權限、秘密管理、rate limiting、備份、realtime、APNs、universal links、帳號刪除／保留政策。完整設定見 `Docs/backend-deployment.md`。

## 2. 已執行驗證

| 項目 | 實際結果 | 狀態 |
|---|---|---|
| 指定 SwiftPM 完整命令 | 55 tests，0 failures | pass |
| 五包素材資格 | 51 reading 可正式練習；49 listening 僅預覽且 session 拒絕 | pass |
| 七批原始匯出整合 | 7 批／51 groups／100 items／30 assets；重開、重匯、升版、回滾通過 | pass |
| 模考契約 XCTest | 合法表單與必要負向案例共 9 tests | pass |
| 獨立 HTTP process | 兩個 Swift client + outsider；重啟持久化、聊天、權限、server scoring、離線 deadline worker | pass |
| 全 iOS 原始碼型別檢查 | iPhoneOS 26.2 SDK，exit 0，無警告 | pass（補充證據） |
| Python 服務語法 | `python3 -m py_compile Backend/local_server.py`，exit 0 | pass |
| 完整 unsigned xcodebuild | exit 70，進入 source compilation 前即因 iOS 26.2 component 未安裝而停止 | blocked |
| Simulator UI 驗收 | 未執行；本機沒有相符可用 runtime | not_run |
| 實體 iPhone 驗收 | 未執行 | not_run |
| 雙實體手機／公開網路 | 未執行；目前只驗證本機跨 process | not_run |

SwiftPM 指定命令：

```bash
env CLANG_MODULE_CACHE_PATH=/Users/ziii/Desktop/TOEIC_IOS_App/.swiftpm-build/module-cache \
  swift test --scratch-path /Users/ziii/Desktop/TOEIC_IOS_App/.swiftpm-build
```

完整 Xcode 命令及原始錯誤證據見 `artifacts/build/xcodebuild-diagnosis-2026-10-29.md`。型別檢查不能替代這個失敗的完整建置。

## 3. 契約對齊狀態

| 文件 | 現行 SHA-256 | 狀態 |
|---|---|---|
| `specs/content-contract-v1.md` | `f3aee0f0ae02ae4b69bc066deb4be83acd72c687b121b72d0331f4f7567a28c1` | 既有共同基線 |
| `specs/validation-report-v1.md` | `8c64b71847e83f5179e3c3fa605af14312b1a058418ca8e0b4af044d2da22ccc` | 既有共同基線 |
| `specs/mock-form-contract-v1.md` | `f8d3e70867c256f95384c9c490735afcbebadbed91728f86450e262b28ae650e` | Codex accepted；Antigravity re-acceptance pending |

Antigravity 狀態文件接受的是修改前 hash `0588948a0b61cb43ed9e64abd8b12d35740560108790869f91c11920873a8f6f`。現行文件加入非循環封裝、正式題組狀態與 AVFoundation 解碼時長規則後 hash 已改變，所以現在不能宣稱 shared acceptance。

## 4. 已知風險與尚未驗收

- 正式 diagnostic、battle、mock 池目前都是 0；相關入口正確顯示不足，但尚無正式內容可做端到端學習品質驗收。
- 目前沒有真實 200 題 form package 與整卷音檔，無法驗證 45 分鐘播放、長時間背景／中斷恢復及完整交卷。
- SwiftUI UI 尚未在 Simulator 或真機執行；最大 Dynamic Type、VoiceOver、降低透明度／動態效果、44pt 觸控區及視覺版面仍屬待實機驗收。
- 真機音訊路由、來電、背景、media-service reset、斷網／切網、APNs 與 universal link 未執行。
- HTTP 參考服務未達公開 Internet 安全要求，也沒有端對端加密宣稱。

## 5. 下一個內容包要求與最小使用者操作

Antigravity 下一步：

1. 重新讀取現行 `specs/mock-form-contract-v1.md`，記錄相同 `f8d3...650e` hash 或提出具體不相容差異。
2. 按用途分開輸出正式 `diagnostic`、`battle`、`mock` 題組；不得只改 training 標籤或重用同 family 跨池。
3. 先發布完整、不可變的 mock 題組來源包，再發布獨立 form package；form report 不得 self-reference。
4. 正式 mock 題組與整卷時間線音檔必須 `human_reviewed`，素材、hash、decoded duration、timeline 與 unlock 均符合現行契約。

使用者最小必要操作：

1. 在 Xcode → Settings → Components 安裝 iOS 26.2 platform component。
2. 重新執行本文件列出的完整 unsigned `xcodebuild`；成功後才能開始 Simulator／真機 UI 驗收。
3. 若要雙手機測試，提供一個可信 HTTPS 測試端點與 public client ID；production OTP／APNs 則另需對應供應商與 Apple 憑證設定。

除此之外，本輪不需要使用者手動修題庫或修改 Antigravity 原始批次。
