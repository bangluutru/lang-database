# Phase 1.2C — Controlled Canary Release Report

**Release ID:** `canary-1.2c`  
**Parent Baseline:** `golden-pilot-v1.1`  
**Final Status:** **`CANARY_1_2C_RELEASED`**  
**Release Timestamp:** `2026-10-01T07:38:10Z`  

## 1. Candidate Disposition & Promotion Audit

| Category | Count | Status / Outcome |
|---|:---:|---|
| **Selected Candidates** | **120** | Total stratified candidate pool sample |
| Approved Unchanged | 77 | Promoted directly to Canary |
| Approved After Revision | 25 | Successfully revalidated & promoted to Canary |
| Statutory / Industry Abbreviations | 8 | Linked in `relationships.jsonl` (not in vocabulary) |
| Rejected Extraction Artifacts | 1 | Quarantined (`用語一覧`) |
| Rejected Composite Taxonomy Labels | 9 | Preserved in staging evidence, excluded from Canary |
| Failed Revalidation | 0 | None (100% revalidation pass rate) |
| **Promoted Canonical Records** | **`102`** | Output in `vocabulary.jsonl` |

## 2. Release File Artifacts & Cryptographic Checksums

| File | SHA-256 Checksum | Description |
|---|---|---|
| `vocabulary.jsonl` | `f1d0d0fc27226162e80b8bf0acce1c2ad9844e5739e378e5dd24019c1e9835ef` | Canonical Canary professional vocabulary (102 terms) |
| `relationships.jsonl` | `be1f792f7f4062b3387a6cd85868714452b959666b0770df30f902f48b4a0825` | Abbreviation / alias relationships (8 relationships) |
| `dataset_manifest.json` | - | Release metadata, distribution & pool invariants |
| `validation_manifest.json` | - | Verification record for Gates A through F |
| `promotion_audit.jsonl` | - | Complete audit disposition for all 120 candidates |
| `checksums.sha256` | - | Cryptographic bundle hashes |

**Canonical Dataset SHA-256:** `4f2ac4a34ee170b445653900fe7067cd4474295ffab75d745877bc2b5830eb8d`  

## 3. Domain Distribution of Canonical Canary Records

| Domain | Promoted Count |
|---|:---:|
| `accounting` | 10 |
| `business` | 6 |
| `finance` | 17 |
| `hr` | 16 |
| `legal` | 12 |
| `management` | 4 |
| `office_communication` | 11 |
| `purchasing` | 4 |
| `sales` | 1 |
| `tax` | 9 |
| `trade` | 12 |

## 4. Source Diversity Distribution

| Source ID | Term Count |
|---|:---:|
| `fsa-edinet-taxonomy` | 26 |
| `smrj-business-guidance` | 22 |
| `egov-corporate-law` | 18 |
| `mhlw-labor` | 16 |
| `nta-tax-glossary` | 9 |
| `japan-customs-trade` | 8 |
| `jetro-trade` | 4 |
| `asbj-accounting-standards` | 1 |
