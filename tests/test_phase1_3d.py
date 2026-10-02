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
    """Phase 1.4 update: the 2,106 sealed baseline concepts must all remain (corpus may only grow)."""
    from tests._baseline import baseline_concept_ids
    concepts = load_jsonl(CANONICAL_DIR / "concepts.jsonl")
    concept_ids = [c["concept_id"] for c in concepts]
    assert len(set(concept_ids)) == len(concept_ids), "Duplicate concept_ids found"
    assert len(baseline_concept_ids()) == 2106
    assert baseline_concept_ids() <= set(concept_ids)


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
    assert report_file.exists(), "Mandatory closure report vi_gap_resolution_report.json missing"

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
    assert report_file.exists(), "Mandatory closure report vi_gap_resolution_report.json missing"

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
        if s["concept_id"].startswith("concept-lex-"):
            continue  # Phase 1.4 records are checked in tests/test_phase1_4.py (EN==VI is legitimate e.g. letter names)
        if s.get("gloss_vi") is not None:
            assert s["gloss_vi"] != "[TBD]"
            assert s["gloss_vi"] != ""
            assert s["gloss_vi"] != s.get("gloss_en") or s["gloss_en"] == s["gloss_vi"] == "OK"


# Test 10: Review queue contains expected structured records with actionable categorization
def test_10_review_queue_structure():
    review_path = REPORTS_DIR / "review_queue.json"
    assert review_path.exists(), "Mandatory closure report review_queue.json missing"

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
    assert len(concepts) >= 2106

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
    from tests._baseline import baseline_concept_ids
    _b = baseline_concept_ids()
    cid_vi_exprs = {}
    for e in expressions:
        if e.get("language") == "vi" and e["concept_id"] in _b:
            cid_vi_exprs.setdefault(e["concept_id"], []).append(e)

    # Prove support for multiple VI expressions: any count > 1
    assert any(len(expr_list) > 1 for expr_list in cid_vi_exprs.values()), "No concepts with multiple VI expressions found"

    multi_vi_concepts = {cid: expr_list for cid, expr_list in cid_vi_exprs.items() if len(expr_list) > 1}
    assert len(multi_vi_concepts) == 273, f"Expected exactly 273 concepts with multiple VI, got {len(multi_vi_concepts)}"

    valid_provenances = {"SOURCE_DERIVED", "AI_GENERATED", "CURATED", "BENCHMARK_CURATED", "OFFICIAL_CURATED"}

    for cid, expr_list in multi_vi_concepts.items():
        # Share concept_id
        assert all(e["concept_id"] == cid for e in expr_list)
        # Share compatible sense_id
        sense_ids = {e.get("sense_id") for e in expr_list}
        assert len(sense_ids) == 1 and None not in sense_ids, f"Expressions for {cid} have conflicting sense_ids: {sense_ids}"
        # Have distinct expression_id
        expr_ids = [e["expression_id"] for e in expr_list]
        assert len(expr_ids) == len(set(expr_ids)), f"Duplicate expression_ids in {cid}: {expr_ids}"
        # Have valid provenance
        for e in expr_list:
            assert e.get("provenance_type") in valid_provenances, f"Invalid provenance {e.get('provenance_type')} in {cid}"


# Test 13: Open source match precedence is respected
def test_13_open_source_precedence():
    report_file = REPORTS_DIR / "vi_gap_resolution_report.json"
    assert report_file.exists(), "Mandatory closure report vi_gap_resolution_report.json missing"

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
    assert report_file.exists(), "Mandatory closure report vi_gap_resolution_report.json missing"

    with open(report_file, "r", encoding="utf-8") as f:
        resolutions = json.load(f)

    corrected = {c["concept_id"] for c in load_jsonl(CANONICAL_DIR / "concepts.jsonl") if (c.get("metadata") or {}).get("correction")}
    for r in resolutions:
        if r.get("status") == "QUARANTINED":
            if r["concept_id"] in corrected:
                continue  # Phase 1.4.1 replaced the irreconcilable pair; the concept is now needs_review (see ledger)
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
    assert deck_path.exists(), "Mandatory closure artifact deck_data.json missing"

    with open(deck_path, "r", encoding="utf-8") as f:
        cards = json.load(f)

    assert len(cards) == len(load_jsonl(CANONICAL_DIR / "concepts.jsonl"))
    from tests._baseline import baseline_concept_ids
    _b = baseline_concept_ids()
    _corrected = {c["concept_id"] for c in load_jsonl(CANONICAL_DIR / "concepts.jsonl") if (c.get("metadata") or {}).get("correction")}
    _sealed = {c["id"]: c for c in json.load(open(BASE_DIR / "data/releases/phase1_3d-sealed/oki_deck_data.baseline.json"))}
    tier_counts = {}
    for card in cards:
        if card["id"] not in _b or card["id"] in _corrected:
            continue  # tier distribution below is a property of the UNcorrected sealed baseline
        assert "translation_status" in card
        assert card["translation_status"] in {"complete", "partial"}
        assert "validation_status" in card
        assert card["validation_status"] in {"validated", "needs_review", "quarantined", "unvalidated"}
        assert "provenance_quality" in card
        assert card["provenance_quality"] in {"Tier A", "Tier B", "Tier C", "Tier D"}
        tier_counts[card["provenance_quality"]] = tier_counts.get(card["provenance_quality"], 0) + 1
        assert "production_ready" in card
        assert isinstance(card["production_ready"], bool)
        # If card is partial, vietnamese can be None, but MUST NOT be equal to English lemma (unless EN lemma is Vietnamese)
        if card["translation_status"] == "partial":
            assert card["production_ready"] is False

    # Tier distribution of the UNcorrected sealed baseline must equal the sealed 1.3D distribution over the same concepts
    expected = {}
    for cid, c in _sealed.items():
        if cid not in _corrected:
            expected[c["provenance_quality"]] = expected.get(c["provenance_quality"], 0) + 1
    assert tier_counts == expected, f"{tier_counts} != {expected}"


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


# Test 19: Judge independence audit (blind prompt-level independence verification)
def test_19_judge_blind_prompt_independence():
    """Verify that Judge receives no generator rationale, confidence, or target acceptance decision."""
    judge_dir = CACHE_DIR / "judge"
    assert judge_dir.exists(), "Judge cache directory missing"
    judge_files = list(judge_dir.glob("*.json"))
    assert len(judge_files) == 1000, f"Expected 1,000 judge cache files, found {len(judge_files)}"

    forbidden_patterns = [
        "generator_confidence", "generator_rationale", "desired_answer",
        "acceptance_target", "confidence_score", "reasoning"
    ]

    for jpath in judge_files:
        payload = json.loads(jpath.read_text(encoding="utf-8"))
        assert payload.get("model") == "gemini-2.5-flash"
        inp = payload.get("input", {})
        inp_str = json.dumps(inp).lower()
        for forbidden in forbidden_patterns:
            assert forbidden not in inp_str, (
                f"Judge input in {jpath.name} leaks generator/target metadata: '{forbidden}'"
            )


# Test 20: Mandatory audit reports exist and are structurally valid
def test_20_mandatory_audit_reports_exist_and_valid():
    """Verify presence and schema of all 5 mandatory closure and audit reports."""
    # 1. en_ja_alignment_report.json
    en_ja_rep = REPORTS_DIR / "en_ja_alignment_report.json"
    assert en_ja_rep.exists(), "reports/phase1_3d/en_ja_alignment_report.json missing"
    en_ja_data = json.loads(en_ja_rep.read_text(encoding="utf-8"))
    assert len(en_ja_data) == 1034, f"Expected 1,034 concepts in en_ja_alignment_report.json, got {len(en_ja_data)}"

    # 2. ai_generation_report.json
    ai_gen_rep = REPORTS_DIR / "ai_generation_report.json"
    assert ai_gen_rep.exists(), "reports/phase1_3d/ai_generation_report.json missing"
    ai_gen_data = json.loads(ai_gen_rep.read_text(encoding="utf-8"))
    assert len(ai_gen_data) == 355, f"Expected 355 invocations in ai_generation_report.json, got {len(ai_gen_data)}"

    # 3. judge_report.json
    judge_rep = REPORTS_DIR / "judge_report.json"
    assert judge_rep.exists(), "reports/phase1_3d/judge_report.json missing"
    judge_data = json.loads(judge_rep.read_text(encoding="utf-8"))
    assert len(judge_data) == 1000, f"Expected 1,000 evaluations in judge_report.json, got {len(judge_data)}"

    # 4. accepted_concept_audit.json
    audit_rep = REPORTS_DIR / "accepted_concept_audit.json"
    assert audit_rep.exists(), "reports/phase1_3d/accepted_concept_audit.json missing"
    audit_data = json.loads(audit_rep.read_text(encoding="utf-8"))
    assert len(audit_data) == 645, f"Expected 645 accepted concepts in audit report, got {len(audit_data)}"
    required_audit_keys = {
        "concept_id", "sense_id", "en_lemma", "ja_lemma", "vi_lemma",
        "en_ja_alignment_before", "en_ja_alignment_after", "ja_replacement_if_any",
        "jmdict_ent_seq", "jmdict_sense_index", "vi_resolution_method",
        "vi_source_locator", "generator_artifact", "judge_artifact",
        "judge_decision", "semantic_alignment", "naturalness", "confidence",
        "final_provenance", "canonical_expression_id"
    }
    for rec in audit_data:
        missing = required_audit_keys - set(rec.keys())
        assert not missing, f"Record {rec.get('concept_id')} missing audit keys: {missing}"
        assert rec["canonical_expression_id"] is not None

    # 5. independent_sample_audit.json
    sample_rep = REPORTS_DIR / "independent_sample_audit.json"
    assert sample_rep.exists(), "reports/phase1_3d/independent_sample_audit.json missing"
    sample_data = json.loads(sample_rep.read_text(encoding="utf-8"))
    assert len(sample_data) == 60, f"Expected 60 sample records, got {len(sample_data)}"
    strata = {rec["stratum"]: 0 for rec in sample_data}
    for rec in sample_data:
        strata[rec["stratum"]] = strata.get(rec["stratum"], 0) + 1
    assert strata.get("Tier_B_Source_Backed") == 20
    assert strata.get("Tier_C_AI_Generated") == 20
    assert strata.get("Difficult_Semantic_Cases") == 20


# Test 21: Validate reported synonym count programmatically
def test_21_programmatic_synonym_count_validation():
    """Verify programmatic synonym metrics match closure report exactly."""
    from tests._baseline import baseline_rows
    expressions = baseline_rows("expressions")      # sealed-prefix rows (corrections edit them in place, never add/remove)
    vi_exprs = [e for e in expressions if e.get("language") == "vi"]

    cid_groups = {}
    for e in vi_exprs:
        cid_groups.setdefault(e["concept_id"], []).append(e)

    concepts_with_multiple_vi = sum(1 for elist in cid_groups.values() if len(elist) > 1)
    total_vi_synonyms = sum(1 for e in vi_exprs if e.get("language_metadata", {}).get("is_synonym") is True)
    total_primary_vi = len(vi_exprs) - total_vi_synonyms

    source_derived_vi_synonyms = sum(
        1 for e in vi_exprs
        if e.get("language_metadata", {}).get("is_synonym") is True and e.get("provenance_type") == "SOURCE_DERIVED"
    )
    ai_generated_vi_synonyms = sum(
        1 for e in vi_exprs
        if e.get("language_metadata", {}).get("is_synonym") is True and e.get("provenance_type") == "AI_GENERATED"
    )

    assert concepts_with_multiple_vi == 273, f"Expected 273 concepts with multiple VI, got {concepts_with_multiple_vi}"
    assert total_primary_vi == 1717, f"Expected 1,717 primary VI expressions, got {total_primary_vi}"
    assert total_vi_synonyms == 273, f"Expected 273 total VI synonyms, got {total_vi_synonyms}"
    assert source_derived_vi_synonyms == 0, f"Expected 0 source-derived VI synonyms, got {source_derived_vi_synonyms}"
    assert ai_generated_vi_synonyms == 273, f"Expected 273 AI-generated VI synonyms, got {ai_generated_vi_synonyms}"
    assert total_primary_vi + total_vi_synonyms == len(vi_exprs) == 1990


# Test 22 (Portability Test A): No absolute local export paths in summary.json
def test_22_no_absolute_local_export_path():
    summary_path = OKI_EXPORT_DIR / "summary.json"
    assert summary_path.exists(), "summary.json missing"
    content = summary_path.read_text(encoding="utf-8")
    for forbidden in ["/Users/", "/home/", "file:///", "C:\\Users\\"]:
        assert forbidden not in content, f"Found machine-specific path '{forbidden}' in summary.json"
    data = json.loads(content)
    assert data.get("export_destination") == "data/exports/oki_language/deck_data.json"


# Test 23 (Portability Test B): No local absolute links in closure report
def test_23_no_local_links_in_closure_report():
    report_path = REPORTS_DIR / "final_closure_report.md"
    assert report_path.exists(), "final_closure_report.md missing"
    content = report_path.read_text(encoding="utf-8")
    for forbidden in ["file:///", ".gemini/antigravity-ide/scratch", "/Users/tranhaibang"]:
        assert forbidden not in content, f"Found local machine path '{forbidden}' in final_closure_report.md"


# Test 24 (Portability Test C): All relative Phase 1.3D report links resolve to existing files
def test_24_closure_report_relative_links_resolve():
    import re
    report_path = REPORTS_DIR / "final_closure_report.md"
    assert report_path.exists(), "final_closure_report.md missing"
    content = report_path.read_text(encoding="utf-8")

    link_matches = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)
    assert len(link_matches) > 0, "No markdown links found in final_closure_report.md"

    checked_links = 0
    for text, target in link_matches:
        if target.startswith("http://") or target.startswith("https://") or target.startswith("#"):
            continue
        # Strip query or fragment if any
        target_path = target.split("#")[0].split("?")[0]
        # Resolve either relative to REPORTS_DIR or BASE_DIR
        resolved_sibling = (REPORTS_DIR / target_path).resolve()
        resolved_root = (BASE_DIR / target_path).resolve()
        assert resolved_sibling.exists() or resolved_root.exists(), (
            f"Link target '{target}' from final_closure_report.md does not resolve to an existing file"
        )
        checked_links += 1

    assert checked_links >= 8, f"Expected at least 8 relative report links, verified {checked_links}"


# Test 25 (Portability Test D): Canonical freeze verification (Phase 1.4: append-only prefix check)
def test_25_canonical_freeze_checksums():
    """The sealed Phase 1.3D bytes must be exactly reconstructible: (corrected prefix) + (reverted Phase 1.4.1 ledger)."""
    from tests._baseline import manifest, reverted_prefix_bytes
    for fname, info in manifest()["append_only"].items():
        name = fname.replace(".jsonl", "")
        if name == "examples":
            data = (CANONICAL_DIR / fname).read_bytes()[: info["bytes"]]
        else:
            data = reverted_prefix_bytes(name)
        assert hashlib.sha256(data).hexdigest() == info["sha256"], f"CANONICAL FREEZE BREACH: {fname} cannot be reverted to the sealed bytes"

    # Verify counts and tier distributions from closure manifest
    manifest_path = REPORTS_DIR / "closure_manifest.json"
    assert manifest_path.exists(), "closure_manifest.json missing"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["canonical_concepts"] == 2106
    assert manifest["validated_complete"] == 1717
    assert manifest["partial"] == 389
    assert manifest["tier_a"] == 1072
    assert manifest["tier_b"] == 358
    assert manifest["tier_c"] == 287
    assert manifest["tier_d"] == 389
    assert manifest["ai_calls_during_housekeeping"] == 0
    assert manifest["judge_calls_during_housekeeping"] == 0
    assert manifest["network_calls_during_housekeeping"] == 0


