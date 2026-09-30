"""
tests/test_validation_independence.py
Tests verifying validation independence, release gate enforcement, draft quarantine,
TTS phonetic safety, and rejection of unnatural collocations and corrupted readings.
"""

import copy
import pytest
from pathlib import Path
import json

BASE_DIR = Path(__file__).resolve().parent.parent
import sys
sys.path.append(str(BASE_DIR / "scripts"))

from validate_dataset import DatasetValidator

@pytest.fixture
def validator():
    return DatasetValidator()

@pytest.fixture
def sample_candidate():
    return {
        "id": "jp-pro-accounting-000001",
        "term": {
            "surface": "貸借対照表",
            "reading": "たいしゃくたいしょうひょう",
            "romaji": "taishakutaishouhyou"
        },
        "domain": {
            "primary": "accounting",
            "secondary": ["finance"],
            "semantic_class": "financial_statement"
        },
        "meaning": {
            "vi": {"short": "bảng cân đối kế toán", "explanation": "Báo cáo tài chính."},
            "en": {"preferred": "Balance sheet", "short": "Balance sheet"}
        },
        "professional_level": {"tier": "PRO-A1", "description": "Essential"},
        "general_japanese": {"jlpt_level": None, "jlpt_status": "not_mapped"},
        "priority": {
            "score": 90,
            "factors": {"workplace_frequency": 30, "learner_usefulness": 30, "source_authority": 20, "cross_domain_value": 10}
        },
        "collocations": [
            {"text": "貸借対照表を作成する", "predicate": "作成する", "particle": "を", "semantic_class": "financial_statement", "register": "professional"},
            {"text": "貸借対照表を開示する", "predicate": "開示する", "particle": "を", "semantic_class": "financial_statement", "register": "professional"}
        ],
        "examples": [
            {"ja": "公認会計士の監査を経て、今期の貸借対照表が承認されました。", "vi": "Bảng cân đối đã duyệt.", "en": "Balance sheet approved.", "register": "statutory_reporting"},
            {"ja": "投資家への適時開示に向けて、貸借対照表の注記を確認します。", "vi": "Kiểm tra thuyết minh.", "en": "Check footnotes.", "register": "investor_relations"}
        ],
        "dialogue": [
            {"speaker": "A", "ja": "貸借対照表の処理は済みましたか。", "vi": "Xong chưa?", "en": "Done?"},
            {"speaker": "B", "ja": "はい、帳簿と照合いたしました。", "vi": "Đã khớp sổ.", "en": "Reconciled."}
        ],
        "sources": [{"source_id": "fsa_edinet_2026", "source_file": "1f_AccountList.xlsx", "source_term_exact": "貸借対照表", "source_record_id": "BalanceSheetAbstract"}],
        "lineage": {
            "origin_type": "official_extracted",
            "source_id": "fsa_edinet_2026",
            "source_file": "1f_AccountList.xlsx",
            "source_record_id": "BalanceSheetAbstract",
            "source_term_exact": "貸借対照表",
            "extracted_candidate_id": "cand-fsa-000001",
            "normalized_candidate_id": "norm-000001",
            "canonical_id": "jp-pro-accounting-000001"
        },
        "tts": {
            "display_text": "貸借対照表",
            "speech_text": "貸借対照表",
            "preferred_reading": "たいしゃくたいしょうひょう",
            "pronunciation_type": "standard_kanji_kana",
            "pause_after_term_ms": 1200
        },
        "status": "candidate"
    }

def test_builder_cannot_self_certify(validator, sample_candidate):
    """Builder declaring 'status: production' or 'validated: true' must not bypass validation."""
    bogus = copy.deepcopy(sample_candidate)
    bogus["status"] = "production"
    bogus["provenance"] = {"validated": True}
    bogus["confidence"] = {"reading": 0.99, "canonical_term": 1.0}
    
    # Validator must reject circular confidence floats
    sch_ok, sch_errs = validator.validate_schema(bogus)
    assert not sch_ok
    assert any("Circular artificial confidence scores" in err for err in sch_errs)

def test_corrupted_reading_rejection(validator, sample_candidate):
    """A corrupted reading like 'まっしんぐ' for 'ラッシング' must be rejected."""
    bad_entry = copy.deepcopy(sample_candidate)
    bad_entry["term"]["surface"] = "ラッシング"
    bad_entry["term"]["reading"] = "まっしんぐ"
    
    status, lvl, meth, evid, errs = validator.validate_reading("ラッシング", "まっしんぐ")
    assert status == "rejected"
    assert any("Phonetic corruption" in err for err in errs)

def test_fake_jlpt_rejection(validator, sample_candidate):
    """An entry attempting to deduce JLPT level from PRO tier must be rejected."""
    bad_entry = copy.deepcopy(sample_candidate)
    bad_entry["general_japanese"]["jlpt_level"] = "N2"
    bad_entry["general_japanese"]["jlpt_status"] = "inferred"
    
    sch_ok, sch_errs = validator.validate_schema(bad_entry)
    assert not sch_ok
    assert any("Fake JLPT level found" in err for err in sch_errs)

def test_prohibited_collocation_rejection(validator, sample_candidate):
    """Prohibited generic domain collocations (e.g. '土地を精算する') must be rejected."""
    bad_entry = copy.deepcopy(sample_candidate)
    bad_entry["term"]["surface"] = "土地"
    bad_entry["collocations"] = [
        {"text": "土地を精算する", "predicate": "精算する", "particle": "を", "semantic_class": "asset", "register": "professional"},
        {"text": "土地の残高", "predicate": "残高", "particle": "の", "semantic_class": "asset", "register": "professional"}
    ]
    
    col_ok, col_errs = validator.validate_collocations(bad_entry)
    assert col_ok == "fail"
    assert any("Prohibited generic template collision" in err for err in col_errs)

def test_tts_acronym_slash_safety(validator, sample_candidate):
    """TTS speech_text must not retain raw slash character for acronyms."""
    bad_entry = copy.deepcopy(sample_candidate)
    bad_entry["term"]["surface"] = "B/L"
    bad_entry["tts"]["display_text"] = "B/L"
    bad_entry["tts"]["speech_text"] = "B/L"  # Raw slash unexpanded!
    
    tts_status, tts_errs = validator.validate_tts(bad_entry)
    assert tts_status == "fail"
    assert any("raw slash character" in err for err in tts_errs)

def test_draft_contamination_guard(validator, sample_candidate):
    """Any entry referencing FSA 2027 draft must be blocked immediately."""
    contaminated = copy.deepcopy(sample_candidate)
    contaminated["lineage"]["source_id"] = "fsa_edinet_2027_draft"
    contaminated["lineage"]["source_file"] = "staging/fsa_edinet_2027_draft/draft_list.xlsx"
    
    draft_status, draft_errs = validator.validate_draft_contamination(contaminated)
    assert draft_status == "fail"
    assert any("2027 draft contamination" in err for err in draft_errs)
