"""
scripts/phase1_3b/models.py
Canonical entity definitions for Phase 1.3B:
Tri-Language Learning Graph (Concept -> Sense -> Expression + Classifications).
"""

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Any, Set
from enum import Enum
import hashlib
import json


class LanguageCode(str, Enum):
    EN = "en"
    JA = "ja"
    VI = "vi"


class ClassificationStatus(str, Enum):
    OFFICIAL = "official"                         # Issued directly by authorized organization
    SOURCE_DERIVED = "source_derived"             # Directly stated in published academic/corpus source
    CORPUS_DERIVED = "corpus_derived"             # Computed deterministically from raw corpus frequency
    COMMUNITY_CONSENSUS = "community_consensus"   # Standard community/pedagogical agreement (e.g. widely accepted JLPT lists)
    INFERRED = "inferred"                         # Statistically or rule inferred
    AI_PROPOSED = "ai_proposed"                   # Proposed by AI model, pending review


class ClassificationSystem(str, Enum):
    # Japanese
    JOYO_KANJI = "JOYO_KANJI"
    SCHOOL_GRADE = "SCHOOL_GRADE"
    JLPT = "JLPT"
    JP_FREQUENCY = "JP_FREQUENCY"
    JP_CORE = "JP_CORE"
    
    # English
    CEFR = "CEFR"
    NGSL = "NGSL"
    NGSL_SPOKEN = "NGSL_SPOKEN"
    NAWL = "NAWL"
    BUSINESS_SERVICE_LIST = "BUSINESS_SERVICE_LIST"
    TOEIC = "TOEIC"
    EIKEN = "EIKEN"
    IELTS = "IELTS"
    TOEFL = "TOEFL"
    EN_FREQUENCY = "EN_FREQUENCY"
    
    # Vietnamese
    VI_CORE_500 = "VI_CORE_500"
    VI_CORE_1000 = "VI_CORE_1000"
    VI_CORE_2000 = "VI_CORE_2000"
    VI_CORE_5000 = "VI_CORE_5000"
    VI_FREQUENCY = "VI_FREQUENCY"
    VI_SPOKEN = "VI_SPOKEN"
    
    # Professional
    PROFESSIONAL_TIER = "PROFESSIONAL_TIER"


class TriLanguageStatus(str, Enum):
    COMPLETE = "complete"                       # Verified EN + JA + VI expressions exist
    PARTIAL = "partial"                         # At least 2 languages exist
    MISSING_EN = "missing_en"
    MISSING_JA = "missing_ja"
    MISSING_VI = "missing_vi"
    AMBIGUOUS_ALIGNMENT = "ambiguous_alignment" # Polysemy or sense mismatch requiring manual review


class RelationshipType(str, Enum):
    SYNONYM_OF = "SYNONYM_OF"
    ANTONYM_OF = "ANTONYM_OF"
    ABBREVIATION_OF = "ABBREVIATION_OF"
    VARIANT_OF = "VARIANT_OF"
    DERIVED_FROM = "DERIVED_FROM"
    SINO_COGNATE_OF = "SINO_COGNATE_OF"         # Hán-Việt ↔ Sino-Japanese cognate
    HYPERNYM_OF = "HYPERNYM_OF"
    HYPONYM_OF = "HYPONYM_OF"


class ValidationDimension(str, Enum):
    SOURCE_VERIFIED = "SOURCE_VERIFIED"
    LICENSE_VERIFIED = "LICENSE_VERIFIED"
    STRUCTURE_VERIFIED = "STRUCTURE_VERIFIED"
    LEXICAL_VERIFIED = "LEXICAL_VERIFIED"
    SEMANTIC_ALIGNMENT_VERIFIED = "SEMANTIC_ALIGNMENT_VERIFIED"
    TRANSLATION_VERIFIED = "TRANSLATION_VERIFIED"
    PRONUNCIATION_VERIFIED = "PRONUNCIATION_VERIFIED"
    CLASSIFICATION_VERIFIED = "CLASSIFICATION_VERIFIED"
    EXAMPLE_VERIFIED = "EXAMPLE_VERIFIED"
    AI_ENRICHMENT_VERIFIED = "AI_ENRICHMENT_VERIFIED"


# ==============================================================================
# 1. Canonical Graph Entities
# ==============================================================================

@dataclass
class Concept:
    """Language-independent semantic anchor."""
    concept_id: str                              # e.g. "concept-000101"
    canonical_name: str                          # e.g. "financial_depreciation"
    domains: List[str] = field(default_factory=list)
    primary_domain: str = "general"
    status: str = "canonical"                    # "canonical", "candidate", "quarantine"
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = "2026-10-01T00:00:00Z"
    updated_at: str = "2026-10-01T00:00:00Z"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Sense:
    """Specific meaning / definition belonging to a Concept."""
    sense_id: str                                # e.g. "sense-000101-01"
    concept_id: str
    part_of_speech: str                          # "noun", "verb", "adjective", etc.
    gloss_en: str
    gloss_ja: str
    gloss_vi: str
    definition_en: Optional[str] = None
    definition_ja: Optional[str] = None
    definition_vi: Optional[str] = None
    register: str = "general"                    # "professional", "general", "academic", "spoken"
    status: str = "verified"                     # "verified", "candidate", "ambiguous"
    created_at: str = "2026-10-01T00:00:00Z"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Expression:
    """Language-specific lexical realization for a Sense."""
    expression_id: str                           # e.g. "expr-ja-000101-01"
    concept_id: str
    sense_id: str
    language: str                                # "en", "ja", "vi"
    lemma: str                                   # Canonical dictionary lemma
    display_form: str                            # Surface presentation form
    reading: Optional[str] = None                # Kana for JA
    pronunciation: Optional[str] = None          # IPA for EN, Tone/regional for VI
    romanization: Optional[str] = None           # Hepburn for JA
    part_of_speech: str = "noun"
    register: str = "general"
    usage_notes: Optional[str] = None
    language_metadata: Dict[str, Any] = field(default_factory=dict)
    # Provenance and License tracking
    provenance_type: str = "OFFICIAL_EXTRACTED"  # OFFICIAL_EXTRACTED, OFFICIAL_CURATED, INTERNAL_CURATED, MODEL_ASSISTED
    source_evidence: List[Dict[str, Any]] = field(default_factory=list)
    license: str = "CC-BY-4.0"
    status: str = "verified"                     # "verified", "candidate", "quarantine"
    created_at: str = "2026-10-01T00:00:00Z"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Classification:
    """Many-to-many learning classification attached to Concept, Sense, or Expression."""
    classification_id: str                       # e.g. "class-000101-01"
    target_type: str                             # "concept", "sense", "expression"
    target_id: str
    classification_system: str                   # From ClassificationSystem
    classification_value: str                    # e.g. "B1", "N3", "Core 1000", "Grade 4"
    classification_status: str                   # From ClassificationStatus
    source_id: str                               # e.g. "ngsl-project", "joyo-kanji-agency"
    evidence: Optional[str] = None
    confidence: str = "HIGH"                     # "HIGH", "MEDIUM", "LOW"
    exam_metadata: Dict[str, Any] = field(default_factory=dict)  # IELTS topic, TOEFL domain, etc.
    created_at: str = "2026-10-01T00:00:00Z"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Example:
    """Pedagogical sentence example linked to a Sense."""
    example_id: str                              # e.g. "ex-000101-01"
    sense_id: str
    concept_id: str
    language: str                                # "en", "ja", "vi"
    text: str
    translation_links: Dict[str, str] = field(default_factory=dict)  # {"en": "...", "vi": "...", "ja": "..."}
    source_id: str = "curated_pedagogical"
    source_record_id: Optional[str] = None
    license: str = "CC-BY-4.0"
    attribution: str = "Open Language Database"
    review_status: str = "verified"              # "verified", "pending", "quarantined"
    created_at: str = "2026-10-01T00:00:00Z"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Relationship:
    """Semantic or morphological edge between Concepts, Senses, or Expressions."""
    relationship_id: str                         # e.g. "rel-000101-01"
    source_type: str                             # "concept", "sense", "expression"
    source_id: str
    target_type: str                             # "concept", "sense", "expression"
    target_id: str
    relationship_type: str                       # From RelationshipType
    bidirectional: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)
    provenance: Dict[str, Any] = field(default_factory=dict)
    created_at: str = "2026-10-01T00:00:00Z"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class TriLanguageCoverage:
    """Coverage metrics at Concept / Sense level."""
    concept_id: str
    sense_id: str
    has_en: bool
    has_ja: bool
    has_vi: bool
    en_status: str                               # "verified", "candidate", "missing"
    ja_status: str                               # "verified", "candidate", "missing"
    vi_status: str                               # "verified", "candidate", "missing"
    tri_language_status: str                     # From TriLanguageStatus

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class OriginType(str, Enum):
    SOURCE_DERIVED = "source_derived"
    CORPUS_DERIVED = "corpus_derived"
    HUMAN_CURATED = "human_curated"
    AI_GENERATED = "ai_generated"


LanguageEnum = LanguageCode


@dataclass
class SourceEvidence:
    """Auditable evidence tracking for ingested sources and values."""
    source_id: str
    source_version: str = "1.0"
    source_locator: str = ""
    source_record_id: Optional[str] = None
    field_name: Optional[str] = None
    extracted_value: Optional[str] = None
    origin: str = OriginType.SOURCE_DERIVED.value
    model: Optional[str] = None
    generation_version: Optional[str] = None
    input_hash: Optional[str] = None
    generated_at: Optional[str] = None
    raw_sha256: Optional[str] = None
    curated_sha256: Optional[str] = None
    retrieved_at: Optional[str] = None
    curated_at: Optional[str] = None
    source_url: Optional[str] = None
    reference_url: Optional[str] = None
    license: str = "CC-BY-4.0"
    commercial_use: bool = True
    redistribution_allowed: bool = True
    derivatives_allowed: bool = True
    attribution_required: bool = True
    share_alike: bool = False
    review_status: str = "verified"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

