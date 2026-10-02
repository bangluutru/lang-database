"""
scripts/phase1_4/baseline_fixes.py
Loads the hand-authored remediation table (data/phase1_4/baseline_fixes/part*.tsv), resolves every proposed Japanese
form against JMdict (the gloss must equal/contain the English lemma, POS must be compatible) and returns structured
fix plans. No network, no external API: the table was authored by the coding agent after manual review.
"""
import glob
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from scripts.phase1_4.common import BASE_DIR, CANONICAL_DIR, read_jsonl
from scripts.phase1_4.build_candidates import Resolver, preferred_form


def load_table():
    rows = {}
    for p in sorted(glob.glob(str(BASE_DIR / "data/phase1_4/baseline_fixes/part*.tsv"))):
        for line in open(p, encoding="utf-8"):
            if not line.strip() or line.startswith("#"):
                continue
            f = line.rstrip("\n").split("\t")
            cid = "concept-" + f[0]
            ja, vi, pos = (f + ["-", "-", "-"])[1:4]
            rows[cid] = {"ja": None if ja == "-" else ja, "vi": None if vi == "-" else vi, "pos": None if pos == "-" else pos}
    return rows


def baseline_view():
    man = json.loads((BASE_DIR / "data/releases/phase1_3d-sealed/baseline_manifest.json").read_text())
    ex = read_jsonl(CANONICAL_DIR / "expressions.jsonl")[: man["append_only"]["expressions.jsonl"]["lines"]]
    by = defaultdict(lambda: defaultdict(list))
    for e in ex:
        by[e["concept_id"]][e["language"]].append(e)
    return by


def _first_sense(R, surf, pos):
    """Override path ('!'): first POS-compatible JMdict sense of the (highest priority) entry for this surface."""
    best = None
    for seq in sorted(set(R.by_surface.get(surf, []))):
        e = R.jm[seq]
        for s in e["senses"]:
            if R._pos_ok(pos, s, False):
                from scripts.phase1_4 import lexicons as L
                pri = max([L.pri_score(k["pri"]) for k in e["kanji"]] + [L.pri_score(r["pri"]) for r in e["readings"]] + [0])
                if best is None or pri > best[0]:
                    best = (pri, e, s)
                break
    if not best:
        return None
    _, e, s = best
    return {"entry": e, "sense_idx": s["idx"], "gloss_score": 0, "suru": False}


class FixResolver(Resolver):
    """Baseline-remediation resolver: additionally treats vs-s / vs-i (suru-verbs such as 欲する, 愛する) as verbs.
    Kept out of the shared Resolver so wave-1 candidate generation (already judged) is not perturbed."""

    def corroborate_ja(self, surface, kana_alt, en_word, en_pos, wikt_gloss):
        """Same contract as Resolver.corroborate_ja but ties are broken by JMdict commonness (not ent_seq), so that
        e.g. 兄弟 resolves to きょうだい and 人 to ひと."""
        from scripts.phase1_4 import lexicons as L
        from scripts.phase1_4.build_candidates import gloss_norm
        base, suru = surface, False
        if en_pos == "verb" and surface.endswith("する") and len(surface) > 2:
            base, suru = surface[:-2], True
        target = gloss_norm(en_word)
        best = None
        for seq in sorted(set(self.by_surface.get(base, []))):
            e = self.jm[seq]
            pri = max([L.pri_score(k["pri"]) for k in e["kanji"]] + [L.pri_score(r["pri"]) for r in e["readings"]] + [0])
            for sn in e["senses"]:
                gl = [gloss_norm(g) for g in sn["glosses"]]
                if target in gl:
                    score = 3 if gl[0] == target else 2
                elif any(g.startswith(target + " ") or g.endswith(" " + target) for g in gl):
                    score = 1
                else:
                    continue
                if not self._pos_ok(en_pos, sn, suru):
                    continue
                key = (score, pri, -sn["idx"], -seq)
                if best is None or key > best[0]:
                    best = (key, e, sn)
        if not best:
            return None
        key, e, sn = best
        return {"ent_seq": e["seq"], "sense_idx": sn["idx"], "gloss_score": key[0], "gloss_overlap": 0, "jm_pos": sn["pos"],
                "jm_pos_tags": sn["pos_tags"], "jm_glosses": sn["glosses"][:8], "jm_misc": sn["misc"], "jm_field": sn["field"],
                "suru": suru, "entry": e}

    @staticmethod
    def _pos_ok(en_pos, s, suru):
        if en_pos == "verb" and set(s["pos_tags"]) & {"vs-s", "vs-i"}:
            return True
        return Resolver._pos_ok(en_pos, s, suru)


def plan(R=None):
    R = R or FixResolver()
    by = baseline_view()
    table = load_table()
    plans, failures = [], []
    for cid, fx in sorted(table.items()):
        if cid not in by:
            failures.append((cid, "unknown concept"))
            continue
        e = by[cid]
        en = e["en"][0]
        pos = fx["pos"] or en["part_of_speech"]
        p = {"concept_id": cid, "en": en["lemma"], "old_pos": en["part_of_speech"], "new_pos": pos if pos != en["part_of_speech"] else None,
             "old_ja": e["ja"][0]["lemma"], "old_vi": e["vi"][0]["lemma"] if e["vi"] else None, "new_vi": fx["vi"], "ja": None}
        if fx["ja"] == "?":
            p["flag_only"] = True
            plans.append(p)
            continue
        if fx["ja"]:
            surf, override = fx["ja"], fx["ja"].startswith("!")
            surf = surf.lstrip("!")
            c = None
            en_l = en["lemma"].lower()
            tries = [(en_l, pos)]
            if pos == "adverb":
                tries += [(en_l, "conjunction"), (en_l, "expression"), (en_l, "pronoun")]
            tries += [(en_l + "s", pos), (en_l + "es", pos)]          # JMdict glosses plural nouns (brothers, sisters)
            for t_en, t_pos in ([] if override else tries):
                c = R.corroborate_ja(surf, None, t_en, t_pos, "")
                if c:
                    break
            if not c and override:
                c = next((x for x in (_first_sense(R, surf, q) for q in ([pos, "conjunction", "expression"] if pos == "adverb" else [pos])) if x), None)
                if c:
                    c["override"] = True
            if not c:
                failures.append((cid, f"{en['lemma']} <- {fx['ja']}: no JMdict sense glossing it with compatible POS"))
                continue
            ent, s = c["entry"], c["entry"]["senses"][c["sense_idx"]]
            lemma, reading, note = preferred_form(ent, s, surf.removesuffix("する") if c["suru"] else surf, c["suru"])
            p["ja"] = {"lemma": lemma, "reading": reading, "ent_seq": ent["seq"], "sense_idx": c["sense_idx"],
                       "gloss_score": c["gloss_score"], "gloss_override": bool(c.get("override")), "jm_pos_tags": s["pos_tags"], "jm_glosses": s["glosses"][:6], "form_note": note}
        plans.append(p)
    return plans, failures


if __name__ == "__main__":
    plans, failures = plan()
    print(len(plans), "plans;", len(failures), "failures")
    for f in failures:
        print("FAIL", f)
