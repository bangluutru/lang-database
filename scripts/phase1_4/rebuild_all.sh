#!/bin/sh
# Deterministic, OFFLINE rebuild of every derived artefact from the committed inputs (no network, no external API).
# Safe to run any time; if the working tree was clean it must stay clean afterwards.
set -e
PY=".venv/bin/python"
$PY scripts/phase1_4/build_jmdict_candidates.py >/dev/null
$PY scripts/phase1_4/select_corpus.py >/dev/null
$PY scripts/phase1_4/run_judge.py collect >/dev/null
$PY scripts/handoff/build_validation_overrides.py
$PY -c "from scripts.phase1_4 import build_canonical as B; B.build(write=True)" >/dev/null
$PY scripts/phase1_4/export_views.py >/dev/null
$PY scripts/phase1_4/generate_reports.py >/dev/null
$PY scripts/phase1_4/write_final_report.py
echo "rebuild ok"
