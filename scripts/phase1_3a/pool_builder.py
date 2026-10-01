"""
scripts/phase1_3a/pool_builder.py
Phase 1.3A.1 Candidate Pool Builder and Manifest Generator.
Saves the versioned candidate pool and hardened manifest per Sections 32 & 35:
- staging/candidate_pool_phase_1_3a.jsonl
- staging/candidate_pool_phase_1_3a_manifest.json
Preserves historical 1.3.0 manifest as staging/candidate_pool_phase_1_3a_v1.3.0_manifest.json.
"""

from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime, timezone
import hashlib
import json
import shutil

from scripts.phase1_3a.models import NormalizedCandidate


def compute_file_sha256(filepath: Path) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


class Phase13PoolBuilder:
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.staging_dir = self.base_dir / "staging"
        self.staging_dir.mkdir(parents=True, exist_ok=True)

    def build_and_save_pool(
        self,
        surviving_candidates: List[NormalizedCandidate],
        raw_count: int,
        parent_commit: str = "ba12af1f783eaad2ba18576406d1292f23876eaf"
    ) -> Dict[str, Any]:
        """
        Saves candidate_pool_phase_1_3a.jsonl and its version 1.3.1 manifest.
        """
        pool_file = self.staging_dir / "candidate_pool_phase_1_3a.jsonl"
        manifest_file = self.staging_dir / "candidate_pool_phase_1_3a_manifest.json"
        audit_130_manifest = self.staging_dir / "candidate_pool_phase_1_3a_v1.3.0_manifest.json"

        # Preserve historical 1.3.0 manifest if present
        if manifest_file.exists() and not audit_130_manifest.exists():
            shutil.copy2(manifest_file, audit_130_manifest)

        # Write candidates
        with open(pool_file, "w", encoding="utf-8") as f:
            for cand in surviving_candidates:
                f.write(json.dumps(cand.to_dict(), ensure_ascii=False) + "\n")

        pool_sha256 = compute_file_sha256(pool_file)
        now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        # Distribution aggregations
        domain_dist: Dict[str, int] = {}
        source_dist: Dict[str, int] = {}
        prov_dist: Dict[str, int] = {}
        for c in surviving_candidates:
            domain_dist[c.domain] = domain_dist.get(c.domain, 0) + 1
            prov_dist[c.term_provenance] = prov_dist.get(c.term_provenance, 0) + 1
            for s in c.source_ids:
                source_dist[s] = source_dist.get(s, 0) + 1

        manifest_data = {
            "pool_version": "1.3.1",
            "parent_pool_version": "1.3.0",
            "parent_pool_sha256": "736c4511557b68ab0242f17c9517dd74cc041378d936d9eacef9870294eb1407",
            "parent_phase": "Phase 1.3A",
            "parent_commit": parent_commit,
            "candidate_count": len(surviving_candidates),
            "raw_candidate_count": raw_count,
            "source_registry_version": "1.3.1",
            "provenance_schema_version": "1.3.1",
            "extractor_versions": {
                "MasterPhase13Extractor": "1.3.1",
                "FsaEdinetPhase13Extractor": "1.3.1",
                "GenericJsonCatalogExtractor": "1.3.1",
                "NtaPhase13Extractor": "1.3.1",
                "JicpaPhase13Extractor": "1.3.1"
            },
            "generated_at": now_iso,
            "file_path": str(pool_file.relative_to(self.base_dir)),
            "sha256": pool_sha256,
            "provenance_distribution": prov_dist,
            "source_distribution": source_dist,
            "domain_distribution": domain_dist
        }

        with open(manifest_file, "w", encoding="utf-8") as f:
            json.dump(manifest_data, f, indent=2, ensure_ascii=False)

        return manifest_data
