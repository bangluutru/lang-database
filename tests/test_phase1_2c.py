"""
tests/test_phase1_2c.py
Comprehensive Test Suite for Phase 1.2C: Controlled Canary Expansion & Promotion Pipeline.

Verifies:
1. Selection: Determinism, Domain Stratification (11 domains), Source Diversity, Draft Exclusion.
2. State Machine: Valid lifecycle transitions, illegal jump rejection, unapproved promotion prevention.
3. Dedup Gates: Exact duplicate, Orthographic variant, Abbreviation, Alias, Polysemy/Sense split.
4. Linguistic Quality: Script validation, reading integrity, diacritic leakage prevention.
5. Provenance & Licensing: Full evidence chain preservation, RED source blocking.
6. Human Review Boundary: Strict quarantine, no unapproved promotion, non-falsification.
7. Canary Release Engine: Isolated artifact generation, valid manifests, reproducible hashes.
8. Baseline Immutability: Golden Pilot v1 and v1.1 hashes unchanged, production count = 800.
"""

import pytest
import json
import hashlib
from pathlib import Path
import sys
import yaml

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from scripts.canary.models import (
    CanaryState,
    CanaryCandidateRecord,
    HumanReviewDecision,
    GateStatus
)
from scripts.canary.state_machine import (
    PromotionStateMachine,
    InvalidStateTransitionError,
    UnapprovedPromotionError
)
from scripts.canary.selector import CanarySelector
from scripts.canary.validator import CanaryValidator
from scripts.canary.review_manager import CanaryReviewManager
from scripts.canary.release_builder import CanaryReleaseBuilder, compute_canonical_dataset_hash
from scripts.canary.quality_auditor import CanaryQualityAuditor
from scripts.canary.decision_importer import (
    CanaryDecisionImporter,
    DecisionValidationError,
    RevalidationFailedError
)
from scripts.canary.gloss_integrity_auditor import GlossIntegrityAuditor

# Frozen baseline hashes
GOLDEN_PILOT_V1_CANONICAL_HASH = "27830fa0d861012f7878f9d95d1da5fe281a14076b38bb03c41f446d56a0c45c"
GOLDEN_PILOT_V1_VOCAB_HASH = "1da7f6b958d3a1c4ccb12c4850b05ea5828b2d6ab8872077fea2e250d0e435c6"

GOLDEN_PILOT_V1_1_CANONICAL_HASH = "5ae36d8ace6884a50a0e1fa8c8fd4399660575a133ea2dcbdcf8e16b1f51be15"
GOLDEN_PILOT_V1_1_VOCAB_HASH = "1e18d574e1c1b0f54451456e33648518f6e49a7e0dfc37eb1fec3dd35e55325d"


def get_file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


# -----------------------------------------------------------------------------
# 1. Selection Tests
# -----------------------------------------------------------------------------
class TestCanarySelection:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.config_path = BASE_DIR / "config" / "canary_config.yaml"
        self.pool_path = BASE_DIR / "staging" / "canary_candidate_pool.jsonl"
        self.selector = CanarySelector(self.config_path)

    def test_selection_determinism(self):
        """Running selection twice produces identical candidate IDs in identical order."""
        run1 = self.selector.select_canary_candidates(self.pool_path)
        run2 = self.selector.select_canary_candidates(self.pool_path)

        assert len(run1) == len(run2) == 120
        ids1 = [r.candidate_id for r in run1]
        ids2 = [r.candidate_id for r in run2]
        assert ids1 == ids2

    def test_domain_stratification(self):
        """Selection covers all 11 professional domains with configured quotas."""
        selected = self.selector.select_canary_candidates(self.pool_path)
        domain_counts = {}
        for r in selected:
            domain_counts[r.domain] = domain_counts.get(r.domain, 0) + 1

        assert len(domain_counts) == 11
        for dom, quota_info in self.selector.domain_quotas.items():
            expected_target = quota_info["target"]
            assert domain_counts.get(dom, 0) == expected_target

        # Accounting must not dominate (18/120 = 15%)
        assert domain_counts["accounting"] == 18
        assert domain_counts["finance"] == 18

    def test_draft_exclusion(self):
        """Draft source fsa-edinet-2027-draft must be 100% excluded."""
        selected = self.selector.select_canary_candidates(self.pool_path)
        for r in selected:
            for ev in r.source_evidence:
                assert ev.get("source_id") != "fsa-edinet-2027-draft"
                assert ev.get("source_version") != "2027-draft"

    def test_authority_preference(self):
        """Authority class A and B must constitute the majority of selections."""
        selected = self.selector.select_canary_candidates(self.pool_path)
        auth_a_count = sum(1 for r in selected if r.authority_class == "A")
        auth_b_count = sum(1 for r in selected if r.authority_class == "B")
        auth_d_count = sum(1 for r in selected if r.authority_class == "D")

        assert auth_d_count == 0
        assert (auth_a_count + auth_b_count) >= 90


# -----------------------------------------------------------------------------
# 2. State Machine Tests
# -----------------------------------------------------------------------------
class TestPromotionStateMachine:
    def _create_dummy_candidate(self, candidate_id="test-001", surface="テスト科目"):
        return CanaryCandidateRecord(
            candidate_id=candidate_id,
            surface=surface,
            normalized_surface=surface,
            reading="てすとかもく",
            domain="accounting",
            subdomain="financial_accounting",
            meaning_gloss="Test account item",
            authority_class="A",
            reuse_status="GREEN",
            source_evidence=[{
                "source_id": "fsa-edinet-taxonomy",
                "source_version": "2026-final",
                "source_locator": "sheet:1,row:1",
                "raw_snapshot_hash": "2fb26e82471d7570e51588996f89c80dc2db8aa74b0bcb0203ead36c588d5c86",
                "source_term_exact": surface,
                "reuse_status": "GREEN"
            }],
            pro_level_candidate="PRO-A1",
            priority={"professional_importance": "high", "workplace_frequency": "high"},
            state=CanaryState.CANDIDATE
        )

    def test_valid_lifecycle_progression(self):
        """candidate -> selected -> validation_passed -> human_review_passed -> promotion_eligible -> canary"""
        cand = self._create_dummy_candidate()
        assert cand.state == CanaryState.CANDIDATE

        PromotionStateMachine.transition(cand, CanaryState.SELECTED_FOR_CANARY, "test", "selected")
        assert cand.state == CanaryState.SELECTED_FOR_CANARY

        PromotionStateMachine.transition(cand, CanaryState.VALIDATION_PASSED, "test", "val passed")
        assert cand.state == CanaryState.VALIDATION_PASSED

        # Human review approval
        cand.human_review = {"decision": HumanReviewDecision.APPROVE.value, "reviewer": "auditor"}
        PromotionStateMachine.transition(cand, CanaryState.HUMAN_REVIEW_PASSED, "test", "human approved")
        assert cand.state == CanaryState.HUMAN_REVIEW_PASSED

        PromotionStateMachine.transition(cand, CanaryState.PROMOTION_ELIGIBLE, "test", "eligible")
        assert cand.state == CanaryState.PROMOTION_ELIGIBLE

        PromotionStateMachine.transition(cand, CanaryState.CANARY, "test", "promoted to canary")
        assert cand.state == CanaryState.CANARY

    def test_illegal_jump_candidate_to_canary(self):
        """Direct jump from candidate to canary must raise InvalidStateTransitionError."""
        cand = self._create_dummy_candidate()
        with pytest.raises(InvalidStateTransitionError):
            PromotionStateMachine.transition(cand, CanaryState.CANARY, "test", "illegal jump")

    def test_illegal_jump_selected_to_canary(self):
        """Direct jump from selected_for_canary to canary must raise InvalidStateTransitionError."""
        cand = self._create_dummy_candidate()
        PromotionStateMachine.transition(cand, CanaryState.SELECTED_FOR_CANARY, "test", "selected")
        with pytest.raises(InvalidStateTransitionError):
            PromotionStateMachine.transition(cand, CanaryState.CANARY, "test", "illegal jump")

    def test_unapproved_promotion_blocked(self):
        """Promotion to canary without HumanReviewDecision.APPROVE raises UnapprovedPromotionError."""
        cand = self._create_dummy_candidate()
        PromotionStateMachine.transition(cand, CanaryState.SELECTED_FOR_CANARY, "test", "selected")
        PromotionStateMachine.transition(cand, CanaryState.VALIDATION_PASSED, "test", "val passed")
        PromotionStateMachine.transition(cand, CanaryState.HUMAN_REVIEW_PASSED, "test", "human passed")
        PromotionStateMachine.transition(cand, CanaryState.PROMOTION_ELIGIBLE, "test", "eligible")

        # Without human_review approval
        cand.human_review = None
        with pytest.raises(UnapprovedPromotionError):
            PromotionStateMachine.transition(cand, CanaryState.CANARY, "test", "promote without review")

        # With REJECT decision
        cand.human_review = {"decision": HumanReviewDecision.REJECT.value}
        with pytest.raises(UnapprovedPromotionError):
            PromotionStateMachine.transition(cand, CanaryState.CANARY, "test", "promote rejected")


# -----------------------------------------------------------------------------
# 3. Dedup & Variation Gates Tests
# -----------------------------------------------------------------------------
class TestDedupAndVariationGates:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.validator = CanaryValidator(
            taxonomy_path=BASE_DIR / "config" / "domain_taxonomy.yaml",
            production_path=BASE_DIR / "data" / "production_vocabulary.jsonl",
            golden_v1_path=BASE_DIR / "data" / "releases" / "golden-pilot-v1" / "vocabulary.jsonl",
            golden_v1_1_path=BASE_DIR / "data" / "releases" / "golden-pilot-v1.1" / "vocabulary.jsonl"
        )

    def _create_record(self, surface, domain="accounting", subdomain="financial_accounting"):
        return CanaryCandidateRecord(
            candidate_id="test-rec",
            surface=surface,
            normalized_surface=surface,
            reading="てすと",
            domain=domain,
            subdomain=subdomain,
            meaning_gloss="Test gloss",
            authority_class="A",
            reuse_status="GREEN",
            source_evidence=[{
                "source_id": "fsa-edinet-taxonomy",
                "source_version": "2026-final",
                "source_locator": "sheet:1,row:1",
                "raw_snapshot_hash": "2fb26e82471d7570e51588996f89c80dc2db8aa74b0bcb0203ead36c588d5c86",
                "source_term_exact": surface,
                "reuse_status": "GREEN"
            }],
            pro_level_candidate="PRO-A1",
            priority={"professional_importance": "high", "workplace_frequency": "high"},
            state=CanaryState.SELECTED_FOR_CANARY
        )

    def test_exact_duplicate_detection(self):
        """Existing baseline term '減価償却累計額' in accounting is detected as exact duplicate."""
        rec = self._create_record("減価償却累計額", domain="accounting", subdomain="fixed_assets")
        res = self.validator.validate_gate_b_dedup(rec, {})
        assert res.status == GateStatus.FAIL
        assert any("Exact duplicate" in r for r in res.reasons)

    def test_orthographic_variant_detection(self):
        """Orthographic variant '売り掛け金' is detected and mapped to '売掛金'."""
        rec = self._create_record("売り掛け金", domain="accounting", subdomain="financial_accounting")
        res = self.validator.validate_gate_b_dedup(rec, {})
        assert res.status == GateStatus.NEEDS_REVIEW
        assert res.details.get("variant_target") == "売掛金"

    def test_abbreviation_detection(self):
        """Abbreviation 'NACCS' is detected and mapped to '輸出入・港湾関連情報処理システム'."""
        rec = self._create_record("NACCS", domain="trade", subdomain="customs_clearance")
        res = self.validator.validate_gate_b_dedup(rec, {})
        assert res.status == GateStatus.NEEDS_REVIEW
        assert res.details.get("abbreviation_full_form") == "輸出入・港湾関連情報処理システム"

    def test_polysemy_cross_domain_ambiguity(self):
        """Term '手付金' in trade collides with baseline '手付金' in business -> detected as polysemy."""
        rec = self._create_record("手付金", domain="trade", subdomain="contracts")
        res = self.validator.validate_gate_b_dedup(rec, {})
        assert res.status == GateStatus.NEEDS_REVIEW
        assert res.details.get("polysemy_detected") is True


# -----------------------------------------------------------------------------
# 4. Japanese Linguistic Validation Tests
# -----------------------------------------------------------------------------
class TestLinguisticValidationGate:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.validator = CanaryValidator(
            taxonomy_path=BASE_DIR / "config" / "domain_taxonomy.yaml",
            production_path=BASE_DIR / "data" / "production_vocabulary.jsonl",
            golden_v1_path=BASE_DIR / "data" / "releases" / "golden-pilot-v1" / "vocabulary.jsonl",
            golden_v1_1_path=BASE_DIR / "data" / "releases" / "golden-pilot-v1.1" / "vocabulary.jsonl"
        )

    def _create_record(self, surface, reading, gloss="Standard gloss"):
        return CanaryCandidateRecord(
            candidate_id="test-rec",
            surface=surface,
            normalized_surface=surface,
            reading=reading,
            domain="finance",
            subdomain="corporate_finance",
            meaning_gloss=gloss,
            authority_class="A",
            reuse_status="GREEN",
            source_evidence=[{
                "source_id": "fsa-edinet-taxonomy",
                "source_version": "2026-final",
                "source_locator": "sheet:1,row:1",
                "raw_snapshot_hash": "2fb26e82471d7570e51588996f89c80dc2db8aa74b0bcb0203ead36c588d5c86",
                "source_term_exact": surface,
                "reuse_status": "GREEN"
            }],
            pro_level_candidate="PRO-A1",
            priority={"professional_importance": "high", "workplace_frequency": "high"},
            state=CanaryState.SELECTED_FOR_CANARY
        )

    def test_valid_katakana_middle_dot(self):
        """Katakana loanword with middle dot 'キャッシュ・フロー' passes Gate C."""
        rec = self._create_record("キャッシュ・フロー", "きゃっしゅ・ふろー")
        res = self.validator.validate_gate_c_linguistics(rec)
        assert res.status == GateStatus.PASS

    def test_non_kana_reading_fails(self):
        """Reading with unconverted latin characters fails Gate C."""
        rec = self._create_record("貸借対照表(B/S)", "たいしゃくたいしょうひょうBS")
        res = self.validator.validate_gate_c_linguistics(rec)
        assert res.status == GateStatus.FAIL
        assert any("non-kana" in r for r in res.reasons)

    def test_vietnamese_diacritic_leakage_fails(self):
        """English gloss contaminated with Vietnamese diacritics fails Gate C."""
        rec = self._create_record("売掛金", "うりかけきん", gloss="Tài sản ngắn hạn và công nợ")
        res = self.validator.validate_gate_c_linguistics(rec)
        assert res.status == GateStatus.FAIL
        assert any("Vietnamese diacritics leakage" in r for r in res.reasons)


# -----------------------------------------------------------------------------
# 5. Provenance & Licensing Integrity Tests
# -----------------------------------------------------------------------------
class TestProvenanceAndLicensing:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.validator = CanaryValidator(
            taxonomy_path=BASE_DIR / "config" / "domain_taxonomy.yaml",
            production_path=BASE_DIR / "data" / "production_vocabulary.jsonl",
            golden_v1_path=BASE_DIR / "data" / "releases" / "golden-pilot-v1" / "vocabulary.jsonl",
            golden_v1_1_path=BASE_DIR / "data" / "releases" / "golden-pilot-v1.1" / "vocabulary.jsonl"
        )

    def test_red_source_blocked(self):
        """Candidate with reuse_status RED must fail Gate A and transition to licensing_blocked."""
        rec = CanaryCandidateRecord(
            candidate_id="test-red",
            surface="著作権侵害リスク用語",
            normalized_surface="著作権侵害リスク用語",
            reading="ちょさくけんしんがいりすくようご",
            domain="legal",
            subdomain="corporate_law",
            meaning_gloss="Copyrighted text",
            authority_class="C",
            reuse_status="RED",
            source_evidence=[{
                "source_id": "test-red-source",
                "source_version": "2026",
                "source_locator": "p:1",
                "raw_snapshot_hash": "2fb26e82471d7570e51588996f89c80dc2db8aa74b0bcb0203ead36c588d5c86",
                "source_term_exact": "著作権侵害リスク用語",
                "reuse_status": "RED"
            }],
            pro_level_candidate="PRO-A3",
            priority={"professional_importance": "low", "workplace_frequency": "low"},
            state=CanaryState.SELECTED_FOR_CANARY
        )
        self.validator.validate_candidate(rec, {})
        assert rec.state == CanaryState.LICENSING_BLOCKED

    def test_missing_evidence_fields_blocked(self):
        """Candidate missing raw_snapshot_hash or source_locator fails Gate A."""
        rec = CanaryCandidateRecord(
            candidate_id="test-incomplete",
            surface="不完全証跡用語",
            normalized_surface="不完全証跡用語",
            reading="ふかんぜんしょうせきようご",
            domain="accounting",
            subdomain="financial_accounting",
            meaning_gloss="Incomplete evidence",
            authority_class="A",
            reuse_status="GREEN",
            source_evidence=[{
                "source_id": "fsa-edinet-taxonomy",
                "source_version": "2026-final",
                # missing source_locator and raw_snapshot_hash
                "source_term_exact": "不完全証跡用語"
            }],
            pro_level_candidate="PRO-A3",
            priority={"professional_importance": "low", "workplace_frequency": "low"},
            state=CanaryState.SELECTED_FOR_CANARY
        )
        self.validator.validate_candidate(rec, {})
        assert rec.state == CanaryState.INSUFFICIENT_EVIDENCE


# -----------------------------------------------------------------------------
# 6. Human Review & Release Promotion Boundary Tests
# -----------------------------------------------------------------------------
class TestHumanReviewAndReleaseBoundary:
    def test_pending_human_review_blocks_canary_release(self, tmp_path):
        """When candidates are pending human review, CanaryReleaseBuilder does NOT create release."""
        cand = CanaryCandidateRecord(
            candidate_id="cand-001",
            surface="収益認識",
            normalized_surface="収益認識",
            reading="しゅうえきにんしき",
            domain="accounting",
            subdomain="financial_accounting",
            meaning_gloss="Revenue recognition",
            authority_class="B",
            reuse_status="YELLOW",
            source_evidence=[{
                "source_id": "asbj-accounting-standards",
                "source_version": "2026",
                "source_locator": "standard:29",
                "raw_snapshot_hash": "504d0191ee02791e4335788c9444b2585aad3479bca978c06034b1e146fc85ac",
                "source_term_exact": "収益認識",
                "reuse_status": "YELLOW"
            }],
            pro_level_candidate="PRO-A1",
            priority={"professional_importance": "high", "workplace_frequency": "high"},
            state=CanaryState.VALIDATION_PASSED
        )

        res = CanaryReleaseBuilder.build_canary_release(
            records=[cand],
            release_dir=tmp_path / "canary_release",
            md_report_path=tmp_path / "report.md",
            json_report_path=tmp_path / "report.json"
        )

        assert res["release_created"] is False
        assert res["status"] == "READY_FOR_HUMAN_REVIEW"
        assert not (tmp_path / "canary_release" / "vocabulary.jsonl").exists()

    def test_promotion_workflow_with_human_approval(self, tmp_path):
        """With explicit human approval, CanaryReleaseBuilder creates isolated release with manifests."""
        cand = CanaryCandidateRecord(
            candidate_id="cand-001",
            surface="収益認識",
            normalized_surface="収益認識",
            reading="しゅうえきにんしき",
            domain="accounting",
            subdomain="financial_accounting",
            meaning_gloss="Revenue recognition",
            authority_class="B",
            reuse_status="YELLOW",
            source_evidence=[{
                "source_id": "asbj-accounting-standards",
                "source_version": "2026",
                "source_locator": "standard:29",
                "raw_snapshot_hash": "504d0191ee02791e4335788c9444b2585aad3479bca978c06034b1e146fc85ac",
                "source_term_exact": "収益認識",
                "reuse_status": "YELLOW"
            }],
            pro_level_candidate="PRO-A1",
            priority={"professional_importance": "high", "workplace_frequency": "high"},
            state=CanaryState.VALIDATION_PASSED,
            human_review={"decision": HumanReviewDecision.APPROVE.value, "reviewer": "auditor"}
        )

        # Transition candidate to promotion eligible
        PromotionStateMachine.transition(cand, CanaryState.HUMAN_REVIEW_PASSED, "human", "approved")
        PromotionStateMachine.transition(cand, CanaryState.PROMOTION_ELIGIBLE, "pipeline", "eligible")

        release_dir = tmp_path / "canary_release"
        res = CanaryReleaseBuilder.build_canary_release(
            records=[cand],
            release_dir=release_dir,
            md_report_path=tmp_path / "report.md",
            json_report_path=tmp_path / "report.json"
        )

        assert res["release_created"] is True
        assert res["status"] in ("CANARY_RELEASE_READY", "CANARY_1_2C_RELEASED")
        assert res["promoted_count"] == 1
        assert (release_dir / "vocabulary.jsonl").exists()
        assert (release_dir / "dataset_manifest.json").exists()
        assert (release_dir / "validation_manifest.json").exists()
        assert (release_dir / "checksums.sha256").exists()

        # Check manifest parent baseline link
        with open(release_dir / "dataset_manifest.json", "r") as f:
            man = json.load(f)
            assert man["parent_baseline"] == "golden-pilot-v1.1"


# -----------------------------------------------------------------------------
# 7. Frozen Baseline Immutability Tests
# -----------------------------------------------------------------------------
class TestBaselineImmutability:
    def test_golden_pilot_v1_unchanged(self):
        """Golden Pilot v1 vocabulary and canonical hash must be unchanged."""
        v1_dir = BASE_DIR / "data" / "releases" / "golden-pilot-v1"
        vocab_path = v1_dir / "vocabulary.jsonl"
        assert vocab_path.exists()
        assert get_file_sha256(vocab_path) == GOLDEN_PILOT_V1_VOCAB_HASH

        with open(vocab_path, "r", encoding="utf-8") as f:
            records = [json.loads(line) for line in f if line.strip()]
        assert len(records) == 800
        assert compute_canonical_dataset_hash(records) == GOLDEN_PILOT_V1_CANONICAL_HASH

    def test_golden_pilot_v1_1_unchanged(self):
        """Golden Pilot v1.1 vocabulary and canonical hash must be unchanged."""
        v1_1_dir = BASE_DIR / "data" / "releases" / "golden-pilot-v1.1"
        vocab_path = v1_1_dir / "vocabulary.jsonl"
        assert vocab_path.exists()
        assert get_file_sha256(vocab_path) == GOLDEN_PILOT_V1_1_VOCAB_HASH

        with open(vocab_path, "r", encoding="utf-8") as f:
            records = [json.loads(line) for line in f if line.strip()]
        assert len(records) == 800
        assert compute_canonical_dataset_hash(records) == GOLDEN_PILOT_V1_1_CANONICAL_HASH

    def test_production_vocabulary_count_strictly_800(self):
        """Production vocabulary must remain strictly 800 records (no canary leakage)."""
        prod_path = BASE_DIR / "data" / "production" / "vocabulary.jsonl"
        assert prod_path.exists()
        with open(prod_path, "r", encoding="utf-8") as f:
            prod_records = [json.loads(line) for line in f if line.strip()]
        assert len(prod_records) == 800


# -----------------------------------------------------------------------------
# 8. Human Review Package & Quality Audit Tests
# -----------------------------------------------------------------------------
class TestHumanReviewPackageIntegrity:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.pack_jsonl = BASE_DIR / "staging" / "review_queue" / "canary_1_2c_human_review_ready.jsonl"
        self.pack_json = BASE_DIR / "reports" / "phase_1_2c_human_review_pack.json"
        self.pack_md = BASE_DIR / "reports" / "phase_1_2c_human_review_pack.md"
        assert self.pack_jsonl.exists()
        assert self.pack_json.exists()
        assert self.pack_md.exists()

        with open(self.pack_jsonl, "r", encoding="utf-8") as f:
            self.records = [json.loads(l) for l in f if l.strip()]

    def test_review_pack_counts_and_uniqueness(self):
        """Exactly 120 unique candidates with unique candidate IDs and proposed IDs."""
        assert len(self.records) == 120
        cids = [r["candidate_id"] for r in self.records]
        assert len(set(cids)) == 120
        pids = [r["proposed_id"] for r in self.records]
        assert len(set(pids)) == 120

    def test_all_11_domains_present(self):
        """All 11 professional domains are represented in the review pack."""
        domains = {r["domain"] for r in self.records}
        assert len(domains) == 11
        expected = {
            "accounting", "finance", "tax", "hr", "trade", "legal",
            "office_communication", "business", "management", "purchasing", "sales"
        }
        assert domains == expected

    def test_review_complexity_classification_valid(self):
        """Every record is classified into REVIEW-A, REVIEW-B, or REVIEW-C."""
        valid_complexities = {"REVIEW-A", "REVIEW-B", "REVIEW-C"}
        for r in self.records:
            assert r.get("review_complexity") in valid_complexities
            assert isinstance(r.get("quality_flags"), list)

    def test_naccs_is_review_c_abbreviation(self):
        """NACCS must be classified as REVIEW-C and flagged as an abbreviation."""
        naccs_rec = next((r for r in self.records if r["surface"] == "NACCS"), None)
        assert naccs_rec is not None
        assert naccs_rec["review_complexity"] == "REVIEW-C"
        assert "ABBREVIATION_FLAG" in naccs_rec["quality_flags"]
        assert naccs_rec["suggested_relationship"]["type"] == "ABBREVIATION_OF"
        assert naccs_rec["suggested_relationship"]["target_surface"] == "輸出入・港湾関連情報処理システム"

    def test_reading_corrections_flagged(self):
        """Linguistic phonetic bugs (e.g. 貸出金 -> たいしゅつきん) are flagged with READING_REVIEW_REQUIRED."""
        kashidashi = next((r for r in self.records if r["surface"] == "貸出金"), None)
        assert kashidashi is not None
        assert "READING_REVIEW_REQUIRED" in kashidashi["quality_flags"]
        assert kashidashi["suggested_reading"] == "かしだしきん"
        assert kashidashi["review_complexity"] == "REVIEW-C"

    def test_human_decisions_strictly_pending(self):
        """No automated approvals: all 120 records must have human_decision PENDING."""
        for r in self.records:
            assert r["human_decision"] == HumanReviewDecision.PENDING.value
            assert r["reviewer"] is None
            assert r["reviewed_at"] is None


# -----------------------------------------------------------------------------
# 9. Decision Importer & Revalidation Loop Tests
# -----------------------------------------------------------------------------
class TestDecisionImporterAndRevalidationLoop:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.importer = CanaryDecisionImporter()

    def _create_candidate(self, cid="cand-test", surface="貸出金", reading="たいしゅつきん"):
        return CanaryCandidateRecord(
            candidate_id=cid,
            surface=surface,
            normalized_surface=surface,
            reading=reading,
            domain="finance",
            subdomain="banking",
            meaning_gloss="Loans and bills discounted",
            authority_class="A",
            reuse_status="GREEN",
            source_evidence=[{
                "source_id": "fsa-edinet-taxonomy",
                "source_version": "2026-final",
                "source_locator": "sheet:banking,row:1",
                "raw_snapshot_hash": "2fb26e82471d7570e51588996f89c80dc2db8aa74b0bcb0203ead36c588d5c86",
                "source_term_exact": surface,
                "reuse_status": "GREEN"
            }],
            pro_level_candidate="PRO-A1",
            priority={"workplace_frequency": "high", "professional_importance": "high"},
            state=CanaryState.VALIDATION_PASSED
        )

    def test_pending_decision_blocks_promotion(self):
        """Candidate with PENDING decision cannot promote."""
        cand = self._create_candidate()
        decision = {"decision": "PENDING"}
        res = self.importer.apply_decision(cand, decision, {})
        assert res.state == CanaryState.VALIDATION_PASSED
        assert not PromotionStateMachine.can_promote(res)

    def test_approve_decision_transitions_to_eligible(self):
        """Valid APPROVE decision transitions candidate to PROMOTION_ELIGIBLE."""
        cand = self._create_candidate()
        decision = {
            "decision": "APPROVE",
            "reviewer": "lead_terminologist",
            "reviewed_at": "2026-10-01T06:00:00Z",
            "notes": "Approved"
        }
        res = self.importer.apply_decision(cand, decision, {})
        assert res.state == CanaryState.PROMOTION_ELIGIBLE
        assert PromotionStateMachine.can_promote(res)

    def test_reject_decision_transitions_to_rejected(self):
        """REJECT decision transitions candidate to REJECTED and blocks promotion."""
        cand = self._create_candidate()
        decision = {
            "decision": "REJECT",
            "reviewer": "lead_terminologist",
            "reviewed_at": "2026-10-01T06:00:00Z",
            "notes": "Non-vocabulary artifact"
        }
        res = self.importer.apply_decision(cand, decision, {})
        assert res.state == CanaryState.REJECTED
        assert not PromotionStateMachine.can_promote(res)

    def test_needs_revision_blocks_promotion(self):
        """NEEDS_REVISION transitions to NEEDS_REVIEW and blocks promotion."""
        cand = self._create_candidate()
        decision = {
            "decision": "NEEDS_REVISION",
            "reviewer": "lead_terminologist",
            "reviewed_at": "2026-10-01T06:00:00Z",
            "notes": "Needs reading correction"
        }
        res = self.importer.apply_decision(cand, decision, {})
        assert res.state == CanaryState.NEEDS_REVIEW
        assert not PromotionStateMachine.can_promote(res)

    def test_variant_requires_target_id(self):
        """VARIANT_OF decision without target_id raises DecisionValidationError."""
        cand = self._create_candidate()
        decision = {
            "decision": "VARIANT_OF",
            "reviewer": "lead_terminologist",
            "reviewed_at": "2026-10-01T06:00:00Z"
            # Missing target_id
        }
        with pytest.raises(DecisionValidationError):
            self.importer.apply_decision(cand, decision, {})

    def test_empty_reviewer_rejected(self):
        """Completed decision with empty reviewer raises DecisionValidationError."""
        cand = self._create_candidate()
        decision = {
            "decision": "APPROVE",
            "reviewer": "",
            "reviewed_at": "2026-10-01T06:00:00Z"
        }
        with pytest.raises(DecisionValidationError):
            self.importer.apply_decision(cand, decision, {})

    def test_missing_timestamp_rejected(self):
        """Completed decision without timestamp raises DecisionValidationError."""
        cand = self._create_candidate()
        decision = {
            "decision": "APPROVE",
            "reviewer": "lead_terminologist"
            # Missing reviewed_at
        }
        with pytest.raises(DecisionValidationError):
            self.importer.apply_decision(cand, decision, {})

    def test_revision_revalidation_loop_success(self):
        """Revision with valid reading (貸出金 -> かしだしきん) revalidates and becomes eligible."""
        cand = self._create_candidate(surface="貸出金", reading="たいしゅつきん")
        decision = {
            "decision": "APPROVE",
            "reviewer": "lead_terminologist",
            "reviewed_at": "2026-10-01T06:00:00Z",
            "revised_reading": "かしだしきん",
            "notes": "Corrected reading to standard banking reading"
        }
        res = self.importer.apply_decision(cand, decision, {})
        assert res.reading == "かしだしきん"
        assert res.state == CanaryState.PROMOTION_ELIGIBLE

    def test_revision_revalidation_loop_failure(self):
        """Revision with invalid reading (non-kana characters) fails revalidation."""
        cand = self._create_candidate(surface="貸出金", reading="たいしゅつきん")
        decision = {
            "decision": "APPROVE",
            "reviewer": "lead_terminologist",
            "reviewed_at": "2026-10-01T06:00:00Z",
            "revised_reading": "かしだしきん123"  # Contains invalid ASCII digits in reading
        }
        with pytest.raises(RevalidationFailedError):
            self.importer.apply_decision(cand, decision, {})


# -----------------------------------------------------------------------------
# 10. Candidate Pool Versioning Tests
# -----------------------------------------------------------------------------
class TestCandidatePoolVersioning:
    def test_candidate_pool_manifest_exists_and_matches(self):
        """Candidate pool manifest exists, candidate count is 1755, and sha256 matches."""
        manifest_path = BASE_DIR / "staging" / "candidate_pool_manifest.json"
        assert manifest_path.exists()

        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)

        assert manifest["candidate_count"] == 1755
        pool_file = BASE_DIR / "staging" / "canary_candidate_pool.jsonl"
        assert pool_file.exists()

        with open(pool_file, "r", encoding="utf-8") as f:
            actual_count = sum(1 for line in f if line.strip())
        assert actual_count == manifest["candidate_count"]

        actual_sha = get_file_sha256(pool_file)
        assert actual_sha == manifest["sha256"]


# -----------------------------------------------------------------------------
# 11. Historical Report Immutability Tests
# -----------------------------------------------------------------------------
class TestHistoricalReportImmutability:
    def test_historical_phase_1_2b_reports_archived_and_immutable(self):
        """Archived Phase 1.2B closure reports exist and their SHA-256 hashes match manifest."""
        archive_dir = BASE_DIR / "reports" / "archive" / "phase_1_2b"
        manifest_path = archive_dir / "manifest.json"
        assert archive_dir.exists()
        assert manifest_path.exists()

        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)

        assert manifest["policy"] == "IMMUTABLE_HISTORICAL_RECORD"
        assert len(manifest["files"]) >= 7

        for filename, meta in manifest["files"].items():
            fpath = archive_dir / filename
            assert fpath.exists(), f"Archived file {filename} missing"
            computed_sha = get_file_sha256(fpath)
            assert computed_sha == meta["sha256"], f"Historical report {filename} modified!"


# -----------------------------------------------------------------------------
# 12. Decision Ingestion & Validation Integrity Tests (Section 27)
# -----------------------------------------------------------------------------
class TestDecisionIngestionAndProvenance:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.importer = CanaryDecisionImporter()
        self.decisions_file = BASE_DIR / "staging" / "review_decisions" / "canary_1_2c_authorized_decisions.jsonl"
        self.queue_file = BASE_DIR / "staging" / "review_queue" / "canary_1_2c_human_review_ready.jsonl"

    def test_every_decision_references_valid_candidate(self):
        """Every decision record must reference an existing selected candidate in review ready queue."""
        assert self.decisions_file.exists()
        with open(self.queue_file, "r", encoding="utf-8") as qf:
            valid_cids = {json.loads(line)["candidate_id"] for line in qf if line.strip()}

        with open(self.decisions_file, "r", encoding="utf-8") as df:
            decisions = [json.loads(line) for line in df if line.strip()]

        assert len(decisions) == 120
        for d in decisions:
            assert d["candidate_id"] in valid_cids

    def test_duplicate_decisions_rejected(self, tmp_path):
        """Duplicate decisions for the same candidate_id are strictly rejected."""
        dup_file = tmp_path / "dup_decisions.jsonl"
        d1 = {
            "candidate_id": "cand-001",
            "decision": "APPROVE",
            "reviewer": "authorized-human-review",
            "reviewed_at": "2026-10-01T07:30:00Z"
        }
        d2 = {
            "candidate_id": "cand-001",
            "decision": "REJECT",
            "reviewer": "authorized-human-review",
            "reviewed_at": "2026-10-01T07:30:00Z"
        }
        with open(dup_file, "w", encoding="utf-8") as f:
            f.write(json.dumps(d1) + "\n" + json.dumps(d2) + "\n")

        with pytest.raises(DecisionValidationError, match="Duplicate decision"):
            self.importer.load_decisions(dup_file)

    def test_unauthorized_decision_type_rejected(self):
        """Unauthorized decision type raises DecisionValidationError."""
        cand = CanaryCandidateRecord(
            candidate_id="cand-001",
            surface="テスト",
            normalized_surface="テスト",
            reading="てすと",
            domain="business",
            subdomain="general",
            meaning_gloss="Test",
            authority_class="A",
            reuse_status="GREEN",
            source_evidence=[],
            pro_level_candidate="PRO-A1",
            priority={}
        )
        invalid_decision = {
            "decision": "UNAUTHORIZED_AUTO_APPROVE",
            "reviewer": "authorized-human-review",
            "reviewed_at": "2026-10-01T07:30:00Z"
        }
        with pytest.raises(DecisionValidationError, match="Invalid decision"):
            self.importer.apply_decision(cand, invalid_decision, {})

    def test_reviewer_provenance_required(self):
        """Completed decision without reviewer provenance raises DecisionValidationError."""
        cand = CanaryCandidateRecord(
            candidate_id="cand-001",
            surface="テスト",
            normalized_surface="テスト",
            reading="てすと",
            domain="business",
            subdomain="general",
            meaning_gloss="Test",
            authority_class="A",
            reuse_status="GREEN",
            source_evidence=[],
            pro_level_candidate="PRO-A1",
            priority={}
        )
        # Missing reviewer
        d_no_reviewer = {"decision": "APPROVE", "reviewed_at": "2026-10-01T07:30:00Z"}
        with pytest.raises(DecisionValidationError, match="non-empty 'reviewer'"):
            self.importer.apply_decision(cand, d_no_reviewer, {})

        # Missing reviewed_at
        d_no_time = {"decision": "APPROVE", "reviewer": "authorized-human-review"}
        with pytest.raises(DecisionValidationError, match="'reviewed_at' timestamp"):
            self.importer.apply_decision(cand, d_no_time, {})


# -----------------------------------------------------------------------------
# 13. Authoritative Reading Corrections (Section 5 & 27)
# -----------------------------------------------------------------------------
class TestAuthoritativeReadingCorrections:
    CORRECTIONS_FIXTURES = [
        ("加盟店貸勘定", "かめいてんかしかんじょう", "かめいてんたいかんじょう"),
        ("買現先勘定", "かいげんさきかんじょう", "ばいげんさきかんじょう"),
        ("貸出金", "かしだしきん", "たいしゅつきん"),
        ("特定輸出者", "とくていゆしゅつしゃ", "とくていゆしゅつもの"),
        ("資本金の額", "しほんきんのがく", "しほんきんのひたい"),
        ("準備金の額", "じゅんびきんのがく", "じゅんびきんのひたい"),
        ("顛末書", "てんまつしょ", "てんまつかき"),
        ("事業計画書", "じぎょうけいかくしょ", "じぎょうけいかくかき"),
        (
            "印紙税法別表第一課税物件表の適用に関する通則",
            "いんしぜいほうべっぴょうだいいっかぜいぶっけんひょうのてきようにかんするつうそく",
            "いんしぜいほうべっぴょうだいいっかぜいぶっけんおもてのてきようにかんするつうそく"
        ),
    ]

    @pytest.mark.parametrize("surface,correct_reading,incorrect_reading", CORRECTIONS_FIXTURES)
    def test_reading_corrections_present_in_release(self, surface, correct_reading, incorrect_reading):
        """All 9 authoritative reading corrections appear with their correct reading in vocabulary.jsonl."""
        vocab_path = BASE_DIR / "data" / "releases" / "canary-1.2c" / "vocabulary.jsonl"
        assert vocab_path.exists()

        found = False
        with open(vocab_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    item = json.loads(line)
                    if item["term"]["surface"] == surface:
                        found = True
                        assert item["term"]["reading"] == correct_reading
                        assert item["term"]["reading"] != incorrect_reading
        assert found, f"Term '{surface}' missing from Canary vocabulary release!"


# -----------------------------------------------------------------------------
# 14. Authoritative Gloss Corrections & Integrity (Section 6, 12, 13, 27)
# -----------------------------------------------------------------------------
class TestGlossCorrectionsAndIntegrity:
    SEMANTIC_GLOSS_FIXTURES = [
        ("収益認識", "Revenue recognition", "Financial Accounting"),
        ("住民税", "Inhabitant tax / Municipal resident tax", "Local Tax"),
        ("非課税所得", "Tax-exempt income", "Income Tax"),
        ("適格請求書", "Qualified invoice (Japanese invoice system)", "Consumption Tax"),
        ("印紙税法基本通達", "Basic Circular on Stamp Tax Law", "Tax Filing"),
        ("印紙税法", "Stamp Tax Act", "Tax Filing"),
        ("印紙税法施行令", "Order for Enforcement of the Stamp Tax Act", "Tax Filing"),
        ("行政不服審査法", "Administrative Complaint Review Act", "Tax Filing"),
        ("行政事件訴訟法", "Administrative Case Litigation Act", "Tax Filing"),
        ("通関手続", "Customs clearance procedure", "Customs clearance"),
        ("36協定", "Article 36 Agreement (overtime work agreement)", "Article 36 Agreement (Overtime work agreement"),
        ("支払渡し", "Documents against Payment (D/P)", "Documents against Payment (D/P"),
        ("引受渡し", "Documents against Acceptance (D/A)", "Documents against Acceptance (D/A"),
        ("特恵関税", "Preferential tariff", "Generalized System of Preferences (GSP"),
        ("拝啓", "Dear Sir/Madam (formal opening)", "Dear Sir/Madam (formal opening"),
        ("敬具", "Sincerely yours (formal closing)", "Sincerely yours (formal closing"),
    ]

    @pytest.mark.parametrize("surface,expected_gloss,old_gloss", SEMANTIC_GLOSS_FIXTURES)
    def test_gloss_corrections_applied(self, surface, expected_gloss, old_gloss):
        """Generic category placeholders and unmatched punctuation glosses are repaired."""
        vocab_path = BASE_DIR / "data" / "releases" / "canary-1.2c" / "vocabulary.jsonl"
        with open(vocab_path, "r", encoding="utf-8") as f:
            rec = next((json.loads(line) for line in f if json.loads(line)["term"]["surface"] == surface), None)
        assert rec is not None
        assert rec["meaning"]["en_gloss"] == expected_gloss
        assert rec["meaning"]["en_gloss"] != old_gloss

    def test_gloss_integrity_audit_detects_unmatched_parens(self):
        """GlossIntegrityAuditor detects unmatched parentheses, brackets, and quotes."""
        issues = GlossIntegrityAuditor.audit_single_gloss("テスト", "Broken parens (test")
        codes = [i["code"] for i in issues]
        assert "UNMATCHED_PARENTHESES" in codes

        issues = GlossIntegrityAuditor.audit_single_gloss("テスト", "Broken brackets [test")
        codes = [i["code"] for i in issues]
        assert "UNMATCHED_BRACKETS" in codes

    def test_all_release_glosses_pass_integrity_audit(self):
        """All 102 canonical concepts in canary-1.2c vocabulary have clean glosses."""
        vocab_path = BASE_DIR / "data" / "releases" / "canary-1.2c" / "vocabulary.jsonl"
        with open(vocab_path, "r", encoding="utf-8") as f:
            records = [json.loads(line) for line in f if line.strip()]

        assert len(records) == 102
        for r in records:
            issues = GlossIntegrityAuditor.audit_single_gloss(
                surface=r["term"]["surface"],
                gloss=r["meaning"]["en_gloss"],
                domain=r["domain"]["primary"],
                subdomain=r["domain"]["subdomain"]
            )
            assert not issues, f"Gloss integrity failure on {r['term']['surface']}: {issues}"


# -----------------------------------------------------------------------------
# 15. Extraction Artifact & Composite Taxonomy Rejection (Section 9, 10, 11, 27)
# -----------------------------------------------------------------------------
class TestArtifactAndCompositeTaxonomyRejection:
    COMPOSITE_LABELS = [
        "受取手形、売掛金及び契約資産",
        "受取手形及び売掛金",
        "受取手形及び売掛金(純額)",
        "売掛金及び契約資産",
        "売掛金及び契約資産(純額)",
        "受取手形(純額)",
        "売掛金(純額)",
        "契約資産(純額)",
        "コールローン及び買入手形",
    ]

    def test_yogo_ichiran_rejected_from_canonical_canary(self):
        """Web heading extraction artifact '用語一覧' must NOT enter Canary vocabulary."""
        vocab_path = BASE_DIR / "data" / "releases" / "canary-1.2c" / "vocabulary.jsonl"
        with open(vocab_path, "r", encoding="utf-8") as f:
            surfaces = {json.loads(line)["term"]["surface"] for line in f if line.strip()}
        assert "用語一覧" not in surfaces

        # Must appear in audit trail as rejected
        audit_path = BASE_DIR / "data" / "releases" / "canary-1.2c" / "promotion_audit.jsonl"
        with open(audit_path, "r", encoding="utf-8") as af:
            yogo = next((json.loads(line) for line in af if json.loads(line)["surface"] == "用語一覧"), None)
        assert yogo is not None
        assert yogo["decision"] == "REJECT"
        assert yogo["decision_reason"] == "NON_VOCABULARY_EXTRACTION_ARTIFACT"

    @pytest.mark.parametrize("composite_surface", COMPOSITE_LABELS)
    def test_composite_taxonomy_labels_rejected(self, composite_surface):
        """EDINET composite reporting lines must NOT enter Canary canonical vocabulary."""
        vocab_path = BASE_DIR / "data" / "releases" / "canary-1.2c" / "vocabulary.jsonl"
        with open(vocab_path, "r", encoding="utf-8") as f:
            surfaces = {json.loads(line)["term"]["surface"] for line in f if line.strip()}
        assert composite_surface not in surfaces

    def test_underlying_atomic_concepts_preserved(self):
        """Atomic component concepts (e.g. 契約資産, コールローン, 買入手形) remain canonical."""
        vocab_path = BASE_DIR / "data" / "releases" / "canary-1.2c" / "vocabulary.jsonl"
        with open(vocab_path, "r", encoding="utf-8") as f:
            surfaces = {json.loads(line)["term"]["surface"] for line in f if line.strip()}

        for atomic_term in ["契約資産", "コールローン", "買入手形"]:
            assert atomic_term in surfaces, f"Valid atomic concept '{atomic_term}' should be preserved!"


# -----------------------------------------------------------------------------
# 16. Abbreviation Relationships & Target Integrity (Section 7, 8, 18, 27)
# -----------------------------------------------------------------------------
class TestAbbreviationRelationshipsAndIntegrity:
    ABBREVIATION_FIXTURES = [
        ("NACCS", "輸出入・港湾関連情報処理システム"),
        ("印法", "印紙税法"),
        ("印基通", "印紙税法基本通達"),
        ("印令", "印紙税法施行令"),
        ("印法通則", "印紙税法別表第一課税物件表の適用に関する通則"),
        ("行審法", "行政不服審査法"),
        ("行訴法", "行政事件訴訟法"),
        (
            "オン化省令",
            "行政手続等における情報通信の技術の利用に関する法律に基づく国税関係法令に係る情報通信技術を活用した行政の推進等に関する省令"
        ),
    ]

    def test_abbreviations_not_in_vocabulary(self):
        """Abbreviations must not inflate canonical concept count in vocabulary.jsonl."""
        vocab_path = BASE_DIR / "data" / "releases" / "canary-1.2c" / "vocabulary.jsonl"
        with open(vocab_path, "r", encoding="utf-8") as f:
            surfaces = {json.loads(line)["term"]["surface"] for line in f if line.strip()}

        for abbrev, _ in self.ABBREVIATION_FIXTURES:
            assert abbrev not in surfaces, f"Abbreviation '{abbrev}' should not be in vocabulary.jsonl!"

    @pytest.mark.parametrize("abbrev,expected_target", ABBREVIATION_FIXTURES)
    def test_abbreviations_mapped_in_relationships(self, abbrev, expected_target):
        """Abbreviations are correctly mapped to targets in relationships.jsonl."""
        rel_path = BASE_DIR / "data" / "releases" / "canary-1.2c" / "relationships.jsonl"
        assert rel_path.exists()
        with open(rel_path, "r", encoding="utf-8") as rf:
            relationships = [json.loads(line) for line in rf if line.strip()]

        match = next((r for r in relationships if r["source_term"] == abbrev), None)
        assert match is not None
        assert match["relationship_type"] == "ABBREVIATION_OF"
        assert match["target_term"] == expected_target

    def test_missing_canonical_target_blocks_release(self, tmp_path):
        """Missing or unresolved relationship target blocks release construction."""
        cand = CanaryCandidateRecord(
            candidate_id="cand-bogus-abbrev",
            surface="テスト略称",
            normalized_surface="テスト略称",
            reading="てすとりゃくしょう",
            domain="trade",
            subdomain="customs_clearance",
            meaning_gloss="Test abbreviation",
            authority_class="A",
            reuse_status="GREEN",
            source_evidence=[{"source_id": "test", "source_version": "1", "source_locator": "1", "raw_snapshot_hash": "a", "source_term_exact": "テスト略称", "reuse_status": "GREEN"}],
            pro_level_candidate="PRO-A1",
            priority={},
            state=CanaryState.VALIDATION_PASSED,
            human_review={
                "decision": "ABBREVIATION_OF",
                "reviewer": "authorized-human-review",
                "reviewed_at": "2026-10-01T07:30:00Z",
                "relationship_type": "ABBREVIATION_OF",
                "relationship_target": "NON_EXISTENT_CANONICAL_TARGET_99999"
            }
        )
        bogus_dec = {
            "candidate_id": "cand-bogus-abbrev",
            "decision": "ABBREVIATION_OF",
            "relationship_target": "NON_EXISTENT_CANONICAL_TARGET_99999"
        }
        with pytest.raises(Exception):
            CanaryReleaseBuilder.build_canary_release(
                records=[cand],
                decisions=[bogus_dec],
                release_dir=tmp_path / "test_blocked_release",
                md_report_path=tmp_path / "test.md",
                json_report_path=tmp_path / "test.json"
            )


# -----------------------------------------------------------------------------
# 17. Quality Flag Deduplication (Section 14 & 27)
# -----------------------------------------------------------------------------
class TestQualityFlagDeduplication:
    def test_quality_flags_deterministic_and_unique(self):
        """Quality flags in human review ready queue must be unique with preserved deterministic order."""
        ready_file = BASE_DIR / "staging" / "review_queue" / "canary_1_2c_human_review_ready.jsonl"
        assert ready_file.exists()
        with open(ready_file, "r", encoding="utf-8") as f:
            records = [json.loads(line) for line in f if line.strip()]

        for r in records:
            flags = r.get("quality_flags", [])
            assert len(flags) == len(set(flags)), f"Duplicate flags detected in {r['surface']}: {flags}"

        # Specifically check net valuation composite line items
        net_recs = [r for r in records if "(純額)" in r["surface"]]
        assert len(net_recs) >= 5
        for nr in net_recs:
            assert nr["quality_flags"].count("CANONICAL_VALUE_REVIEW_REQUIRED") == 1


# -----------------------------------------------------------------------------
# 18. Canary Release Invariants & Baseline Immutability (Section 22, 24, 25, 27)
# -----------------------------------------------------------------------------
class TestCanaryReleaseInvariantsAndImmutability:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.release_dir = BASE_DIR / "data" / "releases" / "canary-1.2c"
        self.manifest_path = self.release_dir / "dataset_manifest.json"
        self.vocab_path = self.release_dir / "vocabulary.jsonl"
        self.rel_path = self.release_dir / "relationships.jsonl"
        self.audit_path = self.release_dir / "promotion_audit.jsonl"

    def test_release_files_exist_and_counts_match_manifest(self):
        """Release manifests, vocabulary, relationships, and audit trails exist with matching counts."""
        assert self.manifest_path.exists()
        assert self.vocab_path.exists()
        assert self.rel_path.exists()
        assert self.audit_path.exists()

        with open(self.manifest_path, "r", encoding="utf-8") as mf:
            m = json.load(mf)

        with open(self.vocab_path, "r", encoding="utf-8") as vf:
            vocab_count = sum(1 for line in vf if line.strip())
        with open(self.rel_path, "r", encoding="utf-8") as rf:
            rel_count = sum(1 for line in rf if line.strip())
        with open(self.audit_path, "r", encoding="utf-8") as af:
            audit_count = sum(1 for line in af if line.strip())

        assert vocab_count == 102
        assert rel_count == 8
        assert audit_count == 120
        assert m["canonical_release_count"] == vocab_count
        assert m["abbreviation_count"] == rel_count
        assert m["selected_count"] == audit_count
        assert m["parent_baseline"] == "golden-pilot-v1.1"

    def test_release_hashes_match_checksums_and_manifest(self):
        """Cryptographic sha256 checksums match across manifest and checksums.sha256."""
        with open(self.manifest_path, "r", encoding="utf-8") as mf:
            m = json.load(mf)

        vocab_hash = get_file_sha256(self.vocab_path)
        rel_hash = get_file_sha256(self.rel_path)

        assert vocab_hash == m["vocabulary_sha256"]
        assert rel_hash == m["relationships_sha256"]

        # Check checksums.sha256 file
        cs_file = self.release_dir / "checksums.sha256"
        assert cs_file.exists()
        with open(cs_file, "r", encoding="utf-8") as f:
            lines = [l.strip().split() for l in f if l.strip()]
        cs_map = {name: h for h, name in lines}

        assert cs_map["vocabulary.jsonl"] == vocab_hash
        assert cs_map["relationships.jsonl"] == rel_hash
        assert cs_map["dataset_manifest.json"] == get_file_sha256(self.manifest_path)

    def test_golden_pilot_v1_and_v1_1_immutable(self):
        """Golden Pilot v1 and v1.1 vocabulary files remain strictly immutable."""
        gp_v1 = BASE_DIR / "data" / "releases" / "golden-pilot-v1" / "vocabulary.jsonl"
        gp_v1_1 = BASE_DIR / "data" / "releases" / "golden-pilot-v1.1" / "vocabulary.jsonl"

        assert get_file_sha256(gp_v1) == GOLDEN_PILOT_V1_VOCAB_HASH
        assert get_file_sha256(gp_v1_1) == GOLDEN_PILOT_V1_1_VOCAB_HASH

    def test_production_vocabulary_remains_strictly_800(self):
        """Production vocabulary remains strictly 800 records and unchanged."""
        prod_vocab = BASE_DIR / "data" / "production" / "vocabulary.jsonl"
        assert prod_vocab.exists()
        assert get_file_sha256(prod_vocab) == GOLDEN_PILOT_V1_1_VOCAB_HASH
        with open(prod_vocab, "r", encoding="utf-8") as pf:
            count = sum(1 for line in pf if line.strip())
        assert count == 800

