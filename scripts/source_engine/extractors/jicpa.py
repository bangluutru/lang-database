"""
scripts/source_engine/extractors/jicpa.py
Extractor for JICPA Accounting and Audit keywords index.
"""

from pathlib import Path
from typing import List
from bs4 import BeautifulSoup
from datetime import datetime, timezone

from scripts.source_engine.extractors.base import BaseExtractor
from scripts.source_engine.models import ExtractedCandidate


class JicpaExtractor(BaseExtractor):
    def extract_candidates(self) -> List[ExtractedCandidate]:
        html_path = self.raw_snapshot_path / "jicpa_keyword_index.html"
        if not html_path.exists():
            return []

        soup = BeautifulSoup(html_path.read_text(encoding="utf-8", errors="ignore"), "html.parser")
        candidates = []
        seen = set()
        now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        import unicodedata

        for a in soup.find_all("a", href=True):
            href = a["href"]
            if "/keyword/" in href and href != "/cpainfo/introduction/keyword/":
                txt = a.get_text().strip()
                norm_key = unicodedata.normalize("NFKC", txt)
                if norm_key and norm_key not in seen and len(norm_key) <= 30:
                    seen.add(norm_key)
                    seq = len(candidates) + 1
                    kw_id = href.strip("/").split("/")[-1]

                    candidates.append(ExtractedCandidate(
                        candidate_id=f"cand-jicpa-{seq:06d}",
                        source_id=self.source_id,
                        source_version=self.source_version,
                        source_record_id=f"jicpa_{kw_id}",
                        source_locator=f"file:jicpa_keyword_index.html, href:{href}",
                        source_term_exact=txt,
                        source_context="日本公認会計士協会 会計・監査用語キーワード",
                        source_definition=None,
                        extracted_at=now_iso,
                        extractor_version=self.extractor_version,
                        raw_snapshot_hash=self.raw_snapshot_hash,
                        primary_domain="accounting",
                        subdomain="audit",
                        authority_class=self.authority_class,
                        reuse_status=self.reuse_status
                    ))

        return candidates
