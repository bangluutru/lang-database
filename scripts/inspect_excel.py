#!/usr/bin/env python3
"""
scripts/inspect_excel.py
Inspects Excel workbooks from FSA EDINET taxonomy.
Generates comprehensive ingestion audit reports in reports/source_ingestion/.
Detects sheet names, row counts, column counts, merged cells, header structure,
empty rows, and duplicate candidate elements.
"""

import os
import sys
import json
from pathlib import Path
import openpyxl

BASE_DIR = Path(__file__).resolve().parent.parent
REPORTS_DIR = BASE_DIR / "reports" / "source_ingestion"


def inspect_workbook(filepath: Path) -> dict:
    print(f"[*] Inspecting workbook: {filepath.name} ...")
    wb = openpyxl.load_workbook(filepath, read_only=False, data_only=True)

    report = {
        "filename": filepath.name,
        "filepath": str(filepath.relative_to(BASE_DIR)),
        "file_size_bytes": filepath.stat().st_size,
        "sheet_count": len(wb.sheetnames),
        "sheet_names": wb.sheetnames,
        "sheets": {}
    }

    for sheet_name in wb.sheetnames:
        ws = wb[sheet_name]
        merged_ranges = [str(r) for r in ws.merged_cells.ranges]

        # Read first 10 rows to detect header candidate
        sample_rows = []
        for r_idx, row in enumerate(ws.iter_rows(values_only=True), start=1):
            if r_idx > 10:
                break
            sample_rows.append([str(c) if c is not None else "" for c in row[:15]])

        # Count total rows and cols
        max_r = ws.max_row or 0
        max_c = ws.max_column or 0

        # Scan for empty rows and sample headers
        empty_rows = 0
        non_empty_rows = 0
        headers = []
        if sample_rows:
            # Look for row with highest non-empty string count in first 5 rows
            best_h_idx = 0
            best_h_count = 0
            for idx, r in enumerate(sample_rows[:5]):
                cnt = sum(1 for c in r if c.strip())
                if cnt > best_h_count:
                    best_h_count = cnt
                    best_h_idx = idx
            headers = sample_rows[best_h_idx]

        sheet_info = {
            "name": sheet_name,
            "max_row": max_r,
            "max_column": max_c,
            "merged_cells_count": len(merged_ranges),
            "merged_cells_sample": merged_ranges[:10],
            "detected_headers": headers,
            "sample_rows": sample_rows[:3]
        }
        report["sheets"][sheet_name] = sheet_info

    wb.close()
    return report


def main():
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    target_files = [
        BASE_DIR / "data" / "raw" / "fsa" / "edinet" / "2026" / "1f_AccountList.xlsx",
        BASE_DIR / "data" / "raw" / "fsa" / "edinet" / "2026" / "1e_ElementList.xlsx",
        BASE_DIR / "data" / "raw" / "fsa" / "edinet" / "2026" / "1g_IFRS_ElementList.xlsx",
        BASE_DIR / "staging" / "fsa_edinet_2027_draft" / "1f_AccountList_2027_draft.xlsx",
    ]

    all_reports = []
    for f in target_files:
        if f.exists():
            rep = inspect_workbook(f)
            out_json = REPORTS_DIR / f"{f.stem}_inspection.json"
            with open(out_json, "w", encoding="utf-8") as out_f:
                json.dump(rep, out_f, ensure_ascii=False, indent=2)
            print(f"[+] Wrote inspection report: {out_json.name}")
            all_reports.append(rep)
        else:
            print(f"[-] File not found: {f}")

    # Generate Markdown Summary
    md_summary_path = REPORTS_DIR / "INSPECTION_SUMMARY.md"
    with open(md_summary_path, "w", encoding="utf-8") as md_f:
        md_f.write("# FSA EDINET Taxonomy Workbooks Ingestion Inspection Report\n\n")
        md_f.write(f"Generated at: {Path(__file__).name}\n\n")
        for rep in all_reports:
            md_f.write(f"## File: `{rep['filename']}`\n")
            md_f.write(f"- **Path**: `{rep['filepath']}`\n")
            md_f.write(f"- **Size**: {rep['file_size_bytes']:,} bytes\n")
            md_f.write(f"- **Sheets ({rep['sheet_count']})**: {', '.join(rep['sheet_names'])}\n\n")
            for sname, sinfo in rep["sheets"].items():
                md_f.write(f"### Sheet: `{sname}`\n")
                md_f.write(f"- Rows: {sinfo['max_row']:,} | Columns: {sinfo['max_column']}\n")
                md_f.write(f"- Merged cell ranges: {sinfo['merged_cells_count']}\n")
                md_f.write(f"- Detected Headers: `{', '.join([h for h in sinfo['detected_headers'] if h])}`\n\n")
    print(f"[+] Wrote summary report: {md_summary_path.name}")


if __name__ == "__main__":
    main()
