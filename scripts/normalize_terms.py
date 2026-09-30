#!/usr/bin/env python3
"""
scripts/normalize_terms.py
Normalizes candidate terms from data/extracted/ into Layer C canonical vocabulary structures.
Applies Unicode NFKC normalization, fullwidth/halfwidth standardization,
strips whitespace and non-lexical annotations, and structures canonical identity.
Outputs: data/normalized/normalized_candidates.jsonl
"""

import json
import unicodedata
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
EXTRACTED_DIR = BASE_DIR / "data" / "extracted"
OUTPUT_FILE = BASE_DIR / "data" / "normalized" / "normalized_candidates.jsonl"


def normalize_japanese(text: str) -> str:
    if not text:
        return ""
    # Unicode NFKC normalization
    text = unicodedata.normalize("NFKC", text)
    # Strip spaces
    text = text.strip()
    # Normalize brackets
    text = text.replace("（", "(").replace("）", ")")
    # Clean trailing/leading non-lexical symbols
    text = re.sub(r"^[・\-\s]+", "", text)
    text = re.sub(r"[・\-\s]+$", "", text)
    return text


def main():
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    print("[*] Normalizing candidates from data/extracted/ ...")

    candidate_files = [
        EXTRACTED_DIR / "fsa_accounting_candidates.jsonl",
        EXTRACTED_DIR / "nta_tax_candidates.jsonl",
        EXTRACTED_DIR / "jicpa_asbj_candidates.jsonl",
        EXTRACTED_DIR / "trade_business_candidates.jsonl",
    ]

    total_in = 0
    normalized_list = []
    seen = set()

    for cfile in candidate_files:
        if not cfile.exists():
            continue
        print(f"    Reading {cfile.name} ...")
        with open(cfile, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                total_in += 1
                item = json.loads(line)
                raw_surface = item.get("surface_candidate") or item.get("source_term_exact", "")
                norm_surface = normalize_japanese(raw_surface)

                # Skip if empty or too long/short
                if not norm_surface or len(norm_surface) < 2 or len(norm_surface) > 40:
                    continue

                domain = item.get("category", "business")
                key = (norm_surface, domain)
                if key in seen:
                    continue
                seen.add(key)

                seq = len(normalized_list) + 1
                normalized_item = {
                    "normalized_candidate_id": f"norm-{seq:06d}",
                    "extracted_candidate_id": item.get("extracted_candidate_id", f"cand-gen-{seq:06d}"),
                    "surface": norm_surface,
                    "domain": domain,
                    "sub_category": item.get("sub_category", ""),
                    "source_id": item.get("source_id", "unknown"),
                    "source_file": item.get("source_file", ""),
                    "source_record_id": item.get("source_record_id", ""),
                    "source_term_exact": item.get("source_term_exact", norm_surface),
                    "official_en": item.get("official_en", ""),
                    "metadata": {
                        "balance": item.get("balance", ""),
                        "element_name": item.get("element_name", ""),
                        "nta_code": item.get("nta_code", ""),
                        "sheet": item.get("sheet", "")
                    }
                }
                normalized_list.append(normalized_item)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as out_f:
        for item in normalized_list:
            out_f.write(json.dumps(item, ensure_ascii=False) + "\n")

    print(f"[+] Total input candidates: {total_in}")
    print(f"[+] Normalized unique (surface, domain) entries: {len(normalized_list)}")
    print(f"[+] Saved to {OUTPUT_FILE.relative_to(BASE_DIR)}")


if __name__ == "__main__":
    main()
