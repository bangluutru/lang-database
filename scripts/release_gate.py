#!/usr/bin/env python3
"""
scripts/release_gate.py
Release Gate for JP Professional Vocabulary Database (Phase 1.1).

ARCHITECTURAL PRINCIPLE:
Strict Release Gate separating candidate validation from production release.
Routes records based on independent validation decisions:
  - 'pass'         -> data/production/vocabulary.jsonl & data/production/jp_professional_pilot.jsonl
  - 'needs_review' -> staging/review_queue/needs_review.jsonl
  - 'rejected'     -> staging/review_queue/rejected.jsonl

Synchronizes relationship graph and expressions, and updates the SQLite FTS5 database.
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime, timezone

BASE_DIR = Path(__file__).resolve().parent.parent
VALIDATED_FILE = BASE_DIR / "data" / "validated" / "validated_candidates.jsonl"
EXPR_CANDIDATES = BASE_DIR / "data" / "enriched" / "learning_expressions_candidates.jsonl"
REL_CANDIDATES = BASE_DIR / "data" / "enriched" / "learning_relationships_candidates.jsonl"

PROD_DIR = BASE_DIR / "data" / "production"
PROD_DIR.mkdir(parents=True, exist_ok=True)
STAGING_QUEUE_DIR = BASE_DIR / "staging" / "review_queue"
STAGING_QUEUE_DIR.mkdir(parents=True, exist_ok=True)

VOCAB_PROD = PROD_DIR / "vocabulary.jsonl"
PILOT_PROD = PROD_DIR / "jp_professional_pilot.jsonl"
EXPR_PROD = PROD_DIR / "expressions.jsonl"
REL_PROD = PROD_DIR / "relationships.jsonl"

NEEDS_REVIEW_FILE = STAGING_QUEUE_DIR / "needs_review.jsonl"
REJECTED_FILE = STAGING_QUEUE_DIR / "rejected.jsonl"

RELEASE_VERSION = "v1.1.0-prod"

def run_release_gate():
    print("[*] Initiating Phase 1.1 Production Release Gate...")
    if not VALIDATED_FILE.exists():
        print(f"[!] Error: Validated candidates file not found: {VALIDATED_FILE}")
        sys.exit(1)

    production_records = []
    needs_review_records = []
    rejected_records = []
    released_ids = set()

    with open(VALIDATED_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            entry = json.loads(line)
            val_rec = entry.get("lineage", {}).get("validation_record", {})
            decision = val_rec.get("release_decision", "needs_review")

            if decision == "pass":
                entry["status"] = "production"
                entry["lineage"]["release_version"] = RELEASE_VERSION
                production_records.append(entry)
                released_ids.add(entry["id"])
            elif decision == "needs_review":
                entry["status"] = "needs_review"
                needs_review_records.append(entry)
            else:
                entry["status"] = "rejected"
                rejected_records.append(entry)

    # 1. Write production datasets
    with open(VOCAB_PROD, "w", encoding="utf-8") as f:
        for entry in production_records:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    print(f"[+] Released {len(production_records)} records to {VOCAB_PROD}")

    with open(PILOT_PROD, "w", encoding="utf-8") as f:
        for entry in production_records:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    print(f"[+] Released {len(production_records)} records to {PILOT_PROD}")

    # 2. Write staging review queues
    with open(NEEDS_REVIEW_FILE, "w", encoding="utf-8") as f:
        for entry in needs_review_records:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    print(f"[+] Quarantined {len(needs_review_records)} records to {NEEDS_REVIEW_FILE}")

    with open(REJECTED_FILE, "w", encoding="utf-8") as f:
        for entry in rejected_records:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    print(f"[+] Quarantined {len(rejected_records)} rejected records to {REJECTED_FILE}")

    # 3. Synchronize expressions
    if EXPR_CANDIDATES.exists():
        with open(EXPR_CANDIDATES, "r", encoding="utf-8") as fin, open(EXPR_PROD, "w", encoding="utf-8") as fout:
            count = 0
            for line in fin:
                if line.strip():
                    item = json.loads(line)
                    item["status"] = "production"
                    fout.write(json.dumps(item, ensure_ascii=False) + "\n")
                    count += 1
        print(f"[+] Released {count} workplace expressions to {EXPR_PROD}")

    # 4. Synchronize relationship graph (only edges whose source_id is released)
    if REL_CANDIDATES.exists():
        rel_count = 0
        with open(REL_CANDIDATES, "r", encoding="utf-8") as fin, open(REL_PROD, "w", encoding="utf-8") as fout:
            for line in fin:
                if line.strip():
                    edge = json.loads(line)
                    if edge["source_id"] in released_ids:
                        fout.write(json.dumps(edge, ensure_ascii=False) + "\n")
                        rel_count += 1
        print(f"[+] Released {rel_count} active graph edges to {REL_PROD}")

    # 5. Re-export SQLite database
    print("[*] Rebuilding SQLite query layer with released production dataset...")
    export_script = BASE_DIR / "scripts" / "export_sqlite.py"
    if export_script.exists():
        res = subprocess.run([sys.executable, str(export_script)], capture_output=True, text=True)
        if res.returncode == 0:
            print("[+] SQLite database successfully rebuilt with FTS5 search index.")
        else:
            print(f"[!] SQLite export warning:\n{res.stderr}")

    print("\n" + "="*50)
    print("RELEASE GATE SUMMARY:")
    print(f"  Production Released: {len(production_records)}")
    print(f"  Needs Review:        {len(needs_review_records)}")
    print(f"  Rejected:            {len(rejected_records)}")
    print("="*50)

if __name__ == "__main__":
    run_release_gate()
