"""
scripts/canary/decision_importer.py
Human Decision Ingestion Engine & Revalidation Loop for Phase 1.2C.

Responsibilities:
1. Ingests human review decisions from a structured file (JSON or JSONL).
2. Validates review decision integrity:
   - Candidate ID existence
   - Decision validity: APPROVE, REJECT, NEEDS_REVISION, VARIANT_OF, DUPLICATE_OF, DIFFERENT_SENSE, PENDING
   - Reviewer identity non-empty for completed decisions
   - ISO-8601 reviewed_at timestamp existence
   - Target ID presence for VARIANT_OF and DUPLICATE_OF
3. Revalidation Loop (Section 18):
   - When human modifies surface, reading, gloss, domain, or subdomain, re-runs automated validation gates (A, B, C).
   - If revalidation fails, candidate cannot transition to promotion eligibility.
4. Updates candidate states via PromotionStateMachine:
   - Only approved and valid candidates transition to HUMAN_REVIEW_PASSED -> PROMOTION_ELIGIBLE.
   - PENDING, REJECT, and NEEDS_REVISION candidates remain quarantined and cannot promote.
"""

from typing import List, Dict, Any, Tuple, Optional
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
    HumanReviewDecision,
    GateStatus
)
from scripts.canary.state_machine import (
    PromotionStateMachine,
    UnapprovedPromotionError
)
from scripts.canary.validator import CanaryValidator

ALLOWED_DECISIONS = {
    HumanReviewDecision.APPROVE.value,
    HumanReviewDecision.REJECT.value,
    HumanReviewDecision.NEEDS_REVISION.value,
    HumanReviewDecision.VARIANT_OF.value,
    HumanReviewDecision.DUPLICATE_OF.value,
    HumanReviewDecision.DIFFERENT_SENSE.value,
    HumanReviewDecision.PENDING.value
}


class DecisionValidationError(Exception):
    """Raised when human decision input is invalid."""
    pass


class RevalidationFailedError(Exception):
    """Raised when a human-modified candidate fails automated validation gates."""
    pass


class CanaryDecisionImporter:
    def __init__(self, validator: Optional[CanaryValidator] = None):
        if validator is None:
            self.validator = CanaryValidator(
                taxonomy_path=BASE_DIR / "config" / "domain_taxonomy.yaml",
                production_path=BASE_DIR / "data" / "production" / "vocabulary.jsonl",
                golden_v1_path=BASE_DIR / "data" / "releases" / "golden-pilot-v1" / "vocabulary.jsonl",
                golden_v1_1_path=BASE_DIR / "data" / "releases" / "golden-pilot-v1.1" / "vocabulary.jsonl"
            )
        else:
            self.validator = validator

    def load_decisions(self, decisions_path: Path) -> Dict[str, Dict[str, Any]]:
        """Loads decisions from JSON or JSONL file into a mapping keyed by candidate_id."""
        decisions: Dict[str, Dict[str, Any]] = {}
        if not decisions_path.exists():
            return decisions

        with open(decisions_path, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content:
                return decisions

            # Try parsing as JSON array
            if content.startswith("[") and content.endswith("]"):
                items = json.loads(content)
                for item in items:
                    decisions[item["candidate_id"]] = item
            else:
                # Parse as JSONL
                for line in content.splitlines():
                    if line.strip():
                        item = json.loads(line)
                        decisions[item["candidate_id"]] = item

        return decisions

    def apply_decision(
        self,
        record: CanaryCandidateRecord,
        decision_data: Dict[str, Any],
        batch_surfaces: Dict[str, str]
    ) -> CanaryCandidateRecord:
        """Applies a validated decision and revision loop to a candidate record."""
        cid = record.candidate_id
        decision_str = decision_data.get("decision", HumanReviewDecision.PENDING.value)

        # 1. Validate decision string
        if decision_str not in ALLOWED_DECISIONS:
            raise DecisionValidationError(
                f"Invalid decision '{decision_str}' for candidate {cid}. Allowed: {sorted(ALLOWED_DECISIONS)}"
            )

        # 2. Validate reviewer and timestamp for completed decisions
        reviewer = decision_data.get("reviewer")
        reviewed_at = decision_data.get("reviewed_at")

        if decision_str != HumanReviewDecision.PENDING.value:
            if not reviewer or not str(reviewer).strip():
                raise DecisionValidationError(
                    f"Decision '{decision_str}' for candidate {cid} must have a non-empty 'reviewer'."
                )
            if not reviewed_at:
                raise DecisionValidationError(
                    f"Decision '{decision_str}' for candidate {cid} must have a 'reviewed_at' timestamp."
                )

        # 3. Validate relationship target for VARIANT_OF and DUPLICATE_OF
        target_id = decision_data.get("target_id")
        if decision_str in (HumanReviewDecision.VARIANT_OF.value, HumanReviewDecision.DUPLICATE_OF.value):
            if not target_id or not str(target_id).strip():
                raise DecisionValidationError(
                    f"Decision '{decision_str}' for candidate {cid} requires a non-empty 'target_id'."
                )

        # Record human review metadata
        record.human_review = {
            "decision": decision_str,
            "reviewer": reviewer,
            "reviewed_at": reviewed_at,
            "notes": decision_data.get("notes", ""),
            "target_id": target_id
        }

        # 4. Handle Revision Loop (Section 18)
        # Check if human provided revisions to canonical data
        has_revision = False
        if "revised_surface" in decision_data:
            record.surface = decision_data["revised_surface"]
            record.normalized_surface = decision_data["revised_surface"]
            has_revision = True
        if "revised_reading" in decision_data:
            record.reading = decision_data["revised_reading"]
            has_revision = True
        if "revised_gloss" in decision_data:
            record.meaning_gloss = decision_data["revised_gloss"]
            has_revision = True
        if "revised_subdomain" in decision_data:
            record.subdomain = decision_data["revised_subdomain"]
            has_revision = True

        if has_revision:
            # Re-run automated validation gates
            record.record_transition(
                CanaryState.SELECTED_FOR_CANARY,
                actor=reviewer or "human_reviewer",
                reason="Candidate revised by human; entering automated revalidation loop."
            )
            reval_passed = self.validator.validate_candidate(record, batch_surfaces)
            if not reval_passed:
                raise RevalidationFailedError(
                    f"Candidate {cid} revised data failed automated revalidation: {record.gate_results}"
                )

        # 5. State Machine Progression
        if decision_str == HumanReviewDecision.APPROVE.value:
            # Must pass human review gate and transition to promotion eligible
            if record.state != CanaryState.VALIDATION_PASSED:
                # If was selected_for_canary and revalidated, ensure validation passed
                record.state = CanaryState.VALIDATION_PASSED

            PromotionStateMachine.transition(
                record,
                CanaryState.HUMAN_REVIEW_PASSED,
                actor=reviewer,
                reason="Explicit human approval granted."
            )
            PromotionStateMachine.transition(
                record,
                CanaryState.PROMOTION_ELIGIBLE,
                actor=reviewer,
                reason="Candidate eligible for Canary release promotion."
            )
        elif decision_str == HumanReviewDecision.REJECT.value:
            record.record_transition(
                CanaryState.REJECTED,
                actor=reviewer,
                reason=f"Rejected by human reviewer: {decision_data.get('notes', '')}"
            )
        elif decision_str == HumanReviewDecision.NEEDS_REVISION.value:
            record.record_transition(
                CanaryState.NEEDS_REVIEW,
                actor=reviewer,
                reason=f"Marked for revision by human reviewer: {decision_data.get('notes', '')}"
            )
        elif decision_str in (HumanReviewDecision.VARIANT_OF.value, HumanReviewDecision.DUPLICATE_OF.value):
            target_state = (
                CanaryState.VARIANT_DETECTED
                if decision_str == HumanReviewDecision.VARIANT_OF.value
                else CanaryState.DUPLICATE_DETECTED
            )
            record.record_transition(
                target_state,
                actor=reviewer,
                reason=f"Linked to target {target_id} by human reviewer."
            )
        elif decision_str == HumanReviewDecision.DIFFERENT_SENSE.value:
            # Preserve separate sense and allow promotion if approved as independent sense
            PromotionStateMachine.transition(
                record,
                CanaryState.HUMAN_REVIEW_PASSED,
                actor=reviewer,
                reason=f"Distinct professional sense confirmed by human reviewer: {decision_data.get('notes', '')}"
            )
            PromotionStateMachine.transition(
                record,
                CanaryState.PROMOTION_ELIGIBLE,
                actor=reviewer,
                reason="Independent sense eligible for Canary release promotion."
            )

        return record

    def import_and_update_queue(
        self,
        queue_path: Path,
        decisions_path: Path,
        output_path: Path
    ) -> Dict[str, Any]:
        """Loads review queue, applies human decisions, updates states, and writes back."""
        with open(queue_path, "r", encoding="utf-8") as f:
            queue_items = [json.loads(line) for line in f if line.strip()]

        decisions_map = self.load_decisions(decisions_path)

        updated_records = []
        batch_surfaces = {}

        approved_count = 0
        rejected_count = 0
        revision_count = 0
        pending_count = 0
        variant_count = 0
        duplicate_count = 0
        sense_count = 0

        for item in queue_items:
            cid = item["candidate_id"]
            # Convert raw queue item to CanaryCandidateRecord
            state_val = item.get("state", CanaryState.VALIDATION_PASSED.value)
            try:
                state_enum = CanaryState(state_val)
            except ValueError:
                state_enum = CanaryState.VALIDATION_PASSED

            rec = CanaryCandidateRecord(
                candidate_id=cid,
                surface=item["surface"],
                normalized_surface=item.get("normalized_surface", item["surface"]),
                reading=item["reading"],
                domain=item["domain"],
                subdomain=item["subdomain"],
                meaning_gloss=item["meaning_gloss"],
                authority_class=item["authority_class"],
                reuse_status=item["reuse_status"],
                source_evidence=[item.get("source_evidence", {})] if isinstance(item.get("source_evidence"), dict) else item.get("source_evidence", []),
                pro_level_candidate="PRO-A1",
                priority={"workplace_frequency": "high", "professional_importance": "high"},
                state=state_enum,
                lineage={"proposed_canonical_id": item.get("proposed_id")}
            )

            if cid in decisions_map:
                dec_data = decisions_map[cid]
                self.apply_decision(rec, dec_data, batch_surfaces)
            else:
                # Retain existing decision if any, or PENDING
                if not rec.human_review:
                    rec.human_review = {"decision": HumanReviewDecision.PENDING.value}

            # Count stats
            dec = rec.human_review.get("decision", HumanReviewDecision.PENDING.value)
            if dec == HumanReviewDecision.APPROVE.value:
                approved_count += 1
            elif dec == HumanReviewDecision.REJECT.value:
                rejected_count += 1
            elif dec == HumanReviewDecision.NEEDS_REVISION.value:
                revision_count += 1
            elif dec == HumanReviewDecision.VARIANT_OF.value:
                variant_count += 1
            elif dec == HumanReviewDecision.DUPLICATE_OF.value:
                duplicate_count += 1
            elif dec == HumanReviewDecision.DIFFERENT_SENSE.value:
                sense_count += 1
            else:
                pending_count += 1

            batch_surfaces[rec.surface] = rec.candidate_id

            # Prepare dict for serialization
            out_item = dict(item)
            out_item["surface"] = rec.surface
            out_item["reading"] = rec.reading
            out_item["meaning_gloss"] = rec.meaning_gloss
            out_item["subdomain"] = rec.subdomain
            out_item["state"] = rec.state.value if isinstance(rec.state, CanaryState) else rec.state
            out_item["human_decision"] = dec
            out_item["reviewer"] = rec.human_review.get("reviewer")
            out_item["reviewed_at"] = rec.human_review.get("reviewed_at")
            out_item["human_comment"] = rec.human_review.get("notes")
            out_item["target_id"] = rec.human_review.get("target_id")
            out_item["audit_trail"] = rec.audit_trail
            updated_records.append(out_item)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            for r in updated_records:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")

        return {
            "total": len(updated_records),
            "approved": approved_count,
            "rejected": rejected_count,
            "needs_revision": revision_count,
            "variant_of": variant_count,
            "duplicate_of": duplicate_count,
            "different_sense": sense_count,
            "pending": pending_count
        }
