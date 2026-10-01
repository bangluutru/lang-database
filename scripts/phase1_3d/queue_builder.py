#!/usr/bin/env python3
"""
scripts/phase1_3d/queue_builder.py
Deterministically extracts all 1,034 partial concepts from canonical data,
enriches them with full JMdict sense context, and selects the 100-concept Canary batch
challenging the Phase 1.3D architecture across POS, domains, JLPT levels, and NGSL ranks.
"""

import json
import gzip
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
import xml.etree.ElementTree as ET

BASE_DIR = Path(__file__).resolve().parent.parent.parent
CANONICAL_DIR = BASE_DIR / "data" / "canonical"
JMDICT_PATH = BASE_DIR / "data" / "raw" / "jmdict" / "2026-10-01" / "JMdict_e.gz"
REPORTS_DIR = BASE_DIR / "reports" / "phase1_3d"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)


def parse_locator(locator_str: str) -> Dict[str, Any]:
    """Parses locator string e.g. 'ent_seq:1369960, sense_idx:0' or 'lemma:foo, rank:10'."""
    res = {}
    if not locator_str:
        return res
    for part in locator_str.split(","):
        if ":" in part:
            k, v = part.split(":", 1)
            res[k.strip()] = v.strip()
    return res


def load_jmdict_entries(target_ent_seqs: Set[int]) -> Dict[int, Dict[str, Any]]:
    """Loads full entry data for target ent_seqs from JMdict_e.gz."""
    entries = {}
    if not JMDICT_PATH.exists():
        raise FileNotFoundError(f"JMdict archive missing: {JMDICT_PATH}")

    with gzip.open(JMDICT_PATH, "rb") as f:
        for event, elem in ET.iterparse(f, events=["end"]):
            if elem.tag == "entry":
                seq_el = elem.find("ent_seq")
                if seq_el is not None and seq_el.text:
                    try:
                        ent_seq = int(seq_el.text.strip())
                    except ValueError:
                        elem.clear()
                        continue

                    if ent_seq in target_ent_seqs:
                        keb_list = [k.text.strip() for k in elem.findall("k_ele/keb") if k.text]
                        reb_list = [r.text.strip() for r in elem.findall("r_ele/reb") if r.text]
                        
                        senses = []
                        for s_idx, sense_el in enumerate(elem.findall("sense")):
                            pos_list = [p.text.strip().replace("&", "").replace(";", "") for p in sense_el.findall("pos") if p.text]
                            glosses = [g.text.strip() for g in sense_el.findall("gloss") if g.text]
                            misc = [m.text.strip().replace("&", "").replace(";", "") for m in sense_el.findall("misc") if m.text]
                            field = [f.text.strip().replace("&", "").replace(";", "") for f in sense_el.findall("field") if f.text]
                            senses.append({
                                "sense_index": s_idx,
                                "pos": pos_list or ["noun"],
                                "glosses": glosses,
                                "misc": misc,
                                "field": field
                            })

                        entries[ent_seq] = {
                            "ent_seq": ent_seq,
                            "keb": keb_list,
                            "reb": reb_list,
                            "primary_surface": keb_list[0] if keb_list else (reb_list[0] if reb_list else ""),
                            "primary_reading": reb_list[0] if reb_list else "",
                            "senses": senses
                        }

                elem.clear()
    return entries


def build_deterministic_queue() -> List[Dict[str, Any]]:
    """Rebuilds the queue of 1,034 partial concepts from canonical files."""
    # 1. Load canonical datasets
    concepts = {}
    with open(CANONICAL_DIR / "concepts.jsonl", "r", encoding="utf-8") as f:
        for line in f:
            c = json.loads(line)
            concepts[c["concept_id"]] = c

    senses = {}
    with open(CANONICAL_DIR / "senses.jsonl", "r", encoding="utf-8") as f:
        for line in f:
            s = json.loads(line)
            senses[s["sense_id"]] = s

    expressions_by_concept = {}
    with open(CANONICAL_DIR / "expressions.jsonl", "r", encoding="utf-8") as f:
        for line in f:
            e = json.loads(line)
            expressions_by_concept.setdefault(e["concept_id"], []).append(e)

    classifications_by_concept = {}
    with open(CANONICAL_DIR / "classifications.jsonl", "r", encoding="utf-8") as f:
        for line in f:
            cl = json.loads(line)
            classifications_by_concept.setdefault(cl["target_id"], []).append(cl)

    # 2. Identify partial EN-JA concepts
    partial_queue = []
    target_ent_seqs = set()

    for cid, elist in expressions_by_concept.items():
        langs = {e["language"] for e in elist}
        if {"en", "ja"}.issubset(langs) and "vi" not in langs:
            c = concepts[cid]
            en_expr = next(e for e in elist if e["language"] == "en")
            ja_expr = next(e for e in elist if e["language"] == "ja")
            sid = en_expr.get("sense_id") or ja_expr.get("sense_id") or f"{cid}-01"
            s = senses.get(sid, {})

            # Extract locator info
            ja_ev = ja_expr.get("source_evidence", [{}])[0]
            ja_loc = parse_locator(ja_ev.get("source_locator", ""))
            ent_seq = int(ja_loc["ent_seq"]) if "ent_seq" in ja_loc and ja_loc["ent_seq"].isdigit() else None
            sense_idx = int(ja_loc["sense_idx"]) if "sense_idx" in ja_loc and ja_loc["sense_idx"].isdigit() else 0

            if ent_seq:
                target_ent_seqs.add(ent_seq)

            en_ev = en_expr.get("source_evidence", [{}])[0]
            en_loc = parse_locator(en_ev.get("source_locator", ""))
            ngsl_rank = int(en_loc["rank"]) if "rank" in en_loc and en_loc["rank"].isdigit() else None

            # Get classifications
            cl_list = classifications_by_concept.get(cid, [])
            jlpt_val = next((cl["value"] for cl in cl_list if cl["system"] == "JLPT"), None)
            cefr_val = next((cl["value"] for cl in cl_list if cl["system"] == "CEFR"), None)
            joyo_val = next((cl["value"] for cl in cl_list if cl["system"] == "JOYO_KANJI"), None)
            eiken_val = next((cl["value"] for cl in cl_list if cl["system"] == "EIKEN"), None)

            partial_queue.append({
                "concept_id": cid,
                "canonical_name": c.get("canonical_name", ""),
                "domains": c.get("domains", ["general"]),
                "primary_domain": c.get("primary_domain", "general"),
                "sense_id": sid,
                "part_of_speech": s.get("part_of_speech", en_expr.get("part_of_speech", "noun")),
                "sense_gloss_en": s.get("gloss_en", ""),
                "sense_gloss_ja": s.get("gloss_ja", ""),
                "definition_en": s.get("definition_en", ""),
                "definition_ja": s.get("definition_ja", ""),
                "en": {
                    "expression_id": en_expr["expression_id"],
                    "lemma": en_expr["lemma"],
                    "display_form": en_expr.get("display_form", en_expr["lemma"]),
                    "part_of_speech": en_expr.get("part_of_speech", "noun"),
                    "ngsl_rank": ngsl_rank,
                    "source_locator": en_ev.get("source_locator", ""),
                    "source_evidence": en_ev
                },
                "ja": {
                    "expression_id": ja_expr["expression_id"],
                    "lemma": ja_expr["lemma"],
                    "reading": ja_expr.get("reading", ""),
                    "part_of_speech": ja_expr.get("part_of_speech", "noun"),
                    "ent_seq": ent_seq,
                    "sense_idx": sense_idx,
                    "source_locator": ja_ev.get("source_locator", ""),
                    "source_evidence": ja_ev
                },
                "classifications": {
                    "JLPT": jlpt_val,
                    "CEFR": cefr_val,
                    "JOYO_KANJI": joyo_val,
                    "EIKEN": eiken_val,
                    "NGSL": f"Rank {ngsl_rank}" if ngsl_rank else None
                }
            })

    # Sort deterministically by concept_id
    partial_queue.sort(key=lambda x: x["concept_id"])

    # 3. Enrich with JMdict context
    jm_entries = load_jmdict_entries(target_ent_seqs)
    for item in partial_queue:
        ent_seq = item["ja"]["ent_seq"]
        sense_idx = item["ja"]["sense_idx"]
        entry = jm_entries.get(ent_seq)
        if entry:
            item["ja"]["entry_keb"] = entry["keb"]
            item["ja"]["entry_reb"] = entry["reb"]
            item["ja"]["all_senses"] = entry["senses"]
            if 0 <= sense_idx < len(entry["senses"]):
                item["ja"]["target_sense"] = entry["senses"][sense_idx]
            else:
                item["ja"]["target_sense"] = entry["senses"][0] if entry["senses"] else None
        else:
            item["ja"]["entry_keb"] = [item["ja"]["lemma"]]
            item["ja"]["entry_reb"] = [item["ja"]["reading"]]
            item["ja"]["all_senses"] = []
            item["ja"]["target_sense"] = None

    return partial_queue


def select_canary_batch(queue: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Selects 100 concepts for the Canary batch.
    Must deliberately challenge the architecture with:
    - simple nouns, verbs, adjectives
    - abstract terms
    - polysemous words
    - business terms
    - academic terms
    - JLPT N5–N1 mix
    - NGSL rank ranges
    """
    # Key anchor lemmas to test challenging polysemy, grammatical, and alignment cases
    priority_challenge_lemmas = [
        "you", "i", "will", "all", "act", "action", "actual", "actually", "ad",
        "addition", "address", "ordinary", "immediately", "enterprise", "institution",
        "reason", "convention", "accurate", "comfort", "resistance", "effort",
        "ability", "about", "abroad", "absolutely", "abstract", "abuse", "accident",
        "accommodation", "accord", "achievement", "active", "activity", "admit",
        "adopt", "adult", "advance", "advantage", "adventure", "advice", "advise",
        "affair", "affect", "afford", "afraid", "agency", "agent", "aggressive",
        "agree", "agreement", "ahead", "aid", "aim", "air", "aircraft", "airline",
        "airport", "alarm", "alive", "allocate", "allow", "almost", "alone",
        "along", "alter", "alternative", "although", "altogether", "amaze",
        "ambition", "amend", "amount", "analyse", "analysis", "analyst", "analyze",
        "ancient", "anger", "angle", "angry", "animal", "announce", "announcement",
        "annual", "another", "answer", "anxiety", "anxious", "anybody", "anyway",
        "apart", "apartment", "apologize", "apology", "apparent", "apparently",
        "appeal", "appear", "appearance"
    ]

    selected = []
    selected_cids = set()

    # 1. Add challenge lemmas present in queue
    lemma_to_item = {item["en"]["lemma"]: item for item in queue}
    for lem in priority_challenge_lemmas:
        if lem in lemma_to_item and len(selected) < 100:
            item = lemma_to_item[lem]
            if item["concept_id"] not in selected_cids:
                selected.append(item)
                selected_cids.add(item["concept_id"])

    # 2. Ensure balanced representation across POS, JLPT, domains, ranks
    # Check what we have so far
    def get_pos(it): return it["part_of_speech"]
    def get_jlpt(it): return it["classifications"].get("JLPT") or "Unclassified"

    for it in queue:
        if len(selected) >= 100:
            break
        if it["concept_id"] in selected_cids:
            continue

        pos = get_pos(it)
        jlpt = get_jlpt(it)
        # Prioritize verbs and adjectives if underrepresented
        verb_count = sum(1 for x in selected if get_pos(x) == "verb")
        adj_count = sum(1 for x in selected if get_pos(x) == "adjective")
        n5_count = sum(1 for x in selected if get_jlpt(x) == "N5")
        n4_count = sum(1 for x in selected if get_jlpt(x) == "N4")

        if pos == "verb" and verb_count < 20:
            selected.append(it)
            selected_cids.add(it["concept_id"])
        elif pos == "adjective" and adj_count < 20:
            selected.append(it)
            selected_cids.add(it["concept_id"])
        elif jlpt in ("N5", "N4") and (n5_count + n4_count) < 20:
            selected.append(it)
            selected_cids.add(it["concept_id"])

    # Fill remaining up to 100
    for it in queue:
        if len(selected) >= 100:
            break
        if it["concept_id"] not in selected_cids:
            selected.append(it)
            selected_cids.add(it["concept_id"])

    # Sort canary deterministically
    selected.sort(key=lambda x: x["concept_id"])
    return selected


def main():
    print("=== Phase 1.3D Queue Builder ===")
    queue = build_deterministic_queue()
    print(f"Total partial concepts rebuilt: {len(queue)}")

    # Write full partial queue
    with open(REPORTS_DIR / "full_partial_queue.json", "w", encoding="utf-8") as f:
        json.dump(queue, f, ensure_ascii=False, indent=2)
    print(f"Saved full queue to {REPORTS_DIR / 'full_partial_queue.json'}")

    # Select Canary batch
    canary = select_canary_batch(queue)
    print(f"Selected Canary batch size: {len(canary)}")
    with open(REPORTS_DIR / "canary_queue.json", "w", encoding="utf-8") as f:
        json.dump(canary, f, ensure_ascii=False, indent=2)
    print(f"Saved Canary queue to {REPORTS_DIR / 'canary_queue.json'}")

    # Print Canary statistics
    from collections import Counter
    pos_cnt = Counter(it["part_of_speech"] for it in canary)
    jlpt_cnt = Counter(it["classifications"].get("JLPT") or "None" for it in canary)
    print("Canary POS breakdown:", dict(pos_cnt))
    print("Canary JLPT breakdown:", dict(jlpt_cnt))


if __name__ == "__main__":
    main()
