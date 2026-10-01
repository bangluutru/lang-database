"""
scripts/source_engine/extractors/asbj.py
Extractor for ASBJ Accounting Standards catalog.
"""

from pathlib import Path
from typing import List
import json
from datetime import datetime, timezone

from scripts.source_engine.extractors.base import BaseExtractor
from scripts.source_engine.models import ExtractedCandidate


class AsbjExtractor(BaseExtractor):
    def extract_candidates(self) -> List[ExtractedCandidate]:
        catalog_path = self.raw_snapshot_path / "asbj_accounting_standards_catalog.json"
        if not catalog_path.exists():
            return []

        with open(catalog_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        candidates = []
        now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        for idx, std in enumerate(data.get("standards", []), start=1):
            short_term = std.get("short") or std.get("name")
            full_name = std.get("name")
            code = std.get("code")
            article = std.get("article", "")

            candidates.append(ExtractedCandidate(
                candidate_id=f"cand-asbj-{idx:06d}",
                source_id=self.source_id,
                source_version=self.source_version,
                source_record_id=f"asbj_{code}",
                source_locator=f"catalog:asbj_standards, code:{code}, article:{article}",
                source_term_exact=short_term,
                source_context=f"企業会計基準委員会 会計基準: {full_name} ({code})",
                source_definition=None,
                extracted_at=now_iso,
                extractor_version=self.extractor_version,
                raw_snapshot_hash=self.raw_snapshot_hash,
                primary_domain="accounting",
                subdomain="financial_accounting",
                authority_class=self.authority_class,
                reuse_status=self.reuse_status
            ))

        return candidates
