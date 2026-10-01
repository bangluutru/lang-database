"""
scripts/phase1_3b/legacy_bridge.py
Bidirectional projection layer between legacy Phase 1.1c production records (jp-pro-*)
and the canonical Tri-Language Learning Graph (Concept -> Sense -> Expression).
"""

import json
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional

from scripts.phase1_3b.models import (
    Concept,
    Sense,
    Expression,
    Classification,
    ClassificationSystem,
    ClassificationStatus,
    Example,
    TriLanguageCoverage,
    TriLanguageStatus
)

BASE_DIR = Path(__file__).resolve().parent.parent.parent


class LegacyBridge:
    """Manages lossless projection between legacy jp-pro-* records and canonical graph."""
    
    def __init__(self, base_dir: Optional[Path] = None):
        self.base_dir = base_dir or BASE_DIR
        self.legacy_mapping: Dict[str, Dict[str, Any]] = {}
        self.reverse_mapping: Dict[str, str] = {}  # concept_id -> legacy_id

    def project_legacy_record(
        self, record: Dict[str, Any]
    ) -> Tuple[Concept, Sense, List[Expression], List[Classification], List[Example], TriLanguageCoverage]:
        """Projects a single legacy jp-pro-* record into canonical graph entities."""
        legacy_id = record["id"]
        # Example ID: "jp-pro-accounting-000001"
        parts = legacy_id.split("-")
        domain_tag = parts[2] if len(parts) >= 4 else "general"
        idx = parts[-1]
        
        concept_id = f"concept-pro-{domain_tag}-{idx}"
        sense_id = f"sense-pro-{domain_tag}-{idx}-01"
        
        # 1. Concept
        term_obj = record.get("term", {})
        surf = term_obj.get("surface", "")
        primary_domain = record.get("domain", {}).get("primary", domain_tag)
        sec_domains = record.get("domain", {}).get("secondary", [])
        
        concept = Concept(
            concept_id=concept_id,
            canonical_name=f"{primary_domain}_{surf}",
            domains=[primary_domain] + [d for d in sec_domains if d != primary_domain],
            primary_domain=primary_domain,
            status="canonical",
            metadata={"legacy_id": legacy_id, "semantic_class": record.get("domain", {}).get("semantic_class")},
            created_at="2026-10-01T00:00:00Z"
        )
        
        # 2. Sense
        meaning_obj = record.get("meaning", {})
        en_meaning = meaning_obj.get("en", {})
        vi_meaning = meaning_obj.get("vi", {})
        
        sense = Sense(
            sense_id=sense_id,
            concept_id=concept_id,
            part_of_speech=record.get("concept", {}).get("type", "compound_noun"),
            gloss_en=en_meaning.get("preferred") or en_meaning.get("short") or "",
            gloss_ja=surf,
            gloss_vi=vi_meaning.get("preferred") or vi_meaning.get("short") or "",
            definition_en=en_meaning.get("short"),
            definition_ja=f"{surf} (実務用語)",
            definition_vi=vi_meaning.get("explanation"),
            register="professional",
            status="verified",
            created_at="2026-10-01T00:00:00Z"
        )
        
        # 3. Expressions (JA, EN, VI)
        expressions: List[Expression] = []
        
        # JA Expression
        ja_expr_id = f"expr-ja-pro-{domain_tag}-{idx}"
        ja_expr = Expression(
            expression_id=ja_expr_id,
            concept_id=concept_id,
            sense_id=sense_id,
            language="ja",
            lemma=surf,
            display_form=surf,
            reading=term_obj.get("reading"),
            romanization=term_obj.get("romaji"),
            part_of_speech="noun",
            register="professional",
            language_metadata={
                "romaji_metadata": term_obj.get("romaji_metadata", {}),
                "tts": record.get("tts", {})
            },
            provenance_type="OFFICIAL_EXTRACTED",
            source_evidence=record.get("sources", []),
            license="PDL-1.0 / CC-BY-4.0",
            status="verified",
            created_at="2026-10-01T00:00:00Z"
        )
        expressions.append(ja_expr)
        
        # EN Expression
        en_lemma = en_meaning.get("preferred") or en_meaning.get("short") or ""
        en_expr_id = f"expr-en-pro-{domain_tag}-{idx}"
        en_expr = Expression(
            expression_id=en_expr_id,
            concept_id=concept_id,
            sense_id=sense_id,
            language="en",
            lemma=en_lemma,
            display_form=en_lemma,
            part_of_speech="noun",
            register="professional",
            language_metadata={"alternatives": en_meaning.get("alternatives", [])},
            provenance_type="OFFICIAL_CURATED",
            license="CC-BY-4.0",
            status="verified",
            created_at="2026-10-01T00:00:00Z"
        )
        expressions.append(en_expr)
        
        # VI Expression
        vi_lemma = vi_meaning.get("preferred") or vi_meaning.get("short") or ""
        vi_expr_id = f"expr-vi-pro-{domain_tag}-{idx}"
        vi_expr = Expression(
            expression_id=vi_expr_id,
            concept_id=concept_id,
            sense_id=sense_id,
            language="vi",
            lemma=vi_lemma,
            display_form=vi_lemma,
            part_of_speech="noun",
            register="professional",
            language_metadata={"professional_context": vi_meaning.get("professional_context")},
            provenance_type="OFFICIAL_CURATED",
            license="CC-BY-4.0",
            status="verified",
            created_at="2026-10-01T00:00:00Z"
        )
        expressions.append(vi_expr)
        
        # 4. Classifications
        classifications: List[Classification] = []
        tier = record.get("professional_level", {}).get("tier")
        if tier:
            classifications.append(Classification(
                classification_id=f"class-tier-{domain_tag}-{idx}",
                target_type="concept",
                target_id=concept_id,
                classification_system=ClassificationSystem.PROFESSIONAL_TIER.value,
                classification_value=tier,
                classification_status=ClassificationStatus.OFFICIAL.value,
                source_id="jp-pro-vocabulary-spec",
                evidence=f"Tier assigned by professional frequency weighting: score {record.get('priority', {}).get('score', 0)}"
            ))
            
        # 5. Examples
        examples: List[Example] = []
        for i, ex in enumerate(record.get("examples", [])):
            examples.append(Example(
                example_id=f"ex-pro-{domain_tag}-{idx}-{i+1:02d}",
                sense_id=sense_id,
                concept_id=concept_id,
                language="ja",
                text=ex.get("ja", ""),
                translation_links={
                    "vi": ex.get("vi", ""),
                    "en": ex.get("en", "")
                },
                source_id="jp-pro-pilot-examples",
                license="CC-BY-4.0",
                review_status=ex.get("status", "verified")
            ))
            
        # 6. Tri-Language Coverage
        coverage = TriLanguageCoverage(
            concept_id=concept_id,
            sense_id=sense_id,
            has_en=bool(en_lemma),
            has_ja=bool(surf),
            has_vi=bool(vi_lemma),
            en_status="verified" if en_lemma else "missing",
            ja_status="verified" if surf else "missing",
            vi_status="verified" if vi_lemma else "missing",
            tri_language_status=TriLanguageStatus.COMPLETE.value if (en_lemma and surf and vi_lemma) else TriLanguageStatus.PARTIAL.value
        )
        
        # Record mapping
        self.legacy_mapping[legacy_id] = {
            "legacy_id": legacy_id,
            "concept_id": concept_id,
            "sense_id": sense_id,
            "ja_expression_id": ja_expr_id,
            "en_expression_id": en_expr_id,
            "vi_expression_id": vi_expr_id,
            "expression_ids": [ja_expr_id, en_expr_id, vi_expr_id]
        }
        self.reverse_mapping[concept_id] = legacy_id

        
        return concept, sense, expressions, classifications, examples, coverage

    def project_production_dataset(
        self, vocab_path: Optional[Path] = None
    ) -> Dict[str, List[Any]]:
        """Projects full or sample production dataset into canonical lists."""
        target_path = vocab_path or (self.base_dir / "data" / "production" / "vocabulary.jsonl")
        
        concepts = []
        senses = []
        expressions = []
        classifications = []
        examples = []
        coverages = []
        
        with open(target_path, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                record = json.loads(line)
                c, s, exprs, classes, exs, cov = self.project_legacy_record(record)
                concepts.append(c)
                senses.append(s)
                expressions.extend(exprs)
                classifications.extend(classes)
                examples.extend(exs)
                coverages.append(cov)
                
        return {
            "concepts": concepts,
            "senses": senses,
            "expressions": expressions,
            "classifications": classifications,
            "examples": examples,
            "coverages": coverages
        }

    def save_legacy_mapping(self, out_path: Optional[Path] = None):
        """Persists the machine-readable mapping table for external consumers."""
        dest = out_path or (self.base_dir / "data" / "canonical" / "legacy_mapping.json")
        dest.parent.mkdir(parents=True, exist_ok=True)
        with open(dest, "w", encoding="utf-8") as f:
            json.dump(self.legacy_mapping, f, indent=2, ensure_ascii=False)
