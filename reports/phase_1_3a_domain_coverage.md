# Phase 1.3A Domain Coverage Report

## Summary of Professional Domain Representation

| Domain | Prod (800) | Canary 1.2C (102) | Raw | Deduplicated | Review Batch | Auth A | Auth B | Auth C | REVIEW-A | REVIEW-B | REVIEW-C |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **accounting** | 200 | 10 | 2534 | 2350 | **220** | 220 | 0 | 0 | 220 | 0 | 0 |
| **finance** | 0 | 17 | 724 | 690 | **150** | 150 | 0 | 0 | 150 | 0 | 0 |
| **tax** | 200 | 9 | 1149 | 238 | **234** | 234 | 0 | 0 | 46 | 170 | 18 |
| **hr** | 0 | 16 | 163 | 104 | **104** | 104 | 0 | 0 | 99 | 1 | 4 |
| **trade** | 200 | 12 | 199 | 92 | **85** | 85 | 0 | 0 | 65 | 2 | 18 |
| **legal** | 0 | 12 | 176 | 106 | **97** | 97 | 0 | 0 | 89 | 3 | 5 |
| **office_communication** | 0 | 11 | 49 | 24 | **24** | 24 | 0 | 0 | 23 | 1 | 0 |
| **business** | 200 | 6 | 447 | 432 | **120** | 120 | 0 | 0 | 120 | 0 | 0 |
| **management** | 0 | 4 | 26 | 14 | **14** | 12 | 0 | 2 | 13 | 1 | 0 |
| **purchasing** | 0 | 4 | 119 | 57 | **57** | 57 | 0 | 0 | 53 | 0 | 4 |
| **sales** | 0 | 1 | 30 | 9 | **9** | 9 | 0 | 0 | 9 | 0 | 0 |

## Domain Balancing & Domination Prevention (Sections 6 & 7)
- **Accounting & Finance Control**: Accounting (220) and Finance (150) were strictly capped to prevent EDINET taxonomies from overwhelming the review batch.
- **Practical Domain Expansion**: High-priority domains (Tax: 231, HR: 103, Legal: 94, Trade: 85, Purchasing: 57) form over 51% of the final review batch.

## Coverage Gaps & Observations
- `sales` (9 candidates) and `management` (14 candidates) represent the smallest cohorts. These should receive targeted secondary source expansion in Phase 1.3B.
- All 11 professional domains have candidates ready for human/LLM review.