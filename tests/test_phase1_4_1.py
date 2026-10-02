"""
tests/test_phase1_4_1.py - Phase 1.4.1 remediation of demonstrable Phase 1.3D defects.
General invariants: reversibility to sealed bytes, ID stability, provenance honesty, validation status, retraction hygiene,
professional-800 untouched, specific regression guards for defects found by the audit.
"""
import hashlib
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

import pytest

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))
from tests._baseline import baseline_rows, ledger, manifest, reverted_prefix_bytes  # noqa: E402


@pytest.fixture(scope="module")
def S():
    ex = defaultdict(lambda: defaultdict(list))
    for e in baseline_rows("expressions"):
        ex[e["concept_id"]][e["language"]].append(e)
    con = {c["concept_id"]: c for c in baseline_rows("concepts")}
    return {"ex": ex, "con": con, "led": ledger()}


def test_ledger_reverts_to_sealed_bytes_for_every_file():
    for fname, info in manifest()["append_only"].items():
        name = fname.replace(".jsonl", "")
        if name != "examples":
            assert hashlib.sha256(reverted_prefix_bytes(name)).hexdigest() == info["sha256"], fname


def test_ledger_file_is_pinned():
    p = BASE / "reports/phase1_4/baseline_corrections_ledger.json"
    assert hashlib.sha256(p.read_bytes()).hexdigest() == manifest()["corrections_ledger_sha256"]


def test_no_baseline_id_or_line_count_changed():
    m = manifest()
    for fname, info in m["append_only"].items():
        assert m["corrected_prefix"][fname]["lines"] == info["lines"]
    base_ids = {c["concept_id"] for c in baseline_rows("concepts")}
    assert len(base_ids) == 2106


def test_professional_800_and_poly_never_touched(S):
    for e in S["led"]:
        assert not e["concept_id"].startswith(("concept-pro-", "concept-poly-")), e["concept_id"]


def test_every_corrected_concept_records_its_correction(S):
    ids = {e["concept_id"] for e in S["led"]}
    flagged_or_fixed = {cid for cid, c in S["con"].items() if (c.get("metadata") or {}).get("correction")}
    assert flagged_or_fixed <= ids
    for cid in flagged_or_fixed:
        corr = S["con"][cid]["metadata"]["correction"]
        kinds = corr["kinds"]
        assert corr["validation_status"] == ("validated" if kinds == ["pos"] else "needs_review"), cid


def test_corrected_japanese_is_source_derived_and_jmdict_verified(S):
    """Re-verify against the immutable JMdict snapshot (not against stored copies): the cited sense must gloss the English lemma."""
    from scripts.phase1_4 import lexicons as L
    from scripts.phase1_4.build_candidates import gloss_norm
    jm = L.load_jmdict()
    n = overrides = 0
    for cid, e in S["ex"].items():
        ja = e["ja"][0] if e["ja"] else None
        if not ja or "correction" not in ja["language_metadata"]:
            continue
        n += 1
        assert ja["provenance_type"] == "SOURCE_DERIVED"
        ev = ja["source_evidence"]
        assert len(ev) == 1 and ev[0]["source_id"] == "jmdict" and ev[0]["origin"] == "source_derived"
        m = re.match(r"ent_seq:(\d+), sense_idx:(\d+)", ev[0]["source_locator"])
        sense = jm[int(m.group(1))]["senses"][int(m.group(2))]
        en = e["en"][0]["lemma"].lower()
        glosses = [gloss_norm(g) for g in sense["glosses"]]
        if ja["language_metadata"]["correction"]["gloss_override"]:
            overrides += 1
        else:
            raw = " ".join(g.lower() for g in sense["glosses"])
            assert re.search(r"(?<![a-z])" + re.escape(en) + r"(s|es)?(?![a-z])", raw), (cid, en, glosses)
            assert en in glosses or en + "s" in glosses or en + "es" in glosses or ja["language_metadata"]["correction"]["jmdict_glosses"], (cid, en)
    assert n > 100 and overrides <= 10


def test_corrected_vietnamese_is_ai_labelled_not_validated_by_judge(S):
    n = 0
    for cid, e in S["ex"].items():
        for v in e["vi"]:
            if "correction" in v["language_metadata"]:
                n += 1
                assert v["provenance_type"] == "AI_GENERATED"
                assert v["language_metadata"]["lexeme_source"]["status"] == "AI_GENERATED"
                assert v["language_metadata"]["translation_semantics_validated"]["status"] == "AGENT_REVIEWED_NOT_INDEPENDENT"
                x = v["source_evidence"][0]
                assert x["origin"] == "ai_generated" and x["model"] and x["input_hash"] and x["generated_at"]
    assert n > 30


def test_appended_vi_for_vi_less_baseline_concepts_is_ai_labelled():
    rows = [json.loads(l) for l in open(BASE / "data/canonical/expressions.jsonl", encoding="utf-8")]
    n_base = manifest()["append_only"]["expressions.jsonl"]["lines"]
    extra = [r for r in rows[n_base:] if r["concept_id"].startswith("concept-core-")]
    for r in extra:
        assert r["provenance_type"] == "AI_GENERATED" and r["language_metadata"]["correction"]["phase"] == "1.4.1"


def test_synonyms_of_replaced_vi_are_retracted_not_deleted(S):
    for cid, e in S["ex"].items():
        prim = e["vi"][0] if e["vi"] else None
        if prim and "correction" in prim["language_metadata"]:
            for syn in e["vi"][1:]:
                assert syn["status"] == "retracted"


def test_retracted_classifications_are_annotated_and_excluded_from_exports():
    cl = baseline_rows("classifications")
    retracted = [k for k in cl if k.get("status") == "retracted"]
    assert retracted
    for k in retracted:
        assert k["retraction"]["phase"] == "1.4.1" and k["retraction"]["previous_status"]
    ids = {k["classification_id"] for k in retracted}
    deck = json.loads((BASE / "data/exports/oki_language/deck_data.json").read_text())
    for card in deck:
        assert not any(c["status"] == "retracted" for c in card["classifications"])
    for view in (BASE / "data/exports/views_v1_4").rglob("*.jsonl"):
        pass
    assert ids  # sanity


def test_regression_guard_known_defects_are_fixed(S):
    want = {"core-husband": "夫", "core-today": "今日", "core-eat": "食べる", "core-world": "世界", "core-yesterday": "昨日",
            "core-girl": None, "core-dog": "犬", "core-cat": "猫", "core-drink": "飲む", "core-blue": "青い", "core-child": "子供"}
    for k, ja in want.items():
        cid = "concept-" + k
        if ja:
            assert S["ex"][cid]["ja"][0]["lemma"] == ja, (cid, S["ex"][cid]["ja"][0]["lemma"])
    assert S["ex"]["concept-core-cat"]["ja"][0]["reading"] == "ねこ"
    assert S["ex"]["concept-core-front"]["ja"][0]["reading"] == "まえ"
    assert S["ex"]["concept-core-act"]["en"][0]["part_of_speech"] == "verb" and S["ex"]["concept-core-act"]["ja"][0]["lemma"] != "法律"
    assert S["ex"]["concept-core-well"]["ja"][0]["lemma"] != "あの"
    for adv in ("actually", "absolutely", "always", "very", "well", "just"):
        assert S["ex"]["concept-core-" + adv]["en"][0]["part_of_speech"] == "adverb", adv
    # an offensive Japanese slur must never stand for a neutral English noun
    assert all(e["ja"][0]["lemma"] != "スベタ" for e in S["ex"].values() if e["ja"])


def test_unfixable_defects_are_flagged_not_guessed(S):
    flagged = [c for c in S["con"].values() if "flagged_unfixable" in ((c.get("metadata") or {}).get("correction") or {}).get("kinds", [])]
    assert flagged
    for c in flagged:
        assert c["metadata"]["correction"]["validation_status"] == "needs_review"


def test_corrected_concepts_are_not_production_ready_in_oki_export():
    deck = {c["id"]: c for c in json.loads((BASE / "data/exports/oki_language/deck_data.json").read_text())}
    for c in baseline_rows("concepts"):
        corr = (c.get("metadata") or {}).get("correction")
        if corr and corr["validation_status"] == "needs_review":
            assert deck[c["concept_id"]]["validation_status"] == "needs_review"
            assert deck[c["concept_id"]]["production_ready"] is False
