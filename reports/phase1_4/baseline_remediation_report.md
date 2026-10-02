# Phase 1.4.1 — Baseline (Phase 1.3D) Defect Remediation Report

## Trigger
Phase 1.4 re-judged 150 sealed core concepts: only **49%** strict accept; ~17% of EN–JA pairs WRONG
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
| Japanese expression replaced (JMdict-verified) | 233 |
| Vietnamese expression replaced / added (AI_GENERATED, agent-authored) | 56 / 4 |
| Part-of-speech corrected (e.g. adverbs tagged as verbs) | 133 |
| Concepts flagged unfixable (needs_review) | 9 |
| Vietnamese synonyms retracted (they described the replaced form) | 11 |
| Derived classifications retracted (JLPT/Jōyō/VI-core of replaced forms) | 339 |
| Field-level ledger entries | 3,387 |

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
| EN POS incompatible with the JMdict sense of the JA form | 75 | 12 |
| -ly adverbs not tagged adverb | 31 | 0 |
| JA whose JMdict sense does not gloss the EN lemma | 0 | 9 (8 labelled overrides + 1) |
| JA without JMdict evidence (curated daily list; manually reviewed) | 410 | 399 |

## NOT done / honest caveats
* The remediation is **agent-reviewed, not independently validated**; the judge audit was not re-run (external API prohibited). Corrected concepts need a human or independent-model pass.
* The review fixed *clear* errors only. BROAD/NARROW nuance (e.g. `hard`↔khó, `athlete`↔tuyển thủ, `region`↔địa phương) was left as is.
* ~399 core concepts keep a curated JA without JMdict evidence; they passed manual reading but are not source-verified.
* 12 residual POS mismatches and 9 flagged concepts remain in `needs_review`.
