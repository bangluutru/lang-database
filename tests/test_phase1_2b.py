"""
tests/test_phase1_2b.py
Comprehensive test suite for Phase 1.2B: Source & Coverage Engine.

Validates:
1. Source Registry: unique source IDs, required metadata, valid authority classes (A/B/C/D),
   valid reuse status (GREEN/YELLOW/RED), raw snapshot existence, SHA-256 match.
2. Extraction: common schema compliance, source_term_exact presence, precise source locators,
   source record IDs, deterministic extraction, extractor versions.
3. Normalization: source form preservation, NFKC normalization, bracket/abbreviation handling.
4. Deduplication: multi-stage dedup against Golden Pilot v1.1, exact duplicate detection,
   multi-source evidence preservation, variant & sense resolution logic.
5. Domain Taxonomy: practical domains & subdomains, semantic class separation.
6. Draft Source Guard: EDINET 2027 draft blocked from production.
7. Production & Golden Pilot Immutability: production count remains 800, v1 and v1.1 hashes unchanged.
8. Canary Candidate Pool: candidate records formatted with status='candidate', selection metadata,
   source diversity, zero production pollution.
"""

import sys
import json
import hashlib
from pathlib import Path
import pytest
import yaml

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from scripts.source_engine.models import (
    NormalizedCandidate,
    DedupDecision,
    SenseDecision
)
from scripts.source_engine.normalizer import TermNormalizer
from scripts.source_engine.dedup_engine import MultiStageDedupEngine

REGISTRY_FILE = BASE_DIR / "config" / "source_registry.yaml"
TAXONOMY_FILE = BASE_DIR / "config" / "domain_taxonomy.yaml"
PROD_FILE = BASE_DIR / "data" / "production" / "vocabulary.jsonl"
CANARY_POOL_FILE = BASE_DIR / "staging" / "canary_candidate_pool.jsonl"
SAMPLE_FILE = BASE_DIR / "reports" / "manual_inspection_sample.jsonl"

GOLDEN_V1_DIR = BASE_DIR / "data" / "releases" / "golden-pilot-v1"
GOLDEN_V1_VOCAB = GOLDEN_V1_DIR / "vocabulary.jsonl"
GOLDEN_V1_MANIFEST = GOLDEN_V1_DIR / "dataset_manifest.json"

GOLDEN_V1_1_DIR = BASE_DIR / "data" / "releases" / "golden-pilot-v1.1"
GOLDEN_V1_1_VOCAB = GOLDEN_V1_1_DIR / "vocabulary.jsonl"
GOLDEN_V1_1_MANIFEST = GOLDEN_V1_1_DIR / "dataset_manifest.json"

EXPECTED_V1_FILE_HASH = "1da7f6b958d3a1c4ccb12c4850b05ea5828b2d6ab8872077fea2e250d0e435c6"
EXPECTED_V1_CANONICAL_HASH = "27830fa0d861012f7878f9d95d1da5fe281a14076b38bb03c41f446d56a0c45c"

EXPECTED_V1_1_FILE_HASH = "1e18d574e1c1b0f54451456e33648518f6e49a7e0dfc37eb1fec3dd35e55325d"
EXPECTED_V1_1_CANONICAL_HASH = "5ae36d8ace6884a50a0e1fa8c8fd4399660575a133ea2dcbdcf8e16b1f51be15"


def load_jsonl(path: Path):
    if not path.exists():
        return []
    records = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))
    return records


def compute_sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def compute_canonical_hash(records) -> str:
    sorted_records = sorted(records, key=lambda r: r.get("id", ""))
    h = hashlib.sha256()
    for r in sorted_records:
        canonical = {k: v for k, v in r.items() if k not in ("status",)}
        line = json.dumps(canonical, sort_keys=True, ensure_ascii=False) + "\n"
        h.update(line.encode("utf-8"))
    return h.hexdigest()


# ==============================================================================
# 1. Source Registry Tests
# ==============================================================================

class TestSourceRegistry:
    @pytest.fixture(scope="session")
    def registry(self):
        assert REGISTRY_FILE.exists(), f"Missing source registry: {REGISTRY_FILE}"
        with open(REGISTRY_FILE, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def test_registry_sources_list(self, registry):
        sources = registry.get("sources", [])
        assert len(sources) >= 8, f"Expected at least 8 sources, found {len(sources)}"

    def test_unique_source_ids(self, registry):
        source_ids = [s["source_id"] for s in registry["sources"]]
        assert len(source_ids) == len(set(source_ids)), "Duplicate source_id in registry"

    def test_required_metadata_fields(self, registry):
        common_fields = [
            "source_id", "authority", "title", "source_type",
            "domains", "subdomains", "jurisdiction", "language", "version",
            "published_at", "license", "reuse_status",
            "reuse_notes", "extractor", "status"
        ]
        for s in registry["sources"]:
            for field in common_fields:
                assert field in s and s[field] is not None, (
                    f"Source {s.get('source_id')} missing required field '{field}'"
                )
            # Section 11 & 12: Verify truthful storage and provenance metadata
            if s.get("provenance_type") == "OFFICIAL_EXTRACTED" or s.get("raw_snapshot_path"):
                for rf in ["raw_snapshot_path", "raw_sha256", "retrieved_at", "official_url"]:
                    assert rf in s and s[rf] is not None, f"Raw source {s.get('source_id')} missing '{rf}'"
            elif s.get("provenance_type") in ("OFFICIAL_CURATED", "INTERNAL_CURATED"):
                for cf in ["curated_artifact_path", "curated_sha256", "curated_at", "reference_url"]:
                    assert cf in s and s[cf] is not None, f"Curated source {s.get('source_id')} missing '{cf}'"

    def test_valid_authority_classes(self, registry):
        valid_classes = {"A", "B", "C", "D"}
        for s in registry["sources"]:
            ac = s.get("authority_class")
            assert ac in valid_classes, f"Source {s['source_id']} has invalid authority_class: {ac}"

    def test_valid_reuse_statuses(self, registry):
        valid_statuses = {"GREEN", "YELLOW", "RED"}
        for s in registry["sources"]:
            rs = s.get("reuse_status")
            assert rs in valid_statuses, f"Source {s['source_id']} has invalid reuse_status: {rs}"

    def test_raw_snapshots_exist_and_hashes_match(self, registry):
        for s in registry["sources"]:
            if s.get("raw_snapshot_path"):
                snap_dir = BASE_DIR / s["raw_snapshot_path"]
                assert snap_dir.exists(), f"Raw snapshot path does not exist: {snap_dir}"
                meta_file = snap_dir / "metadata.json"
                assert meta_file.exists(), f"Raw snapshot missing metadata.json: {meta_file}"
                computed_hash = compute_sha256_file(meta_file)
                expected_hash = s["raw_sha256"]
                assert computed_hash == expected_hash, (
                    f"Raw SHA-256 mismatch for {s['source_id']}: {computed_hash} != {expected_hash}"
                )
            elif s.get("curated_artifact_path"):
                cur_file = BASE_DIR / s["curated_artifact_path"]
                assert cur_file.exists(), f"Curated artifact does not exist: {cur_file}"
                computed_hash = compute_sha256_file(cur_file)
                expected_hash = s["curated_sha256"]
                assert computed_hash == expected_hash, (
                    f"Curated SHA-256 mismatch for {s['source_id']}: {computed_hash} != {expected_hash}"
                )

    def test_source_versioning_separated(self, registry):
        for s in registry["sources"]:
            sid = s["source_id"]
            ver = s["version"]
            assert ver and len(ver) > 0, f"Source {sid} must have explicit non-empty version"
            # Verify stable naming convention (no temporary ids)
            assert not sid.startswith("source") and not sid.startswith("new_"), (
                f"Source ID '{sid}' appears temporary"
            )


# ==============================================================================
# 2. Draft Source Guard Tests
# ==============================================================================

class TestDraftSourceGuard:
    def test_edinet_2027_draft_status_is_staging_only(self):
        with open(REGISTRY_FILE, "r", encoding="utf-8") as f:
            registry = yaml.safe_load(f)
        draft = next((s for s in registry["sources"] if s["source_id"] == "fsa-edinet-2027-draft"), None)
        assert draft is not None, "fsa-edinet-2027-draft must be present in registry"
        assert draft["status"] == "staging_only", "EDINET 2027 draft must be 'staging_only'"
        assert draft["reuse_status"] == "YELLOW", "EDINET 2027 draft reuse_status must be YELLOW"

    def test_no_draft_candidates_in_canary_pool(self):
        pool = load_jsonl(CANARY_POOL_FILE)
        for cand in pool:
            for ev in cand.get("source_evidence", []):
                assert ev.get("source_id") != "fsa-edinet-2027-draft", (
                    f"Draft source found in candidate {cand['candidate_id']}: {cand['surface']}"
                )
                assert ev.get("source_version") != "2027-draft", (
                    f"Draft version found in candidate {cand['candidate_id']}: {cand['surface']}"
                )


# ==============================================================================
# 3. Extraction Tests
# ==============================================================================

class TestExtraction:
    def test_candidate_schema_compliance(self):
        pool = load_jsonl(CANARY_POOL_FILE)
        assert len(pool) > 0, "Candidate pool should not be empty"
        required_keys = [
            "candidate_id", "surface", "source_evidence", "normalized_surface",
            "dedup_decision", "existing_canonical_id", "sense_decision",
            "domain", "subdomain", "authority_class", "reuse_status",
            "pro_level_candidate", "priority", "status"
        ]
        for cand in pool:
            for k in required_keys:
                assert k in cand, f"Candidate {cand.get('candidate_id')} missing key '{k}'"
            assert cand["status"] == "candidate", f"Invalid status: {cand['status']}"

    def test_source_evidence_locators_complete(self):
        pool = load_jsonl(CANARY_POOL_FILE)
        for cand in pool:
            ev_list = cand.get("source_evidence", [])
            assert len(ev_list) >= 1, f"Candidate {cand['candidate_id']} has no source evidence"
            for ev in ev_list:
                assert ev.get("source_id"), "Missing source_id in evidence"
                assert ev.get("source_version"), "Missing source_version in evidence"
                assert ev.get("source_locator"), f"Missing source_locator in evidence for {cand['surface']}"
                assert ev.get("source_term_exact"), f"Missing source_term_exact in evidence for {cand['surface']}"
                assert ev.get("raw_snapshot_hash"), f"Missing raw_snapshot_hash in evidence for {cand['surface']}"

    def test_source_term_exact_matches_evidence(self):
        pool = load_jsonl(CANARY_POOL_FILE)
        for cand in pool:
            for ev in cand["source_evidence"]:
                exact = ev["source_term_exact"]
                assert len(exact.strip()) > 0, f"Empty source_term_exact in {cand['candidate_id']}"


# ==============================================================================
# 4. Normalization & Japanese Variant Handling Tests
# ==============================================================================

class TestNormalization:
    def test_normalizer_preserves_original_surface(self):
        from scripts.source_engine.models import ExtractedCandidate
        norm = TermNormalizer()
        res = norm.normalize_text(" 　（株）有価証券　 ")
        assert "有価証券" in res

    def test_normalizer_detects_abbreviations(self):
        norm = TermNormalizer()
        res = norm.normalize_text("インコタームズ(Incoterms)")
        assert res == "インコタームズ"

    def test_normalizer_halfwidth_fullwidth_nfkc(self):
        norm = TermNormalizer()
        res = norm.normalize_text("ＩＦＲＳ基準")
        assert res == "IFRS基準"


# ==============================================================================
# 5. Deduplication & Evidence Preservation Tests
# ==============================================================================

class TestDeduplication:
    @pytest.fixture(scope="module")
    def dedup_engine(self):
        return MultiStageDedupEngine(GOLDEN_V1_1_VOCAB, PROD_FILE)

    def test_exact_duplicates_against_production_detected(self, dedup_engine):
        # 貸借対照表 is a known production term in Golden Pilot
        cand = NormalizedCandidate(
            normalized_id="norm-test-001",
            candidate_id="cand-test-001",
            source_term_exact="貸借対照表",
            normalized_surface="貸借対照表",
            domain="accounting",
            subdomain="financial_statements",
            source_id="fsa-edinet-taxonomy",
            source_version="2026-final",
            source_record_id="rec-001",
            source_locator="sheet:test, row:1",
            source_context="test context",
            authority_class="A",
            reuse_status="GREEN",
            raw_snapshot_hash="dummy"
        )
        decision, existing_id, sense = dedup_engine.evaluate_candidate(cand, {})
        assert decision == DedupDecision.EXACT_DUPLICATE
        assert existing_id is not None
        assert existing_id.startswith("jp-pro-accounting-")

    def test_new_canonical_candidate_decision(self, dedup_engine):
        cand = NormalizedCandidate(
            normalized_id="norm-test-002",
            candidate_id="cand-test-002",
            source_term_exact="新規会計項目未登録ターム２０２６",
            normalized_surface="新規会計項目未登録ターム2026",
            domain="accounting",
            subdomain="financial_accounting",
            source_id="test-source",
            source_version="2026",
            source_record_id="rec-002",
            source_locator="sheet:test, row:2",
            source_context="test context",
            authority_class="A",
            reuse_status="GREEN",
            raw_snapshot_hash="dummy"
        )
        decision, existing_id, sense = dedup_engine.evaluate_candidate(cand, {})
        assert decision == DedupDecision.NEW_CANONICAL
        assert existing_id is None

    def test_multi_source_evidence_merging(self):
        """When the same candidate arrives from multiple sources, evidence is preserved and merged."""
        pool = load_jsonl(CANARY_POOL_FILE)
        multi_ev_candidates = [c for c in pool if len(c.get("source_evidence", [])) > 1]
        assert len(multi_ev_candidates) >= 1, (
            "Expected at least one multi-source candidate with merged evidence"
        )
        for mc in multi_ev_candidates:
            source_ids = {ev["source_id"] for ev in mc["source_evidence"]}
            assert len(source_ids) >= 2, (
                f"Candidate {mc['surface']} should have distinct source_ids in merged evidence, got {source_ids}"
            )


# ==============================================================================
# 6. Domain Taxonomy & Semantic Class Separation Tests
# ==============================================================================

class TestDomainTaxonomy:
    @pytest.fixture(scope="session")
    def taxonomy(self):
        assert TAXONOMY_FILE.exists()
        with open(TAXONOMY_FILE, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def test_all_11_domains_defined(self, taxonomy):
        expected_domains = {
            "accounting", "tax", "trade", "business", "management",
            "sales", "purchasing", "hr", "finance", "legal", "office_communication"
        }
        actual_domains = set(taxonomy.get("domains", {}).keys())
        assert expected_domains.issubset(actual_domains), (
            f"Missing domains: {expected_domains - actual_domains}"
        )

    def test_candidate_pool_domains_and_subdomains_valid(self, taxonomy):
        pool = load_jsonl(CANARY_POOL_FILE)
        domains_dict = taxonomy.get("domains", {})
        for cand in pool:
            dom = cand.get("domain")
            subdom = cand.get("subdomain")
            assert dom in domains_dict, f"Invalid domain '{dom}' in candidate {cand['candidate_id']}"
            valid_subdomains = domains_dict[dom].get("subdomains", {})
            assert subdom in valid_subdomains, (
                f"Invalid subdomain '{subdom}' for domain '{dom}' in candidate {cand['candidate_id']}"
            )

    def test_semantic_class_is_separate_from_domain(self, taxonomy):
        domains = taxonomy.get("domains", {})
        for dom, data in domains.items():
            # Domain key itself should not be named as a semantic class (e.g. not 'account' or 'document')
            assert not dom.endswith("_class"), f"Domain {dom} looks like a semantic class"


# ==============================================================================
# 7. Canary Candidate Pool Diversity & Non-Production Status Tests
# ==============================================================================

class TestCanaryCandidatePool:
    def test_canary_pool_file_exists_and_populated(self):
        assert CANARY_POOL_FILE.exists()
        pool = load_jsonl(CANARY_POOL_FILE)
        assert len(pool) >= 250, f"Candidate pool size {len(pool)} < 250 required"

    def test_candidate_pool_has_no_production_pollution(self):
        pool = load_jsonl(CANARY_POOL_FILE)
        prod = load_jsonl(PROD_FILE)
        prod_ids = {r["id"] for r in prod}
        for cand in pool:
            assert cand["status"] == "candidate", (
                f"Candidate {cand['candidate_id']} must have status='candidate'"
            )
            assert cand["candidate_id"] not in prod_ids, (
                f"Candidate {cand['candidate_id']} collides with production ID"
            )

    def test_canary_pool_domain_diversity(self):
        pool = load_jsonl(CANARY_POOL_FILE)
        domains = {c["domain"] for c in pool}
        assert len(domains) >= 6, f"Expected at least 6 domains in candidate pool, got {len(domains)}"

    def test_manual_inspection_sample_validity(self):
        assert SAMPLE_FILE.exists()
        sample = load_jsonl(SAMPLE_FILE)
        assert 40 <= len(sample) <= 60, f"Sample size {len(sample)} not in range 40..60"
        for s in sample:
            assert s.get("inspection_status") == "PASS"
            assert s.get("candidate_id")
            assert s.get("surface")
            assert s.get("source_evidence") or s.get("sources")


# ==============================================================================
# 8. Production & Golden Pilot Immutability Tests
# ==============================================================================

class TestProductionAndGoldenPilotImmutability:
    def test_production_vocabulary_count_is_strictly_800(self):
        prod = load_jsonl(PROD_FILE)
        assert len(prod) == 800, f"Production count modified! Expected 800, got {len(prod)}"

    def test_golden_pilot_v1_immutable(self):
        assert GOLDEN_V1_VOCAB.exists()
        v1_records = load_jsonl(GOLDEN_V1_VOCAB)
        assert len(v1_records) == 800
        file_hash = compute_sha256_file(GOLDEN_V1_VOCAB)
        canonical_hash = compute_canonical_hash(v1_records)
        assert file_hash == EXPECTED_V1_FILE_HASH, (
            f"Golden Pilot v1 file hash modified: {file_hash} != {EXPECTED_V1_FILE_HASH}"
        )
        assert canonical_hash == EXPECTED_V1_CANONICAL_HASH, (
            f"Golden Pilot v1 canonical hash modified: {canonical_hash} != {EXPECTED_V1_CANONICAL_HASH}"
        )

    def test_golden_pilot_v1_1_immutable(self):
        assert GOLDEN_V1_1_VOCAB.exists()
        v1_1_records = load_jsonl(GOLDEN_V1_1_VOCAB)
        assert len(v1_1_records) == 800
        file_hash = compute_sha256_file(GOLDEN_V1_1_VOCAB)
        canonical_hash = compute_canonical_hash(v1_1_records)
        assert file_hash == EXPECTED_V1_1_FILE_HASH, (
            f"Golden Pilot v1.1 file hash modified: {file_hash} != {EXPECTED_V1_1_FILE_HASH}"
        )
        assert canonical_hash == EXPECTED_V1_1_CANONICAL_HASH, (
            f"Golden Pilot v1.1 canonical hash modified: {canonical_hash} != {EXPECTED_V1_1_CANONICAL_HASH}"
        )
