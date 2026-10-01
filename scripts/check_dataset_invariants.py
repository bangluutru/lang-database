#!/usr/bin/env python3
"""
scripts/check_dataset_invariants.py
Machine-enforced dataset invariants for the Golden Pilot v1.

Usage:
  python scripts/check_dataset_invariants.py               # production + golden pilot
  python scripts/check_dataset_invariants.py --prod-only   # production only
  python scripts/check_dataset_invariants.py --golden-only # golden pilot only

Exits with code 0 if all invariants hold, 1 otherwise.
These invariants are permanently machine-enforced and run at CI/CD time.
"""

import json
import hashlib
import sys
import argparse
from pathlib import Path
from typing import List, Dict, Tuple

BASE_DIR = Path(__file__).resolve().parent.parent

PROD_FILE       = BASE_DIR / "data" / "production" / "vocabulary.jsonl"
GOLDEN_VOCAB    = BASE_DIR / "data" / "releases" / "golden-pilot-v1" / "vocabulary.jsonl"
GOLDEN_MANIFEST = BASE_DIR / "data" / "releases" / "golden-pilot-v1" / "dataset_manifest.json"
GOLDEN_CHECKSUMS= BASE_DIR / "data" / "releases" / "golden-pilot-v1" / "checksums.sha256"
CANDIDATES_FILE = BASE_DIR / "data" / "enriched" / "learning_candidates.jsonl"
REJECTED_FILE   = BASE_DIR / "staging" / "review_queue" / "rejected.jsonl"
NEEDS_REVIEW_FILE = BASE_DIR / "staging" / "review_queue" / "needs_review.jsonl"
PERM_Q_FILE     = BASE_DIR / "staging" / "review_queue" / "permanent_quarantine.jsonl"

VALID_RELEASE_VERSIONS = {"v1.1.0a-prod", "v1.1.0b-prod", "v1.1.0c-prod"}
FORBIDDEN_MODEL_IDS    = {"independent-linguistic-judge-2.0"}
SUPPRESSIONS_FILE      = BASE_DIR / "config" / "known_invariant_suppressions.json"

failures: List[str] = []
warnings: List[str] = []   # Known-backlog violations — tracked but don't fail CI


def _load_suppressions() -> Dict:
    """Load known pre-existing violations that are tracked for Phase 1.2 remediation.
    New violations not in the suppression list will still fail CI.
    """
    if not SUPPRESSIONS_FILE.exists():
        return {}
    with open(SUPPRESSIONS_FILE, encoding="utf-8") as f:
        return json.load(f)

SUPPRESSIONS = _load_suppressions()
_INV9_SUPPRESSED  = set(SUPPRESSIONS.get("inv9_template_injection_backlog", []))
_INV10_SUPPRESSED = set(SUPPRESSIONS.get("inv10_term_not_referenced_backlog", []))


def check(condition: bool, message: str) -> bool:
    """Assert invariant; if False, record failure."""
    if not condition:
        failures.append(message)
    return condition


def load_jsonl(path: Path) -> List[Dict]:
    if not path.exists():
        return []
    records = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))
    return records


def compute_sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def compute_canonical_dataset_hash(records: List[Dict]) -> str:
    sorted_records = sorted(records, key=lambda r: r.get("id", ""))
    h = hashlib.sha256()
    for r in sorted_records:
        canonical = {k: v for k, v in r.items() if k not in ("status",)}
        line = json.dumps(canonical, sort_keys=True, ensure_ascii=False) + "\n"
        h.update(line.encode("utf-8"))
    return h.hexdigest()


# ── Invariant groups ──────────────────────────────────────────────────────────

def invariants_pilot_freeze_equation() -> None:
    """INV-1: 800 = production + needs_review + permanent_quarantine."""
    prod = load_jsonl(PROD_FILE)
    review = load_jsonl(NEEDS_REVIEW_FILE)
    perm_q = load_jsonl(PERM_Q_FILE)
    total = len(prod) + len(review) + len(perm_q)
    check(
        total == 800,
        f"INV-1 FAIL: Pilot freeze equation: "
        f"{len(prod)} + {len(review)} + {len(perm_q)} = {total} ≠ 800"
    )
    print(f"  INV-1: prod={len(prod)} review={len(review)} perm_q={len(perm_q)} total={total}")


def invariants_zero_generated_in_production() -> None:
    """INV-2: No learning object in production may have status 'generated'."""
    prod = load_jsonl(PROD_FILE)
    violations = []
    for r in prod:
        for c in r.get("collocations", []):
            if c.get("status") == "generated":
                violations.append(f"{r['id']}:collocation:{c.get('text', '')[:40]}")
        for ex in r.get("examples", []):
            if ex.get("status") == "generated":
                violations.append(f"{r['id']}:example:{ex.get('ja', '')[:40]}")
        for turn in r.get("dialogue", []):
            if turn.get("status") == "generated":
                violations.append(f"{r['id']}:dialogue:{turn.get('ja', '')[:40]}")
    check(
        not violations,
        f"INV-2 FAIL: Generated learning objects in production: {violations[:5]}"
    )
    print(f"  INV-2: zero generated status — violations={len(violations)}")


def invariants_model_provenance() -> None:
    """INV-3: All production records must have truthful Gemini model metadata."""
    prod = load_jsonl(PROD_FILE)
    violations = []
    for r in prod:
        lv = r.get("linguistic_validation", {})
        judge = lv.get("linguistic_judge", {})
        model = judge.get("model", "")

        if model in FORBIDDEN_MODEL_IDS:
            violations.append(f"{r['id']}: forbidden model '{model}'")
            continue
        if not ("gemini" in model.lower()):
            violations.append(f"{r['id']}: non-Gemini model '{model}'")
            continue
        input_hash = judge.get("input_hash", "")
        if len(input_hash) != 64:
            violations.append(f"{r['id']}: invalid SHA-256 hash len={len(input_hash)}")

    check(
        not violations,
        f"INV-3 FAIL: Model provenance violations: {violations[:5]}"
    )
    print(f"  INV-3: model provenance — violations={len(violations)}")


def invariants_no_duplicate_ids() -> None:
    """INV-4: Production must have no duplicate IDs."""
    prod = load_jsonl(PROD_FILE)
    ids = [r.get("id") for r in prod]
    seen = set()
    dups = set()
    for i in ids:
        if i in seen:
            dups.add(i)
        seen.add(i)
    check(not dups, f"INV-4 FAIL: Duplicate IDs in production: {dups}")
    print(f"  INV-4: no duplicate IDs — duplicates={len(dups)}")


def invariants_release_versions() -> None:
    """INV-5: All release versions must be known."""
    prod = load_jsonl(PROD_FILE)
    bad = []
    for r in prod:
        rv = r.get("lineage", {}).get("release_version", "")
        if rv not in VALID_RELEASE_VERSIONS:
            bad.append(f"{r['id']}: '{rv}'")
    check(not bad, f"INV-5 FAIL: Unknown release versions: {bad[:5]}")
    print(f"  INV-5: release versions — violations={len(bad)}")


def invariants_jlpt_decoupled() -> None:
    """INV-6: All production records must have jlpt_level=null."""
    prod = load_jsonl(PROD_FILE)
    bad = []
    for r in prod:
        gj = r.get("general_japanese", {})
        if gj.get("jlpt_level") is not None:
            bad.append(r["id"])
    check(not bad, f"INV-6 FAIL: Records with non-null jlpt_level: {bad[:5]}")
    print(f"  INV-6: JLPT decoupled — violations={len(bad)}")


def invariants_permanent_quarantine_have_reason() -> None:
    """INV-7: All permanently quarantined records must have an explicit reason."""
    perm_q = load_jsonl(PERM_Q_FILE)
    bad = []
    for r in perm_q:
        has_reason = r.get("_quarantine_reason") or r.get("_quarantine_categories")
        has_status = r.get("status") == "permanent_quarantine"
        if not has_reason or not has_status:
            bad.append(r.get("id", "unknown"))
    check(not bad, f"INV-7 FAIL: Permanent quarantine records missing reason/status: {bad[:5]}")
    print(f"  INV-7: permanent quarantine metadata — violations={len(bad)}")


def invariants_golden_pilot_hash() -> None:
    """INV-8: Golden Pilot SHA-256 must match manifest."""
    if not GOLDEN_VOCAB.exists() or not GOLDEN_MANIFEST.exists():
        print("  INV-8: Golden Pilot not yet frozen — SKIP")
        return

    with open(GOLDEN_MANIFEST, encoding="utf-8") as f:
        manifest = json.load(f)

    expected_file_hash = manifest.get("vocabulary_file_sha256", "")
    computed_file_hash = compute_sha256_file(GOLDEN_VOCAB)
    check(
        computed_file_hash == expected_file_hash,
        f"INV-8 FAIL: Golden Pilot file SHA-256 mismatch:\n"
        f"  computed: {computed_file_hash}\n"
        f"  expected: {expected_file_hash}"
    )

    golden_entries = load_jsonl(GOLDEN_VOCAB)
    expected_canonical = manifest.get("dataset_hash", "")
    computed_canonical = compute_canonical_dataset_hash(golden_entries)
    check(
        computed_canonical == expected_canonical,
        f"INV-8b FAIL: Canonical dataset hash mismatch:\n"
        f"  computed: {computed_canonical}\n"
        f"  expected: {expected_canonical}"
    )
    print(f"  INV-8: Golden Pilot hash — file_match={computed_file_hash==expected_file_hash} canonical_match={computed_canonical==expected_canonical}")


def invariants_no_accounting_templates_on_business() -> None:
    """INV-9: No accounting ledger template examples in business/trade records.
    
    Exemptions:
    - sem_class=account: accounting-adjacent terms that legitimately reference ledgers
      (e.g., 手付金 — a deposit that appears on balance sheets)
    - sem_class containing 'account': similarly accounting-adjacent
    """
    prod = load_jsonl(PROD_FILE)
    accounting_markers = ["帳簿照合", "補助元帳", "証憑書類と", "仕訳内容", "計上内容や残高"]
    non_accounting = {"business", "trade"}
    # Semantic classes that legitimately appear in ledger/accounting contexts
    accounting_adjacent_classes = {"account", "receivable_account", "payable_account",
                                    "provision_account", "tax_account", "equity_valuation_account"}
    bad = []
    for r in prod:
        domain = r.get("domain", {}).get("primary", "")
        if domain not in non_accounting:
            continue
        sem_class = r.get("domain", {}).get("semantic_class", "")
        if sem_class in accounting_adjacent_classes or "account" in sem_class:
            continue  # Legitimately accounting-adjacent; ledger references are expected
        for ex in r.get("examples", []):
            ja = ex.get("ja", "")
            for marker in accounting_markers:
                if marker in ja:
                    bad.append(f"{r['id']}:{r['term']['surface']}:{marker}")
                    break
    # Partition: new violations fail CI; known backlog violations are tracked as warnings
    new_bad = [v for v in bad if v.split(':')[0] not in _INV9_SUPPRESSED]
    known_bad = [v for v in bad if v.split(':')[0] in _INV9_SUPPRESSED]
    if known_bad:
        warnings.append(f"INV-9 BACKLOG ({len(known_bad)} records pending Phase 1.2 remediation): {known_bad[:3]}")
    check(not new_bad, f"INV-9 FAIL: NEW accounting template injection in business/trade: {new_bad[:5]}")
    print(f"  INV-9: no accounting template injection — new={len(new_bad)} backlog={len(known_bad)}")


def invariants_examples_reference_term() -> None:
    """INV-10: At least one example or one dialogue turn must reference the target term.
    
    Also accepts:
    - Known stable abbreviations (RCEP for 地域的な包括的経済連携協定, etc.)
    - Terms where the surface is split across a hyphen or space in the example
    """
    prod = load_jsonl(PROD_FILE)
    # Known stable abbreviation map: surface -> accepted abbreviation
    ABBREVIATIONS: Dict[str, str] = {
        "地域的な包括的経済連携協定": "RCEP",
        "包括的・先進的環太平洋パートナーシップ協定": "CPTPP",
        "環太平洋パートナーシップに関する包括的及び先進的な協定": "CPTPP",
    }
    bad = []
    for r in prod:
        surface = r["term"]["surface"]
        examples = r.get("examples", [])
        dialogue = r.get("dialogue", [])
        abbrev = ABBREVIATIONS.get(surface, "")
        
        def has_ref(text: str) -> bool:
            if surface in text:
                return True
            if abbrev and abbrev in text:
                return True
            # Also check reading (for phonetic representation)
            reading = r.get("term", {}).get("reading", "")
            if reading and reading in text:
                return True
            return False
        
        any_ex = any(has_ref(ex.get("ja", "")) for ex in examples)
        any_dlg = any(has_ref(turn.get("ja", "")) for turn in dialogue)
        if not (any_ex or any_dlg):
            bad.append(f"{r['id']}:{surface}")
    # Partition: new violations fail CI; known backlog violations are tracked as warnings
    new_bad = [v for v in bad if v.split(':')[0] not in _INV10_SUPPRESSED]
    known_bad = [v for v in bad if v.split(':')[0] in _INV10_SUPPRESSED]
    if known_bad:
        warnings.append(f"INV-10 BACKLOG ({len(known_bad)} records pending Phase 1.2 remediation): {known_bad}")
    check(not new_bad, f"INV-10 FAIL: NEW term not referenced in examples or dialogue: {new_bad[:5]}")
    print(f"  INV-10: term reference in content — new={len(new_bad)} backlog={len(known_bad)}")


def invariants_governance_predicates_not_on_sales() -> None:
    """INV-11: Corporate governance predicates must not appear in non-governance collocations.
    
    Exemptions:
    - Governance-concept semantic classes legitimately use these predicates
      (取締役会, 定時株主総会, 臨時株主総会 are governance entities that resolve, convene, etc.)
    """
    prod = load_jsonl(PROD_FILE)
    governance_preds = ["決議する", "招集する"]
    # Note: '届出書を提出する' is NOT a governance predicate — it is a statutory filing
    # predicate that legitimately applies to compensation/equity terms (e.g. ストックオプション).
    governance_exempt_classes = {
        "financial_statement", "statutory_document", "professional_service_firm",
        "account", "provision_account", "tax_account", "tax_obligation",
        # Governance-concept classes — their own predicates are legitimate
        "organization", "corporate_meeting", "board_meeting", "corporate_governance",
        "corporate_body", "shareholder_meeting", "statutory_meeting",
        # Compensation/equity classes — they legitimately use 決議する (board approval)
        "executive_compensation", "equity_compensation",
    }
    non_governance_domains = {"business", "trade"}
    bad = []
    for r in prod:
        domain = r.get("domain", {}).get("primary", "")
        if domain not in non_governance_domains:
            continue
        sem_class = r.get("domain", {}).get("semantic_class", "")
        if sem_class in governance_exempt_classes:
            continue
        # Also exempt terms whose surface IS a governance body (the collocation describes themselves)
        surface = r["term"]["surface"]
        governance_surfaces = {"取締役会", "定時株主総会", "臨時株主総会", "監査役会", "指名委員会", "報酬委員会"}
        if surface in governance_surfaces:
            continue
        for c in r.get("collocations", []):
            text = c.get("text", "")
            for gp in governance_preds:
                if gp in text:
                    bad.append(f"{r['id']}:{surface}:{gp} in '{text}'")
    check(not bad, f"INV-11 FAIL: Governance predicates in non-governance collocations: {bad[:5]}")
    print(f"  INV-11: no governance predicate injection — violations={len(bad)}")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Check dataset invariants")
    parser.add_argument("--prod-only", action="store_true")
    parser.add_argument("--golden-only", action="store_true")
    args = parser.parse_args()

    print("=" * 60)
    print("DATASET INVARIANT CHECK")
    print("=" * 60)

    if not args.golden_only:
        print("\n[Production Invariants]")
        invariants_pilot_freeze_equation()
        invariants_zero_generated_in_production()
        invariants_model_provenance()
        invariants_no_duplicate_ids()
        invariants_release_versions()
        invariants_jlpt_decoupled()
        invariants_permanent_quarantine_have_reason()
        invariants_no_accounting_templates_on_business()
        invariants_examples_reference_term()
        invariants_governance_predicates_not_on_sales()

    if not args.prod_only:
        print("\n[Golden Pilot Invariants]")
        invariants_golden_pilot_hash()

    print("\n" + "=" * 60)
    if warnings:
        print(f"BACKLOG WARNINGS: {len(warnings)} (tracked for Phase 1.2 remediation)")
        for w in warnings:
            print(f"  ⚠️  {w}")
        print()
    if failures:
        print(f"INVARIANT VIOLATIONS: {len(failures)}")
        for fmsg in failures:
            print(f"  ❌ {fmsg}")
        print("=" * 60)
        sys.exit(1)
    else:
        suffix = " (with backlog warnings)" if warnings else ""
        print(f"ALL INVARIANTS PASS ✓{suffix}")
        print("=" * 60)
        sys.exit(0)


if __name__ == "__main__":
    main()
