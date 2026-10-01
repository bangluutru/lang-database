"""
scripts/source_engine/dedup_engine.py
Multi-stage Deduplication and Sense Resolution Engine for Phase 1.2B.
Compares normalized candidates against Golden Pilot v1.1, production database,
and candidate-to-candidate pools.
Preserves multi-source evidence and assigns explainable dedup/sense decisions.
"""

from typing import List, Dict, Tuple, Optional, Any
from pathlib import Path
import json

from scripts.source_engine.models import (
    NormalizedCandidate,
    DedupDecision,
    SenseDecision,
    CanaryCandidate,
    SourceEvidence
)

# Known abbreviation-to-canonical mappings
ABBREVIATION_PAIRS = {
    "FOB": "本船甲板渡し",
    "CIF": "運賃保険料込み条件",
    "CFR": "運賃込み条件",
    "DDP": "関税込持込渡し",
    "EXW": "工場渡し",
    "FCA": "運送人渡し",
    "CIP": "輸送費保険料込み条件",
    "CPT": "輸送費込み条件",
    "DAP": "仕向地持込渡し",
    "DPU": "荷卸込持込渡し",
    "B/L": "船荷証券",
    "L/C": "信用状",
    "T/T": "電信送金",
    "D/P": "支払渡し",
    "D/A": "引受渡し",
    "AWB": "航空貨物運送状",
    "S/I": "船積指図書",
    "NDA": "秘密保持契約",
    "PO": "発注書",
    "J-SOX": "内部統制",
    "RCEP": "地域的な包括的経済連携協定",
    "CPTPP": "環太平洋パートナーシップに関する包括的及び先進的な協定"
}

# Known orthographic / notation variants
KNOWN_VARIANTS_MAP = {
    "売掛金勘定": "売掛金",
    "買掛金勘定": "買掛金",
    "仕入高": "仕入",
    "売上高": "売上",
    "有給休暇": "年次有給休暇",
    "有休": "年次有給休暇",
    "36協定書": "36協定",
    "サブロク協定": "36協定",
    "取締役会決議": "取締役会",
    "代表取締役社長": "代表取締役",
    "インボイス": "適格請求書",
    "インボイス制度": "適格請求書等保存方式",
    "相みつ": "相見積もり",
    "あいみつ": "相見積もり"
}

# Polysemous professional terms where domain distinguishes sense
POLYSEMOUS_TERMS = {
    "決済": {
        "banking": "銀行間の資金決済・送金決済 (Financial Clearing & Settlement)",
        "accounting": "債権債務の決済・消込 (Clearing of Accounts / Settlement of Debt)",
        "securities": "株式・債券等の受渡決済 (Securities Settlement)"
    },
    "引当": {
        "accounting": "引当金の設定・繰入 (Accounting Provisioning)",
        "logistics": "倉庫在庫の引当・確保 (Inventory Allocation)",
        "banking": "担保・融資枠の引当 (Collateral Allocation)"
    },
    "清算": {
        "accounting": "仮払金や出張費の精算/清算 (Expense Clearance / Reimbursement)",
        "corporate_law": "会社の解散に伴う法的手続 (Corporate Liquidation)"
    },
    "査定": {
        "hr": "人事考課・勤務評定 (Employee Performance Assessment)",
        "tax": "課税標準額の決定・税額査定 (Tax Assessment)",
        "insurance": "損害保険の損害査定 (Insurance Loss Assessment)"
    }
}


class MultiStageDedupEngine:
    def __init__(self, golden_v1_1_path: Path, production_path: Path):
        self.golden_v1_1_path = golden_v1_1_path
        self.production_path = production_path
        self.canonical_index: Dict[str, Dict[str, Any]] = {}
        self.load_canonical_baselines()

    def load_canonical_baselines(self):
        """Loads Golden Pilot v1.1 and production records into indexing structures."""
        # Load production records
        if self.production_path.exists():
            with open(self.production_path, "r", encoding="utf-8") as f:
                for line in f:
                    if not line.strip():
                        continue
                    rec = json.loads(line)
                    surface = rec.get("term", {}).get("surface", "")
                    if surface:
                        self.canonical_index[surface] = {
                            "id": rec.get("id"),
                            "surface": surface,
                            "domain": rec.get("domain", {}).get("primary", ""),
                            "subdomain": rec.get("domain", {}).get("subdomain", ""),
                            "semantic_class": rec.get("domain", {}).get("semantic_class", ""),
                            "status": rec.get("status")
                        }

        # Ensure Golden Pilot v1.1 is indexed
        if self.golden_v1_1_path.exists():
            with open(self.golden_v1_1_path, "r", encoding="utf-8") as f:
                for line in f:
                    if not line.strip():
                        continue
                    rec = json.loads(line)
                    surface = rec.get("term", {}).get("surface", "")
                    if surface and surface not in self.canonical_index:
                        self.canonical_index[surface] = {
                            "id": rec.get("id"),
                            "surface": surface,
                            "domain": rec.get("domain", {}).get("primary", ""),
                            "subdomain": rec.get("domain", {}).get("subdomain", ""),
                            "semantic_class": rec.get("domain", {}).get("semantic_class", ""),
                            "status": rec.get("status")
                        }

    def evaluate_candidate(
        self,
        candidate: NormalizedCandidate,
        existing_pool_surfaces: Dict[str, CanaryCandidate]
    ) -> Tuple[DedupDecision, Optional[str], SenseDecision]:
        surface = candidate.normalized_surface
        domain = candidate.domain

        # 1. Exact Duplicate against Existing Canonical Baseline (Production / Golden Pilot)
        if surface in self.canonical_index:
            base_rec = self.canonical_index[surface]
            base_domain = base_rec["domain"]

            # Polysemous term check
            if surface in POLYSEMOUS_TERMS and domain != base_domain:
                return (
                    DedupDecision.POSSIBLE_DIFFERENT_SENSE,
                    base_rec["id"],
                    SenseDecision.DIFFERENT_SENSE
                )
            else:
                return (
                    DedupDecision.EXACT_DUPLICATE,
                    base_rec["id"],
                    SenseDecision.SAME_SENSE
                )

        # 2. Duplicate against Candidates already processed in current pool
        if surface in existing_pool_surfaces:
            pool_item = existing_pool_surfaces[surface]
            if surface in POLYSEMOUS_TERMS and domain != pool_item.domain:
                return (
                    DedupDecision.POSSIBLE_DIFFERENT_SENSE,
                    pool_item.candidate_id,
                    SenseDecision.DIFFERENT_SENSE
                )
            return (
                DedupDecision.EXACT_DUPLICATE,
                pool_item.candidate_id,
                SenseDecision.SAME_SENSE
            )

        # 3. Known Variant Matching
        if surface in KNOWN_VARIANTS_MAP:
            target_canonical = KNOWN_VARIANTS_MAP[surface]
            if target_canonical in self.canonical_index:
                return (
                    DedupDecision.VARIANT_OF,
                    self.canonical_index[target_canonical]["id"],
                    SenseDecision.SAME_SENSE
                )
            elif target_canonical in existing_pool_surfaces:
                return (
                    DedupDecision.VARIANT_OF,
                    existing_pool_surfaces[target_canonical].candidate_id,
                    SenseDecision.SAME_SENSE
                )

        # 4. Known Abbreviation Matching
        if surface in ABBREVIATION_PAIRS:
            canonical_target = ABBREVIATION_PAIRS[surface]
            if canonical_target in self.canonical_index:
                return (
                    DedupDecision.ABBREVIATION_OF,
                    self.canonical_index[canonical_target]["id"],
                    SenseDecision.SAME_SENSE
                )
            elif canonical_target in existing_pool_surfaces:
                return (
                    DedupDecision.ABBREVIATION_OF,
                    existing_pool_surfaces[canonical_target].candidate_id,
                    SenseDecision.SAME_SENSE
                )

        # 5. Reverse Abbreviation Matching (Canonical form matching known abbrev)
        for abbrev, full_form in ABBREVIATION_PAIRS.items():
            if surface == full_form:
                if abbrev in self.canonical_index:
                    return (
                        DedupDecision.NEW_CANONICAL,
                        self.canonical_index[abbrev]["id"],
                        SenseDecision.SAME_SENSE
                    )

        # 6. Ambiguity checks (overly short or multi-clause phrase)
        if len(surface) <= 1 or ("及び" in surface and len(surface) > 15):
            return (
                DedupDecision.NEEDS_REVIEW,
                None,
                SenseDecision.AMBIGUOUS
            )

        # 7. Otherwise: Genuine New Canonical Candidate
        return (
            DedupDecision.NEW_CANONICAL,
            None,
            SenseDecision.SAME_SENSE
        )
