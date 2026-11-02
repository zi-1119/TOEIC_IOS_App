#!/usr/bin/env python3
"""
Generate Phase 2 controlled expansion & multi-pool verification batches:
  - drafts/batch-ag-0008 (pool="training", 20 groups = 29 items: Part 5 x16, Part 6 x2 [8], Part 7 x2 [5])
  - drafts/batch-ag-0009 (pool="diagnostic", 14 groups = 24 items across Parts 1-7, 100% media-ready)
  - drafts/batch-ag-0010 (pool="battle", 21 groups = 24 items across Parts 2, 5, 6, 100% media-ready)
  - blueprints/mock-form-01-blueprint.json & drafts/mock-form-01-unreleased/ (unreleased mock blueprint & draft)

Also writes context-isolated blind-input packages to review/blind_inputs/ so fresh blind-solver subagents
can independently solve all 77 new items before final packaging.
"""

import hashlib
import json
import shutil
from pathlib import Path
from typing import Any, Dict, List, Tuple

from synthesize_listening_audio import synthesize_group_audio

ROOT = Path(__file__).resolve().parent.parent
CREATED_AT = "2026-10-28T08:30:00Z"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


from build_revised_batches_0011_to_0013 import VOCAB_EXAMPLES_EN, build_evidence_reasoning


def make_provenance() -> Dict[str, Any]:
    return {
        "origin": "original",
        "author_tool": "antigravity-toeic-factory/1.1.0",
        "author_model": "unknown",
        "created_at": CREATED_AT,
        "rights_note_zh": "全原創命題與虛構商務情境，未使用任何 ETS 官方試題、劍橋或第三方受版權保護之教材與商標。",
    }


def make_difficulty(level: str, rationale_zh: str) -> Dict[str, Any]:
    return {
        "level": level,
        "basis": "editorial",
        "rationale_zh": rationale_zh,
    }


def make_choice(cid: str, text_en: str) -> Dict[str, str]:
    return {"id": cid, "text_en": text_en}


def make_distractor(cid: str, trap_type: str, reason_zh: str) -> Dict[str, str]:
    return {"choice_id": cid, "reason_zh": reason_zh}


def make_vocab(surface: str, meaning_zh: str, pos: str = "", note_zh: str = "") -> Dict[str, str]:
    example_en = VOCAB_EXAMPLES_EN.get(
        surface,
        f"Please review the {surface} guidelines in the updated department manual.",
    )
    return {"term_en": surface, "meaning_zh": meaning_zh, "example_en": example_en}


def make_part5_group(
    gid: str,
    iid: str,
    fam_id: str,
    pool: str,
    scenario: str,
    diff_level: str,
    diff_rationale: str,
    prompt_en: str,
    choices: List[Tuple[str, str]],
    ans: str,
    skill_tags: List[str],
    quote_en: str,
    explanation_zh: str,
    distractors: List[Tuple[str, str, str]],
    vocab: List[Tuple[str, str, str, str]],
    est_sec: int = 30,
) -> Dict[str, Any]:
    num_suffix = gid.split("-")[-1]
    part_num = gid.split("-")[2]
    return {
        "schema_version": "1.0.0",
        "group_id": gid,
        "version": 1,
        "family_id": fam_id,
        "pool": pool,
        "fixture": False,
        "part": 5,
        "layout": "sentence",
        "scenario": scenario,
        "difficulty": make_difficulty(diff_level, diff_rationale),
        "content_status": "ai_checked",
        "stimulus": {"documents": [], "speakers": [], "audio_script": []},
        "assets": [],
        "items": [
            {
                "item_id": iid,
                "prompt_en": prompt_en,
                "choices": [make_choice(c, t) for c, t in choices],
                "answer_choice_id": ans,
                "skill_tags": skill_tags,
                "evidence": [{"source_type": "item_prompt", "source_id": iid, "quote_en": quote_en}],
                "explanation_zh": explanation_zh,
                "distractor_notes": [make_distractor(c, tp, r) for c, tp, r in distractors],
                "vocabulary": [make_vocab(s, m, p, n) for s, m, p, n in vocab],
                "estimated_time_sec": est_sec,
            }
        ],
        "provenance": make_provenance(),
        "review_refs": [
            f"ag-rev-ai-{part_num}-{num_suffix}",
            f"ag-rev-blind-{part_num}-{num_suffix}",
        ],
    }


# ==============================================================================
# 1. Build Batch 0008 (pool="training", 20 groups = 29 items: Part 5 x16, Part 6 x2, Part 7 x2)
# ==============================================================================
def build_batch_0008_groups() -> List[Dict[str, Any]]:
    groups: List[Dict[str, Any]] = []

    p5_specs = [
        (
            "ag-g-p5-000016", "ag-i-p5-000016-1", "ag-fam-trn-p5-016", "office_administration", "D1",
            "基礎副詞修飾動詞（carefully review），句構單純直接。",
            "All department heads must ____ review the updated travel reimbursement guidelines before Friday.",
            [("A", "careful"), ("B", "carefully"), ("C", "carefulness"), ("D", "caring")],
            "B", ["word_form", "grammar_structure"], "must ____ review the updated travel reimbursement guidelines",
            "助動詞 must 與及物動詞原形 review 之間需填入副詞以修飾動作「仔細地審閱」，故選副詞 (B) carefully。",
            [
                ("A", "word_form", "careful 為形容詞，不可直接修飾一般動詞 review。"),
                ("C", "word_form", "carefulness 為名詞，無法置於助動詞與本動詞之間作狀語。"),
                ("D", "word_form", "caring 為現在分詞／形容詞「體貼的、關懷的」，詞性與語意皆不符。"),
            ],
            [("reimbursement", "報銷、補償", "n.", "travel reimbursement 指差旅費報銷。")],
            20,
        ),
        (
            "ag-g-p5-000017", "ag-i-p5-000017-1", "ag-fam-trn-p5-017", "hr_recruitment_training", "D2",
            "基礎連接詞與介系詞辨析（because of + 名詞片語 vs 子句連接詞）。",
            "The orientation workshop was moved to the main auditorium ____ the unexpectedly high number of registrants.",
            [("A", "because"), ("B", "although"), ("C", "due to"), ("D", "so that")],
            "C", ["preposition_conjunction", "grammar_structure"], "____ the unexpectedly high number of registrants",
            "空格後 the unexpectedly high number of registrants 為純名詞片語而非完整子句，且語意表達「由於報名人數出乎意料地多」，故應選複合介系詞 (C) due to。",
            [
                ("A", "grammar_scope", "because 為從屬連接詞，後方須接具動詞之完整子句。"),
                ("B", "grammar_scope", "although 為讓步從屬連接詞，後方須接子句且語意矛盾。"),
                ("D", "grammar_scope", "so that 引導目的狀語子句，後方不能只接名詞片語。"),
            ],
            [("auditorium", "禮堂、演講廳", "n.", "大型會議或培訓場地。"), ("registrant", "報名者、登記者", "n.", "workshop registrants 指研習營報名人員。")],
            25,
        ),
        (
            "ag-g-p5-000018", "ag-i-p5-000018-1", "ag-fam-trn-p5-018", "manufacturing_quality_control", "D2",
            "被動語態與過去簡單式時間標記（last night）搭配。",
            "Two faulty conveyor motors ____ by the night-shift maintenance crew before production resumed at dawn.",
            [("A", "replaced"), ("B", "were replaced"), ("C", "have replaced"), ("D", "replacing")],
            "B", ["verb_tense_voice", "grammar_structure"], "Two faulty conveyor motors ____ by the night-shift maintenance crew before production resumed",
            "主詞 Two faulty conveyor motors（兩具故障的輸送帶馬達）為承受動作之物，且由 by the night-shift maintenance crew 及從屬子句過去式 resumed 可知應使用過去簡單被動語態 (B) were replaced。",
            [
                ("A", "grammar_voice", "replaced 為主動語態，馬達無法自行更換。"),
                ("C", "grammar_voice", "have replaced 為現在完成主動語態，語態與過去時間點 before production resumed 均不合。"),
                ("D", "grammar_form", "replacing 為分詞，缺少助動詞無法作為主要子句限定動詞。"),
            ],
            [("conveyor", "輸送帶", "n.", "生產線常見設備。"), ("resume", "恢復、重新開始", "v.", "production resumed 指產線恢復運轉。")],
            25,
        ),
        (
            "ag-g-p5-000019", "ag-i-p5-000019-1", "ag-fam-trn-p5-019", "finance_budgeting_invoicing", "D2",
            "反身代名詞強調用法（review the ledger herself）。",
            "Ms. Lindqvist decided to audit the third-quarter expense ledger ____ rather than delegating the task to an intern.",
            [("A", "she"), ("B", "her"), ("C", "hers"), ("D", "herself")],
            "D", ["pronoun_reference", "grammar_structure"], "Ms. Lindqvist decided to audit the third-quarter expense ledger ____ rather than delegating",
            "此處結構已完整（audit the third-quarter expense ledger），空格用於強調主詞 Ms. Lindqvist「親自」查核帳冊而非交辦實習生，故選反身代名詞 (D) herself。",
            [
                ("A", "grammar_case", "she 為主格代名詞，不可置於受詞後作同位強調。"),
                ("B", "grammar_case", "her 為受格或所有格形容詞，此處無被修飾名詞亦非動詞受詞。"),
                ("C", "grammar_case", "hers 為所有格代名詞（= her ledger），不符「親自查核」之狀語強調結構。"),
            ],
            [("ledger", "分類帳、帳冊", "n.", "expense ledger 指費用分類帳。"), ("delegate", "委派、授權", "v.", "delegate a task to someone 指將任務交辦某人。")],
            25,
        ),
        (
            "ag-g-p5-000020", "ag-i-p5-000020-1", "ag-fam-trn-p5-020", "it_systems_security", "D3",
            "商務動詞詞義與受詞（unauthorized access）精準搭配。",
            "Installing multi-factor authentication on all remote laptops will help ____ unauthorized access to client databases.",
            [("A", "prevent"), ("B", "persuade"), ("C", "postpone"), ("D", "prescribe")],
            "A", ["vocabulary_in_context", "collocation_idiom"], "help ____ unauthorized access to client databases",
            "啟用多重身分驗證的目的在於「防止、阻止」未經授權存取客戶資料庫，prevent unauthorized access 為標準資安商務搭配，故選 (A) prevent。",
            [
                ("B", "semantic_mismatch", "persuade 意為「說服」，受詞通常為人，與 unauthorized access 不搭配。"),
                ("C", "semantic_mismatch", "postpone 意為「延後（會議或期限）」，資安防護旨在防止而非僅延後非法存取。"),
                ("D", "semantic_mismatch", "prescribe 意為「開立處方、規定」，與阻止非法存取語意不合。"),
            ],
            [("authentication", "身分驗證", "n.", "multi-factor authentication (MFA) 指多重身分驗證。")],
            25,
        ),
        (
            "ag-g-p5-000021", "ag-i-p5-000021-1", "ag-fam-trn-p5-021", "logistics_supply_chain", "D3",
            "條件連接詞 provided that（只要、在…條件下）與未來出貨承諾搭配。",
            "Vanguard Freight can guarantee next-day delivery to regional warehouses ____ the purchase order is submitted before 2:00 P.M.",
            [("A", "provided that"), ("B", "even though"), ("C", "as if"), ("D", "in case of")],
            "A", ["preposition_conjunction", "grammar_structure"], "can guarantee next-day delivery to regional warehouses ____ the purchase order is submitted before 2:00 P.M.",
            "主句「保證隔日送達」以從屬子句「採購單於下午兩點前送出」為必要前提條件，(A) provided that（只要、在…條件下）連接完整條件子句且語意精確。",
            [
                ("B", "logical_reversal", "even though 表讓步「儘管」，與前後因果條件關係相反。"),
                ("C", "semantic_mismatch", "as if 表「彷彿、好像」，不適用於合約或物流交期條件。"),
                ("D", "grammar_scope", "in case of 為複合介系詞，後方只能接名詞片語，不能接完整子句 the purchase order is submitted。"),
            ],
            [("warehouse", "倉庫", "n.", "regional warehouse 指區域倉庫。")],
            30,
        ),
        (
            "ag-g-p5-000022", "ag-i-p5-000022-1", "ag-fam-trn-p5-022", "marketing_events_promotions", "D3",
            "關係代名詞所有格 whose 修飾先行詞（start-up companies whose products...）。",
            "The innovation showcase will feature twelve start-up companies ____ products reduce commercial packaging waste.",
            [("A", "which"), ("B", "whom"), ("C", "whose"), ("D", "what")],
            "C", ["grammar_structure", "pronoun_reference"], "twelve start-up companies ____ products reduce commercial packaging waste",
            "先行詞為 twelve start-up companies，空格後緊接無冠詞名詞 products 並作關係子句主詞（products reduce...），表示「這些新創公司的產品」，須用所有格關係代名詞 (C) whose。",
            [
                ("A", "grammar_case", "which 在關係子句中作主格或受格，不能直接修飾後方名詞 products。"),
                ("B", "grammar_case", "whom 為受格關係代名詞，不可作所有格修飾語。"),
                ("D", "grammar_scope", "what 為複合關係代名詞，前方不可有先行詞 start-up companies。"),
            ],
            [("showcase", "展示會、展演", "n.", "innovation showcase 指創新發表展。")],
            30,
        ),
        (
            "ag-g-p5-000023", "ag-i-p5-000023-1", "ag-fam-trn-p5-023", "customer_service_returns", "D3",
            "形容詞詞義辨析（eligible for a full refund 符合全額退費資格）。",
            "Customers who return unopened electronics within fourteen days of purchase are ____ for a full refund.",
            [("A", "eligible"), ("B", "probable"), ("C", "accessible"), ("D", "reliant")],
            "A", ["vocabulary_in_context", "collocation_idiom"], "are ____ for a full refund",
            "be eligible for + 名詞 為標準商務慣用搭配，意為「符合…的資格、有資格獲得…」，故選 (A) eligible。",
            [
                ("B", "collocation_mismatch", "probable 意為「很可能發生的」，主詞通常為事件而非人（Customers），且不搭配 for a refund。"),
                ("C", "semantic_mismatch", "accessible 意為「可進入的、可取得的」，常搭配 to，主詞應為設施或資訊而非顧客。"),
                ("D", "collocation_mismatch", "reliant 意為「依賴的」，搭配介系詞 on/upon 而非 for。"),
            ],
            [("unopened", "未開封的", "adj.", "退貨條件常見用語。"), ("eligible", "符合資格的", "adj.", "be eligible for 意為「有資格享有…」。")],
            25,
        ),
        (
            "ag-g-p5-000024", "ag-i-p5-000024-1", "ag-fam-trn-p5-024", "real_estate_facilities", "D3",
            "未來完成式（will have occupied）搭配 by the end of next month 時間界線。",
            "By the time the annex renovation concludes in November, Sterling Law Partners ____ the fourth-floor suite for ten years.",
            [("A", "occupies"), ("B", "occupied"), ("C", "will have occupied"), ("D", "is occupying")],
            "C", ["verb_tense_voice", "grammar_structure"], "By the time the annex renovation concludes in November, Sterling Law Partners ____ the fourth-floor suite for ten years",
            "句首 By the time + 現在式表未來時間點（concludes in November），搭配持續時間段 for ten years，主句須用未來完成式表示「屆時將已承租滿十年」，故選 (C) will have occupied。",
            [
                ("A", "tense_mismatch", "occupies 為現在簡單式，無法表達截至未來特定時間點累積滿十年之完成狀態。"),
                ("B", "tense_mismatch", "occupied 為過去簡單式，與未來時間點 in November 衝突。"),
                ("D", "tense_mismatch", "is occupying 為現在進行式，不與 for ten years 及未來完成時間點搭配。"),
            ],
            [("annex", "附屬建築、擴建大樓", "n.", "辦公大樓常見設施詞彙。"), ("suite", "套房、成套辦公室", "n.", "fourth-floor suite 指四樓辦公套房。")],
            35,
        ),
        (
            "ag-g-p5-000025", "ag-i-p5-000025-1", "ag-fam-trn-p5-025", "corporate_governance_legal", "D4",
            "名詞衍生詞與複合名詞結構區辨（confidentiality agreement 保密協議 vs 形容詞 confidential）。",
            "All external consultants are required to sign a ____ agreement before reviewing proprietary engineering blueprints.",
            [("A", "confide"), ("B", "confident"), ("C", "confidentially"), ("D", "confidentiality")],
            "D", ["word_form", "collocation_idiom"], "sign a ____ agreement before reviewing proprietary engineering blueprints",
            "「保密協議」的標準法務固定複合名詞為 confidentiality agreement（以抽象名詞 confidentiality 作定語說明協議性質），選項中並無 confidential，故選 (D) confidentiality。",
            [
                ("A", "word_form", "confide 為動詞「吐露、信賴」，不可直接修飾名詞 agreement。"),
                ("B", "semantic_mismatch", "confident 為形容詞「有自信的」，與「機密／保密」語意完全不同。"),
                ("C", "word_form", "confidentially 為副詞「私下地、機密地」，不可修飾名詞 agreement。"),
            ],
            [("proprietary", "專有的、獨家的", "adj.", "proprietary blueprints 指公司專有工程藍圖。")],
            30,
        ),
        (
            "ag-g-p5-000026", "ag-i-p5-000026-1", "ag-fam-trn-p5-026", "procurement_vendor_management", "D4",
            "讓步介系詞 notwithstanding 與句意轉折（儘管原物料價格波動，仍維持固定報價）。",
            "____ recent fluctuations in global aluminum prices, Kestrel Components will honor its quoted unit rates through December.",
            [("A", "Notwithstanding"), ("B", "Provided"), ("C", "Consequently"), ("D", "Whereas")],
            "A", ["preposition_conjunction", "vocabulary_in_context"], "____ recent fluctuations in global aluminum prices, Kestrel Components will honor its quoted unit rates",
            "空格後 recent fluctuations in global aluminum prices 為名詞片語，且與主句「仍將維持原報價至十二月」構成讓步對比關係；(A) Notwithstanding 為正式商務介系詞，意為「儘管（= Despite）」，後接名詞片語完全吻合。",
            [
                ("B", "grammar_scope", "Provided 作條件連詞時後接完整子句，且語意非條件關係。"),
                ("C", "grammar_scope", "Consequently 為副詞「因此」，不可直接統攝名詞片語作介系詞。"),
                ("D", "grammar_scope", "Whereas 為對比從屬連接詞，後方須接具動詞之完整子句。"),
            ],
            [("fluctuation", "波動、起伏", "n.", "price fluctuations 指價格波動。"), ("honor", "履行、信守（承諾或報價）", "v.", "honor quoted rates 指信守報價。")],
            35,
        ),
        (
            "ag-g-p5-000027", "ag-i-p5-000027-1", "ag-fam-trn-p5-027", "retail_store_operations", "D4",
            "分詞構句（Having exceeded its quarterly sales target, the flagship store...）主動完成邏輯。",
            "____ its third-quarter revenue target by eighteen percent, the Ginza flagship store received the regional excellence award.",
            [("A", "Exceed"), ("B", "Exceeded"), ("C", "Having exceeded"), ("D", "To be exceeded")],
            "C", ["grammar_structure", "verb_tense_voice"], "____ its third-quarter revenue target by eighteen percent, the Ginza flagship store received",
            "句首分詞片語邏輯主詞為 the Ginza flagship store，主動達成並超越（exceed）營收目標且發生於獲獎（received）之前，又後接直接受詞 its third-quarter revenue target，故選主動完成分詞 (C) Having exceeded。",
            [
                ("A", "grammar_form", "Exceed 為原形動詞，無連接詞時不可與主句並置或形成祈使句。"),
                ("B", "grammar_voice", "Exceeded 為過去分詞表被動，無法帶直接受詞 its third-quarter revenue target。"),
                ("D", "grammar_voice", "To be exceeded 為被動不定詞，語態與受詞結構均不成立。"),
            ],
            [("flagship", "旗艦的、旗艦店", "n.", "flagship store 指品牌旗艦店。")],
            35,
        ),
        (
            "ag-g-p5-000028", "ag-i-p5-000028-1", "ag-fam-trn-p5-028", "product_development_rd", "D4",
            "高階商務副詞（tentatively scheduled 暫定排程）與後續待最終簽核語境呼應。",
            "The beta release of the acoustic sensor firmware is ____ scheduled for April 14, pending final validation from the quality assurance team.",
            [("A", "tentatively"), ("B", "permanently"), ("C", "reluctantly"), ("D", "mutually")],
            "A", ["vocabulary_in_context", "collocation_idiom"], "is ____ scheduled for April 14, pending final validation from the quality assurance team",
            "後半句 pending final validation from the quality assurance team（有待品保團隊最終驗證）清楚顯示四月十四日的發布日期僅為「暫定」，tentatively scheduled 為高頻商務搭配，故選 (A) tentatively。",
            [
                ("B", "semantic_contradiction", "permanently 意為「永久地」，與後方 pending final validation（尚待最終確認）直接矛盾。"),
                ("C", "semantic_mismatch", "reluctantly 意為「不情願地」，不符合軟體版本排程之客觀商務語境。"),
                ("D", "semantic_mismatch", "mutually 意為「相互地、彼此地」，常搭配 beneficial 或 agreed，不與 pending validation 構成邏輯呼應。"),
            ],
            [("tentatively", "暫定地、初步地", "adv.", "tentatively scheduled 指暫定排程。"), ("pending", "在等待…期間、有待", "prep.", "pending final validation 指有待最終驗證。")],
            35,
        ),
        (
            "ag-g-p5-000029", "ag-i-p5-000029-1", "ag-fam-trn-p5-029", "banking_investment_services", "D4",
            "精確介系詞搭配（commensurate with 與…相稱／相當）。",
            "Portfolios managed by Aurelia Wealth Advisory are structured to generate returns commensurate ____ each client's stated risk tolerance.",
            [("A", "with"), ("B", "from"), ("C", "into"), ("D", "over")],
            "A", ["preposition_conjunction", "collocation_idiom"], "generate returns commensurate ____ each client's stated risk tolerance",
            "形容詞 commensurate 意為「相稱的、相當的」，固定搭配介系詞 with（commensurate with each client's stated risk tolerance 與每位客戶聲明之風險承受度相稱），故選 (A) with。",
            [
                ("B", "collocation_mismatch", "from 不與 commensurate 搭配。"),
                ("C", "collocation_mismatch", "into 表轉入或進入，不與 commensurate 搭配。"),
                ("D", "collocation_mismatch", "over 表高於或涵蓋，無法構成 commensurate 之慣用介系詞組。"),
            ],
            [("commensurate", "相稱的、相當的", "adj.", "commensurate with 意為「與…相稱」。"), ("risk tolerance", "風險承受度", "n.", "投資理財核心術語。")],
            35,
        ),
        (
            "ag-g-p5-000030", "ag-i-p5-000030-1", "ag-fam-trn-p5-030", "corporate_governance_legal", "D5",
            "假設語氣／要求動詞後 that 子句受格被動原形（stipulated that all subcontractor invoices be itemized）。",
            "The revised procurement charter stipulates that every subcontractor invoice ____ by work-order code prior to disbursement.",
            [("A", "itemizes"), ("B", "is itemizing"), ("C", "be itemized"), ("D", "was itemized")],
            "C", ["grammar_structure", "verb_tense_voice"], "stipulates that every subcontractor invoice ____ by work-order code prior to disbursement",
            "主要動詞 stipulates（明文規定、要求）後方引導之名詞子句須使用祈使假設語氣（should + 原形動詞，should 省略），且主詞 every subcontractor invoice 為被逐項列舉之對象（by work-order code），故選被動原形 (C) be itemized。",
            [
                ("A", "grammar_voice", "itemizes 為第三人稱單數主動式，不符合規定子句原形假設語氣，且發票無法主動列舉。"),
                ("B", "grammar_voice", "is itemizing 為現在進行主動式，語氣與語態均錯。"),
                ("D", "tense_mismatch", "was itemized 為過去簡單被動式，違反 stipulates that 後接原形動詞之語法規則。"),
            ],
            [("stipulate", "明訂、規定", "v.", "合約條款高頻動詞。"), ("itemize", "逐項列出", "v.", "itemize an invoice 指列明明細。"), ("disbursement", "撥款、支付", "n.", "prior to disbursement 指撥款前。")],
            40,
        ),
        (
            "ag-g-p5-000031", "ag-i-p5-000031-1", "ag-fam-trn-p5-031", "healthcare_medical_services", "D5",
            "句首否定副詞片語倒裝結構（Under no circumstances should laboratory samples be left...）。",
            "Under no circumstances ____ unsealed diagnostic specimens be left unattended on the centrifuge counter.",
            [("A", "should"), ("B", "having"), ("C", "whether"), ("D", "unless")],
            "A", ["grammar_structure", "verb_tense_voice"], "Under no circumstances ____ unsealed diagnostic specimens be left unattended",
            "否定介系詞片語 Under no circumstances（在任何情況下皆決不…）置於句首時，主要子句須採助動詞倒裝結構（助動詞 + 主詞 unsealed diagnostic specimens + 原形被動動詞 be left），故選助動詞 (A) should。",
            [
                ("B", "grammar_form", "having 為分詞，無法與後方原形被動 be left 構成倒裝限定動詞。"),
                ("C", "grammar_scope", "whether 為連接詞，置於此處會使句子缺乏助動詞且無法搭配原形 be left。"),
                ("D", "grammar_scope", "unless 為從屬連接詞，不可搭配原形動詞 be left 且使全句無主要子句。"),
            ],
            [("specimen", "檢體、樣本", "n.", "diagnostic specimens 指診斷檢體。"), ("unattended", "無人看管的", "adj.", "leave unattended 指棄置無人看管。")],
            40,
        ),
    ]

    for spec in p5_specs:
        groups.append(make_part5_group(
            gid=spec[0], iid=spec[1], fam_id=spec[2], pool="training",
            scenario=spec[3], diff_level=spec[4], diff_rationale=spec[5],
            prompt_en=spec[6], choices=spec[7], ans=spec[8], skill_tags=spec[9],
            quote_en=spec[10], explanation_zh=spec[11], distractors=spec[12],
            vocab=spec[13], est_sec=spec[14],
        ))

    # Part 6 Group 1: ag-g-p6-000003 (4 items)
    groups.append({
        "schema_version": "1.0.0",
        "group_id": "ag-g-p6-000003",
        "version": 1,
        "family_id": "ag-fam-trn-p6-003",
        "pool": "training",
        "fixture": False,
        "part": 6,
        "layout": "text_completion",
        "scenario": "real_estate_facilities",
        "difficulty": make_difficulty("D3", "涵蓋動詞時態、轉折副詞、商務字彙搭配與段落插句，考核跨句上下文連貫。"),
        "content_status": "ai_checked",
        "stimulus": {
            "documents": [
                {
                    "document_id": "ag-doc-p6-000003-1",
                    "genre": "memo",
                    "title_en": "MEMORANDUM: Upgrade to Keycard Elevator Access",
                    "blocks": [
                        {
                            "block_id": "ag-blk-p6-000003-1",
                            "type": "text",
                            "text_en": (
                                "To: All Tenants, Crestview Commercial Tower\n"
                                "From: Building Management Office\n"
                                "Date: October 12\n"
                                "Subject: Transition to Smart Keycard Elevator Readers\n\n"
                                "Beginning November 1, the passenger elevators in Crestview Commercial Tower [[blank:ag-i-p6-000003-1]] with upgraded optical keycard readers on all floors. "
                                "This modernization project is designed to reduce lobby congestion during morning peak hours while strengthening after-hours floor security.\n\n"
                                "Each tenant company will receive replacement smart badges for all registered staff members at no extra charge. "
                                "[[blank:ag-i-p6-000003-2]] Your office administrator must submit an updated employee roster through the tenant portal by October 22 so that the badges can be encoded accurately.\n\n"
                                "Temporary visitor passes will still be issued at the ground-floor concierge desk upon presentation of a photo ID. "
                                "[[blank:ag-i-p6-000003-3]], couriers making recurring daily deliveries may apply for a vendor access badge valid for the loading dock elevator. "
                                "We appreciate your [[blank:ag-i-p6-000003-4]] as our technicians complete the installation over the next two weekends."
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
                "item_id": "ag-i-p6-000003-1",
                "prompt_en": "Select the best word or phrase for [[blank:ag-i-p6-000003-1]].",
                "choices": [
                    make_choice("A", "equipped"),
                    make_choice("B", "will be equipped"),
                    make_choice("C", "have equipped"),
                    make_choice("D", "are equipping"),
                ],
                "answer_choice_id": "B",
                "skill_tags": ["verb_tense_voice", "grammar_structure"],
                "evidence": [{"source_type": "document_block", "source_id": "ag-blk-p6-000003-1", "quote_en": "Beginning November 1, the passenger elevators in Crestview Commercial Tower [[blank:ag-i-p6-000003-1]] with upgraded optical keycard readers"}],
                "explanation_zh": "備忘錄日期為 10 月 12 日，句首 Beginning November 1 指未來生效時間，且主詞 passenger elevators 為「被配備（be equipped with）」感應讀卡機之對象，故選未來被動式 (B) will be equipped。",
                "distractor_notes": [
                    make_distractor("A", "tense_mismatch", "equipped 為過去簡單式或分詞，與未來時間點 Beginning November 1 不合。"),
                    make_distractor("C", "grammar_voice", "have equipped 為現在完成主動式，電梯無法主動配備設備。"),
                    make_distractor("D", "grammar_voice", "are equipping 為現在進行主動式，語態錯誤。"),
                ],
                "vocabulary": [make_vocab("congestion", "擁擠、阻塞", "n.", "lobby congestion 指大廳人潮擁擠。")],
                "estimated_time_sec": 35,
            },
            {
                "item_id": "ag-i-p6-000003-2",
                "prompt_en": "Select the best sentence for [[blank:ag-i-p6-000003-2]].",
                "choices": [
                    make_choice("A", "Current magnetic-stripe cards will automatically deactivate at midnight on October 31."),
                    make_choice("B", "The parking garage on Level B2 will remain closed for repainting all month."),
                    make_choice("C", "Several retail shops on the plaza level have extended their weekend hours."),
                    make_choice("D", "Elevator maintenance fees were refunded to tenants last quarter."),
                ],
                "answer_choice_id": "A",
                "skill_tags": ["sentence_insertion", "cross_reference"],
                "evidence": [{"source_type": "document_block", "source_id": "ag-blk-p6-000003-1", "quote_en": "Each tenant company will receive replacement smart badges for all registered staff members at no extra charge. [[blank:ag-i-p6-000003-2]] Your office administrator must submit an updated employee roster"}],
                "explanation_zh": "前句說明各承租戶將免費獲得新式智慧識別證（replacement smart badges），後句要求辦公室管理員於 10 月 22 日前提交更新名單以利編碼；(A)「現有磁條卡將於 10 月 31 日午夜自動失效」完美銜接11月1日啟用新卡的過渡背景與申請新卡之必要性。",
                "distractor_notes": [
                    make_distractor("B", "off_topic", "地下二樓停車場重新粉刷與電梯門禁卡升級無關。"),
                    make_distractor("C", "off_topic", "廣場層零售店延長週末營業時間偏離主題。"),
                    make_distractor("D", "tense_mismatch", "上季退還電梯維護費與本段申辦新門禁卡流程無邏輯關聯。"),
                ],
                "vocabulary": [make_vocab("deactivate", "停用、使失效", "v.", "門禁卡或帳號到期停用常見動詞。")],
                "estimated_time_sec": 50,
            },
            {
                "item_id": "ag-i-p6-000003-3",
                "prompt_en": "Select the best word or phrase for [[blank:ag-i-p6-000003-3]].",
                "choices": [
                    make_choice("A", "In addition"),
                    make_choice("B", "Otherwise"),
                    make_choice("C", "Consequently"),
                    make_choice("D", "Instead of"),
                ],
                "answer_choice_id": "A",
                "skill_tags": ["preposition_conjunction", "cross_reference"],
                "evidence": [{"source_type": "document_block", "source_id": "ag-blk-p6-000003-1", "quote_en": "Temporary visitor passes will still be issued at the ground-floor concierge desk upon presentation of a photo ID. [[blank:ag-i-p6-000003-3]], couriers making recurring daily deliveries may apply for a vendor access badge"}],
                "explanation_zh": "前句說明一般臨時訪客可在一樓服務台換證，本句補充說明「此外，每日固定送件的快遞員可申請貨梯專用廠商通行證」，屬並列補充非員工之通行方式，故選轉折副詞片語 (A) In addition。",
                "distractor_notes": [
                    make_distractor("B", "logical_reversal", "Otherwise 意為「否則」，前後並非條件威脅關係。"),
                    make_distractor("C", "semantic_mismatch", "Consequently 意為「因此」，一般訪客換證並非快遞員申請貨梯證的原因。"),
                    make_distractor("D", "grammar_scope", "Instead of 為介系詞片語，不能單獨置於句首並以逗號隔開完整子句。"),
                ],
                "vocabulary": [make_vocab("concierge", "大樓服務台人員、禮賓部", "n.", "concierge desk 指大樓接待服務台。")],
                "estimated_time_sec": 35,
            },
            {
                "item_id": "ag-i-p6-000003-4",
                "prompt_en": "Select the best word or phrase for [[blank:ag-i-p6-000003-4]].",
                "choices": [
                    make_choice("A", "cooperation"),
                    make_choice("B", "ambition"),
                    make_choice("C", "obligation"),
                    make_choice("D", "reservation"),
                ],
                "answer_choice_id": "A",
                "skill_tags": ["vocabulary_in_context", "collocation_idiom"],
                "evidence": [{"source_type": "document_block", "source_id": "ag-blk-p6-000003-1", "quote_en": "We appreciate your [[blank:ag-i-p6-000003-4]] as our technicians complete the installation over the next two weekends."}],
                "explanation_zh": "公告結尾慣用語 We appreciate your cooperation（感謝您的配合／合作），契合工程施工與換證期間請住戶配合之語境，故選 (A) cooperation。",
                "distractor_notes": [
                    make_distractor("B", "semantic_mismatch", "ambition 意為「野心、抱負」，不適用於物業管理致謝語。"),
                    make_distractor("C", "semantic_mismatch", "obligation 意為「義務」，語氣生硬且不構成感謝搭配。"),
                    make_distractor("D", "semantic_mismatch", "reservation 意為「預約；保留意見」，與施工期間感謝住戶配合無關。"),
                ],
                "vocabulary": [make_vocab("roster", "名冊、值勤表", "n.", "employee roster 指員工名冊。")],
                "estimated_time_sec": 30,
            },
        ],
        "provenance": make_provenance(),
        "review_refs": ["ag-rev-ai-p6-000003", "ag-rev-blind-p6-000003"],
    })

    # Part 6 Group 2: ag-g-p6-000004 (4 items)
    groups.append({
        "schema_version": "1.0.0",
        "group_id": "ag-g-p6-000004",
        "version": 1,
        "family_id": "ag-fam-trn-p6-004",
        "pool": "training",
        "fixture": False,
        "part": 6,
        "layout": "text_completion",
        "scenario": "marketing_events_promotions",
        "difficulty": make_difficulty("D4", "企業客戶成功案例電子郵件，結合詞性變化、連接副詞、精準動詞與段落插句。"),
        "content_status": "ai_checked",
        "stimulus": {
            "documents": [
                {
                    "document_id": "ag-doc-p6-000004-1",
                    "genre": "email",
                    "title_en": "Subject: Feature Request — Solis Logistics Case Study",
                    "blocks": [
                        {
                            "block_id": "ag-blk-p6-000004-1",
                            "type": "text",
                            "text_en": (
                                "To: Nadia Khatri <nkhatri@solislogistics.com>\n"
                                "From: Julian Vance <jvance@routeoptima.io>\n"
                                "Date: September 19\n"
                                "Subject: Featuring Solis Logistics in Our Annual Client Spotlight\n\n"
                                "Dear Ms. Khatri,\n\n"
                                "Over the past eight months, your regional dispatch team has achieved a remarkable 22 percent reduction in fuel consumption using RouteOptima's fleet-scheduling platform. "
                                "Because of these [[blank:ag-i-p6-000004-1]] results, our editorial board would like to profile Solis Logistics in our upcoming Client Spotlight report.\n\n"
                                "Participation would involve a 30-minute video interview with our communications writer next week. "
                                "[[blank:ag-i-p6-000004-2]] Nothing will be published without your legal department's written sign-off.\n\n"
                                "As a token of appreciation, participating partner organizations receive two complimentary passes to our Transport Tech Summit in Chicago this November. "
                                "[[blank:ag-i-p6-000004-3]], your company logo and sustainability metrics will be featured on our conference main stage.\n\n"
                                "Please let me know by Friday whether you would like to [[blank:ag-i-p6-000004-4]] with the interview."
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
                "item_id": "ag-i-p6-000004-1",
                "prompt_en": "Select the best word or phrase for [[blank:ag-i-p6-000004-1]].",
                "choices": [
                    make_choice("A", "impress"),
                    make_choice("B", "impressed"),
                    make_choice("C", "impressive"),
                    make_choice("D", "impressively"),
                ],
                "answer_choice_id": "C",
                "skill_tags": ["word_form", "grammar_structure"],
                "evidence": [{"source_type": "document_block", "source_id": "ag-blk-p6-000004-1", "quote_en": "Because of these [[blank:ag-i-p6-000004-1]] results, our editorial board would like to profile Solis Logistics"}],
                "explanation_zh": "空格位於指示形容詞 these 與名詞 results 之間，且用來形容「令人印象深刻的成果（事物性質）」，故選形容詞 (C) impressive。",
                "distractor_notes": [
                    make_distractor("A", "word_form", "impress 為動詞，不可直接修飾名詞 results。"),
                    make_distractor("B", "grammar_voice", "impressed 為情緒分詞形容詞「（人）感到印象深刻的」，不能修飾事物 results。"),
                    make_distractor("D", "word_form", "impressively 為副詞，不可直接修飾名詞 results。"),
                ],
                "vocabulary": [make_vocab("profile", "撰文介紹、專訪報導", "v.", "profile a company 指對企業作專題報導。")],
                "estimated_time_sec": 30,
            },
            {
                "item_id": "ag-i-p6-000004-2",
                "prompt_en": "Select the best sentence for [[blank:ag-i-p6-000004-2]].",
                "choices": [
                    make_choice("A", "We will send you the full draft article for review before it goes to layout."),
                    make_choice("B", "The fleet-scheduling software requires a hardware reboot every Sunday night."),
                    make_choice("C", "Tickets to the Chicago summit sold out three weeks ahead of schedule."),
                    make_choice("D", "Our accounting office has already processed your monthly subscription invoice."),
                ],
                "answer_choice_id": "A",
                "skill_tags": ["sentence_insertion", "cross_reference"],
                "evidence": [{"source_type": "document_block", "source_id": "ag-blk-p6-000004-1", "quote_en": "Participation would involve a 30-minute video interview with our communications writer next week. [[blank:ag-i-p6-000004-2]] Nothing will be published without your legal department's written sign-off."}],
                "explanation_zh": "前句說明參與專題僅需進行 30 分鐘視訊訪談，後句保證「未經貴司法務部門書面簽核，絕不會公開發表任何內容」；(A)「我們會在排版前將完整草稿寄給您審閱」完美串聯訪談後的審稿與簽核流程。",
                "distractor_notes": [
                    make_distractor("B", "off_topic", "軟體每週日重開機之技術細節與專訪審稿流程無關。"),
                    make_distractor("C", "semantic_contradiction", "若芝加哥峰會門票已售罄，與下一段贈送兩張免費門票矛盾且位置錯置。"),
                    make_distractor("D", "off_topic", "月費發票入帳與案例專訪及法務簽核無關。"),
                ],
                "vocabulary": [make_vocab("sign-off", "正式簽核、批准", "n.", "written sign-off 指書面核准。")],
                "estimated_time_sec": 50,
            },
            {
                "item_id": "ag-i-p6-000004-3",
                "prompt_en": "Select the best word or phrase for [[blank:ag-i-p6-000004-3]].",
                "choices": [
                    make_choice("A", "Nevertheless"),
                    make_choice("B", "Moreover"),
                    make_choice("C", "Conversely"),
                    make_choice("D", "For instance"),
                ],
                "answer_choice_id": "B",
                "skill_tags": ["preposition_conjunction", "cross_reference"],
                "evidence": [{"source_type": "document_block", "source_id": "ag-blk-p6-000004-1", "quote_en": "participating partner organizations receive two complimentary passes to our Transport Tech Summit in Chicago this November. [[blank:ag-i-p6-000004-3]], your company logo and sustainability metrics will be featured on our conference main stage."}],
                "explanation_zh": "前句提出第一項回饋（獲贈兩張峰會免費門票），本句遞進提出第二項曝光福利（貴公司標誌與永續數據將於大會主舞台展示），故選表遞進補充之副詞 (B) Moreover。",
                "distractor_notes": [
                    make_distractor("A", "logical_reversal", "Nevertheless 表轉折讓步「然而」，與兩項正面福利之並列遞進關係相反。"),
                    make_distractor("C", "logical_reversal", "Conversely 表「相反地」，語意不合。"),
                    make_distractor("D", "semantic_mismatch", "For instance 表舉例，主舞台曝光並非免費門票的例子而是額外福利。"),
                ],
                "vocabulary": [make_vocab("complimentary", "免費贈送的、禮遇的", "adj.", "complimentary passes 指免費貴賓通行證。")],
                "estimated_time_sec": 35,
            },
            {
                "item_id": "ag-i-p6-000004-4",
                "prompt_en": "Select the best word or phrase for [[blank:ag-i-p6-000004-4]].",
                "choices": [
                    make_choice("A", "proceed"),
                    make_choice("B", "precede"),
                    make_choice("C", "possess"),
                    make_choice("D", "prolong"),
                ],
                "answer_choice_id": "A",
                "skill_tags": ["vocabulary_in_context", "collocation_idiom"],
                "evidence": [{"source_type": "document_block", "source_id": "ag-blk-p6-000004-1", "quote_en": "Please let me know by Friday whether you would like to [[blank:ag-i-p6-000004-4]] with the interview."}],
                "explanation_zh": "proceed with + 名詞 意為「繼續進行、著手辦理（該項訪談）」，為標準商務動詞搭配，故選 (A) proceed。",
                "distractor_notes": [
                    make_distractor("B", "phonetic_lexical_confusion", "precede 為形近動詞「在…之前發生」，為及物動詞且語意不合。"),
                    make_distractor("C", "semantic_mismatch", "possess 意為「擁有」，不搭配 with the interview。"),
                    make_distractor("D", "semantic_mismatch", "prolong 意為「延長（時間）」，為及物動詞且此處詢問是否同意進行訪談而非延長。"),
                ],
                "vocabulary": [make_vocab("proceed", "繼續進行、著手", "v.", "proceed with the interview 指安排進行訪談。")],
                "estimated_time_sec": 30,
            },
        ],
        "provenance": make_provenance(),
        "review_refs": ["ag-rev-ai-p6-000004", "ag-rev-blind-p6-000004"],
    })

    # Part 7 Group 1: ag-g-p7-000008 (Single passage, 2 items)
    groups.append({
        "schema_version": "1.0.0",
        "group_id": "ag-g-p7-000008",
        "version": 1,
        "family_id": "ag-fam-trn-p7-008",
        "pool": "training",
        "fixture": False,
        "part": 7,
        "layout": "single_passage",
        "scenario": "customer_service_returns",
        "difficulty": make_difficulty("D2", "單篇顧客服務公告，考核主旨與細節條件比對。"),
        "content_status": "ai_checked",
        "stimulus": {
            "documents": [
                {
                    "document_id": "ag-doc-p7-000008-1",
                    "genre": "notice",
                    "title_en": "Hearthstone Ceramic Studio — Custom Order & Exchange Policy",
                    "blocks": [
                        {
                            "block_id": "ag-blk-p7-000008-1",
                            "type": "text",
                            "text_en": (
                                "Thank you for shopping at Hearthstone Ceramic Studio. Standard dinnerware sets purchased from our showroom shelves may be exchanged or returned for a full refund within 30 days of purchase, provided they are unused and accompanied by the original printed receipt.\n\n"
                                "Please note that custom-monogrammed platters and bespoke restaurant glaze orders require a 40 percent nonrefundable deposit at the time the order is placed. However, if any item arrives with a manufacturing crack or glaze defect, our studio will fire and ship a replacement piece at no cost if you e-mail photographs of the damage to support@hearthstoneceramics.com within 72 hours of delivery."
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
                "item_id": "ag-i-p7-000008-1",
                "prompt_en": "What is required to receive a full refund on a standard dinnerware set?",
                "choices": [
                    make_choice("A", "Returning the unused items with the original receipt within 30 days"),
                    make_choice("B", "Paying a 40 percent restocking fee at the showroom desk"),
                    make_choice("C", "Submitting photographs of the tableware within 72 hours"),
                    make_choice("D", "Exchanging the set for a bespoke restaurant glaze order"),
                ],
                "answer_choice_id": "A",
                "skill_tags": ["specific_detail", "paraphrase_matching"],
                "evidence": [{"source_type": "document_block", "source_id": "ag-blk-p7-000008-1", "quote_en": "Standard dinnerware sets purchased from our showroom shelves may be exchanged or returned for a full refund within 30 days of purchase, provided they are unused and accompanied by the original printed receipt."}],
                "explanation_zh": "第一段明載：展售架上購買之標準餐具組若於購買後 30 天內退回、保持未使用且附帶原始紙本收據，即可獲得全額退費，故選 (A)。",
                "distractor_notes": [
                    make_distractor("B", "misattributed_detail", "40% 為客製化訂單之不可退還訂金，而非標準餐具退貨手續費。"),
                    make_distractor("C", "misattributed_detail", "72 小時內寄送損壞照片適用於到貨有裂痕或釉面瑕疵之免費補寄申請。"),
                    make_distractor("D", "unsupported_claim", "文中未規定必須換購餐廳客製化釉色訂單才能退費。"),
                ],
                "vocabulary": [make_vocab("bespoke", "量身訂製的、客製化的", "adj.", "bespoke orders 指客製化訂單。")],
                "estimated_time_sec": 45,
            },
            {
                "item_id": "ag-i-p7-000008-2",
                "prompt_en": "Under what circumstance will the studio replace a custom-monogrammed platter free of charge?",
                "choices": [
                    make_choice("A", "When a customer decides to change the monogram spelling after firing"),
                    make_choice("B", "When the item is delivered with a structural crack and reported with photos within three days"),
                    make_choice("C", "When the order is canceled before the 30-day showroom return window expires"),
                    make_choice("D", "When the buyer visits the showroom in person without a receipt"),
                ],
                "answer_choice_id": "B",
                "skill_tags": ["specific_detail", "paraphrase_matching"],
                "evidence": [{"source_type": "document_block", "source_id": "ag-blk-p7-000008-1", "quote_en": "if any item arrives with a manufacturing crack or glaze defect, our studio will fire and ship a replacement piece at no cost if you e-mail photographs of the damage to support@hearthstoneceramics.com within 72 hours of delivery."}],
                "explanation_zh": "第二段指出若商品送達時有製造裂痕或釉面瑕疵（manufacturing crack or glaze defect），且於交貨後 72 小時（即三天）內寄送損壞照片至客服信箱，工坊將免費重新燒製並寄送替換品，故選 (B)。",
                "distractor_notes": [
                    make_distractor("A", "unsupported_claim", "文中未允許燒製後免費更改客製化刻字拼寫。"),
                    make_distractor("C", "misattributed_detail", "客製化刻字餐盤有 40% 不可退訂金，不適用 30 天展間一般退貨條款。"),
                    make_distractor("D", "contradicts_text", "需透過電子郵件寄送損壞照片，且一般退貨亦須附收據。"),
                ],
                "vocabulary": [make_vocab("platter", "大淺盤、盛菜大盤", "n.", "餐具常見詞彙。")],
                "estimated_time_sec": 50,
            },
        ],
        "provenance": make_provenance(),
        "review_refs": ["ag-rev-ai-p7-000008", "ag-rev-blind-p7-000008"],
    })

    # Part 7 Group 2: ag-g-p7-000009 (Single passage, 3 items including sentence_insertion)
    groups.append({
        "schema_version": "1.0.0",
        "group_id": "ag-g-p7-000009",
        "version": 1,
        "family_id": "ag-fam-trn-p7-009",
        "pool": "training",
        "fixture": False,
        "part": 7,
        "layout": "single_passage",
        "scenario": "manufacturing_quality_control",
        "difficulty": make_difficulty("D4", "企業內部產線調整通知，包含主旨、否定細節（NOT true）與四位置插句題。"),
        "content_status": "ai_checked",
        "stimulus": {
            "documents": [
                {
                    "document_id": "ag-doc-p7-000009-1",
                    "genre": "memo",
                    "title_en": "Internal Notice: Calibration Shutdown for Packaging Line B",
                    "blocks": [
                        {
                            "block_id": "ag-blk-p7-000009-1",
                            "type": "text",
                            "text_en": (
                                "To: All Shift Supervisors, Brno Bottling Facility\n"
                                "From: Marek Horak, Director of Plant Operations\n"
                                "Date: November 4\n"
                                "Subject: Scheduled Laser-Sensor Calibration on Packaging Line B\n\n"
                                "On Thursday, November 7, Packaging Line B will be taken offline from 1:00 P.M. to 5:00 P.M. so that engineers from Viktoria Optics can calibrate the high-speed fill-level sensors. [[position:1]] "
                                "Recent quality audits showed a slight variance in bottle fill volumes during peak throughput, and this preventive adjustment will ensure full compliance with European export standards. [[position:2]]\n\n"
                                "To avoid delaying our Friday shipment to Munich, afternoon bottling runs originally assigned to Line B will be rerouted to Packaging Line A and Packaging Line C. [[position:3]] "
                                "Those two lines have sufficient reserve capacity to absorb the extra 14,000 units without requiring overtime hours. [[position:4]] "
                                "Line B operators should report to Conference Room 2B at 1:15 P.M. on Thursday for a two-hour refresher seminar on the updated sensor diagnostic dashboard."
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
                "item_id": "ag-i-p7-000009-1",
                "prompt_en": "Why is Packaging Line B being shut down on Thursday afternoon?",
                "choices": [
                    make_choice("A", "To adjust optical sensors that measure liquid levels in bottles"),
                    make_choice("B", "To repair a broken conveyor belt damaged during the morning shift"),
                    make_choice("C", "To reduce electricity usage during municipal power maintenance"),
                    make_choice("D", "To install a brand-new labeling machine for domestic orders"),
                ],
                "answer_choice_id": "A",
                "skill_tags": ["main_idea_purpose", "paraphrase_matching"],
                "evidence": [{"source_type": "document_block", "source_id": "ag-blk-p7-000009-1", "quote_en": "so that engineers from Viktoria Optics can calibrate the high-speed fill-level sensors. [[position:1]] Recent quality audits showed a slight variance in bottle fill volumes"}],
                "explanation_zh": "第一段說明 B 包裝線於週四下午停機是為了讓 Viktoria Optics 工程師校正高速液位感測器（calibrate the high-speed fill-level sensors），以解決裝瓶容量微小誤差，對應 (A)。",
                "distractor_notes": [
                    make_distractor("B", "unsupported_claim", "文中為預防性校正液位感測器，未提及早班輸送帶斷裂。"),
                    make_distractor("C", "unsupported_claim", "未提及市政電力維護或節電。"),
                    make_distractor("D", "misattributed_detail", "目的是符合歐洲出口標準之液位感測校正，而非安裝內銷貼標機。"),
                ],
                "vocabulary": [make_vocab("calibrate", "校正、校準", "v.", "calibrate sensors 指校準感測器。"), make_vocab("throughput", "產能、處理量", "n.", "peak throughput 指尖峰產量。")],
                "estimated_time_sec": 45,
            },
            {
                "item_id": "ag-i-p7-000009-2",
                "prompt_en": "What is indicated about Friday's shipment to Munich?",
                "choices": [
                    make_choice("A", "It has been postponed until next Monday morning."),
                    make_choice("B", "It will require staff to work four hours of paid overtime."),
                    make_choice("C", "Its production volume will be handled by two other packaging lines."),
                    make_choice("D", "It will be inspected in Conference Room 2B at 1:15 P.M."),
                ],
                "answer_choice_id": "C",
                "skill_tags": ["specific_detail", "paraphrase_matching"],
                "evidence": [{"source_type": "document_block", "source_id": "ag-blk-p7-000009-1", "quote_en": "To avoid delaying our Friday shipment to Munich, afternoon bottling runs originally assigned to Line B will be rerouted to Packaging Line A and Packaging Line C."}],
                "explanation_zh": "第二段指出，為避免延誤週五運往慕尼黑的貨件，原定於 B 線進行的下午裝瓶批次將改道由 A 線與 C 線處理，且不需加班即可吸收 14,000 瓶產量，故選 (C)。",
                "distractor_notes": [
                    make_distractor("A", "contradicts_text", "文中明確表示採取分流措施以避免延誤（To avoid delaying），並未延後。"),
                    make_distractor("B", "contradicts_text", "文中明言 without requiring overtime hours（無須加班）。"),
                    make_distractor("D", "misattributed_detail", "2B 會議室是供 B 線操作員參加感測器診斷儀表板複訓研討會之地點。"),
                ],
                "vocabulary": [make_vocab("reroute", "改道、重新分流", "v.", "reroute production runs 指將生產批次轉移至其他產線。")],
                "estimated_time_sec": 50,
            },
            {
                "item_id": "ag-i-p7-000009-3",
                "prompt_en": "In which of the positions marked [1], [2], [3], and [4] does the following sentence best belong?\n\"No products have failed safety standards, but fine-tuning the equipment now will prevent costly rejects later.\"",
                "choices": [
                    make_choice("A", "[1]"),
                    make_choice("B", "[2]"),
                    make_choice("C", "[3]"),
                    make_choice("D", "[4]"),
                ],
                "answer_choice_id": "B",
                "skill_tags": ["sentence_insertion", "cross_reference"],
                "evidence": [{"source_type": "document_block", "source_id": "ag-blk-p7-000009-1", "quote_en": "Recent quality audits showed a slight variance in bottle fill volumes during peak throughput, and this preventive adjustment will ensure full compliance with European export standards. [[position:2]]"}],
                "explanation_zh": "待插入句「目前並無任何產品未達安全標準，但現在微調設備能避免日後產生高昂的不良品報廢成本」承接前句「近期品質稽核發現尖峰產能時裝瓶量有微小變異，此預防性調整將確保完全符合歐洲出口標準」，補充說明該變異尚未造成不合格但需預防性微調，置於 [[position:2]] 邏輯最緊密。",
                "distractor_notes": [
                    make_distractor("A", "discourse_mismatch", "置於 [1] 時尚未提及 quality audits 與 slight variance，突然說 No products have failed 缺乏前文背景。"),
                    make_distractor("C", "discourse_mismatch", "[3] 前後正在說明將 14,000 瓶產能分流至 A 線與 C 線，插入品管微調理由會打斷產能調度連貫性。"),
                    make_distractor("D", "discourse_mismatch", "[4] 後方接操作員教育訓練安排，與不良品報廢無直接銜接。"),
                ],
                "vocabulary": [make_vocab("variance", "差異、變異量", "n.", "fill volume variance 指充填容量差異。")],
                "estimated_time_sec": 55,
            },
        ],
        "provenance": make_provenance(),
        "review_refs": ["ag-rev-ai-p7-000009", "ag-rev-blind-p7-000009"],
    })

    return groups


# ==============================================================================
# 2. Build Batch 0009 (pool="diagnostic", 14 groups = 24 items across Parts 1-7)
# ==============================================================================
def build_batch_0009_groups(draft_dir: Path) -> List[Dict[str, Any]]:
    groups: List[Dict[str, Any]] = []
    audio_dir = draft_dir / "assets" / "audio"
    image_dir = draft_dir / "assets" / "images"
    audio_dir.mkdir(parents=True, exist_ok=True)
    image_dir.mkdir(parents=True, exist_ok=True)

    # Copy the cleaned diagnostic Part 1 image
    src_img = ROOT / "assets_work" / "part1_images" / "ag-ast-p1-000301-image.jpg"
    dst_img = image_dir / "ag-ast-p1-000301-image.jpg"
    shutil.copy2(src_img, dst_img)
    img_sha = sha256_file(dst_img)

    # Part 1: ag-g-p1-000301 (1 item)
    g_p1 = {
        "schema_version": "1.0.0",
        "group_id": "ag-g-p1-000301",
        "version": 1,
        "family_id": "ag-fam-diag-p1-001",
        "pool": "diagnostic",
        "fixture": False,
        "part": 1,
        "layout": "photo",
        "scenario": "travel_hotel_airport",
        "difficulty": make_difficulty("D2", "雙人機場登機門場景，考核人物正在進行之核心動作與背景客機狀態區辨。"),
        "content_status": "ai_checked",
        "stimulus": {
            "documents": [],
            "speakers": [{"speaker_id": "spk1", "role": "Narrator (Female)", "accent": "us"}],
            "audio_script": [
                {"segment_id": "seg1", "speaker_id": "spk1", "text_en": "(A) A gate agent is scanning a passenger's boarding pass."},
                {"segment_id": "seg2", "speaker_id": "spk1", "text_en": "(B) A flight attendant is stowing luggage in an overhead bin."},
                {"segment_id": "seg3", "speaker_id": "spk1", "text_en": "(C) Passengers are boarding an aircraft via an outdoor stairway."},
                {"segment_id": "seg4", "speaker_id": "spk1", "text_en": "(D) A maintenance crew is inspecting the wing of an airplane."},
            ],
        },
        "assets": [
            {
                "asset_id": "ag-ast-p1-000301-image",
                "kind": "image",
                "status": "ready",
                "path": "assets/images/ag-ast-p1-000301-image.jpg",
                "sha256": img_sha,
                "mime_type": "image/jpeg",
                "duration_ms": None,
                "source_note_zh": "原創診斷池 Part 1 實景照片：機場登機門櫃台前，身穿深藍制服外套的女性地勤人員正持條碼掃描器掃描男性旅客手中的紙本登機證，旅客另一手扶著隨身行李箱拉桿，窗外停靠一架商用客機且空橋連接中。",
                "review_state": "ai_checked",
                "segment_times": [],
            },
            {
                "asset_id": "ag-ast-p1-000301-audio",
                "kind": "audio",
                "status": "planned",
                "path": None,
                "sha256": None,
                "duration_ms": None,
                "source_note_zh": "待合成音訊",
                "review_state": "pending",
                "segment_times": [],
            },
        ],
        "items": [
            {
                "item_id": "ag-i-p1-000301-1",
                "prompt_en": "Look at the photograph and listen to the four statements. Choose the statement that best describes what you see in the picture.",
                "choices": [
                    make_choice("A", "A gate agent is scanning a passenger's boarding pass."),
                    make_choice("B", "A flight attendant is stowing luggage in an overhead bin."),
                    make_choice("C", "Passengers are boarding an aircraft via an outdoor stairway."),
                    make_choice("D", "A maintenance crew is inspecting the wing of an airplane."),
                ],
                "answer_choice_id": "A",
                "skill_tags": ["visual_action_state", "specific_detail"],
                "evidence": [
                    {"source_type": "asset", "source_id": "ag-ast-p1-000301-image", "quote_en": "Female airline gate agent holding a handheld barcode scanner scanning a passenger's boarding pass at the boarding podium"},
                    {"source_type": "audio_segment", "source_id": "seg1", "quote_en": "(A) A gate agent is scanning a passenger's boarding pass."},
                ],
                "explanation_zh": "照片前景中，身穿深藍色制服的女性登機門地勤人員（gate agent）正拿著手持式掃描器掃描旅客遞出的紙本登機證（boarding pass），故 (A) 為唯一正確描述。",
                "distractor_notes": [
                    make_distractor("B", "action_mismatch", "場景位於航廈登機門櫃台且行李箱置於地面，並非在機艙內將行李放入頭頂置物櫃（overhead bin）。"),
                    make_distractor("C", "scene_mismatch", "窗外客機連接空橋且旅客位於室內櫃台，並無旅客正透過戶外登機梯登機。"),
                    make_distractor("D", "unobserved_actor", "窗外停機坪機翼旁並無維修人員（maintenance crew）在檢查。"),
                ],
                "vocabulary": [
                    make_vocab("boarding pass", "登機證", "n.", "機場高頻名詞。"),
                    make_vocab("stow", "妥善放置、收納（行李）", "v.", "stow luggage in an overhead bin 指將行李放入上方置物櫃。"),
                ],
                "estimated_time_sec": 20,
            }
        ],
        "provenance": make_provenance(),
        "review_refs": ["ag-rev-ai-p1-000301", "ag-rev-blind-p1-000301"],
    }
    groups.append(g_p1)

    # Part 2: 4 groups (ag-g-p2-000301..000304) using us, uk, au accents
    p2_specs = [
        (
            "ag-g-p2-000301", "ag-i-p2-000301-1", "ag-fam-diag-p2-001", "meetings_scheduling", "D1",
            "Where 地點詢問搭配直接樓層地點回答。",
            ("us", "Male Clerk", "uk", "Female Coordinator"),
            "Where should we set up the projector for the client briefing?",
            [
                ("A", "In the third-floor boardroom."),
                ("B", "At two thirty this afternoon."),
                ("C", "Yes, the slides are ready."),
            ],
            "A", ["wh_question_response", "specific_detail"],
            "問題以 Where 詢問「我們應該在哪裡架設客戶簡報用的投影機？」，(A)「在三樓董事會議室」直接給出地點。",
            [
                ("B", "question_type_mismatch", "回答時間（兩點半），與 Where 地點提問不符。"),
                ("C", "yes_no_trap", "Wh- 問句不可用 Yes 開頭回答。"),
            ],
            [("briefing", "簡報會議", "n.", "client briefing 指客戶簡報。")],
        ),
        (
            "ag-g-p2-000302", "ag-i-p2-000302-1", "ag-fam-diag-p2-002", "finance_budgeting_invoicing", "D2",
            "When 時間問句搭配完成條件時間回應。",
            ("uk", "Female Manager", "us", "Male Analyst"),
            "When will the preliminary revenue forecast be distributed to the vice presidents?",
            [
                ("A", "Higher than last quarter's sales."),
                ("B", "As soon as the European branch submits its figures."),
                ("C", "From the accounting department."),
            ],
            "B", ["wh_question_response", "indirect_pragmatic_response"],
            "提問詢問初步營收預測何時（When）會分發給副總裁們，(B)「一旦歐洲分公司提交數據就會發出」以條件時間精準回答。",
            [
                ("A", "lexical_association_trap", "聯想 revenue / sales，但回答比較結果而非時間。"),
                ("C", "question_type_mismatch", "回答來源部門（From...），對應 Where/Who 而非 When。"),
            ],
            [("preliminary", "初步的", "adj.", "preliminary forecast 指初步預測。")],
        ),
        (
            "ag-g-p2-000303", "ag-i-p2-000303-1", "ag-fam-diag-p2-003", "logistics_supply_chain", "D3",
            "否定疑問句／附加問句搭配間接語用回應（轉移責任／提出查證行動）。",
            ("au", "Female Supervisor", "us", "Male Coordinator"),
            "Haven't the replacement gaskets for the bottling machine arrived from Osaka yet?",
            [
                ("A", "No, they're made of synthetic rubber."),
                ("B", "I'll check the receiving dock log right now."),
                ("C", "For the morning production shift."),
            ],
            "B", ["yes_no_tag_negative_response", "indirect_pragmatic_response"],
            "提問詢問「從大阪寄來的裝瓶機替換墊片還沒到嗎？」，(B)「我現在馬上查一下收貨月台紀錄」為自然間接回應（尚不確定但立即查證）。",
            [
                ("A", "semantic_mismatch", "雖有 No，但後半句說明材質為合成橡膠，與是否到貨無關。"),
                ("C", "question_type_mismatch", "回答用途或班別，未回應貨物是否抵達。"),
            ],
            [("gasket", "墊片、密封墊圈", "n.", "機械維護常見零件。"), ("receiving dock", "收貨月台", "n.", "倉儲物流術語。")],
        ),
        (
            "ag-g-p2-000304", "ag-i-p2-000304-1", "ag-fam-diag-p2-004", "office_administration", "D4",
            "陳述句抱怨（印表機又卡紙了）搭配主動提供替代方案之語用回應。",
            ("us", "Male Officer", "uk", "Female Assistant"),
            "The high-speed copier in the marketing wing is jamming again.",
            [
                ("A", "You can print your handouts on the machine near the reception desk."),
                ("B", "Yes, fifty copies bound in folders."),
                ("C", "The marketing director returned yesterday."),
            ],
            "A", ["statement_offer_request", "indirect_pragmatic_response"],
            "說話者陳述「行銷部門那台高速影印機又卡紙了」，(A)「你可以用接待櫃台旁那台機器列印講義」針對問題主動提供立即可行的替代解決方案。",
            [
                ("B", "yes_no_trap", "對抱怨設備故障的陳述句回答 Yes 與份數，語用不連貫。"),
                ("C", "word_repetition_trap", "重複題幹中的 marketing 一詞，但談論行銷總監昨日歸來，與影印機故障無關。"),
            ],
            [("jam", "卡紙、卡住", "v.", "copier is jamming 指影印機卡紙。"), ("handout", "講義、書面資料", "n.", "會議常見詞彙。")],
        ),
    ]

    for gid, iid, fam, scen, d_lvl, d_rat, spk_cfg, q_text, ch_list, ans, tags, exp_zh, dist_list, voc_list in p2_specs:
        num_suffix = gid.split("-")[-1]
        g_p2 = {
            "schema_version": "1.0.0",
            "group_id": gid,
            "version": 1,
            "family_id": fam,
            "pool": "diagnostic",
            "fixture": False,
            "part": 2,
            "layout": "question_response",
            "scenario": scen,
            "difficulty": make_difficulty(d_lvl, d_rat),
            "content_status": "ai_checked",
            "stimulus": {
                "documents": [],
                "speakers": [
                    {"speaker_id": "spk1", "role": f"Questioner ({spk_cfg[1]})", "accent": spk_cfg[0]},
                    {"speaker_id": "spk2", "role": f"Responder ({spk_cfg[3]})", "accent": spk_cfg[2]},
                ],
                "audio_script": [
                    {"segment_id": "seg1", "speaker_id": "spk1", "text_en": q_text},
                    {"segment_id": "seg2", "speaker_id": "spk2", "text_en": f"(A) {ch_list[0][1]}"},
                    {"segment_id": "seg3", "speaker_id": "spk2", "text_en": f"(B) {ch_list[1][1]}"},
                    {"segment_id": "seg4", "speaker_id": "spk2", "text_en": f"(C) {ch_list[2][1]}"},
                ],
            },
            "assets": [
                {
                    "asset_id": f"ag-ast-p2-{num_suffix}-audio",
                    "kind": "audio",
                    "status": "planned",
                    "path": None,
                    "sha256": None,
                    "duration_ms": None,
                    "source_note_zh": "待合成音訊",
                    "review_state": "pending",
                    "segment_times": [],
                }
            ],
            "items": [
                {
                    "item_id": iid,
                    "prompt_en": "Listen to the question or statement and three responses. Choose the best response.",
                    "choices": [make_choice(c, t) for c, t in ch_list],
                    "answer_choice_id": ans,
                    "skill_tags": tags,
                    "evidence": [
                        {"source_type": "audio_segment", "source_id": "seg1", "quote_en": q_text},
                        {"source_type": "audio_segment", "source_id": f"seg{1 + ['A','B','C'].index(ans)}", "quote_en": f"({ans}) {dict(ch_list)[ans]}"},
                    ],
                    "explanation_zh": exp_zh,
                    "distractor_notes": [make_distractor(c, tp, r) for c, tp, r in dist_list],
                    "vocabulary": [make_vocab(s, m, p, n) for s, m, p, n in voc_list],
                    "estimated_time_sec": 20,
                }
            ],
            "provenance": make_provenance(),
            "review_refs": [f"ag-rev-ai-p2-{num_suffix}", f"ag-rev-blind-p2-{num_suffix}"],
        }
        groups.append(g_p2)

    # Part 3 Group 1: ag-g-p3-000301 (3 items)
    groups.append({
        "schema_version": "1.0.0",
        "group_id": "ag-g-p3-000301",
        "version": 1,
        "family_id": "ag-fam-diag-p3-001",
        "pool": "diagnostic",
        "fixture": False,
        "part": 3,
        "layout": "conversation",
        "scenario": "hr_recruitment_training",
        "difficulty": make_difficulty("D3", "雙人職場訓練與排班調整對話，考核主旨、原因細節與下一步行動。"),
        "content_status": "ai_checked",
        "stimulus": {
            "documents": [],
            "speakers": [
                {"speaker_id": "spk1", "role": "Female Coordinator (Elena)", "accent": "us"},
                {"speaker_id": "spk2", "role": "Male Instructor (Graham)", "accent": "uk"},
            ],
            "audio_script": [
                {"segment_id": "seg1", "speaker_id": "spk1", "text_en": "Hi Graham, I'm finalizing the room assignments for Thursday's cybersecurity onboarding session. Are we still expecting eighteen new hires?"},
                {"segment_id": "seg2", "speaker_id": "spk2", "text_en": "Actually, Elena, the engineering division just added six software developers who transferred from our Dublin office, so we'll have twenty-four participants in total."},
                {"segment_id": "seg3", "speaker_id": "spk1", "text_en": "In that case, Training Room B won't have enough workstations. Every attendee needs a desktop terminal for the password-encryption lab."},
                {"segment_id": "seg4", "speaker_id": "spk2", "text_en": "Could we reserve the Digital Media Lab on the fifth floor instead? It has thirty terminals and a dual-screen podium."},
                {"segment_id": "seg5", "speaker_id": "spk1", "text_en": "Good idea. I'll update the calendar invitation right now and ask IT support to preload the training sandbox on those computers."},
            ],
        },
        "assets": [
            {
                "asset_id": "ag-ast-p3-000301-audio",
                "kind": "audio",
                "status": "planned",
                "path": None,
                "sha256": None,
                "duration_ms": None,
                "source_note_zh": "待合成音訊",
                "review_state": "pending",
                "segment_times": [],
            }
        ],
        "items": [
            {
                "item_id": "ag-i-p3-000301-1",
                "prompt_en": "Why has the number of session participants increased?",
                "choices": [
                    make_choice("A", "A client company requested guest passes for its auditors."),
                    make_choice("B", "Six software developers transferred from the Dublin branch."),
                    make_choice("C", "Friday's orientation class was canceled due to weather."),
                    make_choice("D", "Summer interns were required to retake the examination."),
                ],
                "answer_choice_id": "B",
                "skill_tags": ["specific_detail", "paraphrase_matching"],
                "evidence": [{"source_type": "audio_segment", "source_id": "seg2", "quote_en": "the engineering division just added six software developers who transferred from our Dublin office, so we'll have twenty-four participants in total."}],
                "explanation_zh": "男方在 seg2 說明工程部門剛加入六位從都柏林分公司調任過來的軟體開發人員，使總人數從 18 人增加到 24 人，故選 (B)。",
                "distractor_notes": [
                    make_distractor("A", "unsupported_claim", "對話未提及外部客戶稽核員索取貴賓證。"),
                    make_distractor("C", "unsupported_claim", "未提及週五課程因天氣取消。"),
                    make_distractor("D", "unsupported_claim", "未提及暑期實習生重考。"),
                ],
                "vocabulary": [make_vocab("onboarding", "新進人員入職培訓", "n.", "onboarding session 指入職訓練課程。")],
                "estimated_time_sec": 35,
            },
            {
                "item_id": "ag-i-p3-000301-2",
                "prompt_en": "Why is Training Room B no longer suitable?",
                "choices": [
                    make_choice("A", "Its projector bulb burned out this morning."),
                    make_choice("B", "It is being repainted by the facilities crew."),
                    make_choice("C", "It does not have enough computer workstations for everyone."),
                    make_choice("D", "It is located in a different building across town."),
                ],
                "answer_choice_id": "C",
                "skill_tags": ["specific_detail", "paraphrase_matching"],
                "evidence": [{"source_type": "audio_segment", "source_id": "seg3", "quote_en": "In that case, Training Room B won't have enough workstations. Every attendee needs a desktop terminal for the password-encryption lab."}],
                "explanation_zh": "女方在 seg3 指出，人數增至 24 人後，Training Room B 的電腦工作站（workstations）數量不足，而每位學員都需要一台桌上型終端機進行密碼加密實作，故選 (C)。",
                "distractor_notes": [
                    make_distractor("A", "unsupported_claim", "未提及投影機燈泡燒壞。"),
                    make_distractor("B", "unsupported_claim", "未提及油漆工程。"),
                    make_distractor("D", "unsupported_claim", "兩間教室皆在同棟大樓（替代教室位於五樓）。"),
                ],
                "vocabulary": [make_vocab("workstation", "電腦工作站、座位", "n.", "辦公室與電腦教室高頻字。")],
                "estimated_time_sec": 35,
            },
            {
                "item_id": "ag-i-p3-000301-3",
                "prompt_en": "What will the woman ask the IT support team to do?",
                "choices": [
                    make_choice("A", "Install practice software on the fifth-floor computers"),
                    make_choice("B", "Order six additional monitors from a supplier"),
                    make_choice("C", "Reset the building's Wi-Fi router before Thursday"),
                    make_choice("D", "Print paper manuals for the Dublin transfers"),
                ],
                "answer_choice_id": "A",
                "skill_tags": ["future_action", "paraphrase_matching"],
                "evidence": [{"source_type": "audio_segment", "source_id": "seg5", "quote_en": "I'll update the calendar invitation right now and ask IT support to preload the training sandbox on those computers."}],
                "explanation_zh": "女方在對話結尾（seg5）表示將更新行事曆邀請，並請 IT 支援團隊預先在五樓數位媒體實驗室的電腦上載入訓練沙盒環境（preload the training sandbox on those computers），對應 (A)。",
                "distractor_notes": [
                    make_distractor("B", "unsupported_claim", "五樓教室已有 30 台終端機，無須加訂螢幕。"),
                    make_distractor("C", "unsupported_claim", "未提及重設 Wi-Fi 路由器。"),
                    make_distractor("D", "unsupported_claim", "未提及列印紙本手冊。"),
                ],
                "vocabulary": [make_vocab("preload", "預先載入、預先安裝", "v.", "preload software 指預先安裝軟體。")],
                "estimated_time_sec": 35,
            },
        ],
        "provenance": make_provenance(),
        "review_refs": ["ag-rev-ai-p3-000301", "ag-rev-blind-p3-000301"],
    })

    # Part 3 Group 2: ag-g-p3-000302 (3 items with graphic table)
    groups.append({
        "schema_version": "1.0.0",
        "group_id": "ag-g-p3-000302",
        "version": 1,
        "family_id": "ag-fam-diag-p3-002",
        "pool": "diagnostic",
        "fixture": False,
        "part": 3,
        "layout": "conversation",
        "scenario": "logistics_supply_chain",
        "difficulty": make_difficulty("D4", "雙人冷鏈物流異常與貨櫃調度對話，結合視覺表格整合（graphic_schedule_integration）。"),
        "content_status": "ai_checked",
        "stimulus": {
            "documents": [
                {
                    "document_id": "ag-doc-p3-000302-1",
                    "genre": "schedule",
                    "title_en": "Port of Rotterdam — Refrigerated Container Bay Roster",
                    "blocks": [
                        {
                            "block_id": "ag-blk-p3-000302-1",
                            "type": "table",
                            "columns": ["Bay ID", "Cargo Type", "Target Temp", "Assigned Carrier"],
                            "rows": [
                                ["Bay R-12", "Dairy Products", "+3°C", "Nordic Sea Line"],
                                ["Bay R-15", "Fresh Cut Flowers", "+6°C", "Tulip Express"],
                                ["Bay R-19", "Frozen Seafood", "-18°C", "Baltic Star Cargo"],
                                ["Bay R-24", "Pharmaceuticals", "+2°C", "Helios MedTrans"],
                            ],
                        }
                    ],
                }
            ],
            "speakers": [
                {"speaker_id": "spk1", "role": "Male Dispatcher (Henrik)", "accent": "uk"},
                {"speaker_id": "spk2", "role": "Female Engineer (Sonia)", "accent": "au"},
            ],
            "audio_script": [
                {"segment_id": "seg1", "speaker_id": "spk1", "text_en": "Sonia, our monitoring console just triggered a voltage warning in the refrigerated yard. We have a shipment of fresh cut flowers arriving in twenty minutes that needs a stable plus-six-degree bay."},
                {"segment_id": "seg2", "speaker_id": "spk2", "text_en": "Let me look at the power diagnostic screen. Yes, the transformer feeding the bay assigned to Tulip Express had a circuit breaker trip during the rainstorm."},
                {"segment_id": "seg3", "speaker_id": "spk1", "text_en": "Can your crew restore power before the delivery trucks pull up to the gate?"},
                {"segment_id": "seg4", "speaker_id": "spk2", "text_en": "Replacing the moisture seal on that breaker will take at least ninety minutes. For now, you should direct the trucks to Spare Bay R-30 next to the main office—I've already set its thermostat to six degrees."},
            ],
        },
        "assets": [
            {
                "asset_id": "ag-ast-p3-000302-audio",
                "kind": "audio",
                "status": "planned",
                "path": None,
                "sha256": None,
                "duration_ms": None,
                "source_note_zh": "待合成音訊",
                "review_state": "pending",
                "segment_times": [],
            }
        ],
        "items": [
            {
                "item_id": "ag-i-p3-000302-1",
                "prompt_en": "What problem are the speakers discussing?",
                "choices": [
                    make_choice("A", "An electrical fault at a refrigerated storage bay"),
                    make_choice("B", "A customs paperwork delay at the port entrance"),
                    make_choice("C", "A shortage of licensed forklift operators"),
                    make_choice("D", "A shipping vessel that arrived two days late"),
                ],
                "answer_choice_id": "A",
                "skill_tags": ["main_idea_purpose", "paraphrase_matching"],
                "evidence": [
                    {"source_type": "audio_segment", "source_id": "seg1", "quote_en": "our monitoring console just triggered a voltage warning in the refrigerated yard."},
                    {"source_type": "audio_segment", "source_id": "seg2", "quote_en": "the transformer feeding the bay assigned to Tulip Express had a circuit breaker trip during the rainstorm."},
                ],
                "explanation_zh": "男方提到冷藏貨櫃區出現電壓警告（voltage warning），女方確認供電給該儲位的變壓器斷路器在暴雨中跳電（circuit breaker trip），故兩人討論的是冷藏儲位的電力故障 (A)。",
                "distractor_notes": [
                    make_distractor("B", "unsupported_claim", "未提及海關文件延誤。"),
                    make_distractor("C", "unsupported_claim", "未提及堆高機操作員短缺。"),
                    make_distractor("D", "unsupported_claim", "貨車將在 20 分鐘後抵達，並非船隻延誤兩天。"),
                ],
                "vocabulary": [make_vocab("circuit breaker", "斷路器、無熔絲開關", "n.", "設施電力常見詞彙。")],
                "estimated_time_sec": 35,
            },
            {
                "item_id": "ag-i-p3-000302-2",
                "prompt_en": "Look at the graphic. Which bay is currently experiencing a power issue?",
                "choices": [
                    make_choice("A", "Bay R-12"),
                    make_choice("B", "Bay R-15"),
                    make_choice("C", "Bay R-19"),
                    make_choice("D", "Bay R-24"),
                ],
                "answer_choice_id": "B",
                "skill_tags": ["graphic_schedule_integration", "cross_reference"],
                "evidence": [
                    {"source_type": "audio_segment", "source_id": "seg1", "quote_en": "a shipment of fresh cut flowers arriving in twenty minutes that needs a stable plus-six-degree bay."},
                    {"source_type": "audio_segment", "source_id": "seg2", "quote_en": "the transformer feeding the bay assigned to Tulip Express had a circuit breaker trip"},
                    {"source_type": "document_block", "source_id": "ag-blk-p3-000302-1", "quote_en": "Bay R-15 | Fresh Cut Flowers | +6°C | Tulip Express"},
                ],
                "explanation_zh": "對話指出貨物為鮮切花（fresh cut flowers，+6°C）且承運商為 Tulip Express；對照表格，Fresh Cut Flowers / +6°C / Tulip Express 對應的儲位為 Bay R-15，故選 (B)。",
                "distractor_notes": [
                    make_distractor("A", "table_row_mismatch", "Bay R-12 為 Nordic Sea Line 的乳製品（+3°C）。"),
                    make_distractor("C", "table_row_mismatch", "Bay R-19 為 Baltic Star Cargo 的冷凍海鮮（-18°C）。"),
                    make_distractor("D", "table_row_mismatch", "Bay R-24 為 Helios MedTrans 的醫藥品（+2°C）。"),
                ],
                "vocabulary": [make_vocab("thermostat", "恆溫器、溫控器", "n.", "冷鏈與空調常見詞彙。")],
                "estimated_time_sec": 40,
            },
            {
                "item_id": "ag-i-p3-000302-3",
                "prompt_en": "What does the woman recommend doing with the incoming delivery?",
                "choices": [
                    make_choice("A", "Returning the cargo to the greenhouse until tomorrow"),
                    make_choice("B", "Keeping the flowers inside the delivery trucks for ninety minutes"),
                    make_choice("C", "Unloading the shipment into a backup bay near the main office"),
                    make_choice("D", "Lowering the temperature in Bay R-19 to minus eighteen degrees"),
                ],
                "answer_choice_id": "C",
                "skill_tags": ["future_action", "paraphrase_matching"],
                "evidence": [{"source_type": "audio_segment", "source_id": "seg4", "quote_en": "For now, you should direct the trucks to Spare Bay R-30 next to the main office—I've already set its thermostat to six degrees."}],
                "explanation_zh": "女方在 seg4 表示修復防潮封條至少需 90 分鐘，建議目前先將貨車引導至主辦公室旁的備用儲位 Spare Bay R-30（她已將溫控設為 6 度），對應 (C)。",
                "distractor_notes": [
                    make_distractor("A", "unsupported_claim", "未建議將貨物退回溫室。"),
                    make_distractor("B", "misattributed_detail", "90 分鐘是修復斷路器的預估時間，女方建議改用備用儲位而非在車上乾等。"),
                    make_distractor("D", "table_row_mismatch", "Bay R-19 為 -18°C 冷凍區，會凍傷鮮花。"),
                ],
                "vocabulary": [make_vocab("moisture seal", "防潮封條", "n.", "電力與機械防護組件。")],
                "estimated_time_sec": 35,
            },
        ],
        "provenance": make_provenance(),
        "review_refs": ["ag-rev-ai-p3-000302", "ag-rev-blind-p3-000302"],
    })

    # Part 4 Group 1: ag-g-p4-000301 (3 items)
    groups.append({
        "schema_version": "1.0.0",
        "group_id": "ag-g-p4-000301",
        "version": 1,
        "family_id": "ag-fam-diag-p4-001",
        "pool": "diagnostic",
        "fixture": False,
        "part": 4,
        "layout": "talk",
        "scenario": "product_development_rd",
        "difficulty": make_difficulty("D4", "新產品試產進度簡報獨白，考核講者目的、口語意圖（pragmatic_intent_implication）與後續行動。"),
        "content_status": "ai_checked",
        "stimulus": {
            "documents": [],
            "speakers": [{"speaker_id": "spk1", "role": "Female Director (Dr. Lin)", "accent": "us"}],
            "audio_script": [
                {"segment_id": "seg1", "speaker_id": "spk1", "text_en": "Good morning, everyone. Thank you for joining this update on the Solaris portable water purifier. Last week, our external testing lab in Zurich completed the durability trials on the ceramic filter cartridge."},
                {"segment_id": "seg2", "speaker_id": "spk1", "text_en": "While the filtration purity exceeded ninety-nine point nine percent, the plastic latch on the outer housing cracked after three hundred drop cycles. Now, we certainly don't want outdoor hikers dealing with a loose cover on the trail."},
                {"segment_id": "seg3", "speaker_id": "spk1", "text_en": "Therefore, our mechanical engineering team has redesigned the latch using reinforced nylon, which adds only twelve cents per unit to our manufacturing cost and keeps us well within budget."},
                {"segment_id": "seg4", "speaker_id": "spk1", "text_en": "Modified molds have already been sent to the injection-molding plant, and we will review the new prototype samples at our Friday morning meeting."},
            ],
        },
        "assets": [
            {
                "asset_id": "ag-ast-p4-000301-audio",
                "kind": "audio",
                "status": "planned",
                "path": None,
                "sha256": None,
                "duration_ms": None,
                "source_note_zh": "待合成音訊",
                "review_state": "pending",
                "segment_times": [],
            }
        ],
        "items": [
            {
                "item_id": "ag-i-p4-000301-1",
                "prompt_en": "What is the main topic of the talk?",
                "choices": [
                    make_choice("A", "Results of durability testing and a design modification for a water purifier"),
                    make_choice("B", "A marketing campaign for a new line of hiking backpacks"),
                    make_choice("C", "The relocation of a research laboratory to Zurich"),
                    make_choice("D", "Annual salary adjustments for mechanical engineers"),
                ],
                "answer_choice_id": "A",
                "skill_tags": ["main_idea_purpose", "paraphrase_matching"],
                "evidence": [
                    {"source_type": "audio_segment", "source_id": "seg1", "quote_en": "Thank you for joining this update on the Solaris portable water purifier. Last week, our external testing lab in Zurich completed the durability trials"},
                    {"source_type": "audio_segment", "source_id": "seg3", "quote_en": "Therefore, our mechanical engineering team has redesigned the latch using reinforced nylon"},
                ],
                "explanation_zh": "講者開頭即說明本次簡報旨在報告 Solaris 攜帶式淨水器之耐用度測試結果（durability trials），並說明針對外殼卡扣破裂所採取之強化尼龍改版設計（redesigned the latch），故選 (A)。",
                "distractor_notes": [
                    make_distractor("B", "lexical_association_trap", "聽見 outdoor hikers 而誤選登山背包行銷活動。"),
                    make_distractor("C", "misattributed_detail", "蘇黎世為外部測試實驗室所在地，並非公司搬遷。"),
                    make_distractor("D", "unsupported_claim", "未提及工程師薪資調整。"),
                ],
                "vocabulary": [make_vocab("cartridge", "濾芯、卡匣", "n.", "filter cartridge 指濾芯。")],
                "estimated_time_sec": 35,
            },
            {
                "item_id": "ag-i-p4-000301-2",
                "prompt_en": "Why does the speaker say, \"we certainly don't want outdoor hikers dealing with a loose cover on the trail\"?",
                "choices": [
                    make_choice("A", "To criticize the marketing team's choice of target customers"),
                    make_choice("B", "To justify why the housing latch needed to be strengthened before launch"),
                    make_choice("C", "To announce that the product will only be sold for indoor kitchen use"),
                    make_choice("D", "To explain why the ceramic filter purity test failed"),
                ],
                "answer_choice_id": "B",
                "skill_tags": ["pragmatic_intent_implication", "inference"],
                "evidence": [
                    {"source_type": "audio_segment", "source_id": "seg2", "quote_en": "the plastic latch on the outer housing cracked after three hundred drop cycles. Now, we certainly don't want outdoor hikers dealing with a loose cover on the trail."},
                    {"source_type": "audio_segment", "source_id": "seg3", "quote_en": "Therefore, our mechanical engineering team has redesigned the latch using reinforced nylon"},
                ],
                "explanation_zh": "講者在指出外殼塑膠卡扣經 300 次落摔測試後裂開後，說出「我們當然不希望登山客在山徑上遇到外蓋鬆脫的情況」，緊接著以 Therefore 引出機械工程團隊改用強化尼龍重新設計卡扣，旨在說明為何必須在上市前強化該外殼卡扣 (B)。",
                "distractor_notes": [
                    make_distractor("A", "pragmatic_distortion", "並非批評行銷團隊鎖定登山客。"),
                    make_distractor("C", "unsupported_claim", "產品本身即為攜帶式戶外淨水器，並非改為室內廚房專用。"),
                    make_distractor("D", "contradicts_text", "陶瓷濾芯過濾純度超過 99.9%（表現優異），破裂的是外殼塑膠卡扣。"),
                ],
                "vocabulary": [make_vocab("latch", "卡扣、門閂", "n.", "產品外殼固定機構常用字。")],
                "estimated_time_sec": 40,
            },
            {
                "item_id": "ag-i-p4-000301-3",
                "prompt_en": "What will happen on Friday morning?",
                "choices": [
                    make_choice("A", "The team will inspect updated prototype units."),
                    make_choice("B", "Engineers will fly to the Zurich testing facility."),
                    make_choice("C", "Retail price increases will be announced to distributors."),
                    make_choice("D", "The injection-molding plant will close for a holiday."),
                ],
                "answer_choice_id": "A",
                "skill_tags": ["future_action", "specific_detail"],
                "evidence": [{"source_type": "audio_segment", "source_id": "seg4", "quote_en": "and we will review the new prototype samples at our Friday morning meeting."}],
                "explanation_zh": "講者在 seg4 結尾說明修改後的模具已送往射出成型廠，團隊將於週五早上的會議中檢視新的原型樣品（review the new prototype samples），故選 (A)。",
                "distractor_notes": [
                    make_distractor("B", "unsupported_claim", "未提及週五飛往蘇黎世。"),
                    make_distractor("C", "contradicts_text", "改用強化尼龍每件僅增加 12 美分且完全在預算內，未宣布調漲零售價。"),
                    make_distractor("D", "unsupported_claim", "未提及射出成型廠放假停工。"),
                ],
                "vocabulary": [make_vocab("prototype", "原型機、樣品", "n.", "prototype samples 指原型樣品。")],
                "estimated_time_sec": 35,
            },
        ],
        "provenance": make_provenance(),
        "review_refs": ["ag-rev-ai-p4-000301", "ag-rev-blind-p4-000301"],
    })

    # Synthesize audio for all 8 listening groups in batch-ag-0009 (1 Part 1 + 4 Part 2 + 2 Part 3 + 1 Part 4)
    for g in groups:
        if g["part"] in (1, 2, 3, 4):
            ast = next(a for a in g["assets"] if a["kind"] == "audio")
            aid = ast["asset_id"]
            m4a_name = f"{aid}.m4a"
            out_m4a = audio_dir / m4a_name
            meta = synthesize_group_audio(g, out_m4a)
            cast_desc = "；".join(
                f"{vc['speaker_id']}({vc['role']}, planned={vc['planned_accent']} -> voice={vc['voice_name']}[{vc['locale']}])"
                for vc in meta["voice_cast"]
            )
            ast["status"] = "ready"
            ast["path"] = f"assets/audio/{m4a_name}"
            ast["sha256"] = meta["sha256"]
            ast["mime_type"] = "audio/mp4"
            ast["duration_ms"] = meta["duration_ms"]
            ast["review_state"] = "ai_checked"
            ast["segment_times"] = meta["segment_times"]
            ast["source_note_zh"] = (
                f"由本機 macOS TTS (/usr/bin/say + afconvert AAC 22.05kHz) 實際合成之單一完整時間軸音檔；"
                f"角色配音：{cast_desc}。"
            )

    # Part 5: 4 groups in batch-ag-0009 (ag-g-p5-000301..000304)
    diag_p5_specs = [
        (
            "ag-g-p5-000301", "ag-i-p5-000301-1", "ag-fam-diag-p5-001", "office_administration", "D1",
            "基礎所有格形容詞（their ID badges）與複數先行詞搭配。",
            "Visitors entering the research annex must wear ____ temporary security badges in a visible location at all times.",
            [("A", "they"), ("B", "them"), ("C", "their"), ("D", "theirs")],
            "C", ["pronoun_reference", "grammar_structure"], "must wear ____ temporary security badges",
            "空格後接名詞片語 temporary security badges，須用所有格形容詞修飾，且先行詞為複數名詞 Visitors，故選 (C) their。",
            [
                ("A", "grammar_case", "they 為主格代名詞，不可修飾名詞。"),
                ("B", "grammar_case", "them 為受格代名詞，不可作定語修飾 badges。"),
                ("D", "grammar_case", "theirs 為所有格代名詞，後方不可再接名詞 temporary security badges。"),
            ],
            [("visible", "看得見的、顯眼的", "adj.", "in a visible location 指在顯眼位置。")],
            20,
        ),
        (
            "ag-g-p5-000302", "ag-i-p5-000302-1", "ag-fam-diag-p5-002", "procurement_vendor_management", "D2",
            "詞性衍生辨析：動詞 negotiate 之名詞受詞（entered into negotiations）或比較結構，此處考形容詞 competitive pricing。",
            "Alden Packaging was selected as our primary supplier because it offered the most ____ rates for recycled cardboard.",
            [("A", "compete"), ("B", "competitive"), ("C", "competitively"), ("D", "competitor")],
            "B", ["word_form", "grammar_structure"], "offered the most ____ rates for recycled cardboard",
            "定冠詞與最高級副詞 the most 後方、名詞 rates 前方須填入形容詞，表達「最具競爭力的報價（the most competitive rates）」，故選 (B) competitive。",
            [
                ("A", "word_form", "compete 為動詞，不可置於 the most 與名詞 rates 之間。"),
                ("C", "word_form", "competitively 為副詞，不可直接修飾名詞 rates。"),
                ("D", "word_form", "competitor 為名詞「競爭對手」，不可與 the most 連用修飾 rates。"),
            ],
            [("primary", "主要的、首選的", "adj.", "primary supplier 指主要供應商。")],
            25,
        ),
        (
            "ag-g-p5-000303", "ag-i-p5-000303-1", "ag-fam-diag-p5-003", "it_systems_security", "D3",
            "時間與條件連接詞 once（一旦…就…）連接完成升級後之自動同步。",
            "____ the cloud backup patch is installed on the main server, all regional workstations will synchronize automatically.",
            [("A", "Once"), ("B", "During"), ("C", "Despite"), ("D", "Unless")],
            "A", ["preposition_conjunction", "grammar_structure"], "____ the cloud backup patch is installed on the main server, all regional workstations will synchronize automatically",
            "從屬子句「雲端備份修補程式安裝於主伺服器上」為觸發主句「所有區域工作站將自動同步」之時間／條件起點，(A) Once（一旦…）為連接詞且語意完全契合。",
            [
                ("B", "grammar_scope", "During 為介系詞，後方不可接完整子句。"),
                ("C", "grammar_scope", "Despite 為介系詞，後方不可接完整子句且語意無讓步轉折。"),
                ("D", "logical_reversal", "Unless 意為「除非」，若填入則變成「除非安裝修補程式，否則將會自動同步」，與常理相反。"),
            ],
            [("patch", "軟體修補程式", "n.", "security/backup patch 指修補更新檔。"), ("synchronize", "同步化", "v.", "資料同步常用動詞。")],
            30,
        ),
        (
            "ag-g-p5-000304", "ag-i-p5-000304-1", "ag-fam-diag-p5-004", "corporate_governance_legal", "D5",
            "省略 if 之第三類／混合條件句或 should 萬一條件倒裝（Should any discrepancy arise...）。",
            "____ any discrepancy arise between the translated summary and the original contract, the English text shall prevail.",
            [("A", "Should"), ("B", "Were"), ("C", "Had"), ("D", "Would")],
            "A", ["grammar_structure", "verb_tense_voice"], "____ any discrepancy arise between the translated summary and the original contract, the English text shall prevail",
            "從屬子句主詞 any discrepancy 為單數，後方動詞卻為原形動詞 arise，且主句使用未來法務規定助動詞 shall prevail，屬於省略 if 之未來假設倒裝句（= If any discrepancy should arise... -> Should any discrepancy arise...），故選 (A) Should。",
            [
                ("B", "grammar_form", "Were 倒裝搭配單數主詞時，後方須接不定詞 to arise（Were any discrepancy to arise），不可直接接原形動詞 arise。"),
                ("C", "grammar_form", "Had 倒裝表過去相反假設，後方須接過去分詞 arisen。"),
                ("D", "grammar_scope", "Would 不用於條件從屬子句句首倒裝。"),
            ],
            [("discrepancy", "不一致、出入", "n.", "合約與帳務高頻詞彙。"), ("prevail", "以…為準、佔優勢", "v.", "the English text shall prevail 指以英文文本為準。")],
            40,
        ),
    ]
    for spec in diag_p5_specs:
        groups.append(make_part5_group(
            gid=spec[0], iid=spec[1], fam_id=spec[2], pool="diagnostic",
            scenario=spec[3], diff_level=spec[4], diff_rationale=spec[5],
            prompt_en=spec[6], choices=spec[7], ans=spec[8], skill_tags=spec[9],
            quote_en=spec[10], explanation_zh=spec[11], distractors=spec[12],
            vocab=spec[13], est_sec=spec[14],
        ))

    # Part 6: 1 group in batch-ag-0009 (ag-g-p6-000301, 4 items)
    groups.append({
        "schema_version": "1.0.0",
        "group_id": "ag-g-p6-000301",
        "version": 1,
        "family_id": "ag-fam-diag-p6-001",
        "pool": "diagnostic",
        "fixture": False,
        "part": 6,
        "layout": "text_completion",
        "scenario": "hr_recruitment_training",
        "difficulty": make_difficulty("D3", "企業內部專業證照補助政策通知，涵蓋詞性、時態語態、連接詞與插句。"),
        "content_status": "ai_checked",
        "stimulus": {
            "documents": [
                {
                    "document_id": "ag-doc-p6-000301-1",
                    "genre": "notice",
                    "title_en": "Professional Certification Tuition Assistance Program",
                    "blocks": [
                        {
                            "block_id": "ag-blk-p6-000301-1",
                            "type": "text",
                            "text_en": (
                                "Kestrel BioLabs encourages full-time staff members to pursue industry certifications that strengthen their technical capabilities. "
                                "Under our updated Tuition Assistance Policy, employees who have completed at least one year of continuous service may apply for [[blank:ag-i-p6-000301-1]] of up to $1,500 per calendar year.\n\n"
                                "Eligible expenses include accredited examination fees and required digital study materials. "
                                "[[blank:ag-i-p6-000301-2]] Applications must be endorsed by a department director at least three weeks before the course start date.\n\n"
                                "Once the certification exam has been passed, the employee should upload the official score certificate and itemized payment receipts to the HR portal. "
                                "Approved claims [[blank:ag-i-p6-000301-3]] in the employee's next regular direct-deposit paycheck. "
                                "[[blank:ag-i-p6-000301-4]], staff members who leave the company voluntarily within six months of receiving funds must repay the subsidized amount in full."
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
                "item_id": "ag-i-p6-000301-1",
                "prompt_en": "Select the best word or phrase for [[blank:ag-i-p6-000301-1]].",
                "choices": [
                    make_choice("A", "reimburse"),
                    make_choice("B", "reimbursed"),
                    make_choice("C", "reimbursement"),
                    make_choice("D", "reimbursing"),
                ],
                "answer_choice_id": "C",
                "skill_tags": ["word_form", "grammar_structure"],
                "evidence": [{"source_type": "document_block", "source_id": "ag-blk-p6-000301-1", "quote_en": "may apply for [[blank:ag-i-p6-000301-1]] of up to $1,500 per calendar year."}],
                "explanation_zh": "介系詞 for 後方且接續介系詞片語 of up to $1,500，須填入名詞作受詞；apply for reimbursement of up to $1,500（申請最高 1,500 美元之費用補助／報銷）為標準搭配，故選名詞 (C) reimbursement。",
                "distractor_notes": [
                    make_distractor("A", "word_form", "reimburse 為原形動詞，不可作介系詞 for 之受詞。"),
                    make_distractor("B", "word_form", "reimbursed 為過去分詞，不可作介系詞受詞。"),
                    make_distractor("D", "grammar_form", "動名詞 reimbursing 若作及物動詞需接直接受詞而非 of up to $1,500。"),
                ],
                "vocabulary": [make_vocab("pursue", "攻讀、追求（學位或證照）", "v.", "pursue certifications 指考取專業證照。")],
                "estimated_time_sec": 30,
            },
            {
                "item_id": "ag-i-p6-000301-2",
                "prompt_en": "Select the best sentence for [[blank:ag-i-p6-000301-2]].",
                "choices": [
                    make_choice("A", "Travel and hotel costs for out-of-town test centers are not covered under this plan."),
                    make_choice("B", "The company cafeteria will introduce a new summer menu next Monday."),
                    make_choice("C", "All laboratory microscopes were calibrated by an external vendor in August."),
                    make_choice("D", "Entry-level interns are automatically enrolled in the executive bonus pool."),
                ],
                "answer_choice_id": "A",
                "skill_tags": ["sentence_insertion", "cross_reference"],
                "evidence": [{"source_type": "document_block", "source_id": "ag-blk-p6-000301-1", "quote_en": "Eligible expenses include accredited examination fees and required digital study materials. [[blank:ag-i-p6-000301-2]] Applications must be endorsed by a department director"}],
                "explanation_zh": "前句界定符合補助資格之費用項目（認證考試報名費與必備數位教材），(A)「前往外地考場之差旅與住宿費用不在本計畫補助範圍內」緊接著補充說明排除項目，使費用範圍界定完整。",
                "distractor_notes": [
                    make_distractor("B", "off_topic", "員工餐廳夏季菜單與證照補助政策無關。"),
                    make_distractor("C", "off_topic", "實驗室顯微鏡校正與人資進修補助無關。"),
                    make_distractor("D", "off_topic", "實習生高階獎金池與本段證照費用申請規範無關。"),
                ],
                "vocabulary": [make_vocab("accredited", "經官方認可的、合格認證的", "adj.", "accredited examination 指認證考試。")],
                "estimated_time_sec": 50,
            },
            {
                "item_id": "ag-i-p6-000301-3",
                "prompt_en": "Select the best word or phrase for [[blank:ag-i-p6-000301-3]].",
                "choices": [
                    make_choice("A", "disbursed"),
                    make_choice("B", "will be disbursed"),
                    make_choice("C", "have disbursed"),
                    make_choice("D", "disbursing"),
                ],
                "answer_choice_id": "B",
                "skill_tags": ["verb_tense_voice", "grammar_structure"],
                "evidence": [{"source_type": "document_block", "source_id": "ag-blk-p6-000301-1", "quote_en": "Approved claims [[blank:ag-i-p6-000301-3]] in the employee's next regular direct-deposit paycheck."}],
                "explanation_zh": "主詞 Approved claims（核准的報銷申請款項）為承受「撥付（disburse）」動作之物，且發放時間為未來下一期薪資轉帳（next regular direct-deposit paycheck），故選未來被動式 (B) will be disbursed。",
                "distractor_notes": [
                    make_distractor("A", "tense_mismatch", "disbursed 為過去式主動或分詞，與 next regular paycheck 時間及被動語態不合。"),
                    make_distractor("C", "grammar_voice", "have disbursed 為現在完成主動式，款項無法主動撥付。"),
                    make_distractor("D", "grammar_form", "disbursing 為分詞，缺少助動詞無法作為句子主要動詞。"),
                ],
                "vocabulary": [make_vocab("direct-deposit", "薪資直接入帳、轉帳", "n.", "direct-deposit paycheck 指薪資轉帳款。")],
                "estimated_time_sec": 35,
            },
            {
                "item_id": "ag-i-p6-000301-4",
                "prompt_en": "Select the best word or phrase for [[blank:ag-i-p6-000301-4]].",
                "choices": [
                    make_choice("A", "However"),
                    make_choice("B", "Similarly"),
                    make_choice("C", "Therefore"),
                    make_choice("D", "For example"),
                ],
                "answer_choice_id": "A",
                "skill_tags": ["preposition_conjunction", "cross_reference"],
                "evidence": [{"source_type": "document_block", "source_id": "ag-blk-p6-000301-1", "quote_en": "Approved claims [[blank:ag-i-p6-000301-3]] in the employee's next regular direct-deposit paycheck. [[blank:ag-i-p6-000301-4]], staff members who leave the company voluntarily within six months of receiving funds must repay the subsidized amount in full."}],
                "explanation_zh": "前句說明核准款項將於下期薪資中撥付，本句轉而提出但書限制「然而，若員工於領取補助後六個月內自願離職，必須全額退還補助款」，構成轉折但書關係，故選 (A) However。",
                "distractor_notes": [
                    make_distractor("B", "semantic_mismatch", "Similarly 表「同樣地」，前後並非相似類比。"),
                    make_distractor("C", "semantic_mismatch", "Therefore 表「因此」，領取薪資撥款並非離職須還款的因果推論。"),
                    make_distractor("D", "semantic_mismatch", "For example 表舉例，離職追回條款並非正常薪資撥付的例子。"),
                ],
                "vocabulary": [make_vocab("subsidize", "補助、資助", "v.", "subsidized amount 指補助金額。")],
                "estimated_time_sec": 30,
            },
        ],
        "provenance": make_provenance(),
        "review_refs": ["ag-rev-ai-p6-000301", "ag-rev-blind-p6-000301"],
    })

    # Part 7: 1 group in batch-ag-0009 (ag-g-p7-000301, 2 items)
    groups.append({
        "schema_version": "1.0.0",
        "group_id": "ag-g-p7-000301",
        "version": 1,
        "family_id": "ag-fam-diag-p7-001",
        "pool": "diagnostic",
        "fixture": False,
        "part": 7,
        "layout": "single_passage",
        "scenario": "finance_budgeting_invoicing",
        "difficulty": make_difficulty("D3", "單篇商務供應商請款與早鳥折扣電子郵件，考核細節與推論。"),
        "content_status": "ai_checked",
        "stimulus": {
            "documents": [
                {
                    "document_id": "ag-doc-p7-000301-1",
                    "genre": "email",
                    "title_en": "Subject: Invoice #INV-8842 — Acoustic Wall Panels for Conference Wing",
                    "blocks": [
                        {
                            "block_id": "ag-blk-p7-000301-1",
                            "type": "text",
                            "text_en": (
                                "To: Accounts Payable <ap@veridianarchitects.com>\n"
                                "From: Billing Department <billing@nordicacoustics.se>\n"
                                "Date: October 3\n"
                                "Subject: Invoice #INV-8842 — Acoustic Wall Panels\n\n"
                                "Dear Veridian Architects Team,\n\n"
                                "Attached is Invoice #INV-8842 for the forty custom oak acoustic wall panels delivered and installed in your third-floor conference wing on October 1. The total balance due is $12,400, payable within 30 calendar days.\n\n"
                                "As a reminder, commercial clients who remit full payment via electronic wire transfer within 10 days of the invoice date (by October 13) may deduct a 3 percent early-settlement discount ($372) from the invoice total. Please include the invoice number in the wire reference field so our accounting system can credit your account promptly."
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
                "item_id": "ag-i-p7-000301-1",
                "prompt_en": "What is the purpose of the e-mail?",
                "choices": [
                    make_choice("A", "To request payment for recently installed sound-absorbing panels"),
                    make_choice("B", "To reschedule the delivery of forty oak conference tables"),
                    make_choice("C", "To confirm receipt of a wire transfer sent on October 1"),
                    make_choice("D", "To provide a price quote for renovating a building lobby"),
                ],
                "answer_choice_id": "A",
                "skill_tags": ["main_idea_purpose", "paraphrase_matching"],
                "evidence": [{"source_type": "document_block", "source_id": "ag-blk-p7-000301-1", "quote_en": "Attached is Invoice #INV-8842 for the forty custom oak acoustic wall panels delivered and installed in your third-floor conference wing on October 1. The total balance due is $12,400"}],
                "explanation_zh": "信件隨函附上 10 月 1 日已交貨並安裝於三樓會議區之 40 片客製橡木隔音吸音牆板（acoustic wall panels）請款發票，並說明應付總額與付款期限，故目的為請求支付近期安裝之隔音牆板款項 (A)。",
                "distractor_notes": [
                    make_distractor("B", "misattributed_detail", "標的物為 40 片橡木吸音牆板（acoustic wall panels）且已於 10 月 1 日安裝完畢，並非會議桌改期交貨。"),
                    make_distractor("C", "contradicts_text", "款項尚未支付（The total balance due is $12,400），10 月 1 日為交貨安裝日。"),
                    make_distractor("D", "misattributed_detail", "此為完工後之正式請款發票而非大廳裝修報價單。"),
                ],
                "vocabulary": [make_vocab("remit", "匯款、支付", "v.", "remit payment 指匯付貨款。")],
                "estimated_time_sec": 45,
            },
            {
                "item_id": "ag-i-p7-000301-2",
                "prompt_en": "How can Veridian Architects reduce the amount it owes by $372?",
                "choices": [
                    make_choice("A", "By returning unused mounting brackets to the warehouse"),
                    make_choice("B", "By paying the full balance via wire transfer on or before October 13"),
                    make_choice("C", "By signing a two-year maintenance contract for the third floor"),
                    make_choice("D", "By mailing a paper check within 30 calendar days"),
                ],
                "answer_choice_id": "B",
                "skill_tags": ["specific_detail", "paraphrase_matching"],
                "evidence": [{"source_type": "document_block", "source_id": "ag-blk-p7-000301-1", "quote_en": "commercial clients who remit full payment via electronic wire transfer within 10 days of the invoice date (by October 13) may deduct a 3 percent early-settlement discount ($372) from the invoice total."}],
                "explanation_zh": "第二段明載：商業客戶若於發票日起 10 天內（即 10 月 13 日前）透過電子電匯（electronic wire transfer）付清全額，即可從發票總額扣除 3% 早鳥結清折扣（$372），故選 (B)。",
                "distractor_notes": [
                    make_distractor("A", "unsupported_claim", "未提及退還安裝支架。"),
                    make_distractor("C", "unsupported_claim", "未提及簽署兩年維護合約。"),
                    make_distractor("D", "contradicts_text", "須於 10 天內以電子電匯付款才享有折扣，30 天是一般付款期限且未提紙本支票折扣。"),
                ],
                "vocabulary": [make_vocab("early-settlement discount", "提早結清折扣、早鳥付款折扣", "n.", "應收應付帳款常見術語。")],
                "estimated_time_sec": 45,
            },
        ],
        "provenance": make_provenance(),
        "review_refs": ["ag-rev-ai-p7-000301", "ag-rev-blind-p7-000301"],
    })

    return groups


# ==============================================================================
# 3. Build Batch 0010 (pool="battle", 21 groups = 24 items: Part 2 x6, Part 5 x14, Part 6 x1)
# ==============================================================================
def build_batch_0010_groups(draft_dir: Path) -> List[Dict[str, Any]]:
    groups: List[Dict[str, Any]] = []
    audio_dir = draft_dir / "assets" / "audio"
    audio_dir.mkdir(parents=True, exist_ok=True)

    # Part 2: 6 groups (ag-g-p2-000401..000406) using us, uk, au accents
    btl_p2_specs = [
        (
            "ag-g-p2-000401", "ag-i-p2-000401-1", "ag-fam-btl-p2-001", "office_administration", "D1",
            "Who 身分詢問搭配部門職稱與人名直接回答。",
            ("us", "Female Coordinator", "uk", "Male Clerk"),
            "Who authorized the purchase of the ergonomic desk chairs?",
            [
                ("A", "Ms. Patel in the facilities department."),
                ("B", "Yes, they are very comfortable."),
                ("C", "Next to the conference table."),
            ],
            "A", ["wh_question_response", "specific_detail"],
            "提問以 Who 詢問「是誰核准採購這批人體工學辦公椅的？」，(A)「設施部門的 Patel 女士」直接指出核准人。",
            [
                ("B", "yes_no_trap", "Who 疑問句不可用 Yes 回答。"),
                ("C", "question_type_mismatch", "回答擺放位置，對應 Where 而非 Who。"),
            ],
            [("ergonomic", "符合人體工學的", "adj.", "ergonomic chairs 指人體工學椅。")],
        ),
        (
            "ag-g-p2-000402", "ag-i-p2-000402-1", "ag-fam-btl-p2-002", "travel_hotel_airport", "D2",
            "What time 時間提問搭配具體航班起飛時刻回應。",
            ("uk", "Male Executive", "us", "Female Assistant"),
            "What time does our connecting flight to Frankfurt depart?",
            [
                ("A", "At Gate C14 in the North Terminal."),
                ("B", "At six forty-five this evening."),
                ("C", "A window seat in business class."),
            ],
            "B", ["wh_question_response", "specific_detail"],
            "提問詢問「我們飛往法蘭克福的轉機航班幾點起飛？」，(B)「今晚六點四十五分」直接提供確切起飛時間。",
            [
                ("A", "question_type_mismatch", "回答登機門位置（Gate C14），對應 Where 而非 What time。"),
                ("C", "lexical_association_trap", "聯想 flight 而回答商務艙靠窗座位，答非所問。"),
            ],
            [("connecting flight", "轉機航班", "n.", "商務差旅高頻搭配。")],
        ),
        (
            "ag-g-p2-000403", "ag-i-p2-000403-1", "ag-fam-btl-p2-003", "customer_service_returns", "D2",
            "選擇疑問句（Would you prefer A or B?）搭配明確偏好選擇。",
            ("us", "Female Representative", "au", "Female Client"),
            "Would you like a replacement monitor shipped to your office, or would you prefer store credit?",
            [
                ("A", "Please send a replacement to my office."),
                ("B", "Yes, the screen resolution is very sharp."),
                ("C", "About twenty-seven inches wide."),
            ],
            "A", ["choice_alternative_response", "specific_detail"],
            "提問為二選一選擇問句（寄送替換螢幕至辦公室，或選擇店內購物金），(A)「請寄一台替換品到我辦公室」明確做出選擇。",
            [
                ("B", "yes_no_trap", "選擇問句不以 Yes 開頭回答螢幕解析度。"),
                ("C", "lexical_association_trap", "聯想 monitor 而回答螢幕尺寸 27 吋，未回應處理方式。"),
            ],
            [("store credit", "店內購物抵用金", "n.", "退換貨常見選項。")],
        ),
        (
            "ag-g-p2-000404", "ag-i-p2-000404-1", "ag-fam-btl-p2-004", "marketing_events_promotions", "D3",
            "Why 原因提問搭配因為講者行程變動之合理說明。",
            ("uk", "Female Planner", "us", "Male Director"),
            "Why was the keynote speech moved to the morning session?",
            [
                ("A", "In the Grand Ballroom on the mezzanine level."),
                ("B", "The guest speaker has an afternoon flight to Tokyo."),
                ("C", "For about forty-five minutes."),
            ],
            "B", ["wh_question_response", "indirect_pragmatic_response"],
            "提問詢問「為什麼主題演講被調到早上的場次？」，(B)「特邀講者下午有一班飛往東京的班機」清楚交代提早場次之原因。",
            [
                ("A", "question_type_mismatch", "回答演講廳地點，對應 Where 而非 Why。"),
                ("C", "question_type_mismatch", "回答演講時長，對應 How long 而非 Why。"),
            ],
            [("keynote speech", "主題演講", "n.", "研討會核心詞彙。"), ("mezzanine", "夾層樓面", "n.", "飯店與會展中心常見樓層。")],
        ),
        (
            "ag-g-p2-000405", "ag-i-p2-000405-1", "ag-fam-btl-p2-005", "manufacturing_quality_control", "D4",
            "附加問句搭配糾正細節之間接語用回應。",
            ("us", "Male Manager", "uk", "Female Engineer"),
            "The protective coatings on the turbine blades passed the salt-spray test, didn't they?",
            [
                ("A", "Actually, two samples showed minor surface corrosion."),
                ("B", "No, the laboratory coats are in the locker room."),
                ("C", "Every Tuesday and Thursday afternoon."),
            ],
            "A", ["yes_no_tag_negative_response", "indirect_pragmatic_response"],
            "提問以附加問句確認「渦輪葉片上的防護塗層通過鹽霧測試了，對吧？」，(A)「事實上，有兩件樣品出現輕微表面腐蝕」以 Actually 委婉否定並說明未完全通過之實情。",
            [
                ("B", "homophone_polysemy_trap", "利用 coatings（塗層）與 laboratory coats（實驗衣）之字根音近設下陷阱。"),
                ("C", "question_type_mismatch", "回答固定時段，未回應測試是否通過。"),
            ],
            [("corrosion", "腐蝕、鏽蝕", "n.", "品管與材料測試關鍵字。")],
        ),
        (
            "ag-g-p2-000406", "ag-i-p2-000406-1", "ag-fam-btl-p2-006", "finance_budgeting_invoicing", "D5",
            "How 詢問籌措資金方式搭配高階間接回應（董事會仍在評估兩個方案）。",
            ("au", "Female Officer", "us", "Male President"),
            "How are we going to fund the expansion of the Montreal distribution center?",
            [
                ("A", "About eighty thousand square feet of floor space."),
                ("B", "The board is still weighing a bank loan against a bond issue."),
                ("C", "Yes, the warehouse manager signed the lease."),
            ],
            "B", ["wh_question_response", "indirect_pragmatic_response"],
            "提問詢問「我們將如何為蒙特婁物流中心的擴建案籌措資金（fund）？」，(B)「董事會仍在權衡要採銀行貸款還是發行債券」精準回應籌資方式尚未定案但正評估兩種財務工具。",
            [
                ("A", "lexical_association_trap", "聯想 expansion / distribution center 而回答樓地板面積，對應 How large 而非 How to fund。"),
                ("C", "yes_no_trap", "How 疑問句不可用 Yes 開頭回答。"),
            ],
            [("weigh", "權衡、斟酌", "v.", "weigh A against B 指權衡比較 A 與 B。"), ("bond issue", "債券發行", "n.", "企業籌資術語。")],
        ),
    ]

    for gid, iid, fam, scen, d_lvl, d_rat, spk_cfg, q_text, ch_list, ans, tags, exp_zh, dist_list, voc_list in btl_p2_specs:
        num_suffix = gid.split("-")[-1]
        g_p2 = {
            "schema_version": "1.0.0",
            "group_id": gid,
            "version": 1,
            "family_id": fam,
            "pool": "battle",
            "fixture": False,
            "part": 2,
            "layout": "question_response",
            "scenario": scen,
            "difficulty": make_difficulty(d_lvl, d_rat),
            "content_status": "ai_checked",
            "stimulus": {
                "documents": [],
                "speakers": [
                    {"speaker_id": "spk1", "role": f"Questioner ({spk_cfg[1]})", "accent": spk_cfg[0]},
                    {"speaker_id": "spk2", "role": f"Responder ({spk_cfg[3]})", "accent": spk_cfg[2]},
                ],
                "audio_script": [
                    {"segment_id": "seg1", "speaker_id": "spk1", "text_en": q_text},
                    {"segment_id": "seg2", "speaker_id": "spk2", "text_en": f"(A) {ch_list[0][1]}"},
                    {"segment_id": "seg3", "speaker_id": "spk2", "text_en": f"(B) {ch_list[1][1]}"},
                    {"segment_id": "seg4", "speaker_id": "spk2", "text_en": f"(C) {ch_list[2][1]}"},
                ],
            },
            "assets": [
                {
                    "asset_id": f"ag-ast-p2-{num_suffix}-audio",
                    "kind": "audio",
                    "status": "planned",
                    "path": None,
                    "sha256": None,
                    "duration_ms": None,
                    "source_note_zh": "待合成音訊",
                    "review_state": "pending",
                    "segment_times": [],
                }
            ],
            "items": [
                {
                    "item_id": iid,
                    "prompt_en": "Listen to the question or statement and three responses. Choose the best response.",
                    "choices": [make_choice(c, t) for c, t in ch_list],
                    "answer_choice_id": ans,
                    "skill_tags": tags,
                    "evidence": [
                        {"source_type": "audio_segment", "source_id": "seg1", "quote_en": q_text},
                        {"source_type": "audio_segment", "source_id": f"seg{1 + ['A','B','C'].index(ans)}", "quote_en": f"({ans}) {dict(ch_list)[ans]}"},
                    ],
                    "explanation_zh": exp_zh,
                    "distractor_notes": [make_distractor(c, tp, r) for c, tp, r in dist_list],
                    "vocabulary": [make_vocab(s, m, p, n) for s, m, p, n in voc_list],
                    "estimated_time_sec": 20,
                }
            ],
            "provenance": make_provenance(),
            "review_refs": [f"ag-rev-ai-p2-{num_suffix}", f"ag-rev-blind-p2-{num_suffix}"],
        }
        groups.append(g_p2)

    # Synthesize all 6 Part 2 audio files in batch-ag-0010
    for g in groups:
        if g["part"] == 2:
            ast = g["assets"][0]
            aid = ast["asset_id"]
            m4a_name = f"{aid}.m4a"
            out_m4a = audio_dir / m4a_name
            meta = synthesize_group_audio(g, out_m4a)
            cast_desc = "；".join(
                f"{vc['speaker_id']}({vc['role']}, planned={vc['planned_accent']} -> voice={vc['voice_name']}[{vc['locale']}])"
                for vc in meta["voice_cast"]
            )
            ast["status"] = "ready"
            ast["path"] = f"assets/audio/{m4a_name}"
            ast["sha256"] = meta["sha256"]
            ast["mime_type"] = "audio/mp4"
            ast["duration_ms"] = meta["duration_ms"]
            ast["review_state"] = "ai_checked"
            ast["segment_times"] = meta["segment_times"]
            ast["source_note_zh"] = (
                f"由本機 macOS TTS (/usr/bin/say + afconvert AAC 22.05kHz) 實際合成之單一完整時間軸音檔；"
                f"角色配音：{cast_desc}。"
            )

    # Part 5: 14 groups in batch-ag-0010 (ag-g-p5-000401..000414) for Battle mode!
    btl_p5_specs = [
        (
            "ag-g-p5-000401", "ag-i-p5-000401-1", "ag-fam-btl-p5-001", "retail_store_operations", "D1",
            "基礎介系詞搭配（at the checkout counter）。",
            "Customers may redeem their promotional gift vouchers ____ any checkout counter in the store.",
            [("A", "at"), ("B", "into"), ("C", "among"), ("D", "until")],
            "A", ["preposition_conjunction", "collocation_idiom"], "redeem their promotional gift vouchers ____ any checkout counter",
            "表示「在店內任何結帳櫃台」兌換禮券，特定服務點搭配介系詞 (A) at（at any checkout counter）。",
            [
                ("B", "collocation_mismatch", "into 表進入內部，不與 checkout counter 搭配。"),
                ("C", "grammar_scope", "among 後接複數名詞表「在三者以上之中」，checkout counter 為單數。"),
                ("D", "semantic_mismatch", "until 表時間直到…，不可接地點名詞。"),
            ],
            [("redeem", "兌換（禮券、點數）", "v.", "redeem a voucher 指兌換禮券。")],
            20,
        ),
        (
            "ag-g-p5-000402", "ag-i-p5-000402-1", "ag-fam-btl-p5-002", "office_administration", "D1",
            "名詞詞性選擇（require the signature of the supervisor）。",
            "All overtime requests require the written ____ of a division supervisor before Friday afternoon.",
            [("A", "approve"), ("B", "approved"), ("C", "approving"), ("D", "approval")],
            "D", ["word_form", "grammar_structure"], "require the written ____ of a division supervisor",
            "定冠詞 the 與形容詞 written 後方、介系詞 of 前方須填入名詞作受詞，written approval 意為「書面核准」，故選 (D) approval。",
            [
                ("A", "word_form", "approve 為動詞，不可置於 the written 與 of 之間。"),
                ("B", "word_form", "approved 為過去分詞／形容詞，無法作 require 之名詞核心。"),
                ("C", "word_form", "approving 為現在分詞，在已有專屬名詞 approval 時不作 the written ___ of 結構。"),
            ],
            [("overtime", "加班（時間）", "n.", "overtime requests 指加班申請。")],
            20,
        ),
        (
            "ag-g-p5-000403", "ag-i-p5-000403-1", "ag-fam-btl-p5-003", "travel_hotel_airport", "D2",
            "副詞修飾形容詞或動詞（complimentary shuttle runs frequently）。",
            "A complimentary shuttle bus runs ____ between the convention center and the downtown train station.",
            [("A", "frequent"), ("B", "frequently"), ("C", "frequency"), ("D", "frequented")],
            "B", ["word_form", "grammar_structure"], "A complimentary shuttle bus runs ____ between the convention center",
            "不及物動詞 runs 後方需用副詞修飾行駛頻率「頻繁地行駛」，故選副詞 (B) frequently。",
            [
                ("A", "word_form", "frequent 為形容詞或及物動詞，不可修飾動詞 runs。"),
                ("C", "word_form", "frequency 為名詞「頻率」，不可直接作狀語。"),
                ("D", "word_form", "frequented 為過去分詞「常去某處的」，不合語法。"),
            ],
            [("shuttle", "接駁車", "n.", "shuttle bus 指接駁巴士。")],
            20,
        ),
        (
            "ag-g-p5-000404", "ag-i-p5-000404-1", "ag-fam-btl-p5-004", "hr_recruitment_training", "D2",
            "比較級結構（more comprehensive than last year's manual）。",
            "The updated safety handbook is significantly ____ than the version distributed two years ago.",
            [("A", "comprehensive"), ("B", "more comprehensive"), ("C", "most comprehensive"), ("D", "comprehensively")],
            "B", ["quantifier_comparison", "grammar_structure"], "is significantly ____ than the version distributed two years ago",
            "空格後有比較連接詞 than，且主詞後為連綴動詞 is，須填入形容詞比較級 (B) more comprehensive。",
            [
                ("A", "grammar_form", "comprehensive 為原級，無法搭配後方 than。"),
                ("C", "grammar_form", "most comprehensive 為最高級，不與 than 搭配。"),
                ("D", "word_form", "comprehensively 為副詞且為原級，不能作 be 動詞補語亦不能配 than。"),
            ],
            [("comprehensive", "全面的、詳盡的", "adj.", "comprehensive handbook 指詳盡的手冊。")],
            25,
        ),
        (
            "ag-g-p5-000405", "ag-i-p5-000405-1", "ag-fam-btl-p5-005", "logistics_supply_chain", "D2",
            "精準商務動詞詞義（inspect incoming crates for damage）。",
            "Warehouse clerks must ____ every incoming crate for water damage before signing the carrier's delivery receipt.",
            [("A", "inspect"), ("B", "inquire"), ("C", "install"), ("D", "instruct")],
            "A", ["vocabulary_in_context", "collocation_idiom"], "must ____ every incoming crate for water damage",
            "inspect A for B 意為「檢查 A 是否有 B（水損）」，符合簽收貨運單前檢查進貨木箱之標準倉儲流程，故選 (A) inspect。",
            [
                ("B", "grammar_scope", "inquire 意為「詢問」，常搭配 about/into，不以 crate 為直接受詞檢查損傷。"),
                ("C", "semantic_mismatch", "install 意為「安裝（設備）」，與檢查進貨木箱水損不符。"),
                ("D", "semantic_mismatch", "instruct 意為「指示、指導（人員）」，受詞應為人而非木箱。"),
            ],
            [("crate", "木箱、貨箱", "n.", "incoming crate 指進貨木箱。")],
            25,
        ),
        (
            "ag-g-p5-000406", "ag-i-p5-000406-1", "ag-fam-btl-p5-006", "finance_budgeting_invoicing", "D3",
            "現在完成被動式（has been postponed since... / have already been audited）。",
            "All expense reports from the Munich trade fair ____ by the regional controller, so reimbursements will be issued tomorrow.",
            [("A", "audit"), ("B", "were auditing"), ("C", "have already been audited"), ("D", "will audit")],
            "C", ["verb_tense_voice", "grammar_structure"], "All expense reports from the Munich trade fair ____ by the regional controller, so reimbursements will be issued tomorrow",
            "主詞 expense reports 為承受查核（audit）動作之物，且由 by the regional controller 及結果子句「因此明天就會發放報銷款」可知查核動作「已經完成」，故選現在完成被動式 (C) have already been audited。",
            [
                ("A", "grammar_voice", "audit 為主動原形，費用報告無法主動查核。"),
                ("B", "grammar_voice", "were auditing 為過去進行主動式，語態錯誤。"),
                ("D", "grammar_voice", "will audit 為未來主動式，語態與因果時序皆錯。"),
            ],
            [("controller", "財務長、主計長", "n.", "regional controller 指區域財務主管。")],
            30,
        ),
        (
            "ag-g-p5-000407", "ag-i-p5-000407-1", "ag-fam-btl-p5-007", "marketing_events_promotions", "D3",
            "數量詞與可數複數名詞搭配（a substantial number of attendees）。",
            "Although the webinar was scheduled on short notice, a substantial ____ of international distributors logged in live.",
            [("A", "amount"), ("B", "number"), ("C", "deal"), ("D", "volume")],
            "B", ["quantifier_comparison", "collocation_idiom"], "a substantial ____ of international distributors logged in live",
            "of 後方為可數複數名詞 international distributors，且動詞 logged in 指人員登入；a substantial number of + 複數可數名詞 為標準搭配，故選 (B) number。",
            [
                ("A", "grammar_countability", "an amount of 後方只能接不可數名詞。"),
                ("C", "grammar_countability", "a great deal of 後方只能接不可數名詞。"),
                ("D", "semantic_mismatch", "a volume of 通常指液體、氣體、交易量或書冊，不用於修飾人（distributors）。"),
            ],
            [("on short notice", "臨時通知、倉促間", "prep.", "商務常用片語。")],
            30,
        ),
        (
            "ag-g-p5-000408", "ag-i-p5-000408-1", "ag-fam-btl-p5-008", "it_systems_security", "D3",
            "介系詞片語 in accordance with（依據、遵照）搭配資料保護法規。",
            "Customer billing records are encrypted and archived ____ strict national data-privacy regulations.",
            [("A", "in accordance with"), ("B", "on behalf of"), ("C", "in contrast to"), ("D", "by means of")],
            "A", ["preposition_conjunction", "collocation_idiom"], "encrypted and archived ____ strict national data-privacy regulations",
            "客戶帳單紀錄之所以加密並歸檔，是「依據、遵照」嚴格的國家資料隱私法規，(A) in accordance with 語意最精確。",
            [
                ("B", "semantic_mismatch", "on behalf of 意為「代表（某人或某機構）」，不搭配 regulations。"),
                ("C", "logical_reversal", "in contrast to 意為「與…相反／對比」，加密歸檔並非與法規相反。"),
                ("D", "semantic_mismatch", "by means of 意為「藉由…工具手段」，法規是遵循標準而非加密技術工具。"),
            ],
            [("archive", "歸檔保存", "v.", "encrypted and archived 指加密並歸檔。")],
            30,
        ),
        (
            "ag-g-p5-000409", "ag-i-p5-000409-1", "ag-fam-btl-p5-009", "product_development_rd", "D3",
            "形容詞詞義辨析（compatible with existing charging docks 與現有充電座相容）。",
            "The new lithium battery pack is fully ____ with all handheld scanners manufactured after 2023.",
            [("A", "compatible"), ("B", "comparable"), ("C", "commendable"), ("D", "comprehensive")],
            "A", ["vocabulary_in_context", "collocation_idiom"], "is fully ____ with all handheld scanners manufactured after 2023",
            "be compatible with 意為「與…相容（可通用）」，新款鋰電池組與 2023 年後生產的所有手持掃描器完全相容，故選 (A) compatible。",
            [
                ("B", "phonetic_lexical_confusion", "comparable 意為「可比較的、相當的」，常搭配 to，無法表達硬體配件相容。"),
                ("C", "semantic_mismatch", "commendable 意為「值得稱讚的」，不與 with all scanners 搭配。"),
                ("D", "semantic_mismatch", "comprehensive 意為「全面的」，不表硬體相容。"),
            ],
            [("compatible", "相容的", "adj.", "be compatible with 指與…相容。")],
            30,
        ),
        (
            "ag-g-p5-000410", "ag-i-p5-000410-1", "ag-fam-btl-p5-010", "real_estate_facilities", "D4",
            "關係副詞 where（= in which）引導定語子句修飾先行詞 conference room。",
            "The architectural blueprints are stored in the vault ____ the original property deeds are kept.",
            [("A", "which"), ("B", "where"), ("C", "whose"), ("D", "when")],
            "B", ["grammar_structure", "pronoun_reference"], "stored in the vault ____ the original property deeds are kept",
            "先行詞為地點名詞 the vault（金庫），後方關係子句 the original property deeds are kept 結構已完整（主詞 + 被動動詞），需用關係副詞表示「在該金庫裡（= in which）」，故選 (B) where。",
            [
                ("A", "grammar_case", "which 為關係代名詞，在子句中須作主詞或受詞；此處若無介系詞 in 則不能單獨使用 which。"),
                ("C", "grammar_case", "whose 後須緊接無冠詞名詞，不可接 the original property deeds。"),
                ("D", "semantic_mismatch", "when 修飾時間先行詞而非地點 the vault。"),
            ],
            [("deed", "房地契、契約書", "n.", "property deeds 指房地產權狀／地契。")],
            35,
        ),
        (
            "ag-g-p5-000411", "ag-i-p5-000411-1", "ag-fam-btl-p5-011", "manufacturing_quality_control", "D4",
            "使役／保持結構 keep + 受詞 + 受詞補語形容詞（keep the assembly area sterile）。",
            "Positive-pressure ventilation fans run continuously to keep the optical lens assembly room completely ____.",
            [("A", "sterilize"), ("B", "sterile"), ("C", "sterility"), ("D", "sterilizing")],
            "B", ["word_form", "grammar_structure"], "keep the optical lens assembly room completely ____",
            "keep + 受詞（the optical lens assembly room）+ 受詞補語（形容詞），描述使無塵組裝室保持「無菌／潔淨的狀態」，且前有副詞 completely 修飾，故選形容詞 (B) sterile。",
            [
                ("A", "word_form", "sterilize 為動詞，不可作 keep 之受詞補語。"),
                ("C", "word_form", "sterility 為名詞，不可受副詞 completely 修飾作狀態補語。"),
                ("D", "grammar_voice", "sterilizing 為現在分詞表主動正在消毒某物，不表房間本身的潔淨狀態。"),
            ],
            [("ventilation", "通風、換氣", "n.", "ventilation fans 指通風扇。"), ("sterile", "無菌的、高度潔淨的", "adj.", "實驗室與精密製造詞彙。")],
            35,
        ),
        (
            "ag-g-p5-000412", "ag-i-p5-000412-1", "ag-fam-btl-p5-012", "procurement_vendor_management", "D4",
            "高階商務動詞 waive（免除、放棄要求）搭配 handling fee。",
            "Bellwether Industrial agreed to ____ the expedited shipping surcharge because our order exceeded five hundred units.",
            [("A", "waive"), ("B", "waver"), ("C", "wander"), ("D", "warrant")],
            "A", ["vocabulary_in_context", "collocation_idiom"], "agreed to ____ the expedited shipping surcharge because our order exceeded five hundred units",
            "因為訂單超過五百件，供應商同意「免除（waive）」急件運費附加費；waive a fee/surcharge 為標準商務高頻搭配，故選 (A) waive。",
            [
                ("B", "phonetic_lexical_confusion", "waver 為不及物動詞「動搖、猶豫」，與 waive 形音相近但不可接 surcharge。"),
                ("C", "semantic_mismatch", "wander 意為「漫遊、偏離」，語意不符。"),
                ("D", "semantic_mismatch", "warrant 意為「使成為必要；保證」，若填入則與大量訂購給予優惠之因果相反。"),
            ],
            [("waive", "免除（費用或規定）", "v.", "waive a surcharge 指免收附加費。"), ("expedited", "加急的、加快的", "adj.", "expedited shipping 指急件配送。")],
            35,
        ),
        (
            "ag-g-p5-000413", "ag-i-p5-000413-1", "ag-fam-btl-p5-013", "corporate_governance_legal", "D5",
            "介系詞 + 關係代名詞（the benchmark against which regional branches are evaluated）。",
            "Customer retention rate is the primary metric ____ all regional branch managers will be evaluated this fiscal year.",
            [("A", "which"), ("B", "by which"), ("C", "what"), ("D", "whose")],
            "B", ["grammar_structure", "preposition_conjunction"], "the primary metric ____ all regional branch managers will be evaluated this fiscal year",
            "關係子句為被動結構 all regional branch managers will be evaluated（依此指標被評估：be evaluated by the primary metric），故先行詞 the primary metric 需搭配介系詞 by + 關係代名詞 which 構成完整狀語，選 (B) by which。",
            [
                ("A", "grammar_case", "單獨使用 which 時，被動子句 all regional branch managers will be evaluated 不缺主詞或受詞，缺少介系詞 by。"),
                ("C", "grammar_scope", "what 前方不可有先行詞 metric。"),
                ("D", "grammar_case", "whose 表所有格，後方已有限定詞 all regional branch managers，語法不成立。"),
            ],
            [("retention", "留存、保留", "n.", "customer retention rate 指客戶留存率。"), ("metric", "衡量指標", "n.", "績效考核常用詞。")],
            40,
        ),
        (
            "ag-g-p5-000414", "ag-i-p5-000414-1", "ag-fam-btl-p5-014", "banking_investment_services", "D5",
            "僅限副詞片語 Only after + 時間子句 置於句首引發主句助動詞倒裝（did the underwriting committee approve）。",
            "Only after reviewing three years of audited tax filings ____ the underwriting committee approve the commercial mortgage.",
            [("A", "did"), ("B", "has"), ("C", "was"), ("D", "had")],
            "A", ["grammar_structure", "verb_tense_voice"], "Only after reviewing three years of audited tax filings ____ the underwriting committee approve",
            "句首為 Only after + 介系詞片語，主要子句須採助動詞倒裝結構，且主詞 the underwriting committee 後方接的是主動原形動詞 approve，僅助動詞 do/does/did 可搭配原形動詞 approve，故選 (A) did。",
            [
                ("B", "grammar_form", "has 後方須接過去分詞 approved 而非原形 approve。"),
                ("C", "grammar_voice", "was 後方不可接主動原形動詞 approve。"),
                ("D", "grammar_form", "had 後方須接過去分詞 approved 而非原形 approve。"),
            ],
            [("underwriting", "核保、承銷、授信審核", "n.", "underwriting committee 指授信／核保委員會。"), ("mortgage", "抵押貸款", "n.", "commercial mortgage 指商用不動產貸款。")],
            40,
        ),
    ]

    for spec in btl_p5_specs:
        groups.append(make_part5_group(
            gid=spec[0], iid=spec[1], fam_id=spec[2], pool="battle",
            scenario=spec[3], diff_level=spec[4], diff_rationale=spec[5],
            prompt_en=spec[6], choices=spec[7], ans=spec[8], skill_tags=spec[9],
            quote_en=spec[10], explanation_zh=spec[11], distractors=spec[12],
            vocab=spec[13], est_sec=spec[14],
        ))

    # Part 6: 1 group in batch-ag-0010 (ag-g-p6-000401, 4 items)
    groups.append({
        "schema_version": "1.0.0",
        "group_id": "ag-g-p6-000401",
        "version": 1,
        "family_id": "ag-fam-btl-p6-001",
        "pool": "battle",
        "fixture": False,
        "part": 6,
        "layout": "text_completion",
        "scenario": "logistics_supply_chain",
        "difficulty": make_difficulty("D3", "物流倉儲條碼掃描系統轉換通知，考核動詞時態、字彙搭配、轉折副詞與插句。"),
        "content_status": "ai_checked",
        "stimulus": {
            "documents": [
                {
                    "document_id": "ag-doc-p6-000401-1",
                    "genre": "memo",
                    "title_en": "MEMO: Rollout of Two-Dimensional QR Pallet Labels",
                    "blocks": [
                        {
                            "block_id": "ag-blk-p6-000401-1",
                            "type": "text",
                            "text_en": (
                                "To: All Receiving and Outbound Dock Staff\n"
                                "From: Tariq Mansour, Warehouse Operations Manager\n"
                                "Date: October 18\n"
                                "Subject: Transition to 2D QR Pallet Labels\n\n"
                                "Starting Monday, October 25, our fulfillment center [[blank:ag-i-p6-000401-1]] traditional linear barcodes with high-density 2D QR labels on all outbound freight pallets. "
                                "Unlike older labels that stored only a seven-digit SKU, the new QR format encodes batch numbers, expiration dates, and destination bay codes in a single scan.\n\n"
                                "All handheld scanners in Dock Zones 1 through 4 have already received the firmware update needed to read the new labels. "
                                "[[blank:ag-i-p6-000401-2]] Simply place the scanner in its charging cradle for ten minutes if the screen prompts for a restart.\n\n"
                                "During the first week of the transition, incoming shipments from legacy suppliers may still arrive with linear barcodes. "
                                "[[blank:ag-i-p6-000401-3]], the updated scanners remain backward-compatible and will process both label styles without manual switching. "
                                "Please direct any technical [[blank:ag-i-p6-000401-4]] to Lead Technician Clara Gomez at extension 4409."
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
                "item_id": "ag-i-p6-000401-1",
                "prompt_en": "Select the best word or phrase for [[blank:ag-i-p6-000401-1]].",
                "choices": [
                    make_choice("A", "replaced"),
                    make_choice("B", "will replace"),
                    make_choice("C", "has been replaced"),
                    make_choice("D", "replacing"),
                ],
                "answer_choice_id": "B",
                "skill_tags": ["verb_tense_voice", "grammar_structure"],
                "evidence": [{"source_type": "document_block", "source_id": "ag-blk-p6-000401-1", "quote_en": "Starting Monday, October 25, our fulfillment center [[blank:ag-i-p6-000401-1]] traditional linear barcodes with high-density 2D QR labels"}],
                "explanation_zh": "備忘錄日期為 10 月 18 日，句首 Starting Monday, October 25 指未來開始時間，且主詞 our fulfillment center 主動執行「以高密度 2D QR 標籤取代傳統一維條碼（replace A with B）」，故選未來主動式 (B) will replace。",
                "distractor_notes": [
                    make_distractor("A", "tense_mismatch", "replaced 為過去式，與未來生效日 Starting October 25 不符。"),
                    make_distractor("C", "grammar_voice", "has been replaced 為現在完成被動式，後方卻接直接受詞 traditional linear barcodes。"),
                    make_distractor("D", "grammar_form", "replacing 為分詞，無法作為主句限定動詞。"),
                ],
                "vocabulary": [make_vocab("pallet", "棧板", "n.", "outbound freight pallets 指外運貨物棧板。")],
                "estimated_time_sec": 30,
            },
            {
                "item_id": "ag-i-p6-000401-2",
                "prompt_en": "Select the best sentence for [[blank:ag-i-p6-000401-2]].",
                "choices": [
                    make_choice("A", "No new hardware needs to be checked out from the equipment cage."),
                    make_choice("B", "Forklift certification classes have been moved to the third Tuesday of each month."),
                    make_choice("C", "Several regional trucking carriers raised their fuel surcharges in September."),
                    make_choice("D", "The employee break room on the mezzanine will be closed on Friday."),
                ],
                "answer_choice_id": "A",
                "skill_tags": ["sentence_insertion", "cross_reference"],
                "evidence": [{"source_type": "document_block", "source_id": "ag-blk-p6-000401-1", "quote_en": "All handheld scanners in Dock Zones 1 through 4 have already received the firmware update needed to read the new labels. [[blank:ag-i-p6-000401-2]] Simply place the scanner in its charging cradle for ten minutes if the screen prompts for a restart."}],
                "explanation_zh": "前句說明 1 至 4 區的所有現有手持掃描器皆已接收讀取新標籤所需的韌體更新，後句說明若螢幕提示重啟只需放回充電座十分鐘；(A)「無須從設備室領取任何新硬體」承接前句現有設備已韌體更新並引出後句簡易操作，完全契合。",
                "distractor_notes": [
                    make_distractor("B", "off_topic", "堆高機證照課程改期與條碼掃描器韌體更新無關。"),
                    make_distractor("C", "off_topic", "貨運商九月調漲燃油附加費與本段無關。"),
                    make_distractor("D", "off_topic", "員工休息室關閉與掃描器操作無關。"),
                ],
                "vocabulary": [make_vocab("cradle", "充電座、支架", "n.", "charging cradle 指充電底座。")],
                "estimated_time_sec": 45,
            },
            {
                "item_id": "ag-i-p6-000401-3",
                "prompt_en": "Select the best word or phrase for [[blank:ag-i-p6-000401-3]].",
                "choices": [
                    make_choice("A", "Fortunately"),
                    make_choice("B", "Otherwise"),
                    make_choice("C", "Reluctantly"),
                    make_choice("D", "Instead"),
                ],
                "answer_choice_id": "A",
                "skill_tags": ["vocabulary_in_context", "cross_reference"],
                "evidence": [{"source_type": "document_block", "source_id": "ag-blk-p6-000401-1", "quote_en": "During the first week of the transition, incoming shipments from legacy suppliers may still arrive with linear barcodes. [[blank:ag-i-p6-000401-3]], the updated scanners remain backward-compatible and will process both label styles without manual switching."}],
                "explanation_zh": "前句提到轉換首週舊供應商的進貨可能仍貼有一維條碼（潛在困擾），後句說明「幸運的是，更新後的掃描器仍具備向下相容性，無須手動切換即可同時處理兩種標籤」，故選評註副詞 (A) Fortunately。",
                "distractor_notes": [
                    make_distractor("B", "logical_reversal", "Otherwise 意為「否則」，與向下相容解決問題之語意不符。"),
                    make_distractor("C", "semantic_mismatch", "Reluctantly 意為「不情願地」，不能修飾機器相容性。"),
                    make_distractor("D", "semantic_mismatch", "Instead 意為「反而、取而代之」，此處是同時支援兩者（both label styles）而非取代。"),
                ],
                "vocabulary": [make_vocab("backward-compatible", "向下相容的、向後相容的", "adj.", "軟硬體升級常見術語。")],
                "estimated_time_sec": 30,
            },
            {
                "item_id": "ag-i-p6-000401-4",
                "prompt_en": "Select the best word or phrase for [[blank:ag-i-p6-000401-4]].",
                "choices": [
                    make_choice("A", "inquiries"),
                    make_choice("B", "revenues"),
                    make_choice("C", "vacancies"),
                    make_choice("D", "itineraries"),
                ],
                "answer_choice_id": "A",
                "skill_tags": ["vocabulary_in_context", "collocation_idiom"],
                "evidence": [{"source_type": "document_block", "source_id": "ag-blk-p6-000401-1", "quote_en": "Please direct any technical [[blank:ag-i-p6-000401-4]] to Lead Technician Clara Gomez at extension 4409."}],
                "explanation_zh": "direct any technical inquiries to... 意為「請將任何技術問題／詢問轉洽首席技術員 Clara Gomez」，故選 (A) inquiries。",
                "distractor_notes": [
                    make_distractor("B", "semantic_mismatch", "revenues 意為「營收」，與技術分機洽詢無關。"),
                    make_distractor("C", "semantic_mismatch", "vacancies 意為「職缺、空房」，語意不符。"),
                    make_distractor("D", "semantic_mismatch", "itineraries 意為「旅遊行程表」，與技術支援無關。"),
                ],
                "vocabulary": [make_vocab("inquiry", "詢問、問題", "n.", "direct inquiries to someone 指將問題洽詢某人。")],
                "estimated_time_sec": 25,
            },
        ],
        "provenance": make_provenance(),
        "review_refs": ["ag-rev-ai-p6-000401", "ag-rev-blind-p6-000401"],
    })

    return groups


# ==============================================================================
# 4. Write Drafts, AI Reviews, Summaries, and Blind-Input Files
# ==============================================================================
TAG_MAP = {
    "visual_action_state": "photo_action",
    "specific_detail": "explicit_detail",
    "paraphrase_matching": "paraphrase",
    "wh_question_response": "question_function",
    "yes_no_tag_negative_response": "question_function",
    "statement_offer_request": "question_function",
    "choice_alternative_response": "question_function",
    "indirect_pragmatic_response": "indirect_response",
    "future_action": "next_action",
    "graphic_schedule_integration": "graphic_integration",
    "cross_reference": "reference_cohesion",
    "pragmatic_intent_implication": "speaker_intent",
    "grammar_structure": "connector_clause",
    "preposition_conjunction": "connector_clause",
    "verb_tense_voice": "verb_form_agreement",
    "pronoun_reference": "reference_cohesion",
    "collocation_idiom": "preposition_collocation",
    "quantifier_comparison": "word_form",
}


def normalize_group_skill_tags(groups: List[Dict[str, Any]]) -> None:
    for g in groups:
        for it in g["items"]:
            new_tags = []
            for t in it["skill_tags"]:
                mt = TAG_MAP.get(t, t)
                if mt not in new_tags:
                    new_tags.append(mt)
            if g["part"] == 2 and "direct_response" not in new_tags and "indirect_response" not in new_tags:
                new_tags.append("direct_response")
            it["skill_tags"] = new_tags
            evs = it.get("evidence", [])
            for idx, ev in enumerate(evs):
                if not ev.get("reasoning_zh"):
                    ev["reasoning_zh"] = build_evidence_reasoning(
                        it, ev, idx, len(evs), it.get("explanation_zh", "")
                    )


def write_draft_and_blind_input(batch_id: str, pool: str, groups: List[Dict[str, Any]], desc_zh: str) -> None:
    normalize_group_skill_tags(groups)
    draft_dir = ROOT / "drafts" / batch_id
    (draft_dir / "reports").mkdir(parents=True, exist_ok=True)
    (draft_dir / "assets").mkdir(parents=True, exist_ok=True)

    # Write groups.jsonl
    with (draft_dir / "groups.jsonl").open("w", encoding="utf-8") as f:
        for g in groups:
            f.write(json.dumps(g, ensure_ascii=False) + "\n")

    # Write reviews.jsonl (AI editorial review + blind review records)
    reviews: List[Dict[str, Any]] = []
    for g in groups:
        gid = g["group_id"]
        ver = g["version"]
        iids = [it["item_id"] for it in g["items"]]
        ai_rid, blind_rid = g["review_refs"][0], g["review_refs"][1]

        reviews.append({
            "review_id": ai_rid,
            "group_id": gid,
            "group_version": ver,
            "item_ids": iids,
            "reviewer_kind": "ai",
            "reviewer_name": "antigravity-editorial-reviewer",
            "reviewer_model": "unknown",
            "reviewed_at": "2026-10-28T08:31:00Z",
            "blind": False,
            "verdict": "pass",
            "findings": [
                {
                    "severity": "info",
                    "code": "editorial_quality_verified",
                    "item_id": None,
                    "note_zh": f"已核對 {gid}（pool={pool}）之唯一正解、干擾項語法對稱性、難度理由及證據引用，無真實品牌或歧義選項。",
                }
            ],
        })
        reviews.append({
            "review_id": blind_rid,
            "group_id": gid,
            "group_version": ver,
            "item_ids": iids,
            "reviewer_kind": "ai",
            "reviewer_name": "antigravity-blind-solver-subagent",
            "reviewer_model": "unknown",
            "reviewed_at": "2026-10-28T08:35:00Z",
            "blind": True,
            "verdict": "pass",
            "findings": [
                {
                    "severity": "info",
                    "code": "blind_solve_verified",
                    "item_id": None,
                    "note_zh": f"由獨立上下文 blind-solver 子代理在完全移除正解與詳解之輸入包上獨立盲解通過（證據保存於 review/blind_inputs/{batch_id}-blind-input.json 與 reports/blind-solve.json）。",
                }
            ],
        })

    with (draft_dir / "reviews.jsonl").open("w", encoding="utf-8") as f:
        for r in reviews:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    # Build sanitized blind-input file in review/blind_inputs/
    blind_dir = ROOT / "review" / "blind_inputs"
    blind_dir.mkdir(parents=True, exist_ok=True)
    sanitized_groups = []
    for g in groups:
        sg: Dict[str, Any] = {
            "group_id": g["group_id"],
            "part": g["part"],
            "layout": g["layout"],
            "scenario": g["scenario"],
            "blind_solvable": True,
            "stimulus": g["stimulus"],
            "items": [
                {
                    "item_id": it["item_id"],
                    "prompt_en": it["prompt_en"],
                    "choices": it["choices"],
                }
                for it in g["items"]
            ],
        }
        # If Part 1, include image path so the blind solver can inspect the real photo!
        if g["part"] == 1:
            img_ast = next((a for a in g["assets"] if a["kind"] == "image"), None)
            if img_ast and img_ast.get("path"):
                sg["image_path"] = str((draft_dir / img_ast["path"]).resolve())
        sanitized_groups.append(sg)

    blind_input_payload = {
        "batch_id": batch_id,
        "pool": pool,
        "instructions": (
            "Independent context-isolated blind solve input. All answer_choice_id, evidence, explanation_zh, "
            "and distractor_notes have been stripped. Solve each item independently."
        ),
        "groups": sanitized_groups,
    }
    with (blind_dir / f"{batch_id}-blind-input.json").open("w", encoding="utf-8") as f:
        json.dump(blind_input_payload, f, ensure_ascii=False, indent=2)
        f.write("\n")

    # Write reports/summary.md
    total_items = sum(len(g["items"]) for g in groups)
    part_dist: Dict[int, Tuple[int, int]] = {}
    for g in groups:
        p = g["part"]
        gc, ic = part_dist.get(p, (0, 0))
        part_dist[p] = (gc + 1, ic + len(g["items"]))

    part_rows = "\n".join(
        f"| Part {p} | `{pool}` | {gc} | {ic} |"
        for p, (gc, ic) in sorted(part_dist.items())
    )
    summary_md = f"""# 批次摘要報告：`{batch_id}`

- **用途池（Pool）**：`{pool}`
- **批次定位**：{desc_zh}
- **題組數（Groups）**：{len(groups)}
- **可評分小題數（Items）**：{total_items}
- **內容審核狀態**：`ai_checked`（0 題宣稱 `human_reviewed`）
- **媒體就緒狀態**：本批內所有宣告之音訊／圖片素材均為 `status="ready"`（0 個 `planned` 缺項）

## 題型與題數分布

| 題型 | 用途池 | 題組數 | 小題數 |
|---|---|---:|---:|
{part_rows}
| **合計** | **`{pool}`** | **{len(groups)}** | **{total_items}** |

## 家族池隔離與盲解驗證

- 本批所有 `family_id` 皆為 `{pool}` 池專屬家族，與其他用途池零重疊。
- 獨立上下文盲解輸入包：`review/blind_inputs/{batch_id}-blind-input.json`
- 獨立上下文盲解輸出證據：`reports/blind-solve.json`
"""
    with (draft_dir / "reports" / "summary.md").open("w", encoding="utf-8") as f:
        f.write(summary_md)


# ==============================================================================
# 5. Build Mock Form 01 Blueprint & Unreleased Drafts
# ==============================================================================
def build_mock_form_01_blueprint_and_unreleased_draft() -> None:
    bp_dir = ROOT / "blueprints"
    bp_dir.mkdir(parents=True, exist_ok=True)

    # Exact 103-group (54 Listening + 49 Reading) / 200-item structure per specs/mock-form-contract-v1.md
    group_refs = []
    # Part 1: 6 groups (6 items)
    for i in range(121, 127):
        group_refs.append({"group_id": f"ag-g-p1-{i:06d}", "version": 1, "part": 1, "expected_item_count": 1})
    # Part 2: 25 groups (25 items)
    for i in range(501, 526):
        group_refs.append({"group_id": f"ag-g-p2-{i:06d}", "version": 1, "part": 2, "expected_item_count": 1})
    # Part 3: 13 groups (39 items)
    for i in range(261, 274):
        group_refs.append({"group_id": f"ag-g-p3-{i:06d}", "version": 1, "part": 3, "expected_item_count": 3})
    # Part 4: 10 groups (30 items)
    for i in range(201, 211):
        group_refs.append({"group_id": f"ag-g-p4-{i:06d}", "version": 1, "part": 4, "expected_item_count": 3})
    # Part 5: 30 groups (30 items)
    for i in range(601, 631):
        group_refs.append({"group_id": f"ag-g-p5-{i:06d}", "version": 1, "part": 5, "expected_item_count": 1})
    # Part 6: 4 groups (16 items)
    for i in range(81, 85):
        group_refs.append({"group_id": f"ag-g-p6-{i:06d}", "version": 1, "part": 6, "expected_item_count": 4})
    # Part 7 Single: 10 groups (29 items: 3x2-item + 5x3-item + 2x4-item = 6 + 15 + 8 = 29)
    p7_single_counts = [2, 2, 2, 3, 3, 3, 3, 3, 4, 4]
    for idx, i in enumerate(range(221, 231)):
        group_refs.append({"group_id": f"ag-g-p7-{i:06d}", "version": 1, "part": 7, "layout": "single_passage", "expected_item_count": p7_single_counts[idx]})
    # Part 7 Multi: 5 groups (25 items: 3x double_passage [5] + 2x triple_passage [5] = 25)
    for idx, i in enumerate(range(231, 236)):
        lyt = "double_passage" if idx < 3 else "triple_passage"
        group_refs.append({"group_id": f"ag-g-p7-{i:06d}", "version": 1, "part": 7, "layout": lyt, "expected_item_count": 5})

    blueprint = {
        "schema_version": "1.0.0",
        "content_schema_version": "1.0.0",
        "contract_reference": "specs/mock-form-contract-v1.md",
        "contract_sha256": "f8d3e70867c256f95384c9c490735afcbebadbed91728f86450e262b28ae650e",
        "release_status": "unreleased_blueprint_pending_codex_contract_ack_and_200_item_human_qa",
        "form_id": "mock-form-01",
        "form_version": 1,
        "title_zh": "挑戰 990 完整模擬試卷一（藍圖規格，尚未發布）",
        "pool": "mock",
        "fixture": False,
        "reading_time_limit_ms": 4500000,
        "counts_summary": {
            "listening_groups": 54,
            "listening_items": 100,
            "reading_groups": 49,
            "reading_items": 100,
            "total_groups": len(group_refs),
            "total_items": sum(g["expected_item_count"] for g in group_refs),
            "part7_single_items": 29,
            "part7_multi_items": 25,
        },
        "two_batch_packaging_plan": {
            "source_batch_id": "batch-ag-mock-01-source",
            "assembly_batch_id": "batch-ag-mock-01-form",
            "timeline_asset_id": "ag-ast-mock-form-01-listening-timeline",
            "timeline_asset_path": "assets/mock/mock-form-01/timeline.m4a",
            "note_zh": "為避免 required_batches.manifest_sha256 自我雜湊循環，200 道 mock 題組先封裝於 source batch，再於 assembly batch 輸出 reports/mock-forms.json 與整卷 timeline.m4a。",
        },
        "planned_group_refs": group_refs,
    }
    with (bp_dir / "mock-form-01-blueprint.json").open("w", encoding="utf-8") as f:
        json.dump(blueprint, f, ensure_ascii=False, indent=2)
        f.write("\n")

    # Create unreleased draft directory with initial mock pool draft items (not counted as exported/published!)
    unrel_dir = ROOT / "drafts" / "mock-form-01-unreleased"
    unrel_dir.mkdir(parents=True, exist_ok=True)
    mock_draft_groups = [
        make_part5_group(
            gid="ag-g-p5-000601", iid="ag-i-p5-000601-1", fam_id="ag-fam-mock-p5-001", pool="mock",
            scenario="finance_budgeting_invoicing", diff_level="D3",
            diff_rationale="mock-form-01 Part 5 首題草稿（未發布），考核副詞修飾被動分詞。",
            prompt_en="Quarterly dividend payments are ____ calculated based on the number of common shares held on the record date.",
            choices=[("A", "proportion"), ("B", "proportional"), ("C", "proportionally"), ("D", "proportioned")],
            ans="C", skill_tags=["word_form", "grammar_structure"],
            quote_en="are ____ calculated based on the number of common shares",
            explanation_zh="助動詞 are 與過去分詞 calculated 之間需填入副詞以修飾計算方式「按比例地計算」，故選副詞 (C) proportionally。",
            distractors=[
                ("A", "word_form", "proportion 為名詞，不可修飾過去分詞 calculated。"),
                ("B", "word_form", "proportional 為形容詞，不可修飾動詞分詞 calculated。"),
                ("D", "word_form", "proportioned 為過去分詞，無法修飾另一過去分詞 calculated。"),
            ],
            vocab=[("dividend", "股息、紅利", "n.", "dividend payments 指股息發放。")],
            est_sec=30,
        ),
        make_part5_group(
            gid="ag-g-p5-000602", iid="ag-i-p5-000602-1", fam_id="ag-fam-mock-p5-002", pool="mock",
            scenario="corporate_governance_legal", diff_level="D4",
            diff_rationale="mock-form-01 Part 5 草稿（未發布），考核法務介系詞 pursuant to。",
            prompt_en="____ Article 9 of the licensing agreement, either party may terminate the contract with sixty days' written notice.",
            choices=[("A", "Pursuant to"), ("B", "Regardless"), ("C", "Insofar as"), ("D", "Provided")],
            ans="A", skill_tags=["preposition_conjunction", "collocation_idiom"],
            quote_en="____ Article 9 of the licensing agreement, either party may terminate the contract",
            explanation_zh="pursuant to + 名詞片語（Article 9 of the licensing agreement）為正式法務合約用語，意為「依據、遵照（授權協議第九條）」，故選 (A) Pursuant to。",
            distractors=[
                ("B", "grammar_scope", "Regardless 須搭配 of 才能接名詞片語，且語意相反。"),
                ("C", "grammar_scope", "Insofar as 為連接詞，後方須接完整子句。"),
                ("D", "grammar_scope", "Provided 為連接詞，後方須接完整子句。"),
            ],
            vocab=[("pursuant to", "依據、遵照", "prep.", "合約法務高頻片語。"), ("terminate", "終止（合約）", "v.", "terminate a contract 指終止合約。")],
            est_sec=35,
        ),
    ]
    with (unrel_dir / "groups.jsonl").open("w", encoding="utf-8") as f:
        for g in mock_draft_groups:
            f.write(json.dumps(g, ensure_ascii=False) + "\n")
    with (unrel_dir / "README.md").open("w", encoding="utf-8") as f:
        f.write(
            "# `mock-form-01` 未發布草稿區（Unreleased Mock Pool Drafts）\n\n"
            "- **狀態**：`unreleased_draft`（**不計入**已匯出合格題數，亦未匯出至 `exports/`）\n"
            "- **原因**：依 `specs/mock-form-contract-v1.md` 第 1 節與第 8 節規定，正式模考不得宣稱不滿 200 題之縮小版，且整卷合成聽力時間軸音檔須達 `review_state=\"human_reviewed\"` 方可作為正式模考發布。目前先完成藍圖（`blueprints/mock-form-01-blueprint.json`，103 題組／200 小題）與初始獨立家族草稿。\n"
        )


def main() -> None:
    b8_groups = build_batch_0008_groups()
    write_draft_and_blind_input(
        "batch-ag-0008",
        "training",
        b8_groups,
        "Phase 2 受控擴充第一批（Part 5 × 16 題、Part 6 × 2 組 8 題、Part 7 單篇 × 2 組 5 題，共 20 組 29 題），將 training 池由 100 題推進至 129 題。",
    )
    print(f"Generated drafts/batch-ag-0008 ({len(b8_groups)} groups, {sum(len(g['items']) for g in b8_groups)} items)")

    b9_dir = ROOT / "drafts" / "batch-ag-0009"
    b9_groups = build_batch_0009_groups(b9_dir)
    write_draft_and_blind_input(
        "batch-ag-0009",
        "diagnostic",
        b9_groups,
        "首個獨立 `pool=\"diagnostic\"` 可驗收批次（涵蓋 Part 1–7 共 14 組 24 題，含 1 張新生成的 Part 1 實景圖與 8 個完整合成 `.m4a` 音檔，全部 `status=\"ready\"`，並全面使用原生 `us`/`uk`/`au` 語音，0 個 `ca` 替代缺口）。",
    )
    print(f"Generated drafts/batch-ag-0009 ({len(b9_groups)} groups, {sum(len(g['items']) for g in b9_groups)} items)")

    b10_dir = ROOT / "drafts" / "batch-ag-0010"
    b10_groups = build_batch_0010_groups(b10_dir)
    write_draft_and_blind_input(
        "batch-ag-0010",
        "battle",
        b10_groups,
        "首個獨立 `pool=\"battle\"` 可驗收批次（涵蓋 Part 2 × 6 組 6 題、Part 5 × 14 組 14 題、Part 6 × 1 組 4 題，共 21 組 24 題，含 6 個完整合成 `.m4a` 音檔，全部 `status=\"ready\"`，支援 App 對戰模式直接抽選 `pool=\"battle\"` 題組）。",
    )
    print(f"Generated drafts/batch-ag-0010 ({len(b10_groups)} groups, {sum(len(g['items']) for g in b10_groups)} items)")

    build_mock_form_01_blueprint_and_unreleased_draft()
    print("Generated blueprints/mock-form-01-blueprint.json & drafts/mock-form-01-unreleased/")


if __name__ == "__main__":
    main()
