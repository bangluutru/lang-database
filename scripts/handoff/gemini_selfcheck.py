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


def t3_main(tid):
    """G3 (T3-style promotion review) mode."""
    import re
    from scripts.phase1_4.build_candidates import gloss_norm
    packet = {json.loads(l)["id"]: json.loads(l) for l in (REPO / f"data/phase1_4/handoff/packets/{tid}.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()}
    out = REPO / f"data/phase1_4/handoff/decisions/{tid}.jsonl"
    if not out.exists():
        print(f"missing {out.relative_to(REPO)}"); return 1
    rows = [json.loads(l) for l in out.read_text(encoding="utf-8").splitlines() if l.strip()]
    vn = L.load_vn_freq()
    jm = None
    block, warn, lines = [], [], []
    if [r["id"] for r in rows] != list(packet):
        block.append("ids/order differ from the packet")
    for r in rows:
        p = packet.get(r["id"])
        if not p:
            block.append(f"unknown id {r['id']}"); continue
        f, n = [], r["note"].strip()
        if r.get("reviewer") != "gemini-3.8":
            f.append("BLOCK reviewer must be exactly 'gemini-3.8'")
        if len(n) < 60:
            f.append("BLOCK note shorter than 60 chars")
        if r["verdict"] == "ACCEPT" and "falsified" not in n.lower():
            f.append("BLOCK ACCEPT note lacks 'falsified: ...' (rule H3 step 6)")
        rev = r.get("revision") or {}
        if r["verdict"] == "REVISE":
            if "ja" in rev:
                if jm is None:
                    jm = L.load_jmdict()
                want = gloss_norm(p["en"])
                ok = any(rev["ja"] in [k["text"] for k in e["kanji"]] + [x["text"] for x in e["readings"]] and any(want in [gloss_norm(g) for g in sn["glosses"]] for sn in e["senses"]) for e in jm.values())
                if not ok:
                    f.append(f"BLOCK revised ja '{rev['ja']}' not found in JMdict with a sense glossed '{p['en']}'")
                if not re.search(r"\d{6,8}", n):
                    f.append("BLOCK REVISE of ja must cite the ent_seq in note")
            if "vi" in rev and rev["vi"] not in vn:
                f.append("revised vi not in vn_freq (justify in note)")
        if p.get("vi") and r["verdict"] == "ACCEPT" and p["vi"] not in vn:
            f.append("ACCEPT with vi not in vn_freq: justify")
        if r["verdict"] == "ACCEPT" and r["confidence"] != "HIGH":
            f.append("BLOCK ACCEPT requires HIGH")
        if f:
            (block if any(x.startswith("BLOCK") for x in f) else warn).append(f"{p['en']}: " + "; ".join(f))
        lines.append(f"| {p['en']} | {p['ja']} | {p.get('vi')} | {r['verdict']} | {r['confidence']} | {', '.join(f) or 'ok'} |")
    from collections import Counter
    for dn, c in Counter(r["note"].strip() for r in rows).items():
        if c > 1:
            block.append(f"identical note used for several items: {dn[:70]}")
    acc = sum(r["verdict"] == "ACCEPT" for r in rows)
    if rows and acc / len(rows) > 0.5:
        warn.append(f"ACCEPT rate {acc}/{len(rows)} > 50%: over-lenient? re-run the falsify step on every ACCEPT")
    if rows and len(rows) >= 20 and acc / len(rows) < 0.05:
        warn.append("ACCEPT rate < 5%: over-strict?")
    for fn, label in ((f"worksheet_{tid}.md", "worksheet"), (f"self_review_{tid}.md", "self-review")):
        fp = REPO / "handoff/work" / fn
        if not fp.exists():
            block.append(f"missing handoff/work/{fn}")
        elif label == "worksheet":
            miss = [i for i in packet if i not in fp.read_text(encoding="utf-8")]
            if miss:
                block.append(f"worksheet has no block for {len(miss)} item(s), e.g. {miss[0]}")
    md = [f"# Selfcheck {tid} (T3 mode): {len(rows)} rows, {len(block)} blocking, {len(warn)} warnings", "", "| en | ja | vi | verdict | conf | flags |", "|---|---|---|---|---|---|", *lines, "",
          "## Blocking", *([f"- {b}" for b in block] or ["- none"]), "", "## Warnings", *([f"- {w}" for w in warn] or ["- none"])]
    path = REPO / "handoff/work" / f"selfcheck_{tid}.md"
    path.write_text("\n".join(md), encoding="utf-8")
    print("\n".join(md))
    return 1 if block else 0


def a1_main(tid):
    """A1 (authoring) mode: objective gates + required work files + confidence audit table."""
    from scripts.handoff import validate_authored as VA
    slots = [json.loads(l) for l in (REPO / f"data/phase1_4/handoff/packets/{tid}.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    out = REPO / f"data/phase1_4/handoff/decisions/{tid}.jsonl"
    if not out.exists():
        print(f"missing {out.relative_to(REPO)}"); return 1
    rows = [json.loads(l) for l in out.read_text(encoding="utf-8").splitlines() if l.strip()]
    res, fblock = VA.analyse(rows, slots)
    block = list(fblock)
    warn, lines = [], []
    by = {r["id"]: r for r in rows}
    for x in res:
        for b in x["block"]:
            block.append(f"{x['id']}: {b}")
        for w in x["warn"]:
            warn.append(f"{x['id']}: {w}")
        r = by.get(x["id"], {})
        if x.get("skip"):
            lines.append(f"| {x['id']} | SKIP | - | - | - | {r.get('reason', '')[:50]} |")
        else:
            e = x["evidence"]
            lines.append(f"| {x['id']} | {r.get('en', {}).get('lemma')} / {r.get('ja', {}).get('lemma')} / {r.get('vi', {}).get('lemma')} | {r.get('confidence')} | {x['ceiling']} | pri={e.get('ja_pri')} field={e.get('ja_field_match')} vnrank={e.get('vi_vn_freq_rank')} wiktvi={e.get('vi_in_wikt')} | {'BLOCK' if x['block'] else 'ok'} |")
    done = [r for r in rows if not r.get("skip")]
    high = sum(r.get("confidence") == "HIGH" for r in done)
    if done and len(done) >= 10 and high / len(done) > 0.6:
        warn.append(f"HIGH share {high}/{len(done)} > 60%: Gemini's confidence tends to run above reality. Re-run the falsification for every HIGH.")
    skips = len(rows) - len(done)
    if skips > len(rows) * 0.4:
        warn.append(f"{skips} skipped slots (> 40%): explain in the report")
    wdir = REPO / "handoff/work"
    ws = wdir / f"worksheet_{tid}.md"
    if not ws.exists():
        block.append(f"missing handoff/work/worksheet_{tid}.md")
    else:
        t = ws.read_text(encoding="utf-8")
        miss = [s_["id"] for s_ in slots if s_["id"] not in t]
        if miss:
            block.append(f"worksheet has no block for {len(miss)} slot(s), e.g. {miss[0]}")
    rep = wdir / f"report_{tid}.md"
    need = ["## Mechanical results", "## Confidence audit", "## Least sure", "## Skipped slots", "## Declaration"]
    if not rep.exists():
        block.append(f"missing handoff/work/report_{tid}.md (review report, see Part I6)")
    else:
        rt = rep.read_text(encoding="utf-8")
        for h in need:
            if h not in rt:
                block.append(f"report lacks heading '{h}'")
        if "I have not run git and have not modified any file outside my write zones." not in rt:
            block.append("report lacks the exact Declaration sentence")
        miss = [r["id"] for r in done if r["id"] not in rt.split("## Confidence audit")[-1]] if "## Confidence audit" in rt else []
        if miss:
            block.append(f"Confidence audit section does not mention {len(miss)} entries, e.g. {miss[0]}")
    if not (wdir / f"self_review_{tid}.md").exists():
        block.append(f"missing handoff/work/self_review_{tid}.md")
    md = [f"# Selfcheck {tid} (A1 authoring): {len(rows)} rows, {len(block)} blocking, {len(warn)} warnings", "",
          "| slot | en / ja / vi | claimed | ceiling | objective evidence | gate |", "|---|---|---|---|---|---|", *lines, "",
          "## Blocking", *([f"- {b}" for b in block] or ["- none"]), "", "## Warnings", *([f"- {w}" for w in warn] or ["- none"])]
    (wdir / f"selfcheck_{tid}.md").write_text("\n".join(md), encoding="utf-8")
    print("\n".join(md))
    return 1 if block else 0


def main(tid):
    if tid.startswith("A1"):
        return a1_main(tid)
    if tid.startswith("G3"):
        return t3_main(tid)
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
