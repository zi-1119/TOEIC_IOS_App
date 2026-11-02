# Antigravity 題庫端交付與交接清單（`antigravity-delivery.md`）

- **交付時間（UTC）**：`2026-10-28T08:47:00Z`
- **對應指令**：[02-antigravity-next-round.md](file:///Users/ziii/Desktop/TOEIC_IOS_App/handoff/2026-10-28/02-antigravity-next-round.md)（已確認讀至結尾標記 `END-ANTIGRAVITY-HANDOFF-2026-10-28`）
- **對應模考契約狀態**：[antigravity-contract-status.md](file:///Users/ziii/Desktop/TOEIC_IOS_App/handoff/2026-10-28/antigravity-contract-status.md)（對齊 `specs/mock-form-contract-v1.md` SHA-256 `0588948a0b61cb43ed9e64abd8b12d35740560108790869f91c11920873a8f6f`）
- **Codex 端契約與接收回饋狀態**：截至本報告產出時，`handoff/2026-10-28/codex-contract-status.md` 尚未建立（`pending`），因此所有新交付批次與跨邊界項目統一標記為 **`producer validated / receiver pending`**，絕不單方面宣稱 App 端已匯入或實機播放完成。

---

## 一、全量已匯出不可變批次清單與 `manifest.json` SHA-256（`exports/batch-ag-0001` .. `0010`）

既有 `exports/batch-ag-0001` 至 `exports/batch-ag-0007` 完全保留未覆寫；本輪新增匯出 `batch-ag-0008`（`training` 擴充）、`batch-ag-0009`（`diagnostic` 獨立池）與 `batch-ag-0010`（`battle` 獨立池）：

| Batch ID | Pool | 題組版本 | 題組數 | 小題數 | 包內檔案數 (`manifest.files`) | 實體音圖資產 | `manifest.json` SHA-256 | 接收端狀態 |
|---|---|---|---:|---:|---:|---|---|---|
| `batch-ag-0001` | `training` | `v1` | 20 | 20 | 5 | 0 ready / 8 planned | `33cdbceab178bdbd34e52b90f223d9f208330a741c3c62e0dce092bd5a829582` | 基線已驗收（8組聽力已被 `0006`/`0007` v2 取代） |
| `batch-ag-0002` | `training` | `v1` | 13 | 19 | 5 | 0 ready / 11 planned | `803a20cbb72328b9d80e4d42ff57b7a124fe7910aa55b87ac090716599aebb2d` | 基線已驗收（8組聽力已被 `0006`/`0007` v2 取代） |
| `batch-ag-0003` | `training` | `v1` | 6 | 18 | 5 | 0 ready / 6 planned | `63c998c7b22c6085790b3ae9297e607b86b298611e27e9182e20cb3ff50cccea` | 基線已驗收（6組聽力已被 `0006`/`0007` v2 取代） |
| `batch-ag-0004` | `training` | `v1` | 5 | 15 | 5 | 0 ready / 5 planned | `d14648fc40de3cd818d7f1ae5fbd9f18428ef944757c7913ccedff73f2445769` | 基線已驗收（5組聽力已被 `0006`/`0007` v2 取代） |
| `batch-ag-0005` | `training` | `v1` | 7 | 28 | 5 | 純文字與表格 | `b30084117255155390113215ee5926d5805fd3b2e9237fa95333e3da28e1031e` | 基線已驗收 |
| `batch-ag-0006` | `training` | `v2` | 4 | 8 | 11 | **1 圖 + 4 音檔 `ready`** | `fcfac99c0976f6494e764f68813652cea7b686888bb39a2e1589d4b060c85a96` | 四題型聽力樣本包（取代 v1 同 ID 4 組） |
| `batch-ag-0007` | `training` | `v2` | 23 | 41 | 31 | **2 圖 + 23 音檔 `ready`** | `72392de96d92ead8f8695873064ce42aabe425c5cecfbe6839b05ca1fdf9f317` | 其餘 23 組聽力升級包（取代 v1 同 ID 23 組） |
| **`batch-ag-0008`** | **`training`** | **`v1`** | **20** | **29** | **5** | **純文字（Part 5/6/7）** | `bd1c0eceb2e13d704661c3e05afc6c38b9edf549163d181d36cef70552089f46` | **`producer validated / receiver pending`** |
| **`batch-ag-0009`** | **`diagnostic`** | **`v1`** | **14** | **24** | **14** | **1 圖 + 8 音檔 `ready`** | `1a4488a32b8a37b63de2bcb9399776dcbdb99ad016cdebb79d25849aa50ca324` | **`producer validated / receiver pending`** |
| **`batch-ag-0010`** | **`battle`** | **`v1`** | **21** | **24** | **11** | **6 音檔 `ready`** | `b181005a70a07966fbf198d4b244c1f6b130da0f173254712ae50b88ad1b5f11` | **`producer validated / receiver pending`** |

---

## 二、批次依賴關係、建議匯入順序與版本取代關係

### 1. 建議匯入順序
1. **第一階段基線與媒體升級（`pool="training"` 100 題）**：
   - 依序匯入 `batch-ag-0001` → `0002` → `0003` → `0004` → `0005` → `0006` → `0007`（或直接匯入閱讀基線 + `0006` + `0007`）。
2. **本輪新增三包（無前置依賴衝突，可依序累加匯入）**：
   - `batch-ag-0008`（`pool="training"` 新增 20 組 29 題閱讀題：`ag-g-p5-000016..000031`、`ag-g-p6-000003..000004`、`ag-g-p7-000008..000009`）
   - `batch-ag-0009`（`pool="diagnostic"` 獨立池首包 14 組 24 題：`ag-g-p1-000301`、`ag-g-p2-000301..000304`、`ag-g-p3-000301..000302`、`ag-g-p4-000301`、`ag-g-p5-000301..000304`、`ag-g-p6-000301`、`ag-g-p7-000301`）
   - `batch-ag-0010`（`pool="battle"` 獨立池首包 21 組 24 題：`ag-g-p2-000401..000406`、`ag-g-p5-000401..000414`、`ag-g-p6-000401`）

### 2. 版本取代（Supersede）明細
- **`batch-ag-0006`（`version=2`）取代之 `version=1` 題組（共 4 組 8 題）**：
  - `ag-g-p1-000001`（原在 `batch-ag-0002` v1）
  - `ag-g-p2-000001`（原在 `batch-ag-0001` v1）
  - `ag-g-p3-000001`（原在 `batch-ag-0003` v1）
  - `ag-g-p4-000001`（原在 `batch-ag-0004` v1）
- **`batch-ag-0007`（`version=2`）取代之 `version=1` 題組（共 23 組 41 題）**：
  - Part 1：`ag-g-p1-000002`、`ag-g-p1-000003`（原在 `batch-ag-0002` v1）
  - Part 2：`ag-g-p2-000002..000008`（原在 `batch-ag-0001` v1）、`ag-g-p2-000009..000013`（原在 `batch-ag-0002` v1）
  - Part 3：`ag-g-p3-000002..000006`（原在 `batch-ag-0003` v1）
  - Part 4：`ag-g-p4-000002..000005`（原在 `batch-ag-0004` v1）
- **`batch-ag-0008`、`batch-ag-0009`、`batch-ag-0010`**：全數為全新 `group_id`、`item_id`、`family_id`（`version=1`），不覆蓋任何既有題組。

---

## 三、累計題數與本輪淨新增題數（按 Part、Pool 與品質關卡嚴格分列）

### 1. 按 Part × Pool 分列（去重後有效題組共 **106 組**、可評分小題共 **177 題**）

| Part | 先前 `training` 基線 | 本輪 `training` 淨新增 (`0008`) | **累計 `training`** | **本輪 `diagnostic` 淨新增 (`0009`)** | **本輪 `battle` 淨新增 (`0010`)** | **累計 `mock` (已匯出)** | **全域去重後有效總計** |
|---|---:|---:|---:|---:|---:|---:|---:|
| Part 1 | 3 (3組) | +0 | **3** | **+1 (1組)** | +0 | 0 | **4 題 (4組)** |
| Part 2 | 13 (13組) | +0 | **13** | **+4 (4組)** | **+6 (6組)** | 0 | **23 題 (23組)** |
| Part 3 | 18 (6組) | +0 | **18** | **+6 (2組)** | +0 | 0 | **24 題 (8組)** |
| Part 4 | 15 (5組) | +0 | **15** | **+3 (1組)** | +0 | 0 | **18 題 (6組)** |
| Part 5 | 15 (15組) | **+16 (16組)** | **31** | **+4 (4組)** | **+14 (14組)** | 0 | **49 題 (49組)** |
| Part 6 | 8 (2組) | **+8 (2組)** | **16** | **+4 (1組)** | **+4 (1組)** | 0 | **24 題 (6組)** |
| Part 7 | 28 (7組) | **+5 (2組)** | **33** | **+2 (1組)** | +0 | 0 | **35 題 (10組)** |
| **合計** | **100 題 (51組)** | **+29 題 (+20組)** | **129 題 (71組)** | **+24 題 (+14組)** | **+24 題 (+21組)** | **0 題** | **177 題 (106組)** |

> **另計未發布草稿（不計入已匯出合格數）**：`drafts/mock-form-01-unreleased/groups.jsonl` 含 **2 組 2 題** `pool="mock"` 獨立家族草稿，及 `blueprints/mock-form-01-blueprint.json` 完整 **103 組 / 200 題** 模考藍圖。

### 2. 按審核、盲解模式、素材就緒與校準維度分列

| 統計維度 | 先前累計 | 本輪淨新增 | 目前全域累計 | 證據與邊界說明 |
|---|---:|---:|---:|---|
| **`ai_checked`（AI 審核與結構驗證合格候選）** | 100 題 | **+77 題** | **177 題** | 106 個獨立題組，跨池 `family_id` 零重疊 |
| **`human_reviewed`（真人審閱完成）** | 0 題 | **+0 題** | **0 題** | 無真人審閱絕不標記 `human_reviewed`；已產出 [review/human_review_pack_phase1/](file:///Users/ziii/Desktop/TOEIC_IOS_App/review/human_review_pack_phase1/README-HUMAN-REVIEWER.md) |
| **純閱讀文字獨立盲解（Part 5–7 `blind=true`）** | 51 題 | **+57 題** | **108 題** | 含 `batch-ag-0008` (29題)、`0009` (10題)、`0010` (18題)，均由新啟動之隔離子代理完成 |
| **聽力逐字稿獨立盲解（Part 2–4 `blind=true`）** | 46 題 | **+19 題** | **65 題** | 含 `batch-ag-0009` (13題)、`0010` (6題)，依 `audio_script` + 圖表盲解通過 |
| **Part 1 實體圖片視覺盲解（Part 1 `blind=true`）** | 3 題 | **+1 題** | **4 題** | 含 `batch-ag-0009` `ag-g-p1-000301` 新生成機場登機門實景照視覺盲解 |
| **純聽音盲解（Audio-Only Blind Solve）** | 0 題 | **+0 題** | **0 / 69 題 (`not_run`)** | 誠實標示 `not_run`；目前盲解子代理係讀稿／看圖作答 |
| **`media_ready`（實體媒體與文字完全就緒）** | 100 題 | **+77 題** | **177 / 177 題** | 累計 **4 張實景 JPEG + 41 個 `.m4a` 音檔**全數 `status="ready"`（0 個 `planned` 缺項） |
| **`calibrated`（實測數據統計難度校準）** | 0 題 | **+0 題** | **0 題** | 全數為 `basis="editorial"` |

---

## 四、本輪已執行的驗證命令與結果摘要

1. **模考附加契約對齊與 Schema 檢查**：
   - 核對 `specs/mock-form-contract-v1.md` SHA-256 = `0588948a0b61cb43ed9e64abd8b12d35740560108790869f91c11920873a8f6f`
   - 建立 `specs/mock-forms.schema.json` 並更新 `scripts/validate_and_package.py` 支援 `reports/mock-forms.json` 毫秒時間軸驗證。
2. **第一階段 100 題深度品質複審與真人抽審包產出**：
   - 執行：`python3 scripts/build_deep_reaudit_and_human_pack.py`
   - 結果：產出 [reports/quality-reaudit-100.md](file:///Users/ziii/Desktop/TOEIC_IOS_App/reports/quality-reaudit-100.md)、`reports/quality-reaudit-100.json` 及 [review/human_review_pack_phase1/](file:///Users/ziii/Desktop/TOEIC_IOS_App/review/human_review_pack_phase1/README-HUMAN-REVIEWER.md)（27 組優先抽樣／53 題 + 全量 100 題檢核表 + JSONL 回填模板）。
3. **新批次生成、獨立子代理盲解與打包匯出**：
   - 執行：`python3 scripts/generate_batches_0008_to_0010.py`
   - 獨立子代理盲解：
     - `batch-ag-0008`：子代理 `4f32bad9-9003-4cbe-b226-026516df0e37` → 29 / 29 命中正解（0 歧義）
     - `batch-ag-0009`：子代理 `11023d07-f42f-4121-a48c-12abbb5f3182` → 24 / 24 命中正解（含 `ag-ast-p1-000301-image.jpg` 視覺盲解，0 歧義）
     - `batch-ag-0010`：子代理 `5cf2dbb2-eaa3-4d6a-8cfd-b671f5af77d8` → 24 / 24 命中正解（0 歧義）
   - 打包驗證：
     ```bash
     python3 scripts/validate_and_package.py --source-dir drafts/batch-ag-0008 --batch-id batch-ag-0008 --export
     python3 scripts/validate_and_package.py --source-dir drafts/batch-ag-0009 --batch-id batch-ag-0009 --export
     python3 scripts/validate_and_package.py --source-dir drafts/batch-ag-0010 --batch-id batch-ag-0010 --export
     ```
   - 結果：三批皆為 `pass: 12, warning: 0, fail: 0, not_run: 1 (final_manifest_pending)`，外部驗收報告 `reports/post-package-verification/batch-ag-0008..0010-import-check.json` 全數 `all_file_hashes_match: true`。
4. **41 個 `.m4a` 音檔與 4 張照片時長／波形技術審計**：
   - 執行：`python3 scripts/audit_audio_timing_and_alignment.py`
   - 結果：產出 [reports/audio-technical-and-media-matrix.md](file:///Users/ziii/Desktop/TOEIC_IOS_App/reports/audio-technical-and-media-matrix.md) 與 `reports/audio-technical-audit.json`；41 個音檔之 `afinfo valid_frames` 與 `metadata.duration_ms` 誤差 `<= 0.5 ms`，波形 RMS 與 `segment_times` 100% 對齊。

---

## 五、仍待 Codex、真人審閱或外部服務完成的事項

1. **待 Codex 工作區確認與整合（`receiver pending`）**：
   - 完成 `handoff/2026-10-28/codex-contract-status.md`，並確認本報告與 `antigravity-contract-status.md` 所列之「雙批次模考封裝架構（source batch + form assembly batch）」與 `AVFoundation` M4A priming/container duration 量測方式。
   - 匯入本輪新增之 `exports/batch-ag-0008`（`training`）、`exports/batch-ag-0009`（`diagnostic` 24 題）與 `exports/batch-ag-0010`（`battle` 24 題），使 App 端診斷與對戰模式直接綁定各自專屬用途池。
   - 修復 `.planning/2026-10-28-integration-audit/findings.md` 所列之 App 端 `.toeicpkg` bundle 名稱硬編碼與工作區環境問題，並在模擬器／實機完成 Part 1 照片顯示與 Part 1–4 音訊播放驗收。
2. **待真人審閱者（Human Reviewer）完成**：
   - 依 [review/human_review_pack_phase1/README-HUMAN-REVIEWER.md](file:///Users/ziii/Desktop/TOEIC_IOS_App/review/human_review_pack_phase1/README-HUMAN-REVIEWER.md) 對 27 組優先抽樣（及全量題組）執行命題審閱與實際耳機聽審，填寫 `human-review-response-template.jsonl` 後再以新版本批次升為 `human_reviewed`。
3. **待外部雲端多口音 Neural TTS 服務（或商用配音）完成**：
   - 替換 `batch-ag-0007` 中 8 個含 `accent="ca"` 角色之題組音檔（本輪新增之 `batch-ag-0009` 與 `batch-ag-0010` 已 100% 採用原生 `us`/`uk`/`au` 語音，無新增 `ca` 缺口）。
