# TOEIC 原創題庫生產進度（PROGRESS.md）

最後更新時間（UTC）：`2026-10-28T08:46:33Z`

## 1. 當前階段與嚴格分開統計之核心指標

- **目前階段**：已完成 **Gate 1（模考契約對齊 `specs/mock-form-contract-v1.md`）、Gate 2（現有 100 題深度品質複審、真人審閱包與 27 音檔容器／有效音框／波形對齊技術審計）、Gate 3（`batch-ag-0008` training 擴充、`batch-ag-0009` diagnostic 獨立池交付、`batch-ag-0010` battle 獨立池交付）及 Gate 4（完整交接報告）**。
- **嚴格分開統計指標**：
  - **AI 審核合格數（`accepted_candidate_count`, `ai_checked`）**：**177 題**（106 個獨立題組：`training` 129 題、`diagnostic` 24 題、`battle` 24 題、`mock` 0 題）
  - **人工審核完成數（`fully_reviewed_count`, `human_reviewed`）**：**0 題**
  - **獨立盲解驗證分類**：
    - 純閱讀文字盲解（Part 5–7）：**108 題**（PASS）
    - 聽力逐字稿盲解（Part 2–4）：**65 題**（PASS）
    - Part 1 實體照片視覺盲解（Part 1）：**4 題**（PASS）
    - 純聽音盲解（不看稿 Audio-Only）：**0 / 69 題**（`not_run`）
  - **素材就緒數（`media_ready_item_count`）**：**177 / 177 題**（4 張實景照片 + 41 個 `.m4a` 音檔全數 `status=ready`）
  - **難度校準完成數（`calibrated_item_count`）**：**0 題**（全數為 `basis="editorial"`）
  - **未發布模考草稿（`unreleased_mock_draft_count`）**：**2 題**（位於 `drafts/mock-form-01-unreleased/`，不計入已發布合格題）

## 2. 已匯出不可變批次清單（`exports/batch-ag-0001` .. `0010`）

| Batch ID | Pool | 版本 | 角色與定位 | 題組數 | 小題數 | 實體音圖資產 | 狀態 |
|---|---|---|---|---:|---:|---|---|
| `batch-ag-0001` | `training` | `v1` | 原始五包基線（Part 2 × 8 + Part 5 × 12，不可變） | 20 | 20 | 0 ready / 8 planned | `exported` |
| `batch-ag-0002` | `training` | `v1` | 原始五包基線（Part 1 × 3 + Part 2 × 5 + Part 5 × 3 + Part 6 × 8，不可變） | 13 | 19 | 0 ready / 11 planned | `exported` |
| `batch-ag-0003` | `training` | `v1` | 原始五包基線（Part 3 × 6 組 18 題，不可變） | 6 | 18 | 0 ready / 6 planned | `exported` |
| `batch-ag-0004` | `training` | `v1` | 原始五包基線（Part 4 × 5 組 15 題，不可變） | 5 | 15 | 0 ready / 5 planned | `exported` |
| `batch-ag-0005` | `training` | `v1` | 原始五包基線（Part 7 × 7 組 28 題，純文字表格，不可變） | 7 | 28 | 無須外部音圖 | `exported` |
| `batch-ag-0006` | `training` | `v2` | 四題型聽力可播放樣本升級包（`ag-g-p1/p2/p3/p4-000001`） | 4 | 8 | 1 圖 + 4 音檔 `ready` | `exported` |
| `batch-ag-0007` | `training` | `v2` | 第一階段其餘 23 組聽力媒體補齊升級包 | 23 | 41 | 2 圖 + 23 音檔 `ready` | `exported` |
| `batch-ag-0008` | `training` | `v1` | **Phase 2 `training` 受控擴充第一批**（Part 5 × 16 + Part 6 × 8 + Part 7 × 5） | 20 | 29 | 純文字無須外部音圖 | `exported` |
| `batch-ag-0009` | `diagnostic` | `v1` | **首個獨立 `diagnostic` 池全題型批次**（Part 1–7 共 14 組 24 題） | 14 | 24 | **1 圖 + 8 音檔 `ready`** | `exported` |
| `batch-ag-0010` | `battle` | `v1` | **首個獨立 `battle` 池對戰批次**（Part 2 × 6 + Part 5 × 14 + Part 6 × 4） | 21 | 24 | **6 音檔 `ready`** | `exported` |

## 3. 中斷續跑與交接指引

- 本輪完整交接清單與驗證命令請見：[handoff/2026-10-28/antigravity-delivery.md](file:///Users/ziii/Desktop/TOEIC_IOS_App/handoff/2026-10-28/antigravity-delivery.md)
- 模考附加契約對齊狀態請見：[handoff/2026-10-28/antigravity-contract-status.md](file:///Users/ziii/Desktop/TOEIC_IOS_App/handoff/2026-10-28/antigravity-contract-status.md)
