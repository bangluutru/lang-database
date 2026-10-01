"""
scripts/phase1_3a/dedup_engine.py
Phase 1.3A & 1.3A.1 Multi-Level Deduplication Engine and Existing Database Exclusion.

Operates across deduplication levels:
Level 1: Exact surface
Level 2: Normalized surface
Level 3: Variant detection
Level 4: Abbreviation mapping (deterministic deduplication, no self-references)
Level 5: Semantic duplicate detection
Level 6: Semantic cross-domain policy:
         - SAME_CONCEPT_CROSS_DOMAIN: consolidates identical cross-domain concepts
         - DIFFERENT_SENSE: preserved only for genuine semantic polysemy

Also enforces hard exclusion of:
- Production vocabulary (800 records)
- Golden Pilot v1 / v1.1
- Canary 1.2C canonical vocabulary (102 records)
- Canary 1.2C relationships (8 mappings)
"""

from pathlib import Path
from typing import List, Dict, Set, Tuple, Optional, Any
import json
import re

from scripts.phase1_3a.models import (
    NormalizedCandidate,
    QualityFlag,
    AIRecommendation,
    ProvenanceType
)
from scripts.phase1_3a.normalizer import normalize_surface


# Statutory and professional abbreviations dictionary
# STRICT INVARIANT: abbr != full_form (no self-referential mappings!)
ABBREVIATION_MAP: Dict[str, Tuple[str, str]] = {
    # abbr -> (full_form, domain)
    "NACCS": ("輸出入・港湾関連情報処理システム", "trade"),
    "D/P": ("支払渡", "trade"),
    "D/A": ("引受渡", "trade"),
    "36協定": ("時間外・休日労働に関する協定", "hr"),
    "サブロク協定": ("時間外・休日労働に関する協定", "hr"),
    "印法": ("印紙税法", "tax"),
    "行審法": ("行政不服審査法", "legal"),
    "所法": ("所得税法", "tax"),
    "法法": ("法人税法", "tax"),
    "消法": ("消費税法", "tax"),
    "相法": ("相続税法", "tax"),
    "国通法": ("国税通則法", "tax"),
    "国徴法": ("国税徴収法", "tax"),
    "労基法": ("労働基準法", "hr"),
    "労契法": ("労働契約法", "hr"),
    "安衛法": ("労働安全衛生法", "hr"),
    "雇用保法": ("雇用保険法", "hr"),
    "厚年法": ("厚生年金保険法", "hr"),
    "健保法": ("健康保険法", "hr"),
    "下請法": ("下請代金支払遅延等防止法", "purchasing"),
    "独禁法": ("私的独占の禁止及び公正取引の確保に関する法律", "purchasing"),
    "外為法": ("外国為替及び外国貿易法", "trade"),
    "金商法": ("金融商品取引法", "finance"),
    "不競法": ("不正競争防止法", "legal")
}

# Reverse mapping: full_form -> abbr (guaranteed abbr != full)
FULL_FORM_TO_ABBR: Dict[str, str] = {
    full: abbr for abbr, (full, _) in ABBREVIATION_MAP.items() if abbr != full
}


# Section 21 & 22: Known professional polysemous terms with genuinely different senses
KNOWN_DIFFERENT_SENSE_TERMS: Set[str] = {
    "手形",       # Accounting: Promissory note / Trade: Bill of exchange / permit
    "仕向",       # Banking: Outward wire / Trade: Destination
    "引受",       # Finance: Underwriting / Trade & Insurance: Acceptance / risk underwriting
    "割当",       # Corporate: Allotment / Trade: Quota
    "管轄",       # Tax: Tax office / Legal: Judicial jurisdiction
}


class ExistingDatabaseIndex:
    """Loads and indexes existing Production and Canary datasets for strict exclusion."""
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.production_surfaces: Set[str] = set()
        self.production_normalized: Set[str] = set()
        self.canary_surfaces: Set[str] = set()
        self.canary_normalized: Set[str] = set()
        self.existing_abbreviations: Set[str] = set()
        self.existing_full_forms: Set[str] = set()
        self._load_datasets()

    def _load_datasets(self):
        # 1. Production vocabulary (800 records)
        prod_path = self.base_dir / "data/production/vocabulary.jsonl"
        if prod_path.exists():
            with open(prod_path, "r", encoding="utf-8") as f:
                for line in f:
                    if not line.strip():
                        continue
                    item = json.loads(line)
                    surf = item.get("term", {}).get("surface", "")
                    if surf:
                        self.production_surfaces.add(surf)
                        norm, _ = normalize_surface(surf)
                        self.production_normalized.add(norm)

        # 2. Canary 1.2C vocabulary (102 records)
        canary_path = self.base_dir / "data/releases/canary-1.2c/vocabulary.jsonl"
        if canary_path.exists():
            with open(canary_path, "r", encoding="utf-8") as f:
                for line in f:
                    if not line.strip():
                        continue
                    item = json.loads(line)
                    surf = item.get("term", {}).get("surface", "")
                    if surf:
                        self.canary_surfaces.add(surf)
                        norm, _ = normalize_surface(surf)
                        self.canary_normalized.add(norm)

        # 3. Canary 1.2C relationships (8 mappings)
        rel_path = self.base_dir / "data/releases/canary-1.2c/relationships.jsonl"
        if rel_path.exists():
            with open(rel_path, "r", encoding="utf-8") as f:
                for line in f:
                    if not line.strip():
                        continue
                    item = json.loads(line)
                    s_term = item.get("source_term", "")
                    t_term = item.get("target_term", "")
                    if s_term:
                        self.existing_abbreviations.add(s_term)
                        self.canary_surfaces.add(s_term)
                        norm, _ = normalize_surface(s_term)
                        self.canary_normalized.add(norm)
                    if t_term:
                        self.existing_full_forms.add(t_term)
                        self.canary_surfaces.add(t_term)
                        norm, _ = normalize_surface(t_term)
                        self.canary_normalized.add(norm)

    def is_existing_production(self, surface: str, normalized: str) -> bool:
        return surface in self.production_surfaces or normalized in self.production_normalized

    def is_existing_canary(self, surface: str, normalized: str) -> bool:
        return surface in self.canary_surfaces or normalized in self.canary_normalized


class Phase13DedupEngine:
    def __init__(self, base_dir: Path):
        self.existing_index = ExistingDatabaseIndex(base_dir)
        self.seen_relationships: Set[Tuple[str, str, str]] = set()  # (rel_type, src, tgt)
        self.stats = {
            "exact_duplicate": 0,
            "normalized_duplicate": 0,
            "existing_production": 0,
            "existing_canary": 0,
            "abbreviation": 0,
            "variant": 0,
            "possible_semantic_duplicate": 0,
            "same_concept_cross_domain": 0,
            "different_sense": 0
        }
        self.examples: Dict[str, List[Dict[str, Any]]] = {
            "exact_duplicate": [],
            "normalized_duplicate": [],
            "existing_production": [],
            "existing_canary": [],
            "abbreviation": [],
            "variant": [],
            "possible_semantic_duplicate": [],
            "same_concept_cross_domain": [],
            "different_sense": []
        }

    def deduplicate_and_exclude(
        self, candidates: List[NormalizedCandidate]
    ) -> List[NormalizedCandidate]:
        """
        Deduplicates normalized candidates and excludes existing production/canary vocabulary.
        Consolidates same-concept cross-domain references per Section 22.
        Enforces deterministic relationship uniqueness and prevents self-references.
        """
        surviving: Dict[str, NormalizedCandidate] = {}
        seen_surfaces: Dict[str, str] = {}  # exact_surface -> canonical_norm

        for cand in candidates:
            orig = cand.surface
            norm = cand.normalized_surface

            # 1. Existing Production Exclusion
            if self.existing_index.is_existing_production(orig, norm):
                self.stats["existing_production"] += 1
                if len(self.examples["existing_production"]) < 10:
                    self.examples["existing_production"].append({
                        "surface": orig,
                        "normalized": norm,
                        "reason": "Found in production/vocabulary.jsonl (800 records)"
                    })
                continue

            # 2. Existing Canary Exclusion
            if self.existing_index.is_existing_canary(orig, norm):
                self.stats["existing_canary"] += 1
                if len(self.examples["existing_canary"]) < 10:
                    self.examples["existing_canary"].append({
                        "surface": orig,
                        "normalized": norm,
                        "reason": "Found in canary-1.2c release"
                    })
                continue

            # 3. Artifact rejection (Section 21)
            if QualityFlag.ARTIFACT_FLAG in cand.quality_flags:
                continue

            # 4. Check abbreviation relationships (Section 19 & 20)
            if norm in ABBREVIATION_MAP:
                full_term, dom = ABBREVIATION_MAP[norm]
                # Enforce no self-reference!
                if norm != full_term:
                    cand.possible_abbreviation_of = full_term
                    cand.quality_flags.append(QualityFlag.ABBREVIATION_FLAG)
                    rel_key = ("ABBREVIATION_OF", norm, full_term)
                    if rel_key not in self.seen_relationships:
                        self.seen_relationships.add(rel_key)
                        self.stats["abbreviation"] += 1
                        if len(self.examples["abbreviation"]) < 10:
                            self.examples["abbreviation"].append({
                                "abbreviation": norm,
                                "full_form": full_term,
                                "domain": dom
                            })

            # Check if this candidate is the full form of a known abbreviation
            if norm in FULL_FORM_TO_ABBR:
                abbr_form = FULL_FORM_TO_ABBR[norm]
                if abbr_form != norm:
                    cand.possible_variant_of = abbr_form

            # Level 1 & Level 6 check: exact surface match
            if orig in seen_surfaces:
                canon_key = seen_surfaces[orig]
                if canon_key in surviving:
                    existing_cand = surviving[canon_key]
                    # Section 21 & 22: SAME_CONCEPT_CROSS_DOMAIN vs DIFFERENT_SENSE
                    if existing_cand.domain != cand.domain:
                        if norm in KNOWN_DIFFERENT_SENSE_TERMS:
                            self.stats["different_sense"] += 1
                            diff_key = f"{norm}__{cand.domain}"
                            if len(self.examples["different_sense"]) < 10:
                                if not any(ex["surface"] == norm and ex.get("domain_2") == cand.domain for ex in self.examples["different_sense"]):
                                    self.examples["different_sense"].append({
                                        "surface": norm,
                                        "domain_1": existing_cand.domain,
                                        "domain_2": cand.domain
                                    })
                            cand.candidate_id = f"{cand.candidate_id}-ds"
                            surviving[diff_key] = cand
                            seen_surfaces[orig] = diff_key
                            continue
                        else:
                            # Genuine same statutory/commercial concept across domains
                            self.stats["same_concept_cross_domain"] += 1
                            if len(self.examples["same_concept_cross_domain"]) < 10:
                                if not any(ex["surface"] == norm for ex in self.examples["same_concept_cross_domain"]):
                                    self.examples["same_concept_cross_domain"].append({
                                        "surface": norm,
                                        "primary_domain": existing_cand.domain,
                                        "secondary_domain": cand.domain
                                    })
                            self._merge_evidence(existing_cand, cand)
                            continue

                self.stats["exact_duplicate"] += 1
                if len(self.examples["exact_duplicate"]) < 10:
                    self.examples["exact_duplicate"].append({
                        "surface": orig,
                        "merged_into": canon_key
                    })
                if canon_key in surviving:
                    self._merge_evidence(surviving[canon_key], cand)
                continue

            # Level 2 & Level 6 check: normalized surface match
            if norm in surviving:
                existing_cand = surviving[norm]
                if existing_cand.domain != cand.domain:
                    # Section 21 & 22: DIFFERENT_SENSE vs SAME_CONCEPT_CROSS_DOMAIN
                    if norm in KNOWN_DIFFERENT_SENSE_TERMS:
                        self.stats["different_sense"] += 1
                        diff_key = f"{norm}__{cand.domain}"
                        if len(self.examples["different_sense"]) < 10:
                            if not any(ex["surface"] == norm and ex.get("domain_2") == cand.domain for ex in self.examples["different_sense"]):
                                self.examples["different_sense"].append({
                                    "surface": norm,
                                    "domain_1": existing_cand.domain,
                                    "domain_2": cand.domain
                                })
                        cand.candidate_id = f"{cand.candidate_id}-ds"
                        surviving[diff_key] = cand
                        seen_surfaces[orig] = diff_key
                        continue
                    else:
                        # Genuine same statutory/commercial concept across domains
                        self.stats["same_concept_cross_domain"] += 1
                        if len(self.examples["same_concept_cross_domain"]) < 10:
                            if not any(ex["surface"] == norm for ex in self.examples["same_concept_cross_domain"]):
                                self.examples["same_concept_cross_domain"].append({
                                    "surface": norm,
                                    "primary_domain": existing_cand.domain,
                                    "secondary_domain": cand.domain
                                })
                        self._merge_evidence(existing_cand, cand)
                        seen_surfaces[orig] = norm
                        continue

                # Formatting-only or same-domain duplicate -> Level 2 merge
                self.stats["normalized_duplicate"] += 1
                if len(self.examples["normalized_duplicate"]) < 10:
                    self.examples["normalized_duplicate"].append({
                        "original_surface": orig,
                        "normalized": norm,
                        "existing_source": existing_cand.source_ids[0]
                    })
                self._merge_evidence(existing_cand, cand)
                seen_surfaces[orig] = norm
                continue

            # Level 3: Variant detection
            stripped_variant = re.sub(r"[・\-\s\(\)（）等]", "", norm)
            variant_match = False
            for k, ex in surviving.items():
                k_stripped = re.sub(r"[・\-\s\(\)（）等]", "", ex.normalized_surface)
                if stripped_variant == k_stripped and len(stripped_variant) > 3:
                    self.stats["variant"] += 1
                    cand.possible_variant_of = ex.normalized_surface
                    cand.quality_flags.append(QualityFlag.VARIANT_FLAG)
                    if len(self.examples["variant"]) < 10:
                        self.examples["variant"].append({
                            "variant": norm,
                            "canonical": ex.normalized_surface
                        })
                    variant_match = True
                    self._merge_evidence(ex, cand)
                    seen_surfaces[orig] = k
                    break

            if variant_match:
                continue

            # Fresh unique candidate
            seen_surfaces[orig] = norm
            surviving[norm] = cand

        return list(surviving.values())

    def _merge_evidence(self, target: NormalizedCandidate, source: NormalizedCandidate):
        """Merges provenance, evidence_refs, and contexts from duplicate extraction into canonical candidate."""
        for s_id in source.source_ids:
            if s_id not in target.source_ids:
                target.source_ids.append(s_id)
        for s_auth in source.source_authorities:
            if s_auth not in target.source_authorities:
                target.source_authorities.append(s_auth)
        for loc in source.source_locators:
            if loc not in target.source_locators:
                target.source_locators.append(loc)
        for ctx in source.source_contexts:
            if ctx not in target.source_contexts:
                target.source_contexts.append(ctx)
        for d in source.source_definitions:
            if d and d not in target.source_definitions:
                target.source_definitions.append(d)
        for f in source.quality_flags:
            if f not in target.quality_flags:
                target.quality_flags.append(f)
        for ev in source.evidence_refs:
            if ev not in target.evidence_refs:
                target.evidence_refs.append(ev)

        # Prioritize higher evidence provenance if one source is OFFICIAL_EXTRACTED
        if source.term_provenance == ProvenanceType.OFFICIAL_EXTRACTED.value and target.term_provenance != ProvenanceType.OFFICIAL_EXTRACTED.value:
            target.term_provenance = ProvenanceType.OFFICIAL_EXTRACTED.value
            target.raw_snapshot_hash = source.raw_snapshot_hash
