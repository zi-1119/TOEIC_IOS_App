# Antigravity 模考附加契約對齊狀態（`antigravity-contract-status.md`）

- **紀錄日期（Asia/Taipei）**：`2026-10-29`
- **Antigravity 接受文件**：[specs/mock-form-contract-v1.md](file:///Users/ziii/Desktop/TOEIC_IOS_App/specs/mock-form-contract-v1.md)
- **Antigravity 接受 SHA-256**：`f8d3e70867c256f95384c9c490735afcbebadbed91728f86450e262b28ae650e`（與 [codex-contract-status.md](file:///Users/ziii/Desktop/TOEIC_IOS_App/handoff/2026-10-28/codex-contract-status.md) 完全一致，達成 **Shared Acceptance**）
- **Content Contract 1.0.0 SHA-256**：`f3aee0f0ae02ae4b69bc066deb4be83acd72c687b121b72d0331f4f7567a28c1`
- **Validation Report 1.0.0 SHA-256**：`8c64b71847e83f5179e3c3fa605af14312b1a058418ca8e0b4af044d2da22ccc`

---

## 一、雙邊共同接受狀態（Shared Acceptance Confirmed）

- Antigravity 已重新讀取磁碟上現行 `specs/mock-form-contract-v1.md`，確認其 SHA-256 為 `f8d3e70867c256f95384c9c490735afcbebadbed91728f86450e262b28ae650e`，與 Codex 在 `handoff/2026-10-28/codex-contract-status.md` 記錄之接受值完全一致。
- 已同步更新 [specs/mock-forms.schema.json](file:///Users/ziii/Desktop/TOEIC_IOS_App/specs/mock-forms.schema.json) 與 `scripts/validate_and_package.py`，100% 對齊現行 `specs/mock-form-contract-v1.md` wire format 與 `TOEICPath/Data/MockFormContract.swift`。

---

## 二、Antigravity 題庫端支援與驗證規則對照

| 契約項目 | 規格內容 | Antigravity 支援狀態 |
|---|---|---|
| 頂層欄位與版本 | `form_schema_version: "1.0.0"`、`content_schema_version: "1.0.0"`、`content_set`、`assets`、`forms` | **完全支援並由 JSON Schema 強制驗證** |
| 非循環雙階段封裝 (`required_batches`) | 先發布 `pool="mock"` 題組來源批次（計算固定 `manifest.json` SHA-256），再發布獨立 form package（`groups.jsonl` 可為 0 行，於 `content_set.required_batches` 引用來源批次 `manifest_sha256`） | **完全支援** |
| 整卷時間線資產登錄 | 頂層 `assets[]` 登錄 `kind: "mock_audio_timeline"`，實體檔案置於 `assets/mock/<form_id>/timeline.m4a` 並列入 form package 的 `manifest.json.files` | **完全支援** |
| 題組與題數結構 | 每份表單 200 唯一小題（100 聽力 + 100 閱讀），Part 1–7 為 `6 / 25 / 39 / 30 / 30 / 16 / 54`，Part 7 為單篇 29 題 + 雙／三篇 25 題，完整題組不拆分（54 聽力題組 + 49 閱讀題組 = 103 題組） | **完全支援** |
| 毫秒時間線事件 (`listening_timeline`) | `events[]` 依 `sequence` 嚴格遞增，支援 `directions`、`item_unlock`（`end_ms == start_ms`）、`stimulus`、`response_options`（Part 1–2 必備）、`response_window`（每道聽力題必備）、`pause` | **完全支援** |
| Apple `AVAudioFile` 解碼時長對齊 | `AVAudioFile.length / sampleRate` 即 CoreAudio `valid_frames` 時長，與本專案合成器寫入之 `duration_ms` 誤差 `<= 1 ms`（遠小於契約 `100 ms` 容差） | **完全支援** |
| 正式啟用 vs 開發預覽門檻 | 正式啟用要求來源題組 `content_status="human_reviewed"` 且時間線音檔 `review_state="human_reviewed"`；未完成真人審閱前保持 `ai_checked` 候選狀態，絕不偽標 `human_reviewed` | **嚴格遵守** |
