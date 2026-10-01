# PHASE 1.2A — EXISTING BACKLOG REMEDIATION

**Starting commit:** `8b7522f62098dc6e24f9e674b5843cffedbaa127`  
**Final commit:** Pending git commit  
**Original Golden Pilot v1:** 800  
**INV-9 initial backlog:** 91  
**INV-10 initial backlog:** 3  
**Records requiring actual modification:** 92  
**Records passing after inspection without modification:** 0  

### Systemic generator defects discovered:
1. Fallback accounting ledger template (`月末の帳簿照合`, `補助元帳`, `計上内容や残高`, `今月の月次決算で`) unconditionally applied to non-accounting domains (`business`, `trade`) in `example_generator.py`.
2. `person_role` semantic frame defaulted to corporate governance board/shareholder appointment for international trade counterparties (`輸出者`).
3. Term surface omission / substitution in fallback examples (`備品台帳` for `備品管理`, `輸出業務` for `輸出者`, `外貨建取引` for `外国為替`).

### Invariant Backlog Status:
- **INV-9 remaining:** 0
- **INV-10 remaining:** 0
- **True Linguistic Judge coverage:** 92/92 (100%)
- **Blind Rejudge coverage:** 92/92 (100%)
- **Adversarial audit coverage:** 92/92 (100%)

### Release Baselines:
- **Golden Pilot v1:** UNCHANGED
- **Golden Pilot v1 canonical SHA-256:** `27830fa0d861012f7878f9d95d1da5fe281a14076b38bb03c41f446d56a0c45c`
- **Golden Pilot v1 vocabulary SHA-256:** `1da7f6b958d3a1c4ccb12c4850b05ea5828b2d6ab8872077fea2e250d0e435c6`
- **Golden Pilot v1.1 records:** 800
- **Golden Pilot v1.1 canonical SHA-256:** `5ae36d8ace6884a50a0e1fa8c8fd4399660575a133ea2dcbdcf8e16b1f51be15`
- **Golden Pilot v1.1 vocabulary SHA-256:** `1e18d574e1c1b0f54451456e33648518f6e49a7e0dfc37eb1fec3dd35e55325d`

### Invariant Checks & Suppressions:
- **Tests:** 123
  - **Passed:** 123
  - **Failed:** 0
  - **Skipped:** 0
- **Dataset invariants:** PASS (0 warnings, 0 failures)
- **New suppressions introduced:** 0

### Known limitations:
None. All 92 records remediated, deterministically checked, and validated via True Linguistic Judge with real Gemini execution on Vertex AI.

### FINAL STATUS:
READY FOR INDEPENDENT REVIEW
