# Session hand-off (read this FIRST in a new Claude session)

Repo: `lang-database` (EN–JA–VI learning lexical graph). Owner writes Vietnamese; reply in Vietnamese. Last updated 2026-10-03.

## Hard rules (also in `CLAUDE.md`)
1. **NO external/paid API calls** (owner decision; ~25–90 USD were spent before the ban). You are the LLM. Guard: `scripts/external_api_guard.py`.
2. Sealed Phase 1.3D bytes may only differ via the reversible ledger `reports/phase1_4/baseline_corrections_ledger.json`; canonical files are append-only; professional-800 / Golden Pilot untouched.
3. Provenance ≠ validation. Anything an agent writes is `AI_GENERATED`; validation is a separate dimension.
4. Worker agent **GPT 6 Luna never commits**. Only Claude reviews + commits. Luna works through the file mailbox (`handoff/PROTOCOL.md`).
5. Owner wants **token economy**: use the batch/exception-only review mode (below), terse replies.

## Where things stand (git `main`, tags phase1.4-closure, phase1.4.1-closure, phase1.4.2-closure)
* Corpus ≈ 6.8k concepts (see `reports/phase1_4/final_metrics.json`, `final_closure_report.md`, `baseline_remediation_report.md`). Tests: ~479 passing (`.venv/bin/python -m pytest -q`).
* Phase 1.4 (expansion), 1.4.1 (baseline defect remediation), 1.4.2 (Luna hand-off: T1/T2/T4 all done; T3 first 9 packets done) are committed and pushed.
* **In progress: T3 wave 2** — review-queue candidates T3_009…T3_029 (T3_001–009 committed). Queue state lives in `handoff/state.json` (local, git-ignored);
  inspect with `python scripts/handoff/mailbox.py status`.

## How to resume the loop (token-saving mode)
```bash
cd <repo>; python scripts/handoff/mailbox.py status          # who is waiting for whom
python scripts/handoff/mailbox.py guard                      # must say "guard ok" before any commit
# start the watcher as a persistent Monitor (wakes ONLY when >=5 submissions wait or Luna is idle):
python scripts/handoff/mailbox.py watch-claude --interval 15 --batch 5
# when woken:
python scripts/handoff/mailbox.py review-batch               # validates all SUBMITTED tasks, writes handoff/work/review_batch.md (exceptions only)
#   read that ONE file; for T3 ACCEPT lines you agree with:   python scripts/handoff/claude_accept.py T3_0NN word word ...   (auto-commits)
#   for T4 proposals you want to change:                       python scripts/handoff/claude_override.py T4_0NN "en=vi" "en2=NULL"   (auto-commits)
python scripts/handoff/mailbox.py approve-batch              # commits each task, chains on; or  --rework T3_012="feedback"
```
Judgement criteria for T3 (promotion into the corpus): accept only core/neutral, sense-specific, natural pairs; reject rare/archaic/regional/too-narrow/too-broad senses
(examples of rejects: `school`=fish school, `duty`=義理, `kid`=nhóc vs 子, `immigration`=移民). For T4: fix regional/pejorative/over-literal Vietnamese (`mền`→`chăn`, `đổi chác`→`hoán đổi`).

## After the T3 queue is empty
1. `./scripts/phase1_4/rebuild_all.sh` (offline, deterministic; applies `claude_review_T3.json`, T4 proposals+overrides, validation overrides). Then `pytest`, commit, push.
2. **T4 extension (Luna proposes VI for the remaining partial concepts incl. newly promoted T3 ones):**
   `python scripts/phase1_4/handoff/make_packets.py --extend T4` (adds NEW packets only, never edits existing ones; floor value 30), then `python scripts/handoff/mailbox.py plan`, run the loop above.
   After approval run `rebuild_all.sh` again.
3. Re-run `python scripts/phase1_4/write_final_report.py`, tag e.g. `phase1.4.3-closure`, push.

## Key facts / discoveries to remember
* Sealed baseline was weak (49% strict accept on a 150 sample): Luna independently validated 280 corrected concepts; 18 changed afterwards stay `needs_review`.
* Lemma-level list classifications (NGSL/CEFR/JLPT/VI-core) are projected only onto core senses (`is_core_sense`).
* Match-before-create indexes only the **sealed (corrected) baseline** (`baseline_expressions()`), never Phase 1.4 output.
* Hand-off decisions are inputs, never edited by Claude: Claude's own decisions live in `claude_review_T3.json` and `claude_overrides_T4.json`.
* Known gaps: T4 Vietnamese is `AI_GENERATED` + `needs_review`; ~14.5k low-priority candidates never judged; IT/healthcare/travel domain packs thin; no spoken-Vietnamese view.

## Costs seen (for planning)
Luna route ≈ 3k tokens/packet for Claude before batch mode; batch/exception mode targets ≈ 1k/packet. Self-doing T4 would cost ≈ 130–250k vs ≈ 100k via Luna.
