"""
scripts/phase1_4/lexicons.py
Loaders for every upstream reference used by Phase 1.4. Each loader reads ONLY from the
immutable raw snapshots in data/raw/ (after SHA-256 verification) and preserves a source
locator so that every derived fact is reconstructible.
"""

import csv
import gzip
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Dict, List, Tuple

from scripts.phase1_4.common import RAW_DIR, nfc, sha256_file


def verify_snapshot(source_id: str, version: str) -> Dict[str, Any]:
    d = RAW_DIR / source_id / version
    meta = json.loads((d / "metadata.json").read_text(encoding="utf-8"))
    art = d / meta["artifact_filename"]
    if sha256_file(art) != meta["artifact_sha256"]:
        raise ValueError(f"SHA-256 mismatch for raw snapshot {source_id}/{version}")
    return meta


# ---------------------------------------------------------------- English lists
def load_en_lists() -> Dict[str, Dict[str, Any]]:
    """lemma -> {ngsl_rank, ngsl_spoken_rank, nawl, bsl_rank, tsl_rank}. Rank = list rank."""
    out: Dict[str, Dict[str, Any]] = {}

    def put(lemma, key, val):
        lemma = lemma.strip().lower()
        if lemma:
            out.setdefault(lemma, {})[key] = val

    def _int(x):
        try:
            return int(str(x).strip())
        except ValueError:
            return None

    def rows(src, ver, fn, enc):
        verify_snapshot(src, ver)
        with open(RAW_DIR / src / ver / fn, "r", encoding=enc, errors="replace") as f:
            for i, row in enumerate(csv.reader(f)):
                if i == 0 or not row:
                    continue
                yield i + 1, row

    for ln, r in rows("ngsl", "1.2", "NGSL_12_stats.csv", "utf-8-sig"):
        put(r[0], "ngsl_rank", _int(r[1]))
    for ln, r in rows("ngsl_spoken", "1.2", "NGSL-Spoken_12_stats.csv", "utf-8-sig"):
        put(r[0], "ngsl_spoken_rank", _int(r[1]))
    for ln, r in rows("bsl", "1.2", "BSL_120_stats.csv", "latin-1"):
        put(r[0], "bsl_rank", _int(r[1]))
    for ln, r in rows("tsl", "1.2", "TSL_12_stats.csv", "latin-1"):
        put(r[0], "tsl_rank", _int(r[1]))
    verify_snapshot("nawl", "1.2")
    with open(RAW_DIR / "nawl/1.2/NAWL_12_lemmatized_for_teaching.csv", "r", encoding="latin-1") as f:
        for i, line in enumerate(f):
            if line.strip():
                put(line.split(",")[0], "nawl", i + 1)
    return out


# ---------------------------------------------------------------- Vietnamese
def load_vn_freq() -> Dict[str, Dict[str, Any]]:
    verify_snapshot("vn_freq", "1.0")
    out: Dict[str, Dict[str, Any]] = {}
    with open(RAW_DIR / "vn_freq/1.0/vn_word_frequencies.tsv", "r", encoding="utf-8") as f:
        for ln, line in enumerate(f, 1):
            p = line.rstrip("\n").split("\t")
            if len(p) < 3:
                continue
            w = nfc(p[2]).lower()
            if w not in out:
                out[w] = {"rank": int(p[0]), "count": int(p[1]),
                          "pos": [x.strip() for x in (p[3] if len(p) > 3 else "").split(",") if x.strip()],
                          "line": ln}
    return out


# ---------------------------------------------------------------- JLPT
def load_jlpt() -> List[Dict[str, Any]]:
    verify_snapshot("jlpt_consensus", "2026-v1")
    out = []
    with open(RAW_DIR / "jlpt_consensus/2026-v1/JLPT_vocab_ALL.csv", "r", encoding="utf-8-sig") as f:
        for ln, row in enumerate(csv.DictReader(f), 2):
            out.append({"kanji": nfc(row["Kanji"]), "reading": nfc(row["Reading"]),
                        "level": int(row["Level"]), "line": ln})
    return out


# ---------------------------------------------------------------- JMdict
_POS_MAP = {
    "n": "noun", "n-adv": "noun", "n-t": "noun", "n-suf": "noun", "n-pref": "noun", "n-pr": "noun",
    "vs": "noun", "vs-i": "noun", "vs-s": "noun", "pn": "pronoun", "num": "numeral", "ctr": "counter",
    "adj-i": "adjective", "adj-na": "adjective", "adj-no": "adjective", "adj-pn": "adjective",
    "adj-t": "adjective", "adj-f": "adjective", "adj-ix": "adjective",
    "adv": "adverb", "adv-to": "adverb", "conj": "conjunction", "int": "interjection", "prt": "particle",
    "exp": "expression", "aux": "auxiliary", "aux-v": "auxiliary", "aux-adj": "auxiliary",
    "pref": "prefix", "suf": "suffix", "cop": "copula",
}


_VERB_RE = __import__("re").compile(r"^(v1|v1-s|v2.*|v4.*|v5.*|vk|vz|vn|vr)$")


def jmdict_pos(tags: List[str]) -> str:
    """Coarse POS from JMdict tags. NOTE: 'vi'/'vt' are transitivity flags and 'vs*' marks suru-nouns, so
    neither makes an entry a verb by itself (a Phase 1.4 fix: 1.3C-era heuristics treated any v* as verb)."""
    for t in tags:
        if _VERB_RE.match(t):
            return "verb"
    for t in tags:
        if t in _POS_MAP:
            return _POS_MAP[t]
    return "noun"


def load_jmdict() -> Dict[int, Dict[str, Any]]:
    """ent_seq -> entry with kanji/reading elements, priority tags and sense-separated glosses."""
    meta = verify_snapshot("jmdict", "2026-10-01")
    path = RAW_DIR / "jmdict/2026-10-01/JMdict_e.gz"
    # JMdict defines its POS/misc tags as XML entities in the DTD; expand them to the codes.
    import re
    raw = gzip.open(path, "rb").read().decode("utf-8")
    ents = dict(re.findall(r'<!ENTITY ([^ ]+) "([^"]*)">', raw))
    raw = re.sub(r"<!DOCTYPE.*?\]>", "", raw, flags=re.S)
    raw = re.sub(r"&([A-Za-z0-9_-]+);", lambda m: "@@" + m.group(1) + "@@" if m.group(1) in ents else m.group(0), raw)
    root = ET.fromstring(raw)
    out: Dict[int, Dict[str, Any]] = {}
    for entry in root.iter("entry"):
        seq = int(entry.findtext("ent_seq"))
        kan = [{"text": k.findtext("keb"), "pri": [p.text for p in k.findall("ke_pri")],
                "inf": [i.text.strip("@") for i in k.findall("ke_inf")]} for k in entry.findall("k_ele")]
        rea = [{"text": r.findtext("reb"), "pri": [p.text for p in r.findall("re_pri")],
                "restr": [x.text for x in r.findall("re_restr")],
                "inf": [i.text.strip("@") for i in r.findall("re_inf")]} for r in entry.findall("r_ele")]
        senses = []
        last_pos: List[str] = []
        for si, s in enumerate(entry.findall("sense")):
            pos = [p.text.strip("@") for p in s.findall("pos")]
            if pos:
                last_pos = pos
            else:
                pos = last_pos
            senses.append({
                "idx": si,
                "pos_tags": pos,
                "pos": jmdict_pos(pos),
                "glosses": [g.text.strip() for g in s.findall("gloss")
                            if g.text and g.get("{http://www.w3.org/XML/1998/namespace}lang", "eng") == "eng"],
                "misc": [m.text.strip("@") for m in s.findall("misc")],
                "field": [m.text.strip("@") for m in s.findall("field")],
                "restr_kanji": [x.text for x in s.findall("stagk")],
                "restr_reading": [x.text for x in s.findall("stagr")],
            })
        out[seq] = {"seq": seq, "kanji": kan, "readings": rea, "senses": senses}
    return out


PRIORITY_COMMON = {"ichi1", "news1", "spec1", "spec2", "gai1"}


def pri_score(tags: List[str]) -> int:
    """Higher = more common. nfNN buckets are 500-word bands (nf01 = top 500)."""
    best = 0
    for t in tags:
        if t in PRIORITY_COMMON:
            best = max(best, 3)
        elif t in ("ichi2", "news2", "gai2"):
            best = max(best, 2)
        elif t.startswith("nf"):
            try:
                n = int(t[2:])
                best = max(best, 3 if n <= 24 else 2)
            except ValueError:
                pass
    return best


# ---------------------------------------------------------------- Wiktionary
def load_wikt() -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    meta = verify_snapshot("wiktionary_en", "2026-09-28")
    rows = []
    with gzip.open(RAW_DIR / "wiktionary_en/2026-09-28/wikt_en_translations.jsonl.gz", "rt", encoding="utf-8") as f:
        for ln, line in enumerate(f, 1):
            d = json.loads(line)
            d["_line"] = ln
            rows.append(d)
    return rows, meta
