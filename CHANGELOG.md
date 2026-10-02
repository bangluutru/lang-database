# Changelog

## [Phase 1.4] - 2026-10-02 — Curated corpus expansion (2,106 → 6,935 concepts)

### Added
- Wiktionary (EN edition, CC-BY-SA-4.0) snapshot `data/raw/wiktionary_en/2026-09-28` (filtered extract + full-upstream SHA-256).
- `scripts/phase1_4/`: sense-level candidate builder, JMdict corroboration, learning-value scoring, match-before-create,
  blind pairwise judge, append-only deterministic promotion, views/Oki exporters, reports.
- 4,829 new concepts (`concept-lex-*`): 2,514 tri-language (source-derived VI), 2,315 judge-validated EN–JA partials.
- `data/exports/views_v1_4/` learning views (JLPT, Jōyō, CEFR, NGSL/spoken/academic, exam relevance, VI Core, VI-first lexicon, 12 domains).
- **Project rule: no external/paid API calls** — `CLAUDE.md`, `AGENTS.md`, `scripts/external_api_guard.py`, `tests/test_external_api_policy.py`.
- Sealed-baseline manifest `data/releases/phase1_3d-sealed/` + prefix-hash tests.

### Changed / Fixed
- Canonical JSONL files are append-only; 1.3D hard-coded count tests converted to baseline-subset invariants; 3 tests already failing at the sealed commit fixed.
- JMdict POS: `vi`/`vt` no longer treated as verb markers. ATTRIBUTION: JLPT licence corrected to CC-BY-3.0.
- Additive classification backfill (991 rows) for sealed concepts (NGSL-Spoken / NAWL / BSL / VI core); no sealed record modified.

### Known issues
- Sealed baseline spot audit: 49% strict-accept on 150 sampled core concepts (see `reports/phase1_4/baseline_defect_audit.json`); remediation deferred.


All notable changes to the **English–Japanese–Vietnamese Learning Lexical Graph** are documented here in accordance with [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) and Semantic Versioning.

---

## [v1.3c-expansion] - 2026-10-01

### Phase 1.3C — Authoritative Source Acquisition & Curated Corpus Expansion

#### Added
- **Authoritative Downloader & Immutable Snapshot Framework (`scripts/acquire_sources.py`)**:
  - Implemented manifest-driven acquisition supporting `--source`, `--all-approved`, `--dry-run`, `--verify-only`, `--force-refresh`.
  - Acquired and verified 11 immutable upstream raw source snapshots in `data/raw/` with cryptographic `metadata.json` and `SHA256SUMS`:
    `kanjidic2`, `joyo`, `jmdict`, `ngsl`, `ngsl_spoken`, `nawl`, `bsl`, `tsl`, `vn_freq`, `unihan`, `jlpt_consensus`.
- **Production Extraction Adapters (`scripts/phase1_3c/adapters/production_adapters.py`)**:
  - Built streaming, memory-efficient parsers for XML, CSV, TSV, and ZIP archives.
  - Implemented Unihan variant inheritance allowing Japanese shinjitai kanji to inherit Sino-Vietnamese readings from traditional variants.
  - Value-level provenance tracking anchoring every extracted field to exact line/byte/entry locators.
- **Strict Provenance Guard & Special Negative Test (`scripts/phase1_3c/provenance_guard.py` & `tests/test_phase1_3c.py`)**:
  - Audited seed fixtures and corrected all Phase 1.3B seed adapters to `origin="seed_curated"`.
  - Enforced Section 26 Negative Test: unbacked local curated values claiming `SOURCE_DERIVED` fail provenance verification and enter quarantine.
- **Tri-Language Canonical Learning Expansion (`scripts/phase1_3c/aligner_and_expander.py`)**:
  - Scaled the canonical learning graph to **2,106 high-value concepts** and **6,318 expressions** (2,106 EN, 2,106 JA, 2,106 VI).
  - 100% complete tri-language coverage; zero partial or unaligned concepts in canonical production.
  - Preserved existing 800 professional legal/financial concepts and their `legacy_mapping.json` completely untouched.
- **Sense-Correct Polysemy Disambiguation**:
  - Enforced strict sense boundaries for polysemous words (`right`, `bank`, `charge`, `interest`, `capital`, `issue`, `order`, etc.).
  - Guaranteed `right` retains exactly 3 distinct concepts (`right_correct`, `right_direction`, `right_entitlement`) without generic collisions.
- **Downstream Oki-Language Export Adapter (`scripts/phase1_3c/export_oki_language.py`)**:
  - Generated `data/exports/oki_language/deck_data.json` containing 2,106 cards formatted for the oki-language learning web app.
- **Source License Matrix & Redistribution Audit Reports (`reports/licenses/`)**:
  - Documented share-alike boundaries under CC-BY-SA 3.0 for Japanese dictionary data and modular multi-licensing strategy.
- **Phase 1.3C Test Suite (`tests/test_phase1_3c.py`)**:
  - 9 automated tests passing 100% (total 314 tests in repository passing).

---

## [v1.3b-foundation] - 2026-10-01

### Phase 1.3B — Tri-Language Learning Graph & Open Source Ingestion Foundation

#### Added
- **Tri-Language Canonical Graph Schemas (`schemas/` & `scripts/phase1_3b/models.py`)**:
  - `Concept`: Language-independent semantic anchor.
  - `Sense`: Distinct meaning level with individual POS, register, glosses, and definition.
  - `Expression`: Language-specific lexical realization for English, Japanese, and Vietnamese.
  - `Classification`: Many-to-many learning classifications attached to Concepts/Senses/Expressions.
  - `Relationship`: Directed semantic and morphological edges including `SINO_COGNATE_OF`.
  - `Example`: Pedagogical sentence examples with multi-language translation linkages.
  - `SourceEvidence`: Value-level provenance tracking upstream source, locator, and license.
  - `TriLanguageCoverage`: Deterministic coverage tracking at concept/sense level.
- **Machine-Readable License Gate (`config/license_policy.yaml` & `scripts/phase1_3b/license_gate.py`)**:
  - Automatic approval for permissive/share-alike open licenses (`CC0-1.0`, `CC-BY-4.0`, `CC-BY-SA-4.0`, `PDL-1.0`, `MIT`).
  - Automatic quarantine for non-redistributable or proprietary licenses (`CC-BY-NC-4.0`, `CC-BY-ND-4.0`, `PROPRIETARY`, `UNKNOWN`).
- **Foundation Source Adapters (`scripts/phase1_3b/adapters/`)**:
  - `BaseSourceAdapter`: Common abstract adapter contract enforcing SHA-256 checks, license gating, and idempotent extraction.
  - `JMdictSeedAdapter`: Japanese core lexical foundation under CC-BY-SA-4.0.
  - `JoyoKanjiAdapter`: Official Agency for Cultural Affairs Jōyō Kanji grades under PDL-1.0.
  - `NGSLSeedAdapter`: New General Service List (NGSL v1.2) English core lemmas under CC-BY-SA-4.0.
  - `VietnameseCoreAdapter`: Vietnamese core vocabulary & verified Hán-Việt cognates under CC-BY-4.0.
- **Sense-Level Tri-Language Alignment Engine (`scripts/phase1_3b/alignment_engine.py`)**:
  - Evaluates cross-language equivalence across EN ↔ JA ↔ VI at sense level.
  - Enforces polysemy separation (e.g. `right` cleanly divided across `right_correct`, `right_direction`, `right_entitlement`).
  - Audits POS agreement, domain consistency, and Hán-Việt cognate linkages.
- **Legacy Backward Compatibility Bridge (`scripts/phase1_3b/legacy_bridge.py`)**:
  - Projects all 800 legacy `jp-pro-*` records into canonical `Concept`, `Sense`, `Expression`, and `Classification` records.
  - Generates machine-readable `data/canonical/legacy_mapping.json` maintaining 100% bi-directional mapping.
  - Strictly preserves frozen Golden Pilot releases (v1 & v1.1), Canary 1.2c, and production vocabulary.
- **Projected Learning Views (`data/exports/` & `scripts/phase1_3b/view_exporter.py`)**:
  - Generated dynamically without duplicating canonical lexical records:
    - `cross_language/en_ja_vi_core.jsonl` (812 records)
    - `cross_language/business_en_ja_vi.jsonl` (408 records)
    - `japanese/jlpt_n5.jsonl` (3 records)
    - `japanese/joyo_kanji.jsonl` (4 records)
    - `english/ngsl_core.jsonl` (9 records)
    - `english/cefr_b1.jsonl` (5 records)
    - `english/toeic_essential.jsonl` (6 records)
    - `vietnamese/vi_core_500.jsonl` (6 records)
- **Phase 1.3B Automated Test Suite (`tests/test_phase1_3b.py`)**:
  - 13 comprehensive unit and regression tests covering all 15 core invariants from Section 25.

---

## [v1.1c-closure] - 2026-10-01


### Phase 1.1C — Quarantine Remediation & Pilot Freeze

#### Added
- **Phase 1.1C Remediation Pipeline (`scripts/run_phase1_1c.py`)**:
  - Root-cause diagnosis for all 28 quarantined records: systemic failure classification
    (`EXAMPLE_DOES_NOT_CONTAIN_TERM`, `DOMAIN_FACTUAL_ERROR`, `COLLOCATION_ERROR`,
    `TECHNICAL_VALIDATION_FAILURE`).
  - Two-pass remediation (critic → resolver → resolver_v2 if needed → rejudge → adversarial audit)
    applied to every recoverable record.
  - Recovery rate tracked and reported; each recovered record must independently pass
    critic + blind rejudge + adversarial audit before promotion.
- **Machine-Enforced Dataset Invariants (`scripts/check_dataset_invariants.py`)**:
  - 11 permanent invariants: pilot freeze equation, zero-generated, model provenance,
    no duplicates, release versions, JLPT decoupled, quarantine metadata,
    no accounting template injection, term reference, no governance predicates.
- **Golden Pilot v1 Freeze (`data/releases/golden-pilot-v1/`)**:
  - Immutable regression baseline: `vocabulary.jsonl`, `dataset_manifest.json`,
    `validation_manifest.json`, `checksums.sha256`.
  - Canonical SHA-256 (sort-by-ID, exclude mutable fields) recorded in manifest.
  - File SHA-256 of `vocabulary.jsonl` cross-verified against manifest.
  - Immutability policy: corrections produce golden-pilot-v1.1 or v2, never overwrite.
- **Model Policy Config (`config/linguistic_validation.yaml`)**:
  - Declarative model/prompt_version/schema_version per validation stage.
  - Cache key must include model + prompt_version + schema_version (enforced in tests).
- **Phase 1.1C Test Suite (`tests/test_phase1_1c.py`)**:
  - 7 test classes: quarantine reconciliation, model provenance, cache identity,
    golden pilot immutability, dataset hashing, known-bad regression fixtures,
    reproducibility.
  - Permanent regression fixtures for all systemic bugs discovered in 1.1A/1.1B/1.1C.
- **CI/CD Guard (`.github/workflows/golden_pilot_guard.yml`)**:
  - Invariant checks + regression tests + Golden Pilot hash verification on every push.

#### Changed
- Production release version extended to `v1.1.0c-prod` for recovered quarantine records.
- `test_schema.py`: accepts `v1.1.0c-prod` and `generation_method=remediated_phase_1_1c`.
- `test_pipeline.py`: tests that `rejected.jsonl` contains only `permanent_quarantine` records.
- Pilot freeze equation: 800 = production + needs_review + permanent_quarantine enforced.

#### Fixed
- **Systemic: Wrong template injection** — 15 business/trade records had accounting ledger
  examples or corporate governance collocations applied via fallback templates.
  Remediated: new examples explicitly use the target term in domain-appropriate sentences.
- **Systemic: Organization predicate mismatch** — `organization` semantic class defaulted
  to governance predicates (決議する, 招集する) for non-governance entities.

---

## [v1.1a-closure] - 2026-10-01


### Added
- **Independent Linguistic Judge (`scripts/linguistic_validator.py`)**:
  - Implemented two-pass evaluation (Pass A: Critic, Pass B: Resolver) assessing collocation naturalness, semantic compatibility, professional domain correctness, workplace register, and cross-language contamination.
  - Implemented SHA-256 deterministic validation caching in `data/validation_cache/` to ensure full reproducibility and avoid redundant LLM/heuristic evaluations.
  - Standalone regression test suite `tests/test_linguistic_validation.py` verifying naturalness pass/fail suites, mixed language detection, and production status conformance.
- **Production Verification Rule**:
  - Release Gate strictly promotes objects from `linguistically_validated` to `production_verified`.
  - Enforced constraint: production vocabulary dataset contains strictly **ZERO** learning objects with status `generated`.
- **Structured Pronunciation Evidence Locators**:
  - Upgraded verified lexicon and candidate lineage to include structured evidence objects (`source_id`, `source_type`, `source_reference`, `retrieved_at`).
  - Added official statutory evidence locator for `雑損控除` (`ざっそんこうじょ`, Income Tax Act Art. 72).
- **Stratified Spot-Check Sample**:
  - Generated `reports/manual_spot_check_sample.jsonl` with 36 deterministically sampled records across 4 domains and 3 PRO tiers for human reviewer spot-checks.

### Changed
- **Remediated All 11 Quarantined Records Upstream**:
  - Fixed 10 typographical/phonetic corruptions directly in domain knowledge banks: `その他有価証券評価差額金`, `ふるさと納税`, `事前確定届出給与`, `白色申告`, `招集通知`, `航空貨物運送状`, `クリーンB/L`, `貨物受領証`, `他法令確認`, `ラッシング`.
  - Added industry verified lexicon entry for `雑損控除` with NTA statutory evidence.
  - Production released records increased from 789 to **800** (100% of candidate corpus released to production).
- **Eliminated False "Verified" Semantics in Builders**:
  - Replaced builder-assigned `"status": "verified"` and `"validation_method": "semantic_frame_verified"` with honest candidate representation: `"status": "generated"`, `"generation_method": "semantic_frame"`.
- **Eliminated Cross-Language Translation Contamination (800 Records)**:
  - Fixed English translation template interpolation bug in `example_generator.py` where Vietnamese text leaked into English strings (`"completed {vi_short} procedures..."` -> `"completed {en_clean} procedures..."`).
- **Refined Semantic Class Ontology (32 Classes)**:
  - Expanded `semantic_classes.py` from coarse fallbacks to 32 fine-grained domain-specific classes (`tax_scheme`, `executive_compensation`, `equity_valuation_account`, `tangible_fixed_asset`, `depreciable_asset`, `allowance_provision`, `retained_earnings`, `customs_procedure`, `transport_operation`, `legal_instrument`, `tax_deduction`, `incoterms_rule`, etc.).
  - Remediated 1,124 collocations with domain-appropriate natural predicates.
- **Updated Test Suite**:
  - Test suite expanded to 39 passing tests (including 15 new linguistic regression tests).

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
