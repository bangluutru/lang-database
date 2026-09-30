# Linguistic Validation & Quality Assurance Specification (Phase 1.1)

## 1. Overview

Phase 1.1 establishes an **independent, evidence-based linguistic validation engine** for the JP Professional Vocabulary Database.

Under this architecture:
- The dataset builder **cannot self-certify** records (`"validated": true` and artificial confidence floats like `0.99` are completely removed).
- The validator evaluates records across **8 isolated dimensions**.
- The **Release Gate** enforces data integrity by routing passed records to production while quarantining unverified or corrupted entries into staging review queues.
- Real metrics are reported transparently without artificial score inflation.

---

## 2. The 8 Validation Stages

```
┌────────────────────────────────────────────────────────┐
│                   VALIDATION STAGES                    │
│                                                        │
│  Stage 1: Schema Validation                            │
│  Stage 2: Source Lineage & Physical Existence          │
│  Stage 3: 4-Level Pronunciation Hierarchy              │
│  Stage 4: Translation QA (Vietnamese & English)        │
│  Stage 5: Collocation Naturalness & Semantic Frames    │
│  Stage 6: Example Sentence Workplace Register          │
│  Stage 7: TTS Phonetic Safety & Acronym Expansion      │
│  Stage 8: Draft Contamination Quarantine Guard         │
└────────────────────────────────────────────────────────┘
```

### Stage 1: Schema Validation
- Validates canonical ID syntax (`^jp-pro-[a-z_]+-[0-9]{6}$`).
- Verifies domain belongs to the 21 recognized domains.
- Enforces professional tiers (`PRO-A1`, `PRO-A2`, `PRO-A3`) and requires an explicit descriptive definition.
- Verifies priority score (0–100) and ensures `workplace_frequency + learner_usefulness + source_authority + cross_domain_value == score`.
- Enforces decoupled JLPT: `general_japanese.jlpt_level` must be `null` and `jlpt_status` must be `"not_mapped"`.
- Strictly rejects any record carrying static circular confidence scores.

### Stage 2: Source Lineage & Physical Existence
- Validates presence of the `lineage` block.
- For `origin_type == "official_extracted"`:
  - Verifies presence of `extracted_candidate_id` and `normalized_candidate_id`.
  - Verifies physical existence of the record in `data/normalized/normalized_candidates.jsonl`.
  - Verifies `source_term_exact` matches the surface form.
  - Verifies the source file is not in draft status.
- For `origin_type == "curated"`:
  - Verifies explicit declaration of curated status.
  - Verifies presence of documented `source_record_id`.

### Stage 3: 4-Level Pronunciation Hierarchy
- **Level 1 (Authoritative Acronym Registry):** Verified against `ACRONYM_SPEECH_MAP` for Latin acronyms and symbols (`FOB`, `CIF`, `B/L`, `L/C`, `e-Tax`, etc.).
- **Level 2 (Dictionary Cross-Check):** Morphological tokenization via Janome IPAdic converted to Hiragana matching reading, or verified industry-standard lexicon (`INDUSTRY_VERIFIED_LEXICON`).
- **Level 3 (Algorithmic Cross-Check):** pykakasi Hepburn/Hiragana conversion agreement.
- **Level 4 (Unverified / AI-Generated):** Phonetic variations differing from dictionaries are flagged for human review or rejected if corrupted.

### Stage 4: Translation Validation
- **Vietnamese:** Verifies `short`, `preferred`, `explanation`, and `professional_context`. Enforces minimum length, grammatical validity, and absence of generic placeholder tokens (`[TODO]`, `...`).
- **English:** Verifies `preferred` and `short` translations are present without placeholders.

### Stage 5: Semantic Collocation Validation
- Maps term to 24 ontological semantic classes (e.g. `account`, `financial_statement`, `tax_deduction`, `shipping_document`, `trade_term`, `freight_charge`, `cargo_operation`, `person_role`, `organization`, `contract`, `metric`).
- Verifies each collocation specifies `predicate`, `particle`, `semantic_class`, `register`, and `status`.
- Actively blocks prohibited generic domain collisions (e.g. `土地を精算する`, `FOBの残高`, `取締役を精算する`).

### Stage 6: Example Sentence Validation
- Verifies at least 2 workplace example sentences per entry.
- Verifies every example specifies `ja`, `vi`, `en`, and `register` (e.g. `statutory_reporting`, `logistics_workplace`, `trade_contract`, `corporate_accounting`).
- Checks that the Japanese sentence contains the target term (`surface in ex["ja"]`) or its speech form.
- Checks minimum length (`len(ja) >= 15`).
- Verifies multi-speaker dialogue has at least 2 turns (Speaker A & B) situated in professional workplace contexts.

### Stage 7: TTS Metadata Validation
- Verifies `display_text`, `speech_text`, `preferred_reading`, `pronunciation_type`, and `pause_after_term_ms`.
- Verifies that `speech_text` does not contain raw slashes `/` (e.g. `B/L` expanded to `ビーエル`).
- Verifies numeric compounds use spoken kanji numerals (e.g. `1株当たり` -> `一株当たり`, `2割特例` -> `二割特例`).

### Stage 8: Draft Contamination Quarantine Guard
- Verifies that no candidate references `fsa_edinet_2027_draft` or `staging/fsa_edinet_2027_draft/`.
- Strictly blocks any draft taxonomy item from entering production.

---

## 3. Real Validation Results (800 Pilot Candidates)

| Metric | Count | Rate | Status |
| :--- | :--- | :--- | :--- |
| **Total Candidates Evaluated** | 800 | 100.0% | Input Corpus |
| **Schema Valid** | 800 | 100.0% | Complete |
| **Official Source Verified** | 637 | 79.6% | Lineage verified against Layer B |
| **Curated Documented** | 163 | 20.4% | Documented curated origin |
| **Reading Verified** | 789 | 98.6% | Levels 1, 2, 3 verified |
| **Reading Needs Review** | 2 | 0.3% | Phonetic variance |
| **Reading Rejected** | 9 | 1.1% | Phonetic corruption detected |
| **VI Translation Verified** | 800 | 100.0% | Complete |
| **Collocations Verified** | 800 | 100.0% | Semantic frame validated |
| **Examples Verified** | 800 | 100.0% | Workplace register validated |
| **TTS Ready** | 800 | 100.0% | Engine-independent metadata |
| **Draft Contamination Free** | 800 | 100.0% | Zero draft contamination |
| **Production Ready (PASS)** | **789** | **98.6%** | **Released to Production** |
| **Review Queue (NEEDS REVIEW)** | **2** | **0.3%** | **Quarantined in Staging** |
| **Rejected (FAIL)** | **9** | **1.1%** | **Quarantined in Staging** |

---

## 4. Quarantined Records Detail

### Needs Review Queue (`staging/review_queue/needs_review.jsonl`)
Entries requiring linguistic review due to multi-reading variance:

1. `jp-pro-tax-000042` — **白色申告**: Reading `しろいろしんこく`. Common workplace kun-yomi reading vs formal tax on-yomi `はくしょくしんこく`.
2. `jp-pro-tax-000066` — **雑損控除**: Reading `ざっそんこうじょ`. Rendaku phonetic assimilation vs dictionary base form `ざつそんこうじょ`.

### Rejection Queue (`staging/review_queue/rejected.jsonl`)
Entries caught with genuine phonetic corruption in the pilot data:

1. `jp-pro-accounting-000119` — **その他有価証券評価差額金**: Reading `そのたゆうかしょうけんひょうかがくきん` (missing syllable `さ`).
2. `jp-pro-tax-000065` — **ふるさと納税**: Reading `ふるさとづぜい` (corrupted character `づぜい` instead of `のうぜい`).
3. `jp-pro-tax-000101` — **事前確定届出給与**: Reading `じぜんかくていとどけいできゅうよ` (corrupted syllable `とどけいで` instead of `とどけで`).
4. `jp-pro-business-000042` — **招集通知**: Reading `しょうしゅうちつ` (corrupted ending `つ` instead of `つうち`).
5. `jp-pro-trade-000028` — **航空貨物運送状**: Reading `こうくうかもとうんそうじょう` (missing syllable `つ`).
6. `jp-pro-trade-000041` — **クリーンB/L**: Reading `くりーんはーえる` (corrupted acronym `はーえる` instead of `びーえる`).
7. `jp-pro-trade-000056` — **貨物受領証**: Reading `かもとじゅりょうしょう` (missing syllable `つ`).
8. `jp-pro-trade-000102` — **他法令確認**: Reading `たほうれいきか確認` (contains kanji inside kana reading string).
9. `jp-pro-trade-000174` — **ラッシング**: Reading `まっしんぐ` (corrupted initial kana `ま` instead of `ら`).

*Note on Data Integrity:* In adherence to Directive Section 26 ("Do not optimize for 800/800 PASS. Optimize for truth."), these entries were intentionally quarantined rather than silently altered or passed. They will be remediated in the candidate review queue prior to Phase 1.2.

---

## 5. Execution Pipeline Commands

To reproduce the entire validation and release workflow:

```bash
# 1. Enrich normalized candidates into learning candidates
.venv/bin/python3 scripts/build_pilot_dataset.py

# 2. Run independent validation across all 8 stages
.venv/bin/python3 scripts/validate_dataset.py

# 3. Enforce the release gate (routes pass to production, others to staging)
.venv/bin/python3 scripts/release_gate.py

# 4. Run test suite
.venv/bin/pytest tests/ -v
```
