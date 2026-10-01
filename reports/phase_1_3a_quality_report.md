# Phase 1.3A Quality & Linguistic Integrity Report

## Quality Gate and Audit Findings (Section 34)

| Quality Metric / Flag | Count in Review Pack | Status |
| :--- | :---: | :--- |
| `reading_review_required` | 39 | Flagged for phonetic compound verification in REVIEW-B/C |
| `gloss_review_required` | 186 | Flagged for English precision verification in REVIEW-B/C |
| `canonical_value_review_required` | 13 | Borderline compound structure flagged for human review |
| `abbreviation_flag` | 7 | Mapped with possible_abbreviation_of relationship |
| `variant_flag` | 0 | Mapped with possible_variant_of relationship |
| `semantic_duplicate_flag` | 0 | Verified distinct |
| `artifact_flag` | 0 | 0 in review pack (all 100% rejected at quality gate) |
| `taxonomy_variant_flag` | 13 | Controlled reporting labels in REVIEW-C |
| `truncated_gloss` | 0 | Flagged and repaired / quarantined |
| `malformed_parentheses` | 0 | Audited per Section 22 integrity rules |
| `rejected_composite_taxonomy_labels` | 334 | Rejected from review pack (XBRL Section 14) |
| `rejected_extraction_artifacts` | 0 | Rejected navigational/page headings |

## Reading Regression Fixtures Verification
- `貸出金` → `かしだしきん` (貸: かし, not たい) ✓
- `加盟店貸勘定` → `かめいてんかしかんじょう` (貸: かし, not たい) ✓
- `特定輸出者` → `とくていゆしゅつしゃ` (者: しゃ, not もの) ✓
- `資本金の額` → `しほんきんのがく` (額: がく, not ひたい) ✓
- `準備金の額` → `じゅんびきんのがく` (額: がく, not ひたい) ✓
- `顛末書` → `てんまつしょ` (書: しょ, not かき) ✓
- `事業計画書` → `じぎょうけいかくしょ` (書: しょ, not かき) ✓
- `課税物件表` → `かぜいぶっけんひょう` (表: ひょう, not おもて) ✓
- `買現先勘定` → `かいげんさきかんじょう` (先: さき, not せん) ✓