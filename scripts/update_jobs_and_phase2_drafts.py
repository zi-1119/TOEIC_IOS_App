#!/usr/bin/env python3
"""
Updates:
1. jobs/jobs-phase1-100.json (adds job-ag-0006 and job-ag-0007 v2 media upgrade jobs)
2. jobs/roadmap-phase2-400.json (assigns batch-ag-0008 .. batch-ag-0018 for 100 -> 400 expansion)
3. blueprints/phase2-100-to-400-blueprint.json (detailed Part x Scenario x Skill x Difficulty blueprint for remaining 300 items)
4. drafts/phase2-unreleased-batch-ag-0008/groups.jsonl (10 unreleased text draft items: Part 5 x 6 + Part 6 x 4, tracked separately as draft_unreleased)
"""

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main() -> None:
    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    # 1. Update jobs/jobs-phase1-100.json
    jobs_p1_path = ROOT / "jobs" / "jobs-phase1-100.json"
    jobs_p1 = json.loads(jobs_p1_path.read_text(encoding="utf-8"))
    jobs_p1["updated_at"] = now_iso
    existing_ids = {j["job_id"] for j in jobs_p1["jobs"]}

    v2_jobs = [
        {
            "job_id": "job-ag-0006",
            "parts": [1, 2, 3, 4],
            "pool": "training",
            "group_count": 4,
            "item_count": 8,
            "skills": [
                "photo_action",
                "question_function",
                "direct_response",
                "main_idea_purpose",
                "explicit_detail",
                "paraphrase",
                "next_action",
            ],
            "scenarios": [
                "research_laboratory",
                "logistics_shipping",
                "marketing_printing",
                "retail_delivery",
            ],
            "difficulty_targets": {"D1": 2, "D2": 6, "D3": 0, "D4": 0, "D5": 0},
            "constraints": [
                "不覆寫 exports/batch-ag-0001..0005；保留原 group_id/item_id/family_id 並升版為 version=2",
                "Part 1 補齊真實 1200x896 JPEG 照片並完成獨立視覺盲解 (blind=true)",
                "Part 1-4 補齊實測毫秒時間碼 segment_times 之 AAC .m4a 音檔 (status=ready)",
            ],
            "output_batch_id": "batch-ag-0006",
            "status": "exported",
            "retry_count": 0,
            "notes_zh": "第一階段聽力四題型可播放樣本包（ag-g-p1-000001、ag-g-p2-000001、ag-g-p3-000001、ag-g-p4-000001，v2 實體音圖就緒）。",
        },
        {
            "job_id": "job-ag-0007",
            "parts": [1, 2, 3, 4],
            "pool": "training",
            "group_count": 23,
            "item_count": 41,
            "skills": [
                "photo_action",
                "photo_state_location",
                "question_function",
                "direct_response",
                "indirect_response",
                "main_idea_purpose",
                "explicit_detail",
                "paraphrase",
                "speaker_intent",
                "next_action",
                "inference",
                "graphic_integration",
                "conditions_exceptions",
                "chronology",
            ],
            "scenarios": [
                "retail_bakery",
                "public_waterfront",
                "maintenance_inspection",
                "procurement_contract",
                "finance_reimbursement",
                "event_catering",
                "it_support",
                "retail_merchandising",
                "hospitality_transport",
                "hr_onboarding",
                "manufacturing_operations",
                "trade_show_exhibition",
                "sales_visit",
                "medical_appointment",
                "hospitality_events",
                "product_development",
                "healthcare_administration",
                "logistics_shipping",
                "corporate_training",
                "public_museum_tour",
                "manufacturing_safety",
                "transportation_commute",
                "sales_analytics",
            ],
            "difficulty_targets": {"D1": 1, "D2": 6, "D3": 14, "D4": 10, "D5": 10},
            "constraints": [
                "不覆寫 exports/batch-ag-0001..0005；保留原 group_id/item_id/family_id 並升版為 version=2",
                "補齊第一階段剩餘 2 張 Part 1 圖片與 23 個 Part 1-4 音檔 (status=ready)，使 100 題試行集全數 3 張圖片與 27 個音檔就緒",
                "ca 口音標記角色誠實揭露使用 macOS 北美英語語音代用合成，不捏造原生加拿大口音驗收",
            ],
            "output_batch_id": "batch-ag-0007",
            "status": "exported",
            "retry_count": 0,
            "notes_zh": "第一階段其餘 23 組聽力題組媒體補齊包（2 張 Part 1 圖片 + 23 個 Part 1-4 音檔，v2 素材就緒）。",
        },
    ]

    jobs_p1["jobs"] = [j for j in jobs_p1["jobs"] if j["job_id"] not in {"job-ag-0006", "job-ag-0007"}] + v2_jobs
    jobs_p1_path.write_text(json.dumps(jobs_p1, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    # 2. Update jobs/roadmap-phase2-400.json (batches batch-ag-0008 .. batch-ag-0018)
    roadmap_p2 = {
        "schema_version": "1.0.0",
        "phase": "phase2_400_expansion",
        "updated_at": now_iso,
        "pool": "training",
        "gating_condition_zh": "須先讓現有 100 題閱讀題與四種聽力樣本在 App 完成匯入、作答與解析驗收，始得將第二階段草稿轉為正式匯出批次。",
        "baseline_accepted_items": 100,
        "target_cumulative_items": 400,
        "remaining_quota_items": 300,
        "part_remaining_quotas": {
            "1": {"phase1_done": 3, "phase2_target_cumulative": 12, "remaining_to_add": 9},
            "2": {"phase1_done": 13, "phase2_target_cumulative": 50, "remaining_to_add": 37},
            "3": {"phase1_done": 18, "phase2_target_cumulative": 78, "remaining_to_add": 60},
            "4": {"phase1_done": 15, "phase2_target_cumulative": 60, "remaining_to_add": 45},
            "5": {"phase1_done": 15, "phase2_target_cumulative": 60, "remaining_to_add": 45},
            "6": {"phase1_done": 8, "phase2_target_cumulative": 32, "remaining_to_add": 24},
            "7": {"phase1_done": 28, "phase2_target_cumulative": 108, "remaining_to_add": 80},
        },
        "planned_jobs": [
            {
                "job_id": "job-ag-0008",
                "output_batch_id": "batch-ag-0008",
                "parts": [5, 6],
                "pool": "training",
                "group_count": 23,
                "item_count": 32,
                "status": "draft_in_progress",
                "unreleased_draft_items_prepared": 10,
                "retry_count": 0,
                "description_zh": "Part 5（20題）+ Part 6（3組12題）；目前已於 drafts/phase2-unreleased-batch-ag-0008/ 預備 10 題未發布草稿（Part 5 × 6 + Part 6 × 4），分開統計不計入已發布合格題。",
            },
            {
                "job_id": "job-ag-0009",
                "output_batch_id": "batch-ag-0009",
                "parts": [5, 6],
                "pool": "training",
                "group_count": 28,
                "item_count": 37,
                "status": "planned",
                "retry_count": 0,
                "description_zh": "Part 5（25題）+ Part 6（3組12題），完成 400 題里程碑之 Part 5（+45）與 Part 6（+24）全部配額。",
            },
            {
                "job_id": "job-ag-0010",
                "output_batch_id": "batch-ag-0010",
                "parts": [1, 2],
                "pool": "training",
                "group_count": 23,
                "item_count": 23,
                "status": "planned",
                "retry_count": 0,
                "description_zh": "Part 1（5題）+ Part 2（18題），涵蓋製造現場、商務會議、物流倉儲與市政工程情境。",
            },
            {
                "job_id": "job-ag-0011",
                "output_batch_id": "batch-ag-0011",
                "parts": [1, 2],
                "pool": "training",
                "group_count": 23,
                "item_count": 23,
                "status": "planned",
                "retry_count": 0,
                "description_zh": "Part 1（4題）+ Part 2（19題），完成 400 題里程碑之 Part 1（+9）與 Part 2（+37）全部配額。",
            },
            {
                "job_id": "job-ag-0012",
                "output_batch_id": "batch-ag-0012",
                "parts": [3],
                "pool": "training",
                "group_count": 10,
                "item_count": 30,
                "status": "planned",
                "retry_count": 0,
                "description_zh": "Part 3 簡短對話（10組30題），含三人對話 2 組與圖表整合題 2 組。",
            },
            {
                "job_id": "job-ag-0013",
                "output_batch_id": "batch-ag-0013",
                "parts": [3],
                "pool": "training",
                "group_count": 10,
                "item_count": 30,
                "status": "planned",
                "retry_count": 0,
                "description_zh": "Part 3 簡短對話（10組30題），完成 400 題里程碑之 Part 3（+60）全部配額。",
            },
            {
                "job_id": "job-ag-0014",
                "output_batch_id": "batch-ag-0014",
                "parts": [4],
                "pool": "training",
                "group_count": 8,
                "item_count": 24,
                "status": "planned",
                "retry_count": 0,
                "description_zh": "Part 4 簡短獨白（8組24題），涵蓋機場航班廣播、新產品發表會與園區導覽。",
            },
            {
                "job_id": "job-ag-0015",
                "output_batch_id": "batch-ag-0015",
                "parts": [4],
                "pool": "training",
                "group_count": 7,
                "item_count": 21,
                "status": "planned",
                "retry_count": 0,
                "description_zh": "Part 4 簡短獨白（7組21題），完成 400 題里程碑之 Part 4（+45）全部配額。",
            },
            {
                "job_id": "job-ag-0016",
                "output_batch_id": "batch-ag-0016",
                "parts": [7],
                "pool": "training",
                "group_count": 8,
                "item_count": 26,
                "status": "planned",
                "retry_count": 0,
                "description_zh": "Part 7 單篇閱讀（8組26題），涵蓋企業內部備忘錄、客訴處理信、多人即時訊息串與財經新聞。",
            },
            {
                "job_id": "job-ag-0017",
                "output_batch_id": "batch-ag-0017",
                "parts": [7],
                "pool": "training",
                "group_count": 7,
                "item_count": 29,
                "status": "planned",
                "retry_count": 0,
                "description_zh": "Part 7 單篇（4組14題）+ 雙篇閱讀（3組15題）。",
            },
            {
                "job_id": "job-ag-0018",
                "output_batch_id": "batch-ag-0018",
                "parts": [7],
                "pool": "training",
                "group_count": 5,
                "item_count": 25,
                "status": "planned",
                "retry_count": 0,
                "description_zh": "Part 7 多篇閱讀（雙篇2組10題 + 三篇3組15題），完成 400 題里程碑之 Part 7（+80）全部配額。",
            },
        ],
    }
    (ROOT / "jobs" / "roadmap-phase2-400.json").write_text(
        json.dumps(roadmap_p2, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    # 3. Write blueprints/phase2-100-to-400-blueprint.json
    blueprint_p2 = {
        "schema_version": "1.0.0",
        "blueprint_id": "blueprint-phase2-100-to-400",
        "created_at": now_iso,
        "pool": "training",
        "gating_rule_zh": "必須待第一階段 100 題（含閱讀題與 Part 1-4 四種聽力樣本）於 iOS App 完成匯入、作答與詳解顯示驗證後，始得將第二階段草稿轉為已發布批次。",
        "quota_summary": {
            "phase1_completed_items": 100,
            "phase2_addition_items": 300,
            "phase2_cumulative_target_items": 400,
            "master_4800_remaining_after_phase2": 4400,
        },
        "difficulty_distribution_targets_300": {
            "D1": {"ratio": 0.15, "target_items": 45},
            "D2": {"ratio": 0.25, "target_items": 75},
            "D3": {"ratio": 0.20, "target_items": 60},
            "D4": {"ratio": 0.15, "target_items": 45},
            "D5": {"ratio": 0.25, "target_items": 75},
        },
        "part_blueprints": [
            {
                "part": 1,
                "layout": "photo",
                "phase1_done": 3,
                "phase2_add_groups": 9,
                "phase2_add_items": 9,
                "phase2_cumulative_items": 12,
                "reserved_group_ids": "ag-g-p1-000004 .. ag-g-p1-000012",
                "target_skills": ["photo_action", "photo_state_location", "paraphrase"],
                "planned_scenarios": [
                    "construction_site_inspection",
                    "conference_room_setup",
                    "warehouse_forklift_loading",
                    "outdoor_cafe_patio",
                    "airport_check_in_counter",
                    "library_reading_area",
                    "hotel_lobby_luggage",
                    "bicycle_repair_workshop",
                    "supermarket_produce_aisle",
                ],
            },
            {
                "part": 2,
                "layout": "question_response",
                "phase1_done": 13,
                "phase2_add_groups": 37,
                "phase2_add_items": 37,
                "phase2_cumulative_items": 50,
                "reserved_group_ids": "ag-g-p2-000014 .. ag-g-p2-000050",
                "target_skills": [
                    "question_function",
                    "direct_response",
                    "indirect_response",
                    "paraphrase",
                    "speaker_intent",
                ],
                "question_type_mix": {
                    "wh_questions": 16,
                    "yes_no_and_negative_questions": 8,
                    "tag_and_choice_questions": 6,
                    "indirect_requests_and_statements": 7,
                },
            },
            {
                "part": 3,
                "layout": "conversation",
                "phase1_done": 18,
                "phase2_add_groups": 20,
                "phase2_add_items": 60,
                "phase2_cumulative_items": 78,
                "reserved_group_ids": "ag-g-p3-000007 .. ag-g-p3-000026",
                "target_skills": [
                    "main_idea_purpose",
                    "explicit_detail",
                    "paraphrase",
                    "speaker_intent",
                    "next_action",
                    "inference",
                    "graphic_integration",
                    "conditions_exceptions",
                    "chronology",
                ],
                "special_group_quotas": {
                    "three_speaker_conversations": 3,
                    "graphic_integration_conversations": 4,
                    "spoken_intent_quote_questions": 5,
                },
            },
            {
                "part": 4,
                "layout": "talk",
                "phase1_done": 15,
                "phase2_add_groups": 15,
                "phase2_add_items": 45,
                "phase2_cumulative_items": 60,
                "reserved_group_ids": "ag-g-p4-000006 .. ag-g-p4-000020",
                "target_skills": [
                    "main_idea_purpose",
                    "explicit_detail",
                    "paraphrase",
                    "speaker_intent",
                    "next_action",
                    "inference",
                    "graphic_integration",
                    "conditions_exceptions",
                    "chronology",
                ],
                "special_group_quotas": {
                    "graphic_integration_talks": 3,
                    "spoken_intent_quote_questions": 4,
                },
            },
            {
                "part": 5,
                "layout": "sentence",
                "phase1_done": 15,
                "phase2_add_groups": 45,
                "phase2_add_items": 45,
                "phase2_cumulative_items": 60,
                "reserved_group_ids": "ag-g-p5-000016 .. ag-g-p5-000060",
                "target_skills": [
                    "word_form",
                    "verb_form_agreement",
                    "preposition_collocation",
                    "connector_clause",
                    "vocabulary_in_context",
                    "reference_cohesion",
                    "conditions_exceptions",
                    "chronology",
                ],
            },
            {
                "part": 6,
                "layout": "text_completion",
                "phase1_done": 8,
                "phase2_add_groups": 6,
                "phase2_add_items": 24,
                "phase2_cumulative_items": 32,
                "reserved_group_ids": "ag-g-p6-000003 .. ag-g-p6-000008",
                "target_skills": [
                    "word_form",
                    "verb_form_agreement",
                    "connector_clause",
                    "vocabulary_in_context",
                    "reference_cohesion",
                    "sentence_insertion",
                ],
            },
            {
                "part": 7,
                "layout": "single_passage / double_passage / triple_passage",
                "phase1_done": 28,
                "phase2_add_groups": 20,
                "phase2_add_items": 80,
                "phase2_cumulative_items": 108,
                "reserved_group_ids": "ag-g-p7-000008 .. ag-g-p7-000027",
                "structure_breakdown": {
                    "single_passage": {"groups": 12, "items": 40},
                    "double_passage": {"groups": 5, "items": 25},
                    "triple_passage": {"groups": 3, "items": 15},
                },
                "target_skills": [
                    "main_idea_purpose",
                    "explicit_detail",
                    "paraphrase",
                    "speaker_intent",
                    "next_action",
                    "inference",
                    "vocabulary_in_context",
                    "sentence_insertion",
                    "cross_document",
                    "conditions_exceptions",
                    "chronology",
                ],
            },
        ],
    }
    (ROOT / "blueprints" / "phase2-100-to-400-blueprint.json").write_text(
        json.dumps(blueprint_p2, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    # 4. Create unreleased Phase 2 text drafts in drafts/phase2-unreleased-batch-ag-0008/
    # (7 groups = 10 items: Part 5 x 6 items + Part 6 x 1 group [4 items], content_status="draft")
    unrel_dir = ROOT / "drafts" / "phase2-unreleased-batch-ag-0008"
    unrel_dir.mkdir(parents=True, exist_ok=True)

    p5_draft_specs = [
        (
            "ag-g-p5-000016",
            "ag-fam-p5-wordform-customs-declaration-accuracy",
            "customs_clearance",
            "D2",
            "副詞修飾過去分詞 completed，考驗基礎詞性變化辨析。",
            "ag-i-p5-000016-1",
            "All international airfreight parcels must have an ____ completed customs declaration attached to the outer carton.",
            [
                {"id": "A", "text_en": "accurate"},
                {"id": "B", "text_en": "accurately"},
                {"id": "C", "text_en": "accuracy"},
                {"id": "D", "text_en": "more accurate"},
            ],
            "B",
            ["word_form"],
            "空格位於不定冠詞 an 與過去分詞形容詞 completed 之間，需填入副詞 accurately（精確地）修飾 completed。",
            [
                {"choice_id": "A", "reason_zh": "形容詞不可直接修飾過去分詞 completed。"},
                {"choice_id": "C", "reason_zh": "名詞不可修飾分詞。"},
                {"choice_id": "D", "reason_zh": "形容詞比較級結構與冠詞 an 不搭配且無法修飾 completed。"},
            ],
            [{"term_en": "customs declaration", "meaning_zh": "報關單", "example_en": "Please sign the customs declaration before shipping."}],
        ),
        (
            "ag-g-p5-000017",
            "ag-fam-p5-connector-audit-postponement-owing-to",
            "finance_auditing",
            "D3",
            "介系詞片語 owing to 後接名詞片語表原因，區分從屬連接詞與副詞。",
            "ag-i-p5-000017-1",
            "The external inventory audit at the Busan depot was postponed ____ a scheduled software migration.",
            [
                {"id": "A", "text_en": "owing to"},
                {"id": "B", "text_en": "even though"},
                {"id": "C", "text_en": "consequently"},
                {"id": "D", "text_en": "provided that"},
            ],
            "A",
            ["connector_clause", "preposition_collocation"],
            "空格後為純名詞片語 a scheduled software migration，需使用複合介系詞 owing to（由於）引導原因。",
            [
                {"choice_id": "B", "reason_zh": "even though 為從屬連接詞，後須接完整子句。"},
                {"choice_id": "C", "reason_zh": "consequently 為副詞，無法直接連接名詞片語作受詞。"},
                {"choice_id": "D", "reason_zh": "provided that 為條件連接詞，後須接子句。"},
            ],
            [{"term_en": "software migration", "meaning_zh": "軟體系統轉移／升級", "example_en": "The database will be offline during the software migration."}],
        ),
        (
            "ag-g-p5-000018",
            "ag-fam-p5-vocab-tenant-lease-termination-notice",
            "commercial_leasing",
            "D3",
            "合約語境動詞辨析（terminate 終止租約 vs.fabricate/nominate/circulate）。",
            "ag-i-p5-000018-1",
            "Commercial tenants wishing to ____ their lease agreement early must submit written notice at least sixty days in advance.",
            [
                {"id": "A", "text_en": "nominate"},
                {"id": "B", "text_en": "terminate"},
                {"id": "C", "text_en": "circulate"},
                {"id": "D", "text_en": "fabricate"},
            ],
            "B",
            ["vocabulary_in_context", "conditions_exceptions"],
            "依後文「提前至少六十天提交書面通知」可知，此處指商業承租戶希望提前「終止（terminate）」租約。",
            [
                {"choice_id": "A", "reason_zh": "nominate 意為「提名；任命」，不與 lease agreement 搭配。"},
                {"choice_id": "C", "reason_zh": "circulate 意為「傳閱；流通」，與提前六十天書面通知之解約語境不符。"},
                {"choice_id": "D", "reason_zh": "fabricate 意為「製造；偽造」，語意不合。"},
            ],
            [{"term_en": "terminate a lease", "meaning_zh": "終止租約", "example_en": "Either party may terminate the lease with sixty days' notice."}],
        ),
        (
            "ag-g-p5-000019",
            "ag-fam-p5-verb-subjunctive-board-recommendation-retain",
            "corporate_governance",
            "D4",
            "建議動詞 recommend 後接 that 子句之假設語氣原形動詞（should 省略）。",
            "ag-i-p5-000019-1",
            "The risk committee recommended that the firm ____ an independent cybersecurity consultancy before launching the mobile payment platform.",
            [
                {"id": "A", "text_en": "retains"},
                {"id": "B", "text_en": "retained"},
                {"id": "C", "text_en": "retain"},
                {"id": "D", "text_en": "retaining"},
            ],
            "C",
            ["verb_form_agreement"],
            "建議動詞 recommended 後的 that 名詞子句中，助動詞 should 省略，動詞須用原形 retain（聘請）。",
            [
                {"choice_id": "A", "reason_zh": "一般現在式第三人稱單數不符合建議子句省略 should 的語法。"},
                {"choice_id": "B", "reason_zh": "過去式不可用於表建議之要求性 that 子句。"},
                {"choice_id": "D", "reason_zh": "動名詞／現在分詞無法作子句主要動詞。"},
            ],
            [{"term_en": "retain a consultancy", "meaning_zh": "聘請顧問公司", "example_en": "We retained an external legal firm to review the merger."}],
        ),
        (
            "ag-g-p5-000020",
            "ag-fam-p5-collocation-comply-with-sterilization-protocol",
            "medical_manufacturing",
            "D2",
            "高頻職場動詞片語搭配 comply with（遵守規範）。",
            "ag-i-p5-000020-1",
            "All cleanroom technicians are required to comply ____ the updated sterilization protocols posted outside Lab 4.",
            [
                {"id": "A", "text_en": "with"},
                {"id": "B", "text_en": "to"},
                {"id": "C", "text_en": "for"},
                {"id": "D", "text_en": "at"},
            ],
            "A",
            ["preposition_collocation"],
            "comply 為不及物動詞，固定搭配介系詞 with（comply with + 規定／標準，表「遵守」）。",
            [
                {"choice_id": "B", "reason_zh": "conform 或 adhere 才搭配 to，comply 不搭配 to。"},
                {"choice_id": "C", "reason_zh": "comply 不與 for 搭配。"},
                {"choice_id": "D", "reason_zh": "comply 不與 at 搭配。"},
            ],
            [{"term_en": "comply with", "meaning_zh": "遵守；依從", "example_en": "All vendors must comply with our safety guidelines."}],
        ),
        (
            "ag-g-p5-000021",
            "ag-fam-p5-chronology-by-the-time-future-perfect",
            "construction_project",
            "D5",
            "By the time + 現在式子句搭配主要子句未來完成式（will have been installed）。",
            "ag-i-p5-000021-1",
            "By the time the regional hospital wing opens to patients in November, the automated pharmacy dispensing units ____.",
            [
                {"id": "A", "text_en": "will install"},
                {"id": "B", "text_en": "were installing"},
                {"id": "C", "text_en": "will have been installed"},
                {"id": "D", "text_en": "have installed"},
            ],
            "C",
            ["verb_form_agreement", "chronology"],
            "時間副詞子句 By the time ... opens in November 指未來某時間點之前完成的被動動作，主詞 dispensing units 為被安裝對象，故用未來完成被動式 will have been installed。",
            [
                {"choice_id": "A", "reason_zh": "主動語態錯誤，設備無法自行安裝。"},
                {"choice_id": "B", "reason_zh": "過去進行式與未來時間 in November 矛盾且主動語態錯誤。"},
                {"choice_id": "D", "reason_zh": "現在完成主動式語態錯誤且未搭配 By the time 未來時間軸。"},
            ],
            [{"term_en": "dispensing unit", "meaning_zh": "配藥設備；發放裝置", "example_en": "The automated dispensing unit reduces medication errors."}],
        ),
    ]

    unrel_groups = []
    for gid, fam, scen, d_lvl, d_rat, iid, prompt, choices, ans, tags, expl, d_notes, vocab in p5_draft_specs:
        unrel_groups.append({
            "schema_version": "1.0.0",
            "group_id": gid,
            "version": 1,
            "family_id": fam,
            "pool": "training",
            "fixture": False,
            "part": 5,
            "layout": "sentence",
            "scenario": scen,
            "difficulty": {"level": d_lvl, "rationale_zh": d_rat, "basis": "editorial"},
            "content_status": "draft",
            "stimulus": {"documents": [], "speakers": [], "audio_script": []},
            "assets": [],
            "items": [
                {
                    "item_id": iid,
                    "prompt_en": prompt,
                    "choices": choices,
                    "answer_choice_id": ans,
                    "skill_tags": tags,
                    "evidence": [
                        {
                            "source_type": "item_prompt",
                            "source_id": iid,
                            "quote_en": prompt,
                            "reasoning_zh": expl,
                        }
                    ],
                    "explanation_zh": expl,
                    "distractor_notes": d_notes,
                    "vocabulary": vocab,
                    "estimated_time_sec": 20,
                }
            ],
            "provenance": {
                "origin": "original",
                "author_tool": "antigravity-toeic-factory/1.0.0",
                "author_model": "unknown",
                "created_at": now_iso,
                "rights_note_zh": "本題組為本專案原創命題內容（第二階段未發布草稿），未抄襲 ETS 官方試題或商業題庫。",
            },
            "review_refs": [],
        })

    # Add 1 Part 6 group (4 items)
    p6_gid = "ag-g-p6-000003"
    p6_doc_id = "ag-doc-p6-000003-1"
    p6_blk_id = "ag-blk-p6-000003-1"
    p6_text = (
        "To: All Field Service Engineers\n"
        "From: Henrik Lindqvist, Director of Fleet Operations\n"
        "Date: October 14\n"
        "Subject: Transition to Digital Maintenance Logs\n\n"
        "Beginning November 1, our regional service vans will no longer carry paper inspection booklets. "
        "Instead, engineers will record all diagnostic readings directly in the FieldSync mobile application [[blank:ag-i-p6-000003-1]] leaving a client's facility. "
        "[[blank:ag-i-p6-000003-2]] "
        "This change will allow the central dispatch team to monitor spare-part inventory in real time and reorder depleted components [[blank:ag-i-p6-000003-3]]. "
        "If your company-issued tablet requires a software update to run the latest version of FieldSync, please [[blank:ag-i-p6-000003-4]] the IT Help Desk before October 25."
    )
    unrel_groups.append({
        "schema_version": "1.0.0",
        "group_id": p6_gid,
        "version": 1,
        "family_id": "ag-fam-p6-fleet-digital-maintenance-logs",
        "pool": "training",
        "fixture": False,
        "part": 6,
        "layout": "text_completion",
        "scenario": "field_service_operations",
        "difficulty": {
            "level": "D3",
            "rationale_zh": "內部營運公告段落填空，結合時間連接詞、上下文插句、副詞詞性與動詞搭配。",
            "basis": "editorial",
        },
        "content_status": "draft",
        "stimulus": {
            "documents": [
                {
                    "document_id": p6_doc_id,
                    "genre": "memo",
                    "title_en": "Transition to Digital Maintenance Logs",
                    "blocks": [{"block_id": p6_blk_id, "type": "text", "text_en": p6_text}],
                }
            ],
            "speakers": [],
            "audio_script": [],
        },
        "assets": [],
        "items": [
            {
                "item_id": "ag-i-p6-000003-1",
                "prompt_en": "Select the best word or phrase to complete [[blank:ag-i-p6-000003-1]].",
                "choices": [
                    {"id": "A", "text_en": "prior to"},
                    {"id": "B", "text_en": "as though"},
                    {"id": "C", "text_en": "insofar as"},
                    {"id": "D", "text_en": "except for"},
                ],
                "answer_choice_id": "A",
                "skill_tags": ["preposition_collocation", "chronology"],
                "evidence": [
                    {
                        "source_type": "document_block",
                        "source_id": p6_blk_id,
                        "quote_en": "record all diagnostic readings directly in the FieldSync mobile application [[blank:ag-i-p6-000003-1]] leaving a client's facility.",
                        "reasoning_zh": "在離開客戶廠區之前（prior to leaving）先將檢測讀數登錄至行動應用程式。",
                    }
                ],
                "explanation_zh": "空格後接動名詞片語 leaving a client's facility，選複合介系詞 (A) prior to（在……之前）表示工程師應在離開客戶端前完成數位登錄。",
                "distractor_notes": [
                    {"choice_id": "B", "reason_zh": "as though（彷彿）為從屬連接詞，語意與結構皆不合。"},
                    {"choice_id": "C", "reason_zh": "insofar as（在……範圍內）後接子句。"},
                    {"choice_id": "D", "reason_zh": "except for（除了……之外）不符合現場作業流程語意。"},
                ],
                "vocabulary": [{"term_en": "prior to", "meaning_zh": "在……之前", "example_en": "Please complete the safety checklist prior to departure."}],
                "estimated_time_sec": 25,
            },
            {
                "item_id": "ag-i-p6-000003-2",
                "prompt_en": "Select the best sentence to complete [[blank:ag-i-p6-000003-2]].",
                "choices": [
                    {"id": "A", "text_en": "Paper booklets will still be mailed to customers every Friday."},
                    {"id": "B", "text_en": "Each entry must also include the client's digital signature on the tablet screen."},
                    {"id": "C", "text_en": "Several service vans were repainted at the downtown garage last month."},
                    {"id": "D", "text_en": "The company picnic has been moved to the indoor pavilion."},
                ],
                "answer_choice_id": "B",
                "skill_tags": ["sentence_insertion", "reference_cohesion"],
                "evidence": [
                    {
                        "source_type": "document_block",
                        "source_id": p6_blk_id,
                        "quote_en": "engineers will record all diagnostic readings directly in the FieldSync mobile application ... [[blank:ag-i-p6-000003-2]] This change will allow the central dispatch team to monitor spare-part inventory",
                        "reasoning_zh": "前句說明在行動 App 登錄檢測讀數，B 項補充說明每筆登錄（Each entry）亦須包含客戶在平板螢幕上的數位簽名，與後句 This change 緊密銜接。",
                    }
                ],
                "explanation_zh": "前句說明改用 FieldSync App 記錄檢測數據，(B)「每筆紀錄亦須包含客戶在平板螢幕上的數位簽名」直接延續數位化登錄流程，且與末段提及之 company-issued tablet 前後呼應。",
                "distractor_notes": [
                    {"choice_id": "A", "reason_zh": "與首句「不再使用紙本紀錄簿」直接矛盾。"},
                    {"choice_id": "C", "reason_zh": "工程車上月重新烤漆與數位維修紀錄無關。"},
                    {"choice_id": "D", "reason_zh": "公司野餐地點變更完全偏離主題。"},
                ],
                "vocabulary": [{"term_en": "digital signature", "meaning_zh": "數位簽名", "example_en": "The courier tablet captures the recipient's digital signature."}],
                "estimated_time_sec": 35,
            },
            {
                "item_id": "ag-i-p6-000003-3",
                "prompt_en": "Select the best word to complete [[blank:ag-i-p6-000003-3]].",
                "choices": [
                    {"id": "A", "text_en": "prompt"},
                    {"id": "B", "text_en": "promptly"},
                    {"id": "C", "text_en": "promptness"},
                    {"id": "D", "text_en": "prompted"},
                ],
                "answer_choice_id": "B",
                "skill_tags": ["word_form"],
                "evidence": [
                    {
                        "source_type": "document_block",
                        "source_id": p6_blk_id,
                        "quote_en": "reorder depleted components [[blank:ag-i-p6-000003-3]].",
                        "reasoning_zh": "修飾動詞片語 reorder depleted components 需用副詞 promptly（迅速地）。",
                    }
                ],
                "explanation_zh": "空格位於完整動詞片語 reorder depleted components 之後，需用副詞 (B) promptly（迅速地；即時地）修飾動詞 reorder。",
                "distractor_notes": [
                    {"choice_id": "A", "reason_zh": "形容詞或動詞原形無法置於受詞後修飾動詞。"},
                    {"choice_id": "C", "reason_zh": "名詞無法修飾動詞。"},
                    {"choice_id": "D", "reason_zh": "過去分詞語法不通。"},
                ],
                "vocabulary": [{"term_en": "depleted", "meaning_zh": "耗盡的；存量不足的", "example_en": "Depleted stock items are automatically flagged for reorder."}],
                "estimated_time_sec": 20,
            },
            {
                "item_id": "ag-i-p6-000003-4",
                "prompt_en": "Select the best word to complete [[blank:ag-i-p6-000003-4]].",
                "choices": [
                    {"id": "A", "text_en": "contact"},
                    {"id": "B", "text_en": "appoint"},
                    {"id": "C", "text_en": "assemble"},
                    {"id": "D", "text_en": "endure"},
                ],
                "answer_choice_id": "A",
                "skill_tags": ["vocabulary_in_context"],
                "evidence": [
                    {
                        "source_type": "document_block",
                        "source_id": p6_blk_id,
                        "quote_en": "please [[blank:ag-i-p6-000003-4]] the IT Help Desk before October 25.",
                        "reasoning_zh": "若平板電腦需要軟體更新，請在 10 月 25 日前聯繫（contact）IT 支援中心。",
                    }
                ],
                "explanation_zh": "受詞為 the IT Help Desk（資訊支援中心），故選 (A) contact（聯繫）。",
                "distractor_notes": [
                    {"choice_id": "B", "reason_zh": "appoint 意為「指派；任命」，不與 IT Help Desk 搭配。"},
                    {"choice_id": "C", "reason_zh": "assemble 意為「組裝；集合」，語意不合。"},
                    {"choice_id": "D", "reason_zh": "endure 意為「忍受」，語意不合。"},
                ],
                "vocabulary": [{"term_en": "help desk", "meaning_zh": "技術支援服務台", "example_en": "Contact the IT help desk if your password expires."}],
                "estimated_time_sec": 20,
            },
        ],
        "provenance": {
            "origin": "original",
            "author_tool": "antigravity-toeic-factory/1.0.0",
            "author_model": "unknown",
            "created_at": now_iso,
            "rights_note_zh": "本題組為本專案原創命題內容（第二階段未發布草稿），未抄襲 ETS 官方試題或商業題庫。",
        },
        "review_refs": [],
    })

    with (unrel_dir / "groups.jsonl").open("w", encoding="utf-8") as f:
        for g in unrel_groups:
            f.write(json.dumps(g, ensure_ascii=False) + "\n")

    print("Updated jobs/jobs-phase1-100.json, jobs/roadmap-phase2-400.json, blueprints/phase2-100-to-400-blueprint.json, and drafts/phase2-unreleased-batch-ag-0008/groups.jsonl (7 groups, 10 items).")


if __name__ == "__main__":
    main()
