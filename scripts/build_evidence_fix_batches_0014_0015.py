#!/usr/bin/env python3
"""
Immutable v3 evidence-pointer fix for Part 2 groups found defective after batch-ag-0012/0013 (v2) were published.

Defect (found 2026-10-31 by the new quote-in-source check in validate_and_package.py references-001):
  For 10 Part 2 items, the second `evidence` entry quotes the correct response text (e.g. "(B) ...") but
  `source_id` points to the wrong audio segment (question segment or the previous option, off-by-one).
  Stimulus, choices, answer keys, audio binaries and segment_times are correct and are NOT changed.

Outputs (exports/batch-ag-0012 and 0013 stay untouched):
  - exports/batch-ag-0014 : pool="diagnostic", 4 groups / 4 items, version 2 -> 3 (supersedes those groups in batch-ag-0012)
  - exports/batch-ag-0015 : pool="battle",     6 groups / 6 items, version 2 -> 3 (supersedes those groups in batch-ag-0013)
"""

import copy
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List

from validate_and_package import ROOT, normalize_text, quote_in_source

REVISED_AT = "2026-10-30T17:35:00Z"


def load_jsonl(p: Path) -> List[Dict[str, Any]]:
    return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]


def fix_group(g: Dict[str, Any]) -> List[str]:
    """Repoint audio_segment evidence to the segment that actually contains the quote. Returns change log lines."""
    segs = g["stimulus"]["audio_script"]
    changes: List[str] = []
    for it in g["items"]:
        for idx, ev in enumerate(it["evidence"]):
            if ev["source_type"] != "audio_segment":
                continue
            cur = next((s for s in segs if s["segment_id"] == ev["source_id"]), None)
            if cur and quote_in_source(ev["quote_en"], cur["text_en"]):
                continue
            matches = [s for s in segs if quote_in_source(ev["quote_en"], s["text_en"])]
            if len(matches) != 1:
                raise RuntimeError(f"{it['item_id']} evidence[{idx}]: cannot uniquely locate quote {ev['quote_en']!r}")
            changes.append(
                f"{it['item_id']} evidence[{idx}].source_id: {ev['source_id']} -> {matches[0]['segment_id']} "
                f"（引文「{ev['quote_en']}」）"
            )
            ev["source_id"] = matches[0]["segment_id"]
    return changes


def build(old_batch: str, new_batch: str) -> Dict[str, Any]:
    old_dir = ROOT / "exports" / old_batch
    draft = ROOT / "drafts" / new_batch
    if draft.exists():
        shutil.rmtree(draft)
    (draft / "reports").mkdir(parents=True)
    (draft / "assets").mkdir(parents=True)

    groups = load_jsonl(old_dir / "groups.jsonl")
    old_reviews = {r["review_id"]: r for r in load_jsonl(old_dir / "reviews.jsonl")}
    blind_old = json.loads((old_dir / "reports" / "blind-solve.json").read_text(encoding="utf-8"))

    out_groups, out_reviews, changelog = [], [], []
    for g in groups:
        ng = copy.deepcopy(g)
        changes = fix_group(ng)
        if not changes:
            continue
        ng["version"] = 3
        ng["review_refs"] = [re.sub(r"-v2$", "", r) + "-v3" for r in g["review_refs"]]
        # copy referenced assets
        for a in ng["assets"]:
            if a.get("path"):
                dst = draft / a["path"]
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(old_dir / a["path"], dst)
        out_groups.append(ng)
        changelog.append({"group_id": ng["group_id"], "from_version": 2, "to_version": 3,
                          "source_batch": old_batch, "changes": changes})
        for old_rid, new_rid in zip(g["review_refs"], ng["review_refs"]):
            r = copy.deepcopy(old_reviews[old_rid])
            r["review_id"] = new_rid
            r["group_version"] = 3
            r["reviewed_at"] = REVISED_AT
            r["findings"] = [{
                "severity": "warning",
                "code": "evidence_pointer_corrected",
                "item_id": ng["items"][0]["item_id"],
                "note_zh": (
                    "v3 僅修正 evidence.source_id 指向（原 v2 引文正確但指到題目句或前一選項段落）；"
                    "題幹、選項、正解、音檔與 segment_times 與 v2 完全相同。"
                    + ("盲解結果沿用 v2 之獨立盲解紀錄（輸入內容未變）。" if r.get("blind") else "")
                ),
            }]
            out_reviews.append(r)

    item_ids = {it["item_id"] for g in out_groups for it in g["items"]}
    blind = dict(blind_old)
    blind["batch_id"] = new_batch
    blind["items"] = [i for i in blind_old["items"] if i["item_id"] in item_ids]
    blind["skipped_groups"] = []
    blind["note_zh"] = f"沿用 {old_batch} 之獨立上下文盲解紀錄；v3 未改動任何盲解輸入（題幹／選項／音訊稿）。"

    with (draft / "groups.jsonl").open("w", encoding="utf-8") as f:
        for g in out_groups:
            f.write(json.dumps(g, ensure_ascii=False) + "\n")
    with (draft / "reviews.jsonl").open("w", encoding="utf-8") as f:
        for r in out_reviews:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    (draft / "reports" / "blind-solve.json").write_text(json.dumps(blind, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (draft / "reports" / "changelog.json").write_text(json.dumps(
        {"batch_id": new_batch, "supersedes_groups_in": old_batch, "groups": changelog}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8")

    pool = out_groups[0]["pool"]
    lines = "\n".join(f"- `{c['group_id']}` v2→v3：" + "；".join(c["changes"]) for c in changelog)
    (draft / "reports" / "summary.md").write_text(f"""# 批次摘要報告：`{new_batch}`（evidence 指向修正，v2 → v3）

- **用途池**：`{pool}`
- **題組／小題**：{len(out_groups)} 組／{len(item_ids)} 題（修訂，不算新增題）
- **取代關係**：取代 `{old_batch}` 內同 `group_id` 的 v2；`{old_batch}` 其餘題組維持 v2 有效。安裝時須先安裝 `{old_batch}` 再安裝本包（或同一 transaction）。
- **內容審核狀態**：`ai_checked`（0 題 `human_reviewed`）
- **音檔**：與 v2 位元完全相同（SHA-256 不變），仍為舊聲線；Karen＋標號＋400ms 候選尚待實機試聽，未套用。

## 修正明細

{lines}
""", encoding="utf-8")

    subprocess.run([sys.executable, str(ROOT / "scripts" / "validate_and_package.py"),
                    "--source-dir", str(draft), "--batch-id", new_batch, "--export"], check=True)
    return {"batch": new_batch, "groups": len(out_groups), "items": len(item_ids)}


if __name__ == "__main__":
    print(build("batch-ag-0012", "batch-ag-0014"))
    print(build("batch-ag-0013", "batch-ag-0015"))
