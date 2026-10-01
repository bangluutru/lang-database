"""
scripts/canary/state_machine.py
State machine governing the candidate promotion lifecycle for Phase 1.2C.

Enforces:
1. Deterministic state progression:
   candidate -> selected_for_canary -> validation_passed -> human_review_passed -> promotion_eligible -> canary
2. Rejection of direct jumps (e.g. candidate -> canary).
3. Prohibition of promotion without explicit human review approval.
"""

from typing import Set, Dict
from scripts.canary.models import CanaryState, CanaryCandidateRecord, HumanReviewDecision


class InvalidStateTransitionError(Exception):
    """Raised when an illegal transition is attempted."""
    pass


class UnapprovedPromotionError(Exception):
    """Raised when promotion is attempted without human review approval."""
    pass


class GateFailureError(Exception):
    """Raised when a candidate fails validation gates."""
    pass


class PromotionStateMachine:
    VALID_TRANSITIONS: Dict[CanaryState, Set[CanaryState]] = {
        CanaryState.CANDIDATE: {
            CanaryState.SELECTED_FOR_CANARY,
            CanaryState.REJECTED,
            CanaryState.NEEDS_REVIEW
        },
        CanaryState.SELECTED_FOR_CANARY: {
            CanaryState.VALIDATION_PASSED,
            CanaryState.VARIANT_DETECTED,
            CanaryState.DUPLICATE_DETECTED,
            CanaryState.SENSE_AMBIGUOUS,
            CanaryState.LICENSING_BLOCKED,
            CanaryState.INSUFFICIENT_EVIDENCE,
            CanaryState.REJECTED,
            CanaryState.NEEDS_REVIEW
        },
        CanaryState.VALIDATION_PASSED: {
            CanaryState.HUMAN_REVIEW_PASSED,
            CanaryState.REJECTED,
            CanaryState.NEEDS_REVIEW
        },
        CanaryState.HUMAN_REVIEW_PASSED: {
            CanaryState.PROMOTION_ELIGIBLE,
            CanaryState.NEEDS_REVIEW,
            CanaryState.REJECTED
        },
        CanaryState.PROMOTION_ELIGIBLE: {
            CanaryState.CANARY,
            CanaryState.NEEDS_REVIEW,
            CanaryState.REJECTED
        },
        CanaryState.CANARY: set(),  # Terminal state for Canary release
        # Terminal / Review states
        CanaryState.REJECTED: set(),
        CanaryState.NEEDS_REVIEW: {CanaryState.SELECTED_FOR_CANARY, CanaryState.REJECTED},
        CanaryState.VARIANT_DETECTED: set(),
        CanaryState.DUPLICATE_DETECTED: set(),
        CanaryState.SENSE_AMBIGUOUS: set(),
        CanaryState.INSUFFICIENT_EVIDENCE: set(),
        CanaryState.LICENSING_BLOCKED: set(),
    }

    @classmethod
    def transition(
        cls,
        record: CanaryCandidateRecord,
        target_state: CanaryState,
        actor: str,
        reason: str
    ) -> CanaryCandidateRecord:
        current = record.state
        if isinstance(current, str):
            current = CanaryState(current)

        allowed = cls.VALID_TRANSITIONS.get(current, set())
        if target_state not in allowed:
            raise InvalidStateTransitionError(
                f"Illegal state transition: {current.value} -> {target_state.value} for candidate {record.candidate_id}. "
                f"Allowed target states: {[s.value for s in allowed]}"
            )

        # Gate guard: promotion requires human review approval
        if target_state == CanaryState.CANARY:
            if current != CanaryState.PROMOTION_ELIGIBLE:
                raise UnapprovedPromotionError(
                    f"Candidate {record.candidate_id} must be in '{CanaryState.PROMOTION_ELIGIBLE.value}' before promotion to Canary, currently '{current.value}'"
                )
            if not record.human_review or record.human_review.get("decision") != HumanReviewDecision.APPROVE.value:
                raise UnapprovedPromotionError(
                    f"Candidate {record.candidate_id} has not been approved by Human Review. Promotion blocked."
                )

        record.record_transition(target_state, actor, reason)
        return record

    @classmethod
    def can_promote(cls, record: CanaryCandidateRecord) -> bool:
        current = record.state
        if isinstance(current, str):
            current = CanaryState(current)
        if current != CanaryState.PROMOTION_ELIGIBLE:
            return False
        if not record.human_review:
            return False
        return record.human_review.get("decision") == HumanReviewDecision.APPROVE.value
