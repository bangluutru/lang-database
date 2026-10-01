"""
tests/test_phase1_2a.py
Verification suite for Phase 1.2A: Existing Backlog Remediation & Golden Pilot v1.1.

Validates:
1. Zero known debt (INV-9 backlog = 0, INV-10 backlog = 0).
2. Suppressions file is empty.
3. All 92 remediated records have full True Linguistic Judge evidence.
4. Golden Pilot v1 remains 100% IMMUTABLE with original hashes.
5. Golden Pilot v1.1 is frozen with 800 records and new deterministic hashes.
"""

import json
import hashlib
from pathlib import Path
import pytest

BASE_DIR = Path(__file__).resolve().parent.parent

PROD_FILE = BASE_DIR / "data" / "production" / "vocabulary.jsonl"
SUPPRESSIONS_FILE = BASE_DIR / "config" / "known_invariant_suppressions.json"

GOLDEN_V1_DIR = BASE_DIR / "data" / "releases" / "golden-pilot-v1"
GOLDEN_V1_VOCAB = GOLDEN_V1_DIR / "vocabulary.jsonl"
GOLDEN_V1_MANIFEST = GOLDEN_V1_DIR / "dataset_manifest.json"

GOLDEN_V1_1_DIR = BASE_DIR / "data" / "releases" / "golden-pilot-v1.1"
GOLDEN_V1_1_VOCAB = GOLDEN_V1_1_DIR / "vocabulary.jsonl"
GOLDEN_V1_1_MANIFEST = GOLDEN_V1_1_DIR / "dataset_manifest.json"
GOLDEN_V1_1_VALIDATION = GOLDEN_V1_1_DIR / "validation_manifest.json"
GOLDEN_V1_1_CHECKSUMS = GOLDEN_V1_1_DIR / "checksums.sha256"

EXPECTED_V1_FILE_HASH = "1da7f6b958d3a1c4ccb12c4850b05ea5828b2d6ab8872077fea2e250d0e435c6"
EXPECTED_V1_CANONICAL_HASH = "27830fa0d861012f7878f9d95d1da5fe281a14076b38bb03c41f446d56a0c45c"


def load_jsonl(path: Path):
    if not path.exists():
        return []
    records = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))
    return records


def compute_sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def compute_canonical_hash(records) -> str:
    sorted_records = sorted(records, key=lambda r: r.get("id", ""))
    h = hashlib.sha256()
    for r in sorted_records:
        canonical = {k: v for k, v in r.items() if k not in ("status",)}
        line = json.dumps(canonical, sort_keys=True, ensure_ascii=False) + "\n"
        h.update(line.encode("utf-8"))
    return h.hexdigest()


class TestBacklogRemediation:
    """Verifies that all INV-9 and INV-10 backlog debt is eliminated."""

    def test_suppressions_file_has_zero_backlog(self):
        assert SUPPRESSIONS_FILE.exists(), f"Missing suppressions file: {SUPPRESSIONS_FILE}"
        with open(SUPPRESSIONS_FILE, "r", encoding="utf-8") as f:
            sup = json.load(f)
        inv9 = sup.get("inv9_template_injection_backlog", [])
        inv10 = sup.get("inv10_term_not_referenced_backlog", [])
        assert len(inv9) == 0, f"INV-9 backlog not zero: {len(inv9)} remaining"
        assert len(inv10) == 0, f"INV-10 backlog not zero: {len(inv10)} remaining"

    def test_production_has_zero_accounting_template_injections(self):
        prod = load_jsonl(PROD_FILE)
        accounting_markers = ["帳簿照合", "補助元帳", "証憑書類と", "仕訳内容", "計上内容や残高"]
        non_accounting = {"business", "trade"}
        accounting_adjacent_classes = {
            "account", "receivable_account", "payable_account",
            "provision_account", "tax_account", "equity_valuation_account"
        }

        bad = []
        for r in prod:
            domain = r.get("domain", {}).get("primary", "")
            if domain not in non_accounting:
                continue
            sem_class = r.get("domain", {}).get("semantic_class", "")
            if sem_class in accounting_adjacent_classes or "account" in sem_class:
                continue
            surface = r["term"]["surface"]
            for ex in r.get("examples", []):
                ja = ex.get("ja", "")
                for marker in accounting_markers:
                    if marker in ja:
                        bad.append(f"{r['id']}:{surface}:{marker}")
                        break

        assert not bad, f"Found {len(bad)} records with accounting template injections: {bad[:5]}"

    def test_production_all_examples_reference_terms(self):
        prod = load_jsonl(PROD_FILE)
        abbreviations = {
            "地域的な包括的経済連携協定": "RCEP",
            "包括的・先進的環太平洋パートナーシップ協定": "CPTPP",
            "環太平洋パートナーシップに関する包括的及び先進的な協定": "CPTPP",
        }

        bad = []
        for r in prod:
            surface = r["term"]["surface"]
            abbrev = abbreviations.get(surface, "")
            reading = r.get("term", {}).get("reading", "")

            def has_ref(text: str) -> bool:
                if surface in text:
                    return True
                if abbrev and abbrev in text:
                    return True
                if reading and reading in text:
                    return True
                return False

            any_ex = any(has_ref(ex.get("ja", "")) for ex in r.get("examples", []))
            any_dlg = any(has_ref(turn.get("ja", "")) for turn in r.get("dialogue", []))
            if not (any_ex or any_dlg):
                bad.append(f"{r['id']}:{surface}")

        assert not bad, f"Found {len(bad)} records where term is not referenced: {bad}"

    def test_remediated_records_have_full_provenance(self):
        prod = load_jsonl(PROD_FILE)
        remediated_count = 0
        for r in prod:
            lv = r.get("linguistic_validation", {})
            if lv.get("remediated") and lv.get("phase") == "1.2A":
                remediated_count += 1
                assert lv.get("status") == "production_verified"
                assert lv.get("critic"), f"Record {r['id']} missing critic"
                assert lv.get("resolver"), f"Record {r['id']} missing resolver"
                assert lv.get("rejudge"), f"Record {r['id']} missing rejudge"
                assert lv.get("adversarial_audit"), f"Record {r['id']} missing adversarial_audit"
                assert lv.get("validated_at"), f"Record {r['id']} missing validated_at"

        assert remediated_count == 92, f"Expected 92 remediated records, found {remediated_count}"


class TestGoldenPilotV1Immutability:
    """Verifies that Golden Pilot v1 was NOT modified in any way."""

    def test_v1_files_exist(self):
        assert GOLDEN_V1_VOCAB.exists()
        assert GOLDEN_V1_MANIFEST.exists()

    def test_v1_file_sha256_unchanged(self):
        actual = compute_sha256_file(GOLDEN_V1_VOCAB)
        assert actual == EXPECTED_V1_FILE_HASH, (
            f"Golden Pilot v1 file SHA-256 corrupted!\n"
            f"  Expected: {EXPECTED_V1_FILE_HASH}\n"
            f"  Actual:   {actual}"
        )

    def test_v1_canonical_sha256_unchanged(self):
        records = load_jsonl(GOLDEN_V1_VOCAB)
        actual = compute_canonical_hash(records)
        assert actual == EXPECTED_V1_CANONICAL_HASH, (
            f"Golden Pilot v1 canonical SHA-256 corrupted!\n"
            f"  Expected: {EXPECTED_V1_CANONICAL_HASH}\n"
            f"  Actual:   {actual}"
        )


class TestGoldenPilotV1Point1:
    """Verifies that Golden Pilot v1.1 release is properly frozen."""

    def test_v1_1_directory_exists(self):
        assert GOLDEN_V1_1_DIR.exists()
        assert GOLDEN_V1_1_VOCAB.exists()
        assert GOLDEN_V1_1_MANIFEST.exists()
        assert GOLDEN_V1_1_VALIDATION.exists()
        assert GOLDEN_V1_1_CHECKSUMS.exists()

    def test_v1_1_record_count_is_800(self):
        records = load_jsonl(GOLDEN_V1_1_VOCAB)
        assert len(records) == 800, f"Expected 800 records in v1.1, got {len(records)}"

    def test_v1_1_manifest_metadata(self):
        with open(GOLDEN_V1_1_MANIFEST, "r", encoding="utf-8") as f:
            manifest = json.load(f)
        assert manifest.get("release") == "golden-pilot-v1.1"
        assert manifest.get("production_verified") == 800
        assert manifest.get("immutable") is True
        lineage = manifest.get("lineage", {})
        assert lineage.get("predecessor") == "golden-pilot-v1"
        assert lineage.get("phase") == "1.2A"
        assert lineage.get("remediated_records_count") == 92

    def test_v1_1_hashes_match_manifest(self):
        with open(GOLDEN_V1_1_MANIFEST, "r", encoding="utf-8") as f:
            manifest = json.load(f)
        records = load_jsonl(GOLDEN_V1_1_VOCAB)
        computed_file_hash = compute_sha256_file(GOLDEN_V1_1_VOCAB)
        computed_canonical_hash = compute_canonical_hash(records)

        assert computed_file_hash == manifest.get("vocabulary_file_sha256")
        assert computed_canonical_hash == manifest.get("dataset_hash")

    def test_v1_1_checksums_file(self):
        with open(GOLDEN_V1_1_CHECKSUMS, "r", encoding="utf-8") as f:
            content = f.read()
        assert "vocabulary.jsonl" in content
        assert "dataset_manifest.json" in content
        assert "validation_manifest.json" in content
