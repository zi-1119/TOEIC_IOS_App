#!/usr/bin/env python3
"""
Negative unit test suite for scripts/validate_and_package.py AND full re-validation audit
of all historical batches (exports/batch-ag-0001 .. 0010).

Verifies that validate_batch strictly rejects:
  1. Missing evidence.reasoning_zh
  2. Placeholder evidence.reasoning_zh ("待補")
  3. Legacy vocabulary keys (surface/pos/note_zh instead of term_en/meaning_zh/example_en)
  4. Vocabulary entry as array instead of object
  5. Placeholder/short vocabulary.example_en
  6. Legacy document keys (doc_id/doc_type instead of document_id/genre)
  7. Extra trap_type in distractor_notes
  8. Extra prompt_hash in provenance
  9. Missing item_id in reviews.jsonl findings
  10. Invalid enum value (pool="practice" / difficulty.level="D9")
  11. Broken evidence reference (non-existent block_id / segment_id)
  12. Corrupted asset SHA-256 checksum
  13. Intra-batch duplicate group_id / item_id
  14. Cross-pool family_id conflict (same family_id in training and battle)
"""

import copy
import json
import tempfile
from pathlib import Path
from typing import Any, Callable, Dict, List, Tuple

from validate_and_package import ROOT, validate_batch


def load_baseline_sample() -> Tuple[Dict[str, Any], List[Dict[str, Any]], Dict[str, Any]]:
    b1 = ROOT / "exports" / "batch-ag-0001"
    groups = [json.loads(line) for line in (b1 / "groups.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    reviews = [json.loads(line) for line in (b1 / "reviews.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    blind = json.loads((b1 / "reports" / "blind-solve.json").read_text(encoding="utf-8"))
    # Use a single Part 5 group from batch-ag-0001 and a Part 6 group from batch-ag-0002 as clean templates
    g_p5 = copy.deepcopy(next(g for g in groups if g["part"] == 5))
    b2 = ROOT / "exports" / "batch-ag-0002"
    groups_b2 = [json.loads(line) for line in (b2 / "groups.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    g_p6 = copy.deepcopy(next(g for g in groups_b2 if g["part"] == 6))

    # Give them fresh test IDs so they don't collide with global-index.json unless testing cross-batch collision
    g_p5["group_id"] = "ag-g-p5-999001"
    g_p5["family_id"] = "ag-fam-test-999001"
    g_p5["prompt_test_unique"] = False
    del g_p5["prompt_test_unique"]
    g_p5["items"][0]["item_id"] = "ag-i-p5-999001-1"
    g_p5["items"][0]["prompt_en"] = "The regional compliance officer will ____ inspect the chemical storage lockers next Tuesday morning."
    g_p5["items"][0]["evidence"][0]["source_id"] = "ag-i-p5-999001-1"
    g_p5["items"][0]["evidence"][0]["quote_en"] = "will ____ inspect the chemical storage lockers"
    g_p5["review_refs"] = ["ag-rev-test-ai-1", "ag-rev-test-blind-1"]

    test_reviews = [
        {
            "review_id": "ag-rev-test-ai-1",
            "group_id": "ag-g-p5-999001",
            "group_version": 1,
            "item_ids": ["ag-i-p5-999001-1"],
            "reviewer_kind": "ai",
            "reviewer_name": "test-ai",
            "reviewer_model": "unknown",
            "reviewed_at": "2026-10-29T00:00:00Z",
            "blind": False,
            "verdict": "pass",
            "findings": [{"item_id": None, "severity": "info", "code": "ok", "note_zh": "測試通過"}],
        },
        {
            "review_id": "ag-rev-test-blind-1",
            "group_id": "ag-g-p5-999001",
            "group_version": 1,
            "item_ids": ["ag-i-p5-999001-1"],
            "reviewer_kind": "ai",
            "reviewer_name": "test-blind",
            "reviewer_model": "unknown",
            "reviewed_at": "2026-10-29T00:00:00Z",
            "blind": True,
            "verdict": "pass",
            "findings": [{"item_id": None, "severity": "info", "code": "ok", "note_zh": "盲解通過"}],
        },
    ]
    test_blind = {
        "batch_id": "batch-test-neg",
        "items": [
            {
                "group_id": "ag-g-p5-999001",
                "item_id": "ag-i-p5-999001-1",
                "selected_choice_id": g_p5["items"][0]["answer_choice_id"],
            }
        ],
    }
    return g_p5, test_reviews, test_blind, g_p6


def run_case(
    name: str,
    mutate_fn: Callable[[List[Dict[str, Any]], List[Dict[str, Any]], Path], None],
    expected_failed_check_id: str,
) -> Dict[str, Any]:
    g_p5, test_reviews, test_blind, _ = load_baseline_sample()
    groups = [copy.deepcopy(g_p5)]
    reviews = copy.deepcopy(test_reviews)

    with tempfile.TemporaryDirectory() as tmp:
        tdir = Path(tmp)
        (tdir / "reports").mkdir(parents=True, exist_ok=True)
        (tdir / "assets").mkdir(parents=True, exist_ok=True)
        (tdir / "reports" / "summary.md").write_text("# Test Summary\n", encoding="utf-8")
        (tdir / "reports" / "blind-solve.json").write_text(json.dumps(test_blind), encoding="utf-8")

        mutate_fn(groups, reviews, tdir)

        with (tdir / "groups.jsonl").open("w", encoding="utf-8") as f:
            for g in groups:
                f.write(json.dumps(g, ensure_ascii=False) + "\n")
        with (tdir / "reviews.jsonl").open("w", encoding="utf-8") as f:
            for r in reviews:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")

        rep, _, _ = validate_batch(tdir, "batch-test-neg")
        failed_ids = [c["check_id"] for c in rep["checks"] if c["status"] == "fail"]
        passed = (rep["overall_result"] == "fail") and (expected_failed_check_id in failed_ids)
        if not passed:
            raise AssertionError(
                f"Negative test '{name}' FAILED to reject! Expected {expected_failed_check_id} in {failed_ids}, got overall={rep['overall_result']}"
            )
        msg = next(c["message_zh"] for c in rep["checks"] if c["check_id"] == expected_failed_check_id)
        return {
            "test_name": name,
            "expected_failed_check": expected_failed_check_id,
            "actual_failed_checks": failed_ids,
            "overall_result": rep["overall_result"],
            "rejected_correctly": True,
            "sample_error_message_zh": msg[:180],
        }


def main() -> None:
    results = []

    # First verify unmutated baseline passes (0 fails)
    g_p5, test_reviews, test_blind, g_p6 = load_baseline_sample()
    with tempfile.TemporaryDirectory() as tmp:
        tdir = Path(tmp)
        (tdir / "reports").mkdir(parents=True, exist_ok=True)
        (tdir / "reports" / "summary.md").write_text("# Clean\n", encoding="utf-8")
        (tdir / "reports" / "blind-solve.json").write_text(json.dumps(test_blind), encoding="utf-8")
        (tdir / "groups.jsonl").write_text(json.dumps(g_p5, ensure_ascii=False) + "\n", encoding="utf-8")
        (tdir / "reviews.jsonl").write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in test_reviews) + "\n", encoding="utf-8")
        clean_rep, _, _ = validate_batch(tdir, "batch-test-clean")
        assert clean_rep["counts"]["fail"] == 0, f"Clean baseline failed: {clean_rep}"

    # 1. Missing evidence.reasoning_zh
    def m_missing_reasoning(gs, rs, d):
        del gs[0]["items"][0]["evidence"][0]["reasoning_zh"]
    results.append(run_case("missing_evidence_reasoning_zh", m_missing_reasoning, "structure-001"))

    # 2. Placeholder evidence.reasoning_zh ("待補")
    def m_placeholder_reasoning(gs, rs, d):
        gs[0]["items"][0]["evidence"][0]["reasoning_zh"] = "待補"
    results.append(run_case("placeholder_evidence_reasoning_zh", m_placeholder_reasoning, "content_quality-001"))

    # 3. Wrong vocabulary keys (surface/pos/note_zh)
    def m_bad_vocab_keys(gs, rs, d):
        gs[0]["items"][0]["vocabulary"] = [{"surface": "inspect", "meaning_zh": "檢查", "pos": "v.", "note_zh": "test"}]
    results.append(run_case("wrong_vocabulary_keys_surface_pos", m_bad_vocab_keys, "structure-001"))

    # 4. Vocabulary item as array instead of object
    def m_vocab_array(gs, rs, d):
        gs[0]["items"][0]["vocabulary"] = [["inspect", "檢查", "v.", "test"]]
    results.append(run_case("vocabulary_entry_is_array_not_object", m_vocab_array, "structure-001"))

    # 5. Placeholder vocabulary.example_en
    def m_placeholder_example(gs, rs, d):
        gs[0]["items"][0]["vocabulary"][0]["example_en"] = "TODO"
    results.append(run_case("placeholder_vocabulary_example_en", m_placeholder_example, "content_quality-001"))

    # 6. Wrong document keys (doc_id/doc_type instead of document_id/genre)
    def m_bad_doc_keys(gs, rs, d):
        gs[0]["stimulus"]["documents"] = [
            {
                "doc_id": "ag-doc-bad-1",
                "doc_type": "memo",
                "title_en": "Bad Doc",
                "blocks": [{"block_id": "b1", "type": "text", "text_en": "Sample text."}],
            }
        ]
    results.append(run_case("wrong_document_keys_doc_id_doc_type", m_bad_doc_keys, "structure-001"))

    # 7. Extra trap_type in distractor_notes
    def m_extra_trap_type(gs, rs, d):
        gs[0]["items"][0]["distractor_notes"][0]["trap_type"] = "word_form"
    results.append(run_case("extra_field_distractor_notes_trap_type", m_extra_trap_type, "structure-001"))

    # 8. Extra prompt_hash in provenance
    def m_extra_prompt_hash(gs, rs, d):
        gs[0]["provenance"]["prompt_hash"] = "sha256:12345"
    results.append(run_case("extra_field_provenance_prompt_hash", m_extra_prompt_hash, "structure-001"))

    # 9. Missing item_id in reviews.jsonl findings
    def m_missing_finding_item_id(gs, rs, d):
        del rs[0]["findings"][0]["item_id"]
    results.append(run_case("missing_review_finding_item_id", m_missing_finding_item_id, "structure-001"))

    # 10. Wrong enum (pool="practice", difficulty.level="D9")
    def m_bad_enum(gs, rs, d):
        gs[0]["pool"] = "practice"
        gs[0]["difficulty"]["level"] = "D9"
    results.append(run_case("invalid_enum_pool_and_difficulty", m_bad_enum, "structure-001"))

    # 11. Broken evidence reference
    def m_broken_ref(gs, rs, d):
        gs[0]["items"][0]["evidence"][0]["source_type"] = "document_block"
        gs[0]["items"][0]["evidence"][0]["source_id"] = "non-existent-block-999"
    results.append(run_case("broken_evidence_reference", m_broken_ref, "references-001"))

    # 12. Bad asset SHA-256 hash
    def m_bad_asset_hash(gs, rs, d):
        f_path = d / "assets" / "dummy.m4a"
        f_path.write_bytes(b"real bytes")
        gs[0]["assets"] = [
            {
                "asset_id": "ag-ast-test-bad-sha",
                "kind": "audio",
                "status": "ready",
                "path": "assets/dummy.m4a",
                "sha256": "0" * 64,
                "mime_type": "audio/mp4",
                "duration_ms": 1000,
                "source_note_zh": "測試損毀雜湊",
                "review_state": "ai_checked",
                "segment_times": [],
            }
        ]
    results.append(run_case("bad_asset_sha256_checksum", m_bad_asset_hash, "assets-001"))

    # 13. Duplicate group_id / item_id
    def m_dup_ids(gs, rs, d):
        gs.append(copy.deepcopy(gs[0]))
    results.append(run_case("duplicate_intra_batch_group_and_item_id", m_dup_ids, "uniqueness-001"))

    # 14. Cross-pool family_id conflict
    def m_cross_pool_family(gs, rs, d):
        g2 = copy.deepcopy(gs[0])
        g2["group_id"] = "ag-g-p5-999002"
        g2["items"][0]["item_id"] = "ag-i-p5-999002-1"
        g2["items"][0]["evidence"][0]["source_id"] = "ag-i-p5-999002-1"
        g2["pool"] = "battle"  # Same family_id ag-fam-test-999001 in training and battle!
        gs.append(g2)
    results.append(run_case("cross_pool_family_id_conflict", m_cross_pool_family, "uniqueness-001"))

    # 15. Evidence quote not present in referenced source (off-by-one / wrong pointer, found in 0012/0013 v2 Part 2)
    def m_quote_not_in_source(gs, rs, d):
        gs[0]["items"][0]["evidence"][0]["quote_en"] = "Yes, the slides are ready for the client briefing."
    results.append(run_case("evidence_quote_not_in_referenced_source", m_quote_not_in_source, "references-001"))

    # 16. Wrong scalar type (estimated_time_sec as string, fixture as string)
    def m_wrong_type(gs, rs, d):
        gs[0]["items"][0]["estimated_time_sec"] = "30"
        gs[0]["fixture"] = "false"
    results.append(run_case("wrong_scalar_types", m_wrong_type, "structure-001"))

    # 17. Missing required top-level field (family_id)
    def m_missing_required(gs, rs, d):
        del gs[0]["family_id"]
    results.append(run_case("missing_required_family_id", m_missing_required, "structure-001"))

    # Now re-validate all existing batches in exports/batch-ag-*
    reval_batches = []
    for bdir in sorted((ROOT / "exports").iterdir()):
        if not bdir.is_dir() or not bdir.name.startswith("batch-ag-"):
            continue
        bid = bdir.name
        old_val = json.loads((bdir / "reports" / "validation.json").read_text(encoding="utf-8"))
        new_val, _, _ = validate_batch(bdir, bid)
        failed_checks = [
            {"check_id": c["check_id"], "code": c["code"], "message_zh": c["message_zh"]}
            for c in new_val["checks"]
            if c["status"] == "fail"
        ]
        reval_batches.append({
            "batch_id": bid,
            "historical_overall_result": old_val["overall_result"],
            "historical_counts": old_val["counts"],
            "revalidated_overall_result": new_val["overall_result"],
            "revalidated_counts": new_val["counts"],
            "was_false_positive_in_history": (old_val["counts"]["fail"] == 0 and new_val["counts"]["fail"] > 0),
            "failed_checks": failed_checks,
        })

    out_payload = {
        "negative_test_count": len(results),
        "all_negative_tests_passed": all(r["rejected_correctly"] for r in results),
        "negative_tests": results,
        "historical_batches_revalidation": reval_batches,
    }
    out_path = ROOT / "reports" / "revalidation-audit-2026-10-31.json"
    out_path.write_text(json.dumps(out_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"All {len(results)} negative tests passed! Re-validated {len(reval_batches)} batches -> {out_path}")
    for rb in reval_batches:
        print(
            f"  {rb['batch_id']}: historical={rb['historical_overall_result']}({rb['historical_counts']}) "
            f"-> revalidated={rb['revalidated_overall_result']}({rb['revalidated_counts']}) "
            f"false_positive={rb['was_false_positive_in_history']}"
        )


if __name__ == "__main__":
    main()
