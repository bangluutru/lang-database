# Claude <-> Luna mailbox protocol (local folder, no git for Luna)

Everything is files under this repository folder. Luna has **no git access**. Only Claude reviews and commits.

## Who may write where
| Actor | May write | Must never |
|---|---|---|
| Luna | `data/phase1_4/handoff/decisions/*.jsonl`, `handoff/mailbox/to_claude/**`, `handoff/work/**` | run `git`, edit any other file, call any external API |
| Claude | `handoff/mailbox/to_luna/**`, `handoff/state.json`, commits, code/tests | — |

`python scripts/handoff/mailbox.py guard` fails if the working tree contains a change outside Luna's zones; Claude refuses to commit until it is clean.

## Loop (repeats automatically until the queue is empty)
1. **Claude** `plan` -> queue = T1 packets, T2, T4 packets, first 8 T3 packets. The first task is `ASSIGNED` (file `to_luna/TASK-<id>.json`).
2. **Luna** `python scripts/handoff/mailbox.py luna-next --wait` -> receives the task JSON (state `IN_PROGRESS`), reads the packet, writes `decisions/<packet>.jsonl`
   (one line per item, same order) following `docs/handoff/LUNA_HANDOFF.md`.
3. **Luna** `python scripts/handoff/mailbox.py luna-done <id>` -> runs the format gate; on success writes `to_claude/DONE-<id>.json` (state `SUBMITTED`). On failure it prints the errors: fix and rerun.
4. **Claude** is woken by the watcher (`watch-claude`), runs `review <id>` (validator + stratified sample file `handoff/work/review_<id>.md`), reads the sample, then either
   * `review <id> --approve --commit` -> commits decisions + review log, state `COMMITTED`, **the next task is assigned automatically**; or
   * `review <id> --rework "specific feedback"` -> writes `to_luna/REVIEW-<id>.json`, re-assigns the same task with the feedback (attempt+1). After 3 attempts the task is `ESCALATED` to the owner.
5. **Luna** goes back to step 2 (`luna-next --wait` blocks until there is work). When the queue is empty Luna sees `NO_TASK`/keeps waiting; Claude reports to the owner.

## Questions
Luna may write `handoff/mailbox/to_claude/QUESTION-<n>.md`; the watcher wakes Claude, who answers in `to_luna/ANSWER-<n>.md`.

## Engineering tasks (I1-I3 in the handoff doc) are NOT in the queue
They change code; Claude assigns them explicitly in a task note after T1/T2 are approved, and still reviews + commits.

## Invariants
* Atomic writes (tmp+rename); `state.json` guarded by a file lock; runtime state is git-ignored; only decisions + `review_log.jsonl` are committed.
* Each decision file is committed only after validator OK + complete + Claude's review. Rework history is in `state.json` events.
