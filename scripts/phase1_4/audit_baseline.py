#!/usr/bin/env python3
"""
scripts/phase1_4/audit_baseline.py
Read-only linguistic audit of a deterministic sample of the SEALED Phase 1.3D complete core concepts using the
same blind pairwise gate judge. It never modifies canonical data: findings are written to
reports/phase1_4/baseline_defect_audit.json for separate, documented follow-up (frozen-baseline rule).
"""
import hashlib, json, re, sys
from collections import Counter, defaultdict
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from scripts.phase1_4.common import CANONICAL_DIR, REPORTS_DIR, read_jsonl, write_json
from scripts.phase1_4 import judge as J, lexicons as L

N = 150

def main():
    man = json.loads((Path(__file__).resolve().parent.parent.parent / "data/releases/phase1_3d-sealed/baseline_manifest.json").read_text())
    nb = man["append_only"]["expressions.jsonl"]["lines"]
    exprs = read_jsonl(CANONICAL_DIR / "expressions.jsonl")[:nb]
    senses = {s["concept_id"]: s for s in read_jsonl(CANONICAL_DIR / "senses.jsonl")[:man["append_only"]["senses.jsonl"]["lines"]]}
    by = defaultdict(lambda: defaultdict(list))
    for e in exprs:
        by[e["concept_id"]][e["language"]].append(e)
    jm = L.load_jmdict()
    pool = [c for c in sorted(by) if c.startswith("concept-core-") and by[c]["vi"] and by[c]["ja"] and by[c]["en"]]
    pool.sort(key=lambda c: hashlib.sha256(c.encode()).hexdigest())
    items = []
    for cid in pool[:N]:
        e, j, v = by[cid]["en"][0], by[cid]["ja"][0], by[cid]["vi"][0]
        gl = []
        for ev in j["source_evidence"]:
            m = re.match(r"ent_seq:(\d+), sense_idx:(\d+)", ev.get("source_locator") or "")
            if m and int(m.group(1)) in jm:
                gl = jm[int(m.group(1))]["senses"][int(m.group(2))]["glosses"][:6]
        items.append({"id": cid, "en": e["lemma"], "en_pos": e["part_of_speech"], "en_sense": senses[cid]["definition_en"][:300],
                      "ja": j["lemma"], "ja_reading": j["reading"], "ja_pos": j["part_of_speech"], "ja_glosses": gl, "vi": v["lemma"]})
    res = J.judge_items(items, workers=8)
    rows = [{"concept_id": i["id"], "en": i["en"], "ja": i["ja"], "vi": i["vi"], "vi_provenance": by[i["id"]]["vi"][0]["provenance_type"],
             "judge": res.get(i["id"])} for i in items]
    acc = sum(1 for r in rows if r["judge"] and J.is_accept_tri(r["judge"]))
    pairs = Counter()
    for r in rows:
        if r["judge"]:
            for k in ("en_ja", "en_vi", "ja_vi"):
                pairs[f"{k}:{r['judge'].get(k)}"] += 1
    summary = {"sample": len(rows), "strict_accept": acc, "strict_accept_rate": round(acc / max(1, len(rows)), 3),
               "pair_verdicts": dict(pairs), "note": "Sealed baseline is NOT modified; defects are reported only."}
    write_json(REPORTS_DIR / "baseline_defect_audit.json", {"summary": summary, "records": rows})
    print(json.dumps(summary, indent=1))

if __name__ == "__main__":
    main()
