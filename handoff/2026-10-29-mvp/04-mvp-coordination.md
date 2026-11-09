# 自動協調到 MVP — 2026-10-30

## 2026-11-09 恢復工作（優先於下列歷史狀態）

**11:35補充**：下段build路徑疑問已結案：Codex僅將DerivedData搬至/tmp/toeic-audio-preview-derived.qMkazm/，交付已補記；協調者獨立比對device及simulator兩份.app各10音檔皆一致。不要重複追問或重建。

**11:34接收更新**：Codex試聽入口已交付，見codex-audio-preview-delivery.md。協調者讀實作並獨立跑AudioPreviewCatalogTests 3/3通過（含10音檔來源逐位元與SHA比對），檢查78/78及雙平台BUILD SUCCEEDED日誌；SeedContent/exports/原試聽包無diff。手機入口為「我的」頁的「題庫與下載」區段→「音質試聽」，可重新Run裝機驗收。不是正式換音，仍100題。此次沒有重新跑全套build/模擬器，UI證據來自Codex交付。日誌所列本輪兩個build目錄目前不存在，已詢問Codex是否收尾清理及補記，不據此假稱本輪獨立比對built app。AG readiness報告已出現，待UI確認完成及接收；其新增check_audio_promotion_readiness.py會寫JSON，不是嚴格唯讀，且ffprobe format.duration被標成decoded，下一輪需校正說明/欄名，非手機試聽阻擋。不要重派A/B功能或正式換音；等待真人短清單回饋。

使用者明確要求「繼續指揮antigravity還有codex」，解除先前暫停。既有 GitHub 公開備份為 main 的 0a6b939；本輪不自動 commit/push，不更動簽章或帳號。恢復原30分鐘協調排程，尚未取得新的真人驗收。

- Codex：新增極簡離線「音質試聽」入口，原樣使用 assets_work/audio-listening-pack-2026-10-31/ 的既有5組A/B共10音檔。原音/新版候選可切換，禁止同時播放，離開停止；在既有次要入口放置，不干擾一鍵測驗。資源與正式SeedContent分離，不替換正式音訊、不改題數/用途池/分數。App、測試、Xcode資源由Codex獨占。交付 handoff/2026-10-29-mvp/codex-audio-preview-delivery.md，含實際build/測試與手機路徑。
- Antigravity：不重做已完成標號解析修正或100題盲解。先同步接收事實：0011–0015已通過真實接收端，合併177唯一題（129 training/24 diagnostic/24 battle），手機仍內建100題。整理現有換音所需16組Part1/2的版本、素材引用與待驗門檻，輸出 reports/audio-promotion-readiness-2026-11-09.md；只建立交付對照與檢查，不產音、不發布換音。更新自己交付報告過時欄位。僅可寫自己reports/handoff，不改Swift/SeedContent/既有exports/試聽包/協調記錄。
- 根協調者只寫04與協調planning，實際派送後記錄送達。舊標號解析修正6測試、10音檔hash及題庫接收均已完成，不再重派。待新交付才做針對性驗證；音質仍需使用者iPhone喇叭接受。好友、正式模考、4800題暫不擴張。


使用者明確授權本協調對話自動指揮原 Codex 與 Antigravity 對話直到 MVP。這是協調、實作與驗收授權，不是購買、公開部署、改帳號權限、偽造人工驗收或刪資料的授權。

## 第一階段退出條件：簡單離線測驗 MVP

- 首頁一鍵開始約10題，可選閱讀/聽力/混合；題目、選項、下一題、交卷操作清楚。
- 交卷後成績、逐題解析、錯題與重啟保存正常；完整題組、不重複填滿、不跨用途池、不虛構990分。
- 新裝與既有空殼升級自動載入合規題庫及圖片/音訊；更新冪等、不降級、不遺失資料。
- 新77題的格式問題以不可變修訂包修復，真正通過接收端 importer；不以檔案存在或producer自報通過當交付。
- 聽力素材清楚、Part1/2標號對應正確；先小樣本試聽通過再擴大。Karen+A–D方向已獲偏好，約400ms標號間隔候選仍待實機確認，不假定已接受。沒有真人確認就保留待驗。
- 核心測試、完整iOS build、代表性模擬器操作、大字級檢查有實際結果；真機與聽感回饋需要使用者，不能用build代替。
- 無阻擋基本測驗的已知重大缺陷。完成可自動驗證工作後，集中提供一次短真機驗收清單；未獲驗收前只稱候選MVP。

好友聊天/跨手機對戰、校準診斷、完整200題模考及4800題長期規劃保留，不納入本次「簡單測驗」第一階段完成宣稱。不得以此擅自刪除既有功能。這些功能另列未完成與所需外部部署/人工輸入。

## 負責範圍與當前任務

Codex 原對話 `01a17ce9-8a33-7820-93ff-2a12030dc960`（local）負責App/後端/接收測試/SeedContent。先讀 codex-simple-test-delivery.md 與 .planning/2026-10-30-simple-test-verification/；本協調對話已完成72測試、iOS與Simulator build、兩輪UI驗證並修正完成關閉及blank代碼呈現。保留現有修改，勿重做。接續最大字級/長文章/聽力與混合測驗、交卷保存、錯題回顧、素材更新接收；修確切缺陷後交可Run版本，不擴充不必要畫面。

Antigravity 原題庫對話 `4040d36a-0930-4363-9a2c-a7935fcaaf56`，TOEIC_IOS_App專案，負責scripts/題庫/音圖/不可變exports。先完成02-antigravity-mvp.md的0008–0010修訂，接著03-antigravity-audio-regression.md；音訊最新候選為 artifacts/audio-comparison/part1-research-laboratory/candidate-karen-labels-400ms-gap.m4a，非正式已驗收包。不改Swift/簽章/共同契約，先產候選和真實驗證，不自行假造human_reviewed。

協調者：先讀狀態和實際檔案，分工派送；正在工作時不重複派同一任務，不與Codex同時寫App或與AG同時改生成器。產物有變動才跑對應驗證；記錄已派送/已接收/已驗證，不以空等待宣告失敗。遇配額或網路可有限重試，連續同錯不頻繁重試/換模型/買額度。保留未經授權的新草稿；原manifest.json附件已於10/31 01:27經使用者明確確認後連同接續指令送出，不再是阻礙。

## 節奏、證據與停止

### 2026-10-31 最新協調狀態

**最新接收結果**：Codex產音標號小修正已交付至codex-audio-label-fix.md，協調者獨立執行6項專屬單元測試0失敗、10個試聽音檔hash與原manifest相同，確認共同合成路徑使用修正。此項已完成，不要再派AG或Codex重做，也不代表新手機音訊已上線。現在等待使用者iPhone試聽及App實機回饋；未回覆前不發布換音、不更新SeedContent、不冒稱真人驗收，不重複催驗。

**18:35責任更新**：AG的18:09小修正任務於15秒後quota失敗；原對話UI現已閒置，明示2026/11/7 01:27:05（台灣）恢復。保留使用者模型，不買額度、不Retry未恢復配額。標號解析小修正暫轉交Codex：僅scripts/synthesize_listening_audio.py、專屬回歸測試及獨立交付記錄；禁止覆寫exports/試聽包/SeedContent，不擴張題庫、不重跑已過App建置。此項取代18:10的AG獨占安排，完成前不要重啟AG同項工作。其餘內容製作仍維持原分工，真人試聽尚待回覆。

**18:10最新狀態（優先於下列歷史紀錄）**：Codex已完成App候選交付，75測試與完整iOS/Simulator build、Part6最大字級均通過，cursor :22 idle。0011–0015真實接收與協調者獨立回歸已通過177唯一題（129/24/24），未內建，手機仍100題。AG已交付antigravity-mvp-delivery.md及5題A/B試聽包；協調者驗10音檔SHA256與時間碼均通過，未替代人工聽審。18:09已在AG原對話送出scripts/synthesize_listening_audio.py標號解析缺陷修正與測試任務，UI顯示Working；AG獨占該修正，Codex不重做。不得重製已交使用者的試聽檔或覆寫exports。下一步接收該小修正並等待使用者iPhone喇叭5題試聽，通過後才發布不可變換音版本、派Codex更新SeedContent。真人App/音質/VoiceOver仍待驗，排程保留，無變化不催促。

- 使用者已自行切換 Antigravity 到 Opus 5.5 並要求繼續；UI 確認目前為 Claude Opus 5.5 Medium。這是使用者指定的變更，不得再按舊 quota 訊息推斷仍不能使用此模型，也不得自行換其他模型或啟用 Overages。
- 10/31 01:27 使用者回覆「可以，一起送出並繼續」，協調者已在原對話送出 manifest.json 及接續指令，UI 顯示新的 User message（含附件）、Working、Stop execution，輸入框清空。AG 已恢復執行，不要再次送同一單。尚未交付新成果，不代表驗收完成。
- Codex 已收到續作與分工更新：負責 App/UI/接收端驗證；撤回先前 AG 配額中斷時的題庫修訂 fallback 寫入權，避免與 AG 復工衝突。
- 新修訂 exports/batch-ag-0011、0012、0013 已存在，協調者獨立 schema 與 manifest SHA256 檢查通過（29/24/24 題），真正 Swift importer 驗收仍待 Codex。不能直接宣稱新增77題已可用。
- 13:45更新：Codex已交付0011–0013實際importer回歸通過（合併177唯一題，training129/diagnostic24/battle24），仍未內建；Xcode Run仍100題。最新codex-simple-test-delivery.md記錄75測試、iOS/Simulator完整build成功及UI矩陣，已有簡單測驗候選版可測。Codex仍在處理0014/0015的10題v3引用修訂驗收，勿重派；音訊候選與實體iPhone仍未驗收。AG UI目前Mac鎖定不可讀，已通知使用者，保持退避且勿推測AG執行狀態。

約每30分鐘檢查一次：使用Codex wait_threads快照；AG用可用UI/交付檔驗證，不能把改檔當作對方收到。通知只在有可測版本、實質故障或需要人決定時發出；無變化不重複催促。

將最新狀態、已派送任務及阻礙記到 .planning/2026-10-30-mvp-coordination/。若全部自動項目通過且使用者驗收完成，停用此協調排程並交付總結；若只剩人工試聽/帳號或付費批准，明示等待誰、要做什麼，避免無限重做或自行代替批准。不可將尚未完成的好友/模考稱為完整產品完成。
