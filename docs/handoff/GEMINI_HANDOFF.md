# Handoff to Gemini 3.8 (Antigravity) — Vietnamese proposals for EN–JA concepts (PILOT, 30 items)

Audience: **Gemini 3.8** running in Antigravity with access to this repo. Reviewer: **Claude**, then the owner.
This is a **pilot**: only task `T4_059` (30 items). Do NOT start any other task, even if the mailbox shows one. Claude decides after reviewing whether you continue.
Follow the steps literally and in order. Do not "improve" the process. When unsure, say so (LOW confidence) rather than guess.

## 0. Hard rules (breaking any one = stop, tell Claude)
1. **No external or paid API call, ever.** You are the model: read, decide, write. Do not call Gemini/Vertex/OpenAI/any hosted model from code or a script. Never set or read `LANGDB_ALLOW_EXTERNAL_API`. Do not touch `scripts/external_api_guard.py`. No network downloads.
2. **No git.** Never run `git` (no add/commit/stash/checkout/reset). Claude commits.
3. **Write only to these places:**
   * `data/phase1_4/handoff/decisions/T4_059.jsonl` (your answer)
   * `handoff/work/` (your notes / self-review)
   * `handoff/mailbox/to_claude/` (questions)
   Everything else is read-only for you: especially `data/canonical/`, `data/production/`, `data/releases/`, `data/raw/`, `reports/`, `scripts/`, `tests/`, packets, other decision files.
4. **Look only at your own packet.** Do not open other `decisions/T4_*.jsonl` files or `claude_overrides_T4.json` to copy answers: the pilot measures YOUR judgement. (Reading `docs/` and `handoff/PROTOCOL.md` is fine.)
5. **Provenance:** what you write is AI-generated Vietnamese. Use `"reviewer":"gemini-3.8"` exactly. Never describe your output as dictionary-derived.
6. Semantic correctness beats completion. `null` is a good answer when no good single word exists.

## 1. The job
`data/phase1_4/handoff/packets/T4_059.jsonl` has 30 lines. Each is an English concept (one *sense*) that already has a validated Japanese pair and **no Vietnamese**. For each item choose the single most natural **Vietnamese equivalent of the stated sense** (not of the English word in general).

Packet fields: `id, en, pos, ja, ja_reading, ja_jmdict_glosses, en_sense_definition, learning_value, rejected_vi_before`.
* The sense is defined by `en_sense_definition` **and** by the Japanese word `ja` (e.g. `学年` with "academic year" means the school/academic year, `桁` = girder/beam). Give a Vietnamese word that fits that exact sense and part of speech.
* `pos` must be compatible: verb → Vietnamese verb (do not start with `sự/việc`), noun → noun, adjective → adjective/stative, adverb → adverb.

## 2. Output format (one JSON object per line, SAME ORDER as the packet, EXACTLY 30 lines)
```json
{"task":"T4","id":"<id copied from packet>","reviewer":"gemini-3.8","vi_lemma":"sân bay","synonyms":[],"confidence":"HIGH","note":"Standard word for airport; vn_freq rank 1442."}
```
* `vi_lemma`: lower-case Vietnamese with correct diacritics, 1–3 words (max 4), no punctuation, no parentheses, no slash, no English. Or `null`.
* `synonyms`: `[]` or ONE extra form that is equally good. Not a longer paraphrase.
* `confidence`: `HIGH` only if you verified attestation (§3) or are certain it is the normal everyday word. Otherwise `MEDIUM`/`LOW`. `null` can never be `HIGH`.
* `note`: ≥ 15 characters, English or Vietnamese, say WHY (attestation rank, sense reasoning, or why null). Notes like "good" are not accepted.
* Never reuse `rejected_vi_before` (if not null, it was already rejected as wrong).

## 3. How to decide each item (do these 5 steps for EVERY item)
1. Read `en_sense_definition` + `ja` + `ja_jmdict_glosses`. Write down in one phrase what the concept means.
2. Think of 1–3 Vietnamese candidates a native speaker would say today (northern/standard written Vietnamese; avoid southern-only or slang, e.g. `mền`→`chăn`, `má`→`mẹ`).
3. Check attestation (offline):
   ```bash
   python scripts/phase1_4/handoff/lookup.py vi "sân bay"      # rank/POS if in the Vietnamese frequency list; absence is not proof of error
   python scripts/phase1_4/handoff/lookup.py wikt airport      # Wiktionary senses with JA/VI translations for the English word
   python scripts/phase1_4/handoff/lookup.py ja 空港             # JMdict gloss of the Japanese word (to confirm the sense)
   ```
4. Pick the candidate that is **neither broader nor narrower** than the sense and has the same POS. Typical mistakes seen before — avoid them:
   * too narrow / specific: `bút`→ not `bút mực`; `túi` → not `túi áo`; `áo khoác` → not `áo choàng`.
   * over-literal or bookish paraphrase: `đi du lịch` (not `di chuyển`); `sửa chữa` (not `khắc phục`).
   * wrong sense of a polysemous word: check that the Vietnamese fits THIS sense (e.g. "pick" as pluck fruit = `hái`).
   * wrong POS: noun for a verb concept, or an explanation instead of a word.
   * copy of the English word / transliteration unless Vietnamese really uses it (`tivi`, `vinyl` may be fine if you can justify).
   * phrases that explain instead of name (`việc đọc lại`). Prefer the standard lexicalised word.
5. Fill the JSON line. If two good options exist, put the more common in `vi_lemma` and the other in `synonyms`.

Rules of thumb for hard items: if the English has two readings in the definition, follow the one that matches `ja`. If Vietnamese has no single natural word (needs a long explanation), answer `null`, confidence `LOW` or `MEDIUM`, and put the best explanation phrase in `note`.

## 4. Self-check (mandatory, this is your quality gate)
After writing the file:
```bash
python scripts/phase1_4/handoff/validate_decisions.py data/phase1_4/handoff/decisions/T4_059.jsonl
python scripts/handoff/gemini_selfcheck.py T4_059
```
* The validator must say `30 decisions checked, 0 problems`.
* The self-check prints a table + flags and writes `handoff/work/selfcheck_T4_059.md`. Fix every **Blocking** item. For every **Warning**, either change the answer or make `note` explain why the warning is a false alarm.
* Then do a **second pass yourself**: re-read all 30 lines and for each ask: (a) would a Vietnamese teacher teach this word for this sense? (b) POS ok? (c) too broad/narrow? (d) is the confidence honest? Change what you doubt, lowering confidence when unsure.
* Write `handoff/work/self_review_T4_059.md` with exactly: counts (HIGH/MEDIUM/LOW/null), the 5 items you are least sure about with one sentence each, and any rule in this document you found unclear or disagree with.

## 5. Submit
```bash
python scripts/handoff/mailbox.py luna-done T4_059
```
(The command name says "luna" for historical reasons; it is the generic submit command.) If it prints `REFUSED`, fix the listed problems and run it again. After it prints success, **stop**. Do not run `luna-next` again and do not start further tasks. Tell the owner "T4_059 submitted".
Questions: write `handoff/mailbox/to_claude/QUESTION-g1.md` and continue with the other items.

## 6. What Claude will check
All 30 items individually: sense fit, POS, naturalness, regional/pejorative words, over-literal paraphrases, honesty of confidence (a wrong answer marked HIGH is penalised much more than a LOW/null), rule compliance (§0), and whether your self-review caught your own weak items. A clean pilot (few wrong, honest confidence, no rule violations) unlocks larger batches.
