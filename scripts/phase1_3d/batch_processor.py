#!/usr/bin/env python3
"""
scripts/phase1_3d/batch_processor.py
Batch Processor for Phase 1.3D.
Processes the full partial queue of 1,034 concepts across deterministic batches:
- Batch 1: Canary 100 concepts (already processed, loaded from cache)
- Batch 2: Next 200 concepts
- Batch 3: Remaining 734 concepts
Executes:
1. Gate 1: EN-JA Semantic Alignment & POS Compatibility (EnJaValidator)
2. Gate 2: Vietnamese Source-First Lookup (ViSourceResolver)
3. Fallback: AI Candidate Generation (AiCandidateGenerator)
4. Gate 3: Blind Linguistic Judge (LinguisticJudge)
5. Structured Routing: Auto-Accept, Human Review Queue, or Quarantine
"""

import sys
import json
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from scripts.phase1_3d.en_ja_validator import EnJaValidator
from scripts.phase1_3d.vi_source_resolver import ViSourceResolver
from scripts.phase1_3d.ai_candidate_generator import AiCandidateGenerator
from scripts.phase1_3d.linguistic_judge import LinguisticJudge
from scripts.phase1_3d.canary_runner import CanaryRunner

REPORTS_DIR = BASE_DIR / "reports" / "phase1_3d"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)
FULL_QUEUE_PATH = REPORTS_DIR / "full_partial_queue.json"


class BatchProcessor:
    """Processes full queue of 1,034 partial concepts in deterministic batches."""

    def __init__(self, concurrency: int = 6):
        self.concurrency = concurrency
        self.en_ja_validator = EnJaValidator(max_workers=concurrency)
        self.vi_resolver = ViSourceResolver()
        self.ai_generator = AiCandidateGenerator()
        self.judge = LinguisticJudge()
        self.canary_runner = CanaryRunner(concurrency=concurrency)

    def process_batch(self, batch_name: str, queue_items: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], Counter, List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Processes a single batch of partial concepts."""
        total = len(queue_items)
        print(f"\n=== Processing {batch_name} ({total} items, concurrency={self.concurrency}) ===", flush=True)

        # Stage 1: Validate EN-JA Alignment
        print(f"[{batch_name}] Stage 1: Validating EN-JA Alignment...", flush=True)
        en_ja_results = self.en_ja_validator.validate_queue(queue_items)
        en_ja_map = {r["concept_id"]: r for r in en_ja_results}

        # Stage 2 & 3: Process Vietnamese Resolution & Linguistic Judgment
        print(f"[{batch_name}] Stage 2 & 3: Vietnamese Resolution & Linguistic Judgment...", flush=True)
        processed_items = []
        metrics = Counter()
        metrics["total_batch"] = total
        review_queue = []
        rejected_candidates = []

        with ThreadPoolExecutor(max_workers=self.concurrency) as executor:
            future_to_cid = {
                executor.submit(self.canary_runner.process_concept, item, en_ja_map[item["concept_id"]]): item["concept_id"]
                for item in queue_items
            }
            for idx, future in enumerate(as_completed(future_to_cid), 1):
                record, deltas, rev_ent, rej_ent = future.result()
                processed_items.append(record)
                metrics.update(deltas)
                if rev_ent:
                    review_queue.append(rev_ent)
                if rej_ent:
                    rejected_candidates.append(rej_ent)
                if idx % 25 == 0 or idx == total:
                    print(f"[{batch_name}] Processed {idx}/{total} items (accepted={metrics['judge_auto_accepted']}, review={metrics['judge_review']})...", flush=True)

        # Sort deterministically by concept_id
        processed_items.sort(key=lambda x: x["concept_id"])
        review_queue.sort(key=lambda x: x["concept_id"])
        rejected_candidates.sort(key=lambda x: x["concept_id"])

        print(f"[{batch_name}] Summary: Accepted={metrics['judge_auto_accepted']}, Review={metrics['judge_review']}, Quarantined={metrics['quarantined_concepts']}, Replacements={metrics['ja_expression_replacements']}", flush=True)
        return processed_items, metrics, review_queue, rejected_candidates

    def run_all(self) -> Dict[str, Any]:
        if not FULL_QUEUE_PATH.exists():
            raise FileNotFoundError(f"Missing full partial queue: {FULL_QUEUE_PATH}")

        with open(FULL_QUEUE_PATH, "r", encoding="utf-8") as f:
            full_queue = json.load(f)

        print(f"Loaded full partial queue: {len(full_queue)} concepts.")

        # Partition into batches:
        # Batch 1: First 100 (Canary)
        # Batch 2: Next 200 (items 100 to 300)
        # Batch 3: Remaining 734 (items 300 to end)
        b1_items = full_queue[:100]
        b2_items = full_queue[100:300]
        b3_items = full_queue[300:]

        all_processed = []
        all_metrics = Counter()
        all_metrics["total_concepts"] = len(full_queue)
        all_review = []
        all_rejected = []

        # Process Batch 1 (Canary 100)
        b1_res, b1_m, b1_rev, b1_rej = self.process_batch("Batch 1 (Canary 100)", b1_items)
        all_processed.extend(b1_res)
        all_metrics.update(b1_m)
        all_review.extend(b1_rev)
        all_rejected.extend(b1_rej)

        # Process Batch 2 (200 concepts)
        b2_res, b2_m, b2_rev, b2_rej = self.process_batch("Batch 2 (200 concepts)", b2_items)
        all_processed.extend(b2_res)
        all_metrics.update(b2_m)
        all_review.extend(b2_rev)
        all_rejected.extend(b2_rej)

        # Process Batch 3 (734 concepts)
        b3_res, b3_m, b3_rev, b3_rej = self.process_batch("Batch 3 (734 concepts)", b3_items)
        all_processed.extend(b3_res)
        all_metrics.update(b3_m)
        all_review.extend(b3_rev)
        all_rejected.extend(b3_rej)

        # Sort all deterministically
        all_processed.sort(key=lambda x: x["concept_id"])
        all_review.sort(key=lambda x: x["concept_id"])
        all_rejected.sort(key=lambda x: x["concept_id"])

        # Save Combined Output Reports
        with open(REPORTS_DIR / "vi_gap_resolution_report.json", "w", encoding="utf-8") as f:
            json.dump(all_processed, f, ensure_ascii=False, indent=2)

        with open(REPORTS_DIR / "review_queue.json", "w", encoding="utf-8") as f:
            json.dump(all_review, f, ensure_ascii=False, indent=2)

        with open(REPORTS_DIR / "rejected_candidates.json", "w", encoding="utf-8") as f:
            json.dump(all_rejected, f, ensure_ascii=False, indent=2)

        with open(REPORTS_DIR / "final_metrics.json", "w", encoding="utf-8") as f:
            json.dump(dict(all_metrics), f, ensure_ascii=False, indent=2)

        print(f"\n=== Full Queue Processing Complete ({len(all_processed)} concepts) ===")
        print(f"Total Accepted for Canonical: {all_metrics['judge_auto_accepted']}")
        print(f"Total Routed to Review Queue: {len(all_review)}")
        print(f"Total Quarantined Concepts: {all_metrics['quarantined_concepts']}")
        print(f"Total JA Expression Replacements: {all_metrics['ja_expression_replacements']}")

        return dict(all_metrics)


def main():
    processor = BatchProcessor(concurrency=8)
    processor.run_all()


if __name__ == "__main__":
    main()
