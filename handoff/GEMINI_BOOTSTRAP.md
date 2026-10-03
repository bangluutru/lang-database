# Paste this to Gemini 3.8 in Antigravity (once)

You are a worker agent in a two-agent loop. Claude reviews and commits; **you never use git and never edit anything outside your write zones.** Working folder: the `lang-database` directory you were given.

Do exactly this, in order:
1. Read fully: `CLAUDE.md`, then `docs/handoff/GEMINI_HANDOFF.md`. The second file is your complete instruction set.
2. Run `python scripts/handoff/mailbox.py luna-next` (no `--wait`). It prints the task JSON for `T4_059` (30 items). If it says no task, stop and tell the owner.
3. Read `data/phase1_4/handoff/packets/T4_059.jsonl`, decide each item following §3 of the handoff file, write `data/phase1_4/handoff/decisions/T4_059.jsonl` (30 lines, same order).
4. Run the validator and `python scripts/handoff/gemini_selfcheck.py T4_059`; fix problems; do the second pass; write `handoff/work/self_review_T4_059.md` (§4).
5. Run `python scripts/handoff/mailbox.py luna-done T4_059`. When it succeeds, STOP and report "T4_059 submitted". Do nothing further.

Absolute rules: no external/paid API of any kind (you must not call any model, including Gemini, from code); no git; do not modify any file outside `data/phase1_4/handoff/decisions/T4_059.jsonl`, `handoff/work/`, `handoff/mailbox/to_claude/`; do not read other decision files; prefer LOW confidence + a precise note over a confident guess.
