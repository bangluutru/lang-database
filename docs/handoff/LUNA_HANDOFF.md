# Handoff to GPT 6 Luna — independent validation & Vietnamese completion

Audience: **GPT 6 Luna** acting as a coding/review agent in this repository. Reviewer of your work: **Claude** (and the owner).
Read this whole file, then `CLAUDE.md`, then start with Task T1. Do not skip the rules in §1.

## 0. Why you are being asked
Phase 1.4/1.4.1 built a 6,760-concept EN–JA–VI learning corpus. Claude authored the baseline corrections itself, so they have
**no independent validation**. You are a different model: your independent judgement is exactly what is missing. Your decisions
are the *validation* dimension; they never change where a lexical form came from (its *provenance*).

## 1. Hard rules (violating any = stop and report)
1. **No external or paid API calls. Ever.** You are the LLM: read the packet, decide, write the file. Do not call Vertex/Gemini/OpenAI/Anthropic/any hosted model,
   do not set `LANGDB_ALLOW_EXTERNAL_API`, do not touch `scripts/external_api_guard.py`. Free downloads are also out of scope for these tasks.
2. **Never edit** `data/canonical/*.jsonl`, `data/production/`, `data/releases/**`, `reports/phase1_4/baseline_corrections_ledger.json`,
   `data/raw/**`. Your outputs go only to `data/phase1_4/handoff/decisions/` (and the code/tests listed in §6).
3. **Provenance is sacred.** Anything *you* write (a Vietnamese proposal, a revision) is `AI_GENERATED` with reviewer label `gpt-6-luna`. Never describe your output as source-derived.
4. **Semantic correctness beats completion.** "REJECT" and "LOW confidence" are good answers. Do not force a tri-language pair. Do not pad to hit counts.
5. Work offline from the packets + the lookup tool. Do not invent dictionary facts; verify with `lookup.py` (§3).
6. Do not run the full test suite repeatedly or rebuild the corpus unless a task in §6 tells you to. Commit only what §7 lists.

## 2. Orientation (5 minutes)
* Model: **Concept → Sense → Expression** (EN, JA, VI). One *sense* per concept; polysemous words are separate concepts. Judge the **stated sense**, not the word in general.
* Packets: `data/phase1_4/handoff/packets/{T1,T2,T3,T4}_NNN.jsonl` (40 items each; index in `../packet_index.json`). Regenerate with
  `python scripts/phase1_4/handoff/make_packets.py` (deterministic; do not edit packets).
* Your output: `data/phase1_4/handoff/decisions/<same file name>` — **one JSON line per packet item, same order, same count**.
* Format gate (run after every file): `python scripts/phase1_4/handoff/validate_decisions.py data/phase1_4/handoff/decisions/T1_001.jsonl`

## 3. Verification tool (offline)
```bash
python scripts/phase1_4/handoff/lookup.py ja 猫        # JMdict: ent_seq, sense, POS tags, glosses, priority
python scripts/phase1_4/handoff/lookup.py en cat       # reverse: which Japanese words JMdict glosses as "cat"
python scripts/phase1_4/handoff/lookup.py vi "sân bay" # Vietnamese corpus frequency (rank/POS); absence is not proof of error
python scripts/phase1_4/handoff/lookup.py wikt airport # Wiktionary EN extract: senses with JA/VI translations
```

## 4. Linguistic standard (apply to every item)
Judge each **pair** separately — EN↔JA, EN↔VI, JA↔VI — with: `OK` (a competent translator would use this), `BROAD` (target covers more than the sense),
`NARROW` (covers only part), `WRONG` (different meaning/false friend/wrong POS), `NA` (no VI present).
* **Sense-specific.** `bank` (finance) ≠ `bank` (river). `right` has several concepts. If the target only fits another sense → WRONG, not OK.
* **POS must be compatible** across the three (noun↔noun, adverb↔adverb). A Japanese noun glossing an English verb is a POS mismatch unless it is a する-noun used verbally.
* **Naturalness:** prefer the everyday, current, standard word a learner should be taught. Penalise archaic, rare-kanji, honorific/humble-only (e.g. 伺う for "ask"), slang, offensive, dialect-only forms.
* **Register:** neutral stays neutral. A slur or vulgar word standing for a neutral English noun is WRONG.
* **Vietnamese:** natural modern word, correct diacritics, lower-case, 1–4 words. Hán–Việt forms are fine only if they are the normal modern word for *this* sense
  (watch false friends: `bất minh` ≠ "unclear"; `chức nghiệp` is archaic for "career"; `phiên dịch` = interpreting, not written translation).
* **Strictness:** ACCEPT only if every pair is OK and you are HIGH confidence. Borderline = REVISE or REJECT with a precise reason. A near-miss with a clearly better word → REVISE.

## 5. Tasks

### T1 — Independent validation of 303 corrected baseline concepts (8 packets). **Do this first.**
Each item shows the *current* corrected pair (`ja`, `vi`, `pos`), JMdict glosses, the English sense, and `changed.previous_lemmas` (what was there before).
Output per item (`task":"T1"`):
```json
{"task":"T1","id":"concept-core-husband","reviewer":"gpt-6-luna","verdict":"ACCEPT","en_ja":"OK","en_vi":"OK","ja_vi":"OK","naturalness":"NATURAL","confidence":"HIGH","revision":null,"note":"夫 is the standard word for a woman's/man's husband; chồng is the normal Vietnamese equivalent."}
```
* `ACCEPT` — all pairs OK/NA, HIGH confidence. `REVISE` — fixable: give `"revision":{"ja":"…","vi":"…","pos":"…"}` (any subset) and say why. `REJECT` — wrong and you see no good fix.
* If a revised `ja` is proposed, **verify it with `lookup.py ja`/`en`** (the JMdict sense must gloss the English lemma). Put the evidence (ent_seq) in `note`.
* Expected: most JA fixes are right; the weaker part is the agent-authored Vietnamese. Be sceptical of VI.

### T2 — 9 flagged concepts with no verified fix (1 packet)
`cost, false, fit, inspire, manner, critical, vital, attachment, actual`. Find a Japanese (and VI if present) equivalent that JMdict glosses with the English lemma and that matches POS.
Output `REVISE` with `revision.ja` (+`vi`) and the ent_seq in `note`, or `REJECT` = "no verifiable fix exists". Never `ACCEPT`.

### T3 — Human-review queue: 1,127 Phase 1.4 candidates (29 packets, highest learning value first)
An earlier model judged these REVIEW (plausible, not auto-acceptable). They are **not in the corpus**. Decide whether each is good enough to promote.
Same output schema as T1 (`"task":"T3"`). `ACCEPT` = promote as-is (rare; HIGH only). `REVISE` = would be fine with a changed `ja`/`vi` (record it; revisions are collected, not auto-applied).
Do T3 in value order and **stop after the first ~300 items** unless asked to continue — quality over volume.

### T4 — Vietnamese for validated EN–JA partial concepts: 1,315 items (33 packets, value ≥ 45)
These have a validated EN–JA pair and **no Vietnamese**. Propose the single most natural Vietnamese equivalent of the stated sense (provenance will be `AI_GENERATED`, reviewer `gpt-6-luna`).
```json
{"task":"T4","id":"concept-lex-airport-nou-6ce705","reviewer":"gpt-6-luna","vi_lemma":"sân bay","synonyms":[],"confidence":"HIGH","note":"Standard word; vn_freq rank 1442."}
```
* `vi_lemma` = `null` when no good single equivalent exists (then confidence ≠ HIGH). At most one synonym, only if equally good. Do not reuse `rejected_vi_before`.
* Do **not** transliterate or copy the English word unless Vietnamese really uses it. Check `lookup.py vi` for attestation; rare-but-correct terms are allowed, say so in `note`.

## 6. Engineering tasks (only after T1 & T2 are reviewed and approved by Claude)
Implement, with tests, **without touching sealed data**:
* **I1 — validation overrides.** Read accepted T1 decisions → write `data/phase1_4/validation_overrides.json` (`{concept_id:{status:"validated",basis:"independent_agent_review",reviewer:"gpt-6-luna",decision_sha:…}}`)
  only for `ACCEPT` + HIGH. Consume it in `scripts/phase1_4/export_views.py` (card `validation_status`, `production_ready`) and `generate_reports.py`. Corrected-concept provenance must stay untouched.
  Test: overridden concepts become `validated`; REVISE/REJECT never do; sealed-prefix tests still pass.
* **I2 — manual acceptances for T3.** Add `data/phase1_4/manual_acceptances.json` (cand_ids) and a hook in `scripts/phase1_4/route.py` mirroring `manual_exclusions` (route to the same ACCEPT kind the judge result implies; require `earlier judge en_ja != WRONG`).
  Rebuild with `scripts/phase1_4/build_canonical.py` (append-only) and show the rebuild is byte-identical when run twice.
* **I3 — T4 ingestion.** Add AI-VI from T4 decisions (provenance `AI_GENERATED`, evidence model `gpt-6-luna`, `input_hash` of the packet item, validation `AGENT_REVIEWED_NOT_INDEPENDENT`, concept stays `needs_review` until Claude/owner reviews).
* Never skip tests; never weaken `tests/`. Run `python -m pytest -q` before reporting (expected: all pass).

## 7. Deliverables & hygiene (local mailbox workflow — see `handoff/PROTOCOL.md`)
You have **no git**. Claude reviews and commits. You communicate only through the mailbox commands:
`luna-next --wait` (get work) → write `data/phase1_4/handoff/decisions/<packet>.jsonl` → `luna-done <task_id>` (format gate + notify Claude) → repeat.
1. Decisions: one line per packet item, same order, validated by `luna-done`.
2. When the queue is empty (or you notice a systematic problem), write `data/phase1_4/handoff/REPORT_LUNA.md` (counts per verdict, 10 least-sure items, systematic error patterns, disagreements with this document) and tell Claude via `handoff/mailbox/to_claude/QUESTION-<n>.md`.
3. Never run `git`, never write outside: `data/phase1_4/handoff/decisions/`, `handoff/mailbox/to_claude/`, `handoff/work/`. `python scripts/handoff/mailbox.py guard` lets anyone verify this.

## 8. What Claude will check (so you can self-check first)
* 100 % of your `REVISE`, `REJECT` and every T2 item; a stratified 15 % sample of `ACCEPT` (focus: Vietnamese naturalness and POS).
* Disagreement rate with the earlier judge on T3 and with Claude on T1. If your ACCEPT rate on T1 is ≥ 95 % or ≤ 40 % Claude will re-examine your calibration.
* Evidence discipline: each REVISE of JA cites an ent_seq; each T4 note mentions attestation or why it is natural.
* Hard-rule compliance (§1) — a single external API call or sealed-data edit voids the batch.

## 9. When in doubt
Choose `LOW` confidence + a precise note over a confident guess. Ask the owner/Claude by writing the question in `REPORT_LUNA.md`; do not improvise around the rules.
