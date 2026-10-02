#!/usr/bin/env python3
"""Claude-only helper: record which of Luna's T3 ACCEPT decisions Claude confirms for promotion.
usage: claude_accept.py T3_001 sit hot because ...   (English headwords of Luna-ACCEPTed items in that packet)"""
import json, subprocess, sys
from pathlib import Path
R = Path(__file__).resolve().parent.parent.parent
packet, words = sys.argv[1], sys.argv[2:]
pk = {}
for l in (R / f"data/phase1_4/handoff/packets/{packet}.jsonl").read_text(encoding="utf-8").splitlines():
    d = json.loads(l); pk.setdefault(d["en"], []).append(d["id"])
dec = {json.loads(l)["id"]: json.loads(l) for l in (R / f"data/phase1_4/handoff/decisions/{packet}.jsonl").read_text(encoding="utf-8").splitlines()}
p = R / "data/phase1_4/handoff/claude_review_T3.json"
o = json.loads(p.read_text(encoding="utf-8")) if p.exists() else {"note": "T3 candidates promoted: Luna ACCEPT(HIGH) AND confirmed by Claude", "accepted": []}
for w in words:
    for cid in pk[w]:
        assert dec[cid]["verdict"] == "ACCEPT", (w, dec[cid]["verdict"])
        if cid not in o["accepted"]:
            o["accepted"].append(cid)
o["accepted"].sort()
p.write_text(json.dumps(o, ensure_ascii=False, indent=1), encoding="utf-8")
print(len(o["accepted"]), "accepted total")
subprocess.run(["git", "add", str(p.relative_to(R))], cwd=R, check=True)
subprocess.run(["git", "commit", "-q", "-m", f"docs(handoff): Claude T3 promotions ({packet})\n\nCo-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>"], cwd=R, check=True)
