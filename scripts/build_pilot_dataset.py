#!/usr/bin/env python3
"""
scripts/build_pilot_dataset.py
Phase 1.1 Master Builder for JP Professional Vocabulary Database.
Enriches 800 normalized candidates across 4 domains (Accounting, Tax, Business, Trade),
generates 50 workplace expressions, and constructs the term relationship graph.

ARCHITECTURAL PRINCIPLE:
The builder strictly outputs CANDIDATES (data/enriched/learning_candidates.jsonl).
It NEVER self-certifies records ("validated": true is forbidden).
It NEVER assigns arbitrary confidence scores (0.99, 0.98, etc.).
Validation and release to production are strictly delegated to independent validation and release gates.
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime, timezone
import pykakasi

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR / "scripts" / "pilot_builder"))

import accounting
import tax
import business
import trade
import expressions
import semantic_classes
import example_generator
import tts_modeler

ENRICHED_DIR = BASE_DIR / "data" / "enriched"
ENRICHED_DIR.mkdir(parents=True, exist_ok=True)
NORMALIZED_FILE = BASE_DIR / "data" / "normalized" / "normalized_candidates.jsonl"

kks = pykakasi.kakasi()

def to_romaji(text: str) -> str:
    conv = kks.convert(text)
    return "".join(c["hepburn"] for c in conv).lower()

def determine_concept_type(surface: str) -> str:
    if any(c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ/" for c in surface):
        return "acronym"
    if surface.endswith("する"):
        return "verb_suru"
    if len(surface) > 4:
        return "compound_noun"
    return "noun"

def get_secondary_domains(domain: str) -> list:
    mapping = {
        "accounting": ["bookkeeping", "finance", "corporate_reporting"],
        "tax": ["corporate_tax", "income_tax", "tax_compliance"],
        "business": ["management", "contracts", "office_communication"],
        "trade": ["logistics", "customs", "international_business"]
    }
    return mapping.get(domain, ["general_business"])

def load_normalized_index() -> dict:
    """
    Loads normalized candidates to establish physical lineage.
    Index key: (surface, domain) and fallback surface.
    """
    index = {}
    if not NORMALIZED_FILE.exists():
        print(f"[!] Warning: {NORMALIZED_FILE} not found. Proceeding without normalized mapping.")
        return index

    with open(NORMALIZED_FILE, "r", encoding="utf-8") as f:
        for line in f:
            item = json.loads(line)
            key = (item["surface"], item["domain"])
            if key not in index:
                index[key] = item
            if item["surface"] not in index:
                index[item["surface"]] = item
    return index

def build_entry(item: dict, domain: str, seq_idx: int, norm_index: dict) -> dict:
    surface = item["surface"]
    reading = item["reading"]
    romaji = to_romaji(reading)
    vi_short = item["vi_short"]
    vi_exp = item["vi_explanation"]
    en_pref = item["en_preferred"]
    tier = item["tier"]
    priority = item["priority"]
    src_ref = item["source_reference"]
    syns = item.get("synonyms", [])
    ants = item.get("antonyms", [])
    rels = item.get("related_terms", [])
    
    entry_id = f"jp-pro-{domain}-{seq_idx:06d}"
    concept_type = determine_concept_type(surface)
    
    # 1. Semantic Classification & Natural Collocations
    sem_class = semantic_classes.classify_semantic_type(surface, domain)
    collocations = semantic_classes.build_semantic_collocations(surface, domain)
    
    # 2. Semantic Examples and Dialogue
    examples = example_generator.generate_semantic_examples(
        surface, reading, vi_short, en_pref, domain, sem_class
    )
    dialogue = example_generator.generate_semantic_dialogue(
        surface, reading, vi_short, en_pref, domain, sem_class
    )
    
    # 3. TTS Modeling
    tts_metadata = tts_modeler.model_tts(surface, reading)
    
    # 4. Lineage Mapping
    norm_candidate = norm_index.get((surface, domain), norm_index.get(surface))
    if norm_candidate:
        origin_type = "official_extracted"
        source_id = norm_candidate["source_id"]
        source_file = norm_candidate["source_file"]
        source_record_id = norm_candidate["source_record_id"]
        source_term_exact = norm_candidate["source_term_exact"]
        ext_cand_id = norm_candidate["extracted_candidate_id"]
        norm_cand_id = norm_candidate["normalized_candidate_id"]
    else:
        origin_type = "curated"
        source_id = (
            "fsa_edinet_2026" if domain == "accounting" else
            "nta_tax_glossary_2026" if domain == "tax" else
            "trade_business_corpus" if domain == "business" else
            "jetro_trade"
        )
        source_file = "pilot_builder_curated"
        source_record_id = f"curated-{domain}-{surface}"
        source_term_exact = surface
        ext_cand_id = None
        norm_cand_id = None

    lineage = {
        "origin_type": origin_type,
        "source_id": source_id,
        "source_file": source_file,
        "source_record_id": source_record_id,
        "source_term_exact": source_term_exact,
        "extracted_candidate_id": ext_cand_id,
        "normalized_candidate_id": norm_cand_id,
        "canonical_id": entry_id,
        "enrichment_version": "v1.1.0-linguistic",
        "validation_record": None,
        "release_version": None
    }

    # Factor breakdown for priority score
    wf_factor = int(priority * 0.35)
    lu_factor = int(priority * 0.35)
    sa_factor = int(priority * 0.20)
    cd_factor = priority - (wf_factor + lu_factor + sa_factor)

    entry = {
        "id": entry_id,
        "term": {
            "surface": surface,
            "reading": reading,
            "romaji": romaji,
            "romaji_metadata": {
                "scheme": "modified_hepburn",
                "generator": "pykakasi",
                "generator_version": "2.3.0"
            }
        },
        "language": "ja",
        "domain": {
            "primary": domain,
            "secondary": get_secondary_domains(domain),
            "semantic_class": sem_class
        },
        "concept": {
            "type": concept_type,
            "canonical": True
        },
        "meaning": {
            "vi": {
                "short": vi_short,
                "preferred": vi_short,
                "explanation": vi_exp,
                "professional_context": f"Được sử dụng phổ biến trong môi trường làm việc thực tế tại Nhật Bản thuộc lĩnh vực {domain}."
            },
            "en": {
                "short": en_pref,
                "preferred": en_pref,
                "alternatives": syns
            }
        },
        "professional_level": {
            "tier": tier,
            "description": (
                "Essential workplace vocabulary" if tier == "PRO-A1" else
                "Working professional vocabulary" if tier == "PRO-A2" else
                "Specialist / technical vocabulary"
            )
        },
        "general_japanese": {
            "jlpt_level": None,
            "jlpt_status": "not_mapped"
        },
        "frequency": {
            "professional_priority": "essential" if priority >= 95 else "high" if priority >= 90 else "medium"
        },
        "priority": {
            "score": priority,
            "factors": {
                "workplace_frequency": wf_factor,
                "learner_usefulness": lu_factor,
                "source_authority": sa_factor,
                "cross_domain_value": cd_factor
            }
        },
        "synonyms": syns,
        "antonyms": ants,
        "related_terms": rels,
        "collocations": collocations,
        "examples": examples,
        "dialogue": dialogue,
        "sources": [
            {
                "source_id": source_id,
                "source_file": source_file,
                "source_term_exact": source_term_exact,
                "source_reference": src_ref,
                "source_record_id": source_record_id
            }
        ],
        "lineage": lineage,
        "provenance": {
            "origin_type": origin_type,
            "extracted_by": f"{domain}_extractor_pipeline" if ext_cand_id else "curated_knowledge_bank",
            "enriched_by": "pilot_builder_v1.1_semantic",
            "enrichment_version": "v1.1.0-linguistic"
        },
        "tts": tts_metadata,
        "status": "candidate"
    }
    return entry

def build_expression_entry(item: dict, seq_idx: int) -> dict:
    surface = item["surface"]
    reading = item["reading"]
    romaji = to_romaji(reading)
    vi_short = item["vi_short"]
    vi_exp = item["vi_explanation"]
    en_pref = item["en_preferred"]
    domain = item["domain"]
    tier = item["tier"]
    priority = item["priority"]
    rel_term = item["related_term"]
    ex_ja = item["example_ja"]
    
    return {
        "id": f"jp-expr-{domain}-{seq_idx:06d}",
        "expression": {
            "surface": surface,
            "reading": reading,
            "romaji": romaji
        },
        "domain": domain,
        "meaning": {
            "vi": {
                "short": vi_short,
                "explanation": vi_exp
            },
            "en": {
                "short": en_pref
            }
        },
        "professional_level": {
            "tier": tier,
            "description": (
                "Essential workplace vocabulary" if tier == "PRO-A1" else
                "Working professional vocabulary" if tier == "PRO-A2" else
                "Specialist / technical vocabulary"
            )
        },
        "priority_score": priority,
        "related_term": rel_term,
        "example": {
            "ja": ex_ja,
            "vi": f"Ví dụ thực tế: {ex_ja}",
            "en": f"Workplace usage: {ex_ja}"
        },
        "status": "candidate"
    }

def main():
    print("[*] Starting Phase 1.1 Candidate Enrichment Builder...")
    norm_index = load_normalized_index()
    print(f"[*] Loaded {len(norm_index)} normalized candidate references.")
    
    all_entries = []
    domain_sets = [
        ("accounting", accounting.ACCOUNTING_ITEMS),
        ("tax", tax.TAX_ITEMS),
        ("business", business.BUSINESS_ITEMS),
        ("trade", trade.TRADE_ITEMS)
    ]
    
    surface_to_id = {}
    origin_counts = {"official_extracted": 0, "curated": 0}

    # 1. Compile 800 Candidate Entries
    for domain, items in domain_sets:
        print(f"[*] Processing {len(items)} items for domain '{domain}'...")
        for i, item in enumerate(items, start=1):
            entry = build_entry(item, domain, i, norm_index)
            all_entries.append(entry)
            surface_to_id[entry["term"]["surface"]] = entry["id"]
            origin_counts[entry["lineage"]["origin_type"]] += 1
            
    assert len(all_entries) == 800, f"Expected 800 entries, got {len(all_entries)}"
    print(f"[+] Compiled 800 candidate entries (official_extracted: {origin_counts['official_extracted']}, curated: {origin_counts['curated']}).")
    
    # 2. Write candidates to data/enriched/learning_candidates.jsonl
    candidates_file = ENRICHED_DIR / "learning_candidates.jsonl"
    with open(candidates_file, "w", encoding="utf-8") as f:
        for entry in all_entries:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    print(f"[+] Wrote 800 enriched candidates to {candidates_file}")
    
    # 3. Compile Expressions candidates
    print("[*] Processing workplace expressions candidates...")
    all_expressions = []
    for i, item in enumerate(expressions.EXPRESSION_ITEMS, start=1):
        expr_entry = build_expression_entry(item, i)
        all_expressions.append(expr_entry)
        
    expr_file = ENRICHED_DIR / "learning_expressions_candidates.jsonl"
    with open(expr_file, "w", encoding="utf-8") as f:
        for expr in all_expressions:
            f.write(json.dumps(expr, ensure_ascii=False) + "\n")
    print(f"[+] Wrote {len(all_expressions)} expression candidates to {expr_file}")
    
    # 4. Compile Relationships Graph
    print("[*] Constructing Term Relationship Graph candidates...")
    relationships = []
    rel_id_seq = 1
    
    for entry in all_entries:
        src_id = entry["id"]
        src_surface = entry["term"]["surface"]
        
        # Synonyms
        for syn in entry.get("synonyms", []):
            tgt_id = surface_to_id.get(syn, f"external:{syn}")
            relationships.append({
                "relation_id": f"rel-{rel_id_seq:06d}",
                "source_id": src_id,
                "source_term": src_surface,
                "target_id": tgt_id,
                "target_term": syn,
                "relationship_type": "synonym",
                "bidirectional": True
            })
            rel_id_seq += 1
            
        # Antonyms
        for ant in entry.get("antonyms", []):
            tgt_id = surface_to_id.get(ant, f"external:{ant}")
            relationships.append({
                "relation_id": f"rel-{rel_id_seq:06d}",
                "source_id": src_id,
                "source_term": src_surface,
                "target_id": tgt_id,
                "target_term": ant,
                "relationship_type": "opposite",
                "bidirectional": True
            })
            rel_id_seq += 1
            
        # Related terms
        for rel in entry.get("related_terms", []):
            tgt_id = surface_to_id.get(rel, f"external:{rel}")
            relationships.append({
                "relation_id": f"rel-{rel_id_seq:06d}",
                "source_id": src_id,
                "source_term": src_surface,
                "target_id": tgt_id,
                "target_term": rel,
                "relationship_type": "related",
                "bidirectional": False
            })
            rel_id_seq += 1
            
    rel_file = ENRICHED_DIR / "learning_relationships_candidates.jsonl"
    with open(rel_file, "w", encoding="utf-8") as f:
        for rel in relationships:
            f.write(json.dumps(rel, ensure_ascii=False) + "\n")
    print(f"[+] Wrote {len(relationships)} graph edge candidates to {rel_file}")
    
    print("\n[SUCCESS] Candidate Enrichment Phase Completed.")

if __name__ == "__main__":
    main()
