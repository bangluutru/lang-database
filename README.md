# English–Japanese–Vietnamese Learning Lexical Graph (Phase 1.3B)

> **Curated, open, machine-readable English–Japanese–Vietnamese Learning Lexical Graph built on a canonical `Concept` → `Sense` → `Expression` tri-language architecture.**

Designed specifically as a pedagogical **source-of-truth** to support:
- Vietnamese users learning Japanese and English
- Japanese users learning English and Vietnamese
- International users utilizing English as a bridge to Japanese and Vietnamese
- Audio vocabulary shadowing, multi-modal video lesson rendering, and adaptive spaced-repetition engines

---

## 1. Architectural Evolution (Phase 1.3B Tri-Language Graph)

- **Semantic Separation: Concept vs. Sense vs. Expression**:
  - `Concept`: Language-independent semantic identity (e.g. `concept-000101`). Never uses raw English strings as IDs.
  - `Sense`: Distinct semantic meaning with individual POS, register, and glosses (`sense-000101-01`). Polysemous words (e.g. `right`) are never collapsed.
  - `Expression`: Language-specific lexical realization (`en`, `ja`, `vi`). Language-specific phonetic and morphological fields (JA: reading, kanji; VI: Hán-Việt cognates; EN: IPA).
- **Many-to-Many Learning Classifications**:
  - Classifications attach to Concepts, Senses, or Expressions without duplicating lexical records.
  - Dimensions: Japanese (Jōyō Kanji, JLPT, JP Frequency, JP Core), English (CEFR, NGSL, TOEIC, EIKEN, IELTS, TOEFL), Vietnamese (VI Core 500/1000/2000/5000, VI Frequency), Professional Tiers.
  - Classification provenance is explicit: `official`, `source_derived`, `corpus_derived`, `community_consensus`, `inferred`, `ai_proposed`.
- **Machine-Readable License Gate (`config/license_policy.yaml`)**:
  - Enforces redistribution and commercial-use compatibility (`CC0-1.0`, `CC-BY-4.0`, `CC-BY-SA-4.0`, `PDL-1.0`, `MIT`).
  - Automatically quarantines `CC-BY-NC-4.0`, `CC-BY-ND-4.0`, `PROPRIETARY`, and `UNKNOWN` sources.
- **Independent AI Provenance Guarantee**:
  - AI outputs carry `origin = ai_generated`, `model`, `generation_version`, `input_hash`, `generated_at`, `review_status = pending`.
  - AI proposals never masquerade as source-derived truth.
- **Backward Compatibility & Legacy Bridge**:
  - All 800 legacy `jp-pro-*` records are projected into canonical entities.
  - Machine-readable `legacy_mapping.json` maintains exact forward and reverse traceability.
  - Frozen release records (`data/production/vocabulary.jsonl`, Golden Pilot v1 & v1.1, Canary 1.2c) remain 100% immutable.
- **Projected Learning Views (`data/exports/`)**:
  - Cross-language: `en_ja_vi_core.jsonl`, `business_en_ja_vi.jsonl`
  - Language-specific: `japanese/jlpt_n5.jsonl`, `japanese/joyo_kanji.jsonl`, `english/ngsl_core.jsonl`, `english/cefr_b1.jsonl`, `english/toeic_essential.jsonl`, `vietnamese/vi_core_500.jsonl`.


---

## 2. Canonical Graph Metrics (Phase 1.3B Foundation)

| Metric | Value | Details |
|---|---|---|
| **Total Canonical Concepts** | **812** | 800 legacy projected + 12 foundation seed concepts |
| **Total Canonical Senses** | **812** | Sense-level definitions with POS, register, and glosses |
| **Total Lexical Expressions** | **2,436** | 812 English + 812 Japanese + 812 Vietnamese |
| **Tri-Language Complete Concepts** | **812** | 100% complete EN ↔ JA ↔ VI coverage across canonical concepts |
| **Ambiguous Alignments** | **0** | Zero unverified sense collisions |
| **Polysemy Separations Preserved** | **13** | E.g. `right` split across correct, direction, and entitlement |
| **Hán-Việt Verified Cognates** | **11** | Sino-Vietnamese ↔ Sino-Japanese validated linkages |
| **Learning Classifications Attached**| **867** | Attached many-to-many without duplicating lexical entries |
| **Pedagogical Examples Attached** | **1,612** | Curated workplace & learning context examples |
| **Projected Learning Views** | **8** | Decks generated dynamically into `data/exports/` |
| **Legacy Production Baseline** | **800** | Byte-for-byte frozen in `data/production/vocabulary.jsonl` |
| **Pytest Test Suite** | **305 Passed** | 100% passing across legacy suite (292) + Phase 1.3B (13) |

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

