"""
scripts/source_engine/extractors/nta.py
Extractor for National Tax Agency (NTA) TaxAnswer & statutory tax terms.
"""

from pathlib import Path
from typing import List
import re
from bs4 import BeautifulSoup
from datetime import datetime, timezone

from scripts.source_engine.extractors.base import BaseExtractor
from scripts.source_engine.models import ExtractedCandidate

CORE_NTA_TERMS = [
    ("国税", "national_tax", "国税通則法", "core_tax"),
    ("地方税", "local_tax", "地方税法", "core_tax"),
    ("直接税", "direct_tax", "税制基本", "core_tax"),
    ("間接税", "indirect_tax", "税制基本", "core_tax"),
    ("所得税", "income_tax", "所得税法", "income_tax"),
    ("法人税", "corporate_tax", "法人税法", "corporate_tax"),
    ("消費税", "consumption_tax", "消費税法", "consumption_tax"),
    ("住民税", "resident_tax", "地方税法", "local_tax"),
    ("確定申告", "tax_return", "タックスアンサー2020", "tax_filing"),
    ("青色申告", "blue_return", "タックスアンサー2070", "tax_filing"),
    ("白色申告", "white_return", "タックスアンサー2070", "tax_filing"),
    ("年末調整", "year_end_adjustment", "タックスアンサー2662", "withholding_tax"),
    ("源泉徴収", "withholding_tax", "タックスアンサー2500", "withholding_tax"),
    ("源泉所得税", "withholding_income_tax", "タックスアンサー2500", "withholding_tax"),
    ("課税所得", "taxable_income", "所得税法", "income_tax"),
    ("非課税所得", "non_taxable_income", "所得税法", "income_tax"),
    ("課税標準", "tax_base", "国税通則法", "corporate_tax"),
    ("税額控除", "tax_credit", "タックスアンサー1200", "deductions"),
    ("所得控除", "income_deduction", "タックスアンサー1100", "deductions"),
    ("基礎控除", "basic_deduction", "タックスアンサー1199", "deductions"),
    ("配偶者控除", "spouse_deduction", "タックスアンサー1191", "deductions"),
    ("扶養控除", "dependent_deduction", "タックスアンサー1180", "deductions"),
    ("医療費控除", "medical_deduction", "タックスアンサー1120", "deductions"),
    ("社会保険料控除", "social_insurance_deduction", "タックスアンサー1130", "deductions"),
    ("インボイス制度", "qualified_invoice", "適格請求書等保存方式", "consumption_tax"),
    ("適格請求書", "qualified_invoice_doc", "消費税法", "consumption_tax"),
    ("適格請求書発行事業者", "invoice_issuer", "消費税法", "consumption_tax"),
    ("電子帳簿保存法", "electronic_book_act", "電帳法", "tax_filing"),
    ("税務調査", "tax_audit", "国税通則法", "tax_audit"),
    ("税務署", "tax_office", "国税庁組織規則", "tax_filing"),
    ("給与所得", "employment_income", "タックスアンサー1400", "income_tax"),
    ("事業所得", "business_income", "タックスアンサー1350", "income_tax"),
    ("譲渡所得", "capital_gains", "タックスアンサー1440", "income_tax"),
    ("青色申告特別控除", "special_blue_deduction", "タックスアンサー2072", "deductions"),
    ("仕入税額控除", "input_tax_credit", "タックスアンサー6401", "consumption_tax"),
    ("簡易課税制度", "simplified_tax_system", "タックスアンサー6505", "consumption_tax"),
    ("中間申告", "interim_return", "タックスアンサー6609", "tax_filing"),
    ("予定納税", "prepayment_tax", "タックスアンサー2040", "tax_payment"),
    ("修正申告", "amended_return", "タックスアンサー2026", "tax_filing"),
    ("更正の請求", "correction_request", "タックスアンサー2026", "tax_filing"),
    ("還付申告", "refund_return", "タックスアンサー2030", "tax_filing"),
    ("延滞税", "delinquent_tax", "タックスアンサー9205", "tax_audit"),
    ("過少申告加算税", "understatement_penalty", "国税通則法", "tax_audit"),
    ("無申告加算税", "non_filing_penalty", "国税通則法", "tax_audit"),
    ("重加算税", "heavy_penalty_tax", "国税通則法", "tax_audit")
]


class NtaTaxExtractor(BaseExtractor):
    def extract_candidates(self) -> List[ExtractedCandidate]:
        candidates = []
        seen = set()
        now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        # 1. Core Statutory Terms
        for term, code, legal_ref, subdomain in CORE_NTA_TERMS:
            if term in seen:
                continue
            seen.add(term)
            seq = len(candidates) + 1
            candidates.append(ExtractedCandidate(
                candidate_id=f"cand-nta-{seq:06d}",
                source_id=self.source_id,
                source_version=self.source_version,
                source_record_id=f"statutory_{code}",
                source_locator=f"statute:{legal_ref}",
                source_term_exact=term,
                source_context=f"国税庁 法定税務用語。根拠法令: {legal_ref}",
                source_definition=None,
                extracted_at=now_iso,
                extractor_version=self.extractor_version,
                raw_snapshot_hash=self.raw_snapshot_hash,
                primary_domain="tax",
                subdomain=subdomain,
                authority_class=self.authority_class,
                reuse_status=self.reuse_status
            ))

        # 2. Extract from nta_senmon_yogo.html
        senmon_file = self.raw_snapshot_path / "nta_senmon_yogo.html"
        if senmon_file.exists():
            soup = BeautifulSoup(senmon_file.read_text(encoding="utf-8", errors="ignore"), "html.parser")
            for dt in soup.find_all("dt"):
                term = dt.get_text().strip()
                term = re.sub(r"\[.*?\]|\(.*?\)|（.*?）", "", term).strip()
                if not term or term in seen or len(term) < 2 or len(term) > 30:
                    continue
                seen.add(term)
                seq = len(candidates) + 1
                candidates.append(ExtractedCandidate(
                    candidate_id=f"cand-nta-{seq:06d}",
                    source_id=self.source_id,
                    source_version=self.source_version,
                    source_record_id=f"senmon_{seq}",
                    source_locator="file:nta_senmon_yogo.html, tag:<dt>",
                    source_term_exact=term,
                    source_context="国税庁 タックスアンサー 専門用語集掲載用語",
                    source_definition=None,
                    extracted_at=now_iso,
                    extractor_version=self.extractor_version,
                    raw_snapshot_hash=self.raw_snapshot_hash,
                    primary_domain="tax",
                    subdomain="tax_filing",
                    authority_class=self.authority_class,
                    reuse_status=self.reuse_status
                ))

        ryaku_file = self.raw_snapshot_path / "nta_ryaku_yogo.html"
        if ryaku_file.exists():
            raw_bytes = ryaku_file.read_bytes()
            try:
                html_text = raw_bytes.decode("cp932")
            except Exception:
                html_text = raw_bytes.decode("utf-8", errors="ignore")
            soup = BeautifulSoup(html_text, "html.parser")
            for td in soup.find_all("td"):
                text = td.get_text().strip()
                for line in text.split("\n"):
                    term = line.strip()
                    term = re.sub(r"\(.*?\)|（.*?）", "", term).strip()
                    if not term or term in seen or len(term) < 2 or len(term) > 30:
                        continue
                    if any(stop in term for stop in ["について", "とは", "の手続", "の計算"]):
                        continue
                    seen.add(term)
                    seq = len(candidates) + 1
                    candidates.append(ExtractedCandidate(
                        candidate_id=f"cand-nta-{seq:06d}",
                        source_id=self.source_id,
                        source_version=self.source_version,
                        source_record_id=f"ryaku_{seq}",
                        source_locator="file:nta_ryaku_yogo.html, tag:<td>",
                        source_term_exact=term,
                        source_context="国税庁 タックスアンサー 省略用語・法令名例",
                        source_definition=None,
                        extracted_at=now_iso,
                        extractor_version=self.extractor_version,
                        raw_snapshot_hash=self.raw_snapshot_hash,
                        primary_domain="tax",
                        subdomain="tax_filing",
                        authority_class=self.authority_class,
                        reuse_status=self.reuse_status
                    ))

        return candidates
