# Project rules for AI coding agents (Claude Code, Codex, Gemini CLI, Cursor, …)

## 1. NO EXTERNAL / PAID API CALLS — hard rule (owner decision, Phase 1.4)

**Do not call any external LLM or paid API** (Vertex AI / Gemini, OpenAI, Anthropic API, Cohere, …), directly or through
a project script, subagent or workflow. No “small test”, no “canary”, no “just this batch”.

Instead:
* **You are the LLM.** If a linguistic judgement, translation proposal or audit is needed, read the data and decide it
  yourself, then write the result into the repo with honest provenance (see §3).
* **Use the caches** under `data/ai/` and `data/phase1_4/` — they allow fully offline, deterministic rebuilds.
* **If you believe an external call is truly necessary: STOP and ask the owner** first, stating the model, the number of
  calls and an estimated cost. Never infer permission from earlier work, from a script's defaults, or from existing
  credentials (`gcloud` being logged in is NOT permission).

Technical guard: every code path that reaches an external model API calls
`scripts/external_api_guard.py::require_external_api_permission()`, which raises unless the owner sets
`LANGDB_ALLOW_EXTERNAL_API=I_AM_THE_OWNER_AND_APPROVE_COSTS` for one command. **Agents must never set, export, hard-code,
or work around this variable**, never add new un-guarded network model calls, and never delete the guard.
`tests/test_external_api_policy.py` enforces this.

Free, public, license-clean *data downloads* (e.g. an open dataset snapshot) are allowed under `SOURCE_POLICY.md`;
anything that costs money or sends project data to a hosted model is not.

## 2. Frozen assets (Phase 1.3D baseline `a07f61e`)
Never edit or reorder the sealed bytes of `data/canonical/*.jsonl`, `data/production/`, `data/releases/golden-pilot-*`,
`data/canonical/legacy_mapping.json`. Canonical files are **append-only**. The only sanctioned edit of the sealed prefix is
the owner-approved Phase 1.4.1 remediation: every changed field is in `reports/phase1_4/baseline_corrections_ledger.json`
and reverting that ledger must reproduce the sealed SHA-256 (`tests/test_phase1_4*.py`, `data/releases/phase1_3d-sealed/baseline_manifest.json`).
Any further correction needs the owner's approval, a ledger entry and a passing revert test.

## 3. Provenance discipline
Origin (`SOURCE_DERIVED`, `CURATED`, `INFERRED`, `AI_GENERATED`, …) and validation (validated / review / quarantined) are
separate dimensions. Content you (an AI agent) write yourself is `AI_GENERATED` (record model/agent, input, time) — never
relabel it as source-derived, and never upgrade origin because a review approved it.

## 4. Semantic quality over counts
Do not force tri-language completeness or reach a size target by lowering quality. Partial concepts are legitimate.

## 5. Delegation
Work packages for another agent (GPT 6 Luna) are defined in `docs/handoff/LUNA_HANDOFF.md`; its decisions are validated by `scripts/phase1_4/handoff/validate_decisions.py` and reviewed by Claude/the owner before any integration.
