#!/usr/bin/env python3
"""
Builds data/phase1_4/validation_overrides.json from Luna's T1 decisions (independent model review of Claude's baseline corrections).
A corrected baseline concept becomes `validated` ONLY if Luna returned ACCEPT with HIGH confidence AND the concept was not changed
afterwards (not in a later correction part). Provenance is never touched; the basis is recorded.
"""
import glob, hashlib, json, sys
from pathlib import Path
R = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(R))
later = set()
for p in sorted(glob.glob(str(R / "data/phase1_4/baseline_fixes/part6*.tsv"))) + sorted(glob.glob(str(R / "data/phase1_4/baseline_fixes/part[7-9]*.tsv"))):
    for l in open(p, encoding="utf-8"):
        if l.strip() and not l.startswith("#"):
            later.add("concept-" + l.split("\t")[0])
out = {}
for p in sorted(glob.glob(str(R / "data/phase1_4/handoff/decisions/T[12]_*.jsonl"))):
    for l in open(p, encoding="utf-8"):
        d = json.loads(l)
        if d["task"] == "T1" and d["verdict"] == "ACCEPT" and d["confidence"] == "HIGH" and d["id"] not in later:
            out[d["id"]] = {"status": "validated", "basis": "independent_agent_review", "reviewer": d["reviewer"], "task": "T1",
                            "decision_sha256": hashlib.sha256(l.strip().encode()).hexdigest()}
(R / "data/phase1_4/validation_overrides.json").write_text(json.dumps(dict(sorted(out.items())), ensure_ascii=False, indent=1), encoding="utf-8")
print(len(out), "concepts validated by independent review;", len(later), "re-edited after review (stay needs_review)")
