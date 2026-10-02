#!/usr/bin/env python3
"""
scripts/phase1_4/handoff/make_packets.py
Builds self-contained WORK PACKETS (JSONL, 40 items per file) for an external coding agent (e.g. GPT 6 Luna).
Packets contain everything needed to decide; the agent must not need the network or any other file.

  T1  independent validation of the 296 Phase 1.4.1-corrected baseline concepts
  T2  the 9 flagged-unfixable baseline concepts (find a verifiable fix or confirm "no fix")
  T3  human-review queue of Phase 1.4 candidates (judge said REVIEW; plausible but not auto-accepted)
  T4  Vietnamese proposals for validated EN-JA partial concepts (high learning value first)
Deterministic ordering; re-running overwrites identically.
"""
import json
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))
from scripts.phase1_4.common import BASE_DIR, CANONICAL_DIR, P14_DIR, read_jsonl

OUT = BASE_DIR / "data/phase1_4/handoff/packets"
N = 40


def write_packets(name, items):
    OUT.mkdir(parents=True, exist_ok=True)
    for old in OUT.glob(f"{name}_*.jsonl"):
        old.unlink()
    for i in range(0, len(items), N):
        p = OUT / f"{name}_{i // N + 1:03d}.jsonl"
        p.write_text("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in items[i:i + N]), encoding="utf-8")
    return (len(items) + N - 1) // N


def main():
    concepts = {c["concept_id"]: c for c in read_jsonl(CANONICAL_DIR / "concepts.jsonl")}
    ex = defaultdict(lambda: defaultdict(list))
    for e in read_jsonl(CANONICAL_DIR / "expressions.jsonl"):
        if e.get("status") != "retracted":
            ex[e["concept_id"]][e["language"]].append(e)
    senses = {s["concept_id"]: s for s in read_jsonl(CANONICAL_DIR / "senses.jsonl")}
    led = json.loads((BASE_DIR / "reports/phase1_4/baseline_corrections_ledger.json").read_text())["entries"]
    hist = defaultdict(dict)
    for e in led:
        if e["file"] == "expressions" and e["field"] == "lemma":
            hist[e["concept_id"]][e["id"].split("-")[1]] = e["old"]      # language -> previous lemma
    summary = {}

    def card(cid):
        e = ex[cid]
        en, ja = e["en"][0], e["ja"][0]
        vi = e["vi"][0] if e["vi"] else None
        return {"id": cid, "en": en["lemma"], "pos": en["part_of_speech"], "ja": ja["lemma"], "ja_reading": ja["reading"],
                "ja_jmdict_glosses": (ja["language_metadata"].get("jmdict_glosses") or (ja["language_metadata"].get("correction") or {}).get("jmdict_glosses") or []),
                "vi": vi["lemma"] if vi else None, "vi_provenance": vi["provenance_type"] if vi else None,
                "en_sense_definition": (senses[cid].get("definition_en") or "")[:300]}

    t1, t2 = [], []
    for cid, c in sorted(concepts.items()):
        corr = (c.get("metadata") or {}).get("correction")
        if not corr:
            continue
        item = card(cid)
        item["changed"] = {"kinds": corr["kinds"], "previous_lemmas": hist.get(cid, {}), "agent_note": corr["reason"]}
        (t2 if "flagged_unfixable" in corr["kinds"] else t1).append(item)
    summary["T1"] = (len(t1), write_packets("T1", t1))
    summary["T2"] = (len(t2), write_packets("T2", t2))

    pool = {c["cand_id"]: c for c in read_jsonl(P14_DIR / "scored_pool.jsonl")}
    t3 = []
    for r in read_jsonl(P14_DIR / "review_queue.jsonl"):
        c = pool.get(r["cand_id"])
        if not c:
            continue
        j = r.get("judge") or {}
        t3.append({"id": c["cand_id"], "en": c["en"]["lemma"], "pos": c["en"]["pos"], "en_sense_definition": c["en"]["wikt_gloss"][:300],
                   "ja": c["ja"]["lemma"], "ja_reading": c["ja"]["reading"], "ja_jmdict_glosses": c["ja"]["jm_glosses"][:6],
                   "vi": (c["vi"] or {}).get("lemma"), "learning_value": c["value"]["total"],
                   "earlier_model_judge": {k: j.get(k) for k in ("en_ja", "en_vi", "ja_vi", "verdict", "note")}})
    t3.sort(key=lambda x: (-x["learning_value"], x["id"]))
    summary["T3"] = (len(t3), write_packets("T3", t3))

    t4 = []
    for cid, c in sorted(concepts.items()):
        md = c.get("metadata") or {}
        if cid.startswith("concept-lex-") and md.get("translation_status") == "partial" and md.get("learning_value", {}).get("total", 0) >= 45:
            item = card(cid)
            item.update(learning_value=md["learning_value"]["total"], rejected_vi_before=(md.get("rejected_vi_candidate") or {}).get("lemma"))
            t4.append(item)
    t4.sort(key=lambda x: (-x["learning_value"], x["id"]))
    summary["T4"] = (len(t4), write_packets("T4", t4))
    (OUT.parent / "packet_index.json").write_text(json.dumps(summary, indent=1))
    print(json.dumps(summary))


if __name__ == "__main__":
    main()
