#!/usr/bin/env python3
"""
Prepare a context-isolated blind solving input file from a draft groups.jsonl.
Strips all answer keys (answer_choice_id), evidence, explanations (explanation_zh),
distractor rationales (distractor_notes), and difficulty rationales so the
blind solver subagent only receives the stimulus, prompts, and choices.
"""

import argparse
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare blind input JSON from groups.jsonl")
    parser.add_argument("--groups", required=True, help="Path to draft groups.jsonl")
    parser.add_argument("--output", required=True, help="Path to output blind-input.json")
    parser.add_argument("--batch-id", required=True, help="Batch ID")
    args = parser.parse_args()

    groups_path = Path(args.groups)
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    blind_groups = []
    with groups_path.open("r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            group = json.loads(line)
            part = group["part"]
            layout = group["layout"]

            has_planned_image = any(
                a.get("kind") == "image" and a.get("status") == "planned"
                for a in group.get("assets", [])
            )
            blind_solvable = not (part == 1 and has_planned_image)

            stripped_items = []
            for item in group["items"]:
                stripped_items.append(
                    {
                        "item_id": item["item_id"],
                        "prompt_en": item["prompt_en"],
                        "choices": item["choices"],
                    }
                )

            blind_groups.append(
                {
                    "group_id": group["group_id"],
                    "part": part,
                    "layout": layout,
                    "scenario": group["scenario"],
                    "blind_solvable": blind_solvable,
                    "blind_skip_reason": (
                        "Part 1 圖片素材尚處於 status=planned，無實際圖檔可供純視覺盲解；待圖片就緒後再執行視覺盲解。"
                        if not blind_solvable
                        else None
                    ),
                    "stimulus": group["stimulus"],
                    "items": stripped_items,
                }
            )

    payload = {
        "batch_id": args.batch_id,
        "instructions": (
            "Independent blind solving sheet. Answer keys, evidence, and explanations "
            "have been stripped. For each group where blind_solvable is true, solve "
            "each item independently based ONLY on the provided stimulus and choices."
        ),
        "groups": blind_groups,
    }

    with out_path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
        f.write("\n")

    print(f"Prepared blind input with {len(blind_groups)} groups -> {out_path}")


if __name__ == "__main__":
    main()
