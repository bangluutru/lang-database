"""
scripts/external_api_guard.py
PROJECT RULE (see CLAUDE.md / AGENTS.md): NO PAID / EXTERNAL LLM API CALLS.

Any code path that would contact an external model API (Vertex AI, Gemini, OpenAI, Anthropic API, ...) must call
`require_external_api_permission()` first. It raises unless the *human owner* has explicitly enabled it by setting
LANGDB_ALLOW_EXTERNAL_API=I_AM_THE_OWNER_AND_APPROVE_COSTS in the environment for that single command.
Coding agents must NEVER set this variable themselves. Use the LLM you already are (read the data, judge it yourself,
write the result into the repo) or the cached artefacts in data/ai/.
"""
import os

TOKEN = "I_AM_THE_OWNER_AND_APPROVE_COSTS"


class ExternalAPIForbidden(RuntimeError):
    pass


def require_external_api_permission(what: str = "external LLM API") -> None:
    if os.environ.get("LANGDB_ALLOW_EXTERNAL_API") != TOKEN:
        raise ExternalAPIForbidden(
            f"Blocked: {what}. This project forbids external/paid API calls (see CLAUDE.md). "
            "Work from cached artefacts in data/ai/ or review the data yourself as the coding agent. "
            "Only the human owner may enable calls, per command, via LANGDB_ALLOW_EXTERNAL_API.")
