# Phase 1.4 (+1.4.1 remediation) Final Closure Report

**Headline:** corpus grew from 2,106 to **6,760** concepts — below the ~10,000 target, deliberately. Reaching 10,000 needed
AI-generated Vietnamese at scale or a lower semantic gate; external AI was stopped by the owner and the gate was not lowered.
Phase 1.4.1 then **corrected demonstrable Phase 1.3D defects** (see `baseline_remediation_report.md`).

```text
Baseline:                    a07f61e1f9d55da7ef5d06e6a8bd54f904fbd75c
Corpus before:               2,106 concepts
Corpus after:                6,760 concepts
Tri-language complete:       4,149  (baseline 1,721 + new 2,428)
Partial:                     2,611  (baseline 385 + new 2,226 judge-validated EN–JA, VI absent)
New concepts:                4,654   (175 candidates were absorbed by corrected baseline concepts instead of duplicating them)

JLPT N5/N4/N3/N2/N1:         421 / 354 / 1139 / 651 / 1066
CEFR A1/A2/B1/B2/C1/C2:      761 / 652 / 1070 / 1336 / 111 / 0  (C2: no open basis, none inferred)
Vietnamese Core 500/1000/2000/5000 (cumulative): 372 / 707 / 1167 / 1911

Vietnamese provenance (per concept):  {"AI_GENERATED": 331, "BENCHMARK_CURATED": 21, "CURATED": 227, "NO_VI": 2611, "OFFICIAL_CURATED": 800, "SOURCE_DERIVED": 2770}
  (1.4 added 0 AI-generated VI; 1.4.1 added 60 agent-authored corrections, labelled AI_GENERATED)
Validation:                  {"needs_review/complete": 185, "needs_review/partial": 333, "quarantined/partial": 2, "validated/complete": 3964, "validated/partial": 2276}
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
* Judged primary candidates: semantic rejection 15.6%, review 12.9%.
* Learning views: `data/exports/views_v1_4/`; Oki deck regenerated.

## 2. Phase 1.4.1 (baseline remediation) — summary
Full detail: `reports/phase1_4/baseline_remediation_report.md`. 3,387 field-level ledger entries; 233 Japanese forms and
56 Vietnamese forms replaced, 133 POS fixes, 9 unfixable concepts flagged. Corrected concepts are `needs_review` (no independent validation).

## 3. Known limitations
* Below 10k; 2,226 new concepts are partial; ~14,500 lower-priority candidates unjudged.
* Domain packs IT / healthcare / travel are thin; no spoken-Vietnamese view; CEFR/EIKEN/TOEIC/IELTS/TOEFL are inferred.
* No external API was used after the owner's prohibition: the remediation is agent-reviewed, not model-judged; independent validation of corrections is outstanding.
* The 150-concept sealed-baseline judge audit (49% strict accept) was **not re-run** after remediation (no API); deterministic indicators are compared instead.
