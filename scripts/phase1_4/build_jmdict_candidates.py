#!/usr/bin/env python3
"""
scripts/phase1_4/build_jmdict_candidates.py
Wave-2 candidate source: JMdict-ANCHORED EN-JA candidates that fill curriculum gaps left by the
Wiktionary route (no Wiktionary sense block exists for them).

  A. JA-seeded  : JLPT (N5..N2, plus N1 entries with JMdict priority) entries not yet covered. Sense = a JMdict
                  sense of that entry (first sense whose POS/register are usable); EN headword = its first
                  short gloss.
  B. EN-seeded  : NGSL / NGSL-Spoken / BSL / TSL / NAWL lemmas not yet covered. JMdict senses whose FIRST gloss
                  equals the lemma (reverse lookup), best by priority/JLPT, at most one per (lemma, POS).

These candidates carry NO Vietnamese; they can only become tri-language via the AI route (AI_GENERATED VI,
independently judged) or stay legitimately partial. The anchor is recorded (`en.anchor = "jmdict"`) so that
provenance reflects that the EN gloss comes from JMdict, not from Wiktionary.
"""
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, List

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from scripts.phase1_4.common import CANONICAL_DIR, P14_DIR, read_jsonl, write_jsonl, write_json, baseline_expressions
from scripts.phase1_4 import lexicons as L
from scripts.phase1_4.build_candidates import preferred_form, gloss_norm, en_headword_ok, BAD_TR_TAGS

BAD_MISC = {"vulg", "derog", "obs", "arch", "obsc", "sl", "rare", "X", "joc", "id", "poet", "hist", "uk-only"}
EN_POS = {"noun": "noun", "verb": "verb", "adjective": "adjective", "adverb": "adverb", "pronoun": "pronoun",
          "numeral": "numeral", "conjunction": "conjunction", "interjection": "interjection", "counter": "noun"}


KNOWN_EN: set = set()


def headword_from_glosses(glosses: List[str], pos: str):
    """First of the leading glosses that is a *real English headword* (present in an English curriculum list, in the
    Wiktionary extract, or already an EN lemma in the corpus) and POS-consistent with the JMdict marking."""
    for g in glosses[:4]:
        n = gloss_norm(g)
        if not n or "," in g or ";" in g or len(n.split()) > 3 or not en_headword_ok(n):
            continue
        if (pos == "verb") != g.lower().startswith("to "):
            continue
        if n in KNOWN_EN:
            return n
    return None


def usable_sense(e, s, restr_ok=True):
    if set(s["misc"]) & BAD_MISC or not s["glosses"]:
        return False
    if s["pos"] not in EN_POS:
        return False
    return True


def ent_pri(e) -> int:
    return max([L.pri_score(k["pri"]) for k in e["kanji"]] + [L.pri_score(r["pri"]) for r in e["readings"]] + [0])


def make(e, s, en, pos, surface_hint, suru, signals, seed) -> Dict[str, Any]:
    lemma, reading, note = preferred_form(e, s, surface_hint, suru)
    return {
        "cand_id": f"jm-{e['seq']}-{s['idx']}-{re.sub('[^a-z0-9]+', '_', en)}",
        "en": {"lemma": en, "pos": pos, "ipa": None, "anchor": "jmdict", "wikt_line": None, "wikt_sense": None,
               "wikt_gloss": "; ".join(s["glosses"][:6]), "wikt_parents": [], "wikt_tags": [], "wikt_topics": [],
               "seed": seed},
        "ja": {"lemma": lemma, "reading": reading, "wikt_surface": lemma, "form_note": note, "ent_seq": e["seq"],
               "sense_idx": s["idx"], "gloss_score": 3 if gloss_norm(s["glosses"][0]) == en else 2, "gloss_overlap": 0,
               "jm_pos_tags": s["pos_tags"], "jm_glosses": s["glosses"][:8], "jm_misc": s["misc"], "jm_field": s["field"],
               "suru": suru, "pri_score": ent_pri(e), "synonyms": []},
        "ja_uncorroborated": [], "vi": None, "signals": signals,
    }


def main():
    jm = L.load_jmdict()
    en_lists = L.load_en_lists()
    # coverage is defined by the Wiktionary route only (wave 1); previous wave-2 output must not feed back
    pool = [c for c in read_jsonl(P14_DIR / "scored_pool.jsonl") if not c["cand_id"].startswith("jm-")]
    exprs = baseline_expressions()
    covered_ja = {e["lemma"] for e in exprs if e["language"] == "ja"}
    covered_ja |= {c["ja"]["lemma"] for c in pool}
    covered_ent = {(c["ja"]["ent_seq"]) for c in pool}
    covered_en = {(e["lemma"].lower()) for e in exprs if e["language"] == "en"} | {c["en"]["lemma"].lower() for c in pool}
    by_surface = defaultdict(list)
    for seq, e in jm.items():
        for k in e["kanji"]:
            by_surface[k["text"]].append(seq)
        for r in e["readings"]:
            by_surface[r["text"]].append(seq)
    out, stats = [], Counter()
    wk_rows, _ = L.load_wikt()
    KNOWN_EN.update(en_lists)
    KNOWN_EN.update(r["word"].lower() for r in wk_rows)
    KNOWN_EN.update(covered_en)

    # ---------------- A. JLPT-seeded
    seen_ent = set()
    for r in L.load_jlpt():
        lv = r["level"]
        surf, rd = r["kanji"], r["reading"]
        if surf in covered_ja:
            stats["A_covered"] += 1
            continue
        seqs = [q for q in by_surface.get(surf, []) if rd in [x["text"] for x in jm[q]["readings"]]]
        if not seqs:
            stats["A_no_jmdict_match"] += 1
            continue
        e = jm[sorted(seqs, key=lambda q: -ent_pri(jm[q]))[0]]
        if e["seq"] in covered_ent or e["seq"] in seen_ent:
            stats["A_entry_already_used"] += 1
            continue
        if lv == 1 and ent_pri(e) < 2:
            stats["A_n1_low_priority_skipped"] += 1
            continue
        cand = None
        for s in e["senses"]:
            if not usable_sense(e, s):
                continue
            pos = EN_POS[s["pos"]]
            suru = False
            en = headword_from_glosses(s["glosses"], pos)
            if not en:
                stats["A_no_known_headword"] += 1
                continue
            if pos == "noun" and ("vs" in s["pos_tags"] or "vs-i" in s["pos_tags"]):
                pass
            cand = make(e, s, en, pos, surf, suru, {}, "jlpt")
            break
        if not cand:
            stats["A_no_usable_sense"] += 1
            continue
        seen_ent.add(e["seq"])
        out.append(cand)
        stats["A_candidates"] += 1

    # ---------------- B. EN-list-seeded reverse lookup
    gloss_index = defaultdict(list)
    for seq, e in jm.items():
        for s in e["senses"]:
            if not usable_sense(e, s) or not s["glosses"]:
                continue
            g0 = gloss_norm(s["glosses"][0])
            gloss_index[g0].append((seq, s["idx"]))
    jlpt_by_form = {(x["kanji"], x["reading"]): x["level"] for x in L.load_jlpt()}
    for lemma in sorted(en_lists):
        if lemma in covered_en or not en_headword_ok(lemma) or lemma not in gloss_index:
            stats["B_skip"] += 1
            continue
        best = {}
        for seq, si in gloss_index[lemma]:
            e = jm[seq]
            s = e["senses"][si]
            if seq in covered_ent or seq in seen_ent:
                continue
            pos = EN_POS[s["pos"]]
            lv = min([jlpt_by_form.get((k["text"], r["text"]), 9) for k in e["kanji"] for r in e["readings"]]
                     + [jlpt_by_form.get((r["text"], r["text"]), 9) for r in e["readings"]])
            key = (ent_pri(e), lv < 9, -lv, -si, -seq)
            if pos not in best or key > best[pos][0]:
                best[pos] = (key, e, s)
        for pos, (key, e, s) in sorted(best.items()):
            if key[0] < 2 and not key[1]:
                stats["B_low_priority_skipped"] += 1
                continue
            surface = e["kanji"][0]["text"] if e["kanji"] else e["readings"][0]["text"]
            out.append(make(e, s, lemma, pos, surface, False, {}, "en_list"))
            seen_ent.add(e["seq"])
            stats["B_candidates"] += 1

    # ---------------- signals (same sources as the Wiktionary route)
    from scripts.phase1_4.build_candidates import Resolver  # noqa: F401  (kept for parity of signal logic)
    jl = {}
    for r in L.load_jlpt():
        jl.setdefault((r["kanji"], r["reading"]), r)
        jl.setdefault((r["kanji"], None), r)
    for c in out:
        sig = {}
        enl = en_lists.get(c["en"]["lemma"])
        if enl:
            sig["en"] = enl
        j = c["ja"]
        hit = jl.get((j["lemma"], j["reading"])) or jl.get((j["lemma"], None))
        if hit:
            sig["jlpt"] = {"level": hit["level"], "line": hit["line"]}
        if j["pri_score"]:
            sig["jmdict_pri"] = j["pri_score"]
        c["signals"] = sig
    out.sort(key=lambda c: c["cand_id"])
    write_jsonl(P14_DIR / "candidates_jm.jsonl", out)
    stats["total"] = len(out)
    write_json(P14_DIR / "candidates_jm_stats.json", dict(stats))
    print(dict(stats))


if __name__ == "__main__":
    main()
