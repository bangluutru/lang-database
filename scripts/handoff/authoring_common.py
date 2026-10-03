"""Shared offline lookups for Gemini 'A1' authoring tasks (JMdict, Wiktionary translations, vn_freq, canonical). No network, no API."""
import json
import sys
from functools import lru_cache
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO))
from scripts.phase1_4 import lexicons as L                      # noqa: E402
from scripts.phase1_4.build_candidates import gloss_norm        # noqa: E402

DOMAIN_FIELDS = {"it": ["comp", "internet"], "healthcare": ["med", "anat", "psy"], "travel": [], "manufacturing": ["engr", "mech", "elec"]}
BLOCK_MISC = {"arch", "obs", "rare", "vulg", "sl", "derog", "col", "joc", "dated", "hist"}
POS_MAP = {"noun": lambda t: t.startswith("n") or t.startswith("vs") or t in ("ctr",),
           "verb": lambda t: t.startswith("v"), "adjective": lambda t: t.startswith("adj"), "adverb": lambda t: t.startswith("adv"),
           "expression": lambda t: t in ("exp", "int", "conj"), "determiner": lambda t: t in ("adj-pn", "adj-no")}


@lru_cache(None)
def jm():
    return L.load_jmdict()


@lru_cache(None)
def vn():
    return L.load_vn_freq()


@lru_cache(None)
def wikt_vi():
    """english word (lower) -> set of Vietnamese translation lemmas listed by Wiktionary for any sense"""
    rows, _ = L.load_wikt()
    out = {}
    for r in rows:
        for s in r["senses"]:
            for t in s["translations"]:
                if t["lang_code"] == "vi":
                    out.setdefault(r["word"].lower(), set()).add(t["word"].lower())
    return out


@lru_cache(None)
def wikt_glosses():
    rows, _ = L.load_wikt()
    out = {}
    for r in rows:
        out.setdefault(r["word"].lower(), []).extend(s["gloss"].lower() for s in r["senses"])
    return out


@lru_cache(None)
def canonical():
    """returns (set of (lang, lemma_lower), {(en_lemma_lower, ja_lemma): concept_id})"""
    lex, pairs, by = set(), {}, {}
    for l in open(REPO / "data/canonical/expressions.jsonl", encoding="utf-8"):
        e = json.loads(l)
        if e.get("status") == "retracted":
            continue
        lex.add((e["language"], e["lemma"].lower()))
        by.setdefault(e["concept_id"], {})[e["language"]] = e["lemma"].lower()
    for cid, d in by.items():
        if "en" in d and "ja" in d:
            pairs[(d["en"], d["ja"])] = cid
    return lex, pairs


def entry_forms(e):
    return [k["text"] for k in e["kanji"]] + [r["text"] for r in e["readings"]]


def entry_pri(e):
    return max([L.pri_score(k["pri"]) for k in e["kanji"]] + [L.pri_score(r["pri"]) for r in e["readings"]] + [0])
