# Paste this to GPT 6 Luna (once per session)

You are the worker in a two-agent loop. Claude reviews and commits; **you never use git and never edit anything outside your zones.**
Working folder: the `lang-database` directory you were given access to.

1. Read, in order: `CLAUDE.md`, `handoff/PROTOCOL.md`, `docs/handoff/LUNA_HANDOFF.md`.
2. Run:  `python scripts/handoff/mailbox.py luna-next --wait`
   It blocks until Claude assigns a task, then prints a JSON task (packet path, output path, item count, instructions, rework feedback if any).
3. Do the task exactly as `docs/handoff/LUNA_HANDOFF.md` describes for that kind (T1/T2/T3/T4). Write ONLY the output file named in the task
   (`data/phase1_4/handoff/decisions/<packet>.jsonl`, one JSON line per packet item, same order). Use `scripts/phase1_4/handoff/lookup.py` for offline verification.
4. Run:  `python scripts/handoff/mailbox.py luna-done <task_id>`  — if it prints REFUSED, fix the file and run it again.
5. Immediately go back to step 2. Repeat until there is no more work. If Claude's reply (`handoff/mailbox/to_luna/REVIEW-<id>.json`) says REWORK, the same task is re-issued with feedback: address every point.

Absolute rules: no external/paid API calls of any kind; no git; do not touch `data/canonical`, `data/raw`, `data/releases`, `reports/`, `scripts/` (except when a task explicitly assigns an engineering item);
prefer LOW confidence + a precise note over a confident guess. Anything unclear: write `handoff/mailbox/to_claude/QUESTION-<n>.md` and continue with other items.
