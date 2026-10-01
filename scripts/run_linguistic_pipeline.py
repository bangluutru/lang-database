#!/usr/bin/env python3
"""
scripts/run_linguistic_pipeline.py
Phase 1.1B True Independent Linguistic Judge Execution Pipeline.

Executes:
1. Concept / Semantic Classification Audit (Already completed across 800 records, loaded/verified).
2. Pass A: LLM Critic evaluation of 800 records (3,200 collocations, 1,600 examples, 1,600 dialogue turns).
3. Pass B: Resolver on flagged learning objects (producing Candidate v2).
4. Pass C: Re-Judge (blind verification of Candidate v2).
5. Validation Evidence Metadata Attachment.
6. Writes to data/validated/validated_candidates.jsonl.
7. Generates detailed statistics and reports.
"""

import sys
import os
import json
import copy
import time
from pathlib import Path
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from scripts.llm_judge import TrueLinguisticJudge

CANDIDATES_FILE = BASE_DIR / "data" / "enriched" / "learning_candidates.jsonl"
VALIDATED_FILE = BASE_DIR / "data" / "validated" / "validated_candidates.jsonl"
SEMANTIC_AUDIT_FILE = BASE_DIR / "reports" / "semantic_audit_results.json"
VALIDATED_FILE.parent.mkdir(parents=True, exist_ok=True)


def load_semantic_audit_map() -> dict:
    audit_map = {}
    if SEMANTIC_AUDIT_FILE.exists():
        with open(SEMANTIC_AUDIT_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            for r in data.get("results", []):
                entry_id = r.get("entry_id")
                aud = r.get("audit")
                if entry_id and aud:
                    audit_map[entry_id] = aud
                if aud and "term" in aud:
                    audit_map[aud["term"]] = aud
    return audit_map


def process_record(item: dict, judge: TrueLinguisticJudge, audit_map: dict) -> tuple:
    entry_id = item["id"]
    surface = item["term"]["surface"]

    # 1. Semantic Audit Data
    audit = audit_map.get(entry_id) or audit_map.get(surface)
    if not audit:
        audit = judge.audit_semantic_class(item)

    # 2. Pass A: Critic
    critic = judge.critic_learning_object(item)
    overall_decision = critic.get("overall_decision", "pass")

    was_rewritten = False
    rejudge_data = None
    processed_item = copy.deepcopy(item)
    issues_discovered = []

    # Check if any component was flagged for rewrite
    needs_rewrite = (overall_decision == "rewrite")
    colls_critic = critic.get("collocations", [])
    exs_critic = critic.get("examples", [])
    dial_critic = critic.get("dialogue", {})
    trans_critic = critic.get("translations", {})

    for c in colls_critic:
        if c.get("decision") == "rewrite":
            needs_rewrite = True
            issues_discovered.append(f"Collocation '{c.get('text')}': {c.get('reason')}")
    for ex in exs_critic:
        if ex.get("decision") == "rewrite":
            needs_rewrite = True
            issues_discovered.append(f"Example {ex.get('index')}: {ex.get('reason')}")
    if dial_critic.get("decision") == "rewrite":
        needs_rewrite = True
        issues_discovered.append(f"Dialogue: {dial_critic.get('reason')}")
    if trans_critic.get("vi") == "rewrite" or trans_critic.get("en") == "rewrite":
        needs_rewrite = True
        issues_discovered.append(f"Translation: {trans_critic.get('reason')}")

    if needs_rewrite:
        was_rewritten = True
        # Apply component rewrites from critic suggestions if available
        # Collocations
        for c in colls_critic:
            idx = c.get("index", 0)
            if c.get("decision") == "rewrite" and c.get("suggested_text") and idx < len(processed_item["collocations"]):
                processed_item["collocations"][idx]["text"] = c["suggested_text"]
                processed_item["collocations"][idx]["status"] = "resolved_candidate"

        # Examples
        for ex in exs_critic:
            idx = ex.get("index", 0)
            if ex.get("decision") == "rewrite" and idx < len(processed_item["examples"]):
                if ex.get("suggested_ja"):
                    processed_item["examples"][idx]["ja"] = ex["suggested_ja"]
                if ex.get("suggested_vi"):
                    processed_item["examples"][idx]["vi"] = ex["suggested_vi"]
                if ex.get("suggested_en"):
                    processed_item["examples"][idx]["en"] = ex["suggested_en"]
                processed_item["examples"][idx]["status"] = "resolved_candidate"

        # Dialogue
        if dial_critic.get("decision") == "rewrite" and dial_critic.get("suggested_turns"):
            turns = dial_critic["suggested_turns"]
            if isinstance(turns, list) and len(turns) >= 2:
                processed_item["dialogue"] = [
                    {"speaker": t.get("speaker", "A"), "ja": t.get("ja", ""), "vi": t.get("vi", ""), "en": t.get("en", ""), "status": "resolved_candidate"}
                    for t in turns
                ]

        # Pass C: Re-Judge
        rejudge_data = judge.rejudge_learning_object(processed_item)

    # Determine final validation status
    if not was_rewritten:
        if overall_decision == "pass":
            val_status = "linguistically_validated"
        elif overall_decision == "human_review":
            val_status = "needs_human_review"
        else:
            val_status = "rejected"
    else:
        if rejudge_data.get("decision") == "pass":
            val_status = "linguistically_validated"
        elif rejudge_data.get("decision") == "human_review":
            val_status = "needs_human_review"
        else:
            val_status = "rejected"

    # Attach provenance metadata
    processed_item["linguistic_validation"] = {
        "status": val_status,
        "semantic_audit": {
            "status": "pass" if audit.get("decision") in ["correct", "incorrect"] else "review",
            "decision": audit.get("decision"),
            "original_class": audit.get("current_class"),
            "audited_class": audit.get("suggested_semantic_class"),
            "model": audit.get("metadata", {}).get("model", judge.model),
            "prompt_version": audit.get("metadata", {}).get("prompt_version", "semantic_audit_v1"),
            "input_hash": audit.get("metadata", {}).get("input_hash"),
            "validated_at": audit.get("metadata", {}).get("validated_at")
        },
        "linguistic_judge": {
            "status": "pass" if overall_decision == "pass" else "rewrite_flagged",
            "critic_decision": overall_decision,
            "summary_reason": critic.get("summary_reason"),
            "model": critic.get("metadata", {}).get("model", judge.model),
            "prompt_version": critic.get("metadata", {}).get("prompt_version", "linguistic_judge_v1"),
            "input_hash": critic.get("metadata", {}).get("input_hash"),
            "validated_at": critic.get("metadata", {}).get("validated_at")
        },
        "rejudge": {
            "required": was_rewritten,
            "status": rejudge_data.get("decision") if rejudge_data else None,
            "model": rejudge_data.get("metadata", {}).get("model") if rejudge_data else None,
            "prompt_version": rejudge_data.get("metadata", {}).get("prompt_version") if rejudge_data else None,
            "input_hash": rejudge_data.get("metadata", {}).get("input_hash") if rejudge_data else None,
            "validated_at": rejudge_data.get("metadata", {}).get("validated_at") if rejudge_data else None
        }
    }

    # Summary of changes for reports
    report_meta = {
        "entry_id": entry_id,
        "term": surface,
        "domain": item.get("domain", {}).get("primary"),
        "tier": item.get("tier"),
        "was_rewritten": was_rewritten,
        "val_status": val_status,
        "critic": critic,
        "rejudge": rejudge_data,
        "issues_discovered": issues_discovered
    }

    return processed_item, report_meta


def main():
    print("[*] Starting Phase 1.1B True Linguistic Judge Execution Pipeline...")
    judge = TrueLinguisticJudge()
    audit_map = load_semantic_audit_map()
    print(f"[+] Loaded {len(audit_map)} semantic audit mappings.")

    records = []
    with open(CANDIDATES_FILE, "r", encoding="utf-8") as f:
        for line in f:
            records.append(json.loads(line))
    print(f"[+] Loaded {len(records)} candidates for linguistic audit.")

    validated_results = []
    report_metadata_list = []

    print("[*] Executing Pass A (Critic) and Pass C (Re-Judge) with thread pool (workers=8)...", flush=True)
    start_time = time.time()

    with ThreadPoolExecutor(max_workers=8) as executor:
        future_to_rec = {
            executor.submit(process_record, rec, judge, audit_map): rec for rec in records
        }

        completed = 0
        for future in as_completed(future_to_rec):
            try:
                proc_item, r_meta = future.result()
                validated_results.append(proc_item)
                report_metadata_list.append(r_meta)
                completed += 1
                if completed % 25 == 0 or completed == len(records):
                    elapsed = time.time() - start_time
                    print(f"  [>] Progress: {completed}/{len(records)} records processed ({elapsed:.1f}s elapsed, {completed/elapsed:.1f} rec/s)", flush=True)
            except Exception as e:
                rec = future_to_rec[future]
                print(f"[!] Exception on {rec['id']} ({rec['term']['surface']}): {e}. Retrying sequentially...", flush=True)
                try:
                    proc_item, r_meta = process_record(rec, judge, audit_map)
                    validated_results.append(proc_item)
                    report_metadata_list.append(r_meta)
                    completed += 1
                except Exception as e2:
                    print(f"[!] Persistent failure on {rec['id']}: {e2}. Routing to needs_human_review.", flush=True)
                    fallback_item = copy.deepcopy(rec)
                    fallback_item["status"] = "needs_human_review"
                    fallback_item["linguistic_validation"] = {
                        "status": "needs_human_review",
                        "error": str(e2)
                    }
                    validated_results.append(fallback_item)
                    report_metadata_list.append({
                        "entry_id": rec["id"],
                        "term": rec["term"]["surface"],
                        "domain": rec.get("domain", {}).get("primary"),
                        "tier": rec.get("tier"),
                        "was_rewritten": False,
                        "val_status": "needs_human_review",
                        "issues_discovered": [str(e2)]
                    })
                    completed += 1

    # Sort validated results by entry ID to preserve canonical ordering
    validated_results.sort(key=lambda x: x["id"])
    report_metadata_list.sort(key=lambda x: x["entry_id"])

    # Write to validated_candidates.jsonl
    with open(VALIDATED_FILE, "w", encoding="utf-8") as f:
        for item in validated_results:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")
    print(f"[+] Wrote {len(validated_results)} validated candidates to {VALIDATED_FILE}")

    # Calculate statistics
    total_records = len(validated_results)
    passed_unchanged = sum(1 for m in report_metadata_list if not m["was_rewritten"] and m["val_status"] == "linguistically_validated")
    passed_after_rewrite = sum(1 for m in report_metadata_list if m["was_rewritten"] and m["val_status"] == "linguistically_validated")
    human_review_count = sum(1 for m in report_metadata_list if m["val_status"] == "needs_human_review")
    rejected_count = sum(1 for m in report_metadata_list if m["val_status"] == "rejected")

    print("\n" + "=" * 50)
    print("PHASE 1.1B LINGUISTIC PIPELINE EXECUTION SUMMARY")
    print("=" * 50)
    print(f"Total Records Audited:      {total_records}")
    print(f"Passed Unchanged:           {passed_unchanged}")
    print(f"Passed After Rewrite:       {passed_after_rewrite}")
    print(f"Needs Human Review:         {human_review_count}")
    print(f"Rejected:                   {rejected_count}")
    print(f"Total Execution Time:       {time.time() - start_time:.1f}s")
    print("=" * 50)

    # Save summary report
    summary_path = BASE_DIR / "reports" / "pipeline_execution_summary.json"
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump({
            "total_records": total_records,
            "passed_unchanged": passed_unchanged,
            "passed_after_rewrite": passed_after_rewrite,
            "human_review_count": human_review_count,
            "rejected_count": rejected_count,
            "reports": report_metadata_list
        }, f, ensure_ascii=False, indent=2)
    print(f"[+] Saved execution metadata to {summary_path}")


if __name__ == "__main__":
    main()
