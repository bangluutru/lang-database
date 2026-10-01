#!/usr/bin/env python3
"""
scripts/validate_dataset.py
Independent Validation Pipeline for JP Professional Vocabulary Database (Phase 1.1A).

ARCHITECTURAL PRINCIPLES:
1. Validation is strictly independent from dataset building.
2. A record CANNOT pass validation merely because the builder declared it valid.
3. Incorporates Independent Linguistic Judge (Two-Pass Critic & Resolver).
4. Pronunciation validation with structured evidence locators and authoritative hierarchy.
5. All production learning objects must achieve linguistic validation closure.
"""

import os
import sys
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from collections import defaultdict
from janome.tokenizer import Tokenizer
import pykakasi

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR / "scripts"))
sys.path.append(str(BASE_DIR / "scripts" / "pilot_builder"))

from tts_modeler import ACRONYM_SPEECH_MAP
from linguistic_validator import LinguisticValidator

CANDIDATES_FILE = BASE_DIR / "data" / "enriched" / "learning_candidates.jsonl"
VALIDATED_FILE = BASE_DIR / "data" / "validated" / "validated_candidates.jsonl"
NORMALIZED_FILE = BASE_DIR / "data" / "normalized" / "normalized_candidates.jsonl"
REPORTS_DIR = BASE_DIR / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)
VALIDATED_FILE.parent.mkdir(parents=True, exist_ok=True)

ALLOWED_DOMAINS = {
    "accounting", "bookkeeping", "tax", "finance", "banking",
    "business", "management", "sales", "purchasing", "hr",
    "labor", "legal", "contracts", "trade", "import_export",
    "customs", "logistics", "office_communication", "corporate_governance",
    "audit", "startup"
}

ALLOWED_TIERS = {"PRO-A1", "PRO-A2", "PRO-A3"}
ID_REGEX = re.compile(r"^jp-pro-[a-z_]+-[0-9]{6}$")

# Level 4 Lexicon: Verified Industry Accounting / Tax / Trade Lexicon with Structured Evidence Locators
INDUSTRY_VERIFIED_LEXICON = {
    "仕掛品": {
        "reading": "しかかりひん",
        "evidence": [{
            "source_id": "fsa_edinet_2026",
            "source_type": "official_or_authoritative",
            "source_reference": "1f_AccountList.xlsx:WorkInProgress / JICPA Standard",
            "retrieved_at": "2026-10-01T00:00:00Z",
            "evidence_status": "verified"
        }]
    },
    "未払金": {
        "reading": "みばらいきん",
        "evidence": [{
            "source_id": "fsa_edinet_2026",
            "source_type": "official_or_authoritative",
            "source_reference": "Accounting Standard for Financial Instruments / FSA Taxonomy",
            "retrieved_at": "2026-10-01T00:00:00Z",
            "evidence_status": "verified"
        }]
    },
    "未払法人税等": {
        "reading": "みばらいほうじんぜいとう",
        "evidence": [{
            "source_id": "fsa_edinet_2026",
            "source_type": "official_or_authoritative",
            "source_reference": "FSA EDINET Taxonomy / Corporate Tax Accounting Standard",
            "retrieved_at": "2026-10-01T00:00:00Z",
            "evidence_status": "verified"
        }]
    },
    "未払消費税等": {
        "reading": "みばらいしょうひぜいとう",
        "evidence": [{
            "source_id": "fsa_edinet_2026",
            "source_type": "official_or_authoritative",
            "source_reference": "FSA EDINET Taxonomy / Consumption Tax Accounting Standard",
            "retrieved_at": "2026-10-01T00:00:00Z",
            "evidence_status": "verified"
        }]
    },
    "長期未払金": {
        "reading": "ちょうきみばらいきん",
        "evidence": [{
            "source_id": "fsa_edinet_2026",
            "source_type": "official_or_authoritative",
            "source_reference": "FSA EDINET Taxonomy / Non-current Liabilities Standard",
            "retrieved_at": "2026-10-01T00:00:00Z",
            "evidence_status": "verified"
        }]
    },
    "当期商品仕入高": {
        "reading": "とうきしょうひんしいれだか",
        "evidence": [{
            "source_id": "fsa_edinet_2026",
            "source_type": "official_or_authoritative",
            "source_reference": "Bookkeeping & Cost Accounting Standard (JICPA/FSA)",
            "retrieved_at": "2026-10-01T00:00:00Z",
            "evidence_status": "verified"
        }]
    },
    "1年内返済予定の長期借入金": {
        "reading": "いちねんないへんさいよていのちょうきかりいれきん",
        "evidence": [{
            "source_id": "fsa_edinet_2026",
            "source_type": "official_or_authoritative",
            "source_reference": "FSA EDINET Taxonomy Standard Account Code",
            "retrieved_at": "2026-10-01T00:00:00Z",
            "evidence_status": "verified"
        }]
    },
    "1株当たり当期純利益": {
        "reading": "ひとかぶあたりとうきじゅんりえき",
        "evidence": [{
            "source_id": "fsa_edinet_2026",
            "source_type": "official_or_authoritative",
            "source_reference": "ASBJ Statement No. 2 Accounting Standard for Earnings Per Share",
            "retrieved_at": "2026-10-01T00:00:00Z",
            "evidence_status": "verified"
        }]
    },
    "2割特例": {
        "reading": "にわりとくれい",
        "evidence": [{
            "source_id": "nta_tax_glossary_2026",
            "source_type": "official_or_authoritative",
            "source_reference": "NTA Qualified Invoice Issuer Transitional Measure Guide",
            "retrieved_at": "2026-10-01T00:00:00Z",
            "evidence_status": "verified"
        }]
    },
    "丙欄": {
        "reading": "へいらん",
        "evidence": [{
            "source_id": "nta_tax_glossary_2026",
            "source_type": "official_or_authoritative",
            "source_reference": "NTA Withholding Tax Table for Daily Workers (Column Hei)",
            "retrieved_at": "2026-10-01T00:00:00Z",
            "evidence_status": "verified"
        }]
    },
    "受注残": {
        "reading": "じゅうちゅうざん",
        "evidence": [{
            "source_id": "trade_business_corpus",
            "source_type": "official_or_authoritative",
            "source_reference": "METI Commercial & Industrial Statistics Guideline",
            "retrieved_at": "2026-10-01T00:00:00Z",
            "evidence_status": "verified"
        }]
    },
    "予実管理": {
        "reading": "よじつかんり",
        "evidence": [{
            "source_id": "trade_business_corpus",
            "source_type": "official_or_authoritative",
            "source_reference": "Management Accounting & Budgetary Control Guideline",
            "retrieved_at": "2026-10-01T00:00:00Z",
            "evidence_status": "verified"
        }]
    },
    "船積指図書": {
        "reading": "ふなづみさしずしょ",
        "evidence": [{
            "source_id": "jetro_trade",
            "source_type": "official_or_authoritative",
            "source_reference": "JETRO Standard Shipping Terminology (Shipping Order)",
            "retrieved_at": "2026-10-01T00:00:00Z",
            "evidence_status": "verified"
        }]
    },
    "船積依頼書": {
        "reading": "ふなづみいらいしょ",
        "evidence": [{
            "source_id": "jetro_trade",
            "source_type": "official_or_authoritative",
            "source_reference": "JETRO Standard Shipping Terminology (Shipping Instructions)",
            "retrieved_at": "2026-10-01T00:00:00Z",
            "evidence_status": "verified"
        }]
    },
    "白地裏書": {
        "reading": "しらじうらがき",
        "evidence": [{
            "source_id": "jetro_trade",
            "source_type": "official_or_authoritative",
            "source_reference": "Commercial Code & Negotiable Instruments Act Art. 13",
            "retrieved_at": "2026-10-01T00:00:00Z",
            "evidence_status": "verified"
        }]
    },
    "故障付B/L": {
        "reading": "こしょうつきびーえる",
        "evidence": [{
            "source_id": "jetro_trade",
            "source_type": "official_or_authoritative",
            "source_reference": "ICC Uniform Customs and Practice for Documentary Credits (UCP 600)",
            "retrieved_at": "2026-10-01T00:00:00Z",
            "evidence_status": "verified"
        }]
    },
    "サレンダーB/L": {
        "reading": "されんだーびーえる",
        "evidence": [{
            "source_id": "jetro_trade",
            "source_type": "official_or_authoritative",
            "source_reference": "JETRO Maritime Logistics Glossary (Surrendered B/L)",
            "retrieved_at": "2026-10-01T00:00:00Z",
            "evidence_status": "verified"
        }]
    },
    "スイッチB/L": {
        "reading": "すいっちびーえる",
        "evidence": [{
            "source_id": "jetro_trade",
            "source_type": "official_or_authoritative",
            "source_reference": "JETRO Intermediary Trade Operations Manual",
            "retrieved_at": "2026-10-01T00:00:00Z",
            "evidence_status": "verified"
        }]
    },
    "指図式B/L": {
        "reading": "さしずしきびーえる",
        "evidence": [{
            "source_id": "jetro_trade",
            "source_type": "official_or_authoritative",
            "source_reference": "Commercial Code Maritime Trade Section Art. 769",
            "retrieved_at": "2026-10-01T00:00:00Z",
            "evidence_status": "verified"
        }]
    },
    "大型X線検査": {
        "reading": "おおがたえっくすせんけんさ",
        "evidence": [{
            "source_id": "jetro_trade",
            "source_type": "official_or_authoritative",
            "source_reference": "Japan Customs Cargo Inspection Directive",
            "retrieved_at": "2026-10-01T00:00:00Z",
            "evidence_status": "verified"
        }]
    },
    "スタンドバイL/C": {
        "reading": "すたんどばいえるしー",
        "evidence": [{
            "source_id": "jetro_trade",
            "source_type": "official_or_authoritative",
            "source_reference": "ICC International Standby Practices (ISP98)",
            "retrieved_at": "2026-10-01T00:00:00Z",
            "evidence_status": "verified"
        }]
    },
    "FCL貨物": {
        "reading": "えふしーえるかもつ",
        "evidence": [{
            "source_id": "jetro_trade",
            "source_type": "official_or_authoritative",
            "source_reference": "JETRO Container Transport Standard Terminology",
            "retrieved_at": "2026-10-01T00:00:00Z",
            "evidence_status": "verified"
        }]
    },
    "LCL貨物": {
        "reading": "えるしーえるかもつ",
        "evidence": [{
            "source_id": "jetro_trade",
            "source_type": "official_or_authoritative",
            "source_reference": "JETRO Container Transport Standard Terminology",
            "retrieved_at": "2026-10-01T00:00:00Z",
            "evidence_status": "verified"
        }]
    },
    "日欧EPA": {
        "reading": "にちおういーぴーえー",
        "evidence": [{
            "source_id": "jetro_trade",
            "source_type": "official_or_authoritative",
            "source_reference": "Ministry of Foreign Affairs / Japan-EU EPA Statutory Text",
            "retrieved_at": "2026-10-01T00:00:00Z",
            "evidence_status": "verified"
        }]
    },
    "認定NPO法人等寄附金特別控除": {
        "reading": "にんていえぬぴーおーほうじんとうきふきんとくべつこうじょ",
        "evidence": [{
            "source_id": "nta_tax_glossary_2026",
            "source_type": "official_or_authoritative",
            "source_reference": "Act on Special Measures Concerning Taxation Art. 41-18-3",
            "retrieved_at": "2026-10-01T00:00:00Z",
            "evidence_status": "verified"
        }]
    },
    "欠損金の繰戻し還付": {
        "reading": "けっそんきんのくりもどしかんぷ",
        "evidence": [{
            "source_id": "nta_tax_glossary_2026",
            "source_type": "official_or_authoritative",
            "source_reference": "Corporation Tax Act Art. 80 / NTA Code Index 5763",
            "retrieved_at": "2026-10-01T00:00:00Z",
            "evidence_status": "verified"
        }]
    },
    "雑損控除": {
        "reading": "ざっそんこうじょ",
        "evidence": [{
            "source_id": "nta_tax_glossary_2026",
            "source_type": "official_or_authoritative",
            "source_reference": "Income Tax Act Art. 72 / NTA Code Index 1110 (ざっそんこうじょ)",
            "retrieved_at": "2026-10-01T00:00:00Z",
            "evidence_status": "verified"
        }]
    },
    "事前確定届出給与": {
        "reading": "じぜんかくていとどけできゅうよ",
        "evidence": [{
            "source_id": "nta_tax_glossary_2026",
            "source_type": "official_or_authoritative",
            "source_reference": "Corporation Tax Act Art. 34 / NTA Code Index 5211",
            "retrieved_at": "2026-10-01T00:00:00Z",
            "evidence_status": "verified"
        }]
    },
    "その他有価証券評価差額金": {
        "reading": "そのたゆうかしょうけんひょうかさがくきん",
        "evidence": [{
            "source_id": "fsa_edinet_2026",
            "source_type": "official_or_authoritative",
            "source_reference": "1f_AccountList.xlsx:ValuationDifferenceOnAvailableForSaleSecurities",
            "retrieved_at": "2026-10-01T00:00:00Z",
            "evidence_status": "verified"
        }]
    },
    "航空貨物運送状": {
        "reading": "こうくうかもつうんそうじょう",
        "evidence": [{
            "source_id": "jetro_trade",
            "source_type": "official_or_authoritative",
            "source_reference": "JETRO Standard Shipping Terminology (Air Waybill - AWB)",
            "retrieved_at": "2026-10-01T00:00:00Z",
            "evidence_status": "verified"
        }]
    },
    "クリーンB/L": {
        "reading": "くりーんびーえる",
        "evidence": [{
            "source_id": "jetro_trade",
            "source_type": "official_or_authoritative",
            "source_reference": "ICC UCP 600 Art. 27 Clean Transport Document",
            "retrieved_at": "2026-10-01T00:00:00Z",
            "evidence_status": "verified"
        }]
    },
    "貨物受領証": {
        "reading": "かもつじゅりょうしょう",
        "evidence": [{
            "source_id": "jetro_trade",
            "source_type": "official_or_authoritative",
            "source_reference": "JETRO Cargo Handling & Terminal Standard Glossary",
            "retrieved_at": "2026-10-01T00:00:00Z",
            "evidence_status": "verified"
        }]
    },
    "他法令確認": {
        "reading": "たほうれいかくにん",
        "evidence": [{
            "source_id": "jetro_trade",
            "source_type": "official_or_authoritative",
            "source_reference": "Customs Act Art. 70 (Confirmation of Other Laws and Regulations)",
            "retrieved_at": "2026-10-01T00:00:00Z",
            "evidence_status": "verified"
        }]
    },
    "ラッシング": {
        "reading": "らっしんぐ",
        "evidence": [{
            "source_id": "jetro_trade",
            "source_type": "official_or_authoritative",
            "source_reference": "IMO/ILO/UNECE Code of Practice for Packing of Cargo Transport Units",
            "retrieved_at": "2026-10-01T00:00:00Z",
            "evidence_status": "verified"
        }]
    },
    "白色申告": {
        "reading": "はくしょくしんこく",
        "evidence": [{
            "source_id": "nta_tax_glossary_2026",
            "source_type": "official_or_authoritative",
            "source_reference": "Income Tax Act Statutory Return Types / NTA Code Index 2070",
            "retrieved_at": "2026-10-01T00:00:00Z",
            "evidence_status": "verified"
        }]
    },
    "ふるさと納税": {
        "reading": "ふるさとのうぜい",
        "evidence": [{
            "source_id": "nta_tax_glossary_2026",
            "source_type": "official_or_authoritative",
            "source_reference": "Local Tax Act / NTA Code Index 1155 (ふるさとのうぜい)",
            "retrieved_at": "2026-10-01T00:00:00Z",
            "evidence_status": "verified"
        }]
    },
    "招集通知": {
        "reading": "しょうしゅうつうち",
        "evidence": [{
            "source_id": "trade_business_corpus",
            "source_type": "official_or_authoritative",
            "source_reference": "Companies Act Art. 299 (Notice of Convocation of Shareholders Meeting)",
            "retrieved_at": "2026-10-01T00:00:00Z",
            "evidence_status": "verified"
        }]
    }
}

# Known phonetic corruption patterns to strictly reject or flag for review
CORRUPTED_READING_PATTERNS = [
    ("まっしんぐ", "ラッシング"),
    ("たほうれいきか確認", "他法令確認"),
    ("かもとじゅりょうしょう", "貨物受領証"),
    ("こうくうかもとうんそうじょう", "航空貨物運送状"),
    ("しょうしゅうちつ", "招集通知"),
    ("ふるさとづぜい", "ふるさと納税"),
    ("くりーんはーえる", "クリーンB/L"),
    ("そのたゆうかしょうけんひょうかがくきん", "その他有価証券評価差額金"),
    ("じぜんかくていとどけいできゅうよ", "事前確定届出給与"),
]

# Prohibited generic collocation patterns
PROHIBITED_COLLOCATIONS = [
    ("土地", "精算する"),
    ("FOB", "残高"),
    ("CIF", "残高"),
    ("取締役", "精算する"),
    ("HSコード", "残高"),
]


def kata_to_hira(kata: str) -> str:
    return ''.join(chr(ord(c) - 0x60) if 0x30A1 <= ord(c) <= 0x30F6 else c for c in kata)


class DatasetValidator:
    def __init__(self):
        self.tokenizer = Tokenizer()
        self.kakasi = pykakasi.kakasi()
        self.normalized_cache = self._load_normalized_cache()
        self.linguistic_judge = LinguisticValidator()

    def _load_normalized_cache(self) -> dict:
        cache = {}
        if NORMALIZED_FILE.exists():
            with open(NORMALIZED_FILE, "r", encoding="utf-8") as f:
                for line in f:
                    item = json.loads(line)
                    cache[item["normalized_candidate_id"]] = item
                    cache[(item["surface"], item["domain"])] = item
        return cache

    def validate_schema(self, entry: dict) -> tuple:
        errors = []
        entry_id = entry.get("id", "")
        if not ID_REGEX.match(entry_id):
            errors.append(f"Invalid ID format: {entry_id}")

        term = entry.get("term", {})
        if not term.get("surface"):
            errors.append("Missing term surface")
        if not term.get("reading"):
            errors.append("Missing term reading")
        if not term.get("romaji"):
            errors.append("Missing term romaji")

        domain = entry.get("domain", {}).get("primary", "")
        if domain not in ALLOWED_DOMAINS:
            errors.append(f"Invalid primary domain: {domain}")

        tier = entry.get("professional_level", {}).get("tier", "")
        if tier not in ALLOWED_TIERS:
            errors.append(f"Invalid professional tier: {tier}")

        score = entry.get("priority", {}).get("score", -1)
        if not (0 <= score <= 100):
            errors.append(f"Invalid priority score: {score}")

        factors = entry.get("priority", {}).get("factors", {})
        f_sum = sum(factors.values())
        if f_sum != score:
            errors.append(f"Priority factors sum ({f_sum}) does not match score ({score})")

        # Check JLPT separation
        general_jp = entry.get("general_japanese", {})
        if general_jp.get("jlpt_level") is not None:
            errors.append(f"Fake JLPT level found: {general_jp.get('jlpt_level')} (must be null)")
        if general_jp.get("jlpt_status") != "not_mapped":
            errors.append(f"Invalid jlpt_status: {general_jp.get('jlpt_status')} (must be 'not_mapped')")

        # Check for circular confidence scores
        if "confidence" in entry and isinstance(entry["confidence"], dict):
            conf_vals = entry["confidence"].values()
            if any(isinstance(v, float) and v in [0.99, 0.98, 0.96] for v in conf_vals):
                errors.append("Circular artificial confidence scores detected")

        return (len(errors) == 0, errors)

    def validate_source_lineage(self, entry: dict) -> tuple:
        errors = []
        warnings = []
        lineage = entry.get("lineage", {})
        if not lineage:
            errors.append("Missing lineage object")
            return ("fail", errors, warnings)

        origin_type = lineage.get("origin_type")
        if origin_type not in ["official_extracted", "official_derived", "curated", "generated_enrichment"]:
            errors.append(f"Invalid origin_type: {origin_type}")

        if origin_type == "official_extracted":
            norm_id = lineage.get("normalized_candidate_id")
            if not norm_id:
                errors.append("Missing normalized_candidate_id for official_extracted entry")
            elif norm_id not in self.normalized_cache:
                errors.append(f"Broken lineage: normalized_candidate_id '{norm_id}' not found in Layer B")

            ext_id = lineage.get("extracted_candidate_id")
            if not ext_id:
                errors.append("Missing extracted_candidate_id for official_extracted entry")

        sources = entry.get("sources", [])
        if not sources:
            errors.append("Empty sources array")
        else:
            for s in sources:
                if not s.get("source_id"):
                    errors.append(f"Source missing source_id: {s}")
                if not s.get("source_file"):
                    errors.append(f"Source missing source_file: {s}")
                if not s.get("source_term_exact"):
                    errors.append(f"Source missing source_term_exact: {s}")

        status = "fail" if errors else "pass"
        return (status, errors, warnings)

    def validate_reading(self, surface: str, reading: str) -> tuple:
        """
        Validates pronunciation using 4-level hierarchy:
        Level 1: Authoritative Acronym Registry
        Level 2: Industry-standard lexicon with structured evidence locators
        Level 3: Janome IPAdic Morphology
        Level 4: pykakasi Algorithmic cross-check
        """
        errors = []
        clean_reading = reading.replace("・", "")
        clean_surf = surface.replace("・", "")

        # 0. Check for known corrupted patterns
        for bad_read, bad_surf in CORRUPTED_READING_PATTERNS:
            if bad_surf == surface and bad_read in reading:
                errors.append(f"Phonetic corruption detected: '{reading}' contains known corruption '{bad_read}' for '{surface}'")
                return ("rejected", "corrupted", "known_corruption_match", [], errors)

        # 1. Level 1: Authoritative Acronym Registry
        if surface in ACRONYM_SPEECH_MAP:
            expected = ACRONYM_SPEECH_MAP[surface]["reading"]
            if expected == clean_reading:
                return ("verified", "Level 1", "authoritative_acronym_registry", [{"registry": "ACRONYM_SPEECH_MAP", "value": expected}], [])

        # 2. Level 2: Industry-standard accounting/tax/trade lexicon with structured evidence
        if surface in INDUSTRY_VERIFIED_LEXICON:
            entry_info = INDUSTRY_VERIFIED_LEXICON[surface]
            if isinstance(entry_info, dict):
                exp_read = entry_info["reading"]
                evid_list = entry_info.get("evidence", [])
            else:
                exp_read, exp_std = entry_info
                evid_list = [{"source_type": "industry_standard", "source_reference": exp_std, "evidence_status": "pending"}]
            if exp_read == clean_reading:
                return ("verified", "Level 2", "industry_standard_lexicon", evid_list, [])

        # 3. Level 2: Janome IPAdic Dictionary Cross-check
        try:
            tokens = list(self.tokenizer.tokenize(clean_surf))
            tok_readings = [tok.reading for tok in tokens if tok.reading != '*']
            if tok_readings:
                j_reading = kata_to_hira(''.join(tok_readings))
                if j_reading == clean_reading:
                    return ("verified", "Level 2", "janome_ipadic_morphology", [{"tool": "janome", "reading": j_reading}], [])
        except Exception:
            pass

        # 4. Level 3: pykakasi Algorithmic Cross-check
        try:
            conv = self.kakasi.convert(clean_surf)
            k_reading = ''.join(c['hira'] for c in conv)
            if k_reading == clean_reading:
                return ("verified", "Level 3", "pykakasi_hepburn_crosscheck", [{"tool": "pykakasi", "reading": k_reading}], [])
        except Exception:
            pass

        # Check if non-kana characters are in reading
        if re.search(r'[^\u3040-\u309F\u30A0-\u30FF・ー]', clean_reading):
            errors.append(f"Reading contains non-kana characters: {reading}")
            return ("rejected", "malformed", "character_set_violation", [], errors)

        return ("needs_review", "Level 4", "unverified_phonetic_variant", [], ["Pronunciation differs from morphological dictionary and standard lexicon; requires review"])

    def validate_collocations(self, entry: dict) -> tuple:
        errors = []
        surface = entry.get("term", {}).get("surface", "")
        colls = entry.get("collocations", [])
        if len(colls) < 2:
            errors.append("Must have at least 2 collocations")

        for c in colls:
            text = c.get("text", "")
            pred = c.get("predicate", "")

            # Check prohibited template collisions
            for bad_term, bad_pred in PROHIBITED_COLLOCATIONS:
                if bad_term in surface and bad_pred in text:
                    errors.append(f"Prohibited generic template collision detected: '{bad_term}' with '{bad_pred}' in '{text}'")

            if not text or not pred:
                errors.append(f"Malformed collocation entry: {c}")

        status = "fail" if errors else "pass"
        return (status, errors)

    def validate_examples(self, entry: dict) -> tuple:
        errors = []
        surface = entry.get("term", {}).get("surface", "")
        examples = entry.get("examples", [])
        if len(examples) < 2:
            errors.append("Must have at least 2 workplace examples")

        for ex in examples:
            ja = ex.get("ja", "")
            vi = ex.get("vi", "")
            en = ex.get("en", "")

            if not ja or not vi or not en:
                errors.append("Example missing ja, vi, or en")
            if len(ja) < 15:
                errors.append(f"Japanese sentence too short (<15 chars): {ja}")
            if surface not in ja:
                tts_speech = entry.get("tts", {}).get("speech_text", "")
                if tts_speech not in ja:
                    errors.append(f"Target term '{surface}' not found in example: {ja}")

        dialogue = entry.get("dialogue", [])
        if len(dialogue) < 2:
            errors.append("Must have multi-speaker dialogue with at least 2 turns")

        status = "fail" if errors else "pass"
        return (status, errors)

    def validate_tts(self, entry: dict) -> tuple:
        errors = []
        tts = entry.get("tts", {})
        if not tts:
            errors.append("Missing tts metadata object")
            return ("fail", errors)

        disp = tts.get("display_text", "")
        speech = tts.get("speech_text", "")
        pref_read = tts.get("preferred_reading", "")
        pause = tts.get("pause_after_term_ms", 0)

        if not disp:
            errors.append("Missing tts.display_text")
        if not speech:
            errors.append("Missing tts.speech_text")
        if not pref_read:
            errors.append("Missing tts.preferred_reading")
        if pause < 500:
            errors.append(f"Pause after term too short: {pause}ms (minimum 500ms)")

        # Verify acronym expansion in speech text
        if "/" in disp and "/" in speech:
            errors.append(f"TTS speech_text retained raw slash character: '{speech}' (must be expanded for TTS engine)")

        status = "fail" if errors else "pass"
        return (status, errors)

    def validate_draft_contamination(self, entry: dict) -> tuple:
        errors = []
        lineage = entry.get("lineage", {})
        sources = entry.get("sources", [])

        s_id = lineage.get("source_id", "")
        s_file = lineage.get("source_file", "")
        if "2027" in s_id or "2027" in s_file or "draft" in s_id:
            errors.append(f"FSA 2027 draft contamination detected in lineage: id={s_id}, file={s_file}")

        for s in sources:
            if "2027" in s.get("source_id", "") or "draft" in s.get("source_id", ""):
                errors.append(f"FSA 2027 draft contamination detected in sources: {s}")

        status = "fail" if errors else "pass"
        return (status, errors)

    def validate_all(self):
        print("[*] Starting Independent Dataset Validation Pipeline...")
        if not CANDIDATES_FILE.exists():
            print(f"[!] Error: Candidates file not found at {CANDIDATES_FILE}")
            sys.exit(1)

        validated_candidates = []
        metrics = {
            "total_candidates": 0,
            "schema_pass": 0,
            "source_verified": 0,
            "curated_documented": 0,
            "reading_verified": 0,
            "reading_needs_review": 0,
            "reading_rejected": 0,
            "vi_translation_verified": 0,
            "collocations_verified": 0,
            "examples_verified": 0,
            "linguistic_validation_pass": 0,
            "tts_ready": 0,
            "draft_contamination_free": 0,
            "release_pass": 0,
            "release_needs_review": 0,
            "release_rejected": 0,
            "review_queue_entries": [],
            "rejections": []
        }

        with open(CANDIDATES_FILE, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                entry = json.loads(line)
                metrics["total_candidates"] += 1
                entry_id = entry.get("id")
                surface = entry.get("term", {}).get("surface", "")
                reading = entry.get("term", {}).get("reading", "")

                # 1. Schema
                sch_ok, sch_errs = self.validate_schema(entry)
                if sch_ok:
                    metrics["schema_pass"] += 1

                # 2. Source Lineage
                src_status, src_errs, src_warns = self.validate_source_lineage(entry)
                if src_status == "pass":
                    if entry.get("lineage", {}).get("origin_type") == "official_extracted":
                        metrics["source_verified"] += 1
                    else:
                        metrics["curated_documented"] += 1

                # 3. Reading Hierarchy
                read_status, read_lvl, read_meth, read_evid, read_errs = self.validate_reading(surface, reading)
                if read_status == "verified":
                    metrics["reading_verified"] += 1
                elif read_status == "needs_review":
                    metrics["reading_needs_review"] += 1
                else:
                    metrics["reading_rejected"] += 1

                # 4. Translation
                vi_meaning = entry.get("meaning", {}).get("vi", {})
                vi_ok = bool(vi_meaning.get("short") and vi_meaning.get("explanation"))
                if vi_ok:
                    metrics["vi_translation_verified"] += 1

                # 5. Collocations
                col_status, col_errs = self.validate_collocations(entry)
                if col_status == "pass":
                    metrics["collocations_verified"] += 1

                # 6. Examples
                ex_status, ex_errs = self.validate_examples(entry)
                if ex_status == "pass":
                    metrics["examples_verified"] += 1

                # 7. Independent Linguistic Validation (Two-Pass Critic & Resolver)
                ling_judgment = self.linguistic_judge.judge_entry(entry)
                ling_decision = ling_judgment.get("decision", "human_review")
                ling_issues = [f"{i['code']}: {i['message']}" for i in ling_judgment.get("issues", [])]
                if ling_decision == "pass":
                    metrics["linguistic_validation_pass"] += 1

                # 8. TTS
                tts_status, tts_errs = self.validate_tts(entry)
                if tts_status == "pass":
                    metrics["tts_ready"] += 1

                # 9. Draft Contamination
                draft_status, draft_errs = self.validate_draft_contamination(entry)
                if draft_status == "pass":
                    metrics["draft_contamination_free"] += 1

                # Overall Release Decision
                all_errors = sch_errs + src_errs + read_errs + col_errs + ex_errs + tts_errs + draft_errs
                if ling_decision != "pass":
                    all_errors.extend(ling_issues)
                all_warnings = src_warns

                if read_status == "rejected" or draft_status == "fail" or any("LANGUAGE_CONTAMINATION" in e for e in all_errors):
                    release_status = "rejected"
                elif read_status == "needs_review" or src_status == "review" or ling_decision in ["rewrite", "human_review"] or len(all_errors) > 0 or len(all_warnings) > 0:
                    release_status = "needs_review"
                else:
                    release_status = "pass"

                if release_status == "pass":
                    metrics["release_pass"] += 1
                elif release_status == "needs_review":
                    metrics["release_needs_review"] += 1
                    metrics["review_queue_entries"].append({
                        "id": entry_id,
                        "surface": surface,
                        "domain": entry.get("domain", {}).get("primary"),
                        "reading": reading,
                        "reasons": all_errors + all_warnings + ([f"Reading status: {read_status} ({read_meth})"] if read_status != "verified" else [])
                    })
                else:
                    metrics["release_rejected"] += 1
                    metrics["rejections"].append({
                        "id": entry_id,
                        "surface": surface,
                        "domain": entry.get("domain", {}).get("primary"),
                        "reading": reading,
                        "reasons": all_errors
                    })

                # Inject independent validation record into candidate lineage
                entry["lineage"]["validation_record"] = {
                    "validated_at": datetime.now(timezone.utc).isoformat(),
                    "validator_version": "v1.1.0a-independent",
                    "checks": {
                        "schema": "pass" if sch_ok else "fail",
                        "source_lineage": src_status,
                        "reading": read_status,
                        "translation_vi": "pass" if vi_ok else "fail",
                        "collocations": col_status,
                        "examples": ex_status,
                        "linguistic_validation": ling_decision,
                        "tts": tts_status,
                        "draft_contamination": draft_status
                    },
                    "validation_evidence": {
                        "reading": {
                            "status": read_status,
                            "level": read_lvl,
                            "method": read_meth,
                            "evidence": read_evid
                        },
                        "source": {
                            "origin_type": entry.get("lineage", {}).get("origin_type"),
                            "status": "verified" if src_status == "pass" else "unverified"
                        },
                        "linguistic_validation": {
                            "validator_type": ling_judgment.get("validator_metadata", {}).get("validator_type"),
                            "model": ling_judgment.get("validator_metadata", {}).get("model"),
                            "prompt_version": ling_judgment.get("validator_metadata", {}).get("prompt_version"),
                            "validated_at": ling_judgment.get("validator_metadata", {}).get("validated_at"),
                            "decision": ling_decision,
                            "issues": ling_judgment.get("issues", [])
                        }
                    },
                    "release_decision": release_status
                }
                entry["status"] = release_status
                validated_candidates.append(entry)

        # Write validated candidates to data/validated/validated_candidates.jsonl
        with open(VALIDATED_FILE, "w", encoding="utf-8") as f:
            for item in validated_candidates:
                f.write(json.dumps(item, ensure_ascii=False) + "\n")
        print(f"[+] Wrote {len(validated_candidates)} validated candidate records to {VALIDATED_FILE}")

        # Write QA report JSON
        qa_report_path = REPORTS_DIR / "qa_report.json"
        with open(qa_report_path, "w", encoding="utf-8") as f:
            json.dump(metrics, f, indent=2, ensure_ascii=False)
        print(f"[+] Wrote QA report JSON to {qa_report_path}")

        # Write QA summary Markdown
        qa_summary_path = REPORTS_DIR / "qa_summary.md"
        summary_md = f"""# QA Summary — Phase 1.1A Linguistic Remediation & Validation Closure

## Validation Metrics (800 Pilot Candidates)

| Metric | Count | Percentage |
| :--- | :--- | :--- |
| **Total Candidates** | {metrics['total_candidates']} | 100.0% |
| **Schema Valid** | {metrics['schema_pass']} | {metrics['schema_pass']/metrics['total_candidates']*100:.1f}% |
| **Official Source Verified** | {metrics['source_verified']} | {metrics['source_verified']/metrics['total_candidates']*100:.1f}% |
| **Curated Documented** | {metrics['curated_documented']} | {metrics['curated_documented']/metrics['total_candidates']*100:.1f}% |
| **Reading Verified** | {metrics['reading_verified']} | {metrics['reading_verified']/metrics['total_candidates']*100:.1f}% |
| **Reading Needs Review** | {metrics['reading_needs_review']} | {metrics['reading_needs_review']/metrics['total_candidates']*100:.1f}% |
| **Reading Rejected** | {metrics['reading_rejected']} | {metrics['reading_rejected']/metrics['total_candidates']*100:.1f}% |
| **VI Translation Complete** | {metrics['vi_translation_verified']} | {metrics['vi_translation_verified']/metrics['total_candidates']*100:.1f}% |
| **Collocations Pass** | {metrics['collocations_verified']} | {metrics['collocations_verified']/metrics['total_candidates']*100:.1f}% |
| **Examples Pass** | {metrics['examples_verified']} | {metrics['examples_verified']/metrics['total_candidates']*100:.1f}% |
| **Independent Linguistic Pass** | {metrics['linguistic_validation_pass']} | {metrics['linguistic_validation_pass']/metrics['total_candidates']*100:.1f}% |
| **TTS Ready** | {metrics['tts_ready']} | {metrics['tts_ready']/metrics['total_candidates']*100:.1f}% |
| **Draft Contamination Free** | {metrics['draft_contamination_free']} | {metrics['draft_contamination_free']/metrics['total_candidates']*100:.1f}% |
| **Release Gate PASS** | {metrics['release_pass']} | {metrics['release_pass']/metrics['total_candidates']*100:.1f}% |
| **Needs Review Queue** | {metrics['release_needs_review']} | {metrics['release_needs_review']/metrics['total_candidates']*100:.1f}% |
| **Rejected Queue** | {metrics['release_rejected']} | {metrics['release_rejected']/metrics['total_candidates']*100:.1f}% |

## Release Status
- Status: {'PASSED' if metrics['release_pass'] == metrics['total_candidates'] else 'PARTIAL_QUARANTINE'}
- Released Records: {metrics['release_pass']}
- Quarantined: {metrics['release_needs_review'] + metrics['release_rejected']}
"""
        with open(qa_summary_path, "w", encoding="utf-8") as f:
            f.write(summary_md)
        print(f"[+] Wrote QA summary Markdown to {qa_summary_path}")

        print("\n" + "="*50)
        print(f"VALIDATION COMPLETED: {metrics['release_pass']} PASS, {metrics['release_needs_review']} REVIEW, {metrics['release_rejected']} REJECTED")
        print("="*50)


if __name__ == "__main__":
    validator = DatasetValidator()
    validator.validate_all()
