# 初步發現

- 32 個 Swift 核心 XCTest 於本輪重跑通過，0 failures。這不涵蓋 SwiftUI 實機操作。
- 既有真實題庫測試只載入 0001–0005，尚未涵蓋補素材的 0006–0007。
- Antigravity 報告稱 100 唯一小題、51 題組、3 圖片及 27 音檔；待獨立匯入驗證。
- AppModel 依賴 LocalBackendClient / LocalBackendHub；Hub 保存至本機 state.json，並非跨裝置服務。
- 目前無正式模考內容；題庫均為 training。README 的缺素材描述尚未同步最新 v2 匯出。
- 盲解有移除答案的輸入腳本及獨立結果檔，不能僅憑紀錄宣稱已驗證模型完整獨立上下文；未經人工校審／實測難度校準。

## 本輪七批整合驗證

- 使用 SwiftPM 已編譯的真實 App 核心模組，另建獨立 CLI 稽核程式，未改動原有測試或產品檔案。
- 0001–0007 全部成功安裝；最終 7 啟用批次、51 題組、100 唯一小題、30 個真實素材路徑，0 正式模考卷。
- 27 個聽力題組均採用 v2；Part 1 圖片引用可解析。重開恢復與重複匯入 0007 均通過，不增為 149 題。
- 各 Part 小題數：3 / 13 / 18 / 15 / 15 / 8 / 28。
- 新發現：PracticeHomeView 的單 Part 入口固定選第一個完整題組，非題組清單或輪替；AppModel.createLocalBattle 取前 10 個 Part 5，未篩 battle pool；DiagnosticRouter 在無 diagnostic pool 時回退全部題庫。需繼續確認影響。
- 模考契約未同步：Antigravity 報告仍引用舊 proposed 秒數欄位；App baseline 使用毫秒 timeline 與精確 group_refs。缺少雙方接受與真實試卷驗收。

- 獨立探針已重現用途池問題：DiagnosticRouter 取到 training `ag-g-p2-000002`，DailyPlanner 對 mock-only 輸入返回 1 組（應為 0）。
- Antigravity 模考報告的 93 題組總數與自身配額不符：54 聽力 + 49 閱讀 = 103。
- 67 manifest 檔案雜湊全吻合；27 m4a 可解析且時間碼引用完整。容器長度差異 102.5–140.5 ms，需以實際 iOS 解碼核對，不直接視為單題音訊驗收失敗。
- 狀態 ai_checked=100 / human_reviewed=0；D1–D5=8/17/26/33/16；專用 diagnostic/battle/mock 池均為 0。
