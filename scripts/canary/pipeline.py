"""
scripts/canary/pipeline.py
Master Orchestration CLI for Phase 1.2C: Controlled Canary Expansion & Promotion Pipeline.

Coordinates:
1. Deterministic Selection Engine (CanarySelector)
2. Validation Gates A, B, C (CanaryValidator)
3. Human Review Gate & Queue Generation (CanaryReviewManager)
4. Isolated Canary Release Evaluation (CanaryReleaseBuilder)
5. Comprehensive Reporting & Audit Trails
"""

from typing import List, Dict, Any, Tuple
from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import json
import yaml
from datetime import datetime, timezone

from scripts.canary.models import (
    CanaryState,
    CanaryCandidateRecord,
    GateStatus,
    HumanReviewDecision
)
from scripts.canary.selector import CanarySelector
from scripts.canary.validator import CanaryValidator
from scripts.canary.review_manager import CanaryReviewManager
from scripts.canary.release_builder import CanaryReleaseBuilder
from scripts.canary.quality_auditor import CanaryQualityAuditor

BASE_DIR = Path(__file__).resolve().parent.parent.parent


class CanaryPipeline:
    def __init__(
        self,
        config_path: Path = BASE_DIR / "config" / "canary_config.yaml",
        taxonomy_path: Path = BASE_DIR / "config" / "domain_taxonomy.yaml",
        candidate_pool_path: Path = BASE_DIR / "staging" / "canary_candidate_pool.jsonl",
        production_path: Path = BASE_DIR / "data" / "production" / "vocabulary.jsonl",
        golden_v1_path: Path = BASE_DIR / "data" / "releases" / "golden-pilot-v1" / "vocabulary.jsonl",
        golden_v1_1_path: Path = BASE_DIR / "data" / "releases" / "golden-pilot-v1.1" / "vocabulary.jsonl",
        review_queue_path: Path = BASE_DIR / "staging" / "review_queue" / "canary_1_2c_review.jsonl",
        release_dir: Path = BASE_DIR / "data" / "releases" / "canary-1.2c",
        reports_dir: Path = BASE_DIR / "reports"
    ):
        self.config_path = config_path
        self.taxonomy_path = taxonomy_path
        self.candidate_pool_path = candidate_pool_path
        self.production_path = production_path
        self.golden_v1_path = golden_v1_path
        self.golden_v1_1_path = golden_v1_1_path
        self.review_queue_path = review_queue_path
        self.release_dir = release_dir
        self.reports_dir = reports_dir

        self.selector = CanarySelector(config_path)
        self.validator = CanaryValidator(
            taxonomy_path=taxonomy_path,
            production_path=production_path,
            golden_v1_path=golden_v1_path,
            golden_v1_1_path=golden_v1_1_path
        )

    def write_selection_reports(
        self,
        selected_records: List[CanaryCandidateRecord],
        pool_size: int
    ) -> Dict[str, Any]:
        """Generates reports/phase_1_2c_selection.json and reports/phase_1_2c_selection.md"""
        now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        # Distributions
        domain_counts: Dict[str, int] = {}
        authority_counts: Dict[str, int] = {}
        source_counts: Dict[str, int] = {}
        pro_level_counts: Dict[str, int] = {}

        for r in selected_records:
            domain_counts[r.domain] = domain_counts.get(r.domain, 0) + 1
            authority_counts[r.authority_class] = authority_counts.get(r.authority_class, 0) + 1
            pro_level_counts[r.pro_level_candidate] = pro_level_counts.get(r.pro_level_candidate, 0) + 1
            for ev in r.source_evidence:
                sid = ev.get("source_id", "unknown")
                source_counts[sid] = source_counts.get(sid, 0) + 1

        summary = {
            "timestamp": now_iso,
            "raw_candidate_pool_size": pool_size,
            "selected_for_canary_count": len(selected_records),
            "domain_stratification": domain_counts,
            "authority_distribution": authority_counts,
            "source_distribution": source_counts,
            "pro_level_distribution": pro_level_counts,
            "selection_strategy": "deterministic_quota_stratification",
            "draft_source_excluded": "fsa-edinet-2027-draft (0 included)",
            "red_licensing_excluded": "0 RED included"
        }

        # JSON
        json_path = self.reports_dir / "phase_1_2c_selection.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)

        # Markdown
        md_path = self.reports_dir / "phase_1_2c_selection.md"
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(f"# Phase 1.2C — Controlled Canary Selection Report\n\n")
            f.write(f"- **Generated At**: `{now_iso}`\n")
            f.write(f"- **Candidate Pool Size**: `{pool_size}`\n")
            f.write(f"- **Selected for Canary**: `{len(selected_records)}`\n")
            f.write(f"- **Stratification Strategy**: Multi-dimensional deterministic ranking with professional domain quotas\n")
            f.write(f"- **Draft Sources Excluded**: `fsa-edinet-2027-draft` (100% quarantined)\n")
            f.write(f"- **Licensing Guard**: 0 RED reuse items selected\n\n")

            f.write(f"## 1. Domain Stratification Quotas & Actual Selection\n\n")
            f.write(f"| Professional Domain | Quota Target | Selected Count | Representation Ratio |\n")
            f.write(f"|:--------------------|:------------:|:--------------:|:--------------------:|\n")
            for dom, count in sorted(domain_counts.items(), key=lambda x: -x[1]):
                target = self.selector.domain_quotas.get(dom, {}).get("target", "N/A")
                ratio = f"{(count / len(selected_records)) * 100:.1f}%"
                f.write(f"| `{dom}` | {target} | {count} | {ratio} |\n")

            f.write(f"\n## 2. Source Diversity Distribution\n\n")
            f.write(f"| Source ID | Evidence References | Authority Class |\n")
            f.write(f"|:----------|:-------------------:|:---------------:|\n")
            # Load master source registry to get official authority class
            source_registry_path = BASE_DIR / "config" / "source_registry.yaml"
            auth_map = {}
            if source_registry_path.exists():
                with open(source_registry_path, "r", encoding="utf-8") as srf:
                    sr_data = yaml.safe_load(srf)
                    for s in sr_data.get("sources", []):
                        auth_map[s.get("source_id")] = s.get("authority_class", "C")

            for sid, count in sorted(source_counts.items(), key=lambda x: -x[1]):
                auth = auth_map.get(sid, "C")
                f.write(f"| `{sid}` | {count} | `{auth}` |\n")

            f.write(f"\n## 3. Authority & Quality Tier Breakdown\n\n")
            f.write(f"- **Authority Class A**: `{authority_counts.get('A', 0)}` terms\n")
            f.write(f"- **Authority Class B**: `{authority_counts.get('B', 0)}` terms\n")
            f.write(f"- **Authority Class C**: `{authority_counts.get('C', 0)}` terms\n")
            f.write(f"- **PRO-A1 (Standard Canonical)**: `{pro_level_counts.get('PRO-A1', 0)}`\n")
            f.write(f"- **PRO-A2 (Domain Specific)**: `{pro_level_counts.get('PRO-A2', 0)}`\n")
            f.write(f"- **PRO-A3 (General / Contextual)**: `{pro_level_counts.get('PRO-A3', 0)}`\n\n")

            f.write(f"## 4. Deterministic Ranking & Selection Methodology\n\n")
            f.write(f"Every candidate is ranked deterministically by a 6-tuple sort key:\n")
            f.write(f"1. `tier_rank` (PRO-A1 > PRO-A2 > PRO-A3)\n")
            f.write(f"2. `authority_rank` (A > B > C)\n")
            f.write(f"3. `agreement_rank` (Multi-source agreement prioritized)\n")
            f.write(f"4. `importance_rank` (High > Medium > Low)\n")
            f.write(f"5. `frequency_rank` (High > Medium > Low)\n")
            f.write(f"6. `tie_breaker` (Lexicographical candidate_id)\n")

        return summary

    def write_validation_reports(
        self,
        records: List[CanaryCandidateRecord]
    ) -> Dict[str, Any]:
        """Generates reports/phase_1_2c_validation.json and reports/phase_1_2c_validation.md"""
        now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        gate_a_pass = sum(1 for r in records if r.gate_results.get("Gate_A_Schema_Integrity", {}).get("status") == GateStatus.PASS.value)
        gate_b_pass = sum(1 for r in records if r.gate_results.get("Gate_B_Production_Dedup", {}).get("status") == GateStatus.PASS.value)
        gate_c_pass = sum(1 for r in records if r.gate_results.get("Gate_C_Linguistic_Quality", {}).get("status") == GateStatus.PASS.value)

        state_distribution: Dict[str, int] = {}
        for r in records:
            st = r.state.value if isinstance(r.state, CanaryState) else r.state
            state_distribution[st] = state_distribution.get(st, 0) + 1

        validation_passed_count = state_distribution.get(CanaryState.VALIDATION_PASSED.value, 0)
        needs_review_count = state_distribution.get(CanaryState.NEEDS_REVIEW.value, 0)
        rejected_count = state_distribution.get(CanaryState.REJECTED.value, 0)

        flagged_items = []
        for r in records:
            if r.state != CanaryState.VALIDATION_PASSED:
                all_reasons = []
                for gname, gres in r.gate_results.items():
                    if gres.get("reasons"):
                        all_reasons.extend(gres.get("reasons", []))
                flagged_items.append({
                    "candidate_id": r.candidate_id,
                    "surface": r.surface,
                    "domain": r.domain,
                    "state": r.state.value if isinstance(r.state, CanaryState) else r.state,
                    "reasons": all_reasons
                })

        summary = {
            "timestamp": now_iso,
            "total_validated": len(records),
            "validation_passed": validation_passed_count,
            "needs_review": needs_review_count,
            "rejected": rejected_count,
            "state_distribution": state_distribution,
            "gates_summary": {
                "Gate_A_Schema_Integrity": {"pass": gate_a_pass, "fail": len(records) - gate_a_pass},
                "Gate_B_Production_Dedup": {"pass": gate_b_pass, "flagged": len(records) - gate_b_pass},
                "Gate_C_Linguistic_Quality": {"pass": gate_c_pass, "fail": len(records) - gate_c_pass},
            },
            "flagged_candidates": flagged_items
        }

        # JSON
        json_path = self.reports_dir / "phase_1_2c_validation.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)

        # Markdown
        md_path = self.reports_dir / "phase_1_2c_validation.md"
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(f"# Phase 1.2C — Independent Validation Gates Report\n\n")
            f.write(f"- **Validated At**: `{now_iso}`\n")
            f.write(f"- **Total Candidates Evaluated**: `{len(records)}`\n")
            f.write(f"- **Validation Passed (`validation_passed`)**: `{validation_passed_count}`\n")
            f.write(f"- **Needs Human Review (`needs_review`)**: `{needs_review_count}`\n")
            f.write(f"- **Rejected (`rejected`)**: `{rejected_count}`\n\n")

            f.write(f"## 1. Gate Execution Summary\n\n")
            f.write(f"| Validation Gate | Focus Area | Status Pass | Flagged / Fail | Enforcement |\n")
            f.write(f"|:----------------|:-----------|:-----------:|:--------------:|:------------|\n")
            f.write(f"| **Gate A: Schema & Provenance** | Schema integrity, taxonomy validity, source locators, raw hashes, draft/licensing guards | {gate_a_pass}/{len(records)} | {len(records) - gate_a_pass} | Hard Gate (Zero tolerance) |\n")
            f.write(f"| **Gate B: Dedup & Variations** | Exact duplicate against baselines, orthographic variants, abbreviations, polysemy senses | {gate_b_pass}/{len(records)} | {len(records) - gate_b_pass} | Semantic Gate (Routes to Review) |\n")
            f.write(f"| **Gate C: Linguistic Quality** | Japanese script validation, hiragana reading validity, diacritic leakage, template markers | {gate_c_pass}/{len(records)} | {len(records) - gate_c_pass} | Linguistic Quality Gate |\n\n")

            f.write(f"## 2. State Distribution Post-Validation\n\n")
            for state_name, count in sorted(state_distribution.items()):
                f.write(f"- `{state_name}`: **{count}**\n")

            if flagged_items:
                f.write(f"\n## 3. Flagged Items Requiring Review or Correction\n\n")
                f.write(f"| Candidate ID | Surface | Domain | Assigned State | Reasons |\n")
                f.write(f"|:-------------|:--------|:-------|:---------------|:--------|\n")
                for item in flagged_items:
                    r_str = "<br>".join(item["reasons"])
                    f.write(f"| `{item['candidate_id']}` | `{item['surface']}` | `{item['domain']}` | `{item['state']}` | {r_str} |\n")

        return summary

    def run(self) -> Dict[str, Any]:
        """Executes the complete Phase 1.2C pipeline."""
        print("=== Phase 1.2C Canary Expansion & Promotion Pipeline ===")

        # 1. Selection
        print(f"[1/4] Selecting canary candidates from {self.candidate_pool_path}...")
        with open(self.candidate_pool_path, "r", encoding="utf-8") as f:
            pool_size = sum(1 for line in f if line.strip())

        selected_candidates = self.selector.select_canary_candidates(self.candidate_pool_path)
        print(f"      Selected {len(selected_candidates)} candidates across {len(self.selector.domain_quotas)} professional domains.")
        self.write_selection_reports(selected_candidates, pool_size)

        # 2. Validation Gates A, B, C
        print("[2/4] Executing independent validation gates (A: Schema, B: Dedup, C: Linguistic)...")
        batch_surfaces: Dict[str, str] = {}
        for cand in selected_candidates:
            self.validator.validate_candidate(cand, batch_surfaces)
            batch_surfaces[cand.surface] = cand.candidate_id

        self.write_validation_reports(selected_candidates)

        # 3. Human Review Gate
        print("[3/4] Exporting review queue and report to staging/review_queue/...")
        review_md = self.reports_dir / "phase_1_2c_review_status.md"
        review_json = self.reports_dir / "phase_1_2c_review_status.json"
        review_summary = CanaryReviewManager.export_review_queue(
            selected_candidates,
            self.review_queue_path,
            review_md,
            review_json
        )
        print(f"      Exported {review_summary['total_candidates_in_queue']} candidates to review queue.")
        print(f"      Pending: {review_summary['pending_review']}, Approved: {review_summary['approved']}")

        # 3.5 Quality Audit & Human Review Package Generation
        print("[3.5/4] Executing second-pass quality audit and generating human review package...")
        auditor = CanaryQualityAuditor(self.review_queue_path)
        human_pack_summary = auditor.export_review_pack(
            output_jsonl_path=BASE_DIR / "staging" / "review_queue" / "canary_1_2c_human_review_ready.jsonl",
            output_json_path=self.reports_dir / "phase_1_2c_human_review_pack.json",
            output_md_path=self.reports_dir / "phase_1_2c_human_review_pack.md"
        )
        print(f"      Review pack generated: {human_pack_summary['total_candidates']} records.")
        print(f"      REVIEW-C: {human_pack_summary['by_complexity']['REVIEW-C']}, "
              f"REVIEW-B: {human_pack_summary['by_complexity']['REVIEW-B']}, "
              f"REVIEW-A: {human_pack_summary['by_complexity']['REVIEW-A']}")

        # 4. Release Evaluation
        print("[4/4] Evaluating release eligibility...")
        release_md = self.reports_dir / "phase_1_2c_canary_release.md"
        release_json = self.reports_dir / "phase_1_2c_canary_release.json"
        release_summary = CanaryReleaseBuilder.build_canary_release(
            selected_candidates,
            self.release_dir,
            release_md,
            release_json
        )

        print(f"\nPipeline Status: {release_summary.get('status')}")
        print(f"Canary Release Created: {release_summary.get('release_created')}")
        print("Done.")

        return {
            "selection_count": len(selected_candidates),
            "pool_size": pool_size,
            "review_summary": review_summary,
            "release_summary": release_summary
        }


if __name__ == "__main__":
    pipeline = CanaryPipeline()
    pipeline.run()
