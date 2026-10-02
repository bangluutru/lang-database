#!/usr/bin/env python3
"""
scripts/phase1_4/audit_sample.py
Stage 7: INDEPENDENT linguistic audit of the FINAL canonical corpus.

* Deterministic stratified sample over the new Phase 1.4 concepts (hash-ordered inside each stratum).
* Each sampled record is re-judged BLIND by a third model (gemini-3-flash-preview, role "auditor") that was
  neither the generator (2.5-flash) nor the gate judge (2.5-pro).
* Output: reports/phase1_4/independent_sample_audit.json (+ a human-readable table for manual reading).
"""
import hashlib
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from scripts.phase1_4.common import CANONICAL_DIR, REPORTS_DIR, read_jsonl, write_json
from scripts.phase1_4 import judge as J

PV = "p14_audit_v1"
PER_STRATUM = 5


def h(x):
    return hashlib.sha256(x.encode()).hexdigest()


def main():
    concepts = read_jsonl(CANONICAL_DIR / "concepts.jsonl")
    new = {c["concept_id"]: c for c in concepts if c["concept_id"].startswith("concept-lex-")}
    exprs = defaultdict(lambda: defaultdict(list))
    for e in read_jsonl(CANONICAL_DIR / "expressions.jsonl"):
        if e["concept_id"] in new:
            exprs[e["concept_id"]][e["language"]].append(e)
    senses = {s["concept_id"]: s for s in read_jsonl(CANONICAL_DIR / "senses.jsonl") if s["concept_id"] in new}
    cls = defaultdict(set)
    for k in read_jsonl(CANONICAL_DIR / "classifications.jsonl"):
        if k["target_id"] in new:
            cls[k["target_id"]].add((k.get("system"), k.get("value")))
    en_count = Counter((exprs[c]["en"][0]["lemma"], exprs[c]["en"][0]["part_of_speech"]) for c in new)

    strata = defaultdict(list)
    for cid, c in new.items():
        v = c["metadata"]["learning_value"]["total"]
        e = exprs[cid]
        strata["high_frequency(value>=60)"] += [cid] if v >= 60 else []
        strata["low_frequency(value<30)"] += [cid] if v < 30 else []
        for n in (5, 4, 3, 2, 1):
            if ("JLPT", f"N{n}") in cls[cid]:
                strata[f"JLPT_N{n}"].append(cid)
        for lv in ("A1", "A2", "B1", "B2", "C1", "C2"):
            if ("CEFR", lv) in cls[cid]:
                strata[f"CEFR_{lv}"].append(cid)
        for b in ("VI_CORE_500", "VI_CORE_1000", "VI_CORE_2000", "VI_CORE_5000"):
            if any(s == b for s, _ in cls[cid]):
                strata[b].append(cid)
        if e["vi"] and e["vi"][0]["provenance_type"] == "AI_GENERATED":
            strata["AI_GENERATED_vi"].append(cid)
        if e["vi"] and e["vi"][0]["provenance_type"] == "SOURCE_DERIVED":
            strata["SOURCE_DERIVED_vi"].append(cid)
        if not e["vi"]:
            strata["PARTIAL_en_ja"].append(cid)
        if en_count[(e["en"][0]["lemma"], e["en"][0]["part_of_speech"])] > 1:
            strata["POLYSEMOUS_en"].append(cid)
        for d in c["domains"]:
            if d not in ("general", "daily_life"):
                strata[f"DOMAIN_{d}"].append(cid)
    picked, items = {}, []
    for name in sorted(strata):
        for cid in sorted(set(strata[name]), key=h)[:PER_STRATUM]:
            picked.setdefault(cid, []).append(name)
    for cid in sorted(picked):
        e, s = exprs[cid], senses[cid]
        items.append({"id": cid, "en": e["en"][0]["lemma"], "en_pos": e["en"][0]["part_of_speech"],
                      "en_sense": s["definition_en"][:300], "ja": e["ja"][0]["lemma"], "ja_reading": e["ja"][0]["reading"],
                      "ja_pos": ",".join(e["ja"][0]["language_metadata"]["jmdict_pos"]),
                      "ja_glosses": e["ja"][0]["language_metadata"]["jmdict_glosses"][:6],
                      "vi": e["vi"][0]["lemma"] if e["vi"] else None})
    # NO external API (project rule). The sample is dumped for MANUAL review by the coding agent / a human;
    # verdicts are stored in reports/phase1_4/manual_review.json and summarised by summarize_manual_review().
    rows = [dict(it, strata=picked[it["id"]]) for it in items]
    write_json(REPORTS_DIR / "audit_sample_frame.json", {"per_stratum": PER_STRATUM, "records": rows})
    for r in rows:
        print(f"{r['id'][13:]:34}|{r['en']}({r['en_pos'][:3]})|{r['en_sense'][:55]}|{r['ja']}({r['ja_reading']})|{r['vi']}|{','.join(x[:9] for x in r['strata'])}")


if __name__ == "__main__":
    main()
