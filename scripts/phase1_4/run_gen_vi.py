#!/usr/bin/env python3
"""
scripts/phase1_4/run_gen_vi.py
Stage 4: AI-assisted Vietnamese gap resolution (source-first, AI-second).

Targets ONLY candidates whose EN-JA pair was judge-validated but that have no accepted Vietnamese form:
  (a) no Wiktionary VI existed                           -> results["enja"] accepted
  (b) Wiktionary VI existed but the judge rejected it    -> results["recheck"] accepted (rejected form goes into 'avoid')
and whose learning value >= MIN_AI_VI_VALUE.

Generated forms are stored in data/phase1_4/ai_vi.json with model / prompt_version / input_hash /
generated_at, then judged BLIND by a different model (results["tri_ai"]).
"""
import argparse
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from scripts.phase1_4.common import P14_DIR, read_jsonl, write_json
from scripts.phase1_4 import gen_vi, judge as J
from scripts.phase1_4.route import MIN_AI_VI_VALUE
from scripts.phase1_4.run_judge import CREATABLE, prefilter


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()
    pool = {c["cand_id"]: c for c in read_jsonl(P14_DIR / "scored_pool.jsonl")}
    R = json.loads((P14_DIR / "judge_results.json").read_text())
    todo = []
    for cid in sorted(pool):
        c = pool[cid]
        if c["match"]["decision"] not in CREATABLE or prefilter(c) or c["value"]["total"] < MIN_AI_VI_VALUE:
            continue
        if c["vi"]:
            tri, rc = R.get("tri", {}).get(cid), R.get("recheck", {}).get(cid)
            if tri is None or J.is_accept_tri(tri) or rc is None or not J.is_accept_en_ja(rc):
                continue
            avoid = [c["vi"]["lemma"]]
        else:
            ej = R.get("enja", {}).get(cid)
            if ej is None or not J.is_accept_en_ja(ej):
                continue
            avoid = []
        todo.append(gen_vi.to_item(c, avoid))
    if args.limit:
        todo = todo[:args.limit]
    print("generation targets:", len(todo))
    out, prov = gen_vi.generate(todo, workers=args.workers)
    path = P14_DIR / "ai_vi.json"
    cur = json.loads(path.read_text()) if path.exists() else {}
    for cid, g in out.items():
        if not g.get("vi_lemma"):
            cur.setdefault(cid, None)
            continue
        p = prov[cid]
        cur[cid] = {"vi_lemma": g["vi_lemma"].strip().lower(), "synonyms": g.get("synonyms", []),
                    "definition_vi": g.get("definition_vi"), "generator_confidence": g.get("confidence"),
                    "generator_rationale": g.get("rationale"), "model": p["model"], "prompt_version": p["prompt_version"],
                    "input_hash": p["input_hash"], "generated_at": p["created_at"]}
    cur = {k: v for k, v in cur.items() if v}
    write_json(path, cur)
    # --- blind judging of generated forms (different model, no generator metadata)
    items = []
    for cid, g in cur.items():
        it = J.to_item(pool[cid], vi_lemma=g["vi_lemma"])
        items.append(it)
    res = J.judge_items(items, workers=args.workers)
    allres = json.loads((P14_DIR / "judge_results.json").read_text())
    allres.setdefault("tri_ai", {}).update(res)
    write_json(P14_DIR / "judge_results.json", allres)
    ctr = Counter("ACCEPT_STRICT" if J.is_accept_tri(r) else r.get("verdict") for r in res.values())
    print("generated", len(cur), "judged", len(res), dict(ctr))


if __name__ == "__main__":
    main()
