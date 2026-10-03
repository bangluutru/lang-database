#!/usr/bin/env python3
"""
scripts/phase1_4/handoff/validate_decisions.py
Machine gate for decisions written by an external agent (GPT 6 Luna). Usage:
    python scripts/phase1_4/handoff/validate_decisions.py data/phase1_4/handoff/decisions/T1_001.jsonl [...]
Exit code != 0 if ANY line violates the schema. Content quality is judged by the human/Claude reviewer; this only
guarantees format, enumerations, id integrity and internal consistency, so reviewers never waste time on malformed output.
"""
import json
import re
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent.parent.parent
PACKETS = BASE / "data/phase1_4/handoff/packets"
PAIR = {"OK", "BROAD", "NARROW", "WRONG", "NA"}
NAT = {"NATURAL", "ACCEPTABLE", "AWKWARD", "WRONG"}
CONF = {"HIGH", "MEDIUM", "LOW"}
VERD = {"ACCEPT", "REVISE", "REJECT"}
POS = {"noun", "verb", "adjective", "adverb", "pronoun", "preposition", "conjunction", "interjection", "numeral", "determiner", "expression", "particle"}
VI_RE = re.compile(r"^[a-zàáảãạăằắẳẵặâầấẩẫậđèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵ ]+$")
KANA_KANJI = re.compile(r"[぀-ヿ一-鿿々ー]")
REVIEWER = re.compile(r"^[a-z0-9 ._()-]{3,60}$")


def packet_ids(task):
    ids = set()
    for p in sorted(list(PACKETS.glob(f"{task}_*.jsonl")) + list(PACKETS.glob(f"G{task[1:]}_*.jsonl"))):   # G3_/G4_ = Gemini packets
        for l in p.read_text(encoding="utf-8").splitlines():
            if l.strip():
                ids.add(json.loads(l)["id"])
    return ids


def check(d, valid_ids, errs, where):
    def bad(m):
        errs.append(f"{where}: {m}")

    t = d.get("task")
    if t not in ("T1", "T2", "T3", "T4"):
        return bad("task must be T1|T2|T3|T4")
    if d.get("id") not in valid_ids[t]:
        return bad(f"id {d.get('id')} is not in the {t} packets")
    if not REVIEWER.match(str(d.get("reviewer", "")).lower()):
        bad("reviewer missing (use e.g. 'gpt-6-luna')")
    if d.get("confidence") not in CONF:
        bad("confidence must be HIGH|MEDIUM|LOW")
    note = str(d.get("note", ""))
    if len(note.strip()) < 15:
        bad("note must explain the decision in >= 15 characters")
    if t == "T4":
        v = d.get("vi_lemma")
        if v is not None:
            if not isinstance(v, str) or not VI_RE.match(v) or len(v.split()) > 4:
                bad("vi_lemma must be 1-4 Vietnamese syllable-words, lower-case, no punctuation (or null if no good equivalent)")
        syn = d.get("synonyms", [])
        if not isinstance(syn, list) or len(syn) > 1 or any(not VI_RE.match(str(s)) for s in syn):
            bad("synonyms: list of at most 1 valid Vietnamese form")
        if v is None and d.get("confidence") == "HIGH":
            bad("null vi_lemma cannot be HIGH confidence")
        return
    if d.get("verdict") not in VERD:
        return bad("verdict must be ACCEPT|REVISE|REJECT")
    for k in ("en_ja", "en_vi", "ja_vi"):
        if d.get(k) not in PAIR:
            bad(f"{k} must be one of {sorted(PAIR)}")
    if d.get("naturalness") not in NAT:
        bad("naturalness invalid")
    rev = d.get("revision")
    if d["verdict"] == "ACCEPT":
        if rev:
            bad("ACCEPT must not carry a revision")
        if any(d.get(k) not in ("OK", "NA") for k in ("en_ja", "en_vi", "ja_vi")):
            bad("ACCEPT requires every pair OK/NA")
        if d.get("confidence") != "HIGH" or d.get("naturalness") not in ("NATURAL", "ACCEPTABLE"):
            bad("ACCEPT requires HIGH confidence and NATURAL/ACCEPTABLE")
    if d["verdict"] == "REVISE":
        if not isinstance(rev, dict) or not set(rev) <= {"ja", "vi", "pos"} or not rev:
            return bad("REVISE needs revision {ja?, vi?, pos?}")
        if "ja" in rev and not KANA_KANJI.search(str(rev["ja"])):
            bad("revision.ja must be Japanese script")
        if "vi" in rev and not VI_RE.match(str(rev["vi"])):
            bad("revision.vi must be Vietnamese lower-case words")
        if "pos" in rev and rev["pos"] not in POS:
            bad(f"revision.pos must be one of {sorted(POS)}")
    if d["verdict"] == "REJECT" and rev:
        bad("REJECT must not carry a revision")
    if t == "T2" and d["verdict"] == "ACCEPT":
        bad("T2 items are known-defective: use REVISE (with a JMdict-glossed ja) or REJECT (= no verifiable fix)")


def main(paths):
    if paths and Path(paths[0]).name.startswith("A1_"):         # Gemini authoring tasks have their own mechanical gate
        sys.path.insert(0, str(BASE))
        from scripts.handoff import validate_authored
        return validate_authored.main(paths[0])
    valid = {t: packet_ids(t) for t in ("T1", "T2", "T3", "T4")}
    errs, seen = [], set()
    n = 0
    for p in paths:
        for i, l in enumerate(Path(p).read_text(encoding="utf-8").splitlines(), 1):
            if not l.strip():
                continue
            n += 1
            try:
                d = json.loads(l)
            except json.JSONDecodeError as e:
                errs.append(f"{p}:{i}: invalid JSON ({e})")
                continue
            key = (d.get("task"), d.get("id"))
            if key in seen:
                errs.append(f"{p}:{i}: duplicate decision for {key}")
            seen.add(key)
            check(d, valid, errs, f"{p}:{i}")
    print(f"{n} decisions checked, {len(errs)} problems")
    for e in errs[:50]:
        print("  ", e)
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
