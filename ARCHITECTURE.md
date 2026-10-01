# System Architecture: JP Professional Vocabulary Database

## 1. Architectural Evolution: Phase 1 vs. Phase 1.1

The **JP Professional Vocabulary Database** is designed as a foundational, decoupled linguistic knowledge base engineered for high-integrity machine consumption (downstream curriculum generation, audio shadowing lesson synthesis, video slide rendering, and flashcard engines).

### Old Architecture (Phase 1 Pilot — Circular Validation)
```
[Raw/Curated Banks] ──> [Builder] ───(self-certifies "validated": true & confidence 0.99)──> [Production File]
                                │                                                                    │
                                └───> [Validator] ◄──(checks builder's declared values)──────────────┘
```
*Problems:* Builder declared records valid without independent checks; artificial confidence floats (0.99, 0.98); fake JLPT derived from PRO tier; collocations generated from universal domain templates.

### New Architecture (Phase 1.1 — Data Integrity & Linguistic Closure)
```
┌────────────────────────────────────────────────────────────────────────┐
│                      OFFICIAL / TRUSTED SOURCES                        │
│         FSA (EDINET 2026) │ NTA │ JICPA │ ASBJ │ JETRO │ Customs       │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                   LAYER A: RAW UNTOUCHED SOURCE                        │
│   data/raw/{source}/ - Raw files, SHA-256 Checksums, Source Registry   │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ (extract_fsa.py, extract_nta.py, etc.)
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                   LAYER B: EXTRACTED CANDIDATES                        │
│   data/extracted/ - cand-{source}-{seq:06d}, source_record_id preserved│
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ (normalize_terms.py)
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                   LAYER C: NORMALIZED CANDIDATES                       │
│   data/normalized/ - norm-{seq:06d}, NFKC, lineage pointers retained   │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ (build_pilot_dataset.py)
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                   LAYER D: ENRICHED LEARNING CANDIDATES                │
│   data/enriched/ - learning_candidates.jsonl                           │
│   • Semantic class classification (32 fine-grained ontological types)  │
│   • Semantic frame collocations (status: "generated")                  │
│   • Workplace examples & dialogue turns (status: "generated")          │
│   • Decoupled JLPT (null, not_mapped)                                  │
│   • TTS display vs speech text modeling (acronym expansion)            │
│   • Lineage metadata injected                                          │
│   • Strict candidate status (NO self-certification, NO fake confidence)│
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                   LAYER E: INDEPENDENT VALIDATOR & LINGUISTIC JUDGE    │
│   scripts/validate_dataset.py & scripts/linguistic_validator.py        │
│   1. Schema Validation (no artificial floats, JLPT null)               │
│   2. Physical Source Lineage Verification (Layer B lookup)             │
│   3. 4-Level Reading Hierarchy (Janome IPAdic + Lexicon cross-check)   │
│   4. Translation QA & Language Contamination Detection                 │
│   5. Independent Two-Pass Linguistic Judge (Critic & Resolver)         │
│      - Collocation naturalness & semantic compatibility                │
│      - Professional domain correctness & workplace register            │
│      - SHA-256 deterministic validation cache                          │
│   6. Example Sentence & Multi-speaker Dialogue QA                      │
│   7. TTS Metadata QA (speech text slash safety, pause duration)        │
│   8. Draft Contamination Guard (blocks FSA 2027 draft contamination)   │
│   Output: data/validated/validated_candidates.jsonl                    │
│   (Upgrades certified objects to status: "linguistically_validated")  │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                   LAYER F: PRODUCTION RELEASE GATE                     │
│   scripts/release_gate.py                                              │
│   Routes by independent decision:                                      │
│     ├── PASS (≥772 entries) ──> data/production/vocabulary.jsonl       │
│     │                           data/production/jp_professional_pilot.jsonl
│     │                           data/production/jp_professional.db     │
│     │   * Promotes objects to status: "production_verified"            │
│     │   * Strictly asserts ZERO "generated" objects in production      │
│     ├── REVIEW (0 entries) ──> staging/review_queue/needs_review.jsonl │
│     └── REJECT → QUARANTINE ──> staging/review_queue/rejected.jsonl    │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│             LAYER F2: PHASE 1.1C QUARANTINE REMEDIATION                │
│   scripts/run_phase1_1c.py                                             │
│   Applies to quarantined records only:                                 │
│     1. Root-cause diagnosis (systemic vs record-level)                 │
│     2. Critic → Resolver (corrects template injection, wrong preds)    │
│     3. Blind Re-judge (independent pass with corrected content)        │
│     4. Adversarial Audit (adversarial scrutiny before promotion)       │
│     ├── RECOVERED ──> merged into data/production/vocabulary.jsonl     │
│     │                  (release_version: v1.1.0c-prod, remediated: true)
│     └── PERMANENT QUARANTINE → staging/review_queue/permanent_quarantine.jsonl
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│             LAYER F3: GOLDEN PILOT FREEZE                              │
│   data/releases/golden-pilot-v1/                                       │
│   Immutable regression baseline frozen at Phase 1.1C:                 │
│   • vocabulary.jsonl  — all production records, sorted by ID          │
│   • dataset_manifest.json — canonical SHA-256, file SHA-256,          │
│                              domain counts, model policy, commit hash  │
│   • validation_manifest.json — validation architecture metadata        │
│   • checksums.sha256  — file integrity                                 │
│   • Invariant: corrections produce v1.1 or v2, NEVER overwrite in place│
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                   LAYER G: DOWNSTREAM CONSUMERS                        │
│   • Curriculum Planning Engine (query by domain, tier, priority)       │
│   • Audio & Shadowing Lesson Synthesizer (TTS speech text, pause ms)   │
│   • Video Slide & Subtitle Renderer                                    │
│   • Adaptive Quiz & Flashcard Engines                                  │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. End-to-End Lineage Tracking

Every vocabulary record maintains an immutable `lineage` block tracing its origin from government files to production release:

```json
"lineage": {
  "origin_type": "official_extracted",
  "source_id": "fsa_edinet_2026",
  "source_file": "1f_AccountList.xlsx",
  "source_record_id": "BalanceSheetAbstract",
  "source_term_exact": "貸借対照表",
  "extracted_candidate_id": "cand-fsa-000001",
  "normalized_candidate_id": "norm-000001",
  "canonical_id": "jp-pro-accounting-000001",
  "enrichment_version": "v1.1.0-linguistic",
  "validation_record": {
    "validated_at": "2026-10-01T08:30:00Z",
    "validator_version": "v1.1.0-independent",
    "checks": {
      "schema": "pass",
      "source_lineage": "pass",
      "reading": "verified",
      "translation_vi": "pass",
      "collocations": "pass",
      "examples": "pass",
      "tts": "pass",
      "draft_contamination": "pass"
    },
    "release_decision": "pass"
  },
  "release_version": "v1.1.0-prod"
}
```

For curated items:
- `origin_type`: `"curated"`
- `source_file`: `"pilot_builder_curated"`
- `source_record_id`: `"curated-{domain}-{surface}"`
- Curated items are never disguised as official government extractions.

---

## 3. Pronunciation Validation Hierarchy

Pronunciation is validated against a 4-level hierarchy:
- **Level 1 (Authoritative Registry):** Exact match in authoritative source or curated acronym phonetic registry (`ACRONYM_SPEECH_MAP`).
- **Level 2 (Dictionary Cross-Check):** Morphological tokenization via Janome IPAdic matching katakana-to-hiragana conversion, or official accounting/tax industry lexicon (`INDUSTRY_VERIFIED_LEXICON`).
- **Level 3 (Algorithmic Cross-Check):** pykakasi Hepburn/Hiragana conversion agreement.
- **Level 4 (Unverified / AI-Generated):** Pronunciation variants differing from dictionaries. Quarantined to `needs_review` or `rejected`.

---

## 4. TTS-Specific Modeling

The database is completely engine-independent. To avoid pronunciation failures on slashes, Latin acronyms, and numeric kanji compounds, display and spoken forms are separated:

| Term | Display Text | Speech Text | Preferred Reading | Pronunciation Type |
| :--- | :--- | :--- | :--- | :--- |
| `B/L` | `B/L` | `ビーエル` | `びーえる` | `acronym_alphabet` |
| `クリーンB/L` | `クリーンB/L` | `クリーンビーエル` | `くりーんびーえる` | `mixed_compound` |
| `FOB` | `FOB` | `エフオービー` | `えふおーびー` | `acronym_alphabet` |
| `e-Tax` | `e-Tax` | `イータックス` | `いーたっくす` | `acronym_alphabet` |
| `1株当たり当期純利益` | `1株当たり当期純利益` | `一株当たり当期純利益` | `ひとかぶあたりとうきじゅんりえき` | `numeric_compound` |
| `貸借対照表` | `貸借対照表` | `貸借対照表` | `たいしゃくたいしょうひょう` | `standard_kanji_kana` |

---

## 5. Decoupled JLPT vs. Professional Tiers

Professional difficulty and general Japanese language proficiency (JLPT) are distinct dimensions:
- **Professional Tiers:**
  - `PRO-A1`: Essential workplace vocabulary (high frequency foundational operations).
  - `PRO-A2`: Working professional vocabulary (routine transactions, filings, analysis).
  - `PRO-A3`: Specialist / technical vocabulary (statutory schedules, legal disputes, complex instruments).
- **JLPT Mapping:**
  - `general_japanese: { "jlpt_level": null, "jlpt_status": "not_mapped" }`
  - Inferred precision is strictly prohibited. Integration with the existing JLPT database will occur in a dedicated phase.

---

## 6. Storage Strategy

- **JSONL (`.jsonl`):** Line-by-line master records under `data/production/` and staging queues under `staging/review_queue/`.
- **SQLite (`.db`):** Local relational database with FTS5 search index (`data/production/jp_professional.db`).
- **Deterministic Pipeline:** All candidate enrichment, validation, and release gate scripts are reproducible and deterministic.

---

## 7. Phase 1.3B Architecture: Tri-Language Learning Lexical Graph

Phase 1.3B evolves the vocabulary pipeline into a unified, open, machine-readable **English–Japanese–Vietnamese Learning Lexical Graph**.

```
CONCEPT (language-independent semantic identity)
   │
   ├── SENSE (distinct meaning, POS, register, glosses)
   │     │
   │     ├── EN EXPRESSION(S) (lemma, pronunciation, display_form)
   │     ├── JA EXPRESSION(S) (lemma, reading, romaji, kanji)
   │     └── VI EXPRESSION(S) (lemma, pronunciation, Hán-Việt cognates)
   │
   ├── CLASSIFICATIONS (many-to-many: CEFR, NGSL, JLPT, Joyo, TOEIC, IELTS, TOEFL, VI Core)
   ├── EXAMPLES (pedagogical sentences with multi-language links)
   ├── RELATIONSHIPS (synonyms, antonyms, SINO_COGNATE_OF)
   └── SOURCE EVIDENCE & PROVENANCE (value-level traceability, license metadata, AI origin tags)
```

### 7.1 Concept vs. Sense vs. Expression
1. **Concept**: Universal language-independent semantic anchor (e.g. `concept-000101` or `concept-poly-right-correct`). Permanent IDs never use English strings directly.
2. **Sense**: Represents a specific semantic definition under a Concept. Multiple senses exist when justified by distinct meanings. Polysemous words are **never collapsed**:
   - `right` (correct) → `concept-poly-right-correct` / `sense-poly-right-correct-01`
   - `right` (direction) → `concept-poly-right-direction` / `sense-poly-right-direction-01`
   - `right` (entitlement) → `concept-poly-right-entitlement` / `sense-poly-right-entitlement-01`
3. **Expression**: Language-specific lexical realization (`en`, `ja`, `vi`). Language-specific attributes (reading, kanji, kana for JA; Hán-Việt for VI; IPA for EN) live exclusively within the relevant Expression.

### 7.2 Many-to-Many Learning Classification
Learning classifications attach directly to Concepts, Senses, or Expressions without duplicating lexical records:
- **Japanese**: `JOYO_KANJI`, `SCHOOL_GRADE`, `JLPT`, `JP_FREQUENCY`, `JP_CORE`
- **English**: `CEFR`, `NGSL`, `NGSL_SPOKEN`, `NAWL`, `BUSINESS_SERVICE_LIST`, `TOEIC`, `EIKEN`, `IELTS`, `TOEFL`, `EN_FREQUENCY`
- **Vietnamese**: `VI_CORE_500`, `VI_CORE_1000`, `VI_CORE_2000`, `VI_CORE_5000`, `VI_FREQUENCY`, `VI_SPOKEN`
- **Provenance Taxonomy**: Every classification carries `official`, `source_derived`, `corpus_derived`, `community_consensus`, `inferred`, or `ai_proposed`. JLPT classifications are labeled `community_consensus` rather than `official` to prevent false authority claims.

### 7.3 Hán-Việt First-Class Cognate Modeling
Sino-Japanese and Sino-Vietnamese cognates are linked explicitly as `SINO_COGNATE_OF` relationships with verified morphological and semantic evidence (e.g., `経済` ↔ `KINH TẾ` ↔ `kinh tế` ↔ `economy`), while preventing false cognate conflations.

### 7.4 Open Ingestion Foundation & License Gate
- **Adapter Contract (`BaseSourceAdapter`)**: Idempotent extraction requiring `source_id`, `version`, `source_locator`, `license_code`, `raw_sha256`, and value-level `SourceEvidence`.
- **License Gate (`config/license_policy.yaml`)**: Automatically approves `CC0-1.0`, `CC-BY-4.0`, `CC-BY-SA-4.0`, `PDL-1.0`, `MIT`. Quarantines `CC-BY-NC-4.0`, `CC-BY-ND-4.0`, `PROPRIETARY`, and `UNKNOWN`.
- **AI Provenance Separation**: Machine-assisted fields carry `origin = ai_generated`, `model`, `generation_version`, and `review_status = pending`. AI proposals never masquerade as source evidence.

### 7.5 Backward Compatibility & Legacy Bridge
`LegacyBridge` maps all 800 existing `jp-pro-*` records into canonical `Concept`, `Sense`, `Expression`, and `Classification` records while preserving legacy IDs in `data/canonical/legacy_mapping.json`. All legacy production datasets, Golden Pilot releases (v1 & v1.1), and Canaries remain byte-for-byte frozen.

