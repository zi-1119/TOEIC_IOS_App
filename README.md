# TOEIC 路徑（iOS）

原生 SwiftUI、最低 iOS 18、繁體中文學習介面。專案目前已通過核心、跨 process 整合測試與完整 iPhoneOS 無簽署建置。下次在 Xcode 覆蓋 Run 時，App 會自動驗證並啟用內建的 100 題訓練基線與 30 個音圖素材，不需刪除 App 或手動匯入；仍不把這 100 題說成完整題庫，也不提供未經驗證的 990 分數預估。

## 已實作

- 四個固定分頁、首次設定、免登入開始、Dynamic Type / VoiceOver 語意與降低透明度 fallback。
- 內建未修改的七個合格批次；啟動時以既有 importer 原子安裝、重開冪等、失敗回滾，並保留 profile、作答、錯題、曝光、偏好與較新題組版本。
- Part 1–7 真實題組形狀的預覽內容、練習提交後解析、診斷／模考延後揭曉的作答語意。
- 標準與輔助作答條件、逐字稿／慢速／重播紀錄、本機原子化 Codable 儲存。
- 正式 Content Contract 1.0.0 批次目錄／JSONL／SHA-256 阻擋式驗證、私有內容審核畫面、完整模考 200 題配額與題庫不足狀態。
- App 自有 staging、不可變版本目錄與原子啟用目錄；多批共同啟用、最高題組版本合併、各批素材命名空間、重開恢復、跨批次 ID／版本／家族用途池衝突阻擋。
- 可測試的 D1–D5 動態診斷路由、聽讀平衡、Part 覆蓋、題組／家族去重、規則版本與選題理由紀錄；正式診斷池為空時會明確阻擋，不借用 training 題。
- 執行期保留明確 `purpose / contentStatus / fixture`；DailyPlanner、Part 練習、診斷、模考、對戰、錯題入口與 session／服務邊界皆重複執行用途資格檢查。
- 題目一顯示即持久記錄 group／family、題目、版本、來源批次、模式與時間；中途退出、重開或 v1 升 v2 不會洗掉曝光。單 Part 頁會先列未練完整題組，再提供清楚標示的手動複習。
- 可續跑的 200 題模考 runtime，以及 `reports/mock-forms.json` 增補格式的實際解碼／跨批驗證：精確題組版本、必要 manifest 雜湊、整卷素材、毫秒時間線、官方題數與 Part 7 分布都會阻擋式檢查；沒有合格表單與音檔時仍不開放。
- 可執行的兩層後端：裝置內 `LocalBackendHub` 測試替身，以及可獨立啟動的 Python／SQLite HTTP 服務。Swift `NetworkBackendClient` 已串接持久 session、邀請、好友、封鎖／移除、聊天補查／去重、對戰與內容回報；App 依公開 build 設定選擇 HTTP 或本機服務。
- 對戰 match/participant 分離狀態模型、合法轉移、同卷凍結題目與素材欄位、answer-free client payload，以及 server score/winner 欄位。
- 匯入音訊的正常／重播／0.8×／逐句播放、Part 1 本機照片，以及 Part 1–2 作答前文字隱藏；素材缺少、背景或輔助條件不會混入標準證據。
- 完整模考 runtime 已存在，但沒有已接受的正式組卷增補檔與整卷音檔時不會開放；目前不可稱為可用完整模考。

## 已執行驗證

- 未修改 `exports/batch-ag-0001` 至 `batch-ag-0007`：依序匯入後為 7 批、51 題組、100 個唯一小題；Part 1–7 分布為 3/13/18/15/15/8/28，27 個聽力題組解析為 v2。
- 七包合併後有 27 音檔與 3 圖片。測試逐一驗證素材 namespace、安裝路徑、檔案存在與實際 SHA-256；重開、重匯、較高版本替換及失敗回滾皆通過。
- 兩個獨立 Swift HTTP client 與第三個未授權帳號已連到獨立服務 process，驗證持久身分、訊息去重、封鎖／移除權限、服務重啟、伺服器判分，以及兩個 client 關閉後的 worker 逾時結算。
- 指定的 `swift test --scratch-path .swiftpm-build` 最終完整執行為 63 個測試、0 失敗，包含 AppModel 邊界、混合用途池、五包素材資格、七批原始匯出、seed 原子啟用、模考負向契約及本機／跨 process HTTP 整合案例。
- `python3 -m py_compile Backend/local_server.py` 通過；完整 `xcodebuild` 已實際編譯、連結並封裝成功，不以型別檢查代替。
- 建出的 `.app/SeedContent` 有 74 個檔案、7 份 manifest、30 個媒體且與專案 seed byte-identical；直接以 built-App 資源重跑 4 個 seed 測試皆通過。

## 尚未完成／待外部設定

- 現有 100 題全部是 `training / ai_checked`；`diagnostic`、`battle`、`mock` 正式池均為 0。因此診斷、對戰與完整模考會顯示不足，不能拿 training 偷補。
- 模考增補基線已詳列於 `specs/mock-form-contract-v1.md`，並實作精確版本、毫秒時間線、來源 manifest、非循環封裝與 iOS 解碼時長檢查；目前沒有實際 form package。Antigravity 接受的是修改前 hash，新 hash 仍待重新接受，因此正式完整模考不可用。
- HTTP 服務是本機跨 process 的可執行參考層，不是公開雲端部署。Production email OTP、TLS／反向代理、PostgreSQL API 實作、realtime、APNs、濫用防護、秘密管理與備份仍需依 `Docs/backend-deployment.md` 完成。
- 跨 process 已驗證，不等於雙手機或公開網路已驗收；實體雙手機、斷網／網路切換與推播仍未執行。
- 最終 App icon 與品牌素材仍待設計。

## 待實機驗收

- 最大 Dynamic Type、完整 VoiceOver 導覽、降低透明度／動態效果。
- 真機音訊路由、來電、背景與 media-service reset。
- 200 題長時間模考的電量、記憶體、恢復與交卷失敗流程。
- APNs、universal link 邀請與 production OTP 只能在部署設定完成後驗收。

## 建置與驗證

完整無簽署建置指令：

```bash
xcodebuild -project TOEICPath.xcodeproj \
  -scheme TOEICPath \
  -destination 'generic/platform=iOS' \
  -derivedDataPath .build-device \
  CODE_SIGNING_ALLOWED=NO build
```

正式內容契約見 `specs/content-contract-v1.md` 與 `specs/validation-report-v1.md`；App 映射說明見 `Docs/content-import-implementation.md`；後端信任邊界見 `Docs/backend-contract.md`，部署缺口見 `Docs/backend-deployment.md`。規劃與每輪驗證記錄保存在 `.planning/2026-10-27-toeic-ios-complete-app/`。

2026-10-29 最新執行結果為 `** BUILD SUCCEEDED **`，產物在 `.build-device/Build/Products/Debug-iphoneos/TOEICPath.app`。先前 exit 70 的平台元件錯誤仍原樣保存在 `artifacts/build/xcodebuild-diagnosis-2026-10-27.md` 與 `artifacts/build/xcodebuild-diagnosis-2026-10-29.md`，作為歷史診斷證據；目前結果已由 `artifacts/build/xcodebuild-success-2026-10-29.md` 取代。專案保留 Team `VJ3Y39FF2P` 與 Bundle ID `com.local.TOEICPath`。
