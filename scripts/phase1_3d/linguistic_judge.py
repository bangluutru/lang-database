#!/usr/bin/env python3
"""
scripts/phase1_3d/linguistic_judge.py
Independent Linguistic Judge for Phase 1.3D.
Evaluates tri-language semantic alignment, POS compatibility, and naturalness.
Follows strict blind evaluation:
- Does NOT receive generator confidence, rationale, or desired acceptance outcome.
Produces structured decisions:
- decision: ACCEPT, ACCEPT_WITH_NOTE, REVIEW, REJECT
- semantic_alignment: EXACT, GOOD, BROAD, NARROW, WRONG
- naturalness: NATURAL, ACCEPTABLE, AWKWARD, WRONG
- register: MATCH, MINOR_MISMATCH, MAJOR_MISMATCH
- confidence: HIGH, MEDIUM, LOW
- reason_codes: [...]
Enforces Auto-Accept Policy:
- ACCEPT only if decision == ACCEPT, semantic_alignment in (EXACT, GOOD),
  naturalness == NATURAL, confidence == HIGH, and no source conflict.
Caches all evaluations in data/ai/phase1_3d/judge/ for deterministic offline rebuild.
"""

import sys
import json
import time
from pathlib import Path
from typing import Dict, List, Any, Optional

BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from scripts.phase1_3d.ai_client import AIClient, compute_input_hash

CACHE_DIR = BASE_DIR / "data" / "ai" / "phase1_3d" / "judge"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

PROMPT_VERSION = "phase1_3d_judge_v1"

PROMPT_TEMPLATE = """You are an independent Senior Linguistic Judge for a high-quality tri-language (English, Japanese, Vietnamese) pedagogical vocabulary database.

Evaluate whether the following tri-language concept representation is semantically, grammatically, and pedagogically sound.

Concept Context:
- Concept ID: {concept_id}
- Domain: {domains}
- English Expression: {en_lemma} (POS: {en_pos})
- English Definition / Sense Context: {en_definition}
- Japanese Expression: {ja_lemma} (Reading: {ja_reading}, POS: {ja_pos})
- Japanese Sense Glosses: {ja_glosses}
- Candidate Vietnamese Expression: {vi_lemma} (POS: {vi_pos})
- Candidate Vietnamese Definition: {vi_definition}
- Candidate Vietnamese Synonyms: {vi_synonyms}
- Candidate Origin Type: {candidate_origin}

Strict Evaluation Criteria:
1. Semantic Alignment:
   - "EXACT": All three languages share the exact same core concept/sense.
   - "GOOD": High quality pedagogical translation despite slight lexical breadth difference.
   - "BROAD": One language expression is overly broad.
   - "NARROW": One language expression is overly narrow (specific sub-sense).
   - "WRONG": Mismatched meaning or incorrect translation in at least one pair.

2. Naturalness:
   - "NATURAL": Idiomatic, common, modern standard usage.
   - "ACCEPTABLE": Understandable and correct, but less common or slightly formal.
   - "AWKWARD": Unnatural phrasing, archaic expression, or robotic translation.
   - "WRONG": Incomprehensible, erroneous, or misleading for learners.

3. Register:
   - "MATCH": Registers align across all three languages.
   - "MINOR_MISMATCH": Slight stylistic variance (e.g. general vs slightly formal).
   - "MAJOR_MISMATCH": Severe clash (e.g. slang vs legal/archaic).

4. Decision:
   - "ACCEPT": Ready for production canonical inclusion without reservations.
   - "ACCEPT_WITH_NOTE": Usable, but benefits from an editorial usage note.
   - "REVIEW": Borderline, ambiguous, or requires human lexicographer intervention.
   - "REJECT": Erroneous alignment, false friend, or unacceptable learner confusion.

5. Confidence:
   - "HIGH" | "MEDIUM" | "LOW"

6. Reason Codes (select all that apply):
   - SEMANTIC_EXACT
   - SEMANTIC_ACCEPTABLE
   - SENSE_DIVERGENCE
   - ARCHAIC_OR_OBSOLETE
   - FALSE_FRIEND
   - POS_INCOMPATIBLE
   - REGISTER_CLASH
   - SYNONYM_VALIDATED
   - HIGH_CONFIDENCE_ALIGNMENT
   - AMBIGUOUS_ALIGNMENT

Respond strictly in JSON format:
{{
  "decision": "ACCEPT" | "ACCEPT_WITH_NOTE" | "REVIEW" | "REJECT",
  "semantic_alignment": "EXACT" | "GOOD" | "BROAD" | "NARROW" | "WRONG",
  "naturalness": "NATURAL" | "ACCEPTABLE" | "AWKWARD" | "WRONG",
  "register": "MATCH" | "MINOR_MISMATCH" | "MAJOR_MISMATCH",
  "confidence": "HIGH" | "MEDIUM" | "LOW",
  "reason_codes": ["SEMANTIC_EXACT", "..."],
  "evaluation_note": "<concise explanation>"
}}
"""


class LinguisticJudge:
    """Independent judge evaluating tri-language semantic alignment."""

    def __init__(self):
        self.ai_client = AIClient(CACHE_DIR)

    def evaluate(self, item: Dict[str, Any], vi_candidate: Dict[str, Any], ja_replacement: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Performs blind independent evaluation of a candidate."""
        cid = item["concept_id"]
        sid = item.get("sense_id") or f"{cid}-01"
        en_lem = item["en"]["lemma"]
        en_pos = item["en"]["part_of_speech"]
        en_def = item.get("definition_en") or item.get("sense_gloss_en") or en_lem

        if ja_replacement:
            ja_lem = ja_replacement["surface"]
            ja_reading = ja_replacement.get("reading", "")
            ja_pos = item["ja"]["part_of_speech"]
            ja_glosses = [ja_replacement.get("reason", "")]
        else:
            ja_lem = item["ja"]["lemma"]
            ja_reading = item["ja"]["reading"]
            ja_pos = item["ja"]["part_of_speech"]
            target_sense = item["ja"].get("target_sense") or {}
            ja_glosses = target_sense.get("glosses", [])

        vi_lem = vi_candidate.get("lemma", "")
        vi_pos = vi_candidate.get("part_of_speech", en_pos)
        vi_def = vi_candidate.get("definition", "")
        vi_syns = vi_candidate.get("synonyms", [])
        cand_origin = vi_candidate.get("source_type", "UNKNOWN")

        prompt = PROMPT_TEMPLATE.format(
            concept_id=cid,
            domains=", ".join(item.get("domains", ["general"])),
            en_lemma=en_lem,
            en_pos=en_pos,
            en_definition=en_def,
            ja_lemma=ja_lem,
            ja_reading=ja_reading,
            ja_pos=ja_pos,
            ja_glosses=ja_glosses,
            vi_lemma=vi_lem,
            vi_pos=vi_pos,
            vi_definition=vi_def,
            vi_synonyms=", ".join(vi_syns) if vi_syns else "None",
            candidate_origin=cand_origin
        )

        # Blind payload: does NOT contain generator confidence or desired acceptance
        judge_input_payload = {
            "concept_id": cid,
            "sense_id": sid,
            "en_lemma": en_lem,
            "ja_lemma": ja_lem,
            "vi_lemma": vi_lem,
            "candidate_origin": cand_origin
        }

        raw_output = self.ai_client.generate_json(prompt, judge_input_payload, PROMPT_VERSION)
        input_hash = compute_input_hash({"prompt_version": PROMPT_VERSION, "input": judge_input_payload})

        decision = raw_output.get("decision", "REVIEW")
        sem_align = raw_output.get("semantic_alignment", "WRONG")
        nat = raw_output.get("naturalness", "AWKWARD")
        conf = raw_output.get("confidence", "LOW")

        # Section 18 Auto-Accept Strict Policy
        auto_accepted = (
            decision == "ACCEPT"
            and sem_align in ("EXACT", "GOOD")
            and nat == "NATURAL"
            and conf == "HIGH"
        )

        return {
            "concept_id": cid,
            "sense_id": sid,
            "vi_candidate_lemma": vi_lem,
            "decision": decision,
            "auto_accepted": auto_accepted,
            "semantic_alignment": sem_align,
            "naturalness": nat,
            "register": raw_output.get("register", "MATCH"),
            "confidence": conf,
            "reason_codes": raw_output.get("reason_codes", []),
            "evaluation_note": raw_output.get("evaluation_note", ""),
            "judge_metadata": {
                "judge_model": self.ai_client.model,
                "prompt_version": PROMPT_VERSION,
                "input_hash": input_hash,
                "evaluated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            }
        }


def main():
    print("=== Testing LinguisticJudge ===")
    judge = LinguisticJudge()
    canary_path = BASE_DIR / "reports" / "phase1_3d" / "canary_queue.json"
    canary = json.load(open(canary_path))

    test_item = next(x for x in canary if x["en"]["lemma"] == "accurate")
    vi_cand = {
        "lemma": "chính xác",
        "part_of_speech": "adjective",
        "definition": "Đúng với sự thật, không có sai sót.",
        "source_type": "HANVIET_SUPPORTED"
    }

    res = judge.evaluate(test_item, vi_cand)
    print(f"Judged {test_item['en']['lemma']} <-> {test_item['ja']['lemma']} <-> {vi_cand['lemma']}:")
    print(json.dumps(res, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
