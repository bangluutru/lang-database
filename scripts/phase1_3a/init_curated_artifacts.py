"""
scripts/phase1_3a/init_curated_artifacts.py
Initializes curated statutory catalogs and metadata under data/curated/phase1_3a/.
Separates genuine retrieved raw snapshots from internally curated domain catalogs.

Sources curated with official references:
- nenkin-social-insurance (Japan Pension Service reference)
- naccs-trade (NACCS trade/customs reference)
- jftc-subcontract (Fair Trade Commission Subcontract Act reference)
- smea-procurement (Small and Medium Enterprise Agency supply chain reference)
- moj-commercial-registration (Ministry of Justice commercial registration reference)
- jpo-intellectual-property (Japan Patent Office IP reference)
- meti-commerce-operations (METI commerce & sales reference)
- nta-corporate-tax (National Tax Agency statutory corporate tax reference)
"""

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import json
import hashlib
import shutil

from scripts.phase1_3a.catalogs.tax_catalog import TAX_TERMS
from scripts.phase1_3a.catalogs.hr_catalog import HR_TERMS
from scripts.phase1_3a.catalogs.trade_catalog import TRADE_TERMS
from scripts.phase1_3a.catalogs.purchasing_catalog import PURCHASING_TERMS
from scripts.phase1_3a.catalogs.legal_catalog import LEGAL_TERMS
from scripts.phase1_3a.catalogs.business_catalog import BUSINESS_TERMS


def compute_sha256(filepath: Path) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def init_curated_artifacts() -> dict:
    target_dir = BASE_DIR / "data" / "curated" / "phase1_3a"
    target_dir.mkdir(parents=True, exist_ok=True)

    jftc_terms = [t for t in PURCHASING_TERMS if "下請法" in t.get("statute", "") or "独占禁止" in t.get("statute", "") or t.get("subdomain") in ("supplier_management", "inspection", "pricing")]
    moj_terms = [t for t in LEGAL_TERMS if t.get("subdomain") != "intellectual_property"]
    jpo_terms = [t for t in LEGAL_TERMS if t.get("subdomain") == "intellectual_property"]

    catalogs_spec = {
        "nenkin-social-insurance": {
            "filename": "nenkin_social_insurance_curated.json",
            "content": {"source": "日本年金機構 (Reference)", "curated_terms": HR_TERMS},
            "reference_url": "https://www.nenkin.go.jp/service/kounen/jigyosho-hiho/hihokensha1/index.html",
            "curation_method": "Internally curated domain catalog structured from official Japan Pension Service guidance and statutory forms",
            "authority_class": "A"
        },
        "naccs-trade": {
            "filename": "naccs_trade_curated.json",
            "content": {"source": "輸出入・港湾関連情報処理センター (Reference)", "curated_terms": TRADE_TERMS},
            "reference_url": "https://bbs.naccs.jp/naccs/dfw/bbs/doc/",
            "curation_method": "Internally curated catalog referencing NACCS EDI specifications and customs procedures",
            "authority_class": "A"
        },
        "jftc-subcontract": {
            "filename": "jftc_subcontract_curated.json",
            "content": {"source": "公正取引委員会 (Reference)", "curated_terms": jftc_terms},
            "reference_url": "https://www.jftc.go.jp/shitauke/",
            "curation_method": "Internally curated statutory catalog referencing Fair Trade Commission Subcontract Act guidelines",
            "authority_class": "A"
        },
        "smea-procurement": {
            "filename": "smea_procurement_curated.json",
            "content": {"source": "中小企業庁 (Reference)", "curated_terms": PURCHASING_TERMS},
            "reference_url": "https://www.chusho.meti.go.jp/keiei/torihiki/",
            "curation_method": "Internally curated catalog referencing Small and Medium Enterprise Agency fair supply chain guidelines",
            "authority_class": "A"
        },
        "moj-commercial-registration": {
            "filename": "moj_commercial_registration_curated.json",
            "content": {"source": "法務省民事局 (Reference)", "curated_terms": moj_terms},
            "reference_url": "https://www.moj.go.jp/MINJI/minji06.html",
            "curation_method": "Internally curated statutory catalog referencing Ministry of Justice Commercial Registration procedures",
            "authority_class": "A"
        },
        "jpo-intellectual-property": {
            "filename": "jpo_intellectual_property_curated.json",
            "content": {"source": "特許庁 (Reference)", "curated_terms": jpo_terms},
            "reference_url": "https://www.jpo.go.jp/",
            "curation_method": "Internally curated statutory catalog referencing Japan Patent Office industrial property guidance",
            "authority_class": "A"
        },
        "meti-commerce-operations": {
            "filename": "meti_commerce_curated.json",
            "content": {"source": "経済産業省 (Reference)", "curated_terms": BUSINESS_TERMS},
            "reference_url": "https://www.meti.go.jp/policy/economy/chizai/chiteki/",
            "curation_method": "Internally curated catalog referencing METI commercial guidelines and trade transaction standards",
            "authority_class": "A"
        },
        "nta-corporate-tax": {
            "filename": "nta_corporate_tax_curated.json",
            "content": {"source": "国税庁 (Reference)", "curated_terms": TAX_TERMS},
            "reference_url": "https://www.nta.go.jp/taxes/shiraberu/taxanswer/index2.htm",
            "curation_method": "Internally curated statutory catalog referencing National Tax Agency corporate tax directives",
            "authority_class": "A"
        }
    }

    curated_records = []
    hashes = {}

    for source_id, spec in catalogs_spec.items():
        file_path = target_dir / spec["filename"]
        file_path.write_text(json.dumps(spec["content"], indent=2, ensure_ascii=False), encoding="utf-8")
        file_hash = compute_sha256(file_path)
        file_size = file_path.stat().st_size
        hashes[source_id] = file_hash

        curated_records.append({
            "source_id": source_id,
            "filename": spec["filename"],
            "artifact_path": f"data/curated/phase1_3a/{spec['filename']}",
            "reference_url": spec["reference_url"],
            "curation_method": spec["curation_method"],
            "curated_at": "2026-10-01T08:00:00Z",
            "file_size_bytes": file_size,
            "sha256": file_hash,
            "content_type": "application/json",
            "provenance_type": "OFFICIAL_CURATED",
            "authority_class": spec["authority_class"],
            "status": "CURATED_WITH_OFFICIAL_REFERENCE"
        })

    metadata = {
        "directory": "data/curated/phase1_3a",
        "created_at": "2026-10-01T08:00:00Z",
        "provenance_schema_version": "1.3.1",
        "files_count": len(curated_records),
        "artifacts": curated_records
    }

    meta_path = target_dir / "metadata.json"
    meta_path.write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8")
    meta_hash = compute_sha256(meta_path)
    hashes["metadata"] = meta_hash
    print(f"[+] Initialized {len(curated_records)} curated artifacts in data/curated/phase1_3a (meta sha256={meta_hash[:12]}...)")

    return hashes


def cleanup_fake_raw_snapshots():
    """Removes internally curated directories that were incorrectly placed in data/raw/."""
    fake_raw_dirs = [
        BASE_DIR / "data" / "raw" / "nenkin",
        BASE_DIR / "data" / "raw" / "naccs",
        BASE_DIR / "data" / "raw" / "jftc",
        BASE_DIR / "data" / "raw" / "smea",
        BASE_DIR / "data" / "raw" / "moj",
        BASE_DIR / "data" / "raw" / "jpo",
        BASE_DIR / "data" / "raw" / "meti",
        BASE_DIR / "data" / "raw" / "nta" / "corporate-tax"
    ]
    for d in fake_raw_dirs:
        if d.exists():
            shutil.rmtree(d)
            print(f"[-] Removed fake raw directory: {d.relative_to(BASE_DIR)}")


if __name__ == "__main__":
    init_curated_artifacts()
    cleanup_fake_raw_snapshots()
