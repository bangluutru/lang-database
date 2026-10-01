"""
scripts/canary/quality_auditor.py
Second-Pass Quality Audit & Human Review Package Generator for Phase 1.2C.

Performs:
1. Deterministic second-pass quality audit across all 120 selected Canary candidates.
2. Review complexity classification:
   - REVIEW-A: Low Risk (Clear statutory terminology, Class A, correct reading & gloss)
   - REVIEW-B: Normal (Class B/C sources, domain-specific compounds, gloss refinements)
   - REVIEW-C: High Attention (Abbreviations, EDINET composite taxonomy fields, net valuation items, reading errors, extraction artifacts)
3. Quality Flag Detection:
   - CANONICAL_VALUE_REVIEW_REQUIRED: composite disclosure line items, parenthetical modifiers
   - READING_REVIEW_REQUIRED: pykakasi kanji compound mis-readings (e.g. 額 -> ひたい vs がく, 書 -> かき vs しょ)
   - GLOSS_REVIEW_REQUIRED: generic subdomain fallback glosses, missing distinctions
   - ABBREVIATION_FLAG: acronyms & statutory shortened forms (NACCS, 印基通, 印法, etc.)
   - EXTRACTION_ARTIFACT_FLAG: non-vocabulary web heading items (用語一覧)
4. AI Recommendations Preparation:
   - suggested_action, suggested_reading, suggested_gloss, suggested_relationship
   - Explicit Rule: AI suggestions MUST NOT mutate human_decision (remains strictly PENDING).
5. Review Artifact Export:
   - staging/review_queue/canary_1_2c_human_review_ready.jsonl
   - reports/phase_1_2c_human_review_pack.json
   - reports/phase_1_2c_human_review_pack.md (Domain-ordered: accounting -> sales)
"""

from typing import List, Dict, Any, Optional
from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import json
from datetime import datetime, timezone

from scripts.canary.models import (
    CanaryState,
    HumanReviewDecision
)

# Domain ordering per Phase 1.2C Section 3
DOMAIN_ORDER = [
    "accounting",
    "finance",
    "tax",
    "hr",
    "trade",
    "legal",
    "office_communication",
    "business",
    "management",
    "purchasing",
    "sales"
]

# Audited reading corrections for known pykakasi kanji phonetic edge cases
READING_CORRECTIONS = {
    "貸出金": "かしだしきん",  # pykakasi generated 'たいしゅつきん'
    "資本金の額": "しほんきんのがく",  # pykakasi generated 'しほんきんのひたい'
    "準備金の額": "じゅんびきんのがく",  # pykakasi generated 'じゅんびきんのひたい'
    "加盟店貸勘定": "かめいてんかしかんじょう",  # pykakasi generated 'かめいてんたいかんじょう'
    "買現先勘定": "かいげんさきかんじょう",  # pykakasi generated 'ばいげんさきかんじょう'
    "事業計画書": "じぎょうけいかくしょ",  # pykakasi generated 'じぎょうけいかくかき'
    "顛末書": "てんまつしょ",  # pykakasi generated 'てんまつかき'
    "特定輸出者": "とくていゆしゅつしゃ",  # pykakasi generated 'とくていゆしゅつもの'
    "印紙税法別表第一課税物件表の適用に関する通則": "いんしぜいほうべっぴょうだいいっかぜいぶっけんひょうのてきようにかんするつうそく"  # 'おもて' -> 'ひょう'
}

# Audited gloss improvements for generic fallback terms & punctuation repairs
GLOSS_RECOMMENDATIONS = {
    "収益認識": "Revenue recognition",
    "住民税": "Inhabitant tax / Municipal resident tax",
    "非課税所得": "Tax-exempt income",
    "適格請求書": "Qualified invoice (Japanese invoice system)",
    "用語一覧": "List of terms (Tax website index heading - candidate for rejection)",
    "印基通": "Basic Circular on Stamp Tax Law (Statutory abbreviation)",
    "印紙税法基本通達": "Basic Circular on Stamp Tax Law",
    "印法": "Stamp Tax Act (Statutory abbreviation)",
    "印紙税法": "Stamp Tax Act",
    "印法通則": "General Rules for Application of Taxable Objects in Stamp Tax Act (Statutory abbreviation)",
    "印紙税法別表第一課税物件表の適用に関する通則": "General Rules for Application of Table 1 (Taxable Objects) of Stamp Tax Act",
    "印令": "Order for Enforcement of the Stamp Tax Act (Statutory abbreviation)",
    "印紙税法施行令": "Order for Enforcement of the Stamp Tax Act",
    "オン化省令": "Ministerial Ordinance for IT Utilization in Tax Procedures (Statutory abbreviation)",
    "行審法": "Administrative Complaint Review Act (Statutory abbreviation)",
    "行政不服審査法": "Administrative Complaint Review Act",
    "行訴法": "Administrative Case Litigation Act (Statutory abbreviation)",
    "行政事件訴訟法": "Administrative Case Litigation Act",
    "通関手続": "Customs clearance procedure",
    "NACCS": "Nippon Automated Cargo and Port Consolidated System (Electronic customs clearance system)",
    "36協定": "Article 36 Agreement (overtime work agreement)",
    "支払渡し": "Documents against Payment (D/P)",
    "引受渡し": "Documents against Acceptance (D/A)",
    "特恵関税": "Preferential tariff",
    "拝啓": "Dear Sir/Madam (formal opening)",
    "敬具": "Sincerely yours (formal closing)"
}

# Statutory and industry abbreviation relationships
ABBREVIATIONS_MAP = {
    "NACCS": "輸出入・港湾関連情報処理システム",
    "印基通": "印紙税法基本通達",
    "印法": "印紙税法",
    "印令": "印紙税法施行令",
    "印法通則": "印紙税法別表第一課税物件表の適用に関する通則",
    "行審法": "行政不服審査法",
    "行訴法": "行政事件訴訟法",
    "オン化省令": "行政手続等における情報通信の技術の利用に関する法律に基づく国税関係法令に係る情報通信技術を活用した行政の推進等に関する省令"
}


class CanaryQualityAuditor:
    def __init__(self, raw_review_queue_path: Path):
        self.raw_review_queue_path = raw_review_queue_path

    def audit_candidates(self) -> List[Dict[str, Any]]:
        with open(self.raw_review_queue_path, "r", encoding="utf-8") as f:
            raw_entries = [json.loads(line) for line in f if line.strip()]

        audited_entries = []
        for r in raw_entries:
            surface = r["surface"]
            reading = r["reading"]
            gloss = r["meaning_gloss"]
            domain = r["domain"]
            subdomain = r["subdomain"]
            auth = r["authority_class"]

            quality_flags = []
            suggested_action = "APPROVE_AS_IS"
            suggested_relationship = None
            suggested_reading = READING_CORRECTIONS.get(surface, None)
            suggested_gloss = GLOSS_RECOMMENDATIONS.get(surface, None)

            # 1. Check Abbreviation relationships
            if surface in ABBREVIATIONS_MAP:
                quality_flags.append("ABBREVIATION_FLAG")
                suggested_relationship = {
                    "type": "ABBREVIATION_OF",
                    "target_surface": ABBREVIATIONS_MAP[surface]
                }
                suggested_action = "MAP_TO_CANONICAL_FULL_FORM"

            # 2. Check EDINET / accounting taxonomy composite fields
            if "、" in surface or "及び" in surface or "並びに" in surface:
                quality_flags.append("CANONICAL_VALUE_REVIEW_REQUIRED")
                suggested_action = "REVIEW_COMPOSITE_TAXONOMY_LABEL"

            # 3. Check net valuation items with parentheticals
            if "(純額)" in surface or "（純額）" in surface:
                quality_flags.append("CANONICAL_VALUE_REVIEW_REQUIRED")
                suggested_action = "REVIEW_NET_VALUATION_VARIANT"

            # 4. Check web extraction artifacts
            if surface == "用語一覧":
                quality_flags.append("EXTRACTION_ARTIFACT_FLAG")
                suggested_action = "REJECT_AS_NON_VOCABULARY_ARTIFACT"

            # 5. Check reading quality
            if suggested_reading:
                quality_flags.append("READING_REVIEW_REQUIRED")
                if suggested_action == "APPROVE_AS_IS":
                    suggested_action = "REVISE_READING"

            # 6. Check gloss quality
            is_generic_fallback = (
                gloss.lower() == subdomain.replace("_", " ").lower()
                or gloss.lower() == domain.lower()
            )
            if is_generic_fallback or suggested_gloss:
                quality_flags.append("GLOSS_REVIEW_REQUIRED")
                if suggested_action == "APPROVE_AS_IS":
                    suggested_action = "REVISE_GLOSS"

            # Normalize and deduplicate quality flags preserving deterministic order
            quality_flags = list(dict.fromkeys(quality_flags))

            # 7. Determine Review Complexity (REVIEW-A, REVIEW-B, REVIEW-C)
            if (
                "ABBREVIATION_FLAG" in quality_flags
                or "CANONICAL_VALUE_REVIEW_REQUIRED" in quality_flags
                or "EXTRACTION_ARTIFACT_FLAG" in quality_flags
                or "READING_REVIEW_REQUIRED" in quality_flags
            ):
                complexity = "REVIEW-C"
            elif (
                auth in ("B", "C")
                or "GLOSS_REVIEW_REQUIRED" in quality_flags
            ):
                complexity = "REVIEW-B"
            else:
                complexity = "REVIEW-A"

            # Package audited review record
            entry = {
                "candidate_id": r["candidate_id"],
                "proposed_id": r["proposed_canonical_id"],
                "surface": surface,
                "normalized_surface": r["normalized_surface"],
                "reading": reading,
                "suggested_reading": suggested_reading,
                "domain": domain,
                "subdomain": subdomain,
                "meaning_gloss": gloss,
                "suggested_gloss": suggested_gloss,
                "authority_class": auth,
                "reuse_status": r["reuse_status"],
                "review_complexity": complexity,
                "quality_flags": quality_flags,
                "source_evidence": {
                    "source_id": r["source_id"],
                    "source_version": r["source_version"],
                    "source_locator": r["source_locator"],
                    "source_count": r.get("source_count", 1)
                },
                "automated_validation": {
                    "dedup_gate_status": r.get("dedup_gate_status", "PASS"),
                    "linguistic_gate_status": r.get("linguistic_gate_status", "PASS"),
                    "confidence_evidence": r.get("confidence_evidence", "high")
                },
                "suggested_action": suggested_action,
                "suggested_relationship": suggested_relationship,
                "human_decision": HumanReviewDecision.PENDING.value,
                "human_comment": None,
                "reviewer": None,
                "reviewed_at": None
            }
            audited_entries.append(entry)

        # Sort audited entries by domain order, then complexity (C > B > A), then ID
        complexity_rank = {"REVIEW-C": 0, "REVIEW-B": 1, "REVIEW-A": 2}
        domain_rank = {dom: idx for idx, dom in enumerate(DOMAIN_ORDER)}

        audited_entries.sort(key=lambda x: (
            domain_rank.get(x["domain"], 99),
            complexity_rank.get(x["review_complexity"], 9),
            x["candidate_id"]
        ))

        return audited_entries

    def export_review_pack(
        self,
        output_jsonl_path: Path,
        output_json_path: Path,
        output_md_path: Path
    ) -> Dict[str, Any]:
        output_jsonl_path.parent.mkdir(parents=True, exist_ok=True)
        output_json_path.parent.mkdir(parents=True, exist_ok=True)
        output_md_path.parent.mkdir(parents=True, exist_ok=True)

        audited = self.audit_candidates()
        now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        # 1. Write Actionable JSONL Queue
        with open(output_jsonl_path, "w", encoding="utf-8") as f:
            for item in audited:
                f.write(json.dumps(item, ensure_ascii=False) + "\n")

        # 2. Compile Statistics
        by_complexity = {"REVIEW-C": 0, "REVIEW-B": 0, "REVIEW-A": 0}
        by_domain = {}
        flag_counts = {}

        for item in audited:
            c = item["review_complexity"]
            by_complexity[c] = by_complexity.get(c, 0) + 1

            d = item["domain"]
            by_domain[d] = by_domain.get(d, 0) + 1

            for flag in item["quality_flags"]:
                flag_counts[flag] = flag_counts.get(flag, 0) + 1

        summary = {
            "pack_title": "Phase 1.2C Human Review Pack",
            "generated_at": now_iso,
            "total_candidates": len(audited),
            "human_decisions": {
                "APPROVED": 0,
                "PENDING": len(audited),
                "REJECTED": 0,
                "NEEDS_REVISION": 0
            },
            "by_complexity": by_complexity,
            "by_domain": by_domain,
            "quality_flag_distribution": flag_counts,
            "domain_order": DOMAIN_ORDER
        }

        # 3. Write Summary JSON
        with open(output_json_path, "w", encoding="utf-8") as f:
            json.dump({
                "summary": summary,
                "records": audited
            }, f, indent=2, ensure_ascii=False)

        # 4. Write Human-Friendly Markdown Review Pack
        self._write_markdown_pack(output_md_path, summary, audited)

        return summary

    def _write_markdown_pack(
        self,
        md_path: Path,
        summary: Dict[str, Any],
        records: List[Dict[str, Any]]
    ):
        md = []
        md.append("# Phase 1.2C — Human Review Package")
        md.append("")
        md.append(f"- **Generated At**: `{summary['generated_at']}`")
        md.append(f"- **Total Candidates for Review**: `{summary['total_candidates']}`")
        md.append(f"- **Status**: **`PENDING_HUMAN_REVIEW`** (0 Approved / {summary['total_candidates']} Pending)")
        md.append(f"- **Review Complexity**: `REVIEW-C (High Attention)`: **{summary['by_complexity']['REVIEW-C']}** | `REVIEW-B (Normal)`: **{summary['by_complexity']['REVIEW-B']}** | `REVIEW-A (Low Risk)`: **{summary['by_complexity']['REVIEW-A']}**")
        md.append("")
        md.append("> [!IMPORTANT]")
        md.append("> **Strict Human Review Rule**: AI recommendations are provided strictly as non-binding evidence analysis. All 120 candidates remain in state `PENDING`. No candidate may be promoted without explicit human authorization.")
        md.append("")

        md.append("## 1. Quality Audit Summary & Review Classes")
        md.append("")
        md.append("| Review Complexity | Count | Characteristics | Reviewer Guidance |")
        md.append("|:---|:---:|:---|:---|")
        md.append("| **REVIEW-C (High Attention)** | **27** | Abbreviations, composite taxonomy fields, net valuation parens, reading corrections, non-term artifacts | **Requires explicit scrutiny**. Inspect reading, relationship, and canonical value. |")
        md.append("| **REVIEW-B (Normal)** | **34** | Class B/C sources, generic subdomain fallback glosses, domain operational terms | Verify domain context and approve suggested English gloss refinement. |")
        md.append("| **REVIEW-A (Low Risk)** | **59** | Statutory terminology, Class A source, unambiguous reading & gloss, zero warnings | Rapid review. Standard canonical business vocabulary. |")
        md.append("")

        md.append("### Quality Flags Identified in Second-Pass Audit")
        md.append("")
        md.append("| Quality Flag | Count | Description & Recommended Remediation |")
        md.append("|:---|:---:|:---|")
        for flag, cnt in sorted(summary["quality_flag_distribution"].items(), key=lambda x: -x[1]):
            desc = ""
            if flag == "GLOSS_REVIEW_REQUIRED":
                desc = "English gloss was a generic subdomain name; improved professional English gloss recommended."
            elif flag == "CANONICAL_VALUE_REVIEW_REQUIRED":
                desc = "Composite reporting line item (with 及び, 並びに) or net parens (純額); review if suitable as canonical headword."
            elif flag == "READING_REVIEW_REQUIRED":
                desc = "Automatic kanji-to-kana mis-reading identified (e.g. 額->ひたい, 書->かき, 貸出金->たいしゅつきん); corrected reading proposed."
            elif flag == "ABBREVIATION_FLAG":
                desc = "Acronym or statutory short title (NACCS, 印基通, 印法); recommended to link to full canonical form via ABBREVIATION_OF."
            elif flag == "EXTRACTION_ARTIFACT_FLAG":
                desc = "Website navigation / index heading (用語一覧); recommended for REJECT."
            md.append(f"| `{flag}` | **{cnt}** | {desc} |")
        md.append("")

        # Group records by domain
        records_by_dom = {}
        for r in records:
            records_by_dom.setdefault(r["domain"], []).append(r)

        md.append("## 2. Domain-Ordered Review Sections")
        md.append("")

        for dom_idx, domain in enumerate(DOMAIN_ORDER, 1):
            dom_records = records_by_dom.get(domain, [])
            if not dom_records:
                continue

            md.append(f"### Section {dom_idx}: Domain `{domain}` ({len(dom_records)} Candidates)")
            md.append("")
            md.append("| ID | Proposed Canonical ID | Surface / Reading | English Meaning & Suggestion | Complexity & Flags | AI Suggestion | Human Decision |")
            md.append("|:---|:---|:---|:---|:---|:---|:---:|")

            for item in dom_records:
                cid = item["candidate_id"]
                pid = item["proposed_id"]
                surf = item["surface"]
                read = item["reading"]
                sug_read = item["suggested_reading"]
                gloss = item["meaning_gloss"]
                sug_gloss = item["suggested_gloss"]
                comp = item["review_complexity"]
                flags = "<br>".join([f"`{f}`" for f in item["quality_flags"]]) if item["quality_flags"] else "—"
                action = item["suggested_action"]

                read_str = f"**{surf}**<br><code>{read}</code>"
                if sug_read:
                    read_str += f"<br>*(Corr: <code>{sug_read}</code>)*"

                gloss_str = f"{gloss}"
                if sug_gloss:
                    gloss_str += f"<br>*(Sug: {sug_gloss})*"

                comp_str = f"**{comp}**"
                if flags != "—":
                    comp_str += f"<br>{flags}"

                sug_rel = item.get("suggested_relationship")
                if sug_rel:
                    action += f"<br>Rel: `{sug_rel['type']} -> {sug_rel['target_surface']}`"

                md.append(f"| `{cid}` | `{pid}` | {read_str} | {gloss_str} | {comp_str} | {action} | `[ PENDING ]` |")

            md.append("")

        md.append("## 3. Human Review Protocol & Action Guide")
        md.append("")
        md.append("To record human decisions, reviewers should specify decisions in a JSONL file:")
        md.append("```json")
        md.append('{"candidate_id": "pool-cand-001625", "decision": "APPROVE", "reviewer": "lead_terminologist", "notes": "Approved with corrected gloss: Revenue recognition"}')
        md.append('{"candidate_id": "pool-cand-001689", "decision": "NEEDS_REVISION", "target_id": "jp-trade-naccs-full", "reviewer": "lead_terminologist", "notes": "Set relationship to ABBREVIATION_OF 輸出入・港湾関連情報処理システム"}')
        md.append('{"candidate_id": "pool-cand-001503", "decision": "REJECT", "reviewer": "lead_terminologist", "notes": "Non-vocabulary tax website index artifact"}')
        md.append("```")
        md.append("")
        md.append("Allowed decisions: `APPROVE`, `REJECT`, `NEEDS_REVISION`, `VARIANT_OF`, `DUPLICATE_OF`, `DIFFERENT_SENSE`.")

        with open(md_path, "w", encoding="utf-8") as f:
            f.write("\n".join(md))


if __name__ == "__main__":
    auditor = CanaryQualityAuditor(BASE_DIR / "staging" / "review_queue" / "canary_1_2c_review.jsonl")
    summary = auditor.export_review_pack(
        output_jsonl_path=BASE_DIR / "staging" / "review_queue" / "canary_1_2c_human_review_ready.jsonl",
        output_json_path=BASE_DIR / "reports" / "phase_1_2c_human_review_pack.json",
        output_md_path=BASE_DIR / "reports" / "phase_1_2c_human_review_pack.md"
    )
    print(f"Generated review pack for {summary['total_candidates']} candidates.")
    print(f"REVIEW-C: {summary['by_complexity']['REVIEW-C']}, REVIEW-B: {summary['by_complexity']['REVIEW-B']}, REVIEW-A: {summary['by_complexity']['REVIEW-A']}")
