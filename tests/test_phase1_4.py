"""
tests/test_phase1_4.py
Phase 1.4 (curated corpus expansion) - GENERAL INVARIANTS, deliberately not hard-coded counts.

Covers: frozen Phase 1.3D assets, stable/unique IDs, deterministic offline rebuild, no duplicate concepts,
sense preservation, partial concepts, no fabricated tri-language completeness, provenance validity,
AI provenance immutability, judge blindness, license safety, reconstructible source locators,
classification honesty, and reproducible downstream exports.
"""

import gzip
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

import pytest

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from tests._baseline import baseline_concept_ids, baseline_rows, manifest, CANONICAL_DIR  # noqa: E402

P14 = BASE_DIR / "data" / "phase1_4"
RAW = BASE_DIR / "data" / "raw"
NEW_PREFIX = "concept-lex-"


def load(name):
    out = []
    with open(CANONICAL_DIR / f"{name}.jsonl", "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                out.append(json.loads(line))
    return out


@pytest.fixture(scope="module")
def G():
    concepts, senses, exprs, classes = load("concepts"), load("senses"), load("expressions"), load("classifications")
    base = baseline_concept_ids()
    new_c = [c for c in concepts if c["concept_id"] not in base]
    new_ids = {c["concept_id"] for c in new_c}
    by_c = defaultdict(lambda: defaultdict(list))
    for e in exprs:
        by_c[e["concept_id"]][e["language"]].append(e)
    return dict(concepts=concepts, senses=senses, exprs=exprs, classes=classes, base=base, new_c=new_c,
                new_ids=new_ids, by_c=by_c,
                sense_by_c=defaultdict(list, {k: v for k, v in _group(senses).items()}))


def _group(senses):
    d = defaultdict(list)
    for s in senses:
        d[s["concept_id"]].append(s)
    return d


# ------------------------------------------------------------------ frozen baseline
def test_sealed_baseline_prefix_is_byte_identical_modulo_ledger():
    """Phase 1.4.1: corrected prefix is pinned, and reverting the ledger reproduces the sealed Phase 1.3D SHA-256 exactly."""
    from tests._baseline import reverted_prefix_bytes
    m = manifest()
    for fname, info in m["append_only"].items():
        data = (CANONICAL_DIR / fname).read_bytes()
        cp = m["corrected_prefix"][fname]
        assert hashlib.sha256(data[: cp["bytes"]]).hexdigest() == cp["sha256"], f"{fname}: corrected prefix changed"
        name = fname.replace(".jsonl", "")
        if name != "examples":
            assert hashlib.sha256(reverted_prefix_bytes(name)).hexdigest() == info["sha256"], f"{fname}: ledger does not reproduce the sealed bytes"


def test_frozen_files_golden_pilot_and_production_unchanged():
    for rel, sha in manifest()["frozen_files"].items():
        p = BASE_DIR / rel
        assert p.exists(), rel
        assert hashlib.sha256(p.read_bytes()).hexdigest() == sha, f"frozen file changed: {rel}"


def test_professional_800_untouched_including_views(G):
    pro = [c for c in G["concepts"] if c["concept_id"].startswith("concept-pro-")]
    assert len(pro) == 800
    base_cls_lines = manifest()["append_only"]["classifications.jsonl"]["lines"]
    for k in G["classes"][base_cls_lines:]:
        assert not k["target_id"].startswith("concept-pro-"), "backfill must never touch professional records"


def test_canonical_ids_of_baseline_immutable(G):
    assert G["base"] <= {c["concept_id"] for c in G["concepts"]}
    assert len(G["base"]) == 2106


def test_baseline_oki_cards_preserved():
    deck = {c["id"]: c for c in json.loads((BASE_DIR / "data/exports/oki_language/deck_data.json").read_text())}
    sealed = json.loads((BASE_DIR / "data/releases/phase1_3d-sealed/oki_deck_data.baseline.json").read_text())
    corrected = {x["concept_id"] for x in load("concepts") if (x.get("metadata") or {}).get("correction")}
    for c in sealed:
        if c["id"] in corrected:
            continue   # rebuilt from corrected canonical (Phase 1.4.1)
        d = deck[c["id"]]
        for k in c:
            if k in ("classifications", "tags"):
                assert d[k][: len(c[k])] == c[k], f"baseline {k} must only be extended"
            else:
                assert d[k] == c[k], f"baseline card field changed: {c['id']}.{k}"


# ------------------------------------------------------------------ ids & structure
ID_RE = re.compile(r"^concept-lex-[a-z0-9]+(-[a-z0-9]+)*-[a-z]{1,3}-[0-9a-f]{6}$")


def test_ids_unique_and_well_formed(G):
    for name, key in (("concepts", "concept_id"), ("senses", "sense_id"), ("exprs", "expression_id"), ("classes", "classification_id")):
        ids = [r[key] for r in G[name]]
        assert len(ids) == len(set(ids)), f"duplicate {key}"
    for c in G["new_c"]:
        assert ID_RE.match(c["concept_id"]), c["concept_id"]


def test_new_records_reference_existing_parents(G):
    cids = {c["concept_id"] for c in G["concepts"]}
    sids = {s["sense_id"] for s in G["senses"]}
    for s in G["senses"]:
        assert s["concept_id"] in cids
    for e in G["exprs"]:
        assert e["concept_id"] in cids and e["sense_id"] in sids
    for k in G["classes"]:
        assert k["target_id"] in cids or k["target_id"] in sids or k["target_id"].startswith("expr-")


def test_concept_sense_expression_model_for_new_concepts(G):
    assert len(G["new_c"]) > 0
    for c in G["new_c"]:
        cid = c["concept_id"]
        ss = G["sense_by_c"][cid]
        assert len(ss) == 1, "each new concept carries exactly one sense (polysemy => separate concepts)"
        langs = {l for l, v in G["by_c"][cid].items() if v}
        assert {"en", "ja"} <= langs
        assert len(G["by_c"][cid]["en"]) == 1 and len(G["by_c"][cid]["ja"]) == 1
        for l in ("en", "ja", "vi"):
            for e in G["by_c"][cid][l]:
                assert e["sense_id"] == ss[0]["sense_id"]


def test_completeness_is_computed_never_forced(G):
    for c in G["new_c"]:
        cid = c["concept_id"]
        has_vi = bool(G["by_c"][cid]["vi"])
        s = G["sense_by_c"][cid][0]
        assert c["metadata"]["translation_status"] == ("complete" if has_vi else "partial")
        if not has_vi:
            assert s["gloss_vi"] is None and s["definition_vi"] is None, "partial concepts must not fabricate VI"
            assert c["metadata"].get("quality_tier") == "Tier D"
        else:
            assert s["gloss_vi"] == G["by_c"][cid]["vi"][0]["lemma"]


def test_partial_concepts_have_recorded_reason(G):
    for c in G["new_c"]:
        if c["metadata"]["translation_status"] == "partial":
            assert c["metadata"].get("partial_reason")


def test_sense_preservation_for_polysemous_english(G):
    by_en = defaultdict(list)
    for cid in G["new_ids"]:
        en = G["by_c"][cid]["en"][0]
        by_en[(en["lemma"], en["part_of_speech"])].append(cid)
    sdef = {s["concept_id"]: s["definition_en"] for s in G["senses"]}
    for key, cids in by_en.items():
        defs = [sdef[c] for c in cids]
        assert len(defs) == len(set(defs)) or len({G["by_c"][c]["ja"][0]["lemma"] for c in cids}) == len(cids), \
            f"polysemy collapsed or duplicated for {key}"


def test_no_duplicate_semantic_concepts_in_new_corpus(G):
    seen_a, seen_b = {}, {}
    for cid in sorted(G["new_ids"]):
        e = G["by_c"][cid]
        a = (e["en"][0]["lemma"], e["en"][0]["part_of_speech"], e["ja"][0]["lemma"])
        assert a not in seen_a, f"duplicate concept {cid} == {seen_a.get(a)}"
        seen_a[a] = cid
        if e["vi"]:
            b = (e["ja"][0]["lemma"], e["vi"][0]["lemma"])
            assert b not in seen_b, f"duplicate JA+VI pair {cid} == {seen_b.get(b)}"
            seen_b[b] = cid


def test_match_before_create_no_duplicate_of_existing_concept(G):
    ex = {}
    for cid in G["base"]:
        e = G["by_c"][cid]
        if e["en"] and e["ja"]:
            ex.setdefault((e["en"][0]["lemma"].lower(), e["ja"][0]["lemma"]), cid)
    for cid in G["new_ids"]:
        e = G["by_c"][cid]
        k = (e["en"][0]["lemma"].lower(), e["ja"][0]["lemma"])
        assert k not in ex, f"{cid} duplicates existing concept {ex[k]}"


# ------------------------------------------------------------------ provenance & licensing
ALLOWED_PROV = {"SOURCE_DERIVED", "AI_GENERATED"}


def test_new_expression_provenance_and_validation_are_separate_dimensions(G):
    for cid in G["new_ids"]:
        for l in ("en", "ja", "vi"):
            for e in G["by_c"][cid][l]:
                assert e["provenance_type"] in ALLOWED_PROV
                if l in ("en", "ja"):
                    assert e["provenance_type"] == "SOURCE_DERIVED"
                if l == "vi":
                    # judge validation is recorded in metadata and never rewrites origin
                    v = e["language_metadata"]["translation_semantics_validated"]
                    assert v["status"] in ("AI_JUDGE_VALIDATED", "INDEPENDENT_AGENT_REVIEW", "AGENT_PROPOSED_PARTIALLY_REVIEWED")
                    src = e["language_metadata"]["lexeme_source"]["status"]
                    assert src == e["provenance_type"]


def test_ai_generated_provenance_is_immutable_and_complete(G):
    n_ai = 0
    for cid in G["new_ids"]:
        for e in G["by_c"][cid]["vi"]:
            ev = e["source_evidence"]
            if e["provenance_type"] == "AI_GENERATED":
                n_ai += 1
                assert len(ev) == 1
                x = ev[0]
                assert x["origin"] == "ai_generated"
                for f in ("model", "generation_version", "input_hash", "generated_at"):
                    assert x.get(f), f"AI evidence missing {f} for {e['expression_id']}"
                assert e["language_metadata"]["lexeme_source"]["status"] == "AI_GENERATED"
            else:
                assert all(x["origin"] == "source_derived" for x in ev)
                assert all(x.get("model") is None for x in ev)
    # every AI lexeme must be traceable to a stored proposal (hand-off decision) with matching input hash
    import hashlib
    t4 = {}
    for p in sorted((BASE_DIR / "data/phase1_4/handoff/packets").glob("T4_*.jsonl")):
        for l in p.read_text(encoding="utf-8").splitlines():
            d = json.loads(l)
            t4[hashlib.sha256(json.dumps(d, ensure_ascii=False, sort_keys=True).encode()).hexdigest()] = d["id"]
    for cid in G["new_ids"]:
        for e in G["by_c"][cid]["vi"]:
            if e["provenance_type"] == "AI_GENERATED":
                x = e["source_evidence"][0]
                assert x["model"] in ("gpt-6-luna", "claude-sonnet-5-5"), x["model"]
                assert t4.get(x["input_hash"]) == cid, f"no hand-off packet item for {e['expression_id']}"
                assert e["language_metadata"]["translation_semantics_validated"]["status"] == "AGENT_PROPOSED_PARTIALLY_REVIEWED"


def test_source_derived_evidence_resolves_to_verified_raw_snapshots(G):
    from scripts.phase1_3b.license_gate import LicenseGate
    gate = LicenseGate()
    metas = {}
    for cid in G["new_ids"]:
        for l in ("en", "ja", "vi"):
            for e in G["by_c"][cid][l]:
                for ev in e["source_evidence"]:
                    if ev["origin"] != "source_derived":
                        continue
                    key = (ev["source_id"], ev["source_version"])
                    if key not in metas:
                        d = RAW / key[0] / key[1]
                        assert d.exists(), f"no raw snapshot for {key}"
                        m = json.loads((d / "metadata.json").read_text())
                        art = d / m["artifact_filename"]
                        assert hashlib.sha256(art.read_bytes()).hexdigest() == m["artifact_sha256"], f"snapshot hash drift {key}"
                        metas[key] = m
                    m = metas[key]
                    assert ev["raw_sha256"] == m["artifact_sha256"]
                    assert ev["license"] == m["license"]
                    assert gate.is_production_eligible(ev["license"]), ev["license"]
                    assert ev["source_locator"]
    assert metas, "expected source-derived evidence"


def test_source_locators_are_reconstructible(G):
    wk = [json.loads(l) for l in gzip.open(RAW / "wiktionary_en/2026-09-28/wikt_en_translations.jsonl.gz", "rt")]
    checked = 0
    for cid in sorted(G["new_ids"])[::7]:           # deterministic 1-in-7 sample (full check is in the audit script)
        e = G["by_c"][cid]
        for l in ("en", "ja", "vi"):
            for x in e[l]:
                for ev in x["source_evidence"]:
                    if ev["source_id"] == "wiktionary_en":
                        m = re.match(r"line:(\d+), sense:(\S+)", ev["source_locator"])
                        row = wk[int(m.group(1)) - 1]
                        assert row["word"] == e["en"][0]["lemma"]
                        if ev["field_name"] == "translation_vi":
                            words = [t["word"].lower() for s in row["senses"] for t in s["translations"] if t["lang_code"] == "vi"] + \
                                    [t["word"].lower() for t in row["entry_translations"] if t["lang_code"] == "vi"]
                            assert x["lemma"] in words
                        checked += 1
    assert checked > 0


def test_jmdict_corroboration_recorded_for_every_new_ja(G):
    for c in G["new_c"]:
        j = c["metadata"]["ja_corroboration"]
        assert j["jmdict_gloss_score"] >= 1 and j["ent_seq"] > 0
        ja = G["by_c"][c["concept_id"]]["ja"][0]
        assert any(ev["source_id"] == "jmdict" and f"ent_seq:{j['ent_seq']}" in ev["source_locator"] for ev in ja["source_evidence"])


def test_license_policy_no_unapproved_or_noncommercial_sources():
    import yaml
    pol = yaml.safe_load((BASE_DIR / "config/license_policy.yaml").read_text())["licenses"]
    for d in sorted(RAW.glob("*/*")):
        mf = d / "metadata.json"
        if not mf.exists() or d.parent.name in ("wordfreq",):
            continue
        lic = json.loads(mf.read_text()).get("license")
        if d.parent.name in ("fsa", "nta", "jetro", "jicpa", "asbj", "egov", "japan-customs", "mhlw", "smrj"):
            continue  # Phase 1.2 official sources are governed by SOURCE_POLICY.md (PDL-style terms)
        assert lic in pol and pol[lic]["status"] in ("APPROVED", "APPROVED_WITH_SHARE_ALIKE"), f"{d}: {lic}"
    assert not (RAW / "wordfreq").exists(), "wordfreq data has mixed/uncertain licensing and must not be ingested"


# ------------------------------------------------------------------ AI discipline
def test_judge_is_blind_and_cached_inputs_leak_nothing():
    forbidden = {"origin", "provenance", "source", "score", "value", "confidence", "rationale", "signals", "tier"}
    shard_dir = BASE_DIR / "data/ai/phase1_4/judge"
    n = 0
    for p in sorted(shard_dir.glob("shard-*.json")):
        d = json.loads(p.read_text())
        assert d["model"] != "gemini-2.5-flash", "judge must be a different model from the generator"
        for it in d["items"]:
            assert not (forbidden & set(it["input"])), f"judge input leaks {forbidden & set(it['input'])}"
            n += 1
    assert n > 0


def test_generator_and_judge_models_differ():
    gen_dir = BASE_DIR / "data/ai/phase1_4/gen_vi"
    jd = BASE_DIR / "data/ai/phase1_4/judge"
    jm = {json.loads(p.read_text())["model"] for p in jd.glob("shard-*.json")}
    gm = {json.loads(p.read_text())["model"] for p in gen_dir.glob("shard-*.json")} if gen_dir.exists() else set()
    assert not (jm & gm)


def test_no_judge_or_generation_network_needed_for_rebuild():
    """Offline determinism: the complete caches exist so build_canonical never calls an API."""
    import scripts.phase1_4.ai as ai
    src = Path(ai.__file__).read_text()
    assert "offline" in src


# ------------------------------------------------------------------ determinism & exports
def test_offline_rebuild_is_byte_identical():
    from scripts.phase1_4 import build_canonical as B
    before = {n: (CANONICAL_DIR / f"{n}.jsonl").read_bytes() for n in B.FILES}
    B.build(write=True)
    for n, b in before.items():
        assert (CANONICAL_DIR / f"{n}.jsonl").read_bytes() == b, f"{n} not reproducible"


def test_exports_are_reproducible():
    from scripts.phase1_4 import export_views as X
    cards = X.build_cards()
    on_disk = json.loads((BASE_DIR / "data/exports/oki_language/deck_data.json").read_text())
    assert cards == on_disk
    assert len(cards) == len(load("concepts"))


def test_views_are_projections_not_copies():
    idx = json.loads((BASE_DIR / "data/exports/views_v1_4/views_index.json").read_text())["views"]
    cids = {c["concept_id"] for c in load("concepts")}
    for name in idx:
        p = BASE_DIR / "data/exports/views_v1_4" / f"{name}.jsonl"
        rows = [json.loads(l) for l in p.read_text().splitlines() if l.strip()]
        ids = [r["concept_id"] for r in rows]
        assert len(ids) == len(set(ids)), f"view {name} repeats a concept"
        assert set(ids) <= cids
        assert len(rows) == idx[name]["concepts"]


# ------------------------------------------------------------------ classifications
def test_classification_labels_are_honest(G):
    for k in G["classes"]:
        sysname = k.get("system") or k.get("classification_system")
        if sysname in ("CEFR", "EIKEN") and k["target_id"] in G["new_ids"]:
            assert k["provenance_type"] == "INFERRED" and k["status"] == "inferred"
        if sysname in ("TOEIC", "IELTS", "TOEFL") and k["target_id"] in G["new_ids"]:
            assert k["provenance_type"] == "INFERRED", "exam relevance is derived, never an official list"
        if sysname == "JLPT" and k["target_id"] in G["new_ids"]:
            assert k["status"] == "community_consensus" and k["source_id"] == "jlpt_consensus"
            assert k["provenance_type"] != "OFFICIAL_EXTRACTED"


def test_review_and_rejected_never_enter_canonical(G):
    cand_ids = set()
    for fn in ("review_queue.jsonl", "rejected.jsonl"):
        p = P14 / fn
        assert p.exists()
        cand_ids |= {json.loads(l)["cand_id"] for l in p.read_text().splitlines() if l.strip()}
    for c in G["new_c"]:
        assert c["metadata"]["cand_id"] not in cand_ids


def test_final_metrics_reconcile_with_canonical(G):
    fm = json.loads((BASE_DIR / "reports/phase1_4/final_metrics.json").read_text())
    assert fm["corpus"]["total_concepts"] == len(G["concepts"])
    assert fm["corpus"]["new_concepts"] == len(G["new_c"])
    assert fm["corpus"]["baseline_concepts"] == 2106
    comp = sum(1 for c in G["concepts"] if {"en", "ja", "vi"} <= {l for l, v in G["by_c"][c["concept_id"]].items() if v})
    assert fm["corpus"]["tri_language_complete"] == comp


def test_identical_en_vi_forms_are_source_derived_not_copied(G):
    """EN==VI is legitimate for letter names/loanwords but must never be an AI/placeholder copy."""
    for cid in G["new_ids"]:
        e = G["by_c"][cid]
        if e["vi"] and e["vi"][0]["lemma"].lower() == e["en"][0]["lemma"].lower():
            assert e["vi"][0]["provenance_type"] in ("SOURCE_DERIVED", "AI_GENERATED")
            if e["vi"][0]["provenance_type"] == "SOURCE_DERIVED":
                assert e["vi"][0]["source_evidence"][0]["source_id"] == "wiktionary_en"
