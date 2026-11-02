# TOEIC 題庫共用契約

版本 1.0.0｜2026-10-27｜供兩個工作區對照；前兩份指令已內嵌本契約，無須另外貼一次。

## 共用契約 TOEIC Content Contract 1.0.0（兩邊完全一致）

此節是兩個工作區共同遵守的交換規格。它是本專案的設計決定，不代表 ETS 認證。原始題庫交換包包含答案，屬於私有製作資料；不可整包直接發送到競技客戶端。

### A. 範圍、數量與計數

- 產品只涵蓋 TOEIC Listening & Reading，Part 1–7；英文題目，繁體中文詳解。
- 4,800 是合格、去重後的可評分小題數，不是題組數或生成嘗試數。一段對話的三小題算三題。
- 單純更改人名、日期、公司名的變體屬同一 family，不能當作新增獨立覆蓋。題組與同一家族不得跨用途池。
- 用途池固定為 training、battle、diagnostic、mock。所有開發示例使用 fixture=true，不計入配額。
- 開發種子與產題試行中的 100／400 題均不是額外加在 4,800 之上；合格者按已分配用途計入，曝光歷史不能消失。

| Part | training | battle | diagnostic | mock | 總計 |
|---|---:|---:|---:|---:|---:|
| 1 | 90 | 18 | 12 | 24 | 144 |
| 2 | 375 | 75 | 50 | 100 | 600 |
| 3 | 585 | 117 | 78 | 156 | 936 |
| 4 | 450 | 90 | 60 | 120 | 720 |
| 5 | 450 | 90 | 60 | 120 | 720 |
| 6 | 240 | 48 | 32 | 64 | 384 |
| 7 | 810 | 162 | 108 | 216 | 1,296 |
| 合計 | 3,000 | 600 | 400 | 800 | 4,800 |

mock 為四份各 200 題的完整試卷。每卷 Part 1–7 分別是 6、25、39、30、30、16、54 題；Part 7 為單篇 29、雙／三篇合計 25。完整題組不拆分。聽力約 45 分鐘、閱讀 75 分鐘。100 題驗證集不是縮小版官方模考。

### B. 交換包與責任邊界

每批是一個獨立目錄：
```text
batch-ag-0001/
  manifest.json
  groups.jsonl
  reviews.jsonl
  reports/validation.json
  reports/summary.md
  assets/                     # 只有實際存在的素材；可為空
```

- groups.jsonl 使用 UTF-8、每行一個完整 JSON 題組，不含註解，不包 Markdown code fence。
- JSON 文字換行用正確跳脫；ID 與答案以字串保存，日期時間用 ISO 8601 UTC；不得含 NaN。
- 每包 manifest 欄位：schema_version、batch_id、created_at、producer、group_count、item_count、files。files 是 {path, sha256} 陣列，列出包內所有其他檔案，不列 manifest 自身。雜湊必須由實際檔案計算。
- producer 記錄實際工具與模型；若無法確認模型名稱，寫 unknown，不猜測。
- 只用相對路徑；拒絕絕對路徑、.. 跳脫、越界 symlink；所有雜湊及宣告題數須可重算。
- Antigravity 產生私有候選包；Codex 驗證、隔離、審查、匯入。兩者不直接共同修改正式資料庫。
- 候選包先進 staging，整批驗證成功才原子匯入。相同 group_id + version + hash 重匯不重複；同 ID 同版不同內容是衝突，不能靜默覆寫。
- 跨批也要檢查 item_id 唯一性及 family 用途衝突。歷史版本保留，發布與回滾不改寫既有作答。
- 既有 ID 永不回收。內容／答案／音圖修改須升版，難度數據視改動重新驗證。
- Codex 管理契約與匯入工具；Antigravity 不得單方改欄位。差異寫入 schema-change-request.md，對齊新版本後再切換。契約改動尚未對齊時，繼續做不受影響的工作。

### C. 題組資料模型

每個 group 必填以下欄位，未列擴充先提案。所有列出的陣列可為空，但須通過對應 Part 的語意限制。

| 欄位 | 型別／規則 |
|---|---|
| schema_version | 固定字串 1.0.0 |
| group_id | 永久 ID，例如 ag-g-p3-000001；Codex fixtures 用 cx- 前綴 |
| version | 正整數，從 1 開始 |
| family_id | 同情境／邏輯骨架變體共用，不能靠換 ID 規避近似題偵測 |
| pool | training / battle / diagnostic / mock |
| fixture | boolean；示例與技術測試必須 true |
| part | 整數 1–7 |
| layout | photo / question_response / conversation / talk / sentence / text_completion / single_passage / double_passage / triple_passage |
| scenario | 非空英文短標籤，例如 office_scheduling |
| difficulty | {level: D1–D5, rationale_zh: 字串, basis: editorial}；此版本只有編輯難度，不內嵌假 IRT 參數 |
| content_status | draft / ai_checked / human_reviewed / quarantined / retired |
| stimulus | {documents: 陣列, speakers: 陣列, audio_script: 陣列} |
| assets | 素材陣列，格式見下 |
| items | 非空題目陣列，格式見下 |
| provenance | {origin: original, author_tool: 字串, author_model: 字串, created_at: ISO時間, rights_note_zh: 字串} |
| review_refs | reviews.jsonl 中的 review_id 字串陣列 |

校準狀態由後端另存「版本、參數、樣本、模型、有效日期」，不是作者可自行改成 calibrated 的欄位。content_status 也不等於發布許可。

stimulus.documents 每份格式：
- document_id、genre、title_en（可空字串）、blocks。
- blocks 的每筆為 text 或 table。text 用 {block_id, type:"text", text_en}；table 用 {block_id, type:"table", columns:[字串], rows:[[字串]]}，每列長度與欄數一致。
- 禁止可執行 HTML／JavaScript。文章、表格保持可選取文字，不只提供截圖。
- Part 6 在文字中使用 [[blank:ITEM_ID]] 對應空格，每個小題恰有一個標記。
- Part 7 插句題使用 [[position:SLOT_ID]] 明確標出可插入位置；題目 choice.text_en 引用可見的位置標籤，evidence 指向相關 block。
- Part 3–4 的圖表可用 document/table 呈現，需與音訊數據一致。

stimulus.speakers 每筆為 {speaker_id, role, accent}，accent 為 us / uk / ca / au / unspecified。這是製作標籤，不代表已產生該口音的音檔。
stimulus.audio_script 每筆為 {segment_id, speaker_id, text_en}，speaker_id 必須存在。Part 1／2 必須包含實際會朗讀的選項；Part 2 也包含問題／陳述。Part 3／4 需包含設計要播放的對話／獨白及題目播報段落，時間線另由音訊製作與組卷流程建立。不存在的時間碼不得填造。

每個 item 必填：
- item_id：永久唯一字串。
- prompt_en：題幹；Part 1／2 可用通用指示語，但不能在標準作答畫面洩漏應由音訊提供的內容。
- choices：有序陣列，每筆 {id, text_en}；Part 2 恰為 A/B/C，其餘為 A/B/C/D；不得重複選項。
- answer_choice_id：必須指向其中一個 choice.id。
- skill_tags：非空字串陣列；使用共用 taxonomy，新增標籤需記錄定義。
- evidence：非空陣列，每筆 {source_type, source_id, quote_en, reasoning_zh}。source_type 為 document_block / audio_segment / asset / item_prompt；source_id 指向實際 block_id／segment_id／asset_id／item_id。圖片可 quote_en=""，但 reasoning_zh 要指出可見證據。文法題可指向自身 item_prompt，不得為了填欄位捏造文章。
- explanation_zh：正解理由。
- distractor_notes：每個錯誤選項恰一筆 {choice_id, reason_zh}。
- vocabulary：陣列，每筆 {term_en, meaning_zh, example_en}，可為空。
- estimated_time_sec：正整數或 null，為編輯預估，不是個人能力證據，也不能機械相加冒充正式聽力長度。

每個 asset 必填：
- asset_id、kind（image / audio）、status（planned / ready）。
- path：planned 必須 null；ready 必須為包內實際相對檔案路徑。
- sha256：planned 必須 null；ready 必須為真實檔案雜湊。
- mime_type：planned 可 null；ready 必須和檔案一致。
- duration_ms：audio ready 為正整數，其餘 null。
- source_note_zh：實際來源、工具與必要權利紀錄，不能把未知授權寫成已授權。
- review_state：pending / ai_checked / human_reviewed。
- segment_times：陣列 {segment_id, start_ms, end_ms}，可空；若提供，必須對應真實音檔與 audio_script，時間範圍有效。逐句播放功能依實際時間碼啟用。

### D. 各 Part 的語意限制與顯示

- Part 1：layout=photo，一組一題，須有圖片與音訊；看圖作答，標準模式不顯示朗讀選項文字。
- Part 2：layout=question_response，一組一題，三選一，須有音訊；標準模式不顯示問題稿及選項稿。
- Part 3：layout=conversation，一組恰三題，至少兩位實際對話角色，另可有旁白。
- Part 4：layout=talk，一組恰三題，主體是單人獨白，另可有旁白。
- Part 5：layout=sentence，一組一題，空格在 prompt_en 以 ____ 表示。
- Part 6：layout=text_completion，一組恰四題，含連貫文章和四個對應 blank。
- Part 7：single_passage 一份文件、2–4 題；double_passage 兩份文件、5 題；triple_passage 三份文件、5 題。每份正式模考單篇 29 題，多篇 25 題；四份卷都涵蓋雙篇與三篇。
- Part 1–4 缺 ready 音訊、Part 1 缺 ready 圖片時，可作私有草稿／技術預覽，不得宣稱完整聽力可用。
- 播放時間線包含朗讀、指示與作答停頓；正式聽力的約 45 分鐘是整套時間線，不是任意把每題秒數相加。
- 考試／競技客戶端只取得允許顯示的內容。答案、解析、逐字稿及證據按模式與階段解鎖。
- 私有原始包可同時有題幹、稿件及答案；發布時必須投影成客戶端安全資料，不能僅用 UI 隱藏敏感欄位。

### E. 審查紀錄與發布門檻

reviews.jsonl 每行：
{review_id, group_id, group_version, item_ids, reviewer_kind, reviewer_name, reviewer_model, reviewed_at, blind, verdict, findings}

- reviewer_kind 為 ai / human / program；模型不適用時 reviewer_model=null。
- verdict 為 pass / revise / reject；findings 為 {item_id:字串或null, severity:info|warning|error, code:字串, note_zh:字串} 陣列。
- blind 只有真的先隱藏正解／解析、保存獨立解題結果後，才能 true；用自己的答案再讀一次不能叫盲解。
- 真正盲解的個別答案與證據保存在 reports/ 下並列入 manifest，供比對。
- 不得編造人工審閱者、模型呼叫、試聽、測試或通過紀錄。
- AI 檢查通過最多為 ai_checked。沒有實際人工審閱就不能標 human_reviewed。
- 開發預覽可展示 draft；封閉試用可在明示「AI 審核、未校準」後使用合格的 ai_checked 練習題，不能默認用於可信估分。
- 人工確認內容可用不代表已完成統計校準。可靠程度評估另需實測證據。
- 重大歧義、矛盾、缺答案證據、缺必要素材一律隔離。
- 檢查答案位置分布，但只作批次異常警訊，不強制改答案來湊均勻。
- 去重先檢查完全相同／正規化文字，再檢查語意與題目家族近似；語意近似是待審訊號，不是只靠單一分數自動刪題。

### F. 難度與學習證據

D1 基礎辨識；D2 常見句構與直接理解；D3 改寫與跨句關聯；D4 多條件整合與推論；D5 高干擾、細微語意與實戰速度下的綜合理解。每個 Part 都需有合理的分級，不能把 Part 5 的文法標準直接套到聽力。

training 的初始編輯配置目標：D1 15%、D2 25%、D3 20%、D4 15%、D5 25%。這不是官方比例，也不是個人一定看到的比例；依真實品質與能力覆蓋調整，不能硬湊不合理難題。其餘池以用途命題，不強套此比例。

- 原創題保持日常／職場英語，難度不得靠罕見專業知識、錯誤文法或不自然語音。
- 選擇題須有唯一最佳答案；高難度來自改寫、合理干擾、意圖、資訊整合，不來自歧義。
- 重做、提示、慢速、重播、已看稿、題目家族曝光及中斷要記錄。
- 用過的題目可複習，不能再當作全新能力證據。測驗池耗盡須顯示不足或補題，不以近似題灌水。
- 不使用 correct_rate × 990，也不把 D5 叫作「990 分題」。
- 官方分數的預測需要獨立外部成績驗證；初期只提供程度、弱點與證據充分度。
- 990 是完整訓練路徑的目標，不保證每位使用者必得滿分。

### G. 共同參考來源

這些是研究入口，不是可任意複製進 App 的題庫。執行時可讀取公開官方規格；不抄寫付費題庫或宣稱取得 ETS 內部題目。
- TOEIC 題型與題數：https://toeic.com.tw/toeic/listening-reading/about/content/
- ETS 成績與測驗指南：https://www.ets.org/content/dam/ets-org/pdfs/toeic/toeic-listening-reading-score-user-guide.pdf
- ETS 公開樣題入口：https://toeic.com.tw/sample-test/toeic-listening-reading/sample01.html
- ETS 小樣本校準研究：https://www.ets.org/research/policy_research_reports/publications/report/2024/kgvw.html
- Apple 介面材質：https://developer.apple.com/design/human-interface-guidelines/materials

### H. 首版共用能力標籤（避免兩邊自行取不同名字）

skill_tags 從下列字串選用，一題通常 1–3 個。新增標籤必須先在 taxonomy 版本記錄定義，不能把相似標籤無限增生。

| 標籤 | 意義 |
|---|---|
| photo_action | 圖片中的動作 |
| photo_state_location | 圖片中的狀態與位置 |
| question_function | 辨識問句／陳述的溝通功能 |
| direct_response | 直接回應 |
| indirect_response | 間接回應 |
| main_idea_purpose | 主旨與目的 |
| explicit_detail | 明示細節 |
| paraphrase | 同義改寫 |
| speaker_intent | 說話者意圖 |
| next_action | 下一步行動 |
| inference | 有文本依據的推論 |
| graphic_integration | 音訊與圖表整合 |
| word_form | 詞性與字形 |
| verb_form_agreement | 動詞形式、時態與一致性 |
| preposition_collocation | 介系詞與搭配 |
| connector_clause | 連接詞與子句關係 |
| vocabulary_in_context | 語境詞義 |
| reference_cohesion | 指涉與篇章連貫 |
| sentence_insertion | 句子插入 |
| cross_document | 跨文件整合 |
| conditions_exceptions | 條件與例外 |
| chronology | 時序關係 |

速度、口音與情境是作答／素材維度，不以未驗證的技能分數混入上述標籤。diagnostic 的粗略剖面可聚合相關標籤，樣本不足顯示尚未測足。

