"""
scripts/canary/models.py
Data models and state definitions for Phase 1.2C: Controlled Canary Expansion & Promotion Pipeline.
"""

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Any
from enum import Enum


class CanaryState(str, Enum):
    CANDIDATE = "candidate"
    SELECTED_FOR_CANARY = "selected_for_canary"
    VALIDATION_PASSED = "validation_passed"
    HUMAN_REVIEW_PASSED = "human_review_passed"
    PROMOTION_ELIGIBLE = "promotion_eligible"
    CANARY = "canary"

    # Terminal / Review / Rejection States
    REJECTED = "rejected"
    NEEDS_REVIEW = "needs_review"
    VARIANT_DETECTED = "variant_detected"
    DUPLICATE_DETECTED = "duplicate_detected"
    SENSE_AMBIGUOUS = "sense_ambiguous"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"
    LICENSING_BLOCKED = "licensing_blocked"


class HumanReviewDecision(str, Enum):
    APPROVE = "APPROVE"
    REJECT = "REJECT"
    NEEDS_REVISION = "NEEDS_REVISION"
    VARIANT_OF = "VARIANT_OF"
    DUPLICATE_OF = "DUPLICATE_OF"
    DIFFERENT_SENSE = "DIFFERENT_SENSE"
    PENDING = "PENDING"


class GateStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    NEEDS_REVIEW = "NEEDS_REVIEW"


@dataclass
class GateResult:
    gate_name: str
    status: GateStatus
    reasons: List[str] = field(default_factory=list)
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "gate_name": self.gate_name,
            "status": self.status.value,
            "reasons": self.reasons,
            "details": self.details,
        }


@dataclass
class CanaryCandidateRecord:
    candidate_id: str
    surface: str
    normalized_surface: str
    reading: str
    domain: str
    subdomain: str
    meaning_gloss: str
    authority_class: str
    reuse_status: str
    source_evidence: List[Dict[str, Any]]
    pro_level_candidate: str
    priority: Dict[str, Any]
    state: CanaryState = CanaryState.CANDIDATE
    gate_results: Dict[str, Any] = field(default_factory=dict)
    human_review: Optional[Dict[str, Any]] = None
    lineage: Dict[str, Any] = field(default_factory=dict)
    audit_trail: List[Dict[str, Any]] = field(default_factory=list)

    def record_transition(self, new_state: CanaryState, actor: str, reason: str):
        self.state = new_state
        self.audit_trail.append({
            "to_state": new_state.value,
            "actor": actor,
            "reason": reason
        })

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["state"] = self.state.value if isinstance(self.state, CanaryState) else self.state
        return d
