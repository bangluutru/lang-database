#!/usr/bin/env python3
"""
scripts/download_sources.py
Downloads official public datasets for JP Professional Vocabulary Database.
Computes SHA-256 checksums, writes metadata.json, and strictly separates
2026 production baseline from 2027 draft staging.
"""

import os
import sys
import time
import json
import hashlib
import urllib.request
import urllib.error
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"

# Download definitions
DOWNLOAD_TARGETS = [
    # 1. FSA EDINET 2026 Official Final (Production Baseline)
    {
        "source_id": "fsa_edinet_2026",
        "url": "https://www.fsa.go.jp/search/20251111/1f_AccountList.xlsx",
        "dest_dir": BASE_DIR / "data" / "raw" / "fsa" / "edinet" / "2026",
        "filename": "1f_AccountList.xlsx",
        "content_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "source_status": "final",
        "description": "勘定科目リスト (Account List) - Primary Accounting Taxonomy",
    },
    {
        "source_id": "fsa_edinet_2026",
        "url": "https://www.fsa.go.jp/search/20251111/1e_ElementList.xlsx",
        "dest_dir": BASE_DIR / "data" / "raw" / "fsa" / "edinet" / "2026",
        "filename": "1e_ElementList.xlsx",
        "content_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "source_status": "final",
        "description": "タクソノミ要素リスト (Taxonomy Elements List)",
    },
    {
        "source_id": "fsa_edinet_2026",
        "url": "https://www.fsa.go.jp/search/20251111/1g_IFRS_ElementList.xlsx",
        "dest_dir": BASE_DIR / "data" / "raw" / "fsa" / "edinet" / "2026",
        "filename": "1g_IFRS_ElementList.xlsx",
        "content_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "source_status": "final",
        "description": "国際会計基準タクソノミ要素リスト (IFRS Elements List)",
    },
    {
        "source_id": "fsa_edinet_2026",
        "url": "https://www.fsa.go.jp/search/20251111/1b-3_Yougo.pdf",
        "dest_dir": BASE_DIR / "data" / "raw" / "fsa" / "edinet" / "2026",
        "filename": "1b-3_Yougo.pdf",
        "content_type": "application/pdf",
        "source_status": "final",
        "description": "EDINETタクソノミ用語集 (Taxonomy Glossary)",
    },

    # 2. FSA EDINET 2027 Draft (Strictly Staged, NOT merged into unflagged production)
    {
        "source_id": "fsa_edinet_2027_draft",
        "url": "https://www.fsa.go.jp/search/20260911/1f_AccountList.xlsx",
        "dest_dir": BASE_DIR / "staging" / "fsa_edinet_2027_draft",
        "filename": "1f_AccountList_2027_draft.xlsx",
        "content_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "source_status": "draft",
        "description": "2027年版EDINETタクソノミ（案）勘定科目リスト (Draft for Research)",
    },
    {
        "source_id": "fsa_edinet_2027_draft",
        "url": "https://www.fsa.go.jp/search/20260911/1a-1_KoshinGaiyo.pdf",
        "dest_dir": BASE_DIR / "staging" / "fsa_edinet_2027_draft",
        "filename": "1a-1_KoshinGaiyo_2027_draft.pdf",
        "content_type": "application/pdf",
        "source_status": "draft",
        "description": "2027年版EDINETタクソノミ（案）更新概要 (Draft Summary)",
    },

    # 3. National Tax Agency (NTA - 国税庁) Tax Answer & Glossaries
    {
        "source_id": "nta_tax_glossary_2026",
        "url": "https://www.nta.go.jp/taxes/shiraberu/taxanswer/yogo/senmon.htm",
        "dest_dir": BASE_DIR / "data" / "raw" / "nta" / "taxanswer",
        "filename": "nta_senmon_yogo.html",
        "content_type": "text/html",
        "source_status": "current",
        "description": "国税庁 タックスアンサー 専門用語集",
    },
    {
        "source_id": "nta_tax_glossary_2026",
        "url": "https://www.nta.go.jp/taxes/shiraberu/taxanswer/code/index.htm",
        "dest_dir": BASE_DIR / "data" / "raw" / "nta" / "taxanswer",
        "filename": "nta_code_index.html",
        "content_type": "text/html",
        "source_status": "current",
        "description": "国税庁 タックスアンサー コード一覧 (Tax Categories & Topics)",
    },
    {
        "source_id": "nta_tax_glossary_2026",
        "url": "https://www.nta.go.jp/taxes/shiraberu/taxanswer/yogo/ryaku.htm",
        "dest_dir": BASE_DIR / "data" / "raw" / "nta" / "taxanswer",
        "filename": "nta_ryaku_yogo.html",
        "content_type": "text/html",
        "source_status": "current",
        "description": "国税庁 タックスアンサー 省略用語例",
    },

    # 4. JICPA (日本公認会計士協会) 会計・監査用語かんたん解説集 (Terminology Discovery)
    {
        "source_id": "jicpa_glossary",
        "url": "https://jicpa.or.jp/cpainfo/introduction/keyword/",
        "dest_dir": BASE_DIR / "data" / "raw" / "jicpa" / "glossary",
        "filename": "jicpa_keyword_index.html",
        "content_type": "text/html",
        "source_status": "current",
        "description": "日本公認会計士協会 会計・監査用語かんたん解説集 キーワード一覧",
    },

    # 5. ASBJ Accounting Standards Overview
    {
        "source_id": "asbj_accounting_standards",
        "url": "https://www.asb.or.jp/jp/accounting_standards/",
        "dest_dir": BASE_DIR / "data" / "raw" / "asbj" / "standards",
        "filename": "asbj_standards_list.html",
        "content_type": "text/html",
        "source_status": "current",
        "description": "企業会計基準委員会 会計基準一覧",
    },

    # 6. JETRO Trade Navigation (Terminology Discovery)
    {
        "source_id": "jetro_trade",
        "url": "https://www.jetro.go.jp/theme/export/",
        "dest_dir": BASE_DIR / "data" / "raw" / "jetro" / "trade",
        "filename": "jetro_export_navi.html",
        "content_type": "text/html",
        "source_status": "current",
        "description": "JETRO 貿易・輸出入手続き ナビゲーション (Discovery Reference)",
    },
]


def compute_sha256(filepath: Path) -> str:
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def download_target(target: dict) -> dict:
    dest_dir = target["dest_dir"]
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_file = dest_dir / target["filename"]

    print(f"[*] Downloading {target['filename']} from {target['url']} ...")
    req = urllib.request.Request(target["url"], headers={"User-Agent": USER_AGENT})

    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            data = response.read()
            with open(dest_file, "wb") as f:
                f.write(data)
    except urllib.error.HTTPError as e:
        print(f"    [!] HTTP Error {e.code} downloading {target['url']}")
        return None
    except Exception as e:
        print(f"    [!] Error downloading {target['url']}: {e}")
        return None

    sha256_hash = compute_sha256(dest_file)
    file_size = dest_file.stat().st_size

    record = {
        "filename": target["filename"],
        "source_id": target["source_id"],
        "source_url": target["url"],
        "downloaded_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "file_size_bytes": file_size,
        "sha256": sha256_hash,
        "content_type": target["content_type"],
        "source_status": target["source_status"],
        "description": target["description"],
    }
    print(f"    [OK] Saved {file_size:,} bytes | SHA-256: {sha256_hash[:16]}...")
    return record


def main():
    print("=== Starting Official Source Download Pipeline ===")
    results_by_dir = {}

    for target in DOWNLOAD_TARGETS:
        rec = download_target(target)
        if rec:
            d = str(target["dest_dir"])
            if d not in results_by_dir:
                results_by_dir[d] = []
            results_by_dir[d].append(rec)
        # polite delay between web requests
        time.sleep(1.0)

    # Write metadata.json in each directory
    for dest_dir_str, items in results_by_dir.items():
        meta_path = Path(dest_dir_str) / "metadata.json"
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump({
                "directory": dest_dir_str,
                "updated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "files_count": len(items),
                "files": items
            }, f, ensure_ascii=False, indent=2)
        print(f"[+] Wrote metadata to {meta_path}")

    print("\n=== Download Pipeline Completed Successfully ===")


if __name__ == "__main__":
    main()
