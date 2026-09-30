#!/usr/bin/env python3
"""
scripts/export_sqlite.py
Exports the canonical JSONL production datasets into an indexed SQLite relational database
with Full-Text Search (FTS5) for local rapid querying, lesson compilation, and curriculum planning.
"""

import sys
import json
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
PROD_DIR = BASE_DIR / "data" / "production"
DB_FILE = PROD_DIR / "jp_professional.db"

def export():
    print(f"[*] Exporting JSONL datasets to SQLite database: {DB_FILE} ...")
    if DB_FILE.exists():
        DB_FILE.unlink()
        
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # 1. Create vocabulary table
    cursor.execute("""
    CREATE TABLE vocabulary (
        id TEXT PRIMARY KEY,
        surface TEXT NOT NULL,
        reading TEXT NOT NULL,
        romaji TEXT NOT NULL,
        domain TEXT NOT NULL,
        secondary_domains TEXT,
        concept_type TEXT NOT NULL,
        vi_short TEXT NOT NULL,
        vi_explanation TEXT NOT NULL,
        en_short TEXT NOT NULL,
        en_preferred TEXT NOT NULL,
        tier TEXT NOT NULL,
        priority_score INTEGER NOT NULL,
        jlpt_level TEXT,
        sources_json TEXT NOT NULL,
        collocations_json TEXT,
        examples_json TEXT,
        dialogue_json TEXT,
        tts_json TEXT,
        raw_json TEXT NOT NULL
    );
    """)
    
    # 2. Create expressions table
    cursor.execute("""
    CREATE TABLE expressions (
        id TEXT PRIMARY KEY,
        surface TEXT NOT NULL,
        reading TEXT NOT NULL,
        romaji TEXT NOT NULL,
        domain TEXT NOT NULL,
        vi_short TEXT NOT NULL,
        vi_explanation TEXT NOT NULL,
        en_short TEXT NOT NULL,
        tier TEXT NOT NULL,
        priority_score INTEGER NOT NULL,
        related_term TEXT,
        raw_json TEXT NOT NULL
    );
    """)
    
    # 3. Create relationships table
    cursor.execute("""
    CREATE TABLE relationships (
        relation_id TEXT PRIMARY KEY,
        source_id TEXT NOT NULL,
        source_term TEXT NOT NULL,
        target_id TEXT NOT NULL,
        target_term TEXT NOT NULL,
        relationship_type TEXT NOT NULL,
        bidirectional INTEGER NOT NULL
    );
    """)
    
    # 4. Create FTS5 Virtual Table for Instant Search
    cursor.execute("""
    CREATE VIRTUAL TABLE vocabulary_fts USING fts5(
        id UNINDEXED,
        surface,
        reading,
        romaji,
        domain,
        vi_short,
        vi_explanation,
        en_preferred,
        content='vocabulary',
        content_rowid='rowid'
    );
    """)
    
    # 5. Populate vocabulary
    vocab_file = PROD_DIR / "vocabulary.jsonl"
    with open(vocab_file, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            e = json.loads(line)
            cursor.execute("""
            INSERT INTO vocabulary (
                id, surface, reading, romaji, domain, secondary_domains,
                concept_type, vi_short, vi_explanation, en_short, en_preferred,
                tier, priority_score, jlpt_level, sources_json, collocations_json,
                examples_json, dialogue_json, tts_json, raw_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                e["id"],
                e["term"]["surface"],
                e["term"]["reading"],
                e["term"]["romaji"],
                e["domain"]["primary"],
                json.dumps(e["domain"]["secondary"], ensure_ascii=False),
                e["concept"]["type"],
                e["meaning"]["vi"]["short"],
                e["meaning"]["vi"]["explanation"],
                e["meaning"]["en"]["short"],
                e["meaning"]["en"]["preferred"],
                e["professional_level"]["tier"],
                e["priority"]["score"],
                e.get("general_japanese", {}).get("jlpt_level"),
                json.dumps(e["sources"], ensure_ascii=False),
                json.dumps(e["collocations"], ensure_ascii=False),
                json.dumps(e["examples"], ensure_ascii=False),
                json.dumps(e["dialogue"], ensure_ascii=False),
                json.dumps(e["tts"], ensure_ascii=False),
                line.strip()
            ))
            
    # Populate FTS
    cursor.execute("""
    INSERT INTO vocabulary_fts (rowid, id, surface, reading, romaji, domain, vi_short, vi_explanation, en_preferred)
    SELECT rowid, id, surface, reading, romaji, domain, vi_short, vi_explanation, en_preferred FROM vocabulary;
    """)
    
    # 6. Populate expressions
    expr_file = PROD_DIR / "expressions.jsonl"
    with open(expr_file, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            e = json.loads(line)
            cursor.execute("""
            INSERT INTO expressions (
                id, surface, reading, romaji, domain, vi_short, vi_explanation,
                en_short, tier, priority_score, related_term, raw_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                e["id"],
                e["expression"]["surface"],
                e["expression"]["reading"],
                e["expression"]["romaji"],
                e["domain"],
                e["meaning"]["vi"]["short"],
                e["meaning"]["vi"]["explanation"],
                e["meaning"]["en"]["short"],
                e["professional_level"]["tier"],
                e["priority_score"],
                e.get("related_term", ""),
                line.strip()
            ))
            
    # 7. Populate relationships
    rel_file = PROD_DIR / "relationships.jsonl"
    with open(rel_file, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            r = json.loads(line)
            cursor.execute("""
            INSERT INTO relationships (
                relation_id, source_id, source_term, target_id, target_term,
                relationship_type, bidirectional
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                r["relation_id"],
                r["source_id"],
                r["source_term"],
                r["target_id"],
                r["target_term"],
                r["relationship_type"],
                1 if r.get("bidirectional") else 0
            ))
            
    # 8. Create Indexes
    cursor.execute("CREATE INDEX idx_vocab_domain ON vocabulary(domain);")
    cursor.execute("CREATE INDEX idx_vocab_tier ON vocabulary(tier);")
    cursor.execute("CREATE INDEX idx_vocab_priority ON vocabulary(priority_score);")
    cursor.execute("CREATE INDEX idx_vocab_surface ON vocabulary(surface);")
    cursor.execute("CREATE INDEX idx_rel_source ON relationships(source_id);")
    cursor.execute("CREATE INDEX idx_rel_target ON relationships(target_id);")
    cursor.execute("CREATE INDEX idx_rel_type ON relationships(relationship_type);")
    
    conn.commit()
    
    # 9. Verify counts
    cursor.execute("SELECT COUNT(*) FROM vocabulary")
    v_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM expressions")
    e_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM relationships")
    r_count = cursor.fetchone()[0]
    
    print(f"[+] SQLite Database Created: {DB_FILE}")
    print(f"    - Table vocabulary: {v_count} rows")
    print(f"    - Table expressions: {e_count} rows")
    print(f"    - Table relationships: {r_count} rows")
    
    # 10. Test sample downstream query from Directive Section 43
    print("\n[*] Testing Downstream Lesson Query (Domain=accounting, Level=PRO-A1, Limit=5)...")
    cursor.execute("""
    SELECT id, surface, reading, vi_short, en_preferred, priority_score
    FROM vocabulary
    WHERE domain = 'accounting' AND tier = 'PRO-A1'
    ORDER BY priority_score DESC
    LIMIT 5;
    """)
    sample_rows = cursor.fetchall()
    for row in sample_rows:
        print(f"    {row[0]} | {row[1]} ({row[2]}) | {row[3]} | {row[4]} | Score: {row[5]}")
        
    # Test FTS query
    print("\n[*] Testing FTS5 Search for 'khấu trừ'...")
    cursor.execute("""
    SELECT v.id, v.surface, v.reading, v.vi_short
    FROM vocabulary_fts f
    JOIN vocabulary v ON f.id = v.id
    WHERE vocabulary_fts MATCH 'khấu'
    LIMIT 3;
    """)
    fts_rows = cursor.fetchall()
    for row in fts_rows:
        print(f"    Match: {row[0]} | {row[1]} ({row[2]}) | {row[3]}")
        
    conn.close()

if __name__ == "__main__":
    export()
