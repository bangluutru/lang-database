#!/usr/bin/env python3
"""
scripts/extract_nta.py
Extracts official tax terminology from National Tax Agency (国税庁) sources:
- nta_senmon_yogo.html (Specialized Glossary)
- nta_code_index.html (Tax Answer Code Index)
- nta_ryaku_yogo.html (Statutory Abbreviations & Official Names)
Outputs: data/extracted/nta_tax_candidates.jsonl
"""

import json
import re
from pathlib import Path
from bs4 import BeautifulSoup

BASE_DIR = Path(__file__).resolve().parent.parent
CODE_INDEX_FILE = BASE_DIR / "data" / "raw" / "nta" / "taxanswer" / "nta_code_index.html"
SENMON_FILE = BASE_DIR / "data" / "raw" / "nta" / "taxanswer" / "nta_senmon_yogo.html"
RYAKU_FILE = BASE_DIR / "data" / "raw" / "nta" / "taxanswer" / "nta_ryaku_yogo.html"
OUTPUT_FILE = BASE_DIR / "data" / "extracted" / "nta_tax_candidates.jsonl"

TAX_STOPWORDS = {
    "について", "とは", "のしかた", "のあらまし", "の具体例", "の取扱い", "の手続",
    "の提出範囲と提出枚数等", "の提出義務", "の計算のしかた", "の計算", "があるとき",
    "をしたとき", "となったとき", "を行ったとき", "を受けたとき", "を支払ったとき",
    "に該当する", "に係る", "に関する", "となるもの", "となる人", "となる個人",
    "できるもの", "できないとき", "の意義", "の基本的なしくみ"
}

# Core statutory terms explicitly published and defined by NTA
CORE_NTA_TERMS = [
    ("国税", "national_tax", "国税通則法"),
    ("地方税", "local_tax", "地方税法"),
    ("直接税", "direct_tax", "税制基本"),
    ("間接税", "indirect_tax", "税制基本"),
    ("所得税", "income_tax", "所得税法"),
    ("法人税", "corporate_tax", "法人税法"),
    ("消費税", "consumption_tax", "消費税法"),
    ("住民税", "resident_tax", "地方税法"),
    ("確定申告", "tax_return", "タックスアンサー2020"),
    ("青色申告", "blue_return", "タックスアンサー2070"),
    ("白色申告", "white_return", "タックスアンサー2070"),
    ("年末調整", "year_end_adjustment", "タックスアンサー2662"),
    ("源泉徴収", "withholding_tax", "タックスアンサー2500"),
    ("源泉所得税", "withholding_income_tax", "タックスアンサー2500"),
    ("課税所得", "taxable_income", "所得税法"),
    ("非課税所得", "non_taxable_income", "所得税法"),
    ("課税標準", "tax_base", "国税通則法"),
    ("税額控除", "tax_credit", "タックスアンサー1200"),
    ("所得控除", "income_deduction", "タックスアンサー1100"),
    ("基礎控除", "basic_deduction", "タックスアンサー1199"),
    ("配偶者控除", "spouse_deduction", "タックスアンサー1191"),
    ("扶養控除", "dependent_deduction", "タックスアンサー1180"),
    ("医療費控除", "medical_deduction", "タックスアンサー1120"),
    ("社会保険料控除", "social_insurance_deduction", "タックスアンサー1130"),
    ("インボイス制度", "qualified_invoice", "適格請求書等保存方式"),
    ("適格請求書", "qualified_invoice_doc", "消費税法"),
    ("適格請求書発行事業者", "invoice_issuer", "消費税法"),
    ("電子帳簿保存法", "electronic_book_act", "電帳法"),
    ("税務調査", "tax_audit", "国税通則法"),
    ("税務署", "tax_office", "国税庁組織規則"),
    ("国税局", "regional_tax_bureau", "国税庁組織規則"),
    ("税理士", "certified_tax_accountant", "税理士法"),
    ("給与所得", "employment_income", "タックスアンサー1400"),
    ("事業所得", "business_income", "タックスアンサー1350"),
    ("譲渡所得", "capital_gains", "タックスアンサー1440"),
    ("退職所得", "retirement_income", "タックスアンサー1420"),
    ("不動産所得", "real_estate_income", "タックスアンサー1370"),
    ("給与所得控除", "employment_income_deduction", "タックスアンサー1410"),
    ("青色申告特別控除", "special_blue_deduction", "タックスアンサー2072"),
    ("仕入税額控除", "input_tax_credit", "タックスアンサー6401"),
    ("簡易課税制度", "simplified_tax_system", "タックスアンサー6505"),
    ("中間申告", "interim_return", "タックスアンサー6609"),
    ("予定納税", "prepayment_tax", "タックスアンサー2040"),
    ("修正申告", "amended_return", "タックスアンサー2026"),
    ("更正の請求", "correction_request", "タックスアンサー2026"),
    ("還付申告", "refund_return", "タックスアンサー2030"),
    ("延滞税", "delinquent_tax", "タックスアンサー9205"),
    ("過少申告加算税", "understatement_penalty", "国税通則法"),
    ("無申告加算税", "non_filing_penalty", "国税通則法"),
    ("重加算税", "heavy_penalty_tax", "国税通則法"),
    ("不納付加算税", "non_payment_penalty", "国税通則法"),
    ("e-Tax", "etax_system", "国税電子申告・納税システム"),
    ("益金", "taxable_revenue", "法人税法22条"),
    ("損金", "deductible_expense", "法人税法22条"),
    ("損金算入", "inclusion_in_deductible_expense", "法人税法"),
    ("損金不算入", "exclusion_from_deductible_expense", "法人税法"),
    ("交際費等の損金不算入", "entertainment_expense_disallowance", "タックスアンサー5265"),
    ("役員給与", "directors_compensation", "タックスアンサー5211"),
    ("定期同額給与", "regular_fixed_pay", "タックスアンサー5211"),
    ("事前確定届出給与", "pre_determined_pay", "タックスアンサー5211"),
    ("減価償却費", "depreciation_expense", "タックスアンサー5400"),
    ("別表四", "schedule_4_adjustments", "法人税申告書別表四"),
    ("別表五", "schedule_5_retained_earnings", "法人税申告書別表五")
]


def clean_tax_term(label: str) -> str:
    m_paren = re.search(r"[（\(]([^）\)]+)[）\)]$", label)
    if m_paren:
        inner = m_paren.group(1).strip()
        if len(inner) >= 2 and not any(k in inner for k in ["平成", "令和", "第"]):
            return inner

    term = label
    for sw in TAX_STOPWORDS:
        term = term.replace(sw, "")

    term = re.sub(r"^[ひとつの]\s*", "", term)
    term = re.sub(r"[など等の]$", "", term)
    return term.strip()


def extract_tax_candidates():
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    print("[*] Extracting NTA tax candidates ...")

    candidates = []
    seen = set()

    # 1. First add core statutory terms with official references
    for term, rec_id, ref in CORE_NTA_TERMS:
        if term not in seen:
            seen.add(term)
            seq = len(candidates) + 1
            candidates.append({
                "extracted_candidate_id": f"cand-nta-{seq:06d}",
                "source_id": "nta_tax_glossary_2026",
                "source_file": "core_statutory_catalog",
                "source_record_id": rec_id,
                "source_term_exact": term,
                "surface_candidate": term,
                "sub_category": "core_tax",
                "category": "tax",
                "legal_reference": ref
            })

    # 2. Extract from Senmon Yogo HTML
    if SENMON_FILE.exists():
        with open(SENMON_FILE, "r", encoding="utf-8", errors="ignore") as f:
            soup = BeautifulSoup(f.read(), "html.parser")
            for a in soup.find_all("a", href=True):
                txt = a.get_text().strip()
                if txt and len(txt) <= 25 and txt not in seen and not txt.startswith("http") and "タックスアンサー" not in txt:
                    seen.add(txt)
                    seq = len(candidates) + 1
                    candidates.append({
                        "extracted_candidate_id": f"cand-nta-{seq:06d}",
                        "source_id": "nta_tax_glossary_2026",
                        "source_file": "nta_senmon_yogo.html",
                        "source_record_id": f"senmon_yogo_{seq}",
                        "source_term_exact": txt,
                        "surface_candidate": txt,
                        "sub_category": "senmon_yogo",
                        "category": "tax"
                    })

    # 3. Extract from Tax Answer Code Index
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
            if cleaned in seen:
                continue

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
                sub_cat = "stamp_tax_inshi"

            seen.add(cleaned)
            seq = len(candidates) + 1
            candidates.append({
                "extracted_candidate_id": f"cand-nta-{seq:06d}",
                "source_id": "nta_tax_glossary_2026",
                "source_file": "nta_code_index.html",
                "source_record_id": f"code_{code}",
                "source_term_exact": cleaned,
                "surface_candidate": cleaned,
                "sub_category": sub_cat,
                "category": "tax",
                "nta_code": code,
                "raw_label": raw_text
            })

    # 4. Extract from Ryaku Yogo (Abbreviations)
    if RYAKU_FILE.exists():
        try:
            with open(RYAKU_FILE, "r", encoding="cp932", errors="ignore") as f:
                soup = BeautifulSoup(f.read(), "html.parser")
            for tr in soup.find_all("tr"):
                tds = tr.find_all("td")
                if len(tds) >= 2:
                    short_name = tds[0].get_text().strip()
                    full_name = tds[1].get_text().strip()
                    for term in [short_name, full_name]:
                        if term and len(term) >= 2 and term not in seen:
                            seen.add(term)
                            seq = len(candidates) + 1
                            candidates.append({
                                "extracted_candidate_id": f"cand-nta-{seq:06d}",
                                "source_id": "nta_tax_glossary_2026",
                                "source_file": "nta_ryaku_yogo.html",
                                "source_record_id": f"ryaku_{seq}",
                                "source_term_exact": term,
                                "surface_candidate": term,
                                "sub_category": "statutory_abbreviations",
                                "category": "tax"
                            })
        except Exception as e:
            print(f"[!] Warning reading ryaku yogo: {e}")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for item in candidates:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

    print(f"[+] Successfully extracted {len(candidates)} NTA tax candidates to {OUTPUT_FILE.relative_to(BASE_DIR)}")


if __name__ == "__main__":
    extract_tax_candidates()
