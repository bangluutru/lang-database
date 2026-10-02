"""
scripts/phase1_4/judge.py
Blind, batched, PAIRWISE linguistic judge for Phase 1.4 (model: gemini-2.5-pro).

Blindness: the judge receives only linguistic facts (lemmas, readings, POS, English sense
definition, JMdict glosses). It never receives where a candidate came from, its curriculum
score, whether a Vietnamese form is source-derived or AI-generated, or any desired outcome.

Pairwise output lets the pipeline route precisely: a bad VI form does not poison a good EN-JA
pair (-> partial concept) and a bad EN-JA pair is never rescued by a plausible VI.
"""

import sys
from pathlib import Path
from typing import Any, Dict, List

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from scripts.phase1_4.ai import BatchAI

PROMPT_VERSION = "p14_judge_v1"

HEADER = """You are an independent senior bilingual lexicographer reviewing entries of an English-Japanese-Vietnamese
learner vocabulary database. For EACH item decide whether the three expressions denote the SAME SPECIFIC SENSE.

Item fields:
- en: English lemma, en_pos, en_sense: the intended English sense (a dictionary definition)
- ja: Japanese lemma (+reading), ja_pos (JMdict tags), ja_glosses: English glosses of the Japanese word's matching sense
- vi: Vietnamese lemma, or null (then judge ONLY the EN-JA pair)

Judge each PAIR separately:
- en_ja / en_vi / ja_vi : "OK" (same sense, a competent translator would use this equivalent),
  "BROAD" (target covers more than the sense), "NARROW" (target covers only part / more specific),
  "WRONG" (different meaning, false friend, wrong POS, or only a distant association), "NA" (vi is null).
Then overall:
- naturalness: "NATURAL" | "ACCEPTABLE" | "AWKWARD" | "WRONG"  (is each expression the idiomatic, current, standard one a learner should be taught for this sense? penalise archaic, rare, dialect-only, or over-literal forms)
- register: "MATCH" | "MINOR_MISMATCH" | "MAJOR_MISMATCH"
- pos_ok: true/false (parts of speech are compatible across the three)
- verdict: "ACCEPT" (all pairs OK, natural, suitable as a canonical teaching equivalent) | "REVIEW" (plausible but needs a human) | "REJECT"
- confidence: "HIGH" | "MEDIUM" | "LOW"
- issues: list from [SENSE_DIVERGENCE, FALSE_FRIEND, POS_MISMATCH, REGISTER_CLASH, ARCHAIC_OR_RARE, TOO_BROAD, TOO_NARROW, UNNATURAL_VI, UNNATURAL_JA, NOT_A_TRANSLATION_OF_THIS_SENSE, PROPER_NOUN_OR_TRANSLITERATION_ONLY, MULTIPLE_SENSES_COLLAPSED]
- note: one short sentence.

Be strict. A Sino-Vietnamese or transliterated form is acceptable only if it is the normal modern word for this exact sense.
Polysemous English words: judge only the stated English sense. Do not give credit for a different sense of any word.

Return ONLY JSON: {"results":[{"id":"...","en_ja":"..","en_vi":"..","ja_vi":"..","naturalness":"..","register":"..","pos_ok":true,"verdict":"..","confidence":"..","issues":[],"note":".."}]}
Return exactly one result per input item, using the same id.

ITEMS:
"""


def build_prompt(items: List[Dict[str, Any]]) -> str:
    import json
    rows = []
    for it in items:
        rows.append({k: it[k] for k in ("id", "en", "en_pos", "en_sense", "ja", "ja_reading", "ja_pos",
                                         "ja_glosses", "vi")})
    return HEADER + json.dumps(rows, ensure_ascii=False, indent=0)


def to_item(cand: Dict[str, Any], vi_lemma: Any = "USE_CANDIDATE") -> Dict[str, Any]:
    vi = cand["vi"]["lemma"] if (vi_lemma == "USE_CANDIDATE" and cand.get("vi")) else (None if vi_lemma == "USE_CANDIDATE" else vi_lemma)
    return {
        "id": cand["cand_id"],
        "en": cand["en"]["lemma"],
        "en_pos": cand["en"]["pos"],
        "en_sense": cand["en"]["wikt_gloss"][:300],
        "ja": cand["ja"]["lemma"],
        "ja_reading": cand["ja"]["reading"],
        "ja_pos": ",".join(cand["ja"]["jm_pos_tags"]),
        "ja_glosses": cand["ja"]["jm_glosses"][:6],
        "vi": vi,
    }


def judge_items(items: List[Dict[str, Any]], offline: bool = False, workers: int = 6) -> Dict[str, Dict[str, Any]]:
    ai = BatchAI("judge", "judge")
    return ai.call_items(items, PROMPT_VERSION, build_prompt, batch_size=12, workers=workers, offline=offline)


def is_accept_tri(r: Dict[str, Any]) -> bool:
    return (r.get("verdict") == "ACCEPT" and r.get("confidence") == "HIGH" and r.get("naturalness") == "NATURAL"
            and r.get("en_ja") == "OK" and r.get("en_vi") == "OK" and r.get("ja_vi") == "OK"
            and r.get("pos_ok") is True and r.get("register") in ("MATCH", "MINOR_MISMATCH"))


def is_accept_en_ja(r: Dict[str, Any]) -> bool:
    return (r.get("en_ja") == "OK" and r.get("pos_ok") is True and r.get("naturalness") in ("NATURAL", "ACCEPTABLE")
            and r.get("confidence") in ("HIGH", "MEDIUM") and r.get("register") in ("MATCH", "MINOR_MISMATCH"))
