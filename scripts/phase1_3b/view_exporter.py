"""
scripts/phase1_3b/view_exporter.py
Generates projected pedagogical learning views from the canonical Tri-Language Graph.
Prevents duplicate lexical record proliferation by projecting many-to-many classifications.
"""

from pathlib import Path
from typing import Dict, List, Any, Optional
import json
from collections import defaultdict

from scripts.phase1_3b.models import (
    Concept,
    Sense,
    Expression,
    Classification
)

BASE_DIR = Path(__file__).resolve().parent.parent.parent
EXPORTS_DIR = BASE_DIR / "data" / "exports"


class LearningViewExporter:
    """Exports targeted learning decks and curriculum subsets from canonical storage."""

    def __init__(self, exports_dir: Optional[Path] = None):
        self.exports_dir = exports_dir or EXPORTS_DIR

    def export_all_views(
        self,
        concepts: Dict[str, Concept],
        senses: Dict[str, Sense],
        expressions_by_sense: Dict[str, Dict[str, List[Expression]]],
        classifications_by_target: Dict[str, List[Classification]]
    ) -> Dict[str, int]:
        """Projects and generates all standard learning views."""
        views_generated: Dict[str, int] = {}
        
        # Prepare subdirectories
        (self.exports_dir / "cross_language").mkdir(parents=True, exist_ok=True)
        (self.exports_dir / "japanese").mkdir(parents=True, exist_ok=True)
        (self.exports_dir / "english").mkdir(parents=True, exist_ok=True)
        (self.exports_dir / "vietnamese").mkdir(parents=True, exist_ok=True)

        # 1. Cross-Language: EN_JA_VI_CORE
        core_records = []
        biz_records = []

        for s_id, sense in senses.items():
            concept = concepts.get(sense.concept_id)
            if not concept:
                continue
            exprs = expressions_by_sense.get(s_id, {})
            classes = classifications_by_target.get(concept.concept_id, []) + classifications_by_target.get(s_id, [])
            
            en_expr = exprs.get("en", [None])[0]
            ja_expr = exprs.get("ja", [None])[0]
            vi_expr = exprs.get("vi", [None])[0]

            if en_expr and ja_expr and vi_expr:
                rec = {
                    "concept_id": concept.concept_id,
                    "canonical_name": concept.canonical_name,
                    "sense_id": s_id,
                    "domain": concept.primary_domain,
                    "en": {
                        "lemma": en_expr.lemma,
                        "pronunciation": en_expr.pronunciation,
                        "pos": en_expr.part_of_speech
                    },
                    "ja": {
                        "lemma": ja_expr.lemma,
                        "reading": ja_expr.reading,
                        "romaji": ja_expr.romanization
                    },
                    "vi": {
                        "lemma": vi_expr.lemma,
                        "sino_vietnamese": vi_expr.language_metadata.get("sino_vietnamese")
                    },
                    "classifications": [
                        {"system": c.classification_system, "value": c.classification_value, "status": c.classification_status}
                        for c in classes
                    ],
                    "license": "CC-BY-4.0"
                }
                core_records.append(rec)
                if concept.primary_domain in ("business", "accounting", "finance", "legal"):
                    biz_records.append(rec)

        self._write_jsonl(self.exports_dir / "cross_language" / "en_ja_vi_core.jsonl", core_records)
        views_generated["cross_language/en_ja_vi_core"] = len(core_records)

        self._write_jsonl(self.exports_dir / "cross_language" / "business_en_ja_vi.jsonl", biz_records)
        views_generated["cross_language/business_en_ja_vi"] = len(biz_records)

        # 2. Japanese Views: JLPT_N5, JOYO_KANJI
        jlpt_n5_records = []
        joyo_records = []

        for s_id, sense in senses.items():
            concept = concepts.get(sense.concept_id)
            if not concept:
                continue
            ja_exprs = expressions_by_sense.get(s_id, {}).get("ja", [])
            if not ja_exprs:
                continue
            ja_expr = ja_exprs[0]
            classes = classifications_by_target.get(concept.concept_id, []) + classifications_by_target.get(s_id, [])
            
            has_n5 = any(c.classification_system == "JLPT" and c.classification_value == "N5" for c in classes)
            if has_n5:
                jlpt_n5_records.append({
                    "concept_id": concept.concept_id,
                    "lemma": ja_expr.lemma,
                    "reading": ja_expr.reading,
                    "en_gloss": sense.gloss_en,
                    "vi_gloss": sense.gloss_vi,
                    "jlpt": "N5"
                })
            
            has_joyo = any(c.classification_system == "JOYO_KANJI" for c in classes)
            if has_joyo:
                joyo_class = next(c for c in classes if c.classification_system == "JOYO_KANJI")
                joyo_records.append({
                    "concept_id": concept.concept_id,
                    "kanji": ja_expr.lemma,
                    "reading": ja_expr.reading,
                    "grade": joyo_class.classification_value,
                    "en_meaning": sense.gloss_en,
                    "vi_meaning": sense.gloss_vi
                })

        self._write_jsonl(self.exports_dir / "japanese" / "jlpt_n5.jsonl", jlpt_n5_records)
        views_generated["japanese/jlpt_n5"] = len(jlpt_n5_records)

        self._write_jsonl(self.exports_dir / "japanese" / "joyo_kanji.jsonl", joyo_records)
        views_generated["japanese/joyo_kanji"] = len(joyo_records)

        # 3. English Views: NGSL_CORE, CEFR_B1, TOEIC_ESSENTIAL
        ngsl_records = []
        cefr_b1_records = []
        toeic_records = []

        for s_id, sense in senses.items():
            concept = concepts.get(sense.concept_id)
            if not concept:
                continue
            en_exprs = expressions_by_sense.get(s_id, {}).get("en", [])
            if not en_exprs:
                continue
            en_expr = en_exprs[0]
            classes = classifications_by_target.get(concept.concept_id, []) + classifications_by_target.get(s_id, [])

            if any(c.classification_system == "NGSL" for c in classes):
                ngsl_records.append({
                    "concept_id": concept.concept_id,
                    "lemma": en_expr.lemma,
                    "ipa": en_expr.pronunciation,
                    "ja_translation": sense.gloss_ja,
                    "vi_translation": sense.gloss_vi
                })
            if any(c.classification_system == "CEFR" and c.classification_value == "B1" for c in classes):
                cefr_b1_records.append({
                    "concept_id": concept.concept_id,
                    "lemma": en_expr.lemma,
                    "cefr": "B1",
                    "ja_translation": sense.gloss_ja,
                    "vi_translation": sense.gloss_vi
                })
            if any(c.classification_system == "TOEIC" for c in classes):
                toeic_records.append({
                    "concept_id": concept.concept_id,
                    "lemma": en_expr.lemma,
                    "ja_translation": sense.gloss_ja,
                    "vi_translation": sense.gloss_vi
                })

        self._write_jsonl(self.exports_dir / "english" / "ngsl_core.jsonl", ngsl_records)
        views_generated["english/ngsl_core"] = len(ngsl_records)

        self._write_jsonl(self.exports_dir / "english" / "cefr_b1.jsonl", cefr_b1_records)
        views_generated["english/cefr_b1"] = len(cefr_b1_records)

        self._write_jsonl(self.exports_dir / "english" / "toeic_essential.jsonl", toeic_records)
        views_generated["english/toeic_essential"] = len(toeic_records)

        # 4. Vietnamese Views: VI_CORE_500
        vi_core_records = []
        for s_id, sense in senses.items():
            concept = concepts.get(sense.concept_id)
            if not concept:
                continue
            vi_exprs = expressions_by_sense.get(s_id, {}).get("vi", [])
            if not vi_exprs:
                continue
            vi_expr = vi_exprs[0]
            classes = classifications_by_target.get(concept.concept_id, []) + classifications_by_target.get(s_id, [])

            if any(c.classification_system == "VI_CORE_500" for c in classes):
                vi_core_records.append({
                    "concept_id": concept.concept_id,
                    "lemma": vi_expr.lemma,
                    "sino_vietnamese": vi_expr.language_metadata.get("sino_vietnamese"),
                    "ja_translation": sense.gloss_ja,
                    "en_translation": sense.gloss_en
                })

        self._write_jsonl(self.exports_dir / "vietnamese" / "vi_core_500.jsonl", vi_core_records)
        views_generated["vietnamese/vi_core_500"] = len(vi_core_records)

        return views_generated

    def generate_all_views(self) -> Dict[str, List[Dict[str, Any]]]:
        """Loads and returns all exported views from disk as a dict of view_name -> list of records."""
        views: Dict[str, List[Dict[str, Any]]] = {}
        for view_path in sorted(self.exports_dir.glob("*/*.jsonl")):
            rel_name = f"{view_path.parent.name}/{view_path.stem}"
            with open(view_path, "r", encoding="utf-8") as f:
                views[rel_name] = [json.loads(line) for line in f if line.strip()]
        return views

    def _write_jsonl(self, path: Path, records: List[Dict[str, Any]]):
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            for r in records:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")

