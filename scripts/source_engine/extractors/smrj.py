"""
scripts/source_engine/extractors/smrj.py
Extractor for SMRJ / J-Net21 SME business management and operational guidance.
"""

from pathlib import Path
from typing import List
import json
from datetime import datetime, timezone

from scripts.source_engine.extractors.base import BaseExtractor
from scripts.source_engine.models import ExtractedCandidate


class SmrjBusinessExtractor(BaseExtractor):
    def extract_candidates(self) -> List[ExtractedCandidate]:
        catalog_path = self.raw_snapshot_path / "smrj_business_operations_catalog.json"
        if not catalog_path.exists():
            return []

        with open(catalog_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        candidates = []
        now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        for idx, item in enumerate(data.get("guidance_terms", []), start=1):
            term = item["term"]
            en = item.get("en", "")
            domain = item.get("domain", "business")
            subdomain = item.get("subdomain", "general_business")
            source_ref = item.get("source_ref", "")

            candidates.append(ExtractedCandidate(
                candidate_id=f"cand-smrj-{idx:06d}",
                source_id=self.source_id,
                source_version=self.source_version,
                source_record_id=f"smrj_term_{idx}",
                source_locator=f"guideline:{source_ref}, term:{term}",
                source_term_exact=term,
                source_context=f"中小機構・J-Net21 経営実務手引き。出典: {source_ref} (EN: {en})",
                source_definition=None,
                extracted_at=now_iso,
                extractor_version=self.extractor_version,
                raw_snapshot_hash=self.raw_snapshot_hash,
                primary_domain=domain,
                subdomain=subdomain,
                authority_class=self.authority_class,
                reuse_status=self.reuse_status
            ))

        return candidates
