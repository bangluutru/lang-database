"""
scripts/canary/gloss_integrity_auditor.py
Global Gloss Integrity Audit Engine for Phase 1.2C.

Audits candidate meaning glosses for:
1. Unmatched parentheses: '(' vs ')'
2. Unmatched square brackets: '[' vs ']'
3. Unmatched quotation marks: '"'
4. Obvious truncation / trailing incomplete punctuation (e.g. trailing comma, semicolon, open paren)
5. Generic category placeholders (e.g. 'Tax Filing', 'Financial Accounting', matching domain/subdomain)
6. Empty or whitespace-only glosses
7. Duplicated fragments (e.g. repeated adjacent words)

Generates:
- reports/phase_1_2c_gloss_integrity_audit.json
- reports/phase_1_2c_gloss_integrity_audit.md
"""

from typing import List, Dict, Any, Optional
from pathlib import Path
import sys
import json
import re
from datetime import datetime, timezone

BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))


class GlossIntegrityAuditor:
    def __init__(self, queue_path: Path):
        self.queue_path = queue_path

    @staticmethod
    def audit_single_gloss(
        surface: str,
        gloss: str,
        domain: str = "",
        subdomain: str = ""
    ) -> List[Dict[str, str]]:
        """Audits a single gloss string and returns a list of detected issue dicts."""
        issues = []
        clean_gloss = gloss.strip() if gloss else ""

        # 1. Empty gloss
        if not clean_gloss:
            issues.append({
                "code": "EMPTY_GLOSS",
                "message": "Meaning gloss is empty or whitespace-only."
            })
            return issues

        # 2. Unmatched parentheses
        l_paren = clean_gloss.count("(")
        r_paren = clean_gloss.count(")")
        if l_paren != r_paren:
            issues.append({
                "code": "UNMATCHED_PARENTHESES",
                "message": f"Unmatched parentheses: found {l_paren} '(' and {r_paren} ')'."
            })

        # 3. Unmatched square brackets
        l_sq = clean_gloss.count("[")
        r_sq = clean_gloss.count("]")
        if l_sq != r_sq:
            issues.append({
                "code": "UNMATCHED_BRACKETS",
                "message": f"Unmatched brackets: found {l_sq} '[' and {r_sq} ']'."
            })

        # 4. Unmatched double quotes
        d_quotes = clean_gloss.count('"')
        if d_quotes % 2 != 0:
            issues.append({
                "code": "UNMATCHED_QUOTES",
                "message": f"Unmatched double quotation marks: found {d_quotes} '\"'."
            })

        # 5. Trailing incomplete punctuation
        if re.search(r"[,;:\-\(]$", clean_gloss):
            issues.append({
                "code": "TRAILING_INCOMPLETE_PUNCTUATION",
                "message": f"Gloss ends with trailing incomplete punctuation '{clean_gloss[-1]}'."
            })

        # 6. Generic category placeholders
        norm_gloss = clean_gloss.lower()
        if domain and norm_gloss == domain.lower():
            issues.append({
                "code": "GENERIC_CATEGORY_PLACEHOLDER",
                "message": f"Gloss is identical to domain name '{domain}'."
            })
        elif subdomain and norm_gloss == subdomain.replace("_", " ").lower():
            issues.append({
                "code": "GENERIC_CATEGORY_PLACEHOLDER",
                "message": f"Gloss is identical to subdomain name '{subdomain}'."
            })
        elif norm_gloss in ("tax filing", "financial accounting", "general business"):
            issues.append({
                "code": "GENERIC_CATEGORY_PLACEHOLDER",
                "message": f"Gloss is a generic category placeholder '{clean_gloss}'."
            })

        # 7. Duplicated fragments (repeated adjacent words)
        words = re.findall(r"\b[A-Za-z]+\b", clean_gloss)
        if len(words) >= 4:
            for idx in range(len(words) - 1):
                if words[idx].lower() == words[idx + 1].lower() and words[idx].lower() not in ("that", "had"):
                    issues.append({
                        "code": "DUPLICATED_FRAGMENT",
                        "message": f"Duplicated adjacent word fragment '{words[idx]} {words[idx+1]}'."
                    })

        return issues

    def run_audit(
        self,
        json_report_path: Optional[Path] = None,
        md_report_path: Optional[Path] = None
    ) -> Dict[str, Any]:
        """Runs integrity audit across all records in queue and exports reports."""
        with open(self.queue_path, "r", encoding="utf-8") as f:
            records = [json.loads(line) for line in f if line.strip()]

        total_audited = len(records)
        flagged_records = []
        issue_type_counts: Dict[str, int] = {}

        for rec in records:
            cid = rec["candidate_id"]
            surf = rec["surface"]
            gloss = rec["meaning_gloss"]
            dom = rec.get("domain", "")
            subdom = rec.get("subdomain", "")

            issues = self.audit_single_gloss(surf, gloss, dom, subdom)
            if issues:
                for iss in issues:
                    c = iss["code"]
                    issue_type_counts[c] = issue_type_counts.get(c, 0) + 1

                flagged_records.append({
                    "candidate_id": cid,
                    "surface": surf,
                    "domain": dom,
                    "subdomain": subdom,
                    "original_gloss": gloss,
                    "issues": issues,
                    "suggested_gloss": rec.get("suggested_gloss")
                })

        audit_result = {
            "audited_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "total_records_audited": total_audited,
            "flagged_count": len(flagged_records),
            "clean_count": total_audited - len(flagged_records),
            "status": "ISSUES_FOUND" if flagged_records else "PASS",
            "issue_type_counts": issue_type_counts,
            "flagged_records": flagged_records
        }

        if json_report_path:
            json_report_path.parent.mkdir(parents=True, exist_ok=True)
            with open(json_report_path, "w", encoding="utf-8") as f:
                json.dump(audit_result, f, indent=2, ensure_ascii=False)

        if md_report_path:
            md_report_path.parent.mkdir(parents=True, exist_ok=True)
            self._write_markdown_report(md_report_path, audit_result)

        return audit_result

    def _write_markdown_report(self, md_path: Path, result: Dict[str, Any]):
        lines = [
            "# Phase 1.2C — Global Gloss Integrity Audit Report",
            "",
            f"**Audit Timestamp:** `{result['audited_at']}`  ",
            f"**Total Candidates Audited:** `{result['total_records_audited']}`  ",
            f"**Flagged Records:** `{result['flagged_count']}`  ",
            f"**Clean Records:** `{result['clean_count']}`  ",
            f"**Audit Status:** **`{result['status']}`**  ",
            "",
            "## Issue Type Breakdown",
            "",
            "| Issue Code | Description | Count |",
            "|---|---|:---:|",
            "| `UNMATCHED_PARENTHESES` | Missing closing or opening parenthesis `)` / `(` | " + str(result["issue_type_counts"].get("UNMATCHED_PARENTHESES", 0)) + " |",
            "| `UNMATCHED_BRACKETS` | Missing closing or opening square bracket `]` / `[` | " + str(result["issue_type_counts"].get("UNMATCHED_BRACKETS", 0)) + " |",
            "| `UNMATCHED_QUOTES` | Unpaired quotation marks | " + str(result["issue_type_counts"].get("UNMATCHED_QUOTES", 0)) + " |",
            "| `TRAILING_INCOMPLETE_PUNCTUATION` | Trailing incomplete punctuation (comma, semicolon, hyphen) | " + str(result["issue_type_counts"].get("TRAILING_INCOMPLETE_PUNCTUATION", 0)) + " |",
            "| `GENERIC_CATEGORY_PLACEHOLDER` | Category name placeholder used instead of semantic gloss | " + str(result["issue_type_counts"].get("GENERIC_CATEGORY_PLACEHOLDER", 0)) + " |",
            "| `EMPTY_GLOSS` | Empty or whitespace-only gloss | " + str(result["issue_type_counts"].get("EMPTY_GLOSS", 0)) + " |",
            "| `DUPLICATED_FRAGMENT` | Redundant adjacent duplicate words | " + str(result["issue_type_counts"].get("DUPLICATED_FRAGMENT", 0)) + " |",
            "",
            "## Flagged Candidate Details",
            "",
            "| Candidate ID | Surface | Domain | Current Gloss | Issues | Action / Proposed Resolution |",
            "|---|---|---|---|---|---|",
        ]

        for item in result["flagged_records"]:
            cid = item["candidate_id"]
            surf = item["surface"]
            dom = item["domain"]
            gloss = item["original_gloss"]
            iss_text = "<br>".join([f"• `{i['code']}`: {i['message']}" for i in item["issues"]])
            sugg = item.get("suggested_gloss") or "Requires human revision"
            lines.append(f"| `{cid}` | **{surf}** | `{dom}` | `{gloss}` | {iss_text} | `{sugg}` |")

        lines.append("")
        with open(md_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))


if __name__ == "__main__":
    queue_file = BASE_DIR / "staging" / "review_queue" / "canary_1_2c_human_review_ready.jsonl"
    json_out = BASE_DIR / "reports" / "phase_1_2c_gloss_integrity_audit.json"
    md_out = BASE_DIR / "reports" / "phase_1_2c_gloss_integrity_audit.md"
    auditor = GlossIntegrityAuditor(queue_file)
    res = auditor.run_audit(json_out, md_out)
    print(f"Gloss audit completed. Total audited: {res['total_records_audited']}, Flagged: {res['flagged_count']}, Status: {res['status']}")
