"""
scripts/phase1_3a/extractors/master_extractor.py
Phase 1.3A Master Extraction Orchestrator.
Loads config/source_registry.yaml and extracts raw candidate terminology across all registered
authoritative primary sources, enforcing source provenance, locators, and snapshot hashes.
"""

from typing import List, Dict, Any
from pathlib import Path
import yaml

from scripts.phase1_3a.models import RawCandidate
from scripts.phase1_3a.extractors.edinet_extractor import FsaEdinetPhase13Extractor
from scripts.phase1_3a.extractors.catalog_extractors import (
    GenericJsonCatalogExtractor,
    NtaPhase13Extractor,
    JicpaPhase13Extractor
)

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent


class MasterPhase13Extractor:
    def __init__(self, registry_path: Path):
        self.registry_path = registry_path
        with open(registry_path, "r", encoding="utf-8") as f:
            self.registry = yaml.safe_load(f)
        self.sources = {s["source_id"]: s for s in self.registry.get("sources", [])}

    def extract_all(self) -> List[RawCandidate]:
        all_candidates: List[RawCandidate] = []

        # Mapping of source_id to extractor instance builder
        extractor_factories = {
            "fsa-edinet-taxonomy": lambda s: FsaEdinetPhase13Extractor(
                source_id=s["source_id"],
                source_version=s["version"],
                raw_snapshot_path=BASE_DIR / s["raw_snapshot_path"],
                raw_snapshot_hash=s["raw_sha256"],
                authority_class=s["authority_class"],
                reuse_status=s["reuse_status"]
            ),
            "nta-tax-glossary": lambda s: NtaPhase13Extractor(
                source_id=s["source_id"],
                source_version=s["version"],
                raw_snapshot_path=BASE_DIR / s["raw_snapshot_path"],
                raw_snapshot_hash=s["raw_sha256"],
                authority_class=s["authority_class"],
                reuse_status=s["reuse_status"]
            ),
            "nta-corporate-tax": lambda s: GenericJsonCatalogExtractor(
                filename="nta_corporate_consumption_tax_terms.json",
                root_key="tax_terms",
                default_domain="tax",
                source_id=s["source_id"],
                source_version=s["version"],
                raw_snapshot_path=BASE_DIR / s["raw_snapshot_path"],
                raw_snapshot_hash=s["raw_sha256"],
                authority_class=s["authority_class"],
                reuse_status=s["reuse_status"]
            ),
            "mhlw-labor": lambda s: GenericJsonCatalogExtractor(
                filename="mhlw_employment_insurance_regulations.json",
                root_key="labor_terms",
                default_domain="hr",
                source_id=s["source_id"],
                source_version=s["version"],
                raw_snapshot_path=BASE_DIR / s["raw_snapshot_path"],
                raw_snapshot_hash=s["raw_sha256"],
                authority_class=s["authority_class"],
                reuse_status=s["reuse_status"]
            ),
            "nenkin-social-insurance": lambda s: GenericJsonCatalogExtractor(
                filename="nenkin_social_insurance_terms.json",
                root_key="terms",
                default_domain="hr",
                source_id=s["source_id"],
                source_version=s["version"],
                raw_snapshot_path=BASE_DIR / s["raw_snapshot_path"],
                raw_snapshot_hash=s["raw_sha256"],
                authority_class=s["authority_class"],
                reuse_status=s["reuse_status"]
            ),
            "japan-customs-trade": lambda s: GenericJsonCatalogExtractor(
                filename="customs_tariff_procedures.json",
                root_key="procedures",
                default_domain="trade",
                source_id=s["source_id"],
                source_version=s["version"],
                raw_snapshot_path=BASE_DIR / s["raw_snapshot_path"],
                raw_snapshot_hash=s["raw_sha256"],
                authority_class=s["authority_class"],
                reuse_status=s["reuse_status"]
            ),
            "naccs-trade": lambda s: GenericJsonCatalogExtractor(
                filename="naccs_trade_customs_procedures.json",
                root_key="procedures",
                default_domain="trade",
                source_id=s["source_id"],
                source_version=s["version"],
                raw_snapshot_path=BASE_DIR / s["raw_snapshot_path"],
                raw_snapshot_hash=s["raw_sha256"],
                authority_class=s["authority_class"],
                reuse_status=s["reuse_status"]
            ),
            "jetro-trade": lambda s: GenericJsonCatalogExtractor(
                filename="jetro_incoterms_reference.json",
                root_key="trade_terms",
                default_domain="trade",
                source_id=s["source_id"],
                source_version=s["version"],
                raw_snapshot_path=BASE_DIR / s["raw_snapshot_path"],
                raw_snapshot_hash=s["raw_sha256"],
                authority_class=s["authority_class"],
                reuse_status=s["reuse_status"]
            ),
            "jftc-subcontract": lambda s: GenericJsonCatalogExtractor(
                filename="jftc_subcontract_act_terms.json",
                root_key="guidance",
                default_domain="purchasing",
                source_id=s["source_id"],
                source_version=s["version"],
                raw_snapshot_path=BASE_DIR / s["raw_snapshot_path"],
                raw_snapshot_hash=s["raw_sha256"],
                authority_class=s["authority_class"],
                reuse_status=s["reuse_status"]
            ),
            "smea-procurement": lambda s: GenericJsonCatalogExtractor(
                filename="smea_procurement_supplychain_terms.json",
                root_key="procurement_terms",
                default_domain="purchasing",
                source_id=s["source_id"],
                source_version=s["version"],
                raw_snapshot_path=BASE_DIR / s["raw_snapshot_path"],
                raw_snapshot_hash=s["raw_sha256"],
                authority_class=s["authority_class"],
                reuse_status=s["reuse_status"]
            ),
            "egov-corporate-law": lambda s: GenericJsonCatalogExtractor(
                filename="egov_commercial_code_statutory.json",
                root_key="statutory_terms",
                default_domain="legal",
                source_id=s["source_id"],
                source_version=s["version"],
                raw_snapshot_path=BASE_DIR / s["raw_snapshot_path"],
                raw_snapshot_hash=s["raw_sha256"],
                authority_class=s["authority_class"],
                reuse_status=s["reuse_status"]
            ),
            "moj-commercial-registration": lambda s: GenericJsonCatalogExtractor(
                filename="moj_commercial_registration_terms.json",
                root_key="statutory_terms",
                default_domain="legal",
                source_id=s["source_id"],
                source_version=s["version"],
                raw_snapshot_path=BASE_DIR / s["raw_snapshot_path"],
                raw_snapshot_hash=s["raw_sha256"],
                authority_class=s["authority_class"],
                reuse_status=s["reuse_status"]
            ),
            "jpo-intellectual-property": lambda s: GenericJsonCatalogExtractor(
                filename="jpo_intellectual_property_terms.json",
                root_key="ip_terms",
                default_domain="legal",
                source_id=s["source_id"],
                source_version=s["version"],
                raw_snapshot_path=BASE_DIR / s["raw_snapshot_path"],
                raw_snapshot_hash=s["raw_sha256"],
                authority_class=s["authority_class"],
                reuse_status=s["reuse_status"]
            ),
            "smrj-business-guidance": lambda s: GenericJsonCatalogExtractor(
                filename="smrj_business_operations_catalog.json",
                root_key="guidance_terms",
                default_domain="business",
                source_id=s["source_id"],
                source_version=s["version"],
                raw_snapshot_path=BASE_DIR / s["raw_snapshot_path"],
                raw_snapshot_hash=s["raw_sha256"],
                authority_class=s["authority_class"],
                reuse_status=s["reuse_status"]
            ),
            "meti-commerce-operations": lambda s: GenericJsonCatalogExtractor(
                filename="meti_commerce_transactions_terms.json",
                root_key="commerce_terms",
                default_domain="business",
                source_id=s["source_id"],
                source_version=s["version"],
                raw_snapshot_path=BASE_DIR / s["raw_snapshot_path"],
                raw_snapshot_hash=s["raw_sha256"],
                authority_class=s["authority_class"],
                reuse_status=s["reuse_status"]
            ),
            "asbj-accounting-standards": lambda s: GenericJsonCatalogExtractor(
                filename="asbj_accounting_standards_catalog.json",
                root_key="standards",
                default_domain="accounting",
                source_id=s["source_id"],
                source_version=s["version"],
                raw_snapshot_path=BASE_DIR / s["raw_snapshot_path"],
                raw_snapshot_hash=s["raw_sha256"],
                authority_class=s["authority_class"],
                reuse_status=s["reuse_status"]
            ),
            "jicpa-glossary": lambda s: JicpaPhase13Extractor(
                source_id=s["source_id"],
                source_version=s["version"],
                raw_snapshot_path=BASE_DIR / s["raw_snapshot_path"],
                raw_snapshot_hash=s["raw_sha256"],
                authority_class=s["authority_class"],
                reuse_status=s["reuse_status"]
            )
        }

        print("[*] Running Phase 1.3A Master Extraction across registered authoritative sources...")
        for source_id, factory in extractor_factories.items():
            if source_id not in self.sources:
                print(f"[!] Warning: {source_id} not found in registry, skipping.")
                continue
            s_meta = self.sources[source_id]
            # Draft sources guard (Section 8 & Phase 1.2B invariant)
            if s_meta.get("status") == "staging_only":
                print(f"[*] Skipping staging_only source: {source_id}")
                continue

            extractor = factory(s_meta)
            candidates = extractor.extract_candidates()
            print(f"  [+] {source_id} (Authority {s_meta['authority_class']}): extracted {len(candidates)} raw candidates")
            all_candidates.extend(candidates)

        print(f"[*] Master Extraction completed: {len(all_candidates)} total raw candidates.")
        return all_candidates
