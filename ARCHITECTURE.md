# System Architecture: JP Professional Vocabulary Database

## 1. Architectural Philosophy

The **JP Professional Vocabulary Database** is designed as a foundational, decoupled linguistic knowledge base. It is engineered primarily for **machine consumption** (downstream lesson generation, TTS orchestration, automated video slide rendering, adaptive flashcard engines) while maintaining complete human transparency and verification.

```
┌─────────────────────────────────────────────────────────────┐
│                 OFFICIAL EXTERNAL SOURCES                   │
│   FSA (EDINET 2026) │ NTA (Tax Answer) │ JICPA │ ASBJ │ JETRO│
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                 LAYER A: RAW DATA REPOSITORY                │
│  data/raw/{source}/ - Untouched, SHA-256 Checksums, Meta    │
└──────────────────────────────┬──────────────────────────────┘
                               │ (inspect_excel.py, extractors)
                               ▼
┌─────────────────────────────────────────────────────────────┐
│              LAYER B: EXTRACTED CANDIDATES                  │
│  data/extracted/ - Source items with original hierarchies   │
└──────────────────────────────┬──────────────────────────────┘
                               │ (normalize_terms.py, deduplicate.py)
                               ▼
┌─────────────────────────────────────────────────────────────┐
│              LAYER C: CANONICAL VOCABULARY                  │
│  data/normalized/ - Deduplicated, NFKC, Reading Verified    │
└──────────────────────────────┬──────────────────────────────┘
                               │ (enrich_terms.py, validate_readings.py)
                               ▼
┌─────────────────────────────────────────────────────────────┐
│             LAYER D: ENRICHED LEARNING OBJECTS              │
│  data/production/ - vocabulary.jsonl, relationships.jsonl   │
│                   - SQLite Indexed DB (export_sqlite.py)    │
└──────────────────────────────┬──────────────────────────────┘
                               │
                ┌──────────────┴──────────────┐
                ▼                             ▼
   DOWNSTREAM CURRICULUM AGENT       GEMINI TTS / AUDIO ENGINE
   - Queries by Domain, Level        - Uses Speech Text, Readings
   - Assembles 20-min lessons        - Pause Timings & Multi-speaker
```

---

## 2. Decoupling from Downstream Audio & Video Consumers

A critical architectural mandate is that the database **does not depend on any specific TTS service or video generation framework**.

1. **TTS as a Consumer:**
   - The database stores TTS preparation fields (`preferred_reading`, `speech_text`, `pause_after_term_ms`, `repeat_default`, `display_text`).
   - If Google Cloud Gemini TTS is swapped for AWS Polly, ElevenLabs, or VoicePeak, the vocabulary database remains untouched.
2. **Audio File Independence:**
   - Audio files are ephemeral or downstream pipeline artifacts; they are never baked directly into the master vocabulary schema.

---

## 3. Storage Format Strategy: JSONL & SQLite

| Format | Role | Rationale |
| :--- | :--- | :--- |
| **JSONL (`.jsonl`)** | Primary Master & Version Control | 1 record per line enables clean `git diff`, line-by-line stream parsing, token economics, and scalable ingestion without memory bloat. |
| **SQLite (`.db`)** | Local Fast Query Engine | Instant relational querying, compound indexing on `(domain, tier, priority_score)`, and relationship graph traversals without deploying a dedicated PostgreSQL server. |
| **Excel (`.xlsx`)** | Source Input & Review Export Only | Used for initial government data ingestion and human review sample exports. **Never used as master data storage.** |

---

## 4. Deterministic vs. Probabilistic Tool Division

To guarantee zero hallucination in critical taxonomy facts:

- **Deterministic Code (Python + Janome/Pykakasi + SQLite + OpenPyXL):**
  - File retrieval & HTTP downloads
  - Cryptographic checksum generation (SHA-256)
  - Excel sheet structure inspection & row parsing
  - Unicode NFKC normalization, fullwidth/halfwidth conversion
  - Exact string matching, ID generation, deduplication
  - Reading dictionary validation & schema constraint checks
- **Linguistic AI & Domain Engineering (Gemini / Domain Model):**
  - Workplace natural example generation
  - Contextual dialogue creation (A/B business speakers)
  - Pedagogical explanation in Vietnamese
  - Conceptual similarity clustering & cross-domain mapping
  - Professional priority scoring (0–100) & difficulty tiering (PRO-A1/A2/A3)
