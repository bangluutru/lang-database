"""
scripts/source_engine/extractors/mhlw.py
Extractor for MHLW Labor Standards, employment regulations, and social insurance terms.
"""

from pathlib import Path
from typing import List
import json
from datetime import datetime, timezone

from scripts.source_engine.extractors.base import BaseExtractor
from scripts.source_engine.models import ExtractedCandidate


class MhlwLaborExtractor(BaseExtractor):
    def extract_candidates(self) -> List[ExtractedCandidate]:
        catalog_path = self.raw_snapshot_path / "mhlw_employment_insurance_regulations.json"
        if not catalog_path.exists():
            return []

        with open(catalog_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        candidates = []
        now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        for idx, item in enumerate(data.get("labor_terms", []), start=1):
            term = item["term"]
            en = item.get("en", "")
            subdomain = item.get("subdomain", "employment")
            article = item.get("article", "")

            candidates.append(ExtractedCandidate(
                candidate_id=f"cand-mhlw-{idx:06d}",
                source_id=self.source_id,
                source_version=self.source_version,
                source_record_id=f"mhlw_term_{idx}",
                source_locator=f"statute:{article}, term:{term}",
                source_term_exact=term,
                source_context=f"厚生労働省 労働基準・社会保険法令用語。根拠条文: {article} (Official EN: {en})",
                source_definition=None,
                extracted_at=now_iso,
                extractor_version=self.extractor_version,
                raw_snapshot_hash=self.raw_snapshot_hash,
                primary_domain="hr",
                subdomain=subdomain,
                authority_class=self.authority_class,
                reuse_status=self.reuse_status
            ))

        return candidates
