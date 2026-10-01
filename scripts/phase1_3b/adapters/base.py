"""
scripts/phase1_3b/adapters/base.py
Base Source Adapter contract and abstract interface for Phase 1.3B.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Any, Optional
import hashlib
import json

from scripts.phase1_3b.license_gate import LicenseGate
from scripts.phase1_3b.models import SourceEvidence


class BaseSourceAdapter(ABC):
    """
    Standard contract for all external and internal vocabulary source adapters.
    Guarantees license gating, snapshot hashing, retrieval provenance, and extraction idempotency.
    """

    def __init__(
        self,
        source_id: str,
        source_version: str,
        raw_artifact_path: Path,
        license_code: str,
        license_locator: str,
        source_url: Optional[str] = None,
        reference_url: Optional[str] = None,
        retrieved_at: Optional[str] = None,
        expected_sha256: Optional[str] = None,
        parser_version: str = "1.3.1",
        license_gate: Optional[LicenseGate] = None
    ):
        self.source_id = source_id
        self.source_version = source_version
        self.raw_artifact_path = raw_artifact_path
        self.license = license_code
        self.license_locator = license_locator
        self.source_url = source_url
        self.reference_url = reference_url
        self.retrieved_at = retrieved_at
        self.expected_sha256 = expected_sha256
        self.parser_version = parser_version
        self.license_gate = license_gate or LicenseGate()
        self.records_extracted_count: int = 0

    def compute_sha256(self) -> str:
        """Computes SHA-256 of the raw artifact file."""
        if not self.raw_artifact_path.exists():
            raise FileNotFoundError(f"Raw source artifact not found at {self.raw_artifact_path}")
        h = hashlib.sha256()
        with open(self.raw_artifact_path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                h.update(chunk)
        return h.hexdigest()

    def verify_integrity(self) -> bool:
        """Verifies raw artifact hash matches expectations and license passes gate."""
        if self.expected_sha256:
            actual_hash = self.compute_sha256()
            if actual_hash != self.expected_sha256:
                raise ValueError(
                    f"Integrity check failed for {self.source_id}: "
                    f"expected {self.expected_sha256}, got {actual_hash}"
                )

        # License Gate Check
        approved, status, reason = self.license_gate.evaluate_license(self.license)
        if not approved:
            raise PermissionError(
                f"License Gate blocked source '{self.source_id}': {reason} (status: {status})"
            )
        return True

    def build_source_evidence(self, locator: str) -> SourceEvidence:
        """Constructs auditable SourceEvidence object for an extracted value."""
        lic_entry = self.license_gate.licenses.get(self.license, {})
        actual_hash = self.compute_sha256() if self.raw_artifact_path.exists() else None
        
        return SourceEvidence(
            source_id=self.source_id,
            source_version=self.source_version,
            source_locator=locator,
            raw_sha256=actual_hash,
            retrieved_at=self.retrieved_at,
            source_url=self.source_url,
            reference_url=self.reference_url,
            license=self.license,
            commercial_use=lic_entry.get("commercial_use", True),
            redistribution_allowed=lic_entry.get("redistribution_allowed", True),
            derivatives_allowed=lic_entry.get("derivatives_allowed", True),
            attribution_required=lic_entry.get("attribution_required", True),
            share_alike=lic_entry.get("share_alike", False)
        )

    @abstractmethod
    def extract_records(self) -> List[Dict[str, Any]]:
        """
        Extracts records into normalized dictionary representations with value-level provenance.
        Must be deterministic and idempotent.
        """
        pass

    def get_adapter_summary(self) -> Dict[str, Any]:
        """Provides metadata summary for audit reports."""
        return {
            "source_id": self.source_id,
            "source_version": self.source_version,
            "retrieved_at": self.retrieved_at,
            "license": self.license,
            "license_locator": self.license_locator,
            "raw_artifact_path": str(self.raw_artifact_path),
            "raw_sha256": self.expected_sha256 or (self.compute_sha256() if self.raw_artifact_path.exists() else None),
            "parser_version": self.parser_version,
            "records_extracted": self.records_extracted_count
        }
