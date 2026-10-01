"""
tests/test_phase1_3a_1.py
Hardened regression suite for Phase 1.3A.1:
- Provenance integrity: truthful classification, evidence requirements, no faked raw snapshots
- Metadata semantics: curated_at vs downloaded_at, reference_url vs source_url, no fake data/raw paths
- Relationships: self-reference rejection, relationship deduplication, abbreviation targets
- Semantic dedup: SAME_CONCEPT_CROSS_DOMAIN vs DIFFERENT_SENSE
- Artifact filtering: English, その他, navigation/index labels rejected
- Report consistency: invariant closure.source_count == source_coverage.total_sources
- Human boundary: 100% human_decision == "PENDING"
- Frozen dataset immutability: Production 800, Golden Pilot v1 & v1.1, Canary 1.2C
"""

import sys
from pathlib import Path
import json
import hashlib
import yaml
import pytest

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from scripts.phase1_3a.models import (
    ProvenanceType,
    QualityFlag,
    NormalizedCandidate,
    ReviewCandidate,
    RawCandidate
)
from scripts.phase1_3a.normalizer import is_extraction_artifact, Phase13Normalizer
from scripts.phase1_3a.dedup_engine import (
    Phase13DedupEngine,
    ABBREVIATION_MAP,
    KNOWN_DIFFERENT_SENSE_TERMS
)
from scripts.phase1_3a.run_phase1_3a import EXPECTED_HASHES, verify_frozen_datasets


# ==============================================================================
# 1. Provenance Integrity Tests
# ==============================================================================

def test_internal_catalog_cannot_be_official_extracted():
    """Internal/curated catalogs cannot claim OFFICIAL_EXTRACTED without genuine raw evidence."""
    reg_path = BASE_DIR / "config" / "source_registry.yaml"
    with open(reg_path, "r", encoding="utf-8") as f:
        registry = yaml.safe_load(f)

    for s in registry.get("sources", []):
        if s.get("curated_artifact_path"):
            assert s.get("provenance_type") != ProvenanceType.OFFICIAL_EXTRACTED.value, (
                f"Source {s['source_id']} uses curated_artifact_path but claims OFFICIAL_EXTRACTED"
            )
            assert s.get("provenance_type") in (
                ProvenanceType.OFFICIAL_CURATED.value,
                ProvenanceType.INTERNAL_CURATED.value
            )


def test_official_extracted_requires_raw_evidence():
    """OFFICIAL_EXTRACTED candidates must have genuine raw evidence (raw path, hash, official URL)."""
    pool_path = BASE_DIR / "staging" / "candidate_pool_phase_1_3a.jsonl"
    assert pool_path.exists()
    
    with open(pool_path, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            cand = json.loads(line)
            if cand.get("term_provenance") == ProvenanceType.OFFICIAL_EXTRACTED.value:
                assert cand.get("evidence_refs"), f"Missing evidence_refs for {cand['candidate_id']}"
                assert any(ref.get("raw_snapshot_hash") for ref in cand["evidence_refs"]), (
                    f"Candidate {cand['candidate_id']} claims OFFICIAL_EXTRACTED without raw_snapshot_hash"
                )
                assert any("data/raw" in ref.get("artifact_path", "") for ref in cand["evidence_refs"]), (
                    f"Candidate {cand['candidate_id']} claims OFFICIAL_EXTRACTED without data/raw artifact"
                )


def test_official_curated_uses_curated_artifact_and_reference_url():
    """OFFICIAL_CURATED candidates must cite curated artifact and reference URL."""
    pool_path = BASE_DIR / "staging" / "candidate_pool_phase_1_3a.jsonl"
    with open(pool_path, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            cand = json.loads(line)
            if cand.get("term_provenance") == ProvenanceType.OFFICIAL_CURATED.value:
                assert cand.get("evidence_refs"), f"Candidate {cand['candidate_id']} missing evidence_refs"
                assert any(ref.get("curated_artifact_hash") for ref in cand["evidence_refs"]), (
                    f"Curated candidate {cand['candidate_id']} missing curated_artifact_hash"
                )
                assert any("data/curated" in ref.get("artifact_path", "") for ref in cand["evidence_refs"]), (
                    f"Curated candidate {cand['candidate_id']} missing data/curated artifact_path"
                )
                assert any(ref.get("reference_url") for ref in cand["evidence_refs"]), (
                    f"Curated candidate {cand['candidate_id']} missing reference_url"
                )


def test_internal_curated_must_not_claim_downloaded_snapshot():
    """Curated sources in registry must not specify raw_snapshot_path or fake downloaded_at."""
    reg_path = BASE_DIR / "config" / "source_registry.yaml"
    with open(reg_path, "r", encoding="utf-8") as f:
        registry = yaml.safe_load(f)

    for s in registry.get("sources", []):
        if s.get("provenance_type") in (
            ProvenanceType.OFFICIAL_CURATED.value,
            ProvenanceType.INTERNAL_CURATED.value
        ):
            assert s.get("raw_snapshot_path") is None, (
                f"Curated source {s['source_id']} illegally defines raw_snapshot_path"
            )
            assert s.get("raw_sha256") is None, (
                f"Curated source {s['source_id']} illegally defines raw_sha256"
            )


# ==============================================================================
# 2. Metadata Semantics Tests
# ==============================================================================

def test_curated_metadata_cannot_use_downloaded_at():
    """Generated/curated metadata must use curated_at/created_at, never downloaded_at."""
    meta_path = BASE_DIR / "data" / "curated" / "phase1_3a" / "metadata.json"
    assert meta_path.exists(), "Curated metadata.json does not exist"
    with open(meta_path, "r", encoding="utf-8") as f:
        meta = json.load(f)

    assert "downloaded_at" not in meta, "Curated metadata must not contain 'downloaded_at'"
    assert "curated_at" in meta or "created_at" in meta, "Curated metadata missing curated_at/created_at"
    assert meta.get("artifacts"), "Curated metadata missing artifacts list"
    assert all("reference_url" in a for a in meta["artifacts"])


def test_reference_url_distinguished_from_source_url():
    """Verify registry distinguishes reference_url (consulted) from official_url (extracted)."""
    reg_path = BASE_DIR / "config" / "source_registry.yaml"
    with open(reg_path, "r", encoding="utf-8") as f:
        registry = yaml.safe_load(f)

    for s in registry.get("sources", []):
        if s.get("provenance_type") == ProvenanceType.OFFICIAL_CURATED.value:
            assert s.get("reference_url") is not None, f"Source {s['source_id']} missing reference_url"


def test_no_fake_raw_paths_in_data_raw():
    """data/raw/ must not contain internally generated catalogs masquerading as raw snapshots."""
    forbidden_fake_raw = [
        "data/raw/nenkin",
        "data/raw/naccs",
        "data/raw/jftc",
        "data/raw/smea",
        "data/raw/moj",
        "data/raw/jpo",
        "data/raw/meti",
        "data/raw/nta/corporate-tax"
    ]
    for p in forbidden_fake_raw:
        full_p = BASE_DIR / p
        assert not full_p.exists(), f"Forbidden fake raw directory exists: {full_p}"


# ==============================================================================
# 3. Relationships Tests
# ==============================================================================

def test_relationship_self_reference_rejected():
    """A relationship where source == target must be rejected."""
    # Check static mapping
    for abbr, (full_term, _) in ABBREVIATION_MAP.items():
        assert abbr != full_term, f"Self-referential abbreviation mapping found: {abbr} -> {full_term}"

    # Check dedup engine rejection
    engine = Phase13DedupEngine(BASE_DIR)
    cand = NormalizedCandidate(
        candidate_id="test-self-rel",
        surface="商業登記法",
        normalized_surface="商業登記法",
        domain="legal",
        subdomain="corporate_law",
        source_ids=["moj-commercial-registration"]
    )
    result = engine.deduplicate_and_exclude([cand])
    assert result[0].possible_abbreviation_of != "商業登記法"
    assert ("ABBREVIATION_OF", "商業登記法", "商業登記法") not in engine.seen_relationships


def test_duplicate_relationship_deduplicated():
    """Identical relationships must be deduplicated deterministically."""
    engine = Phase13DedupEngine(BASE_DIR)
    cand1 = NormalizedCandidate(
        candidate_id="c1",
        surface="下請法",
        normalized_surface="下請法",
        domain="purchasing",
        subdomain="subcontracting",
        source_ids=["jftc-subcontract"]
    )
    cand2 = NormalizedCandidate(
        candidate_id="c2",
        surface="下請法",
        normalized_surface="下請法",
        domain="purchasing",
        subdomain="subcontracting",
        source_ids=["smea-procurement"]
    )
    result = engine.deduplicate_and_exclude([cand1, cand2])
    # Relationship count in engine.stats["abbreviation"] should be 1, not 2
    assert engine.stats["abbreviation"] == 1
    rel_key = ("ABBREVIATION_OF", "下請法", "下請代金支払遅延等防止法")
    assert rel_key in engine.seen_relationships


def test_abbreviation_target_required():
    """Every candidate flagged as abbreviation must have a non-empty, distinct target."""
    engine = Phase13DedupEngine(BASE_DIR)
    cand = NormalizedCandidate(
        candidate_id="c-abbr",
        surface="労基法",
        normalized_surface="労基法",
        domain="hr",
        subdomain="labor_standards",
        source_ids=["mhlw-labor-standards-glossary"]
    )
    result = engine.deduplicate_and_exclude([cand])
    assert len(result) == 1
    assert result[0].possible_abbreviation_of == "労働基準法"
    assert result[0].possible_abbreviation_of != result[0].normalized_surface


# ==============================================================================
# 4. Semantic Dedup Tests
# ==============================================================================

def test_same_concept_cross_domain_consolidation():
    """Identical statutory/commercial concepts across domains consolidate into SAME_CONCEPT_CROSS_DOMAIN."""
    engine = Phase13DedupEngine(BASE_DIR)
    cand_legal = NormalizedCandidate(
        candidate_id="c_legal",
        surface="実用新案権",
        normalized_surface="実用新案権",
        domain="legal",
        subdomain="intellectual_property",
        source_ids=["jpo-intellectual-property"]
    )
    cand_acc = NormalizedCandidate(
        candidate_id="c_acc",
        surface="実用新案権",
        normalized_surface="実用新案権",
        domain="accounting",
        subdomain="intangible_assets",
        source_ids=["fsa-edinet-taxonomy"]
    )
    result = engine.deduplicate_and_exclude([cand_legal, cand_acc])
    assert len(result) == 1, "Failed to consolidate same concept across domains"
    assert engine.stats["same_concept_cross_domain"] == 1
    assert "jpo-intellectual-property" in result[0].source_ids
    assert "fsa-edinet-taxonomy" in result[0].source_ids


def test_different_sense_preservation_for_polysemous_terms():
    """Genuinely polysemous terms across domains are preserved as DIFFERENT_SENSE."""
    engine = Phase13DedupEngine(BASE_DIR)
    cand_acc = NormalizedCandidate(
        candidate_id="c_acc",
        surface="手形",
        normalized_surface="手形",
        domain="accounting",
        subdomain="notes_receivable",
        source_ids=["fsa-edinet-taxonomy"]
    )
    cand_trade = NormalizedCandidate(
        candidate_id="c_trade",
        surface="手形",
        normalized_surface="手形",
        domain="trade",
        subdomain="trade_finance",
        source_ids=["japan-customs-tariff-schedule"]
    )
    result = engine.deduplicate_and_exclude([cand_acc, cand_trade])
    assert len(result) == 2, "Failed to preserve genuinely different senses for 手形"
    assert engine.stats["different_sense"] == 1


# ==============================================================================
# 5. Artifact Filtering Tests
# ==============================================================================

def test_english_rejected_as_generic_artifact():
    """'English' and other generic language tags must be rejected."""
    assert is_extraction_artifact("English") is True
    assert is_extraction_artifact("english") is True

    # Confirm absent from regenerated candidate pool
    pool_path = BASE_DIR / "staging" / "candidate_pool_phase_1_3a.jsonl"
    with open(pool_path, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            cand = json.loads(line)
            assert cand.get("normalized_surface") != "English"
            assert cand.get("surface") != "English"


def test_navigation_and_index_labels_rejected():
    """UI navigation and generic headings must be rejected as artifacts."""
    artifacts = ["その他", "Q&A", "ホーム", "トップページ", "メニュー", "サイトマップ", "お知らせ"]
    for art in artifacts:
        assert is_extraction_artifact(art) is True, f"Failed to reject artifact '{art}'"


# ==============================================================================
# 6. Report Consistency Tests
# ==============================================================================

def test_source_count_consistency_across_reports():
    """Invariant: closure.source_count == source_coverage.total_sources."""
    closure_path = BASE_DIR / "reports" / "phase_1_3a_1_closure.json"
    coverage_path = BASE_DIR / "reports" / "phase_1_3a_source_coverage.json"
    assert closure_path.exists()
    assert coverage_path.exists()

    with open(closure_path, "r", encoding="utf-8") as f:
        closure = json.load(f)
    with open(coverage_path, "r", encoding="utf-8") as f:
        coverage = json.load(f)

    assert closure["sources_audited"] == coverage["total_sources"]


def test_provenance_distribution_sums_correctly():
    """Provenance counts must sum exactly to candidate pool count and review batch count."""
    closure_path = BASE_DIR / "reports" / "phase_1_3a_1_closure.json"
    with open(closure_path, "r", encoding="utf-8") as f:
        closure = json.load(f)

    manifest_path = BASE_DIR / "staging" / "candidate_pool_phase_1_3a_manifest.json"
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    # Pool provenance sums to candidate pool count
    pool_prov = manifest["provenance_distribution"]
    sum_pool_prov = sum(pool_prov.values())
    assert sum_pool_prov == manifest["candidate_count"]
    assert closure["candidate_pool"] == manifest["candidate_count"]

    # Review batch provenance sums to review batch count
    batch_prov = closure["provenance"]
    sum_batch_prov = sum(batch_prov.values())
    assert sum_batch_prov == closure["review_batch"]


def test_review_batch_count_matches_jsonl_lines():
    """Review batch JSONL line count must strictly match report count."""
    review_pack = BASE_DIR / "staging" / "review_queue" / "phase_1_3a_professional_review_ready.jsonl"
    assert review_pack.exists()
    line_count = 0
    with open(review_pack, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                line_count += 1

    closure_path = BASE_DIR / "reports" / "phase_1_3a_1_closure.json"
    with open(closure_path, "r", encoding="utf-8") as f:
        closure = json.load(f)

    assert line_count == closure["review_batch"]


# ==============================================================================
# 7. Human Boundary Tests
# ==============================================================================

def test_all_review_candidates_human_decision_pending():
    """CRITICAL: 100% of review candidates must have human_decision == 'PENDING'."""
    review_pack = BASE_DIR / "staging" / "review_queue" / "phase_1_3a_professional_review_ready.jsonl"
    with open(review_pack, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            rec = json.loads(line)
            assert rec["human_decision"] == "PENDING", (
                f"Violation of human boundary: candidate {rec['candidate_id']} has {rec['human_decision']}"
            )


# ==============================================================================
# 8. Frozen Dataset Immutability Tests
# ==============================================================================

def test_frozen_datasets_immutability():
    """Production (800 records), Golden Pilot v1 & v1.1, Canary 1.2C remain byte-for-byte unchanged."""
    assert verify_frozen_datasets() is True

    prod_file = BASE_DIR / "data" / "production" / "vocabulary.jsonl"
    prod_count = 0
    with open(prod_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                prod_count += 1
    assert prod_count == 800, f"Production record count changed! Expected 800, found {prod_count}"
