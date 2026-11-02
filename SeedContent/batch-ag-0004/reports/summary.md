# 批次交付摘要：batch-ag-0004

- **批次編號（batch_id）**：`batch-ag-0004`
- **契約版本（schema_version）**：`1.0.0`
- **產生時間（UTC）**：`2026-10-27T12:05:44Z`
- **用途池（pool）**：`training`（`fixture=false`）
- **題組總數（group_count）**：5 組
- **小題總數（item_count）**：15 題
- **內容審核狀態（content_status）**：全部為 `ai_checked`（0 題 `human_reviewed`）
- **獨立上下文盲解結果**：可盲解文字／音訊稿題 15 題全數一致通過（100% 吻合）；待圖片就緒後盲解之 Part 1 題目 0 題（誠實標記 `blind=false`）。

## 1. 各 Part 題組與小題分布

| 題型 | 題組數 | 小題數 |
|---|---:|---:|
| Part 4 | 5 | 15 |
| **合計** | **5** | **15** |

## 2. 編輯難度分布（Editorial Difficulty）

| 難度等級 | 小題數 |
|---|---:|
| D1 | 0 |
| D2 | 3 |
| D3 | 6 |
| D4 | 3 |
| D5 | 3 |

## 3. 正解選項位置分布

| 選項 | 小題數 |
|---|---:|
| B | 6 |
| C | 8 |
| D | 1 |

## 4. 素材與人工審核缺項聲明（已知限制）

1. **待製音訊／圖片素材**：
   - 待合成音訊（`kind=audio, status=planned`）：**5** 件
   - 待生成圖片（`kind=image, status=planned`）：**0** 件
   - 所有待製素材均已提供完整 `audio_script`、`speakers` 口音規劃與圖片場景規格（`source_note_zh`），依契約將 `path`、`sha256`、`duration_ms` 設為 `null`，並同步列入全域 `reports/ASSET_REQUESTS.md`。在實際音圖就緒並完成驗收前，聽力與看圖題僅供私有草稿或技術預覽，不得宣稱完整聽力可用。
2. **人工審閱與統計校準狀態**：
   - 本批題目已完成程式結構驗證、獨立上下文子代理盲解（`reports/blind-solve.json`）與 AI 命題品質審查，最高狀態為 `ai_checked`。
   - 尚未經過真人命題專家審閱（`fully_reviewed_count = 0`）與真實考生樣本 IRT 統計校準，已列入 `reports/REVIEW_QUEUE.md`。
