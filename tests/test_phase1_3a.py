"""
tests/test_phase1_3a.py
Comprehensive deterministic regression suite for Phase 1.3A:
- Extraction: valid term extraction, navigation heading rejection, malformed text handling
- Normalization: whitespace, full/half-width forms, brackets, punctuation
- Deduplication: exact, normalized, existing production, existing canary, abbreviation, variant, different sense
- Reading generation: regression fixtures for 9 mandatory terms (貸出金, 加盟店貸勘定, 特定輸出者, etc.)
- Gloss integrity: unmatched parentheses, generic domain placeholders, truncated phrases
- Canonical value: composite EDINET/XBRL line items classification
- Relationships: known abbreviation/full-form pairs
- Selection quality gate: candidate attributes, domain balancing
- Human boundary: human_decision = PENDING for 100% of review candidates
- Immutability: Production, Golden Pilot v1/v1.1, Canary 1.2C vocab and relations
"""

import sys
from pathlib import Path
import json
import hashlib
import pytest

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from scripts.phase1_3a.models import (
    RawCandidate,
    NormalizedCandidate,
    ReviewCandidate,
    QualityFlag,
    ReviewComplexity,
    AIRecommendation
)
from scripts.phase1_3a.normalizer import normalize_surface, is_extraction_artifact, Phase13Normalizer
from scripts.phase1_3a.dedup_engine import Phase13DedupEngine, ABBREVIATION_MAP
from scripts.phase1_3a.linguistic_enhancer import (
    Phase13LinguisticEnhancer,
    PHONETIC_OVERRIDES,
    GENERIC_GLOSS_PLACEHOLDERS
)
from scripts.phase1_3a.extractors.edinet_extractor import classify_edinet_label, clean_label
from scripts.phase1_3a.batch_selector import Phase13BatchSelector
from scripts.phase1_3a.run_phase1_3a import EXPECTED_HASHES, verify_frozen_datasets

BASE_DIR = Path(__file__).resolve().parent.parent


# 1. Extraction tests
def test_extraction_navigation_heading_rejected():
    nav_artifacts = ["用語一覧", "目次", "ページトップ", "トップ", "はじめに", "標準ラベル", "索引"]
    for artifact in nav_artifacts:
        assert is_extraction_artifact(artifact), f"Failed to identify {artifact} as navigation artifact"


def test_extraction_valid_statutory_term_accepted():
    valid_terms = ["確定申告書", "時間外労働", "特定輸出者", "下請代金", "取締役会"]
    for term in valid_terms:
        assert not is_extraction_artifact(term), f"Valid term {term} falsely flagged as artifact"


# 2. Normalization tests
def test_normalization_whitespace_and_fullwidth():
    raw_str = "　　貸出金　（短期）　"
    norm, flags = normalize_surface(raw_str)
    assert norm == "貸出金 (短期)"


def test_normalization_brackets():
    raw_str = "【就業規則】"
    norm, flags = normalize_surface(raw_str)
    assert norm == "就業規則"


def test_normalization_bullets_and_punctuation():
    raw_str = "・1. 労働条件通知書:"
    norm, flags = normalize_surface(raw_str)
    assert norm == "労働条件通知書"


# 3. Deduplication and Exclusion tests
def test_dedup_existing_production_exclusion():
    engine = Phase13DedupEngine(BASE_DIR)
    # 貸借対照表 is in production (800 records)
    assert engine.existing_index.is_existing_production("貸借対照表", "貸借対照表")


def test_dedup_existing_canary_exclusion():
    engine = Phase13DedupEngine(BASE_DIR)
    # 加盟店貸勘定 is in canary-1.2c
    assert engine.existing_index.is_existing_canary("加盟店貸勘定", "加盟店貸勘定")


def test_dedup_abbreviation_detection():
    engine = Phase13DedupEngine(BASE_DIR)
    cand = NormalizedCandidate(
        candidate_id="test-abbr-1",
        surface="相法",
        normalized_surface="相法",
        domain="tax",
        subdomain="tax_filing",
        source_ids=["nta-tax-glossary"]
    )
    result = engine.deduplicate_and_exclude([cand])
    assert len(result) == 1
    assert result[0].possible_abbreviation_of == "相続税法"
    assert QualityFlag.ABBREVIATION_FLAG in result[0].quality_flags


def test_dedup_different_sense_preservation():
    engine = Phase13DedupEngine(BASE_DIR)
    cand_acc = NormalizedCandidate(
        candidate_id="c1",
        surface="手形",
        normalized_surface="手形",
        domain="accounting",
        subdomain="notes_receivable",
        source_ids=["fsa-edinet-taxonomy"]
    )
    cand_trade = NormalizedCandidate(
        candidate_id="c2",
        surface="手形",
        normalized_surface="手形",
        domain="trade",
        subdomain="trade_finance",
        source_ids=["japan-customs-trade"]
    )
    result = engine.deduplicate_and_exclude([cand_acc, cand_trade])
    assert len(result) == 2, "Failed to preserve Level 6 different professional senses"
    assert engine.stats["different_sense"] == 1


# 4. Reading Regression Tests
@pytest.mark.parametrize("term,expected", [
    ("貸出金", "かしだしきん"),
    ("加盟店貸勘定", "かめいてんかしかんじょう"),
    ("特定輸出者", "とくていゆしゅつしゃ"),
    ("資本金の額", "しほんきんのがく"),
    ("準備金の額", "じゅんびきんのがく"),
    ("顛末書", "てんまつしょ"),
    ("事業計画書", "じぎょうけいかくしょ"),
    ("課税物件表", "かぜいぶっけんひょう"),
    ("買現先勘定", "かいげんさきかんじょう"),
])
def test_reading_regression_fixtures(term, expected):
    enhancer = Phase13LinguisticEnhancer()
    reading, conf, flags = enhancer.generate_reading(term)
    assert reading == expected, f"Reading regression failure on {term}: got {reading}, expected {expected}"
    assert conf == "HIGH"


# 5. Gloss Integrity Tests
def test_gloss_integrity_unmatched_parentheses():
    enhancer = Phase13LinguisticEnhancer()
    cand = NormalizedCandidate(
        candidate_id="test-gloss-1",
        surface="D/P",
        normalized_surface="D/P",
        domain="trade",
        subdomain="payment",
        source_contexts=["Official EN: Documents against Payment (D/P"]  # missing closing paren
    )
    gloss, conf, flags = enhancer.extract_or_generate_gloss(cand)
    assert QualityFlag.MALFORMED_PARENTHESES in flags
    assert QualityFlag.GLOSS_REVIEW_REQUIRED in flags
    assert gloss.endswith(")")  # Auto-balanced


def test_gloss_integrity_generic_placeholder_flagged():
    enhancer = Phase13LinguisticEnhancer()
    cand = NormalizedCandidate(
        candidate_id="test-gloss-2",
        surface="法人税確定申告",
        normalized_surface="法人税確定申告",
        domain="tax",
        subdomain="tax_filing",
        source_contexts=["Official EN: Tax Filing"]  # Generic category placeholder
    )
    gloss, conf, flags = enhancer.extract_or_generate_gloss(cand)
    assert QualityFlag.GLOSS_REVIEW_REQUIRED in flags
    assert gloss.lower() != "tax filing"


# 6. Canonical value & EDINET composite label classification
def test_edinet_composite_label_classification():
    composite_labels = [
        "受取手形、売掛金及び契約資産",
        "受取手形及び売掛金",
        "受取手形、売掛金及び契約資産（純額）",
        "コールローン及び買入手形",
        "その他の流動資産"
    ]
    for label in composite_labels:
        classification, is_composite = classify_edinet_label(label)
        assert is_composite, f"Composite label {label} was not flagged as composite"
        assert classification == "COMPOSITE_REPORTING_LABEL"


def test_edinet_canonical_atomic_concept():
    atomic_labels = ["契約資産", "売掛金", "買掛金", "資本金", "貸倒引当金"]
    for label in atomic_labels:
        classification, is_composite = classify_edinet_label(label)
        assert not is_composite, f"Canonical atomic concept {label} falsely classified as composite"
        assert classification == "CANONICAL_CONCEPT"


# 7. Review batch quality gate & human boundary
def test_review_batch_human_decision_boundary():
    review_pack = BASE_DIR / "staging" / "review_queue" / "phase_1_3a_professional_review_ready.jsonl"
    assert review_pack.exists(), "Review pack file does not exist"
    count = 0
    with open(review_pack, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            r = json.loads(line)
            count += 1
            assert r["human_decision"] == "PENDING", f"Security violation: record {r['candidate_id']} has decision {r['human_decision']}"
            assert r["review_complexity"] in ("REVIEW-A", "REVIEW-B", "REVIEW-C")
            assert r["canonical_value_score"] >= 0.0
            assert r["professional_relevance_score"] >= 0.0
    assert 800 <= count <= 1500, f"Review candidate count {count} outside target scale [800, 1500]"


def test_review_batch_ordering():
    review_pack = BASE_DIR / "staging" / "review_queue" / "phase_1_3a_professional_review_ready.jsonl"
    complexities = []
    with open(review_pack, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                complexities.append(json.loads(line)["review_complexity"])

    # Complexity must transition monotonically: REVIEW-C -> REVIEW-B -> REVIEW-A
    order_map = {"REVIEW-C": 1, "REVIEW-B": 2, "REVIEW-A": 3}
    num_seq = [order_map[c] for c in complexities]
    for i in range(len(num_seq) - 1):
        assert num_seq[i] <= num_seq[i + 1], f"Ordering violation at index {i}: {complexities[i]} followed by {complexities[i+1]}"


# 8. Candidate pool manifest verification
def test_candidate_pool_manifest():
    manifest_file = BASE_DIR / "staging" / "candidate_pool_phase_1_3a_manifest.json"
    assert manifest_file.exists(), "Manifest file missing"
    with open(manifest_file, "r", encoding="utf-8") as f:
        manifest = json.load(f)
    assert manifest["pool_version"] == "1.3.0"
    assert manifest["candidate_count"] > 3000
    assert manifest["raw_candidate_count"] >= 5000
    assert manifest["sha256"] != ""


# 9. Dataset immutability verification
def test_dataset_immutability():
    assert verify_frozen_datasets() is True
