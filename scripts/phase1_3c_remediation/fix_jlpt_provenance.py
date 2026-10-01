#!/usr/bin/env python3
"""
Phase 1.3C.1 — JLPT Provenance Remediation Script
====================================================
Upstream authoritative determination:
  - Bluskyo/JLPT_Vocabulary README: "Data from https://www.tanos.co.uk/jlpt/
    are licenced under Creative Commons 'BY' by Jonathan Waller"
  - Bluskyo/JLPT_Vocabulary LICENSE file: MIT (covers repository code only)
  - tanos.co.uk community-confirmed: CC-BY (Attribution only, no SA)
  - SPDX canonical identifier: CC-BY-3.0

Correct values:
  license: CC-BY-3.0
  sha256:  810c776c7a72fe9a6860d8629e7f4d3903545808e6cbcff8dde3b52b01800f24
  upstream_url: https://raw.githubusercontent.com/Bluskyo/JLPT_Vocabulary/master/data/vocab/results/JLPT_vocab_ALL.csv
  license_url: https://www.tanos.co.uk/jlpt/  (primary licensor)
  attribution_required: true
  share_alike: false

Documents patched by this script:
  1. data/raw/jlpt_consensus/2026-v1/metadata.json
  2. reports/source_ingestion/acquisition_report.json
  3. reports/source_ingestion/acquisition_summary.md
  4. reports/phase1_3c/expansion_summary.json  (+ fix wrong sha256)
  5. reports/phase1_3c/expansion_summary.md    (+ fix wrong sha256)
  6. reports/licenses/redistribution_audit.json (+ fix wrong sha256)
  7. reports/licenses/source_license_matrix.md
"""

import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

CORRECT_LICENSE = "CC-BY-3.0"
CORRECT_SHA256 = "810c776c7a72fe9a6860d8629e7f4d3903545808e6cbcff8dde3b52b01800f24"
WRONG_LICENSE_SA = "CC-BY-SA-3.0"
WRONG_LICENSE_CC0 = "CC0-1.0"
WRONG_SHA256 = "a34ff749ff35b91b9f67a2167fa940e4f29a008c2a41d99665bc7f4dbda87504"

PROVENANCE_NOTE = (
    "CC-BY-3.0 (Jonathan Waller / tanos.co.uk). "
    "Data published under Creative Commons Attribution ('BY') at https://www.tanos.co.uk/jlpt/. "
    "Repository wrapper (Bluskyo/JLPT_Vocabulary) is MIT. "
    "Determined from: (1) upstream README explicit license statement, "
    "(2) GitHub LICENSE file (MIT, code only), (3) tanos.co.uk attribution notice."
)

errors = []
fixed = []


# ─── 1. metadata.json ─────────────────────────────────────────────────────────
def fix_metadata_json():
    path = REPO_ROOT / "data/raw/jlpt_consensus/2026-v1/metadata.json"
    with open(path) as f:
        d = json.load(f)

    changed = False
    if d.get("license") != CORRECT_LICENSE:
        d["license"] = CORRECT_LICENSE
        changed = True
    if d.get("license_url") != "https://www.tanos.co.uk/jlpt/":
        d["license_url"] = "https://www.tanos.co.uk/jlpt/"
        changed = True
    if d.get("artifact_sha256") != CORRECT_SHA256:
        errors.append(f"FATAL: metadata.json sha256 mismatch: {d.get('artifact_sha256')} vs {CORRECT_SHA256}")
    d["provenance_note"] = PROVENANCE_NOTE

    if changed or "provenance_note" not in d:
        with open(path, "w") as f:
            json.dump(d, f, indent=2, ensure_ascii=False)
            f.write("\n")
        fixed.append(str(path.relative_to(REPO_ROOT)))
    return d


# ─── 2. acquisition_report.json ───────────────────────────────────────────────
def fix_acquisition_report():
    path = REPO_ROOT / "reports/source_ingestion/acquisition_report.json"
    with open(path) as f:
        d = json.load(f)

    changed = False
    for src in d.get("sources", []):
        if src.get("source") == "jlpt_consensus":
            if src.get("license_code") != CORRECT_LICENSE:
                src["license_code"] = CORRECT_LICENSE
                changed = True
            if src.get("license_result") != "APPROVED":
                src["license_result"] = "APPROVED"
                changed = True
            if src.get("sha256") != CORRECT_SHA256:
                errors.append(
                    f"FATAL: acquisition_report sha256 mismatch: "
                    f"{src.get('sha256')} vs {CORRECT_SHA256}"
                )
            src["provenance_note"] = PROVENANCE_NOTE
            changed = True

    if changed:
        with open(path, "w") as f:
            json.dump(d, f, indent=2, ensure_ascii=False)
            f.write("\n")
        fixed.append(str(path.relative_to(REPO_ROOT)))


# ─── 3. acquisition_summary.md ────────────────────────────────────────────────
def fix_acquisition_summary_md():
    path = REPO_ROOT / "reports/source_ingestion/acquisition_summary.md"
    text = path.read_text(encoding="utf-8")

    # Replace JLPT-specific CC-BY-SA-3.0 in the table row for jlpt_consensus
    # Pattern: | `jlpt_consensus` | `2026-v1` | `CC-BY-SA-3.0` |
    new_text = re.sub(
        r"(\|\s*`jlpt_consensus`\s*\|[^|]+\|)\s*`CC-BY-SA-3\.0`\s*(\|)",
        rf"\1 `{CORRECT_LICENSE}` \2",
        text,
    )
    if new_text != text:
        path.write_text(new_text, encoding="utf-8")
        fixed.append(str(path.relative_to(REPO_ROOT)))
    else:
        # Try plain (no backtick) pattern
        new_text2 = re.sub(
            r"(\|\s*`jlpt_consensus`\s*\|[^|]+\|)\s*CC-BY-SA-3\.0\s*(\|)",
            rf"\1 {CORRECT_LICENSE} \2",
            text,
        )
        if new_text2 != text:
            path.write_text(new_text2, encoding="utf-8")
            fixed.append(str(path.relative_to(REPO_ROOT)))


# ─── 4. expansion_summary.json ────────────────────────────────────────────────
def fix_expansion_summary_json():
    path = REPO_ROOT / "reports/phase1_3c/expansion_summary.json"
    with open(path) as f:
        d = json.load(f)

    changed = False
    # Walk the entire structure looking for jlpt_consensus blocks
    def patch_dict(obj):
        nonlocal changed
        if isinstance(obj, dict):
            if obj.get("source_id") == "jlpt_consensus":
                if obj.get("license") != CORRECT_LICENSE:
                    obj["license"] = CORRECT_LICENSE
                    changed = True
                if obj.get("raw_sha256") == WRONG_SHA256:
                    obj["raw_sha256"] = CORRECT_SHA256
                    changed = True
                obj["provenance_note"] = PROVENANCE_NOTE
                changed = True
            for v in obj.values():
                patch_dict(v)
        elif isinstance(obj, list):
            for item in obj:
                patch_dict(item)

    patch_dict(d)

    if changed:
        with open(path, "w") as f:
            json.dump(d, f, indent=2, ensure_ascii=False)
            f.write("\n")
        fixed.append(str(path.relative_to(REPO_ROOT)))


# ─── 5. expansion_summary.md ──────────────────────────────────────────────────
def fix_expansion_summary_md():
    path = REPO_ROOT / "reports/phase1_3c/expansion_summary.md"
    text = path.read_text(encoding="utf-8")

    # Fix license in table row
    new_text = text.replace(
        "| `jlpt_consensus` | 2026-v1 | CC0-1.0 |",
        f"| `jlpt_consensus` | 2026-v1 | {CORRECT_LICENSE} |",
    )
    # Fix wrong SHA256
    new_text = new_text.replace(WRONG_SHA256, CORRECT_SHA256)

    if new_text != text:
        path.write_text(new_text, encoding="utf-8")
        fixed.append(str(path.relative_to(REPO_ROOT)))


# ─── 6. redistribution_audit.json ─────────────────────────────────────────────
def fix_redistribution_audit_json():
    path = REPO_ROOT / "reports/licenses/redistribution_audit.json"
    with open(path) as f:
        d = json.load(f)

    changed = False
    sources = d.get("sources", d)  # handle either {sources: {}} or flat structure
    if isinstance(sources, dict) and "jlpt_consensus" in sources:
        entry = sources["jlpt_consensus"]
        if entry.get("license") != CORRECT_LICENSE:
            entry["license"] = CORRECT_LICENSE
            changed = True
        if entry.get("attribution_required") is False:
            entry["attribution_required"] = True
            changed = True
        if entry.get("category") == "TIER_1_PERMISSIVE":
            entry["category"] = "TIER_2_ATTRIBUTION"
            changed = True
        entry["provenance_note"] = PROVENANCE_NOTE
        changed = True

        # Also fix sha in source_inventory if present
        inventory = d.get("source_inventory", [])
        for row in inventory:
            if isinstance(row, dict) and row.get("source_id") == "jlpt_consensus":
                if row.get("sha256") == WRONG_SHA256:
                    row["sha256"] = CORRECT_SHA256
                    changed = True
                if row.get("license") != CORRECT_LICENSE:
                    row["license"] = CORRECT_LICENSE
                    changed = True

    if changed:
        with open(path, "w") as f:
            json.dump(d, f, indent=2, ensure_ascii=False)
            f.write("\n")
        fixed.append(str(path.relative_to(REPO_ROOT)))


# ─── 7. source_license_matrix.md ──────────────────────────────────────────────
def fix_source_license_matrix_md():
    path = REPO_ROOT / "reports/licenses/source_license_matrix.md"
    text = path.read_text(encoding="utf-8")

    # Fix the jlpt_consensus row
    # From: | `jlpt_consensus` | Community Collation (Tanos / JLPT Vocab Project) | `CC0-1.0` / Open Data | Tier 1 Permissive | NO | YES | YES | NO |
    # To:   | `jlpt_consensus` | Jonathan Waller / tanos.co.uk (via Bluskyo collation) | `CC-BY-3.0` | Tier 2 Attribution | NO | YES | YES | YES |
    new_text = re.sub(
        r"\|\s*`jlpt_consensus`\s*\|[^\n]+\n",
        (
            f"| `jlpt_consensus` | Jonathan Waller / tanos.co.uk (Bluskyo/JLPT_Vocabulary collation) "
            f"| `{CORRECT_LICENSE}` | Tier 2 Attribution | NO | YES | YES | YES |\n"
        ),
        text,
    )

    # Also add/update attribution note in section 4 if CC-BY-3.0 attribution not present
    if "Jonathan Waller" not in text or "tanos.co.uk" not in text:
        attribution_block = (
            "\n- **JLPT Vocabulary Data**:\n"
            "  > JLPT vocabulary lists are based on data from Jonathan Waller's "
            "tanos.co.uk project, licensed under Creative Commons Attribution (CC-BY-3.0). "
            "Reformatted by Bluskyo/JLPT_Vocabulary (MIT). "
            "Attribution: Jonathan Waller, https://www.tanos.co.uk/jlpt/\n"
        )
        # Insert before the last section or append
        if "## 4." in new_text:
            # append within section 4
            new_text = new_text.rstrip() + "\n" + attribution_block + "\n"
        else:
            new_text = new_text.rstrip() + "\n" + attribution_block + "\n"

    if new_text != text:
        path.write_text(new_text, encoding="utf-8")
        fixed.append(str(path.relative_to(REPO_ROOT)))


# ─── Main ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("Phase 1.3C.1 — JLPT Provenance Remediation")
    print("=" * 60)

    fix_metadata_json()
    fix_acquisition_report()
    fix_acquisition_summary_md()
    fix_expansion_summary_json()
    fix_expansion_summary_md()
    fix_redistribution_audit_json()
    fix_source_license_matrix_md()

    if errors:
        print("\n[FATAL ERRORS]")
        for e in errors:
            print(f"  ERROR: {e}")
        sys.exit(1)

    print(f"\n[FIXED] {len(fixed)} documents updated:")
    for f in fixed:
        print(f"  ✓ {f}")

    print("\n[OK] JLPT provenance remediation complete.")
    print(f"     Correct license: {CORRECT_LICENSE}")
    print(f"     Correct sha256:  {CORRECT_SHA256}")
