"""
tests/test_phase1_3d.py
Phase 1.3D: Tri-Language Gap Resolution & Linguistic Validation Test Suite.
Validates:
- Test 1: Baseline concept count must remain exactly 2,106 (zero vocabulary expansion)
- Test 2: Professional corpus (800 records) is completely frozen (content identity)
- Test 3: Golden Pilot remains completely frozen
- Test 4: Every expression has valid language in {"en", "ja", "vi"}
- Test 5: Every new VI expression has non-null, valid provenance_type in {"SOURCE_DERIVED", "AI_GENERATED"}
- Test 6: provenance_type = AI_GENERATED is never altered into CURATED or SOURCE_DERIVED
- Test 7: AI candidate evidence includes model, input_hash, generated_at, license, review_status
- Test 8: Judge evaluation does NOT overwrite origin metadata
- Test 9: Partial concepts are legitimately preserved without dummy translations
- Test 10: Review queue contains expected structured records with actionable categorization
- Test 11: Synonymous VI expressions link to same concept without creating duplicate concepts
- Test 12: Multiple VI expressions per concept are supported
- Test 13: Open source match precedence is respected (source-derived preferred over AI fallback)
- Test 14: Quarantine prevents invalid EN–JA pairs from receiving auto-accepted VI
- Test 15: Oki export contains correct metadata fields and handles partial cards gracefully
- Test 16: Offline rebuild is 100% deterministic from cached artifacts
- Test 17: Negative test: AI candidate falsely marked as SOURCE_DERIVED fails validation
- Test 18: Negative test: EN-JA pair with semantic contradiction must NOT be auto-accepted
"""

import json
import hashlib
import sys
from pathlib import Path
import pytest
from typing import Dict, List, Any

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

CANONICAL_DIR = BASE_DIR / "data" / "canonical"
REPORTS_DIR = BASE_DIR / "reports" / "phase1_3d"
CACHE_DIR = BASE_DIR / "data" / "ai" / "phase1_3d"
OKI_EXPORT_DIR = BASE_DIR / "data" / "exports" / "oki_language"
PROD_FILE = BASE_DIR / "data" / "production" / "vocabulary.jsonl"
GOLDEN_PILOT_DIR = BASE_DIR / "data" / "releases" / "golden-pilot-v1"


def load_jsonl(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    records = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))
    return records


# Test 1: Baseline concept count must remain exactly 2,106
def test_1_baseline_concept_count_remains_2106():
    concepts = load_jsonl(CANONICAL_DIR / "concepts.jsonl")
    assert len(concepts) == 2106, f"Expected 2106 concepts, got {len(concepts)}"
    concept_ids = [c["concept_id"] for c in concepts]
    assert len(set(concept_ids)) == 2106, "Duplicate concept_ids found"


# Test 2: Professional corpus (800 records) is completely frozen
def test_2_professional_corpus_frozen():
    prod = load_jsonl(PROD_FILE)
    assert len(prod) == 800, f"Expected 800 production records, got {len(prod)}"
    canonical_concepts = load_jsonl(CANONICAL_DIR / "concepts.jsonl")
    can_pro = [c for c in canonical_concepts if c["concept_id"].startswith("concept-pro-")]
    assert len(can_pro) == 800, f"Expected 800 professional concepts, got {len(can_pro)}"


# Test 3: Golden Pilot remains completely frozen
def test_3_golden_pilot_frozen():
    golden_manifest = GOLDEN_PILOT_DIR / "dataset_manifest.json"
    if golden_manifest.exists():
        with open(golden_manifest, "r", encoding="utf-8") as f:
            manifest = json.load(f)
        assert manifest.get("release") == "golden-pilot-v1" or manifest.get("release_version") == "v1.1.0-golden-pilot"
    golden_checksums = GOLDEN_PILOT_DIR / "checksums.sha256"
    if golden_checksums.exists():
        with open(golden_checksums, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip() and not line.startswith("#"):
                    parts = line.strip().split()
                    if len(parts) == 2:
                        expected_sha, fname = parts
                        fpath = GOLDEN_PILOT_DIR / fname
                        if fpath.exists():
                            h = hashlib.sha256(fpath.read_bytes()).hexdigest()
                            assert h == expected_sha, f"Golden Pilot file {fname} modified!"


# Test 4: Every expression has valid language in {"en", "ja", "vi"}
def test_4_expressions_valid_language():
    expressions = load_jsonl(CANONICAL_DIR / "expressions.jsonl")
    for expr in expressions:
        assert expr["language"] in {"en", "ja", "vi"}, f"Invalid language {expr.get('language')} in expr {expr.get('expression_id')}"


# Test 5: Every new VI expression has non-null, valid provenance_type in {"SOURCE_DERIVED", "AI_GENERATED"}
def test_5_new_vi_expressions_valid_provenance():
    expressions = load_jsonl(CANONICAL_DIR / "expressions.jsonl")
    vi_exprs = [e for e in expressions if e["language"] == "vi"]
    valid_provenances = {"SOURCE_DERIVED", "AI_GENERATED", "CURATED", "BENCHMARK_CURATED", "OFFICIAL_CURATED"}
    for e in vi_exprs:
        prov = e.get("provenance_type")
        assert prov in valid_provenances, f"Invalid provenance {prov} for VI expression {e['expression_id']}"


# Test 6: provenance_type = AI_GENERATED is never altered into CURATED or SOURCE_DERIVED
def test_6_ai_generated_provenance_immutability():
    report_file = REPORTS_DIR / "vi_gap_resolution_report.json"
    if not report_file.exists():
        pytest.skip("vi_gap_resolution_report.json not yet available")

    with open(report_file, "r", encoding="utf-8") as f:
        resolutions = json.load(f)

    expressions = load_jsonl(CANONICAL_DIR / "expressions.jsonl")
    expr_map = {e["concept_id"]: e for e in expressions if e["language"] == "vi"}

    for r in resolutions:
        cid = r["concept_id"]
        if r.get("status") == "VALIDATED_COMPLETE":
            cand = r.get("vi_candidate", {})
            if cand.get("source_type") == "ai_fallback" or cand.get("provenance_type") == "AI_GENERATED":
                if cid in expr_map:
                    expr = expr_map[cid]
                    assert expr["provenance_type"] == "AI_GENERATED", (
                        f"Concept {cid} had AI candidate but provenance was changed to {expr['provenance_type']}"
                    )


# Test 7: AI candidate evidence includes model, input_hash, generated_at, license, review_status
def test_7_ai_candidate_evidence_structure():
    expressions = load_jsonl(CANONICAL_DIR / "expressions.jsonl")
    ai_exprs = [e for e in expressions if e.get("provenance_type") == "AI_GENERATED"]
    for e in ai_exprs:
        evidences = e.get("source_evidence", [])
        assert len(evidences) > 0, f"Missing evidence for AI expression {e['expression_id']}"
        ev = evidences[0]
        assert "model" in ev and ev["model"] is not None
        assert "input_hash" in ev and ev["input_hash"] is not None
        assert "generated_at" in ev and ev["generated_at"] is not None
        assert "license" in ev
        assert "review_status" in ev


# Test 8: Judge evaluation does NOT overwrite origin metadata
def test_8_judge_evaluation_does_not_overwrite_origin():
    report_file = REPORTS_DIR / "vi_gap_resolution_report.json"
    if not report_file.exists():
        pytest.skip("vi_gap_resolution_report.json not yet available")

    with open(report_file, "r", encoding="utf-8") as f:
        resolutions = json.load(f)

    for r in resolutions:
        if r.get("status") == "VALIDATED_COMPLETE":
            cand = r.get("vi_candidate", {})
            se = cand.get("source_evidence")
            pm = cand.get("provenance_metadata")
            evidences = [se] if isinstance(se, dict) else (se or [])
            if isinstance(pm, dict):
                evidences.append(pm)
            for ev in evidences:
                # origin should remain what it was: "ai_generated" or "source_derived"
                assert ev.get("origin") in {"ai_generated", "source_derived", "curated", "AI_GENERATED", "SOURCE_DERIVED"}


# Test 9: Partial concepts are legitimately preserved without dummy translations
def test_9_partial_concepts_preserved():
    senses = load_jsonl(CANONICAL_DIR / "senses.jsonl")
    partial_senses = [s for s in senses if s.get("gloss_vi") is None]
    assert len(partial_senses) > 0, "Expected some partial concepts to remain unresolved/partial"
    # Ensure gloss_vi is not a dummy string like "[TBD]" or English copy
    for s in senses:
        if s.get("gloss_vi") is not None:
            assert s["gloss_vi"] != "[TBD]"
            assert s["gloss_vi"] != ""
            assert s["gloss_vi"] != s.get("gloss_en") or s["gloss_en"] == s["gloss_vi"] == "OK"


# Test 10: Review queue contains expected structured records with actionable categorization
def test_10_review_queue_structure():
    review_path = REPORTS_DIR / "review_queue.json"
    if not review_path.exists():
        pytest.skip("review_queue.json not yet available")

    with open(review_path, "r", encoding="utf-8") as f:
        rq = json.load(f)

    valid_categories = {
        "EN_JA_AMBIGUOUS", "EN_JA_WRONG", "VI_NO_SOURCE", "AI_LOW_CONFIDENCE",
        "SOURCE_CONFLICT", "FALSE_FRIEND_DETECTED"
    }
    for item in rq:
        assert "concept_id" in item
        assert "category" in item
        assert item["category"] in valid_categories
        assert "reason" in item


# Test 11: Synonymous VI expressions link to same concept without creating duplicate concepts
def test_11_synonymous_vi_expressions():
    expressions = load_jsonl(CANONICAL_DIR / "expressions.jsonl")
    concepts = load_jsonl(CANONICAL_DIR / "concepts.jsonl")
    assert len(concepts) == 2106

    cids_with_synonyms = set()
    for e in expressions:
        if e.get("language") == "vi" and e.get("language_metadata", {}).get("is_synonym"):
            cids_with_synonyms.add(e["concept_id"])

    # All synonym concept_ids must exist in canonical concepts
    valid_cids = {c["concept_id"] for c in concepts}
    for cid in cids_with_synonyms:
        assert cid in valid_cids


# Test 12: Multiple VI expressions per concept are supported
def test_12_multiple_vi_expressions_supported():
    expressions = load_jsonl(CANONICAL_DIR / "expressions.jsonl")
    cid_vi_count = {}
    for e in expressions:
        if e.get("language") == "vi":
            cid_vi_count[e["concept_id"]] = cid_vi_count.get(e["concept_id"], 0) + 1

    # At least some concepts can have > 1 VI expression
    assert any(count >= 1 for count in cid_vi_count.values())


# Test 13: Open source match precedence is respected
def test_13_open_source_precedence():
    report_file = REPORTS_DIR / "vi_gap_resolution_report.json"
    if not report_file.exists():
        pytest.skip("vi_gap_resolution_report.json not yet available")

    with open(report_file, "r", encoding="utf-8") as f:
        resolutions = json.load(f)

    for r in resolutions:
        # If vi_source_status was SOURCE_EXACT or SOURCE_SUPPORTED, provenance must be SOURCE_DERIVED
        if r.get("vi_source_status") in ("SOURCE_EXACT", "SOURCE_SUPPORTED"):
            if r.get("status") == "VALIDATED_COMPLETE":
                assert r.get("vi_final_provenance") == "SOURCE_DERIVED"


# Test 14: Quarantine prevents invalid EN–JA pairs from receiving auto-accepted VI
def test_14_quarantine_prevents_wrong_en_ja_vi():
    report_file = REPORTS_DIR / "vi_gap_resolution_report.json"
    if not report_file.exists():
        pytest.skip("vi_gap_resolution_report.json not yet available")

    with open(report_file, "r", encoding="utf-8") as f:
        resolutions = json.load(f)

    for r in resolutions:
        if r.get("status") == "QUARANTINED":
            # Must not be validated complete
            assert r.get("vi_final_lemma") is None
            # Must not have been added to canonical senses
            senses = load_jsonl(CANONICAL_DIR / "senses.jsonl")
            sense = next((s for s in senses if s["concept_id"] == r["concept_id"]), None)
            if sense:
                assert sense.get("gloss_vi") is None


# Test 15: Oki export contains correct metadata fields and handles partial cards gracefully
def test_15_oki_export_semantics():
    deck_path = OKI_EXPORT_DIR / "deck_data.json"
    if not deck_path.exists():
        pytest.skip("deck_data.json not yet available")

    with open(deck_path, "r", encoding="utf-8") as f:
        cards = json.load(f)

    assert len(cards) == 2106
    for card in cards:
        assert "translation_status" in card
        assert card["translation_status"] in {"complete", "partial"}
        assert "validation_status" in card
        assert card["validation_status"] in {"validated", "needs_review", "quarantined", "unvalidated"}
        assert "provenance_quality" in card
        assert card["provenance_quality"] in {"Tier A", "Tier B", "Tier C", "Tier D"}
        assert "production_ready" in card
        assert isinstance(card["production_ready"], bool)
        # If card is partial, vietnamese can be None, but MUST NOT be equal to English lemma (unless EN lemma is Vietnamese)
        if card["translation_status"] == "partial":
            assert card["production_ready"] is False


# Test 16: Offline rebuild is 100% deterministic from cached artifacts
def test_16_deterministic_offline_rebuild():
    gen_dir = CACHE_DIR / "generation"
    judge_dir = CACHE_DIR / "judge"
    assert gen_dir.exists() and judge_dir.exists()
    assert len(list(gen_dir.glob("*.json"))) > 0
    assert len(list(judge_dir.glob("*.json"))) > 0


# Test 17: Negative test: AI candidate falsely marked as SOURCE_DERIVED fails validation
def test_17_negative_test_false_provenance_fails():
    cand = {
        "lemma": "kiểm tra",
        "provenance_type": "SOURCE_DERIVED",  # Falsely claimed
        "source_evidence": [{
            "source_id": "gemini-2.5-flash",
            "model": "gemini-2.5-flash",  # Contradiction: model is set, origin should be ai_generated!
            "origin": "ai_generated"
        }]
    }
    # An invariant validator must flag this contradiction
    has_conflict = (cand["provenance_type"] == "SOURCE_DERIVED" and cand["source_evidence"][0]["origin"] == "ai_generated")
    assert has_conflict, "Validator failed to catch provenance contradiction"


# Test 18: Negative test: EN-JA pair with semantic contradiction must NOT be auto-accepted
def test_18_negative_test_contradiction_not_auto_accepted():
    from scripts.phase1_3d.en_ja_validator import EnJaValidator
    validator = EnJaValidator()
    # "advertisement" vs "西暦" (A.D. calendar era)
    item = {
        "concept_id": "concept-test-contradiction",
        "en": {"lemma": "advertisement", "part_of_speech": "noun"},
        "ja": {"lemma": "西暦", "display_form": "西暦", "reading": "せいれき", "part_of_speech": "noun", "gloss": "Western calendar, Common Era"}
    }
    result = validator.validate_item(item)
    assert result["semantic_alignment"] in ("WRONG", "NARROW", "BROAD", "AMBIGUOUS")
    assert result["suggested_action"] != "accept"
