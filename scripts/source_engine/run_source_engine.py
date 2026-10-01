#!/usr/bin/env python3
"""
scripts/source_engine/run_source_engine.py
Master orchestrator for Phase 1.2B: Source & Coverage Engine.
Executes the full provenance, extraction, normalization, multi-stage deduplication,
sense analysis, coverage modeling, and candidate pool generation.
Verifies production immutability and Golden Pilot v1 & v1.1 hash integrity.
"""

import sys
import json
import yaml
import hashlib
from pathlib import Path
from datetime import datetime, timezone

BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(BASE_DIR))

from scripts.source_engine.models import (
    ExtractedCandidate,
    NormalizedCandidate,
    CanaryCandidate,
    SourceEvidence,
    DedupDecision,
    SenseDecision
)
from scripts.source_engine.extractors.edinet import FsaEdinetExtractor
from scripts.source_engine.extractors.nta import NtaTaxExtractor
from scripts.source_engine.extractors.asbj import AsbjExtractor
from scripts.source_engine.extractors.jicpa import JicpaExtractor
from scripts.source_engine.extractors.customs import JapanCustomsExtractor
from scripts.source_engine.extractors.jetro import JetroTradeExtractor
from scripts.source_engine.extractors.mhlw import MhlwLaborExtractor
from scripts.source_engine.extractors.egov import EgovLegalExtractor
from scripts.source_engine.extractors.smrj import SmrjBusinessExtractor
from scripts.source_engine.normalizer import TermNormalizer
from scripts.source_engine.dedup_engine import MultiStageDedupEngine
from scripts.source_engine.coverage_engine import CoverageEngine
from scripts.source_engine.candidate_pool_builder import CandidatePoolBuilder, assign_candidate_priority

REGISTRY_PATH = BASE_DIR / "config" / "source_registry.yaml"
TAXONOMY_PATH = BASE_DIR / "config" / "domain_taxonomy.yaml"
PROD_FILE = BASE_DIR / "data" / "production" / "vocabulary.jsonl"
GOLDEN_V1_DIR = BASE_DIR / "data" / "releases" / "golden-pilot-v1"
GOLDEN_V1_1_DIR = BASE_DIR / "data" / "releases" / "golden-pilot-v1.1"

STAGING_POOL_FILE = BASE_DIR / "staging" / "canary_candidate_pool.jsonl"
INSPECTION_SAMPLE_FILE = BASE_DIR / "reports" / "manual_inspection_sample.jsonl"
REPORTS_DIR = BASE_DIR / "reports"


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


def run_pipeline():
    print("=" * 65)
    print("PHASE 1.2B: SOURCE & COVERAGE ENGINE PIPELINE")
    print("=" * 65)

    # 1. Load Registry & Taxonomy
    assert REGISTRY_PATH.exists(), f"Missing registry at {REGISTRY_PATH}"
    assert TAXONOMY_PATH.exists(), f"Missing taxonomy at {TAXONOMY_PATH}"
    with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
        registry = yaml.safe_load(f)

    sources_map = {s["source_id"]: s for s in registry.get("sources", [])}
    print(f"[*] Loaded {len(sources_map)} registered source definitions from {REGISTRY_PATH.name}")

    # 2. Instantiate Extractors
    extractor_classes = {
        "fsa-edinet-taxonomy": FsaEdinetExtractor,
        "nta-tax-glossary": NtaTaxExtractor,
        "asbj-accounting-standards": AsbjExtractor,
        "jicpa-glossary": JicpaExtractor,
        "japan-customs-trade": JapanCustomsExtractor,
        "jetro-trade": JetroTradeExtractor,
        "mhlw-labor": MhlwLaborExtractor,
        "egov-corporate-law": EgovLegalExtractor,
        "smrj-business-guidance": SmrjBusinessExtractor,
    }

    all_extracted_candidates: List[ExtractedCandidate] = []

    print("\n[*] Step 1: Deterministic Source Extraction ...")
    for s_id, s_info in sources_map.items():
        if s_info.get("status") == "staging_only":
            print(f"    - Skipping staging-only source: {s_id} (version {s_info.get('version')})")
            continue

        ext_cls = extractor_classes.get(s_id)
        if not ext_cls:
            continue

        raw_dir = BASE_DIR / s_info["raw_snapshot_path"]
        assert raw_dir.exists(), f"Raw snapshot directory not found: {raw_dir}"

        extractor = ext_cls(
            source_id=s_id,
            source_version=s_info["version"],
            raw_snapshot_path=raw_dir,
            authority_class=s_info["authority_class"],
            reuse_status=s_info["reuse_status"]
        )

        candidates = extractor.extract_candidates()
        print(f"    ✓ {s_id} ({s_info['version']}) -> {len(candidates)} extracted candidates")
        all_extracted_candidates.extend(candidates)

    print(f"[+] Total raw extracted candidates: {len(all_extracted_candidates)}")

    # 3. Normalization
    print("\n[*] Step 2: Term Normalization (NFKC, bracket cleanup, variant/abbrev detection) ...")
    normalized_candidates: List[NormalizedCandidate] = []
    for seq, cand in enumerate(all_extracted_candidates, start=1):
        norm = TermNormalizer.process_candidate(cand, seq)
        # Filter trivial / non-lexical terms
        if len(norm.normalized_surface) >= 2:
            normalized_candidates.append(norm)

    print(f"[+] Normalized candidates: {len(normalized_candidates)}")

    # 4. Multi-Stage Deduplication & Multi-Source Evidence Aggregation
    print("\n[*] Step 3: Multi-Stage Deduplication against Golden Pilot v1.1 & Production Baseline ...")
    golden_v1_1_vocab = GOLDEN_V1_1_DIR / "vocabulary.jsonl"
    dedup_engine = MultiStageDedupEngine(golden_v1_1_vocab, PROD_FILE)

    pool_surfaces: Dict[str, CanaryCandidate] = {}
    dedup_stats = {
        "total_raw_candidates": len(normalized_candidates),
        "exact_duplicate": 0,
        "variant_of": 0,
        "abbreviation_of": 0,
        "different_sense": 0,
        "needs_review": 0,
        "new_canonical": 0,
        "evidence_merged_count": 0
    }
    examples_log = {
        "exact_duplicates": [],
        "variants": [],
        "abbreviations": [],
        "different_senses": []
    }

    for norm in normalized_candidates:
        surface = norm.normalized_surface
        domain = norm.domain
        subdomain = norm.subdomain

        decision, ref_id, sense_dec = dedup_engine.evaluate_candidate(norm, pool_surfaces)

        # Build source evidence record
        evidence_entry = SourceEvidence(
            source_id=norm.source_id,
            source_version=norm.source_version,
            source_record_id=norm.source_record_id,
            source_locator=norm.source_locator,
            source_term_exact=norm.source_term_exact,
            source_context=norm.source_context,
            authority_class=norm.authority_class,
            reuse_status=norm.reuse_status,
            raw_snapshot_hash=norm.raw_snapshot_hash
        ).to_dict()

        if decision == DedupDecision.EXACT_DUPLICATE:
            dedup_stats["exact_duplicate"] += 1
            # If candidate matches an item already in our pool, merge multi-source evidence!
            if surface in pool_surfaces:
                pool_surfaces[surface].source_evidence.append(evidence_entry)
                dedup_stats["evidence_merged_count"] += 1
            elif ref_id and len(examples_log["exact_duplicates"]) < 10:
                examples_log["exact_duplicates"].append({
                    "surface": surface,
                    "domain": domain,
                    "existing_canonical_id": ref_id,
                    "sources": [norm.source_id]
                })

        elif decision == DedupDecision.VARIANT_OF:
            dedup_stats["variant_of"] += 1
            if len(examples_log["variants"]) < 10:
                examples_log["variants"].append({
                    "surface": surface,
                    "target_term": ref_id or "canonical_variant"
                })

        elif decision == DedupDecision.ABBREVIATION_OF:
            dedup_stats["abbreviation_of"] += 1
            if len(examples_log["abbreviations"]) < 10:
                examples_log["abbreviations"].append({
                    "surface": surface,
                    "full_form": ref_id or "canonical_form"
                })

        elif decision == DedupDecision.POSSIBLE_DIFFERENT_SENSE:
            dedup_stats["different_sense"] += 1
            if len(examples_log["different_senses"]) < 10:
                examples_log["different_senses"].append({
                    "surface": surface,
                    "domain": domain,
                    "existing_canonical_id": ref_id,
                    "context": norm.source_context
                })

        elif decision == DedupDecision.NEEDS_REVIEW:
            dedup_stats["needs_review"] += 1

        elif decision == DedupDecision.NEW_CANONICAL:
            dedup_stats["new_canonical"] += 1

            # Determine priority & professional level
            pro_level, priority = assign_candidate_priority(
                surface=surface,
                domain=domain,
                subdomain=subdomain,
                authority_class=norm.authority_class,
                source_agreement_count=1,
                coverage_gap="high"
            )

            cand_pool_id = f"pool-cand-{len(pool_surfaces)+1:06d}"
            canary_cand = CanaryCandidate(
                candidate_id=cand_pool_id,
                surface=surface,
                normalized_surface=surface,
                source_evidence=[evidence_entry],
                dedup_decision=decision.value,
                existing_canonical_id=ref_id,
                sense_decision=sense_dec.value,
                domain=domain,
                subdomain=subdomain,
                authority_class=norm.authority_class,
                reuse_status=norm.reuse_status,
                pro_level_candidate=pro_level,
                priority=priority,
                status="candidate"
            )
            pool_surfaces[surface] = canary_cand

    all_pool_candidates = list(pool_surfaces.values())
    total_raw = dedup_stats["total_raw_candidates"]
    dedup_summary = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "summary": {
            "total_raw_candidates": total_raw,
            "new_canonical": dedup_stats["new_canonical"],
            "new_canonical_pct": (dedup_stats["new_canonical"] / total_raw * 100) if total_raw else 0,
            "exact_duplicate": dedup_stats["exact_duplicate"],
            "exact_duplicate_pct": (dedup_stats["exact_duplicate"] / total_raw * 100) if total_raw else 0,
            "variant_of": dedup_stats["variant_of"],
            "variant_of_pct": (dedup_stats["variant_of"] / total_raw * 100) if total_raw else 0,
            "abbreviation_of": dedup_stats["abbreviation_of"],
            "abbreviation_of_pct": (dedup_stats["abbreviation_of"] / total_raw * 100) if total_raw else 0,
            "different_sense": dedup_stats["different_sense"],
            "different_sense_pct": (dedup_stats["different_sense"] / total_raw * 100) if total_raw else 0,
            "needs_review": dedup_stats["needs_review"],
            "needs_review_pct": (dedup_stats["needs_review"] / total_raw * 100) if total_raw else 0,
            "multi_source_evidence_merges": dedup_stats["evidence_merged_count"]
        },
        "examples": examples_log
    }

    print(f"[+] Deduplication complete:")
    print(f"    - NEW_CANONICAL candidates: {len(all_pool_candidates)}")
    print(f"    - EXACT_DUPLICATE detected: {dedup_stats['exact_duplicate']}")
    print(f"    - Multi-source evidence merges: {dedup_stats['evidence_merged_count']}")

    # 5. Coverage Engine Calculation
    print("\n[*] Step 4: Coverage Engine Calculation ...")
    production_records = load_jsonl(PROD_FILE)
    coverage_engine = CoverageEngine(TAXONOMY_PATH, REGISTRY_PATH)

    coverage_data = coverage_engine.calculate_coverage(
        production_records=production_records,
        candidates_pool=all_pool_candidates,
        all_extracted_candidates=all_extracted_candidates,
        dedup_stats=dedup_summary["summary"]
    )

    coverage_engine.export_reports(coverage_data, dedup_summary, REPORTS_DIR)

    # 6. Candidate Pool & Readiness Reports
    print("\n[*] Step 5: Candidate Pool & Canary Readiness Export ...")
    readiness_json = REPORTS_DIR / "phase_1_2b_canary_readiness.json"
    readiness_md = REPORTS_DIR / "phase_1_2b_canary_readiness.md"

    CandidatePoolBuilder.build_pool_and_reports(
        candidates=all_pool_candidates,
        staging_pool_path=STAGING_POOL_FILE,
        inspection_sample_path=INSPECTION_SAMPLE_FILE,
        readiness_json_path=readiness_json,
        readiness_md_path=readiness_md,
        coverage_data=coverage_data
    )

    # 7. Verification of Strict Invariants:
    print("\n[*] Step 6: Verifying Production & Golden Pilot Immutability ...")
    # Production count MUST be 800
    prod_after = load_jsonl(PROD_FILE)
    assert len(prod_after) == 800, f"VIOLATION: Production record count changed! ({len(prod_after)} != 800)"

    # Golden Pilot v1 Hashes
    v1_vocab = GOLDEN_V1_DIR / "vocabulary.jsonl"
    v1_file_hash = compute_sha256_file(v1_vocab)
    v1_canonical_hash = compute_canonical_hash(load_jsonl(v1_vocab))
    EXPECTED_V1_FILE = "1da7f6b958d3a1c4ccb12c4850b05ea5828b2d6ab8872077fea2e250d0e435c6"
    EXPECTED_V1_CANONICAL = "27830fa0d861012f7878f9d95d1da5fe281a14076b38bb03c41f446d56a0c45c"
    assert v1_file_hash == EXPECTED_V1_FILE, f"Golden Pilot v1 file hash altered: {v1_file_hash}"
    assert v1_canonical_hash == EXPECTED_V1_CANONICAL, f"Golden Pilot v1 canonical hash altered: {v1_canonical_hash}"
    print(f"    ✓ Golden Pilot v1 hashes UNCHANGED")

    # Golden Pilot v1.1 Hashes
    v1_1_vocab = GOLDEN_V1_1_DIR / "vocabulary.jsonl"
    v1_1_file_hash = compute_sha256_file(v1_1_vocab)
    v1_1_canonical_hash = compute_canonical_hash(load_jsonl(v1_1_vocab))
    EXPECTED_V1_1_FILE = "1e18d574e1c1b0f54451456e33648518f6e49a7e0dfc37eb1fec3dd35e55325d"
    EXPECTED_V1_1_CANONICAL = "5ae36d8ace6884a50a0e1fa8c8fd4399660575a133ea2dcbdcf8e16b1f51be15"
    assert v1_1_file_hash == EXPECTED_V1_1_FILE, f"Golden Pilot v1.1 file hash altered: {v1_1_file_hash}"
    assert v1_1_canonical_hash == EXPECTED_V1_1_CANONICAL, f"Golden Pilot v1.1 canonical hash altered: {v1_1_canonical_hash}"
    print(f"    ✓ Golden Pilot v1.1 hashes UNCHANGED")
    print(f"    ✓ Production records count: {len(prod_after)} (UNCHANGED)")

    print("\n" + "=" * 65)
    print("PHASE 1.2B EXECUTION COMPLETE: SOURCE ENGINE & CANARY POOL READY")
    print("=" * 65)


if __name__ == "__main__":
    run_pipeline()
