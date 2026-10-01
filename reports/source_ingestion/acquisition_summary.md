# Upstream Source Acquisition & Ingestion Summary
**Generated at:** 2026-10-01T13:00:45.204825+00:00

## Source Acquisition Table
| Source | Version | License | Status | Artifact Size | SHA-256 | Description |
|---|---|---|---|---|---|---|
| `kanjidic2` | `2026-10-01` | `CC-BY-SA-3.0` | **VERIFIED_EXISTING** | 1453.7 KB | `1c60c9453e1c...` | Authoritative kanji dictionary with codepoints, readings, meanings, and official grade markers |
| `joyo` | `2010-official` | `PDL-1.0` | **VERIFIED_EXISTING** | 951.4 KB | `f5f0cf7d03f3...` | Official 2,136 Jōyō Kanji statutory list derived from Agency for Cultural Affairs 2010 Cabinet Notification |
| `jmdict` | `2026-10-01` | `CC-BY-SA-3.0` | **VERIFIED_EXISTING** | 10332.2 KB | `89777236dbf0...` | Comprehensive Japanese-English dictionary reference universe |
| `ngsl` | `1.2` | `CC-BY-4.0` | **VERIFIED_EXISTING** | 61.1 KB | `2098bab8955a...` | New General Service List 1.2 with empirical frequency rankings (2,809 words) |
| `ngsl_spoken` | `1.2` | `CC-BY-4.0` | **VERIFIED_EXISTING** | 17.0 KB | `07708940c50a...` | New General Service List Spoken 1.2 (721 high-frequency spoken words) |
| `nawl` | `1.2` | `CC-BY-4.0` | **VERIFIED_EXISTING** | 23.1 KB | `1790b0fa22c5...` | New Academic Word List 1.2 (960 academic words) |
| `bsl` | `1.2` | `CC-BY-4.0` | **VERIFIED_EXISTING** | 58.2 KB | `45055265eb4e...` | Business Service List 1.2 for business English terminology |
| `tsl` | `1.2` | `CC-BY-4.0` | **VERIFIED_EXISTING** | 31.3 KB | `2259df25a107...` | TOEIC Service List 1.2 for TOEIC test preparation vocabulary |
| `vn_freq` | `1.0` | `MIT` | **VERIFIED_EXISTING** | 506.5 KB | `8f644d061736...` | Vietnamese word frequencies (19,047 words) with POS tags and empirical corpus counts |
| `unihan` | `16.0.0` | `Unicode-DFS-2016` | **VERIFIED_EXISTING** | 8145.2 KB | `4c93ea9c1f63...` | Unicode Character Database Unihan archive containing Unihan_Readings.txt for Hán-Việt cognates |
| `jlpt_consensus` | `2026-v1` | `CC-BY-3.0` | **VERIFIED_EXISTING** | 191.6 KB | `810c776c7a72...` | Open JLPT vocabulary collation (N5 through N1) based on community consensus |

## Provenance & License Verification
- All sources are stored in immutable snapshots under `data/raw/<source_id>/<version>/`.
- Each snapshot contains `metadata.json`, artifact file, and `SHA256SUMS`.
- No hand-curated JSON is labeled `SOURCE_DERIVED` without upstream artifact verification.
- Non-commercial, no-derivatives, and proprietary sources are strictly quarantined.
