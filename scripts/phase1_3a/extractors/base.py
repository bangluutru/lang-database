"""
scripts/phase1_3a/extractors/base.py
Base extractor interface for Phase 1.3A candidate extraction.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List
from scripts.phase1_3a.models import RawCandidate


class BasePhase13Extractor(ABC):
    def __init__(
        self,
        source_id: str,
        source_version: str,
        raw_snapshot_path: Path,
        raw_snapshot_hash: str,
        authority_class: str,
        reuse_status: str,
        extractor_version: str = "1.3.0"
    ):
        self.source_id = source_id
        self.source_version = source_version
        self.raw_snapshot_path = raw_snapshot_path
        self.raw_snapshot_hash = raw_snapshot_hash
        self.authority_class = authority_class
        self.reuse_status = reuse_status
        self.extractor_version = extractor_version

    @abstractmethod
    def extract_candidates(self) -> List[RawCandidate]:
        """Extracts and returns raw candidate records with complete provenance."""
        pass
