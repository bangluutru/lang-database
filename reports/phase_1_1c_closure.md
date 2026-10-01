# PHASE 1.1C — QUARANTINE REMEDIATION & PILOT FREEZE CLOSURE REPORT

**Generated**: 2026-10-01T02:52:34.988675+00:00
**Final verification**: 2026-10-01T03:10:00+00:00
**Starting commit**: `be6cfffefda5886ee00b9d03b3b5b2eb1bd99ea8`
**Closing commit**: `2910f98`

---

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

---

## Test Suite

**Command**: `pytest tests/ -v --tb=short`
**No live LLM calls required** — all tests operate on frozen data and production records.

| Result | Count |
|--------|-------|
| **Total** | **111** |
| Passed | 111 |
| Failed | 0 |
| Skipped | 0 |
| **Exit code** | **0 (PASS)** |

---

## Dataset Invariants

**Command**: `python scripts/check_dataset_invariants.py`

| Invariant | Result |
|-----------|--------|
| INV-1: Pilot freeze equation (800 = prod + review + perm_q) | ✅ PASS |
| INV-2: Zero `generated` status in production | ✅ PASS |
| INV-3: Truthful Gemini model provenance | ✅ PASS |
| INV-4: No duplicate IDs | ✅ PASS |
| INV-5: Known release versions only | ✅ PASS |
| INV-6: JLPT decoupled (null) | ✅ PASS |
| INV-7: Permanent quarantine metadata | ✅ PASS |
| INV-8: Golden Pilot SHA-256 integrity | ✅ PASS |
| INV-9: No accounting template injection (new violations) | ✅ PASS (0 new; 91 Phase 1.2 backlog) |
| INV-10: Term referenced in examples or dialogue (new) | ✅ PASS (0 new; 3 Phase 1.2 backlog) |
| INV-11: No governance predicate injection | ✅ PASS |
| **Hard failures** | **0** |
| Backlog warnings (Phase 1.2) | 2 |
| **Exit code** | **0 (PASS)** |

---

## Golden Pilot Hash Verification

**Method**: Independent verification using exact algorithm from `compute_canonical_dataset_hash()` in `scripts/run_phase1_1c.py`
(sorted by `id`, `status` excluded, incremental SHA-256 update per record).

| Hash | Computed | Expected | Match |
|------|----------|----------|-------|
| Canonical SHA-256 | `27830fa0d861012f7878f9d95d1da5fe281a14076b38bb03c41f446d56a0c45c` | `27830fa0d861012f7878f9d95d1da5fe281a14076b38bb03c41f446d56a0c45c` | ✅ |
| Vocabulary file SHA-256 | `1da7f6b958d3a1c4ccb12c4850b05ea5828b2d6ab8872077fea2e250d0e435c6` | `1da7f6b958d3a1c4ccb12c4850b05ea5828b2d6ab8872077fea2e250d0e435c6` | ✅ |
| **Result** | | | **PASS ✓** |

---

## Domain Distribution

| Domain | Records |
|--------|---------|
| accounting | 200 |
| business | 200 |
| tax | 200 |
| trade | 200 |

---

## Validation Coverage

| Coverage Type | Records | Coverage % |
|---------------|---------|------------|
| Linguistic judge | 800 | 100.0% |
| Blind rejudge | 800 | 100.0% |
| Adversarial audit (recovered quarantine) | 28 | 3.5% |

---

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

Note: 2 records required a second-pass resolver (完成工事総利益, 甲乙関係). All 28 recovered.

---

## Reconciliation

```
800 = 800 (production_verified) + 0 (needs_review) + 0 (permanent_quarantine)
```

✅ All 800 original records accounted for.

---

## Phase 1.2 Backlog (discovered, not remediated in 1.1C)

| Invariant | Records | Description |
|-----------|---------|-------------|
| INV-9 | 91 | Pre-existing accounting ledger templates in business/trade records from Phase 1.1A/B |
| INV-10 | 3 | Pre-existing records where examples/dialogue don't reference the target term |

Tracked in: `config/known_invariant_suppressions.json`
These are **real quality findings**, not false positives. They will be addressed in Phase 1.2.

---

## Golden Pilot Release

Location: `data/releases/golden-pilot-v1/`

| File | Purpose |
|------|---------|
| `vocabulary.jsonl` | Production records sorted by canonical ID |
| `dataset_manifest.json` | Release metadata, canonical SHA-256, domain counts |
| `validation_manifest.json` | Validation architecture metadata |
| `checksums.sha256` | File integrity checksums |

**Policy**: Immutable. Corrections produce `v1.1` or `v2` — never overwrite in place.
