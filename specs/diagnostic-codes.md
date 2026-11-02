# 驗證工具診斷代碼定義（Diagnostic Codes v1.0.0）

驗證工具名稱：`ag-content-validator`  
工具版本：`1.0.0`  
對應規範：`TOEIC Content Contract 1.0.0`、`Validation Report 1.0.0`

本文件定義 `reports/validation.json` 中 `checks[].code` 與 `reviews.jsonl` 中 `findings[].code` 使用的穩定診斷代碼。

## 1. `structure`（結構、必填欄位、enum、題組形狀）
- `struct_json_schema_valid`：JSON 語法、必填欄位、資料型別與 enum 均符合 Content Contract 1.0.0。
- `struct_json_schema_invalid`：JSON 語法、必填欄位、資料型別或 enum 不符合契約。
- `struct_part_shape_valid`：各題組之 `part`、`layout`、題數、選項數、`documents` 數量、Part 5/6/7 標記與表格列寬均符合規定。
- `struct_part_shape_invalid`：題組之 `part`/`layout`、題數、選項數、空格標記或表格列寬不符規定。
- `struct_html_js_forbidden`：文件或題幹不得包含可執行 HTML/JavaScript。

## 2. `references`（引用完整性與時間碼）
- `ref_evidence_valid`：所有 `item.evidence` 的 `source_type` 與 `source_id` 均正確指向既有之 `document_block`、`audio_segment`、`asset` 或 `item_prompt`。
- `ref_evidence_invalid`：`item.evidence` 引用了不存在的 `source_id` 或不合法的 `source_type`。
- `ref_audio_speakers_valid`：`stimulus.audio_script` 中的所有 `speaker_id` 均存在於 `stimulus.speakers`，且角色配置符合 Part 1–4 要求。
- `ref_audio_speakers_invalid`：`audio_script` 引用了未定義的 `speaker_id` 或角色數不符 Part 要求。
- `ref_review_refs_valid`：每個題組的 `review_refs` 均指向本批次 `reviews.jsonl` 中實際存在且 `group_id`/`version` 相符的審查紀錄。
- `ref_review_refs_invalid`：`review_refs` 缺漏或指向不存在的 `review_id`。
- `ref_segment_times_valid`：`assets[].segment_times` 與 `audio_script` 及 `duration_ms` 一致（若 `planned` 則為空陣列）。
- `ref_segment_times_invalid`：`segment_times` 引用不存在的 `segment_id` 或時間範圍無效。

## 3. `uniqueness`（ID、版本、家族與文字／語意去重）
- `uniq_intra_batch_ids_valid`：本批內 `group_id`、`item_id`、`asset_id`、`review_id` 完全唯一無重複，且同一 `family_id` 未跨 `pool`。
- `uniq_intra_batch_ids_conflict`：本批內發生 ID 重複或同家族跨用途池衝突。
- `uniq_cross_batch_index_valid`：與歷史批次索引比對，無 `item_id` 重複、無同 `group_id` 同版不同內容衝突、無 `family_id` 跨用途池衝突。
- `uniq_cross_batch_index_conflict`：與歷史批次發生 ID、版本或家族跨池衝突。
- `uniq_cross_batch_index_not_run`：尚無歷史批次索引可供跨批比對。
- `uniq_exact_and_normalized_valid`：完全相同文字與正規化文字（小寫、去標點、去空白）檢查通過，無重複題幹、選項組或文稿。
- `uniq_exact_or_normalized_duplicate`：偵測到完全相同或正規化後重複的題幹／文稿。
- `uniq_semantic_family_valid`：基於 n-gram TF-IDF 餘弦相似度、詞彙 Jaccard 相似度與家族邏輯骨架檢查，無未標記之近似題組。
- `uniq_semantic_family_warning`：偵測到語意或結構較接近的題組，已列入人工待審訊號。
- `uniq_semantic_not_run`：未執行語意／家族近似檢查。

## 4. `assets`（素材狀態、路徑安全、檔案存在與雜湊）
- `asset_path_safety_valid`：所有素材路徑均為安全相對路徑（或於 `planned` 時為 `null`），無絕對路徑、`..` 或越界連結。
- `asset_path_safety_invalid`：素材路徑違反安全規範或與 `status` 規則不符。
- `asset_ready_all_valid`：所有必要音訊與圖片素材均為 `ready`，且檔案存在、SHA256 與時長驗證通過。
- `asset_planned_pending_media`：聽力或圖片題含有 `status="planned"` 之待製素材，欄位符合契約（`path/sha256/duration_ms` 為 `null`），但尚不可宣稱完整聽力／看圖可用（於 `authoring` profile 列為 `warning`，於 `release` profile 列為 `fail`）。
- `asset_ready_missing_or_corrupt`：標示為 `ready` 的素材缺檔、雜湊不符或時長無效。

## 5. `review_integrity`（審查紀錄、盲解證據與狀態門檻）
- `rev_status_gate_valid`：`content_status` 與實際審查紀錄一致（未經人工審查最高為 `ai_checked`），無偽造 `human_reviewed`。
- `rev_status_gate_invalid`：`content_status` 超出實際審查證據門檻或含 `reject`/`revise` 卻未隔離。
- `rev_blind_evidence_valid`：標示 `blind=true` 之審查紀錄具備獨立盲解輸入與輸出證據檔（`reports/blind-solve.json`），且作答比對一致。
- `rev_blind_not_applicable_planned_image`：Part 1 圖片素材尚處於 `planned` 階段，無法僅憑空圖片做視覺盲解，已誠實標示 `blind=false` 並排入圖片就緒後重審。
- `rev_blind_mismatch_or_missing`：宣告 `blind=true` 但缺獨立盲解證據檔，或盲解答案與設定正解矛盾。

## 6. `content_quality`（語意、唯一正解、詳解與干擾項品質）
- `qual_editorial_review_valid`：每題均完成 AI 命題品質審查，具備非空正解證據、繁中詳解、全部錯誤選項之具體干擾原因（無「因為答案是 X」式無效解析），且盲解與命題審查均為 `pass`。
- `qual_answer_distribution_info`：批次正解選項位置分布正常（僅供批次偏態監測，不強制改答案湊均勻）。
- `qual_editorial_issue_found`：詳解缺漏、干擾項理由無效或語意審查未通過。

## 7. `package`（打包清單與最終 Manifest 狀態）
- `pkg_pre_manifest_inventory_valid`：組包前之 `groups.jsonl`、`reviews.jsonl`、`reports/summary.md`、`reports/blind-solve.json` 檔案存在且題組／小題數量一致。
- `final_manifest_pending`：`validation.json` 寫出時最終 `manifest.json` 尚未計算完成（避免自我雜湊循環），由封裝腳本緊接著生成 `manifest.json` 並由接收端（或包外驗證報告）核對最終 SHA256。
