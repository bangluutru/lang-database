"""
scripts/phase1_3a/pool_builder.py
Phase 1.3A Candidate Pool Builder and Manifest Generator.
Saves the versioned candidate pool and manifest per Section 35:
- staging/candidate_pool_phase_1_3a.jsonl
- staging/candidate_pool_phase_1_3a_manifest.json
"""

from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime, timezone
import hashlib
import json

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
        generation_commit: str = "b0bbd2aa41d0f61036a8f8935f5003594623c6e0"
    ) -> Dict[str, Any]:
        """
        Saves candidate_pool_phase_1_3a.jsonl and its companion manifest.
        """
        pool_file = self.staging_dir / "candidate_pool_phase_1_3a.jsonl"
        manifest_file = self.staging_dir / "candidate_pool_phase_1_3a_manifest.json"

        # Write candidates
        with open(pool_file, "w", encoding="utf-8") as f:
            for cand in surviving_candidates:
                f.write(json.dumps(cand.to_dict(), ensure_ascii=False) + "\n")

        pool_sha256 = compute_file_sha256(pool_file)
        now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        # Distribution aggregations
        domain_dist: Dict[str, int] = {}
        source_dist: Dict[str, int] = {}
        for c in surviving_candidates:
            domain_dist[c.domain] = domain_dist.get(c.domain, 0) + 1
            for s in c.source_ids:
                source_dist[s] = source_dist.get(s, 0) + 1

        manifest_data = {
            "pool_version": "1.3.0",
            "parent_phase": "Phase 1.2C",
            "candidate_count": len(surviving_candidates),
            "raw_candidate_count": raw_count,
            "source_registry_version": "1.3.0",
            "extractor_versions": {
                "MasterPhase13Extractor": "1.3.0",
                "FsaEdinetPhase13Extractor": "1.3.0",
                "GenericJsonCatalogExtractor": "1.3.0",
                "NtaPhase13Extractor": "1.3.0",
                "JicpaPhase13Extractor": "1.3.0"
            },
            "generation_commit": generation_commit,
            "generated_at": now_iso,
            "file_path": str(pool_file.relative_to(self.base_dir)),
            "sha256": pool_sha256,
            "source_distribution": source_dist,
            "domain_distribution": domain_dist
        }

        with open(manifest_file, "w", encoding="utf-8") as f:
            json.dump(manifest_data, f, indent=2, ensure_ascii=False)

        return manifest_data
