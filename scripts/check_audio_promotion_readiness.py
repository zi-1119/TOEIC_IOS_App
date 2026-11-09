#!/usr/bin/env python3
"""
Read-only readiness check for promoting the Part 1/2 spoken-label audio (Karen + A–D/A–C + 400 ms) to a
new immutable batch. Produces NO audio and publishes nothing.

  python3 scripts/check_audio_promotion_readiness.py
    -> reports/audio-promotion-readiness-2026-11-09.json   (machine-readable)
    exit 0 when every *technical pre-check* passes (human approval is reported separately and is still pending)

Scope: the 16 seed Part 1/2 groups whose bundled audio does not speak option labels
(batch-ag-0006: ag-g-p1-000001, ag-g-p2-000001; batch-ag-0007: ag-g-p1-000002/000003, ag-g-p2-000002..000013).
"""
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

from synthesize_listening_audio import option_gap_spoken_text

ROOT = Path(__file__).resolve().parent.parent
GAP_MS = 400
PACK = ROOT / "assets_work" / "audio-listening-pack-2026-10-31"
OUT_JSON = ROOT / "reports" / "audio-promotion-readiness-2026-11-09.json"
# Hashes recorded at hand-off to the user (handoff/2026-10-29-mvp/codex-audio-label-fix.md)
PACK_HASHES = {
    "01-ag-g-p1-000001-A-original.m4a": "684cd4b76474d8dc727975321314eac90c070a2b720a0274f908a82453ebbef9",
    "01-ag-g-p1-000001-B-karen-labels-400ms.m4a": "8a639bb87401ceb9cc4dd33aacafd997c28a9cf1931f678585eb27e9a1967afe",
    "02-ag-g-p1-000002-A-original.m4a": "08b0874cf58aa9763625ad82b8f4490c219a50d7dcfb8b435f66e402e8cadcde",
    "02-ag-g-p1-000002-B-karen-labels-400ms.m4a": "b37e752a6c360c46fa373418e68564ebf532aaeb21aad0d00ed0bc4f2f300127",
    "03-ag-g-p1-000003-A-original.m4a": "5f92a455908bf43b0ee0b6cee6205d275a5ab027577fdc0cfd973d62acbbfade",
    "03-ag-g-p1-000003-B-karen-labels-400ms.m4a": "44f46c136209bed4daadc1d5705570d38502ab519691291d69ad3bbbdb4d8098",
    "04-ag-g-p2-000004-A-original.m4a": "eb30fe79d8abb0bab1ec6627e51e14ddff30da26289761589c51a08a98bc0848",
    "04-ag-g-p2-000004-B-karen-labels-400ms.m4a": "512b5f6e441b72d4fae9ff2ad11b4dee6dccb8a315aecfdea4268a840931d9bf",
    "05-ag-g-p2-000002-A-original.m4a": "6cd520ed297f651af8551f17e564f1706de00d70d6cea63a76e6c015bb07dbf6",
    "05-ag-g-p2-000002-B-karen-labels-400ms.m4a": "382faa974433036b76c568d04bf390fc4e53246d7b8a990ababee521a6fab9cc",
}


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def decoded_ms(p: Path) -> int:
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)],
                         capture_output=True, text=True, check=True).stdout.strip()
    return round(float(out) * 1000)


def main() -> None:
    pack_meta = {s["group_id"]: s for s in json.loads((PACK / "listening-pack.json").read_text())["samples"]}
    rows, failures = [], []
    for batch in ("batch-ag-0006", "batch-ag-0007"):
        exp, seed = ROOT / "exports" / batch, ROOT / "SeedContent" / batch
        seed_groups = {json.loads(l)["group_id"]: l for l in (seed / "groups.jsonl").read_text().splitlines() if l.strip()}
        for line in (exp / "groups.jsonl").read_text().splitlines():
            g = json.loads(line)
            if g["part"] not in (1, 2):
                continue
            gid, part = g["group_id"], g["part"]
            a = next(x for x in g["assets"] if x["kind"] == "audio")
            segs = g["stimulus"]["audio_script"]
            item = g["items"][0]
            checks = {}
            checks["export_asset_sha256_matches"] = sha(exp / a["path"]) == a["sha256"]
            checks["seed_group_line_identical_to_export"] = seed_groups.get(gid) == line
            checks["seed_asset_sha256_matches"] = (seed / a["path"]).is_file() and sha(seed / a["path"]) == a["sha256"]
            dec = decoded_ms(exp / a["path"])
            # AAC container duration includes encoder priming/padding; allow 200 ms
            checks["decoded_duration_within_200ms"] = abs(dec - a["duration_ms"]) <= 200
            checks["segment_times_cover_all_segments"] = [s["segment_id"] for s in a["segment_times"]] == [s["segment_id"] for s in segs]
            n_opts = 4 if part == 1 else 3
            option_segs = segs if part == 1 else segs[1:]
            checks["option_segment_count_matches_choices"] = len(option_segs) == n_opts == len(item["choices"])
            checks["option_text_matches_choice_text"] = all(
                s["text_en"].strip() == c["text_en"].strip() for s, c in zip(option_segs, item["choices"]))
            checks["current_script_has_no_spoken_label"] = not any(re.match(r"^\s*\(?[A-D][).:\-]\s", s["text_en"]) for s in segs)
            # Parser dry-run (no TTS): raw text must stay unchanged; explicit labels must get the gap
            raw_ok = all(option_gap_spoken_text(part=part, segment_index=i, text_en=s["text_en"], option_label_gap_ms=GAP_MS)
                         == s["text_en"] for i, s in enumerate(segs))
            labelled_ok = True
            for i, s in enumerate(segs):
                if part == 2 and i == 0:
                    continue
                lab = "ABCD"[i if part == 1 else i - 1]
                spoken = option_gap_spoken_text(part=part, segment_index=i, text_en=f"({lab}) {s['text_en']}",
                                                option_label_gap_ms=GAP_MS)
                labelled_ok &= spoken == f"{lab} [[slnc {GAP_MS}]] {s['text_en']}"
            checks["parser_leaves_unlabelled_text_unchanged"] = raw_ok
            checks["parser_labels_explicit_options_only"] = labelled_ok
            if part == 2:
                q = segs[0]["text_en"]
                checks["part2_question_never_labelled"] = option_gap_spoken_text(
                    part=2, segment_index=0, text_en=f"(A) {q}", option_label_gap_ms=GAP_MS) == f"(A) {q}"
            in_pack = gid in pack_meta
            pack_files_ok = None
            if in_pack:
                files = [n for n in PACK_HASHES if gid in n]
                pack_files_ok = all(sha(PACK / n) == PACK_HASHES[n] for n in files) and len(files) == 2
                checks["listening_pack_files_unchanged"] = pack_files_ok
            for k, v in checks.items():
                if not v:
                    failures.append(f"{gid}: {k}")
            rows.append({
                "batch": batch, "group_id": gid, "part": part, "current_version": g["version"],
                "target_version_on_promotion": g["version"] + 1, "family_id": g["family_id"], "pool": g["pool"],
                "item_id": item["item_id"], "answer_choice_id": item["answer_choice_id"],
                "asset_id": a["asset_id"], "asset_path": a["path"], "asset_sha256": a["sha256"],
                "duration_ms_declared": a["duration_ms"], "duration_ms_decoded": dec,
                "speakers": [{"speaker_id": s["speaker_id"], "accent": s["accent"]} for s in g["stimulus"]["speakers"]],
                "review_state": a["review_state"], "in_listening_pack": in_pack,
                "technical_checks": checks,
                "gates": {
                    "G1_human_iphone_speaker_approval_of_direction": "pending_user",
                    "G2_candidate_audio_synthesized": "candidate_in_pack_not_exported" if in_pack else "not_started",
                    "G3_remeasured_segment_times_duration_sha256": "not_started",
                    "G4_audio_only_blind_solve": "not_run",
                    "G5_full_schema_validator_and_negative_tests": "not_started",
                    "G6_codex_real_importer_acceptance": "not_started",
                    "G7_human_review_headphones_and_speaker": "pending_user",
                    "G8_codex_seed_update_and_shipped": "not_started",
                },
            })
    OUT_JSON.write_text(json.dumps({
        "generated_by": "scripts/check_audio_promotion_readiness.py",
        "scope_group_count": len(rows), "label_gap_ms_requested": GAP_MS,
        "technical_precheck_failures": failures, "groups": rows,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"groups={len(rows)} in_pack={sum(r['in_listening_pack'] for r in rows)} failures={len(failures)}")
    for f in failures:
        print("  FAIL", f)
    sys.exit(0 if not failures and len(rows) == 16 else 1)


if __name__ == "__main__":
    main()
