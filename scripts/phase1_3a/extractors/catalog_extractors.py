"""
scripts/phase1_3a/extractors/catalog_extractors.py
Extractors for Phase 1.3A & 1.3A.1 authoritative statutory and procedural source families:
- NTA (TaxAnswer HTML & statutory corporate tax curated)
- MHLW (Labor Standards, Employment Insurance) & Nenkin (Pension, Social Insurance curated)
- Japan Customs, NACCS, and JETRO (Trade, Customs, Tariff, Logistics)
- JFTC & SMEA (Subcontract Act, Procurement, SCM)
- e-Gov, MOJ, and JPO (Companies Act, Commercial Registration, Contracts, IP)
- SMRJ & METI (Business Operations, Management, Sales, Office Communication)
- ASBJ & JICPA (Accounting Standards, Auditing, Internal Control)
"""

from pathlib import Path
from typing import List, Dict, Any, Optional
import json
import re
from datetime import datetime, timezone
from bs4 import BeautifulSoup

from scripts.phase1_3a.extractors.base import BasePhase13Extractor
from scripts.phase1_3a.models import RawCandidate, ProvenanceType
from scripts.source_engine.extractors.nta import CORE_NTA_TERMS


class GenericJsonCatalogExtractor(BasePhase13Extractor):
    """Generic extractor for JSON catalog datasets (both genuine raw snapshots and curated references)."""
    def __init__(self, filename: Optional[str] = None, root_key: str = "terms", default_domain: str = "business", **kwargs):
        super().__init__(**kwargs)
        self.filename = filename
        self.root_key = root_key
        self.default_domain = default_domain

    def extract_candidates(self) -> List[RawCandidate]:
        candidates = []
        now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        # Determine target file and provenance semantics
        if self.curated_artifact_path and self.curated_artifact_path.exists():
            target_file = self.curated_artifact_path
            is_curated = True
            curated_at = "2026-10-01T08:00:00Z"
            extracted_at = ""
            artifact_rel_path = str(self.curated_artifact_path)
            raw_hash = ""
            curated_hash = self.curated_artifact_hash
            source_url = None
            ref_url = self.reference_url
            prov_type = self.provenance_type or ProvenanceType.OFFICIAL_CURATED.value
        elif self.raw_snapshot_path and self.filename:
            target_file = self.raw_snapshot_path / self.filename
            if not target_file.exists():
                return []
            is_curated = False
            curated_at = None
            extracted_at = now_iso
            artifact_rel_path = str(target_file)
            raw_hash = self.raw_snapshot_hash
            curated_hash = ""
            source_url = self.official_url
            ref_url = None
            prov_type = self.provenance_type or ProvenanceType.OFFICIAL_EXTRACTED.value
        else:
            return []

        with open(target_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        items = data.get(self.root_key, [])
        if not items and "curated_terms" in data:
            items = data.get("curated_terms", [])
        if isinstance(items, dict):
            items = list(items.values())

        for idx, item in enumerate(items, start=1):
            term = item.get("term") or item.get("name") or item.get("short") or ""
            if not term or len(term) < 2:
                continue

            en = item.get("en", "")
            domain = item.get("domain", self.default_domain)
            subdomain = item.get("subdomain") or item.get("category", "general")
            statute = item.get("statute") or item.get("law") or item.get("article", "")
            code = item.get("code") or f"{self.source_id}_{idx:04d}"

            if is_curated:
                context = f"Official curated reference: {self.source_id}. Statute: {statute}. Reference URL: {ref_url}"
            else:
                context = f"Official extracted source: {self.source_id}. Statute: {statute}."
            if en:
                context += f" Official EN: {en}"

            candidates.append(RawCandidate(
                candidate_id=f"cand-{self.source_id}-{idx:06d}",
                source_id=self.source_id,
                source_version=self.source_version,
                source_record_id=str(code),
                source_locator=f"file:{target_file.name}, item:{idx}, statute:{statute}",
                source_term_exact=term,
                source_context=context,
                source_definition=item.get("definition"),
                extracted_at=extracted_at,
                curated_at=curated_at,
                extractor_version=self.extractor_version,
                provenance_type=prov_type,
                raw_snapshot_hash=raw_hash,
                curated_artifact_hash=curated_hash,
                artifact_path=artifact_rel_path,
                source_url=source_url,
                reference_url=ref_url,
                primary_domain=domain,
                subdomain=subdomain,
                authority_class=self.authority_class,
                reuse_status=self.reuse_status
            ))

        # Check for companion HTML files ONLY for genuine raw snapshots
        if not is_curated and self.raw_snapshot_path and self.raw_snapshot_path.exists():
            for html_file in self.raw_snapshot_path.glob("*.html"):
                try:
                    content = html_file.read_text(encoding="utf-8")
                except UnicodeDecodeError:
                    content = html_file.read_text(encoding="cp932", errors="replace")

                soup = BeautifulSoup(content, "html.parser")
                existing_terms = {c.source_term_exact for c in candidates}

                for r_idx, li in enumerate(soup.find_all("li"), start=1):
                    a_tag = li.find("a")
                    text = a_tag.get_text().strip() if a_tag else li.get_text().strip()
                    m = re.match(r"^([^\(（]+)[\(（]([^\)）]+)[\)）]", text)
                    if m:
                        term = m.group(1).strip()
                        en = m.group(2).strip()
                    else:
                        parts = re.split(r"[\s:：＝=]", text)
                        term = parts[0].strip() if parts else ""
                        en = ""

                    if not term or len(term) < 2 or len(term) > 40:
                        continue
                    if term in ("目次", "ページトップ", "トップ", "はじめに", "用語一覧", "法令一覧", "ガイドライン"):
                        continue
                    if term in existing_terms:
                        continue
                    existing_terms.add(term)

                    ctx = f"Official statutory/procedural HTML: {html_file.name}. Raw: {li.get_text()[:100]}"
                    if en:
                        ctx += f" Official EN: {en}"

                    candidates.append(RawCandidate(
                        candidate_id=f"cand-{self.source_id}-html-{len(candidates)+1:06d}",
                        source_id=self.source_id,
                        source_version=self.source_version,
                        source_record_id=f"html_li_{r_idx}",
                        source_locator=f"file:{html_file.name}, li:{r_idx}",
                        source_term_exact=term,
                        source_context=ctx,
                        source_definition=None,
                        extracted_at=now_iso,
                        curated_at=None,
                        extractor_version=self.extractor_version,
                        provenance_type=ProvenanceType.OFFICIAL_EXTRACTED.value,
                        raw_snapshot_hash=self.raw_snapshot_hash,
                        curated_artifact_hash="",
                        artifact_path=str(html_file),
                        source_url=self.official_url,
                        reference_url=None,
                        primary_domain=self.default_domain,
                        subdomain="statutory_procedural",
                        authority_class=self.authority_class,
                        reuse_status=self.reuse_status
                    ))

        return candidates


class NtaPhase13Extractor(BasePhase13Extractor):
    """Extracts from NTA TaxAnswer HTML glossaries, code indexes, and statutory catalog."""
    def extract_candidates(self) -> List[RawCandidate]:
        candidates = []
        now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        seen = set()

        # 1. CORE_NTA_TERMS
        for idx, (term, code, law, subdom) in enumerate(CORE_NTA_TERMS, start=1):
            if term in seen:
                continue
            seen.add(term)
            candidates.append(RawCandidate(
                candidate_id=f"cand-nta-core-{idx:04d}",
                source_id=self.source_id,
                source_version=self.source_version,
                source_record_id=code,
                source_locator=f"statutory_core:{law}",
                source_term_exact=term,
                source_context=f"NTA TaxAnswer core statutory term. Law reference: {law}.",
                extracted_at=now_iso,
                curated_at=None,
                extractor_version=self.extractor_version,
                provenance_type=ProvenanceType.OFFICIAL_EXTRACTED.value,
                raw_snapshot_hash=self.raw_snapshot_hash,
                curated_artifact_hash="",
                artifact_path=str(self.raw_snapshot_path) if self.raw_snapshot_path else "",
                source_url=self.official_url,
                reference_url=None,
                primary_domain="tax",
                subdomain=subdom,
                authority_class=self.authority_class,
                reuse_status=self.reuse_status
            ))

        # 2. HTML Glossary parsing
        html_files = [
            ("nta_ryaku_yogo.html", "statutory_abbreviations"),
            ("nta_senmon_yogo.html", "specialist_terms"),
            ("nta_code_index.html", "code_index")
        ]
        for fname, cat in html_files:
            p = self.raw_snapshot_path / fname if self.raw_snapshot_path else None
            if not p or not p.exists():
                continue
            try:
                content = p.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                content = p.read_text(encoding="cp932", errors="replace")

            soup = BeautifulSoup(content, "html.parser")
            for r_idx, row in enumerate(soup.find_all(["tr", "li", "dt"]), start=1):
                text = row.get_text().strip()
                parts = re.split(r"[\s:：＝=（\(]", text)
                term = parts[0].strip() if parts else ""
                if term in ("目次", "ページトップ", "トップ", "はじめに", "用語一覧", "税目", "略称", "正式名称") or len(term) < 2 or len(term) > 35:
                    continue
                if term in seen:
                    continue
                seen.add(term)

                candidates.append(RawCandidate(
                    candidate_id=f"cand-nta-html-{len(candidates)+1:06d}",
                    source_id=self.source_id,
                    source_version=self.source_version,
                    source_record_id=f"{cat}_{r_idx}",
                    source_locator=f"file:{fname}, row:{r_idx}",
                    source_term_exact=term,
                    source_context=f"NTA TaxAnswer glossary item. Raw text: {text[:80]}",
                    extracted_at=now_iso,
                    curated_at=None,
                    extractor_version=self.extractor_version,
                    provenance_type=ProvenanceType.OFFICIAL_EXTRACTED.value,
                    raw_snapshot_hash=self.raw_snapshot_hash,
                    curated_artifact_hash="",
                    artifact_path=str(p),
                    source_url=self.official_url,
                    reference_url=None,
                    primary_domain="tax",
                    subdomain="tax_filing",
                    authority_class=self.authority_class,
                    reuse_status=self.reuse_status
                ))

        return candidates


class JicpaPhase13Extractor(BasePhase13Extractor):
    """Extracts accounting and auditing keywords from JICPA keyword index HTML."""
    def extract_candidates(self) -> List[RawCandidate]:
        if not self.raw_snapshot_path:
            return []
        html_path = self.raw_snapshot_path / "jicpa_keyword_index.html"
        if not html_path.exists():
            return []

        content = html_path.read_text(encoding="utf-8", errors="replace")
        soup = BeautifulSoup(content, "html.parser")
        candidates = []
        now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        seen = set()

        for idx, tag in enumerate(soup.find_all(["dt", "a", "li", "h3", "h4"]), start=1):
            term = tag.get_text().strip()
            term = re.sub(r"^[0-9\.\s・\-]+", "", term).strip()
            if not term or len(term) < 2 or len(term) > 30:
                continue
            if term in ("目次", "キーワード", "五十音順", "トップ", "ホーム", "用語集", "用語一覧"):
                continue
            if term in seen:
                continue
            seen.add(term)

            candidates.append(RawCandidate(
                candidate_id=f"cand-jicpa-{len(candidates)+1:06d}",
                source_id=self.source_id,
                source_version=self.source_version,
                source_record_id=f"jicpa_{idx}",
                source_locator=f"file:jicpa_keyword_index.html, tag:{tag.name}, idx:{idx}",
                source_term_exact=term,
                source_context="JICPA Accounting & Auditing Keyword Index.",
                extracted_at=now_iso,
                curated_at=None,
                extractor_version=self.extractor_version,
                provenance_type=ProvenanceType.OFFICIAL_EXTRACTED.value,
                raw_snapshot_hash=self.raw_snapshot_hash,
                curated_artifact_hash="",
                artifact_path=str(html_path),
                source_url=self.official_url,
                reference_url=None,
                primary_domain="accounting",
                subdomain="audit",
                authority_class=self.authority_class,
                reuse_status=self.reuse_status
            ))

        return candidates
