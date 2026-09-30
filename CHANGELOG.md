# Changelog

All notable changes to the **JP Professional Vocabulary Database** are documented here in accordance with [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) and Semantic Versioning.

---

## [v1.1-closure] - 2026-10-01

### Added
- **Independent Validation Architecture (Decoupled Responsibilities)**:
  - Eliminated circular validation where the builder previously assigned `"validated": true` and arbitrary confidence floats (`0.99`, `0.98`).
  - Implemented `scripts/validate_dataset.py` as an independent 8-stage validation engine evaluating evidence across schema, source lineage, reading, translation, collocations, examples, TTS, and draft contamination.
- **Traceable Data Lineage**:
  - Injected end-to-end lineage into every record: `source_id -> source_record_id -> extracted_candidate_id -> normalized_candidate_id -> canonical_id -> enrichment_version -> validation_record -> release_version`.
  - Distinguishes `origin_type`: `official_extracted` (637 terms) vs. `curated` (163 terms). Curated terms explicitly declare their curated origin and cite knowledge bank IDs.
- **4-Level Pronunciation Verification Hierarchy**:
  - Level 1: Authoritative acronym and symbol registry (`ACRONYM_SPEECH_MAP`).
  - Level 2: Janome IPAdic dictionary morphological cross-check and official industry-standard lexicon (`INDUSTRY_VERIFIED_LEXICON`).
  - Level 3: pykakasi algorithmic cross-check.
  - Level 4: Unverified / variant reading quarantine (`needs_review`).
- **Phonetic Anomaly Detection**:
  - Successfully surfaced and quarantined 9 genuine phonetic corruptions present in pilot source data: `その他有価証券評価差額金`, `ふるさと納税`, `事前確定届出給与`, `招集通知`, `航空貨物運送状`, `クリーンB/L`, `貨物受領証`, `他法令確認`, `ラッシング`.
- **Semantic Class Collocation System**:
  - Implemented `scripts/pilot_builder/semantic_classes.py` with 24 ontological semantic classes (e.g. `financial_statement`, `tax_deduction`, `shipping_document`, `trade_term`, `cargo_operation`, `person_role`, `organization`, `contract`, `metric`).
  - Replaced universal domain templates with natural, semantically constrained predicates.
- **Engine-Independent TTS Phonetic Modeling**:
  - Implemented `scripts/pilot_builder/tts_modeler.py` separating `display_text` from `speech_text` for 33 acronyms and mixed terms (e.g., `B/L` -> `ビーエル`, `FOB` -> `エフオービー`, `e-Tax` -> `イータックス`, `1株当たり当期純利益` -> `一株当たり当期純利益`).
  - Enforced slash character safety in TTS speech text.
- **Production Release Gate**:
  - Implemented `scripts/release_gate.py` routing 789 passed candidates to `data/production/vocabulary.jsonl` and quarantining 2 review candidates and 9 rejected candidates into `staging/review_queue/`.
- **Honest QA Reporting**:
  - Replaced superficial 100% QA claims with transparent metrics in `reports/qa_report.json` and `reports/qa_summary.md`.
- **Expanded Test Suite**:
  - Added `tests/test_validation_independence.py` and `tests/test_reproducibility.py`. Total test suite expanded to 24 tests, all passing.

### Changed
- **Decoupled JLPT Level**:
  - Removed artificial inference linking `PRO-A1/A2/A3` tiers to `N3/N2/N1`.
  - Set `general_japanese: { "jlpt_level": null, "jlpt_status": "not_mapped" }` across all records.
- **Workplace Examples & Dialogues**:
  - Implemented `scripts/pilot_builder/example_generator.py` producing authentic workplace context sentences and dialogues tailored to each semantic class.
- **SQLite Database**:
  - Rebuilt `data/production/jp_professional.db` with 789 validated production records and 2,049 active relationship graph edges.

### Deprecated / Removed
- Deprecated artificial static confidence floats (`confidence: { canonical_term: 1.0, reading: 0.99, ... }`).
- Deprecated builder self-certification (`provenance.validated: true` within candidate builder).
- Deprecated universal collocation templates.

---

## [v0.1-pilot] - 2026-10-01

### Added
- **4-Layer Data Architecture**: Fully established Layer A (Raw Sources), Layer B (Extracted Candidates), Layer C (Canonical Vocabulary), and Layer D (Enriched Learning Objects).
- **Source Governance & Traffic Light Registry**: FSA (`fsa_edinet_2026`), NTA (`nta_tax_glossary_2026`), JICPA, ASBJ, JETRO.
- **Automated Source Ingestion & Checksum**: Downloaded official 2026 EDINET workbooks (`1f_AccountList.xlsx`, etc.). Quarantined 2027 draft taxonomy.
- **Phase 1 Pilot Dataset (800 Canonical Entries)**: 200 Accounting, 200 Tax, 200 Business, 200 Trade.
- **Workplace Idiomatic Expressions Layer**: 50 authentic workplace expressions.
- **Semantic Relationship Graph**: 2,078 relational edges.
- **SQLite Engine & FTS5 Search**: Local SQLite query layer with FTS5 search.
