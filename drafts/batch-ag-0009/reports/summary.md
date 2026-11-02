# 批次摘要報告：`batch-ag-0009`

- **用途池（Pool）**：`diagnostic`
- **批次定位**：首個獨立 `pool="diagnostic"` 可驗收批次（涵蓋 Part 1–7 共 14 組 24 題，含 1 張新生成的 Part 1 實景圖與 8 個完整合成 `.m4a` 音檔，全部 `status="ready"`，並全面使用原生 `us`/`uk`/`au` 語音，0 個 `ca` 替代缺口）。
- **題組數（Groups）**：14
- **可評分小題數（Items）**：24
- **內容審核狀態**：`ai_checked`（0 題宣稱 `human_reviewed`）
- **媒體就緒狀態**：本批內所有宣告之音訊／圖片素材均為 `status="ready"`（0 個 `planned` 缺項）

## 題型與題數分布

| 題型 | 用途池 | 題組數 | 小題數 |
|---|---|---:|---:|
| Part 1 | `diagnostic` | 1 | 1 |
| Part 2 | `diagnostic` | 4 | 4 |
| Part 3 | `diagnostic` | 2 | 6 |
| Part 4 | `diagnostic` | 1 | 3 |
| Part 5 | `diagnostic` | 4 | 4 |
| Part 6 | `diagnostic` | 1 | 4 |
| Part 7 | `diagnostic` | 1 | 2 |
| **合計** | **`diagnostic`** | **14** | **24** |

## 家族池隔離與盲解驗證

- 本批所有 `family_id` 皆為 `diagnostic` 池專屬家族，與其他用途池零重疊。
- 獨立上下文盲解輸入包：`review/blind_inputs/batch-ag-0009-blind-input.json`
- 獨立上下文盲解輸出證據：`reports/blind-solve.json`
