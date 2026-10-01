#!/usr/bin/env python3
"""
scripts/audit_semantic_classes.py
Runs the True Semantic Class Audit across all 800 records using Gemini 3.8 Flash.
Identifies all concept-level misclassifications and saves results to reports/semantic_audit_results.json.
"""

import sys
import json
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR / "scripts"))

from llm_judge import TrueLinguisticJudge

PROD_FILE = BASE_DIR / "data" / "production" / "vocabulary.jsonl"
OUT_FILE = BASE_DIR / "reports" / "semantic_audit_results.json"
OUT_FILE.parent.mkdir(parents=True, exist_ok=True)


def main():
    print("[*] Initializing Semantic Class Audit with True Linguistic Judge (Gemini 3.8 Flash)...")
    judge = TrueLinguisticJudge()

    with open(PROD_FILE, "r", encoding="utf-8") as f:
        entries = [json.loads(line) for line in f if line.strip()]

    print(f"[*] Loaded {len(entries)} production records for semantic audit.")

    results = []
    incorrect_count = 0
    start_time = time.time()

    def process_entry(entry):
        try:
            res = judge.audit_semantic_class(entry)
            return entry["id"], res, None
        except Exception as e:
            return entry["id"], None, str(e)

    # Use 10 concurrent workers
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(process_entry, e): e for e in entries}
        completed = 0
        for fut in as_completed(futures):
            entry_id, audit_res, err = fut.result()
            completed += 1
            if err:
                print(f"[!] Error on {entry_id}: {err}")
                results.append({"entry_id": entry_id, "error": err})
            else:
                results.append({"entry_id": entry_id, "audit": audit_res})
                if audit_res.get("decision") == "incorrect":
                    incorrect_count += 1
                    term = audit_res.get("term")
                    cur = audit_res.get("current_class")
                    sug = audit_res.get("suggested_semantic_class")
                    print(f"  [MISMATCH #{incorrect_count}] {entry_id} ({term}): {cur} -> {sug}")

            if completed % 50 == 0 or completed == len(entries):
                elapsed = time.time() - start_time
                print(f"[*] Progress: {completed}/{len(entries)} ({completed/len(entries)*100:.1f}%) in {elapsed:.1f}s")

    # Sort deterministically by entry_id
    results.sort(key=lambda x: x["entry_id"])

    summary = {
        "audited_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "model": judge.model,
        "total_records": len(entries),
        "incorrect_records": incorrect_count,
        "correct_records": len(entries) - incorrect_count,
        "results": results
    }

    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    print(f"\n[+] Semantic Audit Completed: {incorrect_count} concept misclassifications discovered.")
    print(f"[+] Output written to {OUT_FILE}")


if __name__ == "__main__":
    main()
