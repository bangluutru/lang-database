# Phase 1.2C — Human Review Queue & Boundary Status

**Generated:** 2026-10-01T05:52:28Z  
**Total Records Queued:** 120  
**Pending Human Review:** 120  
**Approved:** 0  
**Rejected / Needs Revision:** 0  
**Review Status:** **PENDING_HUMAN_REVIEW**  

## Stratified Queue Distribution by Domain

| Domain | Count | Primary Authority | Review Status |
|---|:---:|:---:|:---:|
| **accounting** | 18 | Class A/B/C | `PENDING` |
| **finance** | 18 | Class A/B/C | `PENDING` |
| **tax** | 17 | Class A/B/C | `PENDING` |
| **hr** | 16 | Class A/B/C | `PENDING` |
| **trade** | 13 | Class A/B/C | `PENDING` |
| **legal** | 12 | Class A/B/C | `PENDING` |
| **office_communication** | 11 | Class A/B/C | `PENDING` |
| **business** | 6 | Class A/B/C | `PENDING` |
| **management** | 4 | Class A/B/C | `PENDING` |
| **purchasing** | 4 | Class A/B/C | `PENDING` |
| **sales** | 1 | Class A/B/C | `PENDING` |

## Review Queue Sample (First 15 Candidates)

| Candidate ID | Proposed ID | Surface | Reading | Domain | Subdomain | Meaning / Gloss | Authority |
|---|---|---|---|---|---|---|:---:|
| `pool-cand-001625` | `jp-canary-accounting-0001` | **収益認識** | しゅうえきにんしき | accounting | financial_accounting | Financial Accounting | `B` |
| `pool-cand-000860` | `jp-canary-accounting-0002` | **剰余金の配当** | じょうよきんのはいとう | accounting | financial_accounting | Dividends of surplus | `A` |
| `pool-cand-000903` | `jp-canary-accounting-0003` | **減資** | げんし | accounting | financial_accounting | Capital reduction | `A` |
| `pool-cand-000001` | `jp-canary-accounting-0004` | **受取手形、売掛金及び契約資産** | うけとりてがたうりかけきんおよびけいやくしさん | accounting | financial_accounting | Notes and accounts receivable  | `A` |
| `pool-cand-000002` | `jp-canary-accounting-0005` | **受取手形及び売掛金** | うけとりてがたおよびうりかけきん | accounting | financial_accounting | Notes and accounts receivable  | `A` |
| `pool-cand-000003` | `jp-canary-accounting-0006` | **受取手形及び売掛金(純額)** | うけとりてがたおよびうりかけきんじゅんがく | accounting | financial_accounting | Notes and accounts receivable  | `A` |
| `pool-cand-000004` | `jp-canary-accounting-0007` | **売掛金及び契約資産** | うりかけきんおよびけいやくしさん | accounting | financial_accounting | Accounts receivable - trade, a | `A` |
| `pool-cand-000005` | `jp-canary-accounting-0008` | **売掛金及び契約資産(純額)** | うりかけきんおよびけいやくしさんじゅんがく | accounting | financial_accounting | Accounts receivable - trade, a | `A` |
| `pool-cand-000006` | `jp-canary-accounting-0009` | **受取手形(純額)** | うけとりてがたじゅんがく | accounting | financial_accounting | Notes receivable - trade, net | `A` |
| `pool-cand-000007` | `jp-canary-accounting-0010` | **売掛金(純額)** | うりかけきんじゅんがく | accounting | financial_accounting | Accounts receivable - trade, n | `A` |
| `pool-cand-000008` | `jp-canary-accounting-0011` | **契約資産** | けいやくしさん | accounting | financial_accounting | Contract assets | `A` |
| `pool-cand-000009` | `jp-canary-accounting-0012` | **契約資産(純額)** | けいやくしさんじゅんがく | accounting | financial_accounting | Contract assets, net | `A` |
| `pool-cand-000010` | `jp-canary-accounting-0013` | **関係会社売掛金** | かんけいがいしゃうりかけきん | accounting | financial_accounting | Accounts receivable from subsi | `A` |
| `pool-cand-000011` | `jp-canary-accounting-0014` | **割賦売掛金** | かっぷうりかけきん | accounting | financial_accounting | Accounts receivable - installm | `A` |
| `pool-cand-000012` | `jp-canary-accounting-0015` | **開発事業未収入金** | かいはつじぎょうみしゅうにゅうきん | accounting | financial_accounting | Accounts receivable - developm | `A` |

## Human Review Protocol & Promotion Boundary

1. **Strict Boundary:** Candidates in state `validation_passed` remain quarantined in the review queue until an authorized human decision (`APPROVE`, `REJECT`, `NEEDS_REVISION`, `VARIANT_OF`, `DUPLICATE_OF`, `DIFFERENT_SENSE`) is recorded.
2. **No Fake Approvals:** Automatic synthesis of human approval signatures is strictly prohibited.
3. **Promotion Guard:** Only records with `review_status: 'APPROVE'` transition to `PROMOTION_ELIGIBLE` and become eligible for Canary release bundling.
