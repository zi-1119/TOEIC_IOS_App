# 給 Google Antigravity：題庫品質補驗、模考對齊與分階段擴充

請接續既有題庫工作，不重新產一套、不覆寫已交付批次。本輪先修正交付與驗收缺口，再依關卡擴充，不能用題目數量取代品質證據。

## 1. 專案與必讀資料

專案根目錄：`/Users/ziii/Desktop/TOEIC_IOS_App`。若你的工作區實際不同，先確認能讀到下列完整檔案；不得假定同名就是同版本，缺檔請明確列出，不自行猜交換欄位。

以下相對路徑以專案根目錄為基準，請讀完：

- `.planning/2026-10-28-integration-audit/audit-report.md`
- `specs/content-contract-v1.md`
- `specs/validation-report-v1.md` 與現有 JSON Schema
- `specs/antigravity-task-instructions.md`
- `specs/mock-form-contract-v1.md`
- `specs/schema-change-request-mock-forms.md`（舊提案，不作為新版的替代）
- `reports/quota-and-quality-summary.md`、`reports/REVIEW_QUEUE.md`、`reports/mock-assembly-and-pool-isolation.md`
- `PROGRESS.md` 與現有 jobs、global-index
- `handoff/2026-10-28/01-codex-next-round.md`（只讀以了解對方需求）

這份指令補充先前任務；Content Contract 欄位與配額不因新指令自動變更。題目／音訊稿英文，說明與交付繁體中文。產品以挑戰高分為目標，不保證提分、精準預測分數或人人 990。

## 2. 已知基線與責任邊界

2026-10-28 獨立稽核已確認：

- exports 0001–0007 可由 App 真實核心匯入，按最新 group 版本合併後為 51 題組、100 唯一小題。
- 全部 pool=training、content_status=ai_checked；真人審核 0，實測難度校準 0。
- Part 題數 3/13/18/15/15/8/28，D1–D5 標註 8/17/26/33/16，後者是 editorial 而非心理計量難度。
- 0006／0007 為既有 49 聽力小題的 v2 更新，不算新增 49 題；素材已補成 3 圖片、27 音檔。
- 67 個 manifest 檔案 hash 吻合，27 個音檔能解析，但尚未等同逐檔聽審或人工內容驗收。
- 目前 diagnostic、battle、mock 專用題庫為 0，正式模考卷為 0。

先自行核實最新狀態，避免覆蓋後來已修正的工作。你負責 blueprints/jobs/drafts/review/assets_work/exports、題庫報告與產題腳本，不修改 Swift、App 測試、Xcode 專案、後端程式或部署。

既有 0001–0007 必須保持不可變。任何題幹、答案、素材、review 或 metadata 修正都用新唯一 batch_id；相同題組保留 group_id/item_id/family_id，增加 group.version，說明原因並重審。新題才用新永久 ID。先查 jobs/index/exports 防止撞到他人已使用的 0008 等編號。

## 3. 第一關：對齊模考附加契約

你目前的 mock-assembly-and-pool-isolation.md 還引用舊 proposed 秒數欄位，與 App baseline 的毫秒、group_refs、required_batches 及事件時間軸不同。先修文件與生成／驗證流程的落差，不可把文字計畫稱為已交付模考。

協作方式：

1. 本輪 Codex 是 `specs/mock-form-contract-v1.md` 的唯一編輯方；你只讀、提出差異，不同時改共用檔。
2. 在 `handoff/2026-10-28/antigravity-contract-status.md` 記錄讀到的版本與真實 SHA-256、逐項支援狀態、接受／待澄清及原因。
3. 讀 `codex-contract-status.md`。沒有就列 pending，繼續做首批品質與不受影響的素材，不假裝接受已完成，也不反覆輪詢。
4. 雙方記錄接受同一文件 hash 才視為共享基線；任何修改都要重新核對。來源包與組卷包的 manifest 依賴不能自我引用成為不可計算的循環 hash。
5. 若 spec 本身有衝突，用明確例子提出，不自己發明 enum、改時間單位或塞填充值。

修正組卷算術：你目前列的配額為聽力 6+25+13+10=54 組，閱讀 30+4+10+5=49 組，合計 **103 組**，不是 93／39。這是依你目前配額的結果，不代表所有合法卷都必須硬編碼相同總組數；生成器要由實際完整題組推導並檢查。

若要聲稱符合當前正式 TOEIC 題型或特定配置，核對可公開存取的 ETS 官方格式／樣題說明並保存來源及核對日期；只參考結構，不複製試題。無法驗證時明列限制，不把專案自訂數值說成官方規定。

## 4. 第二關：把現有 100 題做成可追溯的品質候選集

逐題核對，不只跑 schema：

- 唯一正解、英文自然、題意完整；每個干擾選項有具體錯誤原因。
- 答案證據必須指向真實文章、音訊段落、照片或題幹，不能為填欄位捏造來源。
- Part 2 間接回應不可兩項都合理；Part 3/4 題目需由所聽資訊支持；Part 6 插句考篇章邏輯；Part 7 多篇題確實有需跨文件整合者。
- D4/D5 以改寫、條件、推論、角色／時間關係及整合提升難度，不靠冷僻專業知識、病句、漏資訊或兩可答案。
- 同 family 的表面換名／換日期不能當新獨立題；檢查正解位置與形式線索，但不要只為均衡 A/B/C/D 犧牲自然性。
- 素材與文字一致：照片可見證據支撐選項；音檔真的朗讀對應 script，說話者區分、停頓、語速、數字／縮寫／專名發音合理。

盲解誠信：保存不含答案／詳解／證據提示的輸入、獨立解題輸出、實際可取得的工具／模型／時間紀錄，再做比較。若無法隔離上下文就 blind=false；不知道模型名稱就寫 unknown，不補造。舊盲解檔與答案一致不等於本輪重新完成盲解。

文字／逐字稿解題與「聽實際音檔後解題」分開記錄。Part 1 真實圖片判題與 image brief 判題分開。不能因音檔合成成功或有 hash 就說已聽審。若修改實質內容或素材，須對相應新版重驗，不能直接複製舊 pass 紀錄。

你可以做 AI 編輯審查、獨立解題、技術音圖檢查，但不能代填真人審閱。建立給使用者／合格英文審閱者的可操作審閱包：題目、素材路徑、審閱清單、疑點與回覆欄位。優先抽樣涵蓋所有 Parts、D1–D5、全部 3 張照片、各語音／角色組合、全部被標疑義與高難度題；記錄樣本實數，抽審不可改稱全量人工審查。

若暫無真人，保留 human_reviewed=0／pending，可繼續做 AI 候選包與不依賴人工的工作。不能一方面要求真人卻自己將這個門檻打勾，也不要因此讓全部生產停擺。

## 5. 音訊時長與品質的技術補驗

稽核發現目前最終 m4a 的 ffprobe 容器時長比 metadata 多約 102.5–140.5ms，synthesize_listening_audio.py 以轉碼前 PCM frames 產生時間碼與時長。這可能涉及 AAC padding，尚未證明 iOS 實際播放錯誤。

請查明並交付：

- 轉碼前 PCM 時間、最終檔案 container／stream 時間與 encoder delay／padding（能讀取者）的對照。
- 27 音檔逐段引用、範圍、單調性與實際聲音對齊的技術檢查；無法聽或分析者標 not_run。
- 與 Codex 交接 iOS AVFoundation 實際解碼核對需求。不得直接把全體時間碼平移固定數值，或宣稱 ffprobe 時間必等於 AVPlayer 可聽時間。
- 有證據才修 metadata／音檔；有修改就新版本新批次，不能重寫已匯出檔。
- 聲音來源與實際 locale 誠實登錄；ca 使用美式／北美替代的限制保留，不因想符合規格就把檔案標成已驗證加拿大口音。

正式模考使用最終整卷音訊的真實播放時長與時間軸。不能拿 estimated_time 相加、強填 45 分鐘或用大量空白湊長度。

## 6. 分階段擴充與計數

長期目標仍是 4,800 個去重小題：training 3,000、battle 600、diagnostic 400、mock 800。遵守原 Part×pool 表與完整題組，fixture 不計數、版本修訂不計新增、草稿不計合格交付。

本輪依以下順序推進，完成一關留下證據再進下一關：

### A. 先修正／補驗現有 100 題

交付品質差異、必要修訂包、真實剩餘審閱項目與 updated index。保留未變更的既有批次。若有答案不唯一／缺證據，先排除或修訂，不能為維持 100 數字讓它通過。

### B. 技術流程穩定後擴至累計 400 題 training 候選

先核對原 blueprint；目前預定各 Part 累計數 12/50/78/60/60/32/108，共 400。這 400 已包含合格的原 100，不是再加 400，也不是把兩版各算一次。

每批約 20–30 小題或 5–10 個長題組，保存 blueprint、草稿、審查、失敗／修訂與封裝證據。高難度題保留，但需合理理由。真人尚未審核時只能稱 ai_checked 候選包，不宣稱正式品質完工。

### C. 開始獨立用途池的可驗收交付

用原配額與現有 blueprint 規劃 diagnostic／battle 的首批，明列數量、Parts、能力、家族及 ready 素材。不得把 training 題或同 family 改標 pool。這些新增題計入各自 400／600 長期配額，不追加總量。

契約兩邊接受後，先產出第一份獨立 mock 200 題與整卷音訊，由 App 實際匯入與播放驗收後，再擴四卷。若契約仍待對齊，可先準備原創 mock 草稿／素材，但不把未定稿 wire 格式輸出為已可用正式卷。

不要在品質、格式或媒體失敗未處理時一口氣衝到 4,800；也不要在完成一次小批後把整個長期目標標完成。對人的審閱與外部工具限制分開列，不補造成功。

## 7. 第一份模考的必要交付

- 獨立 mock family，與 training／diagnostic／battle 及其他卷不重疊。
- 200 唯一小題，Part 數 6/25/39/30/30/16/54；100 聽力與 100 閱讀；Part 7 單篇 29、多篇 25，保留完整題組。
- 正確版本的 `reports/mock-forms.json`；精確 group/source/version 參照、固定題序、正確 required batch manifest hash。
- 單一整卷 ready 音訊，包括需要的指示、題號、題目、Part 1/2 選項、自然過場與作答停頓；圖片及其他必需素材完整。
- 毫秒級 timeline events、unlock、作答窗與音檔相符；閱讀時限 4,500,000ms。
- 組卷描述與每個音訊檔都按契約登錄 manifest；來源相依可實際解析。
- 缺素材、待審或未驗證項目據實標示。即使格式 pass，也不宣稱 iOS 已實播或真人已校準，除非取得相應實際證據。

## 8. 封裝、報告與交接

維持驗證報告／manifest 的正確封裝順序，避免 self-hash 循環。不可為追求全綠，把未跑的檢查改 pass。包內報告若因最終 manifest 尚待外部驗證而 incomplete，依既有契約提供包外 post-package verification，不任意修改已封裝檔案。

新增或更新：

- 本輪逐題品質結果與修訂 changelog。
- 音圖檢查矩陣，區分結構、解碼、實際聽審／看圖、人工與 AI。
- 配額與品質摘要：唯一題數、各 Part/pool、editorial difficulty、ready 素材、ai_checked/human_reviewed、待修／淘汰／未發布分開統計。
- mock 契約對齊紀錄與正確組卷算術。
- 人工審閱包與待辦，不偽造 reviewer。
- `handoff/2026-10-28/antigravity-delivery.md`：實際匯出批次、manifest SHA-256、依賴與匯入順序、取代哪些 group/version、淨新增題數、驗證命令與結果、App 尚需驗收事項。

若 Codex 的接收回報尚未出現，標示 producer validated／receiver pending；只有實際取得 App 接收測試證據才標 receiver passed。不要修改 App 文件來假裝對方已驗收，也不要自行向其他對話發訊息。

缺語音／圖片工具、額度或人工時，列出具體缺項與替代工作；不得未經同意購買、繞過額度、抄付費題庫或現成試題。外部官方資料只能研究格式與合理難度，題目必須原創或有明確授權。

最終回覆分開列：本輪已完成、實際驗證、未執行、需真人／工具／Codex 才能驗收、下一個可交接包。不用「全部完成」掩蓋仍是候選、草稿或 planned 的內容。

讀完後先回覆已讀到結尾標記、核實後的基線與執行順序，接著開始你的工作，不必再問是否開始。

END-ANTIGRAVITY-HANDOFF-2026-10-28
