"""
scripts/phase1_3c/provenance_guard.py
Mandatory Provenance & License Verification Guard for Phase 1.3C.
Enforces Section 2, Section 3, and Section 26:
- Special Negative Rule:
  curated local value + external source URL = SOURCE_DERIVED -> FAIL / QUARANTINE
  unless exact upstream raw snapshot evidence exists and passes verification.
- Prohibits seed fixtures from masquerading as real upstream source-derived data.
"""

import json
from pathlib import Path
from typing import Dict, Any, Tuple, Optional, List

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_RAW_DIR = BASE_DIR / "data" / "raw"
DATA_CURATED_DIR = BASE_DIR / "data" / "curated"

from scripts.phase1_3b.models import SourceEvidence, OriginType
from scripts.phase1_3b.license_gate import LicenseGate


class ProvenanceGuardViolation(Exception):
    """Raised when an unbacked or mislabeled provenance attempt is detected."""
    pass


class ProvenanceGuard:
    """Verifies that every record marked SOURCE_DERIVED or OFFICIAL_EXTRACTED is backed by authentic raw snapshots."""

    def __init__(self, raw_dir: Optional[Path] = None, license_gate: Optional[LicenseGate] = None):
        self.raw_dir = raw_dir or DATA_RAW_DIR
        self.license_gate = license_gate or LicenseGate()

    def verify_evidence(self, evidence: SourceEvidence) -> Tuple[bool, str, str]:
        """
        Verifies a single SourceEvidence object.
        Returns:
            (is_valid: bool, status: str, reason: str)
            status in ("VERIFIED", "QUARANTINED", "REJECTED")
        """
        # Rule 1: SEED_CURATED cannot masquerade as SOURCE_DERIVED
        if evidence.origin == OriginType.SEED_CURATED.value:
            # Seed curated is explicitly accepted for test/reference fixtures, but must NOT claim to be upstream-derived
            return True, "VERIFIED_SEED", "Explicitly identified as curated seed data"

        # Rule 2: AI_GENERATED cannot claim SOURCE_DERIVED
        if evidence.origin == OriginType.AI_GENERATED.value:
            if not evidence.model:
                return False, "QUARANTINED", "AI_GENERATED record missing model metadata"
            return True, "VERIFIED_AI", "Explicitly identified as AI generated"

        # Rule 3: SOURCE_DERIVED and OFFICIAL_EXTRACTED require verifiable raw artifact snapshot
        if evidence.origin in (OriginType.SOURCE_DERIVED.value, OriginType.OFFICIAL_EXTRACTED.value):
            source_id = evidence.source_id
            version = evidence.source_version

            # Check if source is registered in raw snapshots
            source_snapshot_dir = self.raw_dir / source_id / version
            if not source_snapshot_dir.exists():
                return False, "QUARANTINED", (
                    f"PROVENANCE VIOLATION: Source '{source_id}' version '{version}' has no raw snapshot directory in data/raw. "
                    "Cannot mark as SOURCE_DERIVED without raw immutable artifact."
                )

            # Check metadata.json
            meta_file = source_snapshot_dir / "metadata.json"
            if not meta_file.exists():
                return False, "QUARANTINED", (
                    f"PROVENANCE VIOLATION: Raw snapshot for '{source_id}' is missing metadata.json."
                )

            with open(meta_file, "r", encoding="utf-8") as f:
                meta = json.load(f)

            # Check SHA256 match
            if evidence.raw_sha256 and evidence.raw_sha256 != meta.get("artifact_sha256"):
                return False, "QUARANTINED", (
                    f"PROVENANCE VIOLATION: SHA-256 hash mismatch for source '{source_id}'. "
                    f"Record has {evidence.raw_sha256}, snapshot has {meta.get('artifact_sha256')}."
                )

            # Check source locator
            if not evidence.source_locator:
                return False, "QUARANTINED", (
                    f"PROVENANCE VIOLATION: Source locator missing for SOURCE_DERIVED record '{source_id}'."
                )

            # Check license compliance
            lic = evidence.license or meta.get("license")
            if not lic or not self.license_gate.is_production_eligible(lic):
                return False, "QUARANTINED", (
                    f"LICENSE VIOLATION: License '{lic}' is not approved for production redistribution."
                )

            return True, "VERIFIED", f"Authentic upstream evidence verified against raw snapshot of {source_id}"

        # Rule 4: HUMAN_CURATED and CORPUS_DERIVED
        if evidence.origin in (OriginType.HUMAN_CURATED.value, OriginType.CORPUS_DERIVED.value):
            return True, "VERIFIED_CURATED", "Curated or corpus derived evidence"

        return False, "QUARANTINED", f"Unknown provenance origin '{evidence.origin}'"

    def enforce_record_provenance(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Inspects all source evidence in a record.
        If any evidence violates the provenance rule, flags record as quarantined.
        """
        evidences = record.get("source_evidence", [])
        if not evidences:
            return {
                "valid": False,
                "status": "QUARANTINED",
                "reason": "Missing required source_evidence list"
            }

        for ev_dict in evidences:
            ev = SourceEvidence.from_dict(ev_dict) if isinstance(ev_dict, dict) else ev_dict
            valid, status, reason = self.verify_evidence(ev)
            if not valid:
                return {
                    "valid": False,
                    "status": status,
                    "reason": reason,
                    "violating_evidence": ev.to_dict() if hasattr(ev, "to_dict") else ev_dict
                }

        return {"valid": True, "status": "VERIFIED", "reason": "All source evidence verified"}
