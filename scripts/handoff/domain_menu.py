#!/usr/bin/env python3
"""
Grounded candidate menu for Gemini 'A1' authoring (offline; JMdict + canonical).
  python scripts/handoff/domain_menu.py --domain it [--grep network] [--limit 40] [--min-pri 1]
Lists JMdict (entry, sense) pairs tagged with the domain's field tags that are NOT yet in the corpus (JA lemma and EN gloss both absent),
sorted by commonness. Choosing from this menu is the safest way to author an entry; terms you add from your own knowledge must still pass validate_authored.py.
"""
import argparse
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from scripts.handoff.authoring_common import DOMAIN_FIELDS, BLOCK_MISC, jm, entry_pri, canonical, gloss_norm  # noqa


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--domain", required=True, choices=sorted(DOMAIN_FIELDS))
    ap.add_argument("--fields", help="override comma list of JMdict field tags")
    ap.add_argument("--grep", help="keep rows whose English glosses contain this text")
    ap.add_argument("--limit", type=int, default=40)
    ap.add_argument("--min-pri", type=int, default=1)
    ap.add_argument("--status", default="NEW", choices=["NEW", "ALL"])
    a = ap.parse_args()
    fields = set((a.fields.split(",") if a.fields else DOMAIN_FIELDS[a.domain]))
    if not fields:
        print(f"no JMdict field tag exists for '{a.domain}'. Use `python scripts/phase1_4/handoff/lookup.py en <word>` and `wikt <word>` to find grounded terms."); return 0
    lex, pairs = canonical()
    rows = []
    for seq, e in jm().items():
        pri = entry_pri(e)
        if pri < a.min_pri:
            continue
        forms = [k["text"] for k in e["kanji"]] or [r["text"] for r in e["readings"]]
        for s in e["senses"]:
            if not (set(s["field"]) & fields) or (set(s["misc"]) & BLOCK_MISC):
                continue
            g = [x for x in s["glosses"] if len(x.split()) <= 3][:4]
            if not g or (a.grep and not any(a.grep.lower() in x.lower() for x in s["glosses"])):
                continue
            ja_in = ("ja", forms[0].lower()) in lex
            en_in = any(("en", gloss_norm(x)) in lex for x in g)
            status = "NEW" if not (ja_in or en_in) else ("JA_EXISTS" if ja_in else "EN_EXISTS")
            if a.status == "NEW" and status != "NEW":
                continue
            rows.append((-pri, seq, s["idx"], forms[0], e["readings"][0]["text"], s["pos_tags"], g, status))
    rows.sort()
    for pri, seq, idx, f, r, pos, g, st in rows[: a.limit]:
        print(f"ent_seq:{seq} sense:{idx} pri:{-pri} {f} ({r}) {pos} {g} [{st}]")
    print(f"-- {len(rows)} rows match; showing {min(len(rows), a.limit)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
