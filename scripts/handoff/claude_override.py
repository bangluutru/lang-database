#!/usr/bin/env python3
"""Claude-only helper: record per-item overrides of Luna's T4 proposals.  usage: claude_override.py T4_002 coat=áo\ khoác repair=sửa\ chữa aim=NULL"""
import json, subprocess, sys
from pathlib import Path
R = Path(__file__).resolve().parent.parent.parent
packet, pairs = sys.argv[1], sys.argv[2:]
pk = {}
for l in (R / f"data/phase1_4/handoff/packets/{packet}.jsonl").read_text(encoding="utf-8").splitlines():
    d = json.loads(l); pk.setdefault(d["en"], []).append(d["id"])
p = R / "data/phase1_4/handoff/claude_overrides_T4.json"
o = json.loads(p.read_text(encoding="utf-8"))
dec = {json.loads(l)["id"]: json.loads(l) for l in (R / f"data/phase1_4/handoff/decisions/{packet}.jsonl").read_text(encoding="utf-8").splitlines()}
for kv in pairs:
    en, vi = kv.split("=", 1)
    for cid in pk[en]:
        o["overrides"][cid] = {"vi": None if vi == "NULL" else vi, "was": dec[cid].get("vi_lemma")}
p.write_text(json.dumps(o, ensure_ascii=False, indent=1), encoding="utf-8")
print(len(o["overrides"]), "overrides total")
subprocess.run(["git", "add", str(p.relative_to(R))], cwd=R, check=True)
subprocess.run(["git", "commit", "-q", "-m", f"docs(handoff): Claude T4 overrides ({packet})\n\nCo-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>"], cwd=R, check=True)
