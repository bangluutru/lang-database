# Gemini 3.8 — Operating Rules for Vietnamese Proposals (T4), version 2

Audience: **Gemini 3.8** (Antigravity) working in this repository. Reviewer: **Claude**, then the owner.
Status: pilot `T4_059` passed (26/30 good, honest confidence). Further work is allowed **one packet at a time, only when Claude assigns it**.

**Priority order, always: (1) correctness of meaning, (2) following these rules, (3) honest confidence, (4) completeness, (5) speed.**
There is no deadline. A slow, careful packet is better than a fast one. One wrong answer marked HIGH costs more than ten correct `null`/LOW answers.
Follow this document literally. Do not skip a step because an item "looks easy"; easy-looking items are where silent mistakes happen.

---
## PART A — Hard rules (violating any = STOP, write a QUESTION file, do not continue)

A1. **No external/paid API, no model call, no network.** You are the model. Never call Gemini/Vertex/OpenAI/Anthropic or any hosted model from code or a shell command. Never read, set, export or mention `LANGDB_ALLOW_EXTERNAL_API`. Never open `scripts/external_api_guard.py` for editing. No downloads, no `pip install`, no `curl`/`wget`.
A2. **No git.** No `git add/commit/stash/checkout/reset/restore/clean/rm/mv`. Claude commits.
A3. **Write zones (exhaustive).** You may create or modify ONLY:
   * `data/phase1_4/handoff/decisions/<TASK_ID>.jsonl` — your answer for the assigned task
   * `handoff/work/` — worksheet, self-review, scratch notes
   * `handoff/mailbox/to_claude/` — questions
   Everything else is read-only: `data/canonical/`, `data/production/`, `data/releases/`, `data/raw/`, `reports/`, `scripts/`, `tests/`, `docs/`, `CLAUDE.md`, packets, every other `decisions/*.jsonl`, `handoff/state.json`, `handoff/mailbox/to_luna/`.
   If a script or validator seems wrong, **do not fix it** — write `QUESTION-<n>.md`.
A4. **Do not look at other answers.** Do not open any other `decisions/*.jsonl`, `claude_overrides_T4.json`, `claude_review_*.json`, `review_log.jsonl`, or `handoff/work/review_*.md`. Your judgement must be independent; copying other decisions is a violation even if the answer is right.
A5. **Only the assigned task.** Work only on the task Claude put in `handoff/mailbox/to_luna/TASK-<id>.json`. After a successful `luna-done`, **STOP**. Never run `luna-next` in a loop, never start another packet on your own.
A6. **Provenance.** Everything you write is AI-generated. Use `"reviewer":"gemini-3.8"` exactly. Never claim a word "comes from a dictionary" unless a lookup command printed it (then cite the command in the note).
A7. **No fabrication.** Never invent a frequency rank, ent_seq, Wiktionary entry or "native speaker said". Only quote numbers that a lookup command printed to you in this session. If you did not look, say "not checked".
A8. **No bulk shortcuts.** Do not generate the output file with a script/loop/template, do not reuse one note for several items, do not write answers before you have done the per-item steps. Each line is the result of reading that item.
A9. **Counts are never a goal.** Do not pad. Do not force an answer. `null` is correct when no good single word exists.

---
## PART B — The task (T4)

Input: `data/phase1_4/handoff/packets/<TASK_ID>.jsonl`. Each line = one English concept (ONE sense) that already has a validated Japanese pair and **no Vietnamese**.
Fields: `id, en, pos, ja, ja_reading, ja_jmdict_glosses, en_sense_definition, learning_value, rejected_vi_before`.
Goal: the single most natural, current, standard **Vietnamese equivalent of that sense**.

The sense is fixed by **both** `en_sense_definition` and `ja` (+ its JMdict glosses). Where they differ in scope, give a word that fits **their overlap** (the sense the learner is being taught), e.g. `学年` = the school/academic year as a unit of schooling, not "grade level".

### B1. Output line (exactly one JSON object per packet item, same order, same count)
```json
{"task":"T4","id":"<copied from packet>","reviewer":"gemini-3.8","vi_lemma":"sân bay","synonyms":[],"confidence":"HIGH","note":"..."}
```
* `vi_lemma`: Vietnamese, lower-case, correct diacritics, 1–3 words (4 max), no punctuation/parentheses/slash/digits. Or `null`.
* `synonyms`: `[]` or ONE form that is (i) equally standard, (ii) different from `vi_lemma`, (iii) the same POS and sense. Never a longer paraphrase, never a broader/narrower word.
* `note`: see B5. `confidence`: see B4.
* Never output `rejected_vi_before` (if not null it is already known wrong).
* English loanwords (`tivi`, `vinyl`, `gas`…) are allowed ONLY if Vietnamese really uses them as the standard word; then `note` must contain the word `loanword` and say how you know (lookup output or the fact it is the normal word in everyday Vietnamese). Prefer the native/standard word when one exists.

### B2. Per-item procedure — do ALL 7 steps for EVERY item, in this order, and record them in the worksheet (Part C)
1. **Define.** One phrase (≤12 words) stating the sense, in your own words, from `en_sense_definition` + `ja` + `ja_jmdict_glosses`. Note the POS.
2. **Check the Japanese.** Run `python scripts/phase1_4/handoff/lookup.py ja <ja>`; confirm the JMdict sense that matches. If the JA seems to mean something different from the English, do not fix it — answer for the overlap, and lower confidence.
3. **Generate ≥ 2 candidates** (≥ 3 for MEDIUM/hard items): ordinary Vietnamese words a speaker uses today in standard/northern written style. Include at least one *non-obvious* alternative so you are choosing, not rubber-stamping the first idea.
4. **Gather evidence** for each serious candidate: `python scripts/phase1_4/handoff/lookup.py vi "<cand>"` (rank/POS), and `python scripts/phase1_4/handoff/lookup.py wikt <english word>` for translation hints. Absence from vn_freq is not an error but means you must reason explicitly about naturalness.
5. **Test each candidate** against all of these (write the verdict, one short phrase each):
   a. *Sense*: fits THIS sense, not another sense of the English word or of the Vietnamese word.
   b. *Scope*: not broader, not narrower (`bút` not `bút mực`; `túi` not `túi áo`; `hái` for pluck fruit, not `thu thập`).
   c. *POS*: verb→verb (never starts with `sự/việc/cuộc/nỗi`); noun→noun (never starts with `làm/thực hiện/bị/được`); adjective→adjective; adverb→adverb or adverbial phrase that is idiomatic as an adverb (`một ngày nào đó`, not `ngày nào đó`).
   d. *Register/region*: neutral, standard, modern. Reject southern-only/dialect (`mền`→`chăn`, `má`→`mẹ`), slang, pejorative, archaic, overly literary (Hán–Việt only if it is the normal modern word for this sense; check false friends).
   e. *Naturalness*: a Vietnamese teacher would teach it; lexicalised word, not an explanation (`đi du lịch`, not `di chuyển`; no `việc đọc lại`).
   f. *Match with JA nuance*: if `ja` is a strong/weak/colloquial version of the sense, the Vietnamese should not be clearly stronger/weaker (e.g. `厚かましい` = brazen/pushy → `trơ tráo`, not `tự phụ` = conceited).
   g. *Reverse + substitution test (required for every HIGH)*: (i) back-translate your Vietnamese word to English — does it give exactly the English lemma, or something broader/narrower/different (`gây ra`=cause, not exert influence; `nơi sinh`=birthplace only)? (ii) write one short Vietnamese sentence using the word in THIS sense and check it sounds natural; (iii) ask "is there a plainer, more common word everyone uses?" (`bơ` for butter, not the invented `bơ sữa`). Record (i)–(iii) in the worksheet. If any answer is "no/unsure", it is not HIGH.
6. **Decide.** Choose the candidate passing a–f. If two pass, the more common → `vi_lemma`, the other → `synonyms` (only if truly equal). If none passes → `vi_lemma:null`.
7. **Set confidence** (B4) and write the note (B5).

### B3. Typical errors seen so far (read twice)
* too narrow / too concrete: `bút mực`, `túi áo`, `áo choàng`, `hướng ngắm`.
* bookish or abstract paraphrase for an everyday verb: `khắc phục`, `di chuyển`.
* wrong sense of a polysemous Vietnamese word (`đầu tiên` for "head").
* wrong register: slang/regional/childish (`nhóc`, `mền`, `má`).
* nominal prefix on verbs; verb prefix on nouns.
* semantically near but different emotion/attitude (`tự phụ` for "presumptuous/brazen").
* adverb given as a bare noun phrase (`ngày nào đó` instead of `một ngày nào đó`).
* choosing the word first, justifying it afterwards. Do steps 3–5 BEFORE choosing.

### B4. Confidence — strict definitions
* `HIGH` (strictest; in the last calibration 3 of 20 HIGH answers were wrong — all were plausible-looking words that were too narrow, a different verb, or an invented compound): all of (i) you ran the lookups and a-f all pass with no doubt, (ii) the word is either in vn_freq (rank quoted) or demonstrably the normal everyday word (say why), (iii) no plausible competing word of different scope. If any doubt → not HIGH.
* `MEDIUM`: good answer but with one real doubt (compound not in vn_freq and attested only by reasoning; slight scope/nuance gap; two good options). State the doubt in the note.
* `LOW`: best guess, or JA/EN overlap is thin. State what is missing.
* `null` is never HIGH. Expect roughly 40–70 % HIGH on easy packets and fewer on hard ones; a packet that is 100 % HIGH is suspicious and will be re-examined.
* Calibration test before you finalise: "if a Vietnamese linguist read this line, would I bet money it is right?" If not, lower it.

* **Concerning `rejected_vi_before`:** you may not output it as `vi_lemma`. If you genuinely believe it is the correct standard word, choose your best OTHER candidate, set confidence ≤ MEDIUM, and write in the note `QUERY: rejected_vi_before "<word>" may be correct because ...`. Do not invent an unnatural compound just to avoid the rejected word (e.g. `bơ sữa`); `null` or a plain, honest alternative is better.
* **Do not change an answer only to silence a selfcheck warning.** Change it only if the word is really worse than the alternative; otherwise keep it and explain in the note.
* A word marked `loanword` is allowed (see B1); the selfcheck does not forbid it.

### B5. Note (mandatory content, ≥ 40 characters, specific to THIS item)
Must contain: (0) for HIGH: the words `back-translation` result in a few words (e.g. "back-translation = butter"); (1) the sense in a few words, (2) the evidence (`vn_freq rank N` — quote exactly what lookup printed — or `not in vn_freq (checked)` plus why still natural), (3) the main alternative you rejected and why (or "no better alternative"). For MEDIUM/LOW also the doubt. Notes shared verbatim between two items are not allowed (even same-`ja` items like `year` pairs need their own wording).

---
## PART C — Required work files (all inside `handoff/work/`)

1. `worksheet_<TASK_ID>.md` — written **progressively while you work** (not at the end). One block per item, same order as the packet:
```
### <n>. <en> (<pos>) | <ja> | <id>
- sense: ...
- JA check: <ent_seq/gloss you saw, or "no entry">
- candidates: A) ... [rank N / not in vn_freq]  B) ... C) ...
- tests: A: sense ok, scope ok, pos ok, register ok, natural ok, nuance ok | B: scope too narrow | ...
- choice: A (+ synonym B?) ; confidence: HIGH|MEDIUM|LOW ; doubt: ...
```
2. `self_review_<TASK_ID>.md` — after the second pass (see D3): counts (HIGH/MEDIUM/LOW/null), the 5 least-sure items with one sentence each, every item whose answer you CHANGED in the second pass (old → new, why), rule ambiguities.

---
## PART D — Order of work (do not reorder)

D1. **Prepare.** Read `CLAUDE.md`, this file, then `python scripts/handoff/mailbox.py luna-next` (no `--wait`) to get the task. Read the whole packet once before deciding anything.
D2. **Work in sub-batches of 10 items.** For each sub-batch: do B2 steps 1–7 for each item, append to the worksheet, then append the 10 JSON lines to `decisions/<TASK_ID>.jsonl`. After each sub-batch, stop and re-read the 10 lines (cold read), fixing anything doubtful. Never write more than 10 items without re-reading.
D3. **Second pass (mandatory, after all items).** Re-read the whole decision file next to the packet. For every item answer: (a) sense? (b) scope? (c) POS? (d) register? (e) honest confidence? (f) note specific and true? Change what fails and log the change in the self-review. If you changed nothing in a packet of 30, assume you were not critical enough and re-examine the 5 items with the lowest confidence.
D4. **Machine gates.** Run both and fix everything until clean:
```bash
python scripts/phase1_4/handoff/validate_decisions.py data/phase1_4/handoff/decisions/<TASK_ID>.jsonl
python scripts/handoff/gemini_selfcheck.py <TASK_ID>
```
Validator: `0 problems`. Selfcheck: no *Blocking*; every *Warning* is either fixed or addressed in that item's note. Never edit the scripts to make them pass.
D5. **Submit.** `python scripts/handoff/mailbox.py luna-done <TASK_ID>` (command name is historical). If it prints `REFUSED`, fix and rerun. When it succeeds: **STOP** and report "<TASK_ID> submitted".

---
## PART E — When to stop and ask
Write `handoff/mailbox/to_claude/QUESTION-g<n>.md` (what, which item ids, what you tried) and continue with the other items if any of these happens: a rule seems contradictory or impossible; the packet looks malformed; an item's JA and EN clearly mean different things (do not guess — answer `null`/LOW and ask); a command errors; you are tempted to touch a file outside A3. Never "work around" a rule.

## PART F — How Claude will grade (so you can self-grade first)
1. Every item individually: sense, scope, POS, register, nuance, naturalness.
2. Calibration: wrong-but-HIGH is the worst outcome; correct `null`/LOW is fine.
3. Evidence honesty: every quoted rank is re-checked; a fabricated number voids the batch.
4. Process: worksheet exists and matches decisions; second-pass changes were logged; no note is copy-pasted; no rule in Part A broken. A single A1–A5 violation voids the batch.
5. Outcome: ≥ 90 % of items acceptable and no unsafe HIGH → next packet is allowed; otherwise Claude returns specific rework instructions (max 3 attempts).

---
## PART G — Task kind `G4` (calibration packet)
A `G4_NNN` packet has exactly the same format and rules as a T4 packet (Parts A–F). Treat every item as brand new: decide it only from the packet and your own lookups. The output file is `data/phase1_4/handoff/decisions/G4_NNN.jsonl` (lines still use `"task":"T4"`), and the worksheet/self-review/selfcheck use the task id `G4_NNN`. Rule A4 applies with full force: other `decisions/*.jsonl` files (including all `T4_*`) may contain answers for these very items and you must not open them.

---
## PART H — Task kind `G3` (T3-style promotion review)
Applies to packets `G3_NNN`. Parts A, C, D, E, F and G's rules about independence apply unchanged (worksheet, sub-batches of 10, second pass, validator + selfcheck, `luna-done`, stop). Output file: `data/phase1_4/handoff/decisions/G3_NNN.jsonl`; each line has `"task":"T3"`. The task id for worksheet/selfcheck is `G3_NNN`.

### H1. What the job is
Each item is a **candidate concept** (English sense + Japanese + sometimes Vietnamese) that is NOT in the corpus yet. You decide whether it is good enough to be **promoted** into a learner-oriented corpus. Promotion is expensive to undo, so the default is NO. Fields: `id, en, pos, en_sense_definition, ja, ja_reading, ja_jmdict_glosses, vi (or null), learning_value`.

### H2. Output line
```json
{"task":"T3","id":"<packet id>","reviewer":"gemini-3.8","verdict":"ACCEPT","en_ja":"OK","en_vi":"NA","ja_vi":"NA","naturalness":"NATURAL","confidence":"HIGH","revision":null,"note":"..."}
```
* `en_ja`, `en_vi`, `ja_vi` ∈ `OK | BROAD | NARROW | WRONG | NA` (`NA` for a pair with no Vietnamese). `naturalness` ∈ `NATURAL | ACCEPTABLE | AWKWARD | WRONG`. `confidence` ∈ `HIGH | MEDIUM | LOW`.
* `ACCEPT` — promote as is. Allowed ONLY if every pair is OK/NA, naturalness NATURAL/ACCEPTABLE and confidence HIGH (the validator enforces this). Expect a **minority** of items (≈ 15–40 %) to be ACCEPT.
* `REVISE` — a small change would make it good: `"revision":{"ja":"…","vi":"…","pos":"…"}` (any subset). Revised `ja` MUST be verified (H4). Revisions are recorded, not applied automatically.
* `REJECT` — wrong, too narrow/broad, rare/archaic/regional/offensive, or no good fix. `revision` must be `null`.
* When unsure between ACCEPT and anything else, **do not ACCEPT**.

### H3. Per-item procedure (all steps, every item, recorded in the worksheet)
1. **Define the sense** from `en_sense_definition` in ≤12 words (the English side is a specific sense, e.g. `party` = banquet, not political party). Note the POS.
2. **Check the Japanese** with `python scripts/phase1_4/handoff/lookup.py ja <ja>`: find the JMdict sense that matches; note the ent_seq, the POS tags and `misc` marks (arch, rare, vulg, col, sl, hon, hum, obs…). Reverse-check with `lookup.py en <english lemma>`: is `ja` among the usual Japanese words for this lemma, or is there a clearly more common word?
3. **Pair test EN↔JA:** same sense? Is `ja` broader (covers more senses/people/things), narrower, or a different sense? Is it the everyday word a learner should be taught, or rare/formal/honorific/slang? Is it a loanword-only or a single-kanji/bound form that is not used alone? Is POS compatible (する-noun for a verb is ok)?
4. **If `vi` is present:** test EN↔VI and JA↔VI the same way (sense, scope, POS, register, regional/pejorative, over-literal). Check `lookup.py vi "<vi>"`. A bad VI with a good EN–JA pair → `REVISE` (propose better VI) not ACCEPT.
5. **Learner-core test** (promotion criteria used by the reviewers of this project): accept only items that are *core, neutral, sense-specific, natural*. Reject when the sense is rare, archaic, regional/dialectal, technical-obscure, a proper noun/brand, a fish/animal-specific or other very narrow sense of a common word, a word that needs a long explanation, or when the Japanese is a different concept (e.g. `school` = fish school vs 学校; `duty` ≠ 義理; `kid` = nhóc vs 子; `immigration` ≠ 移民 (emigrant/immigrant person vs act)).
6. **Falsify yourself (required before any ACCEPT):** (a) write one sentence in English using the lemma in exactly this sense and its natural Japanese translation using `ja`; if the translation needs a different Japanese word, it is not ACCEPT. (b) Name the single best competing Japanese word for this English sense (from `lookup.py en`) and say why `ja` is at least as good. (c) If `vi` present, back-translate it to English: must give this lemma/sense.
7. **Decide, set confidence, write the note.**

### H4. Evidence rules
* Every `REVISE` with a new `ja` must cite the ent_seq and show it glosses the English lemma; `gemini_selfcheck.py` verifies mechanically that the revised `ja` exists in JMdict with a sense glossed by the lemma and **blocks** otherwise. Never invent a Japanese word.
* Quote only what a lookup printed (ent_seq, ranks). Fabricated evidence voids the batch (rule A7).
* A pair is `OK` only if you checked it; mark `BROAD/NARROW` honestly — a mere "broader but close" is **not** OK for ACCEPT.

### H5. Note (≥ 60 chars, specific)
Contains: the sense; the JMdict evidence (ent_seq + matching gloss or the misc tag you saw); the competing word you compared against and the verdict; for ACCEPT the words `falsified: ...` summarising step 6; for REVISE what exactly changes; for REJECT the decisive reason. No boilerplate shared between items.

### H6. Selfcheck for G3 and what Claude grades
`python scripts/handoff/gemini_selfcheck.py G3_NNN` (same command) enforces: reviewer id, worksheet block per item, notes ≥ 60 chars and unique, ACCEPT notes contain `falsified`, REVISE revisions verified in JMdict, warning when ACCEPT rate > 50 % (over-lenient) or < 5 % (over-strict). Claude grades every ACCEPT (precision matters most: a wrongly promoted concept pollutes the corpus), every REVISE verification, and a sample of REJECTs for recall. Outcome gates: ≥ 85 % of your ACCEPTs must be confirmed by Claude; any ACCEPT of a clearly wrong/rare/offensive pair is a serious error and triggers rework of the packet.

---
## PART I — Task kind `A1`: authoring NEW concepts for the thin domain packs
Everything in Part A (hard rules) applies. This part adds stricter rules because authoring is riskier than reviewing: **you are creating data that did not exist**, and past results show you work fast but (1) drop required information, (2) are more confident than the evidence allows. The process below is designed to stop both. Quality and verifiability beat quantity: a `skip` with a precise reason is a good answer.

### I0. Project direction (why this data exists)
`lang-database` is a curated, open, traceable **English–Japanese–Vietnamese learning lexical graph** (Concept → Sense → Expression) for learners of Japanese/English/Vietnamese and spaced-repetition apps. Known gap: the **IT, healthcare and travel packs are thin** (IT 44, healthcare 98, travel 20 concepts). Goal of A1: add *learner-core, everyday-professional* terms that a learner in these domains genuinely needs — **not** exotic jargon, brand names, abbreviations nobody says, or obsolete words. Each concept = ONE sense with EN, JA and VI expressions that really correspond.
Provenance rule of the project: whatever you write is `AI_GENERATED` (definition, Vietnamese, examples). Japanese and the EN–JA pairing must be **verifiable in JMdict**; Vietnamese must be natural modern Vietnamese.

### I1. Absolute prohibitions specific to A1 (breaking one voids the batch)
1. **No git of any kind, no commit, no push, no PR.** Your files stay uncommitted in the working tree. Claude alone decides what passes, and only after Claude's review passes does Claude commit and push. Do not ask or hint that something should be committed.
2. Do not edit `scripts/`, `tests/`, `docs/`, `data/canonical/`, packets, or the slots file; do not change validators/selfcheck to make them pass.
3. No external/paid API or model call. No network. No new downloads.
4. Do not copy definitions from Wiktionary/JMdict/any dictionary: the `sense_definition` and the three examples must be written by you, in your own words (the validator rejects verbatim Wiktionary glosses; Claude checks for close paraphrase).
5. Do not invent evidence: every `ent_seq`, `sense_idx`, rank and "in Wiktionary" claim must come from a command you ran in this session (I3). The validator recomputes them; a mismatch is a fabrication and voids the batch.
6. Do not output proper nouns, brand/product names, company names, people, place names, slang, vulgar, archaic, or pure-abbreviation entries (e.g. no `ASCII`, `iPhone`, `カタル`).
7. Do not open other decision files or any answer key; do not work outside the assigned slots.

### I2. Locked scope: slots
`data/phase1_4/handoff/packets/A1_NNN.jsonl` = one line per **slot**: `id, domain, subdomain, allowed_pos, topic_hint`. You must produce exactly **one output line per slot, same order**. Either a full entry, or a `skip`. You may not add entries beyond the slots, change domain/subdomain, or use a POS not in `allowed_pos`.

### I3. Grounded sourcing (do this for every slot)
1. Browse candidates with the grounded menu (JMdict, commonness-sorted, only terms not yet in the corpus):
   ```bash
   python scripts/handoff/domain_menu.py --domain it --grep server --limit 30      # it | healthcare | manufacturing (travel has no JMdict field tag)
   ```
   For `travel` (and to widen others) use `python scripts/phase1_4/handoff/lookup.py en <english word>` (JMdict reverse lookup) and `... wikt <english word>` (Wiktionary senses and VI translations).
   The menu is a source of candidates, **not an approval**: many menu rows are rare, too technical, or not learner-core — judge them (I4 step 2).
2. Confirm the Japanese with `lookup.py ja <lemma>` and copy the exact `ent_seq` and `sense` index printed. The JMdict sense you cite MUST have a gloss that equals your English lemma (the validator checks).
3. Check Vietnamese: `lookup.py vi "<term>"` (frequency rank) and `lookup.py wikt <english>` (does Wiktionary list your Vietnamese among its VI translations?). Quote the rank only if the command printed it.
4. Check duplication yourself before writing: `grep -c` is not needed — the validator blocks an existing EN–JA pair and warns on an existing EN or JA lemma; if it warns, you must explain in `falsification.why_distinct` (a genuinely different sense) or drop the entry.

### I4. Per-slot procedure (all steps, every slot; log each step in the worksheet)
1. **Understand the slot**: domain, subdomain, `topic_hint`, allowed POS.
2. **Pick 3 candidates** (menu or lookup). For each write: why it is learner-core (would a learner in this domain meet it in the first months?), its JMdict commonness (pri), and any `misc` tag. Discard rare/archaic/slang/brand/abbreviation/too-narrow ones. Prefer plain high-frequency words over specialist ones.
3. **Choose one** and state why it beats the other two.
4. **Define the sense** in one English sentence (25–220 chars) that pins down THIS sense (not the whole word family) in your own words.
5. **Fix the three expressions**: EN lemma (lower case, base form; acronyms only if the acronym is the normal word), JA lemma + reading exactly as JMdict, VI lemma (natural modern Vietnamese, correct diacritics, 1–4 words; no English copy unless it is really the standard word → `loanword:true` + justification in note).
6. **Test the pair (mandatory falsification, three-way):**
   * EN↔JA: JMdict gloss equals the lemma (copy the gloss), sense not broader/narrower.
   * EN↔VI and JA↔VI: write `back_translation` (your Vietnamese → English; must equal the EN lemma, not something broader/different) and check the Vietnamese is not a word for a *different* sense.
   * Write three **natural example sentences**, one per language, each containing the lemma (inflected forms are allowed for verbs/adjectives), and check the three sentences say the same thing.
   * Name the **closest existing corpus concept** (`concept-…` id found with `grep '"<en>"' data/canonical/concepts.jsonl | head`, or `"none"`) and why yours is distinct (`why_distinct`).
7. **Set confidence** using the objective ceiling (I5) — never above it.
8. **Write the note** (≥ 60 chars, specific): sense, JMdict evidence (ent_seq/sense/pri), VI evidence, the rejected alternative, and any doubt.

### I5. Confidence: objective ceiling + honesty
The validator computes the highest confidence the facts allow and **blocks anything above it**:
* `HIGH` requires ALL of: JMdict gloss equals the EN lemma; JA is common (JMdict priority tag > 0 **or** the sense carries a field tag of the domain, e.g. `comp`/`med`); VI attested (appears in vn_freq **or** in Wiktionary's Vietnamese translations of the English word).
* `MEDIUM` = gloss equal but JA commonness or VI attestation is missing.
* `LOW` = gloss not exactly equal.
Even when the ceiling allows HIGH you should lower the confidence if any doubt remains. **Your habit is to rate HIGH too often.** Expect at most ~50 % HIGH. The report (I6) must include an audit of every entry's claimed vs ceiling confidence and, for every HIGH, one sentence naming the evidence that would convince a skeptical reviewer.

### I6. Required files (all in `handoff/work/`), written progressively
1. `worksheet_<TASK_ID>.md` — one block per slot (same ids), with every step of I4 (candidates, tests, back-translation, closest concept, decision). Append after each sub-batch, not at the end.
2. `self_review_<TASK_ID>.md` — second-pass log: each entry you changed/dropped and why.
3. `report_<TASK_ID>.md` — **the review report you send to Claude**, with EXACTLY these headings:
   * `## Mechanical results` — paste the validator and selfcheck summary lines (counts, blocks=0).
   * `## Confidence audit` — a table with one row per non-skipped entry id: claimed, ceiling, evidence, and for HIGH the convincing-evidence sentence; and a statement of your HIGH share.
   * `## Least sure` — the 5 entries you trust least and why (include at least one HIGH if you have HIGH entries).
   * `## Skipped slots` — each skipped id with what you searched and why nothing qualified.
   * `## Declaration` — the exact sentence: `I have not run git and have not modified any file outside my write zones.`
   Do not submit until all five headings exist; the selfcheck enforces this.

### I7. Entry format (one JSON object per line; example for a real item)
```json
{"task":"A1","id":"A1_001-01","reviewer":"gemini-3.8","domain":"it","subdomain":"software_dev",
 "en":{"lemma":"cache","pos":"noun","sense_definition":"A fast temporary storage that keeps copies of data for quicker repeated access."},
 "ja":{"lemma":"キャッシュ","reading":"キャッシュ"},
 "vi":{"lemma":"bộ nhớ đệm","claimed_vn_freq_rank":null,"claimed_in_wikt":true,"loanword":false},
 "evidence":{"jmdict_ent_seq":1041420,"jmdict_sense_idx":0},
 "falsification":{"example_en":"The browser keeps the page in its cache.","example_ja":"ブラウザはページをキャッシュに保存する。","example_vi":"Trình duyệt lưu trang vào bộ nhớ đệm.",
                  "back_translation":"cache","closest_existing_concept":"none","why_distinct":"No cache concept exists in the corpus."},
 "confidence":"MEDIUM","note":"Sense: temporary fast data store. JMdict 1041420 s0 gloss 'cache', pri 3, field comp. VI 'bộ nhớ đệm' standard; rejected 'bộ nhớ tạm' as vaguer. Doubt: rank not in vn_freq."}
```
Skip line: `{"task":"A1","id":"A1_001-07","reviewer":"gemini-3.8","skip":true,"reason":"<what you searched with which commands and why every candidate failed (>= 40 chars)>"}`.
Field rules: `claimed_vn_freq_rank` and `claimed_in_wikt` are what you believe lookup printed (use `null` if you did not check); they are verified. `loanword:true` only when the Vietnamese is the English/Japanese word itself.

### I8. Order of work (do not reorder)
1. Read `CLAUDE.md`, this document (all Parts), run `luna-next` (no `--wait`), read the whole slots file.
2. Work in **sub-batches of 5 slots**: for each slot do I4 and append its worksheet block; then append the 5 JSON lines to `decisions/<TASK_ID>.jsonl`; then run the validator on the file-so-far if you wish (it will complain about missing slots only) and **cold re-read the 5 entries**, fixing doubts, before the next sub-batch.
3. After all slots: **second pass** over the whole file — re-verify every ent_seq/sense by running `lookup.py ja` again for every HIGH entry (do not trust memory), re-check each example sentence contains the lemma and means the same in all three languages, re-check duplicates, and lower any confidence you cannot defend. Write `self_review`.
4. Machine gates until clean:
   ```bash
   python scripts/phase1_4/handoff/validate_decisions.py data/phase1_4/handoff/decisions/<TASK_ID>.jsonl
   python scripts/handoff/gemini_selfcheck.py <TASK_ID>
   ```
5. Write `report_<TASK_ID>.md` (I6) and re-run selfcheck (it now checks the report).
6. Submit: `python scripts/handoff/mailbox.py luna-done <TASK_ID>`, then **STOP** and tell the owner "<TASK_ID> submitted for Claude's review". Do NOT commit, push, or start another task.

### I9. What happens next (so you know the stakes)
Claude reviews **every** entry (sense, JA/VI naturalness, learner-core value, duplication, example quality) and re-audits your confidence against the evidence. Outcomes per entry: **PASS** (will be integrated), **FIX** (Claude edits or asks you to revise), **FAIL** (dropped). Per batch: all PASS → Claude commits and pushes; any FAIL/FIX → the batch is returned (`REWORK`) with specific feedback, max 3 attempts. **Nothing is committed or pushed before Claude's review passes.** Grading emphasises: wrong-but-HIGH (worst), fabricated evidence (voids batch), missing/omitted fields or skipped steps, duplicates, non-learner-core picks, near-copy of dictionary text.

### I10. Rework slots (`A1_NNN` built from a previous review)
Some slots carry `fixed_en`, `fixed_ja`, `review_feedback` and `previous_attempt`. Rules: keep the same EN lemma and JA lemma (`fixed_*`, the validator enforces it); read `review_feedback` fully and treat each criticism as a hypothesis you must **verify with commands**, not as an order — if you disagree, say so with evidence in the note; fix the problem the reviewer named, and then re-run the complete I4 procedure (all steps, all three example sentences) because a fix often breaks something else. Do not simply copy `previous_attempt`. Confidence must reflect the reviewer's finding (if the previous HIGH was challenged, you need new evidence for HIGH).

### I11. Lessons from the first authoring pilot (A1_001/A1_002) — apply them before you submit
1. **VI scope must equal the EN/JA sense.** Pilot failures: `gây mê` (= general anaesthesia) for `麻酔` (anaesthesia in general); `vé vào cửa` (a ticket) for `入場料` (a fee). Test: does the Vietnamese word cover MORE or LESS than the English sense? If yes, pick another word or lower the confidence and say so.
2. **Department vs specialty.** For hospital slots choose the term learners meet on signs/forms (`khoa nội`, `khoa nhi`) and justify your choice with lookups; avoid tautologies (`khoa nội khoa`).
3. **Example sentences are data, not decoration.** They must be natural, medically/technically correct in all three languages and say the same thing. Never translate a specialist term by guessing (`biểu bì` = epidermis, not `epinephrine`). Avoid regional words when a neutral one exists (`lạc` vs southern `đậu phộng`).
4. **Polysemy.** If the EN lemma already exists in the corpus with another sense (`branch` = tree limb, `icon` = religious painting), name that concept in `closest_existing_concept` and explain the difference.
5. **Confidence.** In the pilot 1 of 11 HIGH claims was too high. Ceiling-allowed does not mean deserved: lower the confidence when scope is even slightly asymmetric.
6. **Manufacturing has few JMdict field tags** (engr/elec/mech): for most slots use `lookup.py en <word>` and `wikt <word>` to find grounded candidates, and expect more MEDIUM answers and honest `skip`s.

### I12. Additional lessons from waves 1–2 (94 entries reviewed; 12 needed rework) — check each before submitting
1. **A matching JMdict gloss is necessary, not sufficient.** `記念` glosses 'souvenir' but means commemoration; `痙攣` glosses 'cramp' but means convulsion/spasm. The selfcheck now warns when your matching gloss is not among the first two glosses of that sense: when it appears, compare the Japanese word's typical meaning with your English sense (use the JMdict glosses list as a scope check) and write the scope check in the note.
2. **Abstract vs concrete.** If the Japanese is an action/abstract noun and the Vietnamese/English is a concrete object (or the reverse), the pair is wrong. Say in the note which one each side is.
3. **Orthography of Vietnamese.** Use modern standard spelling (`công ty`, not `công ti`), correct diacritics, ALL-CAPS acronyms (`IP`, `SSD`) where Vietnamese writes them so. Do not copy a Vietnamese string from a Wiktionary line without checking it is current usage.
4. **Definition scope = VI scope = JA scope.** If the definition says "hotel or flight" the Vietnamese must cover both; otherwise narrow the definition and the examples.
5. **Example sentences**: no tautologies (`tấm thép tấm`), no stacked synonyms, natural in all three languages; they are reviewed like the lemma.
6. **Calibration**: 9–14 % of your HIGH claims were wrong or too high. When unsure, MEDIUM. A MEDIUM that is right is better than a HIGH that must be reworked.
