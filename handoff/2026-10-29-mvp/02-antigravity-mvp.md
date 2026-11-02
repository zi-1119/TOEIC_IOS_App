# 給 Google Antigravity：修正交接，交付真正可進 App 的題庫

2026-10-30協調補充：使用者已要求自動協調到簡單測驗MVP。恢復工作時也請完整讀同目錄 `04-mvp-coordination.md` 與 `03-antigravity-audio-regression.md`；先修不可匯入的新包，再處理小樣本音質，保留原包與人工驗收界線。

## 現況與工作範圍

使用者已在 iPhone 打開 App，但沒有可直接使用的完整內容。這輪先讓離線練習可用，再解鎖專用診斷／對戰／模考。你負責題庫、素材、生成器、驗證器與交付報告，不修改 Swift App、簽章、後端或單方面更動共同交換契約。

工作區 /Users/ziii/Desktop/TOEIC_IOS_App。請完整讀 `.planning/2026-10-29-integration-audit/audit-report.md` 和本文件，再實作修復，不只是回計畫。Codex 同步負責自動內建／啟用原 0001–0007 的 100 題 training。不要把這些已驗收發布包覆寫；你修新包不應阻塞這 100 題的上機練習。

## P0：先修 0008、0009、0010，不再複製格式錯誤

實際 App importer 三批各自在 groups.jsonl 第一行失敗：evidence 缺 reasoning_zh。完整 JSON Schema 檢查又發現 vocabulary 欄位與型別、document 欄位、distractor_notes 額外 trap_type、provenance 額外 prompt_hash 等錯誤。三批合計 55 題組／77 題；691 是欄位違規數，不是題數。現有生產驗證 structure-001 的 pass 是假陽性，必須修正，而非要求 App 放寬契約。

1. 依磁碟上已接受的 content contract、group.schema.json 及相關正式 schema，修生成器。對所有巢狀物件使用完整 JSON Schema 驗證，不只比頂層 keys。驗證失敗必須阻止發布／打包成功狀態。
2. 為上述每種錯誤加負向測試；確認額外欄位、缺必填、錯型別、錯 enum、壞引用、壞 hash、重複 ID、跨用途 family 等能被拒絕。重新驗證既有全部批次，歷史報告誤判須在修訂交付報告明確更正。
3. evidence.reasoning_zh 寫真正的證據推理；vocabulary 使用契約欄位 term_en/meaning_zh/example_en 等，例句有意義；document 使用 document_id/genre。不能以空字串、無關例句或「待補」通過檢查，不能憑空捏造文章證據。
4. 按不可變發布規則產生修訂包：保留原發布包，保留題目與 family 身份，正確升版／新發布批次識別並記錄替代關係；修訂不算新增題。由 manifest 明列新包精確路徑與版本，不能悄悄覆寫 exports 原內容。
5. 交付前須通過完整 schema、引用/素材/hash/用途池檢查，再通過真正 Swift importer 接收測試。不要以 Python validation.json 的 pass 當成 App 已接收。可使用既有稽核探針作為參考並與 Codex 接收結果核對，不與它同時編輯 App 原始碼。

## P0：協助 seed 上機，不重新堆量

提供 `handoff/2026-10-29-mvp/antigravity-seed-index.md`，記錄原 0001–0007 的精確 manifest 路徑、版本、SHA-256、各 Part 小題數、音圖數量、品質狀態與已知限制，供 Codex 選入 App resource。這是交接文件，不是擅自新增交換 schema。

音訊需要實際檢查是否有聲、台詞對應、音量、截斷、停頓、說話者與題序一致；檔案能解析不代表內容正確。圖片要清晰、對應題目。區分「腳本文字盲解」「純聽音盲解」「真人審核」；沒有做過就寫未做，不能自報 human_reviewed。已有基線發現語意或素材缺陷時依修訂流程處理並通知 Codex，不悄悄改包。

## P1：依功能門檻補專用內容

修訂 77 題先被 App 真正接受後，才繼續擴量。當前候選是 training129、diagnostic24、battle24、mock0；成功啟用仍只有 training100。報告分開「生成」「完整驗證」「App 接收」「人工審核」「校準」，不能混成同一可用數。

- 診斷：先交合規的專用 seed，再依 Codex 真實診斷路由需求擴為至少 40–60 題的可測集合，完整保留題組，涵蓋聽讀／各 Part／難度範圍。這是早期功能測試規模，不代表足以精準估分；難度先標編輯估計，不能冒稱心理計量校準。
- 對戰：修好的專用 24 題先供後端建立私人 catalog，與 Codex 確認不含答案的競技 payload 由哪端投影。正解/解析不能提前包進競技客戶端。保持 family 與 training/diagnostic/mock 分離。
- 完整模考：先讀實際 `specs/mock-form-contract-v1.md`，與 Codex 確認同一 SHA-256 再生產。先做一份真實完整 200 題候選卷：Part 1–7 分別 6/25/39/30/30/16/54，題組完整、素材齊全、整卷聽力音訊與時間線、來源／引用／版本可追蹤。依實際契約驗收 P7 組成等細節；不要只交藍圖或兩題範例就報完整卷完成。
- 正式模考的人工審核及整卷音訊門檻必須真的通過。候選卷能進開發預覽不等於正式可用，不能擅自改狀態解鎖。人工工作若需使用者參與，交具體抽審檔與待決項，不偽造審核。

## 交付

更新 `handoff/2026-10-29-mvp/antigravity-mvp-delivery.md`，提供：修正檔案、負向測試結果、全部驗證結果、修訂包精確路徑與替代關係、App importer 真實結果、各池實際有效數、媒體審查方法與未做部分、與 Codex 接受的同一契約 hash。

先交 P0 可接收修訂包與 seed index，再持續 P1。不要把 4800 題當作本輪先決條件，也不要把未通過接收的題數算成使用者手機上能練習的題數。
