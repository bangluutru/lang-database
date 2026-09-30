"""
tests/test_reproducibility.py
Verifies that rebuilding from the same raw sources and candidates produces
100% deterministic canonical IDs, lineage references, and output payloads.
"""

import json
from pathlib import Path
import pytest
import sys

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR / "scripts"))
sys.path.append(str(BASE_DIR / "scripts" / "pilot_builder"))

import accounting
import tax
import business
import trade
from build_pilot_dataset import build_entry, load_normalized_index

def test_deterministic_rebuild():
    """Verify that building the same term twice yields identical canonical IDs and lineage."""
    norm_index = load_normalized_index()
    
    # Test across all 4 domains
    test_cases = [
        (accounting.ACCOUNTING_ITEMS[0], "accounting", 1),
        (tax.TAX_ITEMS[0], "tax", 1),
        (business.BUSINESS_ITEMS[0], "business", 1),
        (trade.TRADE_ITEMS[0], "trade", 1),
    ]
    
    for item, domain, seq_idx in test_cases:
        entry1 = build_entry(item, domain, seq_idx, norm_index)
        entry2 = build_entry(item, domain, seq_idx, norm_index)
        
        # Verify JSON serialized identity
        str1 = json.dumps(entry1, sort_keys=True, ensure_ascii=False)
        str2 = json.dumps(entry2, sort_keys=True, ensure_ascii=False)
        assert str1 == str2, f"Non-deterministic rebuild for {entry1['id']}"
        assert entry1["id"] == f"jp-pro-{domain}-{seq_idx:06d}"
        assert entry1["lineage"]["canonical_id"] == entry1["id"]

def test_normalized_candidates_determinism():
    """Verify that normalized IDs and candidate references are consistent."""
    norm_file = BASE_DIR / "data" / "normalized" / "normalized_candidates.jsonl"
    assert norm_file.exists()
    
    with open(norm_file, "r", encoding="utf-8") as f:
        first_line = json.loads(f.readline())
        
    assert first_line["normalized_candidate_id"] == "norm-000001"
    assert first_line["extracted_candidate_id"] == "cand-fsa-000001"
    assert first_line["surface"] == "貸借対照表"
    assert first_line["source_record_id"] == "BalanceSheetAbstract"
