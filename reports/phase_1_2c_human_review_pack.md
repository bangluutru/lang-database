# Phase 1.2C — Human Review Package

- **Generated At**: `2026-10-01T07:32:13Z`
- **Total Candidates for Review**: `120`
- **Status**: **`PENDING_HUMAN_REVIEW`** (0 Approved / 120 Pending)
- **Review Complexity**: `REVIEW-C (High Attention)`: **27** | `REVIEW-B (Normal)`: **36** | `REVIEW-A (Low Risk)`: **57**

> [!IMPORTANT]
> **Strict Human Review Rule**: AI recommendations are provided strictly as non-binding evidence analysis. All 120 candidates remain in state `PENDING`. No candidate may be promoted without explicit human authorization.

## 1. Quality Audit Summary & Review Classes

| Review Complexity | Count | Characteristics | Reviewer Guidance |
|:---|:---:|:---|:---|
| **REVIEW-C (High Attention)** | **27** | Abbreviations, composite taxonomy fields, net valuation parens, reading corrections, non-term artifacts | **Requires explicit scrutiny**. Inspect reading, relationship, and canonical value. |
| **REVIEW-B (Normal)** | **34** | Class B/C sources, generic subdomain fallback glosses, domain operational terms | Verify domain context and approve suggested English gloss refinement. |
| **REVIEW-A (Low Risk)** | **59** | Statutory terminology, Class A source, unambiguous reading & gloss, zero warnings | Rapid review. Standard canonical business vocabulary. |

### Quality Flags Identified in Second-Pass Audit

| Quality Flag | Count | Description & Recommended Remediation |
|:---|:---:|:---|
| `GLOSS_REVIEW_REQUIRED` | **26** | English gloss was a generic subdomain name; improved professional English gloss recommended. |
| `CANONICAL_VALUE_REVIEW_REQUIRED` | **9** | Composite reporting line item (with 及び, 並びに) or net parens (純額); review if suitable as canonical headword. |
| `READING_REVIEW_REQUIRED` | **9** | Automatic kanji-to-kana mis-reading identified (e.g. 額->ひたい, 書->かき, 貸出金->たいしゅつきん); corrected reading proposed. |
| `ABBREVIATION_FLAG` | **8** | Acronym or statutory short title (NACCS, 印基通, 印法); recommended to link to full canonical form via ABBREVIATION_OF. |
| `EXTRACTION_ARTIFACT_FLAG` | **1** | Website navigation / index heading (用語一覧); recommended for REJECT. |

## 2. Domain-Ordered Review Sections

### Section 1: Domain `accounting` (18 Candidates)

| ID | Proposed Canonical ID | Surface / Reading | English Meaning & Suggestion | Complexity & Flags | AI Suggestion | Human Decision |
|:---|:---|:---|:---|:---|:---|:---:|
| `pool-cand-000001` | `jp-canary-accounting-0004` | **受取手形、売掛金及び契約資産**<br><code>うけとりてがたうりかけきんおよびけいやくしさん</code> | Notes and accounts receivable - trade, and contract assets | **REVIEW-C**<br>`CANONICAL_VALUE_REVIEW_REQUIRED` | REVIEW_COMPOSITE_TAXONOMY_LABEL | `[ PENDING ]` |
| `pool-cand-000002` | `jp-canary-accounting-0005` | **受取手形及び売掛金**<br><code>うけとりてがたおよびうりかけきん</code> | Notes and accounts receivable - trade | **REVIEW-C**<br>`CANONICAL_VALUE_REVIEW_REQUIRED` | REVIEW_COMPOSITE_TAXONOMY_LABEL | `[ PENDING ]` |
| `pool-cand-000003` | `jp-canary-accounting-0006` | **受取手形及び売掛金(純額)**<br><code>うけとりてがたおよびうりかけきんじゅんがく</code> | Notes and accounts receivable - trade, net | **REVIEW-C**<br>`CANONICAL_VALUE_REVIEW_REQUIRED` | REVIEW_NET_VALUATION_VARIANT | `[ PENDING ]` |
| `pool-cand-000004` | `jp-canary-accounting-0007` | **売掛金及び契約資産**<br><code>うりかけきんおよびけいやくしさん</code> | Accounts receivable - trade, and contract assets | **REVIEW-C**<br>`CANONICAL_VALUE_REVIEW_REQUIRED` | REVIEW_COMPOSITE_TAXONOMY_LABEL | `[ PENDING ]` |
| `pool-cand-000005` | `jp-canary-accounting-0008` | **売掛金及び契約資産(純額)**<br><code>うりかけきんおよびけいやくしさんじゅんがく</code> | Accounts receivable - trade, and contract assets, net | **REVIEW-C**<br>`CANONICAL_VALUE_REVIEW_REQUIRED` | REVIEW_NET_VALUATION_VARIANT | `[ PENDING ]` |
| `pool-cand-000006` | `jp-canary-accounting-0009` | **受取手形(純額)**<br><code>うけとりてがたじゅんがく</code> | Notes receivable - trade, net | **REVIEW-C**<br>`CANONICAL_VALUE_REVIEW_REQUIRED` | REVIEW_NET_VALUATION_VARIANT | `[ PENDING ]` |
| `pool-cand-000007` | `jp-canary-accounting-0010` | **売掛金(純額)**<br><code>うりかけきんじゅんがく</code> | Accounts receivable - trade, net | **REVIEW-C**<br>`CANONICAL_VALUE_REVIEW_REQUIRED` | REVIEW_NET_VALUATION_VARIANT | `[ PENDING ]` |
| `pool-cand-000009` | `jp-canary-accounting-0012` | **契約資産(純額)**<br><code>けいやくしさんじゅんがく</code> | Contract assets, net | **REVIEW-C**<br>`CANONICAL_VALUE_REVIEW_REQUIRED` | REVIEW_NET_VALUATION_VARIANT | `[ PENDING ]` |
| `pool-cand-000015` | `jp-canary-accounting-0018` | **加盟店貸勘定**<br><code>かめいてんたいかんじょう</code><br>*(Corr: <code>かめいてんかしかんじょう</code>)* | Accounts receivable - due from franchised stores | **REVIEW-C**<br>`READING_REVIEW_REQUIRED` | REVISE_READING | `[ PENDING ]` |
| `pool-cand-001625` | `jp-canary-accounting-0001` | **収益認識**<br><code>しゅうえきにんしき</code> | Financial Accounting<br>*(Sug: Revenue recognition)* | **REVIEW-B**<br>`GLOSS_REVIEW_REQUIRED` | REVISE_GLOSS | `[ PENDING ]` |
| `pool-cand-000008` | `jp-canary-accounting-0011` | **契約資産**<br><code>けいやくしさん</code> | Contract assets | **REVIEW-A** | APPROVE_AS_IS | `[ PENDING ]` |
| `pool-cand-000010` | `jp-canary-accounting-0013` | **関係会社売掛金**<br><code>かんけいがいしゃうりかけきん</code> | Accounts receivable from subsidiaries and associates - trade | **REVIEW-A** | APPROVE_AS_IS | `[ PENDING ]` |
| `pool-cand-000011` | `jp-canary-accounting-0014` | **割賦売掛金**<br><code>かっぷうりかけきん</code> | Accounts receivable - installment | **REVIEW-A** | APPROVE_AS_IS | `[ PENDING ]` |
| `pool-cand-000012` | `jp-canary-accounting-0015` | **開発事業未収入金**<br><code>かいはつじぎょうみしゅうにゅうきん</code> | Accounts receivable - development business | **REVIEW-A** | APPROVE_AS_IS | `[ PENDING ]` |
| `pool-cand-000013` | `jp-canary-accounting-0016` | **不動産事業未収入金**<br><code>ふどうさんじぎょうみしゅうにゅうきん</code> | Accounts receivable - real estate business | **REVIEW-A** | APPROVE_AS_IS | `[ PENDING ]` |
| `pool-cand-000014` | `jp-canary-accounting-0017` | **完成業務未収入金**<br><code>かんせいぎょうむみしゅうにゅうきん</code> | Accounts receivable - completed service contracts | **REVIEW-A** | APPROVE_AS_IS | `[ PENDING ]` |
| `pool-cand-000860` | `jp-canary-accounting-0002` | **剰余金の配当**<br><code>じょうよきんのはいとう</code> | Dividends of surplus | **REVIEW-A** | APPROVE_AS_IS | `[ PENDING ]` |
| `pool-cand-000903` | `jp-canary-accounting-0003` | **減資**<br><code>げんし</code> | Capital reduction | **REVIEW-A** | APPROVE_AS_IS | `[ PENDING ]` |

### Section 2: Domain `finance` (18 Candidates)

| ID | Proposed Canonical ID | Surface / Reading | English Meaning & Suggestion | Complexity & Flags | AI Suggestion | Human Decision |
|:---|:---|:---|:---|:---|:---|:---:|
| `pool-cand-001318` | `jp-canary-finance-0003` | **コールローン及び買入手形**<br><code>こーるろーんおよびかいいれてがた</code> | Call loans and bills bought | **REVIEW-C**<br>`CANONICAL_VALUE_REVIEW_REQUIRED` | REVIEW_COMPOSITE_TAXONOMY_LABEL | `[ PENDING ]` |
| `pool-cand-001321` | `jp-canary-finance-0006` | **買現先勘定**<br><code>ばいげんさきかんじょう</code><br>*(Corr: <code>かいげんさきかんじょう</code>)* | Securities purchased under resale agreements | **REVIEW-C**<br>`READING_REVIEW_REQUIRED` | REVISE_READING | `[ PENDING ]` |
| `pool-cand-001333` | `jp-canary-finance-0018` | **貸出金**<br><code>たいしゅつきん</code><br>*(Corr: <code>かしだしきん</code>)* | Loans and bills discounted | **REVIEW-C**<br>`READING_REVIEW_REQUIRED` | REVISE_READING | `[ PENDING ]` |
| `pool-cand-001316` | `jp-canary-finance-0001` | **現金預け金**<br><code>げんきんあずけきん</code> | Cash and due from banks | **REVIEW-A** | APPROVE_AS_IS | `[ PENDING ]` |
| `pool-cand-001317` | `jp-canary-finance-0002` | **現金**<br><code>げんきん</code> | Cash | **REVIEW-A** | APPROVE_AS_IS | `[ PENDING ]` |
| `pool-cand-001319` | `jp-canary-finance-0004` | **コールローン**<br><code>こーるろーん</code> | Call loans | **REVIEW-A** | APPROVE_AS_IS | `[ PENDING ]` |
| `pool-cand-001320` | `jp-canary-finance-0005` | **買入手形**<br><code>かいいれてがた</code> | Bills bought | **REVIEW-A** | APPROVE_AS_IS | `[ PENDING ]` |
| `pool-cand-001322` | `jp-canary-finance-0007` | **債券貸借取引支払保証金**<br><code>さいけんたいしゃくとりひきしはらいほしょうきん</code> | Cash collateral provided for securities borrowed | **REVIEW-A** | APPROVE_AS_IS | `[ PENDING ]` |
| `pool-cand-001323` | `jp-canary-finance-0008` | **買入金銭債権**<br><code>かいいれきんせんさいけん</code> | Monetary claims bought | **REVIEW-A** | APPROVE_AS_IS | `[ PENDING ]` |
| `pool-cand-001324` | `jp-canary-finance-0009` | **商品有価証券**<br><code>しょうひんゆうかしょうけん</code> | Trading securities | **REVIEW-A** | APPROVE_AS_IS | `[ PENDING ]` |
| `pool-cand-001325` | `jp-canary-finance-0010` | **商品国債**<br><code>しょうひんこくさい</code> | Trading government bonds | **REVIEW-A** | APPROVE_AS_IS | `[ PENDING ]` |
| `pool-cand-001326` | `jp-canary-finance-0011` | **商品地方債**<br><code>しょうひんちほうさい</code> | Trading local government bonds | **REVIEW-A** | APPROVE_AS_IS | `[ PENDING ]` |
| `pool-cand-001327` | `jp-canary-finance-0012` | **商品政府保証債**<br><code>しょうひんせいふほしょうさい</code> | Trading government guaranteed bonds | **REVIEW-A** | APPROVE_AS_IS | `[ PENDING ]` |
| `pool-cand-001328` | `jp-canary-finance-0013` | **その他の商品有価証券**<br><code>そのほかのしょうひんゆうかしょうけん</code> | Other trading securities | **REVIEW-A** | APPROVE_AS_IS | `[ PENDING ]` |
| `pool-cand-001329` | `jp-canary-finance-0014` | **国債**<br><code>こくさい</code> | Government bonds | **REVIEW-A** | APPROVE_AS_IS | `[ PENDING ]` |
| `pool-cand-001330` | `jp-canary-finance-0015` | **地方債**<br><code>ちほうさい</code> | Local government bonds | **REVIEW-A** | APPROVE_AS_IS | `[ PENDING ]` |
| `pool-cand-001331` | `jp-canary-finance-0016` | **株式**<br><code>かぶしき</code> | Stocks | **REVIEW-A** | APPROVE_AS_IS | `[ PENDING ]` |
| `pool-cand-001332` | `jp-canary-finance-0017` | **その他の証券**<br><code>そのほかのしょうけん</code> | Other securities | **REVIEW-A** | APPROVE_AS_IS | `[ PENDING ]` |

### Section 3: Domain `tax` (17 Candidates)

| ID | Proposed Canonical ID | Surface / Reading | English Meaning & Suggestion | Complexity & Flags | AI Suggestion | Human Decision |
|:---|:---|:---|:---|:---|:---|:---:|
| `pool-cand-001503` | `jp-canary-tax-0004` | **用語一覧**<br><code>ようごいちらん</code> | Tax Filing<br>*(Sug: List of terms (Tax website index heading - candidate for rejection))* | **REVIEW-C**<br>`EXTRACTION_ARTIFACT_FLAG`<br>`GLOSS_REVIEW_REQUIRED` | REJECT_AS_NON_VOCABULARY_ARTIFACT | `[ PENDING ]` |
| `pool-cand-001504` | `jp-canary-tax-0005` | **印基通**<br><code>いんきつう</code> | Tax Filing<br>*(Sug: Basic Circular on Stamp Tax Law (Statutory abbreviation))* | **REVIEW-C**<br>`ABBREVIATION_FLAG`<br>`GLOSS_REVIEW_REQUIRED` | MAP_TO_CANONICAL_FULL_FORM<br>Rel: `ABBREVIATION_OF -> 印紙税法基本通達` | `[ PENDING ]` |
| `pool-cand-001506` | `jp-canary-tax-0007` | **印法**<br><code>いんほう</code> | Tax Filing<br>*(Sug: Stamp Tax Act (Statutory abbreviation))* | **REVIEW-C**<br>`ABBREVIATION_FLAG`<br>`GLOSS_REVIEW_REQUIRED` | MAP_TO_CANONICAL_FULL_FORM<br>Rel: `ABBREVIATION_OF -> 印紙税法` | `[ PENDING ]` |
| `pool-cand-001508` | `jp-canary-tax-0009` | **印法通則**<br><code>いんほうつうそく</code> | Tax Filing<br>*(Sug: General Rules for Application of Taxable Objects in Stamp Tax Act (Statutory abbreviation))* | **REVIEW-C**<br>`ABBREVIATION_FLAG`<br>`GLOSS_REVIEW_REQUIRED` | MAP_TO_CANONICAL_FULL_FORM<br>Rel: `ABBREVIATION_OF -> 印紙税法別表第一課税物件表の適用に関する通則` | `[ PENDING ]` |
| `pool-cand-001509` | `jp-canary-tax-0010` | **印紙税法別表第一課税物件表の適用に関する通則**<br><code>いんしぜいほうべっぴょうだいいっかぜいぶっけんおもてのてきようにかんするつうそく</code><br>*(Corr: <code>いんしぜいほうべっぴょうだいいっかぜいぶっけんひょうのてきようにかんするつうそく</code>)* | Tax Filing<br>*(Sug: General Rules for Application of Table 1 (Taxable Objects) of Stamp Tax Act)* | **REVIEW-C**<br>`READING_REVIEW_REQUIRED`<br>`GLOSS_REVIEW_REQUIRED` | REVISE_READING | `[ PENDING ]` |
| `pool-cand-001510` | `jp-canary-tax-0011` | **印令**<br><code>いんれい</code> | Tax Filing<br>*(Sug: Order for Enforcement of the Stamp Tax Act (Statutory abbreviation))* | **REVIEW-C**<br>`ABBREVIATION_FLAG`<br>`GLOSS_REVIEW_REQUIRED` | MAP_TO_CANONICAL_FULL_FORM<br>Rel: `ABBREVIATION_OF -> 印紙税法施行令` | `[ PENDING ]` |
| `pool-cand-001512` | `jp-canary-tax-0013` | **オン化省令**<br><code>おんかしょうれい</code> | Tax Filing<br>*(Sug: Ministerial Ordinance for IT Utilization in Tax Procedures (Statutory abbreviation))* | **REVIEW-C**<br>`ABBREVIATION_FLAG`<br>`GLOSS_REVIEW_REQUIRED` | MAP_TO_CANONICAL_FULL_FORM<br>Rel: `ABBREVIATION_OF -> 行政手続等における情報通信の技術の利用に関する法律に基づく国税関係法令に係る情報通信技術を活用した行政の推進等に関する省令` | `[ PENDING ]` |
| `pool-cand-001513` | `jp-canary-tax-0014` | **行審法**<br><code>ぎょうしんほう</code> | Tax Filing<br>*(Sug: Administrative Complaint Review Act (Statutory abbreviation))* | **REVIEW-C**<br>`ABBREVIATION_FLAG`<br>`GLOSS_REVIEW_REQUIRED` | MAP_TO_CANONICAL_FULL_FORM<br>Rel: `ABBREVIATION_OF -> 行政不服審査法` | `[ PENDING ]` |
| `pool-cand-001515` | `jp-canary-tax-0016` | **行訴法**<br><code>ぎょうそほう</code> | Tax Filing<br>*(Sug: Administrative Case Litigation Act (Statutory abbreviation))* | **REVIEW-C**<br>`ABBREVIATION_FLAG`<br>`GLOSS_REVIEW_REQUIRED` | MAP_TO_CANONICAL_FULL_FORM<br>Rel: `ABBREVIATION_OF -> 行政事件訴訟法` | `[ PENDING ]` |
| `pool-cand-001500` | `jp-canary-tax-0001` | **住民税**<br><code>じゅうみんぜい</code> | Local Tax<br>*(Sug: Inhabitant tax / Municipal resident tax)* | **REVIEW-B**<br>`GLOSS_REVIEW_REQUIRED` | REVISE_GLOSS | `[ PENDING ]` |
| `pool-cand-001501` | `jp-canary-tax-0002` | **非課税所得**<br><code>ひかぜいしょとく</code> | Income Tax<br>*(Sug: Tax-exempt income)* | **REVIEW-B**<br>`GLOSS_REVIEW_REQUIRED` | REVISE_GLOSS | `[ PENDING ]` |
| `pool-cand-001502` | `jp-canary-tax-0003` | **適格請求書**<br><code>てきかくせいきゅうしょ</code> | Consumption Tax<br>*(Sug: Qualified invoice (Japanese invoice system))* | **REVIEW-B**<br>`GLOSS_REVIEW_REQUIRED` | REVISE_GLOSS | `[ PENDING ]` |
| `pool-cand-001505` | `jp-canary-tax-0006` | **印紙税法基本通達**<br><code>いんしぜいほうきほんつうたつ</code> | Tax Filing<br>*(Sug: Basic Circular on Stamp Tax Law)* | **REVIEW-B**<br>`GLOSS_REVIEW_REQUIRED` | REVISE_GLOSS | `[ PENDING ]` |
| `pool-cand-001507` | `jp-canary-tax-0008` | **印紙税法**<br><code>いんしぜいほう</code> | Tax Filing<br>*(Sug: Stamp Tax Act)* | **REVIEW-B**<br>`GLOSS_REVIEW_REQUIRED` | REVISE_GLOSS | `[ PENDING ]` |
| `pool-cand-001511` | `jp-canary-tax-0012` | **印紙税法施行令**<br><code>いんしぜいほうしこうれい</code> | Tax Filing<br>*(Sug: Order for Enforcement of the Stamp Tax Act)* | **REVIEW-B**<br>`GLOSS_REVIEW_REQUIRED` | REVISE_GLOSS | `[ PENDING ]` |
| `pool-cand-001514` | `jp-canary-tax-0015` | **行政不服審査法**<br><code>ぎょうせいふふくしんさほう</code> | Tax Filing<br>*(Sug: Administrative Complaint Review Act)* | **REVIEW-B**<br>`GLOSS_REVIEW_REQUIRED` | REVISE_GLOSS | `[ PENDING ]` |
| `pool-cand-001516` | `jp-canary-tax-0017` | **行政事件訴訟法**<br><code>ぎょうせいじけんそしょうほう</code> | Tax Filing<br>*(Sug: Administrative Case Litigation Act)* | **REVIEW-B**<br>`GLOSS_REVIEW_REQUIRED` | REVISE_GLOSS | `[ PENDING ]` |

### Section 4: Domain `hr` (16 Candidates)

| ID | Proposed Canonical ID | Surface / Reading | English Meaning & Suggestion | Complexity & Flags | AI Suggestion | Human Decision |
|:---|:---|:---|:---|:---|:---|:---:|
| `pool-cand-001700` | `jp-canary-hr-0002` | **36協定**<br><code>さぶろくきょうてい</code> | Article 36 Agreement (Overtime work agreement<br>*(Sug: Article 36 Agreement (overtime work agreement))* | **REVIEW-B**<br>`GLOSS_REVIEW_REQUIRED` | REVISE_GLOSS | `[ PENDING ]` |
| `pool-cand-001698` | `jp-canary-hr-0004` | **労働基準法**<br><code>ろうどうきじゅんほう</code> | Labor Standards Act | **REVIEW-A** | APPROVE_AS_IS | `[ PENDING ]` |
| `pool-cand-001699` | `jp-canary-hr-0001` | **労働契約**<br><code>ろうどうけいやく</code> | Labor contract / Employment agreement | **REVIEW-A** | APPROVE_AS_IS | `[ PENDING ]` |
| `pool-cand-001701` | `jp-canary-hr-0005` | **時間外労働**<br><code>じかんがいろうどう</code> | Overtime work | **REVIEW-A** | APPROVE_AS_IS | `[ PENDING ]` |
| `pool-cand-001702` | `jp-canary-hr-0003` | **割増賃金**<br><code>わりましちんぎん</code> | Premium wages / Overtime pay | **REVIEW-A** | APPROVE_AS_IS | `[ PENDING ]` |
| `pool-cand-001703` | `jp-canary-hr-0006` | **年次有給休暇**<br><code>ねんじゆうきゅうきゅうか</code> | Annual paid leave | **REVIEW-A** | APPROVE_AS_IS | `[ PENDING ]` |
| `pool-cand-001704` | `jp-canary-hr-0007` | **解雇予告**<br><code>かいこよこく</code> | Advance notice of dismissal | **REVIEW-A** | APPROVE_AS_IS | `[ PENDING ]` |
| `pool-cand-001705` | `jp-canary-hr-0008` | **解雇予告手当**<br><code>かいこよこくてあて</code> | Allowance in lieu of notice | **REVIEW-A** | APPROVE_AS_IS | `[ PENDING ]` |
| `pool-cand-001706` | `jp-canary-hr-0009` | **標準報酬月額**<br><code>ひょうじゅんほうしゅうげつがく</code> | Standard monthly remuneration | **REVIEW-A** | APPROVE_AS_IS | `[ PENDING ]` |
| `pool-cand-001707` | `jp-canary-hr-0010` | **算定基礎届**<br><code>さんていきそとどけ</code> | Annual wage report for social insurance | **REVIEW-A** | APPROVE_AS_IS | `[ PENDING ]` |
| `pool-cand-001708` | `jp-canary-hr-0011` | **賃金台帳**<br><code>ちんぎんだいちょう</code> | Wage ledger / Payroll register | **REVIEW-A** | APPROVE_AS_IS | `[ PENDING ]` |
| `pool-cand-001709` | `jp-canary-hr-0012` | **出勤簿**<br><code>しゅっきんぼ</code> | Attendance record / Time card | **REVIEW-A** | APPROVE_AS_IS | `[ PENDING ]` |
| `pool-cand-001710` | `jp-canary-hr-0013` | **法定三帳簿**<br><code>ほうていさんちょうぼ</code> | Three statutory labor ledgers | **REVIEW-A** | APPROVE_AS_IS | `[ PENDING ]` |
| `pool-cand-001711` | `jp-canary-hr-0014` | **労働者名簿**<br><code>ろうどうしゃめいぼ</code> | Roster of workers / Employee roster | **REVIEW-A** | APPROVE_AS_IS | `[ PENDING ]` |
| `pool-cand-001712` | `jp-canary-hr-0015` | **定年退職**<br><code>ていねんたいしょく</code> | Mandatory retirement | **REVIEW-A** | APPROVE_AS_IS | `[ PENDING ]` |
| `pool-cand-001713` | `jp-canary-hr-0016` | **最低賃金**<br><code>さいていちんぎん</code> | Minimum wage | **REVIEW-A** | APPROVE_AS_IS | `[ PENDING ]` |

### Section 5: Domain `trade` (13 Candidates)

| ID | Proposed Canonical ID | Surface / Reading | English Meaning & Suggestion | Complexity & Flags | AI Suggestion | Human Decision |
|:---|:---|:---|:---|:---|:---|:---:|
| `pool-cand-001689` | `jp-canary-trade-0005` | **NACCS**<br><code>なっくす</code> | Nippon Automated Cargo and Port Consolidated System<br>*(Sug: Nippon Automated Cargo and Port Consolidated System (Electronic customs clearance system))* | **REVIEW-C**<br>`ABBREVIATION_FLAG`<br>`GLOSS_REVIEW_REQUIRED` | MAP_TO_CANONICAL_FULL_FORM<br>Rel: `ABBREVIATION_OF -> 輸出入・港湾関連情報処理システム` | `[ PENDING ]` |
| `pool-cand-001692` | `jp-canary-trade-0008` | **特定輸出者**<br><code>とくていゆしゅつもの</code><br>*(Corr: <code>とくていゆしゅつしゃ</code>)* | AEO Authorized exporter | **REVIEW-C**<br>`READING_REVIEW_REQUIRED` | REVISE_READING | `[ PENDING ]` |
| `pool-cand-001685` | `jp-canary-trade-0001` | **通関手続**<br><code>つうかんてつづき</code> | Customs clearance<br>*(Sug: Customs clearance procedure)* | **REVIEW-B**<br>`GLOSS_REVIEW_REQUIRED` | REVISE_GLOSS | `[ PENDING ]` |
| `pool-cand-001690` | `jp-canary-trade-0006` | **特恵関税**<br><code>とっけいかんぜい</code> | Generalized System of Preferences (GSP<br>*(Sug: Preferential tariff)* | **REVIEW-B**<br>`GLOSS_REVIEW_REQUIRED` | REVISE_GLOSS | `[ PENDING ]` |
| `pool-cand-001694` | `jp-canary-trade-0010` | **梱包明細書**<br><code>こんぽうめいさいしょ</code> | Packing list | **REVIEW-B** | APPROVE_AS_IS | `[ PENDING ]` |
| `pool-cand-001695` | `jp-canary-trade-0011` | **海上保険証券**<br><code>かいじょうほけんしょうけん</code> | Marine insurance policy | **REVIEW-B** | APPROVE_AS_IS | `[ PENDING ]` |
| `pool-cand-001696` | `jp-canary-trade-0012` | **支払渡し**<br><code>しはらいわたし</code> | Documents against Payment (D/P<br>*(Sug: Documents against Payment (D/P))* | **REVIEW-B**<br>`GLOSS_REVIEW_REQUIRED` | REVISE_GLOSS | `[ PENDING ]` |
| `pool-cand-001697` | `jp-canary-trade-0013` | **引受渡し**<br><code>ひきうけわたし</code> | Documents against Acceptance (D/A<br>*(Sug: Documents against Acceptance (D/A))* | **REVIEW-B**<br>`GLOSS_REVIEW_REQUIRED` | REVISE_GLOSS | `[ PENDING ]` |
| `pool-cand-001686` | `jp-canary-trade-0002` | **関税割当**<br><code>かんぜいわりあて</code> | Tariff quota | **REVIEW-A** | APPROVE_AS_IS | `[ PENDING ]` |
| `pool-cand-001687` | `jp-canary-trade-0003` | **関税減免**<br><code>かんぜいげんめん</code> | Tariff exemption and reduction | **REVIEW-A** | APPROVE_AS_IS | `[ PENDING ]` |
| `pool-cand-001688` | `jp-canary-trade-0004` | **戻し税**<br><code>もどしぜい</code> | Duty drawback | **REVIEW-A** | APPROVE_AS_IS | `[ PENDING ]` |
| `pool-cand-001691` | `jp-canary-trade-0007` | **認定通関業者**<br><code>にんていつうかんぎょうしゃ</code> | AEO Customs broker | **REVIEW-A** | APPROVE_AS_IS | `[ PENDING ]` |
| `pool-cand-001693` | `jp-canary-trade-0009` | **特例輸入者**<br><code>とくれいゆにゅうしゃ</code> | AEO Authorized importer | **REVIEW-A** | APPROVE_AS_IS | `[ PENDING ]` |

### Section 6: Domain `legal` (12 Candidates)

| ID | Proposed Canonical ID | Surface / Reading | English Meaning & Suggestion | Complexity & Flags | AI Suggestion | Human Decision |
|:---|:---|:---|:---|:---|:---|:---:|
| `pool-cand-001721` | `jp-canary-legal-0003` | **資本金の額**<br><code>しほんきんのひたい</code><br>*(Corr: <code>しほんきんのがく</code>)* | Amount of stated capital | **REVIEW-C**<br>`READING_REVIEW_REQUIRED` | REVISE_READING | `[ PENDING ]` |
| `pool-cand-001723` | `jp-canary-legal-0005` | **準備金の額**<br><code>じゅんびきんのひたい</code><br>*(Corr: <code>じゅんびきんのがく</code>)* | Amount of reserves | **REVIEW-C**<br>`READING_REVIEW_REQUIRED` | REVISE_READING | `[ PENDING ]` |
| `pool-cand-001715` | `jp-canary-legal-0001` | **会社法**<br><code>かいしゃほう</code> | Companies Act | **REVIEW-A** | APPROVE_AS_IS | `[ PENDING ]` |
| `pool-cand-001720` | `jp-canary-legal-0002` | **譲渡制限株式**<br><code>じょうとせいげんかぶしき</code> | Shares with transfer restrictions | **REVIEW-A** | APPROVE_AS_IS | `[ PENDING ]` |
| `pool-cand-001722` | `jp-canary-legal-0004` | **増資**<br><code>ぞうし</code> | Capital increase | **REVIEW-A** | APPROVE_AS_IS | `[ PENDING ]` |
| `pool-cand-001724` | `jp-canary-legal-0006` | **株主代表訴訟**<br><code>かぶぬしだいひょうそしょう</code> | Shareholder derivative lawsuit | **REVIEW-A** | APPROVE_AS_IS | `[ PENDING ]` |
| `pool-cand-001725` | `jp-canary-legal-0007` | **組織再編**<br><code>そしきさいへん</code> | Corporate reorganization | **REVIEW-A** | APPROVE_AS_IS | `[ PENDING ]` |
| `pool-cand-001726` | `jp-canary-legal-0008` | **吸収合併**<br><code>きゅうしゅうがっぺい</code> | Absorption-type merger | **REVIEW-A** | APPROVE_AS_IS | `[ PENDING ]` |
| `pool-cand-001727` | `jp-canary-legal-0009` | **新設合併**<br><code>しんせつがっぺい</code> | Consolidation-type merger | **REVIEW-A** | APPROVE_AS_IS | `[ PENDING ]` |
| `pool-cand-001728` | `jp-canary-legal-0010` | **会社分割**<br><code>かいしゃぶんかつ</code> | Company split | **REVIEW-A** | APPROVE_AS_IS | `[ PENDING ]` |
| `pool-cand-001729` | `jp-canary-legal-0011` | **株式交換**<br><code>かぶしきこうかん</code> | Share exchange | **REVIEW-A** | APPROVE_AS_IS | `[ PENDING ]` |
| `pool-cand-001730` | `jp-canary-legal-0012` | **株式移転**<br><code>かぶしきいてん</code> | Share transfer | **REVIEW-A** | APPROVE_AS_IS | `[ PENDING ]` |

### Section 7: Domain `office_communication` (11 Candidates)

| ID | Proposed Canonical ID | Surface / Reading | English Meaning & Suggestion | Complexity & Flags | AI Suggestion | Human Decision |
|:---|:---|:---|:---|:---|:---|:---:|
| `pool-cand-001748` | `jp-canary-office_communication-0004` | **顛末書**<br><code>てんまつかき</code><br>*(Corr: <code>てんまつしょ</code>)* | Incident report / Fact report | **REVIEW-C**<br>`READING_REVIEW_REQUIRED` | REVISE_READING | `[ PENDING ]` |
| `pool-cand-001745` | `jp-canary-office_communication-0001` | **回覧**<br><code>かいらん</code> | Internal circular / Routing memo | **REVIEW-B** | APPROVE_AS_IS | `[ PENDING ]` |
| `pool-cand-001746` | `jp-canary-office_communication-0002` | **議事録**<br><code>ぎじろく</code> | Meeting minutes | **REVIEW-B** | APPROVE_AS_IS | `[ PENDING ]` |
| `pool-cand-001747` | `jp-canary-office_communication-0003` | **始末書**<br><code>しまつしょ</code> | Letter of apology / Written reprimand acknowledgment | **REVIEW-B** | APPROVE_AS_IS | `[ PENDING ]` |
| `pool-cand-001749` | `jp-canary-office_communication-0005` | **送付状**<br><code>そうふじょう</code> | Cover letter / Transmittal letter | **REVIEW-B** | APPROVE_AS_IS | `[ PENDING ]` |
| `pool-cand-001750` | `jp-canary-office_communication-0006` | **添え状**<br><code>そえじょう</code> | Accompanying letter | **REVIEW-B** | APPROVE_AS_IS | `[ PENDING ]` |
| `pool-cand-001751` | `jp-canary-office_communication-0007` | **伝言メモ**<br><code>でんごんめも</code> | Telephone message memo | **REVIEW-B** | APPROVE_AS_IS | `[ PENDING ]` |
| `pool-cand-001752` | `jp-canary-office_communication-0008` | **日報**<br><code>にっぽう</code> | Daily work report | **REVIEW-B** | APPROVE_AS_IS | `[ PENDING ]` |
| `pool-cand-001753` | `jp-canary-office_communication-0009` | **週報**<br><code>しゅうほう</code> | Weekly work report | **REVIEW-B** | APPROVE_AS_IS | `[ PENDING ]` |
| `pool-cand-001754` | `jp-canary-office_communication-0010` | **拝啓**<br><code>はいけい</code> | Dear Sir/Madam (formal opening<br>*(Sug: Dear Sir/Madam (formal opening))* | **REVIEW-B**<br>`GLOSS_REVIEW_REQUIRED` | REVISE_GLOSS | `[ PENDING ]` |
| `pool-cand-001755` | `jp-canary-office_communication-0011` | **敬具**<br><code>けいぐ</code> | Sincerely yours (formal closing<br>*(Sug: Sincerely yours (formal closing))* | **REVIEW-B**<br>`GLOSS_REVIEW_REQUIRED` | REVISE_GLOSS | `[ PENDING ]` |

### Section 8: Domain `business` (6 Candidates)

| ID | Proposed Canonical ID | Surface / Reading | English Meaning & Suggestion | Complexity & Flags | AI Suggestion | Human Decision |
|:---|:---|:---|:---|:---|:---|:---:|
| `pool-cand-001731` | `jp-canary-business-0001` | **事業計画書**<br><code>じぎょうけいかくかき</code><br>*(Corr: <code>じぎょうけいかくしょ</code>)* | Business plan | **REVIEW-C**<br>`READING_REVIEW_REQUIRED` | REVISE_READING | `[ PENDING ]` |
| `pool-cand-001732` | `jp-canary-business-0002` | **事業承継**<br><code>じぎょうしょうけい</code> | Business succession | **REVIEW-B** | APPROVE_AS_IS | `[ PENDING ]` |
| `pool-cand-001733` | `jp-canary-business-0003` | **経営改善計画**<br><code>けいえいかいぜんけいかく</code> | Management improvement plan | **REVIEW-B** | APPROVE_AS_IS | `[ PENDING ]` |
| `pool-cand-001734` | `jp-canary-business-0004` | **補助金申請**<br><code>ほじょきんしんせい</code> | Subsidy application | **REVIEW-B** | APPROVE_AS_IS | `[ PENDING ]` |
| `pool-cand-001735` | `jp-canary-business-0005` | **下請代金支払遅延等防止法**<br><code>したうけだいきんしはらいちえんなどぼうしほう</code> | Subcontract Act | **REVIEW-B** | APPROVE_AS_IS | `[ PENDING ]` |
| `pool-cand-001736` | `jp-canary-business-0006` | **親事業者**<br><code>おやじぎょうしゃ</code> | Main subcontracting enterprise | **REVIEW-B** | APPROVE_AS_IS | `[ PENDING ]` |

### Section 9: Domain `management` (4 Candidates)

| ID | Proposed Canonical ID | Surface / Reading | English Meaning & Suggestion | Complexity & Flags | AI Suggestion | Human Decision |
|:---|:---|:---|:---|:---|:---|:---:|
| `pool-cand-001716` | `jp-canary-management-0001` | **株主総会**<br><code>かぶぬしそうかい</code> | General meeting of shareholders | **REVIEW-A** | APPROVE_AS_IS | `[ PENDING ]` |
| `pool-cand-001717` | `jp-canary-management-0002` | **監査役会**<br><code>かんさやくかい</code> | Board of Corporate Auditors | **REVIEW-A** | APPROVE_AS_IS | `[ PENDING ]` |
| `pool-cand-001718` | `jp-canary-management-0003` | **会計監査人**<br><code>かいけいかんさにん</code> | Accounting Auditor | **REVIEW-A** | APPROVE_AS_IS | `[ PENDING ]` |
| `pool-cand-001719` | `jp-canary-management-0004` | **社外監査役**<br><code>しゃがいかんさやく</code> | Outside Corporate Auditor | **REVIEW-A** | APPROVE_AS_IS | `[ PENDING ]` |

### Section 10: Domain `purchasing` (4 Candidates)

| ID | Proposed Canonical ID | Surface / Reading | English Meaning & Suggestion | Complexity & Flags | AI Suggestion | Human Decision |
|:---|:---|:---|:---|:---|:---|:---:|
| `pool-cand-001739` | `jp-canary-purchasing-0002` | **仕入先選定**<br><code>しいれさきせんてい</code> | Supplier selection | **REVIEW-B** | APPROVE_AS_IS | `[ PENDING ]` |
| `pool-cand-001740` | `jp-canary-purchasing-0003` | **買いたたき**<br><code>かいたたき</code> | Forced price cutting | **REVIEW-B** | APPROVE_AS_IS | `[ PENDING ]` |
| `pool-cand-001741` | `jp-canary-purchasing-0001` | **受領拒否**<br><code>じゅりょうきょひ</code> | Refusal of receipt of ordered goods | **REVIEW-B** | APPROVE_AS_IS | `[ PENDING ]` |
| `pool-cand-001742` | `jp-canary-purchasing-0004` | **返品の禁止**<br><code>へんぴんのきんし</code> | Prohibition of return of goods | **REVIEW-B** | APPROVE_AS_IS | `[ PENDING ]` |

### Section 11: Domain `sales` (1 Candidates)

| ID | Proposed Canonical ID | Surface / Reading | English Meaning & Suggestion | Complexity & Flags | AI Suggestion | Human Decision |
|:---|:---|:---|:---|:---|:---|:---:|
| `pool-cand-001738` | `jp-canary-sales-0001` | **新規開拓**<br><code>しんきかいたく</code> | New customer development | **REVIEW-B** | APPROVE_AS_IS | `[ PENDING ]` |

## 3. Human Review Protocol & Action Guide

To record human decisions, reviewers should specify decisions in a JSONL file:
```json
{"candidate_id": "pool-cand-001625", "decision": "APPROVE", "reviewer": "lead_terminologist", "notes": "Approved with corrected gloss: Revenue recognition"}
{"candidate_id": "pool-cand-001689", "decision": "NEEDS_REVISION", "target_id": "jp-trade-naccs-full", "reviewer": "lead_terminologist", "notes": "Set relationship to ABBREVIATION_OF 輸出入・港湾関連情報処理システム"}
{"candidate_id": "pool-cand-001503", "decision": "REJECT", "reviewer": "lead_terminologist", "notes": "Non-vocabulary tax website index artifact"}
```

Allowed decisions: `APPROVE`, `REJECT`, `NEEDS_REVISION`, `VARIANT_OF`, `DUPLICATE_OF`, `DIFFERENT_SENSE`.