# Phase 1.3A & 1.3A.1 Linguistic Quality, Integrity, and Audit Report

## Quality Gate Statistics
- **Total Candidates Evaluated**: 3770
- **Extraction Artifacts Rejected**: 0
- **Composite Taxonomy Labels Rejected**: 334
- **Final Review Candidates Selected**: 1104
- **REVIEW-A Candidates**: 882
- **REVIEW-B Candidates**: 174
- **REVIEW-C Candidates**: 48

## Quality Flag Counts in Selected Batch
- `READING_REVIEW_REQUIRED`: 38
- `GLOSS_REVIEW_REQUIRED`: 181
- `CANONICAL_VALUE_REVIEW_REQUIRED`: 13
- `ABBREVIATION_FLAG`: 6
- `VARIANT_FLAG`: 0
- `SEMANTIC_DUPLICATE_FLAG`: 0
- `ARTIFACT_FLAG`: 0 (Filtered out by gate)
- `TAXONOMY_VARIANT_FLAG`: 14
- `TRUNCATED_GLOSS`: 0
- `MALFORMED_PARENTHESES`: 0

## Phonetic Override Regression Protection Verification
- `貸出金` → `かしだしきん` (貸: かし, not たい) ✓
- `加盟店貸勘定` → `かめいてんかしかんじょう` (貸: かし, not たい) ✓
- `特定輸出者` → `とくていゆしゅつしゃ` (者: しゃ, not もの) ✓
- `資本金の額` → `しほんきんのがく` (額: がく, not ひたい) ✓
- `準備金の額` → `じゅんびきんのがく` (額: がく, not ひたい) ✓
- `顛末書` → `てんまつしょ` (書: しょ, not かき) ✓
- `事業計画書` → `じぎょうけいかくしょ` (書: しょ, not かき) ✓
- `課税物件表` → `かぜいぶっけんひょう` (表: ひょう, not おもて) ✓
- `買現先勘定` → `かいげんさきかんじょう` (先: さき, not せん) ✓