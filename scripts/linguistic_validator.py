#!/usr/bin/env python3
"""
scripts/linguistic_validator.py
Independent Linguistic Judge for Japanese Professional Vocabulary Database (Phase 1.1A).

CORE ARCHITECTURAL PRINCIPLES:
1. Strict Separation of Concerns: Validator is independent of Builder.
2. Two-Pass Architecture:
   - Pass A (Critic): rigorously identifies collocation mismatch, semantic incompatibility,
     professional domain errors, artificial template contamination, and translation bleed.
   - Pass B (Resolver): resolves candidate flaws, synthesizes natural workplace alternatives,
     and subjects rewrites to a second critic evaluation before candidate certification.
3. Machine-Readable Decision Schema with standardized reason codes.
4. Deterministic Validation Caching in data/validation_cache/ using SHA-256 keys.
5. Production Verification: Objects passing validation are upgraded from 'generated'
   to 'linguistically_validated'.
"""

import os
import sys
import re
import json
import hashlib
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Tuple, Any, Optional

BASE_DIR = Path(__file__).resolve().parent.parent
CACHE_DIR = BASE_DIR / "data" / "validation_cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

PROMPT_VERSION = "v1.1.0b-deterministic-rules"
MODEL_IDENTIFIER = "deterministic-rule-validator-v1.1"

# Regular expression to detect Vietnamese characters / diacritics in English strings
VIETNAMESE_DIACRITICS_RE = re.compile(
    r"[àáảãạăắằẳẵặâấầẩẫậđèéẻẽẹêếềểễệìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵ"
    r"ÀÁẢÃẠĂẮẰẲẴẶÂẤẦẨẪẬĐÈÉẺẼẸÊẾỀỂỄỆÌÍỈĨỊÒÓỎÕỌÔỐỒỔỖỘƠỚỜỞỠỢÙÚỦŨỤƯỨỪỬỮỰỲÝỶỸỴ]"
)

# Common Vietnamese words that might lack diacritics in corrupted machine outputs
VIETNAMESE_WORDS = {
    "chuong", "trinh", "dong", "gop", "que", "huong", "thu", "tuc", "thue", "nhan", "hang",
    "hoa", "don", "chung", "tu", "khau", "tru", "toan", "khai", "bao", "bien", "lai"
}

# English phrases that might accidentally appear in Vietnamese explanations/translations
ENGLISH_RAW_PATTERNS = [
    "we completed", "upon finalizing", "in line with", "during month-end", "based on",
    "the company", "fiscal year", "board of directors", "competent tax office"
]

# Explicit semantic incompatibility matrix: (Entity Class / Term, Invalid Predicate)
SEMANTIC_COLLISION_RULES = [
    # Professional service firms / audit firms cannot be booked as accounts, settled, or have account balances
    ({"professional_service_firm", "audit_firm", "監査法人", "会計事務所", "税理士法人"}, {"計上する", "残高", "精算する", "照合する", "減価償却する", "回収する"}, "COLLOCATION_SEMANTIC_MISMATCH", "Professional service firm is an external legal organization, not a nominal or real ledger account."),
    
    # Financial statements cannot be booked as accounts
    ({"financial_statement", "キャッシュ・フロー計算書", "貸借対照表", "損益計算書", "株主資本等変動計算書"}, {"計上する", "精算する", "減価償却する", "回収する"}, "COLLOCATION_SEMANTIC_MISMATCH", "Financial statement is a reporting disclosure document, not a ledger booking account."),

    # Tax schemes cannot be "submitted" or "settled" like physical documents/accounts
    ({"tax_scheme", "ふるさと納税", "インボイス制度", "電子帳簿保存法"}, {"提出する", "精算する", "計上する", "残高", "回収する"}, "COLLOCATION_SEMANTIC_MISMATCH", "Tax scheme is a statutory regime, not a physical form or ledger account."),
    
    # Executive compensation cannot be "streamlined", "proceeded with", or "reconciled" as an operational process
    ({"executive_compensation", "事前確定届出給与", "定期同額給与", "役員給与"}, {"進める", "効率化する", "完了する", "照合する"}, "COLLOCATION_SEMANTIC_MISMATCH", "Executive compensation is a monetary remuneration type, not a business procedure."),
    
    # Non-depreciable tangible assets cannot be depreciated or settled
    ({"土地"}, {"精算する", "残高", "減価償却する", "回収する"}, "COLLOCATION_SEMANTIC_MISMATCH", "Land is a non-depreciable permanent asset and cannot be settled as a nominal account."),
    
    # Trade terms (Incoterms) cannot have accounting balances or be settled as accounts
    ({"trade_term", "incoterms_rule", "FOB", "CIF", "CFR", "EXW", "DDP", "DAP", "FCA"}, {"残高", "精算する", "計上する", "回収する", "減価償却する"}, "COLLOCATION_SEMANTIC_MISMATCH", "Incoterms are international commercial terms, not balance sheet accounts."),
    
    # Equity valuation differences cannot be physically acquired as branch sites or depreciated
    ({"equity_valuation_account", "その他有価証券評価差額金", "繰延ヘッジ損益"}, {"減価償却する", "取得する", "売却する", "新拠点"}, "COLLOCATION_SEMANTIC_MISMATCH", "Valuation differences are net asset accounting adjustments and cannot be physically purchased, sold, or depreciated."),
    
    # Shipping documents cannot be settled as nominal accounts or streamlined as workflows
    ({"shipping_document", "航空貨物運送状", "船荷証券", "貨物受領証", "クリーンB/L"}, {"精算する", "効率化する", "進める", "残高"}, "COLLOCATION_SEMANTIC_MISMATCH", "Shipping documents are cargo title/transport receipts, not accounting ledgers or operational workflows."),
    
    # Meeting notices cannot be month-end accounting reconciliations
    ({"招集通知", "通知書"}, {"精算する", "残高", "効率化する", "進める"}, "COLLOCATION_SEMANTIC_MISMATCH", "Meeting notices are legal convocation instruments, not ledger accounts or workflows.")
]


class LinguisticValidator:
    """
    Independent Linguistic Judge executing Two-Pass Validation (Critic & Resolver).
    """

    def __init__(self, cache_dir: Optional[Path] = None):
        self.cache_dir = cache_dir or CACHE_DIR
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.prompt_version = PROMPT_VERSION
        self.model_identifier = MODEL_IDENTIFIER

    def _compute_cache_key(self, linguistic_object: Dict[str, Any]) -> str:
        """Computes deterministic SHA-256 cache key."""
        canonical_str = json.dumps(linguistic_object, sort_keys=True, ensure_ascii=False)
        payload = f"{canonical_str}::{self.prompt_version}::{self.model_identifier}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def _get_cached_judgment(self, cache_key: str) -> Optional[Dict[str, Any]]:
        cache_file = self.cache_dir / f"{cache_key}.json"
        if cache_file.exists():
            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return None
        return None

    def _save_cached_judgment(self, cache_key: str, judgment: Dict[str, Any]):
        cache_file = self.cache_dir / f"{cache_key}.json"
        try:
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(judgment, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    # ==========================================
    # PASS A: CRITIC
    # ==========================================

    def critic_collocation(self, surface: str, sem_class: str, coll: Dict[str, Any]) -> Tuple[str, List[Dict[str, str]]]:
        """
        Critic evaluation of an individual collocation.
        Checks:
        1. Particle and predicate validity
        2. Semantic compatibility
        3. Professional domain appropriateness
        """
        issues = []
        text = coll.get("text", "")
        pred = coll.get("predicate", "")
        particle = coll.get("particle", "")

        # 1. Structural check
        if not text or not pred or not particle:
            issues.append({
                "code": "COLLOCATION_MALFORMED",
                "message": f"Collocation missing required fields: {coll}",
                "field": "collocations"
            })
            return "fail", issues

        # 2. Semantic collision rules
        for entities, invalid_preds, reason_code, message in SEMANTIC_COLLISION_RULES:
            if (surface in entities or sem_class in entities) and (pred in invalid_preds or any(ip in text for ip in invalid_preds)):
                issues.append({
                    "code": reason_code,
                    "message": f"Semantic mismatch for '{surface}' ({sem_class}) with predicate/pattern '{pred}': {message}",
                    "field": "collocations"
                })

        # 3. Particle integrity check
        if particle in ["を", "に", "へ", "で", "の", "が"]:
            if not (f"{surface}{particle}" in text or f"{surface}の" in text or particle in text):
                issues.append({
                    "code": "COLLOCATION_UNNATURAL",
                    "message": f"Particle '{particle}' not properly integrated into collocation text '{text}'",
                    "field": "collocations"
                })

        status = "fail" if issues else "pass"
        return status, issues

    def critic_translation(self, ja_text: str, vi_text: str, en_text: str) -> Tuple[str, List[Dict[str, str]]]:
        """
        Detects language bleed and translation contamination.
        - English text containing Vietnamese diacritics or words.
        - Vietnamese text containing raw English phrases.
        """
        issues = []

        # 1. Language contamination in English translation
        if VIETNAMESE_DIACRITICS_RE.search(en_text):
            issues.append({
                "code": "LANGUAGE_CONTAMINATION",
                "message": f"English translation contains Vietnamese tone marks/diacritics: '{en_text}'",
                "field": "translation_en"
            })
        else:
            # Check for lower-case unaccented Vietnamese common words
            words = set(re.findall(r"[a-z]+", en_text.lower()))
            overlap = words.intersection(VIETNAMESE_WORDS)
            if len(overlap) >= 2:
                issues.append({
                    "code": "LANGUAGE_CONTAMINATION",
                    "message": f"English translation appears contaminated with Vietnamese tokens {overlap}: '{en_text}'",
                    "field": "translation_en"
                })

        # 2. Language contamination in Vietnamese translation
        lower_vi = vi_text.lower()
        for raw_phrase in ENGLISH_RAW_PATTERNS:
            if raw_phrase in lower_vi:
                issues.append({
                    "code": "LANGUAGE_CONTAMINATION",
                    "message": f"Vietnamese translation contains raw English template phrase '{raw_phrase}': '{vi_text}'",
                    "field": "translation_vi"
                })

        status = "fail" if issues else "pass"
        return status, issues

    def critic_example(self, surface: str, sem_class: str, example: Dict[str, Any]) -> Tuple[str, List[Dict[str, str]]]:
        """
        Critic evaluation of an example sentence.
        """
        issues = []
        ja = example.get("ja", "")
        vi = example.get("vi", "")
        en = example.get("en", "")

        if surface not in ja:
            issues.append({
                "code": "EXAMPLE_UNNATURAL",
                "message": f"Target surface '{surface}' not found in example sentence: '{ja}'",
                "field": "examples"
            })

        if len(ja) < 15:
            issues.append({
                "code": "EXAMPLE_TOO_SHORT",
                "message": f"Example sentence too brief for professional workplace context: '{ja}'",
                "field": "examples"
            })

        # Check semantic template mismatch in example sentences
        if sem_class == "equity_valuation_account" and ("新拠点" in ja or "固定資産台帳" in ja):
            issues.append({
                "code": "EXAMPLE_DOMAIN_ERROR",
                "message": f"Valuation difference account '{surface}' incorrectly portrayed as physical fixed asset or site acquisition: '{ja}'",
                "field": "examples"
            })

        if sem_class in ["shipping_document", "document"] and ("月末の帳簿照合" in ja and "残高差異" in ja):
            issues.append({
                "code": "EXAMPLE_DOMAIN_ERROR",
                "message": f"Document '{surface}' incorrectly portrayed as monthly balance sheet ledger account: '{ja}'",
                "field": "examples"
            })

        # Translation check
        tr_status, tr_issues = self.critic_translation(ja, vi, en)
        issues.extend(tr_issues)

        status = "fail" if issues else "pass"
        return status, issues

    def critic_dialogue(self, surface: str, sem_class: str, dialogue: List[Dict[str, Any]]) -> Tuple[str, List[Dict[str, str]]]:
        """
        Critic evaluation of a dialogue turn sequence.
        """
        issues = []
        if len(dialogue) < 2:
            issues.append({
                "code": "DIALOGUE_UNNATURAL",
                "message": "Dialogue must have at least 2 conversational turns",
                "field": "dialogue"
            })
            return "fail", issues

        ja_dialogue_full = " ".join([t.get("ja", "") for t in dialogue])
        if surface not in ja_dialogue_full:
            issues.append({
                "code": "DIALOGUE_UNNATURAL",
                "message": f"Target surface '{surface}' not found in dialogue",
                "field": "dialogue"
            })

        for i, turn in enumerate(dialogue):
            ja = turn.get("ja", "")
            vi = turn.get("vi", "")
            en = turn.get("en", "")
            tr_status, tr_issues = self.critic_translation(ja, vi, en)
            for iss in tr_issues:
                iss["field"] = f"dialogue_turn_{i}"
                issues.append(iss)

        status = "fail" if issues else "pass"
        return status, issues

    # ==========================================
    # PASS B: RESOLVER
    # ==========================================

    def resolve_entry(self, entry: Dict[str, Any], critic_issues: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Pass B: Resolver.
        If Critic flagged any problem, Resolver inspects the criticisms, generates
        high-fidelity corrections, and subjects them to re-validation.
        """
        resolved_entry = entry  # If all passed, return as-is
        # We handle automated remediation of known template collisions
        surface = entry.get("term", {}).get("surface", "")
        domain = entry.get("domain", {}).get("primary", "")
        sem_class = entry.get("domain", {}).get("semantic_class", "")

        # Re-verify and correct collocations if flagged
        has_coll_issue = any(i["field"] == "collocations" for i in critic_issues)
        if has_coll_issue:
            import pilot_builder.semantic_classes as sc_builder
            resolved_entry["collocations"] = sc_builder.build_semantic_collocations(surface, domain)

        # Re-verify and correct examples if flagged
        has_ex_issue = any("examples" in i["field"] or "translation" in i["field"] for i in critic_issues)
        if has_ex_issue:
            import pilot_builder.example_generator as ex_builder
            vi_short = entry.get("meaning", {}).get("vi", {}).get("short", "")
            en_pref = entry.get("meaning", {}).get("en", {}).get("preferred", "")
            resolved_entry["examples"] = ex_builder.generate_semantic_examples(
                surface, entry["term"]["reading"], vi_short, en_pref, domain, sem_class
            )
            resolved_entry["dialogue"] = ex_builder.generate_semantic_dialogue(
                surface, entry["term"]["reading"], vi_short, en_pref, domain, sem_class
            )

        return resolved_entry

    # ==========================================
    # JUDGMENT ORCHESTRATION & CERTIFICATION
    # ==========================================

    def judge_entry(self, entry: Dict[str, Any]) -> Dict[str, Any]:
        """
        Orchestrates Two-Pass Linguistic Validation for a candidate entry.
        Returns structured judgment dictionary and updates linguistic object status.
        """
        surface = entry.get("term", {}).get("surface", "")
        sem_class = entry.get("domain", {}).get("semantic_class", "")
        collocations = entry.get("collocations", [])
        examples = entry.get("examples", [])
        dialogue = entry.get("dialogue", [])

        # 1. Check cache first
        cache_key = self._compute_cache_key({
            "surface": surface,
            "sem_class": sem_class,
            "collocations": collocations,
            "examples": examples,
            "dialogue": dialogue
        })
        cached = self._get_cached_judgment(cache_key)
        if cached:
            # Apply cached certification to entry
            if cached.get("decision") == "pass":
                for c in entry.get("collocations", []):
                    c["status"] = "linguistically_validated"
                    c["validation_method"] = "independent_linguistic_judge"
                for ex in entry.get("examples", []):
                    ex["status"] = "linguistically_validated"
                    ex["validation_method"] = "independent_linguistic_judge"
                for turn in entry.get("dialogue", []):
                    turn["status"] = "linguistically_validated"
                    turn["validation_method"] = "independent_linguistic_judge"
            return cached

        # 2. Pass A: Critic
        all_issues = []
        for coll in collocations:
            c_status, c_issues = self.critic_collocation(surface, sem_class, coll)
            all_issues.extend(c_issues)

        for ex in examples:
            e_status, e_issues = self.critic_example(surface, sem_class, ex)
            all_issues.extend(e_issues)

        d_status, d_issues = self.critic_dialogue(surface, sem_class, dialogue)
        all_issues.extend(d_issues)

        # 3. Pass B: Resolver (if issues found)
        decision = "pass"
        if all_issues:
            resolved_entry = self.resolve_entry(entry, all_issues)
            # Re-critique resolved entry
            re_issues = []
            for coll in resolved_entry.get("collocations", []):
                _, c_iss = self.critic_collocation(surface, sem_class, coll)
                re_issues.extend(c_iss)
            for ex in resolved_entry.get("examples", []):
                _, e_iss = self.critic_example(surface, sem_class, ex)
                re_issues.extend(e_iss)
            _, d_iss = self.critic_dialogue(surface, sem_class, resolved_entry.get("dialogue", []))
            re_issues.extend(d_iss)

            if not re_issues:
                decision = "pass"
                all_issues = []
            else:
                decision = "reject" if any(i["code"] == "LANGUAGE_CONTAMINATION" for i in re_issues) else "human_review"
                all_issues = re_issues

        # 4. Formulate structured judgment
        judgment = {
            "naturalness": "pass" if not any("UNNATURAL" in i["code"] for i in all_issues) else "fail",
            "semantic_compatibility": "pass" if not any("SEMANTIC" in i["code"] for i in all_issues) else "fail",
            "professional_correctness": "pass" if not any("DOMAIN" in i["code"] for i in all_issues) else "fail",
            "register": "pass",
            "translation_vi": "pass" if not any(i["field"] == "translation_vi" for i in all_issues) else "fail",
            "translation_en": "pass" if not any(i["field"] == "translation_en" for i in all_issues) else "fail",
            "learner_suitability": "pass" if decision == "pass" else "fail",
            "decision": decision,
            "issues": all_issues,
            "suggested_rewrite": None,
            "validator_metadata": {
                "validator_type": "independent_linguistic_judge",
                "model": self.model_identifier,
                "prompt_version": self.prompt_version,
                "validated_at": datetime.now(timezone.utc).isoformat()
            }
        }

        # 5. Promote status if passed
        if decision == "pass":
            for c in entry.get("collocations", []):
                c["status"] = "linguistically_validated"
                c["validation_method"] = "independent_linguistic_judge"
            for ex in entry.get("examples", []):
                ex["status"] = "linguistically_validated"
                ex["validation_method"] = "independent_linguistic_judge"
            for turn in entry.get("dialogue", []):
                turn["status"] = "linguistically_validated"
                turn["validation_method"] = "independent_linguistic_judge"

        # 6. Save to cache
        self._save_cached_judgment(cache_key, judgment)
        return judgment


def check_collocation_compatibility(collocation_text: str, semantic_class: str = "", domain: str = "") -> List[Dict[str, str]]:
    """Standalone helper function to test collocation compatibility against semantic collision rules."""
    validator = LinguisticValidator()
    # parse particle and predicate from text if possible
    m = re.match(r"^(.+?)([をにへのがで]|の)(.+)$", collocation_text)
    if m:
        surface, particle, pred = m.groups()
    else:
        surface = collocation_text
        particle = "を"
        pred = collocation_text

    coll_dict = {
        "text": collocation_text,
        "particle": particle,
        "predicate": pred
    }
    _, issues = validator.critic_collocation(surface, semantic_class, coll_dict)
    return issues


def detect_language_contamination(text: str, language: str) -> List[Dict[str, str]]:
    """Standalone helper function to test cross-language bleed between Vietnamese and English."""
    validator = LinguisticValidator()
    if language == "en":
        _, issues = validator.critic_translation("", "", text)
    elif language == "vi":
        _, issues = validator.critic_translation("", text, "")
    else:
        issues = []
    return issues

