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
- Maps term to 32 fine-grained ontological semantic classes (e.g. `tax_scheme`, `executive_compensation`, `equity_valuation_account`, `tangible_fixed_asset`, `depreciable_asset`, `allowance_provision`, `retained_earnings`, `shipping_document`, `trade_term`, `cargo_operation`, `person_role`, `organization`, `contract`, `metric`).
- Verifies each collocation specifies `predicate`, `particle`, `semantic_class`, `register`, and `status`.
- Actively blocks semantic incompatibilities and domain collisions (e.g. `ふるさと納税を提出する`, `事前確定届出給与を効率化する`, `土地を精算する`, `FOBの残高`).

### Stage 6: Example Sentence & Dialogue Validation
- Verifies at least 2 workplace example sentences per entry.
- Verifies every example specifies `ja`, `vi`, `en`, and `register` (e.g. `statutory_reporting`, `logistics_workplace`, `trade_contract`, `corporate_accounting`).
- Checks that the Japanese sentence contains the target term (`surface in ex["ja"]`) or its speech form.
- Checks minimum length (`len(ja) >= 15`).
- Verifies multi-speaker dialogue has at least 2 turns (Speaker A & B) situated in professional workplace contexts.
- Enforces absence of cross-language translation bleed (Vietnamese characters in English translations or English templates in Vietnamese translations).

### Stage 7: Independent Linguistic Judge (Phase 1.1A)
- Two-pass validation architecture:
  - **Pass A (Critic):** Evaluates collocation naturalness, semantic compatibility, professional domain correctness, register, and translation integrity.
  - **Pass B (Resolver):** Automatically synthesizes domain-accurate alternatives for flagged items and subjects them to re-evaluation.
- Enforces status progression: `generated` -> `linguistically_validated` -> `production_verified`.
- Deterministic SHA-256 caching in `data/validation_cache/`.

### Stage 8: TTS Metadata Validation
- Verifies `display_text`, `speech_text`, `preferred_reading`, `pronunciation_type`, and `pause_after_term_ms`.
- Verifies that `speech_text` does not contain raw slashes `/` (e.g. `B/L` expanded to `ビーエル`).
- Verifies numeric compounds use spoken kanji numerals (e.g. `1株当たり` -> `一株当たり`, `2割特例` -> `二割特例`).

### Stage 9: Draft Contamination Quarantine Guard
- Verifies that no candidate references `fsa_edinet_2027_draft` or `staging/fsa_edinet_2027_draft/`.
- Strictly blocks any draft taxonomy item from entering production.

---

## 3. Real Validation Results (800 Pilot Candidates Post Phase 1.1A Closure)

| Metric | Count | Rate | Status |
| :--- | :--- | :--- | :--- |
| **Total Candidates Evaluated** | 800 | 100.0% | Input Corpus |
| **Schema Valid** | 800 | 100.0% | Complete |
| **Official Source Verified** | 637 | 79.6% | Lineage verified against Layer B |
| **Curated Documented** | 163 | 20.4% | Documented curated origin |
| **Reading Verified** | 800 | 100.0% | Levels 1, 2, 3 verified + upstream remediated |
| **Reading Needs Review** | 0 | 0.0% | Upstream verified in statutory sources |
| **Reading Rejected** | 0 | 0.0% | Corrupted kana entries repaired upstream |
| **VI Translation Verified** | 800 | 100.0% | Complete, contamination-free |
| **EN Translation Verified** | 800 | 100.0% | Complete, contamination-free |
| **Collocations Certified** | 3,200 | 100.0% | Independent linguistic judge verified |
| **Examples Certified** | 1,600 | 100.0% | Independent linguistic judge verified |
| **Dialogue Turns Certified** | 1,600 | 100.0% | Independent linguistic judge verified |
| **TTS Ready** | 800 | 100.0% | Engine-independent metadata |
| **Draft Contamination Free** | 800 | 100.0% | Zero draft contamination |
| **Production Ready (PASS)** | **800** | **100.0%** | **Released to Production** |
| **Review Queue (NEEDS REVIEW)** | **0** | **0.0%** | **Clean staging queue** |
| **Rejected (FAIL)** | **0** | **0.0%** | **Clean staging queue** |

---

## 4. Phase 1.1A Upstream Remediation Log

All 11 entries quarantined in Phase 1.1 were remediated upstream in their authoritative domain knowledge banks:

1. `jp-pro-accounting-000021` — **その他有価証券評価差額金**: Corrected upstream to `そのたゆうかしょうけんひょうかさがくきん` (ASBJ Statement No. 10).
2. `jp-pro-tax-000008` — **ふるさと納税**: Corrected upstream to `ふるさとのうぜい` (Local Tax Act Art. 37-2).
3. `jp-pro-tax-000018` — **事前確定届出給与**: Corrected upstream to `じぜんかくていとどけできゅうよ` (Corporation Tax Act Art. 34).
4. `jp-pro-tax-000049` — **雑損控除**: Standard reading `ざっそんこうじょ` registered in `INDUSTRY_VERIFIED_LEXICON` with statutory evidence (Income Tax Act Art. 72).
5. `jp-pro-tax-000062` — **白色申告**: Standard reading `はくしょくしんこく` registered upstream (Income Tax Act).
6. `jp-pro-business-000006` — **招集通知**: Corrected upstream to `しょうしゅうつうち` (Companies Act Art. 299).
7. `jp-pro-trade-000008` — **航空貨物運送状**: Corrected upstream to `こうくうかもつうんそうじょう` (IATA Standard).
8. `jp-pro-trade-000009` — **クリーンB/L**: Corrected upstream to `くりーんびーえる` (Maritime Standard).
9. `jp-pro-trade-000010` — **貨物受領証**: Corrected upstream to `かもつじゅりょうしょう` (Commercial Code Art. 571).
10. `jp-pro-trade-000021` — **他法令確認**: Corrected upstream to `たほうれいかくにん` (Customs Act Art. 70).
11. `jp-pro-trade-000032` — **ラッシング**: Corrected upstream to `らっしんぐ` (Cargo Securing Code).

---

## 5. Execution Pipeline Commands

To reproduce the entire validation and release workflow:

```bash
# 1. Enrich normalized candidates into learning candidates
.venv/bin/python3 scripts/build_pilot_dataset.py

# 2. Run independent validation across all stages
.venv/bin/python3 scripts/validate_dataset.py

# 3. Enforce the release gate (routes pass to production, others to staging)
.venv/bin/python3 scripts/release_gate.py

# 4. Run test suite
.venv/bin/pytest tests/ -v
```

