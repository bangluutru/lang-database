"""
tests/test_provenance_integrity.py
====================================
Phase 1.3C.1 — Automated Provenance Integrity Test

Enforces ONE SOURCE OF TRUTH across all provenance documents for every
raw source artifact. For each source:

  RAW ARTIFACT
    → calculated SHA256
    → metadata.json            (artifact_sha256, license)
    → SHA256SUMS               (sha256)
    → acquisition_report.json  (sha256, license_code)
    → expansion_summary.json   (raw_sha256, license)
    → redistribution_audit.json (license)

Any mismatch = FAIL.

Additionally enforces known-correct values for JLPT provenance remediation
(Phase 1.3C.1).
"""

import hashlib
import json
import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
RAW_DATA = REPO_ROOT / "data/raw"

# ---------------------------------------------------------------------------
# Ground truth registry for known-corrected sources
# ---------------------------------------------------------------------------
KNOWN_CORRECT = {
    "jlpt_consensus": {
        "version": "2026-v1",
        "artifact_filename": "JLPT_vocab_ALL.csv",
        "sha256": "810c776c7a72fe9a6860d8629e7f4d3903545808e6cbcff8dde3b52b01800f24",
        "license": "CC-BY-3.0",
        # licenses that are FORBIDDEN for this source
        "forbidden_licenses": ["CC-BY-SA-3.0", "CC0-1.0", "CC0", "Public Domain"],
    },
    "kanjidic2": {
        "version": "2026-10-01",
        "artifact_filename": "kanjidic2.xml.gz",
        "sha256": "1c60c9453e1c7a318f3492fd8e13ea792d20130402bcbce9ed84e6165dfa1d60",
        "license": "CC-BY-SA-3.0",
        "forbidden_licenses": [],
    },
    "jmdict": {
        "version": "2026-10-01",
        "artifact_filename": "JMdict_e.gz",
        "sha256": "89777236dbf06f4d7b01c6dbff5e1f707978ddd067061b66bcb782d1f24e6ed3",
        "license": "CC-BY-SA-3.0",
        "forbidden_licenses": [],
    },
    "ngsl": {
        "version": "1.2",
        "artifact_filename": "NGSL_12_stats.csv",
        "sha256": "2098bab8955a120a9766c6282a51d7d578c6cb0a7d946600d2ffb73ba25a0b44",
        "license": "CC-BY-4.0",
        "forbidden_licenses": [],
    },
    "vn_freq": {
        "version": "1.0",
        "artifact_filename": "vietnamese-frequency.zip",
        "sha256": "8f644d06173600f8acb0d2b1a9dd0111c53ef304b9974b76e2cb24bad81fe04d",
        "license": "MIT",
        "forbidden_licenses": [],
    },
    "joyo": {
        "version": "2010-official",
        "artifact_filename": "joyo_kanji_official.json",
        "sha256": "f5f0cf7d03f3a7beddab973d6b1d31eb3cb30a2b0285639ba8f4042fd94e01f1",
        "license": "CC-BY-SA-3.0",
        "forbidden_licenses": ["PDL-1.0", "Government-PD", "CC0-1.0", "Public Domain"],
    },
}


# ---------------------------------------------------------------------------
# Helper: compute SHA256 of a file
# ---------------------------------------------------------------------------
def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


# ---------------------------------------------------------------------------
# Helper: load all metadata.json files from data/raw
# ---------------------------------------------------------------------------
def load_all_metadata() -> dict:
    """Returns {source_id: metadata_dict}"""
    result = {}
    for meta_path in sorted(RAW_DATA.glob("*/*/metadata.json")):
        with open(meta_path) as f:
            d = json.load(f)
        sid = d.get("source_id")
        if sid:
            result[sid] = (d, meta_path)
    return result


# ---------------------------------------------------------------------------
# Helper: load acquisition_report.json
# ---------------------------------------------------------------------------
def load_acquisition_report() -> dict:
    """Returns {source_id: entry_dict}"""
    path = REPO_ROOT / "reports/source_ingestion/acquisition_report.json"
    with open(path) as f:
        d = json.load(f)
    return {s["source"]: s for s in d.get("sources", [])}


# ---------------------------------------------------------------------------
# Helper: load expansion_summary.json JLPT block
# ---------------------------------------------------------------------------
def load_expansion_summary_sources() -> dict:
    """Returns {source_id: entry_dict} from expansion_summary.json"""
    path = REPO_ROOT / "reports/phase1_3c/expansion_summary.json"
    with open(path) as f:
        d = json.load(f)

    result = {}

    def extract(obj):
        if isinstance(obj, dict):
            if "source_id" in obj and "license" in obj:
                result[obj["source_id"]] = obj
            for v in obj.values():
                extract(v)
        elif isinstance(obj, list):
            for v in obj:
                extract(v)

    extract(d)
    return result


# ---------------------------------------------------------------------------
# Helper: load redistribution_audit.json
# ---------------------------------------------------------------------------
def load_redistribution_audit() -> dict:
    path = REPO_ROOT / "reports/licenses/redistribution_audit.json"
    with open(path) as f:
        d = json.load(f)
    return d.get("license_inventory", {})


# ---------------------------------------------------------------------------
# Helper: parse SHA256SUMS file
# ---------------------------------------------------------------------------
def load_sha256sums(sha_path: Path) -> dict:
    """Returns {filename: sha256}"""
    result = {}
    for line in sha_path.read_text().splitlines():
        line = line.strip()
        if line:
            parts = line.split()
            if len(parts) >= 2:
                sha, fname = parts[0], parts[-1].lstrip("*")
                result[fname] = sha
    return result


# ===========================================================================
# TESTS
# ===========================================================================


class TestKnownCorrectValues:
    """For sources in KNOWN_CORRECT, enforce the exact expected values."""

    @pytest.mark.parametrize("source_id,expected", KNOWN_CORRECT.items())
    def test_metadata_license_exact(self, source_id, expected):
        """metadata.json must have the exact correct license for known sources."""
        metadata = load_all_metadata()
        if source_id not in metadata:
            pytest.skip(f"{source_id} not found in raw data")
        d, path = metadata[source_id]
        actual = d.get("license")
        assert actual == expected["license"], (
            f"[{source_id}] metadata.json license mismatch: "
            f"got {actual!r}, expected {expected['license']!r}\n"
            f"File: {path}"
        )

    @pytest.mark.parametrize("source_id,expected", KNOWN_CORRECT.items())
    def test_metadata_sha256_exact(self, source_id, expected):
        """metadata.json artifact_sha256 must match the known-correct value."""
        metadata = load_all_metadata()
        if source_id not in metadata:
            pytest.skip(f"{source_id} not found in raw data")
        d, path = metadata[source_id]
        actual = d.get("artifact_sha256")
        assert actual == expected["sha256"], (
            f"[{source_id}] metadata.json sha256 mismatch: "
            f"got {actual!r}, expected {expected['sha256']!r}"
        )

    @pytest.mark.parametrize("source_id,expected", KNOWN_CORRECT.items())
    def test_no_forbidden_license(self, source_id, expected):
        """No document may contain a forbidden license for this source."""
        if not expected["forbidden_licenses"]:
            return

        metadata = load_all_metadata()
        if source_id not in metadata:
            pytest.skip(f"{source_id} not found in raw data")

        d, _ = metadata[source_id]
        actual_license = d.get("license", "")
        for forbidden in expected["forbidden_licenses"]:
            assert forbidden not in actual_license, (
                f"[{source_id}] metadata.json contains FORBIDDEN license {forbidden!r}. "
                f"Correct license is {expected['license']!r}."
            )

        # Check acquisition_report
        acq = load_acquisition_report()
        if source_id in acq:
            actual = acq[source_id].get("license_code", "")
            for forbidden in expected["forbidden_licenses"]:
                assert forbidden not in actual, (
                    f"[{source_id}] acquisition_report.json contains FORBIDDEN license {forbidden!r}. "
                    f"Correct license is {expected['license']!r}."
                )

        # Check expansion_summary
        exp = load_expansion_summary_sources()
        if source_id in exp:
            actual = exp[source_id].get("license", "")
            for forbidden in expected["forbidden_licenses"]:
                assert forbidden not in actual, (
                    f"[{source_id}] expansion_summary.json contains FORBIDDEN license {forbidden!r}. "
                    f"Correct license is {expected['license']!r}."
                )

        # Check redistribution_audit
        audit = load_redistribution_audit()
        if source_id in audit:
            actual = audit[source_id].get("license", "")
            for forbidden in expected["forbidden_licenses"]:
                assert forbidden not in actual, (
                    f"[{source_id}] redistribution_audit.json contains FORBIDDEN license {forbidden!r}. "
                    f"Correct license is {expected['license']!r}."
                )


class TestRawArtifactIntegrity:
    """For every raw artifact that exists on disk, verify SHA256 consistency."""

    def _collect_artifacts(self):
        """Return list of (source_id, version, artifact_path, metadata_dict)"""
        results = []
        for meta_path in sorted(RAW_DATA.glob("*/*/metadata.json")):
            with open(meta_path) as f:
                d = json.load(f)
            artifact_name = d.get("artifact_filename")
            if not artifact_name:
                continue
            artifact_path = meta_path.parent / artifact_name
            if artifact_path.exists():
                results.append((
                    d.get("source_id", meta_path.parent.parent.name),
                    d.get("source_version", meta_path.parent.name),
                    artifact_path,
                    d,
                ))
        return results

    def test_artifact_sha256_matches_metadata(self):
        """The actual file SHA256 must match metadata.json artifact_sha256."""
        failures = []
        for source_id, version, artifact_path, metadata in self._collect_artifacts():
            expected_sha = metadata.get("artifact_sha256")
            if not expected_sha:
                continue
            actual_sha = sha256_file(artifact_path)
            if actual_sha != expected_sha:
                failures.append(
                    f"[{source_id}/{version}] {artifact_path.name}: "
                    f"actual={actual_sha[:16]}... expected={expected_sha[:16]}..."
                )

        assert not failures, "SHA256 mismatches found:\n" + "\n".join(failures)

    def test_sha256sums_matches_metadata(self):
        """SHA256SUMS file must agree with metadata.json artifact_sha256."""
        failures = []
        for source_id, version, artifact_path, metadata in self._collect_artifacts():
            sha_file = artifact_path.parent / "SHA256SUMS"
            if not sha_file.exists():
                continue
            sums = load_sha256sums(sha_file)
            artifact_name = artifact_path.name
            if artifact_name not in sums:
                failures.append(
                    f"[{source_id}/{version}] {artifact_name} not found in SHA256SUMS"
                )
                continue
            expected_sha = metadata.get("artifact_sha256")
            sha_value = sums[artifact_name]
            if sha_value != expected_sha:
                failures.append(
                    f"[{source_id}/{version}] SHA256SUMS vs metadata.json mismatch: "
                    f"SHA256SUMS={sha_value[:16]}... metadata={expected_sha[:16] if expected_sha else 'None'}..."
                )

        assert not failures, "SHA256SUMS/metadata mismatches:\n" + "\n".join(failures)


class TestCrossDocumentProvenanceConsistency:
    """
    Cross-reference all provenance documents against metadata.json as ground truth.
    Any disagreement on sha256 or license = FAIL.
    """

    def test_acquisition_report_sha256_consistent_with_metadata(self):
        """acquisition_report.json sha256 must match metadata.json for each source."""
        metadata = load_all_metadata()
        acq = load_acquisition_report()
        failures = []

        for source_id, (meta, _) in metadata.items():
            if source_id not in acq:
                continue
            meta_sha = meta.get("artifact_sha256")
            acq_sha = acq[source_id].get("sha256")
            if meta_sha and acq_sha and meta_sha != acq_sha:
                failures.append(
                    f"[{source_id}] acquisition_report.sha256={acq_sha[:16]}... "
                    f"!= metadata.artifact_sha256={meta_sha[:16]}..."
                )

        assert not failures, "acquisition_report/metadata sha256 mismatches:\n" + "\n".join(failures)

    def test_acquisition_report_license_consistent_with_metadata(self):
        """acquisition_report.json license_code must match metadata.json license."""
        metadata = load_all_metadata()
        acq = load_acquisition_report()
        failures = []

        for source_id, (meta, _) in metadata.items():
            if source_id not in acq:
                continue
            meta_lic = meta.get("license")
            acq_lic = acq[source_id].get("license_code")
            if meta_lic and acq_lic and meta_lic != acq_lic:
                failures.append(
                    f"[{source_id}] acquisition_report.license_code={acq_lic!r} "
                    f"!= metadata.license={meta_lic!r}"
                )

        assert not failures, "acquisition_report/metadata license mismatches:\n" + "\n".join(failures)

    def test_expansion_summary_sha256_consistent_with_metadata(self):
        """expansion_summary.json raw_sha256 must match metadata.json for each source."""
        metadata = load_all_metadata()
        exp = load_expansion_summary_sources()
        failures = []

        for source_id, entry in exp.items():
            if source_id not in metadata:
                continue
            meta, _ = metadata[source_id]
            meta_sha = meta.get("artifact_sha256")
            exp_sha = entry.get("raw_sha256")
            if meta_sha and exp_sha and meta_sha != exp_sha:
                failures.append(
                    f"[{source_id}] expansion_summary.raw_sha256={exp_sha[:16]}... "
                    f"!= metadata.artifact_sha256={meta_sha[:16]}..."
                )

        assert not failures, "expansion_summary/metadata sha256 mismatches:\n" + "\n".join(failures)

    def test_expansion_summary_license_consistent_with_metadata(self):
        """expansion_summary.json license must match metadata.json license."""
        metadata = load_all_metadata()
        exp = load_expansion_summary_sources()
        failures = []

        for source_id, entry in exp.items():
            if source_id not in metadata:
                continue
            meta, _ = metadata[source_id]
            meta_lic = meta.get("license")
            exp_lic = entry.get("license")
            if meta_lic and exp_lic and meta_lic != exp_lic:
                failures.append(
                    f"[{source_id}] expansion_summary.license={exp_lic!r} "
                    f"!= metadata.license={meta_lic!r}"
                )

        assert not failures, "expansion_summary/metadata license mismatches:\n" + "\n".join(failures)

    def test_redistribution_audit_license_consistent_with_metadata(self):
        """redistribution_audit.json license must match metadata.json for each source."""
        metadata = load_all_metadata()
        audit = load_redistribution_audit()
        failures = []

        for source_id, entry in audit.items():
            if source_id not in metadata:
                continue
            meta, _ = metadata[source_id]
            meta_lic = meta.get("license")
            audit_lic = entry.get("license")
            if meta_lic and audit_lic and meta_lic != audit_lic:
                failures.append(
                    f"[{source_id}] redistribution_audit.license={audit_lic!r} "
                    f"!= metadata.license={meta_lic!r}"
                )

        assert not failures, "redistribution_audit/metadata license mismatches:\n" + "\n".join(failures)


class TestJLPTSpecificRemediation:
    """
    Phase 1.3C.1 specific assertions for JLPT provenance.
    These are the exact requirements from the independent review.
    """

    SOURCE_ID = "jlpt_consensus"
    CORRECT_LICENSE = "CC-BY-3.0"
    CORRECT_SHA = "810c776c7a72fe9a6860d8629e7f4d3903545808e6cbcff8dde3b52b01800f24"
    FORBIDDEN = ["CC-BY-SA-3.0", "CC0-1.0", "CC0", "Public Domain", "Open Data"]

    def test_metadata_license(self):
        d, _ = load_all_metadata()[self.SOURCE_ID]
        assert d["license"] == self.CORRECT_LICENSE, \
            f"metadata.json license wrong: {d['license']!r}"

    def test_metadata_sha256(self):
        d, _ = load_all_metadata()[self.SOURCE_ID]
        assert d["artifact_sha256"] == self.CORRECT_SHA, \
            f"metadata.json sha256 wrong: {d['artifact_sha256']!r}"

    def test_metadata_license_url_is_tanos(self):
        d, _ = load_all_metadata()[self.SOURCE_ID]
        url = d.get("license_url", "")
        assert "tanos.co.uk" in url, \
            f"metadata.json license_url should reference tanos.co.uk, got: {url!r}"

    def test_metadata_has_provenance_note(self):
        d, _ = load_all_metadata()[self.SOURCE_ID]
        assert "provenance_note" in d, "metadata.json missing provenance_note"
        assert "tanos.co.uk" in d["provenance_note"]

    def test_sha256sums_correct(self):
        sha_path = RAW_DATA / "jlpt_consensus/2026-v1/SHA256SUMS"
        sums = load_sha256sums(sha_path)
        assert "JLPT_vocab_ALL.csv" in sums
        assert sums["JLPT_vocab_ALL.csv"] == self.CORRECT_SHA, \
            f"SHA256SUMS has wrong value: {sums['JLPT_vocab_ALL.csv']!r}"

    def test_file_sha256_matches(self):
        artifact = RAW_DATA / "jlpt_consensus/2026-v1/JLPT_vocab_ALL.csv"
        actual = sha256_file(artifact)
        assert actual == self.CORRECT_SHA, \
            f"Actual file SHA256={actual!r} does not match expected"

    def test_acquisition_report_license(self):
        acq = load_acquisition_report()
        assert self.SOURCE_ID in acq, "jlpt_consensus not in acquisition_report"
        actual = acq[self.SOURCE_ID]["license_code"]
        assert actual == self.CORRECT_LICENSE, \
            f"acquisition_report license_code={actual!r}"

    def test_acquisition_report_sha256(self):
        acq = load_acquisition_report()
        actual = acq[self.SOURCE_ID]["sha256"]
        assert actual == self.CORRECT_SHA, \
            f"acquisition_report sha256={actual!r}"

    def test_expansion_summary_license(self):
        exp = load_expansion_summary_sources()
        if self.SOURCE_ID not in exp:
            pytest.skip("jlpt_consensus not in expansion_summary sources")
        actual = exp[self.SOURCE_ID]["license"]
        assert actual == self.CORRECT_LICENSE, \
            f"expansion_summary license={actual!r}"

    def test_expansion_summary_sha256(self):
        exp = load_expansion_summary_sources()
        if self.SOURCE_ID not in exp:
            pytest.skip("jlpt_consensus not in expansion_summary sources")
        actual = exp[self.SOURCE_ID].get("raw_sha256")
        if actual:
            assert actual == self.CORRECT_SHA, \
                f"expansion_summary raw_sha256={actual!r}"

    def test_redistribution_audit_license(self):
        audit = load_redistribution_audit()
        assert self.SOURCE_ID in audit, "jlpt_consensus not in redistribution_audit"
        actual = audit[self.SOURCE_ID]["license"]
        assert actual == self.CORRECT_LICENSE, \
            f"redistribution_audit license={actual!r}"

    def test_redistribution_audit_attribution_required(self):
        audit = load_redistribution_audit()
        entry = audit[self.SOURCE_ID]
        assert entry.get("attribution_required") is True, \
            "CC-BY-3.0 requires attribution — redistribution_audit.attribution_required must be True"

    @pytest.mark.parametrize("forbidden", FORBIDDEN)
    def test_no_forbidden_license_in_metadata(self, forbidden):
        d, _ = load_all_metadata()[self.SOURCE_ID]
        assert forbidden not in d.get("license", ""), \
            f"metadata.json contains FORBIDDEN license {forbidden!r}"

    @pytest.mark.parametrize("forbidden", FORBIDDEN)
    def test_no_forbidden_license_in_acquisition_report(self, forbidden):
        acq = load_acquisition_report()
        if self.SOURCE_ID not in acq:
            return
        actual = acq[self.SOURCE_ID].get("license_code", "")
        assert forbidden not in actual, \
            f"acquisition_report contains FORBIDDEN license {forbidden!r}"

    @pytest.mark.parametrize("forbidden", FORBIDDEN)
    def test_no_forbidden_license_in_redistribution_audit(self, forbidden):
        audit = load_redistribution_audit()
        if self.SOURCE_ID not in audit:
            return
        actual = audit[self.SOURCE_ID].get("license", "")
        assert forbidden not in actual, \
            f"redistribution_audit contains FORBIDDEN license {forbidden!r}"


class TestJoyoSpecificRemediation:
    """
    Phase 1.3C.1 Block 1: Jōyō Provenance Remediation.
    Verifies that KANJIDIC2-derived Jōyō data:
    1. Cannot claim direct 文化庁 extraction (origin != OFFICIAL_EXTRACTED)
    2. Has CC-BY-SA-3.0 license across all metadata, reports, audits
    3. Has EDRDG as organization and source_derived as authority_level
    4. Cites 文化庁 2010 Cabinet Notification as authority_reference annotation only
    """

    SOURCE_ID = "joyo"
    CORRECT_LICENSE = "CC-BY-SA-3.0"
    CORRECT_SHA = "f5f0cf7d03f3a7beddab973d6b1d31eb3cb30a2b0285639ba8f4042fd94e01f1"
    FORBIDDEN = ["PDL-1.0", "Government-PD", "CC0-1.0", "Public Domain"]

    def test_metadata_license_is_cc_by_sa_3(self):
        d, _ = load_all_metadata()[self.SOURCE_ID]
        assert d["license"] == self.CORRECT_LICENSE, f"metadata.json license wrong: {d['license']!r}"

    def test_metadata_organization_is_edrdg(self):
        d, _ = load_all_metadata()[self.SOURCE_ID]
        assert "Electronic Dictionary Research and Development Group" in d["organization"] or "EDRDG" in d["organization"]

    def test_metadata_authority_level_not_government(self):
        d, _ = load_all_metadata()[self.SOURCE_ID]
        assert d["authority_level"] != "government_statutory", "Cannot claim government_statutory authority"
        assert d["authority_level"] == "source_derived"

    def test_metadata_authority_reference_cites_bunka(self):
        d, _ = load_all_metadata()[self.SOURCE_ID]
        assert "authority_reference" in d
        assert "文化庁" in d["authority_reference"]

    def test_acquisition_report_license_is_cc_by_sa_3(self):
        acq = load_acquisition_report()
        assert self.SOURCE_ID in acq
        assert acq[self.SOURCE_ID]["license_code"] == self.CORRECT_LICENSE

    def test_redistribution_audit_license_is_cc_by_sa_3(self):
        audit = load_redistribution_audit()
        assert self.SOURCE_ID in audit
        assert audit[self.SOURCE_ID]["license"] == self.CORRECT_LICENSE
        assert audit[self.SOURCE_ID].get("share_alike") is True

    @pytest.mark.parametrize("forbidden", FORBIDDEN)
    def test_no_forbidden_license_in_metadata(self, forbidden):
        d, _ = load_all_metadata()[self.SOURCE_ID]
        assert forbidden not in d.get("license", "")

    @pytest.mark.parametrize("forbidden", FORBIDDEN)
    def test_no_forbidden_license_in_acquisition_report(self, forbidden):
        acq = load_acquisition_report()
        if self.SOURCE_ID not in acq:
            return
        assert forbidden not in acq[self.SOURCE_ID].get("license_code", "")

    @pytest.mark.parametrize("forbidden", FORBIDDEN)
    def test_no_forbidden_license_in_redistribution_audit(self, forbidden):
        audit = load_redistribution_audit()
        if self.SOURCE_ID not in audit:
            return
        assert forbidden not in audit[self.SOURCE_ID].get("license", "")
