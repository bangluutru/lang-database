#!/usr/bin/env python3
"""
scripts/phase1_4/extract_wiktionary.py
Deterministic, license-clean extraction of EN-sense-anchored JA/VI translation blocks
from the Wiktextract (kaikki.org) English-edition dump.

Upstream: https://kaikki.org/dictionary/English/kaikki.org-dictionary-English.jsonl.gz
Content license: Wiktionary text is dual-licensed CC-BY-SA 4.0 / GFDL
  (https://en.wiktionary.org/wiki/Wiktionary:Copyrights). We redistribute under CC-BY-SA-4.0
  (already an APPROVED_WITH_SHARE_ALIKE tier in config/license_policy.yaml).

Why this source: Wiktionary `trans-top` blocks list translations *per sense label*. A
(English headword, POS, sense label) block containing both a Japanese and a Vietnamese
translation is an editor-asserted sense-level EN<->JA<->VI alignment, which is exactly what
naive gloss matching (Phase 1.3C) could not provide.

Output (immutable raw snapshot, an extract of the full upstream file):
  data/raw/wiktionary_en/<dump-date>/wikt_en_translations.jsonl.gz
  + metadata.json (identity, upstream sha256 of the full dump, extract sha256, license)
  + SHA256SUMS

The extract keeps only: headword, POS, first IPA, sense glosses (leaf strings), and the
ja/vi translation entries. Line number in the extract (1-based) is the source locator.
"""

import argparse
import gzip
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from scripts.phase1_4.common import RAW_DIR, sha256_file

KEEP_POS = {"noun", "verb", "adj", "adv", "prep", "conj", "pron", "intj", "num",
            "det", "phrase", "particle", "prep_phrase", "contraction", "article"}
UPSTREAM_URL = "https://kaikki.org/dictionary/English/kaikki.org-dictionary-English.jsonl.gz"


def extract(src_gz: Path, out_gz: Path) -> dict:
    n_in = n_out = 0
    with gzip.open(src_gz, "rt", encoding="utf-8") as fin, open(out_gz, "wb") as raw, \
            gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as fo:
        for line in fin:
            n_in += 1
            d = json.loads(line)
            if d.get("lang_code") != "en" or d.get("pos") not in KEEP_POS:
                continue
            def _tr(t):
                return {k: t[k] for k in ("lang_code", "word", "sense", "alt", "roman", "tags", "note") if t.get(k)}

            def _keep(t):
                return t.get("lang_code") in ("ja", "vi") and t.get("word")

            entry_trs = [_tr(t) for t in d.get("translations", []) if _keep(t)]
            senses = []
            any_tr = bool(entry_trs)
            for s in d.get("senses", [])[:40]:
                g = s.get("glosses") or []
                if not g:
                    continue
                s_trs = [_tr(t) for t in s.get("translations", []) if _keep(t)]
                any_tr = any_tr or bool(s_trs)
                senses.append({"gloss": g[-1], "parents": g[:-1], "tags": s.get("tags") or [], "topics": s.get("topics") or [],
                               "translations": s_trs})
            if not any_tr:
                continue
            ipa = None
            for s in d.get("sounds", []):
                if s.get("ipa"):
                    ipa = s["ipa"]
                    break
            rec = {"word": d["word"], "pos": d["pos"], "ipa": ipa, "senses": senses,
                   "entry_translations": entry_trs}
            fo.write((json.dumps(rec, ensure_ascii=False, sort_keys=True) + "\n").encode("utf-8"))
            n_out += 1
    return {"entries_in": n_in, "entries_out": n_out}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True, help="path to downloaded kaikki English jsonl.gz")
    ap.add_argument("--version", default="2026-09-28", help="upstream Last-Modified date")
    ap.add_argument("--retrieved-at", required=True)
    args = ap.parse_args()

    src = Path(args.src)
    out_dir = RAW_DIR / "wiktionary_en" / args.version
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / "wikt_en_translations.jsonl.gz"
    stats = extract(src, out)
    meta = {
        "source_id": "wiktionary_en",
        "source_version": args.version,
        "upstream_url": UPSTREAM_URL,
        "retrieved_at": args.retrieved_at,
        "license": "CC-BY-SA-4.0",
        "license_url": "https://en.wiktionary.org/wiki/Wiktionary:Copyrights",
        "artifact_filename": "wikt_en_translations.jsonl.gz",
        "artifact_sha256": sha256_file(out),
        "upstream_full_artifact_sha256": sha256_file(src),
        "upstream_full_artifact_bytes": src.stat().st_size,
        "parser_version": "1.0.0",
        "organization": "Wiktionary contributors via Wiktextract (T. Ylonen) / kaikki.org",
        "authority_level": "open_collaborative_lexical",
        "description": "Filtered extract of the English Wiktionary (Wiktextract) dump: English headword/POS/sense "
                       "records that carry Japanese and/or Vietnamese translations (sense-linked or entry-level). "
                       "Locator = 1-based line number.",
        "extraction": stats,
        "immutable": True,
    }
    with open(out_dir / "metadata.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
        f.write("\n")
    with open(out_dir / "SHA256SUMS", "w") as f:
        f.write(f"{meta['artifact_sha256']}  wikt_en_translations.jsonl.gz\n")
    print(json.dumps(meta, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
