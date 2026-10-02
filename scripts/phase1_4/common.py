"""
scripts/phase1_4/common.py
Shared helpers for Phase 1.4 (curated corpus expansion).

Determinism rules:
- No wall-clock timestamps in canonical output (a fixed PHASE_TS is used).
- All iteration orders are explicit sorts; IDs are pure functions of semantic keys.
"""

import hashlib
import json
import re
import unicodedata
from pathlib import Path
from typing import Any, Dict, Iterable, List

BASE_DIR = Path(__file__).resolve().parent.parent.parent
CANONICAL_DIR = BASE_DIR / "data" / "canonical"
RAW_DIR = BASE_DIR / "data" / "raw"
P14_DIR = BASE_DIR / "data" / "phase1_4"          # intermediate, committed (small) artifacts
AI_CACHE_DIR = BASE_DIR / "data" / "ai" / "phase1_4"
REPORTS_DIR = BASE_DIR / "reports" / "phase1_4"

PHASE_TS = "2026-10-02T00:00:00Z"
BASELINE_SHA = "a07f61e1f9d55da7ef5d06e6a8bd54f904fbd75c"


def read_jsonl(path: Path) -> List[Dict[str, Any]]:
    out = []
    if not Path(path).exists():
        return out
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                out.append(json.loads(line))
    return out


def write_jsonl(path: Path, rows: Iterable[Dict[str, Any]]) -> int:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    n = 0
    with open(path, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False, sort_keys=False) + "\n")
            n += 1
    return n


def write_json(path: Path, obj: Any) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2, sort_keys=True)
        f.write("\n")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def sha8(text: str, n: int = 8) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:n]


def nfc(s: str) -> str:
    return unicodedata.normalize("NFC", s).strip()


def slug(s: str) -> str:
    """ASCII id-safe slug (lowercase). Non-ascii letters are dropped, so callers must
    add a hash suffix when uniqueness matters."""
    s = unicodedata.normalize("NFKD", s.lower())
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s or "x"


def baseline_expressions():
    """Expressions of the SEALED Phase 1.3D baseline only (verified byte prefix of the append-only file).
    Match-before-create must index the baseline, never Phase 1.4 output, or rebuilds would feed back on themselves."""
    man = json.loads((BASE_DIR / "data/releases/phase1_3d-sealed/baseline_manifest.json").read_text())
    n = man["append_only"]["expressions.jsonl"]["lines"]
    return read_jsonl(CANONICAL_DIR / "expressions.jsonl")[:n]


def is_core_sense(en: Dict[str, Any], ja: Dict[str, Any]) -> bool:
    """Curriculum lists (NGSL/NAWL/BSL/TSL, JLPT, vn_freq) are LEMMA-level. They may be projected onto a concept only
    if that concept is a core (leading) sense of the lemma; otherwise 'death' = Grim Reaper would inherit CEFR A2.
    Core = Wiktionary sense among the first two of its POS entry (or a JMdict-anchored exact first-gloss match),
    and the matching JMdict sense is among the first two senses of the Japanese entry."""
    if ja["sense_idx"] > 1:
        return False
    if en.get("anchor") == "jmdict":
        return ja["gloss_score"] >= 3
    m = re.fullmatch(r"s(\d+)", en.get("wikt_sense") or "")
    return bool(m) and int(m.group(1)) <= 1


def validation_overrides():
    """Independent-review promotions (Luna T1 ACCEPT/HIGH) layered on top of the sealed correction records."""
    p = P14_DIR / "validation_overrides.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}
