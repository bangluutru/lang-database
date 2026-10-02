"""Enforces the project rule: no external/paid LLM API calls (see CLAUDE.md)."""
import os
import re
from pathlib import Path

import pytest

BASE = Path(__file__).resolve().parent.parent
NET = re.compile(r"requests\.(post|get|put)\(|urllib\.request\.urlopen|aiplatform\.googleapis|generativelanguage\.googleapis|api\.openai\.com|api\.anthropic\.com")
ALLOWED_DOWNLOADERS = {"scripts/download_sources.py", "scripts/acquire_sources.py"}  # free open-data snapshots only


def test_policy_documents_exist():
    for f in ("CLAUDE.md", "AGENTS.md"):
        t = (BASE / f).read_text()
        assert "NO EXTERNAL / PAID API CALLS" in t and "external_api_guard" in t


def test_every_model_api_call_site_is_guarded():
    offenders = []
    for p in sorted((BASE / "scripts").rglob("*.py")):
        rel = str(p.relative_to(BASE))
        if rel == "scripts/external_api_guard.py" or rel in ALLOWED_DOWNLOADERS:
            continue
        src = p.read_text(encoding="utf-8")
        if re.search(r"aiplatform\.googleapis|generativelanguage\.googleapis|api\.openai\.com|api\.anthropic\.com|requests\.post\(", src):
            if "require_external_api_permission" not in src:
                offenders.append(rel)
    assert not offenders, f"un-guarded external model call sites: {offenders}"


def test_guard_blocks_by_default(monkeypatch):
    from scripts.external_api_guard import require_external_api_permission, ExternalAPIForbidden
    monkeypatch.delenv("LANGDB_ALLOW_EXTERNAL_API", raising=False)
    with pytest.raises(ExternalAPIForbidden):
        require_external_api_permission("test")


def test_ai_client_refuses_without_permission(monkeypatch, tmp_path):
    monkeypatch.delenv("LANGDB_ALLOW_EXTERNAL_API", raising=False)
    from scripts.external_api_guard import ExternalAPIForbidden
    from scripts.phase1_4.ai import BatchAI
    ai = BatchAI("judge", "judge")
    with pytest.raises(ExternalAPIForbidden):
        ai._post("hello")


def test_owner_variable_is_not_set_in_repo_or_ci():
    for p in list(BASE.rglob("*.sh")) + list(BASE.rglob("*.yml")) + list(BASE.rglob("*.yaml")):
        if ".venv" in p.parts:
            continue
        assert "I_AM_THE_OWNER_AND_APPROVE_COSTS" not in p.read_text(errors="ignore"), p
