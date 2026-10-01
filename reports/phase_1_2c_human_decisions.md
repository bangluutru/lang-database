# Phase 1.2C — Human Review Decisions Report

**Review Authority:** `repository-owner-approved`  
**Review Method:** `LLM-assisted human-authorized review`  
**Reviewer:** `authorized-human-review`  
**Evaluated At:** `2026-10-01T07:36:43Z`  

## Decision Disposition Summary

| Category | Disposition | Count | Destination |
|---|---|:---:|---|
| Approved Unchanged | `APPROVE` | **77** | Canonical Canary Vocabulary |
| Approved With Revision | `APPROVE_WITH_REVISION` | **25** | Revalidation -> Canonical Canary Vocabulary |
| Statutory / Industry Abbreviations | `ABBREVIATION_OF` | **8** | Canary Relationships Metadata |
| Rejected Extraction Artifacts | `REJECT` (artifact) | **1** | Quarantined / Audit Log |
| Rejected Composite Taxonomy Labels | `REJECT` (composite) | **9** | Source Evidence Staging / Audit Log |
| Unresolved / Pending | `PENDING` | **0** | None |
| **Total Evaluated** | | **120** | |

**Canonical Canary Candidates Promoted:** **`102`**  

## Authorized Review Decisions by Domain

| Candidate ID | Surface | Domain | Decision | Reading | Meaning Gloss | Relationship / Notes |
|---|---|---|---|---|---|---|
| `pool-cand-000001` | **受取手形、売掛金及び契約資産** | `accounting` | `REJECT` | `うけとりてがたうりかけきんおよびけいやくしさん` | Notes and accounts receivable - trade, and contract assets | COMPOSITE_REPORTING_TAXONOMY_LABEL |
| `pool-cand-000002` | **受取手形及び売掛金** | `accounting` | `REJECT` | `うけとりてがたおよびうりかけきん` | Notes and accounts receivable - trade | COMPOSITE_REPORTING_TAXONOMY_LABEL |
| `pool-cand-000003` | **受取手形及び売掛金(純額)** | `accounting` | `REJECT` | `うけとりてがたおよびうりかけきんじゅんがく` | Notes and accounts receivable - trade, net | COMPOSITE_REPORTING_TAXONOMY_LABEL |
| `pool-cand-000004` | **売掛金及び契約資産** | `accounting` | `REJECT` | `うりかけきんおよびけいやくしさん` | Accounts receivable - trade, and contract assets | COMPOSITE_REPORTING_TAXONOMY_LABEL |
| `pool-cand-000005` | **売掛金及び契約資産(純額)** | `accounting` | `REJECT` | `うりかけきんおよびけいやくしさんじゅんがく` | Accounts receivable - trade, and contract assets, net | COMPOSITE_REPORTING_TAXONOMY_LABEL |
| `pool-cand-000006` | **受取手形(純額)** | `accounting` | `REJECT` | `うけとりてがたじゅんがく` | Notes receivable - trade, net | COMPOSITE_REPORTING_TAXONOMY_LABEL |
| `pool-cand-000007` | **売掛金(純額)** | `accounting` | `REJECT` | `うりかけきんじゅんがく` | Accounts receivable - trade, net | COMPOSITE_REPORTING_TAXONOMY_LABEL |
| `pool-cand-000009` | **契約資産(純額)** | `accounting` | `REJECT` | `けいやくしさんじゅんがく` | Contract assets, net | COMPOSITE_REPORTING_TAXONOMY_LABEL |
| `pool-cand-000015` | **加盟店貸勘定** | `accounting` | `APPROVE_WITH_REVISION` | `かめいてんかしかんじょう` | Accounts receivable - due from franchised stores | READING_CORRECTION |
| `pool-cand-001625` | **収益認識** | `accounting` | `APPROVE_WITH_REVISION` | `しゅうえきにんしき` | Revenue recognition | GLOSS_CORRECTION |
| `pool-cand-000008` | **契約資産** | `accounting` | `APPROVE` | `けいやくしさん` | Contract assets | VALID_INDEPENDENT_PROFESSIONAL_CONCEPT |
| `pool-cand-000010` | **関係会社売掛金** | `accounting` | `APPROVE` | `かんけいがいしゃうりかけきん` | Accounts receivable from subsidiaries and associates - trade | VALID_INDEPENDENT_PROFESSIONAL_CONCEPT |
| `pool-cand-000011` | **割賦売掛金** | `accounting` | `APPROVE` | `かっぷうりかけきん` | Accounts receivable - installment | VALID_INDEPENDENT_PROFESSIONAL_CONCEPT |
| `pool-cand-000012` | **開発事業未収入金** | `accounting` | `APPROVE` | `かいはつじぎょうみしゅうにゅうきん` | Accounts receivable - development business | VALID_INDEPENDENT_PROFESSIONAL_CONCEPT |
| `pool-cand-000013` | **不動産事業未収入金** | `accounting` | `APPROVE` | `ふどうさんじぎょうみしゅうにゅうきん` | Accounts receivable - real estate business | VALID_INDEPENDENT_PROFESSIONAL_CONCEPT |
| `pool-cand-000014` | **完成業務未収入金** | `accounting` | `APPROVE` | `かんせいぎょうむみしゅうにゅうきん` | Accounts receivable - completed service contracts | VALID_INDEPENDENT_PROFESSIONAL_CONCEPT |
| `pool-cand-000860` | **剰余金の配当** | `accounting` | `APPROVE` | `じょうよきんのはいとう` | Dividends of surplus | VALID_INDEPENDENT_PROFESSIONAL_CONCEPT |
| `pool-cand-000903` | **減資** | `accounting` | `APPROVE` | `げんし` | Capital reduction | VALID_INDEPENDENT_PROFESSIONAL_CONCEPT |
| `pool-cand-001318` | **コールローン及び買入手形** | `finance` | `REJECT` | `こーるろーんおよびかいいれてがた` | Call loans and bills bought | COMPOSITE_REPORTING_TAXONOMY_LABEL |
| `pool-cand-001321` | **買現先勘定** | `finance` | `APPROVE_WITH_REVISION` | `かいげんさきかんじょう` | Securities purchased under resale agreements | READING_CORRECTION |
| `pool-cand-001333` | **貸出金** | `finance` | `APPROVE_WITH_REVISION` | `かしだしきん` | Loans and bills discounted | READING_CORRECTION |
| `pool-cand-001316` | **現金預け金** | `finance` | `APPROVE` | `げんきんあずけきん` | Cash and due from banks | VALID_INDEPENDENT_PROFESSIONAL_CONCEPT |
| `pool-cand-001317` | **現金** | `finance` | `APPROVE` | `げんきん` | Cash | VALID_INDEPENDENT_PROFESSIONAL_CONCEPT |
| `pool-cand-001319` | **コールローン** | `finance` | `APPROVE` | `こーるろーん` | Call loans | VALID_INDEPENDENT_PROFESSIONAL_CONCEPT |
| `pool-cand-001320` | **買入手形** | `finance` | `APPROVE` | `かいいれてがた` | Bills bought | VALID_INDEPENDENT_PROFESSIONAL_CONCEPT |
| `pool-cand-001322` | **債券貸借取引支払保証金** | `finance` | `APPROVE` | `さいけんたいしゃくとりひきしはらいほしょうきん` | Cash collateral provided for securities borrowed | VALID_INDEPENDENT_PROFESSIONAL_CONCEPT |
| `pool-cand-001323` | **買入金銭債権** | `finance` | `APPROVE` | `かいいれきんせんさいけん` | Monetary claims bought | VALID_INDEPENDENT_PROFESSIONAL_CONCEPT |
| `pool-cand-001324` | **商品有価証券** | `finance` | `APPROVE` | `しょうひんゆうかしょうけん` | Trading securities | VALID_INDEPENDENT_PROFESSIONAL_CONCEPT |
| `pool-cand-001325` | **商品国債** | `finance` | `APPROVE` | `しょうひんこくさい` | Trading government bonds | VALID_INDEPENDENT_PROFESSIONAL_CONCEPT |
| `pool-cand-001326` | **商品地方債** | `finance` | `APPROVE` | `しょうひんちほうさい` | Trading local government bonds | VALID_INDEPENDENT_PROFESSIONAL_CONCEPT |
| `pool-cand-001327` | **商品政府保証債** | `finance` | `APPROVE` | `しょうひんせいふほしょうさい` | Trading government guaranteed bonds | VALID_INDEPENDENT_PROFESSIONAL_CONCEPT |
| `pool-cand-001328` | **その他の商品有価証券** | `finance` | `APPROVE` | `そのほかのしょうひんゆうかしょうけん` | Other trading securities | VALID_INDEPENDENT_PROFESSIONAL_CONCEPT |
| `pool-cand-001329` | **国債** | `finance` | `APPROVE` | `こくさい` | Government bonds | VALID_INDEPENDENT_PROFESSIONAL_CONCEPT |
| `pool-cand-001330` | **地方債** | `finance` | `APPROVE` | `ちほうさい` | Local government bonds | VALID_INDEPENDENT_PROFESSIONAL_CONCEPT |
| `pool-cand-001331` | **株式** | `finance` | `APPROVE` | `かぶしき` | Stocks | VALID_INDEPENDENT_PROFESSIONAL_CONCEPT |
| `pool-cand-001332` | **その他の証券** | `finance` | `APPROVE` | `そのほかのしょうけん` | Other securities | VALID_INDEPENDENT_PROFESSIONAL_CONCEPT |
| `pool-cand-001503` | **用語一覧** | `tax` | `REJECT` | `ようごいちらん` | Tax Filing | NON_VOCABULARY_EXTRACTION_ARTIFACT |
| `pool-cand-001504` | **印基通** | `tax` | `ABBREVIATION_OF` | `いんきつう` | Basic Circular on Stamp Tax Law (Statutory abbreviation) | `ABBREVIATION_OF -> 印紙税法基本通達` |
| `pool-cand-001506` | **印法** | `tax` | `ABBREVIATION_OF` | `いんほう` | Stamp Tax Act (Statutory abbreviation) | `ABBREVIATION_OF -> 印紙税法` |
| `pool-cand-001508` | **印法通則** | `tax` | `ABBREVIATION_OF` | `いんほうつうそく` | General Rules for Application of Taxable Objects in Stamp Tax Act (Statutory abbreviation) | `ABBREVIATION_OF -> 印紙税法別表第一課税物件表の適用に関する通則` |
| `pool-cand-001509` | **印紙税法別表第一課税物件表の適用に関する通則** | `tax` | `APPROVE_WITH_REVISION` | `いんしぜいほうべっぴょうだいいっかぜいぶっけんひょうのてきようにかんするつうそく` | General Rules for Application of Table 1 (Taxable Objects) of Stamp Tax Act | READING_CORRECTION; GLOSS_CORRECTION |
| `pool-cand-001510` | **印令** | `tax` | `ABBREVIATION_OF` | `いんれい` | Order for Enforcement of the Stamp Tax Act (Statutory abbreviation) | `ABBREVIATION_OF -> 印紙税法施行令` |
| `pool-cand-001512` | **オン化省令** | `tax` | `ABBREVIATION_OF` | `おんかしょうれい` | Ministerial Ordinance for IT Utilization in Tax Procedures (Statutory abbreviation) | `ABBREVIATION_OF -> 行政手続等における情報通信の技術の利用に関する法律に基づく国税関係法令に係る情報通信技術を活用した行政の推進等に関する省令` |
| `pool-cand-001513` | **行審法** | `tax` | `ABBREVIATION_OF` | `ぎょうしんほう` | Administrative Complaint Review Act (Statutory abbreviation) | `ABBREVIATION_OF -> 行政不服審査法` |
| `pool-cand-001515` | **行訴法** | `tax` | `ABBREVIATION_OF` | `ぎょうそほう` | Administrative Case Litigation Act (Statutory abbreviation) | `ABBREVIATION_OF -> 行政事件訴訟法` |
| `pool-cand-001500` | **住民税** | `tax` | `APPROVE_WITH_REVISION` | `じゅうみんぜい` | Inhabitant tax / Municipal resident tax | GLOSS_CORRECTION |
| `pool-cand-001501` | **非課税所得** | `tax` | `APPROVE_WITH_REVISION` | `ひかぜいしょとく` | Tax-exempt income | GLOSS_CORRECTION |
| `pool-cand-001502` | **適格請求書** | `tax` | `APPROVE_WITH_REVISION` | `てきかくせいきゅうしょ` | Qualified invoice (Japanese invoice system) | GLOSS_CORRECTION |
| `pool-cand-001505` | **印紙税法基本通達** | `tax` | `APPROVE_WITH_REVISION` | `いんしぜいほうきほんつうたつ` | Basic Circular on Stamp Tax Law | GLOSS_CORRECTION |
| `pool-cand-001507` | **印紙税法** | `tax` | `APPROVE_WITH_REVISION` | `いんしぜいほう` | Stamp Tax Act | GLOSS_CORRECTION |
| `pool-cand-001511` | **印紙税法施行令** | `tax` | `APPROVE_WITH_REVISION` | `いんしぜいほうしこうれい` | Order for Enforcement of the Stamp Tax Act | GLOSS_CORRECTION |
| `pool-cand-001514` | **行政不服審査法** | `tax` | `APPROVE_WITH_REVISION` | `ぎょうせいふふくしんさほう` | Administrative Complaint Review Act | GLOSS_CORRECTION |
| `pool-cand-001516` | **行政事件訴訟法** | `tax` | `APPROVE_WITH_REVISION` | `ぎょうせいじけんそしょうほう` | Administrative Case Litigation Act | GLOSS_CORRECTION |
| `pool-cand-001700` | **36協定** | `hr` | `APPROVE_WITH_REVISION` | `さぶろくきょうてい` | Article 36 Agreement (overtime work agreement) | GLOSS_CORRECTION |
| `pool-cand-001698` | **労働基準法** | `hr` | `APPROVE` | `ろうどうきじゅんほう` | Labor Standards Act | VALID_INDEPENDENT_PROFESSIONAL_CONCEPT |
| `pool-cand-001699` | **労働契約** | `hr` | `APPROVE` | `ろうどうけいやく` | Labor contract / Employment agreement | VALID_INDEPENDENT_PROFESSIONAL_CONCEPT |
| `pool-cand-001701` | **時間外労働** | `hr` | `APPROVE` | `じかんがいろうどう` | Overtime work | VALID_INDEPENDENT_PROFESSIONAL_CONCEPT |
| `pool-cand-001702` | **割増賃金** | `hr` | `APPROVE` | `わりましちんぎん` | Premium wages / Overtime pay | VALID_INDEPENDENT_PROFESSIONAL_CONCEPT |
| `pool-cand-001703` | **年次有給休暇** | `hr` | `APPROVE` | `ねんじゆうきゅうきゅうか` | Annual paid leave | VALID_INDEPENDENT_PROFESSIONAL_CONCEPT |
| `pool-cand-001704` | **解雇予告** | `hr` | `APPROVE` | `かいこよこく` | Advance notice of dismissal | VALID_INDEPENDENT_PROFESSIONAL_CONCEPT |
| `pool-cand-001705` | **解雇予告手当** | `hr` | `APPROVE` | `かいこよこくてあて` | Allowance in lieu of notice | VALID_INDEPENDENT_PROFESSIONAL_CONCEPT |
| `pool-cand-001706` | **標準報酬月額** | `hr` | `APPROVE` | `ひょうじゅんほうしゅうげつがく` | Standard monthly remuneration | VALID_INDEPENDENT_PROFESSIONAL_CONCEPT |
| `pool-cand-001707` | **算定基礎届** | `hr` | `APPROVE` | `さんていきそとどけ` | Annual wage report for social insurance | VALID_INDEPENDENT_PROFESSIONAL_CONCEPT |
| `pool-cand-001708` | **賃金台帳** | `hr` | `APPROVE` | `ちんぎんだいちょう` | Wage ledger / Payroll register | VALID_INDEPENDENT_PROFESSIONAL_CONCEPT |
| `pool-cand-001709` | **出勤簿** | `hr` | `APPROVE` | `しゅっきんぼ` | Attendance record / Time card | VALID_INDEPENDENT_PROFESSIONAL_CONCEPT |
| `pool-cand-001710` | **法定三帳簿** | `hr` | `APPROVE` | `ほうていさんちょうぼ` | Three statutory labor ledgers | VALID_INDEPENDENT_PROFESSIONAL_CONCEPT |
| `pool-cand-001711` | **労働者名簿** | `hr` | `APPROVE` | `ろうどうしゃめいぼ` | Roster of workers / Employee roster | VALID_INDEPENDENT_PROFESSIONAL_CONCEPT |
| `pool-cand-001712` | **定年退職** | `hr` | `APPROVE` | `ていねんたいしょく` | Mandatory retirement | VALID_INDEPENDENT_PROFESSIONAL_CONCEPT |
| `pool-cand-001713` | **最低賃金** | `hr` | `APPROVE` | `さいていちんぎん` | Minimum wage | VALID_INDEPENDENT_PROFESSIONAL_CONCEPT |
| `pool-cand-001689` | **NACCS** | `trade` | `ABBREVIATION_OF` | `なっくす` | Nippon Automated Cargo and Port Consolidated System (Electronic customs clearance system) | `ABBREVIATION_OF -> 輸出入・港湾関連情報処理システム` |
| `pool-cand-001692` | **特定輸出者** | `trade` | `APPROVE_WITH_REVISION` | `とくていゆしゅつしゃ` | AEO Authorized exporter | READING_CORRECTION |
| `pool-cand-001685` | **通関手続** | `trade` | `APPROVE_WITH_REVISION` | `つうかんてつづき` | Customs clearance procedure | GLOSS_CORRECTION |
| `pool-cand-001690` | **特恵関税** | `trade` | `APPROVE_WITH_REVISION` | `とっけいかんぜい` | Preferential tariff | GLOSS_CORRECTION |
| `pool-cand-001694` | **梱包明細書** | `trade` | `APPROVE` | `こんぽうめいさいしょ` | Packing list | VALID_INDEPENDENT_PROFESSIONAL_CONCEPT |
| `pool-cand-001695` | **海上保険証券** | `trade` | `APPROVE` | `かいじょうほけんしょうけん` | Marine insurance policy | VALID_INDEPENDENT_PROFESSIONAL_CONCEPT |
| `pool-cand-001696` | **支払渡し** | `trade` | `APPROVE_WITH_REVISION` | `しはらいわたし` | Documents against Payment (D/P) | GLOSS_CORRECTION |
| `pool-cand-001697` | **引受渡し** | `trade` | `APPROVE_WITH_REVISION` | `ひきうけわたし` | Documents against Acceptance (D/A) | GLOSS_CORRECTION |
| `pool-cand-001686` | **関税割当** | `trade` | `APPROVE` | `かんぜいわりあて` | Tariff quota | VALID_INDEPENDENT_PROFESSIONAL_CONCEPT |
| `pool-cand-001687` | **関税減免** | `trade` | `APPROVE` | `かんぜいげんめん` | Tariff exemption and reduction | VALID_INDEPENDENT_PROFESSIONAL_CONCEPT |
| `pool-cand-001688` | **戻し税** | `trade` | `APPROVE` | `もどしぜい` | Duty drawback | VALID_INDEPENDENT_PROFESSIONAL_CONCEPT |
| `pool-cand-001691` | **認定通関業者** | `trade` | `APPROVE` | `にんていつうかんぎょうしゃ` | AEO Customs broker | VALID_INDEPENDENT_PROFESSIONAL_CONCEPT |
| `pool-cand-001693` | **特例輸入者** | `trade` | `APPROVE` | `とくれいゆにゅうしゃ` | AEO Authorized importer | VALID_INDEPENDENT_PROFESSIONAL_CONCEPT |
| `pool-cand-001721` | **資本金の額** | `legal` | `APPROVE_WITH_REVISION` | `しほんきんのがく` | Amount of stated capital | READING_CORRECTION |
| `pool-cand-001723` | **準備金の額** | `legal` | `APPROVE_WITH_REVISION` | `じゅんびきんのがく` | Amount of reserves | READING_CORRECTION |
| `pool-cand-001715` | **会社法** | `legal` | `APPROVE` | `かいしゃほう` | Companies Act | VALID_INDEPENDENT_PROFESSIONAL_CONCEPT |
| `pool-cand-001720` | **譲渡制限株式** | `legal` | `APPROVE` | `じょうとせいげんかぶしき` | Shares with transfer restrictions | VALID_INDEPENDENT_PROFESSIONAL_CONCEPT |
| `pool-cand-001722` | **増資** | `legal` | `APPROVE` | `ぞうし` | Capital increase | VALID_INDEPENDENT_PROFESSIONAL_CONCEPT |
| `pool-cand-001724` | **株主代表訴訟** | `legal` | `APPROVE` | `かぶぬしだいひょうそしょう` | Shareholder derivative lawsuit | VALID_INDEPENDENT_PROFESSIONAL_CONCEPT |
| `pool-cand-001725` | **組織再編** | `legal` | `APPROVE` | `そしきさいへん` | Corporate reorganization | VALID_INDEPENDENT_PROFESSIONAL_CONCEPT |
| `pool-cand-001726` | **吸収合併** | `legal` | `APPROVE` | `きゅうしゅうがっぺい` | Absorption-type merger | VALID_INDEPENDENT_PROFESSIONAL_CONCEPT |
| `pool-cand-001727` | **新設合併** | `legal` | `APPROVE` | `しんせつがっぺい` | Consolidation-type merger | VALID_INDEPENDENT_PROFESSIONAL_CONCEPT |
| `pool-cand-001728` | **会社分割** | `legal` | `APPROVE` | `かいしゃぶんかつ` | Company split | VALID_INDEPENDENT_PROFESSIONAL_CONCEPT |
| `pool-cand-001729` | **株式交換** | `legal` | `APPROVE` | `かぶしきこうかん` | Share exchange | VALID_INDEPENDENT_PROFESSIONAL_CONCEPT |
| `pool-cand-001730` | **株式移転** | `legal` | `APPROVE` | `かぶしきいてん` | Share transfer | VALID_INDEPENDENT_PROFESSIONAL_CONCEPT |
| `pool-cand-001748` | **顛末書** | `office_communication` | `APPROVE_WITH_REVISION` | `てんまつしょ` | Incident report / Fact report | READING_CORRECTION |
| `pool-cand-001745` | **回覧** | `office_communication` | `APPROVE` | `かいらん` | Internal circular / Routing memo | VALID_INDEPENDENT_PROFESSIONAL_CONCEPT |
| `pool-cand-001746` | **議事録** | `office_communication` | `APPROVE` | `ぎじろく` | Meeting minutes | VALID_INDEPENDENT_PROFESSIONAL_CONCEPT |
| `pool-cand-001747` | **始末書** | `office_communication` | `APPROVE` | `しまつしょ` | Letter of apology / Written reprimand acknowledgment | VALID_INDEPENDENT_PROFESSIONAL_CONCEPT |
| `pool-cand-001749` | **送付状** | `office_communication` | `APPROVE` | `そうふじょう` | Cover letter / Transmittal letter | VALID_INDEPENDENT_PROFESSIONAL_CONCEPT |
| `pool-cand-001750` | **添え状** | `office_communication` | `APPROVE` | `そえじょう` | Accompanying letter | VALID_INDEPENDENT_PROFESSIONAL_CONCEPT |
| `pool-cand-001751` | **伝言メモ** | `office_communication` | `APPROVE` | `でんごんめも` | Telephone message memo | VALID_INDEPENDENT_PROFESSIONAL_CONCEPT |
| `pool-cand-001752` | **日報** | `office_communication` | `APPROVE` | `にっぽう` | Daily work report | VALID_INDEPENDENT_PROFESSIONAL_CONCEPT |
| `pool-cand-001753` | **週報** | `office_communication` | `APPROVE` | `しゅうほう` | Weekly work report | VALID_INDEPENDENT_PROFESSIONAL_CONCEPT |
| `pool-cand-001754` | **拝啓** | `office_communication` | `APPROVE_WITH_REVISION` | `はいけい` | Dear Sir/Madam (formal opening) | GLOSS_CORRECTION |
| `pool-cand-001755` | **敬具** | `office_communication` | `APPROVE_WITH_REVISION` | `けいぐ` | Sincerely yours (formal closing) | GLOSS_CORRECTION |
| `pool-cand-001731` | **事業計画書** | `business` | `APPROVE_WITH_REVISION` | `じぎょうけいかくしょ` | Business plan | READING_CORRECTION |
| `pool-cand-001732` | **事業承継** | `business` | `APPROVE` | `じぎょうしょうけい` | Business succession | VALID_INDEPENDENT_PROFESSIONAL_CONCEPT |
| `pool-cand-001733` | **経営改善計画** | `business` | `APPROVE` | `けいえいかいぜんけいかく` | Management improvement plan | VALID_INDEPENDENT_PROFESSIONAL_CONCEPT |
| `pool-cand-001734` | **補助金申請** | `business` | `APPROVE` | `ほじょきんしんせい` | Subsidy application | VALID_INDEPENDENT_PROFESSIONAL_CONCEPT |
| `pool-cand-001735` | **下請代金支払遅延等防止法** | `business` | `APPROVE` | `したうけだいきんしはらいちえんなどぼうしほう` | Subcontract Act | VALID_INDEPENDENT_PROFESSIONAL_CONCEPT |
| `pool-cand-001736` | **親事業者** | `business` | `APPROVE` | `おやじぎょうしゃ` | Main subcontracting enterprise | VALID_INDEPENDENT_PROFESSIONAL_CONCEPT |
| `pool-cand-001716` | **株主総会** | `management` | `APPROVE` | `かぶぬしそうかい` | General meeting of shareholders | VALID_INDEPENDENT_PROFESSIONAL_CONCEPT |
| `pool-cand-001717` | **監査役会** | `management` | `APPROVE` | `かんさやくかい` | Board of Corporate Auditors | VALID_INDEPENDENT_PROFESSIONAL_CONCEPT |
| `pool-cand-001718` | **会計監査人** | `management` | `APPROVE` | `かいけいかんさにん` | Accounting Auditor | VALID_INDEPENDENT_PROFESSIONAL_CONCEPT |
| `pool-cand-001719` | **社外監査役** | `management` | `APPROVE` | `しゃがいかんさやく` | Outside Corporate Auditor | VALID_INDEPENDENT_PROFESSIONAL_CONCEPT |
| `pool-cand-001739` | **仕入先選定** | `purchasing` | `APPROVE` | `しいれさきせんてい` | Supplier selection | VALID_INDEPENDENT_PROFESSIONAL_CONCEPT |
| `pool-cand-001740` | **買いたたき** | `purchasing` | `APPROVE` | `かいたたき` | Forced price cutting | VALID_INDEPENDENT_PROFESSIONAL_CONCEPT |
| `pool-cand-001741` | **受領拒否** | `purchasing` | `APPROVE` | `じゅりょうきょひ` | Refusal of receipt of ordered goods | VALID_INDEPENDENT_PROFESSIONAL_CONCEPT |
| `pool-cand-001742` | **返品の禁止** | `purchasing` | `APPROVE` | `へんぴんのきんし` | Prohibition of return of goods | VALID_INDEPENDENT_PROFESSIONAL_CONCEPT |
| `pool-cand-001738` | **新規開拓** | `sales` | `APPROVE` | `しんきかいたく` | New customer development | VALID_INDEPENDENT_PROFESSIONAL_CONCEPT |
