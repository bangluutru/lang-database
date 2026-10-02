"""
tests/test_phase1_3c.py
Authoritative Source Acquisition & Tri-Language Learning Corpus Expansion Test Suite.
Validates:
- Section 17 & 18: Download checksum stability, immutable snapshot preservation, metadata
- Section 2 & 3: Provenance rules & seed provenance correction
- Section 4: Production parser determinism & locators
- Section 12: Sense-correct Tri-Language Alignment & polysemy disambiguation
- Section 13 & 14: Match-Before-Create & multi-source evidence aggregation
- Section 15 & 16: License matrix compliance & share-alike boundaries
- Section 24: Oki-language export compatibility
- Section 25: Deterministic offline rebuild guarantee & ID stability
- Section 26: SPECIAL NEGATIVE TEST (Curated local JSON + source URL = SOURCE_DERIVED -> QUARANTINE/FAIL)
"""

import hashlib
import json
import sys
from pathlib import Path
import pytest
from typing import Dict, Any

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from scripts.phase1_3b.models import (
    OriginType,
    SourceEvidence,
    LanguageEnum
)
from scripts.phase1_3b.license_gate import LicenseGate
from scripts.phase1_3b.adapters.seed_adapters import (
    JMdictSeedAdapter,
    JoyoKanjiAdapter,
    NGSLSeedAdapter,
    VietnameseCoreAdapter
)
from scripts.phase1_3c.adapters.production_adapters import (
    NGSLAdapter,
    NGSLSpokenAdapter,
    NAWLAdapter,
    BSLAdapter,
    TSLAdapter,
    VietnameseFrequencyAdapter,
    HanVietAdapter,
    JoyoOfficialAdapter,
    JLPTConsensusAdapter
)
from scripts.phase1_3c.provenance_guard import ProvenanceGuard

BASE_DIR = Path(__file__).resolve().parent.parent
CANONICAL_DIR = BASE_DIR / "data" / "canonical"
RAW_DIR = BASE_DIR / "data" / "raw"
EXPORTS_DIR = BASE_DIR / "data" / "exports"


def test_1_raw_snapshots_checksum_and_metadata_stability():
    """Requirement: All 11 approved raw source snapshots must exist with valid metadata.json and SHA256 matches."""
    sources = [
        ("kanjidic2", "2026-10-01", "kanjidic2.xml.gz"),
        ("joyo", "2010-official", "joyo_kanji_official.json"),
        ("jmdict", "2026-10-01", "JMdict_e.gz"),
        ("ngsl", "1.2", "NGSL_12_stats.csv"),
        ("ngsl_spoken", "1.2", "NGSL-Spoken_12_stats.csv"),
        ("nawl", "1.2", "NAWL_12_lemmatized_for_teaching.csv"),
        ("bsl", "1.2", "BSL_120_stats.csv"),
        ("tsl", "1.2", "TSL_12_stats.csv"),
        ("vn_freq", "1.0", "vn_word_frequencies.tsv"),
        ("unihan", "16.0.0", "Unihan.zip"),
        ("jlpt_consensus", "2026-v1", "JLPT_vocab_ALL.csv")
    ]

    for source_id, version, filename in sources:
        snapshot_dir = RAW_DIR / source_id / version
        assert snapshot_dir.exists(), f"Snapshot directory missing: {snapshot_dir}"
        
        meta_file = snapshot_dir / "metadata.json"
        assert meta_file.exists(), f"metadata.json missing for {source_id}"
        
        artifact_file = snapshot_dir / filename
        assert artifact_file.exists(), f"Artifact missing: {artifact_file}"
        
        with open(meta_file, "r", encoding="utf-8") as f:
            meta = json.load(f)
            
        assert meta["source_id"] == source_id
        assert meta["source_version"] == version
        assert meta["artifact_filename"] == filename
        
        # Verify SHA-256 match
        hasher = hashlib.sha256()
        with open(artifact_file, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                hasher.update(chunk)
        calc_sha = hasher.hexdigest()
        assert calc_sha == meta["artifact_sha256"], f"SHA256 mismatch for {source_id}: {calc_sha} vs {meta['artifact_sha256']}"


def test_2_production_parsers_determinism_and_locators():
    """Requirement: Production parsers extract records deterministically with traceable locators."""
    # NGSL
    ngsl = NGSLAdapter()
    ngsl_records = ngsl.extract_records()
    assert len(ngsl_records) == 2809
    sample_ngsl = ngsl_records[0]
    assert sample_ngsl["locator"].startswith("lemma:")
    assert sample_ngsl["source_evidence"]["source_id"] == "ngsl"
    assert sample_ngsl["source_evidence"]["origin"] == OriginType.SOURCE_DERIVED.value

    # Joyo
    joyo = JoyoOfficialAdapter()
    joyo_records = joyo.extract_kanji()
    assert len(joyo_records) == 2136
    sample_joyo = joyo_records[0]
    assert sample_joyo["source_evidence"]["source_id"] == "joyo"
    assert sample_joyo["source_evidence"]["origin"] == OriginType.SOURCE_DERIVED.value
    assert sample_joyo["source_evidence"]["license"] == "CC-BY-SA-3.0"

    # VN Freq
    vn = VietnameseFrequencyAdapter()
    vn_records = vn.extract_records(limit=10)
    assert len(vn_records) == 10
    sample_vn = vn_records[0]
    assert sample_vn["locator"].startswith("rank:")
    assert sample_vn["candidate_band"] == "VI_CORE_500"

    # JLPT
    jlpt = JLPTConsensusAdapter()
    jlpt_records = jlpt.extract_records()
    assert len(jlpt_records) > 8000
    assert jlpt_records[0]["classification_status"] == "community_consensus"


def test_3_special_negative_test_curated_cannot_masquerade_as_source_derived():
    """
    Section 26 MANDATORY SPECIAL NEGATIVE TEST:
    curated local value + external source URL = SOURCE_DERIVED
    Expected: FAIL / QUARANTINE unless exact upstream raw snapshot evidence exists.
    """
    guard = ProvenanceGuard()

    # 1. Negative Case: Curated local record with fabricated upstream origin and fake source_id
    fake_evidence = SourceEvidence(
        source_id="nonexistent_upstream_source",
        source_version="1.0",
        source_locator="entry:9999",
        origin=OriginType.SOURCE_DERIVED.value,
        extracted_value="fabricated_value",
        source_url="https://example.org/fake-dict",
        license="CC-BY-4.0"
    )
    is_valid, status, reason = guard.verify_evidence(fake_evidence)
    assert not is_valid, "Negative test failed: Fabricated evidence without snapshot was accepted"
    assert status == "QUARANTINED"
    assert "PROVENANCE VIOLATION" in reason

    # 2. Negative Case: Source exists, but SHA-256 hash does not match immutable snapshot
    tampered_evidence = SourceEvidence(
        source_id="ngsl",
        source_version="1.2",
        source_locator="lemma:the, rank:1",
        origin=OriginType.SOURCE_DERIVED.value,
        raw_sha256="deadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeef",
        source_url="https://www.newgeneralservicelist.com/",
        license="CC-BY-4.0"
    )
    is_valid, status, reason = guard.verify_evidence(tampered_evidence)
    assert not is_valid, "Negative test failed: Tampered SHA256 was accepted"
    assert status == "QUARANTINED"
    assert "SHA-256 hash mismatch" in reason

    # 3. Negative Case: Record marked SOURCE_DERIVED but missing required source locator
    missing_loc_evidence = SourceEvidence(
        source_id="ngsl",
        source_version="1.2",
        source_locator="",  # Missing locator
        origin=OriginType.SOURCE_DERIVED.value,
        license="CC-BY-4.0"
    )
    is_valid, status, reason = guard.verify_evidence(missing_loc_evidence)
    assert not is_valid, "Negative test failed: Evidence with empty locator was accepted"
    assert status == "QUARANTINED"
    assert "Source locator missing" in reason


def test_4_seed_adapters_marked_seed_curated():
    """Requirement: All Phase 1.3B seed adapters must explicitly declare origin=SEED_CURATED."""
    seed_adapters = [
        JMdictSeedAdapter(),
        JoyoKanjiAdapter(),
        NGSLSeedAdapter(),
        VietnameseCoreAdapter()
    ]
    for adapter in seed_adapters:
        records = adapter.extract_records()
        assert len(records) > 0, f"Seed adapter {adapter.__class__.__name__} produced 0 records"
        sample = records[0]
        ev = sample.get("source_evidence")
        assert ev is not None and len(ev) > 0, f"Sample from {adapter.__class__.__name__} missing source_evidence"
        ev_item = ev[0] if isinstance(ev, list) else ev
        origin = ev_item.origin if hasattr(ev_item, "origin") else ev_item.get("origin")
        assert origin == OriginType.SEED_CURATED.value, (
            f"Seed adapter {adapter.__class__.__name__} failed: origin={origin} must be 'seed_curated'"
        )


def test_5_tri_language_canonical_completeness():
    """Section 22 & 31: Tri-language completeness is a computed metric across validated core and partial concepts."""
    concepts_file = CANONICAL_DIR / "concepts.jsonl"
    expressions_file = CANONICAL_DIR / "expressions.jsonl"
    assert concepts_file.exists()
    assert expressions_file.exists()

    concepts = set()
    with open(concepts_file, "r", encoding="utf-8") as f:
        for line in f:
            c = json.loads(line)
            concepts.add(c["concept_id"])

    concept_to_langs = {}
    with open(expressions_file, "r", encoding="utf-8") as f:
        for line in f:
            e = json.loads(line)
            concept_to_langs.setdefault(e["concept_id"], set()).add(e["language"])

    # Computed completeness metrics
    assert len(concepts) >= 2000, f"Expected >= 2000 canonical concepts, found {len(concepts)}"
    
    complete_tri = [cid for cid in concepts if concept_to_langs.get(cid) == {"en", "ja", "vi"}]
    partial_en_ja = [cid for cid in concepts if concept_to_langs.get(cid) == {"en", "ja"}]
    
    # Validated tri-language core must have >= 1,000 complete tri-language concepts
    assert len(complete_tri) >= 1000, f"Expected >= 1000 complete tri-language concepts, got {len(complete_tri)}"
    
    # Partial learning concepts must exist (EN + JA) without fabricated Vietnamese (389 remain partial)
    assert len(partial_en_ja) > 0, f"Expected partial EN+JA concepts to exist, got {len(partial_en_ja)}"
    
    # All concepts must have expressions
    for cid in concepts:
        assert cid in concept_to_langs, f"Concept {cid} has zero expressions"
        langs = concept_to_langs[cid]
        assert "en" in langs, f"Concept {cid} missing English expression"
        assert "ja" in langs, f"Concept {cid} missing Japanese expression"


def test_6_polysemy_disambiguation_integrity():
    """Section 12: Polysemous words must be split into distinct concepts/senses without generic collision."""
    expressions_file = CANONICAL_DIR / "expressions.jsonl"
    concepts_file = CANONICAL_DIR / "concepts.jsonl"

    right_exprs = []
    bank_exprs = []
    charge_exprs = []
    interest_exprs = []

    with open(expressions_file, "r", encoding="utf-8") as f:
        for line in f:
            e = json.loads(line)
            if e["concept_id"].startswith("concept-lex-"):
                continue  # Phase 1.4 adds further, separate senses; this test pins the 1.3C benchmark set
            if e["language"] == "en":
                lemma = e["lemma"]
                if lemma == "right":
                    right_exprs.append(e)
                elif lemma == "bank":
                    bank_exprs.append(e)
                elif lemma == "charge":
                    charge_exprs.append(e)
                elif lemma == "interest":
                    interest_exprs.append(e)

    # 'right' must have exactly 3 distinct expressions (correct, direction, entitlement)
    assert len(right_exprs) == 3, f"Expected 3 distinct 'right' expressions, got {len(right_exprs)}"
    cids_right = {e["concept_id"] for e in right_exprs}
    assert len(cids_right) == 3, "Each 'right' expression must belong to a distinct concept"

    # 'bank' must have at least 2 distinct senses (financial vs river)
    assert len(bank_exprs) >= 2
    cids_bank = {e["concept_id"] for e in bank_exprs}
    assert len(cids_bank) >= 2, "Bank must have separate concepts for distinct senses"

    # 'charge' must have at least 2 distinct senses (fee vs responsibility)
    assert len(charge_exprs) >= 2
    cids_charge = {e["concept_id"] for e in charge_exprs}
    assert len(cids_charge) >= 2

    # 'interest' must have at least 2 distinct senses (financial vs curiosity)
    assert len(interest_exprs) >= 2
    cids_interest = {e["concept_id"] for e in interest_exprs}
    assert len(cids_interest) >= 2


def test_7_license_compliance_gate():
    """Section 15: All canonical expressions must have approved Tier 1 / Tier 2 licenses."""
    gate = LicenseGate()
    expressions_file = CANONICAL_DIR / "expressions.jsonl"

    with open(expressions_file, "r", encoding="utf-8") as f:
        for line in f:
            e = json.loads(line)
            lic = e.get("license")
            assert lic is not None, f"Expression {e['expression_id']} missing license"
            assert gate.is_production_eligible(lic), f"Expression {e['expression_id']} has non-eligible license {lic}"


def test_8_oki_language_deck_export_validity():
    """Section 24: deck_data.json must exist, be valid JSON, and contain tri-language cards."""
    deck_path = EXPORTS_DIR / "oki_language" / "deck_data.json"
    assert deck_path.exists(), "oki_language/deck_data.json missing"

    with open(deck_path, "r", encoding="utf-8") as f:
        cards = json.load(f)

    assert len(cards) >= 2000, f"Expected >= 2000 oki-language cards, got {len(cards)}"
    sample_card = cards[0]
    assert "id" in sample_card
    assert "english" in sample_card
    assert "japanese" in sample_card
    assert "vietnamese" in sample_card
    assert "reading" in sample_card
    assert "senses" in sample_card
    assert "classifications" in sample_card


def test_9_professional_800_records_intact():
    """Section 23: All 800 professional concepts and legacy mapping must remain 100% frozen."""
    legacy_file = CANONICAL_DIR / "legacy_mapping.json"
    assert legacy_file.exists()

    with open(legacy_file, "r", encoding="utf-8") as f:
        mapping = json.load(f)

    assert len(mapping) == 800, f"Expected 800 legacy records, found {len(mapping)}"
    for legacy_id, canonical_info in mapping.items():
        assert legacy_id.startswith("jp-pro-")
        assert canonical_info["concept_id"].startswith("concept-pro-")
