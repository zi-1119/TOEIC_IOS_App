#!/usr/bin/env python3
"""Build the local Karen Part 1 comparison with a measured label gap.

This reads the immutable seed group but writes only to artifacts/audio-comparison.
It never edits SeedContent or an Antigravity export.
"""

import json
from pathlib import Path

from synthesize_listening_audio import synthesize_group_audio


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "SeedContent" / "batch-ag-0006" / "groups.jsonl"
OUTPUT = (
    ROOT
    / "artifacts"
    / "audio-comparison"
    / "part1-research-laboratory"
    / "candidate-karen-labels-400ms-gap.m4a"
)
GROUP_ID = "ag-g-p1-000001"
LABEL_GAP_MS = 400


def load_group() -> dict:
    with SOURCE.open(encoding="utf-8") as source:
        for line in source:
            group = json.loads(line)
            if group.get("group_id") == GROUP_ID:
                return group
    raise RuntimeError(f"Missing {GROUP_ID} in {SOURCE}")


def main() -> None:
    group = load_group()
    group["stimulus"]["speakers"][0]["accent"] = "au"
    for label, segment in zip("ABCD", group["stimulus"]["audio_script"]):
        segment["text_en"] = f"({label}) {segment['text_en']}"

    metadata = synthesize_group_audio(
        group,
        OUTPUT,
        option_label_gap_ms=LABEL_GAP_MS,
    )
    print(json.dumps({"path": str(OUTPUT), **metadata}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
