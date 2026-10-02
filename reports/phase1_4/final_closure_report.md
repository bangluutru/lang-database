# Phase 1.4 Final Closure Report — Curated Learning Corpus Expansion

**Headline: the corpus grew from 2,106 to 6,935 concepts — below the ~10,000 target. This is deliberate.**
Reaching 10,000 would have required (a) AI-generated Vietnamese at scale or (b) lowering the semantic gate. Neither was
done: external AI calls were stopped by the owner mid-phase (cost / policy), and the stop condition “reaching 10,000
requires lowering quality” applied. Every promoted concept passed a sense-level, blind, pairwise judgement.

```text
Baseline:                    a07f61e1f9d55da7ef5d06e6a8bd54f904fbd75c
Corpus before:               2,106 concepts
Corpus after:                6,935 concepts
Tri-language complete:       4,231  (baseline 1,717 + new 2,514)
Partial:                     2,704  (baseline 389 + new 2,315 judge-validated EN–JA, VI intentionally absent)
New concepts:                4,829

JLPT N5/N4/N3/N2/N1:         412 / 361 / 1188 / 677 / 1130
CEFR A1/A2/B1/B2/C1/C2:      821 / 681 / 1092 / 1355 / 111 / 0  (C2: no open basis, none inferred)
Vietnamese Core 500/1000/2000/5000 (cumulative): 403 / 754 / 1223 / 1981

Vietnamese provenance (per concept, whole corpus):
  SOURCE_DERIVED 2,872 | CURATED 251 | OFFICIAL_CURATED 800 | BENCHMARK_CURATED 21 | AI_GENERATED 287 (all from Phase 1.3D; Phase 1.4 added 0) | no VI 2,704
  (INFERRED applies to classifications only: CEFR / EIKEN / TOEIC / IELTS / TOEFL)
Validation:                  validated/complete 4,231 | validated/partial 2,315 | needs_review/partial 359 | quarantined/partial 30 (last two = sealed 1.3D, untouched)
Sources acquired:            wiktionary_en 2026-09-28 (CC-BY-SA-4.0). Reused: jmdict, kanjidic2, joyo, unihan, ngsl, ngsl_spoken, nawl, bsl, tsl, vn_freq, jlpt_consensus. Rejected: wordfreq (licence).
License audit:               PASS
Phase 1.3D frozen baseline:  PASS   (sealed byte-prefix of all canonical files verified)
Golden Pilot:                PASS
Professional 800:            PASS
Tests:                       passed 453 | failed 0 | skipped 0
Final commit:                see `git tag phase1.4-closure` (reported in chat)
```

## 1. What was built
* **Source:** Wiktionary (English edition, via Wiktextract) translation blocks give *sense-level* EN↔JA↔VI equivalence (the failure mode of 1.3C was headword/gloss matching). Each block is independently corroborated against JMdict (JA word must gloss the EN headword, POS compatible), scored for learning value from independent curriculum signals (NGSL family, JLPT, JMdict priority, vn_freq) and matched against the sealed graph before creation (match-before-create).
* **Gate:** blind pairwise judge (gemini-2.5-pro) — EN↔JA, EN↔VI, JA↔VI judged separately; strict accept requires every pair OK, natural, HIGH confidence. A bad VI never poisons a good EN–JA pair: it yields a *partial* concept.
* **Wave 2:** JMdict-anchored gap fill (JLPT / EN-list lemmas with no Wiktionary block). EN–JA only; anchor recorded as `jmdict`.
* **Append-only promotion** with deterministic IDs `concept-lex-<slug>-<pos>-<hash6>` (hash of EN lemma|POS|JMdict ent_seq:sense). Rebuilds are byte-identical (tested).
* **Views:** `data/exports/views_v1_4/` (JLPT N5–N1, Jōyō, daily/business JA; core/NGSL/CEFR/spoken/academic/EIKEN/TOEIC/IELTS/TOEFL EN; VI Core 500–5000 + a Vietnamese-first lexicon with its own frequency/POS/band; 12 domain packs) — projections, no duplicated concepts. Oki deck regenerated; baseline cards unchanged except additive classifications.

## 2. Evidence the pipeline is reliable (and selective)
Judged primary candidates: semantic rejection **16.1%**, human-review **13.2%**; canary (218 stratified) strict-accept 55%. Pre-judge, **3,125** candidates were stopped as duplicates / existing-concept matches (939 exact existing, 646 new-expression-of-existing, 1,540 in-batch duplicates). Post-judge duplicate suppression: 0 (no duplicate concept in the new corpus; tested).

## 3. Independent review (manual — no external API)
Because external API use was prohibited mid-phase, the planned third-model audit was replaced by a manual read of a deterministic stratified sample (86 records across frequency, JLPT, CEFR, VI-core, source-derived, polysemy, domain). Result: 80 OK, **6 borderline → moved to the review queue** (e.g. `length↔長短`, `matter↔こと/việc`, `cooperation↔協調`), 0 clearly wrong. Details: `reports/phase1_4/manual_review.json`. This is a smaller and less independent audit than planned; treat it as a sanity check, not certification.

## 4. Important discoveries
1. **The sealed baseline is weaker than its closure report implies.** A blind re-judgement of 150 sealed core concepts (read-only; nothing modified) gave only **49% strict accept**; 17% of EN–JA pairs judged WRONG (e.g. `act↔法律`, `actually` tagged as verb, `water↔水分`). Phase 1.3D’s own review queue already hints at this. Not changed (frozen rule); recommended as a dedicated remediation phase. `reports/phase1_4/baseline_defect_audit.json`.
2. **Lemma-level list membership must not be projected onto every sense** (`death`=Grim Reaper inherited CEFR A2). Fixed: lists project only onto core senses; non-core senses get half learning value.
3. **Wiktionary VI is useful but noisy**: ~40% of source VI forms failed the strict gate (4,635 judged, 2,749 strict accepts) (e.g. `mercenary→tay sai`, `fishing→ngư nghiệp`, `translation→phiên dịch` vs 翻訳).
4. **Rebuild feedback bug found & fixed**: match-before-create indexed Phase 1.4 output itself; now it indexes only the sealed baseline (determinism restored).
5. **Latent bugs:** JMdict `vi`/`vt` transitivity flags were treated as verb markers; capitalised headwords (`overseas Chinese`) were lowercased. Both fixed.
6. `ATTRIBUTION.md` stated JLPT data as CC0; the snapshot says CC-BY-3.0 — corrected.
7. Three tests were already failing at the sealed commit (stale pre-1.3D counts); fixed as stale tests and 1.3D hard-coded totals converted to baseline-subset invariants.

## 5. Known limitations / honest gaps
* Size: 6,935, not ~10,000. Of the new concepts 2,315 are partial (EN–JA validated, VI absent): the AI route that would have completed them was stopped. Cached-but-unused AI proposals are kept in `data/phase1_4/deferred/` and `data/ai/phase1_4/gen_vi/` (NOT in canonical).
* ~14,500 lower-priority candidates were never judged (UNJUDGED) and are not in the corpus.
* Domain packs for IT, healthcare, travel are thin (Wiktionary topic tags and JMdict fields are sparse); business/daily_life/science are stronger.
* No spoken-Vietnamese view: vn_freq cannot separate spoken from written. Vietnamese Core bands cover only translatable concepts (see `vi_core_lemma_coverage`).
* CEFR/EIKEN/TOEIC/IELTS/TOEFL are inferred from open lists and labelled INFERRED; JLPT stays community-consensus (CC-BY-3.0).
* Synonym expressions (multiple per language) were not added in 1.4 (unjudged).
* Cost note: ~953 gemini-2.5-pro and 132 gemini-2.5-flash calls were made before the owner prohibited external APIs (est. 25–90 USD; see chat). From then on: zero calls; guard added (`CLAUDE.md`, `AGENTS.md`, `scripts/external_api_guard.py`, `tests/test_external_api_policy.py`).

## 6. Generated metrics appendix


### Funnel (machine-generated)
 and gate behaviour (evidence that quality — not the 10k target — drove the result)

{
 "candidates_scored": 42792,
 "judge_items": {
  "enja": 4099,
  "recheck": 1030,
  "tri": 4635,
  "tri_ai": 0
 },
 "judge_verdicts": {
  "enja": {
   "ACCEPT": 2968,
   "REJECT": 581,
   "REVIEW": 550
  },
  "recheck": {
   "ACCEPT": 825,
   "REJECT": 77,
   "REVIEW": 128
  },
  "tri": {
   "ACCEPT": 2819,
   "REJECT": 1087,
   "REVIEW": 729
  },
  "tri_ai": {}
 },
 "pool_decisions": {
  "DUPLICATE_IN_BATCH": 1540,
  "EXACT_EXISTING_CONCEPT": 939,
  "EXISTING_CONCEPT_NEW_EXPRESSION": 646,
  "EXISTING_CONCEPT_NEW_SENSE": 2199,
  "NEW_CONCEPT": 20831
 },
 "post_judge_duplicates_suppressed": 0,
 "pre_judge_duplicate_or_existing_prevented": {
  "DUPLICATE_IN_BATCH": 1540,
  "EXACT_EXISTING_CONCEPT": 939,
  "EXISTING_CONCEPT_NEW_EXPRESSION": 646
 },
 "review_rate_of_judged_primary": 0.1319,
 "routing_queues": {
  "ACCEPT_PARTIAL_ENJA": 2315,
  "ACCEPT_TRI_AI": 0,
  "ACCEPT_TRI_SOURCE": 2514,
  "BELOW_VALUE_THRESHOLD": 1141,
  "REJECT": 1402,
  "REVIEW": 1152,
  "UNJUDGED": 14506
 },
 "semantic_rejection_rate_of_judged_primary": 0.1605,
 "strict_accepts": {
  "enja_accept": 3073,
  "recheck_accept": 866,
  "tri": 2749,
  "tri_ai": 0
 }
}

* Semantic rejection rate of judged primary candidates: **16.1%**; human-review rate: **13.2%**.
* AI-generated Vietnamese share of new expressions: **0.0%** (0 expressions) — all keep `provenance_type = AI_GENERATED`.

## 2. Independent linguistic review (manual, no external API)

{
 "reviewer": "Claude (coding agent, manual read; no external API)",
 "sample_size": 86,
 "ok": 80,
 "review": 6,
 "wrong": 0,
 "also_found": [
  "lemma-level list classifications were projected onto rare senses (death=Grim Reaper -> CEFR A2); fixed by core-sense rule before final build"
 ]
}

### Sealed-baseline spot audit (read-only, nothing modified)

{
 "note": "Sealed baseline is NOT modified; defects are reported only.",
 "pair_verdicts": {
  "en_ja:BROAD": 6,
  "en_ja:NARROW": 9,
  "en_ja:OK": 110,
  "en_ja:WRONG": 25,
  "en_vi:BROAD": 9,
  "en_vi:NARROW": 13,
  "en_vi:OK": 98,
  "en_vi:WRONG": 30,
  "ja_vi:BROAD": 8,
  "ja_vi:NARROW": 8,
  "ja_vi:OK": 97,
  "ja_vi:WRONG": 37
 },
 "sample": 150,
 "strict_accept": 74,
 "strict_accept_rate": 0.493
}

## 3. Other metrics

{
 "language_coverage_concepts": {
  "en": 6935,
  "ja": 6935,
  "vi": 4231
 },
 "frequency_bands_new_concepts": {
  "learning_value": {
   "10-19": 716,
   "20-29": 535,
   "30-44": 1396,
   "45-59": 1112,
   "60+": 1070
  },
  "ngsl_rank": {
   "<=1000": 394,
   "<=2000": 638,
   "<=2809": 342,
   "<=500": 522
  },
  "no_ngsl_rank": 2933,
  "no_vn_freq_rank": 2712,
  "vn_freq_rank": {
   "<=1000": 179,
   "<=10000": 497,
   "<=2000": 313,
   "<=500": 215,
   "<=5000": 584,
   ">10000": 329
  }
 },
 "by_domain_all_concepts": {
  "accounting": 203,
  "action": 1,
  "banking": 1,
  "bookkeeping": 200,
  "business": 758,
  "commerce": 2,
  "contracts": 200,
  "corporate_reporting": 200,
  "corporate_tax": 200,
  "customs": 200,
  "daily_life": 3241,
  "education": 366,
  "finance": 225,
  "general": 6116,
  "geography": 2,
  "government": 2,
  "healthcare": 100,
  "income_tax": 200,
  "international_business": 200,
  "it": 50,
  "legal": 4,
  "logic": 3,
  "logistics": 210,
  "management": 201,
  "manufacturing": 70,
  "media": 1,
  "nature": 1,
  "office_communication": 200,
  "organization": 1,
  "psychology": 1,
  "publishing": 1,
  "science": 378,
  "society": 4,
  "spatial": 1,
  "tax": 200,
  "tax_compliance": 200,
  "technology": 1,
  "trade": 201,
  "travel": 16
 },
 "quality_tiers_new": {
  "Tier B": 2514,
  "Tier D": 2315
 },
 "source_evidence_rows_new": {
  "bsl": 500,
  "jmdict": 6074,
  "nawl": 360,
  "ngsl": 1896,
  "ngsl_spoken": 713,
  "tsl": 450,
  "vn_freq": 2117,
  "wiktionary_en": 9682
 },
 "concept_anchor_new": {
  "jmdict": 1245,
  "wiktionary": 3584
 },
 "vi_core_lemma_coverage": {
  "note": "top-N vn_freq lists include many function words/particles/proper names that are not translatable concepts, so <100% coverage is expected; the metric tracks progress only.",
  "top1000": {
   "covered_by_a_corpus_VI_lemma": 563,
   "words": 1000
  },
  "top2000": {
   "covered_by_a_corpus_VI_lemma": 977,
   "words": 2000
  },
  "top500": {
   "covered_by_a_corpus_VI_lemma": 285,
   "words": 500
  },
  "top5000": {
   "covered_by_a_corpus_VI_lemma": 1729,
   "words": 5000
  }
 },
 "classification_provenance": {
  "BENCHMARK_CURATED": 18,
  "INFERRED": 9511,
  "SOURCE_DERIVED": 16813,
  "legacy_schema": 867
 },
 "review_and_quarantine": {
  "baseline_quarantined_phase1_3d": 30,
  "baseline_review_queue_phase1_3d": 147,
  "human_review_queue": 1152,
  "semantic_rejects": 1402
 }
}
