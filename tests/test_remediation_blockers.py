"""
tests/test_remediation_blockers.py
Comprehensive test suite verifying remediation of the two independent-review blockers:
1. Jōyō Provenance: KANJIDIC2/EDRDG derived, CC-BY-SA-3.0, source_derived, citing 文化庁 as authority_reference.
2. False Tri-Language Completeness: Honest reclassification of manual fields (BENCHMARK_CURATED, CURATED, INFERRED),
   support for partial concepts (EN+JA), zero fabricated Vietnamese translations, tracking ambiguous alignments in review queue,
   and computing tri-language completeness as a metric rather than preserving a false invariant.
"""

import json
import sys
from pathlib import Path
import pytest

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))
CANONICAL_DIR = BASE_DIR / "data" / "canonical"
RAW_DIR = BASE_DIR / "data" / "raw"
REPORTS_DIR = BASE_DIR / "reports" / "phase1_3c"


class TestBlocker1JoyoProvenanceRemediation:
    """Blocker 1: KANJIDIC2-derived Jōyō data cannot claim direct 文化庁 extraction."""

    def test_joyo_metadata_provenance(self):
        meta_file = RAW_DIR / "joyo" / "2010-official" / "metadata.json"
        assert meta_file.exists()
        with open(meta_file, "r", encoding="utf-8") as f:
            meta = json.load(f)

        assert meta["license"] == "CC-BY-SA-3.0"
        assert "EDRDG" in meta["organization"] or "Electronic Dictionary" in meta["organization"]
        assert meta["authority_level"] == "source_derived"
        assert meta["authority_level"] != "government_statutory"
        assert "文化庁" in meta.get("authority_reference", "")

    def test_joyo_adapter_emits_source_derived(self):
        from scripts.phase1_3c.adapters.production_adapters import JoyoOfficialAdapter
        adapter = JoyoOfficialAdapter()
        records = adapter.extract_kanji()
        assert len(records) == 2136
        for rec in records[:20]:
            ev = rec["source_evidence"]
            assert ev["origin"] == "source_derived"
            assert ev["license"] == "CC-BY-SA-3.0"
            assert ev["source_id"] == "joyo"

    def test_joyo_canonical_classifications_are_source_derived(self):
        with open(CANONICAL_DIR / "classifications.jsonl", "r", encoding="utf-8") as f:
            joyo_classes = [
                json.loads(line) for line in f
                if json.loads(line).get("system") == "JOYO_KANJI"
            ]

        assert len(joyo_classes) > 0
        for cl in joyo_classes:
            assert cl["provenance_type"] == "SOURCE_DERIVED"
            assert cl["provenance_type"] != "OFFICIAL_EXTRACTED"
            assert cl["source_id"] == "joyo"


class TestBlocker2TriLanguageCompletenessAndProvenance:
    """Blocker 2: Removal of false perfect tri-language invariant and honest provenance reclassification."""

    def test_manually_authored_benchmark_cannot_be_source_derived(self):
        """Rule: Manually authored benchmark expressions must be BENCHMARK_CURATED, not SOURCE_DERIVED."""
        with open(CANONICAL_DIR / "expressions.jsonl", "r", encoding="utf-8") as f:
            for line in f:
                e = json.loads(line)
                cid = e.get("concept_id", "")
                if cid.startswith("concept-poly-"):
                    assert e.get("provenance_type") in ("BENCHMARK_CURATED", "CURATED"), (
                        f"Benchmark expression {e['expression_id']} in {cid} has invalid provenance: {e.get('provenance_type')}"
                    )
                    assert e.get("provenance_type") != "SOURCE_DERIVED"
                    for ev in e.get("source_evidence", []):
                        assert ev.get("origin") in ("benchmark_curated", "curated")
                        assert ev.get("origin") != "source_derived"

    def test_partial_concepts_are_valid(self):
        """Rule: Concepts may be partial (e.g. EN + JA) without fabricated Vietnamese."""
        concept_to_langs = {}
        with open(CANONICAL_DIR / "expressions.jsonl", "r", encoding="utf-8") as f:
            for line in f:
                e = json.loads(line)
                concept_to_langs.setdefault(e["concept_id"], set()).add(e["language"])

        partial_en_ja = [cid for cid, langs in concept_to_langs.items() if langs == {"en", "ja"}]
        # Phase 1.4 fix: 1.3D legitimately resolved 645 of the 1,034 earlier partials; 389 genuinely partial remain.
        assert len(partial_en_ja) >= 389, f"Expected >= 389 partial concepts, got {len(partial_en_ja)}"

        # Verify that senses of partial concepts do not fabricate Vietnamese glosses
        partial_cids = set(partial_en_ja)
        with open(CANONICAL_DIR / "senses.jsonl", "r", encoding="utf-8") as f:
            for line in f:
                s = json.loads(line)
                if s["concept_id"] in partial_cids:
                    assert s.get("gloss_vi") is None, f"Partial concept {s['concept_id']} fabricated gloss_vi: {s.get('gloss_vi')}"
                    assert s.get("definition_vi") is None, f"Partial concept {s['concept_id']} fabricated def_vi: {s.get('definition_vi')}"

    def test_missing_vi_ja_en_does_not_fail_canonical_validation(self):
        """Rule: Missing VI/JA/EN does not fail canonical validation."""
        from scripts.phase1_3b.models import Sense, Concept, Expression

        # Construct a partial concept (EN + JA only)
        c = Concept(concept_id="concept-test-partial", canonical_name="test_partial")
        s = Sense(
            sense_id="sense-test-partial-01",
            concept_id="concept-test-partial",
            part_of_speech="noun",
            gloss_en="partial concept test",
            gloss_ja="テスト",
            gloss_vi=None
        )
        e_en = Expression(
            expression_id="expr-en-test-partial",
            concept_id="concept-test-partial",
            sense_id="sense-test-partial-01",
            language="en",
            lemma="test",
            display_form="test",
            provenance_type="SOURCE_DERIVED"
        )
        e_ja = Expression(
            expression_id="expr-ja-test-partial",
            concept_id="concept-test-partial",
            sense_id="sense-test-partial-01",
            language="ja",
            lemma="テスト",
            display_form="テスト",
            provenance_type="SOURCE_DERIVED"
        )

        assert s.gloss_vi is None
        assert c.concept_id == "concept-test-partial"
        assert e_en.language == "en"
        assert e_ja.language == "ja"

    def test_complete_tri_language_status_is_a_computed_metric(self):
        """Rule: Tri-language completeness is a computed metric, not a forced invariant."""
        concepts = set()
        with open(CANONICAL_DIR / "concepts.jsonl", "r", encoding="utf-8") as f:
            for line in f:
                concepts.add(json.loads(line)["concept_id"])

        concept_to_langs = {}
        with open(CANONICAL_DIR / "expressions.jsonl", "r", encoding="utf-8") as f:
            for line in f:
                e = json.loads(line)
                concept_to_langs.setdefault(e["concept_id"], set()).add(e["language"])

        # Phase 1.4: assert on the sealed baseline subset (post-1.3D truth), not on pre-1.3D counts.
        from tests._baseline import baseline_concept_ids
        base = baseline_concept_ids()
        complete_tri = sum(1 for cid in base if concept_to_langs.get(cid, set()) >= {"en", "ja", "vi"})
        partial_en_ja = sum(1 for cid in base if concept_to_langs.get(cid) == {"en", "ja"})

        assert len(base) == 2106
        assert complete_tri == 1717          # Phase 1.3D closure
        assert partial_en_ja == 389
        assert complete_tri + partial_en_ja == len(base)
        # completeness remains a *computed* metric over the whole corpus, never a forced invariant
        all_complete = sum(1 for cid in concepts if concept_to_langs.get(cid, set()) >= {"en", "ja", "vi"})
        assert all_complete >= complete_tri

    def test_every_source_derived_field_resolves_to_raw_evidence(self):
        """Rule: Every SOURCE_DERIVED expression must resolve to authentic raw evidence in data/raw/."""
        with open(CANONICAL_DIR / "expressions.jsonl", "r", encoding="utf-8") as f:
            for line in f:
                e = json.loads(line)
                if e.get("provenance_type") == "SOURCE_DERIVED":
                    ev_list = e.get("source_evidence", [])
                    assert len(ev_list) > 0, f"Expression {e['expression_id']} missing source_evidence"
                    for ev in ev_list:
                        src_id = ev.get("source_id")
                        assert src_id is not None
                        src_dir = RAW_DIR / src_id
                        assert src_dir.exists(), f"Source directory {src_dir} missing for {e['expression_id']}"
                        snapshots = list(src_dir.glob("*"))
                        assert len(snapshots) > 0, f"No snapshots found for source {src_id}"
                        assert ev.get("origin") == "source_derived"
                        assert ev.get("source_locator") is not None
                        assert ev.get("extracted_value") is not None

    def test_inferred_classifications_honest_labeling(self):
        """Rule: CEFR and EIKEN grade mapping must be labeled INFERRED."""
        with open(CANONICAL_DIR / "classifications.jsonl", "r", encoding="utf-8") as f:
            for line in f:
                cl = json.loads(line)
                if cl.get("system") in ("CEFR", "EIKEN"):
                    assert cl.get("provenance_type") == "INFERRED", (
                        f"Classification {cl['classification_id']} must have provenance_type INFERRED, got {cl.get('provenance_type')}"
                    )
                    assert cl.get("status") == "inferred"

    def test_professional_800_records_intact_and_tri_complete(self):
        """Requirement: All 800 professional concepts remain 100% frozen and complete tri-language."""
        legacy_file = CANONICAL_DIR / "legacy_mapping.json"
        assert legacy_file.exists()
        with open(legacy_file, "r", encoding="utf-8") as f:
            mapping = json.load(f)
        assert len(mapping) == 800

        concept_to_langs = {}
        with open(CANONICAL_DIR / "expressions.jsonl", "r", encoding="utf-8") as f:
            for line in f:
                e = json.loads(line)
                cid = e["concept_id"]
                if cid.startswith("concept-pro-"):
                    concept_to_langs.setdefault(cid, set()).add(e["language"])

        assert len(concept_to_langs) == 800
        for cid, langs in concept_to_langs.items():
            assert langs == {"en", "ja", "vi"}, f"Professional record {cid} not tri-complete: {langs}"
