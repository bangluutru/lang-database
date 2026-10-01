# PHASE 1.1C — QUARANTINE REMEDIATION & PILOT FREEZE CLOSURE REPORT

**Generated**: 2026-10-01T02:52:34.988675+00:00
**Starting commit**: `be6cfffefda5886ee00b9d03b3b5b2eb1bd99ea8`

## Summary

| Metric | Value |
|--------|-------|
| Original pilot | 800 |
| Production before remediation | 772 |
| Initial quarantine | 28 |
| Recovered | 28 |
| Still needs review | 0 |
| Permanent quarantine | 0 |
| **Golden Pilot production records** | **800** |

## Domain Distribution

| Domain | Records |
|--------|---------|
| accounting | 200 |
| business | 200 |
| tax | 200 |
| trade | 200 |

## Validation Coverage

| Coverage Type | Records | Coverage % |
|---------------|---------|------------|
| Linguistic judge | 800 | 100.0% |
| Blind rejudge | 800 | 100.0% |
| Adversarial audit (recovered quarantine) | 28 | 3.5% |

## Dataset Hash

```
Canonical SHA-256: 27830fa0d861012f7878f9d95d1da5fe281a14076b38bb03c41f446d56a0c45c
Vocabulary file SHA-256: 1da7f6b958d3a1c4ccb12c4850b05ea5828b2d6ab8872077fea2e250d0e435c6
```

## Failure Category Distribution (Initial 28 Quarantined)

| Category | Count |
|----------|-------|
| TECHNICAL_VALIDATION_FAILURE | 28 |
| EXAMPLE_DOES_NOT_CONTAIN_TERM | 15 |
| DIALOGUE_ERROR | 10 |
| EXAMPLE_NATURALNESS_ERROR | 7 |
| DOMAIN_FACTUAL_ERROR | 7 |
| COLLOCATION_ERROR | 4 |
| SEMANTIC_CLASS_ERROR | 1 |

## Reconciliation

800 = 800 (production) + 0 (needs_review) + 0 (permanent_quarantine)

✓ All 800 original records accounted for: 800 = True

## Golden Pilot Release

Path: `/Users/tranhaibang/.gemini/antigravity-ide/scratch/xtools/lang-database/data/releases/golden-pilot-v1`
Files:
- `vocabulary.jsonl` — production records sorted by canonical ID
- `dataset_manifest.json` — release metadata and hashes
- `validation_manifest.json` — validation architecture metadata
- `checksums.sha256` — file checksums
