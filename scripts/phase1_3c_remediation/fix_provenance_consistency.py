#!/usr/bin/env python3
"""
Phase 1.3C.1 — Systematic Provenance Consistency Remediation
=============================================================
Ground truth is always metadata.json (which has been verified to match
actual raw artifact SHA256).

This script propagates ground-truth values outward to:
  - expansion_summary.json   (stale SHA256 + joyo license)
  - expansion_summary.md     (stale SHA256 + joyo license in table)
  - redistribution_audit.json (joyo license string)

Additionally fixes the KNOWN_CORRECT dict in test_provenance_integrity.py.
"""

import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
RAW_DATA = REPO_ROOT / "data" / "raw"

# ─── Step 1: Load ground truth from all metadata.json files ───────────────────
def load_ground_truth() -> dict:
    """Returns {source_id: {sha256, license, artifact_filename, version}}"""
    truth = {}
    for meta_path in sorted(RAW_DATA.glob("*/*/metadata.json")):
        with open(meta_path) as f:
            d = json.load(f)
        sid = d.get("source_id")
        if sid:
            truth[sid] = {
                "sha256": d.get("artifact_sha256"),
                "license": d.get("license"),
                "artifact_filename": d.get("artifact_filename"),
                "version": d.get("source_version"),
            }
    return truth


# ─── Step 2: Fix expansion_summary.json ───────────────────────────────────────
def fix_expansion_summary_json(truth: dict) -> list:
    path = REPO_ROOT / "reports" / "phase1_3c" / "expansion_summary.json"
    with open(path) as f:
        raw = f.read()

    d = json.loads(raw)
    fixed = []

    def patch(obj):
        if isinstance(obj, dict):
            sid = obj.get("source_id")
            if sid and sid in truth:
                gt = truth[sid]
                if gt["sha256"] and obj.get("raw_sha256") and obj["raw_sha256"] != gt["sha256"]:
                    obj["raw_sha256"] = gt["sha256"]
                    fixed.append(f"  expansion_summary.json [{sid}] raw_sha256 → {gt['sha256'][:20]}...")
                if gt["license"] and obj.get("license") and obj["license"] != gt["license"]:
                    fixed.append(
                        f"  expansion_summary.json [{sid}] license: "
                        f"{obj['license']!r} → {gt['license']!r}"
                    )
                    obj["license"] = gt["license"]
            for v in obj.values():
                patch(v)
        elif isinstance(obj, list):
            for v in obj:
                patch(v)

    patch(d)

    if fixed:
        with open(path, "w") as f:
            json.dump(d, f, indent=2, ensure_ascii=False)
            f.write("\n")
    return fixed


# ─── Step 3: Fix expansion_summary.md table rows ──────────────────────────────
def fix_expansion_summary_md(truth: dict) -> list:
    path = REPO_ROOT / "reports" / "phase1_3c" / "expansion_summary.md"
    text = path.read_text(encoding="utf-8")
    original = text
    fixed = []

    for sid, gt in truth.items():
        if not gt["sha256"] or not gt["artifact_filename"]:
            continue
        # Replace any SHA256 hex strings in rows containing this source_id
        # We look for the 64-hex pattern in table rows that mention the source
        # Use a regex to find the table row for this source
        # Pattern: a row with `source_id` in backticks somewhere in the row
        row_pattern = re.compile(
            r"(\|\s*`" + re.escape(sid) + r"`\s*\|[^\n]*)([0-9a-f]{64})([^\n]*\|)",
            re.IGNORECASE,
        )
        def replace_sha(m):
            old_sha = m.group(2)
            if old_sha != gt["sha256"]:
                fixed.append(f"  expansion_summary.md [{sid}] SHA {old_sha[:16]}... → {gt['sha256'][:16]}...")
                return m.group(1) + gt["sha256"] + m.group(3)
            return m.group(0)

        text = row_pattern.sub(replace_sha, text)

        # Fix license column in joyo row specifically
        if sid == "joyo" and gt["license"]:
            # Match the joyo row and fix Government-PD → PDL-1.0
            text = re.sub(
                r"(\|\s*`joyo`\s*\|[^|]+\|)\s*Government-PD\s*(\|)",
                rf"\1 {gt['license']} \2",
                text,
            )

    if text != original:
        path.write_text(text, encoding="utf-8")
    return fixed


# ─── Step 4: Fix redistribution_audit.json ────────────────────────────────────
def fix_redistribution_audit_json(truth: dict) -> list:
    path = REPO_ROOT / "reports" / "licenses" / "redistribution_audit.json"
    with open(path) as f:
        d = json.load(f)

    fixed = []
    inventory = d.get("license_inventory", {})
    for sid, entry in inventory.items():
        if sid not in truth:
            continue
        gt_license = truth[sid].get("license")
        if gt_license and entry.get("license") != gt_license:
            fixed.append(
                f"  redistribution_audit.json [{sid}] license: "
                f"{entry['license']!r} → {gt_license!r}"
            )
            entry["license"] = gt_license
            # CC-BY-3.0 and other CC-BY licenses require attribution
            if gt_license.startswith("CC-BY") and "SA" not in gt_license:
                entry["attribution_required"] = True
                if "share_alike" in entry:
                    entry["share_alike"] = False

    if fixed:
        with open(path, "w") as f:
            json.dump(d, f, indent=2, ensure_ascii=False)
            f.write("\n")
    return fixed


# ─── Step 5: Fix KNOWN_CORRECT in test file ────────────────────────────────────
def fix_test_known_correct(truth: dict) -> list:
    path = REPO_ROOT / "tests" / "test_provenance_integrity.py"
    text = path.read_text(encoding="utf-8")
    original = text
    fixed = []

    # For each source in KNOWN_CORRECT that has the wrong SHA, patch it
    for sid, gt in truth.items():
        if not gt["sha256"]:
            continue
        # Find pattern: "sha256": "..." in the KNOWN_CORRECT block for this source_id
        # We look for the sha256 value following the source block
        pattern = re.compile(
            r'("' + re.escape(sid) + r'":\s*\{[^}]*?"sha256":\s*")([0-9a-f]{64})(")',
            re.DOTALL,
        )
        def replacer(m, correct_sha=gt["sha256"], sid=sid):
            old = m.group(2)
            if old != correct_sha:
                fixed.append(f"  test KNOWN_CORRECT [{sid}] sha256: {old[:16]}... → {correct_sha[:16]}...")
                return m.group(1) + correct_sha + m.group(3)
            return m.group(0)
        text = pattern.sub(replacer, text)

    if text != original:
        path.write_text(text, encoding="utf-8")
    return fixed


# ─── Main ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("Phase 1.3C.1 — Systematic Provenance Consistency Remediation")
    print("=" * 62)

    truth = load_ground_truth()
    print(f"\n[TRUTH] Loaded ground truth for {len(truth)} sources from metadata.json")

    all_fixed = []

    changes = fix_expansion_summary_json(truth)
    if changes:
        print("\n[expansion_summary.json]")
        for c in changes: print(c)
    all_fixed.extend(changes)

    changes = fix_expansion_summary_md(truth)
    if changes:
        print("\n[expansion_summary.md]")
        for c in changes: print(c)
    all_fixed.extend(changes)

    changes = fix_redistribution_audit_json(truth)
    if changes:
        print("\n[redistribution_audit.json]")
        for c in changes: print(c)
    all_fixed.extend(changes)

    changes = fix_test_known_correct(truth)
    if changes:
        print("\n[test_provenance_integrity.py KNOWN_CORRECT]")
        for c in changes: print(c)
    all_fixed.extend(changes)

    if not all_fixed:
        print("\n[OK] No changes needed — all documents already consistent.")
    else:
        print(f"\n[DONE] {len(all_fixed)} corrections applied.")
