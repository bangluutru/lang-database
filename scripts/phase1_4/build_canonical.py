#!/usr/bin/env python3
"""
scripts/phase1_4/build_canonical.py
Stage 5: deterministic APPEND-ONLY promotion of gate-approved concepts into data/canonical/.

* The sealed Phase 1.3D bytes of every canonical JSONL are verified against
  data/releases/phase1_3d-sealed/baseline_manifest.json and then kept verbatim.
* Phase 1.4 records are appended after them, in sorted-ID order, with no wall-clock values, so
  repeated builds are byte-identical.
* Existing concepts are only ever *referenced* (classification backfill rows are additive).
"""

import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from scripts.phase1_4.common import (BASE_DIR, CANONICAL_DIR, P14_DIR, PHASE_TS, REPORTS_DIR, read_jsonl, sha8,
                                     slug, write_json, write_jsonl)
from scripts.phase1_4 import lexicons as L
from scripts.phase1_4 import judge as J
from scripts.phase1_4.route import route
from scripts.phase1_4.ai import BatchAI, item_key
from scripts.phase1_4 import gen_vi

MANIFEST = BASE_DIR / "data" / "releases" / "phase1_3d-sealed" / "baseline_manifest.json"
FILES = ["concepts", "senses", "expressions", "classifications"]

# ------------------------------------------------------------------ domains
TOPIC_DOMAIN = {
    "business": "business", "finance": "finance", "economics": "finance", "banking": "finance", "money": "finance",
    "accounting": "accounting", "computing": "it", "internet": "it", "software": "it", "programming": "it",
    "computer-science": "it", "electronics": "it", "telecommunications": "it", "medicine": "healthcare",
    "anatomy": "healthcare", "pathology": "healthcare", "pharmacology": "healthcare", "health": "healthcare",
    "dentistry": "healthcare", "sciences": "science", "natural-sciences": "science", "physical-sciences": "science",
    "physics": "science", "chemistry": "science", "biology": "science", "mathematics": "science",
    "geology": "science", "astronomy": "science", "botany": "science", "zoology": "science", "ecology": "science",
    "organic-chemistry": "science", "biochemistry": "science", "microbiology": "science", "geography": "science",
    "meteorology": "science", "statistics": "science", "transport": "travel", "travel": "travel", "tourism": "travel",
    "aviation": "travel", "railways": "travel", "education": "education", "school": "education",
    "academia": "education", "trade": "trade", "commerce": "trade", "engineering": "manufacturing",
    "manufacturing": "manufacturing", "industry": "manufacturing", "mechanical-engineering": "manufacturing",
    "construction": "manufacturing", "logistics": "logistics", "shipping": "logistics", "nautical": "logistics",
}
JM_FIELD_DOMAIN = {"comp": "it", "med": "healthcare", "anat": "healthcare", "finc": "finance", "econ": "finance",
                   "bus": "business", "math": "science", "physics": "science", "chem": "science", "biol": "science",
                   "geol": "science", "astron": "science", "bot": "science", "zool": "science", "engr": "manufacturing",
                   "food": "daily_life", "ling": "education", "Buddh": "general"}


def domains_for(c: Dict[str, Any], en_sig: Dict[str, Any]) -> Tuple[List[str], str]:
    ds = set()
    for t in c["en"].get("wikt_topics", []):
        if t in TOPIC_DOMAIN:
            ds.add(TOPIC_DOMAIN[t])
    for f in c["ja"].get("jm_field", []):
        if f in JM_FIELD_DOMAIN and JM_FIELD_DOMAIN[f] != "general":
            ds.add(JM_FIELD_DOMAIN[f])
    if en_sig.get("bsl_rank"):
        ds.add("business")
    if en_sig.get("nawl"):
        ds.add("education")
    sig = c["signals"]
    common = ((sig.get("jlpt") or {}).get("level", 0) >= 4 or (en_sig.get("ngsl_rank") or 10 ** 6) <= 2000
              or (sig.get("vi_rank") or 10 ** 6) <= 2000)
    if common and not (ds - {"education"}):
        ds.add("daily_life")
    order = ["business", "accounting", "finance", "logistics", "trade", "manufacturing", "it", "science",
             "healthcare", "travel", "education", "daily_life"]
    out = [d for d in order if d in ds]
    primary = out[0] if out else "general"
    return (["general"] + out if out else ["general"]), primary


# ------------------------------------------------------------------ evidence factory
class Ev:
    def __init__(self):
        self.meta = {}
        for sid, ver in (("wiktionary_en", "2026-09-28"), ("jmdict", "2026-10-01"), ("ngsl", "1.2"),
                         ("ngsl_spoken", "1.2"), ("nawl", "1.2"), ("bsl", "1.2"), ("tsl", "1.2"),
                         ("vn_freq", "1.0"), ("jlpt_consensus", "2026-v1")):
            self.meta[sid] = (ver, L.verify_snapshot(sid, ver))

    def src(self, sid: str, locator: str, field: str, value: str, review_status: str = "verified") -> Dict[str, Any]:
        ver, m = self.meta[sid]
        lic = m["license"]
        return {"source_id": sid, "source_version": ver, "source_locator": locator, "source_record_id": None,
                "field_name": field, "extracted_value": str(value)[:200], "origin": "source_derived", "model": None,
                "generation_version": None, "input_hash": None, "generated_at": None,
                "raw_sha256": m["artifact_sha256"], "curated_sha256": None, "retrieved_at": m["retrieved_at"],
                "curated_at": None, "source_url": m["upstream_url"], "reference_url": m.get("license_url"),
                "license": lic, "commercial_use": True, "redistribution_allowed": True, "derivatives_allowed": True,
                "attribution_required": True, "share_alike": lic.startswith("CC-BY-SA") or lic.startswith("ODbL"),
                "review_status": review_status}

    @staticmethod
    def ai(model: str, version: str, locator: str, field: str, value: str, input_hash: str, generated_at: str) -> Dict[str, Any]:
        return {"source_id": model, "source_version": model.split("-", 1)[-1][:8], "source_locator": locator,
                "source_record_id": None, "field_name": field, "extracted_value": str(value)[:200],
                "origin": "ai_generated", "model": model, "generation_version": version, "input_hash": input_hash,
                "generated_at": generated_at, "raw_sha256": None, "curated_sha256": None, "retrieved_at": None,
                "curated_at": None, "source_url": None, "reference_url": None, "license": "CC-BY-4.0",
                "commercial_use": True, "redistribution_allowed": True, "derivatives_allowed": True,
                "attribution_required": True, "share_alike": False, "review_status": "verified"}


# ------------------------------------------------------------------ classification builders
def cls(target: str, system: str, value: str, status: str, source: str, prov: str, method: Optional[str] = None,
        suffix: str = "", extra: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    d = {"classification_id": f"class-{target}-{system.lower()}{suffix}", "target_type": "concept", "target_id": target,
         "system": system, "value": value, "status": status}
    if method:
        d["classification_method"] = method
    d.update({"agreement_ratio": 1.0, "source_id": source, "provenance_type": prov, "created_at": PHASE_TS})
    if extra:
        d.update(extra)
    return d


def en_classifications(target: str, lemma: str, en: Dict[str, Any]) -> List[Dict[str, Any]]:
    out = []
    ngsl = en.get("ngsl_rank")
    if ngsl:
        out.append(cls(target, "NGSL", f"Rank {ngsl}", "source_derived", "ngsl", "SOURCE_DERIVED"))
    if en.get("ngsl_spoken_rank"):
        out.append(cls(target, "NGSL_SPOKEN", f"Rank {en['ngsl_spoken_rank']}", "source_derived", "ngsl_spoken", "SOURCE_DERIVED"))
    if en.get("nawl"):
        out.append(cls(target, "NAWL", "Member", "source_derived", "nawl", "SOURCE_DERIVED"))
    if en.get("bsl_rank"):
        out.append(cls(target, "BUSINESS_SERVICE_LIST", f"Rank {en['bsl_rank']}", "source_derived", "bsl", "SOURCE_DERIVED"))
    # CEFR / EIKEN: INFERRED from list membership (no official vocabulary-level list is claimed)
    cefr = eiken = src = None
    if ngsl:
        cefr, eiken = (("A1", "Grade 5/4") if ngsl <= 500 else ("A2", "Grade 3") if ngsl <= 1000 else
                       ("B1", "Grade Pre-2") if ngsl <= 2000 else ("B2", "Grade 2")), None
        cefr, eiken = cefr
        src = "ngsl"
    elif en.get("bsl_rank") or en.get("tsl_rank") or en.get("ngsl_spoken_rank"):
        cefr, eiken, src = "B2", "Grade 2", ("bsl" if en.get("bsl_rank") else "tsl" if en.get("tsl_rank") else "ngsl_spoken")
    elif en.get("nawl"):
        cefr, eiken, src = "C1", "Grade Pre-1", "nawl"
    if cefr:
        out.append(cls(target, "CEFR", cefr, "inferred", src, "INFERRED", "list_rank_band_derived"))
        out.append(cls(target, "EIKEN", eiken, "inferred", src, "INFERRED", "cefr_grade_mapped"))
    if en.get("tsl_rank") or en.get("bsl_rank"):
        out.append(cls(target, "TOEIC", "High Relevance", "inferred", "tsl" if en.get("tsl_rank") else "bsl",
                       "INFERRED", "list_membership_derived", extra={"exam_relevance": "high"}))
    if en.get("nawl"):
        for sysname, topic in (("IELTS", "academic"), ("TOEFL", "academic_lecture")):
            out.append(cls(target, sysname, "High Relevance", "inferred", "nawl", "INFERRED", "list_membership_derived",
                           extra={"exam_topic": topic, "exam_relevance": "high"}))
    return out


def vi_core_class(target: str, rank: Optional[int]) -> List[Dict[str, Any]]:
    if not rank:
        return []
    band = ("VI_CORE_500" if rank <= 500 else "VI_CORE_1000" if rank <= 1000 else "VI_CORE_2000" if rank <= 2000
            else "VI_CORE_5000" if rank <= 5000 else "VI_GENERAL")
    return [cls(target, band, f"Rank {rank}", "corpus_derived", "vn_freq", "SOURCE_DERIVED",
                suffix="-" + band.lower().replace("_", "-") if False else "")]


def joyo_class(target: str, lemma: str, joyo: Dict[str, int]) -> List[Dict[str, Any]]:
    kan = [ch for ch in lemma if "一" <= ch <= "鿿"]
    if not kan or any(k not in joyo for k in kan):
        return []
    g = max(joyo[k] for k in kan)
    return [cls(target, "JOYO_KANJI", f"Grade {g}", "official_reference", "joyo", "SOURCE_DERIVED", suffix=f"-grade-{g}")]


def jlpt_class(target: str, sig: Dict[str, Any]) -> List[Dict[str, Any]]:
    j = sig.get("jlpt")
    if not j:
        return []
    return [cls(target, "JLPT", f"N{j['level']}", "community_consensus", "jlpt_consensus", "SOURCE_DERIVED", suffix=f"-n{j['level']}")]


# ------------------------------------------------------------------ main build
def verify_and_base() -> Dict[str, bytes]:
    """Return the protected prefix of every canonical file. If Phase 1.4.1 corrections were applied, the protected prefix is
    the CORRECTED one (its hash is pinned in the manifest; reverting the ledger reproduces the sealed 1.3D bytes)."""
    man = json.loads(MANIFEST.read_text())
    base = {}
    for name in FILES + ["examples"]:
        f = f"{name}.jsonl"
        info = man.get("corrected_prefix", {}).get(f) or man["append_only"][f]
        cur = (CANONICAL_DIR / f).read_bytes()
        pref = cur[:info["bytes"]]
        if hashlib.sha256(pref).hexdigest() != info["sha256"]:
            raise SystemExit(f"FROZEN BASELINE VIOLATION: {f} prefix differs from sealed Phase 1.3D")
        base[name] = pref
    return base


from scripts.phase1_4.common import is_core_sense  # noqa: E402



def concept_id_of(c: Dict[str, Any]) -> str:
    en, ja = c["en"], c["ja"]
    return f"concept-lex-{slug(en['lemma'])}-{en['pos'][:3]}-{sha8('%s|%s|%s:%s' % (en['lemma'], en['pos'], ja['ent_seq'], ja['sense_idx']), 6)}"


def load_t4(HO: Path) -> Dict[str, Dict[str, Any]]:
    """concept_id -> accepted Vietnamese proposal from the T4 hand-off (Luna), after Claude's per-item overrides.
    Provenance stays AI_GENERATED either way; the proposer is recorded (gpt-6-luna, or claude when overridden)."""
    out: Dict[str, Dict[str, Any]] = {}
    dec_dir, pk_dir = HO / 'decisions', HO / 'packets'
    ov = json.loads((HO / 'claude_overrides_T4.json').read_text())['overrides'] if (HO / 'claude_overrides_T4.json').exists() else {}
    for p in sorted(dec_dir.glob('T4_*.jsonl')) if dec_dir.exists() else []:
        items = {json.loads(l)['id']: json.loads(l) for l in (pk_dir / p.name).read_text(encoding='utf-8').splitlines() if l.strip()}
        for l in p.read_text(encoding='utf-8').splitlines():
            if not l.strip():
                continue
            d = json.loads(l)
            orig = d.get('reviewer') or 'gpt-6-luna'          # worker agent that wrote the decision (gpt-6-luna | gemini-3.8)
            vi, proposer, was = d.get('vi_lemma'), orig, None
            if d['id'] in ov:
                o = ov[d['id']]
                was, vi, proposer = d.get('vi_lemma'), o['vi'], 'claude-sonnet-5-5'
            if not vi:
                continue
            out[d['id']] = {'vi_lemma': vi, 'proposer': proposer, 'luna_proposal': was if proposer != orig else d.get('vi_lemma'), 'worker': orig,
                            'confidence': d.get('confidence'), 'packet': p.name,
                            'input_hash': hashlib.sha256(json.dumps(items[d['id']], ensure_ascii=False, sort_keys=True).encode()).hexdigest()}
    return out


def build(write: bool = True) -> Dict[str, Any]:
    base = verify_and_base()
    corr = json.loads((P14_DIR / 'baseline_corrections_append.json').read_text()) if (P14_DIR / 'baseline_corrections_append.json').exists() else {'expressions': [], 'classifications': []}
    pool = {c["cand_id"]: c for c in read_jsonl(P14_DIR / "scored_pool.jsonl")}
    results = json.loads((P14_DIR / "judge_results.json").read_text())
    ai_vi = json.loads((P14_DIR / "ai_vi.json").read_text()) if (P14_DIR / "ai_vi.json").exists() else {}
    ev = Ev()
    HO = P14_DIR / 'handoff'
    acc = frozenset(json.loads((HO / 'claude_review_T3.json').read_text())['accepted']) if (HO / 'claude_review_T3.json').exists() else frozenset()
    t4 = load_t4(HO)
    excl = frozenset(json.loads((P14_DIR / 'manual_exclusions.json').read_text())) if (P14_DIR / 'manual_exclusions.json').exists() else frozenset()
    en_lists = L.load_en_lists()
    vn = L.load_vn_freq()
    joyo = {r["kanji"]: r["grade"] for r in json.load(open(BASE_DIR / "data/raw/joyo/2010-official/joyo_kanji_official.json"))}
    judge_ai = BatchAI("judge", "judge")
    judge_prov_cache: Dict[str, Dict[str, Any]] = {}

    routed: Dict[str, Tuple[str, Dict[str, Any]]] = {}
    queues = defaultdict(list)
    for cid in sorted(pool):
        c = pool[cid]
        if c["match"]["decision"] not in ("NEW_CONCEPT", "EXISTING_CONCEPT_NEW_SENSE"):
            continue
        kind, info = route(c, results, ai_vi, excl, acc)
        routed[cid] = (kind, info)
        queues[kind].append(cid)

    # post-judge dedupe over accepted (concept-explosion guard #2)
    accepted_ids = sorted((cid for k in ("ACCEPT_TRI_SOURCE", "ACCEPT_TRI_AI", "ACCEPT_PARTIAL_ENJA") for cid in queues[k]),
                          key=lambda i: (-pool[i]["value"]["total"], i))
    seen1, seen3 = {}, {}
    dups = []
    final_ids = []
    for cid in accepted_ids:
        c = pool[cid]
        kind, info = routed[cid]
        vi = c["vi"]["lemma"] if kind == "ACCEPT_TRI_SOURCE" else (ai_vi[cid]["vi_lemma"] if kind == "ACCEPT_TRI_AI" else None)
        if vi is None and kind == "ACCEPT_PARTIAL_ENJA":              # VI that will be attached from the T4 hand-off
            t4x = t4.get(concept_id_of(c))
            vi = t4x["vi_lemma"] if t4x else None
        k1 = (c["en"]["lemma"], c["en"]["pos"], c["ja"]["ent_seq"], c["ja"]["sense_idx"])
        k3 = (c["ja"]["lemma"], vi) if vi else None
        k4 = (c["en"]["lemma"], c["en"]["pos"], c["ja"]["lemma"])
        if k1 in seen1 or k4 in seen1 or (k3 and k3 in seen3):
            dups.append({"cand_id": cid, "duplicate_of": seen1.get(k1) or seen1.get(k4) or seen3.get(k3)})
            continue
        seen1[k1] = seen1[k4] = cid
        if k3:
            seen3[k3] = cid
        final_ids.append(cid)

    concepts, senses, exprs, classes = [], [], [], []
    used_ids = set()
    rows_meta = []
    judge_model = "gemini-2.5-pro"
    for cid in sorted(final_ids, key=lambda i: (pool[i]["en"]["lemma"], pool[i]["en"]["pos"], i)):
        c = pool[cid]
        kind, info = routed[cid]
        en, ja, sig = c["en"], c["ja"], c["signals"]
        suffix = f"{slug(en['lemma'])}-{en['pos'][:3]}-{sha8('%s|%s|%s:%s' % (en['lemma'], en['pos'], ja['ent_seq'], ja['sense_idx']), 6)}"
        concept_id = f"concept-lex-{suffix}"
        if concept_id in used_ids:
            raise SystemExit(f"ID collision {concept_id}")
        used_ids.add(concept_id)
        sense_id = f"sense-lex-{suffix}-01"
        sig = c["signals"]
        core = is_core_sense(en, ja)
        enl = en_lists.get(en["lemma"].lower(), {}) if core else {}
        sig = sig if core else {}
        doms, primary = domains_for(dict(c, signals=sig), enl)
        t4p = t4.get(concept_id) if kind == "ACCEPT_PARTIAL_ENJA" else None      # Phase 1.4.2: VI proposed in the T4 hand-off
        has_vi = kind in ("ACCEPT_TRI_SOURCE", "ACCEPT_TRI_AI") or bool(t4p)
        vi_lemma = (c["vi"]["lemma"] if kind == "ACCEPT_TRI_SOURCE" else (ai_vi[cid]["vi_lemma"] if kind == "ACCEPT_TRI_AI" else (t4p["vi_lemma"] if t4p else None)))
        tier = "Tier B" if kind == "ACCEPT_TRI_SOURCE" else "Tier C" if (kind == "ACCEPT_TRI_AI" or t4p) else "Tier D"
        jr = info.get("judge_tri") if kind == "ACCEPT_TRI_SOURCE" else info.get("judge_tri_ai") if kind == "ACCEPT_TRI_AI" else (info.get("judge_enja_recheck") or info.get("judge_enja"))
        jkey = {"ACCEPT_TRI_SOURCE": "tri", "ACCEPT_TRI_AI": "tri_ai"}.get(kind, "recheck" if "judge_enja_recheck" in info else "enja")
        meta = {"phase": "1.4", "cand_id": cid, "origin_pipeline": ("jmdict_anchored_gap_fill" if en.get("anchor") == "jmdict" else "wiktionary_sense_block+jmdict_corroboration"),
                "translation_status": "complete" if has_vi else "partial",
                "validation_status": "needs_review" if t4p else "validated",
                "quality_tier": tier, "learning_value": c["value"], "match_decision": c["match"]["decision"],
                "anchor": en.get("anchor", "wiktionary"),
                "list_projection": "core_sense" if core else "not_projected(non-core sense of a lemma-level list entry)",
                "wikt_locator": (f"line:{en['wikt_line']}, sense:{en['wikt_sense']}" if en.get("wikt_line") else None),
                "judge": {"model": judge_model, "prompt_version": J.PROMPT_VERSION, "result_set": jkey,
                          "alignment": {"en_ja": jr.get("en_ja"), "en_vi": jr.get("en_vi"), "ja_vi": jr.get("ja_vi")},
                          "naturalness": jr.get("naturalness"), "verdict": jr.get("verdict"), "confidence": jr.get("confidence")},
                "ja_corroboration": {"jmdict_gloss_score": ja["gloss_score"], "ent_seq": ja["ent_seq"], "sense_idx": ja["sense_idx"]}}
        if info.get("independent_review"):
            meta["independent_review"] = info["independent_review"]
        if t4p:
            meta["vi_proposal"] = {"proposer": t4p["proposer"], "luna_proposal": t4p["luna_proposal"], "packet": t4p["packet"],
                                   "review": "Claude reviewed all flagged proposals + 10% sample of each packet; not independently judged"}
        if c["match"]["decision"] == "EXISTING_CONCEPT_NEW_SENSE":
            meta["polysemy_of"] = c["match"]["existing_concept_id"]
        if not has_vi:
            meta["partial_reason"] = ("vi_source_rejected_by_judge" if info.get("vi_rejected") else
                                      "ai_vi_rejected_by_judge" if info.get("ai_vi_rejected") else "vi_unresolved")
            if info.get("vi_rejected"):
                meta["rejected_vi_candidate"] = info["vi_rejected"]
            if info.get("ai_vi_rejected"):
                meta["rejected_ai_vi_candidate"] = info["ai_vi_rejected"]
        concepts.append({"concept_id": concept_id, "canonical_name": f"lex_{suffix.replace('-', '_')}", "domains": doms,
                         "primary_domain": primary, "status": "canonical", "metadata": meta,
                         "created_at": PHASE_TS, "updated_at": PHASE_TS})
        reg = "informal" if {"informal", "colloquial"} & set(en["wikt_tags"]) else \
              "business" if enl.get("bsl_rank") else "academic" if enl.get("nawl") else "general"
        senses.append({"sense_id": sense_id, "concept_id": concept_id, "part_of_speech": en["pos"],
                       "gloss_en": en["lemma"], "gloss_ja": ja["lemma"], "gloss_vi": vi_lemma,
                       "definition_en": en["wikt_gloss"], "definition_ja": None, "definition_vi": None,
                       "register": reg, "status": "verified", "created_at": PHASE_TS})
        # ---- EN expression
        anchored_jm = en.get("anchor") == "jmdict"
        en_ev = ([ev.src("jmdict", f"ent_seq:{ja['ent_seq']}, sense_idx:{ja['sense_idx']}", "sense_gloss", en["lemma"])]
                 if anchored_jm else
                 [ev.src("wiktionary_en", f"line:{en['wikt_line']}, sense:{en['wikt_sense']}", "headword", en["lemma"])])
        for sid, key, fmt in (("ngsl", "ngsl_rank", "lemma:{l}, rank:{v}"), ("ngsl_spoken", "ngsl_spoken_rank", "lemma:{l}, rank:{v}"),
                              ("bsl", "bsl_rank", "word:{l}, rank:{v}"), ("tsl", "tsl_rank", "word:{l}, rank:{v}"),
                              ("nawl", "nawl", "lemma:{l}")):
            if enl.get(key):
                en_ev.append(ev.src(sid, fmt.format(l=en["lemma"].lower(), v=enl[key]), "lemma", en["lemma"].lower()))
        exprs.append({"expression_id": f"expr-en-lex-{suffix}", "concept_id": concept_id, "sense_id": sense_id,
                      "language": "en", "lemma": en["lemma"], "display_form": en["lemma"], "reading": None,
                      "pronunciation": en.get("ipa"), "romanization": None, "part_of_speech": en["pos"], "register": reg,
                      "usage_notes": None, "language_metadata": {"ipa_source": "wiktionary_en"} if en.get("ipa") else {},
                      "provenance_type": "SOURCE_DERIVED", "source_evidence": en_ev,
                      "license": "CC-BY-SA-3.0" if anchored_jm else "CC-BY-SA-4.0",
                      "status": "verified", "created_at": PHASE_TS})
        # ---- JA expression
        ja_ev = [ev.src("jmdict", f"ent_seq:{ja['ent_seq']}, sense_idx:{ja['sense_idx']}", "primary_surface", ja["lemma"])]
        if not anchored_jm:
            ja_ev.append(ev.src("wiktionary_en", f"line:{en['wikt_line']}, sense:{en['wikt_sense']}", "translation_ja", ja["wikt_surface"]))
        exprs.append({"expression_id": f"expr-ja-lex-{suffix}", "concept_id": concept_id, "sense_id": sense_id,
                      "language": "ja", "lemma": ja["lemma"], "display_form": ja["lemma"], "reading": ja["reading"],
                      "pronunciation": None, "romanization": None, "part_of_speech": en["pos"], "register": reg,
                      "usage_notes": None,
                      "language_metadata": {"jmdict_pos": ja["jm_pos_tags"], "form_note": ja["form_note"],
                                            "wikt_surface": ja["wikt_surface"], "jmdict_glosses": ja["jm_glosses"][:6]},
                      "provenance_type": "SOURCE_DERIVED", "source_evidence": ja_ev, "license": "CC-BY-SA-3.0",
                      "status": "verified", "created_at": PHASE_TS})
        # ---- VI expression
        vi_rank = None
        if has_vi:
            judged_by = {"status": "AI_JUDGE_VALIDATED", "judge_model": judge_model, "prompt_version": J.PROMPT_VERSION}
            if info.get("independent_review"):
                judged_by = {"status": "INDEPENDENT_AGENT_REVIEW", "reviewers": info["independent_review"]["reviewers"],
                             "basis": info["independent_review"]["basis"], "earlier_model_judge": "REVIEW (not auto-accepted)"}
            if kind == "ACCEPT_TRI_SOURCE":
                fr = vn.get(vi_lemma)
                vi_rank = fr["rank"] if fr else None
                vi_ev = [ev.src("wiktionary_en", f"line:{en['wikt_line']}, sense:{en['wikt_sense']}", "translation_vi", vi_lemma)]
                if fr:
                    vi_ev.append(ev.src("vn_freq", f"rank:{fr['rank']}, word:{vi_lemma}", "word", vi_lemma))
                vi_meta = {"lexeme_source": {"status": "SOURCE_DERIVED", "source": "wiktionary_en"},
                           "corpus_attestation": {"vn_freq_rank": vi_rank, "vn_freq_pos": fr["pos"] if fr else []},
                           "translation_semantics_validated": judged_by}
                prov, lic = "SOURCE_DERIVED", "CC-BY-SA-4.0"
            elif t4p:
                fr = vn.get(vi_lemma)
                vi_rank = fr["rank"] if fr else None
                vi_ev = [Ev.ai(t4p["proposer"], "handoff_T4_v1", f"concept:{concept_id}, sense:{sense_id}", "vi_candidate", vi_lemma,
                               t4p["input_hash"], "2026-10-03T00:00:00Z")]
                vi_meta = {"lexeme_source": {"status": "AI_GENERATED", "source": t4p["proposer"]},
                           "corpus_attestation": {"vn_freq_rank": vi_rank, "vn_freq_pos": fr["pos"] if fr else []},
                           "translation_semantics_validated": {"status": "AGENT_PROPOSED_PARTIALLY_REVIEWED", "proposer": t4p["proposer"],
                                                               "reviewer": "claude-sonnet-5-5", "luna_proposal": t4p["luna_proposal"], "worker_agent": t4p["worker"]}}
                prov, lic = "AI_GENERATED", "CC-BY-4.0"
            else:
                g = ai_vi[cid]
                fr = vn.get(vi_lemma)
                vi_rank = fr["rank"] if fr else None
                vi_ev = [Ev.ai(g["model"], g["prompt_version"], f"concept:{concept_id}, sense:{sense_id}", "vi_candidate",
                               vi_lemma, g["input_hash"], g["generated_at"])]
                vi_meta = {"lexeme_source": {"status": "AI_GENERATED", "source": g["model"]},
                           "corpus_attestation": {"vn_freq_rank": vi_rank, "vn_freq_pos": fr["pos"] if fr else []},
                           "ai_definition_vi": g.get("definition_vi"),
                           "translation_semantics_validated": judged_by}
                prov, lic = "AI_GENERATED", "CC-BY-4.0"
            exprs.append({"expression_id": f"expr-vi-lex-{suffix}", "concept_id": concept_id, "sense_id": sense_id,
                          "language": "vi", "lemma": vi_lemma, "display_form": vi_lemma, "reading": None,
                          "pronunciation": None, "romanization": None, "part_of_speech": en["pos"], "register": reg,
                          "usage_notes": None, "language_metadata": vi_meta, "provenance_type": prov,
                          "source_evidence": vi_ev, "license": lic, "status": "verified", "created_at": PHASE_TS})
        # ---- classifications (views)
        classes += en_classifications(concept_id, en["lemma"], enl)
        classes += jlpt_class(concept_id, sig)
        classes += joyo_class(concept_id, ja["lemma"], joyo)
        classes += vi_core_class(concept_id, vi_rank)
        rows_meta.append((concept_id, kind))

    # ---- additive classification backfill for existing concepts (views only; no record is modified)
    backfill = backfill_existing(en_lists, vn)
    classes += backfill
    classes += corr['classifications']
    exprs += corr['expressions']

    # ---- dedupe classification ids (stable)
    seen = set()
    uniq = []
    existing_cids = {json.loads(l)["classification_id"] for l in base["classifications"].decode().splitlines() if l.strip()}
    for k in sorted(classes, key=lambda x: x["classification_id"]):
        if k["classification_id"] in seen or k["classification_id"] in existing_cids:
            continue
        seen.add(k["classification_id"])
        uniq.append(k)
    classes = uniq

    def ser(rows):
        return "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows).encode("utf-8")

    concepts.sort(key=lambda r: r["concept_id"])
    senses.sort(key=lambda r: r["sense_id"])
    exprs.sort(key=lambda r: r["expression_id"])
    assert len({e["expression_id"] for e in exprs}) == len(exprs)
    out_bytes = {"concepts": base["concepts"] + ser(concepts), "senses": base["senses"] + ser(senses),
                 "expressions": base["expressions"] + ser(exprs), "classifications": base["classifications"] + ser(classes)}
    summary = {"new_concepts": len(concepts), "new_senses": len(senses), "new_expressions": len(exprs),
               "new_classifications": len(classes), "backfill_classifications": len([b for b in backfill if b["classification_id"] in seen]),
               "by_kind": dict(Counter(k for _, k in rows_meta)), "post_judge_duplicates": len(dups),
               "queues": {k: len(v) for k, v in queues.items()}}
    if write:
        for name, b in out_bytes.items():
            (CANONICAL_DIR / f"{name}.jsonl").write_bytes(b)
        write_json(P14_DIR / "build_summary.json", summary)
        write_jsonl(P14_DIR / "review_queue.jsonl", [dict(cand_id=i, **{"en": pool[i]["en"]["lemma"], "ja": pool[i]["ja"]["lemma"], "vi": (pool[i]["vi"] or {}).get("lemma"),
                                                                       "judge": routed[i][1].get("judge_tri") or routed[i][1].get("judge_enja")}) for i in sorted(queues["REVIEW"])])
        write_jsonl(P14_DIR / "rejected.jsonl", [dict(cand_id=i, **{"en": pool[i]["en"]["lemma"], "en_sense": pool[i]["en"]["wikt_gloss"][:120], "ja": pool[i]["ja"]["lemma"], "vi": (pool[i]["vi"] or {}).get("lemma"),
                                                                    "judge": routed[i][1].get("judge_tri") or routed[i][1].get("judge_enja")}) for i in sorted(queues["REJECT"])])
        write_jsonl(P14_DIR / "post_judge_duplicates.jsonl", dups)
    print(json.dumps(summary, indent=1))
    return summary


def backfill_existing(en_lists, vn) -> List[Dict[str, Any]]:
    """Additive view rows for the sealed 2,106 concepts: EN-list memberships and VI core bands
    that were not materialised in Phase 1.3C/D. Nothing existing is modified."""
    exprs = read_jsonl(CANONICAL_DIR / "expressions.jsonl")
    # only baseline expressions (not the ones we are about to write)
    man = json.loads(MANIFEST.read_text())
    n_base = man["append_only"]["expressions.jsonl"]["lines"]
    exprs = exprs[:n_base]
    by_c: Dict[str, Dict[str, List[Dict[str, Any]]]] = defaultdict(lambda: defaultdict(list))
    for e in exprs:
        by_c[e["concept_id"]][e["language"]].append(e)
    existing = read_jsonl(CANONICAL_DIR / "classifications.jsonl")[:man["append_only"]["classifications.jsonl"]["lines"]]
    have = {(c.get("target_id"), c.get("system")) for c in existing if "system" in c and c.get("status") != "retracted"}
    out = []
    for cid in sorted(by_c):
        if cid.startswith("concept-pro-"):
            continue  # professional records stay untouched, including views
        en_l = by_c[cid].get("en")
        if en_l:
            lem = en_l[0]["lemma"].lower()
            enl = en_lists.get(lem, {})
            for row in en_classifications(cid, lem, enl):
                if row["system"] in ("NGSL_SPOKEN", "NAWL", "BUSINESS_SERVICE_LIST") and (cid, row["system"]) not in have:
                    row["backfill"] = "phase1.4"
                    out.append(row)
        vi_l = by_c[cid].get("vi")
        if vi_l:
            fr = vn.get(vi_l[0]["lemma"].lower())
            if fr:
                have_vi = any((cid, s) in have for s in ("VI_CORE_500", "VI_CORE_1000", "VI_CORE_2000", "VI_CORE_5000", "VI_GENERAL"))
                if not have_vi:
                    for row in vi_core_class(cid, fr["rank"]):
                        row["backfill"] = "phase1.4"
                        out.append(row)
    return out


if __name__ == "__main__":
    build()
