#!/usr/bin/env python3
"""
scripts/phase1_4/export_views.py
Generated, reproducible exports. Canonical data remains the source of truth.

1. Oki-language deck  (data/exports/oki_language/deck_data.json + summary.json)
   - baseline cards come verbatim from the sealed Phase 1.3D deck (only additive classification rows
     from the Phase 1.4 backfill are appended), new cards use the same schema and semantics.
2. Learning views      (data/exports/views_v1_4/<lang>/<view>.jsonl + views_index.json)
   Views are *classifications over the single canonical graph*: no concept is duplicated.
"""

import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from scripts.phase1_4.common import BASE_DIR, CANONICAL_DIR, read_jsonl, write_json

OKI_DIR = BASE_DIR / "data" / "exports" / "oki_language"
VIEW_DIR = BASE_DIR / "data" / "exports" / "views_v1_4"
BASE_DECK = BASE_DIR / "data" / "releases" / "phase1_3d-sealed" / "oki_deck_data.baseline.json"


def csys(c: Dict[str, Any]):
    return (c.get("system") or c.get("classification_system"), c.get("value") if "value" in c else c.get("classification_value"),
            c.get("status") if "status" in c else c.get("classification_status"))


def build_cards() -> List[Dict[str, Any]]:
    concepts = {c["concept_id"]: c for c in read_jsonl(CANONICAL_DIR / "concepts.jsonl")}
    senses = defaultdict(list)
    for s in read_jsonl(CANONICAL_DIR / "senses.jsonl"):
        senses[s["concept_id"]].append(s)
    exprs = defaultdict(lambda: defaultdict(list))
    for e in read_jsonl(CANONICAL_DIR / "expressions.jsonl"):
        if e.get("status") != "retracted":
            exprs[e["concept_id"]][e["language"]].append(e)
    cls = defaultdict(list)
    for c in read_jsonl(CANONICAL_DIR / "classifications.jsonl"):
        if c.get("status") != "retracted" and c.get("classification_status") != "retracted":
            cls[c["target_id"]].append(c)
    base = {c["id"]: c for c in json.loads(BASE_DECK.read_text())}

    cards = []
    for cid, c in concepts.items():
        cl_list = []
        for k in cls.get(cid, []):
            s, v, st = csys(k)
            cl_list.append({"system": s, "value": v, "status": st})
        corr = (c.get("metadata") or {}).get("correction")
        if cid in base and not corr:
            card = json.loads(json.dumps(base[cid]))
            known = {(x["system"], x["value"], x["status"]) for x in card["classifications"]}
            extra = [x for x in cl_list if (x["system"], x["value"], x["status"]) not in known]
            card["classifications"] += extra
            card["tags"] += [x["value"] for x in extra if x.get("value")]
            cards.append(card)
            continue
        md = dict(c["metadata"])
        if corr:           # Phase 1.4.1 corrected baseline concept: rebuilt from canonical, validation recorded in metadata
            md["validation_status"] = corr["validation_status"]
            md["quality_tier"] = "Tier D" if corr["validation_status"] != "validated" else base[cid]["provenance_quality"]
        en = (exprs[cid].get("en") or [None])[0]
        ja = (exprs[cid].get("ja") or [None])[0]
        vi = (exprs[cid].get("vi") or [None])[0]
        complete = bool(en and ja and vi)
        cards.append({
            "id": cid, "canonical_name": c["canonical_name"], "domains": c["domains"], "primary_domain": c["primary_domain"],
            "english": en["lemma"] if en else None,
            "japanese": (ja.get("display_form") or ja["lemma"]) if ja else None,
            "reading": ja.get("reading") if ja else None,
            "vietnamese": (vi.get("display_form") or vi["lemma"]) if vi else None,
            "pos": en["part_of_speech"] if en else None,
            "translation_status": "complete" if complete else "partial",
            "validation_status": md.get("validation_status", "validated"),
            "provenance_quality": md.get("quality_tier", "Tier D"),
            "production_ready": complete and md.get("validation_status") == "validated",
            "senses": [{"sense_id": s["sense_id"], "pos": s["part_of_speech"], "gloss_en": s["gloss_en"], "gloss_ja": s["gloss_ja"],
                        "gloss_vi": s["gloss_vi"], "definition_en": s["definition_en"], "definition_ja": s["definition_ja"],
                        "definition_vi": s["definition_vi"]} for s in senses[cid]],
            "classifications": cl_list, "examples": [],
            "tags": c["domains"] + [x["value"] for x in cl_list if x.get("value")],
        })
    cards.sort(key=lambda x: x["id"])
    return cards


def export_oki(cards):
    OKI_DIR.mkdir(parents=True, exist_ok=True)
    (OKI_DIR / "deck_data.json").write_text(json.dumps(cards, ensure_ascii=False, indent=2), encoding="utf-8")
    ready = [c for c in cards if c["production_ready"]]
    summary = {
        "total_deck_cards": len(cards), "complete_tri_language_cards": len(ready),
        "partial_cards": sum(1 for c in cards if c["translation_status"] == "partial"),
        "validated_cards": sum(1 for c in cards if c["validation_status"] == "validated"),
        "tier_a_count": sum(1 for c in cards if c["provenance_quality"] == "Tier A"),
        "tier_b_count": sum(1 for c in cards if c["provenance_quality"] == "Tier B"),
        "tier_c_count": sum(1 for c in cards if c["provenance_quality"] == "Tier C"),
        "tier_d_count": sum(1 for c in cards if c["provenance_quality"] == "Tier D"),
        "export_destination": "data/exports/oki_language/deck_data.json", "status": "ready_for_oki_language_import",
    }
    write_json(OKI_DIR / "summary.json", summary)
    return summary


def rank_of(c, prefix):
    for x in c["classifications"]:
        if x["system"] == prefix and x["value"] and str(x["value"]).startswith("Rank"):
            return int(str(x["value"]).split()[1])
    return None


def has(c, system, value=None):
    return any(x["system"] == system and (value is None or x["value"] == value) for x in c["classifications"])


def export_views(cards):
    ok = [c for c in cards if c["validation_status"] == "validated"]
    biz_dom = {"business", "accounting", "finance", "trade", "logistics", "manufacturing"}

    def doms(c):
        return set(c["domains"]) | {c["primary_domain"]}

    views: Dict[str, Dict[str, Any]] = {}

    def add(lang, name, pred):
        views[f"{lang}/{name}"] = pred

    for n in (5, 4, 3, 2, 1):
        add("japanese", f"jlpt_n{n}", lambda c, n=n: has(c, "JLPT", f"N{n}"))
    add("japanese", "joyo_kanji", lambda c: has(c, "JOYO_KANJI"))
    add("japanese", "daily_japanese", lambda c: "daily_life" in doms(c) and bool(c["japanese"]))
    add("japanese", "business_japanese", lambda c: bool(doms(c) & biz_dom) and bool(c["japanese"]))
    add("english", "core_english", lambda c: (rank_of(c, "NGSL") or 10 ** 9) <= 1000)
    add("english", "ngsl", lambda c: has(c, "NGSL"))
    for lv in ("A1", "A2", "B1", "B2", "C1", "C2"):
        add("english", f"cefr_{lv.lower()}", lambda c, lv=lv: has(c, "CEFR", lv))
    add("english", "spoken_english", lambda c: has(c, "NGSL_SPOKEN"))
    add("english", "academic_english", lambda c: has(c, "NAWL"))
    add("english", "eiken_relevance", lambda c: has(c, "EIKEN"))
    add("english", "toeic_relevance", lambda c: has(c, "TOEIC"))
    add("english", "ielts_relevance", lambda c: has(c, "IELTS"))
    add("english", "toefl_relevance", lambda c: has(c, "TOEFL"))
    add("vietnamese", "vi_core_500", lambda c: has(c, "VI_CORE_500"))
    add("vietnamese", "vi_core_1000", lambda c: has(c, "VI_CORE_500") or has(c, "VI_CORE_1000"))
    add("vietnamese", "vi_core_2000", lambda c: any(has(c, s) for s in ("VI_CORE_500", "VI_CORE_1000", "VI_CORE_2000")))
    add("vietnamese", "vi_core_5000", lambda c: any(has(c, s) for s in ("VI_CORE_500", "VI_CORE_1000", "VI_CORE_2000", "VI_CORE_5000")))
    add("vietnamese", "vi_general", lambda c: has(c, "VI_GENERAL"))
    for d in ("business", "accounting", "finance", "logistics", "trade", "manufacturing", "it", "science", "healthcare",
              "travel", "education", "daily_life"):
        add("domains", d, lambda c, d=d: d in doms(c))

    index = {}
    for key in sorted(views):
        rows = [{"concept_id": c["id"], "english": c["english"], "japanese": c["japanese"], "reading": c["reading"],
                 "vietnamese": c["vietnamese"], "pos": c["pos"], "translation_status": c["translation_status"],
                 "provenance_quality": c["provenance_quality"]} for c in ok if views[key](c)]
        p = VIEW_DIR / f"{key}.jsonl"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
        index[key] = {"concepts": len(rows), "complete": sum(1 for r in rows if r["translation_status"] == "complete")}
    write_json(VIEW_DIR / "views_index.json", {
        "note": "Views are projections over the single canonical graph (validated concepts only). "
                "'core_english' = NGSL rank <= 1000; Vietnamese core views are cumulative; no spoken-Vietnamese view is "
                "provided because vn_freq does not separate spoken from written text.",
        "views": index})
    return index


def export_vi_lexicon(cards):
    """Vietnamese-first learning view: one row per Vietnamese lemma with its OWN corpus frequency/POS/band and the
    concepts/equivalents it links to (so Vietnamese is a first-class learning language, not a translation column)."""
    from scripts.phase1_4 import lexicons as L
    vn = L.load_vn_freq()
    rows = {}
    ok = {c["id"]: c for c in cards if c["validation_status"] == "validated" and c["vietnamese"]}
    for cid, c in sorted(ok.items()):
        lem = c["vietnamese"].lower()
        r = rows.setdefault(lem, {"vi": lem, "concept_ids": [], "en": [], "ja": []})
        r["concept_ids"].append(cid)
        r["en"].append(c["english"])
        r["ja"].append(c["japanese"])
    out = []
    for lem in sorted(rows, key=lambda x: (vn.get(x, {}).get("rank", 10 ** 9), x)):
        r = rows[lem]
        f = vn.get(lem)
        rank = f["rank"] if f else None
        r.update({"vn_freq_rank": rank, "vn_freq_count": f["count"] if f else None, "vn_pos": f["pos"] if f else [],
                  "core_band": (None if not rank else "Core 500" if rank <= 500 else "Core 1000" if rank <= 1000 else
                                "Core 2000" if rank <= 2000 else "Core 5000" if rank <= 5000 else "General"),
                  "senses": len(r["concept_ids"])})
        out.append(r)
    p = VIEW_DIR / "vietnamese" / "vi_lexicon.jsonl"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in out), encoding="utf-8")
    return len(out)


def main():
    cards = build_cards()
    s = export_oki(cards)
    idx = export_views(cards)
    n_vi = export_vi_lexicon(cards)
    print("vi_lexicon lemmas:", n_vi)
    print(json.dumps(s, indent=1))
    print(json.dumps(idx, indent=0)[:1500])


if __name__ == "__main__":
    main()
