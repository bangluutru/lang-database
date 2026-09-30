# Changelog

All notable changes to the **JP Professional Vocabulary Database** are documented here in accordance with [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) and Semantic Versioning.

---

## [v0.1-pilot] - 2026-10-01

### Added
- **4-Layer Data Architecture**: Fully established Layer A (Raw Sources), Layer B (Extracted Candidates), Layer C (Canonical Vocabulary), and Layer D (Enriched Learning Objects).
- **Source Governance & Traffic Light Registry**:
  - Registered FSA (`fsa_edinet_2026`, GREEN, PDL-1.0).
  - Registered NTA (`nta_tax_glossary_2026`, GREEN, PDL-1.0).
  - Registered JICPA (`jicpa_glossary`, YELLOW, Terminology Reference only).
  - Registered ASBJ (`asbj_standards`, YELLOW, Terminology Reference only).
  - Registered JETRO (`jetro_trade`, YELLOW, Concept Discovery only).
- **Automated Source Ingestion & Checksum**:
  - Implemented `scripts/download_sources.py` downloading official 2026 EDINET workbooks (`1f_AccountList.xlsx`, `1e_ElementList.xlsx`, `1g_IFRS_ElementList.xlsx`, `1b-3_Yougo.pdf`).
  - SHA-256 verified and immutable storage under `data/raw/fsa/edinet/2026/`.
  - Strict isolation of 2027 draft taxonomy into `staging/fsa_edinet_2027_draft/` marked `source_status: draft`.
- **OpenPyXL Workbook Inspection**:
  - Implemented `scripts/inspect_excel.py` generating comprehensive structural reports in `reports/source_ingestion/`.
- **Phase 1 Pilot Dataset (800 Canonical Entries)**:
  - **Accounting (200 entries)**: Core financial statements (B/S, P/L, C/F), assets, liabilities, equity, revenues, costs, depreciation, and IFRS taxonomy items.
  - **Tax (200 entries)**: Income tax classifications, corporate tax adjustments (Schedule 4 / Schedule 5), consumption tax & qualified invoice system (Peppol), withholding, and tax audit compliance.
  - **Business (200 entries)**: Commercial transactions (quotes, POs, deliveries, invoices), corporate governance (Board, statutory auditors, Ringisho), contracts & IP (NDA, license, civil code non-conformity), HR & labor (payroll, social insurance, leave), sales, and startups.
  - **Trade (200 entries)**: Incoterms 2020 (FOB, CIF, DDP, EXW), shipping documents (B/L, AWB, C/O, packing list), customs clearance & tariffs (HS codes, bonded warehouses, EPA preferential rates), trade finance & L/C (discrepancy, forward contracts), logistics, and EPA/FTA agreements.
- **Workplace Idiomatic Expressions Layer**:
  - 50 authentic workplace expressions in `data/production/expressions.jsonl` (e.g. `請求書を切る`, `経費で落とす`, `数字が合わない`, `相見積もりを取る`, `消込を行う`).
- **Semantic Relationship Graph**:
  - 2,078 relational edges in `data/production/relationships.jsonl` classifying `synonym`, `opposite`, and `related` associations.
- **SQLite Engine & FTS5 Search**:
  - Implemented `scripts/export_sqlite.py` producing `data/production/jp_professional.db` with indexes and FTS5 search table.
- **Automated QA Pipeline**:
  - Implemented `scripts/validate_dataset.py` verifying 15 schema criteria with 100% pass rate recorded in `reports/qa_report.json` and `reports/qa_summary.md`.
- **Automated Test Suite**:
  - Implemented `tests/test_schema.py` and `tests/test_pipeline.py` with 15 passing pytest test cases.
