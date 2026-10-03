#!/usr/bin/env python3
"""
scripts/handoff/gemini_selfcheck.py - mechanical self-check for a T4 decision file BEFORE `luna-done`.
Usage:  python scripts/handoff/gemini_selfcheck.py T4_059
Writes handoff/work/selfcheck_<task>.md and prints it. Exit 0 = no blocking problem, 1 = fix the listed items first.
It only reads local files (no network, no API). Flags are hints: you must either change the item or explain in `note` why the flag is a false alarm.
"""
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO))
from scripts.phase1_4 import lexicons as L

REGIONAL = {"mền", "má", "ba", "tía", "heo", "bự", "nhóc", "thiệt", "hổng", "nghen", "tui", "mần", "chén", "bắp", "đậu phộng", "dzô"}
PEJORATIVE = {"thằng", "con mụ", "đồ", "lũ"}


def main(tid):
    packet = {json.loads(l)["id"]: json.loads(l) for l in (REPO / f"data/phase1_4/handoff/packets/{tid}.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()}
    out = REPO / f"data/phase1_4/handoff/decisions/{tid}.jsonl"
    if not out.exists():
        print(f"missing {out.relative_to(REPO)}"); return 1
    rows = [json.loads(l) for l in out.read_text(encoding="utf-8").splitlines() if l.strip()]
    vn = L.load_vn_freq()
    block, warn, lines = [], [], []
    if [r["id"] for r in rows] != list(packet):
        block.append("ids/order differ from the packet (must be same items, same order, none missing)")
    for r in rows:
        p = packet.get(r["id"])
        if not p:
            block.append(f"unknown id {r['id']}"); continue
        v, f = r.get("vi_lemma"), []
        if r.get("reviewer") != "gemini-3.8":
            block.append(f"{p['en']}: reviewer must be exactly 'gemini-3.8'")
        if v:
            if v.lower() == p["en"].lower() and "loanword" not in r["note"].lower():
                f.append("BLOCK copies the English word (allowed only if note says 'loanword' and why)")
            if v == (p.get("rejected_vi_before") or ""):
                f.append("BLOCK equals rejected_vi_before")
            if v not in vn:
                f.append("not in vn_freq (ok only if you are sure it is a normal modern word; then say so in note)")
            if len(v.split()) > 3:
                f.append("more than 3 syllable-words: is there a shorter standard word?")
            if any(w in REGIONAL for w in v.split()) or any(w in v for w in PEJORATIVE):
                f.append("regional/pejorative marker word")
            if p["pos"] == "verb" and v.split()[0] in ("sự", "việc", "cuộc", "nỗi"):
                f.append("verb concept but VI starts like a noun (POS mismatch)")
            if p["pos"] == "noun" and v.split()[0] in ("làm", "thực", "bị", "được"):
                f.append("noun concept but VI starts like a verb (POS mismatch)")
            if p["pos"] == "adjective" and v.split()[0] in ("sự", "việc", "cuộc"):
                f.append("adjective concept but VI is noun-like")
            if r["confidence"] == "HIGH" and v not in vn and "attest" not in r["note"].lower() and "standard" not in r["note"].lower():
                f.append("HIGH without attestation: note must say why it is standard")
        else:
            if r["confidence"] == "HIGH":
                f.append("BLOCK null vi_lemma cannot be HIGH")
        syn = r.get("synonyms") or []
        if syn and v and syn[0] == v:
            f.append("BLOCK synonym equals vi_lemma")
        if len(r["note"].strip()) < 40:
            f.append("BLOCK note shorter than 40 chars (needs sense + evidence + rejected alternative)")
        if r["confidence"] != "HIGH" and not any(w in r["note"].lower() for w in ("doubt", "unsure", "uncertain", "but", "however", "although", "not in vn_freq", "no single")):
            f.append("MEDIUM/LOW without a stated doubt in note")
        if r["confidence"] == "HIGH" and "back-translation" not in r["note"].lower():
            f.append("BLOCK HIGH note lacks 'back-translation = ...' (rule B2 step 5g)")
        if v and v == (p.get("rejected_vi_before") or "") and r["confidence"] != "LOW":
            f.append("BLOCK rejected_vi_before reused")
        if r["confidence"] == "HIGH" and v and v in vn and f"rank {vn[v]['rank']}" not in r["note"] and str(vn[v]["rank"]) not in r["note"]:
            f.append("HIGH and in vn_freq but note does not quote the rank")
        if f:
            (block if any(x.startswith("BLOCK") for x in f) else warn).append(f"{p['en']} -> {v}: " + "; ".join(f))
        lines.append(f"| {p['en']} | {p['pos']} | {p['ja']} | {v} | {r['confidence']} | {', '.join(f) or 'ok'} |")
    from collections import Counter
    dup = [n for n, c in Counter(r["note"].strip() for r in rows).items() if c > 1]
    for n in dup:
        block.append(f"identical note used for several items: {n[:70]}")
    high = sum(r["confidence"] == "HIGH" for r in rows)
    if rows and high == len(rows) and len(rows) >= 10:
        warn.append("100% HIGH: re-examine your calibration (expected 40-70% on easy packets)")
    ws = REPO / "handoff/work" / f"worksheet_{tid}.md"
    if not ws.exists():
        block.append(f"missing {ws.relative_to(REPO)} (Part C)")
    else:
        wt = ws.read_text(encoding="utf-8")
        miss = [p_["id"] for p_ in packet.values() if p_["id"] not in wt]
        if miss:
            block.append(f"worksheet has no block for {len(miss)} item(s), e.g. {miss[0]}")
    if not (REPO / "handoff/work" / f"self_review_{tid}.md").exists():
        block.append(f"missing handoff/work/self_review_{tid}.md (Part C)")
    md = [f"# Selfcheck {tid}: {len(rows)} rows, {len(block)} blocking, {len(warn)} warnings", "",
          "| en | pos | ja | vi | conf | flags |", "|---|---|---|---|---|---|", *lines, "",
          "## Blocking", *([f"- {b}" for b in block] or ["- none"]), "", "## Warnings", *([f"- {w}" for w in warn] or ["- none"])]
    path = REPO / "handoff/work" / f"selfcheck_{tid}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(md), encoding="utf-8")
    print("\n".join(md))
    return 1 if block else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
