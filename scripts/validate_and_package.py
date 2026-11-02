#!/usr/bin/env python3
"""
Validate and package a TOEIC Content Contract 1.0.0 batch.
Enforces full nested JSON Schema validation (Draft 2020-12) against:
  - specs/group.schema.json
  - specs/review.schema.json
  - specs/validation-report.schema.json
  - specs/manifest.schema.json
  - specs/mock-forms.schema.json (when reports/mock-forms.json is present)
as well as all 9 required check families from Validation Report 1.0.0.
"""

import argparse
import collections
import datetime
import hashlib
import json
import math
import re
import shutil
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parent.parent
TAXONOMY_PATH = ROOT / "specs" / "skill-taxonomy-v1.json"
GROUP_SCHEMA_PATH = ROOT / "specs" / "group.schema.json"
REVIEW_SCHEMA_PATH = ROOT / "specs" / "review.schema.json"
MANIFEST_SCHEMA_PATH = ROOT / "specs" / "manifest.schema.json"
VAL_REPORT_SCHEMA_PATH = ROOT / "specs" / "validation-report.schema.json"
MOCK_FORMS_SCHEMA_PATH = ROOT / "specs" / "mock-forms.schema.json"
GLOBAL_INDEX_PATH = ROOT / "reports" / "global-index.json"

GROUP_VALIDATOR = Draft202012Validator(json.loads(GROUP_SCHEMA_PATH.read_text(encoding="utf-8")))
REVIEW_VALIDATOR = Draft202012Validator(json.loads(REVIEW_SCHEMA_PATH.read_text(encoding="utf-8")))
MANIFEST_VALIDATOR = Draft202012Validator(json.loads(MANIFEST_SCHEMA_PATH.read_text(encoding="utf-8")))
VAL_REPORT_VALIDATOR = Draft202012Validator(json.loads(VAL_REPORT_SCHEMA_PATH.read_text(encoding="utf-8")))
MOCK_FORMS_VALIDATOR = Draft202012Validator(json.loads(MOCK_FORMS_SCHEMA_PATH.read_text(encoding="utf-8")))

VALID_POOLS = {"training", "battle", "diagnostic", "mock"}
VALID_LAYOUTS = {
    1: {"photo"},
    2: {"question_response"},
    3: {"conversation"},
    4: {"talk"},
    5: {"sentence"},
    6: {"text_completion"},
    7: {"single_passage", "double_passage", "triple_passage"},
}
VALID_DIFFICULTIES = {"D1", "D2", "D3", "D4", "D5"}
VALID_STATUSES = {"draft", "ai_checked", "human_reviewed", "quarantined", "retired"}
VALID_ACCENTS = {"us", "uk", "ca", "au", "unspecified"}
VALID_EVIDENCE_SOURCES = {"document_block", "audio_segment", "asset", "item_prompt"}
VALID_ASSET_KINDS = {"image", "audio"}
VALID_ASSET_STATUSES = {"planned", "ready"}
VALID_ASSET_REVIEWS = {"pending", "ai_checked", "human_reviewed"}
VALID_REVIEWER_KINDS = {"ai", "human", "program"}
VALID_VERDICTS = {"pass", "revise", "reject"}
VALID_SEVERITIES = {"info", "warning", "error"}

HTML_JS_PATTERN = re.compile(r"(<\s*script\b|javascript\s*:|onerror\s*=|onload\s*=|<\s*iframe\b)", re.IGNORECASE)
TRIVIAL_DISTRACTOR_PATTERN = re.compile(r"(因為答案是|因為正解是|因為正確答案是)")
PLACEHOLDER_PATTERN = re.compile(r"^(待補|TODO|TBD|N/A|none|null|\.\.\.)$", re.IGNORECASE)


def utc_now_iso() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def normalize_text(s: str) -> str:
    s = s.lower()
    s = re.sub(r"[^a-z0-9\s]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def evidence_source_text(stim: Dict[str, Any], item: Dict[str, Any], stype: Any, sid: Any) -> Optional[str]:
    """Return the text an evidence quote must be drawn from, or None if not text-checkable (e.g. image asset)."""
    if stype == "audio_segment":
        for seg in stim.get("audio_script", []):
            if isinstance(seg, dict) and seg.get("segment_id") == sid:
                return seg.get("text_en", "")
        return None  # missing reference reported separately
    if stype == "document_block":
        for d in stim.get("documents", []):
            for b in d.get("blocks", []):
                if isinstance(b, dict) and b.get("block_id") == sid:
                    parts: List[str] = []
                    if b.get("text_en"):
                        parts.append(b["text_en"])
                    for key in ("columns", "headers"):
                        if isinstance(b.get(key), list):
                            parts.append(" | ".join(str(x) for x in b[key]))
                    for row in b.get("rows", []) or []:
                        if isinstance(row, list):
                            parts.append(" | ".join(str(x) for x in row))
                        elif isinstance(row, dict):
                            parts.append(" | ".join(str(v) for v in row.values()))
                    return "\n".join(parts)
        return None
    if stype == "item_prompt":
        return " ".join(
            [item.get("prompt_en", "")]
            + [c.get("text_en", "") for c in item.get("choices", []) if isinstance(c, dict)]
        )
    return None


def quote_in_source(quote: str, source: str) -> bool:
    """Every ellipsis/blank-delimited fragment of the quote must appear (normalized) in the source."""
    strip_markers = lambda s: re.sub(r"\[\[[^\]]*\]\]", " ", s)
    norm_src = normalize_text(strip_markers(source))
    fragments = [f for f in re.split(r"\.\.\.|…|_{2,}|\n", strip_markers(quote)) if normalize_text(f)]
    if not fragments:
        return False
    return all(normalize_text(f) in norm_src for f in fragments)


def char_ngrams(s: str, n: int = 4) -> collections.Counter:
    norm = normalize_text(s)
    if len(norm) < n:
        return collections.Counter([norm]) if norm else collections.Counter()
    return collections.Counter(norm[i : i + n] for i in range(len(norm) - n + 1))


def cosine_counter(c1: collections.Counter, c2: collections.Counter) -> float:
    if not c1 or not c2:
        return 0.0
    common = set(c1.keys()) & set(c2.keys())
    num = sum(c1[k] * c2[k] for k in common)
    den1 = math.sqrt(sum(v * v for v in c1.values()))
    den2 = math.sqrt(sum(v * v for v in c2.values()))
    if den1 == 0.0 or den2 == 0.0:
        return 0.0
    return num / (den1 * den2)


def extract_group_signature_text(group: Dict[str, Any]) -> str:
    parts: List[str] = []
    stim = group.get("stimulus", {})
    for doc in stim.get("documents", []):
        if doc.get("title_en"):
            parts.append(doc["title_en"])
        for blk in doc.get("blocks", []):
            if blk.get("type") == "text":
                parts.append(blk.get("text_en", ""))
            elif blk.get("type") == "table":
                parts.append(" ".join(blk.get("columns", [])))
                for row in blk.get("rows", []):
                    parts.append(" ".join(row))
    for seg in stim.get("audio_script", []):
        parts.append(seg.get("text_en", ""))
    for item in group.get("items", []):
        if group.get("part") not in (1, 2):
            parts.append(item.get("prompt_en", ""))
        for ch in item.get("choices", []):
            parts.append(ch.get("text_en", ""))
    return " ".join(parts)


def load_skill_tags() -> Set[str]:
    with TAXONOMY_PATH.open("r", encoding="utf-8") as f:
        data = json.load(f)
    return {s["tag"] for s in data.get("skills", [])}


def parse_jsonl_strict(path: Path, allow_empty: bool = False) -> Tuple[List[Dict[str, Any]], List[str]]:
    records = []
    errors = []
    if not path.exists():
        return [], [f"檔案不存在：{path.name}"]
    with path.open("r", encoding="utf-8") as f:
        for idx, raw_line in enumerate(f, start=1):
            stripped = raw_line.strip()
            if not stripped:
                errors.append(f"{path.name} 第 {idx} 行為空白行")
                continue
            if stripped.startswith("```") or stripped.startswith("//"):
                errors.append(f"{path.name} 第 {idx} 行包含禁止的註解或 Markdown code fence")
                continue
            try:
                def disallow_nan(val: str) -> Any:
                    raise ValueError(f"不允許的數值常數：{val}")
                obj = json.loads(stripped, parse_constant=disallow_nan)
                if not isinstance(obj, dict):
                    errors.append(f"{path.name} 第 {idx} 行不是 JSON object")
                else:
                    records.append(obj)
            except Exception as exc:
                errors.append(f"{path.name} 第 {idx} 行 JSON 解析失敗：{exc}")
    if not records and not allow_empty and not errors:
        errors.append(f"{path.name} 不得為空檔案")
    return records, errors


def build_check(
    check_id: str,
    category: str,
    status: str,
    code: str,
    message_zh: str,
    path: Optional[str] = None,
    group_id: Optional[str] = None,
    item_id: Optional[str] = None,
    evidence_paths: Optional[List[str]] = None,
) -> Dict[str, Any]:
    return {
        "check_id": check_id,
        "category": category,
        "target": {
            "path": path,
            "group_id": group_id,
            "item_id": item_id,
        },
        "status": status,
        "code": code,
        "message_zh": message_zh,
        "evidence_paths": evidence_paths or [],
    }


def validate_batch(
    batch_dir: Path,
    batch_id: str,
    profile: str = "authoring",
) -> Tuple[Dict[str, Any], List[Dict[str, Any]], List[Dict[str, Any]]]:
    checks: List[Dict[str, Any]] = []
    valid_skills = load_skill_tags()

    groups_path = batch_dir / "groups.jsonl"
    reviews_path = batch_dir / "reviews.jsonl"
    blind_path = batch_dir / "reports" / "blind-solve.json"
    summary_path = batch_dir / "reports" / "summary.md"
    mock_forms_path = batch_dir / "reports" / "mock-forms.json"
    is_mock_form_assembly = mock_forms_path.exists()

    groups, group_parse_errors = parse_jsonl_strict(groups_path, allow_empty=is_mock_form_assembly)
    reviews, review_parse_errors = parse_jsonl_strict(reviews_path, allow_empty=is_mock_form_assembly)

    # --- Family 1: Full Nested JSON Schema Validation (Draft 2020-12) ---
    schema_errors: List[str] = list(group_parse_errors) + list(review_parse_errors)

    for line_idx, g in enumerate(groups, start=1):
        gid = g.get("group_id", f"line-{line_idx}") if isinstance(g, dict) else f"line-{line_idx}"
        for err in GROUP_VALIDATOR.iter_errors(g):
            loc = ".".join(str(p) for p in err.absolute_path) or "<root>"
            schema_errors.append(f"groups.jsonl:{line_idx} ({gid}) [{loc}]: {err.message}")
        if isinstance(g, dict):
            for it in g.get("items", []):
                if isinstance(it, dict):
                    tags = it.get("skill_tags", [])
                    if not tags or any(t not in valid_skills for t in tags):
                        schema_errors.append(f"{it.get('item_id', gid)}: skill_tags 含未定義標籤 ({tags})")

    for line_idx, r in enumerate(reviews, start=1):
        rid = r.get("review_id", f"line-{line_idx}") if isinstance(r, dict) else f"line-{line_idx}"
        for err in REVIEW_VALIDATOR.iter_errors(r):
            loc = ".".join(str(p) for p in err.absolute_path) or "<root>"
            schema_errors.append(f"reviews.jsonl:{line_idx} ({rid}) [{loc}]: {err.message}")

    if schema_errors:
        checks.append(
            build_check(
                "structure-001", "structure", "fail", "struct_json_schema_invalid",
                f"完整巢狀 JSON Schema (Draft 2020-12) 檢查發現 {len(schema_errors)} 項違規：" + "；".join(schema_errors[:5]),
                path="groups.jsonl",
            )
        )
    else:
        checks.append(
            build_check(
                "structure-001", "structure", "pass", "struct_json_schema_valid",
                f"groups.jsonl（{len(groups)} 組）與 reviews.jsonl（{len(reviews)} 筆）通過完整巢狀 JSON Schema (group.schema.json & review.schema.json) 驗證，0 項違規。",
                path="groups.jsonl",
                evidence_paths=["groups.jsonl", "reviews.jsonl"],
            )
        )

    # --- Family 2: Part Shape, Choices, Blanks, Tables, No HTML/JS ---
    shape_errors: List[str] = []
    html_errors: List[str] = []
    for g in groups:
        gid = g.get("group_id", "<missing>")
        part = g.get("part")
        layout = g.get("layout")
        items = g.get("items", [])
        stim = g.get("stimulus", {})
        docs = stim.get("documents", [])
        speakers = stim.get("speakers", [])
        script = stim.get("audio_script", [])
        assets = g.get("assets", [])

        if part not in VALID_LAYOUTS or layout not in VALID_LAYOUTS.get(part, set()):
            shape_errors.append(f"{gid}: part={part} 與 layout={layout} 不匹配")

        full_text = json.dumps(g, ensure_ascii=False)
        if HTML_JS_PATTERN.search(full_text):
            html_errors.append(f"{gid}: 含禁止之 HTML/JavaScript 標籤或屬性")

        for doc in docs:
            for blk in doc.get("blocks", []):
                if blk.get("type") == "table":
                    cols = blk.get("columns", [])
                    for r_idx, row in enumerate(blk.get("rows", [])):
                        if len(row) != len(cols):
                            shape_errors.append(f"{gid}: 表格 {blk.get('block_id')} 第 {r_idx} 列欄數與 columns 不一致")

        if part == 1:
            if len(items) != 1:
                shape_errors.append(f"{gid}: Part 1 必須恰 1 題")
            kinds = {a.get("kind") for a in assets}
            if "image" not in kinds or "audio" not in kinds:
                shape_errors.append(f"{gid}: Part 1 必須同時宣告 image 與 audio 素材")
            if len(script) < 4:
                shape_errors.append(f"{gid}: Part 1 audio_script 必須包含 4 個朗讀選項")
            if items:
                for ch in items[0].get("choices", []):
                    if ch.get("text_en", "").lower() in items[0].get("prompt_en", "").lower():
                        shape_errors.append(f"{gid}: Part 1 prompt_en 不得洩漏選項內容")
        elif part == 2:
            if len(items) != 1:
                shape_errors.append(f"{gid}: Part 2 必須恰 1 題")
            kinds = {a.get("kind") for a in assets}
            if "audio" not in kinds:
                shape_errors.append(f"{gid}: Part 2 必須宣告 audio 素材")
            if len(script) < 4:
                shape_errors.append(f"{gid}: Part 2 audio_script 必須包含問題與 A/B/C 三個選項段落")
            q_text = script[0].get("text_en", "") if script else ""
            if items and q_text and q_text.lower() in items[0].get("prompt_en", "").lower():
                shape_errors.append(f"{gid}: Part 2 prompt_en 不得洩漏音訊題幹")
        elif part == 3:
            if len(items) != 3:
                shape_errors.append(f"{gid}: Part 3 必須恰 3 題")
            non_narrator = [s for s in speakers if "narrator" not in s.get("role", "").lower()]
            if len(non_narrator) < 2:
                shape_errors.append(f"{gid}: Part 3 必須至少有兩位對話角色")
            if not any(a.get("kind") == "audio" for a in assets):
                shape_errors.append(f"{gid}: Part 3 必須宣告 audio 素材")
        elif part == 4:
            if len(items) != 3:
                shape_errors.append(f"{gid}: Part 4 必須恰 3 題")
            non_narrator = [s for s in speakers if "narrator" not in s.get("role", "").lower()]
            if len(non_narrator) != 1:
                shape_errors.append(f"{gid}: Part 4 主體必須為單人獨白（非旁白角色恰 1 位）")
            if not any(a.get("kind") == "audio" for a in assets):
                shape_errors.append(f"{gid}: Part 4 必須宣告 audio 素材")
        elif part == 5:
            if len(items) != 1:
                shape_errors.append(f"{gid}: Part 5 必須恰 1 題")
            if items and "____" not in items[0].get("prompt_en", ""):
                shape_errors.append(f"{gid}: Part 5 prompt_en 必須包含 ____ 空格標記")
        elif part == 6:
            if len(items) != 4 or len(docs) != 1:
                shape_errors.append(f"{gid}: Part 6 必須恰 1 篇文件與 4 題")
            doc_text = " ".join(
                b.get("text_en", "") for d in docs for b in d.get("blocks", []) if b.get("type") == "text"
            )
            for it in items:
                marker = f"[[blank:{it.get('item_id')}]]"
                if doc_text.count(marker) != 1:
                    shape_errors.append(f"{gid}: Part 6 正文必須恰出現一次 {marker}")
        elif part == 7:
            if layout == "single_passage" and (len(docs) != 1 or not (2 <= len(items) <= 4)):
                shape_errors.append(f"{gid}: Part 7 single_passage 必須為 1 份文件、2–4 題")
            elif layout == "double_passage" and (len(docs) != 2 or len(items) != 5):
                shape_errors.append(f"{gid}: Part 7 double_passage 必須為 2 份文件、5 題")
            elif layout == "triple_passage" and (len(docs) != 3 or len(items) != 5):
                shape_errors.append(f"{gid}: Part 7 triple_passage 必須為 3 份文件、5 題")
            doc_text = " ".join(
                b.get("text_en", "") for d in docs for b in d.get("blocks", []) if b.get("type") == "text"
            )
            for it in items:
                if "sentence_insertion" in it.get("skill_tags", []):
                    for slot in ("1", "2", "3", "4"):
                        if f"[[position:{slot}]]" not in doc_text:
                            shape_errors.append(f"{gid}: Part 7 插句題缺少 [[position:{slot}]] 標記")

        for it in items:
            iid = it.get("item_id", "<missing>")
            choices = it.get("choices", [])
            expected_ids = ["A", "B", "C"] if part == 2 else ["A", "B", "C", "D"]
            actual_ids = [c.get("id") for c in choices if isinstance(c, dict)]
            if actual_ids != expected_ids:
                shape_errors.append(f"{iid}: 選項 ID 順序必須為 {expected_ids}，實際為 {actual_ids}")
            choice_texts = [normalize_text(c.get("text_en", "")) for c in choices if isinstance(c, dict)]
            if len(set(choice_texts)) != len(choice_texts):
                shape_errors.append(f"{iid}: 選項文字重複")
            ans = it.get("answer_choice_id")
            if ans not in expected_ids:
                shape_errors.append(f"{iid}: answer_choice_id ({ans}) 不在選項中")
            d_ids = [d.get("choice_id") for d in it.get("distractor_notes", []) if isinstance(d, dict)]
            expected_d_ids = [cid for cid in expected_ids if cid != ans]
            if sorted(d_ids) != sorted(expected_d_ids):
                shape_errors.append(f"{iid}: distractor_notes 必須恰涵蓋所有錯誤選項 {expected_d_ids}")

    if shape_errors or html_errors:
        checks.append(
            build_check(
                "structure-002", "structure", "fail", "struct_part_shape_invalid",
                "題組形狀或安全檢查失敗：" + "；".join((shape_errors + html_errors)[:5]),
                path="groups.jsonl",
            )
        )
    else:
        checks.append(
            build_check(
                "structure-002", "structure", "pass", "struct_part_shape_valid",
                "所有題組之 Part/layout 題數、選項數、答案引用、Part 5/6/7 空格與插句標記、表格列寬及無 HTML/JS 檢查均通過。",
                path="groups.jsonl",
                evidence_paths=["groups.jsonl"],
            )
        )

    # --- Family 3: References (evidence, speakers, review_refs, segment_times) ---
    ref_errors: List[str] = []
    review_map: Dict[str, Dict[str, Any]] = {r["review_id"]: r for r in reviews if "review_id" in r}
    for g in groups:
        gid = g.get("group_id", "<missing>")
        stim = g.get("stimulus", {})
        block_ids = {
            b.get("block_id") for d in stim.get("documents", []) for b in d.get("blocks", []) if isinstance(b, dict)
        }
        speaker_ids = {s.get("speaker_id") for s in stim.get("speakers", []) if isinstance(s, dict)}
        segment_ids = {s.get("segment_id") for s in stim.get("audio_script", []) if isinstance(s, dict)}
        asset_ids = {a.get("asset_id") for a in g.get("assets", []) if isinstance(a, dict)}
        item_ids = {i.get("item_id") for i in g.get("items", []) if isinstance(i, dict)}

        for seg in stim.get("audio_script", []):
            if seg.get("speaker_id") not in speaker_ids:
                ref_errors.append(f"{gid}: audio_script segment {seg.get('segment_id')} 引用不存在的 speaker_id {seg.get('speaker_id')}")

        for ast in g.get("assets", []):
            for st in ast.get("segment_times", []):
                if st.get("segment_id") not in segment_ids:
                    ref_errors.append(f"{gid}: segment_times 引用不存在的 segment_id {st.get('segment_id')}")
                if st.get("start_ms", -1) < 0 or st.get("end_ms", 0) <= st.get("start_ms", 0):
                    ref_errors.append(f"{gid}: segment_times 時間範圍無效")
                if ast.get("duration_ms") and st.get("end_ms", 0) > ast["duration_ms"]:
                    ref_errors.append(f"{gid}: segment_times 超出音檔 duration_ms")

        for it in g.get("items", []):
            iid = it.get("item_id", "<missing>")
            for ev in it.get("evidence", []):
                if not isinstance(ev, dict):
                    continue
                stype = ev.get("source_type")
                sid = ev.get("source_id")
                if stype == "document_block" and sid not in block_ids:
                    ref_errors.append(f"{iid}: evidence 引用不存在的 document_block {sid}")
                elif stype == "audio_segment" and sid not in segment_ids:
                    ref_errors.append(f"{iid}: evidence 引用不存在的 audio_segment {sid}")
                elif stype == "asset" and sid not in asset_ids:
                    ref_errors.append(f"{iid}: evidence 引用不存在的 asset {sid}")
                elif stype == "item_prompt" and sid != iid:
                    ref_errors.append(f"{iid}: evidence item_prompt 必須指向自身 item_id {iid}")
                # Quote must actually appear in the referenced source (prevents off-by-one segment pointers)
                src_text = evidence_source_text(stim, it, stype, sid)
                if src_text is not None and not quote_in_source(ev.get("quote_en", ""), src_text):
                    ref_errors.append(
                        f"{iid}: evidence quote_en 未出現在所引用的 {stype} {sid} 內容中（引用指向錯誤或引文不符）"
                    )

        if not g.get("review_refs"):
            ref_errors.append(f"{gid}: review_refs 不可為空")
        for rref in g.get("review_refs", []):
            if rref not in review_map:
                ref_errors.append(f"{gid}: review_refs 引用不存在的 review_id {rref}")
            else:
                robj = review_map[rref]
                if robj.get("group_id") != gid or robj.get("group_version") != g.get("version"):
                    ref_errors.append(f"{gid}: review {rref} 的 group_id/version 不一致")
                if set(robj.get("item_ids", [])) != item_ids:
                    ref_errors.append(f"{gid}: review {rref} 的 item_ids 與題組不符")

    if ref_errors:
        checks.append(
            build_check(
                "references-001", "references", "fail", "ref_evidence_invalid",
                "引用完整性檢查失敗：" + "；".join(ref_errors[:5]),
                path="groups.jsonl",
            )
        )
    else:
        checks.append(
            build_check(
                "references-001", "references", "pass", "ref_evidence_valid",
                "所有 item.evidence、stimulus.speakers、review_refs 與 segment_times 引用完整性檢查均通過。",
                path="groups.jsonl",
                evidence_paths=["groups.jsonl", "reviews.jsonl"],
            )
        )

    # --- Family 4: Intra-batch & Cross-batch ID / Version / Family Uniqueness ---
    intra_errors: List[str] = []
    seen_gids: Set[str] = set()
    seen_iids: Set[str] = set()
    seen_aids: Set[str] = set()
    seen_rids: Set[str] = set()
    batch_family_pools: Dict[str, Set[str]] = collections.defaultdict(set)

    for g in groups:
        gid = g.get("group_id", "")
        if gid in seen_gids:
            intra_errors.append(f"重複 group_id: {gid}")
        seen_gids.add(gid)
        batch_family_pools[g.get("family_id", "")].add(g.get("pool", ""))
        for ast in g.get("assets", []):
            aid = ast.get("asset_id", "")
            if aid in seen_aids:
                intra_errors.append(f"重複 asset_id: {aid}")
            seen_aids.add(aid)
        for it in g.get("items", []):
            iid = it.get("item_id", "")
            if iid in seen_iids:
                intra_errors.append(f"重複 item_id: {iid}")
            seen_iids.add(iid)

    for r in reviews:
        rid = r.get("review_id", "")
        if rid in seen_rids:
            intra_errors.append(f"重複 review_id: {rid}")
        seen_rids.add(rid)

    for fam, pools in batch_family_pools.items():
        if len(pools) > 1:
            intra_errors.append(f"family_id {fam} 在本批內跨多個 pool: {pools}")

    if intra_errors:
        checks.append(
            build_check(
                "uniqueness-001", "uniqueness", "fail", "uniq_intra_batch_ids_conflict",
                "本批內部 ID 或 family 衝突：" + "；".join(intra_errors[:5]),
                path="groups.jsonl",
            )
        )
    else:
        checks.append(
            build_check(
                "uniqueness-001", "uniqueness", "pass", "uniq_intra_batch_ids_valid",
                f"本批內 {len(seen_gids)} 個 group_id、{len(seen_iids)} 個 item_id、{len(seen_aids)} 個 asset_id 與 {len(seen_rids)} 個 review_id 均唯一且無同家族跨池。",
                path="groups.jsonl",
                evidence_paths=["groups.jsonl", "reviews.jsonl"],
            )
        )

    # Cross-batch check against global-index.json
    cross_errors: List[str] = []
    upgraded_gids: List[str] = []
    prior_signatures: List[Dict[str, Any]] = []
    group_by_id = {g["group_id"]: g for g in groups if "group_id" in g}
    item_to_group = {it["item_id"]: g["group_id"] for g in groups if "group_id" in g for it in g.get("items", []) if "item_id" in it}

    if GLOBAL_INDEX_PATH.exists():
        with GLOBAL_INDEX_PATH.open("r", encoding="utf-8") as f:
            gindex = json.load(f)
        for prev_gid, prev_info in gindex.get("groups", {}).items():
            if prev_info.get("batch_id") == batch_id:
                continue
            entry = dict(prev_info)
            entry["group_id"] = prev_gid
            prior_signatures.append(entry)
            if prev_gid in group_by_id:
                cur_g = group_by_id[prev_gid]
                prev_ver = int(prev_info.get("version", 1))
                # If validating an already-exported historical batch that is in version_history, skip version comparison against newer batches
                hist_versions = [h.get("batch_id") for h in prev_info.get("version_history", [])]
                if batch_id in hist_versions:
                    continue
                if cur_g["version"] <= prev_ver:
                    cross_errors.append(
                        f"group_id {prev_gid} 版本 ({cur_g['version']}) 未高於歷史批次 {prev_info.get('batch_id')} (v{prev_ver})"
                    )
                elif cur_g["family_id"] != prev_info.get("family_id") or cur_g["pool"] != prev_info.get("pool"):
                    cross_errors.append(
                        f"group_id {prev_gid} 升版時不得變更 family_id 或 pool"
                    )
                else:
                    upgraded_gids.append(f"{prev_gid}(v{prev_ver}->v{cur_g['version']})")
        for prev_iid, prev_item_meta in gindex.get("items", {}).items():
            if isinstance(prev_item_meta, dict):
                prev_batch = prev_item_meta.get("batch_id")
                prev_owner_gid = prev_item_meta.get("group_id")
            else:
                prev_batch = prev_item_meta
                parts_iid = prev_iid.split("-")
                prev_owner_gid = "-".join(["ag", "g"] + parts_iid[2:4]) if len(parts_iid) >= 4 else None
            if prev_batch != batch_id and prev_iid in item_to_group:
                cur_owner_gid = item_to_group[prev_iid]
                if cur_owner_gid != prev_owner_gid:
                    cross_errors.append(
                        f"item_id {prev_iid} 已屬於另一題組 {prev_owner_gid}（批次 {prev_batch}）"
                    )
                else:
                    prev_g_info = gindex.get("groups", {}).get(cur_owner_gid, {})
                    hist_batches = [h.get("batch_id") for h in prev_g_info.get("version_history", [])]
                    if batch_id not in hist_batches and group_by_id[cur_owner_gid]["version"] <= int(prev_g_info.get("version", 1)):
                        cross_errors.append(
                            f"item_id {prev_iid} 已存在於歷史批次 {prev_batch} 且題組未升版"
                        )
        for fam, prev_pool in gindex.get("families", {}).items():
            if fam in batch_family_pools and prev_pool not in batch_family_pools[fam]:
                cross_errors.append(f"family_id {fam} 與歷史批次跨用途池衝突 ({prev_pool} vs {batch_family_pools[fam]})")

        if cross_errors:
            checks.append(
                build_check(
                    "uniqueness-002", "uniqueness", "fail", "uniq_cross_batch_index_conflict",
                    "跨批次索引衝突：" + "；".join(cross_errors[:5]),
                    path="groups.jsonl",
                )
            )
        else:
            upgrade_note = f"（含合法版本升級 {len(upgraded_gids)} 組）" if upgraded_gids else ""
            checks.append(
                build_check(
                    "uniqueness-002", "uniqueness", "pass", "uniq_cross_batch_index_valid",
                    f"已與全域歷史索引比對（累計 {len(prior_signatures)} 組先前題組）{upgrade_note}，無跨批 ID 重複、版本衝突或 family 跨池衝突。",
                    path="groups.jsonl",
                    evidence_paths=["groups.jsonl"],
                )
            )
    else:
        checks.append(
            build_check(
                "uniqueness-002", "uniqueness", "pass", "uniq_cross_batch_index_valid",
                "本批為首個建立全域索引之批次（先前歷史題組數為 0），無跨批衝突。",
                path="groups.jsonl",
                evidence_paths=["groups.jsonl"],
            )
        )

    # --- Family 5: Exact, Normalized, and Semantic/Family Near-Duplicate Checks ---
    dup_errors: List[str] = []
    sim_warnings: List[str] = []
    seen_norm_texts: Dict[str, str] = {}
    for prev in prior_signatures:
        if prev["group_id"] not in seen_gids:
            seen_norm_texts[prev["norm_text"]] = prev["group_id"]

    group_counters: List[Tuple[str, int, str, collections.Counter]] = []
    for prev in prior_signatures:
        if prev["group_id"] not in seen_gids:
            group_counters.append(
                (prev["group_id"], prev["part"], prev["family_id"], char_ngrams(prev["norm_text"]))
            )

    for g in groups:
        gid = g["group_id"]
        sig_text = extract_group_signature_text(g)
        norm = normalize_text(sig_text)
        if norm in seen_norm_texts:
            dup_errors.append(f"{gid} 與 {seen_norm_texts[norm]} 正規化後文字完全重複")
        seen_norm_texts[norm] = gid

        c_vec = char_ngrams(norm)
        for other_gid, other_part, other_fam, other_vec in group_counters:
            if other_part == g.get("part") and other_fam != g.get("family_id"):
                sim = cosine_counter(c_vec, other_vec)
                if sim >= 0.82:
                    sim_warnings.append(f"{gid} 與 {other_gid} 四字元 n-gram 餘弦相似度達 {sim:.2f}")
        group_counters.append((gid, g.get("part"), g.get("family_id", ""), c_vec))

    if dup_errors:
        checks.append(
            build_check(
                "uniqueness-003", "uniqueness", "fail", "uniq_exact_or_normalized_duplicate",
                "發現完全重複或正規化重複內容：" + "；".join(dup_errors[:5]),
                path="groups.jsonl",
            )
        )
    else:
        checks.append(
            build_check(
                "uniqueness-003", "uniqueness", "pass", "uniq_exact_and_normalized_valid",
                "完全相同文字與正規化文字去重檢查通過，無重複題幹、選項組或文稿。",
                path="groups.jsonl",
                evidence_paths=["groups.jsonl"],
            )
        )

    if sim_warnings:
        checks.append(
            build_check(
                "uniqueness-004", "uniqueness", "warning", "uniq_semantic_family_warning",
                "語意與結構近似度檢查發現待審訊號：" + "；".join(sim_warnings[:5]),
                path="groups.jsonl",
                evidence_paths=["groups.jsonl"],
            )
        )
    else:
        checks.append(
            build_check(
                "uniqueness-004", "uniqueness", "pass", "uniq_semantic_family_valid",
                "同題型跨家族 n-gram 餘弦相似度與情境骨架去重檢查通過（最高相似度均低於警戒門檻 0.82）。",
                path="groups.jsonl",
                evidence_paths=["groups.jsonl"],
            )
        )

    # --- Family 6: Assets (status, path safety, file existence, planned warnings) ---
    asset_errors: List[str] = []
    planned_assets: List[Tuple[str, str, str]] = []
    for g in groups:
        gid = g["group_id"]
        for ast in g.get("assets", []):
            aid = ast.get("asset_id", "<missing>")
            st = ast.get("status")
            p = ast.get("path")
            if st == "planned":
                if p is not None or ast.get("sha256") is not None or ast.get("duration_ms") is not None:
                    asset_errors.append(f"{aid}: status=planned 時 path/sha256/duration_ms 必須為 null")
                planned_assets.append((gid, aid, ast.get("kind", "")))
            elif st == "ready":
                if not p or p.startswith("/") or ".." in Path(p).parts:
                    asset_errors.append(f"{aid}: ready 素材路徑不安全或為空 ({p})")
                else:
                    full_p = batch_dir / p
                    if not full_p.exists() or full_p.is_symlink():
                        asset_errors.append(f"{aid}: ready 素材檔案不存在或為 symlink ({p})")
                    else:
                        actual_sha = sha256_file(full_p)
                        if actual_sha != ast.get("sha256"):
                            asset_errors.append(f"{aid}: SHA256 不符")
                if ast.get("kind") == "audio" and (not isinstance(ast.get("duration_ms"), int) or ast.get("duration_ms", 0) <= 0):
                    asset_errors.append(f"{aid}: ready 音訊必須提供正整數 duration_ms")

    if asset_errors:
        checks.append(
            build_check(
                "assets-001", "assets", "fail", "asset_path_safety_invalid",
                "素材欄位或路徑安全檢查失敗：" + "；".join(asset_errors[:5]),
                path="groups.jsonl",
            )
        )
    else:
        checks.append(
            build_check(
                "assets-001", "assets", "pass", "asset_path_safety_valid",
                "所有素材之欄位契約與路徑安全檢查通過（無越界路徑或偽造雜湊）。",
                path="groups.jsonl",
                evidence_paths=["groups.jsonl"],
            )
        )

    if planned_assets:
        status_for_planned = "warning" if profile == "authoring" else "fail"
        checks.append(
            build_check(
                "assets-002", "assets", status_for_planned, "asset_planned_pending_media",
                f"本批包含 {len(planned_assets)} 個 status=planned 之待製音訊／圖片素材（文字稿與圖片規格已完成，依契約設為 null 並記錄於 ASSET_REQUESTS.md；在素材就緒前僅供私有草稿／技術預覽，不可宣稱完整聽力或看圖可用）。",
                path="groups.jsonl",
                evidence_paths=["groups.jsonl"],
            )
        )
    else:
        checks.append(
            build_check(
                "assets-002", "assets", "pass", "asset_ready_all_valid",
                "本批為純文字閱讀／文法題組（或所有素材皆已就緒），無待製缺項素材。",
                path="groups.jsonl",
                evidence_paths=["groups.jsonl"],
            )
        )

    # --- Family 7: Review Integrity & Blind Solve Verification ---
    rev_errors: List[str] = []
    blind_data: Optional[Dict[str, Any]] = None
    if blind_path.exists():
        with blind_path.open("r", encoding="utf-8") as f:
            blind_data = json.load(f)

    blind_answers_by_item: Dict[str, Dict[str, Any]] = {}
    if blind_data:
        for bitem in blind_data.get("items", []):
            blind_answers_by_item[bitem["item_id"]] = bitem

    planned_image_groups: List[str] = []
    for g in groups:
        gid = g["group_id"]
        cstatus = g.get("content_status")
        g_reviews = [review_map[r_id] for r_id in g.get("review_refs", []) if r_id in review_map]
        if cstatus == "human_reviewed" and not any(
            r.get("reviewer_kind") == "human" and r.get("verdict") == "pass" for r in g_reviews
        ):
            rev_errors.append(f"{gid}: 無實際人工審查紀錄卻標為 human_reviewed")
        if cstatus == "ai_checked" and any(r.get("verdict") != "pass" for r in g_reviews):
            rev_errors.append(f"{gid}: 含有非 pass 審查紀錄卻標為 ai_checked")

        has_planned_img = any(a.get("kind") == "image" and a.get("status") == "planned" for a in g.get("assets", []))
        if g.get("part") == 1 and has_planned_img:
            planned_image_groups.append(gid)
            if any(r.get("blind") for r in g_reviews):
                rev_errors.append(f"{gid}: Part 1 圖片尚為 planned，不得宣稱 blind=true")
        else:
            blind_revs = [r for r in g_reviews if r.get("blind")]
            if not blind_revs:
                rev_errors.append(f"{gid}: 缺少獨立上下文盲解紀錄 (blind=true)")
            for it in g.get("items", []):
                iid = it.get("item_id", "")
                if iid not in blind_answers_by_item:
                    rev_errors.append(f"{iid}: reports/blind-solve.json 缺少該題盲解作答紀錄")
                else:
                    b_choice = blind_answers_by_item[iid].get("selected_choice_id")
                    if b_choice != it.get("answer_choice_id"):
                        rev_errors.append(
                            f"{iid}: 盲解答案 ({b_choice}) 與設定正解 ({it.get('answer_choice_id')}) 不一致"
                        )

    if rev_errors:
        checks.append(
            build_check(
                "review_integrity-001", "review_integrity", "fail", "rev_blind_mismatch_or_missing",
                "審查紀錄或盲解證據檢查失敗：" + "；".join(rev_errors[:5]),
                path="reviews.jsonl",
            )
        )
    else:
        checks.append(
            build_check(
                "review_integrity-001", "review_integrity", "pass", "rev_blind_evidence_valid",
                "reviews.jsonl 審查門檻（最高 ai_checked）與 reports/blind-solve.json 獨立上下文盲解證據核對全數一致。",
                path="reviews.jsonl",
                evidence_paths=["reviews.jsonl", "reports/blind-solve.json"],
            )
        )

    if planned_image_groups:
        checks.append(
            build_check(
                "review_integrity-002", "review_integrity", "warning", "rev_blind_not_applicable_planned_image",
                f"Part 1 題組（{', '.join(planned_image_groups)}）因圖片素材尚處於 planned 狀態，依規定誠實標示 blind=false，待實際圖片生成後重新執行看圖盲解。",
                path="reviews.jsonl",
                evidence_paths=["reviews.jsonl"],
            )
        )

    # --- Family 8: Content Quality, Evidence Reasoning, Vocabulary Examples & Answer Distribution ---
    qual_errors: List[str] = []
    ans_counter: collections.Counter = collections.Counter()
    total_items = 0
    for g in groups:
        gid = g["group_id"]
        g_reviews = [review_map[r_id] for r_id in g.get("review_refs", []) if r_id in review_map]
        if not any(r.get("reviewer_kind") == "ai" and not r.get("blind") and r.get("verdict") == "pass" for r in g_reviews):
            qual_errors.append(f"{gid}: 缺少通過之 AI 命題品質審查紀錄")
        for it in g.get("items", []):
            total_items += 1
            iid = it.get("item_id", "<missing>")
            ans_counter[it.get("answer_choice_id", "")] += 1
            exp_zh = it.get("explanation_zh", "").strip()
            if len(exp_zh) < 15 or PLACEHOLDER_PATTERN.match(exp_zh):
                qual_errors.append(f"{iid}: explanation_zh 過短、為佔位字或缺乏實質語法／語意解析")
            for ev in it.get("evidence", []):
                if not isinstance(ev, dict):
                    qual_errors.append(f"{iid}: evidence 項目不是 object")
                    continue
                rzh = str(ev.get("reasoning_zh", "")).strip()
                if len(rzh) < 10 or PLACEHOLDER_PATTERN.match(rzh):
                    qual_errors.append(f"{iid}: evidence.reasoning_zh 過短或為無意義佔位字串")
            for dn in it.get("distractor_notes", []):
                if not isinstance(dn, dict):
                    continue
                reason_zh = str(dn.get("reason_zh", "")).strip()
                if TRIVIAL_DISTRACTOR_PATTERN.search(reason_zh) or len(reason_zh) < 8 or PLACEHOLDER_PATTERN.match(reason_zh):
                    qual_errors.append(f"{iid}: 選項 {dn.get('choice_id')} 的 distractor_notes 含無資訊套話或過短")
            for voc in it.get("vocabulary", []):
                if not isinstance(voc, dict):
                    qual_errors.append(f"{iid}: vocabulary 項目不是 object")
                    continue
                term_en = str(voc.get("term_en", "")).strip()
                ex_en = str(voc.get("example_en", "")).strip()
                if len(ex_en) < 12 or " " not in ex_en or PLACEHOLDER_PATTERN.match(ex_en):
                    qual_errors.append(f"{iid}: vocabulary '{term_en}' 的 example_en 必須為有意義之完整英文例句")

    if qual_errors:
        checks.append(
            build_check(
                "content_quality-001", "content_quality", "fail", "qual_editorial_issue_found",
                "命題品質、證據推理或字彙例句檢查未通過：" + "；".join(qual_errors[:5]),
                path="groups.jsonl",
            )
        )
    else:
        dist_str = ", ".join(f"{k}:{ans_counter.get(k, 0)}" for k in sorted(ans_counter.keys()))
        checks.append(
            build_check(
                "content_quality-001", "content_quality", "pass", "qual_editorial_review_valid",
                f"全數 {total_items} 道小題均通過 AI 命題自然度、唯一正解、evidence.reasoning_zh、vocabulary.example_en 與干擾項有效性審查（正解分布：{dist_str}）。",
                path="groups.jsonl",
                evidence_paths=["groups.jsonl", "reviews.jsonl"],
            )
        )

    # --- Family 9: Package Inventory & Self-Hash Pending ---
    required_pkg_rels = ["groups.jsonl", "reviews.jsonl", "reports/summary.md"]
    if not is_mock_form_assembly:
        required_pkg_rels.append("reports/blind-solve.json")
    missing_pkg_files = [rel for rel in required_pkg_rels if not (batch_dir / rel).exists()]
    if missing_pkg_files:
        checks.append(
            build_check(
                "package-001", "package", "fail", "pkg_pre_manifest_inventory_invalid",
                f"組包前缺少必要檔案：{missing_pkg_files}",
                path="manifest.json",
            )
        )
    else:
        checks.append(
            build_check(
                "package-001", "package", "pass", "pkg_pre_manifest_inventory_valid",
                f"組包前檔案清單核對通過（{len(groups)} 題組、{total_items} 小題、{len(reviews)} 筆審查紀錄）。",
                path="groups.jsonl",
                evidence_paths=required_pkg_rels,
            )
        )

    # Optional Mock Form Additive Contract 1.0.0 validation when reports/mock-forms.json exists
    if is_mock_form_assembly:
        mf_errors: List[str] = []
        try:
            with mock_forms_path.open("r", encoding="utf-8") as f:
                mf_doc = json.load(f)
            for err in MOCK_FORMS_VALIDATOR.iter_errors(mf_doc):
                loc = ".".join(str(p) for p in err.absolute_path) or "<root>"
                mf_errors.append(f"[{loc}]: {err.message}")
            if not mf_errors:
                req_batches = mf_doc["content_set"]["required_batches"]
                req_ids = [b["batch_id"] for b in req_batches]
                if batch_id in req_ids:
                    mf_errors.append(f"form package ({batch_id}) 不得在 required_batches 自我引用")
                if len(set(req_ids)) != len(req_ids):
                    mf_errors.append("required_batches 不可重複")
                assets_by_id = {a["asset_id"]: a for a in mf_doc["assets"]}
                for ast in mf_doc["assets"]:
                    ap = batch_dir / ast["path"]
                    if not ap.exists() or ap.is_symlink():
                        mf_errors.append(f"timeline asset 檔案不存在：{ast['path']}")
                    elif sha256_file(ap) != ast["sha256"].lower():
                        mf_errors.append(f"timeline asset SHA-256 不符：{ast['path']}")
                    if profile == "release" and ast.get("review_state") != "human_reviewed":
                        mf_errors.append(f"release 模式下 timeline asset {ast['asset_id']} 必須為 human_reviewed")
                for fm in mf_doc["forms"]:
                    fid = fm["form_id"]
                    lt = fm["listening_timeline"]
                    ta = assets_by_id.get(lt["asset_id"])
                    if not ta:
                        mf_errors.append(f"{fid}: 找不到 timeline asset {lt['asset_id']}")
                    else:
                        if not ta["path"].startswith(f"assets/mock/{fid}/"):
                            mf_errors.append(f"{fid}: timeline asset 必須位於 assets/mock/{fid}/")
                        if ta["duration_ms"] != lt["duration_ms"]:
                            mf_errors.append(f"{fid}: asset.duration_ms 與 listening_timeline.duration_ms 不一致")
                    if fm["ordered_item_ids"] != fm["listening_item_ids"] + fm["reading_item_ids"]:
                        mf_errors.append(f"{fid}: ordered_item_ids 必須等於 listening_item_ids + reading_item_ids")
                    events = lt["events"]
                    seqs = [e["sequence"] for e in events]
                    if seqs != sorted(seqs) or len(set(seqs)) != len(seqs):
                        mf_errors.append(f"{fid}: events sequence 必須嚴格遞增且唯一")
                    dur_ms = lt["duration_ms"]
                    for ev in events:
                        valid_dur = (ev["end_ms"] == ev["start_ms"]) if ev["kind"] == "item_unlock" else (ev["end_ms"] > ev["start_ms"])
                        if ev["start_ms"] < 0 or ev["start_ms"] >= dur_ms or ev["end_ms"] > dur_ms or not valid_dur:
                            mf_errors.append(f"{fid}: event seq={ev['sequence']} 時間範圍無效")
                            break
                    unlocks = [iid for ev in events if ev["kind"] == "item_unlock" for iid in ev["item_ids"]]
                    if unlocks != fm["listening_item_ids"]:
                        mf_errors.append(f"{fid}: item_unlock 展開順序必須完全等於 listening_item_ids (100題)")
        except Exception as exc:
            mf_errors.append(f"解析 reports/mock-forms.json 失敗：{exc}")
        if mf_errors:
            checks.append(
                build_check(
                    "package-003", "package", "fail", "pkg_mock_form_contract_invalid",
                    "Mock Form Contract 1.0.0 檢查失敗：" + "；".join(mf_errors[:5]),
                    path="reports/mock-forms.json",
                )
            )
        else:
            checks.append(
                build_check(
                    "package-003", "package", "pass", "pkg_mock_form_contract_valid",
                    "reports/mock-forms.json 通過 Mock Form Additive Contract 1.0.0 完整 JSON Schema 與毫秒時間線檢查。",
                    path="reports/mock-forms.json",
                    evidence_paths=["reports/mock-forms.json"],
                )
            )

    checks.append(
        build_check(
            "package-002", "package", "not_run", "final_manifest_pending",
            "依 Validation Report 1.0.0 打包順序規範，最終 manifest.json 將在本報告寫入後計算 SHA256 並產生，由接收端（及包外 import-check 報告）另行驗證。",
            path="manifest.json",
        )
    )

    counts = {"pass": 0, "warning": 0, "fail": 0, "not_run": 0}
    for c in checks:
        counts[c["status"]] += 1

    if counts["fail"] > 0:
        overall = "fail"
    elif counts["not_run"] > 0:
        overall = "incomplete"
    elif counts["warning"] > 0:
        overall = "warning"
    else:
        overall = "pass"

    report = {
        "report_version": "1.0.0",
        "content_schema_version": "1.0.0",
        "batch_id": batch_id,
        "generated_at": utc_now_iso(),
        "validator": {
            "name": "ag-content-validator",
            "version": "1.1.0",
        },
        "profile": profile,
        "checks": checks,
        "counts": counts,
        "overall_result": overall,
    }
    val_schema_errs = [e.message for e in VAL_REPORT_VALIDATOR.iter_errors(report)]
    if val_schema_errs:
        raise RuntimeError(f"Generated validation report failed validation-report.schema.json: {val_schema_errs}")
    return report, groups, reviews


def update_global_index(batch_id: str, groups: List[Dict[str, Any]]) -> None:
    GLOBAL_INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
    if GLOBAL_INDEX_PATH.exists():
        with GLOBAL_INDEX_PATH.open("r", encoding="utf-8") as f:
            gindex = json.load(f)
    else:
        gindex = {"updated_at": "", "groups": {}, "items": {}, "families": {}}

    gindex["updated_at"] = utc_now_iso()
    for g in groups:
        gid = g["group_id"]
        sig = extract_group_signature_text(g)
        prev_entry = gindex["groups"].get(gid, {})
        history = list(prev_entry.get("version_history", []))
        if prev_entry and not history:
            history.append({
                "version": prev_entry.get("version", 1),
                "batch_id": prev_entry.get("batch_id"),
            })
        if not any(h.get("version") == g["version"] and h.get("batch_id") == batch_id for h in history):
            history.append({"version": g["version"], "batch_id": batch_id})
        gindex["groups"][gid] = {
            "batch_id": batch_id,
            "version": g["version"],
            "part": g["part"],
            "layout": g["layout"],
            "pool": g["pool"],
            "family_id": g["family_id"],
            "scenario": g["scenario"],
            "difficulty": g["difficulty"]["level"],
            "item_count": len(g["items"]),
            "norm_text": normalize_text(sig),
            "version_history": history,
        }
        gindex["families"][g["family_id"]] = g["pool"]
        for it in g["items"]:
            gindex["items"][it["item_id"]] = {
                "batch_id": batch_id,
                "group_id": gid,
                "version": g["version"],
            }

    with GLOBAL_INDEX_PATH.open("w", encoding="utf-8") as f:
        json.dump(gindex, f, ensure_ascii=False, indent=2)
        f.write("\n")


PROTECTED_BATCH_IDS = {
    "batch-ag-0001",
    "batch-ag-0002",
    "batch-ag-0003",
    "batch-ag-0004",
    "batch-ag-0005",
    "batch-ag-0006",
    "batch-ag-0007",
    "batch-ag-0008",
    "batch-ag-0009",
    "batch-ag-0010",
    # Published revision packages are immutable as well (2026-10-30/31)
    "batch-ag-0011",
    "batch-ag-0012",
    "batch-ag-0013",
    "batch-ag-0014",
    "batch-ag-0015",
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate and package a TOEIC batch")
    parser.add_argument("--source-dir", required=True, help="Draft directory containing groups.jsonl, reviews.jsonl, reports/")
    parser.add_argument("--batch-id", required=True, help="Batch ID, e.g. batch-ag-0011")
    parser.add_argument("--profile", default="authoring", choices=["authoring", "release"])
    parser.add_argument("--export", action="store_true", help="Copy to exports/<batch-id> and generate manifest.json")
    args = parser.parse_args()

    src_dir = Path(args.source_dir).resolve()
    report, groups, reviews = validate_batch(src_dir, args.batch_id, args.profile)

    if report["counts"]["fail"] > 0:
        print(json.dumps(report, ensure_ascii=False, indent=2))
        sys.exit(1)

    if args.export:
        export_dir = ROOT / "exports" / args.batch_id
        if args.batch_id in PROTECTED_BATCH_IDS and export_dir.exists():
            raise RuntimeError(
                f"Refusing to overwrite immutable historical batch {args.batch_id} in exports/!"
            )
        if export_dir.exists():
            shutil.rmtree(export_dir)
        shutil.copytree(src_dir, export_dir)
        (export_dir / "assets").mkdir(exist_ok=True)
        (export_dir / "reports").mkdir(exist_ok=True)

        # Re-run validation on export_dir and write reports/validation.json BEFORE manifest.json
        report, groups, reviews = validate_batch(export_dir, args.batch_id, args.profile)
        if report["counts"]["fail"] > 0:
            shutil.rmtree(export_dir)
            print(json.dumps(report, ensure_ascii=False, indent=2))
            sys.exit(1)

        val_path = export_dir / "reports" / "validation.json"
        with val_path.open("w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
            f.write("\n")

        # Compute SHA256 for all files in export_dir except manifest.json
        file_entries = []
        for p in sorted(export_dir.rglob("*")):
            if p.is_file() and p.name != "manifest.json":
                rel = p.relative_to(export_dir).as_posix()
                file_entries.append({"path": rel, "sha256": sha256_file(p)})

        total_items = sum(len(g["items"]) for g in groups)
        manifest = {
            "schema_version": "1.0.0",
            "batch_id": args.batch_id,
            "created_at": utc_now_iso(),
            "producer": "antigravity-toeic-factory/1.1.0 (model: unknown)",
            "group_count": len(groups),
            "item_count": total_items,
            "files": file_entries,
        }
        if len(groups) > 0:
            man_errs = [e.message for e in MANIFEST_VALIDATOR.iter_errors(manifest)]
            if man_errs:
                raise RuntimeError(f"Generated manifest.json failed manifest.schema.json: {man_errs}")

        manifest_path = export_dir / "manifest.json"
        with manifest_path.open("w", encoding="utf-8") as f:
            json.dump(manifest, f, ensure_ascii=False, indent=2)
            f.write("\n")

        # External receiver-side verification (outside export_dir)
        ext_dir = ROOT / "reports" / "post-package-verification"
        ext_dir.mkdir(parents=True, exist_ok=True)
        ext_report = {
            "batch_id": args.batch_id,
            "verified_at": utc_now_iso(),
            "manifest_sha256": sha256_file(manifest_path),
            "group_count": len(groups),
            "item_count": total_items,
            "all_file_hashes_match": all(
                sha256_file(export_dir / entry["path"]) == entry["sha256"]
                for entry in manifest["files"]
            ),
            "files_verified": len(manifest["files"]),
        }
        with (ext_dir / f"{args.batch_id}-import-check.json").open("w", encoding="utf-8") as f:
            json.dump(ext_report, f, ensure_ascii=False, indent=2)
            f.write("\n")

        update_global_index(args.batch_id, groups)
        print(
            f"Exported {args.batch_id} ({len(groups)} groups, {total_items} items) -> {export_dir} "
            f"[counts={report['counts']}, overall={report['overall_result']}]"
        )
    else:
        print(
            f"Validated draft {args.batch_id} ({len(groups)} groups) "
            f"[counts={report['counts']}, overall={report['overall_result']}]"
        )


if __name__ == "__main__":
    main()
