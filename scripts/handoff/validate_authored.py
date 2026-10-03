#!/usr/bin/env python3
"""
Mechanical gate for Gemini 'A1' authoring decisions.   python scripts/handoff/validate_authored.py data/phase1_4/handoff/decisions/A1_001.jsonl
Checks only objective facts (schema, JMdict, Wiktionary, vn_freq, canonical duplicates, examples, confidence ceiling). Linguistic quality is judged by Claude.
Exit 1 if any BLOCK problem. WARN lines never fail but must be addressed in the entry's `why_distinct`/`note`.
Also imported by gemini_selfcheck.py (A1 mode) via `analyse()`.
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from scripts.handoff.authoring_common import (REPO, POS_MAP, BLOCK_MISC, DOMAIN_FIELDS, jm, vn, wikt_vi, wikt_glosses, canonical,  # noqa
                                              entry_forms, entry_pri, gloss_norm)

VI_RE = re.compile(r"^[a-zàáảãạăằắẳẵặâầấẩẫậđèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵ ]+$")
KANA = re.compile(r"^[ぁ-ゟ゠-ヿー・]+$")
JA_SCRIPT = re.compile(r"[぀-ヿ一-鿿々ー]")
POSES = set(POS_MAP)
CONF = {"HIGH": 3, "MEDIUM": 2, "LOW": 1}
DOMAINS = set(DOMAIN_FIELDS)


def ceiling(ev):
    """Highest confidence the OBJECTIVE evidence allows. HIGH needs: JA commonly used (JMdict pri>0 or domain field tag) AND VI attested (vn_freq or Wiktionary vi translation)."""
    ja_ok = ev["ja_pri"] > 0 or ev["ja_field_match"]
    vi_ok = ev["vi_vn_freq_rank"] is not None or ev["vi_in_wikt"]
    if ja_ok and vi_ok and ev["pair_gloss_exact"]:
        return "HIGH"
    if ev["pair_gloss_exact"]:
        return "MEDIUM"
    return "LOW"


def stem_ok(lemma, text, lang):
    t, l = text.lower(), lemma.lower()
    if l in t:
        return True
    if lang == "en":
        return len(l) > 4 and l[: max(4, len(l) - 2)] in t
    if lang == "ja":
        return len(l) > 1 and l[:-1] in text
    return False


def analyse(rows, slots):
    """returns (list of per-row dict {id, block:[...], warn:[...], evidence:{...}, ceiling}), file-level block list"""
    lex, pairs = canonical()
    file_block, out, seen_pairs = [], [], {}
    if [r.get("id") for r in rows] != [s["id"] for s in slots]:
        file_block.append("ids/order differ from the slots packet (one line per slot, same order, none missing)")
    for r in rows:
        blk, wrn, ev = [], [], {}
        slot = next((s for s in slots if s["id"] == r.get("id")), None)
        if slot is None:
            out.append({"id": r.get("id"), "block": ["unknown slot id"], "warn": [], "evidence": {}, "ceiling": None}); continue
        if r.get("task") != "A1" or r.get("reviewer") != "gemini-3.8":
            blk.append("task must be 'A1' and reviewer exactly 'gemini-3.8'")
        if r.get("skip") is True:
            if len(str(r.get("reason", ""))) < 40:
                blk.append("skip needs a specific `reason` (>= 40 chars): what you searched and why nothing qualified")
            out.append({"id": r["id"], "block": blk, "warn": wrn, "evidence": {}, "ceiling": None, "skip": True}); continue
        try:
            en, ja, vi, evd, fal = r["en"], r["ja"], r["vi"], r["evidence"], r["falsification"]
        except KeyError as k:
            out.append({"id": r["id"], "block": [f"missing key {k}"], "warn": [], "evidence": {}, "ceiling": None}); continue
        if r.get("domain") != slot["domain"] or r.get("subdomain") != slot["subdomain"]:
            blk.append("domain/subdomain must equal the slot's")
        if slot.get("fixed_en") and en.get("lemma") != slot["fixed_en"]:
            blk.append(f"this rework slot fixes en.lemma to '{slot['fixed_en']}'")
        if slot.get("fixed_ja") and ja.get("lemma") != slot["fixed_ja"]:
            blk.append(f"this rework slot fixes ja.lemma to '{slot['fixed_ja']}'")
        if en.get("pos") not in POSES or en.get("pos") not in slot["allowed_pos"]:
            blk.append(f"en.pos must be one of {slot['allowed_pos']}")
        el = str(en.get("lemma", "")).strip()
        if not re.fullmatch(r"[a-z][a-z \-']{1,40}", el) or el != el.lower() and not el.isupper():
            blk.append("en.lemma: lower-case English (acronyms allowed upper-case), 1-4 words")
        d = str(en.get("sense_definition", ""))
        if not 25 <= len(d) <= 220:
            blk.append("en.sense_definition must be 25-220 chars, in your own words")
        wg = wikt_glosses().get(el.lower(), [])
        if d.lower().strip(" .") in [g.strip(" .") for g in wg]:
            blk.append("sense_definition is a verbatim Wiktionary gloss (must be independently authored)")
        # --- Japanese vs JMdict
        e = jm().get(evd.get("jmdict_ent_seq")) if isinstance(evd.get("jmdict_ent_seq"), int) else None
        if e is None:
            blk.append("evidence.jmdict_ent_seq must be an integer ent_seq that exists in JMdict")
            ev.update(ja_pri=0, ja_field_match=False, pair_gloss_exact=False)
        else:
            if ja.get("lemma") not in entry_forms(e):
                blk.append(f"ja.lemma '{ja.get('lemma')}' is not a form of ent_seq {e['seq']} (forms: {entry_forms(e)[:6]})")
            if ja.get("reading") not in [x["text"] for x in e["readings"]]:
                blk.append(f"ja.reading '{ja.get('reading')}' is not a reading of ent_seq {e['seq']}")
            idx = evd.get("jmdict_sense_idx")
            sn = next((s for s in e["senses"] if s["idx"] == idx), None)
            if sn is None:
                blk.append("evidence.jmdict_sense_idx not found in that entry"); sn = {"glosses": [], "pos_tags": [], "misc": [], "field": []}
            ge = any(gloss_norm(el) == gloss_norm(g) for g in sn["glosses"])
            if not ge:
                blk.append(f"no gloss of ent_seq {e['seq']} sense {idx} equals '{el}' (glosses: {sn['glosses'][:5]})")
            if not any(POS_MAP[en["pos"]](t) for t in sn["pos_tags"]) if en.get("pos") in POS_MAP else True:
                blk.append(f"en.pos '{en.get('pos')}' incompatible with JMdict pos tags {sn['pos_tags']}")
            if set(sn["misc"]) & BLOCK_MISC:
                blk.append(f"JMdict marks this sense {sorted(set(sn['misc']) & BLOCK_MISC)} (archaic/rare/colloquial/slang): not for a learner core")
            ev.update(ja_pri=entry_pri(e), ja_field_match=bool(set(sn["field"]) & set(DOMAIN_FIELDS[slot["domain"]])), pair_gloss_exact=ge, jm_fields=sn["field"])
            if ev["ja_pri"] == 0 and not ev["ja_field_match"]:
                wrn.append("JA entry has no JMdict priority tag and no domain field tag: unusual/rare? justify in note")
        # --- Vietnamese
        vl = str(vi.get("lemma", "")).strip()
        if not vl or not VI_RE.match(vl) or len(vl.split()) > 4:
            blk.append("vi.lemma: lower-case Vietnamese, correct diacritics, 1-4 words, no punctuation")
        if vl == el and not vi.get("loanword"):
            blk.append("vi.lemma equals the English word: set vi.loanword=true and justify, or find the Vietnamese term")
        fr = vn().get(vl)
        ev["vi_vn_freq_rank"] = fr["rank"] if fr else None
        ev["vi_in_wikt"] = vl in wikt_vi().get(el.lower(), set())
        if vi.get("claimed_vn_freq_rank") not in (None, ev["vi_vn_freq_rank"]):
            blk.append(f"vi.claimed_vn_freq_rank {vi.get('claimed_vn_freq_rank')} != actual {ev['vi_vn_freq_rank']} (fabricated or wrong)")
        if vi.get("claimed_in_wikt") not in (None, ev["vi_in_wikt"]):
            blk.append(f"vi.claimed_in_wikt {vi.get('claimed_in_wikt')} != actual {ev['vi_in_wikt']}")
        # --- duplicates
        jl = str(ja.get("lemma", ""))
        if (el.lower(), jl.lower()) in pairs:
            blk.append(f"duplicate: this EN-JA pair already exists as {pairs[(el.lower(), jl.lower())]}")
        else:
            if ("en", el.lower()) in lex:
                wrn.append("EN lemma already exists in the corpus (other sense): explain in why_distinct")
            if ("ja", jl.lower()) in lex:
                wrn.append("JA lemma already exists in the corpus (other concept): explain in why_distinct")
        key = (el.lower(), jl.lower())
        if key in seen_pairs:
            blk.append(f"duplicate of {seen_pairs[key]} in this file")
        seen_pairs[key] = r["id"]
        # --- falsification fields
        for k in ("example_en", "example_ja", "example_vi", "back_translation", "closest_existing_concept", "why_distinct"):
            if not str(fal.get(k, "")).strip() or len(str(fal.get(k))) < 3:
                blk.append(f"falsification.{k} missing")
        if fal.get("example_en") and not stem_ok(el, fal["example_en"], "en"):
            blk.append("example_en does not contain the English lemma")
        if fal.get("example_ja") and not stem_ok(jl, fal["example_ja"], "ja") and not stem_ok(ja.get("reading", ""), fal["example_ja"], "ja"):
            blk.append("example_ja does not contain the Japanese lemma/reading")
        if fal.get("example_vi") and vl.lower() not in str(fal["example_vi"]).lower():
            blk.append("example_vi does not contain the Vietnamese lemma")
        if fal.get("example_ja") and not JA_SCRIPT.search(fal["example_ja"]):
            blk.append("example_ja must be Japanese")
        cm = str(fal.get("closest_existing_concept", ""))
        if cm.startswith("concept-") and f'"{cm}"' not in open(REPO / "data/canonical/concepts.jsonl", encoding="utf-8").read():
            blk.append(f"closest_existing_concept {cm} does not exist")
        # --- confidence ceiling
        ce = ceiling(ev)
        ev["ceiling"] = ce
        c = r.get("confidence")
        if c not in CONF:
            blk.append("confidence must be HIGH|MEDIUM|LOW")
        elif CONF[c] > CONF[ce]:
            blk.append(f"confidence {c} exceeds the ceiling {ce} allowed by objective evidence ({ {k: v for k, v in ev.items() if k != 'ceiling'} })")
        if len(str(r.get("note", ""))) < 60:
            blk.append("note must be >= 60 chars (sense, evidence, rejected alternative, doubt)")
        out.append({"id": r["id"], "block": blk, "warn": wrn, "evidence": ev, "ceiling": ce})
    if len({str(r.get("note", "")).strip() for r in rows if not r.get("skip")}) < len([r for r in rows if not r.get("skip")]):
        file_block.append("identical `note` text used for several entries")
    return out, file_block


def main(path):
    slots_path = REPO / "data/phase1_4/handoff/packets" / Path(path).name
    slots = [json.loads(l) for l in slots_path.read_text(encoding="utf-8").splitlines() if l.strip()]
    rows = [json.loads(l) for l in Path(path).read_text(encoding="utf-8").splitlines() if l.strip()]
    res, fb = analyse(rows, slots)
    nb = len(fb) + sum(len(x["block"]) for x in res)
    print(f"{len(rows)} authored rows checked, {nb} blocking problems")
    for b in fb:
        print("  FILE:", b)
    for x in res:
        for b in x["block"]:
            print(f"  {x['id']}: BLOCK {b}")
        for w in x["warn"]:
            print(f"  {x['id']}: warn {w}")
    return 1 if nb else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
