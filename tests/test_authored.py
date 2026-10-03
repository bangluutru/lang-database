"""Gemini-authored A1 concepts: provenance, review gating and invariants (offline)."""
import json
import glob
from pathlib import Path

import pytest

BASE = Path(__file__).resolve().parent.parent
HO = BASE / "data/phase1_4/handoff"


@pytest.fixture(scope="module")
def corpus():
    con = {}
    for l in (BASE / "data/canonical/concepts.jsonl").read_text(encoding="utf-8").splitlines():
        c = json.loads(l)
        con[c["concept_id"]] = c
    ex = {}
    for l in (BASE / "data/canonical/expressions.jsonl").read_text(encoding="utf-8").splitlines():
        e = json.loads(l)
        ex.setdefault(e["concept_id"], {}).setdefault(e["language"], []).append(e)
    return con, ex


def passed_slots():
    rev = json.loads((HO / "claude_review_A1.json").read_text(encoding="utf-8"))["entries"]
    return {i for i, v in rev.items() if v["verdict"] == "PASS"}


def test_only_claude_passed_entries_are_in_the_corpus(corpus):
    con, _ = corpus
    in_corpus = {c["metadata"]["authored"]["slot"] for c in con.values() if (c.get("metadata") or {}).get("authored")}
    assert in_corpus == passed_slots()          # not one more, not one less (REWORK sources are excluded)
    assert len(in_corpus) == 30


def test_authored_provenance_and_status(corpus):
    con, ex = corpus
    for c in con.values():
        a = (c.get("metadata") or {}).get("authored")
        if not a:
            continue
        m = c["metadata"]
        assert m["validation_status"] == "needs_review" and m["quality_tier"] == "Tier C" and m["translation_status"] == "complete"
        assert m["independent_review"] == {"reviewers": ["gemini-3.8", "claude"], "basis": "A1_authoring_review"}
        assert a["definition_en_source"] == "AI_GENERATED" and a["worker"] == "gemini-3.8"
        assert m["judge"] is None                                  # no automatic judge was involved
        assert c["primary_domain"] == a["domain"] and a["domain"] in ("it", "healthcare", "travel")
        e = ex[c["concept_id"]]
        assert e["en"][0]["provenance_type"] == "SOURCE_DERIVED" and e["ja"][0]["provenance_type"] == "SOURCE_DERIVED"   # JMdict-anchored pair
        vi = e["vi"][0]
        assert vi["provenance_type"] == "AI_GENERATED" and vi["source_evidence"][0]["model"] == "gemini-3.8"


def test_authored_examples_contain_the_lemmas(corpus):
    con, ex = corpus
    for c in con.values():
        a = (c.get("metadata") or {}).get("authored")
        if a:
            e = ex[c["concept_id"]]
            assert e["vi"][0]["lemma"].lower() in a["examples"]["example_vi"].lower()


def test_authored_decisions_are_never_edited_after_review():
    rows = {}
    for p in sorted(glob.glob(str(HO / "decisions/A1_*.jsonl"))):
        for l in Path(p).read_text(encoding="utf-8").splitlines():
            d = json.loads(l)
            rows[d["id"]] = d
    for i in passed_slots():
        assert rows[i]["reviewer"] == "gemini-3.8" and not rows[i].get("skip")
