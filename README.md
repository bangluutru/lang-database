# JP Professional Vocabulary Database

> **Authoritative, Structured Japanese Professional Vocabulary Knowledge Base for Next-Gen Language Learning & Multi-Modal Content Generation.**

Designed specifically as a machine-consumable **source-of-truth** to power:
- Audio vocabulary lessons & Shadowing practice
- Video generation (YouTube, YouTube Shorts, Subtitles)
- Adaptive quizzes, flashcards, and web/mobile apps

---

## 1. Architectural Highlights

- **4-Layer Unidirectional Data Lifecycle**:
  - `Layer A (Raw Sources)`: Untouched official Excel/ZIP/HTML with SHA-256 integrity checks.
  - `Layer B (Extracted Candidates)`: Parsed concepts with source metadata preserved.
  - `Layer C (Canonical Vocabulary)`: NFKC-normalized, deduplicated terms with verified readings.
  - `Layer D (Learning Enrichment)`: Professional Vietnamese translations, English mappings, collocations, natural workplace examples, multi-speaker dialogues, PRO tiers (`PRO-A1`, `PRO-A2`, `PRO-A3`), priority scoring (0–100), and TTS metadata.
- **Strict Provenance & Zero Contamination**:
  - Official source facts (FSA/NTA/JICPA/JETRO) are strictly segregated from AI-generated learner definitions and explanations.
  - 2026 EDINET Final taxonomy is the production baseline. 2027 draft taxonomy is isolated in `staging/fsa_edinet_2027_draft/` marked `source_status: draft`.
- **TTS Engine Decoupling**:
  - The database is completely independent of Gemini TTS or any specific speech synthesis model. TTS is strictly a downstream consumer.
- **Dual-Storage Strategy**:
  - Master format in JSONL (`vocabulary.jsonl`, `expressions.jsonl`, `relationships.jsonl`).
  - High-performance SQLite database (`jp_professional.db`) with FTS5 Full-Text Search.

---

## 2. Dataset Overview (Phase 1 Pilot)

| Metric | Value | Details |
|---|---|---|
| **Total Canonical Entries** | **800** | Exactly 200 per domain across 4 core domains |
| **Accounting** | 200 | Financial statements, B/S, P/L, IFRS, depreciation, reserves |
| **Tax** | 200 | Income tax, Corporate tax (Schedule 4/5), Qualified invoice, Audits |
| **Business & Management** | 200 | Quotations, Contracts, Governance (Board, Ringisho), HR/Labor, Sales |
| **Trade & Logistics** | 200 | Incoterms 2020, B/L, Customs, Tariffs, Trade Finance, EPA/FTA |
| **Workplace Expressions** | **50** | Authentic idiomatic expressions (e.g., `請求書を切る`, `経費で落とす`) |
| **Relationship Graph Edges** | **2,078** | Synonyms, Antonyms, and Related concept linkages |
| **Automated QA Validation** | **100% Pass** | 800 / 800 entries validated against 15 strict schema checks |
| **Pytest Test Cases** | **15 Passed** | 100% test coverage for schema, SQLite, and pipeline |

---

## 3. Directory Layout

```
.
├── ARCHITECTURE.md                 # Detailed architectural blueprint & pipeline design
├── ATTRIBUTION.md                  # Legal citations for government & association sources
├── CHANGELOG.md                    # Release log and change history
├── DATA_SCHEMA.md                  # Comprehensive JSON schema specifications
├── README.md                       # Project overview and reproduction guide
├── SOURCE_POLICY.md                # Traffic-light source classification & anti-scraping ethics
├── data/
│   ├── sources/
│   │   └── source_registry.yaml    # Machine-readable registry of all external sources
│   ├── raw/
│   │   ├── fsa/edinet/2026/        # Untouched 2026 EDINET Excel files + SHA-256 metadata
│   │   ├── nta/                    # National Tax Agency glossaries and tax code indexes
│   │   ├── jicpa/                  # JICPA audit & accounting terminology index
│   │   └── jetro/                  # JETRO trade reference metadata
│   ├── extracted/                  # Layer B extracted candidate JSONL files
│   ├── normalized/                 # Layer C normalized candidate entries
│   └── production/                 # Layer D Production Master Files
│       ├── dataset_manifest.json   # Release manifest with checksums and metrics
│       ├── jp_professional_pilot.jsonl # 800 canonical pilot learning objects
│       ├── vocabulary.jsonl        # 800 canonical entries master
│       ├── expressions.jsonl       # 50 workplace idiomatic expressions
│       ├── relationships.jsonl     # 2,078 semantic relationship edges
│       └── jp_professional.db      # SQLite 3 database with FTS5 search & indexes
├── staging/
│   └── fsa_edinet_2027_draft/      # Strict quarantine for 2027 draft taxonomy
├── reports/
│   ├── source_ingestion/           # Excel inspection reports & summaries
│   ├── qa_report.json              # Full automated QA validation report
│   └── qa_summary.md               # Human-readable QA audit summary
├── scripts/
│   ├── download_sources.py         # Automated downloader with SHA-256 checksums
│   ├── inspect_excel.py            # OpenPyXL workbook inspector & structural reporter
│   ├── extract_fsa.py              # FSA candidate extractor
│   ├── extract_nta.py              # NTA candidate extractor
│   ├── extract_jicpa_asbj.py       # JICPA/ASBJ candidate extractor
│   ├── extract_trade_business.py   # Trade & business candidate extractor
│   ├── normalize_terms.py          # NFKC normalizer & deduplicator
│   ├── build_pilot_dataset.py      # Master compiler for 800 pilot entries & graph
│   ├── validate_dataset.py         # Automated 15-rule QA pipeline
│   ├── export_sqlite.py            # SQLite exporter with FTS5 full-text index
│   └── pilot_builder/              # Domain-specific authoritative knowledge banks
└── tests/
    ├── test_schema.py              # Schema conformity & linguistic integrity tests
    └── test_pipeline.py            # Pipeline integration & SQLite query tests
```

---

## 4. Source Governance & Traffic Light Policy

| Source ID | Organization | Tier | Policy | Usage Scope |
|---|---|---|---|---|
| `fsa_edinet_2026` | Financial Services Agency (FSA) | Tier 1 | **GREEN** (PDL-1.0) | Primary accounting taxonomy, full transformation allowed |
| `nta_tax_glossary_2026`| National Tax Agency (NTA) | Tier 1 | **GREEN** (PDL-1.0) | Primary tax terminology, full transformation allowed |
| `jicpa_glossary` | JICPA (公認会計士協会) | Tier 2 | **YELLOW** (Reference) | Terminology discovery & conceptual cross-check |
| `asbj_standards` | ASBJ (企業会計基準委員会) | Tier 2 | **YELLOW** (Reference) | Accounting standards terminology discovery |
| `jetro_trade` | JETRO (日本貿易振興機構) | Tier 2 | **YELLOW** (Reference) | Trade & customs terminology discovery only |

---

## 5. Downstream Consumer Query Examples

### Query: "Give me 30 PRO-A1 accounting terms for Vietnamese learners"
```sql
SELECT id, surface, reading, vi_short, en_preferred, priority_score
FROM vocabulary
WHERE domain = 'accounting' AND tier = 'PRO-A1'
ORDER BY priority_score DESC
LIMIT 30;
```

### Full-Text Search across Japanese, Readings, and Vietnamese
```sql
SELECT v.id, v.surface, v.reading, v.vi_short
FROM vocabulary_fts f
JOIN vocabulary v ON f.id = v.id
WHERE vocabulary_fts MATCH 'báo cáo tài chính'
LIMIT 10;
```

---

## 6. How to Reproduce & Run Tests

```bash
# 1. Activate Python virtual environment
source .venv/bin/activate

# 2. Run automated source downloads and Excel inspection
python scripts/download_sources.py
python scripts/inspect_excel.py

# 3. Compile Master Pilot Dataset (800 entries + expressions + graph)
python scripts/build_pilot_dataset.py

# 4. Run Automated QA Validation Pipeline
python scripts/validate_dataset.py

# 5. Export SQLite Database with FTS5
python scripts/export_sqlite.py

# 6. Run Full Pytest Test Suite
pytest tests/ -v
```
