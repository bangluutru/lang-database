# QA Summary — Phase 1.1 Data Integrity & Linguistic Validation

## Validation Metrics (800 Pilot Candidates)

| Metric | Count | Percentage |
| :--- | :--- | :--- |
| **Total Candidates** | 800 | 100.0% |
| **Schema Valid** | 800 | 100.0% |
| **Official Source Verified** | 637 | 79.6% |
| **Curated Documented** | 163 | 20.4% |
| **Reading Verified** | 789 | 98.6% |
| **Reading Needs Review** | 2 | 0.2% |
| **Reading Rejected** | 9 | 1.1% |
| **VI Translation Verified** | 800 | 100.0% |
| **Collocations Verified** | 800 | 100.0% |
| **Examples Verified** | 800 | 100.0% |
| **TTS Ready** | 800 | 100.0% |
| **Draft Contamination Free** | 800 | 100.0% |
| **Production Ready (PASS)** | **789** | **98.6%** |
| **Review Queue (NEEDS REVIEW)**| **2** | **0.2%** |
| **Rejected (FAIL)** | **9** | **1.1%** |

## Independent Decision Breakdown
- **PASS**: Meets all 8 linguistic and provenance criteria. Routed to production.
- **NEEDS REVIEW**: Phonetic variance or curated origin requires specialist review. Quarantined to staging review queue.
- **REJECTED**: Corrupted phonetics, draft contamination, or schema failure. Excluded from production.
