#!/usr/bin/env python3
"""
scripts/run_adversarial_audit.py
Phase 1.1B Adversarial Sample Audit.

Executes a strict adversarial linguistic audit on a stratified sample across:
- 4 domains (accounting, tax, business, trade)
- 3 PRO tiers (PRO-A1, PRO-A2, PRO-A3)
Total: 36 records (3 per domain x tier cell).

Uses the strict adversarial prompt:
"Assume this content may contain subtle but plausible-sounding Japanese errors.
Find any expression you would hesitate to teach to a foreign professional."
"""

import sys
import json
from pathlib import Path
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from scripts.llm_judge import TrueLinguisticJudge

VALIDATED_FILE = BASE_DIR / "data" / "validated" / "validated_candidates.jsonl"
ADVERSARIAL_REPORT = BASE_DIR / "reports" / "adversarial_audit_results.json"


def select_stratified_sample(records: list, k_per_cell: int = 3) -> list:
    cells = defaultdict(list)
    for r in records:
        dom = r.get("domain", {}).get("primary")
        tier = r.get("tier") or r.get("professional_level", {}).get("tier")
        if dom and tier:
            cells[(dom, tier)].append(r)

    sample = []
    for (dom, tier), items in sorted(cells.items()):
        # Deterministic sort by id
        items.sort(key=lambda x: x["id"])
        selected = items[:k_per_cell]
        sample.extend(selected)
    return sample


def main():
    print("[*] Starting Phase 1.1B Adversarial Sample Audit...")
    if not VALIDATED_FILE.exists():
        print(f"[!] Error: {VALIDATED_FILE} not found.")
        sys.exit(1)

    records = []
    with open(VALIDATED_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))

    sample = select_stratified_sample(records, k_per_cell=3)
    print(f"[+] Selected {len(sample)} stratified sample records across 12 cells (4 domains x 3 PRO tiers).")

    judge = TrueLinguisticJudge()
    results = []

    print("[*] Executing adversarial audit with thread pool...")
    with ThreadPoolExecutor(max_workers=6) as executor:
        future_to_rec = {executor.submit(judge.adversarial_audit, rec): rec for rec in sample}
        for future in as_completed(future_to_rec):
            rec = future_to_rec[future]
            try:
                res = future.result()
                results.append({
                    "entry_id": rec["id"],
                    "term": rec["term"]["surface"],
                    "domain": rec.get("domain", {}).get("primary"),
                    "tier": rec.get("tier"),
                    "adversarial_audit": res
                })
                print(f"  [>] Audited {rec['id']} ({rec['term']['surface']}): {res.get('adversarial_decision')} (Grade: {res.get('pedagogical_grade')})")
            except Exception as e:
                print(f"[!] Error on {rec['id']}: {e}")

    results.sort(key=lambda x: x["entry_id"])

    clean_count = sum(1 for r in results if r["adversarial_audit"].get("adversarial_decision") == "clean")
    caution_count = sum(1 for r in results if r["adversarial_audit"].get("adversarial_decision") == "caution")
    reject_count = sum(1 for r in results if r["adversarial_audit"].get("adversarial_decision") == "reject")

    print("\n" + "=" * 50)
    print("ADVERSARIAL AUDIT SUMMARY")
    print("=" * 50)
    print(f"Sample Records Audited:     {len(results)}")
    print(f"Clean (Full Pass):          {clean_count}")
    print(f"Caution / Minor Nuance:     {caution_count}")
    print(f"Reject:                     {reject_count}")
    print("=" * 50)

    ADVERSARIAL_REPORT.parent.mkdir(parents=True, exist_ok=True)
    with open(ADVERSARIAL_REPORT, "w", encoding="utf-8") as f:
        json.dump({
            "sample_size": len(results),
            "clean_count": clean_count,
            "caution_count": caution_count,
            "reject_count": reject_count,
            "results": results
        }, f, ensure_ascii=False, indent=2)
    print(f"[+] Saved adversarial audit results to {ADVERSARIAL_REPORT}")


if __name__ == "__main__":
    main()
