#!/usr/bin/env python3
"""
scripts/phase1_3d/en_ja_validator.py
First Gate: Validates English-Japanese semantic alignment and POS compatibility
using full JMdict entry context and an independent bilingual evaluator.
Classifies pairs as EXACT, GOOD, BROAD, NARROW, AMBIGUOUS, WRONG.
Proposes verifiable JMdict replacements for WRONG alignments.
Caches all evaluations in data/ai/phase1_3d/en_ja_alignment/ for deterministic offline rebuild.
"""

import json
import gzip
import re
import sys
from pathlib import Path

from typing import Dict, List, Any, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
import xml.etree.ElementTree as ET

BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from scripts.phase1_3d.ai_client import AIClient, compute_input_hash

BASE_DIR = Path(__file__).resolve().parent.parent.parent
CACHE_DIR = BASE_DIR / "data" / "ai" / "phase1_3d" / "en_ja_alignment"
CACHE_DIR.mkdir(parents=True, exist_ok=True)
JMDICT_PATH = BASE_DIR / "data" / "raw" / "jmdict" / "2026-10-01" / "JMdict_e.gz"

PROMPT_VERSION = "phase1_3d_en_ja_v2"

PROMPT_TEMPLATE = """You are a rigorous bilingual lexicographer evaluating English-Japanese alignment for a tri-language learning vocabulary database.

Evaluate whether the English lemma and the Japanese expression are semantically and grammatically aligned.

Context:
- Concept ID: {concept_id}
- Domain: {domains}
- English Lemma: {en_lemma} (Assigned POS: {en_pos})
- Japanese Surface: {ja_lemma} (Reading: {ja_reading}, Assigned POS: {ja_pos})
- JMdict Target Sense Glosses: {ja_glosses}
- JMdict Misc Tags: {ja_misc}
- All JMdict Entry Senses: {all_senses_summary}

Evaluation Guidelines:
1. POS Alignment:
   - "exact": direct match (noun<->noun, verb<->verb, adj<->adj)
   - "compatible": functionally equivalent (noun<->verbal noun, adj<->adjectival noun na/no, adv<->adv)
   - "mismatch": grammatical conflict (e.g. English verb aligned to pure Japanese noun, or vice-versa)

2. Semantic Alignment:
   - "EXACT": Same lexical sense with strong semantic equivalence for learners.
   - "GOOD": Appropriate learner translation despite minor lexical nuance or slight breadth difference.
   - "BROAD": Japanese expression is substantially broader than the English sense.
   - "NARROW": Japanese expression is substantially narrower than the English sense (e.g. specific technical, musical, or medical sub-sense only).
   - "AMBIGUOUS": Insufficient evidence to determine correct sense.
   - "WRONG": Different meaning, archaic/spurious false match (e.g. 'you' aligned to '真人', 'i' aligned to '寡人'), or abbreviation confusion (e.g. 'ad' aligned to '西暦' Anno Domini instead of advertisement).

3. Naturalness for Learners:
   - Is this Japanese word the standard, natural vocabulary term a general language learner would expect for this English concept?

4. Remediation:
   - If EXACT or GOOD: suggested_action = "proceed"
   - If BROAD or NARROW: suggested_action = "proceed" (if appropriate learner fit) or "human_review"
   - If WRONG: suggested_action = "replace_ja_expression" (if a clear common Japanese word exists) or "quarantine"
   - If replace_ja_expression, provide suggested_ja_replacement with surface and reading.

Respond strictly in JSON format:
{{
  "pos_alignment": "exact" | "compatible" | "mismatch",
  "semantic_alignment": "EXACT" | "GOOD" | "BROAD" | "NARROW" | "AMBIGUOUS" | "WRONG",
  "is_natural_for_learner": true | false,
  "suggested_action": "proceed" | "replace_ja_expression" | "quarantine" | "human_review",
  "reason": "<clear explanation>",
  "suggested_ja_replacement": {{ "surface": "...", "reading": "...", "reason": "..." }} | null
}}
"""


class EnJaValidator:
    """Validates EN-JA alignments and proposes JMdict-traceable remediations."""

    def __init__(self, max_workers: int = 5):
        self.ai_client = AIClient(CACHE_DIR)
        self.max_workers = max_workers
        self._jmdict_index: Optional[Dict[str, List[Dict[str, Any]]]] = None

    def _ensure_jmdict_index(self):
        """Builds lightweight index of common JMdict entries for finding replacement expressions."""
        if self._jmdict_index is not None:
            return
        index: Dict[str, List[Dict[str, Any]]] = {}
        if not JMDICT_PATH.exists():
            self._jmdict_index = index
            return

        with gzip.open(JMDICT_PATH, "rb") as f:
            for event, elem in ET.iterparse(f, events=["end"]):
                if elem.tag == "entry":
                    seq_el = elem.find("ent_seq")
                    if seq_el is not None and seq_el.text:
                        ent_seq = int(seq_el.text.strip())
                        keb_list = [k.text.strip() for k in elem.findall("k_ele/keb") if k.text]
                        reb_list = [r.text.strip() for r in elem.findall("r_ele/reb") if r.text]
                        primary_surf = keb_list[0] if keb_list else (reb_list[0] if reb_list else "")
                        primary_read = reb_list[0] if reb_list else ""

                        for s_idx, sense_el in enumerate(elem.findall("sense")):
                            glosses = [g.text.strip().lower() for g in sense_el.findall("gloss") if g.text]
                            # Index primary surface and reading
                            if primary_surf:
                                index.setdefault(primary_surf, []).append({
                                    "ent_seq": ent_seq,
                                    "sense_idx": s_idx,
                                    "keb": primary_surf,
                                    "reb": primary_read,
                                    "glosses": glosses
                                })
                            if primary_read and primary_read != primary_surf:
                                index.setdefault(primary_read, []).append({
                                    "ent_seq": ent_seq,
                                    "sense_idx": s_idx,
                                    "keb": primary_surf,
                                    "reb": primary_read,
                                    "glosses": glosses
                                })
                    elem.clear()
        self._jmdict_index = index

    def resolve_jmdict_replacement(self, surface: str, reading: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Resolves replacement surface to verified JMdict ent_seq and sense_idx."""
        self._ensure_jmdict_index()
        candidates = self._jmdict_index.get(surface, [])
        if not candidates and reading:
            candidates = self._jmdict_index.get(reading, [])
        if candidates:
            # Pick first sense
            return candidates[0]
        return None

    def validate_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Validates a single partial concept item."""
        cid = item["concept_id"]
        en_lem = item["en"]["lemma"]
        en_pos = item["en"]["part_of_speech"]
        ja_lem = item["ja"]["lemma"]
        ja_reading = item["ja"]["reading"]
        ja_pos = item["ja"]["part_of_speech"]
        domains = item.get("domains", ["general"])

        target_sense = item["ja"].get("target_sense") or {}
        ja_glosses = target_sense.get("glosses", [])
        ja_misc = target_sense.get("misc", [])

        all_senses = item["ja"].get("all_senses", [])
        all_senses_summary = "; ".join(
            f"[Sense {s.get('sense_index', i)}: {', '.join(s.get('glosses', [])[:2])}]"
            for i, s in enumerate(all_senses[:4])
        )

        prompt = PROMPT_TEMPLATE.format(
            concept_id=cid,
            domains=", ".join(domains),
            en_lemma=en_lem,
            en_pos=en_pos,
            ja_lemma=ja_lem,
            ja_reading=ja_reading,
            ja_pos=ja_pos,
            ja_glosses=ja_glosses,
            ja_misc=ja_misc,
            all_senses_summary=all_senses_summary
        )

        res = self.ai_client.generate_json(prompt, item, PROMPT_VERSION)

        # Build validation record
        val_record = {
            "concept_id": cid,
            "en_lemma": en_lem,
            "en_pos": en_pos,
            "ja_lemma": ja_lem,
            "ja_reading": ja_reading,
            "ja_pos": ja_pos,
            "pos_alignment": res.get("pos_alignment", "compatible"),
            "semantic_alignment": res.get("semantic_alignment", "GOOD"),
            "is_natural_for_learner": res.get("is_natural_for_learner", True),
            "suggested_action": res.get("suggested_action", "proceed"),
            "reason": res.get("reason", ""),
            "suggested_ja_replacement": res.get("suggested_ja_replacement"),
            "resolved_replacement": None
        }

        # Resolve JMdict locator for replacement if applicable
        repl = val_record.get("suggested_ja_replacement")
        if repl and isinstance(repl, dict) and repl.get("surface"):
            jm_res = self.resolve_jmdict_replacement(repl["surface"], repl.get("reading"))
            if jm_res:
                val_record["resolved_replacement"] = {
                    "surface": jm_res["keb"] or repl["surface"],
                    "reading": jm_res["reb"] or repl.get("reading", ""),
                    "ent_seq": jm_res["ent_seq"],
                    "sense_idx": jm_res["sense_idx"],
                    "locator": f"ent_seq:{jm_res['ent_seq']}, sense_idx:{jm_res['sense_idx']}",
                    "reason": repl.get("reason", "")
                }

        return val_record

    def validate_queue(self, queue: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validates all items in the queue with thread pool execution."""
        results = []
        total = len(queue)
        print(f"Starting EN-JA validation for {total} items (concurrency={self.max_workers})...")

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_item = {executor.submit(self.validate_item, item): item for item in queue}
            for idx, future in enumerate(as_completed(future_to_item), 1):
                res = future.result()
                results.append(res)
                if idx % 10 == 0 or idx == total:
                    print(f"Validated {idx}/{total} items...")

        # Sort deterministically by concept_id
        results.sort(key=lambda x: x["concept_id"])
        return results


def main():
    print("=== Testing EnJaValidator ===")
    canary_path = BASE_DIR / "reports" / "phase1_3d" / "canary_queue.json"
    if not canary_path.exists():
        print(f"Canary queue missing: {canary_path}")
        return

    with open(canary_path, "r", encoding="utf-8") as f:
        canary = json.load(f)

    validator = EnJaValidator(max_workers=5)
    # Test on first 10
    sample = canary[:10]
    results = validator.validate_queue(sample)
    for r in results:
        print(f"[{r['concept_id']}] {r['en_lemma']} <-> {r['ja_lemma']}: {r['semantic_alignment']} ({r['pos_alignment']}) -> {r['suggested_action']}")


if __name__ == "__main__":
    main()
