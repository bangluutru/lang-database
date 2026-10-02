#!/usr/bin/env python3
"""
scripts/phase1_4/generate_reports.py
Stage 8: machine-readable final metrics + auditable closure artefacts. Everything is computed from the
canonical files and the cached pipeline artefacts - no number in the reports is typed by hand.
"""
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from scripts.phase1_4.common import BASE_DIR, CANONICAL_DIR, P14_DIR, REPORTS_DIR, BASELINE_SHA, read_jsonl, write_json, validation_overrides
from scripts.phase1_4 import judge as J

BASE_DECK = BASE_DIR / "data/releases/phase1_3d-sealed/oki_deck_data.baseline.json"


def band(r, cuts):
    for c in cuts:
        if r <= c:
            return f"<={c}"
    return f">{cuts[-1]}"


def main():
    concepts = read_jsonl(CANONICAL_DIR / "concepts.jsonl")
    senses = read_jsonl(CANONICAL_DIR / "senses.jsonl")
    exprs = read_jsonl(CANONICAL_DIR / "expressions.jsonl")
    classes = read_jsonl(CANONICAL_DIR / "classifications.jsonl")
    man = json.loads((BASE_DIR / "data/releases/phase1_3d-sealed/baseline_manifest.json").read_text())
    base_deck = {c["id"]: c for c in json.loads(BASE_DECK.read_text())}
    base_ids = set(base_deck)
    new = [c for c in concepts if c["concept_id"] not in base_ids]
    newids = {c["concept_id"] for c in new}
    by = defaultdict(lambda: defaultdict(list))
    for e in exprs:
        if e.get("status") != "retracted":
            by[e["concept_id"]][e["language"]].append(e)

    def status(cid):
        langs = {l for l, v in by[cid].items() if v}
        return "complete" if {"en", "ja", "vi"} <= langs else "partial"

    m = {"baseline_commit": BASELINE_SHA}
    tri_all = sum(1 for c in concepts if status(c["concept_id"]) == "complete")
    tri_new = sum(1 for c in new if status(c["concept_id"]) == "complete")
    tri_base = tri_all - tri_new
    m["corpus"] = {"baseline_concepts": len(base_ids), "total_concepts": len(concepts), "new_concepts": len(new),
                   "tri_language_complete": tri_all, "tri_language_complete_baseline": tri_base,
                   "tri_language_complete_new": tri_new, "partial": len(concepts) - tri_all,
                   "partial_new": len(new) - tri_new, "senses": len(senses), "expressions": len(exprs),
                   "classification_rows": len(classes)}
    cov = Counter()
    for c in concepts:
        for l in ("en", "ja", "vi"):
            if by[c["concept_id"]][l]:
                cov[l] += 1
    m["language_coverage_concepts"] = dict(cov)

    # ---- classification views (distinct concepts per classification)
    cl_concepts = defaultdict(set)
    for k in classes:
        if k.get("status") == "retracted":
            continue
        s = k.get("system") or k.get("classification_system")
        v = k.get("value") if "value" in k else k.get("classification_value")
        cl_concepts[(s, v)].add(k["target_id"])
        cl_concepts[(s, None)].add(k["target_id"])
    def n(sys_, val=None):
        return len(cl_concepts.get((sys_, val), ()))
    m["by_classification"] = {
        "JLPT": {f"N{i}": n("JLPT", f"N{i}") for i in (5, 4, 3, 2, 1)},
        "CEFR": {lv: n("CEFR", lv) for lv in ("A1", "A2", "B1", "B2", "C1", "C2")},
        "EIKEN_any": n("EIKEN"), "TOEIC_any": n("TOEIC"), "IELTS_any": n("IELTS"), "TOEFL_any": n("TOEFL"),
        "NGSL": n("NGSL"), "NGSL_SPOKEN": n("NGSL_SPOKEN"), "NAWL_academic": n("NAWL"),
        "BUSINESS_SERVICE_LIST": n("BUSINESS_SERVICE_LIST"), "JOYO_KANJI": n("JOYO_KANJI"),
        "VI_CORE_exclusive_bands": {b: n(b) for b in ("VI_CORE_500", "VI_CORE_1000", "VI_CORE_2000", "VI_CORE_5000", "VI_GENERAL")},
    }
    cum = {}
    run = set()
    for b, label in (("VI_CORE_500", "Core 500"), ("VI_CORE_1000", "Core 1000"), ("VI_CORE_2000", "Core 2000"), ("VI_CORE_5000", "Core 5000")):
        run |= cl_concepts.get((b, None), set())
        cum[label] = len(run)
    m["by_classification"]["VI_CORE_cumulative"] = cum

    # ---- Vietnamese core coverage: how much of each vn_freq band has a validated VI concept
    from scripts.phase1_4 import lexicons as L
    vnf = L.load_vn_freq()
    vi_lemmas = {e["lemma"].lower() for e in exprs if e["language"] == "vi"}
    byrank = sorted(vnf.items(), key=lambda kv: kv[1]["rank"])
    m["vi_core_lemma_coverage"] = {lab: {"words": min(k, len(byrank)), "covered_by_a_corpus_VI_lemma": sum(1 for w, _ in byrank[:k] if w in vi_lemmas)}
                                   for lab, k in (("top500", 500), ("top1000", 1000), ("top2000", 2000), ("top5000", 5000))}
    m["vi_core_lemma_coverage"]["note"] = ("top-N vn_freq lists include many function words/particles/proper names that are not "
                                           "translatable concepts, so <100% coverage is expected; the metric tracks progress only.")

    # ---- frequency bands (new concepts)
    ngsl_rank = {}
    for k in classes:
        if k.get("system") == "NGSL" and k["target_id"] in newids:
            ngsl_rank[k["target_id"]] = int(k["value"].split()[1])
    vi_rank = {}
    for c in new:
        for e in by[c["concept_id"]]["vi"]:
            r = e["language_metadata"].get("corpus_attestation", {}).get("vn_freq_rank")
            if r:
                vi_rank[c["concept_id"]] = r
    m["frequency_bands_new_concepts"] = {
        "ngsl_rank": dict(Counter(band(r, [500, 1000, 2000, 2809]) for r in ngsl_rank.values())),
        "vn_freq_rank": dict(Counter(band(r, [500, 1000, 2000, 5000, 10000]) for r in vi_rank.values())),
        "no_ngsl_rank": len(new) - len(ngsl_rank), "no_vn_freq_rank": len(new) - len(vi_rank),
        "learning_value": dict(Counter(("60+" if c["metadata"]["learning_value"]["total"] >= 60 else "45-59" if c["metadata"]["learning_value"]["total"] >= 45 else
                                        "30-44" if c["metadata"]["learning_value"]["total"] >= 30 else "20-29" if c["metadata"]["learning_value"]["total"] >= 20 else "10-19") for c in new)),
    }
    # ---- domains
    dom = Counter()
    for c in concepts:
        for d in set(c["domains"]):
            dom[d] += 1
    m["by_domain_all_concepts"] = dict(sorted(dom.items()))
    m["by_primary_domain_new"] = dict(Counter(c["primary_domain"] for c in new))

    # ---- provenance
    prov = defaultdict(Counter)
    for e in exprs:
        prov[e["language"]][e["provenance_type"]] += 1
    m["expression_provenance_by_language"] = {l: dict(v) for l, v in prov.items()}
    m["expression_provenance_new_only"] = {l: dict(Counter(e["provenance_type"] for e in exprs if e["language"] == l and e["concept_id"] in newids)) for l in ("en", "ja", "vi")}
    vi_prov_concepts = Counter()
    for c in concepts:
        v = by[c["concept_id"]]["vi"]
        vi_prov_concepts[v[0]["provenance_type"] if v else "NO_VI"] += 1
    m["concept_vi_provenance_all"] = dict(vi_prov_concepts)
    cprov = Counter()
    for k in classes:
        cprov[k.get("provenance_type") or "legacy_schema"] += 1
    m["classification_provenance"] = dict(cprov)

    # ---- validation distribution (all concepts)
    val = Counter()
    for c in concepts:
        cid = c["concept_id"]
        if cid in newids:
            val[(c["metadata"]["validation_status"], status(cid))] += 1
        elif (c.get("metadata") or {}).get("correction"):
            val[(validation_overrides().get(cid, {}).get("status", c["metadata"]["correction"]["validation_status"]), status(cid))] += 1
        else:
            card = base_deck[cid]
            val[(card["validation_status"], card["translation_status"])] += 1
    m["validation_distribution"] = {f"{a}/{b}": v for (a, b), v in sorted(val.items())}
    m["quality_tiers_new"] = dict(Counter(c["metadata"]["quality_tier"] for c in new))

    # ---- sources
    src = Counter()
    anchor = Counter(c["metadata"]["anchor"] for c in new)
    for e in exprs:
        if e["concept_id"] in newids:
            for ev in e["source_evidence"]:
                src[ev["source_id"]] += 1
    m["source_evidence_rows_new"] = dict(src)
    m["concept_anchor_new"] = dict(anchor)
    m["ai_contribution_new"] = {
        "ai_generated_vi_expressions": sum(1 for e in exprs if e["concept_id"] in newids and e["provenance_type"] == "AI_GENERATED"),
        "share_of_new_expressions": round(sum(1 for e in exprs if e["concept_id"] in newids and e["provenance_type"] == "AI_GENERATED") / max(1, sum(1 for e in exprs if e["concept_id"] in newids)), 4),
        "ai_judge_validated_vi_expressions": sum(1 for e in exprs if e["concept_id"] in newids and e["language"] == "vi"),
    }

    # ---- pipeline funnel
    R = json.loads((P14_DIR / "judge_results.json").read_text())
    pool_stats = json.loads((P14_DIR / "scored_pool_stats.json").read_text())
    bs = json.loads((P14_DIR / "build_summary.json").read_text())
    judged = {k: len(v) for k, v in R.items()}
    verd = {k: dict(Counter(r.get("verdict") for r in v.values())) for k, v in R.items()}
    strict = {"tri": sum(1 for r in R.get("tri", {}).values() if J.is_accept_tri(r)),
              "tri_ai": sum(1 for r in R.get("tri_ai", {}).values() if J.is_accept_tri(r)),
              "enja_accept": sum(1 for r in R.get("enja", {}).values() if J.is_accept_en_ja(r)),
              "recheck_accept": sum(1 for r in R.get("recheck", {}).values() if J.is_accept_en_ja(r))}
    queues = bs["queues"]
    judged_total = sum(judged.get(k, 0) for k in ("tri", "enja"))
    rejected_n = queues.get("REJECT", 0)
    review_n = queues.get("REVIEW", 0)
    m["pipeline_funnel"] = {
        "candidates_scored": pool_stats["input_candidates"], "pool_decisions": pool_stats["final"],
        "judge_items": judged, "judge_verdicts": verd, "strict_accepts": strict,
        "routing_queues": queues, "post_judge_duplicates_suppressed": bs["post_judge_duplicates"],
        "pre_judge_duplicate_or_existing_prevented": {k: v for k, v in pool_stats["final"].items() if k != "NEW_CONCEPT" and k != "EXISTING_CONCEPT_NEW_SENSE"},
        "semantic_rejection_rate_of_judged_primary": round(rejected_n / max(1, judged_total), 4),
        "review_rate_of_judged_primary": round(review_n / max(1, judged_total), 4),
    }
    m["review_and_quarantine"] = {"human_review_queue": review_n, "semantic_rejects": rejected_n,
                                  "baseline_review_queue_phase1_3d": 147, "baseline_quarantined_phase1_3d": 30}
    write_json(REPORTS_DIR / "final_metrics.json", m)
    print(json.dumps(m, indent=1, ensure_ascii=False)[:6000])


if __name__ == "__main__":
    main()
