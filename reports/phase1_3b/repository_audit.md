# Phase 1.3B Repository Audit: Architecture, Schemas, Invariants & Compatibility Roadmap

**Baseline Commit**: `074a2b0d6219dcfec7a6592cbb831bda0d96da3a`  
**Phase**: Phase 1.3B.0 — Repository Audit  
**Date**: October 2026  
**Repository**: `bangluutru/lang-database`

---

## 1. Executive Summary & Objective

The mission of Phase 1.3B is to evolve the existing Japanese Professional Vocabulary Database into a curated, open, machine-readable **English–Japanese–Vietnamese Learning Lexical Graph**. 

The fundamental architectural principle is:
> The database MUST NOT be modeled as `Japanese word → English translation → Vietnamese translation`, nor as three disconnected language databases. Rather, the canonical architecture centers on **language-independent Concepts**, resolved into **Senses**, lexicalized into **EN / JA / VI Expressions**, annotated with many-to-many **Learning Classifications**, contextualized in **Domains**, supported by **Examples**, interconnected by **Relationships**, and grounded by strict **Source & Value Provenance**.

Crucially, **no validated work from Phases 1.1–1.3 is to be destroyed**. The 800 production records, Golden Pilot v1/v1.1 releases, and Canary 1.2c remain immutable and preserved as a specialized professional view within the expanded tri-language graph.

This audit report inventories the entire existing system, catalogs all schemas and invariants, diagnoses hard-coded mono-language and AI assumptions, and establishes a safe backward-compatible migration plan.

---

## 2. Inventory of Current Schemas

### 2.1 Production Vocabulary Schema (`data/production/vocabulary.jsonl`)
- **Key Fields**:
  - `id`: Primary key matching `^jp-pro-[a-z_]+-[0-9]{6}$` (e.g. `jp-pro-accounting-000001`).
  - `term`: Japanese-specific object `{surface, reading, romaji, romaji_metadata: {scheme, generator: "pykakasi", generator_version}}`.
  - `language`: Fixed literal `"ja"`.
  - `domain`: Object `{primary, secondary: [], semantic_class}`.
  - `concept`: Object `{type: "compound_noun" | ..., canonical: boolean}`.
  - `meaning`: Multi-language dictionary `{vi: {short, preferred, explanation, professional_context}, en: {short, preferred, alternatives: []}}`.
  - `professional_level`: `{tier: "PRO-A1"|"PRO-A2"|"PRO-A3", description}`.
  - `general_japanese`: `{jlpt_level: null, jlpt_status: "not_mapped"}` (Strictly decoupled from unverified JLPT claims).
  - `frequency`: `{professional_priority}`.
  - `priority`: `{score, factors: {workplace_frequency, learner_usefulness, source_authority, cross_domain_value}}`.
  - `synonyms`, `antonyms`, `related_terms`: String arrays.
  - `collocations`, `examples`, `dialogue`: Curated linguistic frames with `register`, `status`, `generation_method`, and `validation_method`.
  - `sources`: Source lineage citation array.
  - `lineage`: Deep provenance trace down to raw extract candidate IDs and release versions.
  - `tts`: Audio synthesis metadata `{display_text, speech_text, preferred_reading, pronunciation_type, pause_after_term_ms}`.
  - `linguistic_validation`: Gemini validation evidence (`model: "gemini-3.8-flash"`, prompt version, SHA-256 input hash).
  - `status`: `"production"`.

### 2.2 Relational & Expression Schemas (`data/production/`)
- **`expressions.jsonl`**: Flat extraction of terms and their domain/collocation properties for rapid index lookups.
- **`relationships.jsonl`**: Explicit inter-term edges `{relation_id, source_id, source_term, target_id, target_term, relationship_type, bidirectional}`.

### 2.3 Phase 1.2B & 1.2C Canary Candidate Pool Schema (`staging/canary_candidate_pool.jsonl`, `data/releases/canary-1.2c/`)
- Candidate records with `candidate_id`, `surface`, `normalized_surface`, `reading`, `domain`, `subdomain`, `source_ids`, `authority_class`, `selection_rank`, and `status: "candidate"|"approved"`.

### 2.4 Phase 1.3A.1 Hardened Candidate Pool & Review Queue (`staging/candidate_pool_phase_1_3a.jsonl`, `staging/review_queue/`)
- **Pool Version**: `1.3.1` (4,104 records).
- **Field-Level Provenance**:
  - `term_provenance`: `OFFICIAL_EXTRACTED` | `OFFICIAL_CURATED` | `INTERNAL_CURATED` | `MODEL_ASSISTED`.
  - `reading_provenance`: `RULE_BASED` | `MODEL_ASSISTED`.
  - `gloss_provenance`: `OFFICIAL_EXTRACTED` | `OFFICIAL_CURATED` | `MODEL_ASSISTED`.
  - `domain_provenance`: `RULE_BASED`.
  - `evidence_refs`: Array of `{source_id, source_version, authority_class, provenance_type, source_locator, raw_snapshot_hash, curated_artifact_hash, source_url, reference_url, artifact_path}`.
- **Review Queue**: 1,104 records, strictly enforcing `human_decision == "PENDING"`.

---

## 3. Production Invariants & Immutability Guarantees

Machine-enforced by `scripts/check_dataset_invariants.py`:

| Invariant | Description | Current State |
| :--- | :--- | :--- |
| **INV-1** | Freeze equation: `800 = production (800) + review (0) + perm_q (0)` | **PASS** |
| **INV-2** | Zero generated status in production | **PASS** |
| **INV-3** | Model provenance integrity (Forbidden model IDs like `independent-linguistic-judge-2.0` blocked) | **PASS** |
| **INV-4** | Zero duplicate IDs in production | **PASS** |
| **INV-5** | Release versions match recognized production milestones (`v1.1.0a-prod` etc.) | **PASS** |
| **INV-6** | JLPT decoupled (Null/unmapped unless backed by verified consensus) | **PASS** |
| **INV-7** | Permanent quarantine metadata completeness | **PASS** |
| **INV-8** | Golden Pilot v1 hash immutability (`file: 1da7f6...`, `canonical: 27830f...`) | **PASS** |
| **INV-8 (v1.1)** | Golden Pilot v1.1 hash immutability (`file: 1e18d5...`, `canonical: 5ae36d...`) | **PASS** |
| **INV-9** | No accounting template injection in collocations | **PASS** |
| **INV-10** | Term reference in collocations/examples | **PASS** |
| **INV-11** | No governance predicate injection | **PASS** |

**Phase 1.3A.1 Provenance Invariants**:
- Zero fake raw snapshots in `data/raw/` (8 curated sources correctly relocated to `data/curated/phase1_3a/`).
- `metadata.json` for curated sources strictly uses `curated_at` and `reference_url` (never `downloaded_at`).
- Zero self-referential relationships (`source != target`).
- Deduplicated relationships by `(rel_type, src, tgt)`.
- Generic artifacts (`English`, `その他`, `お知らせ`, UI navigation) strictly rejected.
- `SAME_CONCEPT_CROSS_DOMAIN` vs `DIFFERENT_SENSE` policy enforced.

---

## 4. Test Suite Inventory

The repository currently contains **292 deterministic tests** across 12 test modules, all passing:
1. `tests/test_linguistic_validation.py` (28 tests)
2. `tests/test_phase1_1c.py` (58 tests)
3. `tests/test_phase1_2a.py` (12 tests)
4. `tests/test_phase1_2b.py` (28 tests)
5. `tests/test_phase1_2c.py` (96 tests)
6. `tests/test_phase1_3a.py` (26 tests)
7. `tests/test_phase1_3a_1.py` (19 tests)
8. `tests/test_pipeline.py` (5 tests)
9. `tests/test_reproducibility.py` (2 tests)
10. `tests/test_schema.py` (12 tests)
11. `tests/test_validation_independence.py` (6 tests)

*Regression Requirement*: All 292 existing tests must remain 100% green during and after Phase 1.3B migration.

---

## 5. Architectural Diagnostics: Hard-Coded Assumptions & Risks

### 5.1 Hard-Coded Japanese Assumptions
1. **Mono-Language Data Structures**:
   - `data/production/vocabulary.jsonl` assumes `language: "ja"` at root.
   - Core lexical attributes (`surface`, `reading`, `romaji`, `romaji_metadata`) are Japanese-specific.
   - English (`en`) and Vietnamese (`vi`) are relegated to subordinate fields within a nested `meaning` dictionary rather than first-class expressions.
2. **Reading Generation**:
   - `Phase13LinguisticEnhancer` relies directly on `pykakasi` to generate Hiragana/Katakana readings.
   - For English, phonetic transcription requires IPA.
   - For Vietnamese, phonetic information requires tone and regional pronunciation tags, plus Hán-Việt characters where applicable.
3. **Phonetic and Morphological Analysis**:
   - Tokenization heuristics in `normalizer.py` and `dedup_engine.py` use Unicode character blocks (`\u4e00-\u9faf`, Hiragana, Katakana, Full-width).
   - English requires standard Latin lemmatization and morphology.
   - Vietnamese requires compound word segmentation (e.g. `bảng cân đối kế toán` is 5 syllables forming 1 compound term).

### 5.2 Hard-Coded Gemini & Validation Assumptions
1. **Single LLM Validation Gate**:
   - `scripts/release_gate.py` and `scripts/llm_judge.py` expect Gemini validation receipts (`model: "gemini-3.8-flash"`) inside `linguistic_validation`.
   - In Phase 1.3B, structured source data (e.g., JMdict, NGSL, official Jōyō lists) is self-authenticating via source lineage and license verification. AI is only needed for cross-lingual sense alignment, example generation, or synthetic collocations.
2. **AI Provenance Tracking**:
   - Phase 1.3B strictly mandates that AI output is never source evidence, must carry `origin: "ai_generated"`, and must be quarantinable without affecting underlying lexical entries.

### 5.3 Identifier & Relational Assumptions
1. **Legacy ID Format**:
   - `jp-pro-[domain]-[000000]` is hard-coded into `tests/test_schema.py` and `scripts/check_dataset_invariants.py`.
   - *Mitigation*: Concept IDs in the new graph will use `concept-[uuid-or-slug]`, while Expression IDs will use `expr-[lang]-[hash-or-slug]`. A dedicated bidirectional mapping table will link `jp-pro-*` to `(concept_id, sense_id, expression_id)`.
2. **SQLite Schema**:
   - `scripts/export_sqlite.py` creates a flat `vocabulary` table with Japanese column names (`surface`, `reading`, `romaji`).
   - *Mitigation*: Extend the SQLite export architecture to support both the legacy `vocabulary` view (for backward compatibility) and the normalized relational graph (`concepts`, `senses`, `expressions`, `classifications`, `relationships`, `fts_expressions`).

---

## 6. Backward Compatibility & Migration Strategy

```
                                [ Canonical Learning Graph ]
                                             │
                     ┌───────────────────────┴───────────────────────┐
                     ▼                                               ▼
       [ Legacy Compatibility View ]                   [ New Tri-Language Views ]
                     │                                               │
    data/production/vocabulary.jsonl                 data/canonical/
    (800 records, JP-centric schema)                   concepts.jsonl
                     │                                 senses.jsonl
             SQLite Export                             expressions.jsonl
          (legacy vocabulary table)                    classifications.jsonl
                     │                                 examples.jsonl
             Golden Pilot v1 & v1.1                    relationships.jsonl
          (Immutable release hashes)                   provenance.jsonl
```

1. **Dual Storage Model**:
   - The frozen production release at `data/production/vocabulary.jsonl` will remain untouched, preserving all hashes and invariants checked by `check_dataset_invariants.py` and `test_schema.py`.
   - The canonical tri-language graph will reside in `data/canonical/`.
   - A deterministic forward-and-backward bridge script (`scripts/phase1_3b/legacy_bridge.py`) will project existing `jp-pro-*` records into canonical Concepts, Senses, and Expressions, producing `data/canonical/legacy_mapping.json`.
2. **Gradual Ingestion (Seed Pilots Only)**:
   - Phase 1.3B will NOT ingest hundreds of thousands of words.
   - It will establish the adapter architecture, license compliance engine, and seed pilots with 100–300 aligned concepts across EN, JA, and VI.

---

## 7. Audit Conclusion & Next Steps

The current repository is exceptionally well-structured, with robust SHA-256 provenance tracking, zero invariant violations, and 292 passing tests. 

We can proceed safely to **Subphase 1.3B.1: Schema Foundation & Data Models**.
