"""
scripts/source_engine/models.py
Data classes and type definitions for Phase 1.2B Source & Coverage Engine.
"""

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Any
from enum import Enum


class AuthorityClass(str, Enum):
    A = "A"  # Primary official / statutory / regulatory
    B = "B"  # Official professional institution
    C = "C"  # Official business-support institution
    D = "D"  # Trusted secondary reference


class ReuseStatus(str, Enum):
    GREEN = "GREEN"    # Unrestricted canonical / educational reuse
    YELLOW = "YELLOW"  # Terminology reference allowed; independent prose required
    RED = "RED"        # Reference only; no ingestion


class DedupDecision(str, Enum):
    NEW_CANONICAL = "NEW_CANONICAL"
    EXACT_DUPLICATE = "EXACT_DUPLICATE"
    VARIANT_OF = "VARIANT_OF"
    ABBREVIATION_OF = "ABBREVIATION_OF"
    SYNONYM_CANDIDATE = "SYNONYM_CANDIDATE"
    POSSIBLE_DIFFERENT_SENSE = "POSSIBLE_DIFFERENT_SENSE"
    NEEDS_REVIEW = "NEEDS_REVIEW"


class SenseDecision(str, Enum):
    SAME_SENSE = "SAME_SENSE"
    DIFFERENT_SENSE = "DIFFERENT_SENSE"
    AMBIGUOUS = "AMBIGUOUS"
    HUMAN_REVIEW = "HUMAN_REVIEW"


class SourceReadiness(str, Enum):
    READY = "READY"
    PARTIAL = "PARTIAL"
    BLOCKED = "BLOCKED"


@dataclass
class SourceEvidence:
    source_id: str
    source_version: str
    source_record_id: str
    source_locator: str
    source_term_exact: str
    source_context: str
    authority_class: str
    reuse_status: str
    raw_snapshot_hash: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ExtractedCandidate:
    candidate_id: str
    source_id: str
    source_version: str
    source_record_id: str
    source_locator: str
    source_term_exact: str
    source_context: str
    source_definition: Optional[str] = None
    extracted_at: str = ""
    extractor_version: str = "1.2.0"
    raw_snapshot_hash: str = ""
    primary_domain: str = "business"
    subdomain: str = ""
    authority_class: str = "A"
    reuse_status: str = "GREEN"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class NormalizedCandidate:
    normalized_id: str
    candidate_id: str
    source_term_exact: str
    normalized_surface: str
    domain: str
    subdomain: str
    source_id: str
    source_version: str
    source_record_id: str
    source_locator: str
    source_context: str
    authority_class: str
    reuse_status: str
    is_variant: bool = False
    is_abbreviation: bool = False
    raw_snapshot_hash: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class CanaryCandidate:
    candidate_id: str
    surface: str
    normalized_surface: str
    source_evidence: List[Dict[str, Any]]
    dedup_decision: str
    existing_canonical_id: Optional[str]
    sense_decision: str
    domain: str
    subdomain: str
    authority_class: str
    reuse_status: str
    pro_level_candidate: str
    priority: Dict[str, Any]
    status: str = "candidate"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
