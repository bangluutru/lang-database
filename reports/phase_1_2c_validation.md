# Phase 1.2C — Independent Validation Gates Report

- **Validated At**: `2026-10-01T06:14:56Z`
- **Total Candidates Evaluated**: `120`
- **Validation Passed (`validation_passed`)**: `119`
- **Needs Human Review (`needs_review`)**: `1`
- **Rejected (`rejected`)**: `0`

## 1. Gate Execution Summary

| Validation Gate | Focus Area | Status Pass | Flagged / Fail | Enforcement |
|:----------------|:-----------|:-----------:|:--------------:|:------------|
| **Gate A: Schema & Provenance** | Schema integrity, taxonomy validity, source locators, raw hashes, draft/licensing guards | 120/120 | 0 | Hard Gate (Zero tolerance) |
| **Gate B: Dedup & Variations** | Exact duplicate against baselines, orthographic variants, abbreviations, polysemy senses | 119/120 | 1 | Semantic Gate (Routes to Review) |
| **Gate C: Linguistic Quality** | Japanese script validation, hiragana reading validity, diacritic leakage, template markers | 120/120 | 0 | Linguistic Quality Gate |

## 2. State Distribution Post-Validation

- `needs_review`: **1**
- `validation_passed`: **119**

## 3. Flagged Items Requiring Review or Correction

| Candidate ID | Surface | Domain | Assigned State | Reasons |
|:-------------|:--------|:-------|:---------------|:--------|
| `pool-cand-001689` | `NACCS` | `trade` | `needs_review` | Abbreviation detected: 'NACCS' is abbreviation of '輸出入・港湾関連情報処理システム'. |
