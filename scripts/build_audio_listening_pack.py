#!/usr/bin/env python3
"""
Build a SMALL listening pack (candidates only, not an export, not human_reviewed) for the Part 1/2
spoken-label regression in handoff/2026-10-29-mvp/03-antigravity-audio-regression.md.

Direction under test (user-preferred, still pending iPhone-speaker confirmation):
  Karen (en_AU) + spoken A–D labels + requested 400 ms label-to-statement gap, existing 172 WPM / AAC pipeline.

Writes only to assets_work/audio-listening-pack-2026-10-31/. Reads immutable exports. Never edits exports/SeedContent.
  python3 scripts/build_audio_listening_pack.py
"""
import copy
import hashlib
import json
import re
import shutil
import subprocess
from pathlib import Path

from synthesize_listening_audio import synthesize_group_audio

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets_work" / "audio-listening-pack-2026-10-31"
LABEL_GAP_MS = 400

# (batch, group_id, note)
SAMPLES = [
    ("batch-ag-0006", "ag-g-p1-000001", "實機回報混濁、無標號之原題（研究室顯微鏡）"),
    ("batch-ag-0007", "ag-g-p1-000002", "原為 uk 聲線（麵包店）"),
    ("batch-ag-0007", "ag-g-p1-000003", "原即 Karen，實機評為最清楚；本候選只加標號＋間隔"),
    ("batch-ag-0007", "ag-g-p2-000004", "Part 2：回應者原即 Karen；題目句不加標號，只加 A–C"),
    ("batch-ag-0007", "ag-g-p2-000002", "Part 2：回應者由 us 改 Karen；題目句維持 uk 聲線"),
]


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def load_group(batch: str, gid: str) -> dict:
    for line in (ROOT / "exports" / batch / "groups.jsonl").read_text(encoding="utf-8").splitlines():
        g = json.loads(line)
        if g["group_id"] == gid:
            return g
    raise KeyError(gid)


def measure(path: Path) -> dict:
    probe = json.loads(subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "stream=codec_name,sample_rate,channels,bit_rate:format=duration",
         "-of", "json", str(path)], capture_output=True, text=True, check=True).stdout)
    st = probe["streams"][0]
    log = subprocess.run(
        ["ffmpeg", "-nostats", "-hide_banner", "-i", str(path),
         "-af", "ebur128=peak=true,silencedetect=n=-45dB:d=0.25", "-f", "null", "-"],
        capture_output=True, text=True).stderr
    summary = log[log.rfind("Summary:"):] if "Summary:" in log else ""
    lufs = re.search(r"I:\s+(-?[\d.]+) LUFS", summary)
    peak = re.search(r"Peak:\s+(-?[\d.]+|-inf) dBFS", summary)
    silences = [(float(a), float(b)) for a, b in re.findall(r"silence_end: ([\d.]+) \| silence_duration: ([\d.]+)", log)]
    return {
        "codec": st.get("codec_name"), "sample_rate": int(st.get("sample_rate", 0)), "channels": st.get("channels"),
        "bit_rate": int(st.get("bit_rate", 0) or 0), "duration_s": round(float(probe["format"]["duration"]), 3),
        "integrated_lufs": float(lufs.group(1)) if lufs else None,
        "true_peak_dbfs": peak.group(1) if peak else None,
        "silences_ms": [{"end_ms": round(e * 1000), "duration_ms": round(d * 1000)} for e, d in silences],
    }


def main() -> None:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    records = []
    for idx, (batch, gid, note) in enumerate(SAMPLES, 1):
        src_group = load_group(batch, gid)
        audio = next(a for a in src_group["assets"] if a["kind"] == "audio")
        orig_path = ROOT / "exports" / batch / audio["path"]
        orig_out = OUT / f"{idx:02d}-{gid}-A-original.m4a"
        shutil.copy2(orig_path, orig_out)

        g = copy.deepcopy(src_group)
        part = g["part"]
        segs = g["stimulus"]["audio_script"]
        option_segs = segs if part == 1 else segs[1:]  # Part 2: question segment never gets a label
        for label, seg in zip("ABCD", option_segs):
            if re.match(r"^\s*\([A-D]\)", seg["text_en"]):
                raise RuntimeError(f"{gid} already labelled")
            seg["text_en"] = f"({label}) {seg['text_en']}"
        if part == 2:
            q = segs[0]["text_en"]
            if re.match(r"^\s*\(?[A-D]\)?[\s.:-]", q):
                raise RuntimeError(f"{gid}: question would be mis-parsed as a label: {q!r}")
        responder = segs[-1]["speaker_id"]
        for spk in g["stimulus"]["speakers"]:
            if part == 1 or spk["speaker_id"] == responder:
                spk["accent"] = "au"  # Karen
        cand_out = OUT / f"{idx:02d}-{gid}-B-karen-labels-400ms.m4a"
        meta = synthesize_group_audio(g, cand_out, option_label_gap_ms=LABEL_GAP_MS)

        answer = src_group["items"][0]["answer_choice_id"]
        records.append({
            "sample": idx, "group_id": gid, "group_version_in_export": src_group["version"], "source_batch": batch,
            "part": part, "note_zh": note, "answer_choice_id": answer,
            "original": {"file": orig_out.name, "sha256": sha(orig_out), "export_segment_times": audio.get("segment_times"),
                         "metrics": measure(orig_out)},
            "candidate": {"file": cand_out.name, "sha256": meta["sha256"], "duration_ms": meta["duration_ms"],
                          "segment_times": meta["segment_times"], "voice_cast": meta["voice_cast"],
                          "requested_label_gap_ms": LABEL_GAP_MS, "spoken_script": [
                              {"segment_id": s["segment_id"], "text_en": s["text_en"]} for s in segs],
                          "metrics": measure(cand_out)},
            "audio_only_blind_solve": "not_run",
            "human_listening": "pending_user_iphone_speaker",
        })

    (OUT / "listening-pack.json").write_text(json.dumps({
        "created_for": "handoff/2026-10-29-mvp/03-antigravity-audio-regression.md",
        "status": "candidate_only_not_exported_not_human_reviewed",
        "pipeline": "macOS /usr/bin/say 172 WPM, LEI16@22050 → afconvert AAC 64 kbps mono (no upsampling/gain tricks)",
        "samples": records}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for r in records:
        c, o = r["candidate"]["metrics"], r["original"]["metrics"]
        print(f"{r['sample']:02d} {r['group_id']}: orig {o['duration_s']}s {o['integrated_lufs']}LUFS pk{o['true_peak_dbfs']} | "
              f"cand {c['duration_s']}s {c['integrated_lufs']}LUFS pk{c['true_peak_dbfs']} | "
              f"cand silences {[s['duration_ms'] for s in c['silences_ms']]}")


if __name__ == "__main__":
    main()
