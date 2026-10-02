#!/usr/bin/env python3
"""
scripts/phase1_4/build_candidates.py
Stage 1 of Phase 1.4: build SENSE-LEVEL tri-language candidates from upstream sources.

A candidate is anchored on one Wiktionary (English edition) sense block:
    (English headword, POS, sense) -> {ja translations, vi translations}
Sense-level anchoring is what prevents the Phase 1.3C failure mode (headword/gloss matching).

Every candidate is then independently:
  * corroborated on the JA side against JMdict (a JMdict sense of that JA word must gloss the
    English headword, and the POS must be compatible)
  * normalised/validated on the VI side (orthography; attested in the vn_freq corpus or not)
  * scored for LEARNING VALUE from curriculum signals (NGSL/NGSL-S/NAWL/BSL/TSL, JLPT, JMdict
    priority, vn_freq) - a candidate with no curriculum signal is never selected.

Output: data/phase1_4/candidates.jsonl (deterministic ordering) + stats report.
"""

import re
import sys
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from scripts.phase1_4.common import P14_DIR, nfc, sha8, write_jsonl, write_json, slug
from scripts.phase1_4 import lexicons as L

BAD_SENSE_TAGS = {"obsolete", "archaic", "dated", "rare", "nonstandard", "offensive", "vulgar", "derogatory",
                  "dialectal", "historical", "ethnic-slur", "pejorative", "euphemistic", "misspelling",
                  "alt-of", "form-of", "abbreviation", "initialism", "acronym", "plural-only", "slang",
                  "regional", "Britain", "Australia", "uncommon", "humorous", "poetic", "literary", "jargon"}
BAD_TR_TAGS = {"obsolete", "archaic", "dated", "rare", "dialectal", "derogatory", "offensive", "vulgar",
               "historical", "slang", "pejorative", "uncommon", "literary", "poetic", "humorous"}
BAD_GLOSS_RE = re.compile(r"^(plural|singular|alternative|obsolete|archaic|misspelling|abbreviation|initialism|"
                          r"acronym|present participle|past participle|simple past|third-person|comparative|"
                          r"superlative|alternative form|eye dialect|nonstandard|dated form|clipping)\b", re.I)

POS_MAP = {"noun": "noun", "verb": "verb", "adj": "adjective", "adv": "adverb", "prep": "preposition",
           "conj": "conjunction", "pron": "pronoun", "intj": "interjection", "num": "numeral",
           "det": "determiner", "phrase": "expression", "particle": "particle", "prep_phrase": "expression",
           "contraction": "expression", "article": "determiner"}

# JMdict POS compatibility per EN POS
JA_COMPAT = {
    "noun": {"noun", "pronoun", "numeral", "counter", "suffix", "prefix"},
    "verb": {"verb", "noun"},                       # noun here = vs (suru-verb) checked separately
    "adjective": {"adjective", "noun"},             # noun here = adj-no / n with adj usage
    "adverb": {"adverb", "adjective", "noun"},
    "preposition": {"particle", "expression", "conjunction", "adverb", "noun"},
    "conjunction": {"conjunction", "adverb", "expression", "particle"},
    "pronoun": {"pronoun", "noun"},
    "interjection": {"interjection", "expression", "noun"},
    "numeral": {"numeral", "noun", "counter"},
    "determiner": {"adjective", "pronoun", "noun", "expression", "adverb"},
    "expression": {"expression", "noun", "verb", "adjective", "adverb", "conjunction", "interjection"},
    "particle": {"particle", "expression", "adverb", "conjunction"},
}

VI_LETTERS = set("aàáảãạăằắẳẵặâầấẩẫậbcdđeèéẻẽẹêềếểễệfghiìíỉĩịjklmnoòóỏõọôồốổỗộơờớởỡợpqrstuùúủũụưừứửữựvwxyỳýỷỹỵz ")
STOP = set("a an the of to in on at for with by from or and as is are be been it its this that these those one "
           "who whom which what any some not no more most very used usually often especially certain particular "
           "something someone somebody etc such than into out up".split())


def norm_en_word(w: str) -> str:
    """Whitespace-normalised headword; CASE IS PRESERVED (e.g. 'Monday', 'overseas Chinese')."""
    return re.sub(r"\s+", " ", w.strip())


def en_headword_ok(w: str, curriculum=None) -> bool:
    """Lower-case common words always pass; capitalised headwords (days, months, nationalities) pass only if the
    lower-cased form is a curriculum word - this keeps proper names out without losing 'Monday'."""
    if not w or not re.fullmatch(r"[A-Za-z][A-Za-z'\- ]*[A-Za-z]|[A-Za-z]", w):
        return False
    if len(w.split()) > 3:
        return False
    if w != w.lower() and w != "I":
        return bool(curriculum) and w.lower() in curriculum
    return True


def toks(text: str) -> List[str]:
    return [t for t in re.findall(r"[a-z]+", text.lower()) if t not in STOP and len(t) > 2]


def gloss_norm(g: str) -> str:
    g = re.sub(r"\([^)]*\)", "", g.lower()).strip()
    g = re.sub(r"^(to|a|an|the)\s+", "", g)
    return re.sub(r"\s+", " ", g).strip()


def vi_ok(w: str) -> bool:
    w = nfc(w).lower()
    if not w or len(w.split()) > 4 or any(c not in VI_LETTERS for c in w):
        return False
    return True


def kana_only(s: str) -> bool:
    return bool(s) and all(("぀" <= c <= "ヿ") or c in "ー・" for c in s)


RARE_K = {"rK", "iK", "oK", "sK", "ik", "io"}
RARE_R = {"ok", "ik", "io", "rk", "sk"}


def preferred_form(entry: Dict[str, Any], sense: Dict[str, Any], surface: str, suru: bool) -> Tuple[str, str, str]:
    """Pick the learner-appropriate orthography (lemma, reading, form_note) for a JMdict entry/sense.
    Honours rare-kanji flags and 'usually written in kana' (uk) so that e.g. たとえ is not shown as 縦え."""
    rk = sense.get("restr_kanji") or []
    rr = sense.get("restr_reading") or []
    kan = [k for k in entry["kanji"] if (not rk or k["text"] in rk)]
    good_k = [k for k in kan if not (set(k["inf"]) & RARE_K)]
    reads_all = [r for r in entry["readings"] if (not rr or r["text"] in rr) and not (set(r["inf"]) & RARE_R)]
    if not reads_all:
        reads_all = [r for r in entry["readings"] if (not rr or r["text"] in rr)] or entry["readings"]
    note = "orthography:as_listed"
    lemma = None
    if "uk" in sense.get("misc", []) or not kan:
        lemma = None
        note = "orthography:kana_preferred(uk)" if kan else "orthography:kana_only_entry"
    elif surface in [k["text"] for k in good_k]:
        lemma = surface
    elif good_k:
        good_k.sort(key=lambda k: -L.pri_score(k["pri"]))
        lemma = good_k[0]["text"]
        note = "orthography:jmdict_preferred_kanji"
    if lemma is None:
        # kana form; prefer the highest-priority non-rare reading
        reads_all.sort(key=lambda r: -L.pri_score(r["pri"]))
        lemma = reads_all[0]["text"]
        reading = lemma
    else:
        cands = [r for r in reads_all if not r.get("restr") or lemma in r["restr"]]
        cands.sort(key=lambda r: -L.pri_score(r["pri"]))
        reading = (cands or reads_all)[0]["text"]
    if suru:
        lemma, reading = lemma + "する", reading + "する"
    return lemma, reading, note


class Resolver:
    def __init__(self):
        self.jm = L.load_jmdict()
        self.by_surface: Dict[str, List[int]] = defaultdict(list)
        for seq, e in self.jm.items():
            for k in e["kanji"]:
                self.by_surface[k["text"]].append(seq)
            for r in e["readings"]:
                self.by_surface[r["text"]].append(seq)
        self.jlpt = {}
        for r in L.load_jlpt():
            self.jlpt.setdefault((r["kanji"], r["reading"]), r)
            self.jlpt.setdefault((r["kanji"], None), r)
        self.en = L.load_en_lists()
        self.vn = L.load_vn_freq()

    # ---- JA side -----------------------------------------------------------------
    def corroborate_ja(self, surface: str, kana_alt: Optional[str], en_word: str, en_pos: str,
                       wikt_gloss: str) -> Optional[Dict[str, Any]]:
        """Find the best JMdict (entry, sense) for this JA surface that glosses the EN headword."""
        base = surface
        suru = False
        if en_pos == "verb" and surface.endswith("する") and len(surface) > 2:
            base, suru = surface[:-2], True
        seqs = self.by_surface.get(base, [])
        target = gloss_norm(en_word)
        wtok = set(toks(wikt_gloss))
        best = None
        for seq in sorted(set(seqs)):
            e = self.jm[seq]
            if kana_alt and not kana_only(base):
                # honour the Wikt-provided reading when it exists in this entry
                if kana_alt not in [r["text"] for r in e["readings"]] and not suru:
                    continue
            for s in e["senses"]:
                gl = [gloss_norm(g) for g in s["glosses"]]
                if target in gl:
                    score = 3 if gl[0] == target else 2
                elif any(g.startswith(target + " ") or g.endswith(" " + target) for g in gl):
                    score = 1
                else:
                    continue
                pos_ok = self._pos_ok(en_pos, s, suru)
                if not pos_ok:
                    continue
                gtok = set(t for g in s["glosses"] for t in toks(g))
                overlap = len(wtok & gtok)
                key = (score, overlap, -seq, -s["idx"])
                if best is None or key > best[0]:
                    best = (key, e, s)
        if not best:
            return None
        key, e, s = best
        return {"ent_seq": e["seq"], "sense_idx": s["idx"], "gloss_score": key[0], "gloss_overlap": key[1],
                "jm_pos": s["pos"], "jm_pos_tags": s["pos_tags"], "jm_glosses": s["glosses"][:8],
                "jm_misc": s["misc"], "jm_field": s["field"], "suru": suru, "entry": e}

    @staticmethod
    def _pos_ok(en_pos: str, s: Dict[str, Any], suru: bool) -> bool:
        tags = set(s["pos_tags"])
        if en_pos == "verb":
            if suru:
                return "vs" in tags or "vs-i" in tags or "vs-s" in tags
            return s["pos"] == "verb"
        if en_pos == "noun":
            return s["pos"] in JA_COMPAT["noun"] and not (tags & {"exp"})
        if en_pos == "adjective":
            return s["pos"] == "adjective" or bool(tags & {"adj-no", "adj-na", "adj-i", "adj-pn"})
        allowed = JA_COMPAT.get(en_pos)
        return True if allowed is None else s["pos"] in allowed

    def ja_surface_info(self, c: Dict[str, Any], kana_alt: Optional[str]) -> Tuple[str, str]:
        """(lemma, reading) from the corroborating JMdict entry."""
        e = c["entry"]
        suru = c["suru"]
        s = e["senses"][c["sense_idx"]]
        restr_k = s.get("restr_kanji") or []
        restr_r = s.get("restr_reading") or []
        kanji = [k["text"] for k in e["kanji"] if not restr_k or k["text"] in restr_k]
        reads = [r for r in e["readings"] if not restr_r or r["text"] in restr_r]
        reading = None
        if kana_alt and kana_alt in [r["text"] for r in reads]:
            reading = kana_alt
        elif reads:
            reading = reads[0]["text"]
        lemma = None
        return reading or "", ""

    def jlpt_level(self, lemma: str, reading: str) -> Optional[Dict[str, Any]]:
        return self.jlpt.get((lemma, reading)) or self.jlpt.get((lemma, None))


def block_iter(rows: List[Dict[str, Any]]):
    """Yield sense blocks: sense-linked translations, plus entry-level ones grouped by label."""
    for r in rows:
        for si, s in enumerate(r["senses"]):
            if s["translations"]:
                yield r, f"s{si}", s, s["translations"], s["gloss"]
        if r["entry_translations"]:
            groups: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
            for t in r["entry_translations"]:
                groups[t.get("sense", "")].append(t)
            for label in sorted(groups):
                if label:
                    yield r, f"e:{sha8(label, 6)}", {"gloss": label, "parents": [], "tags": [], "topics": []}, groups[label], label


def main():
    rows, wmeta = L.load_wikt()
    R = Resolver()
    out: List[Dict[str, Any]] = []
    stats = Counter()
    for r, bid, sense, trs, gloss in block_iter(rows):
        stats["blocks_seen"] += 1
        w = norm_en_word(r["word"])
        wl = w.lower()
        pos = POS_MAP.get(r["pos"])
        if not pos or not en_headword_ok(w, R.en):
            stats["drop_headword_or_pos"] += 1
            continue
        if set(sense.get("tags", [])) & BAD_SENSE_TAGS or BAD_GLOSS_RE.match(gloss or ""):
            stats["drop_sense_tag_or_form"] += 1
            continue
        if not any(t["lang_code"] == "ja" for t in trs) and not any(t["lang_code"] == "vi" for t in trs):
            continue
        # ---- JA
        ja_cands = []
        for t in trs:
            if t["lang_code"] != "ja" or set(t.get("tags", [])) & BAD_TR_TAGS:
                continue
            surf = nfc(t["word"])
            if not surf or " " in surf:
                continue
            c = R.corroborate_ja(surf, t.get("alt"), w, pos, gloss)
            ja_cands.append({"surface": surf, "alt": t.get("alt"), "roman": t.get("roman"), "corr": c})
        corr = [j for j in ja_cands if j["corr"]]
        # ---- VI
        vi_cands = []
        seen_vi = set()
        for t in trs:
            if t["lang_code"] != "vi" or set(t.get("tags", [])) & BAD_TR_TAGS:
                continue
            v = nfc(t["word"]).lower()
            if v in seen_vi or not vi_ok(v):
                continue
            seen_vi.add(v)
            fr = R.vn.get(v)
            vi_cands.append({"word": v, "vn_rank": fr["rank"] if fr else None,
                             "vn_pos": fr["pos"] if fr else [], "vn_line": fr["line"] if fr else None})
        stats["blocks_with_ja"] += bool(ja_cands)
        stats["blocks_with_ja_corroborated"] += bool(corr)
        stats["blocks_with_vi"] += bool(vi_cands)
        if not ja_cands and not vi_cands:
            continue
        # ---- primary selection
        def ja_key(j):
            c = j["corr"]
            lem_jl = None
            if c:
                e = c["entry"]
                pri = max([L.pri_score(k["pri"]) for k in e["kanji"] if k["text"] == j["surface"].removesuffix("する")]
                          + [L.pri_score(k["pri"]) for k in e["readings"]] + [0])
            else:
                pri = 0
            return (bool(c), c["gloss_score"] if c else 0, pri, c["gloss_overlap"] if c else 0)
        ja_cands.sort(key=ja_key, reverse=True)
        vi_cands.sort(key=lambda v: (v["vn_rank"] is not None, -(v["vn_rank"] or 10 ** 9)), reverse=True)

        ja_prim = None
        ja_ev = None
        if corr:
            pj = ja_cands[0]
            c = pj["corr"]
            e = c["entry"]
            sidx = c["sense_idx"]
            sdef = e["senses"][sidx]
            lemma_pref, reading, form_note = preferred_form(e, sdef, pj["surface"].removesuffix("する") if c["suru"] else pj["surface"], c["suru"])
            ja_prim = {"lemma": lemma_pref, "reading": reading, "wikt_surface": pj["surface"], "form_note": form_note, "ent_seq": e["seq"], "sense_idx": sidx,
                       "gloss_score": c["gloss_score"], "gloss_overlap": c["gloss_overlap"],
                       "jm_pos_tags": c["jm_pos_tags"], "jm_glosses": c["jm_glosses"],
                       "jm_misc": c["jm_misc"], "jm_field": c["jm_field"], "suru": c["suru"],
                       "pri_score": max([L.pri_score(k["pri"]) for k in e["kanji"]] + [L.pri_score(k["pri"]) for k in e["readings"]] + [0])}
            ja_syn = []
            for j in ja_cands[1:]:
                if j["corr"] and j["corr"]["gloss_score"] >= 2 and len(ja_syn) < 2:
                    ce = j["corr"]["entry"]
                    cs = ce["senses"][j["corr"]["sense_idx"]]
                    sl, sr, sn = preferred_form(ce, cs, j["surface"].removesuffix("する") if j["corr"]["suru"] else j["surface"], j["corr"]["suru"])
                    ja_syn.append({"lemma": sl, "reading": sr, "wikt_surface": j["surface"], "form_note": sn,
                                   "ent_seq": ce["seq"], "sense_idx": j["corr"]["sense_idx"]})
            ja_prim["synonyms"] = ja_syn
        stats["ja_prim"] += bool(ja_prim)
        vi_prim = vi_cands[0] if vi_cands else None
        vi_syn = [v for v in vi_cands[1:] if v["vn_rank"] is not None][:2]

        # ---- curriculum signals
        sig: Dict[str, Any] = {}
        enl = R.en.get(wl)
        if enl:
            sig["en"] = enl
        if ja_prim:
            jl = R.jlpt_level(ja_prim["lemma"].removesuffix("する") if ja_prim["suru"] else ja_prim["lemma"], ja_prim["reading"]) \
                or R.jlpt_level(ja_prim["lemma"], ja_prim["reading"])
            if jl:
                sig["jlpt"] = {"level": jl["level"], "line": jl["line"]}
            if ja_prim["pri_score"]:
                sig["jmdict_pri"] = ja_prim["pri_score"]
        if vi_prim and vi_prim["vn_rank"]:
            sig["vi_rank"] = vi_prim["vn_rank"]

        domains = sorted({d for d in sense.get("topics", [])})
        out.append({
            "cand_id": f"wk-{r['_line']}-{bid}",
            "en": {"lemma": w, "pos": pos, "ipa": r.get("ipa"), "wikt_line": r["_line"], "wikt_sense": bid,
                   "wikt_gloss": gloss, "wikt_parents": sense.get("parents", []),
                   "wikt_tags": sense.get("tags", []), "wikt_topics": domains},
            "ja": ja_prim,
            "ja_uncorroborated": [{"surface": j["surface"], "alt": j["alt"]} for j in ja_cands if not j["corr"]][:3],
            "vi": ({"lemma": vi_prim["word"], "vn_rank": vi_prim["vn_rank"], "vn_pos": vi_prim["vn_pos"],
                    "vn_line": vi_prim["vn_line"],
                    "synonyms": [{"lemma": s["word"], "vn_rank": s["vn_rank"], "vn_line": s["vn_line"]} for s in vi_syn]}
                   if vi_prim else None),
            "signals": sig,
        })
    out.sort(key=lambda c: (c["en"]["lemma"], c["en"]["pos"], c["en"]["wikt_line"], c["en"]["wikt_sense"]))
    n = write_jsonl(P14_DIR / "candidates.jsonl", out)
    tri = sum(1 for c in out if c["ja"] and c["vi"])
    sigd = sum(1 for c in out if c["signals"])
    tri_sig = sum(1 for c in out if c["ja"] and c["vi"] and c["signals"])
    en_ja_sig = sum(1 for c in out if c["ja"] and not c["vi"] and c["signals"])
    stats.update({"candidates": n, "tri_candidates": tri, "with_signal": sigd, "tri_with_signal": tri_sig,
                  "en_ja_only_with_signal": en_ja_sig})
    write_json(P14_DIR / "candidates_stats.json", dict(stats))
    print(dict(stats))


if __name__ == "__main__":
    main()
