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
* `HIGH`: all of (i) you ran the lookups and a-f all pass with no doubt, (ii) the word is either in vn_freq (rank quoted) or demonstrably the normal everyday word (say why), (iii) no plausible competing word of different scope. If any doubt → not HIGH.
* `MEDIUM`: good answer but with one real doubt (compound not in vn_freq and attested only by reasoning; slight scope/nuance gap; two good options). State the doubt in the note.
* `LOW`: best guess, or JA/EN overlap is thin. State what is missing.
* `null` is never HIGH. Expect roughly 40–70 % HIGH on easy packets and fewer on hard ones; a packet that is 100 % HIGH is suspicious and will be re-examined.
* Calibration test before you finalise: "if a Vietnamese linguist read this line, would I bet money it is right?" If not, lower it.

### B5. Note (mandatory content, ≥ 40 characters, specific to THIS item)
Must contain: (1) the sense in a few words, (2) the evidence (`vn_freq rank N` — quote exactly what lookup printed — or `not in vn_freq (checked)` plus why still natural), (3) the main alternative you rejected and why (or "no better alternative"). For MEDIUM/LOW also the doubt. Notes shared verbatim between two items are not allowed (even same-`ja` items like `year` pairs need their own wording).

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
