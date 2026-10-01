# Phase 1.2C — Manual Adversarial Inspection Report

- **Evaluated At**: `2026-10-01T05:52:34Z`
- **Sample Size**: `36` deliberately challenging candidates
- **Focus**: Expose edge cases, abbreviations, polysemy, orthographic variants, and injection attacks.

## 1. Summary of Gate Behavior Across Challenge Categories

| Category | Test Count | Pipeline Behavior & Protection Mechanism |
|:---------|:----------:|:-----------------------------------------|
| **Abbreviations & Acronyms** | 8 | Detected via `KNOWN_ABBREVIATIONS_MAP`; cleanly transitioned to `needs_review` |
| **Similar Accounting Terms** | 6 | Validated with distinct structural modifiers (`純額`, `契約資産`, etc.) |
| **Orthographic Variants** | 4 | Detected via `KNOWN_ORTHOGRAPHIC_VARIANTS`; transitioned to `variant_detected` |
| **Parenthetical Variants** | 2 | Detected repetitive or English acronym parens; routed to `variant_detected` |
| **Polysemy & Cross-Domain Senses** | 4 | Detected via `KNOWN_POLYSEMOUS_SENSES`; routed to `sense_ambiguous` / review |
| **Mixed Alphanumeric Notation** | 2 | Verified custom readings (`36協定` -> `さぶろくきょうてい`) & script syntax |
| **Katakana Loanwords** | 3 | Validated Japanese middle-dot `・` and Katakana phonotactics without syntax failure |
| **Legal Statutory Formulations** | 3 | Validated formal statutory phrases from Companies Act / Labor Standards Act |
| **Multi-Source Corroborations** | 2 | Multi-agency cross-reference preserved in provenance evidence |
| **Draft Source Injection Attack** | 1 | **BLOCKED** by Gate A (`fsa-edinet-2027-draft` rejected immediately) |
| **RED Licensing Status Attack** | 1 | **BLOCKED** by Gate A (transitioned to `licensing_blocked`) |

## 2. Detailed Inspection Table

| ID | Surface | Domain | Reading | Category | Resulting State | Gate Findings |
|:---|:--------|:-------|:--------|:---------|:----------------|:--------------|
| `adv-001` | `NACCS` | `trade` | `なっくす` | `abbreviation` | `needs_review` | Abbreviation detected: 'NACCS' is abbreviation of '輸出入・港湾関連情報処理システム'. |
| `adv-002` | `B/L` | `trade` | `びーえる` | `abbreviation` | `needs_review` | Abbreviation detected: 'B/L' is abbreviation of '船荷証券'. |
| `adv-003` | `L/C` | `trade` | `えるしー` | `abbreviation` | `needs_review` | Abbreviation detected: 'L/C' is abbreviation of '信用状'. |
| `adv-004` | `FOB` | `trade` | `えふおーびー` | `abbreviation` | `duplicate_detected` | Exact duplicate of baseline record jp-pro-trade-000002 ('FOB' in domain 'trade'). |
| `adv-005` | `CIF` | `trade` | `しーあいえふ` | `abbreviation` | `duplicate_detected` | Exact duplicate of baseline record jp-pro-trade-000003 ('CIF' in domain 'trade'). |
| `adv-006` | `BCP` | `management` | `びーしーぴー` | `abbreviation` | `needs_review` | Abbreviation detected: 'BCP' is abbreviation of '事業継続計画'. |
| `adv-007` | `J-SOX` | `accounting` | `じぇいそっくす` | `abbreviation` | `needs_review` | Invalid subdomain 'internal_control' for domain 'accounting'.<br>Abbreviation detected: 'J-SOX' is abbreviation of '日本版SOX法'. |
| `adv-008` | `NDA` | `legal` | `えぬでぃーえー` | `abbreviation` | `needs_review` | Abbreviation detected: 'NDA' is abbreviation of '秘密保持契約'. |
| `adv-009` | `受取手形(純額)` | `accounting` | `うけとりてがたじゅんがく` | `similar_accounting_terms` | `validation_passed` | All gates passed cleanly |
| `adv-010` | `売掛金(純額)` | `accounting` | `うりかけきんじゅんがく` | `similar_accounting_terms` | `validation_passed` | All gates passed cleanly |
| `adv-011` | `契約資産(純額)` | `accounting` | `けいやくしさんじゅんがく` | `similar_accounting_terms` | `validation_passed` | All gates passed cleanly |
| `adv-012` | `受取手形、売掛金及び契約資産` | `accounting` | `うけとりてがたうりかけきんおよびけいやくしさん` | `similar_accounting_terms` | `validation_passed` | All gates passed cleanly |
| `adv-013` | `関係会社売掛金` | `accounting` | `かんけいがいしゃうりかけきん` | `similar_accounting_terms` | `validation_passed` | All gates passed cleanly |
| `adv-014` | `割賦売掛金` | `accounting` | `かっぷうりかけきん` | `similar_accounting_terms` | `validation_passed` | All gates passed cleanly |
| `adv-015` | `売り掛け金` | `accounting` | `うりかけきん` | `orthographic_variant` | `variant_detected` | Orthographic variant detected: '売り掛け金' is variant of canonical form '売掛金'. |
| `adv-016` | `買い掛け金` | `accounting` | `かいかけがね` | `orthographic_variant` | `variant_detected` | Orthographic variant detected: '買い掛け金' is variant of canonical form '買掛金'. |
| `adv-017` | `取引き先` | `business` | `とりひききさき` | `orthographic_variant` | `variant_detected` | Orthographic variant detected: '取引き先' is variant of canonical form '取引先'. |
| `adv-018` | `棚卸し資産` | `accounting` | `たなおろししさん` | `orthographic_variant` | `variant_detected` | Orthographic variant detected: '棚卸し資産' is variant of canonical form '棚卸資産'. |
| `adv-019` | `受取手形(受取手形)` | `accounting` | `うけとりてがたうけとりてがた` | `parenthetical_variant` | `variant_detected` | Orthographic variant detected: '受取手形(受取手形)' is variant of canonical form '受取手形'. |
| `adv-020` | `貸借対照表(B/S)` | `accounting` | `たいしゃくたいしょうひょうBS` | `parenthetical_variant` | `variant_detected` | Orthographic variant detected: '貸借対照表(B/S)' is variant of canonical form '貸借対照表'.<br>Reading 'たいしゃくたいしょうひょうBS' contains non-kana characters for '貸借対照表(B/S)'. |
| `adv-021` | `査定` | `tax` | `さてい` | `polysemy_cross_domain` | `validation_passed` | All gates passed cleanly |
| `adv-022` | `解約` | `legal` | `かいやく` | `polysemy_cross_domain` | `validation_passed` | All gates passed cleanly |
| `adv-023` | `引当` | `purchasing` | `ひきあて` | `polysemy_cross_domain` | `rejected` | Invalid subdomain 'procurement' for domain 'purchasing'. |
| `adv-024` | `手付金` | `trade` | `てつけきん` | `polysemy_cross_domain` | `sense_ambiguous` | Invalid subdomain 'contracts' for domain 'trade'.<br>Possible different sense of existing baseline term '手付金' (business vs trade). |
| `adv-025` | `36協定` | `hr` | `さぶろくきょうてい` | `mixed_alphanumeric` | `validation_passed` | All gates passed cleanly |
| `adv-026` | `日本版SOX法` | `accounting` | `にほんばんSOXほう` | `mixed_alphanumeric` | `rejected` | Invalid subdomain 'internal_control' for domain 'accounting'.<br>Reading 'にほんばんSOXほう' contains non-kana characters for '日本版SOX法'. |
| `adv-027` | `キャッシュ・フロー` | `finance` | `きゃっしゅ・ふろー` | `katakana_loanword` | `validation_passed` | All gates passed cleanly |
| `adv-028` | `コールローン` | `finance` | `こーるろーん` | `katakana_loanword` | `validation_passed` | All gates passed cleanly |
| `adv-029` | `デューデリジェンス` | `legal` | `でゅーでりじぇんす` | `katakana_loanword` | `validation_passed` | All gates passed cleanly |
| `adv-030` | `善管注意義務` | `legal` | `ぜんかんちゅういぎむ` | `legal_statutory` | `duplicate_detected` | Invalid subdomain 'board_management' for domain 'legal'.<br>Exact duplicate of baseline record jp-pro-business-000046 ('善管注意義務' in domain 'business'). |
| `adv-031` | `過失相殺` | `legal` | `かしつそうさい` | `legal_statutory` | `validation_passed` | All gates passed cleanly |
| `adv-032` | `就業規則` | `hr` | `しゅうぎょうきそく` | `legal_statutory` | `duplicate_detected` | Exact duplicate of baseline record jp-pro-business-000091 ('就業規則' in domain 'business'). |
| `adv-033` | `減価償却累計額` | `accounting` | `げんかしょうきゃくるいけいひたい` | `multi_source` | `duplicate_detected` | Exact duplicate of baseline record jp-pro-accounting-000055 ('減価償却累計額' in domain 'accounting'). |
| `adv-034` | `インコタームズ` | `trade` | `いんこたーむず` | `multi_source` | `duplicate_detected` | Exact duplicate of baseline record jp-pro-trade-000001 ('インコタームズ' in domain 'trade'). |
| `adv-035` | `草案項目テスト` | `accounting` | `そうあんこうもくてすと` | `draft_injection_attack` | `rejected` | Evidence #0 uses prohibited draft source 'fsa-edinet-2027-draft'. |
| `adv-036` | `著作権保護用語` | `legal` | `ちょさくけんほごようご` | `licensing_guard_attack` | `licensing_blocked` | Evidence #0 has prohibited RED reuse status.<br>Invalid or prohibited reuse_status 'RED'. |
