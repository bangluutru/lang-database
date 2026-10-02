#!/usr/bin/env python3
"""
scripts/phase1_4/run_judge.py
Stage 3: independent pairwise judging of scored candidates.

modes:
  canary : deterministic stratified sample (early-batch reliability evidence)
  tri    : all creatable tri-language candidates with learning value >= --min-tri
  enja   : creatable EN-JA-only candidates (value >= --min-enja) judged on the EN-JA pair
  recheck: EN-JA-only re-judge (vi=null) of tri candidates whose tri judgement failed
"""

import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from scripts.phase1_4.common import P14_DIR, read_jsonl, write_json
from scripts.phase1_4 import judge as J

CREATABLE = ("NEW_CONCEPT", "EXISTING_CONCEPT_NEW_SENSE")

REGISTER_BAD_JA = {"vulg", "derog", "obs", "arch", "obsc", "sl", "rare", "X", "joc", "id", "poet", "hist"}


def prefilter(c):
    """Deterministic gates that run BEFORE any AI call (cheap, explainable rejections)."""
    ja = c["ja"]
    if set(ja["jm_misc"]) & REGISTER_BAD_JA:
        return "ja_register_or_rare:" + ",".join(sorted(set(ja["jm_misc"]) & REGISTER_BAD_JA))
    return None


def pool():
    return read_jsonl(P14_DIR / "scored_pool.jsonl")


def hkey(c):
    return hashlib.sha256(c["cand_id"].encode()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["canary", "tri", "enja", "recheck", "collect"])
    ap.add_argument("--min-tri", type=int, default=10)
    ap.add_argument("--min-enja", type=int, default=20)
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()

    P = [c for c in pool() if c["match"]["decision"] in CREATABLE and not prefilter(c)]
    results_path = P14_DIR / "judge_results.json"
    results = json.loads(results_path.read_text()) if results_path.exists() else {}

    if args.mode == "collect":
        # offline: rebuild judge_results.json purely from the on-disk judge cache (zero API calls)
        from scripts.phase1_4.ai import BatchAI
        ai = BatchAI("judge", "judge")
        out = {"tri": {}, "enja": {}, "recheck": {}, "tri_ai": {}}
        ai_vi = json.loads((P14_DIR / "ai_vi.json").read_text()) if (P14_DIR / "ai_vi.json").exists() else {}
        for c in pool():
            if c["match"]["decision"] not in CREATABLE or prefilter(c):
                continue
            if c["vi"]:
                out["tri"].update(ai.lookup([J.to_item(c)], J.PROMPT_VERSION))
                it = J.to_item(c, vi_lemma=None)
                out["recheck"].update(ai.lookup([it], J.PROMPT_VERSION))
            else:
                out["enja"].update(ai.lookup([J.to_item(c)], J.PROMPT_VERSION))
            if c["cand_id"] in ai_vi:
                out["tri_ai"].update(ai.lookup([J.to_item(c, vi_lemma=ai_vi[c["cand_id"]]["vi_lemma"])], J.PROMPT_VERSION))
        cur = json.loads(results_path.read_text()) if results_path.exists() else {}
        for t, v in out.items():
            cur.setdefault(t, {}).update(v)
        write_json(results_path, cur)
        print("collected", {t: len(v) for t, v in cur.items()})
        return
    if args.mode == "canary":
        bands = [(60, 999, 70), (45, 59, 40), (30, 44, 40), (20, 29, 40), (10, 19, 40)]
        sel = []
        for lo, hi, n in bands:
            s = sorted([c for c in P if c["vi"] and lo <= c["value"]["total"] <= hi], key=hkey)[:n]
            sel += s
        res = J.judge_items([J.to_item(c) for c in sel], workers=args.workers)
        results.setdefault("tri", {}).update(res)
        sel2 = sorted([c for c in P if not c["vi"] and c["value"]["total"] >= 30], key=hkey)[:40]
        res2 = J.judge_items([J.to_item(c) for c in sel2], workers=args.workers)
        results.setdefault("enja", {}).update(res2)
        cur = json.loads(results_path.read_text()) if results_path.exists() else {}
        for t in ("tri", "enja"):
            cur.setdefault(t, {}).update(results.get(t, {}))
        write_json(results_path, cur)
        for nm, rr in (("tri", res), ("enja", res2)):
            ctr = Counter()
            for k, r in rr.items():
                ctr[r.get("verdict")] += 1
                ctr["STRICT_TRI_ACCEPT" if nm == "tri" and J.is_accept_tri(r) else "other"] += 1
                if nm == "enja" and J.is_accept_en_ja(r):
                    ctr["EN_JA_ACCEPT"] += 1
            print("canary", nm, len(rr), dict(ctr))
        return
    elif args.mode == "tri":
        sel = sorted([c for c in P if c["vi"] and c["value"]["total"] >= args.min_tri], key=lambda c: c["cand_id"])
        if args.limit:
            sel = sel[:args.limit]
        res = J.judge_items([J.to_item(c) for c in sel], workers=args.workers)
        tag = "tri"
    elif args.mode == "enja":
        sel = sorted([c for c in P if not c["vi"] and c["value"]["total"] >= args.min_enja], key=lambda c: c["cand_id"])
        if args.limit:
            sel = sel[:args.limit]
        res = J.judge_items([J.to_item(c) for c in sel], workers=args.workers)
        tag = "enja"
    else:
        failed = [c for c in P if c["vi"] and c["cand_id"] in results.get("tri", {}) and not J.is_accept_tri(results["tri"][c["cand_id"]])
                  and results["tri"][c["cand_id"]].get("en_ja") in ("OK",)]
        items = []
        for c in failed:
            it = J.to_item(c, vi_lemma=None)
            it["id"] = c["cand_id"]
            items.append(it)
        res = J.judge_items(items, workers=args.workers)
        tag = "recheck"

    cur = json.loads(results_path.read_text()) if results_path.exists() else {}   # merge-on-write
    cur.setdefault(tag, {}).update(res)
    write_json(results_path, cur)
    ctr = Counter()
    for k, r in res.items():
        ctr[r.get("verdict")] += 1
        ctr["en_ja:" + str(r.get("en_ja"))] += 1
        ctr["en_vi:" + str(r.get("en_vi"))] += 1
        ctr["ja_vi:" + str(r.get("ja_vi"))] += 1
        if tag != "enja" and J.is_accept_tri(r):
            ctr["STRICT_TRI_ACCEPT"] += 1
        if tag in ("enja", "recheck") and J.is_accept_en_ja(r):
            ctr["EN_JA_ACCEPT"] += 1
    print(tag, len(res), dict(ctr))


if __name__ == "__main__":
    main()
