"""Helpers: the sealed Phase 1.3D baseline as a *subset* of the (growing) canonical corpus."""
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
CANONICAL_DIR = BASE_DIR / "data" / "canonical"
MANIFEST = BASE_DIR / "data" / "releases" / "phase1_3d-sealed" / "baseline_manifest.json"


def manifest():
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def baseline_rows(name):
    """Rows of canonical/<name>.jsonl that belong to the sealed baseline (the verified byte prefix)."""
    n = manifest()["append_only"][f"{name}.jsonl"]["lines"]
    out = []
    with open(CANONICAL_DIR / f"{name}.jsonl", "r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            if i >= n:
                break
            if line.strip():
                out.append(json.loads(line))
    return out


def baseline_concept_ids():
    return {c["concept_id"] for c in baseline_rows("concepts")}
