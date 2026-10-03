"""
scripts/phase1_4/route.py
Quality-gate routing: turns (candidate, judge results, AI-VI proposals) into one of

    ACCEPT_TRI_SOURCE   all three languages, VI from Wiktionary sense block, judge-validated
    ACCEPT_TRI_AI       all three languages, VI AI-generated (provenance AI_GENERATED), judge-validated
    ACCEPT_PARTIAL_ENJA EN+JA validated, VI absent/unresolved (legitimate partial concept)
    REVIEW              plausible but not auto-acceptable -> human review queue (NOT in canonical)
    REJECT              semantic rejection (kept in rejection log, NOT in canonical)

Origin (provenance) and validation are separate dimensions: this module only decides validation
routing; it never changes where a lexical form came from.
"""

import json
from typing import Any, Dict, List, Optional, Tuple

from scripts.phase1_4 import judge as J

MIN_TRI_VALUE = 10        # tri-language candidates (VI from source) - minimum learning value
MIN_PARTIAL_VALUE = 30    # EN-JA-only partials - higher bar (no VI to add utility)
MIN_AI_VI_VALUE = 30      # AI-generated VI is only attempted for strong curriculum items


def route(cand: Dict[str, Any], results: Dict[str, Any], ai_vi: Dict[str, Any], manual_exclusions=frozenset(), manual_accept=frozenset(), gemini_accept=frozenset()) -> Tuple[str, Dict[str, Any]]:
    if cand["cand_id"] in manual_exclusions:      # human/agent review overrides any automatic acceptance
        return "REVIEW", {"cand_id": cand["cand_id"], "manual_review": "excluded by manual review"}
    cid = cand["cand_id"]
    value = cand["value"]["total"]
    info: Dict[str, Any] = {"cand_id": cid, "value": value}
    if cid in manual_accept or cid in gemini_accept:   # Phase 1.4.2: independent model ACCEPT + Claude confirmation (claude_review_T3.json = Luna, claude_review_G3.json = Gemini)
        info["independent_review"] = ({"reviewers": ["gemini-3.8", "claude"], "basis": "G3_handoff_review"} if cid in gemini_accept
                                      else {"reviewers": ["gpt-6-luna", "claude"], "basis": "T3_handoff_review"})
        if cand.get("vi"):
            info["judge_tri"] = results.get("tri", {}).get(cid) or {}
            return "ACCEPT_TRI_SOURCE", info
        info["judge_enja"] = results.get("enja", {}).get(cid) or {}
        return "ACCEPT_PARTIAL_ENJA", info
    tri = results.get("tri", {}).get(cid)
    enja = results.get("enja", {}).get(cid)
    recheck = results.get("recheck", {}).get(cid)
    tri_ai = results.get("tri_ai", {}).get(cid)

    if cand.get("vi"):
        if tri is None:
            return "UNJUDGED", info
        info["judge_tri"] = tri
        if J.is_accept_tri(tri) and value >= MIN_TRI_VALUE:
            return "ACCEPT_TRI_SOURCE", info
        # tri failed: was it the VI or the EN-JA pair?
        if tri.get("en_ja") == "OK" and recheck is not None:
            info["judge_enja_recheck"] = recheck
            if J.is_accept_en_ja(recheck) and value >= MIN_PARTIAL_VALUE:
                info["vi_rejected"] = {"lemma": cand["vi"]["lemma"], "reason": tri.get("issues"), "note": tri.get("note")}
                return "ACCEPT_PARTIAL_ENJA", info
        if tri.get("verdict") == "REJECT" or tri.get("en_ja") in ("WRONG",):
            return "REJECT", info
        return "REVIEW", info
    # no source VI
    if enja is None:
        return "UNJUDGED", info
    info["judge_enja"] = enja
    if not J.is_accept_en_ja(enja):
        return ("REJECT" if enja.get("en_ja") == "WRONG" or enja.get("verdict") == "REJECT" else "REVIEW"), info
    if value < MIN_PARTIAL_VALUE:
        return "BELOW_VALUE_THRESHOLD", info
    gen = ai_vi.get(cid)
    if gen and tri_ai is not None:
        info["ai_vi"] = gen
        info["judge_tri_ai"] = tri_ai
        if J.is_accept_tri(tri_ai):
            return "ACCEPT_TRI_AI", info
        info["ai_vi_rejected"] = {"lemma": gen.get("vi_lemma"), "note": tri_ai.get("note"), "issues": tri_ai.get("issues")}
    return "ACCEPT_PARTIAL_ENJA", info
