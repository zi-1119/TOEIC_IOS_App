#!/usr/bin/env python3
"""
Construct draft groups.jsonl for batch-ag-0002 (13 groups, 19 items, pool="training"):
- Part 1: 3 groups = 3 items (ag-g-p1-000001 .. ag-g-p1-000003)
- Part 2: 5 groups = 5 items (ag-g-p2-000009 .. ag-g-p2-000013)
- Part 5: 3 groups = 3 items (ag-g-p5-000013 .. ag-g-p5-000015)
- Part 6: 2 groups = 8 items (ag-g-p6-000001 .. ag-g-p6-000002)
"""

import json
from pathlib import Path

from build_batch_0001_draft import make_part2_group, make_part5_group, make_provenance

ROOT = Path(__file__).resolve().parent.parent


def make_part1_group(
    num: int,
    family_id: str,
    scenario: str,
    diff_level: str,
    diff_rationale_zh: str,
    accent: str,
    image_brief_zh_en: str,
    choices_map: dict,
    ans: str,
    skill_tags: list,
    visual_reasoning_zh: str,
    explanation_zh: str,
    distractor_map: dict,
    vocab: list,
) -> dict:
    gid = f"ag-g-p1-{num:06d}"
    iid = f"ag-i-p1-{num:06d}-1"
    img_aid = f"ag-ast-p1-{num:06d}-image"
    aud_aid = f"ag-ast-p1-{num:06d}-audio"
    segs = {
        k: f"{gid}-seg-{k.lower()}" for k in ("A", "B", "C", "D")
    }

    return {
        "schema_version": "1.0.0",
        "group_id": gid,
        "version": 1,
        "family_id": family_id,
        "pool": "training",
        "fixture": False,
        "part": 1,
        "layout": "photo",
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
                {"speaker_id": "spk_narrator", "role": "narrator", "accent": accent}
            ],
            "audio_script": [
                {"segment_id": segs["A"], "speaker_id": "spk_narrator", "text_en": choices_map["A"]},
                {"segment_id": segs["B"], "speaker_id": "spk_narrator", "text_en": choices_map["B"]},
                {"segment_id": segs["C"], "speaker_id": "spk_narrator", "text_en": choices_map["C"]},
                {"segment_id": segs["D"], "speaker_id": "spk_narrator", "text_en": choices_map["D"]},
            ],
        },
        "assets": [
            {
                "asset_id": img_aid,
                "kind": "image",
                "status": "planned",
                "path": None,
                "sha256": None,
                "mime_type": None,
                "duration_ms": None,
                "source_note_zh": image_brief_zh_en,
                "review_state": "pending",
                "segment_times": [],
            },
            {
                "asset_id": aud_aid,
                "kind": "audio",
                "status": "planned",
                "path": None,
                "sha256": None,
                "mime_type": None,
                "duration_ms": None,
                "source_note_zh": f"待合成 Part 1 四選項朗讀音訊（口音規劃：{accent}）；已完成完整英文朗讀稿。",
                "review_state": "pending",
                "segment_times": [],
            },
        ],
        "items": [
            {
                "item_id": iid,
                "prompt_en": "Look at the photograph and listen to the four statements. Choose the statement that best describes what you see in the photograph.",
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
                        "source_type": "asset",
                        "source_id": img_aid,
                        "quote_en": "",
                        "reasoning_zh": visual_reasoning_zh,
                    },
                    {
                        "source_type": "audio_segment",
                        "source_id": segs[ans],
                        "quote_en": choices_map[ans],
                        "reasoning_zh": "此朗讀敘述與照片畫面之可見證據完全相符。",
                    },
                ],
                "explanation_zh": explanation_zh,
                "distractor_notes": [
                    {"choice_id": k, "reason_zh": v}
                    for k, v in distractor_map.items()
                ],
                "vocabulary": vocab,
                "estimated_time_sec": 15,
            }
        ],
        "provenance": make_provenance(),
        "review_refs": [],
    }


def build_groups() -> list:
    groups = [
        # --- PART 1: 3 GROUPS ---
        make_part1_group(
            num=1,
            family_id="ag-fam-p1-laboratory-technician-microscope",
            scenario="research_laboratory",
            diff_level="D1",
            diff_rationale_zh="單人近景動作題，主體動作（配戴防護手套並透過顯微鏡觀察）清晰明確，適合基礎動作辨識。",
            accent="us",
            image_brief_zh_en=(
                "【待製圖片規格 Image Brief】明亮現代化生物實驗室近景：一名身穿白袍、戴著藍色乳膠手套與護目鏡的女性研究員正坐在實驗桌前，雙手調整桌上的雙筒光學顯微鏡並低頭透過目鏡觀察。桌上旁側整齊擺放著一個裝有密封試管的試管架與一台闔上的筆記型電腦；背景水槽是空的，白板上沒有任何字跡。"
                " (English Brief: Close-up of a female researcher in a white lab coat, protective goggles, and gloves sitting at a lab bench and looking through a microscope while adjusting its focus knob. A rack of sealed test tubes and a closed laptop rest beside her; the sink in the background is empty.)"
            ),
            choices_map={
                "A": "She is looking through a microscope.",
                "B": "She is washing glassware in the sink.",
                "C": "She is writing a formula on the whiteboard.",
                "D": "She is putting on a laboratory coat.",
            },
            ans="A",
            skill_tags=["photo_action"],
            visual_reasoning_zh="照片中女性研究員正低頭透過顯微鏡目鏡觀察並調整焦距旋鈕，桌面與背景並無洗杯子、寫白板或穿衣動作。",
            explanation_zh="本題考單人照片動作描述。(A)「她正透過顯微鏡觀察（looking through a microscope）」直接且準確描述畫面核心人物正在進行的動作。",
            distractor_map={
                "B": "背景雖有實驗室水槽，但研究員並未在水槽清洗玻璃器皿（washing glassware）。",
                "C": "研究員坐在桌前操作顯微鏡，並未站在白板前書寫公式。",
                "D": "is putting on 表「正在穿上」的動作過程，但研究員身上的實驗白袍已經穿好（is wearing）。",
            },
            vocab=[
                {
                    "term_en": "look through a microscope",
                    "meaning_zh": "透過顯微鏡觀察",
                    "example_en": "The technician is looking through a microscope to examine the sample.",
                }
            ],
        ),
        make_part1_group(
            num=2,
            family_id="ag-fam-p1-bakery-counter-pastry-display",
            scenario="retail_bakery",
            diff_level="D3",
            diff_rationale_zh="結合人物互動動作與展示櫃物品狀態，並設計現在進行式被動語態（are being baked）作為典型 Part 1 陷阱。",
            accent="uk",
            image_brief_zh_en=(
                "【待製圖片規格 Image Brief】烘焙坊櫃檯場景：透明玻璃展示櫃內整齊排列著各式已出爐的可頌與水果塔。櫃檯後方一名繫著圍裙的店員正雙手遞出一個牛皮紙袋給櫃檯前的男性顧客；後方烤爐門緊閉，無人正在刷洗地板。"
                " (English Brief: Inside a bakery, rows of croissants and tarts are arranged inside a glass display case. Behind the counter, a clerk wearing an apron is handing a paper bag to a male customer. The floor is clean and nobody is mopping.)"
            ),
            choices_map={
                "A": "Pastries are being removed from the oven.",
                "B": "A customer is stacking trays on the counter.",
                "C": "A clerk is handing a paper bag to a patron.",
                "D": "The bakery floor is being mopped.",
            },
            ans="C",
            skill_tags=["photo_action", "photo_state_location"],
            visual_reasoning_zh="畫面中繫圍裙的店員正將牛皮紙袋遞給櫃檯前的顧客（patron），展示櫃內的糕點已陳列完畢而非正從烤爐取出。",
            explanation_zh="本題考雙人互動動作與同義詞轉換。(C) 使用 `patron`（顧客）代換 `customer`，準確描述「一名店員正把紙袋遞給顧客（handing a paper bag to a patron）」。",
            distractor_map={
                "A": "糕點已經陳列在玻璃展示櫃中，並無「正從烤爐被取出來（are being removed from the oven）」的動作。",
                "B": "顧客正在接過紙袋，並未在櫃檯上堆疊托盤（stacking trays）。",
                "D": "is being mopped 為現在進行式被動（正被拖洗），畫面中無人正在拖地。",
            },
            vocab=[
                {
                    "term_en": "patron",
                    "meaning_zh": "顧客；惠顧者",
                    "example_en": "Restaurant patrons may validate their parking tickets at the front desk.",
                }
            ],
        ),
        make_part1_group(
            num=3,
            family_id="ag-fam-p1-harbor-walkway-benches-empty",
            scenario="public_waterfront",
            diff_level="D4",
            diff_rationale_zh="無人景觀與空間相對位置題，考驗狀態被動與現在進行式被動（are being boarded / is being paved）之區別。",
            accent="au",
            image_brief_zh_en=(
                "【待製圖片規格 Image Brief】晴朗無人的港口水岸步道：數張木製長椅沿著石磚鋪設的岸邊步道整齊排列，面向平靜的水面。水面上有數艘小型帆船用纜繩停靠在木棧碼頭旁，長椅旁的街燈柱立於步道邊緣；畫面中完全沒有任何行人、工人或乘客。"
                " (English Brief: An empty stone-paved waterfront walkway with wooden benches lined up facing the harbor. Several small sailboats are tied to a wooden pier in the calm water, and streetlamps stand along the path. No people are present in the scene.)"
            ),
            choices_map={
                "A": "Passengers are boarding a ferry at the dock.",
                "B": "Wooden benches are lined up along the waterfront walkway.",
                "C": "Workers are paving a stone path near the harbor.",
                "D": "Sailboats are being pulled onto the shore.",
            },
            ans="B",
            skill_tags=["photo_state_location", "paraphrase"],
            visual_reasoning_zh="畫面為無人的水岸景觀，木製長椅沿著水岸步道成排擺放（are lined up along the waterfront walkway），無任何人員登船或鋪路。",
            explanation_zh="本題考無人景觀的空間狀態描述。當照片中完全沒有人物時，凡是隱含「有人正在執行動作」的進行式或進行式被動選項皆為錯誤。(B)「木製長椅沿著水岸步道排列（are lined up along the waterfront walkway）」準確描述靜態位置狀態。",
            distractor_map={
                "A": "畫面中沒有任何乘客（Passengers），因此「正在登船（are boarding）」不成立。",
                "C": "步道已經鋪好石磚，現場並無工人正在鋪路（are paving）。",
                "D": "are being pulled 為現在進行式被動，意指「正被人拉上岸」，但帆船是靜止停泊在碼頭邊。",
            },
            vocab=[
                {
                    "term_en": "line up",
                    "meaning_zh": "排列；排成一列",
                    "example_en": "Chairs are lined up along the wall of the reception hall.",
                }
            ],
        ),
        # --- PART 2: 5 GROUPS (000009 .. 000013) ---
        make_part2_group(
            num=9,
            family_id="ag-fam-p2-wh-how-long-new-hire-orientation",
            scenario="hr_onboarding",
            diff_level="D1",
            diff_rationale_zh="基礎 How long 時間長度疑問句，正解以「兩整天」直接回答持續時間。",
            q_accent="us",
            r_accent="us",
            q_role="new_employee",
            r_role="hr_coordinator",
            question_en="How long does the new employee orientation program last?",
            choices_map={
                "A": "Two full days, starting on Monday morning.",
                "B": "In the third-floor auditorium.",
                "C": "About twelve meters wide.",
            },
            ans="A",
            skill_tags=["question_function", "direct_response"],
            reasoning_zh="發問者以 How long ... last 詢問新進員工職前訓練持續多久，選項 A 直接回答「整整兩天，從週一早上開始」。",
            explanation_zh="題幹詢問「新進員工職前訓練計畫持續多久（How long... last）？」。(A) 回答時間長度「整整兩天，自週一上午開始」，完全符合 How long 的疑問焦點。",
            distractor_map={
                "B": "回答的是地點（在三樓禮堂），適用於 Where 問句。",
                "C": "利用 long 的空間長度字義聯想出「大約十二公尺寬」，不符時間長度問題。",
            },
            vocab=[
                {
                    "term_en": "orientation program",
                    "meaning_zh": "職前訓練計畫；新生訓練",
                    "example_en": "Attendance at the orientation program is mandatory for all new staff.",
                }
            ],
        ),
        make_part2_group(
            num=10,
            family_id="ag-fam-p2-wh-why-packaging-line-stopped",
            scenario="manufacturing_operations",
            diff_level="D2",
            diff_rationale_zh="Why 詢問產線停機原因，正解省略 Because 直接說明光學感應器需更換，貼近真實工廠對話。",
            q_accent="au",
            r_accent="us",
            q_role="plant_manager",
            r_role="line_supervisor",
            question_en="Why has packaging line four been shut down?",
            choices_map={
                "A": "One of the optical sensors needs to be replaced.",
                "B": "Yes, please shut the window.",
                "C": "By five o'clock this evening.",
            },
            ans="A",
            skill_tags=["question_function", "direct_response"],
            reasoning_zh="發問者詢問四號包裝產線為何停機，選項 A 說明「其中一個光學感應器需要更換」，直接給出故障停機原因。",
            explanation_zh="題幹以 Why 詢問「為什麼四號包裝線被關閉停機了？」。(A) 雖未以 Because 開頭，但直接陳述設備停機原因「其中一個光學感應器需要更換」，為標準回應。",
            distractor_map={
                "B": "重複題幹 shut 一詞（shut down 停機 vs shut the window 關窗），且 Why 問句不可用 Yes 回答。",
                "C": "回答的是截止時間（今天傍晚五點前），適用於 When 問句而非 Why。",
            },
            vocab=[
                {
                    "term_en": "shut down",
                    "meaning_zh": "停機；關閉（機器或工廠）",
                    "example_en": "The assembly line was shut down for routine maintenance.",
                }
            ],
        ),
        make_part2_group(
            num=11,
            family_id="ag-fam-p2-tag-question-booth-deposit-paid",
            scenario="trade_show_exhibition",
            diff_level="D3",
            diff_rationale_zh="否定陳述搭配肯定附加問句（..., did we?），正解以具體匯款動作消除發問者疑慮。",
            q_accent="uk",
            r_accent="ca",
            q_role="marketing_manager",
            r_role="event_assistant",
            question_en="We didn't miss the deadline for the trade show booth deposit, did we?",
            choices_map={
                "A": "Right next to the main registration desk.",
                "B": "No, I wired the payment yesterday afternoon.",
                "C": "The keynote speech starts at ten.",
            },
            ans="B",
            skill_tags=["question_function", "direct_response"],
            reasoning_zh="發問者擔心是否錯過了商展攤位訂金繳交期限，選項 B 回答「沒有（沒錯過），我昨天下午已經電匯付款了」。",
            explanation_zh="題幹為附加問句「我們該不會錯過了商展攤位訂金的截止期限吧？」。(B) 以 `No` 表示「沒有錯過」，並補充具體事證「我昨天下午已經電匯款項了（wired the payment）」，清楚解除對方擔憂。",
            distractor_map={
                "A": "誤將攤位訂金（booth deposit）聽成詢問攤位位置，回答「就在主報到櫃檯旁邊」。",
                "C": "受 trade show 場景聯想出專題演講時間，與訂金繳交期限無關。",
            },
            vocab=[
                {
                    "term_en": "wire a payment",
                    "meaning_zh": "電匯款項",
                    "example_en": "The client wired the deposit directly to our corporate account.",
                }
            ],
        ),
        make_part2_group(
            num=12,
            family_id="ag-fam-p2-offer-carry-sample-catalogs",
            scenario="sales_visit",
            diff_level="D4",
            diff_rationale_zh="禮貌提供協助（Would you like me to...），正解不直接說 No thanks，而是指出手推車就在走廊轉角，展現高階口語委婉回應。",
            q_accent="ca",
            r_accent="uk",
            q_role="receptionist",
            r_role="sales_representative",
            question_en="Would you like me to help you carry those product catalogs out to your car?",
            choices_map={
                "A": "Thanks, but I brought a folding cart with me.",
                "B": "The new spring catalog has sixty pages.",
                "C": "It's parked in the underground garage.",
            },
            ans="A",
            skill_tags=["question_function", "indirect_response", "speaker_intent"],
            reasoning_zh="發問者主動提議幫忙把產品型錄搬到車上，選項 A 表達感謝並說明自己帶了摺疊推車，禮貌婉拒協助。",
            explanation_zh="題幹以 Would you like me to... 主動表達協助搬運產品型錄的好意。(A) 先道謝（Thanks），接著說明「不過我自己帶了摺疊手推車（folding cart）」，委婉說明無需勞煩對方。",
            distractor_map={
                "B": "重複題幹 catalog 一詞，但談論春季型錄頁數，未回應搬運協助。",
                "C": "受句尾 car 一詞影響而回答停車位置（停在地下停車場），不合提議句的溝通功能。",
            },
            vocab=[
                {
                    "term_en": "folding cart",
                    "meaning_zh": "摺疊手推車",
                    "example_en": "Use the folding cart to transport heavy boxes of brochures.",
                }
            ],
        ),
        make_part2_group(
            num=13,
            family_id="ag-fam-p2-indirect-embedded-question-dentist-reschedule",
            scenario="medical_appointment",
            diff_level="D5",
            diff_rationale_zh="間接疑問句（Do you know if...）詢問週四下午是否有空檔，正解說明週四休診但主動提供週五上午時段。",
            q_accent="us",
            r_accent="au",
            q_role="patient",
            r_role="clinic_receptionist",
            question_en="Do you know if Dr. Patel has any openings this Thursday afternoon?",
            choices_map={
                "A": "The clinic's grand opening was last month.",
                "B": "She doesn't work Thursdays, but Friday at ten is available.",
                "C": "Yes, I know Dr. Patel very well.",
            },
            ans="B",
            skill_tags=["question_function", "indirect_response", "conditions_exceptions"],
            reasoning_zh="發問者詢問 Patel 醫師週四下午是否有門診空檔（openings），選項 B 說明她週四不看診，並提供週五早上十點的可預約時段。",
            explanation_zh="題幹為間接問句，表面以 Do you know if... 開頭，實際溝通目的是預約週四下午的看診空檔（openings）。(B) 針對核心需求回答「她每逢週四休診，不過週五早上十點有空檔」，兼具原因說明與替代方案。",
            distractor_map={
                "A": "利用 opening 的一詞多義（預約空檔 vs 開幕典禮 grand opening）設下聽力詞彙陷阱。",
                "C": "僅針對字面 Do you know... 回答「我跟 Patel 醫師很熟」，忽略了 if 子句詢問門診空檔的真正目的。",
            },
            vocab=[
                {
                    "term_en": "opening",
                    "meaning_zh": "（預約或職缺的）空檔、名額；開幕",
                    "example_en": "The stylist has one opening left at 3:00 P.M. tomorrow.",
                }
            ],
        ),
        # --- PART 5: 3 GROUPS (000013 .. 000015) ---
        make_part5_group(
            num=13,
            family_id="ag-fam-p5-wordform-comparative-efficiency",
            scenario="energy_sustainability",
            diff_level="D2",
            diff_rationale_zh="考驗比較級結構（than）中，連綴動詞 is 後接形容詞比較級 more efficient。",
            prompt_en="The newly installed solar water heater is significantly ____ than the aging gas-powered unit it replaced.",
            choices_map={
                "A": "efficient",
                "B": "efficiently",
                "C": "more efficient",
                "D": "efficiency",
            },
            ans="C",
            skill_tags=["word_form", "connector_clause"],
            quote_en="is significantly ____ than the aging gas-powered unit",
            reasoning_zh="be 動詞 is 後需用形容詞作主詞補語，且後方有比較連接詞 than 與修飾比較級的副詞 significantly，故須填形容詞比較級 more efficient。",
            explanation_zh="本題考形容詞比較級與詞性判斷。空格位於連綴動詞 `is` 與程度副詞 `significantly`（顯著地）之後，作主詞 `solar water heater` 的補語，應使用形容詞；又因後方有比較標記 `than`（比……），故須選形容詞比較級 **(C) more efficient**（更具能源效率的）。",
            distractor_map={
                "A": "efficient 為形容詞原級，無法與後方的比較連接詞 than 搭配。",
                "B": "efficiently 為副詞原級，既不可作 is 的主詞補語，也缺少比較級形式。",
                "D": "efficiency 為名詞（效率），不可直接受副詞 significantly 修飾並搭配 than。",
            },
            vocab=[
                {
                    "term_en": "aging",
                    "meaning_zh": "老舊的；日漸老化的",
                    "example_en": "The city plans to replace its aging water pipes over the next five years.",
                }
            ],
        ),
        make_part5_group(
            num=14,
            family_id="ag-fam-p5-prep-distinguish-between-among",
            scenario="retail_loyalty_program",
            diff_level="D4",
            diff_rationale_zh="考驗表排除例外條件之複合介系詞（aside from / except for）與其他介系詞之語意辨析。",
            prompt_en="The seasonal discount voucher may be redeemed at any Cortland Apparel store nationwide, ____ outlet locations and airport kiosks.",
            choices_map={
                "A": "aside from",
                "B": "prior to",
                "C": "on behalf of",
                "D": "by means of",
            },
            ans="A",
            skill_tags=["preposition_collocation", "conditions_exceptions"],
            quote_en="at any Cortland Apparel store nationwide, ____ outlet locations and airport kiosks.",
            reasoning_zh="前文說全國門市皆可兌換，逗號後列出暢貨中心與機場櫃位作為排除條件，故填 aside from（除……之外）。",
            explanation_zh="本題考複合介系詞片語的語意與例外條件。前半句指出「季節折扣券可在全國任何一家 Cortland 服飾門市兌換」，逗號後接特定店型 `outlet locations and airport kiosks`（暢貨中心門市與機場小型櫃位），在商務條款中用以標明排除的例外門市，故選 **(A) aside from**（除……之外）。",
            distractor_map={
                "B": "prior to 意為「在……之前（時間）」，後面應接時間或事件，無法接地點名詞表除外。",
                "C": "on behalf of 意為「代表（某人或某機構）」，語意不合折扣券使用限制。",
                "D": "by means of 意為「藉由……手段／方法」，與排除特定門市無關。",
            },
            vocab=[
                {
                    "term_en": "redeem a voucher",
                    "meaning_zh": "兌換抵用券／折價券",
                    "example_en": "Vouchers can be redeemed online or in person.",
                },
                {
                    "term_en": "aside from",
                    "meaning_zh": "除……之外",
                    "example_en": "Aside from a minor delay, the event went smoothly.",
                },
            ],
        ),
        make_part5_group(
            num=15,
            family_id="ag-fam-p5-subjunctive-recommend-that-clause",
            scenario="it_cybersecurity",
            diff_level="D5",
            diff_rationale_zh="高難度要求／建議假設法（mandative subjunctive）：recommended that + 單數主詞 every remote employee + 原形動詞 update。",
            prompt_en="Following last week's security audit, the chief information officer recommended that every remote employee ____ the virtual private network software immediately.",
            choices_map={
                "A": "updates",
                "B": "update",
                "C": "updating",
                "D": "to update",
            },
            ans="B",
            skill_tags=["verb_form_agreement", "connector_clause"],
            quote_en="recommended that every remote employee ____ the virtual private network software",
            reasoning_zh="建議動詞 recommended 後接 that 名詞子句時，子句動詞須省略 should 並使用原形動詞 update，不受單數主詞 every remote employee 影響。",
            explanation_zh="本題考建議／要求動詞後的假設法語氣（Subjunctive Mood）。當主要子句動詞為表「建議、要求、堅持、命令」（如 `recommend, suggest, request, require, insist`）時，其後 `that` 子句中的動詞須為 `(should) + 原形動詞`。因此儘管子句主詞 `every remote employee` 為單數，仍須填入原形動詞 **(B) update**。",
            distractor_map={
                "A": "updates 為第三人稱單數現在式，忽略了 recommended that 觸發的假設法原形動詞規則。",
                "C": "updating 為現在分詞，無法單獨作為 that 子句中的限定動詞。",
                "D": "to update 為不定詞，不可作 that 名詞子句的述語動詞。",
            },
            vocab=[
                {
                    "term_en": "security audit",
                    "meaning_zh": "資安稽核；安全審查",
                    "example_en": "An external firm conducts our annual security audit.",
                }
            ],
        ),
        # --- PART 6: 2 GROUPS = 8 ITEMS ---
        {
            "schema_version": "1.0.0",
            "group_id": "ag-g-p6-000001",
            "version": 1,
            "family_id": "ag-fam-p6-community-library-digital-archive",
            "pool": "training",
            "fixture": False,
            "part": 6,
            "layout": "text_completion",
            "scenario": "public_library_service",
            "difficulty": {
                "level": "D3",
                "rationale_zh": "結合時態、商務語境名詞、跨句轉折副詞與完整句插入題，需理解社區圖書館數位化館藏升級脈絡。",
                "basis": "editorial",
            },
            "content_status": "draft",
            "stimulus": {
                "documents": [
                    {
                        "document_id": "ag-doc-p6-000001-1",
                        "genre": "notice",
                        "title_en": "Oakridge Public Library: Historical Newspaper Archive Upgrade",
                        "blocks": [
                            {
                                "block_id": "ag-blk-p6-000001-1",
                                "type": "text",
                                "text_en": (
                                    "Beginning November 1, the Oakridge Public Library [[blank:ag-i-p6-000001-1]] its online historical newspaper archive to include regional periodicals dating back to 1890. "
                                    "Over the past eight months, our preservation team has scanned more than 40,000 pages of fragile microfilm so that residents can search local history records from home. "
                                    "[[blank:ag-i-p6-000001-2]] "
                                    "To use the new portal, patrons simply need to enter their fourteen-digit library card number on our website. "
                                    "[[blank:ag-i-p6-000001-3]], the third-floor microfilm reading room will close for two weeks starting November 4 while technicians install high-resolution viewing terminals. "
                                    "Patrons who require [[blank:ag-i-p6-000001-4]] locating specific municipal records during this closure may schedule an appointment with a reference librarian."
                                ),
                            }
                        ],
                    }
                ],
                "speakers": [],
                "audio_script": [],
            },
            "assets": [],
            "items": [
                {
                    "item_id": "ag-i-p6-000001-1",
                    "prompt_en": "Select the best word or phrase to fill in blank [[blank:ag-i-p6-000001-1]].",
                    "choices": [
                        {"id": "A", "text_en": "expanded"},
                        {"id": "B", "text_en": "will expand"},
                        {"id": "C", "text_en": "had expanded"},
                        {"id": "D", "text_en": "is expanding from"},
                    ],
                    "answer_choice_id": "B",
                    "skill_tags": ["verb_form_agreement", "chronology"],
                    "evidence": [
                        {
                            "source_type": "document_block",
                            "source_id": "ag-blk-p6-000001-1",
                            "quote_en": "Beginning November 1, the Oakridge Public Library [[blank:ag-i-p6-000001-1]] its online historical newspaper archive",
                            "reasoning_zh": "句首時間標記 Beginning November 1 與後文 will close starting November 4 皆預告即將生效的新措施，故用未來簡單式 will expand。",
                        }
                    ],
                    "explanation_zh": "本題考篇章時態一致性。句首 `Beginning November 1`（自 11 月 1 日起）搭配後文 `will close for two weeks starting November 4` 顯示本公告發布於 11 月之前，預告即將推行的服務升級，且後接直接受詞 `its online historical newspaper archive`，故選未來簡單式 **(B) will expand**。",
                    "distractor_notes": [
                        {"choice_id": "A", "reason_zh": "expanded 為過去簡單式，與預告未來 11 月 1 日生效的公告語境不符。"},
                        {"choice_id": "C", "reason_zh": "had expanded 為過去完成式，需有過去基準點，不適用於預告未來新服務。"},
                        {"choice_id": "D", "reason_zh": "多出介系詞 from，導致後方無法直接接原受詞 its online historical newspaper archive to include...。"},
                    ],
                    "vocabulary": [
                        {
                            "term_en": "periodical",
                            "meaning_zh": "期刊；定期刊物",
                            "example_en": "Back issues of trade periodicals are stored in the digital archive.",
                        }
                    ],
                    "estimated_time_sec": 25,
                },
                {
                    "item_id": "ag-i-p6-000001-2",
                    "prompt_en": "Select the best sentence to fill in blank [[blank:ag-i-p6-000001-2]].",
                    "choices": [
                        {"id": "A", "text_en": "This remote access eliminates the need to visit the branch in person to view delicate paper copies."},
                        {"id": "B", "text_en": "Late fees for overdue hardcover books will increase by ten cents per day."},
                        {"id": "C", "text_en": "Several authors will sign copies of their new novels in the lobby tonight."},
                        {"id": "D", "text_en": "Unfortunately, the scanning project was canceled due to budget cuts."},
                    ],
                    "answer_choice_id": "A",
                    "skill_tags": ["sentence_insertion", "reference_cohesion"],
                    "evidence": [
                        {
                            "source_type": "document_block",
                            "source_id": "ag-blk-p6-000001-1",
                            "quote_en": "our preservation team has scanned more than 40,000 pages of fragile microfilm so that residents can search local history records from home. [[blank:ag-i-p6-000001-2]] To use the new portal, patrons simply need to enter their fourteen-digit library card number",
                            "reasoning_zh": "前句提到已掃描四萬頁微縮膠卷讓居民可從家中搜尋（search ... from home），選項 A 的 This remote access 精準指涉前句「從家中搜尋」，並銜接後句如何使用該新入口網站。",
                        }
                    ],
                    "explanation_zh": "本題考完整句插入與代名詞指涉（Reference & Cohesion）。空格前一句說明團隊已掃描超過四萬頁脆弱的微縮膠卷，「讓居民能從家中檢索地方歷史紀錄（search local history records from home）」；空格後一句說明登入該新入口網站的方式。(A) 開頭的 `This remote access`（這項遠端存取服務）正好回指前句的 `from home`，並自然過渡到後句的網站登入步驟。",
                    "distractor_notes": [
                        {"choice_id": "B", "reason_zh": "談論精裝書逾期罰款調漲，偏離歷史報紙數位典藏主題。"},
                        {"choice_id": "C", "reason_zh": "談論今晚大廳的新書簽名會，與線上資料庫升級無關。"},
                        {"choice_id": "D", "reason_zh": "宣稱掃描計畫因預算刪減而取消，與前句「已完成四萬頁掃描」及後句「啟用新網站」完全矛盾。"},
                    ],
                    "vocabulary": [
                        {
                            "term_en": "fragile",
                            "meaning_zh": "脆弱的；易損壞的",
                            "example_en": "Archival gloves must be worn when handling fragile documents.",
                        }
                    ],
                    "estimated_time_sec": 35,
                },
                {
                    "item_id": "ag-i-p6-000001-3",
                    "prompt_en": "Select the best word or phrase to fill in blank [[blank:ag-i-p6-000001-3]].",
                    "choices": [
                        {"id": "A", "text_en": "For instance"},
                        {"id": "B", "text_en": "In the meantime"},
                        {"id": "C", "text_en": "On the contrary"},
                        {"id": "D", "text_en": "As a result of"},
                    ],
                    "answer_choice_id": "B",
                    "skill_tags": ["reference_cohesion", "chronology"],
                    "evidence": [
                        {
                            "source_type": "document_block",
                            "source_id": "ag-blk-p6-000001-1",
                            "quote_en": "[[blank:ag-i-p6-000001-3]], the third-floor microfilm reading room will close for two weeks starting November 4 while technicians install high-resolution viewing terminals.",
                            "reasoning_zh": "前段說明線上檢索服務啟用，本句補充在相關升級期間三樓實體微縮膠卷閱覽室將暫時關閉兩週以安裝高解析終端機，用 In the meantime（在此期間／同時）銜接最自然。",
                        }
                    ],
                    "explanation_zh": "本題考轉折與時序副詞片語。前文說明讀者可透過網站線上檢索數位典藏，本句則告知「在此同時／與此期間，三樓微縮膠卷閱覽室將自 11 月 4 日起關閉兩週以安裝新終端機」。**(B) In the meantime**（在此期間、與此同時）能妥善銜接同一升級計畫下的並行安排。",
                    "distractor_notes": [
                        {"choice_id": "A", "reason_zh": "For instance（舉例來說）用於舉例說明前句觀點，但實體閱覽室關閉並非輸入圖書證號的例子。"},
                        {"choice_id": "C", "reason_zh": "On the contrary（恰恰相反）用於否定前句陳述，不合文意。"},
                        {"choice_id": "D", "reason_zh": "As a result of 為複合介系詞，後方須接名詞片語而不可直接加逗號與完整子句。"},
                    ],
                    "vocabulary": [
                        {
                            "term_en": "in the meantime",
                            "meaning_zh": "在此期間；與此同時",
                            "example_en": "Your replacement card will arrive in five days; in the meantime, use this temporary pass.",
                        }
                    ],
                    "estimated_time_sec": 25,
                },
                {
                    "item_id": "ag-i-p6-000001-4",
                    "prompt_en": "Select the best word or phrase to fill in blank [[blank:ag-i-p6-000001-4]].",
                    "choices": [
                        {"id": "A", "text_en": "assistance"},
                        {"id": "B", "text_en": "attendance"},
                        {"id": "C", "text_en": "allowance"},
                        {"id": "D", "text_en": "appliance"},
                    ],
                    "answer_choice_id": "A",
                    "skill_tags": ["vocabulary_in_context", "preposition_collocation"],
                    "evidence": [
                        {
                            "source_type": "document_block",
                            "source_id": "ag-blk-p6-000001-1",
                            "quote_en": "Patrons who require [[blank:ag-i-p6-000001-4]] locating specific municipal records during this closure may schedule an appointment with a reference librarian.",
                            "reasoning_zh": "require assistance (in) doing something 意為「需要協助尋找特定市政紀錄」，故可預約參考諮詢館員。",
                        }
                    ],
                    "explanation_zh": "本題考語境名詞與固定搭配。句意為「在閱覽室關閉期間，需要______尋找特定市政紀錄的讀者，可預約參考諮詢館員」。`require assistance + V-ing`（需要協助做某事）與後文「預約諮詢館員」語意完全呼應，故選 **(A) assistance**（協助）。",
                    "distractor_notes": [
                        {"choice_id": "B", "reason_zh": "attendance 意為「出席、到場人數」，不符合請館員幫忙查找資料的語境。"},
                        {"choice_id": "C", "reason_zh": "allowance 意為「津貼、容許量」，與圖書館文獻檢索服務無關。"},
                        {"choice_id": "D", "reason_zh": "appliance 意為「家用電器」，為可數名詞且語意完全不符。"},
                    ],
                    "vocabulary": [
                        {
                            "term_en": "reference librarian",
                            "meaning_zh": "參考諮詢館員",
                            "example_en": "Ask the reference librarian for help with archival databases.",
                        }
                    ],
                    "estimated_time_sec": 20,
                },
            ],
            "provenance": make_provenance(),
            "review_refs": [],
        },
        {
            "schema_version": "1.0.0",
            "group_id": "ag-g-p6-000002",
            "version": 1,
            "family_id": "ag-fam-p6-warehouse-automated-sorting-memo",
            "pool": "training",
            "fixture": False,
            "part": 6,
            "layout": "text_completion",
            "scenario": "logistics_automation",
            "difficulty": {
                "level": "D4",
                "rationale_zh": "物流中心導入光學分揀系統之內部備忘錄，考驗詞性、介系詞搭配、指涉代名詞與完整句插入之跨句邏輯。",
                "basis": "editorial",
            },
            "content_status": "draft",
            "stimulus": {
                "documents": [
                    {
                        "document_id": "ag-doc-p6-000002-1",
                        "genre": "memo",
                        "title_en": "Memo: Trial Run of Optical Parcel Sorting System in Zone B",
                        "blocks": [
                            {
                                "block_id": "ag-blk-p6-000002-1",
                                "type": "text",
                                "text_en": (
                                    "To: All Distribution Center Supervisors\n"
                                    "From: Marcus Vance, Director of Warehouse Operations\n\n"
                                    "Starting next Monday, Zone B will begin a two-week operational trial of our new optical parcel sorting conveyor. "
                                    "The equipment is designed to process up to 3,500 packages per hour, [[blank:ag-i-p6-000002-1]] reducing manual scanning bottlenecks during peak evening shifts. "
                                    "During the initial phase, only standard rectangular cartons weighing under twenty kilograms will be routed through the automated lane. "
                                    "[[blank:ag-i-p6-000002-2]] "
                                    "Floor supervisors must ensure that all shift leads complete the safety checklist [[blank:ag-i-p6-000002-3]] activating the conveyor belts each morning. "
                                    "Any barcode recognition errors should be logged in the shared maintenance spreadsheet so our engineers can calibrate [[blank:ag-i-p6-000002-4]] before full deployment in December."
                                ),
                            }
                        ],
                    }
                ],
                "speakers": [],
                "audio_script": [],
            },
            "assets": [],
            "items": [
                {
                    "item_id": "ag-i-p6-000002-1",
                    "prompt_en": "Select the best word or phrase to fill in blank [[blank:ag-i-p6-000002-1]].",
                    "choices": [
                        {"id": "A", "text_en": "dramatic"},
                        {"id": "B", "text_en": "dramatically"},
                        {"id": "C", "text_en": "dramatize"},
                        {"id": "D", "text_en": "drama"},
                    ],
                    "answer_choice_id": "B",
                    "skill_tags": ["word_form"],
                    "evidence": [
                        {
                            "source_type": "document_block",
                            "source_id": "ag-blk-p6-000002-1",
                            "quote_en": "process up to 3,500 packages per hour, [[blank:ag-i-p6-000002-1]] reducing manual scanning bottlenecks",
                            "reasoning_zh": "空格修飾現在分詞 reducing（減少人工掃描瓶頸），需用副詞 dramatically（大幅地）。",
                        }
                    ],
                    "explanation_zh": "本題考分詞構句中的副詞修飾。逗號後 `____ reducing manual scanning bottlenecks` 為結果分詞構句，修飾分詞動詞 `reducing`（減少）必須使用副詞 **(B) dramatically**（大幅地、顯著地）。",
                    "distractor_notes": [
                        {"choice_id": "A", "reason_zh": "dramatic 為形容詞，只能修飾名詞，不可修飾動詞分詞 reducing。"},
                        {"choice_id": "C", "reason_zh": "dramatize 為原形動詞（使戲劇化），放入分詞片語前造成語法與語意錯誤。"},
                        {"choice_id": "D", "reason_zh": "drama 為名詞（戲劇），無法修飾分詞 reducing。"},
                    ],
                    "vocabulary": [
                        {
                            "term_en": "bottleneck",
                            "meaning_zh": "瓶頸；阻塞環節",
                            "example_en": "Automated scanners helped eliminate bottlenecks at the loading dock.",
                        }
                    ],
                    "estimated_time_sec": 20,
                },
                {
                    "item_id": "ag-i-p6-000002-2",
                    "prompt_en": "Select the best sentence to fill in blank [[blank:ag-i-p6-000002-2]].",
                    "choices": [
                        {"id": "A", "text_en": "Irregularly shaped parcels and heavy crates should continue to be handled at the manual stations in Zone A."},
                        {"id": "B", "text_en": "All warehouse employees must submit their vacation requests to human resources by Friday."},
                        {"id": "C", "text_en": "The optical sorting system was decommissioned after ten years of reliable service."},
                        {"id": "D", "text_en": "Customers can track their international air freight using the mobile application."},
                    ],
                    "answer_choice_id": "A",
                    "skill_tags": ["sentence_insertion", "conditions_exceptions"],
                    "evidence": [
                        {
                            "source_type": "document_block",
                            "source_id": "ag-blk-p6-000002-1",
                            "quote_en": "During the initial phase, only standard rectangular cartons weighing under twenty kilograms will be routed through the automated lane. [[blank:ag-i-p6-000002-2]]",
                            "reasoning_zh": "前句限定初期僅「20公斤以下的標準長方體紙箱」走自動分揀道，選項 A 緊接著說明「形狀不規則包裹與重型木箱應繼續由 A 區人工工作站處理」，條件互補完整。",
                        }
                    ],
                    "explanation_zh": "本題考完整句插入與條件互補邏輯。空格前句指出：「在初期階段，只有 20 公斤以下的標準矩形紙箱會導入自動分揀線」。讀者自然會問：那不符合此規格的包裹怎麼辦？**(A)** 明確補充「形狀不規則的包裹與重型貨箱，應繼續在 A 區的人工工作站處理」，與前句構成嚴密的作業分流說明。",
                    "distractor_notes": [
                        {"choice_id": "B", "reason_zh": "談論向人資部提交休假申請，偏離包裹分揀作業主題。"},
                        {"choice_id": "C", "reason_zh": "宣稱光學分揀系統在服役十年後除役，與首句「下週一啟動新系統試運轉」矛盾。"},
                        {"choice_id": "D", "reason_zh": "談論顧客用手機 App 追蹤國際空運，不屬於針對倉儲主管的內部設備操作備忘錄內容。"},
                    ],
                    "vocabulary": [
                        {
                            "term_en": "irregularly shaped",
                            "meaning_zh": "形狀不規則的",
                            "example_en": "Irregularly shaped items require special packaging materials.",
                        }
                    ],
                    "estimated_time_sec": 35,
                },
                {
                    "item_id": "ag-i-p6-000002-3",
                    "prompt_en": "Select the best word or phrase to fill in blank [[blank:ag-i-p6-000002-3]].",
                    "choices": [
                        {"id": "A", "text_en": "prior to"},
                        {"id": "B", "text_en": "except for"},
                        {"id": "C", "text_en": "on account of"},
                        {"id": "D", "text_en": "in addition"},
                    ],
                    "answer_choice_id": "A",
                    "skill_tags": ["preposition_collocation", "chronology"],
                    "evidence": [
                        {
                            "source_type": "document_block",
                            "source_id": "ag-blk-p6-000002-1",
                            "quote_en": "complete the safety checklist [[blank:ag-i-p6-000002-3]] activating the conveyor belts each morning.",
                            "reasoning_zh": "安全檢查表必須在每天早上啟動輸送帶「之前（prior to + V-ing）」完成。",
                        }
                    ],
                    "explanation_zh": "本題考介系詞片語與作業時序。句意為「現場主管必須確保所有班組長在每天早上啟動輸送帶______完成安全檢查表」。依安全規範，檢查必須在啟動設備之前完成，且空格後為動名詞 `activating`，故選複合介系詞 **(A) prior to**（在……之前）。",
                    "distractor_notes": [
                        {"choice_id": "B", "reason_zh": "except for（除……之外）放入後語意變成「除了啟動輸送帶之外要完成安全表」，不合時序。"},
                        {"choice_id": "C", "reason_zh": "on account of（由於、因為）表因果關係，不符合啟動前完成安檢的程序要求。"},
                        {"choice_id": "D", "reason_zh": "in addition 為副詞片語，後面必須加上 to（in addition to）才能接動名詞 activating。"},
                    ],
                    "vocabulary": [
                        {
                            "term_en": "activate",
                            "meaning_zh": "啟動；開啟（設備或系統）",
                            "example_en": "Press the green button to activate the emergency ventilation system.",
                        }
                    ],
                    "estimated_time_sec": 25,
                },
                {
                    "item_id": "ag-i-p6-000002-4",
                    "prompt_en": "Select the best word or phrase to fill in blank [[blank:ag-i-p6-000002-4]].",
                    "choices": [
                        {"id": "A", "text_en": "theirs"},
                        {"id": "B", "text_en": "itself"},
                        {"id": "C", "text_en": "the sensors"},
                        {"id": "D", "text_en": "each other"},
                    ],
                    "answer_choice_id": "C",
                    "skill_tags": ["reference_cohesion", "vocabulary_in_context"],
                    "evidence": [
                        {
                            "source_type": "document_block",
                            "source_id": "ag-blk-p6-000002-1",
                            "quote_en": "Any barcode recognition errors should be logged in the shared maintenance spreadsheet so our engineers can calibrate [[blank:ag-i-p6-000002-4]] before full deployment in December.",
                            "reasoning_zh": "前文提及 optical parcel sorting conveyor 與 barcode recognition errors，工程師需要校準（calibrate）的對象即為負責辨識條碼的「感應器（the sensors）」，且代名詞選項與複數主詞 engineers 皆無法合理配對。",
                        }
                    ],
                    "explanation_zh": "本題考篇章指涉與語境搭配。前半句提到「任何條碼辨識錯誤都應記錄在共用維修試算表中，以便我們的工程師在十二月全面部署前校準______」。若選反身代名詞 `itself` 與複數主詞 `engineers` 不一致，選 `theirs` 指涉不明；而 **(C) the sensors**（感應器）具體指明光學條碼分揀設備中需校準的元件，語意與文法皆最精準。",
                    "distractor_notes": [
                        {"choice_id": "A", "reason_zh": "theirs 為所有格代名詞（他們的東西），前文並無對應的所屬名詞可指涉。"},
                        {"choice_id": "B", "reason_zh": "itself 為單數反身代名詞，與該子句複數主詞 our engineers 在文法上不相容。"},
                        {"choice_id": "D", "reason_zh": "each other（彼此）若作 calibrate 的受詞，會變成「工程師互相校準對方」，語意荒謬。"},
                    ],
                    "vocabulary": [
                        {
                            "term_en": "full deployment",
                            "meaning_zh": "全面部署；正式全面上線",
                            "example_en": "Software bugs must be resolved prior to full deployment.",
                        }
                    ],
                    "estimated_time_sec": 25,
                },
            ],
            "provenance": make_provenance(),
            "review_refs": [],
        },
    ]
    return groups


def main() -> None:
    out_dir = ROOT / "drafts" / "batch-ag-0002"
    out_dir.mkdir(parents=True, exist_ok=True)
    groups = build_groups()
    groups_path = out_dir / "groups.jsonl"
    with groups_path.open("w", encoding="utf-8") as f:
        for g in groups:
            f.write(json.dumps(g, ensure_ascii=False) + "\n")
    print(f"Wrote {len(groups)} groups ({sum(len(g['items']) for g in groups)} items) to {groups_path}")


if __name__ == "__main__":
    main()
