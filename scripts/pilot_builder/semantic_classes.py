"""
scripts/pilot_builder/semantic_classes.py
Refined linguistic ontology mapping terms to explicit semantic classes and authentic professional collocations.
Outputs candidate collocations with status="generated" and generation_method="semantic_frame".
Builder NEVER self-certifies or marks collocations as verified.
"""
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
SEMANTIC_AUDIT_FILE = BASE_DIR / "reports" / "semantic_audit_results.json"

AUDITED_SEMANTIC_MAP = {}
if SEMANTIC_AUDIT_FILE.exists():
    try:
        with open(SEMANTIC_AUDIT_FILE, "r", encoding="utf-8") as f:
            _audit_data = json.load(f)
            for _r in _audit_data.get("results", []):
                _aud = _r.get("audit")
                if _aud:
                    AUDITED_SEMANTIC_MAP[_aud["term"]] = _aud["suggested_semantic_class"]
    except Exception:
        pass

SEMANTIC_PREDICATES = {
    # 1. Tax Schemes & Statutory Frameworks (e.g. ふるさと納税, インボイス制度)
    "tax_scheme": [
        ("利用する", "を", "utilize tax scheme"),
        ("適用を受ける", "の", "receive application of tax scheme"),
        ("活用する", "を", "take advantage of tax scheme"),
        ("対象となる", "の", "qualify as eligible under tax scheme")
    ],
    # 2. Executive Compensation & Allowances (e.g. 事前確定届出給与, 定期同額給与)
    "executive_compensation": [
        ("支給する", "を", "pay executive compensation"),
        ("損金算入する", "として", "include in deductible expenses as executive compensation"),
        ("届出書を提出する", "の", "submit statutory notification for executive compensation"),
        ("限度額を改定する", "の", "revise maximum ceiling of executive compensation")
    ],
    # 3. Income Tax Classifications (e.g. 給与所得, 不動産所得, 事業所得)
    "income_classification": [
        ("算出する", "を", "calculate income amount"),
        ("区分する", "に", "classify into statutory income category"),
        ("合算する", "を", "aggregate income for total taxable sum"),
        ("確定申告書に記載する", "を", "report income on statutory tax return")
    ],
    # 4. Tax Accounting & Adjustments (e.g. 益金, 損金, 申告調整, 別表四)
    "taxable_income_element": [
        ("算入する", "に", "include in taxable revenue/deductions"),
        ("不算入とする", "に", "exclude from tax deductions/revenue"),
        ("調整を行う", "の", "perform tax return adjustment on"),
        ("加算する", "に", "add back in tax adjustment schedule")
    ],
    # 5. Tax Loss & Relief (e.g. 繰越欠損金, 欠損金の繰戻し還付)
    "tax_loss": [
        ("繰り越す", "を", "carry forward tax loss"),
        ("控除する", "を", "deduct tax loss against current profits"),
        ("充当する", "に", "apply tax loss against taxable income"),
        ("還付を請求する", "の", "claim statutory refund for tax loss")
    ],
    # 6. Statutory Tax Filing (e.g. 確定申告, 年末調整, 青色申告)
    "tax_filing": [
        ("行う", "を", "perform tax filing"),
        ("提出する", "を", "submit tax return"),
        ("期限", "の", "statutory filing deadline"),
        ("手続きを進める", "の", "proceed with statutory filing procedures")
    ],
    # 7. Tax Deductions (e.g. 配偶者控除, 基礎控除, 医療費控除)
    "tax_deduction": [
        ("適用する", "を", "apply tax deduction"),
        ("受ける", "を", "receive tax deduction"),
        ("上限額を計算する", "の", "calculate ceiling amount of tax deduction"),
        ("要件を満たす", "の", "satisfy statutory criteria for tax deduction")
    ],
    # 8. General Taxes (e.g. 法人税, 消費税, 所得税)
    "tax": [
        ("申告する", "を", "declare tax"),
        ("納付する", "を", "pay tax"),
        ("計算する", "を", "calculate tax"),
        ("課される", "が", "tax is levied")
    ],
    # 9. Equity Valuation & Net Asset Accounts (e.g. その他有価証券評価差額金, 繰延ヘッジ損益)
    "equity_valuation_account": [
        ("純資産の部に計上する", "として", "record in net assets as valuation difference"),
        ("税効果会計を適用する", "に", "apply tax effect accounting to valuation difference"),
        ("洗替処理を行う", "を", "perform reversal accounting on valuation difference"),
        ("期末時価で評価替えする", "を", "revalue at term-end market value")
    ],
    # 10. Tangible Fixed Assets (e.g. 土地, 建物, 機械装置)
    "tangible_fixed_asset": [
        ("取得する", "を", "acquire tangible fixed asset"),
        ("固定資産台帳に登録する", "を", "register in fixed asset ledger"),
        ("保有する", "を", "hold tangible fixed asset"),
        ("除却する", "を", "retire/dispose of tangible fixed asset")
    ],
    # 11. Depreciable Assets (e.g. 減価償却資産, 備品, 車両運搬具)
    "depreciable_asset": [
        ("取得する", "を", "acquire depreciable asset"),
        ("減価償却する", "を", "depreciate asset"),
        ("固定資産台帳に計上する", "を", "record in fixed asset ledger"),
        ("耐用年数", "の", "statutory useful life of asset")
    ],
    # 12. Intangible Assets (e.g. のれん, 特許権, ソフトウェア)
    "intangible_asset": [
        ("無形固定資産として計上する", "を", "record as intangible fixed asset"),
        ("償却する", "を", "amortize intangible asset"),
        ("減損処理を行う", "の", "recognize impairment on intangible asset"),
        ("資産価値を評価する", "の", "evaluate asset value of intangible asset")
    ],
    # 13. Securities & Investments (e.g. 有価証券, 売買目的有価証券, 投資有価証券)
    "securities_investment": [
        ("保有する", "を", "hold investment securities"),
        ("時価評価する", "を", "evaluate securities at fair market value"),
        ("取得する", "を", "acquire investment securities"),
        ("売却益を計上する", "の", "record gain on sale of securities")
    ],
    # 14. Financial Statements & Disclosure (e.g. 貸借対照表, 損益計算書, 有価証券報告書)
    "financial_statement": [
        ("作成する", "を", "prepare financial statement"),
        ("開示する", "を", "disclose financial statement"),
        ("承認する", "を", "approve financial statement"),
        ("分析する", "を", "analyze financial statement")
    ],
    # 15. Financial Accounts (e.g. 売掛金, 買掛金, 未払金, 売上高)
    "account": [
        ("計上する", "を", "recognize account in books"),
        ("残高を確認する", "の", "verify balance of account"),
        ("照合する", "を", "reconcile account"),
        ("精算する", "を", "settle account")
    ],
    # 16. General Liabilities (e.g. 借入金, 社債)
    "liability": [
        ("返済する", "を", "repay liability"),
        ("計上する", "を", "record liability"),
        ("残高を圧縮する", "の", "reduce balance of liability"),
        ("返済期日を管理する", "の", "manage maturity date of liability")
    ],
    # 17. Shipping & Transport Documents (e.g. 船荷証券, B/L, 航空貨物運送状, 貨物受領証, クリーンB/L)
    "shipping_document": [
        ("発行する", "を", "issue shipping document"),
        ("受領する", "を", "receive shipping document"),
        ("提出する", "を", "submit shipping document"),
        ("提示する", "を", "present shipping document")
    ],
    # 18. General Documents & Corporate Notices (e.g. 招集通知, 請求書, 見積書, 議事録, 届出書)
    "document": [
        ("作成する", "を", "prepare document"),
        ("提出する", "を", "submit document"),
        ("発送する", "を", "dispatch/send document"),
        ("受領する", "を", "receive document")
    ],
    # 19. Contracts (e.g. 売買契約, 基本合意書)
    "contract": [
        ("締結する", "を", "execute contract"),
        ("更新する", "を", "renew contract"),
        ("解除する", "を", "terminate contract"),
        ("条項を確認する", "の", "review contract clauses")
    ],
    # 20. Contract Clauses & Legal Provisions
    "contract_clause": [
        ("設ける", "を", "stipulate contract clause"),
        ("違反する", "に", "breach contract clause"),
        ("適用する", "を", "apply contract clause"),
        ("精査する", "を", "thoroughly examine contract clause")
    ],
    # 21. Trade Terms & Incoterms (e.g. FOB, CIF, EXW)
    "trade_term": [
        ("条件で契約する", "の", "contract under trade term condition"),
        ("建値で取引する", "の", "trade based on trade term pricing"),
        ("費用負担を取り決める", "における", "determine cost division under trade term"),
        ("危険移転の時点を確認する", "における", "verify point of risk transfer in trade term")
    ],
    # 22. Customs Procedures & Compliance (e.g. 通関, 他法令確認, 輸出申告, 輸入許可)
    "customs_procedure": [
        ("行う", "を", "conduct customs procedure"),
        ("完了する", "を", "complete customs procedure"),
        ("申請する", "を", "apply for customs clearance/procedure"),
        ("適法性を確認する", "の", "verify legal compliance of customs procedure")
    ],
    # 23. Customs Tariffs & Codes (e.g. 関税, HSコード, 実行関税率)
    "customs_tariff": [
        ("適用する", "を", "apply customs tariff"),
        ("照会する", "を", "inquire tariff code/rate"),
        ("納付する", "を", "pay customs duty"),
        ("分類を確認する", "の", "verify tariff classification")
    ],
    # 24. Trade Finance (e.g. 信用状, L/C, 荷為替手形)
    "trade_finance": [
        ("開設する", "を", "open L/C"),
        ("決済する", "を", "settle documentary bill/L/C"),
        ("提示する", "を", "present trade finance document"),
        ("不一致を解消する", "の", "resolve discrepancy in L/C")
    ],
    # 25. Cargo Operations & Logistics (e.g. バンニング, デバンニング, ラッシング, 荷役)
    "cargo_operation": [
        ("行う", "を", "perform cargo operation"),
        ("完了する", "が", "cargo operation is completed"),
        ("作業手順を確認する", "の", "confirm cargo operating steps"),
        ("安全対策を講じる", "時の", "implement safety measures during cargo operation")
    ],
    # 26. Freight Charges & Maritime Fees (e.g. デマレージ, ディテンション, サーチャージ)
    "freight_charge": [
        ("支払う", "を", "pay freight charge/fee"),
        ("請求する", "を", "invoice charge/fee"),
        ("算出する", "を", "calculate freight charge"),
        ("発生を防ぐ", "の", "prevent occurrence of surcharge/fee")
    ],
    # 27. Logistics Facilities (e.g. 保税蔵置場, コンテナヤード, CFS)
    "logistics_facility": [
        ("搬入する", "に", "move cargo into facility"),
        ("搬出する", "から", "move cargo out of facility"),
        ("保管する", "で", "store cargo in facility"),
        ("許可を取得する", "の", "obtain regulatory permit for facility")
    ],
    # 28. Professional Roles (e.g. 取締役, 監査役, 税理士, 通関士)
    "person_role": [
        ("選任する", "を", "appoint professional role"),
        ("就任する", "に", "assume professional role"),
        ("相談する", "に", "consult with professional role"),
        ("職務を遂行する", "の", "execute duties of professional role")
    ],
    # 29. Corporate Organizations & Bodies (e.g. 取締役会, 株主総会, 税務署)
    "organization": [
        ("開催する", "を", "convene corporate meeting/body"),
        ("決議する", "で", "resolve in board/meeting"),
        ("報告する", "に", "report to authority/board"),
        ("届出書を提出する", "へ", "submit notification to authority")
    ],
    # 30. Business & Financial Metrics (e.g. 自己資本比率, ROA, ROE)
    "metric": [
        ("算出する", "を", "calculate financial/business metric"),
        ("改善する", "を", "improve metric"),
        ("分析する", "を", "analyze metric"),
        ("目標値を設定する", "の", "set target value for metric")
    ],
    # 31. Business Practices & Communication (e.g. 報連相, 相見積もり, 根回し)
    "business_practice": [
        ("徹底する", "を", "strictly enforce business practice"),
        ("行う", "を", "conduct business practice"),
        ("習慣づける", "を", "habitualize business practice"),
        ("重要性を共有する", "の", "share importance of business practice")
    ],
    # 32. Professional Service Firms (e.g. 監査法人, 税理士法人, 法律事務所)
    "professional_service_firm": [
        ("選任する", "を", "appoint professional service firm"),
        ("監査を受ける", "の", "undergo audit by audit firm"),
        ("監査契約を締結する", "と", "conclude audit contract with firm"),
        ("事前相談する", "に", "consult in advance with firm")
    ],
    # 33. Statutory Documents & Formal Slips (e.g. 源泉徴収票, 法定調書合計表, 輸出許可書, 輸入許可書)
    "statutory_document": [
        ("交付する", "を", "issue statutory slip/document"),
        ("提出する", "を", "submit statutory tax/customs document"),
        ("保管する", "を", "retain statutory document for mandatory period"),
        ("記載事項を確認する", "の", "verify required statutory entries on document")
    ],
    # 34. Statutory Laws & Formal Codes (e.g. 租税特別措置法, 食品衛生法, 外為法, 会社法)
    "statutory_law": [
        ("遵守する", "を", "comply with statutory law"),
        ("規定に基づく", "の", "based on provisions of statutory law"),
        ("適用を受ける", "の", "be subject to provisions of statutory law"),
        ("改正内容を確認する", "の", "verify statutory amendment details")
    ],
    # 35. Taxpayer & Business Categories (e.g. 免税事業者, 課税事業者, 適格請求書発行事業者)
    "taxpayer_category": [
        ("該当する", "に", "qualify as / fall under taxpayer category"),
        ("判定する", "を", "assess taxpayer category applicability"),
        ("登録を受ける", "の", "obtain registration under category"),
        ("要件を満たす", "の", "satisfy statutory criteria of category")
    ],
    # 36. Audit Opinions & Reports (e.g. 無限定適正意見, 限定付適正意見)
    "audit_opinion": [
        ("表明する", "を", "express audit opinion"),
        ("受領する", "を", "receive audit opinion from auditor"),
        ("記載する", "を", "state audit opinion in report"),
        ("付される", "が", "audit opinion is attached")
    ],
    # 37. International Cargo & Freight Items (e.g. 外国貨物, 内国貨物, FCL貨物, LCL貨物)
    "cargo": [
        ("搬入する", "を", "bring cargo into bonded area"),
        ("搬出する", "を", "haul cargo out of facility"),
        ("蔵入れする", "を", "place cargo into bonded warehouse"),
        ("検査を受ける", "が", "cargo undergoes customs inspection")
    ],
    # 38. Trade Regulations & Compliance (e.g. キャッチオール規制, リスト規制, 安全保障貿易管理)
    "trade_regulation": [
        ("遵守する", "を", "comply with trade regulation"),
        ("対象となる", "の", "fall subject to trade regulation"),
        ("該非判定を行う", "の", "conduct item classification determination under regulation"),
        ("許可を申請する", "の", "apply for license under trade regulation")
    ],
    # 39. Financial Risks & Market Conditions (e.g. 為替リスク, カントリーリスク, 円高, 円安)
    "financial_risk": [
        ("ヘッジする", "を", "hedge financial/currency risk"),
        ("回避する", "を", "avert financial risk"),
        ("管理する", "を", "manage financial/currency risk"),
        ("分析する", "を", "analyze financial risk exposure")
    ],
    # 40. Business Procedures & Accounting Operations (e.g. 棚卸し, 決算処理, 仕訳)
    "procedure": [
        ("進める", "を", "proceed with procedure"),
        ("完了する", "を", "complete procedure"),
        ("手順を確認する", "の", "confirm operating steps of procedure"),
        ("見直す", "を", "review/streamline procedure")
    ]
}

CLASS_PREDICATE_MAP = {
    # Leave & Attendance
    "attendance_status": [("報告する", "を", "report attendance status"), ("管理する", "を", "manage attendance status"), ("記録する", "を", "record attendance status"), ("減給の対象となる", "の", "subject to pay deduction")],
    "statutory_leave": [("取得する", "を", "take statutory leave"), ("申請する", "を", "apply for statutory leave"), ("認める", "を", "grant statutory leave"), ("期間を延長する", "の", "extend statutory leave period")],
    "employee_benefit": [("取得する", "を", "take leave/benefit"), ("付与する", "を", "grant employee benefit/leave"), ("消化する", "を", "use up accrued leave"), ("申請する", "を", "apply for employee leave/benefit")],
    
    # Social Insurance & Labor
    "social_insurance": [("加入する", "に", "enroll in social insurance"), ("保険料を納付する", "の", "pay social insurance premiums"), ("手続きを行う", "の", "process social insurance procedures"), ("資格を取得する", "の", "acquire qualification for social insurance")],
    "social_insurance_scheme": [("適用する", "を", "apply social insurance scheme"), ("加入する", "に", "enroll in social insurance scheme"), ("保険料を算出する", "の", "calculate premiums for social insurance scheme"), ("届出を提出する", "の", "submit statutory filing for scheme")],
    "statutory_scheme": [("適用する", "を", "apply statutory scheme"), ("手続きを進める", "の", "proceed with scheme procedures"), ("要件を満たす", "の", "satisfy scheme requirements"), ("周知する", "を", "notify employees of statutory scheme")],
    "labor_scheme": [("導入する", "を", "introduce labor scheme"), ("適用する", "を", "apply labor scheme"), ("労使協定を締結する", "に関する", "conclude labor-management agreement regarding scheme"), ("運用を見直す", "の", "review operation of labor scheme")],
    
    # Accounting Methods & Principles
    "accounting_method": [("採用する", "を", "adopt accounting method"), ("適用する", "を", "apply accounting method"), ("変更する", "を", "change accounting method"), ("経理処理を行う", "で", "perform accounting processing under method")],
    "accounting_policy": [("決定する", "を", "determine accounting policy"), ("変更する", "を", "change accounting policy"), ("注記する", "を", "disclose accounting policy in notes"), ("適用する", "を", "apply accounting policy")],
    "accounting_principle": [("遵守する", "を", "adhere to accounting principle"), ("評価する", "を", "evaluate accounting principle compliance"), ("前提とする", "を", "premise on accounting principle"), ("注記を開示する", "に関する", "disclose note regarding accounting principle")],
    "bookkeeping_concept": [("記入する", "に", "enter on bookkeeping side"), ("照合する", "と", "reconcile debit/credit side"), ("集計する", "を", "aggregate debit/credit totals"), ("確認する", "の", "verify bookkeeping entries")],
    
    # Corporate Governance & Meetings
    "corporate_meeting": [("招集する", "を", "convene corporate meeting"), ("開催する", "を", "hold corporate meeting"), ("決議する", "で", "pass resolution in meeting"), ("議事録を作成する", "の", "prepare minutes of meeting")],
    "corporate_governance": [("強化する", "を", "strengthen corporate governance"), ("推進する", "を", "promote corporate governance"), ("方針を策定する", "の", "formulate corporate governance policy"), ("体制を構築する", "の", "establish governance framework")],
    "governance_framework": [("構築する", "を", "establish governance framework"), ("運用する", "を", "operate governance framework"), ("評価する", "を", "evaluate governance framework"), ("改善する", "を", "improve governance framework")],
    "compliance_system": [("整備する", "を", "establish compliance system"), ("運用する", "を", "operate compliance system"), ("通報を受ける", "を通じて", "receive reports through compliance hotline"), ("周知徹底する", "を", "thoroughly communicate compliance system")],
    
    # Legal Obligations & Rights
    "legal_obligation": [("遵守する", "を", "comply with legal obligation"), ("果たす", "を", "fulfill legal obligation"), ("負う", "を", "bear legal obligation"), ("違反する", "に", "breach legal obligation")],
    "legal_right": [("行使する", "を", "exercise legal right"), ("有する", "を", "possess legal right"), ("放棄する", "を", "waive legal right"), ("確認する", "の有無を", "confirm existence of legal right")],
    "legal_concept": [("確認する", "を", "confirm legal concept/status"), ("発生を防ぐ", "の", "prevent occurrence of legal event"), ("通知する", "を", "notify of legal event"), ("責任を追及する", "の", "pursue liability for legal event")],
    "contractual_relationship": [("明確にする", "を", "clarify contractual relationship"), ("確認する", "を", "confirm contractual relationship"), ("見直す", "を", "review contractual relationship"), ("合意する", "について", "agree on contractual relationship")],
    
    # Logistics, Transport, Maritime
    "transport_means": [("手配する", "を", "arrange transport vessel/vehicle"), ("運航する", "を", "operate transport vessel"), ("積載する", "に", "load onto vessel"), ("入港を確認する", "の", "confirm port arrival of vessel")],
    "transport_equipment": [("手配する", "を", "arrange transport vessel/equipment"), ("チャーターする", "を", "charter bulk vessel/equipment"), ("荷役を行う", "で", "perform cargo loading on vessel"), ("積載能力を確認する", "の", "verify loading capacity of transport equipment")],
    "logistics_equipment": [("手配する", "を", "arrange logistics container/equipment"), ("積み込む", "に", "load into container/equipment"), ("温度を管理する", "の", "control temperature of container"), ("返却する", "を", "return container/equipment")],
    "logistics_location": [("指定する", "を", "designate logistics destination"), ("変更する", "を", "change logistics destination"), ("確認する", "を", "confirm logistics destination"), ("到着する", "に", "arrive at logistics destination")],
    "logistics_network": [("最適化する", "を", "optimize logistics network/supply chain"), ("構築する", "を", "build supply chain/network"), ("見直す", "を", "review logistics network"), ("寸断を防ぐ", "の", "prevent disruption of supply chain")],
    "maritime_loss": [("宣言する", "を", "declare general average loss"), ("分担する", "を", "apportion maritime loss"), ("算定する", "を", "calculate maritime loss"), ("補償を請求する", "の", "claim compensation for maritime loss")],
    "marine_loss": [("発生する", "が", "particular average loss occurs"), ("算定する", "を", "calculate marine loss"), ("保険金を請求する", "の", "claim insurance proceeds for marine loss"), ("調査する", "を", "investigate marine loss incident")],
    "cargo_incident": [("防止する", "を", "prevent cargo collapse/incident"), ("発生する", "が", "cargo collapse occurs"), ("損害を確認する", "の", "verify damage from cargo incident"), ("対策を講じる", "に対する", "take measures against cargo incident")],
    "cargo_type": [("手配する", "を", "arrange cargo type (FCL/LCL)"), ("仕分ける", "に", "sort into cargo type"), ("輸送する", "として", "transport as cargo type"), ("運賃を比較する", "の", "compare freight rates by cargo type")],
    
    # Markets & Risks
    "market_condition": [("対応する", "に", "respond to market condition"), ("進行する", "が", "market condition progresses"), ("影響を分析する", "の", "analyze impact of market condition"), ("ヘッジする", "リスクを", "hedge risk against market condition")],
    "risk": [("回避する", "を", "avert risk"), ("分析する", "を", "analyze risk"), ("管理する", "を", "manage risk"), ("特定する", "を", "identify risk")],
    "risk_management": [("強化する", "を", "strengthen risk management/security"), ("推進する", "を", "promote risk management"), ("規程を策定する", "の", "formulate risk management rules"), ("監査を実施する", "の", "conduct risk management audit")],
    
    # Taxes
    "tax_rate": [("適用する", "を", "apply tax rate"), ("乗じる", "を", "multiply by applicable tax rate"), ("確認する", "を", "verify applicable tax rate"), ("改定する", "を", "revise tax rate")],
    "tax_base": [("算出する", "を", "calculate tax base"), ("算定する", "を", "compute tax base"), ("確認する", "を", "verify statutory tax base"), ("控除する", "から", "deduct from tax base")],
    "tax_period": [("判定する", "を", "determine statutory tax period"), ("確認する", "を", "verify statutory tax period"), ("設定する", "を", "establish tax period"), ("基準とする", "を", "use as statutory base period")],
    "tax_classification": [("判定する", "を", "determine tax classification"), ("区分する", "に", "classify under tax classification"), ("確認する", "を", "verify tax classification"), ("処理する", "として", "process under tax classification")],
    "tax_treatment": [("適用する", "を", "apply tax treatment (tax exempt)"), ("判定する", "を", "determine tax treatment applicability"), ("確認する", "を", "verify statutory tax treatment"), ("取り扱う", "として", "treat as tax-exempt")],
    "tax_identifier": [("記載する", "を", "state tax registration number"), ("確認する", "を", "verify tax registration number"), ("通知する", "を", "notify tax registration number"), ("公表サイトで照会する", "を", "lookup registration number on official site")],
    "tax_jurisdiction": [("確認する", "を", "verify competent tax jurisdiction"), ("変更する", "を", "change tax jurisdiction location"), ("届け出る", "を", "register tax jurisdiction"), ("所轄とする", "を", "designate competent tax jurisdiction")],
    "tax_nexus": [("判定する", "の有無を", "determine existence of permanent establishment"), ("確認する", "を", "confirm tax nexus"), ("課税される", "を通じて", "be taxed via permanent establishment"), ("認定される", "と", "be recognized as permanent establishment")],
    "taxable_transaction": [("区分する", "に", "classify into taxable transaction"), ("集計する", "を", "aggregate taxable transactions"), ("判定する", "を", "assess taxable transaction criteria"), ("計上する", "を", "record taxable transaction")],
    "taxable_transaction_type": [("判定する", "を", "assess taxable transaction service type"), ("適用する", "を", "apply taxation to cross-border service"), ("申告する", "を", "declare cross-border digital service"), ("確認する", "を", "confirm statutory service category")],
    "tax_category": [("適用する", "を", "apply withholding tax category"), ("区分する", "に", "classify into tax category"), ("確認する", "を", "verify applicable tax table category"), ("選択する", "を", "select tax withholding column")],
    "statutory_authority": [("行使する", "を", "exercise statutory inspection authority"), ("受ける", "の調査を", "undergo inquiry by statutory authority"), ("対応する", "に", "respond to statutory inquiry"), ("規定に基づく", "の", "based on provisions of statutory authority")],
    
    # Systems & Tools
    "software_system": [("利用する", "を", "use software system/portal"), ("入力する", "に", "input data into software system"), ("作成する", "で", "prepare returns using tax software"), ("送信する", "から", "submit electronically via software system")],
    "information_system": [("利用する", "を", "utilize statutory information system"), ("送信する", "を通じて", "transmit tax returns via e-Tax"), ("申請する", "で", "apply through statutory electronic system"), ("導入する", "を", "implement electronic statutory system")],
    "certification": [("取得する", "を", "obtain privacy/regulatory certification"), ("維持する", "を", "maintain certification compliance"), ("更新する", "を", "renew certification"), ("審査を受ける", "の", "undergo certification review")],
    
    # Payroll & Compensation
    "payroll_allowance": [("支給する", "を", "pay payroll allowance"), ("算出する", "を", "calculate payroll allowance"), ("支給基準を設ける", "の", "establish criteria for payroll allowance"), ("割増賃金を支払う", "として", "pay premium wage as allowance")],
    "compensation": [("支給する", "を", "pay fixed overtime compensation"), ("改定する", "を", "revise fixed compensation amount"), ("超過分を精算する", "の", "settle excess overtime beyond fixed allowance"), ("就業規則に定める", "を", "stipulate compensation in work regulations")],
    "employment_type": [("選択する", "を", "select employment type"), ("転換する", "へ", "convert to standard employment type"), ("確認する", "を", "verify employment type conditions"), ("区分する", "で", "categorize by employment type")],
    
    # Business & Strategy
    "business_strategy": [("策定する", "を", "formulate business strategy"), ("推進する", "を", "promote business strategy"), ("見直す", "を", "review business strategy"), ("実行する", "を", "execute business strategy")],
    "management_strategy": [("推進する", "を", "drive forward management strategy/DX"), ("策定する", "を", "formulate management strategy"), ("導入する", "を", "introduce management transformation"), ("加速させる", "を", "accelerate management strategy")],
    "business_model": [("構築する", "を", "build business model"), ("展開する", "を", "expand business model"), ("見直す", "を", "review business model"), ("加盟する", "に", "join franchise/business model")],
    "business_stage": [("迎える", "を", "reach business stage (seed stage)"), ("移行する", "へ", "transition to next business stage"), ("資金調達を行う", "における", "conduct fundraising in seed stage"), ("支援する", "を", "support startup at business stage")],
    "business_activity": [("推進する", "を", "drive business activity"), ("展開する", "を", "expand market channels"), ("注力する", "に", "focus on channel expansion"), ("支援する", "を", "support business development activity")],
    "business_event": [("防ぐ", "を", "prevent business event (lost order)"), ("分析する", "の要因を", "analyze cause of lost order/event"), ("報告する", "を", "report business loss/event"), ("挽回する", "を", "recover from lost order")],
    "market_segment": [("選定する", "を", "select target market segment"), ("分析する", "を", "analyze target market segment"), ("アプローチする", "に", "approach target market segment"), ("開拓する", "を", "develop market segment")],
    "marketing_activity": [("実施する", "を", "launch marketing campaign"), ("企画する", "を", "plan marketing campaign"), ("効果を検証する", "の", "evaluate effectiveness of marketing campaign"), ("展開する", "を", "deploy marketing campaign")],
    "service": [("提供する", "を", "provide after-sales service"), ("充実させる", "を", "enhance after-sales service quality"), ("対応する", "で", "respond with after-sales service"), ("契約を締結する", "の", "conclude after-sales service agreement")],
    
    # Trade Disputes & Restrictions
    "trade_dispute": [("激化する", "が", "trade friction/dispute intensifies"), ("回避する", "を", "avert trade dispute"), ("協議する", "について", "negotiate regarding trade friction"), ("影響を調査する", "の", "investigate impact of trade dispute")],
    "trade_restriction": [("発動する", "を", "impose trade restrictions/sanctions"), ("遵守する", "を", "comply with international economic sanctions"), ("解除する", "を", "lift trade sanctions"), ("対象となる", "の", "fall subject to trade restrictions")],
    "trade_scheme": [("遵守する", "を", "comply with trade security scheme"), ("運用する", "を", "administer trade control scheme"), ("社内規程を整備する", "の", "establish internal compliance program for scheme"), ("説明会を開催する", "の", "hold explanatory briefing on trade scheme")],
    "regulatory_standard": [("遵守する", "を", "comply with regulatory/audit standard"), ("改定する", "を", "revise regulatory audit standards"), ("準拠する", "に", "conform to statutory regulatory standards"), ("確認する", "を", "verify compliance with regulatory standard")]
}

SEMANTIC_PREDICATES.update(CLASS_PREDICATE_MAP)


def classify_semantic_type(surface: str, domain: str) -> str:
    """
    Classifies a term into a fine-grained semantic class to guarantee natural collocation
    and prevent template hallucinations.
    """
    if surface in AUDITED_SEMANTIC_MAP:
        return AUDITED_SEMANTIC_MAP[surface]

    # 1. Tax Schemes & Statutory Frameworks
    if any(k in surface for k in [
        "ふるさと納税", "インボイス制度", "電子帳簿保存法", "賃上げ促進税制", "研究開発税制",
        "中小企業投資促進税制", "グループ通算制度", "セルフメディケーション税制", "少額減価償却資産の特例",
        "税制", "特例制度", "通算制度"
    ]):
        return "tax_scheme"

    # 2. Executive Compensation & Allowances
    if any(k in surface for k in ["事前確定届出給与", "定期同額給与", "役員給与", "役員報酬", "役員賞与", "専従者給与"]):
        return "executive_compensation"

    # 3. Income Tax Classifications
    if any(k in surface for k in [
        "利子所得", "配当所得", "不動産所得", "事業所得", "給与所得", "退職所得",
        "山林所得", "譲渡所得", "一時所得", "雑所得", "総所得金額", "合計所得金額"
    ]):
        return "income_classification"

    # 4. Tax Accounting & Adjustments
    if any(k in surface for k in ["益金", "損金", "損金算入", "損金不算入", "益金算入", "益金不算入", "申告調整", "別表四", "別表五"]):
        return "taxable_income_element"

    # 5. Tax Loss
    if any(k in surface for k in ["繰越欠損金", "繰戻し還付", "欠損金", "貸倒損失"]):
        return "tax_loss"

    # 6. Statutory Tax Deductions
    if any(k in surface for k in ["控除", "特例"]):
        return "tax_deduction"

    # 7. Statutory Tax Filings
    if any(k in surface for k in ["申告", "年末調整", "決定処分", "更正"]):
        return "tax_filing"

    # 8. General Taxes
    if surface.endswith("税") or any(k in surface for k in ["所得税", "法人税", "消費税", "税額", "加算税", "課税", "印紙税"]):
        return "tax"

    # 9. Equity Valuation & Net Asset Accounts
    if any(k in surface for k in ["その他有価証券評価差額金", "繰延ヘッジ損益", "為替換算調整勘定", "土地再評価差額金", "新株予約権"]):
        return "equity_valuation_account"

    # 10. Tangible Fixed Assets
    if any(k in surface for k in ["土地", "構築物"]):
        return "tangible_fixed_asset"

    # 11. Depreciable Assets
    if any(k in surface for k in ["建物", "機械", "車両", "備品", "器具", "減価償却資産"]):
        return "depreciable_asset"

    # 12. Intangible Assets
    if any(k in surface for k in ["のれん", "特許権", "ソフトウェア", "商標権", "借地権", "無形固定資産"]):
        return "intangible_asset"

    # 13. Securities & Investments
    if any(k in surface for k in ["有価証券", "株式", "国債", "社債", "投資有価証券"]):
        return "securities_investment"

    # 14. Financial Statements
    if any(k in surface for k in ["計算書", "対照表", "財務諸表", "決算短信", "報告書", "明細表"]):
        return "financial_statement"

    # 15. Shipping Documents
    if any(k in surface for k in [
        "船荷証券", "B/L", "Waybill", "AWB", "インボイス", "パッキングリスト", "原産地証明書",
        "指図書", "依頼書", "貨物受領証", "運送状", "荷渡指図書", "到着案内書", "ドックレシート",
        "メイツレシート"
    ]):
        return "shipping_document"

    # 16. Documents & Notices
    if surface.endswith("書") and not any(k in surface for k in ["契約書", "計算書", "報告書"]):
        return "document"
    if any(k in surface for k in [
        "招集通知", "通知書", "見積書", "発注書", "納品書", "請求書", "領収書", "受領書",
        "検収書", "稟議書", "議事録", "伝票", "委任状", "行使書"
    ]):
        return "document"

    # 17. Contracts & Clauses
    if any(k in surface for k in ["契約", "合意書", "覚書", "協定"]):
        return "contract"
    if any(k in surface for k in ["条項", "特約", "免責", "義務", "約款"]):
        return "contract_clause"

    # 18. Trade Terms
    if surface in ["FOB", "CIF", "CFR", "EXW", "FCA", "CPT", "CIP", "DAP", "DPU", "DDP", "FAS", "本船渡し", "工場渡し"] or "インコタームズ" in surface or "建値" in surface:
        return "trade_term"

    # 19. Customs Procedures
    if any(k in surface for k in ["通関", "他法令確認", "輸出申告", "輸入申告", "輸出許可", "輸入許可", "検査"]):
        return "customs_procedure"
    if any(k in surface for k in ["関税", "税率", "HSコード", "品目番号", "原産地規則"]):
        return "customs_tariff"

    # 20. Trade Finance
    if any(k in surface for k in ["信用状", "L/C", "為替手形", "荷為替", "送金", "D/P", "D/A", "手形"]):
        return "trade_finance"

    # 21. Cargo Operations
    if any(k in surface for k in ["バンニング", "デバンニング", "船積み", "陸揚げ", "荷役", "荷崩れ", "ラッシング"]):
        return "cargo_operation"
    if any(k in surface for k in ["運賃", "デマレージ", "ディテンション", "フリータイム", "サーチャージ", "THC", "BAF", "CAF"]):
        return "freight_charge"
    if any(k in surface for k in ["保税", "ヤード", "CFS", "CY", "倉庫", "上屋"]):
        return "logistics_facility"

    # 22. Roles & Organizations
    if any(k in surface for k in [
        "取締役", "監査役", "役員", "税理士", "公認会計士", "通関士", "荷受人", "荷送人",
        "社員", "特定扶養親族", "老人扶養親族"
    ]):
        return "person_role"
    if any(k in surface for k in ["取締役会", "株主総会", "税務署", "国税局", "税関", "会社", "フォワーダー", "船社"]):
        return "organization"

    # 23. Metrics
    if any(k in surface for k in ["比率", "率", "KPI", "LTV", "目標", "利益率", "回転率", "損益分岐点"]):
        return "metric"

    # 24. Liabilities
    if any(k in surface for k in ["借入金", "負債", "預り金", "社債"]):
        return "liability"

    # 25. Accounting Accounts
    if domain == "accounting" and any(k in surface for k in ["金", "料", "費", "高", "益", "損", "利益", "損失", "勘定"]):
        return "account"

    # 26. Business Practices
    if any(k in surface for k in ["相見積もり", "報連相", "根回し", "直行直帰", "朝礼", "会議", "アポイント"]):
        return "business_practice"

    # 27. Fallback to procedure
    if any(k in surface for k in ["処理", "管理", "検収", "精算", "確認", "棚卸"]):
        return "procedure"

    return "account" if domain == "accounting" else "procedure"


def build_semantic_collocations(surface: str, domain: str) -> list:
    """
    Builds collocations using semantic frames.
    All outputs explicitly carry status="generated" and generation_method="semantic_frame".
    """
    sem_class = classify_semantic_type(surface, domain)
    preds = SEMANTIC_PREDICATES.get(sem_class, SEMANTIC_PREDICATES["procedure"])

    collocations = []
    for pred, particle, meaning_en in preds:
        if particle.endswith("で") or particle.endswith("における") or particle.endswith("に基づく") or particle.endswith("として"):
            text = f"{surface}{particle}{pred}"
        elif particle == "の":
            text = f"{surface}の{pred}"
        else:
            text = f"{surface}{particle}{pred}"

        collocations.append({
            "text": text,
            "predicate": pred,
            "particle": particle,
            "semantic_class": sem_class,
            "status": "generated",
            "generation_method": "semantic_frame",
            "register": "professional"
        })
    return collocations
