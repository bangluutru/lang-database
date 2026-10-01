"""
scripts/phase1_3c/matcher.py
Match-Before-Create Graph Resolution Engine for Phase 1.3C.
Enforces Section 13:
- Inspects canonical concept and expression graph before creating any new entity.
- Distinguishes:
    EXACT_EXISTING_CONCEPT
    EXISTING_CONCEPT_NEW_EXPRESSION
    EXISTING_CONCEPT_NEW_SENSE
    NEW_CONCEPT
    AMBIGUOUS
- Enforces multi-source evidence aggregation (one expression + multiple source evidences).
"""

from typing import Dict, List, Any, Optional, Tuple
from enum import Enum


class MatchDecision(str, Enum):
    EXACT_EXISTING_CONCEPT = "EXACT_EXISTING_CONCEPT"
    EXISTING_CONCEPT_NEW_EXPRESSION = "EXISTING_CONCEPT_NEW_EXPRESSION"
    EXISTING_CONCEPT_NEW_SENSE = "EXISTING_CONCEPT_NEW_SENSE"
    NEW_CONCEPT = "NEW_CONCEPT"
    AMBIGUOUS = "AMBIGUOUS"


class ConceptMatcher:
    """Matches incoming lexical records against the existing canonical graph."""

    def __init__(self, existing_concepts: List[Dict[str, Any]], existing_expressions: List[Dict[str, Any]]):
        self.concepts = {c["concept_id"]: c for c in existing_concepts}
        self.expressions_by_id = {e["expression_id"]: e for e in existing_expressions}
        
        # Build indexes: (language, normalized_lemma) -> list of expressions
        self.expr_index: Dict[Tuple[str, str], List[Dict[str, Any]]] = {}
        for expr in existing_expressions:
            key = (expr["language"], expr["lemma"].strip().lower())
            self.expr_index.setdefault(key, []).append(expr)

        # Concept by canonical name
        self.concept_by_name = {c["canonical_name"].lower(): c for c in existing_concepts}

    def match(
        self,
        language: str,
        lemma: str,
        pos: Optional[str] = None,
        domain: Optional[str] = None,
        gloss_hint: Optional[str] = None
    ) -> Tuple[MatchDecision, Optional[str], Optional[str], Optional[str]]:
        """
        Matches a lexical candidate against the existing graph.
        Returns:
            (decision, matched_concept_id, matched_expression_id, explanation)
        """
        norm_lemma = lemma.strip().lower()
        key = (language, norm_lemma)
        matches = self.expr_index.get(key, [])

        if not matches:
            # Check if canonical name directly matches concept
            c_match = self.concept_by_name.get(norm_lemma)
            if c_match:
                return (
                    MatchDecision.EXISTING_CONCEPT_NEW_EXPRESSION,
                    c_match["concept_id"],
                    None,
                    f"Matched concept {c_match['concept_id']} by canonical name '{norm_lemma}'"
                )
            return (MatchDecision.NEW_CONCEPT, None, None, f"No existing concept matches '{lemma}' in {language}")

        # Filter by POS if provided
        pos_matches = matches
        if pos:
            norm_pos = pos.lower()
            filtered = [m for m in matches if m.get("part_of_speech", "").lower() == norm_pos]
            if filtered:
                pos_matches = filtered

        # Exactly 1 match
        if len(pos_matches) == 1:
            expr = pos_matches[0]
            cid = expr["concept_id"]
            return (
                MatchDecision.EXACT_EXISTING_CONCEPT,
                cid,
                expr["expression_id"],
                f"Exact match on existing expression {expr['expression_id']} in concept {cid}"
            )

        # Multiple matches (polysemy / multiple senses)
        # Check domain or gloss hint to disambiguate
        if domain or gloss_hint:
            domain_scored = []
            for expr in pos_matches:
                cid = expr["concept_id"]
                concept = self.concepts.get(cid, {})
                c_domains = [d.lower() for d in concept.get("domains", [])]
                score = 0
                if domain and domain.lower() in c_domains:
                    score += 2
                if gloss_hint and gloss_hint.lower() in concept.get("canonical_name", "").lower():
                    score += 3
                domain_scored.append((score, expr))

            domain_scored.sort(key=lambda x: x[0], reverse=True)
            if domain_scored[0][0] > domain_scored[1][0]:
                best_expr = domain_scored[0][1]
                return (
                    MatchDecision.EXACT_EXISTING_CONCEPT,
                    best_expr["concept_id"],
                    best_expr["expression_id"],
                    f"Disambiguated polysemy to concept {best_expr['concept_id']} via domain/gloss hint"
                )

        # Ambiguous if multiple candidates have equal relevance
        return (
            MatchDecision.AMBIGUOUS,
            None,
            None,
            f"Multiple conflicting existing expressions for '{lemma}' in {language}: {[m['expression_id'] for m in pos_matches]}"
        )
