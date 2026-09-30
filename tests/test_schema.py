"""
tests/test_schema.py
Unit tests validating JSON Schema conformity, data lineage, decoupled JLPT,
TTS metadata, and absence of circular self-certification for JP Professional Vocabulary Database.
"""

import json
import re
from pathlib import Path
import pytest

BASE_DIR = Path(__file__).resolve().parent.parent
CANDIDATES_FILE = BASE_DIR / "data" / "enriched" / "learning_candidates.jsonl"
PROD_FILE = BASE_DIR / "data" / "production" / "vocabulary.jsonl"
PILOT_FILE = BASE_DIR / "data" / "production" / "jp_professional_pilot.jsonl"
EXPR_FILE = BASE_DIR / "data" / "production" / "expressions.jsonl"
REL_FILE = BASE_DIR / "data" / "production" / "relationships.jsonl"

ID_REGEX = re.compile(r"^jp-pro-[a-z_]+-[0-9]{6}$")
ALLOWED_TIERS = {"PRO-A1", "PRO-A2", "PRO-A3"}
ALLOWED_DOMAINS = {"accounting", "tax", "business", "trade"}

@pytest.fixture(scope="module")
def candidate_entries():
    assert CANDIDATES_FILE.exists(), f"Candidates file not found at {CANDIDATES_FILE}"
    entries = []
    with open(CANDIDATES_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                entries.append(json.loads(line))
    return entries

@pytest.fixture(scope="module")
def prod_entries():
    assert PROD_FILE.exists(), f"Production file not found at {PROD_FILE}"
    entries = []
    with open(PROD_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                entries.append(json.loads(line))
    return entries

def test_candidate_total_count(candidate_entries):
    """The 800-pilot corpus must be preserved as the full candidate set."""
    assert len(candidate_entries) == 800, f"Expected 800 candidate entries, got {len(candidate_entries)}"

def test_production_release_count(prod_entries):
    """Production contains only entries that passed the Release Gate."""
    assert len(prod_entries) == 789, f"Expected 789 released entries, got {len(prod_entries)}"

def test_id_format_and_uniqueness(prod_entries):
    ids = set()
    for e in prod_entries:
        entry_id = e["id"]
        assert ID_REGEX.match(entry_id), f"Invalid ID format: {entry_id}"
        assert entry_id not in ids, f"Duplicate ID: {entry_id}"
        ids.add(entry_id)

def test_surface_uniqueness_per_domain(prod_entries):
    seen = set()
    for e in prod_entries:
        dom = e["domain"]["primary"]
        surf = e["term"]["surface"]
        key = (dom, surf)
        assert key not in seen, f"Duplicate surface in domain '{dom}': {surf}"
        seen.add(key)

def test_linguistic_fields(prod_entries):
    for e in prod_entries:
        term = e["term"]
        assert term["surface"], "Missing surface"
        assert term["reading"], "Missing reading"
        assert term["romaji"], "Missing romaji"
        assert term.get("romaji_metadata", {}).get("generator") == "pykakasi"
        
        meaning = e["meaning"]
        assert meaning["vi"]["short"], "Missing Vietnamese short translation"
        assert meaning["vi"]["explanation"], "Missing Vietnamese explanation"
        assert meaning["en"]["preferred"], "Missing English preferred translation"

def test_decoupled_jlpt_mapping(prod_entries):
    """Rule 10: JLPT must be unmapped (null) to prevent artificial precision."""
    for e in prod_entries:
        gen_jp = e.get("general_japanese", {})
        assert gen_jp.get("jlpt_level") is None, f"Fake JLPT level found: {gen_jp.get('jlpt_level')} in {e['id']}"
        assert gen_jp.get("jlpt_status") == "not_mapped"

def test_professional_level_tiers(prod_entries):
    """Rule 11: Professional tier must have documented definition."""
    for e in prod_entries:
        pl = e.get("professional_level", {})
        tier = pl.get("tier")
        assert tier in ALLOWED_TIERS, f"Invalid tier: {tier}"
        assert pl.get("description"), f"Tier missing description in {e['id']}"

def test_priority_and_factors(prod_entries):
    for e in prod_entries:
        score = e["priority"]["score"]
        assert 0 <= score <= 100, f"Score out of range: {score}"
        factors = e["priority"]["factors"]
        assert sum(factors.values()) == score, f"Factors sum mismatch for {e['id']}"

def test_tts_metadata_structure(prod_entries):
    """Rule 16: TTS display and speech forms must be modeled separately."""
    for e in prod_entries:
        tts = e["tts"]
        assert tts["display_text"]
        assert tts["speech_text"]
        assert tts["preferred_reading"]
        assert tts["pause_after_term_ms"] >= 500
        assert tts["pronunciation_type"] in ["standard_kanji_kana", "acronym_alphabet", "acronym_word", "mixed_compound", "numeric_compound"]

def test_no_circular_confidence_scores(candidate_entries, prod_entries):
    """Rule 3 & 4: Records must NOT contain static artificial confidence scores."""
    for e in candidate_entries + prod_entries:
        assert "confidence" not in e, f"Circular confidence scores detected in {e['id']}"

def test_full_traceable_lineage(prod_entries):
    """Rule 5 & 6: Production records must possess full traceable lineage."""
    for e in prod_entries:
        lineage = e.get("lineage")
        assert lineage, f"Missing lineage in {e['id']}"
        assert lineage["origin_type"] in ["official_extracted", "curated"]
        assert lineage["source_id"]
        assert lineage["source_file"]
        assert lineage["source_record_id"]
        assert lineage["canonical_id"] == e["id"]
        assert lineage["release_version"] == "v1.1.0-prod"
        assert lineage["validation_record"] is not None
        assert lineage["validation_record"]["release_decision"] == "pass"
