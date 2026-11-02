# 音訊與圖片素材完成狀態及外部服務需求清單（ASSET_REQUESTS.md）

更新時間（UTC）：`2026-10-28T08:46:33Z`

## 1. 全域已匯出題庫素材完成狀態總覽（`batch-ag-0001` .. `batch-ag-0010`）

| 類別 | 數量 | 狀態與說明 |
|---|---:|---|
| 純閱讀／文法無須外部素材小題（Part 5–7） | **108 題** | 純文字與表格，100% 就緒（`training`: 80 題、`diagnostic`: 10 題、`battle`: 18 題） |
| 聽力與看圖題組小題（Part 1–4） | **69 題** | `training`: 49 題（`0006`/`0007` v2）、`diagnostic`: 14 題（`0009` v1）、`battle`: 6 題（`0010` v1） |
| **累計實體就緒圖片資產（`kind=image, status=ready`）** | **4 / 4 件** | 1200×896 JPEG（`training` 3 張 + `diagnostic` 1 張），100% 通過獨立 AI 視覺盲解（`blind=true`） |
| **累計實體就緒音訊資產（`kind=audio, status=ready`）** | **41 / 41 件** | AAC 64kbps 22050Hz `.m4a`（`training` 27 件 + `diagnostic` 8 件 + `battle` 6 件），實測 `duration_ms`、波形 RMS 對齊與逐句 `segment_times` |
| **音訊容器與有效音框差異技術審計** | **27 / 27 通過** | 詳見 `reports/audio-technical-and-media-matrix.md`：`ffprobe` 多出的 `102.5–140.5 ms` 為 CoreAudio AAC `2112` priming frames (`95.78 ms`) + remainder padding，`valid_frames` 與 `duration_ms` 誤差 `<= 0.5 ms` |
| **純聽音盲解（不看稿 Audio-Only Blind Solve）** | **0 / 69 題 (`not_run`)** | 目前子代理盲解為看逐字稿／看圖模式，未宣稱已完成純聽音盲解 |
| **人工試聽與審閱完成數（`review_state=human_reviewed`）** | **0 / 45 件** | 全數標記為 `review_state=ai_checked`，待真人試聽與審閱 |

---

## 2. 全部 45 件就緒音圖資產明細表

| Asset ID | Batch ID | Pool | Group ID | Part | 類型 | 狀態 | 包內路徑 | 長度 (ms) | 時間碼段數 | 口音／視覺實現說明 |
|---|---|---|---|---:|---|---|---|---:|---:|---|
| `ag-ast-p2-000001-audio` | `batch-ag-0006` (v2) | `training` | `ag-g-p2-000001` | Part 2 | `audio` | `ready` | `assets/ag-ast-p2-000001-audio.m4a` | 12974 | 4 | 原生語音 (`us`/`uk`/`au`) |
| `ag-ast-p2-000002-audio` | `batch-ag-0007` (v2) | `training` | `ag-g-p2-000002` | Part 2 | `audio` | `ready` | `assets/ag-ast-p2-000002-audio.m4a` | 17288 | 4 | 原生語音 (`us`/`uk`/`au`) |
| `ag-ast-p2-000003-audio` | `batch-ag-0007` (v2) | `training` | `ag-g-p2-000003` | Part 2 | `audio` | `ready` | `assets/ag-ast-p2-000003-audio.m4a` | 16920 | 4 | `en_US` 北美語音代用 (`ca` 待雲端 Neural TTS) |
| `ag-ast-p2-000004-audio` | `batch-ag-0007` (v2) | `training` | `ag-g-p2-000004` | Part 2 | `audio` | `ready` | `assets/ag-ast-p2-000004-audio.m4a` | 13745 | 4 | 原生語音 (`us`/`uk`/`au`) |
| `ag-ast-p2-000005-audio` | `batch-ag-0007` (v2) | `training` | `ag-g-p2-000005` | Part 2 | `audio` | `ready` | `assets/ag-ast-p2-000005-audio.m4a` | 16083 | 4 | 原生語音 (`us`/`uk`/`au`) |
| `ag-ast-p2-000006-audio` | `batch-ag-0007` (v2) | `training` | `ag-g-p2-000006` | Part 2 | `audio` | `ready` | `assets/ag-ast-p2-000006-audio.m4a` | 16686 | 4 | `en_US` 北美語音代用 (`ca` 待雲端 Neural TTS) |
| `ag-ast-p2-000007-audio` | `batch-ag-0007` (v2) | `training` | `ag-g-p2-000007` | Part 2 | `audio` | `ready` | `assets/ag-ast-p2-000007-audio.m4a` | 17515 | 4 | 原生語音 (`us`/`uk`/`au`) |
| `ag-ast-p2-000008-audio` | `batch-ag-0007` (v2) | `training` | `ag-g-p2-000008` | Part 2 | `audio` | `ready` | `assets/ag-ast-p2-000008-audio.m4a` | 15616 | 4 | `en_US` 北美語音代用 (`ca` 待雲端 Neural TTS) |
| `ag-ast-p1-000001-image` | `batch-ag-0006` (v2) | `training` | `ag-g-p1-000001` | Part 1 | `image` | `ready` | `assets/ag-ast-p1-000001-image.jpg` | — | — | 1200×896 實景照片 (已通過 AI 視覺盲解) |
| `ag-ast-p1-000001-audio` | `batch-ag-0006` (v2) | `training` | `ag-g-p1-000001` | Part 1 | `audio` | `ready` | `assets/ag-ast-p1-000001-audio.m4a` | 15017 | 4 | 原生語音 (`us`/`uk`/`au`) |
| `ag-ast-p1-000002-image` | `batch-ag-0007` (v2) | `training` | `ag-g-p1-000002` | Part 1 | `image` | `ready` | `assets/ag-ast-p1-000002-image.jpg` | — | — | 1200×896 實景照片 (已通過 AI 視覺盲解) |
| `ag-ast-p1-000002-audio` | `batch-ag-0007` (v2) | `training` | `ag-g-p1-000002` | Part 1 | `audio` | `ready` | `assets/ag-ast-p1-000002-audio.m4a` | 16290 | 4 | 原生語音 (`us`/`uk`/`au`) |
| `ag-ast-p1-000003-image` | `batch-ag-0007` (v2) | `training` | `ag-g-p1-000003` | Part 1 | `image` | `ready` | `assets/ag-ast-p1-000003-image.jpg` | — | — | 1200×896 實景照片 (已通過 AI 視覺盲解) |
| `ag-ast-p1-000003-audio` | `batch-ag-0007` (v2) | `training` | `ag-g-p1-000003` | Part 1 | `audio` | `ready` | `assets/ag-ast-p1-000003-audio.m4a` | 13800 | 4 | 原生語音 (`us`/`uk`/`au`) |
| `ag-ast-p2-000009-audio` | `batch-ag-0007` (v2) | `training` | `ag-g-p2-000009` | Part 2 | `audio` | `ready` | `assets/ag-ast-p2-000009-audio.m4a` | 14959 | 4 | 原生語音 (`us`/`uk`/`au`) |
| `ag-ast-p2-000010-audio` | `batch-ag-0007` (v2) | `training` | `ag-g-p2-000010` | Part 2 | `audio` | `ready` | `assets/ag-ast-p2-000010-audio.m4a` | 14549 | 4 | 原生語音 (`us`/`uk`/`au`) |
| `ag-ast-p2-000011-audio` | `batch-ag-0007` (v2) | `training` | `ag-g-p2-000011` | Part 2 | `audio` | `ready` | `assets/ag-ast-p2-000011-audio.m4a` | 17800 | 4 | `en_US` 北美語音代用 (`ca` 待雲端 Neural TTS) |
| `ag-ast-p2-000012-audio` | `batch-ag-0007` (v2) | `training` | `ag-g-p2-000012` | Part 2 | `audio` | `ready` | `assets/ag-ast-p2-000012-audio.m4a` | 16537 | 4 | `en_US` 北美語音代用 (`ca` 待雲端 Neural TTS) |
| `ag-ast-p2-000013-audio` | `batch-ag-0007` (v2) | `training` | `ag-g-p2-000013` | Part 2 | `audio` | `ready` | `assets/ag-ast-p2-000013-audio.m4a` | 16134 | 4 | 原生語音 (`us`/`uk`/`au`) |
| `ag-ast-p3-000001-audio` | `batch-ag-0006` (v2) | `training` | `ag-g-p3-000001` | Part 3 | `audio` | `ready` | `assets/ag-ast-p3-000001-audio.m4a` | 64308 | 9 | 原生語音 (`us`/`uk`/`au`) |
| `ag-ast-p3-000002-audio` | `batch-ag-0007` (v2) | `training` | `ag-g-p3-000002` | Part 3 | `audio` | `ready` | `assets/ag-ast-p3-000002-audio.m4a` | 67514 | 8 | `en_US` 北美語音代用 (`ca` 待雲端 Neural TTS) |
| `ag-ast-p3-000003-audio` | `batch-ag-0007` (v2) | `training` | `ag-g-p3-000003` | Part 3 | `audio` | `ready` | `assets/ag-ast-p3-000003-audio.m4a` | 70154 | 9 | 原生語音 (`us`/`uk`/`au`) |
| `ag-ast-p3-000004-audio` | `batch-ag-0007` (v2) | `training` | `ag-g-p3-000004` | Part 3 | `audio` | `ready` | `assets/ag-ast-p3-000004-audio.m4a` | 61753 | 8 | 原生語音 (`us`/`uk`/`au`) |
| `ag-ast-p3-000005-audio` | `batch-ag-0007` (v2) | `training` | `ag-g-p3-000005` | Part 3 | `audio` | `ready` | `assets/ag-ast-p3-000005-audio.m4a` | 68069 | 7 | `en_US` 北美語音代用 (`ca` 待雲端 Neural TTS) |
| `ag-ast-p3-000006-audio` | `batch-ag-0007` (v2) | `training` | `ag-g-p3-000006` | Part 3 | `audio` | `ready` | `assets/ag-ast-p3-000006-audio.m4a` | 58485 | 8 | 原生語音 (`us`/`uk`/`au`) |
| `ag-ast-p4-000001-audio` | `batch-ag-0006` (v2) | `training` | `ag-g-p4-000001` | Part 4 | `audio` | `ready` | `assets/ag-ast-p4-000001-audio.m4a` | 60672 | 6 | 原生語音 (`us`/`uk`/`au`) |
| `ag-ast-p4-000002-audio` | `batch-ag-0007` (v2) | `training` | `ag-g-p4-000002` | Part 4 | `audio` | `ready` | `assets/ag-ast-p4-000002-audio.m4a` | 60447 | 6 | 原生語音 (`us`/`uk`/`au`) |
| `ag-ast-p4-000003-audio` | `batch-ag-0007` (v2) | `training` | `ag-g-p4-000003` | Part 4 | `audio` | `ready` | `assets/ag-ast-p4-000003-audio.m4a` | 59736 | 6 | 原生語音 (`us`/`uk`/`au`) |
| `ag-ast-p4-000004-audio` | `batch-ag-0007` (v2) | `training` | `ag-g-p4-000004` | Part 4 | `audio` | `ready` | `assets/ag-ast-p4-000004-audio.m4a` | 59819 | 6 | `en_US` 北美語音代用 (`ca` 待雲端 Neural TTS) |
| `ag-ast-p4-000005-audio` | `batch-ag-0007` (v2) | `training` | `ag-g-p4-000005` | Part 4 | `audio` | `ready` | `assets/ag-ast-p4-000005-audio.m4a` | 71447 | 6 | 原生語音 (`us`/`uk`/`au`) |
| `ag-ast-p1-000301-image` | `batch-ag-0009` (v1) | `diagnostic` | `ag-g-p1-000301` | Part 1 | `image` | `ready` | `assets/images/ag-ast-p1-000301-image.jpg` | — | — | 1200×896 實景照片 (已通過 AI 視覺盲解) |
| `ag-ast-p1-000301-audio` | `batch-ag-0009` (v1) | `diagnostic` | `ag-g-p1-000301` | Part 1 | `audio` | `ready` | `assets/audio/ag-ast-p1-000301-audio.m4a` | 21590 | 4 | 原生語音 (`us`/`uk`/`au`) |
| `ag-ast-p2-000301-audio` | `batch-ag-0009` (v1) | `diagnostic` | `ag-g-p2-000301` | Part 2 | `audio` | `ready` | `assets/audio/ag-ast-p2-000301-audio.m4a` | 16023 | 4 | 原生語音 (`us`/`uk`/`au`) |
| `ag-ast-p2-000302-audio` | `batch-ag-0009` (v1) | `diagnostic` | `ag-g-p2-000302` | Part 2 | `audio` | `ready` | `assets/audio/ag-ast-p2-000302-audio.m4a` | 19271 | 4 | 原生語音 (`us`/`uk`/`au`) |
| `ag-ast-p2-000303-audio` | `batch-ag-0009` (v1) | `diagnostic` | `ag-g-p2-000303` | Part 2 | `audio` | `ready` | `assets/audio/ag-ast-p2-000303-audio.m4a` | 17806 | 4 | 原生語音 (`us`/`uk`/`au`) |
| `ag-ast-p2-000304-audio` | `batch-ag-0009` (v1) | `diagnostic` | `ag-g-p2-000304` | Part 2 | `audio` | `ready` | `assets/audio/ag-ast-p2-000304-audio.m4a` | 19959 | 4 | 原生語音 (`us`/`uk`/`au`) |
| `ag-ast-p3-000301-audio` | `batch-ag-0009` (v1) | `diagnostic` | `ag-g-p3-000301` | Part 3 | `audio` | `ready` | `assets/audio/ag-ast-p3-000301-audio.m4a` | 42402 | 5 | 原生語音 (`us`/`uk`/`au`) |
| `ag-ast-p3-000302-audio` | `batch-ag-0009` (v1) | `diagnostic` | `ag-g-p3-000302` | Part 3 | `audio` | `ready` | `assets/audio/ag-ast-p3-000302-audio.m4a` | 37559 | 4 | 原生語音 (`us`/`uk`/`au`) |
| `ag-ast-p4-000301-audio` | `batch-ag-0009` (v1) | `diagnostic` | `ag-g-p4-000301` | Part 4 | `audio` | `ready` | `assets/audio/ag-ast-p4-000301-audio.m4a` | 45787 | 4 | 原生語音 (`us`/`uk`/`au`) |
| `ag-ast-p2-000401-audio` | `batch-ag-0010` (v1) | `battle` | `ag-g-p2-000401` | Part 2 | `audio` | `ready` | `assets/audio/ag-ast-p2-000401-audio.m4a` | 14549 | 4 | 原生語音 (`us`/`uk`/`au`) |
| `ag-ast-p2-000402-audio` | `batch-ag-0010` (v1) | `battle` | `ag-g-p2-000402` | Part 2 | `audio` | `ready` | `assets/audio/ag-ast-p2-000402-audio.m4a` | 14493 | 4 | 原生語音 (`us`/`uk`/`au`) |
| `ag-ast-p2-000403-audio` | `batch-ag-0010` (v1) | `battle` | `ag-g-p2-000403` | Part 2 | `audio` | `ready` | `assets/audio/ag-ast-p2-000403-audio.m4a` | 17186 | 4 | 原生語音 (`us`/`uk`/`au`) |
| `ag-ast-p2-000404-audio` | `batch-ag-0010` (v1) | `battle` | `ag-g-p2-000404` | Part 2 | `audio` | `ready` | `assets/audio/ag-ast-p2-000404-audio.m4a` | 17975 | 4 | 原生語音 (`us`/`uk`/`au`) |
| `ag-ast-p2-000405-audio` | `batch-ag-0010` (v1) | `battle` | `ag-g-p2-000405` | Part 2 | `audio` | `ready` | `assets/audio/ag-ast-p2-000405-audio.m4a` | 21719 | 4 | 原生語音 (`us`/`uk`/`au`) |
| `ag-ast-p2-000406-audio` | `batch-ag-0010` (v1) | `battle` | `ag-g-p2-000406` | Part 2 | `audio` | `ready` | `assets/audio/ag-ast-p2-000406-audio.m4a` | 20021 | 4 | 原生語音 (`us`/`uk`/`au`) |

---

## 3. 外部雲端 Neural TTS 工具、設定與預估用量需求（針對 8 組 `ca` 口音替換與正式模考時間軸）

本機 macOS `/usr/bin/say` 已內建美式（`en_US`）、英式（`en_GB`）與澳式（`en_AU`）原生語音包；`batch-ag-0009`（`diagnostic`）與 `batch-ag-0010`（`battle`）之新增 14 個音檔已 **100% 採用原生 `us`/`uk`/`au` 語音（0 個新增 `ca` 替代缺口）**。僅歷史 `batch-ag-0007` 中 8 個含 `accent="ca"` 角色的題組使用北美英語語音代用合成，並誠實標註。

| Group ID | 目前批次 | Part | 角色與口音規劃 | 腳本總字元數 |
|---|---|---:|---|---:|
| `ag-g-p2-000003` | `batch-ag-0007` | Part 2 | spk_q(procurement_officer/ca), spk_r(legal_assistant/us) | 175 chars |
| `ag-g-p2-000006` | `batch-ag-0007` | Part 2 | spk_q(training_coordinator/us), spk_r(it_specialist/ca) | 186 chars |
| `ag-g-p2-000008` | `batch-ag-0007` | Part 2 | spk_q(hotel_guest/ca), spk_r(concierge/uk) | 205 chars |
| `ag-g-p2-000011` | `batch-ag-0007` | Part 2 | spk_q(marketing_manager/uk), spk_r(event_assistant/ca) | 187 chars |
| `ag-g-p2-000012` | `batch-ag-0007` | Part 2 | spk_q(receptionist/ca), spk_r(sales_representative/uk) | 197 chars |
| `ag-g-p3-000002` | `batch-ag-0007` | Part 3 | spk_1(hotel_event_coordinator/ca), spk_2(corporate_client/us), spk_narrator(narrator/us) | 863 chars |
| `ag-g-p3-000005` | `batch-ag-0007` | Part 3 | spk_1(architect_male/us), spk_2(office_administrator_female/ca), spk_narrator(narrator/us) | 900 chars |
| `ag-g-p4-000004` | `batch-ag-0007` | Part 4 | spk_1(ferry_terminal_announcer/ca), spk_narrator(narrator/us) | 818 chars |
