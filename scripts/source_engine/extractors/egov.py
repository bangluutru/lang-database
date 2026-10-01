"""
scripts/source_engine/extractors/egov.py
Extractor for e-Gov Companies Act and Commercial Registration statutory terminology.
"""

from pathlib import Path
from typing import List
import json
from datetime import datetime, timezone

from scripts.source_engine.extractors.base import BaseExtractor
from scripts.source_engine.models import ExtractedCandidate


class EgovLegalExtractor(BaseExtractor):
    def extract_candidates(self) -> List[ExtractedCandidate]:
        catalog_path = self.raw_snapshot_path / "egov_commercial_code_statutory.json"
        if not catalog_path.exists():
            return []

        with open(catalog_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        candidates = []
        now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        for idx, item in enumerate(data.get("statutory_terms", []), start=1):
            term = item["term"]
            en = item.get("en", "")
            subdomain = item.get("subdomain", "corporate_law")
            statute = item.get("statute", "")
            primary_domain = "management" if subdomain in ("corporate_governance", "board_management", "internal_control") else "legal"

            candidates.append(ExtractedCandidate(
                candidate_id=f"cand-egov-{idx:06d}",
                source_id=self.source_id,
                source_version=self.source_version,
                source_record_id=f"egov_term_{idx}",
                source_locator=f"statute:{statute}, term:{term}",
                source_term_exact=term,
                source_context=f"e-Gov 法令検索 会社法・商法 法定用語。根拠: {statute} (EN: {en})",
                source_definition=None,
                extracted_at=now_iso,
                extractor_version=self.extractor_version,
                raw_snapshot_hash=self.raw_snapshot_hash,
                primary_domain=primary_domain,
                subdomain=subdomain,
                authority_class=self.authority_class,
                reuse_status=self.reuse_status
            ))

        return candidates
