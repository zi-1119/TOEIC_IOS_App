#!/usr/bin/env python3
"""
Producer-side independent re-check of exported batches (does NOT replace the Swift importer receiver check).

  python3 scripts/verify_exports.py batch-ag-0011 batch-ag-0012 batch-ag-0013 batch-ag-0014 batch-ag-0015

For every batch: Draft 2020-12 validation of each groups.jsonl / reviews.jsonl line and manifest.json,
SHA-256 of every manifest-listed file, no unlisted files, and evidence quote-in-source.
Prints the manifest SHA-256 for receiver comparison. Exit code 1 on any failure.
"""
import hashlib
import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

from validate_and_package import evidence_source_text, quote_in_source

ROOT = Path(__file__).resolve().parent.parent
SPECS = ROOT / "specs"


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main(batch_ids):
    gv = Draft202012Validator(json.loads((SPECS / "group.schema.json").read_text()))
    rv = Draft202012Validator(json.loads((SPECS / "review.schema.json").read_text()))
    mv = Draft202012Validator(json.loads((SPECS / "manifest.schema.json").read_text()))
    ok = True
    for bid in batch_ids:
        d = ROOT / "exports" / bid
        errs = []
        man = json.loads((d / "manifest.json").read_text())
        errs += [f"manifest: {e.message}" for e in mv.iter_errors(man)]
        listed = {f["path"]: f["sha256"] for f in man["files"]}
        for path, h in listed.items():
            if not (d / path).is_file() or sha(d / path) != h:
                errs.append(f"hash mismatch/missing: {path}")
        actual = {p.relative_to(d).as_posix() for p in d.rglob("*") if p.is_file() and p.name != "manifest.json"}
        if actual - set(listed):
            errs.append(f"unlisted files: {sorted(actual - set(listed))}")
        groups = [json.loads(l) for l in (d / "groups.jsonl").read_text().splitlines() if l.strip()]
        reviews = [json.loads(l) for l in (d / "reviews.jsonl").read_text().splitlines() if l.strip()]
        for i, g in enumerate(groups, 1):
            errs += [f"groups:{i} {list(e.absolute_path)} {e.message}" for e in gv.iter_errors(g)]
            for it in g.get("items", []):
                for ev in it.get("evidence", []):
                    src = evidence_source_text(g["stimulus"], it, ev.get("source_type"), ev.get("source_id"))
                    if src is not None and not quote_in_source(ev.get("quote_en", ""), src):
                        errs.append(f"evidence quote not in {ev['source_type']} {ev['source_id']} ({it['item_id']})")
        for i, r in enumerate(reviews, 1):
            errs += [f"reviews:{i} {list(e.absolute_path)} {e.message}" for e in rv.iter_errors(r)]
        items = sum(len(g["items"]) for g in groups)
        versions = sorted({g["version"] for g in groups})
        status = "PASS" if not errs else f"FAIL ({len(errs)})"
        print(f"{bid}: {status} groups={len(groups)} items={items} versions={versions} "
              f"pool={sorted({g['pool'] for g in groups})} manifest_sha256={sha(d / 'manifest.json')}")
        for e in errs[:10]:
            print("   -", e)
        ok = ok and not errs
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main(sys.argv[1:] or [p.name for p in sorted((ROOT / "exports").glob("batch-ag-*"))])
