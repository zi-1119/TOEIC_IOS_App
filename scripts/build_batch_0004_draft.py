#!/usr/bin/env python3
"""
Construct draft groups.jsonl for batch-ag-0004 (Part 4 Talks: 5 groups = 15 items, pool="training"):
- ag-g-p4-000001: Voicemail about custom conference table delivery
- ag-g-p4-000002: Maritime museum volunteer tour guide orientation
- ag-g-p4-000003: Cold-storage warehouse morning safety briefing (with speaker intent)
- ag-g-p4-000004: Municipal commuter ferry & shuttle service announcement
- ag-g-p4-000005: Quarterly regional sales & return rate table presentation (with graphic integration)
"""

import json
from pathlib import Path

from build_batch_0001_draft import make_provenance

ROOT = Path(__file__).resolve().parent.parent


def build_groups() -> list:
    groups = [
        # --- Group 1: ag-g-p4-000001 ---
        {
            "schema_version": "1.0.0",
            "group_id": "ag-g-p4-000001",
            "version": 1,
            "family_id": "ag-fam-p4-voicemail-custom-furniture-delivery",
            "pool": "training",
            "fixture": False,
            "part": 4,
            "layout": "talk",
            "scenario": "retail_delivery",
            "difficulty": {
                "level": "D2",
                "rationale_zh": "標準商業語音留言，包含來電目的、大樓貨梯維修限制與回電確認要求。",
                "basis": "editorial",
            },
            "content_status": "draft",
            "stimulus": {
                "documents": [],
                "speakers": [
                    {"speaker_id": "spk_1", "role": "delivery_dispatcher", "accent": "us"},
                    {"speaker_id": "spk_narrator", "role": "narrator", "accent": "us"},
                ],
                "audio_script": [
                    {
                        "segment_id": "ag-g-p4-000001-seg-1",
                        "speaker_id": "spk_1",
                        "text_en": "Hello, Ms. Lindqvist. This is Carlos calling from Artisan Woodworks. I'm pleased to let you know that our craftsmen have finished applying the protective finish to your custom walnut conference table, and it's ready for delivery this Thursday.",
                    },
                    {
                        "segment_id": "ag-g-p4-000001-seg-2",
                        "speaker_id": "spk_1",
                        "text_en": "However, when I contacted your office building's property manager this morning, she informed me that the main freight elevator is undergoing routine cable maintenance until noon on Thursday.",
                    },
                    {
                        "segment_id": "ag-g-p4-000001-seg-3",
                        "speaker_id": "spk_1",
                        "text_en": "Because the tabletop is three meters long, our crew cannot bring it up the passenger elevators. We've therefore scheduled your delivery window for between two and four P.M., once the freight elevator is back in service. Please call me back at 555-0192 to confirm that someone in your suite will be available to sign for the shipment.",
                    },
                    {
                        "segment_id": "ag-g-p4-000001-seg-q1",
                        "speaker_id": "spk_narrator",
                        "text_en": "What did the listener order from Artisan Woodworks?",
                    },
                    {
                        "segment_id": "ag-g-p4-000001-seg-q2",
                        "speaker_id": "spk_narrator",
                        "text_en": "Why was the delivery scheduled for Thursday afternoon instead of the morning?",
                    },
                    {
                        "segment_id": "ag-g-p4-000001-seg-q3",
                        "speaker_id": "spk_narrator",
                        "text_en": "What does the speaker ask the listener to confirm?",
                    },
                ],
            },
            "assets": [
                {
                    "asset_id": "ag-ast-p4-000001-audio",
                    "kind": "audio",
                    "status": "planned",
                    "path": None,
                    "sha256": None,
                    "mime_type": None,
                    "duration_ms": None,
                    "source_note_zh": "待合成 Part 4 語音留言獨白音檔（口音規劃：美式男聲 + 美式旁白）。",
                    "review_state": "pending",
                    "segment_times": [],
                }
            ],
            "items": [
                {
                    "item_id": "ag-i-p4-000001-1",
                    "prompt_en": "What did the listener order from Artisan Woodworks?",
                    "choices": [
                        {"id": "A", "text_en": "A set of reception lobby chairs"},
                        {"id": "B", "text_en": "Built-in bookshelves"},
                        {"id": "C", "text_en": "A custom conference table"},
                        {"id": "D", "text_en": "Hardwood flooring panels"},
                    ],
                    "answer_choice_id": "C",
                    "skill_tags": ["explicit_detail"],
                    "evidence": [
                        {
                            "source_type": "audio_segment",
                            "source_id": "ag-g-p4-000001-seg-1",
                            "quote_en": "our craftsmen have finished applying the protective finish to your custom walnut conference table",
                            "reasoning_zh": "講者明確告知工匠已完成聽眾訂製的胡桃木會議桌（custom walnut conference table）保護漆塗裝。",
                        }
                    ],
                    "explanation_zh": "講者在留言開頭表明來自 Artisan Woodworks，並通知聽眾：「工匠已經為您訂製的胡桃木會議桌（your custom walnut conference table）塗好保護漆，可於本週四配送」，故選 **(C)**。",
                    "distractor_notes": [
                        {"choice_id": "A", "reason_zh": "獨白未提及接待大廳座椅。"},
                        {"choice_id": "B", "reason_zh": "未提及嵌入式書架。"},
                        {"choice_id": "D", "reason_zh": "雖為木製品公司，但訂購的是會議桌而非硬木地板材料。"},
                    ],
                    "vocabulary": [
                        {
                            "term_en": "protective finish",
                            "meaning_zh": "保護塗層；保護漆面",
                            "example_en": "A waterproof protective finish was applied to the wooden deck.",
                        }
                    ],
                    "estimated_time_sec": 25,
                },
                {
                    "item_id": "ag-i-p4-000001-2",
                    "prompt_en": "Why was the delivery scheduled for Thursday afternoon instead of the morning?",
                    "choices": [
                        {"id": "A", "text_en": "The protective coating needs more time to dry."},
                        {"id": "B", "text_en": "All delivery trucks are booked on Thursday morning."},
                        {"id": "C", "text_en": "A building freight elevator is being serviced in the morning."},
                        {"id": "D", "text_en": "The street in front of the office will be closed for a parade."},
                    ],
                    "answer_choice_id": "C",
                    "skill_tags": ["explicit_detail", "paraphrase"],
                    "evidence": [
                        {
                            "source_type": "audio_segment",
                            "source_id": "ag-g-p4-000001-seg-2",
                            "quote_en": "the main freight elevator is undergoing routine cable maintenance until noon on Thursday.",
                            "reasoning_zh": "大樓物業經理告知主貨梯在週四中午前進行例行纜線維護（undergoing routine cable maintenance），故排在下午兩點至四點配送。",
                        }
                    ],
                    "explanation_zh": "講者在第二、三段解釋：「貴辦公大樓的物業經理告知，主貨梯在週四中午前進行例行纜線保養（undergoing routine cable maintenance until noon on Thursday），而三公尺長的桌面進不了客梯，因此安排在下午兩點至四點配送」，選項 **(C)** 以 `is being serviced` 改寫 `undergoing routine cable maintenance`。",
                    "distractor_notes": [
                        {"choice_id": "A", "reason_zh": "第一段已說明保護漆塗裝已經完成（have finished applying）。"},
                        {"choice_id": "B", "reason_zh": "並非貨車排滿，而是客戶大樓貨梯中午前維修。"},
                        {"choice_id": "D", "reason_zh": "未提及辦公室門前封街遊行。"},
                    ],
                    "vocabulary": [
                        {
                            "term_en": "freight elevator",
                            "meaning_zh": "載貨電梯；貨梯",
                            "example_en": "All large deliveries must use the rear freight elevator.",
                        }
                    ],
                    "estimated_time_sec": 25,
                },
                {
                    "item_id": "ag-i-p4-000001-3",
                    "prompt_en": "What does the speaker ask the listener to confirm?",
                    "choices": [
                        {"id": "A", "text_en": "That the final balance has been paid"},
                        {"id": "B", "text_en": "That a staff member can sign for the delivery"},
                        {"id": "C", "text_en": "That the old conference table has been removed"},
                        {"id": "D", "text_en": "That a loading dock permit has been issued"},
                    ],
                    "answer_choice_id": "B",
                    "skill_tags": ["next_action", "explicit_detail"],
                    "evidence": [
                        {
                            "source_type": "audio_segment",
                            "source_id": "ag-g-p4-000001-seg-3",
                            "quote_en": "Please call me back at 555-0192 to confirm that someone in your suite will be available to sign for the shipment.",
                            "reasoning_zh": "講者請聽眾回電確認辦公室裡屆時有人可以簽收貨物（available to sign for the shipment）。",
                        }
                    ],
                    "explanation_zh": "講者在結尾請求：「請回電 555-0192 確認貴辦公室屆時有人在場可以簽收貨品（someone in your suite will be available to sign for the shipment）」，故選 **(B)**。",
                    "distractor_notes": [
                        {"choice_id": "A", "reason_zh": "未提及尾款繳付問題。"},
                        {"choice_id": "C", "reason_zh": "未提及搬走舊會議桌。"},
                        {"choice_id": "D", "reason_zh": "未提及核發裝卸區停車證。"},
                    ],
                    "vocabulary": [
                        {
                            "term_en": "sign for a shipment",
                            "meaning_zh": "簽收貨件",
                            "example_en": "A receptionist must sign for the shipment upon arrival.",
                        }
                    ],
                    "estimated_time_sec": 25,
                },
            ],
            "provenance": make_provenance(),
            "review_refs": [],
        },
        # --- Group 2: ag-g-p4-000002 ---
        {
            "schema_version": "1.0.0",
            "group_id": "ag-g-p4-000002",
            "version": 1,
            "family_id": "ag-fam-p4-museum-volunteer-orientation-tour",
            "pool": "training",
            "fixture": False,
            "part": 4,
            "layout": "talk",
            "scenario": "public_museum_tour",
            "difficulty": {
                "level": "D3",
                "rationale_zh": "博物館志工導覽培訓獨白，需推論聽眾身分並掌握館內動線與接下來立即執行的步驟。",
                "basis": "editorial",
            },
            "content_status": "draft",
            "stimulus": {
                "documents": [],
                "speakers": [
                    {"speaker_id": "spk_1", "role": "museum_volunteer_coordinator", "accent": "uk"},
                    {"speaker_id": "spk_narrator", "role": "narrator", "accent": "us"},
                ],
                "audio_script": [
                    {
                        "segment_id": "ag-g-p4-000002-seg-1",
                        "speaker_id": "spk_1",
                        "text_en": "Welcome, everyone, and thank you for volunteering to help out during the opening weekend of our nineteenth-century navigation exhibit at the Bristol Maritime Museum.",
                    },
                    {
                        "segment_id": "ag-g-p4-000002-seg-2",
                        "speaker_id": "spk_1",
                        "text_en": "Before the museum doors open to ticket holders at ten o'clock, I want to point out a recent change to our lobby layout. Because we expect large crowds for the antique compass display in Gallery B, we've moved the audio headset rental counter from the main entrance to the alcove beside the gift shop.",
                    },
                    {
                        "segment_id": "ag-g-p4-000002-seg-3",
                        "speaker_id": "spk_1",
                        "text_en": "Also, please remember that flash photography is strictly prohibited inside Gallery B to protect the fragile parchment sea charts. Now, let's walk over to the security desk so each of you can pick up your name badge and floor assignment sheet.",
                    },
                    {
                        "segment_id": "ag-g-p4-000002-seg-q1",
                        "speaker_id": "spk_narrator",
                        "text_en": "Who is the speaker addressing?",
                    },
                    {
                        "segment_id": "ag-g-p4-000002-seg-q2",
                        "speaker_id": "spk_narrator",
                        "text_en": "What has been moved next to the gift shop?",
                    },
                    {
                        "segment_id": "ag-g-p4-000002-seg-q3",
                        "speaker_id": "spk_narrator",
                        "text_en": "What will the listeners do next?",
                    },
                ],
            },
            "assets": [
                {
                    "asset_id": "ag-ast-p4-000002-audio",
                    "kind": "audio",
                    "status": "planned",
                    "path": None,
                    "sha256": None,
                    "mime_type": None,
                    "duration_ms": None,
                    "source_note_zh": "待合成 Part 4 博物館志工職前說明獨白音檔（口音規劃：英式女聲 + 美式旁白）。",
                    "review_state": "pending",
                    "segment_times": [],
                }
            ],
            "items": [
                {
                    "item_id": "ag-i-p4-000002-1",
                    "prompt_en": "Who is the speaker addressing?",
                    "choices": [
                        {"id": "A", "text_en": "Antique collectors"},
                        {"id": "B", "text_en": "Museum volunteers"},
                        {"id": "C", "text_en": "Lighting technicians"},
                        {"id": "D", "text_en": "Travel journalists"},
                    ],
                    "answer_choice_id": "B",
                    "skill_tags": ["inference", "main_idea_purpose"],
                    "evidence": [
                        {
                            "source_type": "audio_segment",
                            "source_id": "ag-g-p4-000002-seg-1",
                            "quote_en": "thank you for volunteering to help out during the opening weekend of our nineteenth-century navigation exhibit at the Bristol Maritime Museum.",
                            "reasoning_zh": "講者感謝大家擔任志工在海事博物館特展開幕週末幫忙，並在結尾發放名牌與樓層值勤表，故聽眾為博物館志工。",
                        }
                    ],
                    "explanation_zh": "講者在開頭說：「歡迎各位，感謝大家志願在布里斯托海事博物館十九世紀航海特展開幕週末前來幫忙（thank you for volunteering to help out...）」，並在最後帶大家領取名牌與樓層任務分配表，因此聽眾為 **(B) 博物館志工**。",
                    "distractor_notes": [
                        {"choice_id": "A", "reason_zh": "雖提及古董羅盤展示（antique compass display），但聽眾是館方服務志工而非古董收藏家。"},
                        {"choice_id": "C", "reason_zh": "提及禁用閃光燈（flash photography），並非對燈光技術人員講話。"},
                        {"choice_id": "D", "reason_zh": "未提及旅遊記者採訪。"},
                    ],
                    "vocabulary": [
                        {
                            "term_en": "maritime",
                            "meaning_zh": "海事的；航海的",
                            "example_en": "The maritime museum features historic ship models.",
                        }
                    ],
                    "estimated_time_sec": 25,
                },
                {
                    "item_id": "ag-i-p4-000002-2",
                    "prompt_en": "What has been moved next to the gift shop?",
                    "choices": [
                        {"id": "A", "text_en": "The antique compass display"},
                        {"id": "B", "text_en": "The coat check area"},
                        {"id": "C", "text_en": "The audio guide rental counter"},
                        {"id": "D", "text_en": "The ticket kiosk"},
                    ],
                    "answer_choice_id": "C",
                    "skill_tags": ["explicit_detail", "paraphrase"],
                    "evidence": [
                        {
                            "source_type": "audio_segment",
                            "source_id": "ag-g-p4-000002-seg-2",
                            "quote_en": "we've moved the audio headset rental counter from the main entrance to the alcove beside the gift shop.",
                            "reasoning_zh": "講者說明已將語音耳機租借櫃檯（audio headset rental counter）從正門移至禮品店旁的凹室。",
                        }
                    ],
                    "explanation_zh": "講者在第二段說明：「我們已將語音導覽耳機租借櫃檯（the audio headset rental counter）從正門移到禮品店旁邊的凹室（beside the gift shop）」，選項 **(C) The audio guide rental counter** 為同義改寫。",
                    "distractor_notes": [
                        {"choice_id": "A", "reason_zh": "古董羅盤展示位於 B 展廳（Gallery B），並未移到禮品店旁。"},
                        {"choice_id": "B", "reason_zh": "未提及寄物衣帽間（coat check）。"},
                        {"choice_id": "D", "reason_zh": "僅提及十點對持票觀眾開門，未提移動售票亭。"},
                    ],
                    "vocabulary": [
                        {
                            "term_en": "alcove",
                            "meaning_zh": "凹室；壁龕（大廳或走廊內縮的小空間）",
                            "example_en": "Vending machines are located in the alcove near the elevators.",
                        }
                    ],
                    "estimated_time_sec": 25,
                },
                {
                    "item_id": "ag-i-p4-000002-3",
                    "prompt_en": "What will the listeners do next?",
                    "choices": [
                        {"id": "A", "text_en": "Test the audio headsets"},
                        {"id": "B", "text_en": "Collect their badges and assignment sheets"},
                        {"id": "C", "text_en": "Frame the parchment sea charts"},
                        {"id": "D", "text_en": "Unlock the main entrance doors"},
                    ],
                    "answer_choice_id": "B",
                    "skill_tags": ["next_action", "chronology"],
                    "evidence": [
                        {
                            "source_type": "audio_segment",
                            "source_id": "ag-g-p4-000002-seg-3",
                            "quote_en": "Now, let's walk over to the security desk so each of you can pick up your name badge and floor assignment sheet.",
                            "reasoning_zh": "講者最後說現在一起走到警衛檯領取名牌與樓層任務表（pick up your name badge and floor assignment sheet）。",
                        }
                    ],
                    "explanation_zh": "講者在結尾指示：「現在，我們一起走到警衛櫃檯，讓每位領取各自的名牌與樓層任務分配表（pick up your name badge and floor assignment sheet）」，故選 **(B)**。",
                    "distractor_notes": [
                        {"choice_id": "A", "reason_zh": "僅說明耳機租借櫃檯移位，未要求志工現在測試耳機。"},
                        {"choice_id": "C", "reason_zh": "羊皮紙海圖已是展出文物，並非要志工去裝框。"},
                        {"choice_id": "D", "reason_zh": "十點才開門迎賓，接下來先去警衛檯領名牌。"},
                    ],
                    "vocabulary": [
                        {
                            "term_en": "parchment",
                            "meaning_zh": "羊皮紙",
                            "example_en": "Ancient treaties were written on parchment.",
                        }
                    ],
                    "estimated_time_sec": 25,
                },
            ],
            "provenance": make_provenance(),
            "review_refs": [],
        },
        # --- Group 3: ag-g-p4-000003 (Safety Briefing + Speaker Intent, D4) ---
        {
            "schema_version": "1.0.0",
            "group_id": "ag-g-p4-000003",
            "version": 1,
            "family_id": "ag-fam-p4-factory-safety-briefing-intent",
            "pool": "training",
            "fixture": False,
            "part": 4,
            "layout": "talk",
            "scenario": "manufacturing_safety",
            "difficulty": {
                "level": "D4",
                "rationale_zh": "食品加工廠冷鏈安全晨會簡報，包含異常溫度通報條件與口語意圖推論題。",
                "basis": "editorial",
            },
            "content_status": "draft",
            "stimulus": {
                "documents": [],
                "speakers": [
                    {"speaker_id": "spk_1", "role": "cold_storage_supervisor", "accent": "au"},
                    {"speaker_id": "spk_narrator", "role": "narrator", "accent": "us"},
                ],
                "audio_script": [
                    {
                        "segment_id": "ag-g-p4-000003-seg-1",
                        "speaker_id": "spk_1",
                        "text_en": "Attention, morning shift crew. Before we begin loading the refrigerated trucks for our dairy distributors, I want to review a new safety protocol that goes into effect today across all cold-storage bays.",
                    },
                    {
                        "segment_id": "ag-g-p4-000003-seg-2",
                        "speaker_id": "spk_1",
                        "text_en": "Over the weekend, technicians installed digital thermal alarms above each freezer door. If a freezer door remains open for more than ninety seconds while forklifts are moving pallets, an amber warning light will flash.",
                    },
                    {
                        "segment_id": "ag-g-p4-000003-seg-3",
                        "speaker_id": "spk_1",
                        "text_en": "We certainly don't want a repeat of last month's spoiled yogurt incident. So if you see that amber light flashing, pause your forklift transfers immediately and close the insulated curtain before proceeding. Finally, anyone whose thermal gloves are worn out can exchange them for a new pair at the equipment cage.",
                    },
                    {
                        "segment_id": "ag-g-p4-000003-seg-q1",
                        "speaker_id": "spk_narrator",
                        "text_en": "What was installed in the facility over the weekend?",
                    },
                    {
                        "segment_id": "ag-g-p4-000003-seg-q2",
                        "speaker_id": "spk_narrator",
                        "text_en": "Why does the speaker say, 'We certainly don't want a repeat of last month's spoiled yogurt incident'?",
                    },
                    {
                        "segment_id": "ag-g-p4-000003-seg-q3",
                        "speaker_id": "spk_narrator",
                        "text_en": "What can employees do at the equipment cage?",
                    },
                ],
            },
            "assets": [
                {
                    "asset_id": "ag-ast-p4-000003-audio",
                    "kind": "audio",
                    "status": "planned",
                    "path": None,
                    "sha256": None,
                    "mime_type": None,
                    "duration_ms": None,
                    "source_note_zh": "待合成 Part 4 冷鏈倉儲安全晨會獨白音檔（口音規劃：澳洲男聲 + 美式旁白）。",
                    "review_state": "pending",
                    "segment_times": [],
                }
            ],
            "items": [
                {
                    "item_id": "ag-i-p4-000003-1",
                    "prompt_en": "What was installed in the facility over the weekend?",
                    "choices": [
                        {"id": "A", "text_en": "Automated pallet wrappers"},
                        {"id": "B", "text_en": "Digital temperature alarms"},
                        {"id": "C", "text_en": "High-speed loading ramps"},
                        {"id": "D", "text_en": "Overhead security cameras"},
                    ],
                    "answer_choice_id": "B",
                    "skill_tags": ["explicit_detail", "paraphrase"],
                    "evidence": [
                        {
                            "source_type": "audio_segment",
                            "source_id": "ag-g-p4-000003-seg-2",
                            "quote_en": "Over the weekend, technicians installed digital thermal alarms above each freezer door.",
                            "reasoning_zh": "講者說明週末期間技術人員在每道冷凍庫門上方安裝了數位溫度警報器（digital thermal alarms），對應 digital temperature alarms。",
                        }
                    ],
                    "explanation_zh": "講者在第二段指出：「週末期間，技術人員在每扇冷凍庫門上方安裝了數位溫控警報器（digital thermal alarms）」，選項 **(B) Digital temperature alarms** 以 `temperature` 同義替換 `thermal`。",
                    "distractor_notes": [
                        {"choice_id": "A", "reason_zh": "僅提及堆高機搬運棧板（moving pallets），未安裝自動棧板纏繞機。"},
                        {"choice_id": "C", "reason_zh": "未提及高速裝卸斜坡道。"},
                        {"choice_id": "D", "reason_zh": "門上方安裝的是溫度警報器而非監視攝影機。"},
                    ],
                    "vocabulary": [
                        {
                            "term_en": "thermal",
                            "meaning_zh": "熱量的；溫度的；保溫的",
                            "example_en": "Thermal sensors monitor the temperature inside the cold room.",
                        }
                    ],
                    "estimated_time_sec": 25,
                },
                {
                    "item_id": "ag-i-p4-000003-2",
                    "prompt_en": "Why does the speaker say, \"We certainly don't want a repeat of last month's spoiled yogurt incident\"?",
                    "choices": [
                        {"id": "A", "text_en": "To announce the discontinuation of a dairy product"},
                        {"id": "B", "text_en": "To criticize the quality of a supplier's ingredients"},
                        {"id": "C", "text_en": "To emphasize the importance of following the new procedure"},
                        {"id": "D", "text_en": "To explain why employee shifts have been shortened"},
                    ],
                    "answer_choice_id": "C",
                    "skill_tags": ["speaker_intent"],
                    "evidence": [
                        {
                            "source_type": "audio_segment",
                            "source_id": "ag-g-p4-000003-seg-2",
                            "quote_en": "If a freezer door remains open for more than ninety seconds while forklifts are moving pallets, an amber warning light will flash.",
                            "reasoning_zh": "前文說明冷凍庫門開啟超過九十秒會閃黃燈。",
                        },
                        {
                            "source_type": "audio_segment",
                            "source_id": "ag-g-p4-000003-seg-3",
                            "quote_en": "We certainly don't want a repeat of last month's spoiled yogurt incident. So if you see that amber light flashing, pause your forklift transfers immediately and close the insulated curtain",
                            "reasoning_zh": "講者提及上個月優格變質事件，旨在強調嚴格遵守新關門程序的重要性。",
                        },
                    ],
                    "explanation_zh": "本題考說話者意圖。講者在介紹完冷凍庫門超時開啟的黃燈警報後說：「我們絕對不想重蹈上個月優格腐壞事件的覆轍，所以若看到黃燈閃爍，請立即暫停堆高機搬運並拉上隔熱簾」，目的在於 **(C) 強調遵守這項新溫控安全程序的重要性**。",
                    "distractor_notes": [
                        {"choice_id": "A", "reason_zh": "並未宣布停產某項乳製品。"},
                        {"choice_id": "B", "reason_zh": "優格腐壞是因為冷凍庫失溫，而非批評原料供應商。"},
                        {"choice_id": "D", "reason_zh": "未提及縮短員工班次時數。"},
                    ],
                    "vocabulary": [
                        {
                            "term_en": "spoiled",
                            "meaning_zh": "腐壞的；變質的（食物）",
                            "example_en": "A power outage resulted in several crates of spoiled milk.",
                        }
                    ],
                    "estimated_time_sec": 30,
                },
                {
                    "item_id": "ag-i-p4-000003-3",
                    "prompt_en": "What can employees do at the equipment cage?",
                    "choices": [
                        {"id": "A", "text_en": "Sign out a two-way radio"},
                        {"id": "B", "text_en": "Charge forklift batteries"},
                        {"id": "C", "text_en": "Replace worn protective gloves"},
                        {"id": "D", "text_en": "Pick up delivery manifests"},
                    ],
                    "answer_choice_id": "C",
                    "skill_tags": ["explicit_detail", "paraphrase"],
                    "evidence": [
                        {
                            "source_type": "audio_segment",
                            "source_id": "ag-g-p4-000003-seg-3",
                            "quote_en": "anyone whose thermal gloves are worn out can exchange them for a new pair at the equipment cage.",
                            "reasoning_zh": "講者告知防寒手套磨損（thermal gloves are worn out）的員工可至器材室換領新的一雙。",
                        }
                    ],
                    "explanation_zh": "講者在結尾提醒：「任何人的防寒手套若已磨損（worn out），皆可至器材管理室（at the equipment cage）換領新的一雙」，對應 **(C) 更換磨損的防護手套**。",
                    "distractor_notes": [
                        {"choice_id": "A", "reason_zh": "未提及領取雙向對講機。"},
                        {"choice_id": "B", "reason_zh": "未提及在器材室替堆高機電池充電。"},
                        {"choice_id": "D", "reason_zh": "未提及領取貨運清單。"},
                    ],
                    "vocabulary": [
                        {
                            "term_en": "worn out",
                            "meaning_zh": "磨損的；破舊不堪的",
                            "example_en": "Replace worn-out tires before driving in winter conditions.",
                        }
                    ],
                    "estimated_time_sec": 25,
                },
            ],
            "provenance": make_provenance(),
            "review_refs": [],
        },
        # --- Group 4: ag-g-p4-000004 ---
        {
            "schema_version": "1.0.0",
            "group_id": "ag-g-p4-000004",
            "version": 1,
            "family_id": "ag-fam-p4-radio-traffic-commuter-ferry",
            "pool": "training",
            "fixture": False,
            "part": 4,
            "layout": "talk",
            "scenario": "transportation_commute",
            "difficulty": {
                "level": "D3",
                "rationale_zh": "市政碼頭交通廣播，包含航班暫停原因、替代交通工具與退票／改搭方式。",
                "basis": "editorial",
            },
            "content_status": "draft",
            "stimulus": {
                "documents": [],
                "speakers": [
                    {"speaker_id": "spk_1", "role": "ferry_terminal_announcer", "accent": "ca"},
                    {"speaker_id": "spk_narrator", "role": "narrator", "accent": "us"},
                ],
                "audio_script": [
                    {
                        "segment_id": "ag-g-p4-000004-seg-1",
                        "speaker_id": "spk_1",
                        "text_en": "May I have your attention, please. Due to dense coastal fog reducing visibility across the bay, all high-speed catamaran departures from Pier Seven to Bayside Financial District have been suspended until ten-thirty this morning.",
                    },
                    {
                        "segment_id": "ag-g-p4-000004-seg-2",
                        "speaker_id": "spk_1",
                        "text_en": "To help commuters reach downtown offices with minimal delay, the Port Authority has arranged complimentary express shuttle buses that will depart every fifteen minutes from Bus Bay C, directly outside the west terminal doors.",
                    },
                    {
                        "segment_id": "ag-g-p4-000004-seg-3",
                        "speaker_id": "spk_1",
                        "text_en": "Simply show your digital or paper ferry ticket to the bus driver when boarding. Passengers who prefer not to travel by bus may have their unused ferry fare refunded in full at Customer Service Window Three.",
                    },
                    {
                        "segment_id": "ag-g-p4-000004-seg-q1",
                        "speaker_id": "spk_narrator",
                        "text_en": "Why has ferry service from Pier Seven been suspended?",
                    },
                    {
                        "segment_id": "ag-g-p4-000004-seg-q2",
                        "speaker_id": "spk_narrator",
                        "text_en": "How can commuters board the express shuttle bus?",
                    },
                    {
                        "segment_id": "ag-g-p4-000004-seg-q3",
                        "speaker_id": "spk_narrator",
                        "text_en": "Why should passengers visit Customer Service Window Three?",
                    },
                ],
            },
            "assets": [
                {
                    "asset_id": "ag-ast-p4-000004-audio",
                    "kind": "audio",
                    "status": "planned",
                    "path": None,
                    "sha256": None,
                    "mime_type": None,
                    "duration_ms": None,
                    "source_note_zh": "待合成 Part 4 渡輪碼頭廣播獨白音檔（口音規劃：加拿大女聲 + 美式旁白）。",
                    "review_state": "pending",
                    "segment_times": [],
                }
            ],
            "items": [
                {
                    "item_id": "ag-i-p4-000004-1",
                    "prompt_en": "Why has ferry service from Pier Seven been suspended?",
                    "choices": [
                        {"id": "A", "text_en": "A pier is undergoing structural repairs."},
                        {"id": "B", "text_en": "A vessel is experiencing engine trouble."},
                        {"id": "C", "text_en": "Weather conditions have reduced visibility."},
                        {"id": "D", "text_en": "A harbor regatta is taking place."},
                    ],
                    "answer_choice_id": "C",
                    "skill_tags": ["explicit_detail", "paraphrase"],
                    "evidence": [
                        {
                            "source_type": "audio_segment",
                            "source_id": "ag-g-p4-000004-seg-1",
                            "quote_en": "Due to dense coastal fog reducing visibility across the bay, all high-speed catamaran departures from Pier Seven ... have been suspended",
                            "reasoning_zh": "廣播說明因沿岸濃霧降低海灣能見度（dense coastal fog reducing visibility），故暫停七號碼頭的高速雙體船航班。",
                        }
                    ],
                    "explanation_zh": "廣播開頭指出：「由於沿岸濃霧降低了整個海灣的能見度（Due to dense coastal fog reducing visibility across the bay），所有自七號碼頭開往海灣金融區的高速渡輪暫停行駛至上午十點半」，故選 **(C)**。",
                    "distractor_notes": [
                        {"choice_id": "A", "reason_zh": "廣播未提及碼頭結構維修。"},
                        {"choice_id": "B", "reason_zh": "停航原因為濃霧而非船隻引擎故障。"},
                        {"choice_id": "D", "reason_zh": "未提及港口帆船賽。"},
                    ],
                    "vocabulary": [
                        {
                            "term_en": "visibility",
                            "meaning_zh": "能見度",
                            "example_en": "Heavy rain reduced visibility on the highway to less than fifty meters.",
                        }
                    ],
                    "estimated_time_sec": 25,
                },
                {
                    "item_id": "ag-i-p4-000004-2",
                    "prompt_en": "How can commuters board the express shuttle bus?",
                    "choices": [
                        {"id": "A", "text_en": "By paying a two-dollar surcharge in cash"},
                        {"id": "B", "text_en": "By presenting their existing ferry ticket"},
                        {"id": "C", "text_en": "By registering on the Port Authority app"},
                        {"id": "D", "text_en": "By obtaining a transfer slip from a security guard"},
                    ],
                    "answer_choice_id": "B",
                    "skill_tags": ["explicit_detail", "paraphrase"],
                    "evidence": [
                        {
                            "source_type": "audio_segment",
                            "source_id": "ag-g-p4-000004-seg-3",
                            "quote_en": "Simply show your digital or paper ferry ticket to the bus driver when boarding.",
                            "reasoning_zh": "廣播說明上車時只需向公車司機出示數位或紙本渡輪船票即可免費搭乘接駁車。",
                        }
                    ],
                    "explanation_zh": "廣播在第二、三段說明港務局已安排免費直達接駁巴士（complimentary express shuttle buses），「上車時只需向巴士司機出示您的電子或紙本渡輪船票即可（Simply show your digital or paper ferry ticket to the bus driver）」，對應 **(B) 出示原有的渡輪船票**。",
                    "distractor_notes": [
                        {"choice_id": "A", "reason_zh": "接駁巴士為免費提供（complimentary），無須額外付兩美元現金。"},
                        {"choice_id": "C", "reason_zh": "纸本或電子船票皆可直接出示，無須另在 App 登記。"},
                        {"choice_id": "D", "reason_zh": "未要求向警衛索取轉乘憑證。"},
                    ],
                    "vocabulary": [
                        {
                            "term_en": "complimentary",
                            "meaning_zh": "免費招待的；附贈的",
                            "example_en": "Hotel guests enjoy complimentary breakfast each morning.",
                        }
                    ],
                    "estimated_time_sec": 25,
                },
                {
                    "item_id": "ag-i-p4-000004-3",
                    "prompt_en": "Why should passengers visit Customer Service Window Three?",
                    "choices": [
                        {"id": "A", "text_en": "To report lost luggage"},
                        {"id": "B", "text_en": "To pick up a printed regional map"},
                        {"id": "C", "text_en": "To receive a full refund for an unused ticket"},
                        {"id": "D", "text_en": "To renew a monthly parking pass"},
                    ],
                    "answer_choice_id": "C",
                    "skill_tags": ["next_action", "explicit_detail"],
                    "evidence": [
                        {
                            "source_type": "audio_segment",
                            "source_id": "ag-g-p4-000004-seg-3",
                            "quote_en": "Passengers who prefer not to travel by bus may have their unused ferry fare refunded in full at Customer Service Window Three.",
                            "reasoning_zh": "不想改搭巴士的乘客可至三號客服窗口辦理未使用船票的全額退費（refunded in full）。",
                        }
                    ],
                    "explanation_zh": "廣播最後一句說明：「不願改搭巴士的乘客，可至三號客服窗口將未使用的渡輪票款全額退費（have their unused ferry fare refunded in full at Customer Service Window Three）」，故選 **(C)**。",
                    "distractor_notes": [
                        {"choice_id": "A", "reason_zh": "未提及遺失行李申報。"},
                        {"choice_id": "B", "reason_zh": "未提及索取紙本區域地圖。"},
                        {"choice_id": "D", "reason_zh": "未提及續訂月租停車證。"},
                    ],
                    "vocabulary": [
                        {
                            "term_en": "refund in full",
                            "meaning_zh": "全額退費",
                            "example_en": "Canceled tickets will be refunded in full within five business days.",
                        }
                    ],
                    "estimated_time_sec": 25,
                },
            ],
            "provenance": make_provenance(),
            "review_refs": [],
        },
        # --- Group 5: ag-g-p4-000005 (Graphic Integration: Quarterly Regional Sales, D5) ---
        {
            "schema_version": "1.0.0",
            "group_id": "ag-g-p4-000005",
            "version": 1,
            "family_id": "ag-fam-p4-graphic-quarterly-sales-presentation",
            "pool": "training",
            "fixture": False,
            "part": 4,
            "layout": "talk",
            "scenario": "sales_analytics",
            "difficulty": {
                "level": "D5",
                "rationale_zh": "高難度圖表整合簡報，講者僅提數據特徵（如「唯一達成雙位數營收成長但退貨率卻高達 6.8% 的區域」），考生須交叉比對表格數值定位正確區域。",
                "basis": "editorial",
            },
            "content_status": "draft",
            "stimulus": {
                "documents": [
                    {
                        "document_id": "ag-doc-p4-000005-1",
                        "genre": "report_table",
                        "title_en": "Lumina Home Appliances — Q3 Regional Performance",
                        "blocks": [
                            {
                                "block_id": "ag-blk-p4-000005-1",
                                "type": "table",
                                "columns": ["Region", "Q3 Revenue Growth", "Product Return Rate", "Top-Selling Category"],
                                "rows": [
                                    ["North", "+4.2%", "2.1%", "Air Purifiers"],
                                    ["South", "+11.5%", "6.8%", "Espresso Machines"],
                                    ["East", "+6.0%", "1.9%", "Induction Cooktops"],
                                    ["West", "-1.4%", "2.5%", "Robotic Vacuums"],
                                ],
                            }
                        ],
                    }
                ],
                "speakers": [
                    {"speaker_id": "spk_1", "role": "vice_president_of_sales", "accent": "us"},
                    {"speaker_id": "spk_narrator", "role": "narrator", "accent": "us"},
                ],
                "audio_script": [
                    {
                        "segment_id": "ag-g-p4-000005-seg-1",
                        "speaker_id": "spk_1",
                        "text_en": "Good afternoon, board members. Please turn your attention to the third-quarter regional performance table on the screen. Overall, three of our four domestic territories posted positive revenue growth this quarter.",
                    },
                    {
                        "segment_id": "ag-g-p4-000005-seg-2",
                        "speaker_id": "spk_1",
                        "text_en": "As you can see, the territory whose top-selling category was espresso machines achieved an impressive eleven-point-five percent jump in revenue. However, that same region also recorded an unusually high product return rate of six-point-eight percent.",
                    },
                    {
                        "segment_id": "ag-g-p4-000005-seg-3",
                        "speaker_id": "spk_1",
                        "text_en": "Customer survey cards indicate that the espresso machines themselves aren't defective; rather, buyers find the decalcifying instructions in the printed manual confusing. Meanwhile, for the single region that experienced a slight revenue decline, we plan to launch a targeted social media campaign in October to boost robotic vacuum sales before the holiday shopping season.",
                    },
                    {
                        "segment_id": "ag-g-p4-000005-seg-q1",
                        "speaker_id": "spk_narrator",
                        "text_en": "Look at the graphic. Which region had both the highest revenue growth and the highest product return rate?",
                    },
                    {
                        "segment_id": "ag-g-p4-000005-seg-q2",
                        "speaker_id": "spk_narrator",
                        "text_en": "According to the speaker, what caused the high rate of espresso machine returns?",
                    },
                    {
                        "segment_id": "ag-g-p4-000005-seg-q3",
                        "speaker_id": "spk_narrator",
                        "text_en": "Look at the graphic. Which region will be the focus of an October social media campaign?",
                    },
                ],
            },
            "assets": [
                {
                    "asset_id": "ag-ast-p4-000005-audio",
                    "kind": "audio",
                    "status": "planned",
                    "path": None,
                    "sha256": None,
                    "mime_type": None,
                    "duration_ms": None,
                    "source_note_zh": "待合成 Part 4 季度銷售圖表簡報音檔（口音規劃：美式女聲 + 美式旁白）。",
                    "review_state": "pending",
                    "segment_times": [],
                }
            ],
            "items": [
                {
                    "item_id": "ag-i-p4-000005-1",
                    "prompt_en": "Look at the graphic. Which region had both the highest revenue growth and the highest product return rate?",
                    "choices": [
                        {"id": "A", "text_en": "North"},
                        {"id": "B", "text_en": "South"},
                        {"id": "C", "text_en": "East"},
                        {"id": "D", "text_en": "West"},
                    ],
                    "answer_choice_id": "B",
                    "skill_tags": ["graphic_integration", "explicit_detail"],
                    "evidence": [
                        {
                            "source_type": "audio_segment",
                            "source_id": "ag-g-p4-000005-seg-2",
                            "quote_en": "the territory whose top-selling category was espresso machines achieved an impressive eleven-point-five percent jump in revenue. However, that same region also recorded an unusually high product return rate of six-point-eight percent.",
                            "reasoning_zh": "講者指出熱銷品類為義式濃縮咖啡機、營收成長 11.5% 且退貨率達 6.8% 的區域。",
                        },
                        {
                            "source_type": "document_block",
                            "source_id": "ag-blk-p4-000005-1",
                            "quote_en": "South | +11.5% | 6.8% | Espresso Machines",
                            "reasoning_zh": "對照表格，成長 +11.5%、退貨率 6.8% 且熱銷品為 Espresso Machines 的區域為 South。",
                        },
                    ],
                    "explanation_zh": "講者在第二段指出：「熱銷品類為義式濃縮咖啡機的區域創下 11.5% 的營收成長，但同區域也出現高達 6.8% 的異常退貨率」。對照表格數值，符合 `+11.5%` 與 `6.8%` 的區域為 **(B) South**。",
                    "distractor_notes": [
                        {"choice_id": "A", "reason_zh": "North 成長率為 +4.2%、退貨率為 2.1%。"},
                        {"choice_id": "C", "reason_zh": "East 成長率為 +6.0%、退貨率為 1.9%，為退貨率最低而非最高。"},
                        {"choice_id": "D", "reason_zh": "West 營收成長為負值（-1.4%）。"},
                    ],
                    "vocabulary": [
                        {
                            "term_en": "return rate",
                            "meaning_zh": "退貨率",
                            "example_en": "Clear sizing charts helped reduce our online apparel return rate.",
                        }
                    ],
                    "estimated_time_sec": 30,
                },
                {
                    "item_id": "ag-i-p4-000005-2",
                    "prompt_en": "According to the speaker, what caused the high rate of espresso machine returns?",
                    "choices": [
                        {"id": "A", "text_en": "Glass carafes were damaged during shipping."},
                        {"id": "B", "text_en": "The heating element failed after a few uses."},
                        {"id": "C", "text_en": "The printed maintenance instructions were unclear."},
                        {"id": "D", "text_en": "A competitor released a lower-priced model."},
                    ],
                    "answer_choice_id": "C",
                    "skill_tags": ["explicit_detail", "paraphrase"],
                    "evidence": [
                        {
                            "source_type": "audio_segment",
                            "source_id": "ag-g-p4-000005-seg-3",
                            "quote_en": "Customer survey cards indicate that the espresso machines themselves aren't defective; rather, buyers find the decalcifying instructions in the printed manual confusing.",
                            "reasoning_zh": "顧客問卷顯示機器本身無瑕疵，而是紙本說明書中的除水垢保養說明令人困惑（confusing），對應選項 C「紙本保養說明不夠清楚」。",
                        }
                    ],
                    "explanation_zh": "講者在第三段說明：「顧客問卷卡顯示咖啡機本身並沒有瑕疵（aren't defective），而是買家覺得紙本手冊中的除水垢清潔說明令人困惑難懂（find the decalcifying instructions in the printed manual confusing）」，選項 **(C)** 以 `printed maintenance instructions were unclear` 精準改寫。",
                    "distractor_notes": [
                        {"choice_id": "A", "reason_zh": "獨白未提及運送途中玻璃壺破損。"},
                        {"choice_id": "B", "reason_zh": "講者明確排除機器本身有故障瑕疵（aren't defective）。"},
                        {"choice_id": "D", "reason_zh": "未提及競爭對手推出低價機型。"},
                    ],
                    "vocabulary": [
                        {
                            "term_en": "defective",
                            "meaning_zh": "有瑕疵的；故障的",
                            "example_en": "Defective units will be replaced free of charge.",
                        }
                    ],
                    "estimated_time_sec": 25,
                },
                {
                    "item_id": "ag-i-p4-000005-3",
                    "prompt_en": "Look at the graphic. Which region will be the focus of an October social media campaign?",
                    "choices": [
                        {"id": "A", "text_en": "North"},
                        {"id": "B", "text_en": "South"},
                        {"id": "C", "text_en": "East"},
                        {"id": "D", "text_en": "West"},
                    ],
                    "answer_choice_id": "D",
                    "skill_tags": ["graphic_integration", "next_action"],
                    "evidence": [
                        {
                            "source_type": "audio_segment",
                            "source_id": "ag-g-p4-000005-seg-3",
                            "quote_en": "for the single region that experienced a slight revenue decline, we plan to launch a targeted social media campaign in October to boost robotic vacuum sales",
                            "reasoning_zh": "講者表示針對唯一出現營收微幅下滑（-1.4%）且主推掃地機器人（Robotic Vacuums）的區域，將於十月展開社群媒體行銷活動。",
                        },
                        {
                            "source_type": "document_block",
                            "source_id": "ag-blk-p4-000005-1",
                            "quote_en": "West | -1.4% | 2.5% | Robotic Vacuums",
                            "reasoning_zh": "對照表格，營收微幅下滑（-1.4%）且對應 Robotic Vacuums 的區域為 West。",
                        },
                    ],
                    "explanation_zh": "講者在最後一段指出：「針對唯一出現營收微幅下滑（experienced a slight revenue decline）的區域，我們計畫在十月推出目標式社群媒體宣傳活動，以提振掃地機器人銷量」。對照表格，`Q3 Revenue Growth` 為負數（`-1.4%`）且對應 `Robotic Vacuums` 的區域為 **(D) West**。",
                    "distractor_notes": [
                        {"choice_id": "A", "reason_zh": "North 營收為正成長（+4.2%），熱銷品為空氣清淨機。"},
                        {"choice_id": "B", "reason_zh": "South 營收成長最高（+11.5%），並非營收下滑區域。"},
                        {"choice_id": "C", "reason_zh": "East 營收為正成長（+6.0%），熱銷品為感應爐。"},
                    ],
                    "vocabulary": [
                        {
                            "term_en": "revenue decline",
                            "meaning_zh": "營收下滑",
                            "example_en": "Store closures contributed to a slight revenue decline in the fourth quarter.",
                        }
                    ],
                    "estimated_time_sec": 30,
                },
            ],
            "provenance": make_provenance(),
            "review_refs": [],
        },
    ]
    return groups


def main() -> None:
    out_dir = ROOT / "drafts" / "batch-ag-0004"
    out_dir.mkdir(parents=True, exist_ok=True)
    groups = build_groups()
    groups_path = out_dir / "groups.jsonl"
    with groups_path.open("w", encoding="utf-8") as f:
        for g in groups:
            f.write(json.dumps(g, ensure_ascii=False) + "\n")
    print(f"Wrote {len(groups)} groups ({sum(len(g['items']) for g in groups)} items) to {groups_path}")


if __name__ == "__main__":
    main()
