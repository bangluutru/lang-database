"""
scripts/phase1_3b/license_gate.py
Automated machine-readable license verification gate for Phase 1.3B.
Enforces open redistribution, commercial-use compatibility, and derivative permissions.
"""

from pathlib import Path
from typing import Dict, Any, Tuple, Optional
import yaml

BASE_DIR = Path(__file__).resolve().parent.parent.parent
LICENSE_POLICY_FILE = BASE_DIR / "config" / "license_policy.yaml"


class LicenseGate:
    """Enforces license compatibility for the open lexical database."""

    def __init__(self, policy_path: Optional[Path] = None):
        path = policy_path or LICENSE_POLICY_FILE
        if not path.exists():
            raise FileNotFoundError(f"Missing license policy config: {path}")
        with open(path, "r", encoding="utf-8") as f:
            self.config = yaml.safe_load(f)
        self.licenses: Dict[str, Dict[str, Any]] = self.config.get("licenses", {})
        self.requirements: Dict[str, bool] = self.config.get("production_requirements", {
            "allow_commercial": True,
            "allow_redistribution": True,
            "allow_derivatives": True
        })

    def evaluate_license(self, license_code: str) -> Tuple[bool, str, str]:
        """
        Evaluates a license identifier.
        Returns:
            (is_approved: bool, status: str, reason: str)
        """
        if not license_code:
            return False, "QUARANTINED", "Missing license identification"

        # Check multi-license or combined strings (e.g. 'PDL-1.0 / CC-BY-4.0')
        parts = [p.strip() for p in license_code.replace(";", "/").split("/")]
        
        # If any component in a combined license is explicitly approved and permissive:
        for part in parts:
            lic = self.licenses.get(part)
            if not lic:
                # Fuzzy normalize (e.g. 'CC BY 4.0' -> 'CC-BY-4.0')
                norm_part = part.replace(" ", "-").upper()
                lic = self.licenses.get(norm_part)

            if lic:
                status = lic.get("status", "QUARANTINED")
                if status in ("APPROVED", "APPROVED_WITH_SHARE_ALIKE"):
                    comm = lic.get("commercial_use", False)
                    redist = lic.get("redistribution_allowed", False)
                    deriv = lic.get("derivatives_allowed", False)

                    if self.requirements.get("allow_commercial") and not comm:
                        return False, "QUARANTINED", f"License {part} prohibits commercial use"
                    if self.requirements.get("allow_redistribution") and not redist:
                        return False, "QUARANTINED", f"License {part} prohibits redistribution"
                    if self.requirements.get("allow_derivatives") and not deriv:
                        return False, "QUARANTINED", f"License {part} prohibits derivative works"

                    return True, status, f"License {part} approved for canonical production ({lic.get('name')})"
                else:
                    return False, status, lic.get("quarantine_reason", f"License {part} is not approved for production")

        # Unknown license
        return False, "QUARANTINED", f"Unknown or unverified license '{license_code}' quarantined by policy"

    def is_production_eligible(self, license_code: str) -> bool:
        """Convenience method returning True if license is approved for production."""
        approved, _, _ = self.evaluate_license(license_code)
        return approved

    def evaluate(self, license_code: str):
        """Object-oriented evaluation result for flexible test and pipeline access."""
        approved, status, reason = self.evaluate_license(license_code)
        
        class EvaluationResult:
            def __init__(self, app: bool, st: str, rea: str):
                self.approved = app
                self.status = type("StatusObj", (), {"value": st.lower()})()
                self.reason = rea
                
            def __repr__(self):
                return f"<EvaluationResult approved={self.approved} status={self.status.value}>"

        return EvaluationResult(approved, status, reason)

