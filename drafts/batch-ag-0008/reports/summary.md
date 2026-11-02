# 批次摘要報告：`batch-ag-0008`

- **用途池（Pool）**：`training`
- **批次定位**：Phase 2 受控擴充第一批（Part 5 × 16 題、Part 6 × 2 組 8 題、Part 7 單篇 × 2 組 5 題，共 20 組 29 題），將 training 池由 100 題推進至 129 題。
- **題組數（Groups）**：20
- **可評分小題數（Items）**：29
- **內容審核狀態**：`ai_checked`（0 題宣稱 `human_reviewed`）
- **媒體就緒狀態**：本批內所有宣告之音訊／圖片素材均為 `status="ready"`（0 個 `planned` 缺項）

## 題型與題數分布

| 題型 | 用途池 | 題組數 | 小題數 |
|---|---|---:|---:|
| Part 5 | `training` | 16 | 16 |
| Part 6 | `training` | 2 | 8 |
| Part 7 | `training` | 2 | 5 |
| **合計** | **`training`** | **20** | **29** |

## 家族池隔離與盲解驗證

- 本批所有 `family_id` 皆為 `training` 池專屬家族，與其他用途池零重疊。
- 獨立上下文盲解輸入包：`review/blind_inputs/batch-ag-0008-blind-input.json`
- 獨立上下文盲解輸出證據：`reports/blind-solve.json`
