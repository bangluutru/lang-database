import json, subprocess, sys
from pathlib import Path
BASE = Path(__file__).resolve().parent.parent
V = BASE / "scripts/phase1_4/handoff/validate_decisions.py"

def run(tmp_path, rows):
    p = tmp_path / "d.jsonl"
    p.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
    return subprocess.run([sys.executable, str(V), str(p)], capture_output=True, text=True)

def first_id(task):
    f = sorted((BASE / "data/phase1_4/handoff/packets").glob(f"{task}_*.jsonl"))[0]
    return json.loads(f.read_text().splitlines()[0])["id"]

def good(task="T1"):
    return {"task": task, "id": first_id(task), "reviewer": "gpt-6-luna", "verdict": "ACCEPT", "en_ja": "OK", "en_vi": "OK", "ja_vi": "OK",
            "naturalness": "NATURAL", "confidence": "HIGH", "revision": None, "note": "Pair is exact and idiomatic in all three languages."}

def test_valid_decision_passes(tmp_path):
    assert run(tmp_path, [good()]).returncode == 0

def test_rejects_unknown_id_and_short_note_and_bad_accept(tmp_path):
    g = good(); g["id"] = "concept-core-nonexistent"
    assert run(tmp_path, [g]).returncode != 0
    g = good(); g["note"] = "ok"
    assert run(tmp_path, [g]).returncode != 0
    g = good(); g["en_vi"] = "WRONG"
    assert run(tmp_path, [g]).returncode != 0

def test_revise_needs_valid_revision_and_t2_cannot_accept(tmp_path):
    g = good(); g["verdict"] = "REVISE"; g["revision"] = None
    assert run(tmp_path, [g]).returncode != 0
    g["revision"] = {"vi": "Xin Chào!"}
    assert run(tmp_path, [g]).returncode != 0
    assert run(tmp_path, [good("T2")]).returncode != 0

def test_t4_schema_and_duplicates(tmp_path):
    d = {"task": "T4", "id": first_id("T4"), "reviewer": "gpt-6-luna", "vi_lemma": "sân bay", "synonyms": [], "confidence": "HIGH", "note": "Standard word for this sense."}
    assert run(tmp_path, [d]).returncode == 0
    assert run(tmp_path, [d, d]).returncode != 0
    d2 = dict(d, vi_lemma="Sân bay!")
    assert run(tmp_path, [d2]).returncode != 0
