# Antigravity P0 內建種子題庫索引（`antigravity-seed-index.md`）

- **產出時間（Asia/Taipei）**：`2026-10-29T22:41:00+08:00`
- **對應任務**：`handoff/2026-10-29-mvp/02-antigravity-mvp.md`（P0：協助 seed 上機，提供原 `0001–0007` 合格 100 題之精確索引供 Codex 選入 App Resource 自動內建與啟用）
- **不可變承諾**：`exports/batch-ag-0001` 至 `exports/batch-ag-0007` 自發布以來未曾被覆寫或修改，所有檔案與 `manifest.json` SHA-256 與歷史驗收完全一致，且已通過：
  1. 完整 JSON Schema 巢狀驗證（`group.schema.json`、`review.schema.json`、`manifest.schema.json`、`validation-report.schema.json` 全數 **0 errors**）；
  2. 真實 Swift `ContentVersionStore.install(from:)` 累積安裝與重開驗證（51 唯一題組、100 唯一小題、30 實體音圖資產）。

---

## 一、`batch-ag-0001` 至 `batch-ag-0007` 精確 Manifest 路徑、版本、SHA-256 與題數表

| Batch ID | 相對 Manifest 路徑 | 題組版本 | 用途池 (`pool`) | 題組數 | 小題數 | 各 Part 小題分布 | Ready 圖片 / 音檔 | Planned 素材 | `manifest.json` SHA-256 | 合併後角色說明 |
|---|---|---|---|---:|---:|---|---|---|---|---|
| `batch-ag-0001` | `exports/batch-ag-0001/manifest.json` | `v1` | `training` | 20 | 20 | P2: 8, P5: 12 | 0 / 0 | 8 (P2音檔) | `33cdbceab178bdbd34e52b90f223d9f208330a741c3c62e0dce092bd5a829582` | 提供 **12 組 P5 閱讀題**；8 組 P2 聽力由 `0006`/`0007` (`v2`) 取代 |
| `batch-ag-0002` | `exports/batch-ag-0002/manifest.json` | `v1` | `training` | 13 | 19 | P1: 3, P2: 5, P5: 3, P6: 8 (2組) | 0 / 0 | 11 (3圖+8音) | `803a20cbb72328b9d80e4d42ff57b7a124fe7910aa55b87ac090716599aebb2d` | 提供 **3 組 P5 + 2 組 P6 (共11題閱讀)**；P1/P2 聽力由 `0006`/`0007` (`v2`) 取代 |
| `batch-ag-0003` | `exports/batch-ag-0003/manifest.json` | `v1` | `training` | 6 | 18 | P3: 18 (6組) | 0 / 0 | 6 (P3音檔) | `63c998c7b22c6085790b3ae9297e607b86b298611e27e9182e20cb3ff50cccea` | 全部 6 組 P3 均由 `0006`/`0007` (`v2`) 取代 |
| `batch-ag-0004` | `exports/batch-ag-0004/manifest.json` | `v1` | `training` | 5 | 15 | P4: 15 (5組) | 0 / 0 | 5 (P4音檔) | `d14648fc40de3cd818d7f1ae5fbd9f18428ef944757c7913ccedff73f2445769` | 全部 5 組 P4 均由 `0006`/`0007` (`v2`) 取代 |
| `batch-ag-0005` | `exports/batch-ag-0005/manifest.json` | `v1` | `training` | 7 | 28 | P7: 28 (單篇4組13題 + 雙篇2組10題 + 三篇1組5題) | 0 / 0 | 0 | `b30084117255155390113215ee5926d5805fd3b2e9237fa95333e3da28e1031e` | 提供 **7 組 P7 (28題閱讀)**，無外部媒體依賴 |
| `batch-ag-0006` | `exports/batch-ag-0006/manifest.json` | `v2` | `training` | 4 | 8 | P1: 1, P2: 1, P3: 3 (1組), P4: 3 (1組) | **1 圖 / 4 音檔** | 0 | `fcfac99c0976f6494e764f68813652cea7b686888bb39a2e1589d4b060c85a96` | 取代 `ag-g-p1/p2/p3/p4-000001` 之 `v1`，提供 **4 組 8 題完整就緒聽力** |
| `batch-ag-0007` | `exports/batch-ag-0007/manifest.json` | `v2` | `training` | 23 | 41 | P1: 2, P2: 12, P3: 15 (5組), P4: 12 (4組) | **2 圖 / 23 音檔** | 0 | `72392de96d92ead8f8695873064ce42aabe425c5cecfbe6839b05ca1fdf9f317` | 取代其餘 23 組聽力之 `v1`，提供 **23 組 41 題完整就緒聽力** |

---

## 二、七包累積合併後（Active Catalog）各 Part 有效題組、小題與媒體統計

當 `ContentVersionStore` 依序安裝 `batch-ag-0001` 至 `batch-ag-0007`（或安裝 `0001`, `0002`, `0005`, `0006`, `0007`）並依最高 `version` 合併後，離線可練習之有效 `training` 題庫如下：

| Part | Layout | 生效來源批次 (版本) | 唯一題組數 | 唯一小題數 | 實體圖片數 (`ready`) | 實體音檔數 (`ready`) | Planned 缺項數 |
|---|---|---|---:|---:|---:|---:|---:|
| **Part 1** | `photo` | `0006` (`v2` × 1) + `0007` (`v2` × 2) | **3 組** | **3 題** | **3 張** (`1200×896` JPEG) | **3 個** (`.m4a`) | 0 |
| **Part 2** | `question_response` | `0006` (`v2` × 1) + `0007` (`v2` × 12) | **13 組** | **13 題** | 0 | **13 個** (`.m4a`) | 0 |
| **Part 3** | `conversation` | `0006` (`v2` × 1) + `0007` (`v2` × 5) | **6 組** | **18 題** | 0 | **6 個** (`.m4a`) | 0 |
| **Part 4** | `talk` | `0006` (`v2` × 1) + `0007` (`v2` × 4) | **5 組** | **15 題** | 0 | **5 個** (`.m4a`) | 0 |
| **Part 5** | `sentence` | `0001` (`v1` × 12) + `0002` (`v1` × 3) | **15 組** | **15 題** | 0 | 0 | 0 |
| **Part 6** | `text_completion` | `0002` (`v1` × 2) | **2 組** | **8 題** | 0 | 0 | 0 |
| **Part 7** | `single` (4) / `double` (2) / `triple` (1) | `0005` (`v1` × 7) | **7 組** | **28 題** | 0 | 0 | 0 |
| **合計** | **涵蓋全部 9 種 Layout** | **`0001..0007` 合併** | **51 組** | **100 題** | **3 張圖片** | **27 個音檔** | **0** |

---

## 三、30 件實體媒體資產（3 圖 + 27 音檔）技術與內容品質檢核摘要

1. **Part 1 實景圖片（3 張）**：
   - `batch-ag-0006/assets/images/ag-ast-p1-000001-image.jpg`（實驗室女研究員使用顯微鏡，正解 B）
   - `batch-ag-0007/assets/images/ag-ast-p1-000002-image.jpg`（烘焙坊店員遞紙袋給男顧客，正解 B）
   - `batch-ag-0007/assets/images/ag-ast-p1-000003-image.jpg`（晴朗無人港邊步道木長椅與停泊帆船，正解 B）
   - **驗證狀態**：全部為 `1200×896` JPEG，無文字浮水印或受保護真實商標；均已由獨立視覺子代理（`36e9db34-851a-427c-9840-b44aa170f30a`）在不看正解情況下實際讀圖盲解通過（3/3 命中）。
2. **Part 1–4 音訊檔案（27 個 `.m4a`）**：
   - 編碼規格：AAC LC，`22050 Hz` 單聲道，由本機 macOS TTS（`/usr/bin/say` + `/usr/bin/afconvert`）逐段合成並量測取樣點精確 `segment_times`（`start_ms` / `end_ms`）與 `duration_ms`。
   - **有聲／靜音與台詞時間碼對齊實測**：全部 27 檔皆經 `ffmpeg` 依 MP4 edit list 解碼回 16-bit PCM 並計算波形均方根振幅（RMS）：每個 `segment_times` 區間內均具清晰語音訊號（`min_segment_rms > 900`），每個句間停頓區間均為靜音（`max_pause_rms < 5`），無空音檔、無語尾截斷、無時間碼漂移，說話者角色切換與 `audio_script` 題序 100% 一致。
   - **AVFoundation / `afinfo` 時長與 `ffprobe` 差異說明**：`afinfo` 顯示之 `valid frames` 時長與 `metadata.duration_ms` 誤差 `<= 0.5 ms`；`ffprobe` 容器時長多出的 `102.5–140.5 ms` 為 Apple AAC 編碼器固定寫入之 `2112` priming frames（`95.78 ms`）+ remainder padding。

---

## 四、品質狀態與已知限制（誠實揭露，絕不誇大）

| 檢查維度 | 完成狀態 | 說明 |
|---|---|---|
| `content_status` / `review_state` | **`ai_checked`（100 題 / 30 素材）** | 符合 App `ContentEligibility` 正式 `training` 啟用條件 |
| 純閱讀文字獨立盲解（Part 5–7） | **51 / 51 通過 (`blind=true`)** | 由獨立上下文子代理盲解通過 |
| 聽力逐字稿獨立盲解（Part 2–4） | **46 / 46 通過 (`blind=true`)** | 由獨立上下文子代理依 `audio_script` + 圖表盲解通過 |
| Part 1 照片獨立視覺盲解（Part 1） | **3 / 3 通過 (`blind=true`)** | 由獨立視覺子代理看圖盲解通過 |
| 純聽音盲解（Audio-Only Blind Solve） | **`not_run`（0 / 49 聽力題）** | 尚未由真人或純語音模型在不看文字稿下盲解 |
| 真人命題審閱與實際耳機聽審（`human_reviewed`） | **`not_run`（0 / 100 題、0 / 30 素材）** | 未經真人審閱，絕不偽標 `human_reviewed` |
| 實測作答數據難度校準（`calibrated`） | **`not_run`（0 / 100 題）** | 全數為 `difficulty.basis = "editorial"` 編輯預估難度 |
| 已知口音限制（`ca` 角色語音包） | **8 組使用北美 `en_US` 語音代用** | `batch-ag-0007` 中 8 組含 `accent="ca"` 角色因本機無內建 `en_CA` 語音包，以北美英語語音合成並於 `source_note_zh` 誠實標註 |
| 用途池邊界 | **僅供 `training` 池使用** | 此 100 題全數為 `pool="training"`，不可挪用為 `diagnostic`、`battle` 或 `mock` |
