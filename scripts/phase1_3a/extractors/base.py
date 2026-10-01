"""
scripts/phase1_3a/extractors/base.py
Base extractor interface for Phase 1.3A & 1.3A.1 candidate extraction.
Enforces truthful source provenance, locators, and artifact hash tracking.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional
from scripts.phase1_3a.models import RawCandidate, ProvenanceType


class BasePhase13Extractor(ABC):
    def __init__(
        self,
        source_id: str,
        source_version: str,
        authority_class: str,
        reuse_status: str,
        raw_snapshot_path: Optional[Path] = None,
        raw_snapshot_hash: str = "",
        curated_artifact_path: Optional[Path] = None,
        curated_artifact_hash: str = "",
        official_url: Optional[str] = None,
        reference_url: Optional[str] = None,
        provenance_type: str = ProvenanceType.OFFICIAL_EXTRACTED.value,
        extractor_version: str = "1.3.1"
    ):
        self.source_id = source_id
        self.source_version = source_version
        self.authority_class = authority_class
        self.reuse_status = reuse_status
        self.raw_snapshot_path = raw_snapshot_path
        self.raw_snapshot_hash = raw_snapshot_hash
        self.curated_artifact_path = curated_artifact_path
        self.curated_artifact_hash = curated_artifact_hash
        self.official_url = official_url
        self.reference_url = reference_url
        self.provenance_type = provenance_type
        self.extractor_version = extractor_version

    @abstractmethod
    def extract_candidates(self) -> List[RawCandidate]:
        """Extracts and returns raw candidate records with truthful provenance."""
        pass
