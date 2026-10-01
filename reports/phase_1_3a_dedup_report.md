# Phase 1.3A.1 Multi-Level Deduplication Report

## Deduplication Summary Statistics

- **Exact Duplicates Merged (Level 1)**: 36
- **Normalized Duplicates Merged (Level 2)**: 3
- **Existing Production Vocabulary Excluded**: 499 (800 records protected)
- **Existing Canary 1.2C Concepts Excluded**: 164 (102 canonical concepts + 8 relations protected)
- **Professional Abbreviations Detected (Level 4)**: 6
- **Spelling / Structural Variants Mapped (Level 3)**: 30
- **Same-Concept Cross-Domain Consolidations (Section 22)**: 12
- **Different Professional Senses Preserved (Level 6)**: 0

## Representative Deduplication Examples

### Existing Production & Canary Exclusions
- `貸借対照表` (貸借対照表): Found in production/vocabulary.jsonl (800 records)
- `現金及び預金` (現金及び預金): Found in production/vocabulary.jsonl (800 records)
- `貸倒引当金` (貸倒引当金): Found in production/vocabulary.jsonl (800 records)
- `受取手形` (受取手形): Found in production/vocabulary.jsonl (800 records)
- `売掛金` (売掛金): Found in production/vocabulary.jsonl (800 records)
- `契約資産` (契約資産): Found in canary-1.2c release
- `関係会社売掛金` (関係会社売掛金): Found in canary-1.2c release
- `割賦売掛金` (割賦売掛金): Found in canary-1.2c release
- `開発事業未収入金` (開発事業未収入金): Found in canary-1.2c release
- `不動産事業未収入金` (不動産事業未収入金): Found in canary-1.2c release

### Abbreviation Relationships (Level 4, No Self-References, Deduplicated)
- `消法` → full form: `消費税法` (Domain: tax)
- `所法` → full form: `所得税法` (Domain: tax)
- `相法` → full form: `相続税法` (Domain: tax)
- `法法` → full form: `法人税法` (Domain: tax)
- `外為法` → full form: `外国為替及び外国貿易法` (Domain: trade)

### Same-Concept Cross-Domain Consolidations (Section 22)
- `寄附金`: Consolidated across `accounting` and `tax` into single canonical concept.
- `引当金`: Consolidated across `accounting` and `tax` into single canonical concept.
- `雇用調整助成金`: Consolidated across `accounting` and `hr` into single canonical concept.
- `下請事業者`: Consolidated across `business` and `purchasing` into single canonical concept.
- `自己株式の取得`: Consolidated across `accounting` and `legal` into single canonical concept.

### Structural Variants (Level 3)
- Variant `受取手形・完成工事未収入金` mapped to canonical `受取手形・完成工事未収入金等`
- Variant `未成工事支出金等` mapped to canonical `未成工事支出金`
- Variant `支払手形・工事未払金` mapped to canonical `支払手形・工事未払金等`
- Variant `開発事業等売上高` mapped to canonical `開発事業売上高`
- Variant `不動産事業等売上高` mapped to canonical `不動産事業売上高`