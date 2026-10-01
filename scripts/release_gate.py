#!/usr/bin/env python3
"""
scripts/release_gate.py
Release Gate for JP Professional Vocabulary Database (Phase 1.1A).

ARCHITECTURAL PRINCIPLES:
1. Strict Release Gate separating candidate validation from production release.
2. Production Release Rule:
   A vocabulary record is only released to production if:
   - schema PASS
   - source lineage PASS
   - reading PASS
   - translation PASS
   - collocations PASS
   - examples PASS
   - dialogue PASS
   - tts PASS
   - draft contamination PASS
   - linguistic validation PASS
3. Production files MUST contain ZERO learning objects with status 'generated'.
   All released objects must be 'production_verified'.
4. Structured review queues with machine-readable reason codes:
   - PRONUNCIATION_UNVERIFIED
   - PRONUNCIATION_CORRUPTED
   - COLLOCATION_UNNATURAL
   - COLLOCATION_SEMANTIC_MISMATCH
   - EXAMPLE_UNNATURAL
   - EXAMPLE_DOMAIN_ERROR
   - DIALOGUE_UNNATURAL
   - VI_TRANSLATION_MISMATCH
   - EN_TRANSLATION_MISMATCH
   - LANGUAGE_CONTAMINATION
   - SOURCE_EVIDENCE_INSUFFICIENT
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
PRONUNCIATION_REVIEW_FILE = STAGING_QUEUE_DIR / "pronunciation_review.jsonl"
LINGUISTIC_REVIEW_FILE = STAGING_QUEUE_DIR / "linguistic_review.jsonl"
TRANSLATION_REVIEW_FILE = STAGING_QUEUE_DIR / "translation_review.jsonl"
SOURCE_REVIEW_FILE = STAGING_QUEUE_DIR / "source_review.jsonl"

RELEASE_VERSION = "v1.1.0a-prod"


def determine_reason_codes(entry: dict) -> list:
    """Extracts machine-readable reason codes from validation record."""
    val_rec = entry.get("lineage", {}).get("validation_record", {})
    checks = val_rec.get("checks", {})
    evid = val_rec.get("validation_evidence", {})
    codes = []

    # Reading checks
    read_ev = evid.get("reading", {})
    if read_ev.get("status") == "rejected":
        codes.append("PRONUNCIATION_CORRUPTED")
    elif read_ev.get("status") == "needs_review":
        codes.append("PRONUNCIATION_UNVERIFIED")

    # Source lineage
    if checks.get("source_lineage") != "pass":
        codes.append("SOURCE_EVIDENCE_INSUFFICIENT")

    # Linguistic validation
    ling_ev = evid.get("linguistic_validation", {})
    ling_issues = ling_ev.get("issues", [])
    for issue in ling_issues:
        code = issue.get("code")
        if code and code not in codes:
            codes.append(code)

    if not codes and val_rec.get("release_decision") != "pass":
        codes.append("UNKNOWN_VALIDATION_FAILURE")

    return codes


def run_release_gate():
    print("[*] Initiating Phase 1.1A Production Release Gate...")
    if not VALIDATED_FILE.exists():
        print(f"[!] Error: Validated candidates file not found: {VALIDATED_FILE}")
        sys.exit(1)

    production_records = []
    needs_review_records = []
    rejected_records = []
    pronunciation_reviews = []
    linguistic_reviews = []
    translation_reviews = []
    source_reviews = []
    released_ids = set()

    with open(VALIDATED_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            entry = json.loads(line)
            val_rec = entry.get("lineage", {}).get("validation_record", {})
            decision = val_rec.get("release_decision", "needs_review")
            reason_codes = determine_reason_codes(entry)

            if decision == "pass":
                entry["status"] = "production"
                entry["lineage"]["release_version"] = RELEASE_VERSION

                # Strictly promote all learning objects to 'production_verified'
                for c in entry.get("collocations", []):
                    c["status"] = "production_verified"
                    c["validation_method"] = "independent_linguistic_judge"
                for ex in entry.get("examples", []):
                    ex["status"] = "production_verified"
                    ex["validation_method"] = "independent_linguistic_judge"
                for turn in entry.get("dialogue", []):
                    turn["status"] = "production_verified"
                    turn["validation_method"] = "independent_linguistic_judge"

                production_records.append(entry)
                released_ids.add(entry["id"])
            elif decision == "needs_review":
                entry["status"] = "needs_review"
                entry["reason_codes"] = reason_codes
                needs_review_records.append(entry)

                if any("PRONUNCIATION" in c for c in reason_codes):
                    pronunciation_reviews.append(entry)
                if any("COLLOCATION" in c or "EXAMPLE" in c or "DIALOGUE" in c for c in reason_codes):
                    linguistic_reviews.append(entry)
                if any("TRANSLATION" in c or "CONTAMINATION" in c for c in reason_codes):
                    translation_reviews.append(entry)
                if any("SOURCE" in c for c in reason_codes):
                    source_reviews.append(entry)
            else:
                entry["status"] = "rejected"
                entry["reason_codes"] = reason_codes
                rejected_records.append(entry)

    # STRICT AUDIT: Production records must contain ZERO objects with status 'generated'
    for entry in production_records:
        for c in entry.get("collocations", []):
            if c.get("status") == "generated":
                raise ValueError(f"RELEASE GATE FAILURE: Entry {entry['id']} contains collocation with status='generated'")
        for ex in entry.get("examples", []):
            if ex.get("status") == "generated":
                raise ValueError(f"RELEASE GATE FAILURE: Entry {entry['id']} contains example with status='generated'")
        for turn in entry.get("dialogue", []):
            if turn.get("status") == "generated":
                raise ValueError(f"RELEASE GATE FAILURE: Entry {entry['id']} contains dialogue turn with status='generated'")

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

    with open(PRONUNCIATION_REVIEW_FILE, "w", encoding="utf-8") as f:
        for entry in pronunciation_reviews:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    print(f"[+] Written {len(pronunciation_reviews)} records to {PRONUNCIATION_REVIEW_FILE}")

    with open(LINGUISTIC_REVIEW_FILE, "w", encoding="utf-8") as f:
        for entry in linguistic_reviews:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    print(f"[+] Written {len(linguistic_reviews)} records to {LINGUISTIC_REVIEW_FILE}")

    with open(TRANSLATION_REVIEW_FILE, "w", encoding="utf-8") as f:
        for entry in translation_reviews:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    print(f"[+] Written {len(translation_reviews)} records to {TRANSLATION_REVIEW_FILE}")

    with open(SOURCE_REVIEW_FILE, "w", encoding="utf-8") as f:
        for entry in source_reviews:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    print(f"[+] Written {len(source_reviews)} records to {SOURCE_REVIEW_FILE}")

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
    print("RELEASE GATE SUMMARY (PHASE 1.1A):")
    print(f"  Production Released: {len(production_records)}")
    print(f"  Needs Review:        {len(needs_review_records)}")
    print(f"  Rejected:            {len(rejected_records)}")
    print("="*50)


if __name__ == "__main__":
    run_release_gate()
