"""
tests/test_linguistic_validation.py
Regression test suite for Phase 1.1A Independent Linguistic Judge and Release Gate.

Verifies:
1. Collocation naturalness and semantic compatibility (Pass/Fail suites).
2. Translation language contamination detection (Vietnamese words in English).
3. Production object status verification (ZERO 'generated' objects in production).
"""

import json
from pathlib import Path
import pytest
import sys

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR / "scripts"))

from linguistic_validator import (
    LinguisticValidator,
    check_collocation_compatibility,
    detect_language_contamination,
)

PROD_FILE = BASE_DIR / "data" / "production" / "vocabulary.jsonl"


# ============================================================================
# 1. COLLOCATION REGRESSION SUITE (Section 23)
# ============================================================================

FAIL_COLLOCATIONS = [
    ("ふるさと納税を提出する", "tax_scheme", "tax"),
    ("事前確定届出給与を効率化する", "executive_compensation", "tax"),
    ("土地を精算する", "tangible_fixed_asset", "accounting"),
    ("FOBの残高", "incoterms_rule", "trade"),
]

PASS_COLLOCATIONS = [
    ("申請書を提出する", "document", "business"),
    ("請求書を発行する", "commercial_document", "accounting"),
    ("売掛金を回収する", "receivable_account", "accounting"),
    ("ふるさと納税を利用する", "tax_scheme", "tax"),
    ("事前確定届出給与を支給する", "executive_compensation", "tax"),
    ("貸借対照表を作成する", "financial_statement", "accounting"),
]


@pytest.mark.parametrize("collocation,semantic_class,domain", FAIL_COLLOCATIONS)
def test_collocations_should_fail(collocation, semantic_class, domain):
    """Unnatural / semantically incompatible collocations must be flagged with issues."""
    issues = check_collocation_compatibility(collocation, semantic_class, domain)
    assert len(issues) > 0, f"Expected collocation to FAIL but it passed: {collocation}"


@pytest.mark.parametrize("collocation,semantic_class,domain", PASS_COLLOCATIONS)
def test_collocations_should_pass(collocation, semantic_class, domain):
    """Authentic / semantically compatible collocations must pass cleanly."""
    issues = check_collocation_compatibility(collocation, semantic_class, domain)
    assert len(issues) == 0, f"Expected collocation to PASS but got issues: {collocation} -> {issues}"


# ============================================================================
# 2. TRANSLATION LANGUAGE CONTAMINATION REGRESSION SUITE (Section 24)
# ============================================================================

def test_translation_contamination_mixed_language():
    """Detects mixed language contamination (Vietnamese words in English translation)."""
    contaminated_text = "We completed chương trình đóng góp cho quê hương procedures."
    issues = detect_language_contamination(contaminated_text, "en")
    assert len(issues) > 0, "Failed to detect Vietnamese contamination in English sentence"
    assert any(i["code"] == "LANGUAGE_CONTAMINATION" for i in issues)


def test_translation_contamination_clean_english():
    """Authentic English sentences without contamination should pass."""
    clean_text = "We prepared the balance sheet in accordance with accounting standards."
    issues = detect_language_contamination(clean_text, "en")
    assert len(issues) == 0, f"False positive in clean English sentence: {issues}"


def test_translation_contamination_clean_vietnamese():
    """Authentic Vietnamese sentences without contamination should pass."""
    clean_vi = "Chúng tôi đã lập bảng cân đối kế toán theo chuẩn mực kế toán."
    issues = detect_language_contamination(clean_vi, "vi")
    assert len(issues) == 0, f"False positive in clean Vietnamese sentence: {issues}"


# ============================================================================
# 3. PRODUCTION LINGUISTIC STATUS CONFORMANCE (Section 21)
# ============================================================================

def test_production_learning_objects_have_no_generated_status():
    """Production release dataset must NOT contain any learning objects with status 'generated'."""
    assert PROD_FILE.exists()
    with open(PROD_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            entry = json.loads(line)
            entry_id = entry["id"]

            for col in entry.get("collocations", []):
                assert col.get("status") == "production_verified", (
                    f"Collocation in {entry_id} has invalid status {col.get('status')}"
                )
                assert col.get("status") != "generated"

            for ex in entry.get("examples", []):
                assert ex.get("status") == "production_verified", (
                    f"Example in {entry_id} has invalid status {ex.get('status')}"
                )
                assert ex.get("status") != "generated"

            for dia in entry.get("dialogue", []):
                assert dia.get("status") == "production_verified", (
                    f"Dialogue in {entry_id} has invalid status {dia.get('status')}"
                )
                assert dia.get("status") != "generated"
