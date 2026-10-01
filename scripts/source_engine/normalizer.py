"""
scripts/source_engine/normalizer.py
Candidate normalization engine for Phase 1.2B.
Performs Unicode NFKC standardization, bracket and whitespace cleanup,
variant and abbreviation detection, while preserving the exact original source form.
"""

import unicodedata
import re
from typing import Tuple

from scripts.source_engine.models import ExtractedCandidate, NormalizedCandidate

KNOWN_ABBREVIATIONS = {
    "FOB", "CIF", "CFR", "DDP", "EXW", "FCA", "CIP", "CPT", "DAP", "DPU",
    "B/L", "L/C", "D/P", "D/A", "T/T", "AWB", "S/I", "NACCS", "AEO", "HS",
    "PO", "SOP", "RFP", "SLA", "NDA", "KPI", "PDCA", "BCP", "CSR", "J-SOX",
    "IPO", "IR", "ROA", "ROE", "EBITDA", "CF", "BS", "PL"
}


class TermNormalizer:
    @staticmethod
    def normalize_text(text: str) -> str:
        if not text:
            return ""
        # 1. Unicode NFKC normalization
        norm = unicodedata.normalize("NFKC", text)
        # 2. Trim whitespace
        norm = norm.strip()
        # 3. Standardize full-width brackets and punctuation
        norm = norm.replace("（", "(").replace("）", ")")
        norm = norm.replace("【", "[").replace("】", "]")
        # 4. Strip leading/trailing bullets and dashes
        norm = re.sub(r"^[・\-\*\s]+", "", norm)
        norm = re.sub(r"[・\-\*\s]+$", "", norm)
        # 5. Clean parenthetical annotations if they are purely redundant descriptions or Latin abbreviations
        # e.g. "インコタームズ(Incoterms)" -> "インコタームズ"
        parenthetical_match = re.match(r"^([^\(\)]+)\s*\([A-Za-z0-9\s\/\-_]+\)$", norm)
        if parenthetical_match:
            base_part = parenthetical_match.group(1).strip()
            if len(base_part) >= 2:
                norm = base_part
        return norm

    @classmethod
    def process_candidate(cls, cand: ExtractedCandidate, seq_num: int) -> NormalizedCandidate:
        raw_surface = cand.source_term_exact
        normalized_surface = cls.normalize_text(raw_surface)

        is_abbrev = normalized_surface in KNOWN_ABBREVIATIONS or bool(re.match(r"^[A-Z0-9\/\-]+$", normalized_surface))
        is_variant = (normalized_surface != raw_surface)

        return NormalizedCandidate(
            normalized_id=f"norm-{seq_num:06d}",
            candidate_id=cand.candidate_id,
            source_term_exact=raw_surface,
            normalized_surface=normalized_surface,
            domain=cand.primary_domain,
            subdomain=cand.subdomain,
            source_id=cand.source_id,
            source_version=cand.source_version,
            source_record_id=cand.source_record_id,
            source_locator=cand.source_locator,
            source_context=cand.source_context,
            authority_class=cand.authority_class,
            reuse_status=cand.reuse_status,
            is_variant=is_variant,
            is_abbreviation=is_abbrev,
            raw_snapshot_hash=cand.raw_snapshot_hash
        )
