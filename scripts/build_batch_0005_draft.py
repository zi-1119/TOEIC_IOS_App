#!/usr/bin/env python3
"""
Construct draft groups.jsonl for batch-ag-0005 (Part 7 Reading Comprehension: 7 groups = 28 items, pool="training"):
- Single Passages (4 groups, 3+3+3+4 = 13 items):
  - ag-g-p7-000001: Parking garage repaving notice (3 items, D1)
  - ag-g-p7-000002: Ceramic tableware supplier quality test email (3 items, D2)
  - ag-g-p7-000003: IT support team chat chain with speaker intent (3 items, D3)
  - ag-g-p7-000004: Municipal green rooftop grant article with [[position:1]]..[[position:4]] insertion (4 items, D4)
- Double Passages (2 groups, 5+5 = 10 items):
  - ag-g-p7-000005: Supply chain forum schedule table + speaker swap email (5 items, D4)
  - ag-g-p7-000006: Commercial coffee machine warranty policy + service claim form (5 items, D4)
- Triple Passage (1 group, 5 items):
  - ag-g-p7-000007: Catering package rate table + client revision email + final invoice (5 items, D5)
"""

import json
from pathlib import Path

from build_batch_0001_draft import make_provenance

ROOT = Path(__file__).resolve().parent.parent


def build_groups() -> list:
    groups = [
        # --- Group 1: ag-g-p7-000001 (Single Passage, 3 items, D1) ---
        {
            "schema_version": "1.0.0",
            "group_id": "ag-g-p7-000001",
            "version": 1,
            "family_id": "ag-fam-p7-single-notice-parking-garage-repaving",
            "pool": "training",
            "fixture": False,
            "part": 7,
            "layout": "single_passage",
            "scenario": "office_facilities",
            "difficulty": {
                "level": "D1",
                "rationale_zh": "結構清晰的辦公大樓物業公告，考驗公告目的、施工日期細節與電動車充電限制條件。",
                "basis": "editorial",
            },
            "content_status": "draft",
            "stimulus": {
                "documents": [
                    {
                        "document_id": "ag-doc-p7-000001-1",
                        "genre": "notice",
                        "title_en": "NOTICE TO ALL TENANTS: Underground Parking Garage Repaving",
                        "blocks": [
                            {
                                "block_id": "ag-blk-p7-000001-1",
                                "type": "text",
                                "text_en": (
                                    "Please be advised that Crestview Tower Management will resurface and repaint both levels of the underground parking garage next week. "
                                    "To minimize disruption to commuters, the work will be completed in two phases:\n\n"
                                    "• Phase 1 (Level B1): Closed from Monday, November 9, at 6:00 A.M. through Tuesday, November 10, at 8:00 P.M.\n"
                                    "• Phase 2 (Level B2): Closed from Wednesday, November 11, at 6:00 A.M. through Thursday, November 12, at 8:00 P.M.\n\n"
                                    "During each closure, monthly pass holders who normally park on the affected level may use the overflow surface lot on Elm Street at no extra cost by displaying their yellow hangtag on the rearview mirror. "
                                    "Please note that the electric vehicle charging stations on Level B1 will be shut off during Phase 1; drivers requiring charging stations on Monday or Tuesday should use the public charging hub across from City Hall."
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
                    "item_id": "ag-i-p7-000001-1",
                    "prompt_en": "What is the main purpose of the notice?",
                    "choices": [
                        {"id": "A", "text_en": "To announce an increase in monthly parking fees"},
                        {"id": "B", "text_en": "To inform tenants about temporary garage closures for maintenance"},
                        {"id": "C", "text_en": "To introduce a new security gate system"},
                        {"id": "D", "text_en": "To recruit attendants for the Elm Street surface lot"},
                    ],
                    "answer_choice_id": "B",
                    "skill_tags": ["main_idea_purpose"],
                    "evidence": [
                        {
                            "source_type": "document_block",
                            "source_id": "ag-blk-p7-000001-1",
                            "quote_en": "Crestview Tower Management will resurface and repaint both levels of the underground parking garage next week.",
                            "reasoning_zh": "首段即說明物業管理處下週將對地下停車場兩樓層進行重新鋪面與標線粉刷，並分兩階段封閉。",
                        }
                    ],
                    "explanation_zh": "公告首段說明 Crestview 大樓管理處將於下週對地下停車場兩個樓層進行重新鋪面與重新畫線（resurface and repaint），並列出 B1 與 B2 暫時封閉的時程與替代停車安排，故主旨為 **(B) 通知租戶因維護工程而暫時封閉停車場**。",
                    "distractor_notes": [
                        {"choice_id": "A", "reason_zh": "文中提到月租戶可免費（at no extra cost）使用替代平面停車場，並未調漲月費。"},
                        {"choice_id": "C", "reason_zh": "未提及新門禁閘門系統。"},
                        {"choice_id": "D", "reason_zh": "未提及招募停車場管理員。"},
                    ],
                    "vocabulary": [
                        {
                            "term_en": "resurface",
                            "meaning_zh": "重新鋪設路面",
                            "example_en": "The city will resurface the main avenue next month.",
                        }
                    ],
                    "estimated_time_sec": 30,
                },
                {
                    "item_id": "ag-i-p7-000001-2",
                    "prompt_en": "When will Level B2 be closed?",
                    "choices": [
                        {"id": "A", "text_en": "On Monday and Tuesday"},
                        {"id": "B", "text_en": "On Tuesday and Wednesday"},
                        {"id": "C", "text_en": "On Wednesday and Thursday"},
                        {"id": "D", "text_en": "On Thursday and Friday"},
                    ],
                    "answer_choice_id": "C",
                    "skill_tags": ["explicit_detail"],
                    "evidence": [
                        {
                            "source_type": "document_block",
                            "source_id": "ag-blk-p7-000001-1",
                            "quote_en": "Phase 2 (Level B2): Closed from Wednesday, November 11, at 6:00 A.M. through Thursday, November 12, at 8:00 P.M.",
                            "reasoning_zh": "第二階段（B2 層）封閉時間為 11 月 11 日週三早上六點至 11 月 12 日週四晚上八點。",
                        }
                    ],
                    "explanation_zh": "依據條列項目第二點，`Phase 2 (Level B2)` 封閉時間為 `Wednesday, November 11, at 6:00 A.M. through Thursday, November 12, at 8:00 P.M.`，即 **(C) 週三與週四**。",
                    "distractor_notes": [
                        {"choice_id": "A", "reason_zh": "週一與週二為 B1 樓層（Phase 1）的封閉時段。"},
                        {"choice_id": "B", "reason_zh": "週二屬於 B1 封閉日，B2 從週三才開始封閉。"},
                        {"choice_id": "D", "reason_zh": "工程於週四晚間八點結束，週五並未封閉。"},
                    ],
                    "vocabulary": [
                        {
                            "term_en": "overflow lot",
                            "meaning_zh": "預備／第二停車場（主停車場客滿或封閉時使用）",
                            "example_en": "Visitors were directed to the overflow lot on Elm Street.",
                        }
                    ],
                    "estimated_time_sec": 25,
                },
                {
                    "item_id": "ag-i-p7-000001-3",
                    "prompt_en": "What are monthly pass holders instructed to do to park in the Elm Street lot?",
                    "choices": [
                        {"id": "A", "text_en": "Register their license plate online"},
                        {"id": "B", "text_en": "Display their yellow hangtag in their vehicle"},
                        {"id": "C", "text_en": "Pay a temporary deposit at the security desk"},
                        {"id": "D", "text_en": "Park only in spaces marked for electric vehicles"},
                    ],
                    "answer_choice_id": "B",
                    "skill_tags": ["conditions_exceptions", "explicit_detail"],
                    "evidence": [
                        {
                            "source_type": "document_block",
                            "source_id": "ag-blk-p7-000001-1",
                            "quote_en": "monthly pass holders who normally park on the affected level may use the overflow surface lot on Elm Street at no extra cost by displaying their yellow hangtag on the rearview mirror.",
                            "reasoning_zh": "月租戶只需在後視鏡掛上黃色吊牌（displaying their yellow hangtag）即可免費停放於 Elm Street 平面停車場。",
                        }
                    ],
                    "explanation_zh": "末段首句說明：「受影響樓層的月租通行證持有人，只要將黃色停車吊牌掛在車內後視鏡上（by displaying their yellow hangtag on the rearview mirror），即可免費使用 Elm Street 的預備平面停車場」，故選 **(B)**。",
                    "distractor_notes": [
                        {"choice_id": "A", "reason_zh": "文中未要求上網登錄車牌號碼。"},
                        {"choice_id": "C", "reason_zh": "文中明確表示不額外收費（at no extra cost），無須繳交臨時押金。"},
                        {"choice_id": "D", "reason_zh": "電動車充電站位於 B1 與市政廳對面，並非規定在 Elm Street 只能停電動車位。"},
                    ],
                    "vocabulary": [
                        {
                            "term_en": "rearview mirror",
                            "meaning_zh": "車內後視鏡",
                            "example_en": "Hang your parking permit from the rearview mirror.",
                        }
                    ],
                    "estimated_time_sec": 30,
                },
            ],
            "provenance": make_provenance(),
            "review_refs": [],
        },
        # --- Group 2: ag-g-p7-000002 (Single Passage, 3 items, D2) ---
        {
            "schema_version": "1.0.0",
            "group_id": "ag-g-p7-000002",
            "version": 1,
            "family_id": "ag-fam-p7-single-email-supplier-batch-testing",
            "pool": "training",
            "fixture": False,
            "part": 7,
            "layout": "single_passage",
            "scenario": "procurement_quality",
            "difficulty": {
                "level": "D2",
                "rationale_zh": "供應商寄給連鎖餐飲採購主管的電子郵件，考驗品質測試細節、語意改寫與後續簽約步驟。",
                "basis": "editorial",
            },
            "content_status": "draft",
            "stimulus": {
                "documents": [
                    {
                        "document_id": "ag-doc-p7-000002-1",
                        "genre": "email",
                        "title_en": "Subject: Thermal Shock Test Results — Verona Stoneware Line",
                        "blocks": [
                            {
                                "block_id": "ag-blk-p7-000002-1",
                                "type": "text",
                                "text_en": (
                                    "To: Kenneth Cho <k.cho@bistrocollective.com>\n"
                                    "From: Nadia Al-Mansoor <nalmansoor@kilncraftceramics.com>\n"
                                    "Date: October 19\n"
                                    "Subject: Thermal Shock Test Results — Verona Stoneware Line\n\n"
                                    "Dear Mr. Cho,\n\n"
                                    "Thank you for visiting our showroom last week to evaluate tableware options for Bistro Collective's upcoming restaurant openings in Denver and Salt Lake City. "
                                    "During our meeting, you asked whether the matte glaze on our Verona Stoneware soup bowls could withstand high-temperature commercial dishwashers without chipping or fading.\n\n"
                                    "Our quality assurance lab completed a 200-cycle thermal durability test yesterday, and I am pleased to report that all twelve test bowls showed zero surface wear or discoloration. "
                                    "I have attached the official laboratory certificate to this message for your review.\n\n"
                                    "In addition, I have dispatched a box containing four sample place settings in the olive-green finish to your Denver regional office via express courier. "
                                    "Once your culinary team has had a chance to inspect the samples, please let me know how many sets you would like to include in your initial purchase order so we can reserve kiln capacity for November.\n\n"
                                    "Best regards,\n"
                                    "Nadia Al-Mansoor\n"
                                    "Commercial Accounts Manager, KilnCraft Ceramics"
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
                    "item_id": "ag-i-p7-000002-1",
                    "prompt_en": "What concern did Mr. Cho raise during last week's meeting?",
                    "choices": [
                        {"id": "A", "text_en": "Whether the bowls could endure commercial dishwashing temperatures"},
                        {"id": "B", "text_en": "Whether KilnCraft Ceramics offered an olive-green color"},
                        {"id": "C", "text_en": "Whether shipping to Salt Lake City would cost extra"},
                        {"id": "D", "text_en": "Whether the soup bowls were too heavy for servers to carry"},
                    ],
                    "answer_choice_id": "A",
                    "skill_tags": ["explicit_detail", "paraphrase"],
                    "evidence": [
                        {
                            "source_type": "document_block",
                            "source_id": "ag-blk-p7-000002-1",
                            "quote_en": "During our meeting, you asked whether the matte glaze on our Verona Stoneware soup bowls could withstand high-temperature commercial dishwashers without chipping or fading.",
                            "reasoning_zh": "Cho 先生上週會面時詢問湯碗的霧面釉料能否承受高溫商用洗碗機而不剝落或褪色，以 endure 改寫 withstand。",
                        }
                    ],
                    "explanation_zh": "第一段第二句明確提到：「在我們的會議中，您詢問我們 Verona 陶製湯碗上的霧面釉料是否能承受高溫商用洗碗機（withstand high-temperature commercial dishwashers）而不缺角或褪色」，選項 **(A)** 以 `endure` 同義改寫 `withstand`。",
                    "distractor_notes": [
                        {"choice_id": "B", "reason_zh": "橄欖綠樣品已直接寄出，並非他擔心的問題。"},
                        {"choice_id": "C", "reason_zh": "信中未討論運往鹽湖城的額外運費。"},
                        {"choice_id": "D", "reason_zh": "測試的是耐溫與表面耐磨度，而非碗盤重量。"},
                    ],
                    "vocabulary": [
                        {
                            "term_en": "withstand",
                            "meaning_zh": "承受；耐受（高溫、壓力等）",
                            "example_en": "The stoneware is designed to withstand extreme heat.",
                        }
                    ],
                    "estimated_time_sec": 30,
                },
                {
                    "item_id": "ag-i-p7-000002-2",
                    "prompt_en": "What did Ms. Al-Mansoor attach to the email?",
                    "choices": [
                        {"id": "A", "text_en": "A floor plan of the Denver showroom"},
                        {"id": "B", "text_en": "A laboratory test certificate"},
                        {"id": "C", "text_en": "A revised price catalog"},
                        {"id": "D", "text_en": "A courier reimbursement form"},
                    ],
                    "answer_choice_id": "B",
                    "skill_tags": ["explicit_detail"],
                    "evidence": [
                        {
                            "source_type": "document_block",
                            "source_id": "ag-blk-p7-000002-1",
                            "quote_en": "I have attached the official laboratory certificate to this message for your review.",
                            "reasoning_zh": "第二段末句明確指出隨信附上正式實驗室檢驗證書（official laboratory certificate）。",
                        }
                    ],
                    "explanation_zh": "第二段說明品保實驗室昨天完成了 200 次循環耐熱耐用度測試，且「我已將正式實驗室檢驗證書附在本郵件中供您審閱（I have attached the official laboratory certificate to this message）」，故選 **(B)**。",
                    "distractor_notes": [
                        {"choice_id": "A", "reason_zh": "信中未附展示中心平面圖。"},
                        {"choice_id": "C", "reason_zh": "未附修訂版價格型錄。"},
                        {"choice_id": "D", "reason_zh": "樣品由寄件人快遞寄出，並未附快遞報銷單。"},
                    ],
                    "vocabulary": [
                        {
                            "term_en": "discoloration",
                            "meaning_zh": "變色；褪色",
                            "example_en": "Direct sunlight can cause discoloration of the fabric.",
                        }
                    ],
                    "estimated_time_sec": 25,
                },
                {
                    "item_id": "ag-i-p7-000002-3",
                    "prompt_en": "Why does Ms. Al-Mansoor ask Mr. Cho to confirm his order quantity soon?",
                    "choices": [
                        {"id": "A", "text_en": "Raw clay prices are expected to rise in December."},
                        {"id": "B", "text_en": "The olive-green glaze is being discontinued."},
                        {"id": "C", "text_en": "Production space in the kilns needs to be scheduled for November."},
                        {"id": "D", "text_en": "The showroom will close for renovations next month."},
                    ],
                    "answer_choice_id": "C",
                    "skill_tags": ["next_action", "paraphrase"],
                    "evidence": [
                        {
                            "source_type": "document_block",
                            "source_id": "ag-blk-p7-000002-1",
                            "quote_en": "please let me know how many sets you would like to include in your initial purchase order so we can reserve kiln capacity for November.",
                            "reasoning_zh": "寄件人請對方告知首批採購數量，以便預留十一月份的窯爐產能（reserve kiln capacity for November）。",
                        }
                    ],
                    "explanation_zh": "末段最後一句說明：「待您的廚務團隊檢視完樣品後，請告知首批採購單欲訂購的套數，以便我們預留十一月份的窯爐燒製產能（so we can reserve kiln capacity for November）」，故選 **(C)**。",
                    "distractor_notes": [
                        {"choice_id": "A", "reason_zh": "信中未提及陶土原料十二月漲價。"},
                        {"choice_id": "B", "reason_zh": "橄欖綠為新寄送的樣品色，並未停產。"},
                        {"choice_id": "D", "reason_zh": "未提及展示間下個月整修關閉。"},
                    ],
                    "vocabulary": [
                        {
                            "term_en": "place setting",
                            "meaning_zh": "（供一人使用的）全套個人餐具組",
                            "example_en": "Each five-piece place setting includes a soup bowl and dinner plate.",
                        }
                    ],
                    "estimated_time_sec": 30,
                },
            ],
            "provenance": make_provenance(),
            "review_refs": [],
        },
        # --- Group 3: ag-g-p7-000003 (Single Passage Chat Chain, 3 items, D3) ---
        {
            "schema_version": "1.0.0",
            "group_id": "ag-g-p7-000003",
            "version": 1,
            "family_id": "ag-fam-p7-single-chat-it-deployment-rollout",
            "pool": "training",
            "fixture": False,
            "part": 7,
            "layout": "single_passage",
            "scenario": "it_operations",
            "difficulty": {
                "level": "D3",
                "rationale_zh": "多人企業即時通訊討論串，考驗跨訊息因果推論、口語意圖判讀與時序發展。",
                "basis": "editorial",
            },
            "content_status": "draft",
            "stimulus": {
                "documents": [
                    {
                        "document_id": "ag-doc-p7-000003-1",
                        "genre": "chat",
                        "title_en": "Retail Systems Support Channel — October 24",
                        "blocks": [
                            {
                                "block_id": "ag-blk-p7-000003-1",
                                "type": "text",
                                "text_en": (
                                    "[9:12 A.M.] Victor Morales: Morning, team. The manager at our Waverly Place grocery store just called. Since the overnight point-of-sale (POS) firmware update, Lanes 1 through 4 haven't been recognizing digital loyalty coupons on customer smartphones.\n\n"
                                    "[9:15 A.M.] Haruka Sato: Did the overnight script update the optical scanner drivers on those registers as well, or just the payment terminal software?\n\n"
                                    "[9:17 A.M.] Eliott Vance: Let me check the deployment log... Ah, the scanner driver patch failed on the older Model 400 registers because their memory cache was full. Lanes 5 and 6 at Waverly Place have the newer Model 700 units, so they weren't affected.\n\n"
                                    "[9:18 A.M.] Haruka Sato: That explains it. We saw the exact same memory bottleneck at the Harborview branch last Tuesday.\n\n"
                                    "[9:21 A.M.] Eliott Vance: I'm clearing the temporary cache files on Waverly Place Lanes 1 to 4 remotely right now and pushing the driver patch again. It should finish in about ten minutes.\n\n"
                                    "[9:23 A.M.] Victor Morales: Great. Once your screen shows the installation is complete, let me know so I can have the Waverly Place supervisor run a test scan before the lunch rush starts."
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
                    "item_id": "ag-i-p7-000003-1",
                    "prompt_en": "What problem was reported at the Waverly Place store?",
                    "choices": [
                        {"id": "A", "text_en": "Credit card receipt printers ran out of paper."},
                        {"id": "B", "text_en": "Some checkout registers could not read mobile coupons."},
                        {"id": "C", "text_en": "Self-checkout screens froze during cash transactions."},
                        {"id": "D", "text_en": "Customer loyalty points were calculated twice."},
                    ],
                    "answer_choice_id": "B",
                    "skill_tags": ["explicit_detail", "paraphrase"],
                    "evidence": [
                        {
                            "source_type": "document_block",
                            "source_id": "ag-blk-p7-000003-1",
                            "quote_en": "Lanes 1 through 4 haven't been recognizing digital loyalty coupons on customer smartphones.",
                            "reasoning_zh": "Morales 先生在 9:12 說明 Waverly Place 門市 1 至 4 號結帳櫃檯無法辨識顧客手機上的數位會員折價券。",
                        }
                    ],
                    "explanation_zh": "9:12 A.M. 的訊息指出：「自昨晚收銀系統韌體更新後，1 至 4 號結帳道一直無法辨識顧客智慧型手機上的電子會員折價券（haven't been recognizing digital loyalty coupons on customer smartphones）」，對應 **(B) 部分結帳收銀機無法讀取行動折價券**。",
                    "distractor_notes": [
                        {"choice_id": "A", "reason_zh": "討論串未提及信用卡收據印表機缺紙。"},
                        {"choice_id": "C", "reason_zh": "未提及自助結帳螢幕在現金交易時當機。"},
                        {"choice_id": "D", "reason_zh": "是無法辨識折價券，而非點數重複計算兩次。"},
                    ],
                    "vocabulary": [
                        {
                            "term_en": "point-of-sale (POS)",
                            "meaning_zh": "銷售點管理系統；收銀結帳系統",
                            "example_en": "All retail stores upgraded their point-of-sale terminals.",
                        }
                    ],
                    "estimated_time_sec": 30,
                },
                {
                    "item_id": "ag-i-p7-000003-2",
                    "prompt_en": "At 9:18 A.M., what does Ms. Sato mean when she writes, \"That explains it\"?",
                    "choices": [
                        {"id": "A", "text_en": "She understands why only certain registers at the store malfunctioned."},
                        {"id": "B", "text_en": "She has received the store manager's written incident report."},
                        {"id": "C", "text_en": "She agrees that the store should purchase Model 700 registers immediately."},
                        {"id": "D", "text_en": "She knows why the Harborview branch closed early last Tuesday."},
                    ],
                    "answer_choice_id": "A",
                    "skill_tags": ["speaker_intent", "inference"],
                    "evidence": [
                        {
                            "source_type": "document_block",
                            "source_id": "ag-blk-p7-000003-1",
                            "quote_en": "[9:17 A.M.] Eliott Vance: ... the scanner driver patch failed on the older Model 400 registers because their memory cache was full. Lanes 5 and 6 at Waverly Place have the newer Model 700 units, so they weren't affected.\n\n[9:18 A.M.] Haruka Sato: That explains it. We saw the exact same memory bottleneck at the Harborview branch last Tuesday.",
                            "reasoning_zh": "Vance 在 9:17 查出舊型 400 型收銀機因快取記憶體滿載導致驅動程式更新失敗（而 5、6 號櫃檯為新型 700 型未受影響），Sato 回應 That explains it 表示她明白為何該門市只有特定機台故障。",
                        }
                    ],
                    "explanation_zh": "本題考書面訊息意圖。在 9:17 A.M.，Vance 查出 1 至 4 號舊款 Model 400 收銀機因記憶體快取已滿導致光學掃描器驅動程式修補失敗，而 5、6 號櫃檯為新款 Model 700 故未受影響。Sato 隨即回應「那就說得通了（That explains it），我們上週二在 Harborview 分店也遇到一模一樣的記憶體瓶頸」，表示 **(A) 她明白為何該門市只有部分特定收銀機台發生異常**。",
                    "distractor_notes": [
                        {"choice_id": "B", "reason_zh": "店長是打電話（just called）通報，並非寄送書面報告。"},
                        {"choice_id": "C", "reason_zh": "問題只需遠端清除快取並重推更新即可解決，並未討論立即採購新機台。"},
                        {"choice_id": "D", "reason_zh": "Harborview 分店上週二只是遇到相同的收銀機記憶體瓶頸，並未提早關店。"},
                    ],
                    "vocabulary": [
                        {
                            "term_en": "memory cache",
                            "meaning_zh": "快取記憶體；暫存區",
                            "example_en": "Clearing the memory cache resolved the software installation error.",
                        }
                    ],
                    "estimated_time_sec": 35,
                },
                {
                    "item_id": "ag-i-p7-000003-3",
                    "prompt_en": "What can be inferred about the Waverly Place store?",
                    "choices": [
                        {"id": "A", "text_en": "It opened more recently than the Harborview branch."},
                        {"id": "B", "text_en": "It uses two different models of checkout registers."},
                        {"id": "C", "text_en": "It will shut down Lanes 5 and 6 for ten minutes."},
                        {"id": "D", "text_en": "It no longer accepts paper coupons."},
                    ],
                    "answer_choice_id": "B",
                    "skill_tags": ["inference", "explicit_detail"],
                    "evidence": [
                        {
                            "source_type": "document_block",
                            "source_id": "ag-blk-p7-000003-1",
                            "quote_en": "the scanner driver patch failed on the older Model 400 registers because their memory cache was full. Lanes 5 and 6 at Waverly Place have the newer Model 700 units, so they weren't affected.",
                            "reasoning_zh": "Waverly Place 門市的 1 至 4 號結帳道使用舊款 Model 400，而 5 與 6 號結帳道使用新款 Model 700，可推知該店同時使用兩種不同型號的收銀機。",
                        }
                    ],
                    "explanation_zh": "根據 9:17 A.M. 的訊息，Waverly Place 門市的 1 至 4 號結帳道為舊款 `Model 400 registers`，而 5 與 6 號結帳道則配置新款 `Model 700 units`，由此可確知 **(B) 該門市同時使用兩種不同型號的結帳收銀機**。",
                    "distractor_notes": [
                        {"choice_id": "A", "reason_zh": "文中未比較兩家分店的開幕先後時間。"},
                        {"choice_id": "C", "reason_zh": "需要遠端重推更新約十分鐘的是 1 至 4 號櫃檯，5 與 6 號並未受影響。"},
                        {"choice_id": "D", "reason_zh": "文中僅討論數位折價券掃描異常，未說停收紙本折價券。"},
                    ],
                    "vocabulary": [
                        {
                            "term_en": "lunch rush",
                            "meaning_zh": "午餐尖峰人潮時段",
                            "example_en": "All checkout lanes must be staffed before the lunch rush begins.",
                        }
                    ],
                    "estimated_time_sec": 35,
                },
            ],
            "provenance": make_provenance(),
            "review_refs": [],
        },
        # --- Group 4: ag-g-p7-000004 (Single Passage Article + Sentence Insertion, 4 items, D4) ---
        {
            "schema_version": "1.0.0",
            "group_id": "ag-g-p7-000004",
            "version": 1,
            "family_id": "ag-fam-p7-single-article-green-rooftop-grant",
            "pool": "training",
            "fixture": False,
            "part": 7,
            "layout": "single_passage",
            "scenario": "urban_sustainability",
            "difficulty": {
                "level": "D4",
                "rationale_zh": "商業雜誌專題報導，涵蓋主旨、語境多義詞（offset）、補助細節推論及 [[position:1]]–[[position:4]] 句子插入題。",
                "basis": "editorial",
            },
            "content_status": "draft",
            "stimulus": {
                "documents": [
                    {
                        "document_id": "ag-doc-p7-000004-1",
                        "genre": "article",
                        "title_en": "Portland's Commercial Green-Roof Rebate Draws Strong Corporate Interest",
                        "blocks": [
                            {
                                "block_id": "ag-blk-p7-000004-1",
                                "type": "text",
                                "text_en": (
                                    "PORTLAND (October 22) — Since the Portland Office of Sustainability launched its Commercial Rooftop Canopy Grant eighteen months ago, thirty-four office and warehouse properties across the metropolitan area have converted bare tar rooftops into vegetated gardens. [[position:1]] "
                                    "Under the municipal initiative, commercial building owners receive a rebate of $15 per square meter—up to a maximum of $45,000 per property—to offset the cost of waterproof membranes, lightweight soil, and drought-tolerant native plants.\n\n"
                                    "City engineers designed the program primarily to reduce stormwater runoff into the Willamette River during heavy autumn rains. [[position:2]] "
                                    "However, participating businesses report that the thermal insulation provided by the soil layer has delivered an equally valuable financial benefit. "
                                    "At Cascade Logistics Center, a 4,000-square-meter distribution warehouse near the port, summer air-conditioning expenses dropped by 22 percent during the first year after installation. [[position:3]]\n\n"
                                    "Because the initial grant fund has been nearly exhausted, the City Council voted last week to allocate an additional $1.8 million for the upcoming fiscal year. "
                                    "[[position:4]] Applications for the next funding round open on January 15, and priority will be given to industrial buildings with flat roofs exceeding 1,500 square meters."
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
                    "item_id": "ag-i-p7-000004-1",
                    "prompt_en": "According to the article, what was the city's main reason for creating the grant program?",
                    "choices": [
                        {"id": "A", "text_en": "To attract landscaping companies to relocate to Portland"},
                        {"id": "B", "text_en": "To decrease the amount of rainwater flowing into a local river"},
                        {"id": "C", "text_en": "To create outdoor dining spaces for office employees"},
                        {"id": "D", "text_en": "To replace solar panels on older industrial warehouses"},
                    ],
                    "answer_choice_id": "B",
                    "skill_tags": ["explicit_detail", "paraphrase"],
                    "evidence": [
                        {
                            "source_type": "document_block",
                            "source_id": "ag-blk-p7-000004-1",
                            "quote_en": "City engineers designed the program primarily to reduce stormwater runoff into the Willamette River during heavy autumn rains.",
                            "reasoning_zh": "第二段首句指出市政工程師設計此計畫的主要目的（primarily）是減少秋季豪雨期間流入 Willamette River 的雨水徑流（stormwater runoff）。",
                        }
                    ],
                    "explanation_zh": "第二段開頭明確說明：「市政工程師設計該計畫的主要目的，是為了減少秋季豪雨期間排入威拉米特河的雨水徑流（primarily to reduce stormwater runoff into the Willamette River）」，選項 **(B)** 以 `decrease the amount of rainwater flowing into a local river` 同義改寫。",
                    "distractor_notes": [
                        {"choice_id": "A", "reason_zh": "文中未提及吸引景觀設計公司遷入波特蘭。"},
                        {"choice_id": "C", "reason_zh": "綠屋頂種植的是耐旱原生植物以吸收雨水與隔熱，並非打造員工戶外用餐區。"},
                        {"choice_id": "D", "reason_zh": "未提及取代太陽能板。"},
                    ],
                    "vocabulary": [
                        {
                            "term_en": "stormwater runoff",
                            "meaning_zh": "雨水徑流（未滲入土壤而流入排水系統的雨水）",
                            "example_en": "Vegetated roofs absorb rainwater and reduce stormwater runoff.",
                        }
                    ],
                    "estimated_time_sec": 30,
                },
                {
                    "item_id": "ag-i-p7-000004-2",
                    "prompt_en": "In paragraph 1, the word \"offset\" is closest in meaning to",
                    "choices": [
                        {"id": "A", "text_en": "postpone"},
                        {"id": "B", "text_en": "counterbalance"},
                        {"id": "C", "text_en": "inspect"},
                        {"id": "D", "text_en": "publicize"},
                    ],
                    "answer_choice_id": "B",
                    "skill_tags": ["vocabulary_in_context"],
                    "evidence": [
                        {
                            "source_type": "document_block",
                            "source_id": "ag-blk-p7-000004-1",
                            "quote_en": "commercial building owners receive a rebate of $15 per square meter—up to a maximum of $45,000 per property—to offset the cost of waterproof membranes, lightweight soil, and drought-tolerant native plants.",
                            "reasoning_zh": "商業大樓業主獲得每平方公尺 15 美元的補助回饋金，用來「抵銷、補償（offset / counterbalance）」防水膜、輕質土壤與耐旱植物的建置成本。",
                        }
                    ],
                    "explanation_zh": "本題考語境詞義。第一段指出業主可獲得每平方公尺 15 美元的補助款，「以抵銷／貼補（`to offset`）防水膜、輕量土壤與耐旱原生植物的成本」。`offset` 在財務語境中意為「抵銷、補償、平衡」，與 **(B) counterbalance** 最接近。",
                    "distractor_notes": [
                        {"choice_id": "A", "reason_zh": "postpone 意為「延後、推遲」，不合補助款補貼成本的語意。"},
                        {"choice_id": "C", "reason_zh": "inspect 意為「檢查、視察」。"},
                        {"choice_id": "D", "reason_zh": "publicize 意為「宣傳、公布」。"},
                    ],
                    "vocabulary": [
                        {
                            "term_en": "offset",
                            "meaning_zh": "抵銷；彌補（成本或碳排）",
                            "example_en": "Energy savings will offset the installation cost within three years.",
                        }
                    ],
                    "estimated_time_sec": 25,
                },
                {
                    "item_id": "ag-i-p7-000004-3",
                    "prompt_en": "What is indicated about Cascade Logistics Center?",
                    "choices": [
                        {"id": "A", "text_en": "It will submit its grant application on January 15."},
                        {"id": "B", "text_en": "It lowered its summer cooling costs after installing a green roof."},
                        {"id": "C", "text_en": "It is located less than 1,500 meters from City Hall."},
                        {"id": "D", "text_en": "It received $1.8 million in municipal funding."},
                    ],
                    "answer_choice_id": "B",
                    "skill_tags": ["explicit_detail", "paraphrase"],
                    "evidence": [
                        {
                            "source_type": "document_block",
                            "source_id": "ag-blk-p7-000004-1",
                            "quote_en": "At Cascade Logistics Center, a 4,000-square-meter distribution warehouse near the port, summer air-conditioning expenses dropped by 22 percent during the first year after installation.",
                            "reasoning_zh": "Cascade 物流中心在安裝綠屋頂後的第一年，夏季空調費用下降了 22%（lowered its summer cooling costs）。",
                        }
                    ],
                    "explanation_zh": "第二段末句指出：「在港口附近佔地四千平方公尺的 Cascade 物流中心，安裝後第一年的夏季空調費用下降了 22%（summer air-conditioning expenses dropped by 22 percent）」，對應 **(B) 安裝綠屋頂後降低了夏季冷氣費用**。",
                    "distractor_notes": [
                        {"choice_id": "A", "reason_zh": "Cascade 物流中心已經安裝滿一年，並非明年一月才要申請。"},
                        {"choice_id": "C", "reason_zh": "1,500 平方公尺是第三段提及的優先補助屋頂面積門檻，並非與市政廳的距離。"},
                        {"choice_id": "D", "reason_zh": "180 萬美元是市議會為下一會計年度追加的總預算，單一建物補助上限為 45,000 美元。"},
                    ],
                    "vocabulary": [
                        {
                            "term_en": "thermal insulation",
                            "meaning_zh": "隔熱；保溫",
                            "example_en": "Thick rooftop soil provides natural thermal insulation.",
                        }
                    ],
                    "estimated_time_sec": 30,
                },
                {
                    "item_id": "ag-i-p7-000004-4",
                    "prompt_en": "In which of the positions marked [1], [2], [3], and [4] does the following sentence best belong?\n\"Facility manager Rosa Delgado notes that the cooler indoor temperatures have also reduced wear on the building's rooftop HVAC compressors.\"",
                    "choices": [
                        {"id": "A", "text_en": "[1]"},
                        {"id": "B", "text_en": "[2]"},
                        {"id": "C", "text_en": "[3]"},
                        {"id": "D", "text_en": "[4]"},
                    ],
                    "answer_choice_id": "C",
                    "skill_tags": ["sentence_insertion", "reference_cohesion"],
                    "evidence": [
                        {
                            "source_type": "document_block",
                            "source_id": "ag-blk-p7-000004-1",
                            "quote_en": "At Cascade Logistics Center, a 4,000-square-meter distribution warehouse near the port, summer air-conditioning expenses dropped by 22 percent during the first year after installation. [[position:3]]",
                            "reasoning_zh": "插入句中的 the cooler indoor temperatures 與 the building's rooftop HVAC compressors 直接承接前句 Cascade Logistics Center 夏季空調費用下降 22% 的具體案例。",
                        }
                    ],
                    "explanation_zh": "本題考句子插入（Sentence Insertion）。待插入句提到：「設施經理 Rosa Delgado 指出，較涼爽的室內溫度（`the cooler indoor temperatures`）同時也減少了該建築屋頂空調壓縮機的耗損」。位置 **[3]** 前一句正好舉出單一建築案例 `Cascade Logistics Center` 的夏季空調費用下降 22%，插入句以 `the building's` 指涉該物流中心，並以 `also` 補充降溫帶來的另一項空調設備效益，銜接最緊密，故選 **(C) [3]**。",
                    "distractor_notes": [
                        {"choice_id": "A", "reason_zh": "[1] 前方為計畫總覽（34 處建築參與），尚未提及特定單一建築（the building）或室內降溫。"},
                        {"choice_id": "B", "reason_zh": "[2] 前方談論的是威拉米特河雨水徑流問題，尚未引入隔熱降溫效益。"},
                        {"choice_id": "D", "reason_zh": "[4] 位於第三段市議會追加 180 萬美元預算之後，與單一倉庫的空調壓縮機耗損無關。"},
                    ],
                    "vocabulary": [
                        {
                            "term_en": "exhausted",
                            "meaning_zh": "用盡的；耗盡的（資金或資源）",
                            "example_en": "Once the rebate funds are exhausted, no further grants will be issued.",
                        }
                    ],
                    "estimated_time_sec": 45,
                },
            ],
            "provenance": make_provenance(),
            "review_refs": [],
        },
        # --- Group 5: ag-g-p7-000005 (Double Passage: Conference Schedule + Email, 5 items, D4) ---
        {
            "schema_version": "1.0.0",
            "group_id": "ag-g-p7-000005",
            "version": 1,
            "family_id": "ag-fam-p7-double-conference-schedule-and-email",
            "pool": "training",
            "fixture": False,
            "part": 7,
            "layout": "double_passage",
            "scenario": "event_conference",
            "difficulty": {
                "level": "D4",
                "rationale_zh": "雙篇閱讀（論壇議程表＋講者換場確認信），其中兩題需跨兩份文件比對交換後的演講時段與會議廳編號。",
                "basis": "editorial",
            },
            "content_status": "draft",
            "stimulus": {
                "documents": [
                    {
                        "document_id": "ag-doc-p7-000005-1",
                        "genre": "schedule",
                        "title_en": "Pacific Rim Supply Chain Forum — Friday, November 14 (Afternoon Track)",
                        "blocks": [
                            {
                                "block_id": "ag-blk-p7-000005-1",
                                "type": "table",
                                "columns": ["Time", "Session Title", "Speaker", "Room"],
                                "rows": [
                                    ["1:00 P.M.–2:00 P.M.", "Automated Port Customs Clearance", "Dr. Henrik Lindholm (Nordic Freight)", "Harbor Room A"],
                                    ["2:15 P.M.–3:15 P.M.", "Cold-Chain Packaging Innovations", "Mei-Ling Zhou (FreshRoute Logistics)", "Harbor Room B"],
                                    ["3:30 P.M.–4:30 P.M.", "Reducing Last-Mile Delivery Emissions", "Carlos Mendez (MetroFleet EV)", "Grand Ballroom"],
                                    ["4:45 P.M.–5:45 P.M.", "Maritime Insurance Trends for 2027", "Priya Nair (Oceanic Underwriting)", "Harbor Room A"],
                                ],
                            },
                            {
                                "block_id": "ag-blk-p7-000005-2",
                                "type": "text",
                                "text_en": (
                                    "Note: Conference attendees registered for the Standard Pass may attend all Harbor Room sessions. "
                                    "Admission to sessions held in the Grand Ballroom requires either an All-Access Badge or a $35 single-session upgrade ticket available at the registration desk."
                                ),
                            },
                        ],
                    },
                    {
                        "document_id": "ag-doc-p7-000005-2",
                        "genre": "email",
                        "title_en": "Subject: Friday Session Time Swap Request",
                        "blocks": [
                            {
                                "block_id": "ag-blk-p7-000005-3",
                                "type": "text",
                                "text_en": (
                                    "To: Priya Nair <pnair@oceanicunderwriting.com>\n"
                                    "From: Gavin Cho, Program Coordinator <gcho@pacificsupplyforum.org>\n"
                                    "Date: November 10\n"
                                    "Subject: Friday Session Time Swap Request\n\n"
                                    "Dear Ms. Nair,\n\n"
                                    "I am writing with a scheduling request regarding your presentation at the Pacific Rim Supply Chain Forum this Friday, November 14. "
                                    "Dr. Henrik Lindholm's incoming flight from Stockholm was rescheduled by the airline, and he will now land in Vancouver at 1:30 P.M. on Friday. "
                                    "Consequently, he will not be able to reach the convention center in time for his 1:00 P.M. slot.\n\n"
                                    "Since both of your sessions are assigned to the same room and have a similar number of registered attendees, would you be willing to take the 1:00 P.M.–2:00 P.M. time slot so that Dr. Lindholm can present during your 4:45 P.M. slot instead? "
                                    "If you agree to this change, we will update the mobile event app immediately and provide complimentary airport limousine service for your return trip on Saturday.\n\n"
                                    "Please let me know by 5:00 P.M. today whether this arrangement works for you, and remember to upload your final slide deck to the speaker portal by Wednesday.\n\n"
                                    "Sincerely,\n"
                                    "Gavin Cho"
                                ),
                            }
                        ],
                    },
                ],
                "speakers": [],
                "audio_script": [],
            },
            "assets": [],
            "items": [
                {
                    "item_id": "ag-i-p7-000005-1",
                    "prompt_en": "According to the schedule, which speaker will discuss electric delivery vehicles?",
                    "choices": [
                        {"id": "A", "text_en": "Dr. Henrik Lindholm"},
                        {"id": "B", "text_en": "Mei-Ling Zhou"},
                        {"id": "C", "text_en": "Carlos Mendez"},
                        {"id": "D", "text_en": "Priya Nair"},
                    ],
                    "answer_choice_id": "C",
                    "skill_tags": ["explicit_detail", "paraphrase"],
                    "evidence": [
                        {
                            "source_type": "document_block",
                            "source_id": "ag-blk-p7-000005-1",
                            "quote_en": "3:30 P.M.–4:30 P.M. | Reducing Last-Mile Delivery Emissions | Carlos Mendez (MetroFleet EV) | Grand Ballroom",
                            "reasoning_zh": "議程表中主講「減少最後一哩路配送碳排」且所屬機構為 MetroFleet EV 的講者為 Carlos Mendez。",
                        }
                    ],
                    "explanation_zh": "對照第一篇議程表，3:30 P.M.–4:30 P.M. 場次主題為 `Reducing Last-Mile Delivery Emissions`（減少最後一哩路配送碳排），主講人為來自 `MetroFleet EV` 的 **(C) Carlos Mendez**。",
                    "distractor_notes": [
                        {"choice_id": "A", "reason_zh": "Dr. Lindholm 主講的是自動化港口報關。"},
                        {"choice_id": "B", "reason_zh": "Mei-Ling Zhou 主講的是冷鏈包裝創新。"},
                        {"choice_id": "D", "reason_zh": "Priya Nair 主講的是 2027 年海事保險趨勢。"},
                    ],
                    "vocabulary": [
                        {
                            "term_en": "last-mile delivery",
                            "meaning_zh": "最後一哩路配送（從集貨中心到終端客戶手中的運送階段）",
                            "example_en": "Electric vans are increasingly used for urban last-mile delivery.",
                        }
                    ],
                    "estimated_time_sec": 30,
                },
                {
                    "item_id": "ag-i-p7-000005-2",
                    "prompt_en": "Which session requires Standard Pass holders to pay an additional fee to attend?",
                    "choices": [
                        {"id": "A", "text_en": "Automated Port Customs Clearance"},
                        {"id": "B", "text_en": "Cold-Chain Packaging Innovations"},
                        {"id": "C", "text_en": "Reducing Last-Mile Delivery Emissions"},
                        {"id": "D", "text_en": "Maritime Insurance Trends for 2027"},
                    ],
                    "answer_choice_id": "C",
                    "skill_tags": ["conditions_exceptions", "explicit_detail"],
                    "evidence": [
                        {
                            "source_type": "document_block",
                            "source_id": "ag-blk-p7-000005-2",
                            "quote_en": "Admission to sessions held in the Grand Ballroom requires either an All-Access Badge or a $35 single-session upgrade ticket",
                            "reasoning_zh": "備註說明在 Grand Ballroom 舉行的場次需要全通行證或加購 $35 單場升級票。",
                        },
                        {
                            "source_type": "document_block",
                            "source_id": "ag-blk-p7-000005-1",
                            "quote_en": "3:30 P.M.–4:30 P.M. | Reducing Last-Mile Delivery Emissions | Carlos Mendez (MetroFleet EV) | Grand Ballroom",
                            "reasoning_zh": "表格中唯一在 Grand Ballroom 舉行的場次為 Reducing Last-Mile Delivery Emissions。",
                        },
                    ],
                    "explanation_zh": "第一篇表格下方備註指出：「持有標準通行證（Standard Pass）的與會者可參加所有 Harbor Room 的場次；進入大宴會廳（`Grand Ballroom`）的場次則須持有全通行證，或購買 35 美元的單場升級票」。查表可知唯一在 `Grand Ballroom` 舉行的場次為 **(C) Reducing Last-Mile Delivery Emissions**。",
                    "distractor_notes": [
                        {"choice_id": "A", "reason_zh": "該場次位於 Harbor Room A，標準通行證可直接入場。"},
                        {"choice_id": "B", "reason_zh": "該場次位於 Harbor Room B，標準通行證可直接入場。"},
                        {"choice_id": "D", "reason_zh": "該場次位於 Harbor Room A，標準通行證可直接入場。"},
                    ],
                    "vocabulary": [
                        {
                            "term_en": "surcharge / upgrade ticket",
                            "meaning_zh": "加價升級票券",
                            "example_en": "Standard ticket holders can purchase an upgrade ticket at the door.",
                        }
                    ],
                    "estimated_time_sec": 35,
                },
                {
                    "item_id": "ag-i-p7-000005-3",
                    "prompt_en": "Why is Mr. Cho contacting Ms. Nair?",
                    "choices": [
                        {"id": "A", "text_en": "To invite her to moderate a panel in Harbor Room B"},
                        {"id": "B", "text_en": "To ask her to switch presentation times with another speaker"},
                        {"id": "C", "text_en": "To inform her that her session has been moved to the Grand Ballroom"},
                        {"id": "D", "text_en": "To request her biography for the printed program"},
                    ],
                    "answer_choice_id": "B",
                    "skill_tags": ["main_idea_purpose", "paraphrase"],
                    "evidence": [
                        {
                            "source_type": "document_block",
                            "source_id": "ag-blk-p7-000005-3",
                            "quote_en": "would you be willing to take the 1:00 P.M.–2:00 P.M. time slot so that Dr. Lindholm can present during your 4:45 P.M. slot instead?",
                            "reasoning_zh": "Cho 先生詢問 Nair 女士是否願意與因班機改點而延誤的 Lindholm 博士對調週五演講時段。",
                        }
                    ],
                    "explanation_zh": "第二篇電子郵件中，議程協調員 Gavin Cho 說明 Dr. Lindholm 從斯德哥爾摩飛來的班機改點，無法趕上下午一點的場次，因此詢問 Ms. Nair：「您是否願意改至 1:00 P.M.–2:00 P.M. 時段演講，讓 Dr. Lindholm 改在您原本的 4:45 P.M. 時段發表？」，故致信目的為 **(B) 請她與另一位講者對調演講時段**。",
                    "distractor_notes": [
                        {"choice_id": "A", "reason_zh": "她的場次在 Harbor Room A，並非邀請去 Harbor Room B 主持座談。"},
                        {"choice_id": "C", "reason_zh": "信中說明兩人原本都被安排在同一間會議室（Harbor Room A），並未移至大宴會廳。"},
                        {"choice_id": "D", "reason_zh": "信末僅提醒週三前上傳簡報投影片（slide deck），未索取個人簡介。"},
                    ],
                    "vocabulary": [
                        {
                            "term_en": "slide deck",
                            "meaning_zh": "簡報投影片檔案",
                            "example_en": "Please upload your final slide deck before the conference begins.",
                        }
                    ],
                    "estimated_time_sec": 30,
                },
                {
                    "item_id": "ag-i-p7-000005-4",
                    "prompt_en": "If Ms. Nair agrees to Mr. Cho's request, when will \"Automated Port Customs Clearance\" be presented?",
                    "choices": [
                        {"id": "A", "text_en": "From 1:00 P.M. to 2:00 P.M."},
                        {"id": "B", "text_en": "From 2:15 P.M. to 3:15 P.M."},
                        {"id": "C", "text_en": "From 3:30 P.M. to 4:30 P.M."},
                        {"id": "D", "text_en": "From 4:45 P.M. to 5:45 P.M."},
                    ],
                    "answer_choice_id": "D",
                    "skill_tags": ["cross_document", "chronology"],
                    "evidence": [
                        {
                            "source_type": "document_block",
                            "source_id": "ag-blk-p7-000005-1",
                            "quote_en": "1:00 P.M.–2:00 P.M. | Automated Port Customs Clearance | Dr. Henrik Lindholm (Nordic Freight) | Harbor Room A\n4:45 P.M.–5:45 P.M. | Maritime Insurance Trends for 2027 | Priya Nair (Oceanic Underwriting) | Harbor Room A",
                            "reasoning_zh": "由第一篇表格可知 Automated Port Customs Clearance 為 Dr. Lindholm 的講題，而 Ms. Nair 原時段為 4:45 P.M.–5:45 P.M.。",
                        },
                        {
                            "source_type": "document_block",
                            "source_id": "ag-blk-p7-000005-3",
                            "quote_en": "would you be willing to take the 1:00 P.M.–2:00 P.M. time slot so that Dr. Lindholm can present during your 4:45 P.M. slot instead?",
                            "reasoning_zh": "由第二篇信件可知若 Ms. Nair 同意對調，Dr. Lindholm 將改在 4:45 P.M.–5:45 P.M. 時段演講。",
                        },
                    ],
                    "explanation_zh": "本題為跨文件整合題（Cross-Document Integration）。首先從第一篇議程表查出 `Automated Port Customs Clearance` 是 **Dr. Henrik Lindholm** 的講題，同時查出 **Priya Nair** 原本的時段為 `4:45 P.M.–5:45 P.M.`。再對照第二篇郵件，若 Ms. Nair 同意對調，Dr. Lindholm 將改在 Ms. Nair 原先的時段（`during your 4:45 P.M. slot instead`）發表，即 **(D) 4:45 P.M. 至 5:45 P.M.**。",
                    "distractor_notes": [
                        {"choice_id": "A", "reason_zh": "1:00 P.M.–2:00 P.M. 是對調前原本的時段，對調後將改由 Ms. Nair 主講。"},
                        {"choice_id": "B", "reason_zh": "2:15 P.M.–3:15 P.M. 為 Mei-Ling Zhou 的場次，未受影響。"},
                        {"choice_id": "C", "reason_zh": "3:30 P.M.–4:30 P.M. 為 Carlos Mendez 的場次，未受影響。"},
                    ],
                    "vocabulary": [
                        {
                            "term_en": "customs clearance",
                            "meaning_zh": "海關清關／報關手續",
                            "example_en": "Electronic documentation sped up port customs clearance.",
                        }
                    ],
                    "estimated_time_sec": 40,
                },
                {
                    "item_id": "ag-i-p7-000005-5",
                    "prompt_en": "In which room is Ms. Nair scheduled to speak?",
                    "choices": [
                        {"id": "A", "text_en": "Harbor Room A"},
                        {"id": "B", "text_en": "Harbor Room B"},
                        {"id": "C", "text_en": "Grand Ballroom"},
                        {"id": "D", "text_en": "Vancouver Hall"},
                    ],
                    "answer_choice_id": "A",
                    "skill_tags": ["cross_document", "explicit_detail"],
                    "evidence": [
                        {
                            "source_type": "document_block",
                            "source_id": "ag-blk-p7-000005-1",
                            "quote_en": "4:45 P.M.–5:45 P.M. | Maritime Insurance Trends for 2027 | Priya Nair (Oceanic Underwriting) | Harbor Room A",
                            "reasoning_zh": "議程表顯示 Priya Nair 與 Dr. Lindholm 的場次皆位於 Harbor Room A。",
                        },
                        {
                            "source_type": "document_block",
                            "source_id": "ag-blk-p7-000005-3",
                            "quote_en": "Since both of your sessions are assigned to the same room",
                            "reasoning_zh": "郵件亦確認兩人的場次都在同一間會議室（Harbor Room A）。",
                        },
                    ],
                    "explanation_zh": "根據第一篇議程表，Ms. Priya Nair 與 Dr. Lindholm 的演講廳皆為 **(A) Harbor Room A**（且第二篇郵件亦確認 `both of your sessions are assigned to the same room`，因此即使交換時段仍在 Harbor Room A）。",
                    "distractor_notes": [
                        {"choice_id": "B", "reason_zh": "Harbor Room B 是 Mei-Ling Zhou 的演講廳。"},
                        {"choice_id": "C", "reason_zh": "Grand Ballroom 是 Carlos Mendez 的演講廳。"},
                        {"choice_id": "D", "reason_zh": "Vancouver 是會議舉辦城市（溫哥華），並非會議廳名稱。"},
                    ],
                    "vocabulary": [
                        {
                            "term_en": "underwriting",
                            "meaning_zh": "保險承保業務",
                            "example_en": "She has ten years of experience in marine insurance underwriting.",
                        }
                    ],
                    "estimated_time_sec": 30,
                },
            ],
            "provenance": make_provenance(),
            "review_refs": [],
        },
        # --- Group 6: ag-g-p7-000006 (Double Passage: Warranty Policy + Claim Form, 5 items, D4) ---
        {
            "schema_version": "1.0.0",
            "group_id": "ag-g-p7-000006",
            "version": 1,
            "family_id": "ag-fam-p7-double-warranty-policy-and-claim-form",
            "pool": "training",
            "fixture": False,
            "part": 7,
            "layout": "double_passage",
            "scenario": "customer_warranty",
            "difficulty": {
                "level": "D4",
                "rationale_zh": "雙篇閱讀（商用義式咖啡機保固條款＋客戶線上報修單），需跨文件比對購買日期、故障零件與保固免責條款以推論費用負擔。",
                "basis": "editorial",
            },
            "content_status": "draft",
            "stimulus": {
                "documents": [
                    {
                        "document_id": "ag-doc-p7-000006-1",
                        "genre": "policy",
                        "title_en": "Bellini Commercial Espresso Systems — Limited Warranty Policy",
                        "blocks": [
                            {
                                "block_id": "ag-blk-p7-000006-1",
                                "type": "text",
                                "text_en": (
                                    "1. Coverage Period: Bellini Commercial Espresso Systems warrants the Dual-Boiler Pro 3000 against defects in internal mechanical and electrical components—including the brass brew group, rotary water pump, and digital pressure control board—for twenty-four (24) months from the original date of purchase.\n\n"
                                    "2. Exclusions: This limited warranty does not cover rubber portafilter gaskets, external milk carafes, or damage caused by failure to use a certified water-softening filter. Replacement of excluded accessories is billed at standard catalog rates.\n\n"
                                    "3. On-Site Service & Shipping: During the first twelve (12) months of ownership, Bellini provides complimentary on-site technician dispatch within 80 kilometers of an authorized service center. "
                                    "In months 13 through 24, replacement covered parts remain free of charge, but a flat $85 technician travel fee applies to all on-site visits."
                                ),
                            }
                        ],
                    },
                    {
                        "document_id": "ag-doc-p7-000006-2",
                        "genre": "form",
                        "title_en": "Bellini Authorized Service Request Form",
                        "blocks": [
                            {
                                "block_id": "ag-blk-p7-000006-2",
                                "type": "table",
                                "columns": ["Field", "Customer Entry"],
                                "rows": [
                                    ["Claim Reference", "SR-90412"],
                                    ["Business Name", "Roast & Reed Book Café"],
                                    ["Distance from Service Center", "18 kilometers"],
                                    ["Model", "Dual-Boiler Pro 3000"],
                                    ["Original Purchase Date", "April 10, 2025"],
                                    ["Service Request Date", "October 20, 2026"],
                                ],
                            },
                            {
                                "block_id": "ag-blk-p7-000006-3",
                                "type": "text",
                                "text_en": (
                                    "Issue Description: Yesterday morning, the digital pressure control board stopped displaying the boiler temperature, and the right-hand steam wand began losing pressure. "
                                    "We have always used the official Bellini water-softening filter cartridge and replaced it every ninety days as instructed. "
                                    "In addition to repairing the pressure control board, please have the technician bring two new rubber portafilter gaskets, as ours are worn."
                                ),
                            },
                        ],
                    },
                ],
                "speakers": [],
                "audio_script": [],
            },
            "assets": [],
            "items": [
                {
                    "item_id": "ag-i-p7-000006-1",
                    "prompt_en": "According to the warranty policy, how long are internal electrical components covered?",
                    "choices": [
                        {"id": "A", "text_en": "For 3 months"},
                        {"id": "B", "text_en": "For 12 months"},
                        {"id": "C", "text_en": "For 24 months"},
                        {"id": "D", "text_en": "For 36 months"},
                    ],
                    "answer_choice_id": "C",
                    "skill_tags": ["explicit_detail"],
                    "evidence": [
                        {
                            "source_type": "document_block",
                            "source_id": "ag-blk-p7-000006-1",
                            "quote_en": "warrants the Dual-Boiler Pro 3000 against defects in internal mechanical and electrical components ... for twenty-four (24) months from the original date of purchase.",
                            "reasoning_zh": "保固條款第一條明確記載內部機械與電子零件保固期為自購買日起 24 個月。",
                        }
                    ],
                    "explanation_zh": "第一篇保固條款第 1 條載明：「Bellini 商用義式咖啡系統針對 Dual-Boiler Pro 3000 之內部機械與電子零件瑕疵，提供自原購買日起二十四（24）個月的保固」，故選 **(C)**。",
                    "distractor_notes": [
                        {"choice_id": "A", "reason_zh": "90 天（3個月）是客戶在報修單提到更換濾水芯的週期，而非零件保固期。"},
                        {"choice_id": "B", "reason_zh": "12 個月是免費到府免收車馬費的期限，零件本身保固為 24 個月。"},
                        {"choice_id": "D", "reason_zh": "文中未提及 36 個月。"},
                    ],
                    "vocabulary": [
                        {
                            "term_en": "warrant",
                            "meaning_zh": "提供保固；保證",
                            "example_en": "The manufacturer warrants the motor for two years.",
                        }
                    ],
                    "estimated_time_sec": 25,
                },
                {
                    "item_id": "ag-i-p7-000006-2",
                    "prompt_en": "Why does the customer mention the Bellini water-softening filter cartridge in the request form?",
                    "choices": [
                        {"id": "A", "text_en": "To order a box of replacement filter cartridges"},
                        {"id": "B", "text_en": "To show that the café complied with warranty maintenance requirements"},
                        {"id": "C", "text_en": "To complain that the filter cartridge caused the temperature display to fail"},
                        {"id": "D", "text_en": "To ask the technician how to install a new filter"},
                    ],
                    "answer_choice_id": "B",
                    "skill_tags": ["cross_document", "conditions_exceptions"],
                    "evidence": [
                        {
                            "source_type": "document_block",
                            "source_id": "ag-blk-p7-000006-1",
                            "quote_en": "This limited warranty does not cover ... damage caused by failure to use a certified water-softening filter.",
                            "reasoning_zh": "第一篇第 2 條规定若未使用認證軟水濾芯導致損壞則不在保固範圍內。",
                        },
                        {
                            "source_type": "document_block",
                            "source_id": "ag-blk-p7-000006-3",
                            "quote_en": "We have always used the official Bellini water-softening filter cartridge and replaced it every ninety days as instructed.",
                            "reasoning_zh": "客戶在報修單特別聲明一直都有按指示使用官方軟水濾芯並每 90 天更換，以證明符合保固條件。",
                        },
                    ],
                    "explanation_zh": "本題需跨文件理解。第一篇保固條款第 2 條指出「未使用認證軟水濾芯所造成的損壞不在保固範圍內」。因此客戶在第二篇報修單特別註明「我們一直都使用 Bellini 官方軟水濾芯並按指示每 90 天更換」，目的是 **(B) 證明咖啡館完全遵守保固保養規定（無免責除外事由）**。",
                    "distractor_notes": [
                        {"choice_id": "A", "reason_zh": "客戶要求技師順便帶的是兩個橡膠墊圈（portafilter gaskets），而非濾水芯。"},
                        {"choice_id": "C", "reason_zh": "客戶並非抱怨濾芯導致故障，而是強調有正常使用濾芯。"},
                        {"choice_id": "D", "reason_zh": "客戶已每 90 天自行更換濾芯，並非詢問如何安裝。"},
                    ],
                    "vocabulary": [
                        {
                            "term_en": "exclusion",
                            "meaning_zh": "除外條款；不保事項",
                            "example_en": "Please read the list of warranty exclusions carefully.",
                        }
                    ],
                    "estimated_time_sec": 35,
                },
                {
                    "item_id": "ag-i-p7-000006-3",
                    "prompt_en": "What can be concluded about the digital pressure control board for Roast & Reed Book Café?",
                    "choices": [
                        {"id": "A", "text_en": "The replacement part itself will be provided at no charge."},
                        {"id": "B", "text_en": "It is excluded from the limited warranty policy."},
                        {"id": "C", "text_en": "Its warranty expired on April 10, 2026."},
                        {"id": "D", "text_en": "It must be shipped to the factory in Italy for repair."},
                    ],
                    "answer_choice_id": "A",
                    "skill_tags": ["cross_document", "inference"],
                    "evidence": [
                        {
                            "source_type": "document_block",
                            "source_id": "ag-blk-p7-000006-1",
                            "quote_en": "including the brass brew group, rotary water pump, and digital pressure control board—for twenty-four (24) months from the original date of purchase. ... In months 13 through 24, replacement covered parts remain free of charge",
                            "reasoning_zh": "數位壓力控制板屬於保固 24 個月的內部零件，且在第 13 至 24 個月期間保固零件本身依然免費（remain free of charge）。",
                        },
                        {
                            "source_type": "document_block",
                            "source_id": "ag-blk-p7-000006-2",
                            "quote_en": "Original Purchase Date | April 10, 2025\nService Request Date | October 20, 2026",
                            "reasoning_zh": "購買日為 2025 年 4 月 10 日，報修日為 2026 年 10 月 20 日（約第 18 個月），仍在 24 個月零件免費保固期內。",
                        },
                    ],
                    "explanation_zh": "本題為跨文件推論題。比對第二篇表格，咖啡機購買日為 `April 10, 2025`，報修日為 `October 20, 2026`，持有時間約為 18 個月（落在第 13–24 個月區間）。對照第一篇保固條款第 1 條與第 3 條，`digital pressure control board` 為明確列入 24 個月保固的零件，且在第 13 至 24 個月期間「保固範圍內的替換零件本身仍免費（replacement covered parts remain free of charge）」，故選 **(A)**。",
                    "distractor_notes": [
                        {"choice_id": "B", "reason_zh": "第 1 條明確將 digital pressure control board 列入保固範圍。"},
                        {"choice_id": "C", "reason_zh": "零件保固為 24 個月（至 2027 年 4 月），並非 12 個月。"},
                        {"choice_id": "D", "reason_zh": "客戶距離授權維修中心僅 18 公里，可派遣技師到場維修。"},
                    ],
                    "vocabulary": [
                        {
                            "term_en": "free of charge",
                            "meaning_zh": "免費",
                            "example_en": "Covered replacement parts are supplied free of charge.",
                        }
                    ],
                    "estimated_time_sec": 40,
                },
                {
                    "item_id": "ag-i-p7-000006-4",
                    "prompt_en": "What will Roast & Reed Book Café have to pay for this service visit?",
                    "choices": [
                        {"id": "A", "text_en": "Nothing, because the café is within 80 kilometers of a service center"},
                        {"id": "B", "text_en": "Only a $85 technician travel fee"},
                        {"id": "C", "text_en": "An $85 technician travel fee plus the cost of two rubber gaskets"},
                        {"id": "D", "text_en": "The full cost of the pressure control board and technician labor"},
                    ],
                    "answer_choice_id": "C",
                    "skill_tags": ["cross_document", "conditions_exceptions"],
                    "evidence": [
                        {
                            "source_type": "document_block",
                            "source_id": "ag-blk-p7-000006-1",
                            "quote_en": "2. Exclusions: This limited warranty does not cover rubber portafilter gaskets ... Replacement of excluded accessories is billed at standard catalog rates. ... 3. ... In months 13 through 24, replacement covered parts remain free of charge, but a flat $85 technician travel fee applies to all on-site visits.",
                            "reasoning_zh": "第 13–24 個月期間到場維修需收 $85 技師差旅費，且橡膠墊圈（rubber portafilter gaskets）屬除外配件需按型錄標準價收費。",
                        },
                        {
                            "source_type": "document_block",
                            "source_id": "ag-blk-p7-000006-3",
                            "quote_en": "please have the technician bring two new rubber portafilter gaskets, as ours are worn.",
                            "reasoning_zh": "客戶請技師順便帶來兩個新的橡膠沖煮手把墊圈。",
                        },
                    ],
                    "explanation_zh": "本題考多條件跨文件整合：\n1. **持有期間**：2025 年 4 月至 2026 年 10 月為第 18 個月（`months 13 through 24`），依第 3 條規定須支付 **$85 技師到場差旅費**。\n2. **更換項目**：數位壓力控制板在 24 個月保固內免費；但客戶另要求更換兩個磨損的 `rubber portafilter gaskets`（橡膠墊圈），依第 2 條除外條款規定，橡膠墊圈不在保固內，須按標準型錄價格計費。\n因此咖啡館須支付 **(C) 85 美元的技師差旅費加上兩個橡膠墊圈的費用**。",
                    "distractor_notes": [
                        {"choice_id": "A", "reason_zh": "80 公里內免費派遣技師僅限購買後前 12 個月（During the first twelve months），本案已第 18 個月。"},
                        {"choice_id": "B", "reason_zh": "漏計了不在保固範圍內的兩個橡膠墊圈（rubber portafilter gaskets）費用。"},
                        {"choice_id": "D", "reason_zh": "數位壓力控制板在 24 個月保固期內免費提供。"},
                    ],
                    "vocabulary": [
                        {
                            "term_en": "gasket",
                            "meaning_zh": "墊圈；密封圈",
                            "example_en": "A worn rubber gasket can cause water leaks around the filter holder.",
                        }
                    ],
                    "estimated_time_sec": 45,
                },
                {
                    "item_id": "ag-i-p7-000006-5",
                    "prompt_en": "In the warranty policy, the word \"flat\" in paragraph 3 is closest in meaning to",
                    "choices": [
                        {"id": "A", "text_en": "fixed"},
                        {"id": "B", "text_en": "level"},
                        {"id": "C", "text_en": "shallow"},
                        {"id": "D", "text_en": "dull"},
                    ],
                    "answer_choice_id": "A",
                    "skill_tags": ["vocabulary_in_context"],
                    "evidence": [
                        {
                            "source_type": "document_block",
                            "source_id": "ag-blk-p7-000006-1",
                            "quote_en": "a flat $85 technician travel fee applies to all on-site visits.",
                            "reasoning_zh": "a flat $85 fee 意為「單一固定 85 美元的費用」，故 flat 與 fixed（固定的、均一的）同義。",
                        }
                    ],
                    "explanation_zh": "本題考一詞多義在商務收費語境中的含義。`a flat $85 technician travel fee` 意指不論距離遠近皆收取「均一／固定 85 美元的技師差旅費」，故 `flat` 在此等於 **(A) fixed**（固定的）。",
                    "distractor_notes": [
                        {"choice_id": "B", "reason_zh": "level 對應 flat 的物理空間「平坦的」字義，不適用於費用金額。"},
                        {"choice_id": "C", "reason_zh": "shallow 意為「淺的」。"},
                        {"choice_id": "D", "reason_zh": "dull 意為「沉悶的、無光澤的」。"},
                    ],
                    "vocabulary": [
                        {
                            "term_en": "flat fee",
                            "meaning_zh": "固定費用；均一價",
                            "example_en": "The courier charges a flat fee of $15 for local deliveries.",
                        }
                    ],
                    "estimated_time_sec": 25,
                },
            ],
            "provenance": make_provenance(),
            "review_refs": [],
        },
        # --- Group 7: ag-g-p7-000007 (Triple Passage: Catering Rate Table + Revision Email + Final Invoice, 5 items, D5) ---
        {
            "schema_version": "1.0.0",
            "group_id": "ag-g-p7-000007",
            "version": 1,
            "family_id": "ag-fam-p7-triple-catering-quote-email-invoice",
            "pool": "training",
            "fixture": False,
            "part": 7,
            "layout": "triple_passage",
            "scenario": "event_catering",
            "difficulty": {
                "level": "D5",
                "rationale_zh": "高難度三篇閱讀（外燴方案價目表＋客戶變更人數與餐點信件＋最終結算發票），需整合三份文件才能推得選用方案、免費甜點升級條件與帳單折抵金額。",
                "basis": "editorial",
            },
            "content_status": "draft",
            "stimulus": {
                "documents": [
                    {
                        "document_id": "ag-doc-p7-000007-1",
                        "genre": "rate_sheet",
                        "title_en": "Saffron & Sage Corporate Catering — 2026 Luncheon Packages",
                        "blocks": [
                            {
                                "block_id": "ag-blk-p7-000007-1",
                                "type": "table",
                                "columns": ["Package Tier", "Price per Guest", "Menu Highlights", "Minimum Order"],
                                "rows": [
                                    ["Artisan Express", "$22", "Assorted wraps, seasonal fruit, iced tea", "20 guests"],
                                    ["Bistro Classic", "$30", "Herb-roasted chicken or grilled salmon, two warm sides, coffee service", "30 guests"],
                                    ["Executive Harvest", "$38", "Braised short ribs or truffle risotto, artisan salad, pastry platter", "40 guests"],
                                ],
                            },
                            {
                                "block_id": "ag-blk-p7-000007-2",
                                "type": "text",
                                "text_en": (
                                    "Booking Policies:\n"
                                    "• Volume Perk: Orders for 60 or more guests automatically receive a complimentary artisan dessert platter (a $120 value), regardless of package tier.\n"
                                    "• Final Headcount: Changes to guest count or dietary selections must be submitted at least 72 hours before the event. Late adjustments incur a $75 rush-prep surcharge.\n"
                                    "• Deposit: A $300 advance deposit is required upon booking and is deducted from the final invoice."
                                ),
                            },
                        ],
                    },
                    {
                        "document_id": "ag-doc-p7-000007-2",
                        "genre": "email",
                        "title_en": "Subject: Updated Headcount for October 23 Client Luncheon (Order #CC-418)",
                        "blocks": [
                            {
                                "block_id": "ag-blk-p7-000007-3",
                                "type": "text",
                                "text_en": (
                                    "To: orders@saffronandsage.com\n"
                                    "From: Elena Vance <evance@meridianbio.com>\n"
                                    "Date: October 18\n"
                                    "Subject: Updated Headcount for October 23 Client Luncheon (Order #CC-418)\n\n"
                                    "Hello Catering Team,\n\n"
                                    "I am writing to update the guest count for Meridian Biotech's client luncheon next Friday, October 23. "
                                    "When I paid our $300 deposit last month, we estimated 45 attendees for the herb-roasted chicken and grilled salmon buffet. "
                                    "However, twenty additional regional distributors have just registered, bringing our final total to 65 guests.\n\n"
                                    "Could you also make sure that 15 of the 65 entrées are vegetarian pasta instead of meat or fish? "
                                    "Finally, since our updated headcount qualifies us for your volume perk, please include that platter with the coffee station setup.\n\n"
                                    "Thank you,\n"
                                    "Elena Vance"
                                ),
                            }
                        ],
                    },
                    {
                        "document_id": "ag-doc-p7-000007-3",
                        "genre": "invoice",
                        "title_en": "Saffron & Sage Catering — Final Invoice #INV-8829",
                        "blocks": [
                            {
                                "block_id": "ag-blk-p7-000007-4",
                                "type": "table",
                                "columns": ["Description", "Quantity", "Unit Price", "Amount"],
                                "rows": [
                                    ["Luncheon Buffet Package (Order #CC-418)", "65", "$30.00", "$1,950.00"],
                                    ["Vegetarian Entrée Substitution", "15", "$0.00", "$0.00"],
                                    ["Artisan Dessert Platter (60+ Guest Perk)", "1", "$0.00", "$0.00"],
                                    ["Delivery & Chafing Dish Setup", "1", "$60.00", "$60.00"],
                                    ["Less Advance Deposit Paid (Sept. 15)", "—", "—", "-$300.00"],
                                    ["Balance Due Upon Delivery", "—", "—", "$1,710.00"],
                                ],
                            }
                        ],
                    },
                ],
                "speakers": [],
                "audio_script": [],
            },
            "assets": [],
            "items": [
                {
                    "item_id": "ag-i-p7-000007-1",
                    "prompt_en": "Which catering package did Meridian Biotech order?",
                    "choices": [
                        {"id": "A", "text_en": "Artisan Express"},
                        {"id": "B", "text_en": "Bistro Classic"},
                        {"id": "C", "text_en": "Executive Harvest"},
                        {"id": "D", "text_en": "Custom Weekend Buffet"},
                    ],
                    "answer_choice_id": "B",
                    "skill_tags": ["cross_document", "explicit_detail"],
                    "evidence": [
                        {
                            "source_type": "document_block",
                            "source_id": "ag-blk-p7-000007-3",
                            "quote_en": "we estimated 45 attendees for the herb-roasted chicken and grilled salmon buffet.",
                            "reasoning_zh": "第二篇信件提到預訂的是香草烤雞與烤鮭魚自助餐（herb-roasted chicken and grilled salmon）。",
                        },
                        {
                            "source_type": "document_block",
                            "source_id": "ag-blk-p7-000007-4",
                            "quote_en": "Luncheon Buffet Package (Order #CC-418) | 65 | $30.00 | $1,950.00",
                            "reasoning_zh": "第三篇發票顯示每人單價為 $30.00。",
                        },
                        {
                            "source_type": "document_block",
                            "source_id": "ag-blk-p7-000007-1",
                            "quote_en": "Bistro Classic | $30 | Herb-roasted chicken or grilled salmon, two warm sides, coffee service | 30 guests",
                            "reasoning_zh": "對照第一篇表格，單價 $30 且主菜為香草烤雞或烤鮭魚的方案為 Bistro Classic。",
                        },
                    ],
                    "explanation_zh": "本題為跨三篇文件整合題。第二篇電子郵件提到訂購的主菜為 `herb-roasted chicken and grilled salmon buffet`，第三篇最終發票顯示每人單價為 `$30.00`。對照第一篇價目表，單價 `$30` 且包含香草烤雞或烤鮭魚的方案為 **(B) Bistro Classic**。",
                    "distractor_notes": [
                        {"choice_id": "A", "reason_zh": "Artisan Express 單價為 $22，內容為捲餅與水果。"},
                        {"choice_id": "C", "reason_zh": "Executive Harvest 單價為 $38，內容為燉牛小排或松露燉飯。"},
                        {"choice_id": "D", "reason_zh": "價目表中並無此方案名稱。"},
                    ],
                    "vocabulary": [
                        {
                            "term_en": "entrée",
                            "meaning_zh": "（美式英語）主菜",
                            "example_en": "Guests may choose between a fish entrée and a vegetarian pasta dish.",
                        }
                    ],
                    "estimated_time_sec": 35,
                },
                {
                    "item_id": "ag-i-p7-000007-2",
                    "prompt_en": "Why was Meridian Biotech NOT charged a $75 rush-prep surcharge?",
                    "choices": [
                        {"id": "A", "text_en": "Because Ms. Vance submitted the headcount change more than 72 hours before the event"},
                        {"id": "B", "text_en": "Because the company is a first-time customer"},
                        {"id": "C", "text_en": "Because the number of guests was reduced rather than increased"},
                        {"id": "D", "text_en": "Because the vegetarian pasta costs less to prepare than salmon"},
                    ],
                    "answer_choice_id": "A",
                    "skill_tags": ["cross_document", "conditions_exceptions", "chronology"],
                    "evidence": [
                        {
                            "source_type": "document_block",
                            "source_id": "ag-blk-p7-000007-2",
                            "quote_en": "Changes to guest count or dietary selections must be submitted at least 72 hours before the event. Late adjustments incur a $75 rush-prep surcharge.",
                            "reasoning_zh": "第一篇規定活動前至少 72 小時（3天）提出人數或飲食變更免收 $75 急件準備費。",
                        },
                        {
                            "source_type": "document_block",
                            "source_id": "ag-blk-p7-000007-3",
                            "quote_en": "Date: October 18 ... update the guest count for Meridian Biotech's client luncheon next Friday, October 23.",
                            "reasoning_zh": "第二篇信件寄出日期為 10 月 18 日，距離 10 月 23 日午宴還有 5 天（120 小時），超過 72 小時門檻。",
                        },
                    ],
                    "explanation_zh": "本題考跨文件時序與條件判斷。第一篇預訂政策載明：「人數或飲食選擇變更須於活動至少 72 小時（即三天）前提出，逾期調整將加收 75 美元急件準備費」。對照第二篇郵件，Ms. Vance 於 **10 月 18 日**寄信變更 **10 月 23 日**的午宴人數，提前了整整五天（超過 72 小時），因此第三篇發票未收 $75 急件費，故選 **(A)**。",
                    "distractor_notes": [
                        {"choice_id": "B", "reason_zh": "文中未提供新客戶免收急件費的條款。"},
                        {"choice_id": "C", "reason_zh": "人數是由 45 人增加為 65 人，而非減少。"},
                        {"choice_id": "D", "reason_zh": "免費原因為提前五天通知，與素食義大利麵食材成本無關。"},
                    ],
                    "vocabulary": [
                        {
                            "term_en": "incur a surcharge",
                            "meaning_zh": "產生額外附加費",
                            "example_en": "Orders placed less than three days in advance incur a surcharge.",
                        }
                    ],
                    "estimated_time_sec": 40,
                },
                {
                    "item_id": "ag-i-p7-000007-3",
                    "prompt_en": "Why did Meridian Biotech receive the Artisan Dessert Platter at no charge?",
                    "choices": [
                        {"id": "A", "text_en": "It paid its $300 deposit in September."},
                        {"id": "B", "text_en": "Its updated guest count exceeded 60 people."},
                        {"id": "C", "text_en": "It ordered the Executive Harvest package."},
                        {"id": "D", "text_en": "It redeemed a promotional coupon code."},
                    ],
                    "answer_choice_id": "B",
                    "skill_tags": ["cross_document", "conditions_exceptions"],
                    "evidence": [
                        {
                            "source_type": "document_block",
                            "source_id": "ag-blk-p7-000007-2",
                            "quote_en": "Volume Perk: Orders for 60 or more guests automatically receive a complimentary artisan dessert platter (a $120 value), regardless of package tier.",
                            "reasoning_zh": "第一篇規定凡滿 60 人以上的訂單，不限方案等級皆自動獲贈價值 $120 的手工甜點拼盤。",
                        },
                        {
                            "source_type": "document_block",
                            "source_id": "ag-blk-p7-000007-3",
                            "quote_en": "bringing our final total to 65 guests. ... since our updated headcount qualifies us for your volume perk",
                            "reasoning_zh": "第二篇信件將總人數提高至 65 人，達到 60 人以上滿額贈門檻（第三篇發票亦標明 60+ Guest Perk $0.00）。",
                        },
                    ],
                    "explanation_zh": "第一篇 `Volume Perk` 條款規定：「凡滿 60 位賓客以上的訂單，不論方案等級，皆自動獲贈一份免費的手工甜點拼盤」。第二篇郵件中，Ms. Vance 將人數由 45 人追加至 **65 人**，跨越了 60 人門檻，故第三篇發票上 `Artisan Dessert Platter (60+ Guest Perk)` 計價為 `$0.00`，故選 **(B)**。",
                    "distractor_notes": [
                        {"choice_id": "A", "reason_zh": "300 美元訂金是所有訂單預訂時的必要條件，並非贈送甜點拼盤的原因。"},
                        {"choice_id": "C", "reason_zh": "該公司訂購的是每客 $30 的 Bistro Classic，而非 $38 的 Executive Harvest。"},
                        {"choice_id": "D", "reason_zh": "這是滿 60 人自動享有的滿額優惠，並非使用優惠碼。"},
                    ],
                    "vocabulary": [
                        {
                            "term_en": "perk",
                            "meaning_zh": "額外優惠；福利；附帶禮遇",
                            "example_en": "Free delivery is a perk offered to corporate account holders.",
                        }
                    ],
                    "estimated_time_sec": 35,
                },
                {
                    "item_id": "ag-i-p7-000007-4",
                    "prompt_en": "When did Meridian Biotech pay its advance deposit?",
                    "choices": [
                        {"id": "A", "text_en": "On September 15"},
                        {"id": "B", "text_en": "On October 18"},
                        {"id": "C", "text_en": "On October 20"},
                        {"id": "D", "text_en": "On October 23"},
                    ],
                    "answer_choice_id": "A",
                    "skill_tags": ["explicit_detail", "cross_document"],
                    "evidence": [
                        {
                            "source_type": "document_block",
                            "source_id": "ag-blk-p7-000007-4",
                            "quote_en": "Less Advance Deposit Paid (Sept. 15) | — | — | -$300.00",
                            "reasoning_zh": "第三篇發票第五列明確記載預付訂金支付日期為 9 月 15 日（Sept. 15）。",
                        }
                    ],
                    "explanation_zh": "第二篇郵件提到「當我上個月支付 300 美元訂金時（When I paid our $300 deposit last month）」，再查閱第三篇最終發票的扣抵項目 `Less Advance Deposit Paid (Sept. 15)`，即可確知預付訂金是在 **(A) 9 月 15 日**支付。",
                    "distractor_notes": [
                        {"choice_id": "B", "reason_zh": "10 月 18 日是寄出人數更新郵件的日期。"},
                        {"choice_id": "C", "reason_zh": "10 月 20 日為活動前 72 小時截止日，並非付訂金日期。"},
                        {"choice_id": "D", "reason_zh": "10 月 23 日為午宴舉辦當日。"},
                    ],
                    "vocabulary": [
                        {
                            "term_en": "advance deposit",
                            "meaning_zh": "預付訂金",
                            "example_en": "The advance deposit will be deducted from your final bill.",
                        }
                    ],
                    "estimated_time_sec": 30,
                },
                {
                    "item_id": "ag-i-p7-000007-5",
                    "prompt_en": "What is indicated on the final invoice?",
                    "choices": [
                        {"id": "A", "text_en": "Substituting vegetarian entrées did not increase the package price."},
                        {"id": "B", "text_en": "Delivery and setup were included at no charge."},
                        {"id": "C", "text_en": "The full balance has already been paid by credit card."},
                        {"id": "D", "text_en": "Sixty-five vegetarian meals were ordered."},
                    ],
                    "answer_choice_id": "A",
                    "skill_tags": ["explicit_detail", "inference"],
                    "evidence": [
                        {
                            "source_type": "document_block",
                            "source_id": "ag-blk-p7-000007-4",
                            "quote_en": "Vegetarian Entrée Substitution | 15 | $0.00 | $0.00",
                            "reasoning_zh": "發票第二列顯示 15 份素食主菜替換（Vegetarian Entrée Substitution）的單價與總價皆為 $0.00，未增加方案價格。",
                        }
                    ],
                    "explanation_zh": "觀察第三篇最終發票第二列：`Vegetarian Entrée Substitution | 15 | $0.00 | $0.00`，可知將其中 15 份主菜替換為素食義大利麵完全不加價（單價與金額皆為 `$0.00`），故選 **(A)**。",
                    "distractor_notes": [
                        {"choice_id": "B", "reason_zh": "發票第四列顯示運送與保溫餐爐架設（Delivery & Chafing Dish Setup）收費 $60.00。"},
                        {"choice_id": "C", "reason_zh": "發票最末列顯示 $1,710.00 為送達時應付尾款（Balance Due Upon Delivery），尚未付清。"},
                        {"choice_id": "D", "reason_zh": "總人數為 65 人，但其中只有 15 份是素食主菜（15 of the 65 entrées）。"},
                    ],
                    "vocabulary": [
                        {
                            "term_en": "chafing dish",
                            "meaning_zh": "（外燴自助餐用的）保溫餐爐／保溫盤",
                            "example_en": "The catering crew set up stainless-steel chafing dishes on the buffet table.",
                        }
                    ],
                    "estimated_time_sec": 35,
                },
            ],
            "provenance": make_provenance(),
            "review_refs": [],
        },
    ]
    return groups


def main() -> None:
    out_dir = ROOT / "drafts" / "batch-ag-0005"
    out_dir.mkdir(parents=True, exist_ok=True)
    groups = build_groups()
    groups_path = out_dir / "groups.jsonl"
    with groups_path.open("w", encoding="utf-8") as f:
        for g in groups:
            f.write(json.dumps(g, ensure_ascii=False) + "\n")
    print(f"Wrote {len(groups)} groups ({sum(len(g['items']) for g in groups)} items) to {groups_path}")


if __name__ == "__main__":
    main()
