# Phase 1.3C Expansion Summary Report

**Date**: 2026-10-01  
**Status**: COMPLETED (Remediated)  
**Baseline**: `87536eb`  
**Pipeline Verification**: 100% Deterministic & Offline Rebuildable  

---

## 1. Overview & Objectives Achieved

In Phase 1.3C, the seed-only ingestion mechanism from Phase 1.3B was replaced with a fully reproducible, manifest-driven acquisition engine from **11 authentic upstream datasets**, followed by honest provenance remediation.

### Core Achievements:
1. **Immutable Upstream Snapshots (`data/raw/`)**:
   - Acquired and verified 11 immutable upstream source snapshots with cryptographic SHA-256 sums and `metadata.json`.
2. **Jōyō Provenance Remediation (Blocker 1 Remediated)**:
   - Honestly represented Jōyō kanji provenance:
     - `source`: `KANJIDIC2 / EDRDG`
     - `origin`: `SOURCE_DERIVED`
     - `license`: `CC-BY-SA-3.0` (actual EDRDG license, eliminating contradictory PDL-1.0/statutory claims)
     - `authority_reference`: `文化庁 / 2010 Jōyō Kanji Cabinet Notification` (reference only)
     - `authority_level`: `source_derived`
3. **Tri-Language Pipeline Architecture Enforced (Blocker 2 Remediated)**:
   - Removed the false invariant of perfect 2,106 tri-language completeness.
   - Enforced the architectural progression: `REFERENCE UNIVERSE -> LEARNING CANDIDATES -> VALIDATED TRI-LANGUAGE CORE`.
   - Complete tri-language status is a computed metric:
     - **1,072 Complete Tri-Language Concepts** (800 professional + 21 polysemy benchmark + 6 core seeds + 245 curated daily lexicon).
     - **1,034 Partial Concepts** (`EN + JA` only; zero fabricated Vietnamese translations).
     - **1,034 Ambiguous Alignments** preserved in `reports/phase1_3c/ambiguous_alignments.json` and `reports/phase1_3c/review_queue.json` for human editorial verification.
     - **0 Unresolved Concepts**.
4. **Honest Provenance Reclassification**:
   - Polysemy benchmark expressions and classifications reclassified as `BENCHMARK_CURATED`.
   - Manually mapped CEFR and EIKEN grades reclassified as `INFERRED`.
   - Verified daily Vietnamese lexicon marked as `CURATED`.
   - Upstream extracted lexical data verified as `SOURCE_DERIVED`.
5. **Preservation of Professional Core**:
   - All 800 professional legal/financial concepts and `legacy_mapping.json` remain 100% frozen, intact, and tri-language complete.
6. **Oki-Language Compatibility**:
   - Exported 2,106 deck cards to `data/exports/oki_language/deck_data.json` with dynamic tri-language completeness computation.
7. **Zero AI Bulk Hallucination**:
   - 0 AI-generated fields, 0 unbacked assertions.

---

## 2. Canonical Graph & Provenance Metrics

| Metric | Count | Notes |
|:---|:---:|:---|
| **Total Canonical Concepts** | 2,106 | 800 professional + 21 polysemy + 1,285 core |
| **Total Canonical Senses** | 2,106 | 1-to-1 canonical sense mapping |
| **Total Canonical Expressions** | 5,284 | 2,106 EN + 2,106 JA + 1,072 VI |
| **Complete Tri-Language Concepts** | 1,072 | Validated core (EN + JA + VI) |
| **Partial Concepts** | 1,034 | Learning candidates (`EN + JA` only) |
| **Ambiguous Candidate Alignments** | 1,034 | Tracked in review queue for editorial action |
| **Unresolved Concepts** | 0 | Explicitly resolved or queued |
| **SOURCE_DERIVED Fields** | 6,384 | 2,570 expressions + 3,814 classifications |
| **OFFICIAL_EXTRACTED Fields** | 1,667 | 800 JA expressions + 867 pro classifications |
| **OFFICIAL_CURATED Fields** | 1,600 | 800 EN + 800 VI professional expressions |
| **INFERRED Fields** | 2,629 | CEFR and EIKEN mapped classifications |
| **CURATED Fields** | 251 | Verified daily core Vietnamese expressions |
| **BENCHMARK_CURATED Fields** | 81 | 63 expressions + 18 classifications |
| **AI_GENERATED Fields** | 0 | Zero AI bulk filling |

---

## 3. Source Inventory & Cryptographic Hashes

| Source ID | Version | License | Artifact Filename | Artifact SHA-256 | Provenance Model |
|:---|:---|:---|:---|:---|:---|
| `kanjidic2` | 2026-10-01 | CC-BY-SA-3.0 | `kanjidic2.xml.gz` | `1c60c9453e1c7a318f3492fd8e13ea792d20130402bcbce9ed84e6165dfa1d60` | EDRDG Upstream |
| `joyo` | 2010-official | CC-BY-SA-3.0 | `joyo_kanji_official.json` | `f5f0cf7d03f3a7beddab973d6b1d31eb3cb30a2b0285639ba8f4042fd94e01f1` | KANJIDIC2 / EDRDG derived (`source_derived`) |
| `jmdict` | 2026-10-01 | CC-BY-SA-3.0 | `JMdict_e.gz` | `89777236dbf06f4d7b01c6dbff5e1f707978ddd067061b66bcb782d1f24e6ed3` | EDRDG Upstream |
| `ngsl` | 1.2 | CC-BY-4.0 | `NGSL_12_stats.csv` | `2098bab8955a120a9766c6282a51d7d578c6cb0a7d946600d2ffb73ba25a0b44` | Browne et al. Upstream |
| `ngsl_spoken` | 1.2 | CC-BY-4.0 | `NGSL-Spoken_12_stats.csv` | `07708940c50a07cac4f507fd1e87bdd50081d7b87713a66a99beb3c8c4d11ac8` | Browne et al. Upstream |
| `nawl` | 1.2 | CC-BY-4.0 | `NAWL_12_lemmatized_for_teaching.csv` | `1790b0fa22c5815ebf5a9a15c9363c03a6e906c77bf217f99033734f1459137b` | Browne et al. Upstream |
| `bsl` | 1.2 | CC-BY-4.0 | `BSL_120_stats.csv` | `45055265eb4e74c65f5d26edabbc1a0da38c45bbb924cd9bd01fd391b74ff157` | Browne et al. Upstream |
| `tsl` | 1.2 | CC-BY-4.0 | `TSL_12_stats.csv` | `2259df25a1077b04067ef0c0e9e4c98b46c91e4d539741dfaceba88651ff486d` | Browne et al. Upstream |
| `vn_freq` | 1.0 | MIT | `vn_word_frequencies.tsv` | `8f644d06173600f8acb0d2b1a9dd0111c53ef304b9974b76e2cb24bad81fe04d` | Vu et al. Upstream |
| `unihan` | 16.0.0 | Unicode-DFS-2016 | `Unihan.zip` | `4c93ea9c1f636451729a840978f1667a53886af37ba854fdcce109721c63d43e` | Unicode Consortium |
| `jlpt_consensus` | 2026-v1 | CC-BY-3.0 | `JLPT_vocab_ALL.csv` | `810c776c7a72fe9a6860d8629e7f4d3903545808e6cbcff8dde3b52b01800f24` | Jonathan Waller / Tanos |

---

## 4. Test Suite & Validation Invariants

- **Full Pytest Suite**: 394 passed in 8.55s (100% green).
- **Golden Pilot Invariants**: INV-8 and INV-8 (v1.1) pass.
- **Production Invariants**: INV-1 through INV-11 pass (zero violations).
- **Blocker Verification Tests**: `tests/test_remediation_blockers.py` (10/10 passed).
