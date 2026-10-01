"""
scripts/source_engine/extractors/base.py
Abstract base extractor class for deterministic candidate extraction.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any
from pathlib import Path
import hashlib
from datetime import datetime, timezone

from scripts.source_engine.models import ExtractedCandidate


class BaseExtractor(ABC):
    """
    Common extraction interface for all authoritative source adapters.
    Ensures deterministic output, locator capture, snapshot hashing, and uniform candidate schema.
    """

    def __init__(self, source_id: str, source_version: str, raw_snapshot_path: Path, authority_class: str, reuse_status: str):
        self.source_id = source_id
        self.source_version = source_version
        self.raw_snapshot_path = raw_snapshot_path
        self.authority_class = authority_class
        self.reuse_status = reuse_status
        self.extractor_version = "1.2.0"
        self._raw_snapshot_hash = self._compute_snapshot_hash()

    def _compute_snapshot_hash(self) -> str:
        h = hashlib.sha256()
        meta_file = self.raw_snapshot_path / "metadata.json"
        if meta_file.exists():
            h.update(meta_file.read_bytes())
        else:
            for p in sorted(self.raw_snapshot_path.glob("*")):
                if p.is_file():
                    h.update(p.read_bytes())
        return h.hexdigest()

    @property
    def raw_snapshot_hash(self) -> str:
        return self._raw_snapshot_hash

    @abstractmethod
    def extract_candidates(self) -> List[ExtractedCandidate]:
        """Extract candidate records deterministically from raw snapshot."""
        pass
