# English–Japanese–Vietnamese Learning Lexical Graph (Phase 1.3C)

> **Curated, open, machine-readable English–Japanese–Vietnamese Learning Lexical Graph built on a canonical `Concept` → `Sense` → `Expression` tri-language architecture.**

Designed specifically as a pedagogical **source-of-truth** to support:
- Vietnamese users learning Japanese and English
- Japanese users learning English and Vietnamese
- International users utilizing English as a bridge to Japanese and Vietnamese
- Audio vocabulary shadowing, multi-modal video lesson rendering, and adaptive spaced-repetition engines (e.g. `oki-language`)

---

## 1. Architectural Evolution (Phase 1.3C Authoritative Ingestion & Expansion)

- **Authentic Upstream Source Ingestion (`data/raw/`)**:
  - Replaced seed-only ingestion with reproducible acquisition from 11 verified upstream datasets:
    `kanjidic2`, `joyo`, `jmdict`, `ngsl`, `ngsl_spoken`, `nawl`, `bsl`, `tsl`, `vn_freq`, `unihan`, `jlpt_consensus`.
  - Immutable raw snapshots with SHA-256 verification and `metadata.json`.
- **Strict Provenance Guard & Special Negative Test**:
  - All extracted data is anchored to exact snapshot line/entry locators.
  - Enforces the Section 26 Negative Rule: unbacked local curated JSON claiming `SOURCE_DERIVED` is blocked and quarantined.
  - Seed fixtures are audited and explicitly marked `origin="seed_curated"`.
- **Semantic Separation: Concept vs. Sense vs. Expression**:
  - `Concept`: Language-independent semantic identity (e.g. `concept-core-water`).
  - `Sense`: Distinct semantic meaning with individual POS, register, and glosses. Polysemous words (e.g. `right`, `bank`, `charge`, `interest`) are never collapsed.
  - `Expression`: Language-specific lexical realization (`en`, `ja`, `vi`). Language-specific phonetic and morphological fields (JA: reading, kanji; VI: Hán-Việt cognates; EN: IPA).
- **Many-to-Many Learning Classifications**:
  - Over 8,300 classifications attached to Concepts/Senses without duplicating lexical records:
    CEFR (1,332), EIKEN (1,307), JOYO_KANJI (1,235), JLPT (1,028), NGSL (1,331), VI_CORE (814), TOEIC/IELTS/TOEFL (20), Professional Tiers (800).
- **Backward Compatibility & Legacy Bridge**:
  - All 800 legacy `jp-pro-*` records are projected into canonical entities and remain 100% frozen.
  - `legacy_mapping.json` maintains exact forward and reverse traceability.
- **Oki-Language Compatibility (`data/exports/oki_language/deck_data.json`)**:
  - 2,106 formatted tri-language learning cards exported directly for downstream educational web applications.

---

## 2. Canonical Graph Metrics (Phase 1.3C Expansion)

| Metric | Value | Details |
|---|---|---|
| **Total Canonical Concepts** | **2,106** | 800 professional + 15 polysemy benchmarks + 1,291 core aligned |
| **Total Canonical Senses** | **2,106** | Sense-level definitions with POS, register, and glosses |
| **Total Lexical Expressions** | **6,318** | 2,106 English + 2,106 Japanese + 2,106 Vietnamese |
| **Tri-Language Complete Concepts** | **2,106** | 100% complete EN ↔ JA ↔ VI coverage across canonical concepts |
| **Partial / Ambiguous Concepts** | **0** | Zero unaligned or ambiguous records promoted to canonical |
| **Polysemy Separations Preserved** | **15+** | `right` (3 senses), `bank`, `charge`, `interest`, `issue`, `order`, etc. |
| **Learning Classifications Attached**| **8,362** | CEFR, EIKEN, JLPT, Joyo, NGSL, VI Core, TOEIC, IELTS, TOEFL |
| **Upstream Raw Snapshots** | **11** | Verified immutable in `data/raw/` with SHA-256 sums |
| **Projected Learning Views** | **9** | Decks in `data/exports/` + `oki_language/deck_data.json` |
| **Legacy Production Baseline** | **800** | Byte-for-byte frozen in `data/production/vocabulary.jsonl` |
| **Pytest Test Suite** | **314 Passed** | 100% passing across legacy suite (292) + 1.3B (13) + 1.3C (9) |
| **AI Bulk Data Generation** | **0** | Zero hallucinated translations; strict upstream provenance |

---

## 3. Directory Layout

```
.
├── ARCHITECTURE.md                 # System architecture, Concept-Sense-Expression model
├── ATTRIBUTION.md                  # Legal citations for government & open-source licenses
├── CHANGELOG.md                    # Release log and change history
├── DATA_SCHEMA.md                  # Comprehensive JSON schema specifications
├── README.md                       # Project overview and reproduction guide
├── SOURCE_POLICY.md                # Source governance, license matrix & anti-scraping policy
├── VALIDATION.md                   # Independent validation engine specification & audit
├── config/
│   ├── license_policy.yaml         # Machine-readable license compatibility policy
│   ├── source_registry.yaml        # Machine-readable registry of external sources
│   └── domain_taxonomy.yaml        # 21 recognized professional and general domains
├── schemas/                        # JSON Schema draft 2020-12 canonical contracts
│   ├── concept.schema.json
│   ├── sense.schema.json
│   ├── expression.schema.json
│   ├── classification.schema.json
│   ├── example.schema.json
│   └── relationship.schema.json
├── data/
│   ├── canonical/                  # Canonical Tri-Language Learning Graph
│   │   ├── concepts.jsonl          # 812 concepts
│   │   ├── senses.jsonl            # 812 senses
│   │   ├── expressions.jsonl       # 2,436 expressions (en, ja, vi)
│   │   ├── classifications.jsonl   # 867 learning classifications
│   │   ├── examples.jsonl          # 1,612 pedagogical examples
│   │   └── legacy_mapping.json     # 800 jp-pro-* legacy mappings
│   ├── exports/                    # Projected learning views
│   │   ├── cross_language/         # en_ja_vi_core.jsonl, business_en_ja_vi.jsonl
│   │   ├── japanese/               # jlpt_n5.jsonl, joyo_kanji.jsonl
│   │   ├── english/                # ngsl_core.jsonl, cefr_b1.jsonl, toeic_essential.jsonl
│   │   └── vietnamese/             # vi_core_500.jsonl
│   ├── curated/phase1_3b/          # Curated foundation seed datasets with SHA-256 hashes
│   ├── production/                 # Frozen legacy Japanese professional production dataset (800)
│   └── releases/                   # Immutable frozen releases (v1.0.0, v1.1.0, v1.2.0-canary.1)
├── reports/phase1_3b/              # Phase 1.3B audit & closure reports
│   ├── repository_audit.md         # 1.3B.0 architecture & invariant audit
│   ├── tri_language_alignment_audit.md # Sense-level alignment report
│   └── phase_1_3b_closure.md       # Final closure metrics & verification
├── scripts/phase1_3b/              # Phase 1.3B core orchestration pipeline
│   ├── models.py                   # Canonical entity dataclasses & enums
│   ├── license_gate.py             # Machine-readable license compatibility gate
│   ├── legacy_bridge.py            # Backward-compatibility legacy projection
│   ├── alignment_engine.py         # Tri-language sense-level alignment engine
│   ├── view_exporter.py            # Learning view projection exporter
│   ├── run_phase1_3b.py            # Master orchestration runner
│   └── adapters/                   # Foundation source adapters (JMdict, Joyo, NGSL, VietCore)
└── tests/                          # Automated regression test suite (305 tests)
```

---

## 4. Pipeline Execution & Reproduction

To reproduce the Phase 1.3B Tri-Language Learning Graph and verify all invariants:

```bash
# 1. Activate environment
source .venv/bin/activate

# 2. Run Phase 1.3B orchestration pipeline
python scripts/phase1_3b/run_phase1_3b.py

# 3. Verify dataset invariants
python scripts/check_dataset_invariants.py

# 4. Run entire test suite (305 tests)
pytest tests/ -v
```

