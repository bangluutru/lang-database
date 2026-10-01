# PHASE 1.1C — QUARANTINE DIAGNOSIS REPORT

**Generated**: 2026-10-01T02:44:00.602512+00:00

## Summary

| Metric | Count |
|--------|-------|
| Total quarantined | 28 |
| Systemic (pipeline) errors | 16 |
| Record-level errors | 12 |
| Remediation possible | 28 |

## Failure Category Distribution

| Category | Count |
|----------|-------|
| TECHNICAL_VALIDATION_FAILURE | 28 |
| EXAMPLE_DOES_NOT_CONTAIN_TERM | 15 |
| DIALOGUE_ERROR | 10 |
| EXAMPLE_NATURALNESS_ERROR | 7 |
| DOMAIN_FACTUAL_ERROR | 7 |
| COLLOCATION_ERROR | 4 |
| SEMANTIC_CLASS_ERROR | 1 |

## Record Diagnoses

### jp-pro-accounting-000071 — 創立費
- **Domain**: accounting | **Semantic class**: account
- **Failure stage**: release_gate
- **Categories**: TECHNICAL_VALIDATION_FAILURE
- **Root cause**: Missing validation_record: record never completed the release gate.
- **Systemic**: False
- **Remediation possible**: True
- **Recommended action**: REMEDIATE_AND_REVALIDATE

### jp-pro-accounting-000100 — 退職給付引当金
- **Domain**: accounting | **Semantic class**: account
- **Failure stage**: release_gate
- **Categories**: TECHNICAL_VALIDATION_FAILURE
- **Root cause**: Missing validation_record: record never completed the release gate.
- **Systemic**: False
- **Remediation possible**: True
- **Recommended action**: REMEDIATE_AND_REVALIDATE

### jp-pro-accounting-000136 — 完成工事総利益
- **Domain**: accounting | **Semantic class**: account
- **Failure stage**: release_gate
- **Categories**: TECHNICAL_VALIDATION_FAILURE
- **Root cause**: Missing validation_record: record never completed the release gate.
- **Systemic**: False
- **Remediation possible**: True
- **Recommended action**: REMEDIATE_AND_REVALIDATE

### jp-pro-accounting-000178 — 法人税等調整額
- **Domain**: accounting | **Semantic class**: account
- **Failure stage**: release_gate
- **Categories**: TECHNICAL_VALIDATION_FAILURE
- **Root cause**: Missing validation_record: record never completed the release gate.
- **Systemic**: False
- **Remediation possible**: True
- **Recommended action**: REMEDIATE_AND_REVALIDATE

### jp-pro-business-000027 — 個別契約
- **Domain**: business | **Semantic class**: contract
- **Failure stage**: release_gate
- **Categories**: TECHNICAL_VALIDATION_FAILURE
- **Root cause**: Missing validation_record: record never completed the release gate.
- **Systemic**: False
- **Remediation possible**: True
- **Recommended action**: REMEDIATE_AND_REVALIDATE

### jp-pro-business-000030 — 期日厳守
- **Domain**: business | **Semantic class**: business_practice
- **Failure stage**: release_gate
- **Categories**: TECHNICAL_VALIDATION_FAILURE
- **Root cause**: Missing validation_record: record never completed the release gate.
- **Systemic**: False
- **Remediation possible**: True
- **Recommended action**: REMEDIATE_AND_REVALIDATE

### jp-pro-business-000061 — 契約書
- **Domain**: business | **Semantic class**: document
- **Failure stage**: release_gate
- **Categories**: TECHNICAL_VALIDATION_FAILURE
- **Root cause**: Missing validation_record: record never completed the release gate.
- **Systemic**: False
- **Remediation possible**: True
- **Recommended action**: REMEDIATE_AND_REVALIDATE

### jp-pro-business-000070 — 甲乙関係
- **Domain**: business | **Semantic class**: contractual_relationship
- **Failure stage**: release_gate
- **Categories**: TECHNICAL_VALIDATION_FAILURE
- **Root cause**: Missing validation_record: record never completed the release gate.
- **Systemic**: False
- **Remediation possible**: True
- **Recommended action**: REMEDIATE_AND_REVALIDATE

### jp-pro-business-000101 — 役職手当
- **Domain**: business | **Semantic class**: account
- **Failure stage**: release_gate
- **Categories**: TECHNICAL_VALIDATION_FAILURE, SEMANTIC_CLASS_ERROR
- **Root cause**: Missing validation_record: record never completed the release gate. | Semantic class 'account' inappropriate for domain 'business': triggered wrong collocations/examples.
- **Systemic**: False
- **Remediation possible**: True
- **Recommended action**: REMEDIATE_AND_REVALIDATE

### jp-pro-business-000116 — 健康保険
- **Domain**: business | **Semantic class**: social_insurance
- **Failure stage**: release_gate
- **Categories**: TECHNICAL_VALIDATION_FAILURE
- **Root cause**: Missing validation_record: record never completed the release gate.
- **Systemic**: False
- **Remediation possible**: True
- **Recommended action**: REMEDIATE_AND_REVALIDATE

### jp-pro-business-000132 — 商談
- **Domain**: business | **Semantic class**: business_practice
- **Failure stage**: example_generation
- **Categories**: EXAMPLE_DOES_NOT_CONTAIN_TERM, TECHNICAL_VALIDATION_FAILURE
- **Root cause**: Missing validation_record: record never completed the release gate. | Examples at index [0, 1] do not contain target term '商談' — SYSTEMIC: wrong template was applied (likely fallback generic accounting/governance template).
- **Systemic**: True
- **Remediation possible**: True
- **Recommended action**: REMEDIATE_AND_REVALIDATE

### jp-pro-business-000137 — 競合他社
- **Domain**: business | **Semantic class**: organization
- **Failure stage**: example_generation
- **Categories**: EXAMPLE_DOES_NOT_CONTAIN_TERM, COLLOCATION_ERROR, DIALOGUE_ERROR, TECHNICAL_VALIDATION_FAILURE
- **Root cause**: Missing validation_record: record never completed the release gate. | Examples at index [0, 1] do not contain target term '競合他社' — SYSTEMIC: wrong template was applied (likely fallback generic accounting/governance template). | Dialogue does not reference term '競合他社' — wrong template applied. | Corporate-governance predicates (決議する/招集する) applied to organization term — SYSTEMIC: organization semantic class defaulted to governance predicates.
- **Systemic**: True
- **Remediation possible**: True
- **Recommended action**: REMEDIATE_AND_REVALIDATE

### jp-pro-business-000138 — 差別化
- **Domain**: business | **Semantic class**: business_strategy
- **Failure stage**: example_generation
- **Categories**: EXAMPLE_NATURALNESS_ERROR, DIALOGUE_ERROR, TECHNICAL_VALIDATION_FAILURE, EXAMPLE_DOES_NOT_CONTAIN_TERM, DOMAIN_FACTUAL_ERROR
- **Root cause**: Missing validation_record: record never completed the release gate. | Examples at index [0, 1] do not contain target term '差別化' — SYSTEMIC: wrong template was applied (likely fallback generic accounting/governance template). | Dialogue does not reference term '差別化' — wrong template applied. | Accounting ledger reconciliation phrases injected into non-accounting domain — SYSTEMIC: fallback accounting template applied to business/trade term.
- **Systemic**: True
- **Remediation possible**: True
- **Recommended action**: REMEDIATE_AND_REVALIDATE

### jp-pro-business-000141 — クロージング
- **Domain**: business | **Semantic class**: procedure
- **Failure stage**: example_generation
- **Categories**: EXAMPLE_NATURALNESS_ERROR, DIALOGUE_ERROR, TECHNICAL_VALIDATION_FAILURE, EXAMPLE_DOES_NOT_CONTAIN_TERM, DOMAIN_FACTUAL_ERROR
- **Root cause**: Missing validation_record: record never completed the release gate. | Examples at index [0, 1] do not contain target term 'クロージング' — SYSTEMIC: wrong template was applied (likely fallback generic accounting/governance template). | Dialogue does not reference term 'クロージング' — wrong template applied. | Accounting ledger reconciliation phrases injected into non-accounting domain — SYSTEMIC: fallback accounting template applied to business/trade term.
- **Systemic**: True
- **Remediation possible**: True
- **Recommended action**: REMEDIATE_AND_REVALIDATE

### jp-pro-business-000142 — 成約
- **Domain**: business | **Semantic class**: contract
- **Failure stage**: example_generation
- **Categories**: EXAMPLE_DOES_NOT_CONTAIN_TERM, DIALOGUE_ERROR, TECHNICAL_VALIDATION_FAILURE
- **Root cause**: Missing validation_record: record never completed the release gate. | Examples at index [0, 1] do not contain target term '成約' — SYSTEMIC: wrong template was applied (likely fallback generic accounting/governance template). | Dialogue does not reference term '成約' — wrong template applied.
- **Systemic**: True
- **Remediation possible**: True
- **Recommended action**: REMEDIATE_AND_REVALIDATE

### jp-pro-business-000148 — 市場調査
- **Domain**: business | **Semantic class**: procedure
- **Failure stage**: release_gate
- **Categories**: EXAMPLE_NATURALNESS_ERROR, TECHNICAL_VALIDATION_FAILURE, DOMAIN_FACTUAL_ERROR
- **Root cause**: Missing validation_record: record never completed the release gate. | Accounting ledger reconciliation phrases injected into non-accounting domain — SYSTEMIC: fallback accounting template applied to business/trade term.
- **Systemic**: True
- **Remediation possible**: True
- **Recommended action**: REMEDIATE_AND_REVALIDATE

### jp-pro-business-000155 — 販売促進
- **Domain**: business | **Semantic class**: business_practice
- **Failure stage**: example_generation
- **Categories**: EXAMPLE_DOES_NOT_CONTAIN_TERM, TECHNICAL_VALIDATION_FAILURE
- **Root cause**: Missing validation_record: record never completed the release gate. | Examples at index [0, 1] do not contain target term '販売促進' — SYSTEMIC: wrong template was applied (likely fallback generic accounting/governance template).
- **Systemic**: True
- **Remediation possible**: True
- **Recommended action**: REMEDIATE_AND_REVALIDATE

### jp-pro-business-000165 — 紹介営業
- **Domain**: business | **Semantic class**: business_practice
- **Failure stage**: example_generation
- **Categories**: EXAMPLE_DOES_NOT_CONTAIN_TERM, TECHNICAL_VALIDATION_FAILURE
- **Root cause**: Missing validation_record: record never completed the release gate. | Examples at index [0, 1] do not contain target term '紹介営業' — SYSTEMIC: wrong template was applied (likely fallback generic accounting/governance template).
- **Systemic**: True
- **Remediation possible**: True
- **Recommended action**: REMEDIATE_AND_REVALIDATE

### jp-pro-business-000189 — 出張申請
- **Domain**: business | **Semantic class**: procedure
- **Failure stage**: example_generation
- **Categories**: EXAMPLE_NATURALNESS_ERROR, DIALOGUE_ERROR, TECHNICAL_VALIDATION_FAILURE, EXAMPLE_DOES_NOT_CONTAIN_TERM, DOMAIN_FACTUAL_ERROR
- **Root cause**: Missing validation_record: record never completed the release gate. | Examples at index [0, 1] do not contain target term '出張申請' — SYSTEMIC: wrong template was applied (likely fallback generic accounting/governance template). | Dialogue does not reference term '出張申請' — wrong template applied. | Accounting ledger reconciliation phrases injected into non-accounting domain — SYSTEMIC: fallback accounting template applied to business/trade term.
- **Systemic**: True
- **Remediation possible**: True
- **Recommended action**: REMEDIATE_AND_REVALIDATE

### jp-pro-tax-000035 — 源泉分離課税
- **Domain**: tax | **Semantic class**: tax_scheme
- **Failure stage**: release_gate
- **Categories**: TECHNICAL_VALIDATION_FAILURE
- **Root cause**: Missing validation_record: record never completed the release gate.
- **Systemic**: False
- **Remediation possible**: True
- **Recommended action**: REMEDIATE_AND_REVALIDATE

### jp-pro-tax-000194 — 常設的施設
- **Domain**: tax | **Semantic class**: tax_nexus
- **Failure stage**: release_gate
- **Categories**: TECHNICAL_VALIDATION_FAILURE
- **Root cause**: Missing validation_record: record never completed the release gate.
- **Systemic**: False
- **Remediation possible**: True
- **Recommended action**: REMEDIATE_AND_REVALIDATE

### jp-pro-trade-000061 — 税関
- **Domain**: trade | **Semantic class**: organization
- **Failure stage**: example_generation
- **Categories**: EXAMPLE_DOES_NOT_CONTAIN_TERM, COLLOCATION_ERROR, TECHNICAL_VALIDATION_FAILURE
- **Root cause**: Missing validation_record: record never completed the release gate. | Examples at index [0, 1] do not contain target term '税関' — SYSTEMIC: wrong template was applied (likely fallback generic accounting/governance template). | Corporate-governance predicates (決議する/招集する) applied to organization term — SYSTEMIC: organization semantic class defaulted to governance predicates.
- **Systemic**: True
- **Remediation possible**: True
- **Recommended action**: REMEDIATE_AND_REVALIDATE

### jp-pro-trade-000070 — 関税率
- **Domain**: trade | **Semantic class**: customs_tariff
- **Failure stage**: example_generation
- **Categories**: EXAMPLE_NATURALNESS_ERROR, DIALOGUE_ERROR, TECHNICAL_VALIDATION_FAILURE, EXAMPLE_DOES_NOT_CONTAIN_TERM, DOMAIN_FACTUAL_ERROR
- **Root cause**: Missing validation_record: record never completed the release gate. | Examples at index [0, 1] do not contain target term '関税率' — SYSTEMIC: wrong template was applied (likely fallback generic accounting/governance template). | Dialogue does not reference term '関税率' — wrong template applied. | Accounting ledger reconciliation phrases injected into non-accounting domain — SYSTEMIC: fallback accounting template applied to business/trade term.
- **Systemic**: True
- **Remediation possible**: True
- **Recommended action**: REMEDIATE_AND_REVALIDATE

### jp-pro-trade-000076 — 統計品目番号
- **Domain**: trade | **Semantic class**: customs_tariff
- **Failure stage**: example_generation
- **Categories**: EXAMPLE_DOES_NOT_CONTAIN_TERM, EXAMPLE_NATURALNESS_ERROR, TECHNICAL_VALIDATION_FAILURE, DOMAIN_FACTUAL_ERROR
- **Root cause**: Missing validation_record: record never completed the release gate. | Examples at index [0, 1] do not contain target term '統計品目番号' — SYSTEMIC: wrong template was applied (likely fallback generic accounting/governance template). | Accounting ledger reconciliation phrases injected into non-accounting domain — SYSTEMIC: fallback accounting template applied to business/trade term.
- **Systemic**: True
- **Remediation possible**: True
- **Recommended action**: REMEDIATE_AND_REVALIDATE

### jp-pro-trade-000116 — ディスクレ
- **Domain**: trade | **Semantic class**: trade_finance
- **Failure stage**: example_generation
- **Categories**: EXAMPLE_NATURALNESS_ERROR, DIALOGUE_ERROR, TECHNICAL_VALIDATION_FAILURE, EXAMPLE_DOES_NOT_CONTAIN_TERM, DOMAIN_FACTUAL_ERROR
- **Root cause**: Missing validation_record: record never completed the release gate. | Examples at index [0, 1] do not contain target term 'ディスクレ' — SYSTEMIC: wrong template was applied (likely fallback generic accounting/governance template). | Dialogue does not reference term 'ディスクレ' — wrong template applied. | Accounting ledger reconciliation phrases injected into non-accounting domain — SYSTEMIC: fallback accounting template applied to business/trade term.
- **Systemic**: True
- **Remediation possible**: True
- **Recommended action**: REMEDIATE_AND_REVALIDATE

### jp-pro-trade-000137 — TTM
- **Domain**: trade | **Semantic class**: metric
- **Failure stage**: example_generation
- **Categories**: EXAMPLE_DOES_NOT_CONTAIN_TERM, DIALOGUE_ERROR, TECHNICAL_VALIDATION_FAILURE
- **Root cause**: Missing validation_record: record never completed the release gate. | Examples at index [0, 1] do not contain target term 'TTM' — SYSTEMIC: wrong template was applied (likely fallback generic accounting/governance template). | Dialogue does not reference term 'TTM' — wrong template applied.
- **Systemic**: True
- **Remediation possible**: True
- **Recommended action**: REMEDIATE_AND_REVALIDATE

### jp-pro-trade-000138 — コルレス銀行
- **Domain**: trade | **Semantic class**: organization
- **Failure stage**: example_generation
- **Categories**: EXAMPLE_DOES_NOT_CONTAIN_TERM, COLLOCATION_ERROR, DIALOGUE_ERROR, TECHNICAL_VALIDATION_FAILURE
- **Root cause**: Missing validation_record: record never completed the release gate. | Examples at index [0, 1] do not contain target term 'コルレス銀行' — SYSTEMIC: wrong template was applied (likely fallback generic accounting/governance template). | Dialogue does not reference term 'コルレス銀行' — wrong template applied. | Corporate-governance predicates (決議する/招集する) applied to organization term — SYSTEMIC: organization semantic class defaulted to governance predicates.
- **Systemic**: True
- **Remediation possible**: True
- **Recommended action**: REMEDIATE_AND_REVALIDATE

### jp-pro-trade-000141 — フォワーダー
- **Domain**: trade | **Semantic class**: organization
- **Failure stage**: example_generation
- **Categories**: EXAMPLE_DOES_NOT_CONTAIN_TERM, COLLOCATION_ERROR, DIALOGUE_ERROR, TECHNICAL_VALIDATION_FAILURE
- **Root cause**: Missing validation_record: record never completed the release gate. | Examples at index [0, 1] do not contain target term 'フォワーダー' — SYSTEMIC: wrong template was applied (likely fallback generic accounting/governance template). | Dialogue does not reference term 'フォワーダー' — wrong template applied. | Corporate-governance predicates (決議する/招集する) applied to organization term — SYSTEMIC: organization semantic class defaulted to governance predicates.
- **Systemic**: True
- **Remediation possible**: True
- **Recommended action**: REMEDIATE_AND_REVALIDATE
