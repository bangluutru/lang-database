# Source License Matrix & Redistribution Analysis (Phase 1.3C)

## 1. Executive Summary

This document establishes the authoritative license audit and redistribution matrix for all real upstream datasets ingested in Phase 1.3C of the **Open Language Database** (`lang-database`).

Every record in the canonical database maintains explicit field-level source evidence and record-level licensing terms. No homogeneous blanket license is applied without individual record tracking.

---

## 2. Ingested Upstream Source Inventory

| Source ID | Upstream Entity / Project | License Identifier | License Category | Share-Alike Obligation | Commercial Use | Derivatives Allowed | Attribution Required |
|:---|:---|:---|:---|:---:|:---:|:---:|:---:|
| `kanjidic2` | Electronic Dictionary R&D Group (EDRDG) | `CC-BY-SA-3.0` | Tier 2 Attribution + ShareAlike | **YES** | YES | YES | YES |
| `joyo` | Electronic Dictionary R&D Group (EDRDG) (derived from KANJIDIC2, referencing 文化庁 2010 Cabinet Notification) | `CC-BY-SA-3.0` | Tier 2 Attribution + ShareAlike | **YES** | YES | YES | YES |
| `jmdict` | Electronic Dictionary R&D Group (EDRDG) | `CC-BY-SA-3.0` | Tier 2 Attribution + ShareAlike | **YES** | YES | YES | YES |
| `ngsl` | Dr. Charles Browne, Dr. Brent Culligan, Joseph Phillips | `CC-BY-4.0` | Tier 2 Attribution | NO | YES | YES | YES |
| `ngsl_spoken` | Dr. Charles Browne, Dr. Brent Culligan, Joseph Phillips | `CC-BY-4.0` | Tier 2 Attribution | NO | YES | YES | YES |
| `nawl` | Dr. Charles Browne, Dr. Brent Culligan, Joseph Phillips | `CC-BY-4.0` | Tier 2 Attribution | NO | YES | YES | YES |
| `bsl` | Dr. Charles Browne, Dr. Brent Culligan, Joseph Phillips | `CC-BY-4.0` | Tier 2 Attribution | NO | YES | YES | YES |
| `tsl` | Dr. Charles Browne, Dr. Brent Culligan, Joseph Phillips | `CC-BY-4.0` | Tier 2 Attribution | NO | YES | YES | YES |
| `vn_freq` | tabidots / Vietnamese Word Frequencies Project | `MIT` | Tier 1 Permissive | NO | YES | YES | YES (Notice) |
| `unihan` | Unicode Consortium (Unicode 16.0.0) | `Unicode-DFS-2016` | Tier 2 Permissive Attribution | NO | YES | YES | YES (Notice) |
| `jlpt_consensus` | Jonathan Waller / tanos.co.uk (Bluskyo/JLPT_Vocabulary collation) | `CC-BY-3.0` | Tier 2 Attribution | NO | YES | YES | YES |

---

## 3. Share-Alike (CC-BY-SA 3.0) Contamination Analysis (Section 16)

### 3.1 The Legal Boundary
- `JMdict` and `KANJIDIC2` are published under **CC-BY-SA 3.0**.
- CC-BY-SA 3.0 mandates that if you create an *Adapted Material* (derivative work) based upon the licensed material, you must license the Adapted Material under CC-BY-SA 3.0 or a compatible license.
- **Collective Work / Compilation vs. Derivative Work**:
  - The `lang-database` multi-table relational graph stores data in modular collections (`concepts.jsonl`, `senses.jsonl`, `expressions.jsonl`, `classifications.jsonl`).
  - Individual Japanese expressions derived from JMdict/KANJIDIC2 are tagged with `license: "CC-BY-SA-3.0"`.
  - Non-Japanese expressions (English from NGSL, Vietnamese from vn_freq/Unihan) are tagged with their independent upstream licenses (`CC-BY-4.0`, `MIT`, `Unicode-DFS-2016`).

### 3.2 Redistribution Policy for Canonical and Export Datasets
1. **Canonical JSONL Datasets (`data/canonical/`)**:
   - Distributed as a multi-licensed compilation.
   - Individual records retain their individual source licenses in the `license` and `source_evidence` attributes.
   - The compilation as a whole, when distributed bundled with Japanese JMdict definitions/readings, satisfies CC-BY-SA 3.0 for all adapted Japanese components.
2. **Pedagogical Export Decks (`data/exports/cross_language/`, `data/exports/oki_language/`)**:
   - Because the export decks merge English lemmas, Japanese glosses/readings, and Vietnamese glosses into unified learning cards, the merged cards containing JMdict data are released under **CC-BY-SA 3.0** with full EDRDG copyright attribution.
   - Downstream consumers (including the `oki-language` web application) can freely use, host, redistribute, and build upon these learning decks commercially, provided that:
     1. Appropriate credit is given to EDRDG, the NGSL project, tabidots, and Unicode.
     2. Any derivative improvements to the Japanese lexical cards are shared under CC-BY-SA 3.0.
3. **Quarantine & Non-Commercial Gating**:
   - Any source bearing NC (Non-Commercial) or ND (No-Derivatives) restrictions is strictly PROHIBITED from canonical production and sent to `QUARANTINE`.
   - Zero NC or ND sources are present in Phase 1.3C canonical releases.

---

## 4. Attribution Notices Required in Downstream Products

Downstream consumers must display the following attribution notices (e.g., in `ATTRIBUTION.md` or application "About" modals):
- **Japanese Dictionary Data**:
  > This product uses the JMdict and KANJIDIC2 dictionary files. These files are the property of the Electronic Dictionary Research and Development Group (EDRDG), and are used in conformance with the Group's licence (CC-BY-SA-3.0).
- **English General Service & Academic Vocabulary**:
  > English vocabulary lists (NGSL, NGSL-Spoken, NAWL, BSL, TSL) are provided courtesy of Dr. Charles Browne, Dr. Brent Culligan, and Joseph Phillips under the Creative Commons Attribution 4.0 International License.
- **Vietnamese Lexical Frequency Data**:
  > Vietnamese frequency data is derived from tabidots/vn-freqs under the MIT License.
- **Han-Viet Character Data**:
  > Han-Viet and Kanji readings are derived from the Unicode Character Database (Unihan 16.0.0) under the Unicode Terms of Use (Unicode-DFS-2016).

- **JLPT Vocabulary Data**:
  > JLPT vocabulary lists are based on data from Jonathan Waller's tanos.co.uk project, licensed under Creative Commons Attribution (CC-BY-3.0). Reformatted by Bluskyo/JLPT_Vocabulary (MIT). Attribution: Jonathan Waller, https://www.tanos.co.uk/jlpt/

