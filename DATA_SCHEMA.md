# Data Schema Specification: JP Professional Vocabulary Database (Phase 1.1)

## 1. Multi-Stage Lifecycle Pipeline

The database enforces a strict, decoupled 7-stage transformation pipeline:

```
  Layer A: Raw Sources
  [Untouched official Excel/ZIP/HTML, SHA-256 Checksum, Immutable metadata]
                       │
                       ▼ (Parser & Extraction Scripts: cand-{src}-{seq:06d})
  Layer B: Extracted Candidates
  [Source-specific structured items, original headers, source_record_id preserved]
                       │
                       ▼ (Normalization: norm-{seq:06d}, NFKC, lineage links)
  Layer C: Normalized Candidates
  [Normalized Japanese surface, domain classification, unique concept link]
                       │
                       ▼ (Candidate Enrichment: semantic classes, collocations, TTS)
  Layer D: Enriched Learning Candidates (status: "candidate")
  [Vietnamese explanations, English mappings, semantic collocations, workplace examples,
   multi-speaker dialogue, PRO tiers with descriptions, TTS metadata, Lineage block]
                       │
                       ▼ (Independent 8-Stage Validation Pipeline)
  Layer E: Validated Candidates (status: "pass" | "needs_review" | "rejected")
  [Schema, source lineage physical check, 4-level pronunciation check, translation,
   collocation naturalness, example registers, TTS safety, draft quarantine guard]
                       │
                       ▼ (Release Gate Routing)
  Layer F: Production Releases & Staging Queues
  [vocabulary.jsonl (PASS), staging/review_queue/needs_review.jsonl, staging/review_queue/rejected.jsonl]
                       │
                       ▼ (SQLite Export with FTS5 Full-Text Search)
  Layer G: Downstream Machine & Learning Consumers
```

---

## 2. Canonical Entry Schema (Production Release)

Each released vocabulary record in `data/production/vocabulary.jsonl` adheres strictly to this schema:

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
    "general_japanese",
    "priority",
    "collocations",
    "examples",
    "dialogue",
    "sources",
    "lineage",
    "provenance",
    "tts",
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
        "reading": { "type": "string", "description": "Hiragana pronunciation (independently verified)" },
        "romaji": { "type": "string", "description": "Modified Hepburn romanization" },
        "romaji_metadata": {
          "type": "object",
          "properties": {
            "scheme": { "type": "string", "enum": ["modified_hepburn"] },
            "generator": { "type": "string", "enum": ["pykakasi"] },
            "generator_version": { "type": "string" }
          }
        }
      }
    },
    "language": {
      "type": "string",
      "enum": ["ja"]
    },
    "domain": {
      "type": "object",
      "required": ["primary", "secondary", "semantic_class"],
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
        "secondary": { "type": "array", "items": { "type": "string" } },
        "semantic_class": {
          "type": "string",
          "description": "Ontological classification governing semantic selection and predicate binding (e.g. account, financial_statement, tax, tax_deduction, shipping_document, trade_term, freight_charge, cargo_operation, person_role, organization, contract, metric, procedure, etc.)"
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
          "required": ["short", "preferred", "explanation", "professional_context"],
          "properties": {
            "short": { "type": "string", "description": "Concise professional Vietnamese translation" },
            "preferred": { "type": "string", "description": "Standardized professional translation" },
            "explanation": { "type": "string", "description": "Original learner explanation with practical context" },
            "professional_context": { "type": "string", "description": "Workplace usage domain note" }
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
      "required": ["tier", "description"],
      "properties": {
        "tier": { "type": "string", "enum": ["PRO-A1", "PRO-A2", "PRO-A3"] },
        "description": { "type": "string" }
      }
    },
    "general_japanese": {
      "type": "object",
      "required": ["jlpt_level", "jlpt_status"],
      "properties": {
        "jlpt_level": { "type": ["string", "null"], "default": null, "description": "Must be null until official JLPT mapping is integrated." },
        "jlpt_status": { "type": "string", "enum": ["not_mapped", "mapped"] }
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
    "collocations": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["text", "predicate", "particle", "semantic_class", "status", "register"],
        "properties": {
          "text": { "type": "string" },
          "predicate": { "type": "string" },
          "particle": { "type": "string" },
          "semantic_class": { "type": "string" },
          "status": { "type": "string", "enum": ["verified", "candidate"] },
          "validation_method": { "type": "string" },
          "register": { "type": "string" }
        }
      }
    },
    "examples": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["ja", "vi", "en", "register", "status"],
        "properties": {
          "ja": { "type": "string" },
          "vi": { "type": "string" },
          "en": { "type": "string" },
          "register": { "type": "string" },
          "status": { "type": "string" }
        }
      }
    },
    "dialogue": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["speaker", "ja", "vi", "en"],
        "properties": {
          "speaker": { "type": "string" },
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
        "required": ["source_id", "source_file", "source_term_exact", "source_record_id"],
        "properties": {
          "source_id": { "type": "string" },
          "source_file": { "type": "string" },
          "source_term_exact": { "type": "string" },
          "source_reference": { "type": "string" },
          "source_record_id": { "type": "string" }
        }
      }
    },
    "lineage": {
      "type": "object",
      "required": [
        "origin_type", "source_id", "source_file", "source_record_id",
        "source_term_exact", "canonical_id", "enrichment_version",
        "validation_record", "release_version"
      ],
      "properties": {
        "origin_type": { "type": "string", "enum": ["official_extracted", "official_derived", "curated", "generated_enrichment"] },
        "source_id": { "type": "string" },
        "source_file": { "type": "string" },
        "source_record_id": { "type": "string" },
        "source_term_exact": { "type": "string" },
        "extracted_candidate_id": { "type": ["string", "null"] },
        "normalized_candidate_id": { "type": ["string", "null"] },
        "canonical_id": { "type": "string" },
        "enrichment_version": { "type": "string" },
        "validation_record": { "type": "object" },
        "release_version": { "type": "string" }
      }
    },
    "provenance": {
      "type": "object",
      "required": ["origin_type", "extracted_by", "enriched_by", "enrichment_version"],
      "properties": {
        "origin_type": { "type": "string" },
        "extracted_by": { "type": "string" },
        "enriched_by": { "type": "string" },
        "enrichment_version": { "type": "string" }
      }
    },
    "tts": {
      "type": "object",
      "required": ["display_text", "speech_text", "preferred_reading", "pronunciation_type", "pause_after_term_ms"],
      "properties": {
        "display_text": { "type": "string" },
        "speech_text": { "type": "string" },
        "preferred_reading": { "type": "string" },
        "pronunciation_type": { "type": "string", "enum": ["standard_kanji_kana", "acronym_alphabet", "acronym_word", "mixed_compound", "numeric_compound"] },
        "pause_after_term_ms": { "type": "integer", "default": 1200 }
      }
    },
    "status": {
      "type": "string",
      "enum": ["production", "needs_review", "rejected", "candidate"]
    }
  }
}
```

---

## 3. Canonical Tri-Language Graph Schemas (Phase 1.3B)

The canonical graph stored under `data/canonical/` adheres to JSON Schema Draft 2020-12 specifications stored in `schemas/`.

### 3.1 Concept (`schemas/concept.schema.json`)
```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "Concept",
  "type": "object",
  "required": ["concept_id", "canonical_name", "primary_domain", "status"],
  "properties": {
    "concept_id": { "type": "string", "pattern": "^concept-[a-z0-9_-]+$" },
    "canonical_name": { "type": "string" },
    "domains": { "type": "array", "items": { "type": "string" } },
    "primary_domain": { "type": "string" },
    "status": { "type": "string", "enum": ["canonical", "candidate", "quarantine"] },
    "metadata": { "type": "object" },
    "created_at": { "type": "string", "format": "date-time" },
    "updated_at": { "type": "string", "format": "date-time" }
  }
}
```

### 3.2 Sense (`schemas/sense.schema.json`)
```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "Sense",
  "type": "object",
  "required": ["sense_id", "concept_id", "part_of_speech", "gloss_en", "gloss_ja", "gloss_vi", "status"],
  "properties": {
    "sense_id": { "type": "string", "pattern": "^sense-[a-z0-9_-]+$" },
    "concept_id": { "type": "string" },
    "part_of_speech": { "type": "string" },
    "gloss_en": { "type": "string" },
    "gloss_ja": { "type": "string" },
    "gloss_vi": { "type": "string" },
    "definition_en": { "type": ["string", "null"] },
    "definition_ja": { "type": ["string", "null"] },
    "definition_vi": { "type": ["string", "null"] },
    "register": { "type": "string" },
    "status": { "type": "string", "enum": ["verified", "candidate", "ambiguous"] }
  }
}
```

### 3.3 Expression (`schemas/expression.schema.json`)
```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "Expression",
  "type": "object",
  "required": ["expression_id", "concept_id", "sense_id", "language", "lemma", "display_form", "provenance_type", "license", "status"],
  "properties": {
    "expression_id": { "type": "string", "pattern": "^expr-[a-z]{2}-[a-z0-9_-]+$" },
    "concept_id": { "type": "string" },
    "sense_id": { "type": "string" },
    "language": { "type": "string", "enum": ["en", "ja", "vi"] },
    "lemma": { "type": "string" },
    "display_form": { "type": "string" },
    "reading": { "type": ["string", "null"] },
    "pronunciation": { "type": ["string", "null"] },
    "romanization": { "type": ["string", "null"] },
    "part_of_speech": { "type": "string" },
    "register": { "type": "string" },
    "language_metadata": { "type": "object" },
    "provenance_type": { "type": "string" },
    "source_evidence": { "type": "array" },
    "license": { "type": "string" },
    "status": { "type": "string", "enum": ["verified", "candidate", "quarantine"] }
  }
}
```

### 3.4 Classification (`schemas/classification.schema.json`)
```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "Classification",
  "type": "object",
  "required": ["classification_id", "target_type", "target_id", "classification_system", "classification_value", "classification_status", "source_id"],
  "properties": {
    "classification_id": { "type": "string" },
    "target_type": { "type": "string", "enum": ["concept", "sense", "expression"] },
    "target_id": { "type": "string" },
    "classification_system": { "type": "string" },
    "classification_value": { "type": "string" },
    "classification_status": { "type": "string", "enum": ["official", "source_derived", "corpus_derived", "community_consensus", "inferred", "ai_proposed"] },
    "source_id": { "type": "string" },
    "evidence": { "type": ["string", "null"] },
    "confidence": { "type": "string", "enum": ["HIGH", "MEDIUM", "LOW"] },
    "exam_metadata": { "type": "object" }
  }
}
```

