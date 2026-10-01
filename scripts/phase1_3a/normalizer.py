"""
scripts/phase1_3a/normalizer.py
Phase 1.3A Linguistic Normalizer and Surface Sanitizer.
Implements Unicode NFKC normalization, full/half-width conversions, whitespace sanitation,
Japanese bracket standardization, artifact detection, and original surface preservation.
"""

from typing import Tuple, List, Set
import unicodedata
import re

from scripts.phase1_3a.models import RawCandidate, NormalizedCandidate, QualityFlag


# Known navigation and documentation structure artifacts (Section 13)
KNOWN_ARTIFACTS: Set[str] = {
    "用語一覧", "用語集", "用語", "目次", "ページトップ", "トップ", "はじめに",
    "索引", "五十音順", "ガイドライン", "マニュアル", "目録", "一覧", "メニュー",
    "更新情報", "検索", "詳細", "ヘルプ", "サイトマップ", "リンク集", "関連リンク",
    "標準ラベル", "冗長ラベル", "要素名", "科目分類", "勘定科目リストについて",
    "タクソノミ要素リストについて", "略称", "正式名称", "税目", "コード", "番号"
}


def is_extraction_artifact(text: str) -> bool:
    """Detects whether a surface string is a navigational or structural artifact."""
    clean = text.strip()
    if clean in KNOWN_ARTIFACTS:
        return True
    if re.match(r"^(第[0-9一二三四五六七八九十百千万]+[条項号]|別表[0-9一二三四五六七八九十]*|様式第[0-9]+号)$", clean):
        return True
    if re.match(r"^[0-9\.\s・\-]+$", clean):
        return True
    # Obvious page section labels
    if clean.endswith("一覧") and len(clean) <= 6:
        return True
    return False


def normalize_surface(surface: str) -> Tuple[str, List[QualityFlag]]:
    """
    Normalizes a surface string per Section 15:
    - Unicode NFKC normalization
    - Strip duplicated spaces, leading bullets, trailing punctuation
    - Normalize Japanese brackets
    - Flag artifacts or suspicious patterns
    """
    flags: List[QualityFlag] = []
    if not surface:
        return ("", [QualityFlag.CANONICAL_VALUE_SUSPICIOUS])

    # 1. Unicode NFKC
    norm = unicodedata.normalize("NFKC", surface).strip()

    # 2. Strip leading bullets, numbering, or list markers
    norm = re.sub(r"^[\s・•\-\*▪▫◆◇■□●○]+", "", norm).strip()
    norm = re.sub(r"^[0-9]+[\.\)）]\s*", "", norm).strip()

    # 3. Normalize brackets: replace non-standard brackets with standard half/full-width
    # Strip outermost enclosing brackets e.g. 【用語】 -> 用語
    m_bracket = re.match(r"^[【〔［\[\(（](.*?)[】〕］\]\)）]$", norm)
    if m_bracket:
        inner = m_bracket.group(1).strip()
        if inner:
            norm = inner

    # 4. Strip duplicate spaces
    norm = re.sub(r"\s+", " ", norm).strip()

    # 5. Strip trailing colons or punctuation
    norm = re.sub(r"[:：、,。\.]$", "", norm).strip()

    # Check for artifacts
    if is_extraction_artifact(norm):
        flags.append(QualityFlag.ARTIFACT_FLAG)

    # Check for short or extremely long surfaces
    if len(norm) < 2:
        flags.append(QualityFlag.CANONICAL_VALUE_REVIEW_REQUIRED)
    elif len(norm) > 40:
        flags.append(QualityFlag.CANONICAL_VALUE_REVIEW_REQUIRED)

    return (norm, flags)


class Phase13Normalizer:
    """Normalizes raw candidates into NormalizedCandidate instances."""

    def normalize(self, raw: RawCandidate) -> NormalizedCandidate:
        norm_surface, flags = normalize_surface(raw.source_term_exact)

        # Check if raw candidate was tagged as XBRL composite
        is_composite_xbrl = False
        if raw.source_context and "[XBRL_CLASSIFICATION:COMPOSITE_REPORTING_LABEL]" in raw.source_context:
            is_composite_xbrl = True
            flags.append(QualityFlag.TAXONOMY_VARIANT_FLAG)
            flags.append(QualityFlag.CANONICAL_VALUE_REVIEW_REQUIRED)
        elif raw.source_context and "[XBRL_CLASSIFICATION:TAXONOMY_VARIANT]" in raw.source_context:
            flags.append(QualityFlag.TAXONOMY_VARIANT_FLAG)

        # Detect composite coordinate patterns in surface (Section 14)
        if not is_composite_xbrl:
            if ("及び" in norm_surface or "、" in norm_surface or "又は" in norm_surface) and len(norm_surface) > 7:
                # Unless it's a statutory act title (e.g. 労働安全衛生法及び関連政省令)
                if not norm_surface.endswith("法") and not norm_surface.endswith("規則"):
                    flags.append(QualityFlag.TAXONOMY_VARIANT_FLAG)
                    flags.append(QualityFlag.CANONICAL_VALUE_REVIEW_REQUIRED)
                    is_composite_xbrl = True
            elif norm_surface.endswith("(純額)") or norm_surface.endswith("（純額）"):
                flags.append(QualityFlag.TAXONOMY_VARIANT_FLAG)
                flags.append(QualityFlag.CANONICAL_VALUE_REVIEW_REQUIRED)
                is_composite_xbrl = True

        return NormalizedCandidate(
            candidate_id=raw.candidate_id,
            surface=raw.source_term_exact,
            normalized_surface=norm_surface,
            domain=raw.primary_domain,
            subdomain=raw.subdomain,
            source_ids=[raw.source_id],
            source_authorities=[raw.authority_class],
            source_locators=[raw.source_locator],
            source_contexts=[raw.source_context] if raw.source_context else [],
            source_definitions=[raw.source_definition] if raw.source_definition else [],
            quality_flags=flags,
            is_composite_taxonomy=is_composite_xbrl,
            extracted_at=raw.extracted_at,
            extractor_version=raw.extractor_version,
            raw_snapshot_hash=raw.raw_snapshot_hash
        )

    def normalize_batch(self, raw_candidates: List[RawCandidate]) -> List[NormalizedCandidate]:
        return [self.normalize(c) for c in raw_candidates]
