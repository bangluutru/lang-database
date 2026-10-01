"""
scripts/canary/review_manager.py
Manages the Human Review Gate, Review Artifacts, and Decision Ingestion for Phase 1.2C.

Explicit Rule:
Never fake human approval. If no actual human decisions are provided, candidates remain
in 'PENDING' review status with state 'validation_passed', cleanly halting the pipeline
at the review boundary.
"""

from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import json
from datetime import datetime, timezone

from scripts.canary.models import (
    CanaryState,
    CanaryCandidateRecord,
    HumanReviewDecision
)
from scripts.canary.state_machine import PromotionStateMachine


class CanaryReviewManager:
    @staticmethod
    def generate_proposed_canonical_id(domain: str, index: int) -> str:
        return f"jp-canary-{domain}-{index:04d}"

    @classmethod
    def export_review_queue(
        cls,
        records: List[CanaryCandidateRecord],
        jsonl_path: Path,
        md_report_path: Path,
        json_report_path: Path
    ) -> Dict[str, Any]:
        jsonl_path.parent.mkdir(parents=True, exist_ok=True)
        md_report_path.parent.mkdir(parents=True, exist_ok=True)
        json_report_path.parent.mkdir(parents=True, exist_ok=True)

        now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        domain_counters: Dict[str, int] = {}
        review_entries: List[Dict[str, Any]] = []

        with open(jsonl_path, "w", encoding="utf-8") as f:
            for r in records:
                dom = r.domain
                domain_counters[dom] = domain_counters.get(dom, 0) + 1
                proposed_id = cls.generate_proposed_canonical_id(dom, domain_counters[dom])

                primary_ev = r.source_evidence[0] if r.source_evidence else {}
                gate_b = r.gate_results.get("Gate_B_Production_Dedup", {})
                gate_c = r.gate_results.get("Gate_C_Linguistic_Quality", {})

                # If candidate already has human_review data (e.g. from test fixture), preserve it
                review_status = r.human_review.get("decision", HumanReviewDecision.PENDING.value) if r.human_review else HumanReviewDecision.PENDING.value
                reviewer_notes = r.human_review.get("notes", "") if r.human_review else ""
                reviewed_at = r.human_review.get("reviewed_at", None) if r.human_review else None

                entry = {
                    "candidate_id": r.candidate_id,
                    "proposed_canonical_id": proposed_id,
                    "surface": r.surface,
                    "normalized_surface": r.normalized_surface,
                    "reading": r.reading,
                    "domain": r.domain,
                    "subdomain": r.subdomain,
                    "meaning_gloss": r.meaning_gloss,
                    "authority_class": r.authority_class,
                    "reuse_status": r.reuse_status,
                    "source_id": primary_ev.get("source_id", ""),
                    "source_version": primary_ev.get("source_version", ""),
                    "source_locator": primary_ev.get("source_locator", ""),
                    "source_count": len(r.source_evidence),
                    "dedup_gate_status": gate_b.get("status", "UNKNOWN"),
                    "linguistic_gate_status": gate_c.get("status", "UNKNOWN"),
                    "confidence_evidence": "high" if r.authority_class in ("A", "B") else "medium",
                    "state": r.state.value if isinstance(r.state, CanaryState) else r.state,
                    "review_status": review_status,
                    "reviewer_notes": reviewer_notes,
                    "reviewed_at": reviewed_at,
                }
                review_entries.append(entry)
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")

        # Compile statistics
        stats = {
            "generated_at": now_iso,
            "total_candidates_in_queue": len(records),
            "pending_review": sum(1 for e in review_entries if e["review_status"] == HumanReviewDecision.PENDING.value),
            "approved": sum(1 for e in review_entries if e["review_status"] == HumanReviewDecision.APPROVE.value),
            "rejected": sum(1 for e in review_entries if e["review_status"] == HumanReviewDecision.REJECT.value),
            "needs_revision": sum(1 for e in review_entries if e["review_status"] == HumanReviewDecision.NEEDS_REVISION.value),
            "by_domain": domain_counters,
            "human_review_complete": all(e["review_status"] != HumanReviewDecision.PENDING.value for e in review_entries) if review_entries else False
        }

        # Write machine-readable JSON report
        with open(json_report_path, "w", encoding="utf-8") as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)

        # Write Markdown review report
        md_lines = [
            "# Phase 1.2C — Human Review Queue & Boundary Status",
            "",
            f"**Generated:** {now_iso}  ",
            f"**Total Records Queued:** {len(records)}  ",
            f"**Pending Human Review:** {stats['pending_review']}  ",
            f"**Approved:** {stats['approved']}  ",
            f"**Rejected / Needs Revision:** {stats['rejected'] + stats['needs_revision']}  ",
            f"**Review Status:** **{'COMPLETE' if stats['human_review_complete'] else 'PENDING_HUMAN_REVIEW'}**  ",
            "",
            "## Stratified Queue Distribution by Domain",
            "",
            "| Domain | Count | Primary Authority | Review Status |",
            "|---|:---:|:---:|:---:|",
        ]
        for dom, count in domain_counters.items():
            md_lines.append(f"| **{dom}** | {count} | Class A/B/C | `PENDING` |")

        md_lines.extend([
            "",
            "## Review Queue Sample (First 15 Candidates)",
            "",
            "| Candidate ID | Proposed ID | Surface | Reading | Domain | Subdomain | Meaning / Gloss | Authority |",
            "|---|---|---|---|---|---|---|:---:|",
        ])
        for e in review_entries[:15]:
            md_lines.append(
                f"| `{e['candidate_id']}` | `{e['proposed_canonical_id']}` | **{e['surface']}** | {e['reading']} | {e['domain']} | {e['subdomain']} | {e['meaning_gloss'][:30]} | `{e['authority_class']}` |"
            )

        md_lines.extend([
            "",
            "## Human Review Protocol & Promotion Boundary",
            "",
            "1. **Strict Boundary:** Candidates in state `validation_passed` remain quarantined in the review queue until an authorized human decision (`APPROVE`, `REJECT`, `NEEDS_REVISION`, `VARIANT_OF`, `DUPLICATE_OF`, `DIFFERENT_SENSE`) is recorded.",
            "2. **No Fake Approvals:** Automatic synthesis of human approval signatures is strictly prohibited.",
            "3. **Promotion Guard:** Only records with `review_status: 'APPROVE'` transition to `PROMOTION_ELIGIBLE` and become eligible for Canary release bundling.",
            ""
        ])

        with open(md_report_path, "w", encoding="utf-8") as f:
            f.write("\n".join(md_lines))

        return stats

    @classmethod
    def apply_human_decisions(
        cls,
        records: List[CanaryCandidateRecord],
        decisions_path: Path
    ) -> Tuple[List[CanaryCandidateRecord], Dict[str, int]]:
        """Applies actual human decisions from a JSONL review audit file."""
        if not decisions_path.exists():
            return records, {"applied": 0, "approved": 0, "rejected": 0}

        decisions_map: Dict[str, Dict[str, Any]] = {}
        with open(decisions_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    item = json.loads(line)
                    decisions_map[item["candidate_id"]] = item

        applied = 0
        approved = 0
        rejected = 0

        for r in records:
            if r.candidate_id in decisions_map:
                dec_info = decisions_map[r.candidate_id]
                dec = dec_info.get("decision")
                notes = dec_info.get("notes", "")
                reviewer = dec_info.get("reviewer", "human_expert")
                now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

                r.human_review = {
                    "decision": dec,
                    "notes": notes,
                    "reviewer": reviewer,
                    "reviewed_at": now_iso
                }
                applied += 1

                if dec == HumanReviewDecision.APPROVE.value:
                    PromotionStateMachine.transition(
                        r,
                        CanaryState.HUMAN_REVIEW_PASSED,
                        actor=reviewer,
                        reason=f"Human Review Approved: {notes}"
                    )
                    PromotionStateMachine.transition(
                        r,
                        CanaryState.PROMOTION_ELIGIBLE,
                        actor="review_manager",
                        reason="Transitioned to promotion eligible after human approval"
                    )
                    approved += 1
                elif dec == HumanReviewDecision.REJECT.value:
                    PromotionStateMachine.transition(
                        r,
                        CanaryState.REJECTED,
                        actor=reviewer,
                        reason=f"Human Review Rejected: {notes}"
                    )
                    rejected += 1
                else:
                    PromotionStateMachine.transition(
                        r,
                        CanaryState.NEEDS_REVIEW,
                        actor=reviewer,
                        reason=f"Human Review Flagged: {dec} - {notes}"
                    )

        return records, {"applied": applied, "approved": approved, "rejected": rejected}
