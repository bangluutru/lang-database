"""
scripts/phase1_4/gen_vi.py
AI-assisted Vietnamese candidate generation (generator = gemini-2.5-flash) for candidates whose
EN-JA pair is validated but whose Vietnamese form is missing or was rejected by the judge.

Output provenance is ALWAYS AI_GENERATED. The generator's confidence/rationale is stored for audit
but is never shown to the judge (blind judging is preserved).
"""
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from scripts.phase1_4.ai import BatchAI

PROMPT_VERSION = "p14_vi_gen_v1"

HEADER = """You are a professional English/Japanese -> Vietnamese lexicographer building a learner dictionary.
For EACH item give the single most natural, standard, modern Vietnamese equivalent of the stated SENSE
(not of the English word in general). Rules:
- Match the part of speech (verb -> verb, noun -> noun, adjective -> adjective ...).
- Prefer the everyday word a native speaker would use; do not use archaic, dialect-only, or over-literal calques.
- Keep it as short as natural (1-4 syllables-words). Do not add explanations inside vi_lemma.
- If the sense has no good single-expression Vietnamese equivalent, return vi_lemma = null.
- Never copy a form listed in "avoid" (it was already found unsuitable).
- synonyms: at most ONE other fully acceptable equivalent for the same sense, else [].
- definition_vi: one short Vietnamese sentence defining this sense.
Return ONLY JSON: {"results":[{"id":"..","vi_lemma":"..|null","synonyms":[],"definition_vi":"..","confidence":"HIGH|MEDIUM|LOW","rationale":".."}]}
ITEMS:
"""


def build_prompt(items: List[Dict[str, Any]]) -> str:
    rows = [{k: it.get(k) for k in ("id", "en", "en_pos", "en_sense", "ja", "ja_reading", "ja_glosses", "avoid")} for it in items]
    return HEADER + json.dumps(rows, ensure_ascii=False, indent=0)


def to_item(cand: Dict[str, Any], avoid: List[str]) -> Dict[str, Any]:
    return {"id": cand["cand_id"], "en": cand["en"]["lemma"], "en_pos": cand["en"]["pos"],
            "en_sense": cand["en"]["wikt_gloss"][:300], "ja": cand["ja"]["lemma"],
            "ja_reading": cand["ja"]["reading"], "ja_glosses": cand["ja"]["jm_glosses"][:6], "avoid": sorted(avoid)}


def generate(items: List[Dict[str, Any]], workers: int = 8, offline: bool = False):
    ai = BatchAI("generator", "gen_vi")
    out = ai.call_items(items, PROMPT_VERSION, build_prompt, batch_size=20, workers=workers, offline=offline)
    return out, ai.provenance(items, PROMPT_VERSION)
