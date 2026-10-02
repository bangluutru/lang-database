#!/usr/bin/env python3
"""
scripts/phase1_4/freeze_baseline.py
Records the sealed Phase 1.3D baseline (git a07f61e) as a verifiable manifest:
  * append-only canonical JSONL files -> byte length + SHA-256 of the full baseline bytes
    (Phase 1.4 may only APPEND after these bytes; tests verify the prefix hash)
  * non-appendable frozen files        -> full-file SHA-256
  * Oki deck                           -> per-card SHA-256 (the export is regenerated, baseline cards must be identical)
Run ONCE against the pristine baseline checkout. Re-running after Phase 1.4 data exists fails loudly.
"""
import hashlib, json, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from scripts.phase1_4.common import BASE_DIR, CANONICAL_DIR, BASELINE_SHA, sha256_file

APPEND_ONLY = ["concepts.jsonl", "senses.jsonl", "expressions.jsonl", "classifications.jsonl", "examples.jsonl"]
FROZEN_FILES = ["data/canonical/legacy_mapping.json", "data/production/vocabulary.jsonl",
                "data/production/expressions.jsonl", "data/production/relationships.jsonl",
                "data/production/dataset_manifest.json"]

def main():
    out_dir = BASE_DIR / "data" / "releases" / "phase1_3d-sealed"
    man = out_dir / "baseline_manifest.json"
    if man.exists():
        print("baseline manifest already exists; refusing to overwrite"); return
    head = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, cwd=BASE_DIR).stdout.strip()
    # verify the working tree canonical files equal the sealed commit
    for f in APPEND_ONLY + ["legacy_mapping.json"]:
        blob = subprocess.run(["git", "show", f"{BASELINE_SHA}:data/canonical/{f}"], capture_output=True, cwd=BASE_DIR).stdout
        cur = (CANONICAL_DIR / f).read_bytes()
        if hashlib.sha256(blob).hexdigest() != hashlib.sha256(cur).hexdigest():
            raise SystemExit(f"working tree {f} differs from sealed baseline {BASELINE_SHA}")
    m = {"baseline_commit": BASELINE_SHA, "frozen_at_head": head, "append_only": {}, "frozen_files": {}, "oki_cards": {}}
    for f in APPEND_ONLY:
        b = (CANONICAL_DIR / f).read_bytes()
        m["append_only"][f] = {"bytes": len(b), "lines": b.count(b"\n"), "sha256": hashlib.sha256(b).hexdigest()}
    for f in FROZEN_FILES:
        p = BASE_DIR / f
        if p.exists():
            m["frozen_files"][f] = sha256_file(p)
    # also every golden pilot / release checksum file
    for p in sorted((BASE_DIR / "data" / "releases").glob("golden-pilot-v1*/*")):
        m["frozen_files"][str(p.relative_to(BASE_DIR))] = sha256_file(p)
    deck = json.loads((BASE_DIR / "data/exports/oki_language/deck_data.json").read_text())
    for c in deck:
        m["oki_cards"][c["id"]] = hashlib.sha256(json.dumps(c, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
    out_dir.mkdir(parents=True, exist_ok=True)
    man.write_text(json.dumps(m, indent=1, sort_keys=True) + "\n")
    print(json.dumps({k: (v if k != "oki_cards" else len(v)) for k, v in m.items()}, indent=1)[:1500])

if __name__ == "__main__":
    main()
