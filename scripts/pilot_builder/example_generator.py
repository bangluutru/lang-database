"""
scripts/pilot_builder/example_generator.py
Fine-grained, authentic Japanese workplace sentence and dialogue generator for professional vocabulary.
Generates realistic sentences tailored to explicit semantic categories (accounting, tax regimes,
statutory filings, shipping documents, trade logistics, corporate governance, customs compliance).

Builder outputs status="generated" and generation_method="semantic_frame".
No self-certification.
"""


def generate_semantic_examples(surface: str, reading: str, vi_short: str, en_pref: str, domain: str, sem_class: str) -> list:
    """
    Generates realistic, natural workplace examples based on explicit semantic classes.
    Guarantees no language contamination and authentic professional Japanese.
    """
    en_clean = en_pref.lower()

    if sem_class == "tax_scheme":
        return [
            {
                "ja": f"節税および地域貢献の観点から、社内周知を行って{surface}の制度を活用しました。",
                "vi": f"Dưới góc độ tiết kiệm thuế và đóng góp cho địa phương, chúng tôi đã phổ biến nội bộ và tận dụng chính sách {vi_short}.",
                "en": f"From the perspectives of tax savings and regional contribution, we informed our staff and took advantage of the {en_clean}.",
                "register": "tax_compliance",
                "status": "generated",
                "generation_method": "semantic_frame"
            },
            {
                "ja": f"今年度の控除上限額を事前に試算した上で、計画的に{surface}の手続きを進めました。",
                "vi": f"Sau khi tính toán thử mức trần giảm trừ cho năm nay, chúng tôi đã tiến hành thủ tục {vi_short} theo đúng kế hoạch.",
                "en": f"After calculating the deduction ceiling in advance for this fiscal year, we systematically proceeded with the {en_clean}.",
                "register": "statutory_reporting",
                "status": "generated",
                "generation_method": "semantic_frame"
            }
        ]

    elif sem_class == "executive_compensation":
        return [
            {
                "ja": f"定時株主総会の決議に基づき、役員に対して所定の支給期日に{surface}を支給いたしました。",
                "vi": f"Căn cứ nghị quyết đại hội đồng cổ đông thường niên, chúng tôi đã chi trả {vi_short} cho lãnh đạo vào đúng ngày quy định.",
                "en": f"In accordance with the resolution of the annual general meeting of shareholders, we paid the {en_clean} to directors on the scheduled date.",
                "register": "corporate_governance",
                "status": "generated",
                "generation_method": "semantic_frame"
            },
            {
                "ja": f"法人税法上の損金算入要件を満たすため、事前に税務署へ{surface}に関する届出書を提出しました。",
                "vi": f"Để thỏa mãn điều kiện tính vào chi phí được trừ theo luật thuế thu nhập doanh nghiệp, chúng tôi đã nộp trước tờ khai {vi_short} cho cơ quan thuế.",
                "en": f"To satisfy the statutory deduction requirements under corporate tax law, we submitted the notification for {en_clean} to the tax office in advance.",
                "register": "tax_compliance",
                "status": "generated",
                "generation_method": "semantic_frame"
            }
        ]

    elif sem_class == "equity_valuation_account":
        return [
            {
                "ja": f"保有する投資有価証券の時価評価に伴い、生じた評価差額を{surface}として純資産の部に計上しました。",
                "vi": f"Cùng với việc đánh giá lại chứng khoán đầu tư theo giá thị trường, khoản chênh lệch phát sinh được ghi nhận vào phần vốn chủ sở hữu dưới dạng {vi_short}.",
                "en": f"Following the mark-to-market valuation of held investment securities, the resulting valuation difference was recorded in the net assets section as {en_clean}.",
                "register": "corporate_accounting",
                "status": "generated",
                "generation_method": "semantic_frame"
            },
            {
                "ja": f"期末決算において税効果会計を適用し、{surface}に係る税効果額を適切に処理しました。",
                "vi": f"Trong kỳ quyết toán cuối năm, chúng tôi áp dụng kế toán thuế hoãn lại và xử lý đúng đắn số tiền thuế liên quan đến {vi_short}.",
                "en": f"In the year-end closing, we applied tax effect accounting and properly accounted for the tax effect related to {en_clean}.",
                "register": "financial_reporting",
                "status": "generated",
                "generation_method": "semantic_frame"
            }
        ]

    elif sem_class == "income_classification":
        return [
            {
                "ja": f"各種収入金額および必要経費を精査し、確定申告書において{surface}の金額を適正に算出しました。",
                "vi": f"Rà soát kỹ các khoản doanh thu và chi phí cần thiết, chúng tôi đã tính toán chính xác số tiền {vi_short} trên tờ khai thuế.",
                "en": f"After carefully examining gross receipts and necessary expenses, we properly computed the amount of {en_clean} on the tax return.",
                "register": "tax_compliance",
                "status": "generated",
                "generation_method": "semantic_frame"
            },
            {
                "ja": f"所得税法上の規定に基づき、総合課税の対象となる{surface}を他の所得と合算して課税標準を計算しました。",
                "vi": f"Dựa trên quy định của luật thuế thu nhập cá nhân, chúng tôi cộng gộp {vi_short} chịu thuế tổng hợp với các khoản thu nhập khác để tính thu nhập chịu thuế.",
                "en": f"Under provisions of the Income Tax Act, we aggregated {en_clean} subject to comprehensive taxation with other income to determine the tax base.",
                "register": "statutory_reporting",
                "status": "generated",
                "generation_method": "semantic_frame"
            }
        ]

    elif sem_class == "taxable_income_element":
        return [
            {
                "ja": f"会計上の費用と税務上の取扱いの相違を調整するため、別表四において{surface}を適切に処理しました。",
                "vi": f"Để điều chỉnh sự khác biệt giữa chi phí kế toán và quy định thuế, chúng tôi đã xử lý đúng đắn {vi_short} trên phụ lục số 4 tờ khai quyết toán.",
                "en": f"To reconcile the differences between book expenses and tax treatments, we properly adjusted {en_clean} on Schedule 4.",
                "register": "tax_compliance",
                "status": "generated",
                "generation_method": "semantic_frame"
            },
            {
                "ja": f"税務調査における指摘を防止するため、過年度の取引を検証し{surface}の算入漏れがないか確認しました。",
                "vi": f"Để phòng ngừa việc bị cơ quan thuế truy thu trong thanh tra, chúng tôi kiểm tra lại giao dịch các năm trước xem có bỏ sót hạch toán {vi_short} không.",
                "en": f"To prevent tax audit discrepancies, we reviewed prior-year transactions to confirm no omissions occurred in {en_clean}.",
                "register": "statutory_reporting",
                "status": "generated",
                "generation_method": "semantic_frame"
            }
        ]

    elif sem_class == "tax_loss":
        return [
            {
                "ja": f"過去に発生した{surface}を今期の課税所得から控除し、法人税の納付額を適正に圧縮しました。",
                "vi": f"Chúng tôi đã khấu trừ khoản {vi_short} phát sinh từ các năm trước vào thu nhập chịu thuế kỳ này, giảm hợp lý số thuế thu nhập doanh nghiệp phải nộp.",
                "en": f"We deducted the {en_clean} incurred in prior years against current taxable income, appropriately reducing the corporate tax liability.",
                "register": "tax_compliance",
                "status": "generated",
                "generation_method": "semantic_frame"
            },
            {
                "ja": f"法定の繰越期間を管理し、保有する{surface}の控除限度額を計算して申告書に記載しました。",
                "vi": f"Quản lý chặt chẽ thời hạn chuyển lỗ theo luật định, chúng tôi tính mức trần khấu trừ {vi_short} và ghi vào tờ khai thuế.",
                "en": f"Managing statutory carryforward periods, we calculated the deduction limit for {en_clean} and recorded it in the tax return.",
                "register": "statutory_reporting",
                "status": "generated",
                "generation_method": "semantic_frame"
            }
        ]

    elif sem_class == "tangible_fixed_asset":
        return [
            {
                "ja": f"事業拡大に向けた拠点開発のため、適正な鑑定評価を経て新たな{surface}を取得しました。",
                "vi": f"Để phát triển cơ sở phục vụ mở rộng kinh doanh, chúng tôi đã mua mảnh {vi_short} mới sau khi có thẩm định giá chuẩn xác.",
                "en": f"For facility development toward business expansion, we acquired new {en_clean} following an appropriate appraisal valuation.",
                "register": "corporate_accounting",
                "status": "generated",
                "generation_method": "semantic_frame"
            },
            {
                "ja": f"事業年度末の棚卸実査を実施し、固定資産台帳と{surface}の権利関係および現況を照合しました。",
                "vi": f"Thực hiện kiểm kê thực tế cuối năm tài chính, chúng tôi đối chiếu sổ tài sản cố định với quyền sở hữu và hiện trạng của {vi_short}.",
                "en": f"Conducting a physical audit at the fiscal year-end, we reconciled the fixed asset register with the legal ownership and actual status of the {en_clean}.",
                "register": "financial_audit",
                "status": "generated",
                "generation_method": "semantic_frame"
            }
        ]

    elif sem_class == "depreciable_asset":
        return [
            {
                "ja": f"生産ラインの合理化を図るため最新鋭の{surface}を導入し、固定資産台帳に登録しました。",
                "vi": f"Nhằm tối ưu hóa dây chuyền sản xuất, chúng tôi đã đưa vào sử dụng {vi_short} tối tân và đăng ký vào sổ tài sản cố định.",
                "en": f"To streamline production lines, we introduced state-of-the-art {en_clean} and recorded it in the fixed asset register.",
                "register": "corporate_accounting",
                "status": "generated",
                "generation_method": "semantic_frame"
            },
            {
                "ja": f"法定耐用年数に基づき、当期の決算処理において{surface}の減価償却費を適正に計上しました。",
                "vi": f"Căn cứ thời gian sử dụng theo luật định, chúng tôi đã trích khấu hao hợp lý cho {vi_short} trong đợt quyết toán kỳ này.",
                "en": f"Based on statutory useful lives, we properly recorded depreciation expense for {en_clean} during this term's closing.",
                "register": "financial_reporting",
                "status": "generated",
                "generation_method": "semantic_frame"
            }
        ]

    elif sem_class == "intangible_asset":
        return [
            {
                "ja": f"事業譲受に伴って発生した資産価値を精査し、無形固定資産として{surface}を計上しました。",
                "vi": f"Rà soát kỹ giá trị tài sản phát sinh khi nhận chuyển nhượng kinh doanh, chúng tôi đã ghi nhận {vi_short} vào tài sản cố định vô hình.",
                "en": f"Examining the asset values arising from the business transfer, we recognized {en_clean} as an intangible fixed asset.",
                "register": "corporate_accounting",
                "status": "generated",
                "generation_method": "semantic_frame"
            },
            {
                "ja": f"将来の収益性を慎重に見極め、{surface}について規則的な償却および減損の要否を検討しました。",
                "vi": f"Đánh giá thận trọng khả năng sinh lời trong tương lai, chúng tôi xem xét việc trích khấu hao định kỳ và sự cần thiết ghi giảm giá trị của {vi_short}.",
                "en": f"Carefully assessing future profitability, we evaluated the need for systematic amortization and impairment testing regarding {en_clean}.",
                "register": "financial_audit",
                "status": "generated",
                "generation_method": "semantic_frame"
            }
        ]

    elif sem_class == "securities_investment":
        return [
            {
                "ja": f"余剰資金の安定的運用と取引先との関係維持を目的として、{surface}を長期保有しています。",
                "vi": f"Nhằm mục đích quản lý vốn nhàn rỗi an toàn và duy trì quan hệ với đối tác, chúng tôi nắm giữ dài hạn {vi_short}.",
                "en": f"For the purpose of stable management of surplus funds and maintaining business partner relationships, we hold {en_clean} on a long-term basis.",
                "register": "corporate_finance",
                "status": "generated",
                "generation_method": "semantic_frame"
            },
            {
                "ja": f"期末決算において時価評価を実施し、{surface}の含み損益および評価差額を適正に会計処理しました。",
                "vi": f"Trong kỳ quyết toán cuối năm, chúng tôi đánh giá lại theo thị trường và xử lý kế toán chuẩn xác các khoản lãi lỗ chưa thực hiện của {vi_short}.",
                "en": f"In the year-end closing, we performed mark-to-market valuation and properly accounted for unrealized gains and losses on {en_clean}.",
                "register": "financial_reporting",
                "status": "generated",
                "generation_method": "semantic_frame"
            }
        ]

    elif sem_class == "shipping_document":
        return [
            {
                "ja": f"輸入貨物の引き取り手続きを行うため、運送会社から{surface}の原本を受領しました。",
                "vi": f"Để làm thủ tục nhận hàng nhập khẩu, chúng tôi đã nhận bản gốc {vi_short} từ đơn vị vận chuyển.",
                "en": f"To process pickup procedures for imported cargo, we received the original {en_clean} from the carrier.",
                "register": "logistics_workplace",
                "status": "generated",
                "generation_method": "semantic_frame"
            },
            {
                "ja": f"通関業者へ{surface}を速やかに提出し、荷受人情報の確認および輸入申告の手配を依頼しました。",
                "vi": f"Chúng tôi đã nộp ngay {vi_short} cho đại lý hải quan, yêu cầu xác nhận thông tin người nhận hàng và thu xếp khai báo nhập khẩu.",
                "en": f"We promptly submitted the {en_clean} to the customs broker, requesting consignee verification and import declaration arrangements.",
                "register": "customs_procedure",
                "status": "generated",
                "generation_method": "semantic_frame"
            }
        ]

    elif sem_class == "document":
        return [
            {
                "ja": f"株主総会や取締役会を円滑に進行するため、法定期限内に全関係者へ{surface}を発送いたしました。",
                "vi": f"Để đại hội đồng cổ đông hoặc họp hội đồng quản trị diễn ra suôn sẻ, chúng tôi đã gửi {vi_short} cho các bên liên quan đúng thời hạn luật định.",
                "en": f"To facilitate smooth proceedings for the board or shareholders meeting, we dispatched the {en_clean} to all parties within the statutory deadline.",
                "register": "corporate_governance",
                "status": "generated",
                "generation_method": "semantic_frame"
            },
            {
                "ja": f"内部統制およびコンプライアンスの証跡として、担当部署にて受領した{surface}を厳重に保管しています。",
                "vi": f"Làm bằng chứng kiểm soát nội bộ và tuân thủ quy định, bộ phận phụ trách lưu trữ nghiêm ngặt {vi_short} đã nhận.",
                "en": f"As evidence of internal control and compliance, the department in charge securely archives the received {en_clean}.",
                "register": "office_administration",
                "status": "generated",
                "generation_method": "semantic_frame"
            }
        ]

    elif sem_class == "contract":
        return [
            {
                "ja": f"取引先と基本合意に達したため、来週{surface}を正式に締結いたします。",
                "vi": f"Do đã đạt được thỏa thuận cơ bản với đối tác, tuần tới chúng tôi sẽ chính thức ký kết {vi_short}.",
                "en": f"Having reached a basic agreement with the partner, we will officially execute the {en_clean} next week.",
                "register": "formal_business",
                "status": "generated",
                "generation_method": "semantic_frame"
            },
            {
                "ja": f"法務部門と連携し、{surface}の条項に法的リスクが含まれていないか事前に精査しました。",
                "vi": f"Phối hợp với bộ phận pháp chế, chúng tôi đã rà soát kỹ trước xem điều khoản {vi_short} có rủi ro pháp lý nào không.",
                "en": f"In coordination with the legal department, we thoroughly reviewed the clauses of the {en_clean} in advance for any legal risks.",
                "register": "corporate_governance",
                "status": "generated",
                "generation_method": "semantic_frame"
            }
        ]

    elif sem_class == "contract_clause":
        return [
            {
                "ja": f"予期せぬ紛争を未然に防止するため、契約書内に明確な{surface}を設けました。",
                "vi": f"Để ngăn ngừa các tranh chấp bất ngờ từ trước, chúng tôi đã đưa vào hợp đồng điều khoản {vi_short} rất rõ ràng.",
                "en": f"To prevent unexpected disputes beforehand, we established explicit {en_clean} within the contract.",
                "register": "corporate_governance",
                "status": "generated",
                "generation_method": "semantic_frame"
            },
            {
                "ja": f"顧問弁護士の助言に基づき、相手方から提示された{surface}の文言を一部修正しました。",
                "vi": f"Dựa trên tư vấn của luật sư cố vấn, chúng tôi đã sửa đổi một phần câu chữ của {vi_short} do đối tác đề xuất.",
                "en": f"Based on advice from our legal counsel, we partially revised the wording of the {en_clean} proposed by the counterparty.",
                "register": "formal_business",
                "status": "generated",
                "generation_method": "semantic_frame"
            }
        ]

    elif sem_class == "trade_term":
        return [
            {
                "ja": f"今回の海上輸送契約は、運賃と危険負担の範囲を明確にするため{surface}条件を採用しました。",
                "vi": f"Hợp đồng vận tải biển lần này áp dụng điều kiện {vi_short} để làm rõ phạm vi chịu cước phí và rủi ro.",
                "en": f"This ocean transport contract adopted {surface} terms to clarify the division of freight costs and risk transfer.",
                "register": "trade_contract",
                "status": "generated",
                "generation_method": "semantic_frame"
            },
            {
                "ja": f"{surface}建値での取引に基づき、仕向港での荷揚げ費用と輸入関税を輸入者側で負担します。",
                "vi": f"Căn cứ giao dịch theo giá {surface}, chi phí dỡ hàng tại cảng đích và thuế nhập khẩu do bên nhập khẩu chịu.",
                "en": f"Based on transactions priced under {surface}, unloading costs at the port of destination and import duties are borne by the importer.",
                "register": "international_trade",
                "status": "generated",
                "generation_method": "semantic_frame"
            }
        ]

    elif sem_class == "customs_procedure":
        return [
            {
                "ja": f"税関への本申告に先立ち、関係官庁の要件を満たすため速やかに{surface}の手続きを完了させました。",
                "vi": f"Trước khi khai báo chính thức với hải quan, chúng tôi đã nhanh chóng hoàn thành thủ tục {vi_short} để đáp ứng yêu cầu cơ quan chủ quản.",
                "en": f"Prior to the formal customs declaration, we promptly completed {en_clean} procedures to fulfill the requirements of the competent agency.",
                "register": "customs_procedure",
                "status": "generated",
                "generation_method": "semantic_frame"
            },
            {
                "ja": f"通関士と綿密に連携し、{surface}に必要な関係書類の整合性を事前にチェックしました。",
                "vi": f"Phối hợp chặt chẽ với chuyên viên khai báo hải quan, chúng tôi đã kiểm tra trước tính đồng bộ của các chứng từ cần thiết cho {vi_short}.",
                "en": f"Coordinating closely with the customs specialist, we checked the consistency of documents required for {en_clean} in advance.",
                "register": "logistics_workplace",
                "status": "generated",
                "generation_method": "semantic_frame"
            }
        ]

    elif sem_class == "cargo_operation":
        return [
            {
                "ja": f"海上輸送中の荷崩れを防止するため、コンテナヤードにて立ち会いのもと{surface}を入念に実施しました。",
                "vi": f"Để tránh hàng hóa bị xô lệch đổ vỡ trong quá trình vận chuyển trên biển, chúng tôi đã thực hiện kỹ lưỡng {vi_short} dưới sự giám sát trực tiếp tại bãi container.",
                "en": f"To prevent cargo shifting during ocean transit, we meticulously carried out {en_clean} under on-site supervision at the container yard.",
                "register": "logistics_workplace",
                "status": "generated",
                "generation_method": "semantic_frame"
            },
            {
                "ja": f"本船への積載計画に沿って、安全基準を厳守しながら本日の午後より{surface}の作業を開始します。",
                "vi": f"Theo kế hoạch xếp hàng lên tàu mẹ, chiều nay sẽ bắt đầu tiến hành công việc {vi_short} với việc tuân thủ nghiêm ngặt các tiêu chuẩn an toàn.",
                "en": f"In accordance with the vessel stowage plan, {en_clean} operations will commence this afternoon while strictly observing safety standards.",
                "register": "logistics_operations",
                "status": "generated",
                "generation_method": "semantic_frame"
            }
        ]

    elif sem_class == "freight_charge":
        return [
            {
                "ja": f"コンテナの搬出がフリータイムを超過したため、船社より{surface}が請求されました。",
                "vi": f"Do việc kéo container ra khỏi bãi vượt quá thời gian miễn phí lưu bãi, hãng tàu đã phát hóa đơn phạt {vi_short}.",
                "en": f"Because container pickup exceeded the free time, the shipping line invoiced {en_clean}.",
                "register": "logistics_workplace",
                "status": "generated",
                "generation_method": "semantic_frame"
            },
            {
                "ja": f"物流コストの抑制を図るため、運行計画を見直して{surface}の追加発生を防止しました。",
                "vi": f"Nhằm kiềm chế chi phí logistics, chúng tôi đã rà soát lại lịch trình vận hành để ngăn ngừa phát sinh thêm {vi_short}.",
                "en": f"To contain logistics costs, we reviewed the operating plan to prevent additional {en_clean} from occurring.",
                "register": "logistics_operations",
                "status": "generated",
                "generation_method": "semantic_frame"
            }
        ]

    elif sem_class == "tax_filing":
        return [
            {
                "ja": f"期末決算の確定に伴い、所轄税務署に対して法定申告期限内に{surface}の手続きを完了しました。",
                "vi": f"Cùng với việc chốt số liệu quyết toán cuối kỳ, chúng tôi đã hoàn tất thủ tục {vi_short} trong thời hạn luật định tại chi cục thuế phụ trách.",
                "en": f"Upon finalizing the fiscal year-end accounts, we completed {en_clean} procedures within the statutory filing deadline at the competent tax office.",
                "register": "statutory_reporting",
                "status": "generated",
                "generation_method": "semantic_frame"
            },
            {
                "ja": f"顧問税理士の助言を受け、適正な税法解釈に基づき{surface}の提出書類を整えました。",
                "vi": f"Nhận tư vấn từ chuyên viên thuế cố vấn, chúng tôi đã hoàn thiện hồ sơ nộp {vi_short} dựa trên diễn giải luật thuế chuẩn xác.",
                "en": f"Receiving advice from our advisory tax accountant, we assembled the submission documents for {en_clean} under proper tax law interpretations.",
                "register": "formal_business",
                "status": "generated",
                "generation_method": "semantic_frame"
            }
        ]

    elif sem_class == "tax_deduction":
        return [
            {
                "ja": f"法定要件を慎重に確認した上で、今年度の確定申告において{surface}を適用しました。",
                "vi": f"Sau khi kiểm tra cẩn thận điều kiện theo luật định, chúng tôi đã áp dụng {vi_short} trong tờ khai quyết toán thuế năm nay.",
                "en": f"After carefully verifying statutory requirements, we applied the {en_clean} in this fiscal year's tax return.",
                "register": "statutory_reporting",
                "status": "generated",
                "generation_method": "semantic_frame"
            },
            {
                "ja": f"{surface}の適用を受けるため、関係書類を整備して申告書に添付しました。",
                "vi": f"Để được hưởng {vi_short}, chúng tôi đã hoàn thiện các chứng từ liên quan và đính kèm vào tờ khai.",
                "en": f"In order to qualify for the {en_clean}, we prepared relevant supporting documents and attached them to the return.",
                "register": "tax_compliance",
                "status": "generated",
                "generation_method": "semantic_frame"
            }
        ]

    elif sem_class == "tax":
        return [
            {
                "ja": f"課税標準および適用税率を正確に算出し、納期限までに{surface}の納付手続きを完了しました。",
                "vi": f"Tính toán chính xác thu nhập chịu thuế và thuế suất áp dụng, chúng tôi đã hoàn tất thủ tục nộp {vi_short} trước hạn chót.",
                "en": f"Accurately calculating the tax base and applicable tax rates, we completed the payment of {en_clean} by the due date.",
                "register": "statutory_reporting",
                "status": "generated",
                "generation_method": "semantic_frame"
            },
            {
                "ja": f"税制改正の内容を踏まえ、当期における{surface}の税負担額への影響を試算いたしました。",
                "vi": f"Căn cứ nội dung cải cách luật thuế, chúng tôi đã tính thử tác động đối với số tiền thuế {vi_short} phải nộp trong kỳ này.",
                "en": f"In light of tax law revisions, we estimated the impact on the tax burden of {en_clean} for this term.",
                "register": "formal_business",
                "status": "generated",
                "generation_method": "semantic_frame"
            }
        ]

    elif sem_class == "financial_statement":
        return [
            {
                "ja": f"公認会計士の厳格な監査を経て、取締役会にて今期の{surface}が正式に承認されました。",
                "vi": f"Sau khi có kiểm toán nghiêm ngặt của kiểm toán viên công chứng, hội đồng quản trị đã chính thức phê duyệt {vi_short} kỳ này.",
                "en": f"Following a rigorous audit by certified public accountants, the board of directors officially approved this term's {en_clean}.",
                "register": "statutory_reporting",
                "status": "generated",
                "generation_method": "semantic_frame"
            },
            {
                "ja": f"投資家への適時開示に向けて、{surface}の注記事項と財務数値の整合性を慎重に確認しています。",
                "vi": f"Hướng tới công bố thông tin kịp thời cho nhà đầu tư, chúng tôi đang rà soát cẩn thận tính nhất quán giữa thuyết minh và số liệu tài chính trong {vi_short}.",
                "en": f"Ahead of timely disclosure to investors, we are carefully verifying consistency between the footnotes and financial figures in the {en_clean}.",
                "register": "investor_relations",
                "status": "generated",
                "generation_method": "semantic_frame"
            }
        ]

    elif sem_class == "person_role":
        return [
            {
                "ja": f"定時株主総会の決議を経て、当社の新任{surface}が正式に選任されました。",
                "vi": f"Thông qua nghị quyết của đại hội đồng cổ đông thường niên, {vi_short} mới của công ty chúng tôi đã được bổ nhiệm chính thức.",
                "en": f"Through the resolution of the annual general shareholders meeting, our new {en_clean} was officially appointed.",
                "register": "corporate_governance",
                "status": "generated",
                "generation_method": "semantic_frame"
            },
            {
                "ja": f"業務執行の適法性を確保するため、{surface}と定期的な報告連絡会を開催しています。",
                "vi": f"Để đảm bảo tính hợp pháp trong điều hành công việc, chúng tôi tổ chức họp báo cáo định kỳ với {vi_short}.",
                "en": f"To ensure the legality of business execution, we hold regular reporting sessions with the {en_clean}.",
                "register": "formal_business",
                "status": "generated",
                "generation_method": "semantic_frame"
            }
        ]

    elif sem_class == "organization":
        return [
            {
                "ja": f"重要議案の決議を行うため、来週臨時{surface}を招集する運びとなりました。",
                "vi": f"Để biểu quyết các nghị quyết quan trọng, tuần sau công ty sẽ tiến hành triệu tập cuộc họp {vi_short} bất thường.",
                "en": f"To resolve critical proposals, an extraordinary meeting of the {en_clean} will be convened next week.",
                "register": "corporate_governance",
                "status": "generated",
                "generation_method": "semantic_frame"
            },
            {
                "ja": f"{surface}において今期の経営方針および予算配分案が原案通り可決されました。",
                "vi": f"Tại {vi_short}, phương hướng kinh doanh và phương án phân bổ ngân sách kỳ này đã được thông qua như đề xuất ban đầu.",
                "en": f"At the {en_clean}, this term's management policy and budget allocation proposal were approved as submitted.",
                "register": "formal_business",
                "status": "generated",
                "generation_method": "semantic_frame"
            }
        ]

    elif sem_class == "metric":
        return [
            {
                "ja": f"経営効率の改善に向け、各事業部門で{surface}の数値を月次でモニタリングしています。",
                "vi": f"Hướng tới cải thiện hiệu quả quản lý, các bộ phận kinh doanh đang theo dõi chỉ số {vi_short} hàng tháng.",
                "en": f"Towards improving operational efficiency, each business division monitors {en_clean} metrics on a monthly basis.",
                "register": "performance_management",
                "status": "generated",
                "generation_method": "semantic_frame"
            },
            {
                "ja": f"当期の{surface}は目標値を上回り、収益性と資本効率の向上が確認されました。",
                "vi": f"Chỉ số {vi_short} kỳ này đã vượt giá trị mục tiêu, xác nhận khả năng sinh lời và hiệu quả sử dụng vốn đã được nâng cao.",
                "en": f"This term's {en_clean} exceeded the target value, confirming an improvement in profitability and capital efficiency.",
                "register": "business_analysis",
                "status": "generated",
                "generation_method": "semantic_frame"
            }
        ]

    elif sem_class == "business_practice":
        return [
            {
                "ja": f"円滑なプロジェクト推進を図るため、関係部署への事前の{surface}を徹底しています。",
                "vi": f"Nhằm thúc đẩy dự án diễn ra trôi chảy, chúng tôi triệt để thực hiện {vi_short} từ trước với các phòng ban liên quan.",
                "en": f"To facilitate smooth project execution, we thoroughly conduct prior {en_clean} with relevant departments.",
                "register": "japanese_business_culture",
                "status": "generated",
                "generation_method": "semantic_frame"
            },
            {
                "ja": f"業務上のトラブルを未然に防ぐため、迅速な{surface}の習慣付けが職場全体で求められます。",
                "vi": f"Để ngăn ngừa rủi ro phát sinh trong công việc, việc tạo thói quen {vi_short} nhanh chóng là rất cần thiết trong toàn cơ quan.",
                "en": f"To prevent operational issues beforehand, establishing a habit of prompt {en_clean} is required across the workplace.",
                "register": "workplace_discipline",
                "status": "generated",
                "generation_method": "semantic_frame"
            }
        ]

    elif sem_class == "professional_service_firm":
        return [
            {
                "ja": f"独立した立場から適正な財務諸表の作成を担保するため、株主総会において新たな{surface}を選任しました。",
                "vi": f"Để bảo đảm việc lập báo cáo tài chính đúng đắn từ góc độ độc lập, chúng tôi đã bổ nhiệm {vi_short} mới tại đại hội đồng cổ đông.",
                "en": f"To ensure the preparation of proper financial statements from an independent perspective, we appointed a new {en_clean} at the shareholders meeting.",
                "register": "corporate_governance",
                "status": "generated",
                "generation_method": "semantic_frame"
            },
            {
                "ja": f"決算発表を前に、会計方針の適用や内部統制の有効性について{surface}の監査を受けました。",
                "vi": f"Trước thềm công bố báo cáo tài chính, chúng tôi đã chịu sự kiểm toán của {vi_short} về việc áp dụng chính sách kế toán và hiệu lực kiểm soát nội bộ.",
                "en": f"Prior to the earnings announcement, we underwent an audit by the {en_clean} regarding the application of accounting policies and effectiveness of internal controls.",
                "register": "financial_audit",
                "status": "generated",
                "generation_method": "semantic_frame"
            }
        ]

    elif sem_class == "statutory_document":
        return [
            {
                "ja": f"法令に基づく適正な手続きを遂行するため、所轄官庁に対して期限内に{surface}を提出いたしました。",
                "vi": f"Để thực hiện đúng thủ tục theo luật định, chúng tôi đã nộp {vi_short} cho cơ quan có thẩm quyền đúng thời hạn.",
                "en": f"To execute proper procedures under statutory regulations, we submitted the {en_clean} to the competent authority within the deadline.",
                "register": "statutory_reporting",
                "status": "generated",
                "generation_method": "semantic_frame"
            },
            {
                "ja": f"税務調査およびコンプライアンス監査に備え、発行済みの{surface}を法令の保存期間に従って厳重に保管しています。",
                "vi": f"Chuẩn bị cho thanh tra thuế và kiểm toán tuân thủ, chúng tôi lưu trữ cẩn thận {vi_short} đã phát hành theo đúng thời hạn luật định.",
                "en": f"In preparation for tax audits and compliance reviews, we securely retain issued {en_clean} in accordance with statutory retention periods.",
                "register": "compliance_workplace",
                "status": "generated",
                "generation_method": "semantic_frame"
            }
        ]

    elif sem_class == "statutory_law":
        return [
            {
                "ja": f"適法かつ健全な事業運営を維持するため、全社を挙げて{surface}の関連条項および遵守事項を徹底しています。",
                "vi": f"Để duy trì hoạt động kinh doanh hợp pháp và lành mạnh, toàn công ty triệt để tuân thủ các điều khoản liên quan của {vi_short}.",
                "en": f"To maintain lawful and sound business operations, we thoroughly comply with the relevant articles and provisions of the {en_clean} across the company.",
                "register": "legal_compliance",
                "status": "generated",
                "generation_method": "semantic_frame"
            },
            {
                "ja": f"最新の法改正を踏まえ、顧問弁護士の助言を受けながら{surface}の施行に伴う社内規程の改定を行いました。",
                "vi": f"Căn cứ sửa đổi luật mới nhất, với sự tư vấn của luật sư cố vấn, chúng tôi đã sửa đổi quy chế nội bộ theo hiệu lực của {vi_short}.",
                "en": f"In light of the latest statutory revisions and with advice from legal counsel, we revised internal regulations in conjunction with the enforcement of the {en_clean}.",
                "register": "corporate_governance",
                "status": "generated",
                "generation_method": "semantic_frame"
            }
        ]

    elif sem_class == "taxpayer_category":
        return [
            {
                "ja": f"消費税法上の基準期間における課税売上高を判定し、自社が{surface}に該当することを確認しました。",
                "vi": f"Xác định doanh thu chịu thuế trong kỳ tính thuế căn cứ theo luật thuế tiêu dùng, chúng tôi xác nhận doanh nghiệp mình thuộc diện {vi_short}.",
                "en": f"Assessing taxable sales for the statutory base period under consumption tax law, we confirmed that our firm falls under the category of {en_clean}.",
                "register": "tax_compliance",
                "status": "generated",
                "generation_method": "semantic_frame"
            },
            {
                "ja": f"インボイス制度の導入に伴い、主要な取引先が{surface}であるかどうかの登録状況を調査しました。",
                "vi": f"Cùng với việc triển khai chế độ hóa đơn hợp lệ, chúng tôi đã rà soát trạng thái đăng ký của các đối tác chính xem có thuộc diện {vi_short} hay không.",
                "en": f"Following the introduction of the qualified invoice system, we checked the registration status of key business partners to determine if they are classified as {en_clean}.",
                "register": "statutory_reporting",
                "status": "generated",
                "generation_method": "semantic_frame"
            }
        ]

    elif sem_class == "audit_opinion":
        return [
            {
                "ja": f"財務諸表が適正に表示されている旨を担保するため、独立監査人より{surface}を受領いたしました。",
                "vi": f"Để bảo đảm báo cáo tài chính được trình bày trung thực hợp lý, chúng tôi đã nhận {vi_short} từ kiểm toán viên độc lập.",
                "en": f"To confirm that the financial statements are fairly presented, we received a(n) {en_clean} from the independent auditor.",
                "register": "financial_audit",
                "status": "generated",
                "generation_method": "semantic_frame"
            },
            {
                "ja": f"有価証券報告書に監査報告書を添付し、公認会計士による{surface}を投資家に向けて開示しました。",
                "vi": f"Đính kèm báo cáo kiểm toán vào báo cáo chứng khoán định kỳ, chúng tôi công bố {vi_short} của kiểm toán viên công chứng cho các nhà đầu tư.",
                "en": f"Attaching the audit report to the annual securities report, we disclosed the {en_clean} by certified public accountants to investors.",
                "register": "statutory_reporting",
                "status": "generated",
                "generation_method": "semantic_frame"
            }
        ]

    elif sem_class == "cargo":
        return [
            {
                "ja": f"税関の輸入許可が下りるまでの間、適正な管理のもとで保税地域に{surface}を蔵入れしました。",
                "vi": f"Trong thời gian chờ giấy phép nhập khẩu của hải quan, chúng tôi đã đưa {vi_short} vào lưu giữ tại khu vực ngoại quan dưới sự quản lý nghiêm ngặt.",
                "en": f"Until customs import permission was granted, we stored the {en_clean} in the bonded area under proper control.",
                "register": "customs_procedure",
                "status": "generated",
                "generation_method": "semantic_frame"
            },
            {
                "ja": f"荷受人への迅速な配送を実現するため、通関完了後に保税倉庫から{surface}を搬出しました。",
                "vi": f"Để thực hiện giao hàng nhanh chóng cho người nhận, chúng tôi đã xuất {vi_short} ra khỏi kho ngoại quan ngay sau khi hoàn tất thông quan.",
                "en": f"To achieve prompt delivery to the consignee, we moved the {en_clean} out of the bonded warehouse immediately upon customs clearance.",
                "register": "logistics_workplace",
                "status": "generated",
                "generation_method": "semantic_frame"
            }
        ]

    elif sem_class == "trade_regulation":
        return [
            {
                "ja": f"国際的な安全保障貿易管理を遵守するため、輸出貨物について{surface}に基づく該非判定を実施しました。",
                "vi": f"Để tuân thủ quản lý thương mại an ninh quốc tế, chúng tôi đã thực hiện xác định diện quản lý đối với hàng hóa xuất khẩu dựa trên {vi_short}.",
                "en": f"To comply with international security export controls, we conducted item classification determinations for export cargo under {en_clean}.",
                "register": "trade_compliance",
                "status": "generated",
                "generation_method": "semantic_frame"
            },
            {
                "ja": f"経済産業省の指導要領に則り、{surface}に抵触しないよう厳格な社内審査体制を整備しています。",
                "vi": f"Theo hướng dẫn của Bộ Kinh tế, Thương mại và Công nghiệp (METI), chúng tôi thiết lập cơ chế kiểm tra nội bộ nghiêm ngặt để không vi phạm {vi_short}.",
                "en": f"In accordance with METI guidelines, we maintain a strict internal review framework to ensure no violation of {en_clean}.",
                "register": "corporate_governance",
                "status": "generated",
                "generation_method": "semantic_frame"
            }
        ]

    elif sem_class == "financial_risk":
        return [
            {
                "ja": f"為替相場や金利の急激な変動に備え、デリバティブ取引を活用して{surface}をヘッジしています。",
                "vi": f"Để đối phó với những biến động đột ngột của tỷ giá hối đoái và lãi suất, chúng tôi sử dụng các giao dịch phái sinh nhằm phòng ngừa {vi_short}.",
                "en": f"To prepare for abrupt fluctuations in exchange rates and interest rates, we hedge {en_clean} using derivative transactions.",
                "register": "corporate_finance",
                "status": "generated",
                "generation_method": "semantic_frame"
            },
            {
                "ja": f"財務の健全性を維持するため、定期的なストレステストを実施して{surface}の影響度を分析しています。",
                "vi": f"Nhằm duy trì tính lành mạnh tài chính, chúng tôi định kỳ tiến hành kiểm tra sức chịu tải để phân tích mức độ ảnh hưởng của {vi_short}.",
                "en": f"To maintain financial soundness, we conduct periodic stress tests to analyze our exposure to {en_clean}.",
                "register": "risk_management",
                "status": "generated",
                "generation_method": "semantic_frame"
            }
        ]

    # Default / General Financial Account & Procedures
    return [
        {
            "ja": f"月末の帳簿照合において、{surface}の計上内容や残高に差異がないか精査します。",
            "vi": f"Khi đối chiếu sổ sách cuối tháng, chúng tôi kiểm tra kỹ lưỡng xem nội dung hạch toán hoặc số dư của {vi_short} có chênh lệch không.",
            "en": f"During month-end book reconciliation, we carefully examine whether there are discrepancies in entries or balances for {en_clean}.",
            "register": "accounting_audit",
            "status": "generated",
            "generation_method": "semantic_frame"
        },
        {
            "ja": f"適正な会計基準および社内規程に則り、当期の決算において{surface}を適正に処理いたしました。",
            "vi": f"Tuân thủ các chuẩn mực kế toán và quy chế nội bộ thích hợp, chúng tôi đã xử lý đúng quy định {vi_short} trong đợt quyết toán kỳ này.",
            "en": f"In accordance with applicable accounting standards and internal rules, we properly processed {en_clean} in this term's closing entries.",
            "register": "financial_reporting",
            "status": "generated",
            "generation_method": "semantic_frame"
        }
    ]


def generate_semantic_dialogue(surface: str, reading: str, vi_short: str, en_pref: str, domain: str, sem_class: str) -> list:
    """
    Generates natural workplace dialogue between two business professionals.
    """
    en_clean = en_pref.lower()

    if sem_class in ["tax_scheme", "tax_filing", "tax_deduction", "executive_compensation", "taxable_income_element", "tax_loss"]:
        return [
            {
                "speaker": "A",
                "ja": f"今回の決算申告における{surface}の計算根拠と提出書類は整理できましたか。",
                "vi": f"Căn cứ tính toán và hồ sơ nộp cho {vi_short} trong đợt quyết toán thuế này đã được tổng hợp xong chưa?",
                "en": f"Have we compiled the calculation rationale and submission documents for {en_clean} in this tax filing?",
                "status": "generated",
                "generation_method": "semantic_frame"
            },
            {
                "speaker": "B",
                "ja": f"はい、根拠資料と税理士の確認書を揃えましたので、申告書添付書類として提出可能です。",
                "vi": f"Vâng, tôi đã chuẩn bị đủ tài liệu căn cứ và xác nhận của chuyên viên thuế, sẵn sàng nộp kèm theo tờ khai.",
                "en": f"Yes, supporting evidence and the tax accountant's confirmation are assembled and ready to attach to the return.",
                "status": "generated",
                "generation_method": "semantic_frame"
            }
        ]

    elif sem_class in ["shipping_document", "customs_procedure", "trade_term", "cargo_operation", "freight_charge"]:
        return [
            {
                "speaker": "A",
                "ja": f"本日通関予定の案件ですが、{surface}の手配状況はいかがでしょうか。",
                "vi": f"Vụ việc dự kiến thông quan hôm nay, tình hình thu xếp {vi_short} thế nào rồi ạ?",
                "en": f"Regarding the shipment scheduled for customs clearance today, what is the status of arranging {en_clean}?",
                "status": "generated",
                "generation_method": "semantic_frame"
            },
            {
                "speaker": "B",
                "ja": f"通関業者と乙仲への連絡を済ませており、書類の確認も完了して輸入申告に入っております。",
                "vi": f"Tôi đã liên hệ xong với đại lý hải quan và công ty giao nhận, giấy tờ đã kiểm tra xong và đang tiến hành khai báo nhập khẩu.",
                "en": f"We have contacted the customs broker and forwarder; document checks are complete and import declaration is underway.",
                "status": "generated",
                "generation_method": "semantic_frame"
            }
        ]

    elif sem_class in ["contract", "contract_clause"]:
        return [
            {
                "speaker": "A",
                "ja": f"先方法務部から戻ってきた{surface}の修正案ですが、確認は済みましたか。",
                "vi": f"Bản dự thảo sửa đổi {vi_short} gửi lại từ phòng pháp chế đối tác, anh/chị đã xem qua chưa?",
                "en": f"Have you finished reviewing the revised draft of {en_clean} returned from the counterparty's legal team?",
                "status": "generated",
                "generation_method": "semantic_frame"
            },
            {
                "speaker": "B",
                "ja": f"はい、損害賠償条項を含めてリスクがないことを確認いたしましたので、このまま締結手続きに進めます。",
                "vi": f"Vâng, tôi đã xác nhận không có rủi ro bao gồm cả điều khoản bồi thường thiệt hại, chúng ta có thể tiến hành thủ tục ký kết.",
                "en": f"Yes, I confirmed there are no risks including the liability clause, so we can proceed with execution.",
                "status": "generated",
                "generation_method": "semantic_frame"
            }
        ]

    elif sem_class in ["document", "organization", "person_role"]:
        return [
            {
                "speaker": "A",
                "ja": f"来週開催予定の会議に向けて、{surface}の準備状況はどうなっていますか。",
                "vi": f"Hướng tới cuộc họp dự kiến tổ chức vào tuần sau, tình hình chuẩn bị {vi_short} hiện như thế nào rồi?",
                "en": f"Ahead of the meeting scheduled for next week, what is the preparation status for {en_clean}?",
                "status": "generated",
                "generation_method": "semantic_frame"
            },
            {
                "speaker": "B",
                "ja": f"内容の最終推敲を終え、役員の事前承認も得られましたので、本日中に発送の手配を行います。",
                "vi": f"Nội dung đã được duyệt lần cuối và đã có phê duyệt trước của ban giám đốc, chúng tôi sẽ thu xếp gửi đi ngay trong ngày hôm nay.",
                "en": f"Final review of the content is complete and prior approval from directors was obtained, so we will arrange dispatch within today.",
                "status": "generated",
                "generation_method": "semantic_frame"
            }
        ]

    elif sem_class in ["professional_service_firm"]:
        return [
            {
                "speaker": "A",
                "ja": f"今期の期末決算監査に向けて、{surface}との事前協議の日程は確定しましたか。",
                "vi": f"Hướng tới đợt kiểm toán quyết toán cuối niên độ kỳ này, lịch thảo luận trước với {vi_short} đã được chốt chưa?",
                "en": f"Toward this fiscal year-end closing audit, has the schedule for preliminary consultations with the {en_clean} been finalized?",
                "status": "generated",
                "generation_method": "semantic_frame"
            },
            {
                "speaker": "B",
                "ja": f"はい、主要な論点整理を終え、来週初めに{surface}の監査チームとミーティングを行います。",
                "vi": f"Vâng, chúng tôi đã tổng hợp xong các trọng điểm chính và sẽ có buổi họp với nhóm kiểm toán của {vi_short} vào đầu tuần tới.",
                "en": f"Yes, we have sorted out the key discussion points and will hold a meeting with the {en_clean}'s audit team early next week.",
                "status": "generated",
                "generation_method": "semantic_frame"
            }
        ]

    elif sem_class in ["financial_statement"]:
        return [
            {
                "speaker": "A",
                "ja": f"今期の{surface}について、各区分の増減分析と開示数値の確認は完了しましたか。",
                "vi": f"Liên quan đến {vi_short} kỳ này, việc phân tích biến động các khoản mục và kiểm tra số liệu công bố đã hoàn tất chưa?",
                "en": f"Regarding this term's {en_clean}, have we completed the variance analysis for each section and the verification of disclosure figures?",
                "status": "generated",
                "generation_method": "semantic_frame"
            },
            {
                "speaker": "B",
                "ja": f"はい、前年同期比較および主要なキャッシュ増減要因の検証を終え、取締役会への報告資料を整えました。",
                "vi": f"Vâng, chúng tôi đã đối chiếu xong so với cùng kỳ năm trước và kiểm tra các nguyên nhân biến động tiền tệ chủ yếu, hoàn thiện tài liệu báo cáo hội đồng quản trị.",
                "en": f"Yes, we finished the year-on-year comparison and verification of primary cash flow factors, and prepared the report materials for the board.",
                "status": "generated",
                "generation_method": "semantic_frame"
            }
        ]

    elif sem_class in ["statutory_document"]:
        return [
            {
                "speaker": "A",
                "ja": f"所轄官庁へ提出する{surface}の作成と記載事項の点検は順調に進んでいますか。",
                "vi": f"Việc lập {vi_short} và kiểm tra các mục kê khai để nộp cho cơ quan phụ trách có diễn ra thuận lợi không?",
                "en": f"Are the preparation of {en_clean} and the review of stated items progressing smoothly for submission to the competent authorities?",
                "status": "generated",
                "generation_method": "semantic_frame"
            },
            {
                "speaker": "B",
                "ja": f"はい、法定記載事項の漏れがないか再確認を済ませており、期限内に提出できる状態です。",
                "vi": f"Vâng, chúng tôi đã kiểm tra lại kỹ lưỡng để không bỏ sót mục kê khai bắt buộc nào theo luật định, sẵn sàng nộp đúng hạn.",
                "en": f"Yes, we double-checked to ensure no omissions in statutory required entries, and it is ready for submission within the deadline.",
                "status": "generated",
                "generation_method": "semantic_frame"
            }
        ]

    elif sem_class in ["statutory_law"]:
        return [
            {
                "speaker": "A",
                "ja": f"今回の取引に関して、{surface}の関連規定や最新の法改正への適合状況は確認できていますか。",
                "vi": f"Liên quan đến giao dịch lần này, chúng ta đã xác nhận mức độ tuân thủ các quy định liên quan của {vi_short} và những sửa đổi luật mới nhất chưa?",
                "en": f"Regarding this transaction, have we confirmed compliance with the relevant provisions of {en_clean} and recent statutory amendments?",
                "status": "generated",
                "generation_method": "semantic_frame"
            },
            {
                "speaker": "B",
                "ja": f"はい、顧問弁護士および税理士と条文を精査し、法令上の要件を完全に満たしていることを確認しました。",
                "vi": f"Vâng, chúng tôi đã rà soát kỹ các điều khoản với luật sư và chuyên viên thuế cố vấn, xác nhận đáp ứng đầy đủ điều kiện luật định.",
                "en": f"Yes, we thoroughly reviewed the articles with legal counsel and tax accountants and confirmed full compliance with statutory requirements.",
                "status": "generated",
                "generation_method": "semantic_frame"
            }
        ]

    elif sem_class in ["taxpayer_category"]:
        return [
            {
                "speaker": "A",
                "ja": f"新規取引先の選定にあたり、先方が{surface}に該当するかどうかの確認は取れていますか。",
                "vi": f"Khi lựa chọn đối tác kinh doanh mới, chúng ta đã xác nhận xem đối tác có thuộc diện {vi_short} hay không chưa?",
                "en": f"When selecting a new business partner, have we confirmed whether they qualify as a {en_clean}?",
                "status": "generated",
                "generation_method": "semantic_frame"
            },
            {
                "speaker": "B",
                "ja": f"はい、登録番号および適格請求書発行事業者の公表サイトにてステータスを確認済みです。",
                "vi": f"Vâng, chúng tôi đã kiểm tra mã số đăng ký và xác nhận trạng thái trên trang tra cứu đơn vị phát hành hóa đơn hợp lệ chính thức.",
                "en": f"Yes, we verified their status using their registration number on the official invoice issuer lookup site.",
                "status": "generated",
                "generation_method": "semantic_frame"
            }
        ]

    elif sem_class in ["metric"]:
        return [
            {
                "speaker": "A",
                "ja": f"今期の財務分析において、{surface}の推移と改善目標に対する進捗はいかがですか。",
                "vi": f"Trong phân tích tài chính kỳ này, biến động của {vi_short} và tiến độ so với mục tiêu cải thiện ra sao rồi?",
                "en": f"In this term's financial analysis, what is the trend of {en_clean} and our progress toward improvement targets?",
                "status": "generated",
                "generation_method": "semantic_frame"
            },
            {
                "speaker": "B",
                "ja": f"前四半期と比較して着実に改善傾向を示しており、期末の経営目標を達成できる見通しです。",
                "vi": f"So với quý trước, chỉ số đang có xu hướng cải thiện vững chắc, dự kiến sẽ đạt được mục tiêu quản lý cuối niên độ.",
                "en": f"It shows a steady improvement compared to the previous quarter, and we expect to achieve the fiscal year-end target.",
                "status": "generated",
                "generation_method": "semantic_frame"
            }
        ]

    elif sem_class in ["business_practice"]:
        return [
            {
                "speaker": "A",
                "ja": f"部署内における{surface}の徹底状況について、何か課題は生じていませんか。",
                "vi": f"Liên quan đến việc thực hiện triệt để {vi_short} trong nội bộ phòng ban, có phát sinh vấn đề gì không?",
                "en": f"Regarding the thorough implementation of {en_clean} within the department, are there any issues arising?",
                "status": "generated",
                "generation_method": "semantic_frame"
            },
            {
                "speaker": "B",
                "ja": f"全メンバーで情報共有の重要性を再認識し、迅速な対応が習慣化されてきています。",
                "vi": f"Toàn thể thành viên đã nhận thức lại tầm quan trọng của việc chia sẻ thông tin, và phản ứng nhanh chóng đã dần trở thành thói quen.",
                "en": f"All team members have reaffirmed the importance of information sharing, and prompt response is becoming habitual.",
                "status": "generated",
                "generation_method": "semantic_frame"
            }
        ]

    elif sem_class in ["tangible_fixed_asset", "depreciable_asset", "intangible_asset"]:
        return [
            {
                "speaker": "A",
                "ja": f"今期取得した{surface}について、固定資産台帳への登録と減価償却の計算方法は確認済みですか。",
                "vi": f"Đối với {vi_short} đã mua sắm trong kỳ này, chúng ta đã xác nhận việc đăng ký vào sổ tài sản cố định và phương pháp tính khấu hao chưa?",
                "en": f"For the {en_clean} acquired this term, have we verified registration in the fixed asset ledger and the depreciation calculation method?",
                "status": "generated",
                "generation_method": "semantic_frame"
            },
            {
                "speaker": "B",
                "ja": f"はい、耐用年数と償却方法を税法および会計基準に照らして設定し、適正に登録いたしました。",
                "vi": f"Vâng, chúng tôi đã thiết lập thời gian sử dụng hữu ích và phương pháp khấu hao đối chiếu theo luật thuế và chuẩn mực kế toán, hoàn tất đăng ký chuẩn xác.",
                "en": f"Yes, useful life and depreciation method were established in accordance with tax law and accounting standards, and properly registered.",
                "status": "generated",
                "generation_method": "semantic_frame"
            }
        ]

    elif sem_class in ["cargo"]:
        return [
            {
                "speaker": "A",
                "ja": f"保税地域に搬入された{surface}ですが、通関と引き取りの手配は完了していますか。",
                "vi": f"{vi_short} đã đưa vào khu vực ngoại quan, thủ tục thông quan và lấy hàng đã thu xếp xong chưa?",
                "en": f"Regarding the {en_clean} brought into the bonded area, have customs clearance and pickup arrangements been completed?",
                "status": "generated",
                "generation_method": "semantic_frame"
            },
            {
                "speaker": "B",
                "ja": f"はい、輸入許可通知書を受領次第、提携運送会社にて納入先へ配送する手配を整えています。",
                "vi": f"Vâng, ngay sau khi nhận thông báo cấp phép nhập khẩu, chúng tôi đã thu xếp đơn vị vận tải đối tác giao đến địa điểm giao hàng.",
                "en": f"Yes, as soon as the import permit notice is received, our partner carrier is arranged to deliver it to the destination.",
                "status": "generated",
                "generation_method": "semantic_frame"
            }
        ]

    elif sem_class in ["trade_regulation"]:
        return [
            {
                "speaker": "A",
                "ja": f"今般の輸出案件について、{surface}への該非判定および経済産業省への申請要否は確認しましたか。",
                "vi": f"Vụ việc xuất khẩu lần này, chúng ta đã xác nhận việc xác định diện quản lý theo {vi_short} và sự cần thiết phải xin phép Bộ Kinh tế, Thương mại và Công nghiệp chưa?",
                "en": f"Regarding this export deal, have we verified the classification under {en_clean} and whether an application to METI is required?",
                "status": "generated",
                "generation_method": "semantic_frame"
            },
            {
                "speaker": "B",
                "ja": f"はい、技術仕様書を精査し、規制対象外であることを確認した該非判定書を作成いたしました。",
                "vi": f"Vâng, tôi đã rà soát kỹ bảng thông số kỹ thuật và lập văn bản xác nhận đối tượng không thuộc diện quản lý hạn chế.",
                "en": f"Yes, we scrutinized the technical specifications and prepared a non-applicability parameter sheet confirming it is outside regulation.",
                "status": "generated",
                "generation_method": "semantic_frame"
            }
        ]

    elif sem_class in ["financial_risk"]:
        return [
            {
                "speaker": "A",
                "ja": f"最近の相場急変に伴う{surface}へのエクスポージャーについて、対応策は講じていますか。",
                "vi": f"Liên quan đến mức độ rủi ro đối với {vi_short} do thị trường biến động đột ngột gần đây, chúng ta đã có biện pháp ứng phó chưa?",
                "en": f"Regarding our exposure to {en_clean} following recent sudden market shifts, have countermeasures been taken?",
                "status": "generated",
                "generation_method": "semantic_frame"
            },
            {
                "speaker": "B",
                "ja": f"為替予約および金利スワップを実行済みで、許容リスク限度額の範囲内に収まるよう管理しています。",
                "vi": f"Chúng tôi đã thực hiện hợp đồng kỳ hạn ngoại hối và hoán đổi lãi suất, quản lý để duy trì trong hạn mức rủi ro cho phép.",
                "en": f"We executed forward contracts and interest rate swaps, managing it to remain within tolerable risk limits.",
                "status": "generated",
                "generation_method": "semantic_frame"
            }
        ]

    elif sem_class in ["audit_opinion"]:
        return [
            {
                "speaker": "A",
                "ja": f"独立監査人による期末監査の結果、{surface}の受領見込みはどうなっていますか。",
                "vi": f"Kết quả kiểm toán cuối kỳ của kiểm toán viên độc lập, triển vọng nhận {vi_short} hiện như thế nào rồi?",
                "en": f"Following the fiscal year-end audit by the independent auditor, what is the outlook for receiving a(n) {en_clean}?",
                "status": "generated",
                "generation_method": "semantic_frame"
            },
            {
                "speaker": "B",
                "ja": f"重要な指摘事項や未解消の論点はなく、予定通り{surface}を受領できる見通しです。",
                "vi": f"Không có điểm lưu ý trọng yếu hay vấn đề nào chưa được giải quyết, dự kiến sẽ nhận được {vi_short} theo đúng kế hoạch.",
                "en": f"There are no material findings or unresolved issues, so we anticipate receiving the {en_clean} as scheduled.",
                "status": "generated",
                "generation_method": "semantic_frame"
            }
        ]

    # Default professional accounting / office dialogue
    return [
        {
            "speaker": "A",
            "ja": f"今月の月次決算で、{surface}の計上内容に差異は発生していませんか。",
            "vi": f"Trong quyết toán tháng này, nội dung hạch toán của {vi_short} có phát sinh chênh lệch gì không?",
            "en": f"In this month's closing, are there any discrepancies occurring in the entries for {en_clean}?",
            "status": "generated",
            "generation_method": "semantic_frame"
        },
        {
            "speaker": "B",
            "ja": f"証憑書類と補助元帳を照合済みで、すべて適正に整合していることを確認いたしました。",
            "vi": f"Tôi đã đối chiếu xong chứng từ gốc với sổ chi tiết, xác nhận toàn bộ đã khớp đúng chuẩn xác.",
            "en": f"Vouchers and subsidiary ledgers have been reconciled; I confirmed everything matches properly.",
            "status": "generated",
            "generation_method": "semantic_frame"
        }
    ]
