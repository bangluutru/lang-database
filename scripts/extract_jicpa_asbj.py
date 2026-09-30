#!/usr/bin/env python3
"""
scripts/extract_jicpa_asbj.py
Extracts audit, corporate governance, and professional accounting concepts from JICPA keywords
and authoritative ASBJ accounting standards.
Outputs: data/extracted/jicpa_asbj_candidates.jsonl
"""

import json
from pathlib import Path
from bs4 import BeautifulSoup

BASE_DIR = Path(__file__).resolve().parent.parent
JICPA_FILE = BASE_DIR / "data" / "raw" / "jicpa" / "glossary" / "jicpa_keyword_index.html"
OUTPUT_FILE = BASE_DIR / "data" / "extracted" / "jicpa_asbj_candidates.jsonl"

ASBJ_CANONICAL_STANDARDS = [
    {"term": "会計方針", "en": "Accounting policies", "sub_cat": "asbj_standards"},
    {"term": "会計上の見積り", "en": "Accounting estimates", "sub_cat": "asbj_standards"},
    {"term": "表示方法", "en": "Presentation method", "sub_cat": "asbj_standards"},
    {"term": "税効果会計", "en": "Tax effect accounting", "sub_cat": "asbj_standards"},
    {"term": "法人税等", "en": "Income taxes", "sub_cat": "asbj_standards"},
    {"term": "資産除去債務", "en": "Asset retirement obligations", "sub_cat": "asbj_standards"},
    {"term": "減損損失", "en": "Impairment loss", "sub_cat": "asbj_standards"},
    {"term": "収益認識", "en": "Revenue recognition", "sub_cat": "asbj_standards"},
    {"term": "金融商品", "en": "Financial instruments", "sub_cat": "asbj_standards"},
    {"term": "退職給付", "en": "Retirement benefits", "sub_cat": "asbj_standards"},
    {"term": "企業結合", "en": "Business combinations", "sub_cat": "asbj_standards"},
    {"term": "連結財務諸表", "en": "Consolidated financial statements", "sub_cat": "asbj_standards"},
    {"term": "棚卸資産の評価", "en": "Valuation of inventories", "sub_cat": "asbj_standards"},
    {"term": "包括利益", "en": "Comprehensive income", "sub_cat": "asbj_standards"},
    {"term": "時価算定", "en": "Fair value measurement", "sub_cat": "asbj_standards"},
    {"term": "工事契約", "en": "Construction contracts", "sub_cat": "asbj_standards"},
    {"term": "繰延税金資産", "en": "Deferred tax assets", "sub_cat": "asbj_standards"},
    {"term": "繰延税金負債", "en": "Deferred tax liabilities", "sub_cat": "asbj_standards"},
    {"term": "継続企業の前提", "en": "Going concern assumption", "sub_cat": "asbj_standards"},
]


def extract_jicpa_asbj():
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    print("[*] Extracting JICPA and ASBJ professional candidates ...")

    candidates = []
    seen = set()

    # 1. Extract JICPA Keywords
    if JICPA_FILE.exists():
        with open(JICPA_FILE, "r", encoding="utf-8", errors="ignore") as f:
            soup = BeautifulSoup(f.read(), "html.parser")

        for a in soup.find_all("a", href=True):
            if "/keyword/" in a["href"] and a["href"] != "/cpainfo/introduction/keyword/":
                txt = a.get_text().strip()
                if txt and txt not in seen and len(txt) <= 25:
                    seen.add(txt)
                    seq = len(candidates) + 1
                    kw_id = a["href"].strip("/").split("/")[-1]
                    candidates.append({
                        "extracted_candidate_id": f"cand-jicpa-{seq:06d}",
                        "source_id": "jicpa_glossary",
                        "source_file": "jicpa_keyword_index.html",
                        "source_record_id": f"keyword_{kw_id}",
                        "source_term_exact": txt,
                        "surface_candidate": txt,
                        "sub_category": "audit_corporate_governance",
                        "category": "audit"
                    })

    # 2. Extract ASBJ Standards Terms
    for item in ASBJ_CANONICAL_STANDARDS:
        t = item["term"]
        if t not in seen:
            seen.add(t)
            seq = len(candidates) + 1
            candidates.append({
                "extracted_candidate_id": f"cand-asbj-{seq:06d}",
                "source_id": "asbj_accounting_standards",
                "source_file": "asbj_standards_catalog",
                "source_record_id": f"asbj_{t}",
                "source_term_exact": t,
                "surface_candidate": t,
                "official_en": item["en"],
                "sub_category": item["sub_cat"],
                "category": "accounting"
            })

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for c in candidates:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")

    print(f"[+] Successfully extracted {len(candidates)} JICPA/ASBJ candidates to {OUTPUT_FILE.relative_to(BASE_DIR)}")


if __name__ == "__main__":
    extract_jicpa_asbj()
