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
