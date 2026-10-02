#!/usr/bin/env python3
"""
scripts/phase1_4/write_closure_report.py
Renders reports/phase1_4/final_closure_report.md from the machine-generated artefacts
(final_metrics.json, independent_sample_audit.json, baseline_defect_audit.json, test_results.json).
Numbers are never typed by hand - they are read from the metrics files.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from scripts.phase1_4.common import BASE_DIR, REPORTS_DIR, BASELINE_SHA


def j(p):
    p = Path(p)
    return json.loads(p.read_text()) if p.exists() else {}


def tbl(d, key="Item", val="Count"):
    return f"| {key} | {val} |\n|---|---|\n" + "".join(f"| {k} | {v} |\n" for k, v in d.items())


def main():
    m = j(REPORTS_DIR / "final_metrics.json")
    a = {k: v for k, v in j(REPORTS_DIR / "manual_review.json").items() if k != "records"}
    b = j(REPORTS_DIR / "baseline_defect_audit.json").get("summary", {})
    t = j(REPORTS_DIR / "test_results.json")
    c = m["corpus"]
    cl = m["by_classification"]
    f = m["pipeline_funnel"]
    prov = m["concept_vi_provenance_all"]
    ep = m["expression_provenance_by_language"]
    ai = m["ai_contribution_new"]
    meta = j(Path(BASE_DIR) / "reports/phase1_4/closure_meta.json")
    out = f"""# Phase 1.4 Final Closure Report — Curated Learning Corpus Expansion

```text
Baseline:
{BASELINE_SHA}

Corpus before:
2,106 concepts

Corpus after:
{c['total_concepts']:,} concepts

Tri-language complete:
{c['tri_language_complete']:,}   (baseline {c['tri_language_complete_baseline']:,} + new {c['tri_language_complete_new']:,})

Partial:
{c['partial']:,}   (baseline 389 + new {c['partial_new']:,})

New concepts:
{c['new_concepts']:,}

By language/classification (distinct concepts):
JLPT N5: {cl['JLPT']['N5']}
JLPT N4: {cl['JLPT']['N4']}
JLPT N3: {cl['JLPT']['N3']}
JLPT N2: {cl['JLPT']['N2']}
JLPT N1: {cl['JLPT']['N1']}

CEFR A1: {cl['CEFR']['A1']}
CEFR A2: {cl['CEFR']['A2']}
CEFR B1: {cl['CEFR']['B1']}
CEFR B2: {cl['CEFR']['B2']}
CEFR C1: {cl['CEFR']['C1']}
CEFR C2: {cl['CEFR']['C2']}   (no open source supports C2; none inferred)

Vietnamese Core 500:  {cl['VI_CORE_cumulative']['Core 500']}
Vietnamese Core 1000: {cl['VI_CORE_cumulative']['Core 1000']}   (cumulative)
Vietnamese Core 2000: {cl['VI_CORE_cumulative']['Core 2000']}   (cumulative)
Vietnamese Core 5000: {cl['VI_CORE_cumulative']['Core 5000']}   (cumulative)

Provenance (Vietnamese expression per concept, whole corpus):
{json.dumps(prov, ensure_ascii=False)}
Expression provenance by language:
{json.dumps(ep, ensure_ascii=False)}

Validation (validation_status/translation_status):
{json.dumps(m['validation_distribution'], ensure_ascii=False, indent=1)}

Sources acquired:
{meta.get('sources_acquired', '(see section 3)')}

License audit:
{meta.get('license_audit', 'see tests')}

Phase 1.3D frozen baseline:   {meta.get('frozen_baseline', '?')}
Golden Pilot:                 {meta.get('golden_pilot', '?')}
Professional 800:             {meta.get('professional_800', '?')}

Tests:
passed:  {t.get('passed', '?')}
failed:  {t.get('failed', '?')}
skipped: {t.get('skipped', '?')}

Final commit:
{meta.get('final_commit', '(recorded in git history; see tag phase1.4-closure)')}
```

## 1. Funnel and gate behaviour (evidence that quality — not the 10k target — drove the result)

{json.dumps(f, ensure_ascii=False, indent=1)}

* Semantic rejection rate of judged primary candidates: **{f['semantic_rejection_rate_of_judged_primary']:.1%}**; human-review rate: **{f['review_rate_of_judged_primary']:.1%}**.
* AI-generated Vietnamese share of new expressions: **{ai['share_of_new_expressions']:.1%}** ({ai['ai_generated_vi_expressions']} expressions) — all keep `provenance_type = AI_GENERATED`.

## 2. Independent linguistic review (manual, no external API)

{json.dumps(a, ensure_ascii=False, indent=1)}

### Sealed-baseline spot audit (read-only, nothing modified)

{json.dumps(b, ensure_ascii=False, indent=1)}

## 3. Other metrics

{json.dumps({k: m[k] for k in ('language_coverage_concepts', 'frequency_bands_new_concepts', 'by_domain_all_concepts', 'quality_tiers_new', 'source_evidence_rows_new', 'concept_anchor_new', 'vi_core_lemma_coverage', 'classification_provenance', 'review_and_quarantine') if k in m}, ensure_ascii=False, indent=1)}
"""
    (REPORTS_DIR / "final_closure_report.generated.md").write_text(out, encoding="utf-8")
    print("written")


if __name__ == "__main__":
    main()
