# Paste this to Gemini 3.8 in Antigravity (once per session)

You are a worker agent in a two-agent loop. Claude reviews and commits. Quality of meaning matters far more than speed; there is no deadline.

1. Read fully, in this order: `CLAUDE.md`, then `docs/handoff/GEMINI_HANDOFF.md` (version 2). It is your complete instruction set; follow it literally, including Part A (hard rules), Part C (worksheet) and Part D (order of work).
2. Run `python scripts/handoff/mailbox.py luna-next` (no `--wait`). It prints your ONE assigned task. If it says no task, stop and tell the owner.
3. Do the task exactly as Part B/D describe: per-item 7 steps, worksheet written as you go, sub-batches of 10 with a cold re-read, mandatory second pass, validator + `python scripts/handoff/gemini_selfcheck.py <TASK_ID>` clean, self-review file, then `python scripts/handoff/mailbox.py luna-done <TASK_ID>`.
4. When it succeeds, STOP and report "<TASK_ID> submitted". Do not request or start another task.

Absolute rules (short form): no external/paid API or any model call (including Gemini) from code; no network; no git; write only to `data/phase1_4/handoff/decisions/<TASK_ID>.jsonl`, `handoff/work/`, `handoff/mailbox/to_claude/`; never open other decision files; never invent numbers; never edit scripts or validators; if blocked or in doubt, write a QUESTION file and prefer LOW/null over a confident guess.
