#!/usr/bin/env python3
"""
scripts/phase1_3d/audit_sampler.py
Read-only Semantic Audit Sampler for Phase 1.3D (Sections 22 & 23).
- Audits a representative sample of the 245 curated daily Vietnamese expressions across
  noun, verb, adjective, adverb, functional, and abstract categories.
- Audits a read-only sample of the 800 frozen professional concepts across
  accounting, finance, tax, legal, trade, logistics, HR, and general business.
Guarantees ZERO mutation to canonical files.
Saves audit findings to reports/phase1_3d/.
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from scripts.phase1_3d.linguistic_judge import LinguisticJudge

REPORTS_DIR = BASE_DIR / "reports" / "phase1_3d"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)
CANONICAL_DIR = BASE_DIR / "data" / "canonical"


def sample_daily_vocabulary() -> List[Dict[str, Any]]:
    """Loads and samples curated daily Vietnamese concepts."""
    concepts = {c["concept_id"]: c for c in (json.loads(l) for l in open(CANONICAL_DIR / "concepts.jsonl"))}
    senses = {s["concept_id"]: s for s in (json.loads(l) for l in open(CANONICAL_DIR / "senses.jsonl"))}
    exprs_by_cid = {}
    for l in open(CANONICAL_DIR / "expressions.jsonl"):
        e = json.loads(l)
        exprs_by_cid.setdefault(e["concept_id"], []).append(e)

    curated_items = []
    for cid, elist in exprs_by_cid.items():
        vi_expr = next((e for e in elist if e["language"] == "vi" and e["provenance_type"] == "CURATED" and "core" in e["expression_id"]), None)
        en_expr = next((e for e in elist if e["language"] == "en"), None)
        ja_expr = next((e for e in elist if e["language"] == "ja"), None)
        if vi_expr and en_expr and ja_expr:
            c = concepts.get(cid, {})
            s = senses.get(cid, {})
            curated_items.append({
                "concept_id": cid,
                "domain": c.get("primary_domain", "daily_life"),
                "en": en_expr,
                "ja": ja_expr,
                "vi": vi_expr,
                "pos": s.get("part_of_speech", en_expr.get("part_of_speech", "noun")),
                "sense": s
            })

    curated_items.sort(key=lambda x: x["concept_id"])

    # Sample 30 items balanced across POS
    sampled = []
    by_pos = {}
    for it in curated_items:
        by_pos.setdefault(it["pos"], []).append(it)

    for pos, items in by_pos.items():
        sampled.extend(items[:10])

    return sampled[:30]


def sample_professional_corpus() -> List[Dict[str, Any]]:
    """Loads and samples frozen professional 800 concepts."""
    concepts = {c["concept_id"]: c for c in (json.loads(l) for l in open(CANONICAL_DIR / "concepts.jsonl"))}
    senses = {s["concept_id"]: s for s in (json.loads(l) for l in open(CANONICAL_DIR / "senses.jsonl"))}
    exprs_by_cid = {}
    for l in open(CANONICAL_DIR / "expressions.jsonl"):
        e = json.loads(l)
        exprs_by_cid.setdefault(e["concept_id"], []).append(e)

    pro_items = []
    for cid, elist in exprs_by_cid.items():
        if not cid.startswith("concept-pro-"):
            continue
        vi_expr = next((e for e in elist if e["language"] == "vi"), None)
        en_expr = next((e for e in elist if e["language"] == "en"), None)
        ja_expr = next((e for e in elist if e["language"] == "ja"), None)
        if vi_expr and en_expr and ja_expr:
            c = concepts.get(cid, {})
            s = senses.get(cid, {})
            pro_items.append({
                "concept_id": cid,
                "domain": c.get("primary_domain", "business"),
                "domains": c.get("domains", ["business"]),
                "en": en_expr,
                "ja": ja_expr,
                "vi": vi_expr,
                "pos": s.get("part_of_speech", "noun"),
                "sense": s
            })

    pro_items.sort(key=lambda x: x["concept_id"])

    # Sample 40 items across domains
    by_domain = {}
    for it in pro_items:
        by_domain.setdefault(it["domain"], []).append(it)

    sampled = []
    for dom, items in by_domain.items():
        sampled.extend(items[:6])

    return sampled[:40]


def audit_single_item(judge: LinguisticJudge, it: Dict[str, Any], source_type: str) -> Dict[str, Any]:
    pseudo_item = {
        "concept_id": it["concept_id"],
        "sense_id": it["sense"].get("sense_id", f"{it['concept_id']}-01"),
        "domains": it.get("domains", [it.get("domain", "general")]),
        "en": it["en"],
        "ja": it["ja"],
        "definition_en": it["sense"].get("definition_en", it["en"]["lemma"])
    }
    cand = {
        "lemma": it["vi"]["lemma"],
        "part_of_speech": it["vi"]["part_of_speech"],
        "definition": it["sense"].get("definition_vi", it["vi"]["lemma"]),
        "source_type": source_type
    }
    res = judge.evaluate(pseudo_item, cand)
    return {
        "concept_id": it["concept_id"],
        "domain": it.get("domain", "general"),
        "lemma_en": it["en"]["lemma"],
        "lemma_ja": it["ja"]["lemma"],
        "lemma_vi": it["vi"]["lemma"],
        "decision": res["decision"],
        "semantic_alignment": res["semantic_alignment"],
        "naturalness": res["naturalness"],
        "confidence": res["confidence"],
        "note": res["evaluation_note"]
    }


def run_audits() -> Dict[str, Any]:
    judge = LinguisticJudge()

    # 1. Audit Daily Vocabulary
    print("Sampling daily vocabulary for audit...")
    daily_sample = sample_daily_vocabulary()
    print(f"Auditing {len(daily_sample)} daily vocabulary concepts (concurrency=5)...")
    daily_results = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(audit_single_item, judge, it, "CURATED"): it for it in daily_sample}
        for f in as_completed(futures):
            daily_results.append(f.result())

    daily_results.sort(key=lambda x: x["concept_id"])
    with open(REPORTS_DIR / "daily_vocabulary_audit.json", "w", encoding="utf-8") as f:
        json.dump(daily_results, f, ensure_ascii=False, indent=2)

    # 2. Audit Professional Core
    print("Sampling professional 800 corpus for audit...")
    pro_sample = sample_professional_corpus()
    print(f"Auditing {len(pro_sample)} professional concepts (concurrency=5)...")
    pro_results = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(audit_single_item, judge, it, "OFFICIAL_CURATED"): it for it in pro_sample}
        for f in as_completed(futures):
            pro_results.append(f.result())

    pro_results.sort(key=lambda x: x["concept_id"])
    with open(REPORTS_DIR / "professional_audit.json", "w", encoding="utf-8") as f:
        json.dump(pro_results, f, ensure_ascii=False, indent=2)

    daily_accept_rate = sum(1 for r in daily_results if r["decision"] in ("ACCEPT", "ACCEPT_WITH_NOTE")) / len(daily_results)
    pro_accept_rate = sum(1 for r in pro_results if r["decision"] in ("ACCEPT", "ACCEPT_WITH_NOTE")) / len(pro_results)

    print(f"\n=== Audit Results ===")
    print(f"Daily vocabulary audit ({len(daily_results)} items): {daily_accept_rate * 100:.1f}% ACCEPT rate")
    print(f"Professional corpus audit ({len(pro_results)} items): {pro_accept_rate * 100:.1f}% ACCEPT rate")

    return {
        "daily_sample_count": len(daily_results),
        "daily_accept_rate": daily_accept_rate,
        "professional_sample_count": len(pro_results),
        "professional_accept_rate": pro_accept_rate
    }


if __name__ == "__main__":
    run_audits()
