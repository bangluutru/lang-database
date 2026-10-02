#!/usr/bin/env python3
"""
Offline lookup helper for reviewers (no network, no API).
  python scripts/phase1_4/handoff/lookup.py ja 猫            # JMdict entries/senses/glosses/POS/priority for a Japanese form
  python scripts/phase1_4/handoff/lookup.py en cat           # JMdict senses whose gloss equals the English word (reverse lookup)
  python scripts/phase1_4/handoff/lookup.py vi "sân bay"     # Vietnamese corpus frequency (vn_freq): rank, count, POS
  python scripts/phase1_4/handoff/lookup.py wikt airport     # Wiktionary extract: sense glosses + JA/VI translations for an English headword
"""
import gzip
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))
from scripts.phase1_4 import lexicons as L
from scripts.phase1_4.build_candidates import gloss_norm


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    kind, q = argv[0], " ".join(argv[1:])
    if kind in ("ja", "en"):
        jm = L.load_jmdict()
        for seq, e in sorted(jm.items()):
            forms = [k["text"] for k in e["kanji"]] + [r["text"] for r in e["readings"]]
            for s in e["senses"]:
                hit = (kind == "ja" and q in forms) or (kind == "en" and gloss_norm(q) in [gloss_norm(g) for g in s["glosses"]])
                if hit:
                    pri = max([L.pri_score(k["pri"]) for k in e["kanji"]] + [L.pri_score(r["pri"]) for r in e["readings"]] + [0])
                    print(f"ent_seq:{seq} sense:{s['idx']} pri:{pri} {'/'.join(k['text'] for k in e['kanji'][:2])} ({e['readings'][0]['text']}) "
                          f"[{','.join(s['pos_tags'])}] {s['glosses'][:6]} misc={s['misc']}")
    elif kind == "vi":
        r = L.load_vn_freq().get(q.lower())
        print(r or "not in vn_freq (not necessarily wrong; check naturalness yourself)")
    elif kind == "wikt":
        rows, _ = L.load_wikt()
        for r in rows:
            if r["word"].lower() == q.lower():
                print(f"[{r['pos']}] line {r['_line']}")
                for i, s in enumerate(r["senses"]):
                    tr = [(t["lang_code"], t["word"]) for t in s["translations"]]
                    print(f"   s{i}: {s['gloss'][:90]} {tr}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
