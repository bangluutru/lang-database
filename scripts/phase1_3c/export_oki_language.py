"""
scripts/phase1_3c/export_oki_language.py
Oki-Language Compatibility Export Adapter for Phase 1.3C (Section 24).
Transforms canonical EN-JA-VI learning graph concepts into a downstream deckData-compatible artifact:
    data/exports/oki_language/deck_data.json
Ensures oki-language does not maintain a divergent lexical source of truth.
"""

import json
from pathlib import Path
from typing import Dict, List, Any

BASE_DIR = Path(__file__).resolve().parent.parent.parent
CANONICAL_DIR = BASE_DIR / "data" / "canonical"
OKI_EXPORT_DIR = BASE_DIR / "data" / "exports" / "oki_language"


def export_oki_deck_data() -> Dict[str, Any]:
    """Generates deckData-compatible JSON from canonical concepts."""
    OKI_EXPORT_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Load canonical data
    concepts = {}
    with open(CANONICAL_DIR / "concepts.jsonl", "r", encoding="utf-8") as f:
        for line in f:
            c = json.loads(line)
            concepts[c["concept_id"]] = c

    senses = {}
    with open(CANONICAL_DIR / "senses.jsonl", "r", encoding="utf-8") as f:
        for line in f:
            s = json.loads(line)
            senses.setdefault(s["concept_id"], []).append(s)

    expressions = {}
    with open(CANONICAL_DIR / "expressions.jsonl", "r", encoding="utf-8") as f:
        for line in f:
            e = json.loads(line)
            cid = e["concept_id"]
            lang = e["language"]
            expressions.setdefault(cid, {}).setdefault(lang, []).append(e)

    classifications = {}
    with open(CANONICAL_DIR / "classifications.jsonl", "r", encoding="utf-8") as f:
        for line in f:
            cl = json.loads(line)
            tid = cl.get("target_id")
            if tid:
                classifications.setdefault(tid, []).append(cl)

    examples = {}
    examples_file = CANONICAL_DIR / "examples.jsonl"
    if examples_file.exists():
        with open(examples_file, "r", encoding="utf-8") as f:
            for line in f:
                ex = json.loads(line)
                examples.setdefault(ex["concept_id"], []).append(ex)

    # 2. Transform into deckData cards
    deck_cards = []
    for cid, c in concepts.items():
        exprs = expressions.get(cid, {})
        en_list = exprs.get("en", [])
        ja_list = exprs.get("ja", [])
        vi_list = exprs.get("vi", [])

        en_expr = en_list[0] if en_list else None
        ja_expr = ja_list[0] if ja_list else None
        vi_expr = vi_list[0] if vi_list else None

        # Collect classifications from concept and expressions
        cl_list = []
        for cl in classifications.get(cid, []):
            cl_list.append({"system": cl.get("system"), "value": cl.get("value"), "status": cl.get("status")})
        for lang_exprs in (en_list, ja_list, vi_list):
            for e in lang_exprs:
                for cl in classifications.get(e["expression_id"], []):
                    cl_list.append({"system": cl.get("system"), "value": cl.get("value"), "status": cl.get("status")})

        # Senses
        c_senses = senses.get(cid, [])
        sense_summaries = []
        for s in c_senses:
            sense_summaries.append({
                "sense_id": s.get("sense_id"),
                "pos": s.get("part_of_speech"),
                "gloss_en": s.get("gloss_en"),
                "gloss_ja": s.get("gloss_ja"),
                "gloss_vi": s.get("gloss_vi"),
                "definition_en": s.get("definition_en"),
                "definition_ja": s.get("definition_ja"),
                "definition_vi": s.get("definition_vi")
            })

        # Examples
        c_examples = examples.get(cid, [])
        ex_summaries = []
        for ex in c_examples:
            ex_summaries.append({
                "en": ex.get("sentence_en"),
                "ja": ex.get("sentence_ja"),
                "vi": ex.get("sentence_vi")
            })

        card = {
            "id": cid,
            "canonical_name": c.get("canonical_name"),
            "domains": c.get("domains", []),
            "primary_domain": c.get("primary_domain", "general"),
            "english": en_expr.get("lemma") if en_expr else None,
            "japanese": ja_expr.get("display_form") or ja_expr.get("lemma") if ja_expr else None,
            "reading": ja_expr.get("reading") if ja_expr else None,
            "vietnamese": vi_expr.get("display_form") or vi_expr.get("lemma") if vi_expr else None,
            "pos": en_expr.get("part_of_speech") if en_expr else (ja_expr.get("part_of_speech") if ja_expr else None),
            "senses": sense_summaries,
            "classifications": cl_list,
            "examples": ex_summaries,
            "tags": c.get("domains", []) + [cl["value"] for cl in cl_list if cl.get("value")]
        }
        deck_cards.append(card)

    deck_cards.sort(key=lambda x: x["id"])

    # Output files
    deck_output_file = OKI_EXPORT_DIR / "deck_data.json"
    with open(deck_output_file, "w", encoding="utf-8") as f:
        json.dump(deck_cards, f, ensure_ascii=False, indent=2)

    summary = {
        "total_deck_cards": len(deck_cards),
        "complete_tri_language_cards": sum(1 for c in deck_cards if c["english"] and c["japanese"] and c["vietnamese"]),
        "export_destination": str(deck_output_file),
        "status": "ready_for_oki_language_import"
    }

    summary_file = OKI_EXPORT_DIR / "summary.json"
    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    print(f"[+] Exported {len(deck_cards)} oki-language compatible deck cards to {deck_output_file}")
    return summary


if __name__ == "__main__":
    export_oki_deck_data()
