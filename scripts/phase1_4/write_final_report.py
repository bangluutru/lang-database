#!/usr/bin/env python3
"""Renders reports/phase1_4/final_closure_report.md and baseline_remediation_report.md from the metrics files."""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from scripts.phase1_4.common import REPORTS_DIR, BASELINE_SHA

def J(n): return json.loads((REPORTS_DIR / n).read_text())

def main():
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
Tests:                       see reports/phase1_4/test_results.json
Final commit:                see `git tag phase1.4.1-closure` (reported in chat)
```

## 1. Phase 1.4 (expansion)
* Wiktionary sense blocks → JMdict corroboration → learning-value scoring → match-before-create → blind pairwise judge (gemini-2.5-pro) → append-only promotion with deterministic IDs.
* Judged primary candidates: semantic rejection {f['semantic_rejection_rate_of_judged_primary']:.1%}, review {f['review_rate_of_judged_primary']:.1%}.
* Learning views: `data/exports/views_v1_4/`; Oki deck regenerated.

## 2. Phase 1.4.1 (baseline remediation) — summary
Full detail: `reports/phase1_4/baseline_remediation_report.md`. {rm['ledger_entries']:,} field-level ledger entries; {led.get('fix_ja',0)} Japanese forms and
{led.get('fix_vi',0)} Vietnamese forms replaced, {led.get('fix_pos',0)} POS fixes, {led.get('flagged',0)} unfixable concepts flagged. Corrected concepts are `needs_review` (no independent validation).

## 3. Known limitations
* Below 10k; {c['partial_new']:,} new concepts are partial; ~14,500 lower-priority candidates unjudged.
* Domain packs IT / healthcare / travel are thin; no spoken-Vietnamese view; CEFR/EIKEN/TOEIC/IELTS/TOEFL are inferred.
* No external API was used after the owner's prohibition: the remediation is agent-reviewed, not model-judged; independent validation of corrections is outstanding.
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
