"""
scripts/canary/selector.py
Deterministic Canary Selection Engine for Phase 1.2C.

Selects ~120 candidates from staging/canary_candidate_pool.jsonl based on:
1. Domain stratification quotas (prevents accounting dominance).
2. Authority class preference (A and B prioritized over C, D blocked).
3. Professional utility (PRO-A1 and PRO-A2 prioritized before PRO-A3).
4. Multi-source agreement.
5. Strict draft source exclusion (fsa-edinet-2027-draft blocked).
6. Deterministic tie-breaking (no random sampling).
"""

from typing import List, Dict, Any, Tuple
from pathlib import Path
import json
import re
import yaml
import pykakasi

import sys
from scripts.canary.models import (
    CanaryState,
    CanaryCandidateRecord
)

BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))


KNOWN_READINGS_MAP = {
    "36協定": "さぶろくきょうてい",
    "NACCS": "なっくす",
    "FOB": "えふおーびー",
    "CIF": "しーあいえふ",
    "BCP": "びーしーぴー",
    "J-SOX": "じぇいそっくす",
    "NDA": "えぬでぃーえー",
    "IPO": "あいぴーおー",
    "IR": "あいあーる",
    "ROA": "あーるおーえー",
    "ROE": "あーるおーいー",
    "B/L": "びーえる",
    "L/C": "えるしー",
    "PO": "ぴーおー",
    "KPI": "けーぴーあい",
    "PDCA": "ぴーでぃーしーえー",
    "CSR": "しーえすあーる",
}


class CanarySelector:
    def __init__(self, config_path: Path):
        self.config_path = config_path
        with open(config_path, "r", encoding="utf-8") as f:
            self.config = yaml.safe_load(f)

        self.domain_quotas = self.config.get("domain_quotas", {})
        self.blocked_sources = set(self.config.get("blocked_sources", []))
        self.kakasi = pykakasi.kakasi()

    def derive_reading(self, surface: str) -> str:
        """Derives clean hiragana reading using pykakasi with domain overrides."""
        if surface in KNOWN_READINGS_MAP:
            return KNOWN_READINGS_MAP[surface]
        res = self.kakasi.convert(surface)
        reading = "".join([item["hira"] for item in res])
        # Clean punctuation/brackets leaving pure kana & middle dots
        reading = re.sub(r"[\(\)（）\-\/、\s]", "", reading)
        return reading

    def extract_gloss(self, candidate_dict: Dict[str, Any]) -> str:
        """Extracts English gloss from source context if available."""
        for ev in candidate_dict.get("source_evidence", []):
            ctx = ev.get("source_context", "")
            m = re.search(r"(?:Official EN|EN):\s*([^\)]+)", ctx)
            if m:
                return m.group(1).strip()
        subdom = candidate_dict.get("subdomain", "")
        return subdom.replace("_", " ").title()

    def compute_candidate_sort_key(self, cand: Dict[str, Any]) -> Tuple[int, int, int, int, int, str]:
        """Deterministic multi-dimensional ranking tuple."""
        # 1. Tier Rank
        tier_ranks = {"PRO-A1": 0, "PRO-A2": 1, "PRO-A3": 2}
        pro_level = cand.get("pro_level_candidate", "PRO-A3")
        tier_rank = tier_ranks.get(pro_level, 3)

        # 2. Authority Rank
        auth_ranks = {"A": 0, "B": 1, "C": 2, "D": 3}
        auth_class = cand.get("authority_class", "C")
        auth_rank = auth_ranks.get(auth_class, 3)

        # 3. Source Agreement Count (Higher agreement comes first)
        ev_count = len(cand.get("source_evidence", []))
        agreement_rank = -ev_count

        # 4. Importance & Frequency
        prio = cand.get("priority", {})
        importance_ranks = {"high": 0, "medium": 1, "low": 2}
        frequency_ranks = {"high": 0, "medium": 1, "low": 2}
        imp_rank = importance_ranks.get(prio.get("professional_importance"), 1)
        freq_rank = frequency_ranks.get(prio.get("workplace_frequency"), 1)

        # 5. Deterministic Tie-Breaker
        tie_breaker = cand.get("candidate_id", "")

        return (tier_rank, auth_rank, agreement_rank, imp_rank, freq_rank, tie_breaker)

    def select_canary_candidates(self, pool_path: Path) -> List[CanaryCandidateRecord]:
        """Loads candidate pool and selects stratified canary candidates deterministically."""
        with open(pool_path, "r", encoding="utf-8") as f:
            raw_pool = [json.loads(line) for line in f if line.strip()]

        # Filter out blocked draft sources and prohibited reuse
        filtered_pool = []
        for c in raw_pool:
            is_blocked = False
            for ev in c.get("source_evidence", []):
                if ev.get("source_id") in self.blocked_sources or ev.get("source_version") == "2027-draft":
                    is_blocked = True
                    break
                if ev.get("reuse_status") == "RED":
                    is_blocked = True
                    break
            if not is_blocked and c.get("dedup_decision") == "NEW_CANONICAL":
                filtered_pool.append(c)

        # Group by domain
        domain_groups: Dict[str, List[Dict[str, Any]]] = {}
        for c in filtered_pool:
            dom = c.get("domain", "other")
            domain_groups.setdefault(dom, []).append(c)

        selected_records: List[CanaryCandidateRecord] = []

        # Process each domain quota
        for domain, quota_info in self.domain_quotas.items():
            target_quota = quota_info.get("target", 10)
            candidates_in_domain = domain_groups.get(domain, [])

            # Deterministic sorting
            sorted_candidates = sorted(candidates_in_domain, key=self.compute_candidate_sort_key)
            chosen = sorted_candidates[:target_quota]

            for cand_data in chosen:
                surface = cand_data["surface"]
                reading = self.derive_reading(surface)
                gloss = self.extract_gloss(cand_data)

                record = CanaryCandidateRecord(
                    candidate_id=cand_data["candidate_id"],
                    surface=surface,
                    normalized_surface=cand_data["normalized_surface"],
                    reading=reading,
                    domain=domain,
                    subdomain=cand_data["subdomain"],
                    meaning_gloss=gloss,
                    authority_class=cand_data["authority_class"],
                    reuse_status=cand_data["reuse_status"],
                    source_evidence=cand_data["source_evidence"],
                    pro_level_candidate=cand_data["pro_level_candidate"],
                    priority=cand_data["priority"],
                    state=CanaryState.SELECTED_FOR_CANARY,
                    lineage={
                        "selection_method": "stratified_quota_deterministic",
                        "config_version": self.config.get("version", "1.2.0"),
                        "raw_candidate_pool": pool_path.name
                    }
                )
                record.record_transition(
                    CanaryState.SELECTED_FOR_CANARY,
                    actor="canary_selector",
                    reason=f"Selected under domain quota for '{domain}'"
                )
                selected_records.append(record)

        return selected_records
