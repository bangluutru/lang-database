#!/usr/bin/env python3
"""
scripts/phase1_4/select_corpus.py
Stage 2 of Phase 1.4: learning-value scoring + MATCH-BEFORE-CREATE.

Learning value is a transparent, additive score over *independent* curriculum signals so that
no single list dominates:

    EN  : NGSL rank band (<=500:30, <=1000:27, <=2000:23, <=2809:19) ; NGSL-Spoken +5 ;
          NAWL (academic) +8 ; BSL (business) +8 ; TSL (TOEIC) +6   [EN total capped at 40]
    JA  : JLPT N5:30 N4:26 N3:22 N2:18 N1:12 ; JMdict priority (ichi1/news1/spec1/gai1/nf01-24) +8, tier-2 +4
          [JA total capped at 38]
    VI  : vn_freq rank band (<=500:25, <=1000:22, <=2000:18, <=5000:12, <=10000:6, else 2) [cap 25]
    X   : +6 when >=2 languages carry an independent curriculum signal (cross-language utility),
          +4 when >=3.

Decisions never use score alone - a candidate must also (a) have a corroborated JA side and
(b) not duplicate an existing or already-selected concept.
"""

import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, List, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from scripts.phase1_4.common import CANONICAL_DIR, P14_DIR, read_jsonl, write_jsonl, write_json, baseline_expressions, is_core_sense
from scripts.phase1_4 import lexicons as L
from scripts.phase1_4.build_candidates import gloss_norm


def en_score(sig: Dict[str, Any]) -> int:
    e = sig.get("en")
    if not e:
        return 0
    s = 0
    r = e.get("ngsl_rank")
    if r:
        s = 30 if r <= 500 else 27 if r <= 1000 else 23 if r <= 2000 else 19
    if e.get("ngsl_spoken_rank"):
        s += 5
    if e.get("nawl"):
        s += 8
    if e.get("bsl_rank"):
        s += 8
    if e.get("tsl_rank"):
        s += 6
    return min(s, 40)


def ja_score(sig: Dict[str, Any]) -> int:
    s = 0
    j = sig.get("jlpt")
    if j:
        s += {5: 30, 4: 26, 3: 22, 2: 18, 1: 12}[j["level"]]
    p = sig.get("jmdict_pri", 0)
    s += 8 if p >= 3 else 4 if p == 2 else 0
    return min(s, 38)


def vi_score(sig: Dict[str, Any]) -> int:
    r = sig.get("vi_rank")
    if not r:
        return 0
    return 25 if r <= 500 else 22 if r <= 1000 else 18 if r <= 2000 else 12 if r <= 5000 else 6 if r <= 10000 else 2


def learning_value(sig: Dict[str, Any]) -> Dict[str, Any]:
    a, b, c = en_score(sig), ja_score(sig), vi_score(sig)
    # a language "carries an independent signal" only if its component is meaningful
    langs = sum(1 for x, t in ((a, 10), (b, 10), (c, 10)) if x >= t)
    x = 4 if langs >= 3 else 6 if langs == 2 else 0
    x = 6 if langs == 2 else (10 if langs >= 3 else 0)
    return {"en": a, "ja": b, "vi": c, "cross": x, "langs_with_signal": langs, "total": a + b + c + x}


class ExistingIndex:
    def __init__(self):
        self.exprs = [e for e in baseline_expressions() if e.get('status') != 'retracted']
        self.by_en: Dict[str, List[str]] = defaultdict(list)
        self.by_ja: Dict[str, List[str]] = defaultdict(list)
        self.concept_ja_seq: Dict[str, Tuple[int, int]] = {}
        self.concept_en: Dict[str, str] = {}
        self.concept_ja: Dict[str, str] = {}
        for e in self.exprs:
            cid = e["concept_id"]
            if e["language"] == "en":
                self.by_en[e["lemma"].lower()].append(cid)
                self.concept_en.setdefault(cid, e["lemma"].lower())
            elif e["language"] == "ja":
                self.by_ja[e["lemma"]].append(cid)
                self.concept_ja.setdefault(cid, e["lemma"])
                for ev in e.get("source_evidence", []):
                    m = re.match(r"ent_seq:(\d+), sense_idx:(\d+)", ev.get("source_locator") or "")
                    if m and ev.get("source_id") == "jmdict":
                        self.concept_ja_seq.setdefault(cid, (int(m.group(1)), int(m.group(2))))

    def match(self, cand: Dict[str, Any], jm) -> Tuple[str, str, str]:
        w, ja = cand["en"]["lemma"].lower(), cand["ja"]
        ja_forms = {ja["lemma"], ja.get("wikt_surface")} | {s["lemma"] for s in ja.get("synonyms", [])}
        same_en = self.by_en.get(w, [])
        for cid in same_en:
            if self.concept_ja.get(cid) in ja_forms or self.concept_ja_seq.get(cid, (0, 0))[0] == ja["ent_seq"]:
                return "EXACT_EXISTING_CONCEPT", cid, "same EN lemma and same JA entry/lemma"
        for jl in ja_forms:
            for cid in self.by_ja.get(jl, []):
                # same JA word: is the candidate EN headword just another gloss of the existing JA sense?
                seq = self.concept_ja_seq.get(cid)
                if seq and seq[0] in jm:
                    gl = {gloss_norm(g) for g in jm[seq[0]]["senses"][seq[1]]["glosses"]}
                    if w in gl:
                        return "EXISTING_CONCEPT_NEW_EXPRESSION", cid, f"'{w}' is a gloss of existing JA sense {seq}"
        if same_en:
            # same EN lemma, different JA: synonym vs different sense?
            cand_gl = {gloss_norm(g) for g in ja["jm_glosses"]} - {w}
            for cid in same_en:
                seq = self.concept_ja_seq.get(cid)
                if seq and seq[0] in jm:
                    ex_gl = {gloss_norm(g) for g in jm[seq[0]]["senses"][seq[1]]["glosses"]} - {w}
                    if cand_gl & ex_gl:
                        return "EXISTING_CONCEPT_NEW_EXPRESSION", cid, "JA synonym of existing concept sense (shared JMdict glosses)"
            return "EXISTING_CONCEPT_NEW_SENSE", same_en[0], "same EN lemma, JA sense does not overlap existing sense"
        return "NEW_CONCEPT", "", "no existing concept for this EN lemma or JA entry"


def main():
    cands = read_jsonl(P14_DIR / "candidates.jsonl")
    if (P14_DIR / "candidates_jm.jsonl").exists():           # wave-2 JMdict-anchored candidates
        cands += read_jsonl(P14_DIR / "candidates_jm.jsonl")
    jm = L.load_jmdict()
    ex = ExistingIndex()
    decisions = Counter()
    pool = []
    for c in cands:
        if not c["ja"]:
            decisions["no_corroborated_ja"] += 1
            continue
        lv = learning_value(c["signals"])
        core = is_core_sense(c["en"], c["ja"])
        lv["core_sense"] = core
        if not core:      # lemma-level list signals overstate a rare sense: halve its learning value
            lv["undiscounted_total"] = lv["total"]
            lv["total"] = lv["total"] // 2
        c["value"] = lv
        dec, cid, why = ex.match(c, jm)
        c["match"] = {"decision": dec, "existing_concept_id": cid or None, "reason": why}
        decisions[dec] += 1
        pool.append(c)

    # --- within-batch dedupe (concept-explosion guard) on NEW_CONCEPT / NEW_SENSE only
    creatable = [c for c in pool if c["match"]["decision"] in ("NEW_CONCEPT", "EXISTING_CONCEPT_NEW_SENSE")]
    creatable.sort(key=lambda c: (-c["value"]["total"], c["en"]["lemma"], c["en"]["wikt_line"] or 0, c["en"]["wikt_sense"] or "", c["cand_id"]))
    seen_pair, seen_triple, seen_ja_vi = {}, {}, {}
    for c in creatable:
        k1 = (c["en"]["lemma"], c["en"]["pos"], c["ja"]["ent_seq"])
        k2 = (c["en"]["lemma"], c["en"]["pos"], c["ja"]["lemma"])
        k3 = (c["ja"]["lemma"], c["vi"]["lemma"]) if c["vi"] else None
        dup = None
        if k1 in seen_triple or k2 in seen_pair:
            dup = ("DUPLICATE_IN_BATCH", seen_triple.get(k1) or seen_pair.get(k2), "same EN lemma/POS and same JA entry")
        elif k3 and k3 in seen_ja_vi:
            dup = ("DUPLICATE_IN_BATCH", seen_ja_vi[k3], "same JA+VI primary pair under a different EN synonym headword")
        if dup:
            c["match"] = {"decision": dup[0], "existing_concept_id": None, "duplicate_of_cand": dup[1], "reason": dup[2]}
            decisions["DUPLICATE_IN_BATCH"] += 1
            decisions[c["match"]["decision"] if False else "x"] += 0
            continue
        seen_triple[k1] = seen_pair[k2] = c["cand_id"]
        if k3:
            seen_ja_vi[k3] = c["cand_id"]

    final = Counter(c["match"]["decision"] for c in pool)
    write_jsonl(P14_DIR / "scored_pool.jsonl", pool)
    write_json(P14_DIR / "scored_pool_stats.json", {"input_candidates": len(cands), "pool": len(pool),
                                                      "decisions_before_dedupe": dict(decisions), "final": dict(final)})
    print(dict(final))
    # distribution of creatable by value band, by completeness
    band = Counter()
    for c in pool:
        if c["match"]["decision"] in ("NEW_CONCEPT", "EXISTING_CONCEPT_NEW_SENSE"):
            t = c["value"]["total"]
            b = "60+" if t >= 60 else "45-59" if t >= 45 else "30-44" if t >= 30 else "20-29" if t >= 20 else "10-19" if t >= 10 else "<10"
            band[(b, "tri" if c["vi"] else "en-ja")] += 1
    for k in sorted(band, key=lambda x: (x[0], x[1])):
        print(k, band[k])


if __name__ == "__main__":
    main()
