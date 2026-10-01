"""
scripts/source_engine/extractors/customs.py
Extractor for Japan Customs tariffs, clearance, and import/export procedures.
"""

from pathlib import Path
from typing import List
import json
from datetime import datetime, timezone

from scripts.source_engine.extractors.base import BaseExtractor
from scripts.source_engine.models import ExtractedCandidate


class JapanCustomsExtractor(BaseExtractor):
    def extract_candidates(self) -> List[ExtractedCandidate]:
        catalog_path = self.raw_snapshot_path / "customs_tariff_procedures.json"
        if not catalog_path.exists():
            return []

        with open(catalog_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        candidates = []
        now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        for idx, item in enumerate(data.get("procedures", []), start=1):
            term = item["term"]
            code = item["code"]
            law = item.get("law", "")
            en = item.get("en", "")
            cat = item.get("category", "customs_clearance")

            candidates.append(ExtractedCandidate(
                candidate_id=f"cand-customs-{idx:06d}",
                source_id=self.source_id,
                source_version=self.source_version,
                source_record_id=f"customs_{code}",
                source_locator=f"statute:{law}, code:{code}",
                source_term_exact=term,
                source_context=f"財務省関税局 通関手続・関税制度用語。根拠法令: {law} (Official EN: {en})",
                source_definition=None,
                extracted_at=now_iso,
                extractor_version=self.extractor_version,
                raw_snapshot_hash=self.raw_snapshot_hash,
                primary_domain="trade",
                subdomain=cat,
                authority_class=self.authority_class,
                reuse_status=self.reuse_status
            ))

        return candidates
