# Data Schema Specification: JP Professional Vocabulary Database

## 1. Multi-Layer Data Lifecycle Architecture

The database enforces a unidirectional 4-layer data transformation pipeline:

```
  Layer A: Raw Sources
  [Untouched official Excel/ZIP/HTML, SHA-256 Checksum, Immutable metadata]
                       │
                       ▼ (Parser & Extraction Scripts)
  Layer B: Extracted Candidates
  [Source-specific structured items, original headers, un-normalized text]
                       │
                       ▼ (Normalization, Kana unification, Surface Deduplication)
  Layer C: Canonical Vocabulary
  [Normalized Japanese surface, verified reading, domain classification, unique concept ID]
                       │
                       ▼ (Linguistic Engineering & Learning Enrichment)
  Layer D: Learning Enrichment (Production Release)
  [Vietnamese explanations, English mappings, collocations, natural workplace examples,
   multi-speaker dialogue, PRO-A1/A2/A3 tiers, priority scoring, TTS metadata, Provenance]
```

---

## 2. Canonical Entry Schema (Layer D - Production)

Each vocabulary item in `production/vocabulary.jsonl` and `production/jp_professional_pilot.jsonl` adheres strictly to this schema:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "JPProfessionalVocabularyEntry",
  "type": "object",
  "required": [
    "id",
    "term",
    "language",
    "domain",
    "concept",
    "meaning",
    "professional_level",
    "priority",
    "examples",
    "sources",
    "provenance",
    "tts",
    "confidence",
    "status"
  ],
  "properties": {
    "id": {
      "type": "string",
      "description": "Unique identifier formatted as jp-pro-{domain}-{6-digit-sequence}",
      "pattern": "^jp-pro-[a-z_]+-[0-9]{6}$"
    },
    "term": {
      "type": "object",
      "required": ["surface", "reading", "romaji"],
      "properties": {
        "surface": { "type": "string", "description": "Canonical Japanese surface form (Kanji/Kana)" },
        "reading": { "type": "string", "description": "Hiragana pronunciation (verified)" },
        "romaji": { "type": "string", "description": "Modified Hepburn romanization" }
      }
    },
    "language": {
      "type": "string",
      "enum": ["ja"]
    },
    "domain": {
      "type": "object",
      "required": ["primary", "secondary"],
      "properties": {
        "primary": {
          "type": "string",
          "enum": [
            "accounting", "bookkeeping", "tax", "finance", "banking",
            "business", "management", "sales", "purchasing", "hr",
            "labor", "legal", "contracts", "trade", "import_export",
            "customs", "logistics", "office_communication", "corporate_governance",
            "audit", "startup"
          ]
        },
        "secondary": {
          "type": "array",
          "items": { "type": "string" }
        }
      }
    },
    "concept": {
      "type": "object",
      "required": ["type", "canonical"],
      "properties": {
        "type": { "type": "string", "enum": ["noun", "verb_suru", "compound_noun", "idiomatic_expression", "adjective_na", "acronym"] },
        "canonical": { "type": "boolean", "default": true }
      }
    },
    "meaning": {
      "type": "object",
      "required": ["vi", "en"],
      "properties": {
        "vi": {
          "type": "object",
          "required": ["short", "explanation"],
          "properties": {
            "short": { "type": "string", "description": "Concise professional Vietnamese translation" },
            "explanation": { "type": "string", "description": "Original learner explanation with accounting/business context" },
            "professional_context": { "type": "string", "description": "Practical application notes in Japanese workplace" }
          }
        },
        "en": {
          "type": "object",
          "required": ["short", "preferred"],
          "properties": {
            "short": { "type": "string" },
            "preferred": { "type": "string" },
            "alternatives": { "type": "array", "items": { "type": "string" } }
          }
        }
      }
    },
    "professional_level": {
      "type": "object",
      "required": ["tier"],
      "properties": {
        "tier": {
          "type": "string",
          "enum": ["PRO-A1", "PRO-A2", "PRO-A3"],
          "description": "PRO-A1: Essential Workplace; PRO-A2: Working Professional; PRO-A3: Specialist"
        }
      }
    },
    "general_japanese": {
      "type": "object",
      "properties": {
        "estimated_level": { "type": "string", "enum": ["N1", "N2", "N3", "N4", "N5", "Advanced", "Intermediate"] }
      }
    },
    "frequency": {
      "type": "object",
      "properties": {
        "professional_priority": { "type": "string", "enum": ["essential", "high", "medium", "specialist"] }
      }
    },
    "priority": {
      "type": "object",
      "required": ["score", "factors"],
      "properties": {
        "score": { "type": "integer", "minimum": 0, "maximum": 100 },
        "factors": {
          "type": "object",
          "properties": {
            "workplace_frequency": { "type": "integer" },
            "learner_usefulness": { "type": "integer" },
            "source_authority": { "type": "integer" },
            "cross_domain_value": { "type": "integer" }
          }
        }
      }
    },
    "synonyms": { "type": "array", "items": { "type": "string" } },
    "antonyms": { "type": "array", "items": { "type": "string" } },
    "related_terms": { "type": "array", "items": { "type": "string" } },
    "collocations": { "type": "array", "items": { "type": "string" } },
    "examples": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["ja", "vi", "en"],
        "properties": {
          "ja": { "type": "string" },
          "vi": { "type": "string" },
          "en": { "type": "string" },
          "register": { "type": "string", "enum": ["beginner_workplace", "natural_workplace", "formal_business", "statutory_reporting"] }
        }
      }
    },
    "dialogue": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["speaker", "ja", "vi", "en"],
        "properties": {
          "speaker": { "type": "string", "enum": ["A", "B", "Manager", "Staff", "Accountant", "Client"] },
          "ja": { "type": "string" },
          "vi": { "type": "string" },
          "en": { "type": "string" }
        }
      }
    },
    "sources": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["source_id", "source_term_exact"],
        "properties": {
          "source_id": { "type": "string" },
          "source_term_exact": { "type": "string" },
          "source_reference": { "type": "string" },
          "source_authority": { "type": "string" }
        }
      }
    },
    "provenance": {
      "type": "object",
      "required": ["extracted_by", "enriched_by", "validated"],
      "properties": {
        "extracted_by": { "type": "string" },
        "enriched_by": { "type": "string" },
        "validated": { "type": "boolean" },
        "validation_timestamp": { "type": "string" }
      }
    },
    "tts": {
      "type": "object",
      "required": ["speak_term", "preferred_reading", "pause_after_term_ms"],
      "properties": {
        "speak_term": { "type": "boolean" },
        "preferred_reading": { "type": "string" },
        "pause_after_term_ms": { "type": "integer" },
        "repeat_default": { "type": "integer" },
        "speech_text": { "type": "string" },
        "display_text": { "type": "string" }
      }
    },
    "confidence": {
      "type": "object",
      "required": ["canonical_term", "reading", "vi_translation", "en_translation", "domain_classification"],
      "properties": {
        "canonical_term": { "type": "number", "minimum": 0, "maximum": 1 },
        "reading": { "type": "number", "minimum": 0, "maximum": 1 },
        "vi_translation": { "type": "number", "minimum": 0, "maximum": 1 },
        "en_translation": { "type": "number", "minimum": 0, "maximum": 1 },
        "domain_classification": { "type": "number", "minimum": 0, "maximum": 1 }
      }
    },
    "status": {
      "type": "string",
      "enum": ["production", "staging", "draft"]
    }
  }
}
```

---

## 3. Workplace Expressions Schema (`expressions.jsonl`)

Used for practical idioms, conversational set phrases, and operational collocations (e.g. `請求書を切る`, `経費で落とす`, `数字が合わない`):

```json
{
  "id": "jp-exp-accounting-000001",
  "surface": "経費で落とす",
  "reading": "けいひでおとす",
  "romaji": "keihi de otosu",
  "pattern_type": "colloquial_workplace",
  "related_canonical_id": "jp-pro-accounting-000045",
  "vi_meaning": "tính vào chi phí doanh nghiệp (để trừ thuế hợp lệ)",
  "en_meaning": "write off as an expense / charge to company expenses",
  "context_notes": "Very frequent in Japanese companies when handling receipts and business meals.",
  "formality": "polite_conversational",
  "verified_corpus": true,
  "sources": [{"source_id": "workplace_corpus", "confidence": 0.98}]
}
```

---

## 4. Relationship Graph Schema (`relationships.jsonl`)

```json
{
  "from_id": "jp-pro-accounting-000001",
  "to_id": "jp-pro-accounting-000002",
  "relation_type": "opposite",
  "directed": false,
  "notes": "売掛金 (Accounts Receivable) vs 買掛金 (Accounts Payable)"
}
```

Supported `relation_type` values:
- `broader`: Parent concept (e.g. 収益 -> 売上高)
- `narrower`: Sub-category (e.g. 税金 -> 法人税)
- `opposite`: Opposite accounting flow (e.g. 売掛金 vs 買掛金, 借方 vs 貸方)
- `synonym`: Synonymous concept (e.g. 売掛金 <-> 売上債権)
- `related`: Conceptually related in workflow (e.g. 見積書 -> 発注書 -> 請求書)
- `abbreviation`: Short form or acronym (e.g. L/C <-> 信用状)
- `often_confused_with`: Distinction warning (e.g. 売掛金 vs 未収入金)
- `prerequisite`: Pedagogical progression prerequisite
