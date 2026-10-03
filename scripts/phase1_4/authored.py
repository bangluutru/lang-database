"""
scripts/phase1_4/authored.py
Loads Gemini-authored 'A1' concepts that Claude reviewed as PASS (data/phase1_4/handoff/claude_review_A1.json) and turns them into
JMdict-anchored pool candidates + Vietnamese proposals that build_canonical consumes exactly like any other accepted candidate.
Provenance: JA/EN pairing is JMdict-derived (verified by validate_authored.py); the English sense definition, the Vietnamese lexeme and the
examples are AI_GENERATED (gemini-3.8), concept stays needs_review / Tier C. Deterministic and offline.
"""
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

from scripts.phase1_4.common import P14_DIR, read_jsonl
from scripts.phase1_4 import lexicons as L

HO = P14_DIR / "handoff"


def _passed_rows():
    rp = HO / "claude_review_A1.json"
    if not rp.exists():
        return []
    ok = {i for i, v in json.loads(rp.read_text(encoding="utf-8"))["entries"].items() if v["verdict"] == "PASS"}
    rows = []
    for p in sorted((HO / "decisions").glob("A1_*.jsonl")):
        for l in p.read_text(encoding="utf-8").splitlines():
            if l.strip():
                d = json.loads(l)
                if d["id"] in ok and not d.get("skip"):
                    rows.append((d, p.name, hashlib.sha256(json.dumps(d, ensure_ascii=False, sort_keys=True).encode()).hexdigest()))
    return rows


def load_authored(existing_en_concepts: Dict[str, str]) -> Tuple[Dict[str, Dict[str, Any]], Dict[str, Dict[str, Any]]]:
    """returns (pool candidates keyed by cand_id, vi proposals keyed by candidate id).  existing_en_concepts: lower-case EN lemma -> a concept_id
    that already uses it (to mark polysemy). The caller computes the concept_id of each candidate to attach the VI proposal."""
    jm = L.load_jmdict()
    pool, vis = {}, {}
    for d, packet, ihash in _passed_rows():
        e = jm[d["evidence"]["jmdict_ent_seq"]]
        sn = next(s for s in e["senses"] if s["idx"] == d["evidence"]["jmdict_sense_idx"])
        en, ja = d["en"], d["ja"]
        cid = f"a1-{e['seq']}-{sn['idx']}-{en['lemma'].replace(' ', '-')}"
        other = existing_en_concepts.get(en["lemma"].lower())
        closest = d["falsification"].get("closest_existing_concept", "")
        match = ({"decision": "EXISTING_CONCEPT_NEW_SENSE", "existing_concept_id": closest if closest.startswith("concept-") else other,
                  "reason": "authored sense distinct from existing concept (reviewed)"} if other else
                 {"decision": "NEW_CONCEPT", "existing_concept_id": None, "reason": "no existing concept for this EN lemma or JA entry"})
        pri = max([L.pri_score(k["pri"]) for k in e["kanji"]] + [L.pri_score(r["pri"]) for r in e["readings"]] + [0])
        pool[cid] = {
            "cand_id": cid, "authored": {
                "task": d["id"].split("-")[0], "slot": d["id"], "worker": d["reviewer"], "domain": d["domain"], "subdomain": d["subdomain"],
                "definition_en_source": "AI_GENERATED", "examples": {k: d["falsification"][k] for k in ("example_en", "example_ja", "example_vi")},
                "back_translation": d["falsification"]["back_translation"], "worker_confidence": d["confidence"],
                "worker_note": d["note"], "review": "Claude read every entry; PASS (see claude_review_A1.json)"},
            "en": {"lemma": en["lemma"], "pos": en["pos"], "ipa": None, "anchor": "jmdict", "wikt_line": None, "wikt_sense": None,
                   "wikt_gloss": en["sense_definition"], "wikt_parents": [], "wikt_tags": [], "wikt_topics": [], "seed": "a1_authoring"},
            "ja": {"lemma": ja["lemma"], "reading": ja["reading"], "wikt_surface": ja["lemma"], "form_note": "orthography:authored_from_jmdict",
                   "ent_seq": e["seq"], "sense_idx": sn["idx"], "gloss_score": 3, "gloss_overlap": 0, "jm_pos_tags": sn["pos_tags"],
                   "jm_glosses": sn["glosses"], "jm_misc": sn["misc"], "jm_field": sn["field"], "suru": "vs" in sn["pos_tags"],
                   "pri_score": pri, "synonyms": []},
            "ja_uncorroborated": [], "vi": None, "signals": {"en": {}, "jmdict_pri": pri},
            "value": {"en": 0, "ja": pri, "vi": 0, "cross": 0, "langs_with_signal": 1, "total": 0, "core_sense": sn["idx"] <= 1,
                      "note": "authored concept: not scored by the Phase 1.4 value model"},
            "match": match}
        vis[cid] = {"vi_lemma": d["vi"]["lemma"], "confidence": d["confidence"], "packet": packet, "input_hash": ihash}
    return pool, vis
