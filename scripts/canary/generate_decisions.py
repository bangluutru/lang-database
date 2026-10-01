"""
scripts/canary/generate_decisions.py
Generates the authoritative human review decisions for Phase 1.2C.

Converts authorized human-review results into an immutable, auditable decision artifact:
staging/review_decisions/canary_1_2c_authorized_decisions.jsonl
"""

from typing import List, Dict, Any
from pathlib import Path
import sys
import json
import hashlib

BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

SOURCE_COMMIT = "b545ccf921e6f41a9ae47cbe58b416add04086c5"
REVIEWER = "authorized-human-review"
REVIEW_METHOD = "LLM-assisted human-authorized review"
REVIEW_AUTHORITY = "repository-owner-approved"
REVIEWED_AT = "2026-10-01T07:30:00Z"

# 1. Authoritative Reading Corrections (Section 5)
READING_CORRECTIONS = {
    "加盟店貸勘定": "かめいてんかしかんじょう",
    "買現先勘定": "かいげんさきかんじょう",
    "貸出金": "かしだしきん",
    "特定輸出者": "とくていゆしゅつしゃ",
    "資本金の額": "しほんきんのがく",
    "準備金の額": "じゅんびきんのがく",
    "顛末書": "てんまつしょ",
    "事業計画書": "じぎょうけいかくしょ",
    "印紙税法別表第一課税物件表の適用に関する通則": "いんしぜいほうべっぴょうだいいっかぜいぶっけんひょうのてきようにかんするつうそく",
}

# 2. Authoritative Gloss Corrections (Section 6 & 12)
GLOSS_CORRECTIONS = {
    "収益認識": "Revenue recognition",
    "住民税": "Inhabitant tax / Municipal resident tax",
    "非課税所得": "Tax-exempt income",
    "適格請求書": "Qualified invoice (Japanese invoice system)",
    "印紙税法基本通達": "Basic Circular on Stamp Tax Law",
    "印紙税法": "Stamp Tax Act",
    "印紙税法施行令": "Order for Enforcement of the Stamp Tax Act",
    "行政不服審査法": "Administrative Complaint Review Act",
    "行政事件訴訟法": "Administrative Case Litigation Act",
    "通関手続": "Customs clearance procedure",
    "36協定": "Article 36 Agreement (overtime work agreement)",
    "支払渡し": "Documents against Payment (D/P)",
    "引受渡し": "Documents against Acceptance (D/A)",
    "特恵関税": "Preferential tariff",
    "拝啓": "Dear Sir/Madam (formal opening)",
    "敬具": "Sincerely yours (formal closing)",
    "印紙税法別表第一課税物件表の適用に関する通則": "General Rules for Application of Table 1 (Taxable Objects) of Stamp Tax Act",
}

# 3. Abbreviation Decisions (Section 7)
ABBREVIATIONS = {
    "NACCS": {
        "target": "輸出入・港湾関連情報処理システム",
        "reason": "STATUTORY_OR_INDUSTRY_ABBREVIATION",
        "gloss": "Nippon Automated Cargo and Port Consolidated System (Electronic customs clearance system)"
    },
    "印基通": {
        "target": "印紙税法基本通達",
        "reason": "STATUTORY_ABBREVIATION",
        "gloss": "Basic Circular on Stamp Tax Law (Statutory abbreviation)"
    },
    "印法": {
        "target": "印紙税法",
        "reason": "STATUTORY_ABBREVIATION",
        "gloss": "Stamp Tax Act (Statutory abbreviation)"
    },
    "印法通則": {
        "target": "印紙税法別表第一課税物件表の適用に関する通則",
        "reason": "STATUTORY_ABBREVIATION",
        "gloss": "General Rules for Application of Taxable Objects in Stamp Tax Act (Statutory abbreviation)"
    },
    "印令": {
        "target": "印紙税法施行令",
        "reason": "STATUTORY_ABBREVIATION",
        "gloss": "Order for Enforcement of the Stamp Tax Act (Statutory abbreviation)"
    },
    "オン化省令": {
        "target": "行政手続等における情報通信の技術の利用に関する法律に基づく国税関係法令に係る情報通信技術を活用した行政の推進等に関する省令",
        "reason": "STATUTORY_ABBREVIATION",
        "gloss": "Ministerial Ordinance for IT Utilization in Tax Procedures (Statutory abbreviation)"
    },
    "行審法": {
        "target": "行政不服審査法",
        "reason": "STATUTORY_ABBREVIATION",
        "gloss": "Administrative Complaint Review Act (Statutory abbreviation)"
    },
    "行訴法": {
        "target": "行政事件訴訟法",
        "reason": "STATUTORY_ABBREVIATION",
        "gloss": "Administrative Case Litigation Act (Statutory abbreviation)"
    }
}

# 4. Authoritative Rejections (Section 9 & 10)
REJECTIONS = {
    "用語一覧": "NON_VOCABULARY_EXTRACTION_ARTIFACT",
    "受取手形、売掛金及び契約資産": "COMPOSITE_REPORTING_TAXONOMY_LABEL",
    "受取手形及び売掛金": "COMPOSITE_REPORTING_TAXONOMY_LABEL",
    "受取手形及び売掛金(純額)": "COMPOSITE_REPORTING_TAXONOMY_LABEL",
    "売掛金及び契約資産": "COMPOSITE_REPORTING_TAXONOMY_LABEL",
    "売掛金及び契約資産(純額)": "COMPOSITE_REPORTING_TAXONOMY_LABEL",
    "受取手形(純額)": "COMPOSITE_REPORTING_TAXONOMY_LABEL",
    "売掛金(純額)": "COMPOSITE_REPORTING_TAXONOMY_LABEL",
    "契約資産(純額)": "COMPOSITE_REPORTING_TAXONOMY_LABEL",
    "コールローン及び買入手形": "COMPOSITE_REPORTING_TAXONOMY_LABEL",
}


def build_authorized_decisions(queue_path: Path, output_path: Path) -> List[Dict[str, Any]]:
    with open(queue_path, "r", encoding="utf-8") as f:
        queue_records = [json.loads(line) for line in f if line.strip()]

    decisions = []
    counts = {
        "APPROVE": 0,
        "APPROVE_WITH_REVISION": 0,
        "ABBREVIATION_OF": 0,
        "REJECT": 0
    }

    for rec in queue_records:
        cid = rec["candidate_id"]
        surf = rec["surface"]
        orig_reading = rec["reading"]
        orig_gloss = rec["meaning_gloss"]

        if surf in REJECTIONS:
            reason = REJECTIONS[surf]
            dec_type = "REJECT"
            app_reading = orig_reading
            app_gloss = orig_gloss
            rel_type = None
            rel_target = None
            counts["REJECT"] += 1
        elif surf in ABBREVIATIONS:
            info = ABBREVIATIONS[surf]
            dec_type = "ABBREVIATION_OF"
            reason = info["reason"]
            app_reading = orig_reading
            app_gloss = info["gloss"]
            rel_type = "ABBREVIATION_OF"
            rel_target = info["target"]
            counts["ABBREVIATION_OF"] += 1
        elif surf in READING_CORRECTIONS or surf in GLOSS_CORRECTIONS:
            dec_type = "APPROVE_WITH_REVISION"
            reasons = []
            app_reading = READING_CORRECTIONS.get(surf, orig_reading)
            app_gloss = GLOSS_CORRECTIONS.get(surf, orig_gloss)
            if surf in READING_CORRECTIONS:
                reasons.append("READING_CORRECTION")
            if surf in GLOSS_CORRECTIONS:
                reasons.append("GLOSS_CORRECTION")
            reason = "; ".join(reasons)
            rel_type = None
            rel_target = None
            counts["APPROVE_WITH_REVISION"] += 1
        else:
            dec_type = "APPROVE"
            reason = "VALID_INDEPENDENT_PROFESSIONAL_CONCEPT"
            app_reading = orig_reading
            app_gloss = orig_gloss
            rel_type = None
            rel_target = None
            counts["APPROVE"] += 1

        decision_record = {
            "candidate_id": cid,
            "original_surface": surf,
            "decision": dec_type,
            "decision_reason": reason,
            "original_reading": orig_reading,
            "approved_reading": app_reading,
            "original_gloss": orig_gloss,
            "approved_gloss": app_gloss,
            "relationship_type": rel_type,
            "relationship_target": rel_target,
            "reviewer": REVIEWER,
            "review_method": REVIEW_METHOD,
            "review_authority": REVIEW_AUTHORITY,
            "reviewed_at": REVIEWED_AT,
            "source_commit": SOURCE_COMMIT
        }
        decisions.append(decision_record)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        for d in decisions:
            f.write(json.dumps(d, ensure_ascii=False) + "\n")

    print(f"Generated {len(decisions)} decisions -> {output_path}")
    print(f"Counts: {counts}")
    return decisions


if __name__ == "__main__":
    queue_file = BASE_DIR / "staging" / "review_queue" / "canary_1_2c_human_review_ready.jsonl"
    out_file = BASE_DIR / "staging" / "review_decisions" / "canary_1_2c_authorized_decisions.jsonl"
    build_authorized_decisions(queue_file, out_file)
