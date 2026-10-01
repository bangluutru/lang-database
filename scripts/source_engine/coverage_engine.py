"""
scripts/source_engine/coverage_engine.py
Domain Coverage Engine for Phase 1.2B.
Calculates domain and subdomain coverage matrices, tracks planning targets vs production,
computes coverage gaps, assesses source readiness, and exports machine/human-readable reports.
"""

from typing import List, Dict, Any, Tuple
from pathlib import Path
import json
import yaml
from datetime import datetime, timezone

from scripts.source_engine.models import CanaryCandidate, SourceReadiness

BASE_DIR = Path(__file__).resolve().parent.parent.parent


class CoverageEngine:
    def __init__(self, taxonomy_path: Path, registry_path: Path):
        with open(taxonomy_path, "r", encoding="utf-8") as f:
            self.taxonomy = yaml.safe_load(f)
        with open(registry_path, "r", encoding="utf-8") as f:
            self.registry = yaml.safe_load(f)

    def calculate_coverage(
        self,
        production_records: List[Dict[str, Any]],
        candidates_pool: List[CanaryCandidate],
        all_extracted_candidates: List[Any],
        dedup_stats: Dict[str, Any]
    ) -> Dict[str, Any]:
        # Count production by domain and subdomain
        prod_counts: Dict[str, Dict[str, int]] = {}
        for r in production_records:
            dom = r.get("domain", {}).get("primary", "business")
            sub = r.get("domain", {}).get("subdomain", "general")
            if dom not in prod_counts:
                prod_counts[dom] = {}
            prod_counts[dom][sub] = prod_counts[dom].get(sub, 0) + 1

        # Count candidates by domain and subdomain
        cand_counts: Dict[str, Dict[str, int]] = {}
        for c in candidates_pool:
            dom = c.domain
            sub = c.subdomain or "general"
            if dom not in cand_counts:
                cand_counts[dom] = {}
            cand_counts[dom][sub] = cand_counts[dom].get(sub, 0) + 1

        # Total extracted count per domain
        extracted_counts: Dict[str, int] = {}
        for ec in all_extracted_candidates:
            dom = getattr(ec, "primary_domain", "business")
            extracted_counts[dom] = extracted_counts.get(dom, 0) + 1

        # Build domain matrix
        domain_matrix = {}
        domains_spec = self.taxonomy.get("domains", {})

        for dom_key, dom_info in domains_spec.items():
            target_min, target_max = dom_info.get("target_planning_range", [500, 1000])
            authorities = dom_info.get("authority_primary", [])

            # Source readiness
            readiness = SourceReadiness.READY.value
            matched_sources = [s for s in self.registry.get("sources", []) if s.get("source_id") in authorities or dom_key in s.get("domains", [])]
            if not matched_sources:
                readiness = SourceReadiness.BLOCKED.value
            elif any(s.get("reuse_status") == "RED" for s in matched_sources):
                readiness = SourceReadiness.PARTIAL.value

            prod_total = sum(prod_counts.get(dom_key, {}).values())
            cand_total = sum(cand_counts.get(dom_key, {}).values())
            ext_total = extracted_counts.get(dom_key, 0)

            # Coverage gap assessment
            coverage_ratio = (prod_total + cand_total) / target_min if target_min > 0 else 1.0
            if coverage_ratio < 0.2:
                gap = "critical"
            elif coverage_ratio < 0.5:
                gap = "high"
            elif coverage_ratio < 0.8:
                gap = "medium"
            else:
                gap = "low"

            priority = "high" if gap in ("critical", "high") else ("medium" if gap == "medium" else "normal")

            subdomain_matrix = {}
            for sub_key, sub_info in dom_info.get("subdomains", {}).items():
                p_cnt = prod_counts.get(dom_key, {}).get(sub_key, 0)
                c_cnt = cand_counts.get(dom_key, {}).get(sub_key, 0)
                subdomain_matrix[sub_key] = {
                    "title": sub_info.get("title", sub_key),
                    "current_production": p_cnt,
                    "candidate_pool_count": c_cnt,
                    "total_available": p_cnt + c_cnt
                }

            domain_matrix[dom_key] = {
                "title": dom_info.get("title", dom_key),
                "authorities": authorities,
                "authority_classes": list({s.get("authority_class") for s in matched_sources if s.get("authority_class")}),
                "source_readiness": readiness,
                "target_planning_range": [target_min, target_max],
                "current_production": prod_total,
                "extracted_raw_candidates": ext_total,
                "potential_new_canonical": cand_total,
                "coverage_gap": gap,
                "priority": priority,
                "subdomains": subdomain_matrix
            }

        return {
            "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "phase": "1.2B",
            "production_total": len(production_records),
            "candidate_pool_total": len(candidates_pool),
            "extracted_raw_total": len(all_extracted_candidates),
            "dedup_statistics": dedup_stats,
            "domains": domain_matrix
        }

    def export_reports(self, coverage_data: Dict[str, Any], dedup_data: Dict[str, Any], output_dir: Path):
        output_dir.mkdir(parents=True, exist_ok=True)

        # 1. reports/professional_domain_coverage.json
        cov_json_path = output_dir / "professional_domain_coverage.json"
        with open(cov_json_path, "w", encoding="utf-8") as f:
            json.dump(coverage_data, f, indent=2, ensure_ascii=False)

        # 2. reports/professional_domain_coverage.md
        cov_md_path = output_dir / "professional_domain_coverage.md"
        with open(cov_md_path, "w", encoding="utf-8") as f:
            f.write(self._render_coverage_markdown(coverage_data))

        # 3. reports/phase_1_2b_source_coverage.json
        src_json_path = output_dir / "phase_1_2b_source_coverage.json"
        with open(src_json_path, "w", encoding="utf-8") as f:
            json.dump({
                "phase": "1.2B",
                "registered_sources_count": len(self.registry.get("sources", [])),
                "sources": self.registry.get("sources", []),
                "coverage_summary": coverage_data["domains"]
            }, f, indent=2, ensure_ascii=False)

        # 4. reports/phase_1_2b_source_coverage.md
        src_md_path = output_dir / "phase_1_2b_source_coverage.md"
        with open(src_md_path, "w", encoding="utf-8") as f:
            f.write(self._render_source_coverage_markdown(coverage_data))

        # 5. reports/phase_1_2b_dedup_report.json
        dedup_json_path = output_dir / "phase_1_2b_dedup_report.json"
        with open(dedup_json_path, "w", encoding="utf-8") as f:
            json.dump(dedup_data, f, indent=2, ensure_ascii=False)

        # 6. reports/phase_1_2b_dedup_report.md
        dedup_md_path = output_dir / "phase_1_2b_dedup_report.md"
        with open(dedup_md_path, "w", encoding="utf-8") as f:
            f.write(self._render_dedup_markdown(dedup_data))

        print(f"[+] Exported domain coverage & dedup reports to {output_dir.relative_to(BASE_DIR)}")

    def _render_coverage_markdown(self, data: Dict[str, Any]) -> str:
        md = [
            "# Professional Domain Coverage Matrix",
            "",
            f"**Generated:** {data['generated_at']}  ",
            f"**Phase:** 1.2B — Source & Coverage Engine  ",
            f"**Current Production Baseline:** {data['production_total']} verified records  ",
            f"**Candidate Pool Size:** {data['candidate_pool_total']} new canonical candidates  ",
            "",
            "## Domain Coverage Summary",
            "",
            "| Domain | Current Prod | New Candidates | Planning Target | Readiness | Coverage Gap | Priority |",
            "|---|:---:|:---:|:---:|:---:|:---:|:---:|",
        ]
        for d_key, d in data["domains"].items():
            t_min, t_max = d["target_planning_range"]
            md.append(
                f"| **{d['title']}** | {d['current_production']} | {d['potential_new_canonical']} | "
                f"{t_min}–{t_max} | `{d['source_readiness']}` | `{d['coverage_gap']}` | **{d['priority']}** |"
            )

        md.extend([
            "",
            "---",
            "",
            "## Subdomain Breakdown",
            ""
        ])

        for d_key, d in data["domains"].items():
            md.append(f"### {d['title']}")
            md.append(f"- **Authorities:** {', '.join(d['authorities'])}")
            md.append(f"- **Authority Classes:** {', '.join(d['authority_classes'])}")
            md.append("")
            md.append("| Subdomain | Production | Candidates | Total Available |")
            md.append("|---|:---:|:---:|:---:|")
            for sub_key, sub in d["subdomains"].items():
                md.append(f"| {sub['title']} (`{sub_key}`) | {sub['current_production']} | {sub['candidate_pool_count']} | {sub['total_available']} |")
            md.append("")

        return "\n".join(md)

    def _render_source_coverage_markdown(self, data: Dict[str, Any]) -> str:
        md = [
            "# Phase 1.2B — Authoritative Source Coverage Report",
            "",
            f"**Phase:** 1.2B  ",
            f"**Registered Sources:** {len(self.registry.get('sources', []))}  ",
            "",
            "## Registered Source Families",
            "",
            "| Source ID | Authority | Class | Version | Reuse Status | Status |",
            "|---|---|:---:|:---:|:---:|:---:|",
        ]
        for s in self.registry.get("sources", []):
            md.append(
                f"| `{s.get('source_id')}` | {s.get('authority')} | **{s.get('authority_class')}** | "
                f"{s.get('version')} | `{s.get('reuse_status')}` | `{s.get('status')}` |"
            )

        md.extend([
            "",
            "## Domain Source Readiness & Gaps",
            "",
            "| Domain | Readiness | Extracted Candidates | New Canonical | Gaps & Bottlenecks |",
            "|---|:---:|:---:|:---:|---|",
        ])

        for d_key, d in data["domains"].items():
            gaps = "None - Authoritative sources ready" if d["source_readiness"] == "READY" and d["coverage_gap"] == "low" else f"Planning gap: {d['coverage_gap']} (priority {d['priority']})"
            md.append(f"| **{d['title']}** | `{d['source_readiness']}` | {d['extracted_raw_candidates']} | {d['potential_new_canonical']} | {gaps} |")

        md.append("")
        return "\n".join(md)

    def _render_dedup_markdown(self, dedup_data: Dict[str, Any]) -> str:
        s = dedup_data.get("summary", {})
        md = [
            "# Phase 1.2B — Multi-Stage Deduplication & Sense Analysis Report",
            "",
            f"**Generated:** {dedup_data.get('generated_at')}  ",
            f"**Total Raw Candidates Processed:** {s.get('total_raw_candidates', 0)}  ",
            "",
            "## Deduplication Decision Breakdown",
            "",
            "| Decision | Count | Percentage | Description |",
            "|---|:---:|:---:|---|",
            f"| `NEW_CANONICAL` | **{s.get('new_canonical', 0)}** | {s.get('new_canonical_pct', 0.0):.1f}% | Genuinely new professional concept with verified provenance |",
            f"| `EXACT_DUPLICATE` | {s.get('exact_duplicate', 0)} | {s.get('exact_duplicate_pct', 0.0):.1f}% | Exact surface match against Golden Pilot v1.1 or existing pool (evidence merged) |",
            f"| `VARIANT_OF` | {s.get('variant_of', 0)} | {s.get('variant_of_pct', 0.0):.1f}% | Orthographic / notation variant of existing canonical term |",
            f"| `ABBREVIATION_OF` | {s.get('abbreviation_of', 0)} | {s.get('abbreviation_of_pct', 0.0):.1f}% | Known acronym / short form mapped to full canonical term |",
            f"| `POSSIBLE_DIFFERENT_SENSE` | {s.get('different_sense', 0)} | {s.get('different_sense_pct', 0.0):.1f}% | Polysemous term with distinct domain/semantic sense |",
            f"| `NEEDS_REVIEW` | {s.get('needs_review', 0)} | {s.get('needs_review_pct', 0.0):.1f}% | Ambiguous candidate flagged for manual human inspection |",
            "",
            "---",
            "",
            "## Representative Deduplication Examples",
            "",
            "### 1. Exact Duplicate (Multi-Source Evidence Preservation)",
        ]

        for ex in dedup_data.get("examples", {}).get("exact_duplicates", [])[:4]:
            md.append(f"- **{ex['surface']}** (`{ex['domain']}`) -> matches canonical ID `{ex['existing_canonical_id']}`. Preserved sources: {ex['sources']}")

        md.extend([
            "",
            "### 2. Orthographic / Notation Variant",
        ])
        for ex in dedup_data.get("examples", {}).get("variants", [])[:4]:
            md.append(f"- **{ex['surface']}** -> variant of canonical `{ex['target_term']}`")

        md.extend([
            "",
            "### 3. Abbreviation Mapping",
        ])
        for ex in dedup_data.get("examples", {}).get("abbreviations", [])[:4]:
            md.append(f"- **{ex['surface']}** -> abbreviation of `{ex['full_form']}`")

        md.extend([
            "",
            "### 4. Polysemous Different Sense Candidates",
        ])
        for ex in dedup_data.get("examples", {}).get("different_senses", [])[:4]:
            md.append(f"- **{ex['surface']}** (Domain: `{ex['domain']}`) vs existing `{ex['existing_canonical_id']}`. Sense: {ex['context']}")

        md.append("")
        return "\n".join(md)
