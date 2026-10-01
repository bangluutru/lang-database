"""
scripts/source_engine/extractors/jetro.py
Extractor for JETRO trade navigation and Incoterms 2020 reference terms.
"""

from pathlib import Path
from typing import List
import json
from datetime import datetime, timezone

from scripts.source_engine.extractors.base import BaseExtractor
from scripts.source_engine.models import ExtractedCandidate


class JetroTradeExtractor(BaseExtractor):
    def extract_candidates(self) -> List[ExtractedCandidate]:
        catalog_path = self.raw_snapshot_path / "jetro_incoterms_reference.json"
        if not catalog_path.exists():
            return []

        with open(catalog_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        candidates = []
        now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        for idx, item in enumerate(data.get("trade_terms", []), start=1):
            term = item["term"]
            en = item.get("en", "")
            subdomain = item.get("subdomain", "incoterms")
            ctx = item.get("context", "")

            candidates.append(ExtractedCandidate(
                candidate_id=f"cand-jetro-{idx:06d}",
                source_id=self.source_id,
                source_version=self.source_version,
                source_record_id=f"jetro_term_{idx}",
                source_locator=f"guide:jetro_trade_navi, term:{term}",
                source_term_exact=term,
                source_context=f"JETRO 貿易実務用語。{ctx} (EN: {en})",
                source_definition=None,
                extracted_at=now_iso,
                extractor_version=self.extractor_version,
                raw_snapshot_hash=self.raw_snapshot_hash,
                primary_domain="trade",
                subdomain=subdomain,
                authority_class=self.authority_class,
                reuse_status=self.reuse_status
            ))

        return candidates
