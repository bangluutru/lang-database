# Phase 1.4 (+1.4.1 remediation) Final Closure Report

**Headline:** corpus grew from 2,106 to **7,105** concepts — below the ~10,000 target, deliberately. Reaching 10,000 needed
AI-generated Vietnamese at scale or a lower semantic gate; external AI was stopped by the owner and the gate was not lowered.
Phase 1.4.1 then **corrected demonstrable Phase 1.3D defects** (see `baseline_remediation_report.md`).

```text
Baseline:                    a07f61e1f9d55da7ef5d06e6a8bd54f904fbd75c
Corpus before:               2,106 concepts
Corpus after:                7,105 concepts
Tri-language complete:       6,679  (baseline 1,721 + new 4,958)
Partial:                     426  (baseline 385 + new 41 judge-validated EN–JA, VI absent)
New concepts:                4,999   (175 candidates were absorbed by corrected baseline concepts instead of duplicating them)

JLPT N5/N4/N3/N2/N1:         431 / 359 / 1175 / 681 / 1091
CEFR A1/A2/B1/B2/C1/C2:      772 / 658 / 1098 / 1375 / 118 / 0  (C2: no open basis, none inferred)
Vietnamese Core 500/1000/2000/5000 (cumulative): 549 / 1062 / 1786 / 3013

Vietnamese provenance (per concept):  {"AI_GENERATED": 2607, "BENCHMARK_CURATED": 21, "CURATED": 223, "NO_VI": 426, "OFFICIAL_CURATED": 800, "SOURCE_DERIVED": 3028}
  (1.4 added 0 AI-generated VI; 1.4.1 added 60 agent-authored corrections, labelled AI_GENERATED)
Validation:                  {"needs_review/complete": 2288, "needs_review/partial": 274, "quarantined/partial": 2, "validated/complete": 4391, "validated/partial": 150}
Sources acquired:            wiktionary_en 2026-09-28 (CC-BY-SA-4.0). Reused: jmdict, kanjidic2, joyo, unihan, ngsl, ngsl_spoken, nawl, bsl, tsl, vn_freq, jlpt_consensus. Rejected: wordfreq (licence).
License audit:               PASS
Phase 1.3D frozen baseline:  PASS-WITH-DOCUMENTED-CORRECTIONS (sealed bytes exactly reconstructible by reverting the ledger)
Golden Pilot:                PASS
Professional 800:            PASS (untouched)
Tests:                       see reports/phase1_4/test_results.json (all passing at closure)
Final commit:                see `git tag phase1.4.2-closure` (reported in chat)
```

## 1. Phase 1.4 (expansion)
* Wiktionary sense blocks → JMdict corroboration → learning-value scoring → match-before-create → blind pairwise judge (gemini-2.5-pro) → append-only promotion with deterministic IDs.
* Judged primary candidates: semantic rejection 15.6%, review 9.1%.
* Learning views: `data/exports/views_v1_4/`; Oki deck regenerated.

## 2. Phase 1.4.1 (baseline remediation) — summary
Full detail: `reports/phase1_4/baseline_remediation_report.md`. 3,611 field-level ledger entries; 233 Japanese forms and
56 Vietnamese forms replaced, 133 POS fixes, 9 unfixable concepts flagged. Corrected concepts are `needs_review` (no independent validation).

## 2b. Phase 1.4.2 (independent hand-off to GPT 6 Luna, reviewed and committed by Claude)
50 work packages (T1 303 corrected baseline concepts, T2 9 flagged, T3 first ~300 review-queue candidates, T4 1,315 Vietnamese proposals) were done by Luna through a
file mailbox (`handoff/PROTOCOL.md`); Luna had no git, every packet was validated, sampled and committed by Claude (`data/phase1_4/handoff/review_log.jsonl`).
* **T1** verdicts {'ACCEPT': 280, 'REVISE': 23}: 280 corrected baseline concepts are now **validated by an independent model** (Luna ACCEPT/HIGH and unchanged since); Luna also exposed two of my own
  omissions (stale sense definitions; `import`/`girl` left inconsistent) which were fixed. 18 of Luna's revisions + 3 T2 answers were applied after Claude's review (`part6.tsv`).
* **T3** verdicts {'REVISE': 578, 'ACCEPT': 468, 'REJECT': 81}: Claude confirmed 332 Luna-ACCEPTs; 418 are in the corpus (status validated, basis `INDEPENDENT_AGENT_REVIEW`).
* **T4**: 2308 Vietnamese proposals (15 correctly left empty); Claude overrode/excluded 128 (5.5%) after reviewing every flagged item and ~10% of each packet.
  2247 Vietnamese expressions entered the corpus as `AI_GENERATED`, tier C, **`needs_review`** (proposer and Claude's review recorded; not independently judged).

## 3. Known limitations
* Below 10k; 41 new concepts are partial; ~14,500 lower-priority candidates unjudged.
* Domain packs IT / healthcare / travel are thin; no spoken-Vietnamese view; CEFR/EIKEN/TOEIC/IELTS/TOEFL are inferred.
* No external API was used after the owner's prohibition. T1-validated concepts are independently reviewed by Luna; the T4 Vietnamese proposals and all other corrected concepts are only partially reviewed (`needs_review`).
* The 150-concept sealed-baseline judge audit (49% strict accept) was **not re-run** after remediation (no API); deterministic indicators are compared instead.
