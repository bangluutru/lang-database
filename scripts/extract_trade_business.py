#!/usr/bin/env python3
"""
scripts/extract_trade_business.py
Extracts and structures candidate terms for:
1. Trade / Import-Export / Customs / International Logistics (JETRO-aligned)
2. Business / Office Communication / Contracts / Corporate Governance / Operations
Outputs: data/extracted/trade_business_candidates.jsonl
"""

import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_FILE = BASE_DIR / "data" / "extracted" / "trade_business_candidates.jsonl"

TRADE_TERMS = [
    # Incoterms
    {"term": "FOB", "en": "Free on Board", "sub_cat": "incoterms", "domain": "trade"},
    {"term": "CIF", "en": "Cost, Insurance and Freight", "sub_cat": "incoterms", "domain": "trade"},
    {"term": "DDP", "en": "Delivered Duty Paid", "sub_cat": "incoterms", "domain": "trade"},
    {"term": "EXW", "en": "Ex Works", "sub_cat": "incoterms", "domain": "trade"},
    {"term": "FCA", "en": "Free Carrier", "sub_cat": "incoterms", "domain": "trade"},
    {"term": "CPT", "en": "Carriage Paid To", "sub_cat": "incoterms", "domain": "trade"},
    {"term": "CIP", "en": "Carriage and Insurance Paid To", "sub_cat": "incoterms", "domain": "trade"},
    {"term": "DAP", "en": "Delivered at Place", "sub_cat": "incoterms", "domain": "trade"},
    {"term": "DPU", "en": "Delivered at Place Unloaded", "sub_cat": "incoterms", "domain": "trade"},
    {"term": "CFR", "en": "Cost and Freight", "sub_cat": "incoterms", "domain": "trade"},
    {"term": "FAS", "en": "Free Alongside Ship", "sub_cat": "incoterms", "domain": "trade"},

    # Customs & Clearance
    {"term": "輸入申告", "en": "Import declaration", "sub_cat": "customs", "domain": "trade"},
    {"term": "輸出申告", "en": "Export declaration", "sub_cat": "customs", "domain": "trade"},
    {"term": "通関", "en": "Customs clearance", "sub_cat": "customs", "domain": "trade"},
    {"term": "税関", "en": "Customs office", "sub_cat": "customs", "domain": "trade"},
    {"term": "保税地域", "en": "Bonded area", "sub_cat": "customs", "domain": "trade"},
    {"term": "保税蔵置場", "en": "Bonded warehouse", "sub_cat": "customs", "domain": "trade"},
    {"term": "関税", "en": "Customs duty / tariff", "sub_cat": "customs", "domain": "trade"},
    {"term": "輸入許可", "en": "Import permit", "sub_cat": "customs", "domain": "trade"},
    {"term": "輸出許可", "en": "Export permit", "sub_cat": "customs", "domain": "trade"},
    {"term": "原産地証明書", "en": "Certificate of Origin", "sub_cat": "trade_docs", "domain": "trade"},
    {"term": "船荷証券", "en": "Bill of Lading (B/L)", "sub_cat": "trade_docs", "domain": "trade"},
    {"term": "B/L", "en": "Bill of Lading", "sub_cat": "trade_docs", "domain": "trade"},
    {"term": "信用状", "en": "Letter of Credit (L/C)", "sub_cat": "trade_finance", "domain": "trade"},
    {"term": "L/C", "en": "Letter of Credit", "sub_cat": "trade_finance", "domain": "trade"},
    {"term": "商業送り状", "en": "Commercial Invoice", "sub_cat": "trade_docs", "domain": "trade"},
    {"term": "インボイス", "en": "Invoice", "sub_cat": "trade_docs", "domain": "trade"},
    {"term": "パッキングリスト", "en": "Packing list", "sub_cat": "trade_docs", "domain": "trade"},
    {"term": "荷受人", "en": "Consignee", "sub_cat": "shipping", "domain": "trade"},
    {"term": "荷送人", "en": "Shipper / Consignor", "sub_cat": "shipping", "domain": "trade"},
    {"term": "為替手形", "en": "Bill of exchange", "sub_cat": "trade_finance", "domain": "trade"},
    {"term": "航空貨物運送状", "en": "Air Waybill (AWB)", "sub_cat": "shipping", "domain": "trade"},
    {"term": "フォワーダー", "en": "Freight forwarder", "sub_cat": "logistics", "domain": "trade"},
    {"term": "乙仲", "en": "Customs broker / Forwarding agent", "sub_cat": "customs", "domain": "trade"},
    {"term": "船積み", "en": "Shipment / Loading", "sub_cat": "shipping", "domain": "trade"},
    {"term": "荷役", "en": "Cargo handling / Stevedoring", "sub_cat": "shipping", "domain": "trade"},
    {"term": "海上保険", "en": "Marine insurance", "sub_cat": "trade_insurance", "domain": "trade"},
    {"term": "デマレージ", "en": "Demurrage", "sub_cat": "shipping", "domain": "trade"},
    {"term": "ディテンション", "en": "Detention charge", "sub_cat": "shipping", "domain": "trade"},
    {"term": "コンテナヤード", "en": "Container Yard (CY)", "sub_cat": "logistics", "domain": "trade"},
    {"term": "コンテナフレートステーション", "en": "Container Freight Station (CFS)", "sub_cat": "logistics", "domain": "trade"},
    {"term": "FCL", "en": "Full Container Load", "sub_cat": "logistics", "domain": "trade"},
    {"term": "LCL", "en": "Less than Container Load", "sub_cat": "logistics", "domain": "trade"},
    {"term": "経済連携協定", "en": "Economic Partnership Agreement (EPA)", "sub_cat": "trade_policy", "domain": "trade"},
    {"term": "自由貿易協定", "en": "Free Trade Agreement (FTA)", "sub_cat": "trade_policy", "domain": "trade"},
    {"term": "NACCS", "en": "Nippon Automated Cargo and Port Consolidated System", "sub_cat": "customs_system", "domain": "trade"},
    {"term": "検疫", "en": "Quarantine inspection", "sub_cat": "quarantine", "domain": "trade"},
    {"term": "動植物検疫", "en": "Plant and animal quarantine", "sub_cat": "quarantine", "domain": "trade"},
    {"term": "他法令手続", "en": "Non-customs regulatory procedures", "sub_cat": "customs", "domain": "trade"},
    {"term": "原産地規則", "en": "Rules of origin", "sub_cat": "trade_policy", "domain": "trade"},
    {"term": "関税割当制度", "en": "Tariff quota system", "sub_cat": "customs", "domain": "trade"},
    {"term": "アンチダンピング税", "en": "Anti-dumping duty", "sub_cat": "customs", "domain": "trade"},
    {"term": "為替予約", "en": "Forward exchange contract", "sub_cat": "trade_finance", "domain": "trade"},
    {"term": "電信送金", "en": "Telegraphic Transfer (T/T)", "sub_cat": "trade_finance", "domain": "trade"},
    {"term": "D/P", "en": "Documents against Payment", "sub_cat": "trade_finance", "domain": "trade"},
    {"term": "D/A", "en": "Documents against Acceptance", "sub_cat": "trade_finance", "domain": "trade"},
    {"term": "貿易保険", "en": "Trade insurance", "sub_cat": "trade_insurance", "domain": "trade"},
    {"term": "船荷目録", "en": "Manifest", "sub_cat": "shipping", "domain": "trade"},
    {"term": "外貨建て決済", "en": "Foreign currency settlement", "sub_cat": "trade_finance", "domain": "trade"},
    {"term": "危険負担", "en": "Transfer of risk", "sub_cat": "trade_law", "domain": "trade"},
    {"term": "所有権移転", "en": "Transfer of ownership", "sub_cat": "trade_law", "domain": "trade"},
]

BUSINESS_TERMS = [
    # Workplace Transaction Documents
    {"term": "見積書", "en": "Quotation / Estimate", "sub_cat": "sales_ops", "domain": "business"},
    {"term": "発注書", "en": "Purchase order", "sub_cat": "purchasing", "domain": "business"},
    {"term": "注文請書", "en": "Order acknowledgement", "sub_cat": "sales_ops", "domain": "business"},
    {"term": "納品書", "en": "Delivery note", "sub_cat": "logistics_ops", "domain": "business"},
    {"term": "請求書", "en": "Invoice / Bill", "sub_cat": "finance_ops", "domain": "business"},
    {"term": "領収書", "en": "Receipt", "sub_cat": "accounting_ops", "domain": "business"},
    {"term": "検収", "en": "Inspection and acceptance", "sub_cat": "purchasing", "domain": "business"},
    {"term": "検収書", "en": "Acceptance certificate", "sub_cat": "purchasing", "domain": "business"},
    {"term": "相見積もり", "en": "Competitive bidding / Multiple quotes", "sub_cat": "purchasing", "domain": "business"},
    {"term": "納期", "en": "Delivery deadline / date", "sub_cat": "operations", "domain": "business"},
    {"term": "稟議", "en": "Internal approval request", "sub_cat": "governance", "domain": "business"},
    {"term": "稟議書", "en": "Approval request memo", "sub_cat": "governance", "domain": "business"},
    {"term": "決裁", "en": "Sanction / Final approval", "sub_cat": "governance", "domain": "business"},
    {"term": "押印", "en": "Affixing a seal", "sub_cat": "legal_ops", "domain": "business"},
    {"term": "電子契約", "en": "Electronic contract", "sub_cat": "legal_ops", "domain": "business"},
    {"term": "機密保持契約", "en": "Non-Disclosure Agreement (NDA)", "sub_cat": "contracts", "domain": "business"},
    {"term": "NDA", "en": "Non-Disclosure Agreement", "sub_cat": "contracts", "domain": "business"},
    {"term": "業務委託契約", "en": "Service outsourcing contract", "sub_cat": "contracts", "domain": "business"},
    {"term": "雇用契約", "en": "Employment contract", "sub_cat": "hr_labor", "domain": "business"},
    {"term": "取引基本契約", "en": "Master agreement / Basic transaction contract", "sub_cat": "contracts", "domain": "business"},
    {"term": "覚書", "en": "Memorandum of Understanding (MOU)", "sub_cat": "contracts", "domain": "business"},
    {"term": "立替金", "en": "Advances paid / Out-of-pocket payment", "sub_cat": "accounting_ops", "domain": "business"},
    {"term": "経費精算", "en": "Expense reimbursement / settlement", "sub_cat": "accounting_ops", "domain": "business"},
    {"term": "振込", "en": "Bank transfer", "sub_cat": "banking", "domain": "business"},
    {"term": "振込手数料", "en": "Bank transfer fee", "sub_cat": "banking", "domain": "business"},
    {"term": "口座振替", "en": "Direct debit", "sub_cat": "banking", "domain": "business"},
    {"term": "当座預金", "en": "Current account / Checking account", "sub_cat": "banking", "domain": "business"},
    {"term": "普通預金", "en": "Ordinary savings account", "sub_cat": "banking", "domain": "business"},
    {"term": "小切手", "en": "Check", "sub_cat": "banking", "domain": "business"},
    {"term": "手形割引", "en": "Bill discounting", "sub_cat": "banking", "domain": "business"},
    {"term": "相殺", "en": "Set-off / Offset", "sub_cat": "contracts", "domain": "business"},
    {"term": "連帯保証", "en": "Joint and several guarantee", "sub_cat": "legal", "domain": "business"},
    {"term": "定款", "en": "Articles of incorporation", "sub_cat": "corporate_governance", "domain": "business"},
    {"term": "株主総会", "en": "General meeting of shareholders", "sub_cat": "corporate_governance", "domain": "business"},
    {"term": "取締役会", "en": "Board of directors", "sub_cat": "corporate_governance", "domain": "business"},
    {"term": "登記", "en": "Commercial registration", "sub_cat": "legal", "domain": "business"},
    {"term": "履歴事項全部証明書", "en": "Certificate of full registry records", "sub_cat": "legal", "domain": "business"},
    {"term": "印鑑証明書", "en": "Seal registration certificate", "sub_cat": "legal", "domain": "business"},
    {"term": "委任状", "en": "Power of attorney", "sub_cat": "legal", "domain": "business"},
    {"term": "損害賠償", "en": "Compensation for damages", "sub_cat": "legal", "domain": "business"},
    {"term": "免責条項", "en": "Disclaimer / Limitation of liability clause", "sub_cat": "contracts", "domain": "business"},
    {"term": "管轄裁判所", "en": "Court of competent jurisdiction", "sub_cat": "contracts", "domain": "business"},
    {"term": "就業規則", "en": "Work regulations / Employment rules", "sub_cat": "hr_labor", "domain": "business"},
    {"term": "労働基準法", "en": "Labor Standards Act", "sub_cat": "hr_labor", "domain": "business"},
    {"term": "有給休暇", "en": "Paid annual leave", "sub_cat": "hr_labor", "domain": "business"},
    {"term": "残業手当", "en": "Overtime allowance", "sub_cat": "hr_labor", "domain": "business"},
    {"term": "36協定", "en": "Article 36 Agreement (Overtime pact)", "sub_cat": "hr_labor", "domain": "business"},
    {"term": "社会保険", "en": "Social insurance", "sub_cat": "hr_labor", "domain": "business"},
    {"term": "雇用保険", "en": "Employment insurance", "sub_cat": "hr_labor", "domain": "business"},
    {"term": "労災保険", "en": "Workers' compensation insurance", "sub_cat": "hr_labor", "domain": "business"},
    {"term": "厚生年金", "en": "Employees' Pension Insurance", "sub_cat": "hr_labor", "domain": "business"},
    {"term": "住民税特別徴収", "en": "Special collection of residence tax", "sub_cat": "hr_labor", "domain": "business"},
    {"term": "給与明細", "en": "Pay slip", "sub_cat": "hr_labor", "domain": "business"},
    {"term": "賞与", "en": "Bonus", "sub_cat": "hr_labor", "domain": "business"},
    {"term": "試用期間", "en": "Probationary period", "sub_cat": "hr_labor", "domain": "business"},
    {"term": "解雇予告", "en": "Notice of dismissal", "sub_cat": "hr_labor", "domain": "business"},
]


def extract_trade_business():
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    print("[*] Extracting Trade and Business candidates ...")

    candidates = []
    seen = set()

    for item in TRADE_TERMS:
        t = item["term"]
        if t not in seen:
            seen.add(t)
            candidates.append({
                "source_id": "jetro_trade",
                "source_term_exact": t,
                "surface_candidate": t,
                "official_en": item["en"],
                "sub_category": item["sub_cat"],
                "category": "trade"
            })

    for item in BUSINESS_TERMS:
        t = item["term"]
        if t not in seen:
            seen.add(t)
            candidates.append({
                "source_id": "workplace_standards",
                "source_term_exact": t,
                "surface_candidate": t,
                "official_en": item["en"],
                "sub_category": item["sub_cat"],
                "category": "business"
            })

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for c in candidates:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")

    print(f"[+] Successfully extracted {len(candidates)} Trade & Business candidates to {OUTPUT_FILE.relative_to(BASE_DIR)}")


if __name__ == "__main__":
    extract_trade_business()
