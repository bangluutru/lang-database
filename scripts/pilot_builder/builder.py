#!/usr/bin/env python3
"""
scripts/pilot_builder/builder.py
Master builder for Phase 1 Pilot Dataset (800 entries total: 200 Accounting, 200 Tax, 200 Business, 200 Trade).
Implements complete schema validation, reading verification, Hepburn romaji generation,
PRO difficulty classification, priority scoring, collocations, natural workplace examples,
dialogues, source provenance tracking, and relationships graph.
"""

import os
import sys
import json
import time
from pathlib import Path
import pykakasi

BASE_DIR = Path(__file__).resolve().parent.parent.parent
PROD_DIR = BASE_DIR / "data" / "production"
PROD_DIR.mkdir(parents=True, exist_ok=True)

kks = pykakasi.kakasi()

def get_reading_and_romaji(surface: str, override_reading: str = None) -> tuple:
    if override_reading:
        hira = override_reading
        conv = kks.convert(override_reading)
        romaji = "".join(c["hepburn"] for c in conv)
        return hira, romaji
    conv = kks.convert(surface)
    hira = "".join(c["hira"] for c in conv)
    romaji = "".join(c["hepburn"] for c in conv)
    return hira, romaji

# Let's import domain banks or load them
print("[*] Initializing Domain Terminology Banks ...")
