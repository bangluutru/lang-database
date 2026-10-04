#!/usr/bin/env python3
"""Renders reports/phase1_4/final_closure_report.md and baseline_remediation_report.md from the metrics files."""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from scripts.phase1_4.common import REPORTS_DIR, BASELINE_SHA

def J(n): return json.loads((REPORTS_DIR / n).read_text())

def handoff_stats():
    import glob
    from collections import Counter
    HO = REPORTS_DIR.parent.parent / "data/phase1_4/handoff"
    def dec(t):
        out = []
        for p in sorted(glob.glob(str(HO / f"decisions/{t}_*.jsonl"))):
            out += [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]
        return out
    t1, t2, t3, t4 = dec("T1"), dec("T2"), dec("T3"), dec("T4")
    ov = json.loads((HO / "claude_overrides_T4.json").read_text())["overrides"]
    acc = json.loads((HO / "claude_review_T3.json").read_text())["accepted"]
    vo = json.loads((HO.parent / "validation_overrides.json").read_text())
    cons = [json.loads(l) for l in open(REPORTS_DIR.parent.parent / "data/canonical/concepts.jsonl", encoding="utf-8")]
    exs = [json.loads(l) for l in open(REPORTS_DIR.parent.parent / "data/canonical/expressions.jsonl", encoding="utf-8")]
    from collections import defaultdict
    gem_g3 = [c for c in cons if (c.get("metadata") or {}).get("independent_review", {}).get("reviewers", [None])[0] == "gemini-3.8" and not (c.get("metadata") or {}).get("authored")]
    a1 = [c for c in cons if (c.get("metadata") or {}).get("authored")]
    a1_dom = dict(Counter(c["primary_domain"] for c in a1))
    rl = [json.loads(l) for l in open(HO / "review_log.jsonl", encoding="utf-8") if l.strip()]
    def gem(prefix):
        return [r for r in rl if r["task_id"].startswith(prefix)]
    a1_log = gem("A1_")
    a1_slots = sum(1 for p in sorted(glob.glob(str(HO / "packets/A1_*.jsonl"))) for l in open(p, encoding="utf-8") if l.strip())
    g_stats = {"G3_promoted": len(gem_g3), "A1_concepts": len(a1), "A1_by_domain": a1_dom, "A1_slots_assigned_incl_rework": a1_slots,
               "G_tasks_reviewed": len([r for r in rl if r["task_id"][:2] in ("G3", "G4", "A1") or r["task_id"] == "T4_059"]),
               "T4_059_in_corpus": sum(1 for e in exs if e["language"] == "vi" and e["provenance_type"] == "AI_GENERATED" and e["source_evidence"][0].get("model") == "gemini-3.8" and e["concept_id"] not in {c["concept_id"] for c in a1})}
    return {"GEMINI": g_stats, "T1": dict(Counter(d["verdict"] for d in t1)), "T2": dict(Counter(d["verdict"] for d in t2)), "T3": dict(Counter(d["verdict"] for d in t3)),
            "T4_items": len(t4), "T4_null": sum(1 for d in t4 if d.get("vi_lemma") is None), "claude_T4_overrides": len(ov),
            "T3_claude_confirmed": len(acc), "T3_promoted_in_corpus": sum(1 for c in cons if (c.get("metadata") or {}).get("independent_review")),
            "T1_validated_by_independent_review": len(vo),
            "T4_vi_in_corpus": sum(1 for e in exs if e["language"] == "vi" and e["provenance_type"] == "AI_GENERATED" and e["source_evidence"][0].get("model") in ("gpt-6-luna", "claude-sonnet-5-5", "gemini-3.8"))}


def main():
    hs = handoff_stats()
    m, rm, ba = J("final_metrics.json"), J("baseline_remediation_metrics.json"), J("baseline_defect_audit.json")["summary"]
    c, cl, f, vd = m["corpus"], m["by_classification"], m["pipeline_funnel"], m["validation_distribution"]
    led = rm["ledger_stats"]
    b, a = rm["before"], rm["after"]
    final = f"""# Phase 1.4 (+1.4.1 remediation) Final Closure Report

**Headline:** corpus grew from 2,106 to **{c['total_concepts']:,}** concepts — below the ~10,000 target, deliberately. Reaching 10,000 needed
AI-generated Vietnamese at scale or a lower semantic gate; external AI was stopped by the owner and the gate was not lowered.
Phase 1.4.1 then **corrected demonstrable Phase 1.3D defects** (see `baseline_remediation_report.md`).

```text
Baseline:                    {BASELINE_SHA}
Corpus before:               2,106 concepts
Corpus after:                {c['total_concepts']:,} concepts
Tri-language complete:       {c['tri_language_complete']:,}  (baseline {c['tri_language_complete_baseline']:,} + new {c['tri_language_complete_new']:,})
Partial:                     {c['partial']:,}  (baseline {c['partial']-c['partial_new']:,} + new {c['partial_new']:,} judge-validated EN–JA, VI absent)
New concepts:                {c['new_concepts']:,}   (175 candidates were absorbed by corrected baseline concepts instead of duplicating them)

JLPT N5/N4/N3/N2/N1:         {cl['JLPT']['N5']} / {cl['JLPT']['N4']} / {cl['JLPT']['N3']} / {cl['JLPT']['N2']} / {cl['JLPT']['N1']}
CEFR A1/A2/B1/B2/C1/C2:      {cl['CEFR']['A1']} / {cl['CEFR']['A2']} / {cl['CEFR']['B1']} / {cl['CEFR']['B2']} / {cl['CEFR']['C1']} / {cl['CEFR']['C2']}  (C2: no open basis, none inferred)
Vietnamese Core 500/1000/2000/5000 (cumulative): {cl['VI_CORE_cumulative']['Core 500']} / {cl['VI_CORE_cumulative']['Core 1000']} / {cl['VI_CORE_cumulative']['Core 2000']} / {cl['VI_CORE_cumulative']['Core 5000']}

Vietnamese provenance (per concept):  {json.dumps(m['concept_vi_provenance_all'], ensure_ascii=False)}
  (1.4 added 0 AI-generated VI; 1.4.1 added {led.get('fix_vi',0)+led.get('vi_added',0)} agent-authored corrections, labelled AI_GENERATED)
Validation:                  {json.dumps(vd, ensure_ascii=False)}
Sources acquired:            wiktionary_en 2026-09-28 (CC-BY-SA-4.0). Reused: jmdict, kanjidic2, joyo, unihan, ngsl, ngsl_spoken, nawl, bsl, tsl, vn_freq, jlpt_consensus. Rejected: wordfreq (licence).
License audit:               PASS
Phase 1.3D frozen baseline:  PASS-WITH-DOCUMENTED-CORRECTIONS (sealed bytes exactly reconstructible by reverting the ledger)
Golden Pilot:                PASS
Professional 800:            PASS (untouched)
Tests:                       see reports/phase1_4/test_results.json (all passing at closure)
Final commit:                see `git tag phase1.4.4-closure` (reported in chat)
```

## 1. Phase 1.4 (expansion)
* Wiktionary sense blocks → JMdict corroboration → learning-value scoring → match-before-create → blind pairwise judge (gemini-2.5-pro) → append-only promotion with deterministic IDs.
* Judged primary candidates: semantic rejection {f['semantic_rejection_rate_of_judged_primary']:.1%}, review {f['review_rate_of_judged_primary']:.1%}.
* Learning views: `data/exports/views_v1_4/`; Oki deck regenerated.

## 2. Phase 1.4.1 (baseline remediation) — summary
Full detail: `reports/phase1_4/baseline_remediation_report.md`. {rm['ledger_entries']:,} field-level ledger entries; {led.get('fix_ja',0)} Japanese forms and
{led.get('fix_vi',0)} Vietnamese forms replaced, {led.get('fix_pos',0)} POS fixes, {led.get('flagged',0)} unfixable concepts flagged. Corrected concepts are `needs_review` (no independent validation).

## 2b. Phase 1.4.2 (independent hand-off to GPT 6 Luna, reviewed and committed by Claude)
50 work packages (T1 303 corrected baseline concepts, T2 9 flagged, T3 first ~300 review-queue candidates, T4 1,315 Vietnamese proposals) were done by Luna through a
file mailbox (`handoff/PROTOCOL.md`); Luna had no git, every packet was validated, sampled and committed by Claude (`data/phase1_4/handoff/review_log.jsonl`).
* **T1** verdicts {hs['T1']}: {hs['T1_validated_by_independent_review']} corrected baseline concepts are now **validated by an independent model** (Luna ACCEPT/HIGH and unchanged since); Luna also exposed two of my own
  omissions (stale sense definitions; `import`/`girl` left inconsistent) which were fixed. 18 of Luna's revisions + 3 T2 answers were applied after Claude's review (`part6.tsv`).
* **T3** verdicts {hs['T3']}: Claude confirmed {hs['T3_claude_confirmed']} Luna-ACCEPTs; {hs['T3_promoted_in_corpus']} are in the corpus (status validated, basis `INDEPENDENT_AGENT_REVIEW`).
* **T4**: {hs['T4_items']} Vietnamese proposals ({hs['T4_null']} correctly left empty); Claude overrode/excluded {hs['claude_T4_overrides']} ({hs['claude_T4_overrides']/hs['T4_items']:.1%}) after reviewing every flagged item and ~10% of each packet.
  {hs['T4_vi_in_corpus']} Vietnamese expressions entered the corpus as `AI_GENERATED`, tier C, **`needs_review`** (proposer and Claude's review recorded; not independently judged).

## 2c. Phase 1.4.4 (pilot: Gemini 3.8 in Antigravity as a second worker, reviewed and committed by Claude)
Gemini 3.8 worked through the same file mailbox under stricter written rules (`docs/handoff/GEMINI_HANDOFF.md`, Parts A-I; mechanical gates in
`scripts/handoff/gemini_selfcheck.py` and `validate_authored.py`). It never had git; nothing was committed or pushed before Claude's review passed.
* **Calibration packets** (T4 re-check G4_001/002, T3-style G3_001): Gemini blocked all 10 known-bad promotions in G3_001; after rule changes, G4_002 had no wrong HIGH answers.
* **T4 pilot**: {hs['GEMINI']['T4_059_in_corpus']} Vietnamese proposals (T4_059) integrated, 4 corrected by Claude.
* **G3 promotion review** (91 never-judged candidates, value >= 30): {hs['GEMINI']['G3_promoted']} Gemini ACCEPT(HIGH) entries confirmed by Claude and promoted (`claude_review_G3.json`, basis `G3_handoff_review`).
* **A1 authoring of NEW concepts** for thin packs: {hs['GEMINI']['A1_concepts']} concepts {json.dumps(hs['GEMINI']['A1_by_domain'])} (JMdict-anchored EN-JA pair, AI_GENERATED definition/Vietnamese/examples, `needs_review`, Tier C),
  from {hs['GEMINI']['A1_slots_assigned_incl_rework']} slots including rework slots; every entry read individually by Claude, PASS or reworked to PASS (`claude_review_A1.json`).
* Main lessons: ceiling-by-evidence blocks over-confidence only partly (about 9-14% of HIGH claims were still wrong or too high); typical defects were Vietnamese scope narrower/broader than the sense,
  abstract-vs-concrete pairs (記念 vs souvenir), spelling (`công ti`), acronym case, and clumsy example sentences. All were caught in review and recorded in Part I11.

## 3. Known limitations
* Below 10k; {c['partial_new']:,} new concepts are partial; ~14,500 lower-priority candidates unjudged.
* Domain packs IT / healthcare / travel / manufacturing are still small (A1 added 94 Gemini-authored concepts); no spoken-Vietnamese view; CEFR/EIKEN/TOEIC/IELTS/TOEFL are inferred.
* No external API was used after the owner's prohibition. T1-validated concepts are independently reviewed by Luna; the T4 Vietnamese proposals and all other corrected concepts are only partially reviewed (`needs_review`).
* The 150-concept sealed-baseline judge audit (49% strict accept) was **not re-run** after remediation (no API); deterministic indicators are compared instead.
"""
    (REPORTS_DIR / "final_closure_report.md").write_text(final, encoding="utf-8")
    rem = f"""# Phase 1.4.1 — Baseline (Phase 1.3D) Defect Remediation Report

## Trigger
Phase 1.4 re-judged 150 sealed core concepts: only **{ba['strict_accept_rate']:.0%}** strict accept; ~17% of EN–JA pairs WRONG
(`reports/phase1_4/baseline_defect_audit.json`). The owner asked to fix the discovered defects.

## Method (no external API)
1. **Full manual review** by the coding agent of all 1,306 baseline core/poly concepts (EN | POS | JA(reading) | VI) — professional-800 and Golden Pilot excluded.
2. A hand-authored fix table (`data/phase1_4/baseline_fixes/part1..5.tsv`) proposes a replacement; every Japanese form is then **machine-verified against JMdict**
   (the cited sense must gloss the English lemma, POS compatible; ties broken by JMdict commonness). Proposals that fail verification are not applied.
   Eight `!` overrides (e.g. 決して for *never*, whose JMdict gloss is “(not) ever”) are labelled `gloss_override` in the record.
3. Replacement Vietnamese was written by the agent ⇒ `provenance_type = AI_GENERATED`, validation `AGENT_REVIEWED_NOT_INDEPENDENT`. It is never labelled source-derived.
4. Cases with no verifiable replacement (cost, false, fit, inspire, manner, critical, vital, attachment, actual) are **flagged**, not guessed.

## What changed (all recorded in `reports/phase1_4/baseline_corrections_ledger.json`)
| Change | Count |
|---|---|
| Japanese expression replaced (JMdict-verified) | {led.get('fix_ja',0)} |
| Vietnamese expression replaced / added (AI_GENERATED, agent-authored) | {led.get('fix_vi',0)} / {led.get('vi_added',0)} |
| Part-of-speech corrected (e.g. adverbs tagged as verbs) | {led.get('fix_pos',0)} |
| Concepts flagged unfixable (needs_review) | {led.get('flagged',0)} |
| Vietnamese synonyms retracted (they described the replaced form) | {led.get('synonyms_retracted',0)} |
| Derived classifications retracted (JLPT/Jōyō/VI-core of replaced forms) | {led.get('classifications_retracted',0)} |
| Field-level ledger entries | {rm['ledger_entries']:,} |

Examples: `husband` お父さん→夫, `today` 現代→今日, `eat` 遣る→食べる, `world` 園→世界, `blue` ピンク→青い, `boy` もう→少年, `child` 砂利→子供,
`dog` スベタ(slur)→犬, `act` 法律→演じる, `well/say` あの→よく/言う, `water` 水分→水, `cat` reading ねこま→ねこ, `front` ぜん→まえ.

## Guarantees kept
* IDs never change; no record deleted; the sealed prefix keeps its line counts.
* **Reversible:** reverting the ledger reproduces the sealed Phase 1.3D SHA-256 of concepts/senses/expressions/classifications byte-for-byte (`tests/test_phase1_4_1.py`, `tests/test_phase1_3d.py::test_25`).
* Professional 800, Golden Pilot, legacy mapping: untouched.
* Every corrected concept is `needs_review` (POS-only fixes stay `validated`) and `production_ready=false` in the Oki export; retracted classification/expression rows are excluded from decks and views.
* Match-before-create now indexes the corrected baseline, so 175 Phase 1.4 candidates that previously duplicated defective baseline concepts were absorbed.

## Before / after (deterministic detector on 1,285 core concepts)
| Indicator | Before | After |
|---|---|---|
| EN POS incompatible with the JMdict sense of the JA form | {b['pos_mismatch']} | {a['pos_mismatch']} |
| -ly adverbs not tagged adverb | {b['ly_adverbs_not_tagged_adverb']} | {a['ly_adverbs_not_tagged_adverb']} |
| JA whose JMdict sense does not gloss the EN lemma | {b.get('jm_gloss_missing',0)} | {a.get('jm_gloss_missing',0)} (8 labelled overrides + 1) |
| JA without JMdict evidence (curated daily list; manually reviewed) | {b['ja_without_jmdict_evidence']} | {a['ja_without_jmdict_evidence']} |

## NOT done / honest caveats
* The remediation is **agent-reviewed, not independently validated**; the judge audit was not re-run (external API prohibited). Corrected concepts need a human or independent-model pass.
* The review fixed *clear* errors only. BROAD/NARROW nuance (e.g. `hard`↔khó, `athlete`↔tuyển thủ, `region`↔địa phương) was left as is.
* ~399 core concepts keep a curated JA without JMdict evidence; they passed manual reading but are not source-verified.
* 12 residual POS mismatches and 9 flagged concepts remain in `needs_review`.
"""
    (REPORTS_DIR / "baseline_remediation_report.md").write_text(rem, encoding="utf-8")
    print("ok")

if __name__ == "__main__":
    main()
