"""
scripts/phase1_3b/adapters/seed_adapters.py
Specialized source adapters for Phase 1.3B seed foundation:
- JMdictSeedAdapter (JA lexical entries)
- JoyoKanjiAdapter (Official Jōyō grade classifications)
- NGSLSeedAdapter (EN core lemmas & CEFR levels)
- VietnameseCoreAdapter (VI core expressions & Hán-Việt cognates)
"""

from pathlib import Path
from typing import Dict, List, Any, Optional
import json

from scripts.phase1_3b.adapters.base import BaseSourceAdapter
from scripts.phase1_3b.models import SourceEvidence, OriginType



BASE_DIR = Path(__file__).resolve().parents[3]
DEFAULT_CURATED_DIR = BASE_DIR / "data" / "curated" / "phase1_3b"



class JMdictSeedAdapter(BaseSourceAdapter):
    """Adapter for curated JMdict Japanese core lexical entries."""

    def __init__(self, artifact_path: Optional[Path] = None, expected_sha256: Optional[str] = None):
        target_path = artifact_path or (DEFAULT_CURATED_DIR / "jmdict_seed.json")
        super().__init__(
            source_id="jmdict-seed",
            source_version="2026-v1",
            raw_artifact_path=target_path,
            license_code="CC-BY-SA-4.0",
            license_locator="https://www.edrdg.org/edrdg/licence.html",
            source_url="https://www.edrdg.org/jmdict/j_jmdict.html",
            reference_url="https://www.edrdg.org/jmdict/j_jmdict.html",
            retrieved_at="2026-10-01T12:00:00Z",
            expected_sha256=expected_sha256,
            parser_version="1.3.1"
        )

    def extract(self) -> List[Dict[str, Any]]:
        return self.extract_records()


    def extract_records(self) -> List[Dict[str, Any]]:
        self.verify_integrity()
        with open(self.raw_artifact_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        records = []
        for i, item in enumerate(data):
            locator = f"item_seq:{item.get('ent_seq')}, index:{i}"
            evidence = self.build_source_evidence(locator, origin=OriginType.SEED_CURATED.value)
            keb = item.get("k_ele", [{}])[0].get("keb", "")
            reb = item.get("r_ele", [{}])[0].get("reb", "")
            senses = item.get("sense", [])
            
            records.append({
                "concept_id": item.get("ent_seq"),
                "language": "ja",
                "surface": keb,
                "reading": reb,
                "senses": senses,
                "source_evidence": [evidence.to_dict()],
                "locator": locator
            })
        self.records_extracted_count = len(records)
        return records


class JoyoKanjiAdapter(BaseSourceAdapter):
    """Adapter for official Agency for Cultural Affairs Jōyō Kanji table."""

    def __init__(self, artifact_path: Optional[Path] = None, expected_sha256: Optional[str] = None):
        target_path = artifact_path or (DEFAULT_CURATED_DIR / "joyo_kanji_seed.json")
        super().__init__(
            source_id="joyo-kanji-agency",
            source_version="2026-v1",
            raw_artifact_path=target_path,
            license_code="PDL-1.0",
            license_locator="https://www.bunka.go.jp/chosakuken/",
            source_url="https://www.bunka.go.jp/kokugo_nihongo/sisaku/joho/joho/kijun/naikaku/kanji/",
            reference_url="https://www.bunka.go.jp/kokugo_nihongo/sisaku/joho/joho/kijun/naikaku/kanji/",
            retrieved_at="2026-10-01T12:00:00Z",
            expected_sha256=expected_sha256,
            parser_version="1.3.1"
        )

    def extract(self) -> List[Dict[str, Any]]:
        return self.extract_records()

    def extract_records(self) -> List[Dict[str, Any]]:
        self.verify_integrity()
        with open(self.raw_artifact_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        records = []
        for i, item in enumerate(data):
            locator = f"kanji:{item.get('kanji')}, grade:{item.get('grade')}"
            evidence = self.build_source_evidence(locator, origin=OriginType.SEED_CURATED.value)
            records.append({
                "kanji": item.get("kanji"),
                "grade": item.get("grade"),
                "concept_id": item.get("concept_id"),
                "reading": item.get("reading"),
                "source_evidence": [evidence.to_dict()],
                "locator": locator
            })
        self.records_extracted_count = len(records)
        return records


class NGSLSeedAdapter(BaseSourceAdapter):
    """Adapter for New General Service List (NGSL v1.2) core English lemmas."""

    def __init__(self, artifact_path: Optional[Path] = None, expected_sha256: Optional[str] = None):
        target_path = artifact_path or (DEFAULT_CURATED_DIR / "ngsl_seed.json")
        super().__init__(
            source_id="ngsl-project",
            source_version="1.2",
            raw_artifact_path=target_path,
            license_code="CC-BY-SA-4.0",
            license_locator="http://www.newgeneralservicelist.org/terms-of-use",
            source_url="http://www.newgeneralservicelist.org/",
            reference_url="http://www.newgeneralservicelist.org/",
            retrieved_at="2026-10-01T12:00:00Z",
            expected_sha256=expected_sha256,
            parser_version="1.3.1"
        )

    def extract(self) -> List[Dict[str, Any]]:
        return self.extract_records()

    def extract_records(self) -> List[Dict[str, Any]]:
        self.verify_integrity()
        with open(self.raw_artifact_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        records = []
        for i, item in enumerate(data):
            locator = f"lemma:{item.get('lemma')}, rank:{item.get('ngsl_rank')}"
            evidence = self.build_source_evidence(locator, origin=OriginType.SEED_CURATED.value)
            records.append({
                "concept_id": item.get("concept_id"),
                "language": "en",
                "lemma": item.get("lemma"),
                "pronunciation": item.get("pronunciation"),
                "part_of_speech": item.get("part_of_speech"),
                "ngsl_rank": item.get("ngsl_rank"),
                "cefr_level": item.get("cefr_level"),
                "source_evidence": [evidence.to_dict()],
                "locator": locator
            })
        self.records_extracted_count = len(records)
        return records


class VietnameseCoreAdapter(BaseSourceAdapter):
    """Adapter for curated Vietnamese core vocabulary with verified Hán-Việt cognates."""

    def __init__(self, artifact_path: Optional[Path] = None, expected_sha256: Optional[str] = None):
        target_path = artifact_path or (DEFAULT_CURATED_DIR / "vietnamese_core_seed.json")
        super().__init__(
            source_id="viet-core-seed",
            source_version="2026-v1",
            raw_artifact_path=target_path,
            license_code="CC-BY-SA-4.0",
            license_locator="https://creativecommons.org/licenses/by-sa/4.0/",
            source_url="https://vi.wiktionary.org/",
            reference_url="https://vi.wiktionary.org/",
            retrieved_at="2026-10-01T12:00:00Z",
            expected_sha256=expected_sha256,
            parser_version="1.3.1"
        )

    def extract(self) -> List[Dict[str, Any]]:
        return self.extract_records()

    def extract_records(self) -> List[Dict[str, Any]]:
        self.verify_integrity()
        with open(self.raw_artifact_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        records = []
        for i, item in enumerate(data):
            locator = f"lemma:{item.get('lemma')}, index:{i}"
            evidence = self.build_source_evidence(locator, origin=OriginType.SEED_CURATED.value)
            records.append({
                "concept_id": item.get("concept_id"),
                "language": "vi",
                "lemma": item.get("lemma"),
                "pronunciation": item.get("pronunciation"),
                "sino_vietnamese": item.get("sino_vietnamese"),
                "part_of_speech": item.get("part_of_speech"),

                "source_evidence": [evidence.to_dict()],
                "locator": locator
            })
        self.records_extracted_count = len(records)
        return records

