"""
scripts/pilot_builder/semantic_classes.py
Refined linguistic ontology mapping terms to explicit semantic classes and authentic professional collocations.
Outputs candidate collocations with status="generated" and generation_method="semantic_frame".
Builder NEVER self-certifies or marks collocations as verified.
"""

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
    # 32. Business Procedures & Accounting Operations (e.g. 棚卸し, 決算処理, 仕訳)
    "procedure": [
        ("進める", "を", "proceed with procedure"),
        ("完了する", "を", "complete procedure"),
        ("手順を確認する", "の", "confirm operating steps of procedure"),
        ("見直す", "を", "review/streamline procedure")
    ]
}


def classify_semantic_type(surface: str, domain: str) -> str:
    """
    Classifies a term into a fine-grained semantic class to guarantee natural collocation
    and prevent template hallucinations.
    """
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
