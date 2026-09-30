#!/usr/bin/env python3
"""
scripts/extract_nta.py
Extracts official tax terminology from National Tax Agency (国税庁) sources:
- nta_senmon_yogo.html (Specialized Glossary)
- nta_code_index.html (Tax Answer Code Index)
Outputs: data/extracted/nta_tax_candidates.jsonl
"""

import json
import re
from pathlib import Path
from bs4 import BeautifulSoup

BASE_DIR = Path(__file__).resolve().parent.parent
CODE_INDEX_FILE = BASE_DIR / "data" / "raw" / "nta" / "taxanswer" / "nta_code_index.html"
SENMON_FILE = BASE_DIR / "data" / "raw" / "nta" / "taxanswer" / "nta_senmon_yogo.html"
OUTPUT_FILE = BASE_DIR / "data" / "extracted" / "nta_tax_candidates.jsonl"

TAX_STOPWORDS = {
    "について", "とは", "のしかた", "のあらまし", "の具体例", "の取扱い", "の手続",
    "の提出範囲と提出枚数等", "の提出義務", "の計算のしかた", "の計算", "があるとき",
    "をしたとき", "となったとき", "を行ったとき", "を受けたとき", "を支払ったとき",
    "に該当する", "に係る", "に関する", "となるもの", "となる人", "となる個人",
    "できるもの", "できないとき", "の意義", "の基本的なしくみ"
}


def clean_tax_term(label: str) -> str:
    # First extract term from inside parentheses if present like "災害や盗難などで資産に損害を受けたとき(雑損控除)" -> "雑損控除"
    m_paren = re.search(r"[（\(]([^）\)]+)[）\)]$", label)
    if m_paren:
        inner = m_paren.group(1).strip()
        if len(inner) >= 2 and not any(k in inner for k in ["平成", "令和", "第"]):
            return inner

    term = label
    for sw in TAX_STOPWORDS:
        term = term.replace(sw, "")

    # Clean leading/trailing particles
    term = re.sub(r"^[ひとつの]\s*", "", term)
    term = re.sub(r"[など等の]$", "", term)
    return term.strip()


def extract_tax_candidates():
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    print("[*] Extracting NTA tax candidates ...")

    candidates = []
    seen = set()

    # 1. Extract from Senmon Yogo
    if SENMON_FILE.exists():
        with open(SENMON_FILE, "r", encoding="utf-8", errors="ignore") as f:
            soup = BeautifulSoup(f.read(), "html.parser")
            for a in soup.find_all("a", href=True):
                txt = a.get_text().strip()
                if txt and len(txt) <= 20 and txt not in seen and not txt.startswith("http") and "国税" not in txt and "税務署" not in txt and "タックスアンサー" not in txt:
                    seen.add(txt)
                    candidates.append({
                        "source_id": "nta_tax_glossary_2026",
                        "source_term_exact": txt,
                        "surface_candidate": txt,
                        "sub_category": "senmon_yogo",
                        "category": "tax"
                    })

    # 2. Extract from Tax Answer Code Index
    if CODE_INDEX_FILE.exists():
        with open(CODE_INDEX_FILE, "r", encoding="utf-8", errors="ignore") as f:
            soup = BeautifulSoup(f.read(), "html.parser")

        for a in soup.find_all("a", href=True):
            raw_text = a.get_text().strip()
            m = re.match(r"^(\d{4})\s*(.+)$", raw_text)
            if not m:
                continue

            code, label = m.groups()
            cleaned = clean_tax_term(label)

            if not cleaned or len(cleaned) < 2 or len(cleaned) > 25:
                continue

            # Determine tax subcategory from code range
            sub_cat = "general_tax"
            c_num = int(code)
            if 1000 <= c_num < 2000:
                sub_cat = "income_tax_shotoku"
            elif 2000 <= c_num < 3000:
                sub_cat = "income_tax_business_gensen"
            elif 3000 <= c_num < 4000:
                sub_cat = "capital_gains_joto"
            elif 4000 <= c_num < 5000:
                sub_cat = "inheritance_gift_souzoku"
            elif 5000 <= c_num < 6000:
                sub_cat = "corporate_tax_hojin"
            elif 6000 <= c_num < 7000:
                sub_cat = "consumption_tax_shohi"
            elif 7000 <= c_num < 8000:
                sub_cat = "statutory_records_hotei"

            if cleaned not in seen:
                seen.add(cleaned)
                candidates.append({
                    "source_id": "nta_tax_glossary_2026",
                    "source_term_exact": label,
                    "surface_candidate": cleaned,
                    "nta_code": code,
                    "sub_category": sub_cat,
                    "category": "tax"
                })

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for c in candidates:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")

    print(f"[+] Successfully extracted {len(candidates)} NTA tax candidates to {OUTPUT_FILE.relative_to(BASE_DIR)}")


if __name__ == "__main__":
    extract_tax_candidates()
