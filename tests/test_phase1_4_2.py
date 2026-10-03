"""Phase 1.4.2 - integration of the Luna hand-off (T1 validation, T3 promotions, T4 Vietnamese) with provenance honesty."""
import glob, hashlib, json
from pathlib import Path
import pytest

BASE = Path(__file__).resolve().parent.parent
HO = BASE / "data/phase1_4/handoff"


def jl(p):
    return [json.loads(l) for l in Path(p).read_text(encoding="utf-8").splitlines() if l.strip()]


@pytest.fixture(scope="module")
def C():
    con = {c["concept_id"]: c for c in jl(BASE / "data/canonical/concepts.jsonl")}
    ex = {}
    for e in jl(BASE / "data/canonical/expressions.jsonl"):
        ex.setdefault(e["concept_id"], {}).setdefault(e["language"], []).append(e)
    return con, ex


def decisions(task):
    out = {}
    for p in sorted(glob.glob(str(HO / f"decisions/{task}_*.jsonl"))):
        for l in Path(p).read_text(encoding="utf-8").splitlines():
            d = json.loads(l); out[d["id"]] = (d, l)
    return out


def test_all_reviewed_tasks_are_logged_with_matching_hashes():
    log = jl(HO / "review_log.jsonl")
    done = {r["task_id"] for r in log if r["decision"] == "APPROVED"}
    assert len(done) >= 50 and all(r["reviewer"] == "claude" for r in log)
    for r in log:
        f = HO / "decisions" / f"{r['task_id']}.jsonl"
        assert hashlib.sha256(f.read_bytes()).hexdigest() == r["decision_file_sha256"], f"{f.name} changed after review"


def test_validation_overrides_only_for_luna_accept_high_and_unmodified(C):
    con, _ = C
    vo = json.loads((BASE / "data/phase1_4/validation_overrides.json").read_text())
    t1 = decisions("T1")
    later = set()
    for p in glob.glob(str(BASE / "data/phase1_4/baseline_fixes/part[6-9]*.tsv")):
        later |= {"concept-" + l.split("\t")[0] for l in open(p, encoding="utf-8") if l.strip() and not l.startswith("#")}
    assert len(vo) > 200
    for cid, v in vo.items():
        d, line = t1[cid]
        assert d["verdict"] == "ACCEPT" and d["confidence"] == "HIGH" and d["reviewer"] == "gpt-6-luna"
        assert cid not in later, "concept changed after Luna reviewed it"
        assert hashlib.sha256(line.strip().encode()).hexdigest() == v["decision_sha256"]
        assert (con[cid].get("metadata") or {}).get("correction"), "only corrected baseline concepts are promoted"
        assert v["basis"] == "independent_agent_review"


def test_validation_promotion_never_changes_provenance(C):
    con, ex = C
    vo = json.loads((BASE / "data/phase1_4/validation_overrides.json").read_text())
    for cid in vo:
        for l in ("ja", "vi"):
            for e in ex[cid].get(l, []):
                if "correction" in e["language_metadata"] and l == "vi":
                    assert e["provenance_type"] == "AI_GENERATED"      # agent-authored VI stays AI_GENERATED even when validated
                if "correction" in e["language_metadata"] and l == "ja":
                    assert e["provenance_type"] == "SOURCE_DERIVED"


def test_t3_promotions_require_luna_accept_and_claude_confirmation(C):
    con, _ = C
    acc = set(json.loads((HO / "claude_review_T3.json").read_text())["accepted"])
    t3 = decisions("T3")
    assert all(t3[i][0]["verdict"] == "ACCEPT" for i in acc)
    promoted = [c for c in con.values() if (c.get("metadata") or {}).get("independent_review")]
    assert 30 <= len(promoted) <= len(acc)
    for c in promoted:
        assert c["metadata"]["cand_id"] in acc
        # T4 later adds AI_GENERATED Vietnamese to some promoted concepts; those go back to needs_review by design
        want = "needs_review" if "vi_proposal" in c["metadata"] else "validated"
        assert c["metadata"]["validation_status"] == want
        assert c["metadata"]["independent_review"]["reviewers"] == ["gpt-6-luna", "claude"]


def test_t4_vietnamese_is_ai_generated_needs_review_and_overrides_applied(C):
    con, ex = C
    ov = json.loads((HO / "claude_overrides_T4.json").read_text())["overrides"]
    t4 = decisions("T4")
    n = 0
    for cid, (d, _) in t4.items():
        if cid not in con:
            continue       # concept absorbed/renumbered by later de-duplication
        vi = (ex[cid].get("vi") or [None])[0]
        want = ov[cid]["vi"] if cid in ov else d.get("vi_lemma")
        if want is None:
            assert vi is None
            continue
        if vi is None:
            continue       # the concept may have been rebuilt without a VI slot (e.g. dedupe)
        n += 1
        assert vi["lemma"] == want
        assert vi["provenance_type"] == "AI_GENERATED"
        assert vi["source_evidence"][0]["model"] == ("claude-sonnet-5-5" if cid in ov else d.get("reviewer", "gpt-6-luna"))
        assert con[cid]["metadata"]["validation_status"] == "needs_review"
        assert con[cid]["metadata"]["quality_tier"] == "Tier C"
    assert n > 1000


def test_no_duplicate_ja_vi_pairs_after_t4_ingestion(C):
    con, ex = C
    seen = {}
    for cid, e in ex.items():
        if cid.startswith("concept-lex-") and e.get("vi") and e.get("ja"):
            k = (e["ja"][0]["lemma"], e["vi"][0]["lemma"])
            assert k not in seen, (cid, seen[k])
            seen[k] = cid
