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


ABSENT_KEY = "__absent__"


def ledger():
    return json.loads((BASE_DIR / "reports" / "phase1_4" / "baseline_corrections_ledger.json").read_text(encoding="utf-8"))["entries"]


def reverted_prefix_bytes(name):
    """Current baseline prefix of canonical/<name>.jsonl with the Phase 1.4.1 ledger reverted (old values restored).
    Must equal the sealed Phase 1.3D bytes."""
    info = manifest()["append_only"][f"{name}.jsonl"]
    keyf = {"concepts": "concept_id", "senses": "sense_id", "expressions": "expression_id", "classifications": "classification_id"}.get(name)
    rows = baseline_rows(name)
    if keyf:
        by = {r[keyf]: r for r in rows}
        for e in reversed([x for x in ledger() if x["file"] == name]):
            r = by[e["id"]]
            if isinstance(e["old"], dict) and e["old"].get(ABSENT_KEY):
                r.pop(e["field"], None)
            else:
                r[e["field"]] = e["old"]
    return "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows).encode("utf-8")
