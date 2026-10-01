"""
scripts/phase1_3a/relevance_scorer.py
Phase 1.3A & 1.3A.1 Deterministic Professional Relevance and Canonical Value Scoring.

Computes transparent, multi-dimensional relevance scores and assigns review complexity:
- source_authority & provenance_type (Section 17)
- professional_specificity
- cross_source_support
- canonical_value
- domain_need
- reading_confidence
- gloss_quality
- review_complexity (REVIEW-A, REVIEW-B, REVIEW-C)
- ai_recommendation & ai_reason
"""

from typing import List, Tuple, Dict, Any
import re

from scripts.phase1_3a.models import (
    NormalizedCandidate,
    QualityFlag,
    ReviewComplexity,
    AIRecommendation,
    ProvenanceType
)


HIGH_PRIORITY_DOMAINS = {"tax", "trade", "hr", "legal", "purchasing", "sales"}


def compute_canonical_value_score(candidate: NormalizedCandidate) -> float:
    """Calculates canonical concept value score [0.0 - 1.0]."""
    surface = candidate.normalized_surface

    if candidate.is_composite_taxonomy or QualityFlag.TAXONOMY_VARIANT_FLAG in candidate.quality_flags:
        if "及び" in surface or "、" in surface or "純額" in surface:
            return 0.15
        return 0.40

    if QualityFlag.ARTIFACT_FLAG in candidate.quality_flags:
        return 0.0

    if QualityFlag.ABBREVIATION_FLAG in candidate.quality_flags:
        return 0.70

    if QualityFlag.VARIANT_FLAG in candidate.quality_flags:
        return 0.65

    kanji_count = len(re.findall(r"[\u4e00-\u9faf]", surface))
    total_len = len(surface)

    if 2 <= total_len <= 8 and kanji_count >= 2:
        return 0.95
    elif 9 <= total_len <= 15:
        return 0.85
    elif total_len > 25:
        return 0.60
    return 0.75


def compute_professional_relevance_score(
    candidate: NormalizedCandidate,
    canonical_val: float,
    reading_conf: str,
    gloss_conf: str,
    gloss: str
) -> float:
    """
    Computes deterministic professional relevance score [0.0 - 100.0]
    combining source authority, provenance type, cross-source support, professional specificity,
    domain priority, and linguistic confidence.
    """
    auth_scores = {"A": 1.0, "B": 0.8, "C": 0.6, "D": 0.4}
    primary_auth = candidate.source_authorities[0] if candidate.source_authorities else "C"
    auth_score = auth_scores.get(primary_auth, 0.6)

    prov_weights = {
        ProvenanceType.OFFICIAL_EXTRACTED.value: 1.0,
        ProvenanceType.OFFICIAL_CURATED.value: 0.90,
        ProvenanceType.INTERNAL_CURATED.value: 0.75,
        ProvenanceType.MODEL_ASSISTED.value: 0.60
    }
    prov_score = prov_weights.get(candidate.term_provenance, 0.80)

    cross_count = len(set(candidate.source_ids))
    cross_score = min(1.0, 0.5 + 0.25 * (cross_count - 1))

    surface = candidate.normalized_surface
    kanji_ratio = len(re.findall(r"[\u4e00-\u9faf]", surface)) / max(1, len(surface))
    if kanji_ratio >= 0.5 and 2 <= len(surface) <= 12:
        spec_score = 0.95
    else:
        spec_score = 0.75

    r_score = 1.0 if reading_conf == "HIGH" else (0.75 if reading_conf == "MEDIUM" else 0.4)
    g_score = 1.0 if gloss_conf == "HIGH" else (0.75 if gloss_conf == "MEDIUM" else 0.4)
    if QualityFlag.MALFORMED_PARENTHESES in candidate.quality_flags:
        g_score -= 0.2
    if QualityFlag.TRUNCATED_GLOSS in candidate.quality_flags:
        g_score -= 0.2

    domain_multiplier = 1.15 if candidate.domain in HIGH_PRIORITY_DOMAINS else 1.0

    raw_score = (
        0.20 * auth_score +
        0.10 * prov_score +
        0.20 * cross_score +
        0.20 * canonical_val +
        0.15 * spec_score +
        0.08 * r_score +
        0.07 * g_score
    ) * domain_multiplier * 100.0

    return round(min(100.0, max(0.0, raw_score)), 2)


def assign_review_complexity_and_ai_recommendation(
    candidate: NormalizedCandidate,
    canonical_val: float,
    reading_conf: str,
    gloss_conf: str,
    flags: List[QualityFlag]
) -> Tuple[ReviewComplexity, AIRecommendation, str]:
    """
    Classifies review complexity per Phase 1.3A Section 25 and Phase 1.3A.1 Section 17:
    - REVIEW-C: Potentially problematic, abbreviation, variant, composite label, low confidence reading
    - REVIEW-B: Valid term but reading/gloss/curated origin deserves review
    - REVIEW-A: High confidence canonical professional term (likely approve as-is)
    """
    # 1. REVIEW-C criteria
    if candidate.is_composite_taxonomy or QualityFlag.TAXONOMY_VARIANT_FLAG in flags:
        return (
            ReviewComplexity.REVIEW_C,
            AIRecommendation.REJECT_NON_CANONICAL,
            "Composite financial statement reporting label; non-atomic canonical concept."
        )

    if QualityFlag.ARTIFACT_FLAG in flags:
        return (
            ReviewComplexity.REVIEW_C,
            AIRecommendation.REJECT_ARTIFACT,
            "Navigational or structural extraction artifact."
        )

    if candidate.possible_abbreviation_of or QualityFlag.ABBREVIATION_FLAG in flags:
        full = candidate.possible_abbreviation_of or "canonical full form"
        return (
            ReviewComplexity.REVIEW_C,
            AIRecommendation.ABBREVIATION_OF,
            f"Professional abbreviation; map as relationship to canonical full form: {full}."
        )

    if candidate.possible_variant_of or QualityFlag.VARIANT_FLAG in flags:
        return (
            ReviewComplexity.REVIEW_C,
            AIRecommendation.VARIANT_OF,
            f"Spelling or taxonomy variant of canonical term: {candidate.possible_variant_of}."
        )

    if QualityFlag.SEMANTIC_DUPLICATE_FLAG in flags:
        return (
            ReviewComplexity.REVIEW_C,
            AIRecommendation.POSSIBLE_DUPLICATE,
            f"Possible semantic duplicate of existing concept: {candidate.possible_duplicate_of}."
        )

    if reading_conf == "LOW":
        return (
            ReviewComplexity.REVIEW_C,
            AIRecommendation.APPROVE_WITH_READING_REVIEW,
            "Reading generated with low phonetic confidence; human review of reading required."
        )

    if QualityFlag.MALFORMED_PARENTHESES in flags or QualityFlag.TRUNCATED_GLOSS in flags:
        return (
            ReviewComplexity.REVIEW_C,
            AIRecommendation.APPROVE_WITH_GLOSS_REVIEW,
            "English gloss has malformed parenthesis or truncated syntax; gloss revision required."
        )

    if canonical_val < 0.65:
        return (
            ReviewComplexity.REVIEW_C,
            AIRecommendation.MANUAL_REVIEW_REQUIRED,
            "Borderline canonical value score; manual verification recommended."
        )

    if candidate.term_provenance == ProvenanceType.MODEL_ASSISTED.value and len(set(candidate.source_ids)) < 2:
        return (
            ReviewComplexity.REVIEW_C,
            AIRecommendation.MANUAL_REVIEW_REQUIRED,
            "Model-assisted term without independent corroboration; detailed review required."
        )

    # 2. REVIEW-B criteria
    # Section 17: INTERNAL_CURATED normally at least REVIEW-B unless independently corroborated
    if candidate.term_provenance == ProvenanceType.INTERNAL_CURATED.value and len(set(candidate.source_ids)) < 2:
        return (
            ReviewComplexity.REVIEW_B,
            AIRecommendation.APPROVE_WITH_GLOSS_REVIEW,
            "Internal curated catalog source; corroborate against official reference."
        )

    if reading_conf == "MEDIUM" or QualityFlag.READING_REVIEW_REQUIRED in flags:
        return (
            ReviewComplexity.REVIEW_B,
            AIRecommendation.APPROVE_WITH_READING_REVIEW,
            "Valid professional concept; verify compound phonetic reading."
        )

    if gloss_conf != "HIGH" or QualityFlag.GLOSS_REVIEW_REQUIRED in flags:
        return (
            ReviewComplexity.REVIEW_B,
            AIRecommendation.APPROVE_WITH_GLOSS_REVIEW,
            "Valid professional concept; verify English definition precision."
        )

    # 3. REVIEW-A criteria
    if candidate.term_provenance == ProvenanceType.OFFICIAL_CURATED.value:
        return (
            ReviewComplexity.REVIEW_A,
            AIRecommendation.APPROVE_AS_IS,
            "High-confidence professional term curated from authoritative statutory reference with verified reading and gloss."
        )

    return (
        ReviewComplexity.REVIEW_A,
        AIRecommendation.APPROVE_AS_IS,
        "High-confidence canonical professional term from authoritative primary source with verified reading and gloss."
    )
