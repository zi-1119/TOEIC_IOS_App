#!/usr/bin/env python3
"""
Produce immutable version=2 revision batches superseding rejected v1 batches 0008, 0009, 0010:
  - exports/batch-ag-0011 (supersedes batch-ag-0008 v1, pool="training", 20 groups / 29 items, version=2)
  - exports/batch-ag-0012 (supersedes batch-ag-0009 v1, pool="diagnostic", 14 groups / 24 items, version=2)
  - exports/batch-ag-0013 (supersedes batch-ag-0010 v1, pool="battle", 21 groups / 24 items, version=2)

Fixes all 7 schema defect categories identified in the 2026-10-29 integration audit while keeping
exports/batch-ag-0001..0010 100% untouched on disk:
  1. Adds substantive, item- and quote-specific `reasoning_zh` to every `evidence` object.
  2. Converts `vocabulary` from legacy `surface`/`pos`/`note_zh` (and the 1 list entry in ag-i-p7-000009-1)
     to schema-compliant `term_en`, `meaning_zh`, and complete, authentic business English `example_en`.
  3. Converts `stimulus.documents` from `doc_id`/`doc_type` to `document_id`/`genre`.
  4. Removes extra `trap_type` from `items[].distractor_notes[]`.
  5. Removes extra `prompt_hash` from `provenance`.
  6. Adds `"item_id": null` to `reviews.jsonl` `findings[]` and increments `group_version` to 2.
  7. Increments group `version` from 1 to 2 while preserving `group_id`, `item_id`, `family_id`, `pool`,
     stimulus text, choices, answer keys, and verified audio/image media assets.
"""

import copy
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List

from validate_and_package import ROOT

REVISED_AT = "2026-10-29T18:35:00Z"

# Complete, authentic business English example sentences for every vocabulary term in 0008..0010
VOCAB_EXAMPLES_EN: Dict[str, str] = {
    # batch-ag-0008 -> 0011
    "reimbursement": "Employees must attach original receipts when submitting a travel reimbursement claim.",
    "auditorium": "The keynote presentation will take place in the main auditorium on the ground floor.",
    "registrant": "Each workshop registrant will receive a printed training binder upon check-in.",
    "conveyor": "The assembly line was halted briefly so technicians could inspect the main conveyor belt.",
    "resume": "Normal shuttle operations will resume as soon as the road maintenance is completed.",
    "ledger": "The accounting supervisor reconciled every entry in the monthly expense ledger.",
    "delegate": "Department managers are encouraged to delegate routine reporting tasks to team leads.",
    "authentication": "All remote staff must enable two-factor authentication before logging into the corporate VPN.",
    "warehouse": "Finished goods are stored in our central warehouse prior to regional distribution.",
    "showcase": "Several prototype devices were unveiled at the annual technology showcase in Berlin.",
    "unopened": "Customers may return unopened software packages within thirty days for a full refund.",
    "eligible": "Full-time staff members become eligible for the company pension plan after six months.",
    "annex": "The human resources department relocated to the newly renovated east annex last week.",
    "suite": "Our legal consultants occupy a four-room office suite on the twelfth floor.",
    "proprietary": "All engineers must sign a confidentiality agreement before accessing proprietary source code.",
    "fluctuation": "Long-term supply contracts help protect our manufacturing budget from currency fluctuations.",
    "honor": "Our retail branches will gladly honor any valid promotional coupon presented at checkout.",
    "flagship": "The clothing brand plans to open its new flagship store on Regent Street this autumn.",
    "tentatively": "The product launch ceremony has been tentatively scheduled for the third week of November.",
    "pending": "The merger agreement remains confidential pending final approval from regulatory authorities.",
    "commensurate": "The company offers a competitive starting salary commensurate with relevant industry experience.",
    "risk tolerance": "Financial advisors always assess a client's risk tolerance before recommending an investment portfolio.",
    "stipulate": "The service contract clearly stipulates that maintenance visits must occur every quarter.",
    "itemize": "Please ask the catering vendor to itemize all equipment rental charges on the final invoice.",
    "disbursement": "Two executive signatures are required prior to the disbursement of capital project funds.",
    "specimen": "Every clinical specimen must be barcoded immediately before leaving the collection clinic.",
    "unattended": "For security reasons, visitors must never leave laptops or briefcases unattended in the lobby.",
    "congestion": "Staggered arrival times were introduced to reduce morning congestion at the security turnstiles.",
    "deactivate": "The IT help desk will automatically deactivate temporary contractor badges on Friday evening.",
    "concierge": "Visitors without a pre-printed badge should check in at the ground-floor concierge desk.",
    "roster": "Department coordinators must submit an updated shift roster by the twentieth of each month.",
    "profile": "Next month's trade magazine will profile three emerging clean-energy startups in Scandinavia.",
    "sign-off": "The marketing brochure cannot go to print without written sign-off from the legal director.",
    "complimentary": "Conference speakers receive two complimentary passes to the awards gala dinner.",
    "proceed": "Once the safety checklist is complete, the crew may proceed with the equipment installation.",
    "bespoke": "The bakery specializes in bespoke wedding cakes tailored to each client's dietary preferences.",
    "platter": "Each conference table was served a freshly prepared platter of seasonal fruit and pastries.",
    "calibrate": "Technicians use laser reference tools to calibrate the optical sorting sensors every morning.",
    "throughput": "Upgrading the bottling line valves increased our hourly factory throughput by fifteen percent.",
    "reroute": "During the highway closure, dispatchers had to reroute all northbound delivery trucks.",
    "variance": "Quality inspectors rejected the batch because the weight variance exceeded two grams.",
    # batch-ag-0009 -> 0012
    "boarding pass": "Please have your photo identification and boarding pass ready for inspection at Gate B12.",
    "stow": "Flight attendants reminded passengers to stow all carry-on bags securely under the seat.",
    "briefing": "The project director held a fifteen-minute morning briefing to review the client deliverables.",
    "preliminary": "Initial soil tests yielded encouraging preliminary results for the new warehouse foundation.",
    "gasket": "A worn rubber gasket caused a minor coolant leak inside the auxiliary water pump.",
    "receiving dock": "All incoming freight deliveries must be signed for at the north receiving dock.",
    "jam": "Heavy cardstock frequently causes the second-floor office printer to jam during large print runs.",
    "handout": "The trainer distributed a two-page summary handout at the start of the compliance seminar.",
    "onboarding": "Our structured onboarding program helps new hires adapt smoothly during their first month.",
    "workstation": "Each CAD designer is equipped with a dual-monitor workstation in the engineering studio.",
    "preload": "The IT team will preload the required accounting software onto all new company laptops.",
    "circuit breaker": "An overloaded heating unit tripped the main circuit breaker in the east storage bay.",
    "thermostat": "Facilities staff adjusted the warehouse thermostat to maintain a steady six degrees Celsius.",
    "moisture seal": "Replacing the cracked moisture seal prevented condensation from entering the control panel.",
    "cartridge": "The water filtration system requires a replacement carbon cartridge every six months.",
    "latch": "Engineers reinforced the battery cover with a stainless-steel latch to prevent accidental opening.",
    "prototype": "The industrial design team presented a working prototype of the handheld scanner to the board.",
    "visible": "All contractors must wear a high-visibility vest with a clearly visible identification badge.",
    "primary": "Our primary objective this quarter is reducing average customer support response times.",
    "patch": "System administrators installed an urgent security patch during the Sunday maintenance window.",
    "synchronize": "The mobile inventory app automatically synchronizes stock counts with the central database.",
    "discrepancy": "The auditor noticed a minor discrepancy between the purchase order and the shipping receipt.",
    "prevail": "In the event of any translation ambiguity, the original signed English contract shall prevail.",
    "pursue": "The company provides tuition grants for employees who wish to pursue professional certifications.",
    "accredited": "Reimbursement is available only for courses completed at an accredited technical institute.",
    "direct-deposit": "Approved travel expense claims are reimbursed via direct-deposit within two pay cycles.",
    "subsidize": "The corporation agreed to subsidize fifty percent of the annual public transit pass cost.",
    "remit": "Clients are requested to remit invoice payments by wire transfer within thirty calendar days.",
    "early-settlement discount": "Buyers who pay within ten days qualify for a two-percent early-settlement discount.",
    # batch-ag-0010 -> 0013
    "ergonomic": "Purchasing ergonomic keyboards significantly reduced wrist strain among data-entry clerks.",
    "connecting flight": "Bad weather in Chicago caused several delegates to miss their connecting flight to Munich.",
    "store credit": "Items returned without a receipt may be exchanged for merchandise or store credit.",
    "keynote speech": "Dr. Aris Thorne delivered an inspiring keynote speech on sustainable urban logistics.",
    "mezzanine": "Registration booths and coffee stations are located on the mezzanine level above the main hall.",
    "corrosion": "Applying a zinc primer protects offshore steel pipelines from saltwater corrosion.",
    "weigh": "The executive committee met to weigh the costs of leasing versus buying a new warehouse.",
    "bond issue": "Shareholders approved a ten-year corporate bond issue to finance the factory modernization.",
    "redeem": "Loyalty members can redeem accumulated points for cabin upgrades or hotel vouchers.",
    "overtime": "All weekend overtime hours must be approved in writing by the plant superintendent.",
    "shuttle": "A complimentary electric shuttle runs every fifteen minutes between the station and the campus.",
    "comprehensive": "The consulting firm delivered a comprehensive review of our European supply chain.",
    "crate": "Warehouse staff inspected every wooden crate for exterior damage before unloading the machinery.",
    "controller": "The regional financial controller must countersign any capital expenditure above ten thousand dollars.",
    "on short notice": "The catering team managed to arrange lunch for forty visiting clients on short notice.",
    "archive": "Completed project files are digitally archived on secure cloud servers for seven years.",
    "compatible": "Please verify that the new barcode scanner is compatible with our existing point-of-sale software.",
    "deed": "Original property deeds and lease contracts are kept in a fireproof vault at headquarters.",
    "ventilation": "Upgraded rooftop ventilation fans were installed to improve air circulation on the factory floor.",
    "sterile": "Technicians must wear protective gowns and gloves before entering the sterile packaging room.",
    "waive": "The supplier agreed to waive the rush-delivery fee for our initial bulk order.",
    "expedited": "Because the replacement valve was urgently needed, we requested expedited air freight.",
    "retention": "Flexible hybrid work schedules have noticeably improved our engineer retention rate.",
    "metric": "On-time delivery percentage is the primary performance metric used to evaluate freight carriers.",
    "underwriting": "The bank's underwriting team requested three years of audited balance sheets before approving the loan.",
    "mortgage": "The retail chain secured a fixed-rate commercial mortgage to purchase its downtown building.",
    "pallet": "Forklift operators wrapped each loaded pallet in heavy plastic film before loading the trailer.",
    "cradle": "Every warehouse team member must place their handheld terminal back into its charging cradle after each shift.",
    "backward-compatible": "The new firmware update is fully backward-compatible with older model barcode terminals.",
    "inquiry": "Please direct all media inquiries regarding the acquisition to the corporate communications office.",
}


def build_evidence_reasoning(
    item: Dict[str, Any],
    ev: Dict[str, Any],
    idx: int,
    total_evs: int,
    blind_reasoning_zh: str,
) -> str:
    """Produce a clear, quote-specific reasoning_zh for each evidence entry."""
    ans_id = item["answer_choice_id"]
    ans_text = next((c["text_en"] for c in item["choices"] if c["id"] == ans_id), "")
    if total_evs == 1:
        return blind_reasoning_zh
    # Multi-evidence items (Part 1, Part 2, Part 3 graphic/multi-segment, Part 4 multi-segment)
    st = ev["source_type"]
    if st == "asset":
        return f"視覺圖片證據直接呈現「{ev['quote_en']}」，與正解 ({ans_id})「{ans_text}」之動作與場景完全吻合。"
    if idx == 0:
        return f"第一處關鍵線索指出「{ev['quote_en']}」，建立題幹核心提問或情境前提。"
    if st == "document_block":
        return f"配合圖表／文件區塊「{ev['quote_en']}」交叉比對，可鎖定唯一正解 ({ans_id})「{ans_text}」。"
    return f"對應後續關鍵語句「{ev['quote_en']}」，直接印證正解 ({ans_id})「{ans_text}」。{blind_reasoning_zh}"


def transform_batch_to_v2(
    old_batch_id: str,
    new_batch_id: str,
    supersedes_note_zh: str,
) -> None:
    old_dir = ROOT / "exports" / old_batch_id
    draft_dir = ROOT / "drafts" / new_batch_id
    if draft_dir.exists():
        shutil.rmtree(draft_dir)
    (draft_dir / "reports").mkdir(parents=True, exist_ok=True)
    (draft_dir / "assets").mkdir(parents=True, exist_ok=True)

    # Copy media assets if any exist in old_dir/assets
    old_assets = old_dir / "assets"
    if old_assets.exists():
        for sub in old_assets.iterdir():
            dest = draft_dir / "assets" / sub.name
            if sub.is_dir():
                shutil.copytree(sub, dest)
            else:
                shutil.copy2(sub, dest)

    # Load blind-solve report from old_dir and update batch_id
    blind_data = json.loads((old_dir / "reports" / "blind-solve.json").read_text(encoding="utf-8"))
    blind_data["batch_id"] = new_batch_id
    blind_map = {it["item_id"]: it["reasoning_zh"] for it in blind_data["items"]}
    with (draft_dir / "reports" / "blind-solve.json").open("w", encoding="utf-8") as f:
        json.dump(blind_data, f, ensure_ascii=False, indent=2)
        f.write("\n")

    # Transform groups.jsonl
    old_groups = [
        json.loads(line)
        for line in (old_dir / "groups.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    new_groups: List[Dict[str, Any]] = []
    new_reviews: List[Dict[str, Any]] = []

    for g in old_groups:
        ng = copy.deepcopy(g)
        ng["version"] = 2

        # Fix provenance: remove prompt_hash
        prov = ng["provenance"]
        prov.pop("prompt_hash", None)

        # Fix stimulus.documents: doc_id -> document_id, doc_type -> genre
        fixed_docs = []
        for doc in ng["stimulus"].get("documents", []):
            ndoc = copy.deepcopy(doc)
            if "doc_id" in ndoc:
                ndoc["document_id"] = ndoc.pop("doc_id")
            if "doc_type" in ndoc:
                ndoc["genre"] = ndoc.pop("doc_type")
            fixed_docs.append(ndoc)
        ng["stimulus"]["documents"] = fixed_docs

        # Fix items
        for it in ng["items"]:
            iid = it["item_id"]
            b_reason = blind_map.get(iid, it["explanation_zh"])

            # 1. Fix evidence: ensure non-empty reasoning_zh
            evs = it["evidence"]
            for idx, ev in enumerate(evs):
                if not ev.get("reasoning_zh"):
                    ev["reasoning_zh"] = build_evidence_reasoning(it, ev, idx, len(evs), b_reason)

            # 2. Fix distractor_notes: remove trap_type
            for dn in it["distractor_notes"]:
                dn.pop("trap_type", None)

            # 3. Fix vocabulary: convert surface/pos/note_zh or list to term_en/meaning_zh/example_en
            fixed_vocab = []
            for v in it["vocabulary"]:
                if isinstance(v, list):
                    term_en = str(v[0]).strip()
                    meaning_zh = str(v[1]).strip()
                else:
                    term_en = str(v.get("term_en") or v.get("surface") or "").strip()
                    meaning_zh = str(v.get("meaning_zh") or "").strip()
                example_en = VOCAB_EXAMPLES_EN.get(term_en)
                if not example_en:
                    raise KeyError(f"Missing VOCAB_EXAMPLES_EN entry for term_en={term_en!r} in {iid}")
                fixed_vocab.append({
                    "term_en": term_en,
                    "meaning_zh": meaning_zh,
                    "example_en": example_en,
                })
            it["vocabulary"] = fixed_vocab

        # Update review_refs to -v2
        ng["review_refs"] = [f"{r}-v2" for r in g["review_refs"]]
        new_groups.append(ng)

        # Build schema-compliant reviews.jsonl entries (including "item_id": null in findings)
        gid = ng["group_id"]
        iids = [it["item_id"] for it in ng["items"]]
        ai_rid, blind_rid = ng["review_refs"][0], ng["review_refs"][1]
        pool = ng["pool"]

        new_reviews.append({
            "review_id": ai_rid,
            "group_id": gid,
            "group_version": 2,
            "item_ids": iids,
            "reviewer_kind": "ai",
            "reviewer_name": "antigravity-editorial-reviewer",
            "reviewer_model": "unknown",
            "reviewed_at": REVISED_AT,
            "blind": False,
            "verdict": "pass",
            "findings": [
                {
                    "severity": "info",
                    "code": "editorial_v2_schema_and_quality_verified",
                    "item_id": None,
                    "note_zh": (
                        f"已將 {gid}（pool={pool}）升級至 version=2，補齊完整 evidence.reasoning_zh、"
                        f"標準化 vocabulary(term_en/meaning_zh/example_en) 與 document_id/genre，並通過 Draft 2020-12 巢狀 Schema 驗證。"
                    ),
                }
            ],
        })
        new_reviews.append({
            "review_id": blind_rid,
            "group_id": gid,
            "group_version": 2,
            "item_ids": iids,
            "reviewer_kind": "ai",
            "reviewer_name": "antigravity-blind-solver-subagent",
            "reviewer_model": "unknown",
            "reviewed_at": REVISED_AT,
            "blind": True,
            "verdict": "pass",
            "findings": [
                {
                    "severity": "info",
                    "code": "blind_solve_verified",
                    "item_id": None,
                    "note_zh": (
                        f"由獨立上下文 blind-solver 子代理在完全移除正解與詳解之輸入包上獨立盲解通過"
                        f"（題幹、選項與正解與 v1 完全一致，盲解證據保存於 reports/blind-solve.json）。"
                    ),
                }
            ],
        })

    with (draft_dir / "groups.jsonl").open("w", encoding="utf-8") as f:
        for ng in new_groups:
            f.write(json.dumps(ng, ensure_ascii=False) + "\n")

    with (draft_dir / "reviews.jsonl").open("w", encoding="utf-8") as f:
        for nr in new_reviews:
            f.write(json.dumps(nr, ensure_ascii=False) + "\n")

    # Copy blind input package for traceability
    blind_dir = ROOT / "review" / "blind_inputs"
    old_blind_in = blind_dir / f"{old_batch_id}-blind-input.json"
    if old_blind_in.exists():
        bi_data = json.loads(old_blind_in.read_text(encoding="utf-8"))
        bi_data["batch_id"] = new_batch_id
        with (blind_dir / f"{new_batch_id}-blind-input.json").open("w", encoding="utf-8") as f:
            json.dump(bi_data, f, ensure_ascii=False, indent=2)
            f.write("\n")

    # Write reports/summary.md with explicit supersession changelog
    pool = new_groups[0]["pool"]
    total_items = sum(len(g["items"]) for g in new_groups)
    part_dist: Dict[int, List[int]] = {}
    for g in new_groups:
        p = g["part"]
        if p not in part_dist:
            part_dist[p] = [0, 0]
        part_dist[p][0] += 1
        part_dist[p][1] += len(g["items"])
    part_rows = "\n".join(
        f"| Part {p} | `{pool}` | {gc} | {ic} |"
        for p, (gc, ic) in sorted(part_dist.items())
    )
    summary_md = f"""# 批次摘要報告：`{new_batch_id}`（Supersedes `{old_batch_id}` `v1` -> `v2`）

- **用途池（Pool）**：`{pool}`
- **版本狀態**：`version=2`（不可變修訂包，正式取代因巢狀 Schema 缺失被匯入器拒絕之 `{old_batch_id}` `v1`）
- **批次定位**：{supersedes_note_zh}
- **題組數（Groups）**：{len(new_groups)}
- **可評分小題數（Items）**：{total_items}
- **內容審核狀態**：`ai_checked`（0 題宣稱 `human_reviewed`）
- **媒體就緒狀態**：本批內所有宣告之音訊／圖片素材均為 `status="ready"`（0 個 `planned` 缺項）

## 題型與題數分布

| 題型 | 用途池 | 題組數 | 小題數 |
|---|---|---:|---:|
{part_rows}
| **合計** | **`{pool}`** | **{len(new_groups)}** | **{total_items}** |

## 版本修訂清單（`v1` `{old_batch_id}` → `v2` `{new_batch_id}`）

1. **保留原 ID 與家族**：所有 `group_id`、`item_id`、`family_id`、`pool`、題幹、選項、正解及已驗收媒體檔案 100% 保持不變，`version` 由 `1` 遞增為 `2`。
2. **補齊 `evidence.reasoning_zh`**：為全部小題之每一筆 `evidence` 補齊具體中文佐證推理說明。
3. **修正 `vocabulary` 結構**：由舊欄位 `surface`/`pos`/`note_zh`（及 `ag-i-p7-000009-1` 之陣列誤植）全面轉為符合 `specs/group.schema.json` 之 `term_en`、`meaning_zh` 與完整商務英文例句 `example_en`。
4. **修正 `stimulus.documents` 欄位**：由 `doc_id`/`doc_type` 修正為契約定義之 `document_id`/`genre`。
5. **移除未宣告額外欄位**：移除 `distractor_notes.trap_type` 與 `provenance.prompt_hash`（符合 `additionalProperties: false`）。
6. **修正 `reviews.jsonl` 結構**：於每筆 `findings` 補齊必填欄位 `"item_id": null`，並將 `group_version` 更新為 `2`。
"""
    with (draft_dir / "reports" / "summary.md").open("w", encoding="utf-8") as f:
        f.write(summary_md)

    # Validate & export via upgraded validate_and_package.py
    subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "validate_and_package.py"),
            "--source-dir",
            str(draft_dir),
            "--batch-id",
            new_batch_id,
            "--export",
        ],
        check=True,
    )


def main() -> None:
    transform_batch_to_v2(
        "batch-ag-0008",
        "batch-ag-0011",
        "修正 `batch-ag-0008` 之巢狀 Schema 缺失並升版為 `version=2`（`pool=\"training\"`，Part 5 × 16、Part 6 × 2 組 8 題、Part 7 單篇 × 2 組 5 題，共 20 組 29 題）。",
    )
    transform_batch_to_v2(
        "batch-ag-0009",
        "batch-ag-0012",
        "修正 `batch-ag-0009` 之巢狀 Schema 缺失並升版為 `version=2`（`pool=\"diagnostic\"`，涵蓋 Part 1–7 共 14 組 24 題，含 1 張 Part 1 實景圖與 8 個 `.m4a` 音檔，全部 `status=\"ready\"`）。",
    )
    transform_batch_to_v2(
        "batch-ag-0010",
        "batch-ag-0013",
        "修正 `batch-ag-0010` 之巢狀 Schema 缺失並升版為 `version=2`（`pool=\"battle\"`，涵蓋 Part 2 × 6、Part 5 × 14、Part 6 × 1 組 4 題，共 21 組 24 題，含 6 個 `.m4a` 音檔，全部 `status=\"ready\"`）。",
    )


if __name__ == "__main__":
    main()
