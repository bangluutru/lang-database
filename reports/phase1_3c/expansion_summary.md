# Phase 1.3C Expansion Summary Report

**Date**: 2026-10-01  
**Status**: COMPLETED  
**Baseline**: `691b3fd7cb352f244bb8584c1abcc6a061b9a13a`  
**Pipeline Verification**: 100% Deterministic & Offline Rebuildable  

---

## 1. Overview & Objectives Achieved

In Phase 1.3C, the seed-only ingestion mechanism from Phase 1.3B was replaced with a fully reproducible, manifest-driven acquisition engine from **11 authentic upstream datasets**.

### Core Achievements:
1. **Immutable Upstream Snapshots (`data/raw/`)**:
   - Acquired and verified 11 immutable upstream source snapshots with cryptographic SHA-256 sums and `metadata.json`.
2. **Provenance Hardening**:
   - Seed fixtures were audited and marked `origin="seed_curated"`.
   - Production adapters strictly anchor all extracted values to verified snapshot locators.
   - Enforced the Section 26 Negative Test: local curated values masquerading as `SOURCE_DERIVED` fail provenance verification and enter quarantine.
3. **Tri-Language Canonical Learning Expansion**:
   - Scaled the canonical learning graph from 812 concepts to **2,106 high-value learning concepts**.
   - Every single canonical concept has complete tri-language (EN + JA + VI) coverage (**6,318 total canonical expressions**).
   - Zero concepts lack any of the three languages; zero concepts are partial.
4. **Sense-Correct Polysemy Disambiguation**:
   - Implemented strict sense boundary preservation for high-frequency polysemous words (`right`, `bank`, `charge`, `interest`, `capital`, `issue`, `order`, etc.).
   - Guaranteed that `right` retains exactly 3 distinct concepts/senses (`right_correct`, `right_direction`, `right_entitlement`) without generic concept collisions.
5. **Preservation of Professional Core**:
   - The existing 800 professional legal/financial concepts and their `legacy_mapping.json` are 100% preserved and frozen.
6. **Oki-Language Compatibility**:
   - Exported 2,106 deck cards to `data/exports/oki_language/deck_data.json` satisfying downstream web application requirements.
7. **Zero AI Bulk Filling**:
   - AI bulk hallucination is strictly prohibited (0 AI-generated fields).

---

## 2. Source Inventory & Cryptographic Hashes

| Source ID | Version | License | Artifact Filename | Artifact SHA-256 | Records Extracted |
|:---|:---|:---|:---|:---|:---:|
| `kanjidic2` | 2026-10-01 | CC-BY-SA-3.0 | `kanjidic2.xml.gz` | `3e9b744d564fa7eef449f85c4bfd2105151b752495da5b1db3ff4aee334316a9` | 13,108 kanji |
| `joyo` | 2010-official | Government-PD | `joyo_kanji_official.json` | `f5f0cf7d03f3a7beddab973d6b1d31eb3cb30a2b0285639ba8f4042fd94e01f1` | 2,136 kanji |
| `jmdict` | 2026-10-01 | CC-BY-SA-3.0 | `JMdict_e.gz` | `89777236dbf06f4d7b01c6dbff5e1f707978ddd067061b66bcb782d1f24e6ed3` | 210,000+ entries |
| `ngsl` | 1.2 | CC-BY-4.0 | `NGSL_12_stats.csv` | `2098bab8955a120a9766c6282a51d7d578c6cb0a7d946600d2ffb73ba25a0b44` | 2,809 words |
| `ngsl_spoken` | 1.2 | CC-BY-4.0 | `NGSL-Spoken_12_stats.csv` | `63fcf02cfd3bfb70c3ec778e3ec8650a32e18d6e3c5457ef466e3eb740f930e4` | 721 words |
| `nawl` | 1.2 | CC-BY-4.0 | `NAWL_12_lemmatized_for_teaching.csv` | `01b228965f3752e503ae8d2c943806fcf225022ebae98c393bc3f167e411b43d` | 959 words |
| `bsl` | 1.2 | CC-BY-4.0 | `BSL_120_stats.csv` | `dfb0559eb4f39556a3108ce8a49c95d9a9cb2744747ebc7d6c5da29f6356784d` | 1,745 words |
| `tsl` | 1.2 | CC-BY-4.0 | `TSL_12_stats.csv` | `d4a52efc157f49e4fa87cfa7a57a0fb871ff2f507b973b4290374e2a39a778e1` | 1,250 words |
| `vn_freq` | 1.0 | MIT | `vn_word_frequencies.tsv` | `5bbcf140cb4e92a8b9487c6e61f22aa52a16d507b7ddf54d4ff7db097cb11ce1` | 19,047 words |
| `unihan` | 16.0.0 | Unicode-DFS-2016 | `Unihan.zip` | `c4d3fc0baae90435df178ebf25db544f8002cf7c1bc1ba47db378c2eec4e1f7d` | 67,996 readings |
| `jlpt_consensus` | 2026-v1 | CC0-1.0 | `JLPT_vocab_ALL.csv` | `a34ff749ff35b91b9f67a2167fa940e4f29a008c2a41d99665bc7f4dbda87504` | 8,506 words |

---

## 3. Learning Dimensions & Curriculum Coverage

| System | Classification Value Bands | Aligned Concepts in Canonical Graph |
|:---|:---|:---:|
| **NGSL** | Core Ranks 1 – 2,809 | 1,331 |
| **CEFR** | A1, A2, B1, B2, C1 | 1,332 |
| **EIKEN** | Grade 5/4, Grade 3, Grade Pre-2, Grade 2, Grade Pre-1 | 1,307 |
| **JLPT** | N5 (103), N4, N3, N2, N1 | 1,028 |
| **JOYO_KANJI** | Grades 1 – 6 (Elementary), Grade 7 – 8 (Secondary) | 1,235 |
| **TOEIC** | High Relevance (TSL/BSL) | 13 |
| **IELTS / TOEFL** | Academic Relevance (NAWL) | 6 / 1 |
| **VI_CORE** | VI_CORE_500 (171), VI_CORE_1000 (175), VI_CORE_2000 (178), VI_CORE_5000 (290) | 814 |
| **PROFESSIONAL_TIER** | Accounting, Corporate Governance, Legal, Banking | 800 |

---

## 4. Test Suite & Validation Invariants

- **Full Pytest Suite**: 314 passed in 8.97s (100% green).
- **Golden Pilot Invariants**: INV-8 and INV-8 (v1.1) pass.
- **Production Invariants**: INV-1 through INV-11 pass (zero violations).
- **Special Negative Test (Section 26)**: Verified that unbacked local curated values masquerading as `SOURCE_DERIVED` are quarantined.
