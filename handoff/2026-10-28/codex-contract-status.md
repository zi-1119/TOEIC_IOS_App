# Codex 模考附加契約狀態

- 紀錄日期（Asia/Taipei）：2026-10-29
- Codex 接受文件：`specs/mock-form-contract-v1.md`
- Codex 接受 SHA-256：`f8d3e70867c256f95384c9c490735afcbebadbed91728f86450e262b28ae650e`
- Content Contract 1.0.0 SHA-256：`f3aee0f0ae02ae4b69bc066deb4be83acd72c687b121b72d0331f4f7567a28c1`
- Validation Report 1.0.0 SHA-256：`8c64b71847e83f5179e3c3fa605af14312b1a058418ca8e0b4af044d2da22ccc`

## Codex 支援範圍

- 解碼 `reports/mock-forms.json` 毫秒格式。
- 解析精確 `group_id + version + source_batch_id`，驗證每個來源 manifest SHA-256。
- 強制來源題組為 `mock / fixture=false / human_reviewed`，並阻擋 training、diagnostic、battle 或未核准內容。
- 強制 200 唯一小題、100 聽力＋100 閱讀、Part 1–7 配額 6/25/39/30/30/16/54、Part 7 單篇 29／多篇 25。
- 強制整卷音檔登錄於 form package 的 `assets/mock/<form_id>/`，核對 manifest 檔案 hash、時間線事件、unlock 次數／順序／範圍、Part 1–2 spoken options 與每題 response window。
- 使用 `AVAudioFile.length / sampleRate` 取得 Apple AVFoundation 解碼時長，與 asset／timeline `duration_ms` 容許差 `<= 100 ms`。
- 拒絕 form package 在 `required_batches` 自我引用。Codex 接受 Antigravity 提出的兩階段封裝：先發布 mock 題組來源包，再發布可為 0 題組的獨立 form package；其 report 只引用已完成來源 manifest。
- release 正式啟用仍要求 timeline asset `human_reviewed`。`ai_checked` 候選只能停留在未正式啟用狀態。

## 已執行驗證

- 模考契約 XCTest 9 項通過：合法 200 題、缺來源包、self-hash、錯版本／hash、秒數誤填、缺音檔、解碼時長超差、fixture／非 human-reviewed、unlock 缺漏／重複／倒退／越界、素材錯置。
- 七包基線未含任何 `mock` 題組或 form package；正式可用模考仍為 0，不宣稱完成。

## 對方接受狀態

`handoff/2026-10-28/antigravity-contract-status.md` 接受的舊 SHA-256 是 `0588948a0b61cb43ed9e64abd8b12d35740560108790869f91c11920873a8f6f`。本輪依其 clarification 加入非循環封裝、正式題組狀態及 AVFoundation 解碼細節後，文件 hash 已變更為上述 `f8d3...650e`。

因此目前狀態是 **Codex accepted / Antigravity re-acceptance pending**，不是 shared acceptance。Antigravity 必須重新讀取現行文件並記錄相同 hash，才可標示雙方接受。
