# 初步發現

雙方報告：Codex 稱 55 tests 通過，新增 HTTP/SQLite 獨立 process + Swift network client；Antigravity 新增 0008–0010，聲稱去重 177 題（training129/diagnostic24/battle24）。尚待本輪獨立驗證。

Codex 文件仍描述 100 題、專用池 0，落後於 Antigravity 的新包；新包是否可匯入／符合 runtime 資格須實測。

模考文件目前 Codex 接受 f8d3...650e，Antigravity 接受 0588...8f6f；尚未共享接受同一版本。

已重跑 55 個 XCTest，全部通過，包含兩個獨立 HTTP process/client 測試。完整 xcodebuild 仍 exit70，destination 階段失敗。Part 頁已改為題組選擇器，runtime 中央資格判斷移除跨池 fallback；十批真實資料待驗證。

待查的對戰風險：AppModel 仍從含 correctOptionID 的本機題庫供題；NetworkBackendClient 不送答案，但不等於客戶端沒有答案。服務端 ready 似未檢查傳入 assetChecksums，需確認。

重要實測失敗：真實十批順序匯入在 0008 第一行即被 Swift decoder 拒絕，缺 items[0].evidence[0].reasoning_zh。目前 177 題只是生產端資料數，不代表 App 可用 177。已調整診斷程式逐包捕獲錯誤，繼續檢查 0009/0010 與回滾。

讀檔 hash 檢查97筆全吻合；41音檔可解析、4圖片、跨池 family ID無衝突。完整性通過不等於schema／可匯入通過。

逐包實測：0008/0009/0010均拒絕，失敗原子回滾通過；成功啟用仍training100、其他池0。Draft202012Validator以現有schema獨立驗證，新三包269/212/210違規，全部55組77題受影響。生成器漏reasoning_zh，vocabulary/document等欄位不符；生產驗證器未全面遞迴schema檢查導致誤報pass。

新增本機HTTP探針重現：Alice participant=submitted後仍可POST第二題，HTTP200，最終200分含補答。來源local_server.py:428只查整場active，不查個人submitted。已交付audit-report.md。
