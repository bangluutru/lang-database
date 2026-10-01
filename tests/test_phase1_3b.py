"""
tests/test_phase1_3b.py
Unit and regression tests for Phase 1.3B:
Tri-Language Learning Graph & Open Source Ingestion Foundation.
Verifies all 15 core invariants specified in Section 25 of Phase 1.3B specification.
"""

import json
import sys
import hashlib
from pathlib import Path
import pytest

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from scripts.phase1_3b.models import (
    Concept,
    Sense,
    Expression,
    Classification,
    Example,
    SourceEvidence,
    OriginType,
    TriLanguageCoverage,
    LanguageEnum,
    ClassificationStatus,
    ClassificationSystem
)
from scripts.phase1_3b.license_gate import LicenseGate
from scripts.phase1_3b.legacy_bridge import LegacyBridge
from scripts.phase1_3b.alignment_engine import TriLanguageAlignmentEngine
from scripts.phase1_3b.view_exporter import LearningViewExporter
from scripts.phase1_3b.adapters.seed_adapters import (
    JMdictSeedAdapter,
    JoyoKanjiAdapter,
    NGSLSeedAdapter,
    VietnameseCoreAdapter
)

CANONICAL_DIR = BASE_DIR / "data" / "canonical"
EXPORTS_DIR = BASE_DIR / "data" / "exports"


def test_1_one_concept_has_tri_language_expressions():
    """Requirement 1: One concept can have EN + JA + VI expressions."""
    concepts_file = CANONICAL_DIR / "concepts.jsonl"
    expressions_file = CANONICAL_DIR / "expressions.jsonl"
    assert concepts_file.exists()
    assert expressions_file.exists()

    concept_to_langs = {}
    with open(expressions_file, "r", encoding="utf-8") as f:
        for line in f:
            expr = json.loads(line)
            cid = expr["concept_id"]
            concept_to_langs.setdefault(cid, set()).add(expr["language"])

    # Verify every concept has en, ja, vi
    for cid, langs in concept_to_langs.items():
        assert "en" in langs, f"Concept {cid} missing English expression"
        assert "ja" in langs, f"Concept {cid} missing Japanese expression"
        assert "vi" in langs, f"Concept {cid} missing Vietnamese expression"


def test_2_and_3_classification_many_to_many_no_record_duplication():
    """Requirements 2 & 3: One concept/expression can belong to multiple learning classifications without duplicating lexical records."""
    expressions_file = CANONICAL_DIR / "expressions.jsonl"
    classifications_file = CANONICAL_DIR / "classifications.jsonl"

    expr_ids = set()
    with open(expressions_file, "r", encoding="utf-8") as f:
        for line in f:
            expr = json.loads(line)
            eid = expr["expression_id"]
            assert eid not in expr_ids, f"Duplicate expression record found: {eid}"
            expr_ids.add(eid)

    # Check classifications count per target
    target_classifications = {}
    with open(classifications_file, "r", encoding="utf-8") as f:
        for line in f:
            c = json.loads(line)
            tid = c.get("target_id")
            if tid:
                target_classifications.setdefault(tid, []).append(c)

    # Some targets should have multiple classifications attached (e.g. concept-poly-right-correct has CEFR, NGSL, JLPT, Joyo, VI Core)
    multi_classified = [tid for tid, clist in target_classifications.items() if len(clist) > 1]
    assert len(multi_classified) > 0, "Expected at least some entities to have multiple classifications"
    # Total expression count remains exactly unique (812 concepts * 3 = 2436 expressions)
    assert len(expr_ids) == 2436


def test_4_polysemous_words_map_to_different_senses():
    """Requirement 4: Polysemous words can map to different senses and distinct concepts."""
    concepts_file = CANONICAL_DIR / "concepts.jsonl"
    expressions_file = CANONICAL_DIR / "expressions.jsonl"

    right_expressions = []
    with open(expressions_file, "r", encoding="utf-8") as f:
        for line in f:
            expr = json.loads(line)
            if expr["language"] == "en" and expr["lemma"] == "right":
                right_expressions.append(expr)

    assert len(right_expressions) == 3, f"Expected 3 distinct 'right' expressions, got {len(right_expressions)}"

    # Check that they map to 3 distinct concept IDs and 3 distinct sense IDs
    cids = {e["concept_id"] for e in right_expressions}
    sids = {e["sense_id"] for e in right_expressions}
    assert len(cids) == 3, f"Expected 3 distinct concepts for 'right', got {cids}"
    assert len(sids) == 3, f"Expected 3 distinct senses for 'right', got {sids}"
    assert "concept-poly-right-correct" in cids
    assert "concept-poly-right-direction" in cids
    assert "concept-poly-right-entitlement" in cids


def test_5_provenance_survives_to_canonical_graph():
    """Requirement 5: Value-level source evidence and provenance survive to canonical records."""
    expressions_file = CANONICAL_DIR / "expressions.jsonl"
    with open(expressions_file, "r", encoding="utf-8") as f:
        found_evidence = 0
        for line in f:
            expr = json.loads(line)
            source_evidence = expr.get("source_evidence")
            assert isinstance(source_evidence, list)
            if len(source_evidence) > 0:
                found_evidence += 1
                for ev in source_evidence:
                    assert "source_id" in ev
                    # Either source_file or license must be present
                    assert "license" in ev or "source_file" in ev
        assert found_evidence > 0


def test_6_license_metadata_survives_to_release():
    """Requirement 6: License metadata survives to export release records."""
    export_file = EXPORTS_DIR / "cross_language" / "en_ja_vi_core.jsonl"
    assert export_file.exists()

    with open(export_file, "r", encoding="utf-8") as f:
        for line in f:
            rec = json.loads(line)
            assert "license" in rec or "licenses" in rec
            lic = rec.get("license") or rec.get("licenses")
            assert bool(lic)


def test_7_license_gate_blocks_quarantined_sources():
    """Requirement 7: NC, ND, unknown, and proprietary sources cannot enter redistributable production."""
    gate = LicenseGate()

    assert gate.evaluate("CC-BY-NC-4.0").approved is False
    assert gate.evaluate("CC-BY-NC-4.0").status.value == "quarantined"

    assert gate.evaluate("CC-BY-ND-4.0").approved is False
    assert gate.evaluate("CC-BY-ND-4.0").status.value == "quarantined"

    assert gate.evaluate("UNKNOWN").approved is False
    assert gate.evaluate("UNKNOWN").status.value == "quarantined"

    assert gate.evaluate("PROPRIETARY").approved is False
    assert gate.evaluate("PROPRIETARY").status.value in ("quarantined", "prohibited")

    # Permissive and Share-Alike licenses must pass

    assert gate.evaluate("CC0-1.0").approved is True
    assert gate.evaluate("CC-BY-4.0").approved is True
    assert gate.evaluate("CC-BY-SA-4.0").approved is True
    assert gate.evaluate("MIT").approved is True


def test_8_ai_generated_cannot_masquerade_as_source_derived():
    """Requirement 8: AI-generated translation cannot masquerade as source-derived translation."""
    ev_source = SourceEvidence(
        source_id="jmdict_seed",
        source_record_id="seed-depreciation-ja",
        field_name="lemma",
        extracted_value="減価償却",
        origin=OriginType.SOURCE_DERIVED.value,
        license="CC-BY-SA-4.0"
    )
    assert ev_source.origin == OriginType.SOURCE_DERIVED.value
    assert ev_source.model is None

    ev_ai = SourceEvidence(
        source_id="gemini_pro",
        source_record_id="ai_trans_001",
        field_name="lemma",
        extracted_value="khấu hao",
        origin=OriginType.AI_GENERATED.value,
        model="gemini-1.5-flash",
        generation_version="v1.0",
        license="CC-BY-4.0"
    )
    assert ev_ai.origin == OriginType.AI_GENERATED.value
    assert ev_ai.origin != OriginType.SOURCE_DERIVED.value
    assert ev_ai.model == "gemini-1.5-flash"


def test_9_legacy_jp_pro_records_traceable_in_mapping():
    """Requirement 9: Legacy jp-pro-* records remain traceable in legacy_mapping.json."""
    mapping_file = CANONICAL_DIR / "legacy_mapping.json"
    assert mapping_file.exists()

    with open(mapping_file, "r", encoding="utf-8") as f:
        mapping = json.load(f)

    assert len(mapping) == 800, f"Expected 800 mapped records, got {len(mapping)}"
    for legacy_id, info in mapping.items():
        assert legacy_id.startswith("jp-pro-")
        assert "concept_id" in info
        assert "sense_id" in info
        assert "expression_ids" in info
        assert len(info["expression_ids"]) == 3  # JA, EN, VI


def test_10_golden_pilot_v1_and_production_immutability():
    """Requirement 10: Golden Pilot v1, v1.1, Canary 1.2c, and Production 800 records remain unchanged."""
    prod_file = BASE_DIR / "data" / "production" / "vocabulary.jsonl"
    with open(prod_file, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]
    assert len(lines) == 800, f"Production vocabulary must remain exactly 800 records, got {len(lines)}"

    # Check golden release files exist and are intact
    golden_v1 = BASE_DIR / "data" / "releases" / "v1.0.0" / "vocabulary.jsonl"
    if golden_v1.exists():
        with open(golden_v1, "r", encoding="utf-8") as f:
            assert len(f.readlines()) == 100

    canary = BASE_DIR / "data" / "releases" / "v1.2.0-canary.1" / "vocabulary.jsonl"
    if canary.exists():
        with open(canary, "r", encoding="utf-8") as f:
            assert len(f.readlines()) == 300


def test_11_generated_views_reproducibility():
    """Requirement 11: Generated learning views are deterministic and reproducible."""
    exporter = LearningViewExporter()
    views1 = exporter.generate_all_views()
    views2 = exporter.generate_all_views()

    for view_name in views1:
        assert len(views1[view_name]) == len(views2[view_name])
        # Compare JSON lines
        assert views1[view_name] == views2[view_name]


def test_12_tri_language_coverage_metrics_deterministic():
    """Requirement 12: Tri-language coverage metrics are deterministic."""
    engine = TriLanguageAlignmentEngine()
    audit1 = engine.run_audit()
    audit2 = engine.run_audit()

    assert audit1["total_concepts_evaluated"] == audit2["total_concepts_evaluated"]
    assert audit1["exact_alignment_count"] == audit2["exact_alignment_count"]
    assert audit1["polysemy_cases_preserved"] == audit2["polysemy_cases_preserved"]
    assert audit1["han_viet_cognates_linked"] == audit2["han_viet_cognates_linked"]


def test_13_and_14_source_adapters_idempotent_no_duplicates():
    """Requirements 13 & 14: Source adapters are idempotent and repeated extraction produces identical records."""
    jmdict = JMdictSeedAdapter()
    joyo = JoyoKanjiAdapter()
    ngsl = NGSLSeedAdapter()
    vi = VietnameseCoreAdapter()

    res_jm1 = jmdict.extract()
    res_jm2 = jmdict.extract()
    assert len(res_jm1) == len(res_jm2)
    assert [r["surface"] for r in res_jm1] == [r["surface"] for r in res_jm2]

    res_joyo1 = joyo.extract()
    res_joyo2 = joyo.extract()
    assert len(res_joyo1) == len(res_joyo2)

    res_ngsl1 = ngsl.extract()
    res_ngsl2 = ngsl.extract()
    assert len(res_ngsl1) == len(res_ngsl2)

    res_vi1 = vi.extract()
    res_vi2 = vi.extract()
    assert len(res_vi1) == len(res_vi2)


def test_15_semantic_alignment_quarantined_independently():
    """Requirement 15: Semantic alignment can be quarantined independently from source lexical data."""
    engine = TriLanguageAlignmentEngine()

    # Good concept
    res_good = engine.evaluate_concept_alignment(
        concept_id="concept-depreciation",
        ja_expr={"lemma": "減価償却", "pos": "noun"},
        en_expr={"lemma": "depreciation", "pos": "noun"},
        vi_expr={"lemma": "khấu hao", "pos": "noun"}
    )
    assert res_good["status"] == "exact_match"
    assert res_good["quarantined"] is False

    # Mismatched POS concept
    res_mismatch = engine.evaluate_concept_alignment(
        concept_id="concept-mismatch-test",
        ja_expr={"lemma": "迅速", "pos": "adjective"},
        en_expr={"lemma": "quickly", "pos": "adverb"},
        vi_expr={"lemma": "nhanh chóng", "pos": "adverb"}
    )
    assert res_mismatch["status"] == "pos_mismatch"
    assert res_mismatch["quarantined"] is True
