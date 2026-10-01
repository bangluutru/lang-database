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
