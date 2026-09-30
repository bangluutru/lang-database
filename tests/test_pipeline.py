"""
tests/test_pipeline.py
Integration tests validating the data pipeline, SQLite export, and source registry consistency.
"""

import sqlite3
import yaml
from pathlib import Path
import pytest

BASE_DIR = Path(__file__).resolve().parent.parent
DB_FILE = BASE_DIR / "data" / "production" / "jp_professional.db"
REGISTRY_FILE = BASE_DIR / "data" / "sources" / "source_registry.yaml"

@pytest.fixture(scope="module")
def db_conn():
    assert DB_FILE.exists(), f"Database not found at {DB_FILE}"
    conn = sqlite3.connect(DB_FILE)
    yield conn
    conn.close()

def test_sqlite_counts(db_conn):
    cursor = db_conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM vocabulary")
    assert cursor.fetchone()[0] == 800
    cursor.execute("SELECT COUNT(*) FROM expressions")
    assert cursor.fetchone()[0] == 50
    cursor.execute("SELECT COUNT(*) FROM relationships")
    assert cursor.fetchone()[0] == 2078

def test_downstream_lesson_query(db_conn):
    cursor = db_conn.cursor()
    # Query: 30 PRO-A1 accounting terms for Vietnamese learners
    cursor.execute("""
    SELECT id, surface, reading, vi_short, en_preferred
    FROM vocabulary
    WHERE domain = 'accounting' AND tier = 'PRO-A1'
    ORDER BY priority_score DESC
    LIMIT 30;
    """)
    rows = cursor.fetchall()
    assert len(rows) >= 30
    for r in rows:
        assert r[0].startswith("jp-pro-accounting-")
        assert len(r[1]) > 0
        assert len(r[2]) > 0
        assert len(r[3]) > 0

def test_fts5_search(db_conn):
    cursor = db_conn.cursor()
    cursor.execute("""
    SELECT v.id, v.surface, v.vi_short
    FROM vocabulary_fts f
    JOIN vocabulary v ON f.id = v.id
    WHERE vocabulary_fts MATCH 'hóa đơn'
    LIMIT 5;
    """)
    results = cursor.fetchall()
    assert len(results) > 0

def test_source_registry_integrity():
    assert REGISTRY_FILE.exists()
    with open(REGISTRY_FILE, "r", encoding="utf-8") as f:
        registry = yaml.safe_load(f)
    
    source_ids = {s["source_id"] for s in registry.get("sources", [])}
    assert "fsa_edinet_2026" in source_ids
    assert "nta_tax_glossary_2026" in source_ids
    assert "jicpa_glossary" in source_ids
    assert "jetro_trade" in source_ids
