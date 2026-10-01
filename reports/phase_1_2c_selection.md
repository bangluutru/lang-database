# Phase 1.2C — Controlled Canary Selection Report

- **Generated At**: `2026-10-01T06:14:56Z`
- **Candidate Pool Size**: `1755`
- **Selected for Canary**: `120`
- **Stratification Strategy**: Multi-dimensional deterministic ranking with professional domain quotas
- **Draft Sources Excluded**: `fsa-edinet-2027-draft` (100% quarantined)
- **Licensing Guard**: 0 RED reuse items selected

## 1. Domain Stratification Quotas & Actual Selection

| Professional Domain | Quota Target | Selected Count | Representation Ratio |
|:--------------------|:------------:|:--------------:|:--------------------:|
| `accounting` | 18 | 18 | 15.0% |
| `finance` | 18 | 18 | 15.0% |
| `tax` | 17 | 17 | 14.2% |
| `hr` | 16 | 16 | 13.3% |
| `trade` | 13 | 13 | 10.8% |
| `legal` | 12 | 12 | 10.0% |
| `office_communication` | 11 | 11 | 9.2% |
| `business` | 6 | 6 | 5.0% |
| `management` | 4 | 4 | 3.3% |
| `purchasing` | 4 | 4 | 3.3% |
| `sales` | 1 | 1 | 0.8% |

## 2. Source Diversity Distribution

| Source ID | Evidence References | Authority Class |
|:----------|:-------------------:|:---------------:|
| `fsa-edinet-taxonomy` | 35 | `A` |
| `smrj-business-guidance` | 22 | `C` |
| `egov-corporate-law` | 18 | `A` |
| `nta-tax-glossary` | 17 | `A` |
| `mhlw-labor` | 16 | `A` |
| `japan-customs-trade` | 9 | `A` |
| `jetro-trade` | 4 | `C` |
| `asbj-accounting-standards` | 1 | `B` |

## 3. Authority & Quality Tier Breakdown

- **Authority Class A**: `93` terms
- **Authority Class B**: `1` terms
- **Authority Class C**: `26` terms
- **PRO-A1 (Standard Canonical)**: `2`
- **PRO-A2 (Domain Specific)**: `4`
- **PRO-A3 (General / Contextual)**: `114`

## 4. Deterministic Ranking & Selection Methodology

Every candidate is ranked deterministically by a 6-tuple sort key:
1. `tier_rank` (PRO-A1 > PRO-A2 > PRO-A3)
2. `authority_rank` (A > B > C)
3. `agreement_rank` (Multi-source agreement prioritized)
4. `importance_rank` (High > Medium > Low)
5. `frequency_rank` (High > Medium > Low)
6. `tie_breaker` (Lexicographical candidate_id)
