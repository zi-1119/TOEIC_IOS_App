# 批次摘要報告：`batch-ag-0010`

- **用途池（Pool）**：`battle`
- **批次定位**：首個獨立 `pool="battle"` 可驗收批次（涵蓋 Part 2 × 6 組 6 題、Part 5 × 14 組 14 題、Part 6 × 1 組 4 題，共 21 組 24 題，含 6 個完整合成 `.m4a` 音檔，全部 `status="ready"`，支援 App 對戰模式直接抽選 `pool="battle"` 題組）。
- **題組數（Groups）**：21
- **可評分小題數（Items）**：24
- **內容審核狀態**：`ai_checked`（0 題宣稱 `human_reviewed`）
- **媒體就緒狀態**：本批內所有宣告之音訊／圖片素材均為 `status="ready"`（0 個 `planned` 缺項）

## 題型與題數分布

| 題型 | 用途池 | 題組數 | 小題數 |
|---|---|---:|---:|
| Part 2 | `battle` | 6 | 6 |
| Part 5 | `battle` | 14 | 14 |
| Part 6 | `battle` | 1 | 4 |
| **合計** | **`battle`** | **21** | **24** |

## 家族池隔離與盲解驗證

- 本批所有 `family_id` 皆為 `battle` 池專屬家族，與其他用途池零重疊。
- 獨立上下文盲解輸入包：`review/blind_inputs/batch-ag-0010-blind-input.json`
- 獨立上下文盲解輸出證據：`reports/blind-solve.json`
