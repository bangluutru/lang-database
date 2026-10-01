#!/usr/bin/env python3
"""
scripts/phase1_3d/ai_candidate_generator.py
AI Candidate Translation Generator for Phase 1.3D.
Invoked ONLY when source lookup fails (NO_SOURCE_MATCH) or encounters conflicting/false-friend sources.
Proposes:
- Primary Vietnamese lemma
- Synonyms (0..n)
- Vietnamese definition / gloss
- POS and register
- Sense distinction
Outputs are permanently tagged with provenance_type = "AI_GENERATED" and full execution metadata.
Responses are cached in data/ai/phase1_3d/generation/ for deterministic offline rebuild.
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

CACHE_DIR = BASE_DIR / "data" / "ai" / "phase1_3d" / "generation"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

PROMPT_VERSION = "phase1_3d_vi_gen_v1"

PROMPT_TEMPLATE = """You are an expert bilingual lexicographer specializing in English, Japanese, and Vietnamese vocabulary for language learners.

Generate natural, accurate Vietnamese translations for the following learning concept.

Context:
- Concept ID: {concept_id}
- Domain: {domains}
- English Lemma: {en_lemma} (POS: {en_pos})
- English Definition / Context: {en_definition}
- Japanese Expression: {ja_lemma} (Reading: {ja_reading}, POS: {ja_pos})
- Japanese Sense Glosses: {ja_glosses}

Requirements:
1. Provide the single most natural, high-frequency, standard modern Vietnamese word/phrase as primary_lemma.
2. Provide valid modern Vietnamese synonyms (0 to 3) if applicable.
3. Provide a clear, natural learner definition in Vietnamese.
4. Provide the appropriate Vietnamese part of speech (noun, verb, adjective, adverb).
5. Specify register (general, formal, informal, technical).
6. If the term has significant polysemy, provide a brief sense_distinction note.

Respond strictly in JSON format:
{{
  "primary_lemma": "<main Vietnamese expression>",
  "synonyms": ["<synonym 1>", "<synonym 2>"],
  "part_of_speech": "noun" | "verb" | "adjective" | "adverb",
  "definition_vi": "<clear concise definition in Vietnamese>",
  "register": "general" | "formal" | "informal" | "technical",
  "sense_distinction": "<brief note clarifying this exact sense>"
}}
"""


class AiCandidateGenerator:
    """Generates Vietnamese candidate translations with strict provenance metadata."""

    def __init__(self):
        self.ai_client = AIClient(CACHE_DIR)

    def generate(self, item: Dict[str, Any], ja_replacement: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generates Vietnamese candidates for an item lacking source match."""
        cid = item["concept_id"]
        sid = item.get("sense_id") or f"{cid}-01"
        en_lem = item["en"]["lemma"]
        en_pos = item["en"]["part_of_speech"]
        en_def = item.get("definition_en") or item.get("sense_gloss_en") or en_lem

        # Use replacement JA if available
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

        prompt = PROMPT_TEMPLATE.format(
            concept_id=cid,
            domains=", ".join(item.get("domains", ["general"])),
            en_lemma=en_lem,
            en_pos=en_pos,
            en_definition=en_def,
            ja_lemma=ja_lem,
            ja_reading=ja_reading,
            ja_pos=ja_pos,
            ja_glosses=ja_glosses
        )

        input_payload = {
            "concept_id": cid,
            "sense_id": sid,
            "en": item["en"],
            "ja": item["ja"],
            "ja_replacement": ja_replacement
        }

        raw_output = self.ai_client.generate_json(prompt, input_payload, PROMPT_VERSION)
        input_hash = compute_input_hash({"prompt_version": PROMPT_VERSION, "input": input_payload})

        # Build candidate object with immutable provenance metadata
        timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        candidates = []

        primary_lemma = raw_output.get("primary_lemma", "").strip()
        if primary_lemma:
            candidates.append({
                "lemma": primary_lemma,
                "part_of_speech": raw_output.get("part_of_speech", en_pos),
                "definition": raw_output.get("definition_vi", f"Định nghĩa: {primary_lemma}"),
                "register": raw_output.get("register", "general"),
                "is_primary": True,
                "source_type": "AI_CANDIDATE",
                "provenance_type": "AI_GENERATED",
                "provenance_metadata": {
                    "origin": "AI_GENERATED",
                    "model": self.ai_client.model,
                    "prompt_version": PROMPT_VERSION,
                    "input_hash": input_hash,
                    "concept_id": cid,
                    "sense_id": sid,
                    "generated_at": timestamp
                }
            })

        for syn in raw_output.get("synonyms", []):
            syn_str = syn.strip()
            if syn_str and syn_str != primary_lemma:
                candidates.append({
                    "lemma": syn_str,
                    "part_of_speech": raw_output.get("part_of_speech", en_pos),
                    "definition": raw_output.get("definition_vi", f"Từ đồng nghĩa: {syn_str}"),
                    "register": raw_output.get("register", "general"),
                    "is_primary": False,
                    "source_type": "AI_SYNONYM",
                    "provenance_type": "AI_GENERATED",
                    "provenance_metadata": {
                        "origin": "AI_GENERATED",
                        "model": self.ai_client.model,
                        "prompt_version": PROMPT_VERSION,
                        "input_hash": input_hash,
                        "concept_id": cid,
                        "sense_id": sid,
                        "generated_at": timestamp
                    }
                })

        return {
            "concept_id": cid,
            "sense_id": sid,
            "status": "AI_GENERATED",
            "candidates": candidates,
            "sense_distinction": raw_output.get("sense_distinction", ""),
            "input_hash": input_hash
        }


def main():
    print("=== Testing AiCandidateGenerator ===")
    gen = AiCandidateGenerator()
    canary_path = BASE_DIR / "reports" / "phase1_3d" / "canary_queue.json"
    canary = json.load(open(canary_path))

    test_item = next(x for x in canary if x["en"]["lemma"] == "ability")
    res = gen.generate(test_item)
    print(f"Generated for {test_item['en']['lemma']}:")
    for c in res["candidates"]:
        print(f"  {c['lemma']} (primary={c['is_primary']}) - {c['definition']}")


if __name__ == "__main__":
    main()
