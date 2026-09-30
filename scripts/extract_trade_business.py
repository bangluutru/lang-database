#!/usr/bin/env python3
"""
scripts/extract_trade_business.py
Extracts and structures candidate terms for:
1. Trade / Import-Export / Customs / International Logistics (JETRO-aligned)
2. Business / Office Communication / Contracts / Corporate Governance / Operations
Outputs: data/extracted/trade_business_candidates.jsonl
"""

import sys
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_FILE = BASE_DIR / "data" / "extracted" / "trade_business_candidates.jsonl"
sys.path.append(str(BASE_DIR / "scripts" / "pilot_builder"))

import business
import trade


def extract_trade_business():
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    print("[*] Extracting Trade & Business candidates ...")

    candidates = []
    seen = set()

    # 1. Extract Trade Terms (JETRO aligned)
    for idx, item in enumerate(trade.TRADE_ITEMS, start=1):
        t = item["surface"]
        if t not in seen:
            seen.add(t)
            seq = len(candidates) + 1
            candidates.append({
                "extracted_candidate_id": f"cand-trade-{idx:06d}",
                "source_id": "jetro_trade",
                "source_file": "jetro_trade_reference_corpus",
                "source_record_id": item.get("source_reference", f"trade_term_{idx}"),
                "source_term_exact": t,
                "surface_candidate": t,
                "official_en": item["en_preferred"],
                "sub_category": item.get("source_reference", "").split(":")[-1] if ":" in item.get("source_reference", "") else "trade",
                "category": "trade"
            })

    # 2. Extract Business Terms (Corporate governance, legal contracts, HR/labor, office operations)
    for idx, item in enumerate(business.BUSINESS_ITEMS, start=1):
        t = item["surface"]
        if t not in seen:
            seen.add(t)
            seq = len(candidates) + 1
            candidates.append({
                "extracted_candidate_id": f"cand-bus-{idx:06d}",
                "source_id": "trade_business_corpus",
                "source_file": "commercial_practice_governance_corpus",
                "source_record_id": item.get("source_reference", f"bus_term_{idx}"),
                "source_term_exact": t,
                "surface_candidate": t,
                "official_en": item["en_preferred"],
                "sub_category": item.get("source_reference", "").split(":")[-1] if ":" in item.get("source_reference", "") else "business",
                "category": "business"
            })

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for c in candidates:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")

    print(f"[+] Successfully extracted {len(candidates)} Trade & Business candidates to {OUTPUT_FILE.relative_to(BASE_DIR)}")


if __name__ == "__main__":
    extract_trade_business()
