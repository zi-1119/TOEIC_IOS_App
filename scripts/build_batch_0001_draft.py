#!/usr/bin/env python3
"""
Construct draft groups.jsonl for batch-ag-0001:
First 20 items of the Phase 1 100-item trial (pool="training", fixture=false):
- Part 2: 8 items (ag-g-p2-000001 .. ag-g-p2-000008)
- Part 5: 12 items (ag-g-p5-000001 .. ag-g-p5-000012)
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CREATED_AT = "2026-10-27T11:48:00Z"


def make_provenance() -> dict:
    return {
        "origin": "original",
        "author_tool": "antigravity-toeic-factory/1.0.0",
        "author_model": "unknown",
        "created_at": CREATED_AT,
        "rights_note_zh": "本題組為本專案原創命題內容，未抄襲 ETS 官方試題、商業出版品或第三方付費題庫。",
    }


def make_part2_group(
    num: int,
    family_id: str,
    scenario: str,
    diff_level: str,
    diff_rationale_zh: str,
    q_accent: str,
    r_accent: str,
    q_role: str,
    r_role: str,
    question_en: str,
    choices_map: dict,
    ans: str,
    skill_tags: list,
    reasoning_zh: str,
    explanation_zh: str,
    distractor_map: dict,
    vocab: list,
) -> dict:
    gid = f"ag-g-p2-{num:06d}"
    iid = f"ag-i-p2-{num:06d}-1"
    aid = f"ag-ast-p2-{num:06d}-audio"
    seg_q = f"{gid}-seg-q"
    seg_a = f"{gid}-seg-a"
    seg_b = f"{gid}-seg-b"
    seg_c = f"{gid}-seg-c"
    ans_seg = {"A": seg_a, "B": seg_b, "C": seg_c}[ans]

    return {
        "schema_version": "1.0.0",
        "group_id": gid,
        "version": 1,
        "family_id": family_id,
        "pool": "training",
        "fixture": False,
        "part": 2,
        "layout": "question_response",
        "scenario": scenario,
        "difficulty": {
            "level": diff_level,
            "rationale_zh": diff_rationale_zh,
            "basis": "editorial",
        },
        "content_status": "draft",
        "stimulus": {
            "documents": [],
            "speakers": [
                {"speaker_id": "spk_q", "role": q_role, "accent": q_accent},
                {"speaker_id": "spk_r", "role": r_role, "accent": r_accent},
            ],
            "audio_script": [
                {"segment_id": seg_q, "speaker_id": "spk_q", "text_en": question_en},
                {"segment_id": seg_a, "speaker_id": "spk_r", "text_en": choices_map["A"]},
                {"segment_id": seg_b, "speaker_id": "spk_r", "text_en": choices_map["B"]},
                {"segment_id": seg_c, "speaker_id": "spk_r", "text_en": choices_map["C"]},
            ],
        },
        "assets": [
            {
                "asset_id": aid,
                "kind": "audio",
                "status": "planned",
                "path": None,
                "sha256": None,
                "mime_type": None,
                "duration_ms": None,
                "source_note_zh": (
                    f"待合成雙人應答音檔（發問者口音規劃：{q_accent}，回應者口音規劃：{r_accent}）；"
                    "已完成完整朗讀文字稿，尚未產生實體音檔。"
                ),
                "review_state": "pending",
                "segment_times": [],
            }
        ],
        "items": [
            {
                "item_id": iid,
                "prompt_en": "Listen to the question or statement and choose the best response.",
                "choices": [
                    {"id": "A", "text_en": choices_map["A"]},
                    {"id": "B", "text_en": choices_map["B"]},
                    {"id": "C", "text_en": choices_map["C"]},
                ],
                "answer_choice_id": ans,
                "skill_tags": skill_tags,
                "evidence": [
                    {
                        "source_type": "audio_segment",
                        "source_id": seg_q,
                        "quote_en": question_en,
                        "reasoning_zh": reasoning_zh,
                    },
                    {
                        "source_type": "audio_segment",
                        "source_id": ans_seg,
                        "quote_en": choices_map[ans],
                        "reasoning_zh": "此回應切合發問語意與職場情境。",
                    },
                ],
                "explanation_zh": explanation_zh,
                "distractor_notes": [
                    {"choice_id": k, "reason_zh": v}
                    for k, v in distractor_map.items()
                ],
                "vocabulary": vocab,
                "estimated_time_sec": 12,
            }
        ],
        "provenance": make_provenance(),
        "review_refs": [],
    }


def make_part5_group(
    num: int,
    family_id: str,
    scenario: str,
    diff_level: str,
    diff_rationale_zh: str,
    prompt_en: str,
    choices_map: dict,
    ans: str,
    skill_tags: list,
    quote_en: str,
    reasoning_zh: str,
    explanation_zh: str,
    distractor_map: dict,
    vocab: list,
    est_sec: int = 20,
) -> dict:
    gid = f"ag-g-p5-{num:06d}"
    iid = f"ag-i-p5-{num:06d}-1"
    return {
        "schema_version": "1.0.0",
        "group_id": gid,
        "version": 1,
        "family_id": family_id,
        "pool": "training",
        "fixture": False,
        "part": 5,
        "layout": "sentence",
        "scenario": scenario,
        "difficulty": {
            "level": diff_level,
            "rationale_zh": diff_rationale_zh,
            "basis": "editorial",
        },
        "content_status": "draft",
        "stimulus": {
            "documents": [],
            "speakers": [],
            "audio_script": [],
        },
        "assets": [],
        "items": [
            {
                "item_id": iid,
                "prompt_en": prompt_en,
                "choices": [
                    {"id": "A", "text_en": choices_map["A"]},
                    {"id": "B", "text_en": choices_map["B"]},
                    {"id": "C", "text_en": choices_map["C"]},
                    {"id": "D", "text_en": choices_map["D"]},
                ],
                "answer_choice_id": ans,
                "skill_tags": skill_tags,
                "evidence": [
                    {
                        "source_type": "item_prompt",
                        "source_id": iid,
                        "quote_en": quote_en,
                        "reasoning_zh": reasoning_zh,
                    }
                ],
                "explanation_zh": explanation_zh,
                "distractor_notes": [
                    {"choice_id": k, "reason_zh": v}
                    for k, v in distractor_map.items()
                ],
                "vocabulary": vocab,
                "estimated_time_sec": est_sec,
            }
        ],
        "provenance": make_provenance(),
        "review_refs": [],
    }


def build_groups() -> list:
    groups = [
        # --- PART 2: 8 ITEMS ---
        make_part2_group(
            num=1,
            family_id="ag-fam-p2-wh-where-warehouse-manifest",
            scenario="logistics_shipping",
            diff_level="D1",
            diff_rationale_zh="基礎 Where 地點疑問句，正解以明確位置介系詞片語直接回應，適合檢測基本疑問詞聽辨。",
            q_accent="us",
            r_accent="uk",
            q_role="warehouse_supervisor",
            r_role="shipping_clerk",
            question_en="Where did you leave the signed shipping manifests?",
            choices_map={
                "A": "In the top tray on Ms. Henderson's desk.",
                "B": "Before the courier arrives at noon.",
                "C": "No, the shipment hasn't been weighed.",
            },
            ans="A",
            skill_tags=["question_function", "direct_response"],
            reasoning_zh="發問者以 Where 詢問已簽署貨運清單的放置地點，選項 A 明確指出在 Henderson 女士桌上的最上層文件盤。",
            explanation_zh="題幹詢問「你把簽好名的貨運清單放在哪裡？」，屬於地點疑問句（Where）。(A) 以介系詞片語「在 Henderson 女士桌上的最上層文件盤裡」直接指出位置，為唯一合乎邏輯的回應。",
            distractor_map={
                "B": "以時間副詞子句回答（在快遞中午前抵達之前），適用於 When 疑問句而非 Where。",
                "C": "以 No 開頭並利用 shipping / shipment 同字根語音干擾，但 WH 疑問句不可用 Yes/No 回答。",
            },
            vocab=[
                {
                    "term_en": "shipping manifest",
                    "meaning_zh": "貨運清單；載貨單",
                    "example_en": "Please verify the item count against the shipping manifest.",
                }
            ],
        ),
        make_part2_group(
            num=2,
            family_id="ag-fam-p2-wh-when-equipment-calibration",
            scenario="maintenance_inspection",
            diff_level="D2",
            diff_rationale_zh="When 被動語態問句，考驗聽辨未來時間表達，並排除發音相近字（calibrated / collaborated）干擾。",
            q_accent="uk",
            r_accent="us",
            q_role="lab_manager",
            r_role="maintenance_technician",
            question_en="When will the pressure gauges in Building C be calibrated?",
            choices_map={
                "A": "They collaborated on the quarterly report.",
                "B": "Next Tuesday morning during the scheduled shutdown.",
                "C": "At the main engineering warehouse.",
            },
            ans="B",
            skill_tags=["question_function", "direct_response"],
            reasoning_zh="發問者以 When will 詢問 C 棟壓力錶何時校準，選項 B 提供未來具體時段「下週二上午例行停機期間」。",
            explanation_zh="題幹詢問「C 棟的壓力錶何時會進行校準？」，核心疑問詞為 When will。(B) 明確回答未來時間「下週二早上例行停機維護期間」，時態與語意完全吻合。",
            distractor_map={
                "A": "利用 collaborated（合作）與題幹 calibrated（校準）的諧音設下聽力陷阱，且時態為過去式，語意無關。",
                "C": "回答的是地點（在主工程倉庫），誤將 When 聽成 Where。",
            },
            vocab=[
                {
                    "term_en": "calibrate",
                    "meaning_zh": "校準；校正（儀器）",
                    "example_en": "All laboratory scales must be calibrated every six months.",
                },
                {
                    "term_en": "pressure gauge",
                    "meaning_zh": "壓力錶；壓力計",
                    "example_en": "Check the pressure gauge before opening the valve.",
                },
            ],
        ),
        make_part2_group(
            num=3,
            family_id="ag-fam-p2-wh-who-vendor-contract-review",
            scenario="procurement_contract",
            diff_level="D3",
            diff_rationale_zh="Who 疑問句搭配間接回應（說明法務主管今日休假故尚未指派），需理解職場指派流程而非單純找人名。",
            q_accent="ca",
            r_accent="us",
            q_role="procurement_officer",
            r_role="legal_assistant",
            question_en="Who was assigned to review the raw material supplier's contract?",
            choices_map={
                "A": "Yes, we signed the lease last month.",
                "B": "A three-year renewal option.",
                "C": "The legal director is out today, so no one yet.",
            },
            ans="C",
            skill_tags=["question_function", "indirect_response"],
            reasoning_zh="發問者詢問誰被指派審查原物料供應商合約，選項 C 說明「法務總監今天不在，所以目前還沒指派任何人」，屬於自然合理的間接回應。",
            explanation_zh="題幹以 Who was assigned 詢問負責審查供應商合約的人選。(C) 雖未直接給出人名，但說明「法務總監今天休假外出，因此目前尚未指派任何人（no one yet）」，符合真實職場溝通邏輯。",
            distractor_map={
                "A": "利用 signed 與 assigned 的語音相似性干擾，且 Who 問句不得以 Yes 回應。",
                "B": "僅提及合約條款內容（三年續約選擇權），未回答負責審查的人員是誰。",
            },
            vocab=[
                {
                    "term_en": "raw material",
                    "meaning_zh": "原物料",
                    "example_en": "Rising raw material costs affected our third-quarter margins.",
                }
            ],
        ),
        make_part2_group(
            num=4,
            family_id="ag-fam-p2-yesno-invoice-reimbursement",
            scenario="finance_reimbursement",
            diff_level="D2",
            diff_rationale_zh="否定疑問句（Hasn't...），正解省略 Yes/No 直接說明會計部門今日稍早已完成核准，考驗語意改寫。",
            q_accent="us",
            r_accent="au",
            q_role="sales_representative",
            r_role="accounting_clerk",
            question_en="Hasn't the travel expense reimbursement been approved yet?",
            choices_map={
                "A": "Accounting cleared it earlier this afternoon.",
                "B": "To the regional conference in Seattle.",
                "C": "Direct flights are usually more expensive.",
            },
            ans="A",
            skill_tags=["question_function", "direct_response", "paraphrase"],
            reasoning_zh="發問者詢問差旅費報銷是否尚未核准，選項 A 以 cleared it（已核准放行）同義改寫 approved，直接告知今天下午稍早已通過。",
            explanation_zh="題幹為否定是非問句「差旅費報銷還沒核准嗎？」。在英文自然口語中，回應常省略 Yes/No 而直接陳述事實。(A) 中 Accounting cleared it 即「會計部今天下午稍早已經審核通過了」，以 cleared 同義改寫 approved。",
            distractor_map={
                "B": "受題幹 travel 一詞聯想干擾，回答出差目的地（前往西雅圖的區域會議），文不對題。",
                "C": "利用 expense / expensive 同字根聯想干擾，討論直飛班機票價，與報銷審核進度無關。",
            },
            vocab=[
                {
                    "term_en": "reimbursement",
                    "meaning_zh": "報銷；核銷補償款",
                    "example_en": "Submit your hotel receipts for full reimbursement.",
                }
            ],
        ),
        make_part2_group(
            num=5,
            family_id="ag-fam-p2-choice-catering-menu-selection",
            scenario="event_catering",
            diff_level="D3",
            diff_rationale_zh="選擇問句（A or B），正解不選其一，而是指出活動人數上限與預算尚未最終確認，屬典型間接回應。",
            q_accent="au",
            r_accent="uk",
            q_role="event_planner",
            r_role="department_head",
            question_en="Should we order boxed lunches or a hot buffet for the client seminar?",
            choices_map={
                "A": "Wait until we get the final headcount this afternoon.",
                "B": "Yes, the seminar speaker confirmed her topic.",
                "C": "Put the extra boxes in the storage closet.",
            },
            ans="A",
            skill_tags=["question_function", "indirect_response"],
            reasoning_zh="發問者詢問客戶研討會應訂購餐盒還是熱食自助餐，選項 A 建議「等今天下午拿到最終出席人數再決定」，合理解釋為何暫緩二選一。",
            explanation_zh="題幹為 A or B 選擇問句，詢問應訂購盒餐或自助餐。(A) 指示「等到今天下午確認最終出席人數（final headcount）後再決定」，是商務籌備情境中非常自然的暫緩決策回應。",
            distractor_map={
                "B": "選擇問句不可用 Yes/No 回答，且內容談論講者講題，與餐飲形式無關。",
                "C": "重複題幹 boxed lunches 中的 box 字眼，但語意為「把多餘紙箱放進儲藏室」，屬同詞干擾。",
            },
            vocab=[
                {
                    "term_en": "headcount",
                    "meaning_zh": "出席人數；總人數",
                    "example_en": "The caterer needs an accurate headcount forty-eight hours in advance.",
                }
            ],
        ),
        make_part2_group(
            num=6,
            family_id="ag-fam-p2-request-projector-setup-help",
            scenario="it_support",
            diff_level="D2",
            diff_rationale_zh="禮貌請求句（Could you...），正解欣然答應並指出具體排查動作，干擾項測試多義詞與近音詞。",
            q_accent="us",
            r_accent="ca",
            q_role="training_coordinator",
            r_role="it_specialist",
            question_en="Could you check why the ceiling projector isn't connecting to my laptop?",
            choices_map={
                "A": "Sure, let me see if the display cable is loose.",
                "B": "The architectural project was approved in May.",
                "C": "No, on the top shelf.",
            },
            ans="A",
            skill_tags=["question_function", "direct_response"],
            reasoning_zh="發問者請求協助檢查天花板投影機無法連接筆電的原因，選項 A 答應並表示先檢查顯示器連接線是否鬆脫。",
            explanation_zh="題幹以 Could you check... 提出協助排除設備故障的請求。(A) 以 Sure 答應請求，並提出具體檢查步驟（看看顯示傳輸線是否鬆脫），完全契合 IT 支援語境。",
            distractor_map={
                "B": "利用 project（專案）與題幹 projector（投影機）的字形語音相近設下干擾。",
                "C": "受 ceiling（天花板）空間詞聯想出 on the top shelf（在最上層架子），語意不合請求。",
            },
            vocab=[
                {
                    "term_en": "loose",
                    "meaning_zh": "鬆脫的；未接緊的",
                    "example_en": "A loose power cord caused the monitor to flicker.",
                }
            ],
        ),
        make_part2_group(
            num=7,
            family_id="ag-fam-p2-suggestion-retail-display-window",
            scenario="retail_merchandising",
            diff_level="D4",
            diff_rationale_zh="Why don't we 提議句，正解不直接說好或不好，而是提出前置條件（秋季促銷立牌週四才到貨）間接延後提議。",
            q_accent="uk",
            r_accent="au",
            q_role="store_associate",
            r_role="visual_merchandiser",
            question_en="Why don't we update the front window display before the store opens tomorrow?",
            choices_map={
                "A": "Because the main entrance faces Oak Street.",
                "B": "The autumn promotional banners won't arrive until Thursday.",
                "C": "Yes, I updated my contact information.",
            },
            ans="B",
            skill_tags=["question_function", "indirect_response", "speaker_intent"],
            reasoning_zh="發問者提議明天開店前更新櫥窗陳列，選項 B 指出「秋季促銷橫幅要到週四才會送達」，間接表達明天尚無法更新。",
            explanation_zh="題幹以 Why don't we... 提出行動建議（明天營業前更換前排櫥窗展示），並非詢問原因的真 Why 問句。(B) 指出關鍵展示素材（秋季促銷橫幅）週四才會寄達，婉轉說明為何明天無法執行該提議。",
            distractor_map={
                "A": "誤將 Why don't we 提議句當成詢問原因的疑問句，而以 Because 回答大門朝向，邏輯不通。",
                "C": "重複題幹動詞 update，但談論的是更新個人聯絡資料，與店面櫥窗陳列無關。",
            },
            vocab=[
                {
                    "term_en": "promotional banner",
                    "meaning_zh": "促銷橫幅；宣傳布條",
                    "example_en": "Hang the promotional banner above the seasonal clearance rack.",
                }
            ],
        ),
        make_part2_group(
            num=8,
            family_id="ag-fam-p2-statement-hotel-shuttle-full",
            scenario="hospitality_transport",
            diff_level="D5",
            diff_rationale_zh="職場陳述句（指出八點機場接駁車已客滿），需推論說話者背後有搭車需求，並辨識干擾項中 book 的一詞多義陷阱。",
            q_accent="ca",
            r_accent="uk",
            q_role="hotel_guest",
            r_role="concierge",
            question_en="The eight o'clock airport shuttle is completely booked.",
            choices_map={
                "A": "I read that book on my flight home.",
                "B": "Terminal Two handles all international departures.",
                "C": "There's still room in the eight-thirty van if that works for you.",
            },
            ans="C",
            skill_tags=["question_function", "indirect_response", "speaker_intent"],
            reasoning_zh="房客或櫃檯人員陳述八點鐘的機場接駁車已全滿，選項 C 立即提供八點半廂型車仍有空位的替代方案，展現高自然度服務應對。",
            explanation_zh="題幹為陳述句「八點鐘的機場接駁車已經預約額滿了（completely booked）」。(C) 針對客滿的困境，主動提出替代解決方案：「八點半的廂型車還有空位（still room），看您是否方便」，語用銜接最自然。",
            distractor_map={
                "A": "利用 booked（預訂客滿）與名詞 book（書本）的一詞多義設下經典聽力陷阱。",
                "B": "受 airport 一詞聯想出第二航廈辦理國際線出境，未能回應接駁車客滿的問題。",
            },
            vocab=[
                {
                    "term_en": "completely booked",
                    "meaning_zh": "預訂一空；客滿",
                    "example_en": "All ocean-view suites are completely booked for the holiday weekend.",
                }
            ],
        ),
        # --- PART 5: 12 ITEMS ---
        make_part5_group(
            num=1,
            family_id="ag-fam-p5-wordform-adverb-modify-verb",
            scenario="manufacturing_quality",
            diff_level="D1",
            diff_rationale_zh="基礎詞性題，空格位於助動詞與過去分詞之間，需填入副詞修飾被動動詞。",
            prompt_en="Every batch of ceramic insulators is ____ inspected for microscopic cracks before leaving the factory floor.",
            choices_map={
                "A": "thorough",
                "B": "thoroughly",
                "C": "thoroughness",
                "D": "more thorough",
            },
            ans="B",
            skill_tags=["word_form"],
            quote_en="is ____ inspected for microscopic cracks",
            reasoning_zh="空格夾在 be 動詞 is 與過去分詞 inspected 之間，結構完整，須用副詞 thoroughly 修飾動詞 inspected。",
            explanation_zh="本題考詞性判斷（Word Form）。空格位於被動語態 `is ____ inspected` 中間，用來修飾過去分詞 `inspected`（被檢查），說明檢查的方式與程度，因此必須填入副詞 **(B) thoroughly**（徹底地、仔細地）。",
            distractor_map={
                "A": "thorough 為形容詞（徹底的），不可直接修飾動詞分詞 inspected。",
                "C": "thoroughness 為抽象名詞（徹底性），放入後造成句子結構錯誤。",
                "D": "more thorough 為形容詞比較級，同樣無法修飾動詞 inspected（需為 more thoroughly）。",
            },
            vocab=[
                {
                    "term_en": "insulator",
                    "meaning_zh": "絕緣體；隔熱材",
                    "example_en": "Ceramic insulators are tested under high voltage.",
                },
                {
                    "term_en": "microscopic",
                    "meaning_zh": "極微小的；顯微鏡可見的",
                    "example_en": "The sensor detects microscopic defects on the glass surface.",
                },
            ],
        ),
        make_part5_group(
            num=2,
            family_id="ag-fam-p5-verb-subject-agreement-prepositional",
            scenario="corporate_training",
            diff_level="D2",
            diff_rationale_zh="考驗主詞與動詞單複數一致性；真正主詞為單數名詞 A comprehensive list，後接複數介系詞片語 of optional workshops 作為干擾。",
            prompt_en="A comprehensive list of optional leadership workshops ____ posted on the employee intranet every quarter.",
            choices_map={
                "A": "are",
                "B": "were",
                "C": "is",
                "D": "have been",
            },
            ans="C",
            skill_tags=["verb_form_agreement"],
            quote_en="A comprehensive list of optional leadership workshops ____ posted ... every quarter.",
            reasoning_zh="主詞核心為單數名詞 list（而非介系詞受詞 workshops），且句尾 every quarter 表例行常態，故需用第三人稱單數現在式被動助動詞 is。",
            explanation_zh="本題考主詞與動詞一致性及時態。主詞片語 `A comprehensive list of optional leadership workshops` 的核心主詞為單數可數名詞 **list**（清單），而非介系詞 `of` 後方的複數名詞 `workshops`。加上句尾時間副詞 `every quarter`（每季）表示經常性慣例，應使用現在簡單式單數被動語態 `is posted`，故選 **(C) is**。",
            distractor_map={
                "A": "are 為複數動詞，誤將緊鄰空格的複數名詞 workshops 當成主詞。",
                "B": "were 為過去式複數動詞，既不符合單數主詞 list，也與常態時間副詞 every quarter 不合。",
                "D": "have been 為複數現在完成式助動詞，與單數主詞 list 不一致。",
            },
            vocab=[
                {
                    "term_en": "comprehensive",
                    "meaning_zh": "全面的；詳盡的",
                    "example_en": "New hires receive a comprehensive guide to company benefits.",
                }
            ],
        ),
        make_part5_group(
            num=3,
            family_id="ag-fam-p5-prep-collocation-compliance",
            scenario="public_facilities_safety",
            diff_level="D2",
            diff_rationale_zh="常見商務複合介系詞片語搭配（in accordance with 依照／符合），考驗固定結構辨識。",
            prompt_en="All emergency exit corridors must remain unobstructed at all times in ____ with municipal fire safety codes.",
            choices_map={
                "A": "accordance",
                "B": "authority",
                "C": "admission",
                "D": "observation",
            },
            ans="A",
            skill_tags=["preposition_collocation"],
            quote_en="in ____ with municipal fire safety codes",
            reasoning_zh="in accordance with 為固定商務與法規介系詞片語，意為「依照、符合（法規或規定）」。",
            explanation_zh="本題考商務固定片語搭配。`in accordance with + 名詞` 為多益常考的正式書面片語，意為「依照……；符合……規定」。句意為「所有緊急逃生走廊必須隨時保持暢通無阻，以符合市政消防安全法規」，故選 **(A) accordance**。",
            distractor_map={
                "B": "authority（權限、當局）常搭配 under the authority of，不構成 in authority with。",
                "C": "admission（入場、承認）不與 in ... with 搭配表符合法規。",
                "D": "observation（觀察）若表遵守法規應作 observance（in observance of），且不接 with。",
            },
            vocab=[
                {
                    "term_en": "unobstructed",
                    "meaning_zh": "暢通無阻的；未被遮擋的",
                    "example_en": "Keep the loading dock entrance unobstructed during delivery hours.",
                },
                {
                    "term_en": "in accordance with",
                    "meaning_zh": "依照；符合",
                    "example_en": "Refunds are issued in accordance with our return policy.",
                },
            ],
        ),
        make_part5_group(
            num=4,
            family_id="ag-fam-p5-connector-concession-despite-although",
            scenario="logistics_weather",
            diff_level="D3",
            diff_rationale_zh="考驗從屬連接詞與介系詞、轉折副詞的句法區辨；空格後為完整子句（主詞 heavy fog + 動詞 delayed）。",
            prompt_en="____ heavy fog delayed morning cargo flights out of Anchorage, the perishable seafood shipment still reached Chicago on schedule.",
            choices_map={
                "A": "Despite",
                "B": "Even though",
                "C": "In spite of",
                "D": "Nevertheless",
            },
            ans="B",
            skill_tags=["connector_clause"],
            quote_en="____ heavy fog delayed morning cargo flights out of Anchorage,",
            reasoning_zh="逗號前包含主詞 heavy fog 與及物動詞 delayed，為完整副詞子句，必須由從屬連接詞 Even though 引導。",
            explanation_zh="本題考讓步連接詞與介系詞的用法差異。觀察逗號前半句：`heavy fog`（濃霧）為主詞，`delayed`（延誤了）為限定動詞，`morning cargo flights` 為受詞，構成完整的子句。因此空格必須填入能引導完整副詞子句的從屬連接詞 **(B) Even though**（儘管）。",
            distractor_map={
                "A": "Despite（儘管）為介系詞，後方只能接名詞片語或動名詞（V-ing），不可接含動詞 delayed 的完整子句。",
                "C": "In spite of（儘管）同樣為介系詞片語，不可直接引導完整子句。",
                "D": "Nevertheless（然而、儘管如此）為轉折副詞，通常置於第二句句首並以逗號隔開，無法連接兩個無對等連接詞的子句。",
            },
            vocab=[
                {
                    "term_en": "perishable",
                    "meaning_zh": "易腐壞的（生鮮食品等）",
                    "example_en": "Perishable goods must be stored in refrigerated containers.",
                }
            ],
        ),
        make_part5_group(
            num=5,
            family_id="ag-fam-p5-vocab-adj-confidential-records",
            scenario="hr_personnel",
            diff_level="D2",
            diff_rationale_zh="考驗字形相近形容詞（confidential vs confident）在人事薪資檔案語境中的詞義辨析。",
            prompt_en="Access to ____ employee payroll and performance appraisal files is restricted to authorized human resources personnel.",
            choices_map={
                "A": "confident",
                "B": "confidential",
                "C": "cordial",
                "D": "consecutive",
            },
            ans="B",
            skill_tags=["vocabulary_in_context"],
            quote_en="Access to ____ employee payroll and performance appraisal files is restricted",
            reasoning_zh="修飾員工薪資與績效考核檔案，且後方說明僅限授權人資人員存取，故應為「機密的（confidential）」。",
            explanation_zh="本題考形容詞語境詞義與字形相近字辨析。句意為「存取______員工薪資與績效考核檔案的權限，僅限於獲授權的人力資源人員」。因為涉及薪資與考績且限制存取權限，檔案性質必為「機密的」，故選 **(B) confidential**。",
            distractor_map={
                "A": "confident 意為「有自信的、確信的」，通常用來形容人（如 a confident speaker），不可修飾檔案。",
                "C": "cordial 意為「熱誠的、友好的」（如 a cordial welcome），與資訊權限控管無關。",
                "D": "consecutive 意為「連續不斷的」（如 three consecutive days），放入此處語意不通。",
            },
            vocab=[
                {
                    "term_en": "confidential",
                    "meaning_zh": "機密的；保密的",
                    "example_en": "All client financial records are kept strictly confidential.",
                },
                {
                    "term_en": "performance appraisal",
                    "meaning_zh": "績效考核；工作評估",
                    "example_en": "Annual performance appraisals take place in December.",
                },
            ],
        ),
        make_part5_group(
            num=6,
            family_id="ag-fam-p5-wordform-noun-object-after-adj",
            scenario="real_estate_leasing",
            diff_level="D1",
            diff_rationale_zh="基礎名詞詞性題，空格位於及物動詞 require 與形容詞 prior 之後、介系詞 from 之前，需填入名詞作受詞。",
            prompt_en="Commercial tenants wishing to install exterior signage must obtain written ____ from the building management office.",
            choices_map={
                "A": "authorize",
                "B": "authorized",
                "C": "authorizing",
                "D": "authorization",
            },
            ans="D",
            skill_tags=["word_form"],
            quote_en="must obtain written ____ from the building management office",
            reasoning_zh="及物動詞 obtain 後方需接名詞作受詞，且過去分詞形容詞 written 修飾該空格，故填入名詞 authorization（授權、許可）。",
            explanation_zh="本題考詞性判斷（Word Form）。空格位於及物動詞 `obtain`（取得）與過去分詞形容詞 `written`（書面的）之後，後方緊接介系詞 `from`，因此空格為 `obtain` 的受詞，須填入名詞 **(D) authorization**（授權書、核准許可）。",
            distractor_map={
                "A": "authorize 為原形動詞（授權），不可作為及物動詞 obtain 的受詞。",
                "B": "authorized 為過去分詞或形容詞（獲授權的），後若無被修飾的名詞則結構不完整。",
                "C": "authorizing 為現在分詞或動名詞，若為動名詞後需接賓語，且不可由形容詞 written 直接修飾。",
            },
            vocab=[
                {
                    "term_en": "exterior signage",
                    "meaning_zh": "外部招牌；戶外標誌",
                    "example_en": "City ordinances regulate the size of exterior signage.",
                }
            ],
        ),
        make_part5_group(
            num=7,
            family_id="ag-fam-p5-verb-future-perfect-by-deadline",
            scenario="construction_renovation",
            diff_level="D4",
            diff_rationale_zh="考驗時間副詞子句 By the time + 現在簡單式時，主要子句應搭配未來完成式（will have V-ed）表達屆時已完成的動作。",
            prompt_en="By the time the flagship retail store reopens in November, the contractors ____ the entire second-floor lighting system.",
            choices_map={
                "A": "replaced",
                "B": "had replaced",
                "C": "will have replaced",
                "D": "are replacing",
            },
            ans="C",
            skill_tags=["verb_form_agreement", "chronology"],
            quote_en="By the time the flagship retail store reopens in November, the contractors ____",
            reasoning_zh="By the time 引導的副詞子句使用現在式 reopens 指涉未來時間點（十一月重新開幕時），主句表示在該未來時間點前已經完成的動作，須用未來完成式 will have replaced。",
            explanation_zh="本題考進階時態與時序關係。句首 `By the time + 主詞 + 現在簡單式動詞 (reopens in November)` 表示「到了未來某個時間點（十一月旗艦店重新開幕時）為止」。主要子句描述在該未來截止點之前將已經完成的工程，必須使用未來完成式 **(C) will have replaced**。",
            distractor_map={
                "A": "replaced 為過去簡單式，與指涉未來時間的 reopens in November 時態衝突。",
                "B": "had replaced 為過去完成式，需搭配 By the time + 過去簡單式（reopened），不適用於未來時間。",
                "D": "are replacing 為現在進行式，無法表達「到了未來某時間點已經完成」的累積完成語意。",
            },
            vocab=[
                {
                    "term_en": "flagship store",
                    "meaning_zh": "旗艦店",
                    "example_en": "The brand's flagship store occupies three floors Downtown.",
                }
            ],
        ),
        make_part5_group(
            num=8,
            family_id="ag-fam-p5-connector-relative-pronoun-whose",
            scenario="customer_warranty",
            diff_level="D3",
            diff_rationale_zh="考驗關係代名詞所有格 whose 的用法：先行詞為 customers，關係子句開頭為無冠詞單數名詞 phrase standard warranty。",
            prompt_en="Customers ____ standard two-year warranty has expired may still purchase an extended maintenance plan at a discounted rate.",
            choices_map={
                "A": "who",
                "B": "whom",
                "C": "whose",
                "D": "which",
            },
            ans="C",
            skill_tags=["connector_clause"],
            quote_en="Customers ____ standard two-year warranty has expired",
            reasoning_zh="先行詞 Customers 與後方名詞片語 standard two-year warranty 為所屬關係（顧客的兩年標準保固），故填所有格關係代名詞 whose。",
            explanation_zh="本題考關係代名詞子句結構。空格前方為先行詞 `Customers`（顧客），空格後方緊接名詞片語 `standard two-year warranty`（標準兩年保固）與動詞 `has expired`（已過期）。因為「保固」屬於「顧客」所有（即 `the customers' standard two-year warranty`），空格需填入關係代名詞所有格 **(C) whose**。",
            distractor_map={
                "A": "who 為關係代名詞主格，後方應直接接動詞或助動詞，不可直接修飾無冠詞名詞片語 standard two-year warranty。",
                "B": "whom 為關係代名詞受格，用於取代關係子句中的受詞，不符合此處所有格結構。",
                "D": "which 的先行詞須為事物而非人（Customers），且亦為代名詞主格／受格而非所有格。",
            },
            vocab=[
                {
                    "term_en": "extended maintenance plan",
                    "meaning_zh": "延長保固維修方案",
                    "example_en": "The extended maintenance plan covers annual parts replacement.",
                }
            ],
        ),
        make_part5_group(
            num=9,
            family_id="ag-fam-p5-vocab-verb-waive-fee",
            scenario="banking_account",
            diff_level="D4",
            diff_rationale_zh="考驗商務金融高頻搭配動詞 waive（免除費用／規定），並排除拼字或語意易混淆的動詞。",
            prompt_en=" Horizon Commercial Bank has agreed to ____ the monthly account maintenance fee for small businesses that maintain a minimum balance of $10,000.",
            choices_map={
                "A": "waive",
                "B": "wander",
                "C": "warrant",
                "D": "withstand",
            },
            ans="A",
            skill_tags=["vocabulary_in_context", "preposition_collocation"],
            quote_en="agreed to ____ the monthly account maintenance fee for small businesses",
            reasoning_zh="waive the fee 為標準商務金融搭配，意為「免除、不收取（帳戶管理費）」。",
            explanation_zh="本題考商務動詞詞義與受詞搭配。空格受詞為 `the monthly account maintenance fee`（每月帳戶管理費），後方條件說明「針對維持最低存款餘額達一萬美元的小型企業」。在銀行與商務語境中，「免除費用或免除規定」的標準用字為 **(A) waive**（`waive a fee / requirement`）。",
            distractor_map={
                "B": "wander 為不及物動詞，意為「漫步、偏離」，不可接費用作受詞。",
                "C": "warrant 意為「使……有正當理由；保證」，與免除每月管理費的優惠條件不符。",
                "D": "withstand 意為「承受、抵擋（壓力或衝擊）」，不與銀行費用搭配。",
            },
            vocab=[
                {
                    "term_en": "waive",
                    "meaning_zh": "免除（費用、規定）；放棄（權利）",
                    "example_en": "The hotel agreed to waive the late checkout fee.",
                },
                {
                    "term_en": "minimum balance",
                    "meaning_zh": "最低存款餘額",
                    "example_en": "Checking accounts below the minimum balance incur a service charge.",
                },
            ],
        ),
        make_part5_group(
            num=10,
            family_id="ag-fam-p5-condition-unless-exception",
            scenario="procurement_purchasing",
            diff_level="D3",
            diff_rationale_zh="考驗條件連接詞省略結構（unless + 過去分詞 accompanied...），需理解報銷審核的例外條件。",
            prompt_en="Reimbursement requests for client entertainment meals will not be processed ____ accompanied by an itemized receipt and a list of attendees.",
            choices_map={
                "A": "unless",
                "B": "whereas",
                "C": "so that",
                "D": "as long as",
            },
            ans="A",
            skill_tags=["connector_clause", "conditions_exceptions"],
            quote_en="will not be processed ____ accompanied by an itemized receipt",
            reasoning_zh="主句為否定（will not be processed 不予處理），後方為必要條件（附上明細收據與出席名單），故需填「除非（unless）」。",
            explanation_zh="本題考條件連接詞與簡化副詞子句邏輯。主句指出「招待客戶餐費的報銷申請將不予受理（will not be processed）」，空格後接簡化分詞片語 `accompanied by an itemized receipt...`（原為 `unless they are accompanied by...`，意為「附上明細收據與出席者名單」）。前後構成「若非／除非具備此條件，否則不予受理」的邏輯，故選 **(A) unless**。",
            distractor_map={
                "B": "whereas（然而、鑑於）表前後兩個完整子句的對比反差，不構成條件省略結構。",
                "C": "so that（以便、為了）表目的，後須接完整子句，且語意與「不予受理」矛盾。",
                "D": "as long as（只要）表正面充分條件，若填入則變成「只要附上收據就不予受理」，語意完全相反。",
            },
            vocab=[
                {
                    "term_en": "itemized receipt",
                    "meaning_zh": "列有逐項明細的收據",
                    "example_en": "Credit card slips without an itemized receipt cannot be reimbursed.",
                }
            ],
        ),
        make_part5_group(
            num=11,
            family_id="ag-fam-p5-verb-participle-reduced-clause",
            scenario="publishing_editorial",
            diff_level="D5",
            diff_rationale_zh="高難度分詞構句（簡化形容詞子句）：主要子句已有助動詞 will be held over，空格修飾主詞 Manuscripts（被提交的稿件），需用過去分詞而非限定過去式動詞。",
            prompt_en="Manuscripts ____ after the Friday editorial deadline will be held over for publication in the following month's issue.",
            choices_map={
                "A": "submit",
                "B": "submitting",
                "C": "submitted",
                "D": "will submit",
            },
            ans="C",
            skill_tags=["verb_form_agreement", "connector_clause"],
            quote_en="Manuscripts ____ after the Friday editorial deadline will be held over",
            reasoning_zh="句子主要動詞為 will be held over，故空格至 deadline 為後位修飾主詞 Manuscripts 的分詞片語；稿件是「被提交」，還原為 which are submitted，簡化後為過去分詞 submitted。",
            explanation_zh="本題考簡化關係子句（分詞後位修飾）。分析全句結構，主詞為 `Manuscripts`（稿件），主要子句的限定動詞為後方的 `will be held over`（將被順延保留）。因此，`____ after the Friday editorial deadline` 為修飾主詞 `Manuscripts` 的後位形容詞片語（原為 `which are submitted after...`）。由於「稿件」是「被提交」的承受者，簡化後須用過去分詞 **(C) submitted**。",
            distractor_map={
                "A": "submit 為原形或現在式動詞，放入後會使單一簡單句出現兩個限定動詞（submit 與 will be held over）。",
                "B": "submitting 為現在分詞表主動，但 manuscripts（稿件）不會自己主動提交東西，語態錯誤。",
                "D": "will submit 為未來式主動動詞，既造成雙動詞語法錯誤，且主動語態亦不合邏輯。",
            },
            vocab=[
                {
                    "term_en": "hold over",
                    "meaning_zh": "延後處理；留待下期",
                    "example_en": "Two agenda items were held over until the next board meeting.",
                }
            ],
        ),
        make_part5_group(
            num=12,
            family_id="ag-fam-p5-vocab-adverb-tentatively-scheduled",
            scenario="event_conference",
            diff_level="D5",
            diff_rationale_zh="高難度副詞語境詞義搭配題，需結合後文「待講者簽證核發後才正式確認」推知目前排程為「暫定地（tentatively）」。",
            prompt_en="The keynote address by Dr. Elena Rostova is ____ scheduled for 9:00 A.M. on Wednesday, pending final confirmation of her international flight.",
            choices_map={
                "A": "tentatively",
                "B": "reluctantly",
                "C": "mutually",
                "D": "stringently",
            },
            ans="A",
            skill_tags=["vocabulary_in_context", "preposition_collocation"],
            quote_en="is ____ scheduled for 9:00 A.M. on Wednesday, pending final confirmation",
            reasoning_zh="逗號後說明 pending final confirmation of her international flight（仍有待其國際航班的最終確認），表示週三上午九點的時段目前只是「暫定排程（tentatively scheduled）」。",
            explanation_zh="本題考進階副詞詞義與商務搭配。句尾關鍵線索為 `pending final confirmation of her international flight`（尚待她國際航班的最終確認），這表示週三早上九點的專題演講時間尚未完全定案，而是「暫定安排在……」。在商務英語中，`tentatively scheduled`（暫定排程）為極高頻的標準搭配，故選 **(A) tentatively**。",
            distractor_map={
                "B": "reluctantly 意為「不情願地、勉為其難地」，不符合會議議程待航班確認的客觀語境。",
                "C": "mutually 意為「相互地、共同地」（常搭配 mutually beneficial / agreed），不與 scheduled for 9:00 A.M. 搭配表待確認。",
                "D": "stringently 意為「嚴格地、嚴苛地」（常搭配 stringently enforced 嚴格執行），與尚待確認的語意矛盾。",
            },
            vocab=[
                {
                    "term_en": "tentatively",
                    "meaning_zh": "暫定地；初步地",
                    "example_en": "The product launch is tentatively set for mid-October.",
                },
                {
                    "term_en": "pending",
                    "meaning_zh": "在……之前；有待……",
                    "example_en": "Construction is on hold pending city council approval.",
                },
            ],
        ),
    ]
    return groups


def main() -> None:
    out_dir = ROOT / "drafts" / "batch-ag-0001"
    out_dir.mkdir(parents=True, exist_ok=True)
    groups = build_groups()
    groups_path = out_dir / "groups.jsonl"
    with groups_path.open("w", encoding="utf-8") as f:
        for g in groups:
            f.write(json.dumps(g, ensure_ascii=False) + "\n")
    print(f"Wrote {len(groups)} groups to {groups_path}")


if __name__ == "__main__":
    main()
