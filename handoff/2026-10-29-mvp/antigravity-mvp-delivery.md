# Antigravity MVP 交付報告（題庫端）— 2026-10-31（2026-11-09 更新接收狀態）

範圍：題庫產生器、巢狀驗證、不可變修訂包、音訊候選。本輪沒有修改 Swift、App、SeedContent、簽章、後端或 `specs/mock-form-contract-v1.md`。
`exports/batch-ag-0001`～`0013` 沒有被覆寫，新的成果都另外發布成新批次。

> [!IMPORTANT]
> **2026-11-09 接收狀態**：Codex 的 `ContentVersionStoreTests.testRevisionBatches0011Through0015UpgradeInPlaceAndMergeWithSeedCatalog` 已用真實接收端實測 0001–0007 加 0011–0015，共 12 批／106 組／177 個不重複題目（training 129、diagnostic 24、battle 24）。v3 覆寫、引文來源、素材、重開與重新匯入都通過；協調者 10-31 16:26 獨立重跑同一測試，1 項 0 失敗。
> **手機內建的仍然只有 training 100 題（0001–0007）。** 其餘 77 題（0011–0015）只是通過接收測試，**還沒有內建到 App，也沒有人工驗收**，不能算手機上可練習的題數。

## 1. 狀態總表（各階段分開列）

| 池 | 產生 | 完整 schema＋引用驗證（題庫端） | Codex 真實接收端測試 | 手機內建 | 人工審核 | 校準 |
|---|---:|---:|---|---:|---|---|
| training | 129（100＋0011 的 29） | 129 | 129 通過 | **100** | 0 | 無 |
| diagnostic | 24（0012＋0014 覆蓋） | 24 | 24 通過 | 0 | 0 | 無（難度只是編輯估計） |
| battle | 24（0013＋0015 覆蓋） | 24 | 24 通過 | 0 | 0 | 無 |
| mock | 0 | 0 | — | 0 | 0 | — |

修訂不算新增題。0014／0015 的 10 題，跟 0012／0013 裡同一批題目是同一題，只是升了版本。

## 2. 修訂包與替代關係

| 新包 | 池 | 題組／題數 | 版本 | 取代對象 | manifest.json SHA-256 |
|---|---|---|---|---|---|
| `exports/batch-ag-0011` | training | 20／29 | v2 | `batch-ag-0008` v1 全部（被 importer 拒收） | `e8f2ebe4dba6b50f17a6ee04fd73f154f00aa8d91b98045479d4b134c6174049` |
| `exports/batch-ag-0012` | diagnostic | 14／24 | v2 | `batch-ag-0009` v1 全部（被拒收） | `9742998e21e2bccf8878dff1ab0e144a10c03d10cd28a2d33454deb04a6632b2` |
| `exports/batch-ag-0013` | battle | 21／24 | v2 | `batch-ag-0010` v1 全部（被拒收） | `71d169edccf1e72f635fdb765faa7234ec46ed02553448bb2f16bd3c96c5378b` |
| `exports/batch-ag-0014` | diagnostic | 4／4 | v3 | 0012 中的 `ag-g-p2-000301`～`000304` v2 | `9a4264fafd4f4856494ee0dfe206b0fd409cedd7e348d8a2fc3c47ac5124982e` |
| `exports/batch-ag-0015` | battle | 6／6 | v3 | 0013 中的 `ag-g-p2-000401`～`000406` v2 | `5143f9dcae186bb777c0cca24eade15e470a94fd2b161cc4600a2ee4a4c0f28e` |

**建議接收順序**：0001–0007 → 0011 → 0012 → 0013 → 0014 → 0015。0014／0015 是覆蓋包，只含修正後的題組，所以 0012／0013 仍然要裝。
安裝順序不影響結果：探針實測先裝 0014 再裝 0012，`mergePackages` 一樣選到 v3。

### 2.1 0011–0013（v2）修了什麼
所有題組都保留原本的 group_id／item_id／family_id／pool、題幹、選項、正解和音圖。修正內容：
- 每筆 evidence 補上 `reasoning_zh`
- vocabulary 改成 `term_en`／`meaning_zh`／`example_en`，100 個詞條都有完整商務例句；`ag-i-p7-000009-1` 原本誤寫成陣列，已修正
- `doc_id`／`doc_type` 改成 `document_id`／`genre`
- 移除 `trap_type` 和 `prompt_hash`
- reviews 的 findings 補上 `item_id`

### 2.2 本輪新發現的缺陷 → 0014／0015（v3）
0012／0013 共 **10 題 Part 2**：第二筆 evidence 引用的回應句是對的，但 `source_id` 指到題目句或前一個選項段落（錯一格）。
舊的 references-001 只檢查 ID 存不存在，所以漏掉了；這個缺陷早在 v1 生成時就有。
v3 只改 `source_id`。題幹、選項、正解、音檔位元和 segment_times 都沒變。每題的修改明細在各包的 `reports/changelog.json` 和 `summary.md`。
Swift importer 不會檢查引文是否落在被引用的段落內，所以 0012／0013 本身裝得進去，但解析內容的證據會指錯位置。**請以 0014／0015 為準。**

### 2.3 歷史報告誤判，在此更正
- 0008／0009／0010 的 `validation.json` 原本寫 0 fail，這是假陽性。完整巢狀 schema 檢查其實分別有 309／244／258 項違規（含 reviews 和引用）。
- 0012／0013 的 `validation.json`（2026-10-30 產生）漏報上述 evidence 指向錯誤，用新的驗證器重跑會判 fail。這兩包保留原樣，不覆寫，由 0014／0015 修正。
- 0001–0007 用新的驗證器重跑仍然沒有 fail。表格型 evidence 會依表格列比對，不影響結果。
- 完整紀錄：`reports/revalidation-audit-2026-10-31.json`。舊版 `reports/revalidation-audit-2026-10-29.json` 保留作歷史紀錄。

## 3. 產生器與驗證器修改

| 檔案 | 修改 |
|---|---|
| `scripts/validate_and_package.py` | 用 Draft 2020-12 完整驗證 groups／reviews／validation／manifest／mock-forms；新增 evidence 引文必須出現在被引用段落或表格列的檢查（併入 references-001）；欄位缺失時不再當掉；`PROTECTED_BATCH_IDS` 擴大到 0001–0015，拒絕覆寫 |
| `scripts/generate_batches_0008_to_0010.py` | 修好產生器本身：不再輸出 `prompt_hash`／`trap_type`／舊 vocabulary 鍵／`doc_id`；自動補 `reasoning_zh` 和 findings `item_id`；mock 契約雜湊更新成共同確認的 `f8d3e708…650e` |
| `scripts/build_revised_batches_0011_to_0013.py` | 產生 v2 修訂包（現在 0011–0013 受保護，重跑會被拒絕覆寫） |
| `scripts/build_evidence_fix_batches_0014_0015.py` | 新增：產生 v3 evidence 指向修正包 |
| `scripts/test_validator_negative_cases.py` | 負例測試從 14 項增加到 17 項 |
| `scripts/verify_exports.py` | 新增：獨立於打包流程的 schema、雜湊、未列檔、引文檢查 |
| `scripts/swift_importer_probe.swift`、`scripts/run_swift_importer_probe.sh` | 改用現行 API（`install(from:)`、`activeCatalog()`）；在 `$TMPDIR` 另外建置，不碰 repo 的 `.swiftpm-build` |
| `scripts/build_audio_listening_pack.py` | 新增：產生試聽包 |

### 負例測試結果（17／17 都正確拒絕）
1. 缺 `reasoning_zh`
2. `reasoning_zh` 是佔位字
3. vocabulary 用 surface／pos 等舊鍵
4. vocabulary 寫成陣列
5. 例句是佔位字
6. `doc_id`／`doc_type`
7. 多了 `trap_type`
8. 多了 `prompt_hash`
9. findings 缺 `item_id`
10. 錯誤 enum
11. 壞掉的引用
12. 錯誤的資產 hash
13. 重複 ID
14. family 跨用途池
15. **引文不在被引用段落（新增）**
16. **型別錯誤（新增）**
17. **缺必填 `family_id`（新增）**

另外，乾淨的基線樣本必須 0 fail，測試才會執行。

## 4. 題庫端 Swift 參考探針（不是接收驗收）

這支探針用目前磁碟上的 TOEICPathCore 原始碼建置，2026-10-31 實測：
- 安裝 0001–0007、0011–0015 全部成功。active 共 106 組／177 題／55 個資產，版本分布 v1:24、v2:72、v3:10。
- `ContentEligibility`：training 71 組／129 題，diagnostic 14／24，battle 21／24，mock 0。
- 加入 0008–0010 一起跑時，三包都在 `groups.jsonl` 第 1 行被拒收（缺 `reasoning_zh`），之後的 0011–0015 仍然正常安裝。

**這只是題庫端的參考結果。** 正式接收結果以 Codex 的真實接收端測試為準，見本文開頭 2026-11-09 接收狀態：已通過，結果和本探針一致。

## 5. 音訊回歸（03 文件）

- **標號缺漏盤點**：0006／0007 內建的 3 個 Part 1 加 13 個 Part 2 音檔都**沒有念出選項標號**，這是使用者實機回報的那一類問題。0012／0013 的 1 個 Part 1 加 10 個 Part 2 腳本有「(A)…」標號，`say` 會念出來，但沒有 400 ms 間隔，也不是 Karen 聲線。Part 2 題目句都沒有被誤加標號。
- **試聽包**：`assets_work/audio-listening-pack-2026-10-31/`，共 5 題（Part 1 三題、Part 2 兩題），每題有原檔和候選。度量資料包括長度、LUFS、true peak、實測停頓和段落時間碼，請見該目錄的 `README.md`（含試聽填寫表）和 `listening-pack.json`。實測標號到句子的停頓是 349–378 ms（要求值 400 ms，經 AAC 編碼後測得）。
- 01 候選和 Codex 的 `candidate-karen-labels-400ms-gap.m4a` 參數、時間碼都一樣，但 PCM 不是逐位元相同，因為 TTS 每次輸出不完全一致。
- **未做／待真人**：只靠音訊的盲解（not_run，本機沒有可信的 ASR）、耳機聽審、iPhone 喇叭試聽。所以**沒有任何音訊標成 human_reviewed，也沒有發布換音包**。Karen＋標號＋400ms 方向經使用者確認後，才會依實際最新版本發布 v3／v4 換音包（例如 `ag-g-p1-000001` 目前是 v2，改後會是 v3），並重新量測時間碼、長度和 hash。
- **標號解析缺陷（已修正，2026-10-31）**：`synthesize_listening_audio.py` 原本會把開頭是冠詞 A 的一般句子（例如 "A customer is…"）當成標號。現在只有明確格式的標號才會插入間隔：Part 1 限 A–D；Part 2 題目段永遠不處理，回應只接受 A–C；gap=0 時保持原行為。單元測試 6 項 0 失敗，修正前後 10 個試聽音檔的 hash 都沒變，詳見 `codex-audio-label-fix.md`。
- **外部服務**：本輪沒有使用付費 TTS，也不需要。如果使用者認為本機聲音品質還是不夠，可以考慮雲端神經語音（例如 Azure／Google／ElevenLabs），但需要使用者自己的帳號、金鑰和費用同意，而且會把英文腳本文字傳到第三方。我沒有自行啟用。

## 6. 可重現驗證命令

```bash
cd /Users/ziii/Desktop/TOEIC_IOS_App
python3 scripts/test_validator_negative_cases.py          # 17 負例 + 全部批次重驗
python3 scripts/verify_exports.py batch-ag-0011 batch-ag-0012 batch-ag-0013 batch-ag-0014 batch-ag-0015
shasum -a 256 exports/batch-ag-00{11,12,13,14,15}/manifest.json
./scripts/run_swift_importer_probe.sh                     # 題庫端參考，非接收驗收
python3 scripts/build_audio_listening_pack.py             # 重建試聽候選
```
執行 `verify_exports.py` 的預期結果：0011、0014、0015 判 PASS；0012、0013 判 FAIL，各有 4／6 項，都是 evidence 指向錯誤，已由 0014／0015 修正。

## 7. 待辦

| 項目 | 等誰 |
|---|---|
| ~~用真實 importer 接收 0011–0015~~：已完成，177 題通過，見開頭說明 | Codex（完成） |
| 決定 0011–0015 是否內建進 App（目前沒有內建） | Codex／使用者 |
| 用 iPhone 喇叭試聽 5 題候選（README 表格；Codex 正在 App 內加試聽入口） | 使用者 |
| 試聽通過後，依 `reports/audio-promotion-readiness-2026-11-09.md` 的 G2–G8 發布 16 組 v3 換音不可變包，Codex 再更新 seed | AG → Codex |
| 診斷擴充到 40–60 題、完整 200 題模考 | 暫緩，依 04 文件，第一階段先完成簡單離線測驗 |

共同模考契約 `specs/mock-form-contract-v1.md` 的 SHA-256：`f8d3e70867c256f95384c9c490735afcbebadbed91728f86450e262b28ae650e`（本輪沒有改動）。
