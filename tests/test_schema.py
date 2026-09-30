"""
tests/test_schema.py
Unit tests validating JSON Schema conformity for JP Professional Vocabulary Database.
"""

import json
import re
from pathlib import Path
import pytest

BASE_DIR = Path(__file__).resolve().parent.parent
PILOT_FILE = BASE_DIR / "data" / "production" / "jp_professional_pilot.jsonl"
EXPR_FILE = BASE_DIR / "data" / "production" / "expressions.jsonl"
REL_FILE = BASE_DIR / "data" / "production" / "relationships.jsonl"

ID_REGEX = re.compile(r"^jp-pro-[a-z_]+-[0-9]{6}$")
ALLOWED_TIERS = {"PRO-A1", "PRO-A2", "PRO-A3"}
ALLOWED_DOMAINS = {"accounting", "tax", "business", "trade"}

@pytest.fixture(scope="module")
def pilot_entries():
    assert PILOT_FILE.exists(), f"Pilot file not found at {PILOT_FILE}"
    entries = []
    with open(PILOT_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                entries.append(json.loads(line))
    return entries

def test_pilot_total_count(pilot_entries):
    assert len(pilot_entries) == 800, f"Expected exactly 800 entries, got {len(pilot_entries)}"

def test_domain_distribution(pilot_entries):
    counts = {}
    for e in pilot_entries:
        dom = e["domain"]["primary"]
        counts[dom] = counts.get(dom, 0) + 1
    assert counts == {"accounting": 200, "tax": 200, "business": 200, "trade": 200}

def test_id_format_and_uniqueness(pilot_entries):
    ids = set()
    for e in pilot_entries:
        entry_id = e["id"]
        assert ID_REGEX.match(entry_id), f"Invalid ID format: {entry_id}"
        assert entry_id not in ids, f"Duplicate ID: {entry_id}"
        ids.add(entry_id)

def test_surface_uniqueness_per_domain(pilot_entries):
    seen = set()
    for e in pilot_entries:
        dom = e["domain"]["primary"]
        surf = e["term"]["surface"]
        key = (dom, surf)
        assert key not in seen, f"Duplicate surface in domain '{dom}': {surf}"
        seen.add(key)

def test_linguistic_fields(pilot_entries):
    for e in pilot_entries:
        term = e["term"]
        assert term["surface"], "Missing surface"
        assert term["reading"], "Missing reading"
        assert term["romaji"], "Missing romaji"
        
        meaning = e["meaning"]
        assert meaning["vi"]["short"], "Missing Vietnamese short translation"
        assert meaning["vi"]["explanation"], "Missing Vietnamese explanation"
        assert meaning["en"]["preferred"], "Missing English preferred translation"

def test_professional_level_and_priority(pilot_entries):
    for e in pilot_entries:
        tier = e["professional_level"]["tier"]
        assert tier in ALLOWED_TIERS, f"Invalid tier: {tier}"
        score = e["priority"]["score"]
        assert 0 <= score <= 100, f"Score out of range: {score}"
        factors = e["priority"]["factors"]
        assert sum(factors.values()) == score, f"Factors sum mismatch for {e['id']}"

def test_tts_metadata(pilot_entries):
    for e in pilot_entries:
        tts = e["tts"]
        assert tts["speak_term"] is True
        assert tts["preferred_reading"]
        assert tts["pause_after_term_ms"] > 0
        assert tts["display_text"]

def test_confidence_thresholds(pilot_entries):
    for e in pilot_entries:
        conf = e["confidence"]
        for key in ["canonical_term", "reading", "vi_translation", "en_translation", "domain_classification"]:
            assert conf[key] >= 0.90, f"Confidence below 0.90 for {key} in {e['id']}"

def test_provenance_separation(pilot_entries):
    for e in pilot_entries:
        prov = e["provenance"]
        assert prov["extracted_by"], "Missing extracted_by"
        assert prov["enriched_by"], "Missing enriched_by"
        assert prov["validated"] is True
        sources = e["sources"]
        assert len(sources) > 0, "Missing sources list"
        for s in sources:
            assert s["source_id"], "Missing source_id"
            assert s["source_term_exact"], "Missing source_term_exact"

def test_expressions_file():
    assert EXPR_FILE.exists()
    count = 0
    with open(EXPR_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                e = json.loads(line)
                assert e["id"].startswith("jp-expr-")
                assert e["expression"]["surface"]
                assert e["meaning"]["vi"]["short"]
                count += 1
    assert count == 50

def test_relationships_file():
    assert REL_FILE.exists()
    count = 0
    with open(REL_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                r = json.loads(line)
                assert r["relation_id"].startswith("rel-")
                assert r["source_id"]
                assert r["relationship_type"] in {"synonym", "opposite", "related"}
                count += 1
    assert count > 1000
