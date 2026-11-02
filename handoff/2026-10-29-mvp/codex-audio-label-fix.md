# Part 1／2 標號解析修正 — 2026-10-31

## 結果

已修正`scripts/synthesize_listening_audio.py`開啟`option_label_gap_ms`時，將一般英文冠詞開頭（例如`A customer is waiting...`）誤判成選項A的問題。這是生成器修正，不是新音檔交付；沒有執行真實TTS、沒有覆寫exports、SeedContent或既有試聽包。

現在只有下列明確標號格式會插入`[[slnc N]]`：`(A) text`、`A) text`、`A. text`、`A: text`、`A - text`。規則另外限制：

- Part 1只接受A–D。
- Part 2的第0段永遠視為題目句、保持原文；後續回應只接受A–C，D不處理。
- Part 3／4及其他Part不處理。
- `option_label_gap_ms <= 0`直接回傳原字串，保留舊行為。
- 不符合明確標號的文字逐字保留；單獨的冠詞`A`加空白不再算標號。

## 呼叫端查核

`build_audio_listening_pack.py`會先複製題組，Part 1對四段加`(A)`–`(D)`，Part 2只對`segs[1:]`加`(A)`–`(C)`；`build_part1_audio_comparison.py`也使用明確括號標號。修正放在共同`synthesize_group_audio`實際送字給`/usr/bin/say`之前，因此即使其他呼叫端沒有額外防護，Part 2題目段與普通冠詞仍不會被改寫。本輪依範圍沒有修改這兩個呼叫端。

## 實際驗證

執行：

```text
python3 -m unittest scripts.test_synthesize_listening_audio -v
python3 -m py_compile scripts/synthesize_listening_audio.py scripts/test_synthesize_listening_audio.py
```

結果：6項測試、0失敗；Python編譯檢查exit 0。測試涵蓋一般冠詞A、Part 2題目段、五種明確標號、Part 2非法D、其他Part、gap=0，以及完整`synthesize_group_audio`路徑。完整路徑測試以假的`say`／`afconvert`建立短暫WAV/M4A，實際走相同segment迴圈並檢查送入文字，沒有呼叫TTS或付費服務。

實際合成路徑的Part 2斷言結果：

```text
A customer is waiting outside.
A [[slnc 400]] In the main lobby.
B [[slnc 400]] At three o'clock.
(D) This label is invalid for Part 2.
```

## 既有10音檔未變

修改前與修改後各讀取一次`assets_work/audio-listening-pack-2026-10-31/*.m4a`；10個SHA-256逐一相同：

```text
684cd4b76474d8dc727975321314eac90c070a2b720a0274f908a82453ebbef9  01-ag-g-p1-000001-A-original.m4a
8a639bb87401ceb9cc4dd33aacafd997c28a9cf1931f678585eb27e9a1967afe  01-ag-g-p1-000001-B-karen-labels-400ms.m4a
08b0874cf58aa9763625ad82b8f4490c219a50d7dcfb8b435f66e402e8cadcde  02-ag-g-p1-000002-A-original.m4a
b37e752a6c360c46fa373418e68564ebf532aaeb21aad0d00ed0bc4f2f300127  02-ag-g-p1-000002-B-karen-labels-400ms.m4a
5f92a455908bf43b0ee0b6cee6205d275a5ab027577fdc0cfd973d62acbbfade  03-ag-g-p1-000003-A-original.m4a
44f46c136209bed4daadc1d5705570d38502ab519691291d69ad3bbbdb4d8098  03-ag-g-p1-000003-B-karen-labels-400ms.m4a
eb30fe79d8abb0bab1ec6627e51e14ddff30da26289761589c51a08a98bc0848  04-ag-g-p2-000004-A-original.m4a
512b5f6e441b72d4fae9ff2ad11b4dee6dccb8a315aecfdea4268a840931d9bf  04-ag-g-p2-000004-B-karen-labels-400ms.m4a
6cd520ed297f651af8551f17e564f1706de00d70d6cea63a76e6c015bb07dbf6  05-ag-g-p2-000002-A-original.m4a
382faa974433036b76c568d04bf390fc4e53246d7b8a990ababee521a6fab9cc  05-ag-g-p2-000002-B-karen-labels-400ms.m4a
```

## 邊界

- 沒有重跑Swift 75測試、iOS build或177題importer回歸。
- 沒有修改Swift／App／簽章／共同契約／AG產物／exports／SeedContent。
- 沒有重製或發布音訊，也沒有把5題候選標為已通過、人耳驗收或`human_reviewed`。
- 後續仍等待使用者以iPhone喇叭完成5題A/B試聽，再決定是否建立新的不可變換音批次。
