# PROMPT: SEMANTIC CLASS & CONCEPT AUDIT (v1.1b)

You are an expert Japanese computational lexicographer and ontologist specializing in professional terminology (Accounting, Tax, Corporate Law, Business Management, and International Trade).

## TASK
Evaluate whether the assigned `current_semantic_class` accurately classifies the entity/concept represented by the Japanese term.

## CRITICAL PRINCIPLE: VALIDATE THE CONCEPT BEFORE THE SENTENCE
A semantic class governs all downstream collocation predicates, example sentences, and workplace dialogues.
- An organization or firm (e.g. 監査法人 = audit firm, 税務署 = tax office) is an `organization` or `professional_service_firm`, NEVER an `account` or `procedure`.
- A statutory law or act (e.g. 租税特別措置法 = statutory act) is a `statutory_law`, NEVER a `procedure`.
- A business taxpayer category (e.g. 免税事業者 = tax-exempt business) is a `taxpayer_category`, NEVER a `procedure`.
- A physical tax slip or statutory form (e.g. 源泉徴収票 = withholding tax slip) is a `document` or `statutory_document`, NEVER a `procedure`.
- An accounting asset or ledger line item (e.g. 棚卸資産 = inventories) is an `account`, NEVER a `procedure`.

## PERMISSIBLE ONTOLOGY TAXONOMY (NON-EXHAUSTIVE BUT RECOMMENDED)
- `account`: balance sheet or income statement line item (assets, liabilities, equity, revenues, expenses)
- `tangible_fixed_asset`: land, buildings, structures, machinery
- `depreciable_asset`: machinery, equipment, vehicles, tools
- `intangible_asset`: goodwill (のれん), patents, software, trademark
- `securities_investment`: stocks, government bonds, investment securities
- `equity_valuation_account`: valuation differences, deferred hedges
- `financial_statement`: balance sheet, income statement, cash flow statement, EDINET reports
- `tax`: tax types (corporate tax, income tax, consumption tax)
- `tax_scheme`: statutory tax regimes, donation schemes (ふるさと納税, インボイス制度)
- `tax_filing`: tax return filing processes (確定申告, 青色申告, 年末調整)
- `tax_deduction`: income deductions, tax credits (配偶者控除, 基礎控除, 雑損控除)
- `tax_loss`: loss carryforward, refund of loss carryback
- `taxable_income_element`: taxable additions/subtractions (益金, 損金, 申告調整)
- `executive_compensation`: director remuneration, statutory executive bonuses
- `organization`: corporations, agencies, government bodies, tax offices, customs
- `professional_service_firm`: audit firms (監査法人), tax accountant corporations (税理士法人), advisory firms
- `person_role`: directors, certified accountants, licensed customs brokers, taxpayers
- `taxpayer_category`: tax-exempt enterprise, qualified invoicing business
- `statutory_law`: formal codes, statutory acts, ministerial ordinances
- `document`: business forms, invoices, meeting notices, contracts
- `statutory_document`: official withholding slips, statutory summaries, tax declarations
- `shipping_document`: bills of lading (B/L), air waybills (AWB), packing lists
- `trade_term`: Incoterms (FOB, CIF, EXW, DDP)
- `trade_finance`: letters of credit (L/C), bills of exchange, documentary collection
- `customs_procedure`: import/export customs clearance, statutory verification
- `customs_tariff`: tariff rates, HS codes, rules of origin
- `cargo_operation`: vanning, devanning, lashing, stevedoring
- `freight_charge`: ocean freight, demurrage, detention, surcharges
- `logistics_facility`: bonded yards, container yards, CFS, warehouses
- `contract`: business agreements, commercial treaties
- `contract_clause`: force majeure, warranty, limitation of liability
- `business_practice`: Ringi workflow, preliminary consensus (根回し), report-contact-consult (報連相)
- `metric`: financial ratios, operational metrics, KPI, LTV
- `procedure`: administrative or operational workflows not fitting specialized classes above

## INPUT RECORD
```json
{
  "surface": "{surface}",
  "reading": "{reading}",
  "domain_primary": "{domain_primary}",
  "current_semantic_class": "{current_semantic_class}",
  "meaning_en": "{meaning_en}",
  "meaning_vi": "{meaning_vi}",
  "related_terms": {related_terms}
}
```

## OUTPUT SCHEMA
Respond strictly with a JSON object (no markdown fences, no explanatory preamble):
```json
{
  "decision": "correct" | "incorrect" | "ambiguous" | "needs_human_review",
  "suggested_semantic_class": "string",
  "reason": "Single concise sentence (under 30 words) explaining the classification rationale."
}
```
