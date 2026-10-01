"""
scripts/phase1_3a/models.py
Data models and type definitions for Phase 1.3A: Large-Scale Professional Vocabulary Expansion.
"""

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Any
from enum import Enum


class AuthorityClass(str, Enum):
    A = "A"  # Primary official / statutory / regulatory
    B = "B"  # Official professional institution
    C = "C"  # Official business-support institution
    D = "D"  # Trusted secondary reference


class ReviewComplexity(str, Enum):
    REVIEW_A = "REVIEW-A"  # High confidence canonical professional term (likely approve as-is)
    REVIEW_B = "REVIEW-B"  # Valid professional term, minor review on reading/gloss/domain
    REVIEW_C = "REVIEW-C"  # High attention (abbreviation, variant, compound, low confidence reading, taxonomy-derived)


class AIRecommendation(str, Enum):
    APPROVE_AS_IS = "APPROVE_AS_IS"
    APPROVE_WITH_READING_REVIEW = "APPROVE_WITH_READING_REVIEW"
    APPROVE_WITH_GLOSS_REVIEW = "APPROVE_WITH_GLOSS_REVIEW"
    ABBREVIATION_OF = "ABBREVIATION_OF"
    VARIANT_OF = "VARIANT_OF"
    POSSIBLE_DUPLICATE = "POSSIBLE_DUPLICATE"
    DIFFERENT_SENSE = "DIFFERENT_SENSE"
    REJECT_ARTIFACT = "REJECT_ARTIFACT"
    REJECT_NON_CANONICAL = "REJECT_NON_CANONICAL"
    MANUAL_REVIEW_REQUIRED = "MANUAL_REVIEW_REQUIRED"


class QualityFlag(str, Enum):
    READING_REVIEW_REQUIRED = "READING_REVIEW_REQUIRED"
    GLOSS_REVIEW_REQUIRED = "GLOSS_REVIEW_REQUIRED"
    CANONICAL_VALUE_REVIEW_REQUIRED = "CANONICAL_VALUE_REVIEW_REQUIRED"
    ABBREVIATION_FLAG = "ABBREVIATION_FLAG"
    VARIANT_FLAG = "VARIANT_FLAG"
    SEMANTIC_DUPLICATE_FLAG = "SEMANTIC_DUPLICATE_FLAG"
    ARTIFACT_FLAG = "ARTIFACT_FLAG"
    TAXONOMY_VARIANT_FLAG = "TAXONOMY_VARIANT_FLAG"
    TRUNCATED_GLOSS = "TRUNCATED_GLOSS"
    MALFORMED_PARENTHESES = "MALFORMED_PARENTHESES"


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
    source_definition: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class RawCandidate:
    candidate_id: str
    source_id: str
    source_version: str
    source_record_id: str
    source_locator: str
    source_term_exact: str
    source_context: str
    source_definition: Optional[str] = None
    extracted_at: str = ""
    extractor_version: str = "1.3.0"
    raw_snapshot_hash: str = ""
    primary_domain: str = "business"
    subdomain: str = ""
    authority_class: str = "A"
    reuse_status: str = "GREEN"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class NormalizedCandidate:
    candidate_id: str
    surface: str
    normalized_surface: str
    domain: str
    subdomain: str
    source_ids: List[str] = field(default_factory=list)
    source_authorities: List[str] = field(default_factory=list)
    source_locators: List[str] = field(default_factory=list)
    source_contexts: List[str] = field(default_factory=list)
    source_definitions: List[str] = field(default_factory=list)
    quality_flags: List[QualityFlag] = field(default_factory=list)
    reading: str = ""
    reading_confidence: str = "HIGH"
    meaning_gloss: str = ""
    gloss_confidence: str = "HIGH"
    authority_class: str = "A"
    reuse_status: str = "GREEN"
    is_abbreviation: bool = False
    is_variant: bool = False
    is_artifact: bool = False
    is_composite_taxonomy: bool = False
    possible_duplicate_of: Optional[str] = None
    possible_variant_of: Optional[str] = None
    possible_abbreviation_of: Optional[str] = None
    canonical_target: Optional[str] = None
    dedup_decision: str = "NEW_CANONICAL"
    sense_decision: str = "SAME_SENSE"
    extracted_at: str = ""
    extractor_version: str = "1.3.0"
    raw_snapshot_hash: str = ""

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["quality_flags"] = [f.value if hasattr(f, "value") else str(f) for f in self.quality_flags]
        return d


@dataclass
class ReviewCandidate:
    """Represents a candidate ready for human/LLM review in the Phase 1.3A review batch."""
    candidate_id: str
    surface: str
    normalized_surface: str
    reading: str
    reading_confidence: str
    domain: str
    subdomain: str
    meaning_gloss: str
    gloss_confidence: str
    source_ids: List[str]
    source_authority: str
    cross_source_count: int
    professional_relevance_score: float
    canonical_value_score: float
    review_complexity: str
    quality_flags: List[str] = field(default_factory=list)
    possible_duplicate_of: Optional[str] = None
    possible_variant_of: Optional[str] = None
    possible_abbreviation_of: Optional[str] = None
    ai_recommendation: str = AIRecommendation.APPROVE_AS_IS.value
    ai_reason: str = ""
    human_decision: str = "PENDING"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
