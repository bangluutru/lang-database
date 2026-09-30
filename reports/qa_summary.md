# Quality Assurance (QA) Summary Report

- **Execution Timestamp:** 2026-10-01T08:20:00Z
- **Total Production Pilot Entries:** 800
- **Validation Status:** PASSED (100%)
- **Passed Items:** 800 / 800
- **Failed Items:** 0

## 1. Domain Distribution

| Domain | Canonical Entries | Status |
|---|---|---|
| `accounting` | 200 | Authoritative & Validated |
| `tax` | 200 | Authoritative & Validated |
| `business` | 200 | Authoritative & Validated |
| `trade` | 200 | Authoritative & Validated |
| **Total** | **800** | **Phase 1 Pilot Target Met** |

## 2. Professional Tier Breakdown

| Tier | Level Description | Count | Percentage |
|---|---|---|---|
| **PRO-A1** | Essential Workplace | 436 | 54.5% |
| **PRO-A2** | Working Professional | 318 | 39.8% |
| **PRO-A3** | Specialist | 46 | 5.8% |

## 3. Supplementary Layers Verification

- **Workplace Idiomatic Expressions (`expressions.jsonl`):** 50 verified entries.
- **Knowledge Graph Relationships (`relationships.jsonl`):** 2078 semantic edges (synonym, antonym, related).

## 4. Priority Score Distribution

- **Essential (>=95):** 448 entries (56.0%)
- **High (90-94):** 306 entries (38.2%)
- **Medium (<90):** 46 entries (5.8%)

## 5. Audit Compliance Checklist

- [x] **Zero-Inference Provenance:** Official sources (FSA/NTA/JICPA/JETRO) separated from learning explanations.
- [x] **2027 EDINET Isolation:** Draft terms strictly held in staging; production contains only verified 2026 final taxonomy.
- [x] **Pronunciation Integrity:** 100% Hiragana readings validated with Modified Hepburn romaji.
- [x] **TTS Engine Decoupling:** Full TTS metadata (pronunciation, pauses, speech text) without vendor lock-in.
- [x] **Multi-modal Learning Content:** Every entry contains collocations, multi-register examples, and multi-speaker dialogue.
