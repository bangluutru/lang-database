"""
scripts/phase1_3a/batch_selector.py
Phase 1.3A & 1.3A.1 Review Batch Selector, Domain Balancing, and Quality Gate Enforcement.

Enforces Section 27 Quality Gate & Section 26 Review Pack Format:
- Field-level provenance on every candidate (term, reading, gloss)
- Source provenance, valid domain, non-empty surface
- Exclusion of extraction artifacts and non-canonical composite reporting labels
- Domain balancing: prevents EDINET/accounting from dominating
- Strict human decision boundary: human_decision = "PENDING"
- Ordering: REVIEW-C -> REVIEW-B -> REVIEW-A (within level: domain -> canonical risk -> relevance)
"""

from typing import List, Dict, Set, Tuple, Any
from collections import defaultdict
import json
from pathlib import Path

from scripts.phase1_3a.models import (
    NormalizedCandidate,
    ReviewCandidate,
    QualityFlag,
    ReviewComplexity,
    AIRecommendation
)
from scripts.phase1_3a.linguistic_enhancer import Phase13LinguisticEnhancer
from scripts.phase1_3a.relevance_scorer import (
    compute_canonical_value_score,
    compute_professional_relevance_score,
    assign_review_complexity_and_ai_recommendation,
    HIGH_PRIORITY_DOMAINS
)


class Phase13BatchSelector:
    def __init__(self, target_min: int = 800, target_max: int = 1500):
        self.target_min = target_min
        self.target_max = target_max
        self.enhancer = Phase13LinguisticEnhancer()

    def process_and_select(
        self, candidates: List[NormalizedCandidate]
    ) -> Tuple[List[ReviewCandidate], Dict[str, Any]]:
        """
        Processes normalized candidates, generates readings/glosses, computes scores,
        applies the Section 27 batch quality gate and domain balancing,
        and outputs sorted ReviewCandidate instances.
        """
        evaluated: List[ReviewCandidate] = []
        rejected_artifacts_count = 0
        rejected_composite_count = 0

        for cand in candidates:
            # Section 27 Quality Gate
            # 1. Reject extraction artifacts
            if QualityFlag.ARTIFACT_FLAG in cand.quality_flags:
                rejected_artifacts_count += 1
                continue

            # 2. Reject non-canonical composite financial reporting labels
            # Section 14: Composite financial-statement labels should normally not enter review batch
            if cand.is_composite_taxonomy or QualityFlag.TAXONOMY_VARIANT_FLAG in cand.quality_flags:
                surface = cand.normalized_surface
                if "及び" in surface or "、" in surface or "純額" in surface:
                    rejected_composite_count += 1
                    continue

            # 3. Minimum length / validity check
            if len(cand.normalized_surface) < 2:
                continue

            # Generate reading with provenance
            reading, r_conf, r_flags, reading_prov = self.enhancer.generate_reading(
                cand.normalized_surface, include_provenance=True
            )

            # Generate gloss with provenance
            gloss, g_conf, g_flags, gloss_prov = self.enhancer.extract_or_generate_gloss(
                cand, include_provenance=True
            )

            # Combine all flags
            all_flags = list(set(cand.quality_flags + r_flags + g_flags))

            # Canonical value score
            c_val = compute_canonical_value_score(cand)

            # Professional relevance score
            relevance = compute_professional_relevance_score(
                candidate=cand,
                canonical_val=c_val,
                reading_conf=r_conf,
                gloss_conf=g_conf,
                gloss=gloss
            )

            # Review complexity & AI recommendation
            complexity, ai_rec, ai_reason = assign_review_complexity_and_ai_recommendation(
                candidate=cand,
                canonical_val=c_val,
                reading_conf=r_conf,
                gloss_conf=g_conf,
                flags=all_flags
            )

            # Convert flags to strings for JSON serialization
            flag_strings = [f.value if hasattr(f, "value") else str(f) for f in all_flags]

            seq_id = len(evaluated) + 1
            review_cand = ReviewCandidate(
                candidate_id=f"phase13a-cand-{seq_id:06d}",
                surface=cand.surface,
                reading=reading,
                meaning_gloss=gloss,
                domain=cand.domain,
                subdomain=cand.subdomain,
                source_ids=cand.source_ids,
                authority_class=cand.source_authorities[0] if cand.source_authorities else "C",
                term_provenance=cand.term_provenance,
                reading_provenance=reading_prov,
                gloss_provenance=gloss_prov,
                evidence_refs=cand.evidence_refs,
                cross_source_count=len(set(cand.source_ids)),
                professional_relevance_score=relevance,
                canonical_value_score=c_val,
                review_complexity=complexity.value,
                quality_flags=flag_strings,
                normalized_surface=cand.normalized_surface,
                reading_confidence=r_conf,
                gloss_confidence=g_conf,
                possible_duplicate_of=cand.possible_duplicate_of,
                possible_variant_of=cand.possible_variant_of,
                possible_abbreviation_of=cand.possible_abbreviation_of,
                ai_recommendation=ai_rec.value,
                ai_reason=ai_reason,
                human_decision="PENDING"  # MANDATORY INVARIANT
            )
            evaluated.append(review_cand)

        # Domain Balancing (Section 6 & 7):
        # Prevent EDINET/accounting from dominating.
        domain_groups = defaultdict(list)
        for c in evaluated:
            domain_groups[c.domain].append(c)

        for dom in domain_groups:
            domain_groups[dom].sort(
                key=lambda x: (
                    x.cross_source_count,
                    x.canonical_value_score,
                    x.professional_relevance_score
                ),
                reverse=True
            )

        selected: List[ReviewCandidate] = []

        domain_caps = {
            "accounting": 220,
            "finance": 150,
            "business": 120,
            "management": 80,
            "office_communication": 60,
            "tax": 250,
            "trade": 200,
            "hr": 200,
            "legal": 200,
            "purchasing": 120,
            "sales": 100
        }

        for dom, cands in domain_groups.items():
            cap = domain_caps.get(dom, 150)
            selected.extend(cands[:cap])

        if len(selected) < self.target_min:
            selected_ids = {c.candidate_id for c in selected}
            remaining = [c for c in evaluated if c.candidate_id not in selected_ids]
            remaining.sort(key=lambda x: x.professional_relevance_score, reverse=True)
            needed = self.target_min - len(selected)
            selected.extend(remaining[:needed])

        if len(selected) > self.target_max:
            selected.sort(key=lambda x: x.professional_relevance_score, reverse=True)
            selected = selected[:self.target_max]

        # Section 30: Review Pack Ordering:
        # REVIEW-C -> REVIEW-B -> REVIEW-A
        # Within each level: domain -> canonical risk (lowest canonical_val first) -> relevance (descending)
        complexity_order = {"REVIEW-C": 1, "REVIEW-B": 2, "REVIEW-A": 3}
        selected.sort(
            key=lambda c: (
                complexity_order.get(c.review_complexity, 9),
                c.domain,
                c.canonical_value_score,
                -c.professional_relevance_score
            )
        )

        for idx, cand in enumerate(selected, start=1):
            cand.candidate_id = f"phase13a-cand-{idx:06d}"

        stats = {
            "total_evaluated": len(evaluated),
            "rejected_artifacts": rejected_artifacts_count,
            "rejected_composite_taxonomy": rejected_composite_count,
            "final_review_candidates": len(selected),
            "review_complexity_breakdown": {
                "REVIEW-A": sum(1 for c in selected if c.review_complexity == "REVIEW-A"),
                "REVIEW-B": sum(1 for c in selected if c.review_complexity == "REVIEW-B"),
                "REVIEW-C": sum(1 for c in selected if c.review_complexity == "REVIEW-C")
            },
            "provenance_breakdown": {
                "OFFICIAL_EXTRACTED": sum(1 for c in selected if c.term_provenance == "OFFICIAL_EXTRACTED"),
                "OFFICIAL_CURATED": sum(1 for c in selected if c.term_provenance == "OFFICIAL_CURATED"),
                "INTERNAL_CURATED": sum(1 for c in selected if c.term_provenance == "INTERNAL_CURATED"),
                "MODEL_ASSISTED": sum(1 for c in selected if c.term_provenance == "MODEL_ASSISTED")
            },
            "domain_breakdown": {
                dom: sum(1 for c in selected if c.domain == dom)
                for dom in sorted(list({c.domain for c in selected}))
            }
        }

        return selected, stats
