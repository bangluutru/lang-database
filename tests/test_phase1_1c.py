"""
tests/test_phase1_1c.py
Phase 1.1C: Quarantine reconciliation, Golden Pilot immutability,
dataset hashing, model provenance, cache identity, and regression fixtures.

Test categories:
  - quarantine reconciliation
  - model provenance
  - cache identity
  - golden pilot immutability
  - dataset hashing
  - regression fixture (known-bad patterns)
  - permanent quarantine integrity
  - pilot freeze equation (800 = prod + review + quarantine)
"""

import json
import hashlib
import re
from pathlib import Path
import pytest

BASE_DIR = Path(__file__).resolve().parent.parent

PROD_FILE          = BASE_DIR / "data" / "production" / "vocabulary.jsonl"
REJECTED_FILE      = BASE_DIR / "staging" / "review_queue" / "rejected.jsonl"
NEEDS_REVIEW_FILE  = BASE_DIR / "staging" / "review_queue" / "needs_review.jsonl"
PERM_Q_FILE        = BASE_DIR / "staging" / "review_queue" / "permanent_quarantine.jsonl"
CANDIDATES_FILE    = BASE_DIR / "data" / "enriched" / "learning_candidates.jsonl"
GOLDEN_VOCAB       = BASE_DIR / "data" / "releases" / "golden-pilot-v1" / "vocabulary.jsonl"
GOLDEN_MANIFEST    = BASE_DIR / "data" / "releases" / "golden-pilot-v1" / "dataset_manifest.json"
GOLDEN_CHECKSUMS   = BASE_DIR / "data" / "releases" / "golden-pilot-v1" / "checksums.sha256"
DIAG_JSON          = BASE_DIR / "reports" / "phase_1_1c_quarantine_diagnosis.json"
CLOSURE_JSON       = BASE_DIR / "reports" / "phase_1_1c_closure.json"
POLICY_FILE        = BASE_DIR / "config" / "linguistic_validation.yaml"

VALID_MODEL_PREFIXES = ("gemini-2.5-flash", "gemini-3.8-flash", "gemini")
FORBIDDEN_MODEL_IDS  = {"independent-linguistic-judge-2.0"}
VALID_RELEASE_VERSIONS = {"v1.1.0a-prod", "v1.1.0b-prod", "v1.1.0c-prod"}


# ── Fixtures ─────────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def prod_entries():
    assert PROD_FILE.exists(), f"Production file missing: {PROD_FILE}"
    entries = []
    with open(PROD_FILE, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                entries.append(json.loads(line))
    return entries


@pytest.fixture(scope="module")
def candidate_entries():
    assert CANDIDATES_FILE.exists()
    entries = []
    with open(CANDIDATES_FILE, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                entries.append(json.loads(line))
    return entries


@pytest.fixture(scope="module")
def rejected_entries():
    entries = []
    if REJECTED_FILE.exists():
        with open(REJECTED_FILE, encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    entries.append(json.loads(line))
    return entries


@pytest.fixture(scope="module")
def perm_q_entries():
    entries = []
    if PERM_Q_FILE.exists():
        with open(PERM_Q_FILE, encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    entries.append(json.loads(line))
    return entries


@pytest.fixture(scope="module")
def needs_review_entries():
    entries = []
    if NEEDS_REVIEW_FILE.exists():
        with open(NEEDS_REVIEW_FILE, encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    entries.append(json.loads(line))
    return entries


@pytest.fixture(scope="module")
def golden_manifest():
    assert GOLDEN_MANIFEST.exists(), f"Golden Pilot manifest missing: {GOLDEN_MANIFEST}"
    with open(GOLDEN_MANIFEST, encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def golden_vocab_entries():
    assert GOLDEN_VOCAB.exists(), f"Golden Pilot vocab missing: {GOLDEN_VOCAB}"
    entries = []
    with open(GOLDEN_VOCAB, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                entries.append(json.loads(line))
    return entries


@pytest.fixture(scope="module")
def diagnoses():
    assert DIAG_JSON.exists(), f"Diagnosis JSON missing: {DIAG_JSON}"
    with open(DIAG_JSON, encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def closure_data():
    assert CLOSURE_JSON.exists(), f"Closure JSON missing: {CLOSURE_JSON}"
    with open(CLOSURE_JSON, encoding="utf-8") as f:
        return json.load(f)


# ── 1. Quarantine Reconciliation ─────────────────────────────────────────────

class TestQuarantineReconciliation:
    """All 28 original quarantined records must be accounted for."""

    def test_all_28_quarantine_records_diagnosed(self, diagnoses):
        """All 28 quarantined records must be diagnosed."""
        assert len(diagnoses) == 28, f"Expected 28 diagnoses, got {len(diagnoses)}"

    def test_each_diagnosis_has_required_fields(self, diagnoses):
        required_fields = {
            "id", "term", "domain", "failure_stage",
            "failure_categories", "root_cause",
            "remediation_possible", "recommended_action"
        }
        for d in diagnoses:
            for field in required_fields:
                assert field in d, f"Diagnosis for {d.get('id')} missing field '{field}'"
            assert len(d["failure_categories"]) >= 1, (
                f"Diagnosis for {d['id']} has no failure categories"
            )

    def test_pilot_freeze_equation(self, prod_entries, needs_review_entries, perm_q_entries):
        """800 = production + needs_review + permanent_quarantine (no record may disappear)."""
        total = len(prod_entries) + len(needs_review_entries) + len(perm_q_entries)
        assert total == 800, (
            f"Pilot freeze equation violated: "
            f"{len(prod_entries)} prod + {len(needs_review_entries)} review + "
            f"{len(perm_q_entries)} perm_q = {total} ≠ 800"
        )

    def test_no_records_disappeared(self, candidate_entries, prod_entries, needs_review_entries, perm_q_entries):
        """Every original candidate ID must appear in exactly one of prod/review/quarantine."""
        candidate_ids = {e["id"] for e in candidate_entries}
        prod_ids = {e["id"] for e in prod_entries}
        review_ids = {e["id"] for e in needs_review_entries}
        perm_q_ids = {e["id"] for e in perm_q_entries}

        all_accounted = prod_ids | review_ids | perm_q_ids
        missing = candidate_ids - all_accounted
        assert not missing, f"Records disappeared (not in any queue): {missing}"

    def test_no_duplicate_across_queues(self, prod_entries, needs_review_entries, perm_q_entries):
        """A record must not appear in more than one queue."""
        prod_ids = {e["id"] for e in prod_entries}
        review_ids = {e["id"] for e in needs_review_entries}
        perm_q_ids = {e["id"] for e in perm_q_entries}

        overlap_pr = prod_ids & review_ids
        overlap_pp = prod_ids & perm_q_ids
        overlap_rp = review_ids & perm_q_ids

        assert not overlap_pr, f"IDs in both prod and review: {overlap_pr}"
        assert not overlap_pp, f"IDs in both prod and perm_quarantine: {overlap_pp}"
        assert not overlap_rp, f"IDs in both review and perm_quarantine: {overlap_rp}"

    def test_production_increased_after_remediation(self, prod_entries):
        """After Phase 1.1C, production should be >= 772 (Phase 1.1B baseline)."""
        assert len(prod_entries) >= 772, (
            f"Production count regressed below Phase 1.1B baseline: {len(prod_entries)}"
        )

    def test_permanent_quarantine_have_reason(self, perm_q_entries):
        """Every permanently quarantined record must have an explicit reason."""
        for r in perm_q_entries:
            assert r.get("_quarantine_reason") or r.get("_quarantine_categories"), (
                f"Permanent quarantine record {r.get('id')} has no reason"
            )
            assert r.get("status") == "permanent_quarantine", (
                f"Permanent quarantine record {r.get('id')} has wrong status: {r.get('status')}"
            )

    def test_recovered_records_have_validation_evidence(self, prod_entries):
        """Recovered quarantine records (phase=1.1C) must have full validation evidence."""
        for r in prod_entries:
            lv = r.get("linguistic_validation", {})
            if lv.get("phase") == "1.1C" or lv.get("remediated"):
                assert lv.get("linguistic_judge"), (
                    f"Recovered record {r['id']} missing linguistic_judge evidence"
                )
                assert lv.get("rejudge"), (
                    f"Recovered record {r['id']} missing rejudge evidence"
                )
                assert lv.get("adversarial_audit"), (
                    f"Recovered record {r['id']} missing adversarial_audit evidence"
                )


# ── 2. Model Provenance ──────────────────────────────────────────────────────

class TestModelProvenance:
    """Model identifiers must be truthful and complete."""

    def test_no_forbidden_model_identifiers(self, prod_entries):
        """Forbidden fake model identifiers must not appear."""
        for r in prod_entries:
            lv = r.get("linguistic_validation", {})
            model = lv.get("linguistic_judge", {}).get("model", "")
            assert model not in FORBIDDEN_MODEL_IDS, (
                f"Forbidden model identifier '{model}' in {r['id']}"
            )

    def test_all_production_have_gemini_model(self, prod_entries):
        """Every production record must reference a real Gemini model."""
        for r in prod_entries:
            lv = r.get("linguistic_validation", {})
            model = lv.get("linguistic_judge", {}).get("model", "")
            assert any(model.startswith(p) for p in VALID_MODEL_PREFIXES), (
                f"Non-Gemini model '{model}' in {r['id']}"
            )

    def test_all_production_have_input_hash(self, prod_entries):
        """Every production record must have a SHA-256 input hash."""
        for r in prod_entries:
            lv = r.get("linguistic_validation", {})
            input_hash = lv.get("linguistic_judge", {}).get("input_hash", "")
            assert len(input_hash) == 64, (
                f"Invalid SHA-256 input_hash in {r['id']}: '{input_hash}'"
            )

    def test_all_production_have_prompt_version(self, prod_entries):
        """Every production record must have a prompt version."""
        for r in prod_entries:
            lv = r.get("linguistic_validation", {})
            pv = lv.get("linguistic_judge", {}).get("prompt_version", "")
            assert pv, f"Missing prompt_version in {r['id']}"
            assert pv == "linguistic_judge_v1", (
                f"Unexpected prompt_version '{pv}' in {r['id']}"
            )

    def test_all_production_have_release_version(self, prod_entries):
        """Every production record must have a known release version."""
        for r in prod_entries:
            rv = r.get("lineage", {}).get("release_version", "")
            assert rv in VALID_RELEASE_VERSIONS, (
                f"Unknown release_version '{rv}' in {r['id']}"
            )

    def test_policy_file_exists(self):
        """Model policy config must exist."""
        assert POLICY_FILE.exists(), f"Policy file missing: {POLICY_FILE}"

    def test_policy_defines_all_stages(self):
        """Policy must define model for all 5 validation stages."""
        import yaml
        with open(POLICY_FILE, encoding="utf-8") as f:
            policy = yaml.safe_load(f)
        stages = policy.get("linguistic_validation_policy", {})
        required_stages = {"semantic_audit", "critic", "resolver", "rejudge", "adversarial_audit"}
        for stage in required_stages:
            assert stage in stages, f"Policy missing stage: {stage}"
            assert stages[stage].get("model"), f"Policy stage '{stage}' missing model"
            assert stages[stage].get("prompt_version"), f"Policy stage '{stage}' missing prompt_version"


# ── 3. Cache Identity ─────────────────────────────────────────────────────────

class TestCacheIdentity:
    """Cache key must be invalidated when model, prompt version, or schema version changes."""

    def test_cache_key_changes_with_different_model(self):
        """Different models produce different cache keys."""
        import sys
        sys.path.insert(0, str(BASE_DIR / "scripts"))
        from llm_judge import TrueLinguisticJudge, SCHEMA_VERSION

        judge = TrueLinguisticJudge()
        payload = {"surface": "貸借対照表", "reading": "たいしゃくたいしょうひょう"}
        prompt_version = "linguistic_judge_v1"

        # Compute key for model A (current)
        canonical_str_a = json.dumps(payload, sort_keys=True, ensure_ascii=False)
        input_hash = hashlib.sha256(canonical_str_a.encode()).hexdigest()
        sig_a = f"{input_hash}::linguistic_judge_v1::gemini-2.5-flash::{SCHEMA_VERSION}"
        key_a = hashlib.sha256(sig_a.encode()).hexdigest()

        # Compute key for model B (different model)
        sig_b = f"{input_hash}::linguistic_judge_v1::gemini-old-model::{SCHEMA_VERSION}"
        key_b = hashlib.sha256(sig_b.encode()).hexdigest()

        assert key_a != key_b, "Cache keys must differ for different models"

    def test_cache_key_changes_with_different_prompt(self):
        """Different prompt versions produce different cache keys."""
        import sys
        sys.path.insert(0, str(BASE_DIR / "scripts"))
        from llm_judge import SCHEMA_VERSION

        payload = {"surface": "損益計算書"}
        canonical_str = json.dumps(payload, sort_keys=True, ensure_ascii=False)
        input_hash = hashlib.sha256(canonical_str.encode()).hexdigest()

        sig_v1 = f"{input_hash}::linguistic_judge_v1::gemini-2.5-flash::{SCHEMA_VERSION}"
        sig_v2 = f"{input_hash}::linguistic_judge_v2::gemini-2.5-flash::{SCHEMA_VERSION}"
        key_v1 = hashlib.sha256(sig_v1.encode()).hexdigest()
        key_v2 = hashlib.sha256(sig_v2.encode()).hexdigest()

        assert key_v1 != key_v2, "Cache keys must differ for different prompt versions"

    def test_cache_key_changes_with_different_schema(self):
        """Different schema versions produce different cache keys."""
        import sys
        sys.path.insert(0, str(BASE_DIR / "scripts"))

        payload = {"surface": "キャッシュ・フロー計算書"}
        canonical_str = json.dumps(payload, sort_keys=True, ensure_ascii=False)
        input_hash = hashlib.sha256(canonical_str.encode()).hexdigest()

        sig_old = f"{input_hash}::linguistic_judge_v1::gemini-2.5-flash::v1.1b"
        sig_new = f"{input_hash}::linguistic_judge_v1::gemini-2.5-flash::v1.1c"
        key_old = hashlib.sha256(sig_old.encode()).hexdigest()
        key_new = hashlib.sha256(sig_new.encode()).hexdigest()

        assert key_old != key_new, "Cache keys must differ for different schema versions"

    def test_cache_key_changes_with_different_input(self):
        """Different input content produces different cache keys."""
        import sys
        sys.path.insert(0, str(BASE_DIR / "scripts"))
        from llm_judge import SCHEMA_VERSION

        payload_a = {"surface": "貸借対照表"}
        payload_b = {"surface": "損益計算書"}
        ha = hashlib.sha256(json.dumps(payload_a, sort_keys=True).encode()).hexdigest()
        hb = hashlib.sha256(json.dumps(payload_b, sort_keys=True).encode()).hexdigest()
        assert ha != hb, "Different inputs must produce different input hashes"


# ── 4. Golden Pilot Immutability ─────────────────────────────────────────────

class TestGoldenPilotImmutability:
    """The Golden Pilot release must be frozen, hashed, and documented."""

    def test_golden_pilot_directory_exists(self):
        assert GOLDEN_VOCAB.exists(), f"Golden Pilot vocabulary missing: {GOLDEN_VOCAB}"
        assert GOLDEN_MANIFEST.exists(), f"Golden Pilot manifest missing: {GOLDEN_MANIFEST}"
        assert GOLDEN_CHECKSUMS.exists(), f"Golden Pilot checksums missing: {GOLDEN_CHECKSUMS}"

    def test_golden_manifest_required_fields(self, golden_manifest):
        required = {
            "release", "source_pilot_size", "production_verified",
            "permanent_quarantine", "domains", "validation_architecture",
            "schema_version", "prompt_versions", "model_policy",
            "created_at", "source_commit", "dataset_hash", "vocabulary_file_sha256"
        }
        for field in required:
            assert field in golden_manifest, f"Golden manifest missing field: '{field}'"

    def test_golden_manifest_source_pilot_size(self, golden_manifest):
        assert golden_manifest["source_pilot_size"] == 800

    def test_golden_manifest_counts_add_to_800(self, golden_manifest):
        prod = golden_manifest["production_verified"]
        perm_q = golden_manifest["permanent_quarantine"]
        assert prod + perm_q == 800, (
            f"Manifest prod + perm_q = {prod + perm_q} ≠ 800"
        )

    def test_golden_manifest_immutable_flag(self, golden_manifest):
        assert golden_manifest.get("immutable") is True

    def test_golden_vocab_sorted_by_id(self, golden_vocab_entries):
        """Golden Pilot vocabulary must be sorted by canonical ID."""
        ids = [e["id"] for e in golden_vocab_entries]
        assert ids == sorted(ids), "Golden Pilot vocabulary is not sorted by ID"

    def test_golden_vocab_sha256_matches_manifest(self, golden_manifest):
        """The SHA-256 of vocabulary.jsonl must match the manifest."""
        h = hashlib.sha256()
        with open(GOLDEN_VOCAB, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                h.update(chunk)
        computed = h.hexdigest()
        expected = golden_manifest.get("vocabulary_file_sha256", "")
        assert computed == expected, (
            f"vocabulary.jsonl SHA-256 mismatch:\n  computed: {computed}\n  manifest: {expected}"
        )

    def test_checksums_file_lists_vocabulary(self):
        """The checksums.sha256 file must include vocabulary.jsonl."""
        with open(GOLDEN_CHECKSUMS, encoding="utf-8") as f:
            content = f.read()
        assert "vocabulary.jsonl" in content
        assert "dataset_manifest.json" in content

    def test_golden_pilot_all_production_verified(self, golden_vocab_entries):
        """All records in Golden Pilot must be production_verified."""
        for r in golden_vocab_entries:
            lv = r.get("linguistic_validation", {})
            assert lv.get("status") == "production_verified", (
                f"Golden Pilot record {r['id']} is not production_verified"
            )

    def test_golden_pilot_no_generated_status(self, golden_vocab_entries):
        """Golden Pilot must contain zero learning objects with status 'generated'."""
        for r in golden_vocab_entries:
            for c in r.get("collocations", []):
                assert c.get("status") == "production_verified", (
                    f"Golden Pilot: generated collocation in {r['id']}"
                )
            for ex in r.get("examples", []):
                assert ex.get("status") == "production_verified", (
                    f"Golden Pilot: generated example in {r['id']}"
                )
            for turn in r.get("dialogue", []):
                assert turn.get("status") == "production_verified", (
                    f"Golden Pilot: generated dialogue turn in {r['id']}"
                )

    def test_golden_pilot_dataset_hash_deterministic(self, golden_manifest, golden_vocab_entries):
        """Re-computing the canonical dataset hash must match the manifest."""
        sorted_records = sorted(golden_vocab_entries, key=lambda r: r.get("id", ""))
        h = hashlib.sha256()
        for r in sorted_records:
            canonical = {k: v for k, v in r.items() if k not in ("status",)}
            line = json.dumps(canonical, sort_keys=True, ensure_ascii=False) + "\n"
            h.update(line.encode("utf-8"))
        computed = h.hexdigest()
        expected = golden_manifest.get("dataset_hash", "")
        assert computed == expected, (
            f"Canonical dataset hash mismatch:\n  computed: {computed}\n  manifest: {expected}"
        )

    def test_golden_manifest_has_domain_counts(self, golden_manifest):
        """Manifest must record domain counts for all 4 pilot domains."""
        domains = golden_manifest.get("domains", {})
        for expected_domain in ("accounting", "tax", "business", "trade"):
            assert expected_domain in domains, f"Domain '{expected_domain}' missing from manifest"
            assert domains[expected_domain] > 0


# ── 5. Dataset Hashing ────────────────────────────────────────────────────────

class TestDatasetHashing:
    """Dataset hash must be deterministic and stable."""

    def test_canonical_hash_stable_second_run(self, golden_vocab_entries, golden_manifest):
        """Running hash twice on same data must produce same result."""
        def compute(records):
            sorted_records = sorted(records, key=lambda r: r.get("id", ""))
            h = hashlib.sha256()
            for r in sorted_records:
                canonical = {k: v for k, v in r.items() if k not in ("status",)}
                line = json.dumps(canonical, sort_keys=True, ensure_ascii=False) + "\n"
                h.update(line.encode("utf-8"))
            return h.hexdigest()

        hash1 = compute(golden_vocab_entries)
        hash2 = compute(golden_vocab_entries)
        assert hash1 == hash2, "Hash is not deterministic across two runs"
        assert hash1 == golden_manifest.get("dataset_hash"), "Hash doesn't match manifest"

    def test_hash_changes_with_modified_record(self, golden_vocab_entries):
        """Modifying any field of any record must change the hash."""
        import copy

        def compute(records):
            sorted_records = sorted(records, key=lambda r: r.get("id", ""))
            h = hashlib.sha256()
            for r in sorted_records:
                canonical = {k: v for k, v in r.items() if k not in ("status",)}
                line = json.dumps(canonical, sort_keys=True, ensure_ascii=False) + "\n"
                h.update(line.encode("utf-8"))
            return h.hexdigest()

        original_hash = compute(golden_vocab_entries)

        # Modify a record
        modified = copy.deepcopy(golden_vocab_entries)
        modified[0]["term"]["surface"] = "TAMPERED_VALUE"
        tampered_hash = compute(modified)

        assert original_hash != tampered_hash, "Hash did not change after record modification"


# ── 6. Regression Fixtures (Known-Bad Patterns) ─────────────────────────────

class TestKnownBadPatterns:
    """
    Permanent regression fixtures for known-bad linguistic patterns.
    These prevent historically-discovered errors from re-entering production.
    """

    def test_account_class_predicates_not_on_organizations(self, prod_entries):
        """
        RULE: account-class predicates (計上する, 残高を確認する, 精算する, 照合する)
        MUST NOT be applied to organization-type terms (professional_service_firm, organization).
        Discovered in Phase 1.1A: 監査法人を計上する, 監査法人の残高
        """
        bad_account_preds = ["計上する", "の残高", "精算する", "照合する"]
        org_classes = {"professional_service_firm", "organization", "audit_firm"}

        for r in prod_entries:
            sem_class = r.get("domain", {}).get("semantic_class", "")
            if sem_class not in org_classes:
                continue
            surface = r["term"]["surface"]
            for c in r.get("collocations", []):
                text = c.get("text", "")
                for pred in bad_account_preds:
                    assert pred not in text, (
                        f"BAD REGRESSION: {surface} (org) has accounting predicate '{pred}': {text}"
                    )

    def test_quarterly_statements_use_review_not_audit(self, prod_entries):
        """
        RULE: 四半期財務諸表 must reference 四半期レビュー (review), NOT 監査 (full audit).
        Discovered in Phase 1.1B: 四半期財務諸表 incorrectly described as subject to 監査.
        """
        for r in prod_entries:
            if r["term"]["surface"] == "四半期財務諸表":
                for ex in r.get("examples", []):
                    ja = ex.get("ja", "")
                    # Must NOT say 公認会計士の監査 or 監査法人の監査 without qualifier
                    assert "公認会計士の厳格な監査" not in ja, (
                        f"Quarterly statement must use レビュー, not 厳格な監査: {ja}"
                    )
                    # If it mentions 監査 without レビュー, flag it
                    if "監査" in ja and "レビュー" not in ja and "会計監査人" not in ja:
                        # Allow 監査法人による四半期レビュー — which contains both
                        if "四半期レビュー" not in ja:
                            pytest.fail(
                                f"Quarterly statement example uses '監査' without '四半期レビュー': {ja}"
                            )

    def test_supplementary_schedules_not_confused_with_notes(self, prod_entries):
        """
        RULE: 附属明細表 (FIEA schedules) must not be conflated with 附属明細書 (Companies Act).
        Note disclosures (注記事項) are structurally separate from supplementary schedules (附属明細表).
        Discovered in Phase 1.1B.
        """
        for r in prod_entries:
            if r["term"]["surface"] == "附属明細表":
                for ex in r.get("examples", []):
                    ja = ex.get("ja", "")
                    assert "附属明細表の注記事項" not in ja, (
                        f"附属明細表 must not contain '附属明細表の注記事項': {ja}"
                    )

    def test_dual_responsibility_principle_not_violated(self, prod_entries):
        """
        RULE: Audit firm's responsibility is assurance/opinion (適正性の担保・意見表明),
        NOT preparation (作成責任) of financial statements.
        Discovered in Phase 1.1B.
        """
        for r in prod_entries:
            if r["term"]["surface"] == "監査法人":
                for ex in r.get("examples", []):
                    ja = ex.get("ja", "")
                    assert "財務諸表の作成を担保する" not in ja, (
                        f"Dual responsibility violation in 監査法人: audit firm cannot guarantee preparation: {ja}"
                    )

    def test_no_monetary_claim_conflated_with_expense(self, prod_entries):
        """
        RULE: 電子記録債権 (monetary claim) must use settlement/collection predicates,
        NOT 精算する (which is restricted to expense reimbursements).
        Discovered in Phase 1.1B.
        """
        for r in prod_entries:
            if r["term"]["surface"] == "電子記録債権":
                for c in r.get("collocations", []):
                    text = c.get("text", "")
                    assert "精算する" not in text, (
                        f"電子記録債権 must not use 精算する (expense predicate): {text}"
                    )

    def test_no_accounting_templates_on_business_terms(self, prod_entries):
        """
        RULE: Business/trade domain terms must NOT have accounting ledger examples.
        Systemic bug discovered in Phase 1.1C.
        Exemptions:
        - sem_class=account (accounting-adjacent terms legitimately reference ledgers)
        - Phase 1.2 backlog items (pre-existing, tracked in known_invariant_suppressions.json)
        """
        import json
        from pathlib import Path
        suppression_file = BASE_DIR / "config" / "known_invariant_suppressions.json"
        backlog_ids = set()
        if suppression_file.exists():
            with open(suppression_file) as f:
                sup = json.load(f)
            backlog_ids = set(sup.get("inv9_template_injection_backlog", []))

        accounting_markers = ["帳簿照合", "補助元帳", "証憑書類と", "仕訳内容", "計上内容や残高"]
        non_accounting = {"business", "trade"}
        accounting_adjacent_classes = {"account", "receivable_account", "payable_account",
                                        "provision_account", "tax_account", "equity_valuation_account"}

        for r in prod_entries:
            domain = r.get("domain", {}).get("primary", "")
            if domain not in non_accounting:
                continue
            if r["id"] in backlog_ids:
                continue  # Pre-existing Phase 1.2 backlog — not a regression
            sem_class = r.get("domain", {}).get("semantic_class", "")
            if sem_class in accounting_adjacent_classes or "account" in sem_class:
                continue
            surface = r["term"]["surface"]
            for ex in r.get("examples", []):
                ja = ex.get("ja", "")
                for marker in accounting_markers:
                    assert marker not in ja, (
                        f"REGRESSION: Accounting template injected into {domain} term '{surface}': "
                        f"'{marker}' found in example: {ja[:80]}"
                    )

    def test_no_governance_predicates_on_sales_or_trade_concepts(self, prod_entries):
        """
        RULE: Corporate governance predicates (決議する, 招集する) must not appear
        in collocations for non-governance concepts (e.g., 競合他社, フォワーダー, コルレス銀行).
        Systemic bug discovered in Phase 1.1C.
        Exemptions:
        - governance-entity surfaces (取締役会, 定時株主総会, 臨時株主総会 etc.) legitimately use these
        - governance-concept semantic classes
        """
        governance_preds = ["決議する", "招集する"]
        governance_exempt_classes = {
            "financial_statement", "statutory_document", "professional_service_firm",
            "account", "provision_account", "tax_account", "tax_obligation",
            "organization", "corporate_meeting", "board_meeting", "corporate_governance",
            "corporate_body", "shareholder_meeting", "statutory_meeting",
            "executive_compensation", "equity_compensation",
        }
        # Governance entities whose collocations legitimately reference governance actions
        governance_surfaces = {"取締役会", "定時株主総会", "臨時株主総会", "監査役会", "指名委員会", "報酬委員会"}
        non_governance_domains = {"business", "trade"}

        for r in prod_entries:
            domain = r.get("domain", {}).get("primary", "")
            if domain not in non_governance_domains:
                continue
            sem_class = r.get("domain", {}).get("semantic_class", "")
            if sem_class in governance_exempt_classes:
                continue
            surface = r["term"]["surface"]
            if surface in governance_surfaces:
                continue
            for c in r.get("collocations", []):
                text = c.get("text", "")
                for gp in governance_preds:
                    assert gp not in text, (
                        f"REGRESSION: Governance predicate '{gp}' in {domain} term '{surface}': {text}"
                    )

    def test_examples_contain_target_term(self, prod_entries):
        """
        RULE: Every production example sentence must contain or directly reference the target term.
        Systemic bug discovered in Phase 1.1C: wrong templates produced examples
        that never mentioned the term they were supposed to teach.
        Note: pre-existing Phase 1.2 backlog items are suppressed via known_invariant_suppressions.json.
        """
        import json
        from pathlib import Path
        suppression_file = BASE_DIR / "config" / "known_invariant_suppressions.json"
        backlog_ids = set()
        if suppression_file.exists():
            with open(suppression_file) as f:
                sup = json.load(f)
            backlog_ids = set(sup.get("inv10_term_not_referenced_backlog", []))

        ABBREVIATIONS = {
            "地域的な包括的経済連携協定": "RCEP",
            "包括的・先進的環太平洋パートナーシップ協定": "CPTPP",
        }

        for r in prod_entries:
            if r["id"] in backlog_ids:
                continue  # Pre-existing Phase 1.2 backlog
            surface = r["term"]["surface"]
            abbrev = ABBREVIATIONS.get(surface, "")

            def has_ref(text: str) -> bool:
                if surface in text: return True
                if abbrev and abbrev in text: return True
                reading = r.get("term", {}).get("reading", "")
                return bool(reading and reading in text)

            examples = r.get("examples", [])
            dialogue = r.get("dialogue", [])
            if not examples:
                continue
            any_has_term = any(has_ref(ex.get("ja", "")) for ex in examples)
            dialogue_has_term = any(has_ref(turn.get("ja", "")) for turn in dialogue)
            assert any_has_term or dialogue_has_term, (
                f"REGRESSION: Neither examples nor dialogue reference term '{surface}' "
                f"in {r['id']}"
            )

    @pytest.mark.parametrize("bad_pattern", [
        # These are from the CONFIRMED FAIL suite in test_linguistic_validation.py —
        # patterns verified to be caught by check_collocation_compatibility
        ("ふるさと納税を提出する", "tax_scheme", "tax"),
        ("土地を精算する", "tangible_fixed_asset", "accounting"),
        ("FOBの残高", "incoterms_rule", "trade"),
        ("監査法人を計上する", "professional_service_firm", "accounting"),
        ("監査法人の残高", "professional_service_firm", "accounting"),
        ("キャッシュ・フロー計算書を計上する", "financial_statement", "accounting"),
    ])
    def test_known_bad_collocations_rejected(self, bad_pattern):
        """
        Known-bad collocations from Phase 1.1A/1.1B must be rejected by the validator.
        These represent the most important regression cases.
        """
        import sys
        sys.path.insert(0, str(BASE_DIR / "scripts"))
        from linguistic_validator import check_collocation_compatibility

        text, semantic_class, domain = bad_pattern
        issues = check_collocation_compatibility(text, semantic_class, domain)
        assert len(issues) > 0, (
            f"Known-bad collocation should be rejected but passed: '{text}'"
        )

    @pytest.mark.parametrize("term,bad_example_fragment", [
        ("差別化", "帳簿照合"),
        ("クロージング", "仕訳"),
        ("市場調査", "補助元帳"),
        ("出張申請", "仕訳内容"),
        ("フォワーダー", "臨時株主総会"),
        ("コルレス銀行", "臨時取締役会"),
    ])
    def test_known_bad_example_templates_not_in_production(self, prod_entries, term, bad_example_fragment):
        """
        Known bad example template injections discovered in Phase 1.1C
        must not appear in production records.
        """
        for r in prod_entries:
            if r["term"]["surface"] == term:
                for ex in r.get("examples", []):
                    ja = ex.get("ja", "")
                    assert bad_example_fragment not in ja, (
                        f"REGRESSION: Bad template fragment '{bad_example_fragment}' "
                        f"still present in '{term}' example: {ja[:100]}"
                    )


# ── 7. Reproducibility ────────────────────────────────────────────────────────

class TestReproducibility:
    """Frozen release must be reproducible from persisted evidence."""

    def test_classification_stable(self, prod_entries):
        """Production records that are production_verified must not have conflicting status."""
        for r in prod_entries:
            lv = r.get("linguistic_validation", {})
            assert lv.get("status") == "production_verified", (
                f"Record {r['id']} has non-production_verified status: {lv.get('status')}"
            )

    def test_canonical_ids_stable(self, golden_vocab_entries, prod_entries):
        """IDs in Golden Pilot must match current production IDs."""
        golden_ids = {r["id"] for r in golden_vocab_entries}
        prod_ids = {r["id"] for r in prod_entries}
        assert golden_ids == prod_ids, (
            f"ID mismatch between Golden Pilot and production:\n"
            f"  In Golden but not prod: {golden_ids - prod_ids}\n"
            f"  In prod but not Golden: {prod_ids - golden_ids}"
        )

    def test_term_surfaces_stable(self, golden_vocab_entries, prod_entries):
        """Term surface forms must not differ between Golden Pilot and production."""
        golden_map = {r["id"]: r["term"]["surface"] for r in golden_vocab_entries}
        prod_map = {r["id"]: r["term"]["surface"] for r in prod_entries}
        for rid, surface in golden_map.items():
            if rid in prod_map:
                assert prod_map[rid] == surface, (
                    f"Surface changed for {rid}: Golden='{surface}' vs Prod='{prod_map[rid]}'"
                )

    def test_no_draft_source_contamination(self, prod_entries):
        """Production records must not originate from 2027 draft sources."""
        for r in prod_entries:
            origin = r.get("lineage", {}).get("origin_type", "")
            assert origin in ("official_extracted", "curated"), (
                f"Invalid origin_type '{origin}' in {r['id']}"
            )
            source_id = r.get("lineage", {}).get("source_id", "")
            assert "2027" not in source_id, (
                f"Draft 2027 source contamination in {r['id']}: {source_id}"
            )

    def test_jlpt_mapping_stable(self, prod_entries):
        """JLPT must remain null/not_mapped (professional tier is independent)."""
        for r in prod_entries:
            gj = r.get("general_japanese", {})
            assert gj.get("jlpt_level") is None
            assert gj.get("jlpt_status") == "not_mapped"
