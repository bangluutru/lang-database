# JP Professional Vocabulary Database (Phase 1.1A)

> **Authoritative, Structured Japanese Professional Vocabulary Knowledge Base for Next-Gen Language Learning & Multi-Modal Content Generation.**

Designed specifically as a machine-consumable **source-of-truth** to power:
- Audio vocabulary lessons & Shadowing practice
- Video generation (YouTube, YouTube Shorts, Subtitles)
- Adaptive quizzes, flashcards, and web/mobile apps

---

## 1. Architectural Highlights (Phase 1.1A Linguistic Remediation Closure)

- **Independent Linguistic Judge (`scripts/linguistic_validator.py`)**:
  - Eliminates builder self-certification. The generator marks candidates as `"status": "generated"`.
  - An independent two-pass linguistic judge (Critic & Resolver) evaluates collocation naturalness, semantic compatibility, workplace register, and cross-language translation contamination.
  - Deterministic SHA-256 validation caching in `data/validation_cache/`.
- **Strict Production Release Gate (`scripts/release_gate.py`)**:
  - Upgrades certified objects from `linguistically_validated` to `production_verified`.
  - **Zero-Generated Guarantee**: Strictly enforces that zero objects in production have status `generated`.
- **Traceable End-to-End Lineage & Structured Pronunciation Evidence**:
  - Every production entry traces back: `source_id -> source_record_id -> extracted_candidate_id -> normalized_candidate_id -> canonical_id -> enrichment_version -> validation_record -> release_version`.
  - Structured pronunciation evidence locators citing statutory / authoritative standard documents (ASBJ, NTA, Companies Act, IATA, Customs Act).
- **Fine-Grained Semantic Ontology (32 Classes)**:
  - Eliminates artificial template pairings (e.g. `ふるさと納税を提出する` -> `ふるさと納税を利用する`).
- **Engine-Independent TTS Phonetic Modeling**:
  - Separate modeling of `display_text`, `speech_text`, `preferred_reading`, `pronunciation_type`, and `pause_after_term_ms` (1200ms).
- **Decoupled JLPT vs. Professional Tiers**:
  - Removed artificial inference linking `PRO-A1/A2/A3` tiers to `N3/N2/N1`.

---

## 2. Dataset Overview (Phase 1.1A Closure)

| Metric | Value | Details |
|---|---|---|
| **Total Candidates Evaluated** | **800** | Pilot corpus preserved for validation (200/domain) |
| **Production Ready (PASS)** | **800** | Passed all independent linguistic & structural validation dimensions |
| **Review Queue (NEEDS REVIEW)** | **0** | All 11 previous quarantine items resolved upstream |
| **Rejected (FAIL)** | **0** | Upstream kana corruptions remediated in domain knowledge banks |
| **Collocations Audited & Certified** | **3,200** | 100% evaluated for semantic compatibility & naturalness |
| **Workplace Examples Certified** | **1,600** | 100% verified, clean English & Vietnamese |
| **Workplace Dialogue Turns Certified** | **1,600** | 100% natural conversational continuity |
| **Workplace Expressions** | **50** | Authentic idiomatic expressions (e.g., `請求書を切る`, `経費で落とす`) |
| **Active Relationship Graph Edges** | **2,078** | Synonyms, Antonyms, and Related linkages for released entries |
| **Draft Contamination** | **0%** | FSA 2027 draft taxonomy strictly quarantined in staging |
| **Pytest Test Suite** | **39 Passed** | 100% pass across schema, pipeline, independence, reproducibility, linguistic |


---

## 3. Directory Layout

```
.
├── ARCHITECTURE.md                 # Old vs. New architecture & pipeline design
├── ATTRIBUTION.md                  # Legal citations for government & association sources
├── CHANGELOG.md                    # Release log and change history
├── DATA_SCHEMA.md                  # Comprehensive JSON schema specifications
├── README.md                       # Project overview and reproduction guide
├── SOURCE_POLICY.md                # Traffic-light source classification & anti-scraping ethics
├── VALIDATION.md                   # Independent validation engine specification & audit
├── data/
│   ├── sources/
│   │   └── source_registry.yaml    # Machine-readable registry of external sources
│   ├── raw/
│   │   ├── fsa/edinet/2026/        # Untouched 2026 EDINET Excel files + SHA-256 metadata
│   │   ├── nta/                    # National Tax Agency glossaries and tax code indexes
│   │   ├── jicpa/                  # JICPA audit & accounting terminology index
│   │   └── jetro/                  # JETRO trade reference metadata
│   ├── extracted/                  # Layer B extracted candidate JSONL files (with candidate IDs)
│   ├── normalized/                 # Layer C normalized candidates (with norm IDs & lineage links)
│   ├── enriched/                   # Layer D enriched learning candidates (status: candidate)
│   ├── validated/                  # Layer E validated candidates (with validation_record)
│   └── production/                 # Layer F Production Releases (status: production)
│       ├── dataset_manifest.json   # Release manifest with checksums and metrics
│       ├── jp_professional_pilot.jsonl # 789 validated production entries
│       ├── vocabulary.jsonl        # 789 validated production entries
│       ├── expressions.jsonl       # 50 workplace idiomatic expressions
│       ├── relationships.jsonl     # 2,049 active relationship edges
│       └── jp_professional.db      # SQLite 3 database with FTS5 search & indexes
├── staging/
│   ├── fsa_edinet_2027_draft/      # Strict quarantine for 2027 draft taxonomy
│   └── review_queue/               # Quarantined candidates
│       ├── needs_review.jsonl      # 2 entries with multi-reading variance
│       └── rejected.jsonl          # 9 entries with corrupted readings
├── reports/
│   ├── source_ingestion/           # Excel inspection reports & summaries
│   ├── qa_report.json              # Full automated QA validation report
│   └── qa_summary.md               # Human-readable QA audit summary
├── scripts/
│   ├── download_sources.py         # Automated downloader with SHA-256 checksums
│   ├── inspect_excel.py            # OpenPyXL workbook inspector & structural reporter
│   ├── extract_fsa.py              # FSA candidate extractor (cand-fsa-*)
│   ├── extract_nta.py              # NTA candidate extractor (cand-nta-*)
│   ├── extract_jicpa_asbj.py       # JICPA/ASBJ candidate extractor
│   ├── extract_trade_business.py   # Trade & business candidate extractor
│   ├── normalize_terms.py          # NFKC normalizer & lineage assigner (norm-*)
│   ├── build_pilot_dataset.py      # Candidate builder (semantic collocations, TTS, lineage)
│   ├── validate_dataset.py         # Independent 8-stage validation pipeline
│   ├── release_gate.py             # Release gate routing to production vs. review queues
│   ├── export_sqlite.py            # SQLite exporter with FTS5 full-text index
│   └── pilot_builder/              # Semantic classes, TTS modeler, example generator
└── tests/
    ├── test_schema.py              # Schema conformity & lineage tests
    ├── test_pipeline.py            # Pipeline integration & SQLite query tests
    ├── test_validation_independence.py # Validation independence & constraints tests
    └── test_reproducibility.py     # Deterministic rebuild & checksum tests
```

---

## 4. Pipeline Execution & Reproduction

To reproduce the complete pipeline deterministically from scratch:

```bash
# 1. Activate environment
source .venv/bin/activate

# 2. Extract from raw sources to Layer B
python scripts/extract_fsa.py
python scripts/extract_nta.py
python scripts/extract_jicpa_asbj.py
python scripts/extract_trade_business.py

# 3. Normalize terms to Layer C
python scripts/normalize_terms.py

# 4. Enrich learning candidates to Layer D (data/enriched/)
python scripts/build_pilot_dataset.py

# 5. Run independent validation to Layer E (data/validated/)
python scripts/validate_dataset.py

# 6. Apply Release Gate to Layer F (data/production/ & staging/review_queue/)
python scripts/release_gate.py

# 7. Run full test suite
pytest tests/ -v
```
