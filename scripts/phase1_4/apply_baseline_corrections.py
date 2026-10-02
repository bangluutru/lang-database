#!/usr/bin/env python3
"""
scripts/phase1_4/apply_baseline_corrections.py   (Phase 1.4.1 - remediation of demonstrable Phase 1.3D defects)

WHAT: applies the agent-authored, JMdict-verified correction table (data/phase1_4/baseline_fixes/part*.tsv) to the
sealed canonical prefix, IN PLACE, with a field-level LEDGER (old -> new) so the sealed bytes remain exactly
reconstructible: reverting the ledger reproduces the sealed SHA-256 (tests/test_phase1_4_1.py).

RULES
  * IDs never change. No record is deleted. Line counts of the sealed prefix do not change.
  * Corrected Japanese = JMdict-verified (gloss equals the English lemma, POS compatible; 8 '!' overrides are labelled).
  * Corrected/new Vietnamese forms were written by the coding agent => provenance AI_GENERATED (model = this agent),
    validation 'AGENT_REVIEWED_NOT_INDEPENDENT' (a separate dimension, never SOURCE_DERIVED / judge-validated).
  * Every corrected concept becomes validation_status = needs_review (not independently validated), except POS-only fixes.
  * Classification rows that depended on a replaced form are RETRACTED (status 'retracted'), never deleted; new rows
    are appended by build_canonical from data/phase1_4/baseline_corrections_append.json.
  * Idempotent: if the prefix is already corrected (hash matches manifest.corrected_prefix) it does nothing.
"""
import hashlib
import json
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from scripts.phase1_4.common import BASE_DIR, CANONICAL_DIR, P14_DIR, PHASE_TS, REPORTS_DIR, write_json
from scripts.phase1_4 import lexicons as L
from scripts.phase1_4.baseline_fixes import plan
from scripts.phase1_4.build_canonical import Ev, cls, jlpt_class, joyo_class, vi_core_class

MANIFEST = BASE_DIR / "data/releases/phase1_3d-sealed/baseline_manifest.json"
FILES = ["concepts", "senses", "expressions", "classifications"]
KEYS = {"concepts": "concept_id", "senses": "sense_id", "expressions": "expression_id", "classifications": "classification_id"}
ABSENT = {"__absent__": True}
AGENT = "claude-sonnet-5-5"
GEN_VERSION = "phase1_4_1_manual_v1"
LEDGER_PATH = REPORTS_DIR / "baseline_corrections_ledger.json"


def sha(b):
    return hashlib.sha256(b).hexdigest()


class Editor:
    def __init__(self):
        self.rows = {}
        self.ledger = []
        self.index = {}
        man = json.loads(MANIFEST.read_text())
        self.man = man
        for f in FILES:
            info = man["append_only"][f"{f}.jsonl"]
            raw = (CANONICAL_DIR / f"{f}.jsonl").read_bytes()[: info["bytes"]]
            lines = raw.decode("utf-8").split("\n")[:-1]
            recs = [json.loads(l) for l in lines]
            for l, r in zip(lines, recs):          # serialisation must round-trip exactly, else we could not guarantee reversal
                assert json.dumps(r, ensure_ascii=False) == l, f"non round-trippable line in {f}"
            self.rows[f] = recs
            self.index[f] = {r[KEYS[f]]: r for r in recs}

    def set(self, f, rid, field, new, reason, cid):
        r = self.index[f][rid]
        old = r.get(field, ABSENT) if field in r else ABSENT
        if old == new:
            return
        self.ledger.append({"file": f, "id": rid, "concept_id": cid, "field": field, "old": old, "new": new, "reason": reason})
        r[field] = new

    def serialize(self, f):
        return "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in self.rows[f]).encode("utf-8")


def main():
    man = json.loads(MANIFEST.read_text())
    if "corrected_prefix" in man:
        print("already corrected; nothing to do")
        return
    plans, failures = plan()
    assert not failures, failures
    ed = Editor()
    ev = Ev()
    vn = L.load_vn_freq()
    jl = {}
    for r in L.load_jlpt():
        jl.setdefault((r["kanji"], r["reading"]), r)
        jl.setdefault((r["kanji"], None), r)
    joyo = {r["kanji"]: r["grade"] for r in json.load(open(BASE_DIR / "data/raw/joyo/2010-official/joyo_kanji_official.json"))}
    cls_by_target = defaultdict(list)
    for k in ed.rows["classifications"]:
        cls_by_target[k["target_id"]].append(k)
    exprs_by = defaultdict(lambda: defaultdict(list))
    for e in ed.rows["expressions"]:
        exprs_by[e["concept_id"]][e["language"]].append(e)
    append = {"expressions": [], "classifications": []}
    stats = defaultdict(int)

    for p in plans:
        cid = p["concept_id"]
        suffix = cid[len("concept-"):]
        en_e = exprs_by[cid]["en"][0]
        ja_e = exprs_by[cid]["ja"][0]
        vi_all = exprs_by[cid]["vi"]
        sense = next(s for s in ed.rows["senses"] if s["concept_id"] == cid)
        kinds = []
        if p.get("flag_only"):
            kinds.append("flagged_unfixable")
            reason = "Defect detected (EN-JA pair not supported by JMdict/sense); no verifiable replacement available - flagged for human review."
            ed.set("concepts", cid, "metadata", {"correction": {"phase": "1.4.1", "kinds": kinds, "validation_status": "needs_review",
                   "reason": reason, "ledger": "reports/phase1_4/baseline_corrections_ledger.json"}}, reason, cid)
            stats["flagged"] += 1
            continue
        new_pos = p["new_pos"]
        if new_pos:
            kinds.append("pos")
            for e in (en_e, ja_e, *vi_all):
                ed.set("expressions", e["expression_id"], "part_of_speech", new_pos, f"POS corrected {p['old_pos']} -> {new_pos}", cid)
            ed.set("senses", sense["sense_id"], "part_of_speech", new_pos, f"POS corrected {p['old_pos']} -> {new_pos}", cid)
        old_cls = {(k["system"], k["value"]) for k in cls_by_target[cid] if "system" in k and k.get("status") != "retracted"}
        new_ja = p["ja"]
        if new_ja:
            kinds.append("ja")
            why = f"EN-JA mismatch: '{p['old_ja']}' is not a translation of '{p['en']}' (verified against JMdict)"
            ev_list = [ev.src("jmdict", f"ent_seq:{new_ja['ent_seq']}, sense_idx:{new_ja['sense_idx']}", "primary_surface", new_ja["lemma"])]
            meta = dict(ja_e["language_metadata"])
            meta["correction"] = {"phase": "1.4.1", "from": {"lemma": ja_e["lemma"], "reading": ja_e["reading"], "provenance_type": ja_e["provenance_type"]},
                                   "jmdict_pos": new_ja["jm_pos_tags"], "jmdict_glosses": new_ja["jm_glosses"], "form_note": new_ja["form_note"],
                                   "gloss_override": new_ja["gloss_override"]}
            for fld, val in (("lemma", new_ja["lemma"]), ("display_form", new_ja["lemma"]), ("reading", new_ja["reading"]),
                             ("language_metadata", meta), ("provenance_type", "SOURCE_DERIVED"), ("source_evidence", ev_list),
                             ("license", "CC-BY-SA-3.0")):
                ed.set("expressions", ja_e["expression_id"], fld, val, why, cid)
            ed.set("senses", sense["sense_id"], "gloss_ja", new_ja["lemma"], why, cid)
            # the sense DEFINITION must follow the corrected Japanese sense, else the record contradicts itself
            # (found in Luna's T1 review: 'air' still defined as "tune, melody" after JA became 空気)
            if (sense.get("definition_en") or "").startswith("Core learning sense for"):
                ed.set("senses", sense["sense_id"], "definition_en",
                       f"Core learning sense for '{p['en']}': {', '.join(new_ja['jm_glosses'][:4])}", why, cid)
            if (sense.get("definition_ja") or "").startswith("基本語彙"):
                ed.set("senses", sense["sense_id"], "definition_ja", f"基本語彙: {new_ja['lemma']} ({new_ja['reading']})", why, cid)
        if p["new_vi"]:
            kinds.append("vi")
            nv = p["new_vi"]
            fr = vn.get(nv.lower())
            why = f"VI '{p['old_vi']}' did not match the corrected sense; replaced with '{nv}' (agent-authored)"
            ihash = hashlib.sha256(json.dumps({"en": p["en"], "pos": new_pos or p["old_pos"], "ja": (new_ja or {}).get("lemma", p["old_ja"]),
                                               "old_vi": p["old_vi"]}, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
            vev = [Ev.ai(AGENT, GEN_VERSION, f"concept:{cid}, sense:{sense['sense_id']}", "vi_correction", nv, ihash, PHASE_TS)]
            vmeta = {"lexeme_source": {"status": "AI_GENERATED", "source": AGENT + " (coding agent, manual authoring)"},
                     "corpus_attestation": {"vn_freq_rank": fr["rank"] if fr else None, "vn_freq_pos": fr["pos"] if fr else []},
                     "translation_semantics_validated": {"status": "AGENT_REVIEWED_NOT_INDEPENDENT", "reviewer": AGENT},
                     "correction": {"phase": "1.4.1", "from": p["old_vi"]}}
            if vi_all:
                prim = vi_all[0]
                for fld, val in (("lemma", nv), ("display_form", nv), ("language_metadata", vmeta), ("provenance_type", "AI_GENERATED"),
                                 ("source_evidence", vev), ("license", "CC-BY-4.0")):
                    ed.set("expressions", prim["expression_id"], fld, val, why, cid)
                for syn in vi_all[1:]:       # synonyms of a replaced primary no longer describe the sense
                    ed.set("expressions", syn["expression_id"], "status", "retracted", "synonym of a replaced primary VI form", cid)
                    stats["synonyms_retracted"] += 1
            else:
                append["expressions"].append({
                    "expression_id": f"expr-vi-{suffix}", "concept_id": cid, "sense_id": sense["sense_id"], "language": "vi", "lemma": nv,
                    "display_form": nv, "reading": None, "pronunciation": None, "romanization": None,
                    "part_of_speech": new_pos or p["old_pos"], "register": "general", "usage_notes": None, "language_metadata": vmeta,
                    "provenance_type": "AI_GENERATED", "source_evidence": vev, "license": "CC-BY-4.0", "status": "verified", "created_at": PHASE_TS})
                stats["vi_added"] += 1
            ed.set("senses", sense["sense_id"], "gloss_vi", nv, why, cid)
        # ---- dependent classifications
        if new_ja or p["new_vi"]:
            cur_ja = (new_ja or {}).get("lemma", ja_e["lemma"])
            cur_rd = (new_ja or {}).get("reading", ja_e["reading"])
            cur_vi = p["new_vi"] or (vi_all[0]["lemma"] if vi_all else None)
            want = set()
            rows_new = []
            sig = {}
            if new_ja:
                hit = jl.get((cur_ja, cur_rd)) or jl.get((cur_ja, None))
                if hit:
                    sig["jlpt"] = {"level": hit["level"], "line": hit["line"]}
                rows_new += jlpt_class(cid, sig) + joyo_class(cid, cur_ja, joyo)
            if cur_vi and (p["new_vi"] or new_ja):
                fr = vn.get(cur_vi.lower())
                rows_new += vi_core_class(cid, fr["rank"] if fr else None)
            want = {(r["system"], r["value"]) for r in rows_new}
            dep = {"JLPT", "JOYO_KANJI"} if new_ja else set()
            if p["new_vi"]:
                dep |= {"VI_CORE_500", "VI_CORE_1000", "VI_CORE_2000", "VI_CORE_5000", "VI_GENERAL"}
            for k in cls_by_target[cid]:
                if k.get("system") in dep and k.get("status") != "retracted" and (k["system"], k["value"]) not in want:
                    ed.set("classifications", k["classification_id"], "status", "retracted", "form it was derived from was corrected", cid)
                    ed.set("classifications", k["classification_id"], "retraction",
                           {"phase": "1.4.1", "reason": "derived from a replaced form", "previous_status": k["status"]}, "retraction note", cid)
                    stats["classifications_retracted"] += 1
            have_ids = {k["classification_id"] for k in cls_by_target[cid]}
            for r in rows_new:
                if (r["system"], r["value"]) not in old_cls and r["classification_id"] not in have_ids:
                    r["backfill"] = "phase1.4.1"
                    append["classifications"].append(r)
        # ---- concept metadata (validation is a separate dimension from provenance)
        pos_only = kinds == ["pos"]
        md = {"correction": {"phase": "1.4.1", "kinds": kinds, "validation_status": "validated" if pos_only else "needs_review",
                             "reason": ("POS corrected; lexical content unchanged" if pos_only else
                                        "EN-JA/VI defect corrected by agent; JA verified against JMdict; no independent validation yet"),
                             "ledger": "reports/phase1_4/baseline_corrections_ledger.json"}}
        ed.set("concepts", cid, "metadata", md, "correction record", cid)
        for k in kinds:
            stats["fix_" + k] += 1

    # ---- write corrected prefixes (+ keep whatever tail exists; build_canonical regenerates the tail)
    corrected = {}
    for f in FILES:
        info = man["append_only"][f"{f}.jsonl"]
        path = CANONICAL_DIR / f"{f}.jsonl"
        cur = path.read_bytes()
        assert sha(cur[: info["bytes"]]) == info["sha256"], f"{f}: prefix is not the sealed baseline"
        pref = ed.serialize(f)
        path.write_bytes(pref + cur[info["bytes"]:])
        corrected[f"{f}.jsonl"] = {"bytes": len(pref), "lines": info["lines"], "sha256": sha(pref)}
    # examples are untouched
    corrected["examples.jsonl"] = dict(man["append_only"]["examples.jsonl"])
    # NOT sort_keys: nested old values must keep their original key order for byte-exact reversal
    LEDGER_PATH.parent.mkdir(parents=True, exist_ok=True)
    LEDGER_PATH.write_text(json.dumps({"phase": "1.4.1", "baseline_commit": man["baseline_commit"], "entries": ed.ledger, "stats": dict(stats),
                                       "note": "reverting every entry (field := old; absent => delete) reproduces the sealed Phase 1.3D bytes"},
                                      ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    write_json(P14_DIR / "baseline_corrections_append.json", append)
    man["corrected_prefix"] = corrected
    man["corrections_ledger_sha256"] = sha(LEDGER_PATH.read_bytes())
    MANIFEST.write_text(json.dumps(man, indent=1, sort_keys=True) + "\n")
    print(json.dumps({"ledger_entries": len(ed.ledger), "stats": dict(stats), "append_expressions": len(append["expressions"]),
                      "append_classifications": len(append["classifications"])}, indent=1))


if __name__ == "__main__":
    main()
