"""
scripts/pilot_builder/example_generator.py
Semantic-class aware example and dialogue generator for Japanese professional vocabulary.
Generates realistic Japanese workplace sentences tailored to specific semantic categories:
accounting offices, tax filing, shipping, customs clearance, corporate governance,
procurement, contract execution, and logistics operations.
"""

def generate_semantic_examples(surface: str, reading: str, vi_short: str, en_pref: str, domain: str, sem_class: str) -> list:
    """
    Generates realistic, natural workplace examples based on explicit semantic class.
    """
    en_clean = en_pref.lower()
    
    if sem_class == "contract":
        return [
            {
                "ja": f"取引先と基本合意に達したため、来週{surface}を正式に締結いたします。",
                "vi": f"Do đã đạt được thỏa thuận cơ bản với đối tác, tuần tới chúng tôi sẽ chính thức ký kết {vi_short}.",
                "en": f"Having reached a basic agreement with the partner, we will officially execute the {en_clean} next week.",
                "register": "formal_business",
                "status": "candidate"
            },
            {
                "ja": f"法務部門と連携し、{surface}の条項にリスクが含まれていないか事前に精査しました。",
                "vi": f"Phối hợp với bộ phận pháp chế, chúng tôi đã rà soát kỹ trước xem điều khoản {vi_short} có rủi ro nào không.",
                "en": f"In coordination with the legal department, we thoroughly reviewed the clauses of the {en_clean} in advance for any risks.",
                "register": "corporate_governance",
                "status": "candidate"
            }
        ]

    elif sem_class == "shipping_document":
        return [
            {
                "ja": f"輸入貨物の引き取り手続きを行うため、船会社から{surface}の原本を受領しました。",
                "vi": f"Để làm thủ tục nhận hàng nhập khẩu, chúng tôi đã nhận bản gốc {vi_short} từ hãng tàu.",
                "en": f"To process the pickup of imported cargo, we received the original {en_clean} from the shipping line.",
                "register": "logistics_workplace",
                "status": "candidate"
            },
            {
                "ja": f"通関業者へ{surface}を提出し、迅速な輸入申告の手配を依頼しました。",
                "vi": f"Chúng tôi đã nộp {vi_short} cho đại lý hải quan và yêu cầu thu xếp khai báo nhập khẩu nhanh chóng.",
                "en": f"We submitted the {en_clean} to the customs broker and requested prompt arrangements for import declaration.",
                "register": "customs_procedure",
                "status": "candidate"
            }
        ]

    elif sem_class == "trade_term":
        return [
            {
                "ja": f"今回の海上輸送契約は、運賃と危険負担の範囲を明確にするため{surface}条件を採用しました。",
                "vi": f"Hợp đồng vận tải biển lần này áp dụng điều kiện {vi_short} để làm rõ phạm vi chịu cước phí và rủi ro.",
                "en": f"This ocean transport contract adopted {surface} terms to clarify the division of freight costs and risk transfer.",
                "register": "trade_contract",
                "status": "candidate"
            },
            {
                "ja": f"{surface}建値での取引に基づき、仕向港での荷揚げ費用と輸入関税を輸入者側で負担します。",
                "vi": f"Căn cứ giao dịch theo giá {surface}, chi phí dỡ hàng tại cảng đích và thuế nhập khẩu do bên nhập khẩu chịu.",
                "en": f"Based on transactions priced under {surface}, unloading costs at the port of destination and import duties are borne by the importer.",
                "register": "international_trade",
                "status": "candidate"
            }
        ]

    elif sem_class in ["tax", "tax_filing"]:
        return [
            {
                "ja": f"期末決算の確定に伴い、所轄税務署に対して期限内に{surface}の手続きを完了しました。",
                "vi": f"Cùng với việc chốt số liệu quyết toán cuối kỳ, chúng tôi đã hoàn tất thủ tục {vi_short} đúng hạn tại chi cục thuế phụ trách.",
                "en": f"Upon finalizing the fiscal year-end accounts, we completed {vi_short} procedures within the statutory deadline at the competent tax office.",
                "register": "statutory_reporting",
                "status": "candidate"
            },
            {
                "ja": f"顧問税理士の助言を受け、適正な税務処理に基づき{surface}を計算いたしました。",
                "vi": f"Nhận tư vấn từ chuyên viên thuế cố vấn, chúng tôi đã tính toán {vi_short} dựa trên quy định thuế chuẩn xác.",
                "en": f"With advice from our advisory tax accountant, we calculated {en_clean} in accordance with proper tax regulations.",
                "register": "formal_business",
                "status": "candidate"
            }
        ]

    elif sem_class == "tax_deduction":
        return [
            {
                "ja": f"適用要件を慎重に確認した上で、今年度の法人税申告において{surface}を適用しました。",
                "vi": f"Sau khi kiểm tra cẩn thận điều kiện áp dụng, chúng tôi đã áp dụng {vi_short} trong tờ khai thuế thu nhập doanh nghiệp năm nay.",
                "en": f"After carefully verifying the qualifying conditions, we applied the {en_clean} in this fiscal year's corporate tax return.",
                "register": "statutory_reporting",
                "status": "candidate"
            },
            {
                "ja": f"{surface}の適用を受けるため、関係書類を整備して申告書に添付します。",
                "vi": f"Để được hưởng {vi_short}, chúng tôi hoàn thiện các hồ sơ liên quan và đính kèm vào tờ khai thuế.",
                "en": f"In order to qualify for the {en_clean}, we prepared relevant supporting documents and attached them to the tax return.",
                "register": "tax_compliance",
                "status": "candidate"
            }
        ]

    elif sem_class == "asset":
        return [
            {
                "ja": f"事業拡大に伴い、新拠点として{surface}を取得し固定資産台帳に計上しました。",
                "vi": f"Đi cùng với việc mở rộng kinh doanh, chúng tôi đã mua {vi_short} làm cơ sở mới và ghi vào sổ tài sản cố định.",
                "en": f"In line with business expansion, we acquired {en_clean} as a new site and recorded it in the fixed asset register.",
                "register": "corporate_accounting",
                "status": "candidate"
            },
            {
                "ja": f"期末の減損テストを実施し、保有する{surface}の帳簿価額と回収可能価額を比較検証しました。",
                "vi": f"Chúng tôi đã thực hiện kiểm tra giảm giá trị tài sản cuối kỳ, đối chiếu giữa giá trị ghi sổ và giá trị có thể thu hồi của {vi_short}.",
                "en": f"We conducted a year-end impairment test, comparing and validating the book value and recoverable amount of the held {en_clean}.",
                "register": "financial_audit",
                "status": "candidate"
            }
        ]

    elif sem_class == "liability":
        return [
            {
                "ja": f"設備資金の調達を目的として金融機関と借入契約を結び、{surface}を適切に管理しています。",
                "vi": f"Nhằm mục đích huy động vốn mua sắm thiết bị, chúng tôi đã ký hợp đồng vay ngân hàng và quản lý chặt chẽ khoản {vi_short}.",
                "en": f"We entered into a loan agreement with the financial institution to finance equipment capital and are managing {en_clean} appropriately.",
                "register": "corporate_finance",
                "status": "candidate"
            },
            {
                "ja": f"資金繰り計画に基づき、来期に返済期日が到来する{surface}の返済原資を確保しました。",
                "vi": f"Dựa trên kế hoạch dòng tiền, chúng tôi đã đảm bảo nguồn vốn thanh toán cho {vi_short} đến hạn vào kỳ tới.",
                "en": f"Based on the cash flow plan, we secured repayment funds for {en_clean} maturing in the next fiscal term.",
                "register": "treasury_management",
                "status": "candidate"
            }
        ]

    elif sem_class == "person_role":
        return [
            {
                "ja": f"定時株主総会の決議を経て、当社の新任{surface}が正式に選任されました。",
                "vi": f"Thông qua nghị quyết của đại hội đồng cổ đông thường niên, {vi_short} mới của công ty chúng tôi đã được bổ nhiệm chính thức.",
                "en": f"Through the resolution of the annual general shareholders meeting, our new {en_clean} was officially appointed.",
                "register": "corporate_governance",
                "status": "candidate"
            },
            {
                "ja": f"業務執行の監督機能を強化するため、{surface}と定期的な報告連絡会を開催しています。",
                "vi": f"Để tăng cường chức năng giám sát điều hành kinh doanh, chúng tôi tổ chức họp báo cáo định kỳ với {vi_short}.",
                "en": f"To strengthen oversight of business execution, we hold regular reporting sessions with the {en_clean}.",
                "register": "formal_business",
                "status": "candidate"
            }
        ]

    elif sem_class == "organization":
        return [
            {
                "ja": f"重要議案の決議を行うため、来週臨時{surface}を招集する運びとなりました。",
                "vi": f"Để biểu quyết các nghị quyết quan trọng, tuần sau công ty sẽ tiến hành triệu tập cuộc họp {vi_short} bất thường.",
                "en": f"To resolve critical proposals, an extraordinary meeting of the {en_clean} will be convened next week.",
                "register": "corporate_governance",
                "status": "candidate"
            },
            {
                "ja": f"{surface}において今期の経営方針および予算配分案が原案通り可決されました。",
                "vi": f"Tại {vi_short}, phương hướng kinh doanh và phương án phân bổ ngân sách kỳ này đã được thông qua như đề xuất ban đầu.",
                "en": f"At the {en_clean}, this term's management policy and budget allocation proposal were approved as submitted.",
                "register": "formal_business",
                "status": "candidate"
            }
        ]

    elif sem_class == "metric":
        return [
            {
                "ja": f"経営効率の改善に向け、各事業部門で{surface}の数値を月次でモニタリングしています。",
                "vi": f"Hướng tới cải thiện hiệu quả quản lý, các bộ phận kinh doanh đang theo dõi chỉ số {vi_short} hàng tháng.",
                "en": f"Towards improving operational efficiency, each business division monitors {en_clean} metrics on a monthly basis.",
                "register": "performance_management",
                "status": "candidate"
            },
            {
                "ja": f"当期の{surface}は目標値を上回り、収益性の向上が確認されました。",
                "vi": f"Chỉ số {vi_short} kỳ này đã vượt giá trị mục tiêu, xác nhận khả năng sinh lời đã được nâng cao.",
                "en": f"This term's {en_clean} exceeded the target value, confirming an improvement in profitability.",
                "register": "business_analysis",
                "status": "candidate"
            }
        ]

    elif sem_class == "freight_charge":
        return [
            {
                "ja": f"コンテナの搬出がフリータイムを超過したため、船社より{surface}が請求されました。",
                "vi": f"Do việc kéo container ra khỏi bãi vượt quá thời gian miễn phí lưu bãi, hãng tàu đã phát hóa đơn phạt {vi_short}.",
                "en": f"Because container pickup exceeded the free time, the shipping line invoiced {en_clean}.",
                "register": "logistics_workplace",
                "status": "candidate"
            },
            {
                "ja": f"物流コストの抑制を図るため、{surface}の発生防止に向けた運行スケジュールを再調整しました。",
                "vi": f"Nhằm kiềm chế chi phí logistics, chúng tôi đã tái điều chỉnh lịch trình vận hành để ngăn ngừa phát sinh {vi_short}.",
                "en": f"To contain logistics costs, we rescheduled delivery timelines to prevent the occurrence of {en_clean}.",
                "register": "logistics_operations",
                "status": "candidate"
            }
        ]

    elif sem_class == "cargo_operation":
        return [
            {
                "ja": f"貨物の荷崩れを防ぐため、コンテナヤードにて立ち会いのもと{surface}を実施しました。",
                "vi": f"Để tránh hàng hóa bị xô lệch đổ vỡ, chúng tôi đã tiến hành {vi_short} dưới sự giám sát trực tiếp tại bãi container.",
                "en": f"To prevent cargo shifting, we carried out {en_clean} under on-site supervision at the container yard.",
                "register": "logistics_workplace",
                "status": "candidate"
            },
            {
                "ja": f"本船への積載計画に沿って、本日の午後から{surface}の作業を開始します。",
                "vi": f"Theo kế hoạch xếp hàng lên tàu mẹ, chiều nay sẽ bắt đầu tiến hành công việc {vi_short}.",
                "en": f"In accordance with the vessel stowage plan, {en_clean} operations will commence this afternoon.",
                "register": "logistics_operations",
                "status": "candidate"
            }
        ]

    elif sem_class == "business_practice":
        return [
            {
                "ja": f"円滑なプロジェクト推進を図るため、関係部署への事前の{surface}を徹底しています。",
                "vi": f"Nhằm thúc đẩy dự án diễn ra trôi chảy, chúng tôi triệt để thực hiện {vi_short} từ trước với các phòng ban liên quan.",
                "en": f"To facilitate smooth project execution, we thoroughly conduct prior {en_clean} with relevant departments.",
                "register": "japanese_business_culture",
                "status": "candidate"
            },
            {
                "ja": f"業務上のトラブルを未然に防ぐため、迅速な{surface}の習慣付けが求められます。",
                "vi": f"Để ngăn ngừa rủi ro phát sinh trong công việc, việc tạo thói quen {vi_short} nhanh chóng là rất cần thiết.",
                "en": f"To prevent operational issues beforehand, establishing a habit of prompt {en_clean} is required.",
                "register": "workplace_discipline",
                "status": "candidate"
            }
        ]

    elif sem_class == "document":
        return [
            {
                "ja": f"取引先へ提出するため、担当者が速やかに{surface}を作成して押印を依頼しました。",
                "vi": f"Để nộp cho đối tác, người phụ trách đã nhanh chóng soạn thảo {vi_short} và xin đóng dấu.",
                "en": f"To submit to the client, the person in charge promptly drafted the {en_clean} and requested seal affixation.",
                "register": "office_administration",
                "status": "candidate"
            },
            {
                "ja": f"監査証跡として保管するため、受領した{surface}を電子帳簿保存法の要件に従って保存しました。",
                "vi": f"Để lưu trữ làm bằng chứng kiểm toán, chúng tôi đã lưu {vi_short} nhận được theo đúng yêu cầu của Luật Lưu trữ Sổ sách Điện tử.",
                "en": f"To preserve as an audit trail, we archived the received {en_clean} following the requirements of the Electronic Books Preservation Act.",
                "register": "compliance_recordkeeping",
                "status": "candidate"
            }
        ]

    elif sem_class == "financial_statement":
        return [
            {
                "ja": f"公認会計士の監査を経て、取締役会にて今期の{surface}が正式に承認されました。",
                "vi": f"Sau khi có kiểm toán của kiểm toán viên công chứng, hội đồng quản trị đã chính thức phê duyệt {vi_short} kỳ này.",
                "en": f"Following the audit by certified public accountants, the board of directors officially approved this term's {en_clean}.",
                "register": "statutory_reporting",
                "status": "candidate"
            },
            {
                "ja": f"投資家への適時開示に向けて、{surface}の注記事項と整合性を慎重に確認しています。",
                "vi": f"Hướng tới công bố thông tin kịp thời cho nhà đầu tư, chúng tôi đang rà soát cẩn thận tính nhất quán của thuyết minh trong {vi_short}.",
                "en": f"Ahead of timely disclosure to investors, we are carefully verifying consistency with the footnotes in the {en_clean}.",
                "register": "investor_relations",
                "status": "candidate"
            }
        ]

    # Default / General Account & Procedure
    return [
        {
            "ja": f"月末の帳簿照合において、{surface}の計上漏れや残高差異がないか精査します。",
            "vi": f"Khi đối chiếu sổ sách cuối tháng, chúng tôi kiểm tra kỹ lưỡng xem có bỏ sót hạch toán hay chênh lệch số dư của {vi_short} không.",
            "en": f"During month-end book reconciliation, we carefully examine whether there are unrecorded entries or balance discrepancies in {en_clean}.",
            "register": "accounting_audit",
            "status": "candidate"
        },
        {
            "ja": f"適正な会計基準に則り、当期の決算処理において{surface}を適正に処理いたしました。",
            "vi": f"Tuân thủ các chuẩn mực kế toán thích hợp, chúng tôi đã xử lý đúng quy định {vi_short} trong đợt quyết toán kỳ này.",
            "en": f"In accordance with applicable accounting standards, we properly processed {en_clean} in this term's closing entries.",
            "register": "financial_reporting",
            "status": "candidate"
        }
    ]


def generate_semantic_dialogue(surface: str, reading: str, vi_short: str, en_pref: str, domain: str, sem_class: str) -> list:
    """
    Generates natural workplace dialogue between two business professionals.
    """
    en_clean = en_pref.lower()
    
    if sem_class in ["contract", "contract_clause"]:
        return [
            {
                "speaker": "A",
                "ja": f"先方法務部から戻ってきた{surface}の修正案ですが、確認は済みましたか。",
                "vi": f"Bản dự thảo sửa đổi {vi_short} gửi lại từ phòng pháp chế đối tác, anh/chị đã xem qua chưa?",
                "en": f"Have you finished reviewing the revised draft of {en_clean} returned from the counterparty's legal team?"
            },
            {
                "speaker": "B",
                "ja": f"はい、損害賠償条項を含めてリスクがないことを確認いたしましたので、このまま締結手続きに進めます。",
                "vi": f"Vâng, tôi đã xác nhận không có rủi ro bao gồm cả điều khoản bồi thường thiệt hại, chúng ta có thể tiến hành thủ tục ký kết.",
                "en": f"Yes, I confirmed there are no risks including the liability clause, so we can proceed with execution."
            }
        ]

    elif sem_class in ["shipping_document", "customs_procedure", "trade_term"]:
        return [
            {
                "speaker": "A",
                "ja": f"本日通関予定の案件ですが、{surface}の手配状況はいかがでしょうか。",
                "vi": f"Vụ việc dự kiến thông quan hôm nay, tình hình thu xếp {vi_short} thế nào rồi ạ?",
                "en": f"Regarding the shipment scheduled for customs clearance today, what is the status of arranging {en_clean}?"
            },
            {
                "speaker": "B",
                "ja": f"通関業者と乙仲への連絡を済ませており、書類の確認も完了して輸入申告に入っております。",
                "vi": f"Tôi đã liên hệ xong với đại lý hải quan và công ty giao nhận, giấy tờ đã kiểm tra xong và đang tiến hành khai báo nhập khẩu.",
                "en": f"We have contacted the customs broker and forwarder; document checks are complete and import declaration is underway."
            }
        ]

    elif sem_class in ["tax", "tax_filing", "tax_deduction"]:
        return [
            {
                "speaker": "A",
                "ja": f"今回の決算申告における{surface}の計算根拠は整理できましたか。",
                "vi": f"Căn cứ tính toán {vi_short} trong kỳ quyết toán thuế này đã được tổng hợp xong chưa?",
                "en": f"Have we compiled the calculation rationale for {en_clean} in this tax filing?"
            },
            {
                "speaker": "B",
                "ja": f"はい、根拠資料と税理士の確認書を揃えましたので、申告書添付書類として提出可能です。",
                "vi": f"Vâng, tôi đã chuẩn bị đủ tài liệu căn cứ và xác nhận của chuyên viên thuế, sẵn sàng nộp kèm theo tờ khai.",
                "en": f"Yes, supporting evidence and the tax accountant's confirmation are assembled and ready to attach to the return."
            }
        ]

    # Default professional accounting / office dialogue
    return [
        {
            "speaker": "A",
            "ja": f"今月の月次決算で、{surface}の計上内容に差異は発生していませんか。",
            "vi": f"Trong quyết toán tháng này, nội dung hạch toán của {vi_short} có phát sinh chênh lệch gì không?",
            "en": f"In this month's closing, are there any discrepancies occurring in the entries for {en_clean}?"
        },
        {
            "speaker": "B",
            "ja": f"証憑書類と補助元帳を照合済みで、すべて適正に整合していることを確認いたしました。",
            "vi": f"Tôi đã đối chiếu xong chứng từ gốc với sổ chi tiết, xác nhận toàn bộ đã khớp đúng chuẩn xác.",
            "en": f"Vouchers and subsidiary ledgers have been reconciled; I confirmed everything matches properly."
        }
    ]
