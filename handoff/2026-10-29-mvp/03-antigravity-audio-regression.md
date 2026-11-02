# 實機音質回歸：Part 1 顯微鏡照片

使用者回報：聲音混濁、畫面只有 ABCD 不知如何對應。Codex 接收端查得 ag-g-p1-000001 v2 的音訊沒有朗讀 A/B/C/D 標號，只有四句。音訊技術上可解碼並不代表聽感通過；本次實機音質記為 not_passed。

先保留先前工作與未發布產物，恢復 `02-antigravity-mvp.md` 尚未完成的修訂驗證任務，不從頭覆寫。新增音質優先項如下：

1. 核對這題原音檔與腳本；先交一個真正重新合成、清楚念出 A/B/C/D 加句子且停頓適當的候選。檢查其他 Part 1/2 是否有同樣標號缺漏，勿把 Part 2 題幹誤加選項標號。
2. 保留原 exports；新不可變批次保留 group/family/item 身份，依實際最新版提高 group version（接收端目前 v2，預期修為 v3），更新素材引用、時間碼、時長及 hash。通過完整 schema 與真正 App importer 才交付接收。
3. Codex 的比較候選位於 `/Users/ziii/Desktop/TOEIC_IOS_App/artifacts/audio-comparison/part1-research-laboratory/`，只是比較樣本，不是正式替代。不要只升採樣、提高編碼位元率或增益便宣稱改善；比較來源聲音、失真、清晰度與自然度。
4. 製作能讓使用者試聽的原音與候選比較，據實記錄 audio-only blind solve 是否做過。真人耳機聽審必須由真人完成；若沒有可用審閱者，交試聽包等待回饋，不能自填 human_reviewed。
5. 不擅自購買外部 TTS、要求或外傳金鑰；如本機語音品質不足，列出所需服務、費用、資料傳輸與授權選項供使用者決定。
6. 不改 Swift。Codex 已處理作答規則說明、逐字稿輔助條件、逐句標籤與 1× 不啟用 rate processing；素材修訂不可阻塞既有100題自動載入。交付完成時明示新包路徑，供 Codex 更新 seed，否則手機仍會播放舊音訊。

更新 antigravity-mvp-delivery.md，區分已修腳本、已產候選、已通過匯入、已人工試聽及已隨 App 出貨，不能以其中一項代表全部完成。
