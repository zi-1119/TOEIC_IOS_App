# 給 Codex：依整合稽核修正 App、測評隔離與真實交付

這是一份實作指令，不是要你再寫一輪空泛規劃。請在現有專案上繼續，不重建、不覆蓋他人工作。完成可安全執行的實作與驗證，再交付精確的完成／未完成狀態。

## 1. 專案、目標與必讀文件

專案根目錄：`/Users/ziii/Desktop/TOEIC_IOS_App`。

產品為原生 Swift／SwiftUI iPhone TOEIC Listening & Reading App，英文題目、繁體中文介面與詳解。使用者自行用 Xcode 安裝，不處理 App Store、簽章替代方案或上架。保留離線練習、Part 1–7、錯題／間隔複習、自適應診斷、完整模考，以及真正跨手機的好友聊天與對戰目標。UI 保持簡潔易用，玻璃材質用在導航與控制區，正文須高可讀，支援 Reduce Transparency、VoiceOver 與 Dynamic Type。

先讀完以下檔案，再檢查目前程式；以下相對路徑均以專案根目錄為基準：

- `.planning/2026-10-28-integration-audit/audit-report.md`
- `README.md` 與 `.planning/2026-10-27-toeic-ios-complete-app/` 中的計畫、發現、進度
- `specs/content-contract-v1.md`
- `specs/validation-report-v1.md`
- `specs/mock-form-contract-v1.md`
- `specs/schema-change-request-mock-forms.md`（舊提案，用於辨識差異，不得優先於已確認的新規格）
- `reports/quota-and-quality-summary.md`、`reports/mock-assembly-and-pool-isolation.md`
- `handoff/2026-10-28/02-antigravity-next-round.md`（只讀對方責任，不替對方改資料）

稽核是 2026-10-28 快照，不應盲目假定目前仍相同。先核實並保留已修正的內容。目錄當時不是 Git repo；不要為了方便擅自初始化、重設或清除檔案。

## 2. 已驗證基線，不要破壞

- 32 個核心 XCTest 通過，但不代表 UI／實機驗收。
- 不修改 exports 的情況下，0001–0007 可透過實際 ContentVersionStore 合併為 51 題組、100 唯一小題；27 個聽力題組採 v2，3 圖片與 27 音檔可解析路徑。
- 重開恢復、重複匯入不增題；新增的 49 題 v2 是替換，不是新增獨立題。
- 目前 100 題全部 training／ai_checked；diagnostic、battle、mock 題庫均為 0，實際可用正式模考為 0 份。
- 完整 xcodebuild 最近因 destination 判定 iOS 26.2 平台不可用而 exit 70；不要把核心測試或 typecheck 說成完整 build 成功。

## 3. 分工與共用契約協作

你負責 Swift、App 測試、後端程式／部署說明、執行時驗證與整合回歸；Antigravity 負責題目、素材、產題腳本、題庫驗證與不可變匯出。

不得修改既有 `exports/batch-ag-*`、題目答案、review 紀錄或素材來讓自己的測試通過；不要改對方的 drafts/jobs/assets_work 或生產腳本。新 fixture 放測試專用位置、fixture=true，不進正式計數。

共用 Content Contract 1.0.0 的欄位與 enum 保持相容。模考附加契約目前仍需雙方接受，不可單方面宣稱已共同定案：

1. 你是這一輪 `specs/mock-form-contract-v1.md` 的唯一編輯方；Antigravity 只讀與提出差異。
2. 在 `handoff/2026-10-28/codex-contract-status.md` 記錄你接受的文件版本與真實 SHA-256、程式支援範圍、已跑測試、尚有歧義。
3. 讀取對方的 `antigravity-contract-status.md`；沒有檔案就標待回覆，不假裝取得同意，不反覆輪詢或停止全部獨立工作。
4. 若需改規格，先保存明確差異及相容策略；修改後更新 hash，舊的同意不自動適用。只有兩邊記錄接受同一 hash，才標 shared acceptance。
5. 檢查 required_batches 的相依圖，避免含自身 manifest hash 的循環封裝；給出可真正算出雜湊的包結構，例如先發布題目來源包，再發布引用它的組卷包。若現契約有歧義先澄清，不能填假 hash。

## 4. 第一優先：修正用途隔離與曝光紀錄

稽核位置：LearningEngines 的 DiagnosticRouter / DailyPlanner、AppModel.createLocalBattle、PracticeHomeView、SessionView。

統一資格判斷，且在真正選題、啟動 session、遠端請求邊界都防守，不只 UI 隱藏按鈕：

- 一般訓練／今日計畫只能取 training。
- 正式診斷只能取 diagnostic，禁止專用池為空就退回整個 bank。
- 對戰只能取 battle，禁止直接拿全部 Part 5 前十組。
- 正式模考只能使用通過版本解析的 mock form 與其精確題組版本。
- 錯題與解析入口也要遵守用途、作答狀態與解鎖政策；未提交模考不能經其他入口看到答案。
- 若缺專用題或 ready 素材，顯示具體不足並禁用正式開始。可保留明確標示的示範模式，但與正式紀錄、分數、排名分開；不能偷偷 fallback。
- 未知用途、未核准狀態、fixture 或缺素材不得自動當成正式可用內容。

補上跨 session、跨題目版本的曝光資料：使用穩定 group_id／family_id，展示題目即記曝光，而非只等答題完成。中途退出、重開 App、v1 升 v2 不能洗掉紀錄。若舊資料只有作答紀錄，遷移能確定的曝光，未知資料不可宣稱從未見過。

診斷優先使用未曝光的合格家族，避免以熟題記憶冒充能力。池不足時回報不足；若產品保留重測功能，另標已曝光，排除新題／標準初測證據。練習則應允許有意識的複習，不要把所有曝光題永久封鎖。

驗收至少包括：四池混合、空池、全 fixture、缺素材、全已曝光、退出未答、重啟、版本更新，以及模考題不能被 DailyPlanner 或普通 Part 頁選走。確認三個稽核重現案例修正，而不是只改測試預期。

## 5. 第二優先：讓單 Part 練習真正可用

PracticeHomeView 目前 first(where:) 固定選第一組。改成清楚的題組列表或可解釋的輪替流程，支援至少未練／可複習狀態與難度辨識。不要讓使用者只能反覆做第一題。

保持完整題組，不拆散 Part 3／4／6／7。連續一般練習能覆蓋可用 training 題組，耗盡後提示複習；返回與中途離開不得混用上一個 activeSession。題庫升版後歷史答案保留其原版本，不得拿新版答案重算舊紀錄。

加測試或可重現 UI 驗收步驟：同 Part 多次開始能選到不同未練家族；手動重練有標示；缺素材不計標準聽力；全部練過仍有合理複習入口。

## 6. 題庫整合與正式模考

把七批真實匯出加入可重複執行的回歸測試，不只五批：

- 7 批、51 組、100 唯一小題、27 聽力 v2、30 素材，Part 數量 3/13/18/15/15/8/28。
- 素材 ID namespace、路徑與 hash 正確；重開、重複匯入、較高版本更新、錯誤匯入回滾均有效。
- 同 ID 同版本不同內容拒絕；跨 group itemID、跨池 family 衝突拒絕。
- 將基線 immutable fixtures 與後續題庫增量測試分開，不因新增批次而把 100 寫死為整個未來題庫總數。

模考只接受共同確認的新版毫秒規格：group_refs 的精確 source batch／version、來源 manifest hash、200 唯一小題、100 聽力＋100 閱讀、Part 配額與 Part 7 配額、整卷音訊與時間軸引用、reading 4,500,000ms。不要硬套舊 93 題組常數；依既定組卷配額推導實際數量。

新增負向測試：缺來源包、版本錯誤、hash 錯誤、時間單位錯誤、缺音檔、重複／缺少 unlock、時間倒序／越界、素材錯置、未完成包啟用。保留正式模考不可用狀態直到真實 form 到位，禁止拿 training 湊 200 題假裝正式模考。

對最終 AAC／m4a 使用 iOS 解碼後時長與時間碼核對；ffprobe 對現有音檔觀察到約 102.5–140.5ms 容器差異，不直接視為已證實播放 bug，也不能忽略它宣稱毫秒精準。真實模考測試包括固定時間線、75 分鐘閱讀、背景／電話／耳機路由中斷、終止重開、答案導覽與交卷不復活。

## 7. 真正的跨手機好友與對戰

LocalBackendHub 是本機實作，固定開發驗證碼不是正式驗證。先保留它作測試替身，再讓 AppModel 依賴可替換協定／組合根，而非寫死 local client。

檢查現有 backend/migrations、服務契約與設定，優先延續既有方向。完成能獨立啟動、以網路請求存取的後端最小垂直流程，以及 Swift 網路 client：

- 真實驗證服務邊界、持久帳號與 session；未配置郵件提供者時固定碼僅限明確隔離的測試環境。
- 好友邀請／接受、封鎖／移除、私訊權限、訊息持久化、去重、分頁及重新連線補資料。
- 對戰邀請／接受／ready／開始／作答／結算；雙方同題同序同版；伺服器保存截止時間、冪等答案、斷線恢復與逾時結算。
- 正解、詳解、證據與鎖定逐字稿不得在對戰開始前送給競技客戶端；不可由 client 登錄自己想要的答案或勝負。製作交換包不是可直接公開的對戰 API payload。
- 伺服器必須能在兩個 client 都關閉後處理逾時，不能只靠進畫面時觸發掃描。
- 私有資料授權與帳號切換隔離；第三帳號不得存取別人的對話／對戰。

至少用兩個獨立 client 經實際網路連到服務端進行整合測試，不再用共用 actor 測試冒稱跨裝置。實體雙手機測試另列，不得用模擬通過代替。

缺部署目標、既有帳號／專案、郵件服務、憑證或付費資源時，列出最少必要選擇與安全設定方式，繼續完成本地 server/client 與測試。公開部署、建立付費資源、改正式資料庫前需使用者明確批准。不要要求把秘密貼進聊天，不擅自使用未知憑證或把秘密寫入 repo。推播／即時事件未完成就明列，不要用「後端完成」一詞涵蓋未實作部分。

## 8. 建置、實機、文件與交付

重跑並保存命令、exit code、環境與輸出：

```sh
env CLANG_MODULE_CACHE_PATH=/Users/ziii/Desktop/TOEIC_IOS_App/.swiftpm-build/module-cache swift test --scratch-path /Users/ziii/Desktop/TOEIC_IOS_App/.swiftpm-build
xcodebuild -project TOEICPath.xcodeproj -scheme TOEICPath -destination 'generic/platform=iOS' -derivedDataPath .build-device CODE_SIGNING_ALLOWED=NO build
```

若仍是平台元件問題，調查可安全執行的設定與 destination，不破壞 Xcode 安裝、不大量刪快取、不在無變化時一直重跑。需要下載元件／使用者操作時列精確需求。typecheck 可作補充，但 build 仍標未通過。

能實際操作裝置或模擬器時，驗收照片、音訊、逐句、1x／0.8x、重播、Part 1/2 提交前不可透過畫面或 VoiceOver 洩漏音訊文字、最大字級、Reduce Transparency、背景恢復。不能操作的項目列 not_run，提供步驟與預期結果，不能補寫 pass。

更新 README 與進度，移除「聽力 49 題仍缺素材」等過時敘述，保留尚未人工審題與校準的界線。不得宣稱官方認證、精準 TOEIC 分數或人人可得 990。

最終在 `handoff/2026-10-28/codex-delivery.md` 及回覆列出：

1. 修改檔案、每個稽核問題的處置及剩餘風險。
2. 測試命令／結果、原有／新增測試數、真實題庫整合結果。
3. build、UI、實機、跨 process 網路、雙手機驗收分別通過／失敗／未執行。
4. 實際支援的契約 hash、對方接受狀態及相依缺項。
5. 後端目前可執行到哪一層，部署／憑證／推播哪些尚缺。
6. Antigravity 下一個可交接包的要求，以及需要使用者做的最少操作。

先做 P0 用途隔離與 Part 選題，再做題庫回歸及契約，再完成後端與建置可做部分。不因一個外部阻礙停止所有工作，不因測試變綠就宣稱整個產品完成。不要自行向其他對話發訊息；用上述交接檔傳遞狀態。

讀取完本文件後，先回覆已讀到結尾標記、你的實際基線與本輪執行順序，然後開始實作，不必再問是否開始。

END-CODEX-HANDOFF-2026-10-28
