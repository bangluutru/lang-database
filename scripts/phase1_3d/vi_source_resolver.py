#!/usr/bin/env python3
"""
scripts/phase1_3d/vi_source_resolver.py
Vietnamese Source-First Resolution Engine for Phase 1.3D.
Searches approved open lexical resources before triggering AI fallback:
1. Daily Curated Core Lexicon (daily_en_vi_core)
2. Curated Open Vietnamese Lexical Seed (data/curated/phase1_3b/vietnamese_core_seed.json)
3. Audited Sino-Vietnamese cognates validated against tabidots/vn-freqs (vn_word_frequencies.tsv) and Unihan.
Detects and quarantines false friends and archaic cognates (e.g. 実物 -> thực vật, 交通 -> giao thông for communication).
Assigns resolution statuses: SOURCE_EXACT, SOURCE_SUPPORTED, HANVIET_SUPPORTED, NO_SOURCE_MATCH, CONFLICTING_SOURCE.
"""

import sys
import json
import csv
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple

BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from scripts.phase1_3c.adapters.production_adapters import VietnameseFrequencyAdapter, HanVietAdapter
from scripts.phase1_3c.daily_lexicon import DAILY_EN_VI_CORE

VN_FREQ_PATH = BASE_DIR / "data" / "raw" / "vn_freq" / "1.0" / "vn_word_frequencies.tsv"
SEED_PATH = BASE_DIR / "data" / "curated" / "phase1_3b" / "vietnamese_core_seed.json"

# Known false friends / archaic Sino-Vietnamese pairs where Han characters divert from modern Vietnamese meaning
SINO_VI_FALSE_FRIENDS = {
    ("実物", "thực vật"),    # botany/plant vs real thing
    ("収容", "thu dung"),    # detention/containment vs accommodation
    ("沙汰", "sa đãi"),      # archaic vs affair
    ("世界", "thế giới"),    # world vs social circle
    ("交通", "giao thông"),  # traffic/transport vs communication
    ("世界", "thế giới"),
    ("空気", "không khí"),   # air vs mood/atmosphere (metaphorical)
    ("発作", "phát tác"),    # fit/seizure vs act up
    ("姿勢", "tư thế"),      # posture vs mental approach
    ("切実", "thiết thực"),  # practical vs acute/appropriate
    ("知覚", "tri giác"),    # perception vs awareness
    ("小節", "tiểu tiết"),   # trivial detail vs musical bar
    ("基本", "cơ bản"),      # basically (adverb) vs foundation (noun)
    ("前方", "tiền phương"), # military frontline vs ahead
    ("世界", "thế giới"),
    ("安閑", "an nhàn"),     # leisure vs calm/comfortable
    ("周到", "chu đáo"),
    ("意見", "ý kiến"),      # opinion vs comment
    ("罪人", "tội nhân"),    # criminal (noun) vs criminal (adj)
    ("険悪", "hiểm ác"),     # sinister vs critical/perilous
    ("労力", "lao lực"),     # overwork/exhaustion vs effort
    ("真人", "chân nhân"),   # Daoist immortal vs you
    ("寡人", "quả nhân"),   # monarch self-reference vs I
    ("大体", "đại thể"),     # broadly speaking vs about/almost
    ("到底", "đáo để"),     # shrewd/extreme vs cannot possibly
    ("無形", "vô hình"),     # invisible vs abstract
    ("偶然", "ngẫu nhiên"),  # coincidentally vs accident (event)
    ("事業", "sự nghiệp"),   # career vs activity/project
    ("事実", "sự thực"),     # fact vs actually
    ("西暦", "tây lịch"),    # Western calendar vs ad
    ("加増", "gia tăng"),    # augment vs addition
    ("演説", "diễn thuyết"), # speech/oration vs address
}


class ViSourceResolver:
    """Resolves Vietnamese candidate expressions from approved sources."""

    def __init__(self):
        # 1. Load vn_freq
        self.vn_adapter = VietnameseFrequencyAdapter()
        self.vn_records = self.vn_adapter.extract_records()
        self.vn_by_word: Dict[str, Dict[str, Any]] = {r["word"].lower(): r for r in self.vn_records}

        # 2. Load HanVietAdapter
        self.hanviet_adapter = HanVietAdapter()
        self.hanviet_readings = self.hanviet_adapter.extract_readings()

        # 3. Load curated seed
        self.seed_by_concept: Dict[str, List[Dict[str, Any]]] = {}
        if SEED_PATH.exists():
            with open(SEED_PATH, "r", encoding="utf-8") as f:
                seed_data = json.load(f)
                for item in seed_data:
                    cid = item.get("concept_id")
                    if cid:
                        self.seed_by_concept.setdefault(cid, []).append(item)

    def resolve(self, item: Dict[str, Any], ja_replacement: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Attempts to resolve Vietnamese expressions from approved open sources.
        Returns structured source resolution result with audit evidence.
        """
        cid = item["concept_id"]
        en_lemma = item["en"]["lemma"].lower()
        en_pos = item["en"]["part_of_speech"]
        
        # Use replacement JA if provided and verified
        ja_surf = ja_replacement["surface"] if ja_replacement else item["ja"]["lemma"]
        ja_pos = item["ja"]["part_of_speech"]

        candidates = []

        # 1. Check DAILY_EN_VI_CORE
        if en_lemma in DAILY_EN_VI_CORE:
            vi_word, vi_pos, vi_domain = DAILY_EN_VI_CORE[en_lemma]
            freq_rec = self.vn_by_word.get(vi_word.lower())
            locator = f"lemma:{en_lemma}, vi:{vi_word}"
            ev = {
                "source_id": "daily_en_vi_core",
                "source_version": "1.0",
                "source_locator": locator,
                "origin": "curated",
                "field_name": "word",
                "extracted_value": vi_word,
                "license": "MIT"
            }
            candidates.append({
                "lemma": vi_word,
                "part_of_speech": vi_pos,
                "definition": f"Từ vựng cơ bản: {vi_word}",
                "source_type": "CURATED",
                "frequency_rank": freq_rec["rank"] if freq_rec else None,
                "source_evidence": ev
            })
            return {
                "concept_id": cid,
                "status": "SOURCE_EXACT",
                "candidates": candidates,
                "notes": f"Resolved from DAILY_EN_VI_CORE: {vi_word}"
            }

        # 2. Check Curated Seed (data/curated/phase1_3b/vietnamese_core_seed.json)
        if cid in self.seed_by_concept:
            for s_item in self.seed_by_concept[cid]:
                vi_word = s_item["lemma"]
                freq_rec = self.vn_by_word.get(vi_word.lower())
                ev = {
                    "source_id": "vietnamese_core_seed",
                    "source_version": "1.0",
                    "source_locator": f"concept_id:{cid}, lemma:{vi_word}",
                    "origin": "curated",
                    "field_name": "lemma",
                    "extracted_value": vi_word,
                    "license": s_item.get("license", "CC-BY-4.0")
                }
                candidates.append({
                    "lemma": vi_word,
                    "part_of_speech": s_item.get("part_of_speech", en_pos),
                    "definition": f"Từ vựng cơ bản: {vi_word}",
                    "source_type": "CURATED",
                    "frequency_rank": freq_rec["rank"] if freq_rec else None,
                    "source_evidence": ev
                })
            if candidates:
                return {
                    "concept_id": cid,
                    "status": "SOURCE_SUPPORTED",
                    "candidates": candidates,
                    "notes": f"Resolved from curated seed: {[c['lemma'] for c in candidates]}"
                }

        # 3. Check Sino-Vietnamese cognate from Kanji via Unihan + vn_freq
        import itertools
        char_readings = [self.hanviet_readings.get(ch, {}).get("sino_vietnamese", []) for ch in ja_surf]
        if all(char_readings) and len(ja_surf) >= 2:
            sino_candidates = []
            for prod in itertools.islice(itertools.product(*char_readings), 16):
                cand_str = " ".join(prod).lower()
                # Check false friends
                if (ja_surf, cand_str) in SINO_VI_FALSE_FRIENDS:
                    continue

                if cand_str in self.vn_by_word:
                    rec = self.vn_by_word[cand_str]
                    sino_candidates.append((cand_str, rec))

            if sino_candidates:
                # Sort by frequency rank
                sino_candidates.sort(key=lambda x: x[1]["rank"])
                best_sino, best_rec = sino_candidates[0]
                ev = self.vn_adapter.build_evidence(
                    locator=best_rec["locator"],
                    field_name="word",
                    extracted_value=best_sino
                ).to_dict()

                candidates.append({
                    "lemma": best_sino,
                    "part_of_speech": en_pos,
                    "definition": f"Từ vựng gốc Hán-Việt tương ứng: {best_sino}",
                    "source_type": "HANVIET_SUPPORTED",
                    "frequency_rank": best_rec["rank"],
                    "source_evidence": ev
                })
                return {
                    "concept_id": cid,
                    "status": "HANVIET_SUPPORTED",
                    "candidates": candidates,
                    "notes": f"Derived via Sino-Vietnamese cognate from '{ja_surf}' -> '{best_sino}' (Rank {best_rec['rank']})"
                }

        # 4. Check if a false friend was detected
        for prod in itertools.islice(itertools.product(*char_readings), 16):
            cand_str = " ".join(prod).lower()
            if (ja_surf, cand_str) in SINO_VI_FALSE_FRIENDS:
                return {
                    "concept_id": cid,
                    "status": "CONFLICTING_SOURCE",
                    "candidates": [],
                    "notes": f"False friend / archaic cognate quarantined: '{ja_surf}' -> '{cand_str}'"
                }

        # 5. No source match
        return {
            "concept_id": cid,
            "status": "NO_SOURCE_MATCH",
            "candidates": [],
            "notes": "No verified open Vietnamese source record found. Eligible for AI candidate fallback."
        }


def main():
    print("=== Testing ViSourceResolver ===")
    resolver = ViSourceResolver()
    canary_path = BASE_DIR / "reports" / "phase1_3d" / "canary_queue.json"
    canary = json.load(open(canary_path))

    test_items = [
        next(x for x in canary if x["en"]["lemma"] == "accurate"),
        next(x for x in canary if x["en"]["lemma"] == "adventure"),
        next(x for x in canary if x["en"]["lemma"] == "will"),
        next(x for x in canary if x["en"]["lemma"] == "actual"),
        next(x for x in canary if x["en"]["lemma"] == "you")
    ]

    for it in test_items:
        res = resolver.resolve(it)
        print(f"[{it['concept_id']}] {it['en']['lemma']} <-> {it['ja']['lemma']}: {res['status']}")
        if res["candidates"]:
            print(f"  candidate: {res['candidates'][0]['lemma']} ({res['candidates'][0]['source_type']})")
        else:
            print(f"  notes: {res['notes']}")


if __name__ == "__main__":
    main()
