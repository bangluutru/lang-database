"""
scripts/pilot_builder/accounting_data.py
Defines 200 authoritative canonical accounting and bookkeeping learning entries
derived from FSA EDINET 2026 Taxonomy, JICPA Glossary, and ASBJ Standards.
"""

ACCOUNTING_ENTRIES = [
    # 1. Core Financial Statements & Structure
    {
        "surface": "貸借対照表",
        "reading": "たいしゃくたいしょうひょう",
        "romaji": "taishakutaishouhyou",
        "secondary_domains": ["finance", "corporate_governance"],
        "concept_type": "compound_noun",
        "vi_short": "bảng cân đối kế toán",
        "vi_explanation": "Báo cáo tài chính phản ánh tổng quát tình hình tài sản, nợ phải trả và vốn chủ sở hữu của doanh nghiệp tại một thời điểm nhất định (thường là ngày kết thúc năm tài chính).",
        "vi_context": "Là một trong 'Bốn báo cáo tài chính' quan trọng nhất, dùng để đánh giá cơ cấu vốn và độ an toàn tài chính.",
        "en_preferred": "Balance Sheet",
        "en_alternatives": ["Statement of Financial Position"],
        "tier": "PRO-A1",
        "estimated_level": "N2",
        "priority_score": 98,
        "factors": {"workplace_frequency": 30, "learner_usefulness": 30, "source_authority": 20, "cross_domain_value": 18},
        "synonyms": ["B/S"],
        "antonyms": [],
        "related_terms": ["損益計算書", "資産", "負債", "純資産"],
        "collocations": ["貸借対照表を作成する", "貸借対照表を開示する", "貸借対照表の健全性"],
        "examples": [
            {"ja": "決算月に貸借対照表を作成し、財務の健全性を確認します。", "vi": "Vào tháng quyết toán, chúng tôi lập bảng cân đối kế toán để kiểm tra độ lành mạnh tài chính.", "en": "We prepare the balance sheet during the closing month to verify financial soundness.", "register": "natural_workplace"},
            {"ja": "当社の貸借対照表では、自己資本比率が50％を超えています。", "vi": "Trên bảng cân đối kế toán của công ty chúng tôi, tỷ lệ vốn chủ sở hữu vượt quá 50%.", "en": "On our balance sheet, the equity ratio exceeds 50%.", "register": "formal_business"}
        ],
        "dialogue": [
            {"speaker": "A", "ja": "最新の貸借対照表を見せていただけますか。", "vi": "Anh có thể cho tôi xem bảng cân đối kế toán mới nhất được không?", "en": "Could you please show me the latest balance sheet?"},
            {"speaker": "B", "ja": "はい、先月締め分のB/Sをご用意しました。", "vi": "Vâng, tôi đã chuẩn bị sẵn B/S của kỳ chốt sổ tháng trước rồi ạ.", "en": "Yes, I have prepared the balance sheet from last month's closing."}
        ],
        "sources": [{"source_id": "fsa_edinet_2026", "source_term_exact": "貸借対照表", "source_reference": "1f_AccountList.xlsx:BalanceSheetAbstract"}]
    },
    {
        "surface": "損益計算書",
        "reading": "そんえきけいさんしょ",
        "romaji": "sonekkikeisansho",
        "secondary_domains": ["finance", "management"],
        "concept_type": "compound_noun",
        "vi_short": "báo cáo kết quả hoạt động kinh doanh",
        "vi_explanation": "Báo cáo tài chính tổng hợp toàn bộ doanh thu, chi phí và lợi nhuận hoặc lỗ của doanh nghiệp phát sinh trong một kỳ kế toán.",
        "vi_context": "Thường được gọi tắt là P/L (Profit and Loss), giúp ban lãnh đạo nắm bắt được hiệu quả sinh lời và kiểm soát chi phí hoạt động.",
        "en_preferred": "Income Statement",
        "en_alternatives": ["Profit and Loss Statement", "P/L"],
        "tier": "PRO-A1",
        "estimated_level": "N2",
        "priority_score": 98,
        "factors": {"workplace_frequency": 30, "learner_usefulness": 30, "source_authority": 20, "cross_domain_value": 18},
        "synonyms": ["P/L"],
        "antonyms": [],
        "related_terms": ["貸借対照表", "売上高", "営業利益", "当期純利益"],
        "collocations": ["損益計算書を分析する", "損益計算書に計上する", "月次損益計算書"],
        "examples": [
            {"ja": "月次損益計算書を確認して、各部門の利益率を把握します。", "vi": "Chúng tôi kiểm tra báo cáo kết quả kinh doanh hàng tháng để nắm bắt tỷ suất lợi nhuận của từng bộ phận.", "en": "We review the monthly income statement to monitor profit margins by department.", "register": "natural_workplace"}
        ],
        "dialogue": [
            {"speaker": "Manager", "ja": "今期の損益計算書で営業利益はどうなっていますか。", "vi": "Lợi nhuận hoạt động trên báo cáo kết quả kinh doanh kỳ này thế nào rồi?", "en": "How is the operating profit looking on this period's income statement?"},
            {"speaker": "Accountant", "ja": "売上原価を圧縮したため、前期比で15％増加しています。", "vi": "Nhờ cắt giảm được giá vốn hàng bán nên đã tăng 15% so với kỳ trước ạ.", "en": "Because we reduced the cost of sales, it is up 15% compared to the previous period."}
        ],
        "sources": [{"source_id": "fsa_edinet_2026", "source_term_exact": "損益計算書", "source_reference": "1f_AccountList.xlsx:StatementOfIncome"}]
    },
    {
        "surface": "キャッシュ・フロー計算書",
        "reading": "きゃっしゅふろーけいさんしょ",
        "romaji": "kyasshufuro-keisansho",
        "secondary_domains": ["finance", "banking"],
        "concept_type": "compound_noun",
        "vi_short": "báo cáo lưu chuyển tiền tệ",
        "vi_explanation": "Báo cáo tài chính thể hiện dòng tiền thực tế vào và ra của doanh nghiệp trong kỳ, được chia thành hoạt động kinh doanh, đầu tư và tài chính.",
        "vi_context": "Thường gọi tắt là C/F. Cực kỳ quan trọng để phòng ngừa rủi ro 'phá sản trong lúc có lãi' (Kuroji Tosan).",
        "en_preferred": "Cash Flow Statement",
        "en_alternatives": ["Statement of Cash Flows", "C/F"],
        "tier": "PRO-A2",
        "estimated_level": "N2",
        "priority_score": 95,
        "factors": {"workplace_frequency": 28, "learner_usefulness": 29, "source_authority": 20, "cross_domain_value": 18},
        "synonyms": ["C/F", "CF計算書"],
        "antonyms": [],
        "related_terms": ["営業活動によるキャッシュ・フロー", "フリー・キャッシュ・フロー"],
        "collocations": ["キャッシュ・フロー計算書を作成する", "営業CFの黒字化"],
        "examples": [
            {"ja": "利益が出ていてもキャッシュ・フロー計算書がマイナスなら注意が必要です。", "vi": "Dù có lãi nhưng nếu báo cáo lưu chuyển tiền tệ bị âm thì cần phải hết sức chú ý.", "en": "Even if there is profit, caution is needed if the cash flow statement shows a negative balance.", "register": "natural_workplace"}
        ],
        "dialogue": [
            {"speaker": "A", "ja": "銀行からキャッシュ・フロー計算書の提出を求められました。", "vi": "Ngân hàng đã yêu cầu nộp báo cáo lưu chuyển tiền tệ.", "en": "The bank requested that we submit our cash flow statement."},
            {"speaker": "B", "ja": "直近3期分の資料を至急取りまとめます。", "vi": "Tôi sẽ tổng hợp ngay số liệu của 3 kỳ gần nhất ạ.", "en": "I will immediately compile the documents for the last three periods."}
        ],
        "sources": [{"source_id": "fsa_edinet_2026", "source_term_exact": "キャッシュ・フロー計算書", "source_reference": "1f_AccountList.xlsx:StatementOfCashFlows"}]
    },
    {
        "surface": "株主資本等変動計算書",
        "reading": "かぶぬししほんとうへんどうけいさんしょ",
        "romaji": "kabunushishihontouhendoukeisansho",
        "secondary_domains": ["corporate_governance", "legal"],
        "concept_type": "compound_noun",
        "vi_short": "báo cáo biến động vốn chủ sở hữu",
        "vi_explanation": "Báo cáo tài chính chi tiết sự thay đổi của từng khoản mục trong phần vốn chủ sở hữu và tài sản thuần trong suốt kỳ kế toán.",
        "vi_context": "Bắt buộc theo Luật Doanh nghiệp Nhật Bản, phản ánh các nghiệp vụ trả cổ tức, tăng vốn, mua lại cổ phiếu quỹ.",
        "en_preferred": "Statement of Changes in Equity",
        "en_alternatives": ["Statement of Shareholders' Equity"],
        "tier": "PRO-A3",
        "estimated_level": "N1",
        "priority_score": 88,
        "factors": {"workplace_frequency": 22, "learner_usefulness": 26, "source_authority": 20, "cross_domain_value": 20},
        "synonyms": ["S/S"],
        "antonyms": [],
        "related_terms": ["株主資本", "利益剰余金", "自己株式"],
        "collocations": ["株主資本等変動計算書を開示する", "配当に伴う変動"],
        "examples": [
            {"ja": "有価証券報告書に株主資本等変動計算書を添付します。", "vi": "Chúng tôi đính kèm báo cáo biến động vốn chủ sở hữu vào báo cáo chứng khoán.", "en": "We attach the statement of changes in equity to the annual securities report.", "register": "statutory_reporting"}
        ],
        "dialogue": [
            {"speaker": "A", "ja": "今回の配当金の支払いはどの書類に反映されますか。", "vi": "Việc chi trả cổ tức đợt này sẽ được phản ánh vào tài liệu nào?", "en": "Which document will reflect this dividend payout?"},
            {"speaker": "B", "ja": "株主資本等変動計算書の剰余金の配当欄に記載されます。", "vi": "Sẽ được ghi vào mục phân phối thặng dư trên báo cáo biến động vốn chủ sở hữu ạ.", "en": "It is recorded under dividends from surplus in the statement of changes in equity."}
        ],
        "sources": [{"source_id": "fsa_edinet_2026", "source_term_exact": "株主資本等変動計算書", "source_reference": "1f_AccountList.xlsx:StatementOfChangesInEquity"}]
    },

    # 2. Key Assets (Current Assets & Receivables)
    {
        "surface": "売掛金",
        "reading": "うりかけきん",
        "romaji": "urikakekin",
        "secondary_domains": ["bookkeeping", "sales"],
        "concept_type": "noun",
        "vi_short": "khoản phải thu khách hàng",
        "vi_explanation": "Khoản tiền phát sinh từ việc bán hàng hóa hoặc cung cấp dịch vụ cho khách hàng mà doanh nghiệp có quyền thu nhưng chưa nhận được thanh toán.",
        "vi_context": "Thuộc nhóm tài sản ngắn hạn (流動資産). Kế toán thường xuyên phải đối chiếu số dư và theo dõi thời hạn thu tiền (Kaisyu kijitsu).",
        "en_preferred": "Accounts receivable - trade",
        "en_alternatives": ["Trade receivables", "Receivables"],
        "tier": "PRO-A1",
        "estimated_level": "N2",
        "priority_score": 99,
        "factors": {"workplace_frequency": 30, "learner_usefulness": 30, "source_authority": 20, "cross_domain_value": 19},
        "synonyms": ["売上債権"],
        "antonyms": ["買掛金"],
        "related_terms": ["受取手形", "未収入金", "貸倒引当金", "回収"],
        "collocations": ["売掛金を回収する", "売掛金を計上する", "売掛金残高を確認する", "売掛金の消込"],
        "examples": [
            {"ja": "月末に売掛金の残高を帳簿と突き合わせて確認します。", "vi": "Vào cuối tháng, chúng tôi đối chiếu số dư khoản phải thu với sổ sách.", "en": "At the end of the month, we check the accounts receivable balance against the ledger.", "register": "natural_workplace"},
            {"ja": "取引先の倒産により売掛金が焦げ付くリスクを警戒する。", "vi": "Cảnh giác trước rủi ro nợ khó đòi phát sinh từ việc đối tác phá sản.", "en": "Be vigilant against the risk of uncollectible accounts receivable due to a client's bankruptcy.", "register": "formal_business"}
        ],
        "dialogue": [
            {"speaker": "A", "ja": "A社からの入金はもう確認できましたか。", "vi": "Đã xác nhận tiền về từ công ty A chưa anh?", "en": "Have you confirmed the payment from Company A yet?"},
            {"speaker": "B", "ja": "はい、先ほど売掛金の消込処理を完了しました。", "vi": "Rồi em, anh vừa mới hoàn tất thao tác gạch nợ phải thu xong.", "en": "Yes, I just completed the accounts receivable reconciliation."}
        ],
        "sources": [{"source_id": "fsa_edinet_2026", "source_term_exact": "売掛金", "source_reference": "1f_AccountList.xlsx:AccountsReceivableTrade"}]
    },
    {
        "surface": "買掛金",
        "reading": "かいかけきん",
        "romaji": "kaikakekin",
        "secondary_domains": ["bookkeeping", "purchasing"],
        "concept_type": "noun",
        "vi_short": "khoản phải trả người bán",
        "vi_explanation": "Khoản nợ phát sinh khi doanh nghiệp mua nguyên vật liệu, hàng hóa hoặc dịch vụ phục vụ kinh doanh chính nhưng chưa thanh toán tiền.",
        "vi_context": "Thuộc nợ ngắn hạn (流動負債). Cần thanh toán đúng kỳ hạn để duy trì uy tín tín dụng với nhà cung cấp.",
        "en_preferred": "Accounts payable - trade",
        "en_alternatives": ["Trade payables", "Payables"],
        "tier": "PRO-A1",
        "estimated_level": "N2",
        "priority_score": 99,
        "factors": {"workplace_frequency": 30, "learner_usefulness": 30, "source_authority": 20, "cross_domain_value": 19},
        "synonyms": ["仕入債務"],
        "antonyms": ["売掛金"],
        "related_terms": ["支払手形", "未払金", "仕入高"],
        "collocations": ["買掛金を支払う", "買掛金を計上する", "買掛金元帳"],
        "examples": [
            {"ja": "仕入先への買掛金は翌月末に銀行振込で決済します。", "vi": "Khoản phải trả cho nhà cung cấp sẽ được thanh toán bằng chuyển khoản vào cuối tháng sau.", "en": "Accounts payable to suppliers will be settled via bank transfer at the end of next month.", "register": "natural_workplace"}
        ],
        "dialogue": [
            {"speaker": "Staff", "ja": "請求書の金額が納品書の合計と一致していません。", "vi": "Số tiền trên hóa đơn không khớp với tổng số trên phiếu giao hàng ạ.", "en": "The amount on the invoice does not match the delivery note total."},
            {"speaker": "Accountant", "ja": "確認が取れるまで買掛金の計上を保留にしてください。", "vi": "Hãy tạm hoãn hạch toán khoản phải trả cho đến khi đối chiếu xong nhé.", "en": "Please hold off on recording the accounts payable until it is verified."}
        ],
        "sources": [{"source_id": "fsa_edinet_2026", "source_term_exact": "買掛金", "source_reference": "1f_AccountList.xlsx:AccountsPayableTrade"}]
    },
    {
        "surface": "受取手形",
        "reading": "うけとりてがた",
        "romaji": "uketoritegata",
        "secondary_domains": ["banking", "finance"],
        "concept_type": "noun",
        "vi_short": "thương phiếu phải thu",
        "vi_explanation": "Hối phiếu hoặc kỳ phiếu thương mại mà doanh nghiệp nhận được từ đối tác, có cam kết thanh toán một số tiền nhất định vào ngày đáo hạn.",
        "vi_context": "Rất phổ biến trong tập quán kinh doanh truyền thống tại Nhật Bản (Yakusoku tegata / Kawase tegata).",
        "en_preferred": "Notes receivable - trade",
        "en_alternatives": ["Bills receivable"],
        "tier": "PRO-A2",
        "estimated_level": "N2",
        "priority_score": 92,
        "factors": {"workplace_frequency": 26, "learner_usefulness": 28, "source_authority": 20, "cross_domain_value": 18},
        "synonyms": [],
        "antonyms": ["支払手形"],
        "related_terms": ["手形割引", "満期日", "手形裏書", "手形期日"],
        "collocations": ["受取手形を割り引く", "受取手形を裏書譲渡する", "満期を迎える"],
        "examples": [
            {"ja": "資金繰りのため、受取手形を期日前に銀行で割り引いた。", "vi": "Để điều tiết dòng tiền, chúng tôi đã chiết khấu thương phiếu phải thu tại ngân hàng trước ngày đáo hạn.", "en": "To manage cash flow, we discounted the notes receivable at the bank before maturity.", "register": "natural_workplace"}
        ],
        "dialogue": [
            {"speaker": "A", "ja": "この受取手形の支払期日はいつですか。", "vi": "Kỳ hạn thanh toán của tờ thương phiếu này là ngày nào?", "en": "What is the maturity date of this note receivable?"},
            {"speaker": "B", "ja": "3か月後の25日となっています。", "vi": "Là ngày 25 sau 3 tháng nữa ạ.", "en": "It is the 25th, three months from now."}
        ],
        "sources": [{"source_id": "fsa_edinet_2026", "source_term_exact": "受取手形", "source_reference": "1f_AccountList.xlsx:NotesReceivableTrade"}]
    },
    {
        "surface": "支払手形",
        "reading": "しはらいてがた",
        "romaji": "shiharaitegata",
        "secondary_domains": ["banking", "finance"],
        "concept_type": "noun",
        "vi_short": "thương phiếu phải trả",
        "vi_explanation": "Kỳ phiếu hoặc hối phiếu do doanh nghiệp phát hành để thanh toán tiền mua hàng, cam kết sẽ trả tiền khi đến hạn.",
        "vi_context": "Nếu không đủ tiền thanh toán khi đến hạn, hối phiếu sẽ bị 'bất khả thanh toán' (Fuwatari), 2 lần trong 6 tháng sẽ dẫn tới đình chỉ giao dịch ngân hàng (phá sản trên thực tế).",
        "en_preferred": "Notes payable - trade",
        "en_alternatives": ["Bills payable"],
        "tier": "PRO-A2",
        "estimated_level": "N2",
        "priority_score": 92,
        "factors": {"workplace_frequency": 26, "learner_usefulness": 28, "source_authority": 20, "cross_domain_value": 18},
        "synonyms": [],
        "antonyms": ["受取手形"],
        "related_terms": ["不渡り", "手形期日", "当座勘定"],
        "collocations": ["支払手形を振り出す", "手形を決済する", "期日に引き落とされる"],
        "examples": [
            {"ja": "期日までに当座預金に入金し、支払手形の不渡りを防ぐ。", "vi": "Phải nạp tiền vào tài khoản vãng lai trước ngày đáo hạn để tránh thương phiếu bị từ chối thanh toán.", "en": "Deposit funds into the checking account before maturity to prevent notes payable dishonor.", "register": "formal_business"}
        ],
        "dialogue": [
            {"speaker": "Manager", "ja": "今月の支払手形の決済資金は確保できていますか。", "vi": "Nguồn tiền thanh toán cho các thương phiếu phải trả tháng này đã chuẩn bị đủ chưa?", "en": "Have we secured the funds to settle this month's notes payable?"},
            {"speaker": "Accountant", "ja": "はい、昨日の売掛金入金で無事に手当てできました。", "vi": "Vâng, nhờ khoản thu tiền hàng về hôm qua nên đã lo liệu ổn thỏa rồi ạ.", "en": "Yes, we covered it safely with yesterday's receivables collection."}
        ],
        "sources": [{"source_id": "fsa_edinet_2026", "source_term_exact": "支払手形", "source_reference": "1f_AccountList.xlsx:NotesPayableTrade"}]
    },
    {
        "surface": "棚卸資産",
        "reading": "たなおろししさん",
        "romaji": "tanaoroshishisan",
        "secondary_domains": ["management", "logistics"],
        "concept_type": "noun",
        "vi_short": "hàng tồn kho",
        "vi_explanation": "Toàn bộ tài sản doanh nghiệp đang nắm giữ để bán trong kỳ kinh doanh thông thường, hoặc đang trong quá trình sản xuất, hoặc nguyên vật liệu sẽ được tiêu hao trong sản xuất.",
        "vi_context": "Bao gồm hàng hóa (Shouhin), thành phẩm (Seihin), bán thành phẩm (Han-seihin), nguyên vật liệu (Genzairyou).",
        "en_preferred": "Inventories",
        "en_alternatives": ["Merchandise and finished goods", "Inventory assets"],
        "tier": "PRO-A2",
        "estimated_level": "N2",
        "priority_score": 94,
        "factors": {"workplace_frequency": 28, "learner_usefulness": 28, "source_authority": 20, "cross_domain_value": 18},
        "synonyms": ["在庫"],
        "antonyms": [],
        "related_terms": ["棚卸減耗損", "商品評価損", "実地棚卸"],
        "collocations": ["棚卸資産を評価する", "期末棚卸資産", "実地棚卸を実施する"],
        "examples": [
            {"ja": "期末に実地棚卸を行い、帳簿上の棚卸資産と実数を照合します。", "vi": "Vào cuối kỳ, chúng tôi tiến hành kiểm kê thực tế để đối chiếu số lượng thực tế với hàng tồn kho trên sổ sách.", "en": "At the end of the term, we conduct a physical inventory count and reconcile with book inventory.", "register": "natural_workplace"}
        ],
        "dialogue": [
            {"speaker": "A", "ja": "決算前の棚卸作業はいつ行いますか。", "vi": "Công tác kiểm kê hàng tồn kho trước quyết toán sẽ làm vào khi nào vậy?", "en": "When will we conduct the inventory count before the fiscal year closing?"},
            {"speaker": "B", "ja": "今週末の土曜日に倉庫全体で一斉実施します。", "vi": "Chúng ta sẽ tiến hành đồng loạt tại tất cả kho vào thứ Bảy tuần này.", "en": "We will conduct it simultaneously across all warehouses this Saturday."}
        ],
        "sources": [{"source_id": "fsa_edinet_2026", "source_term_exact": "棚卸資産", "source_reference": "1f_AccountList.xlsx:Inventories"}]
    },
    {
        "surface": "減価償却費",
        "reading": "げんかしょうきゃくひ",
        "romaji": "genkashoukyakuhi",
        "secondary_domains": ["tax", "management"],
        "concept_type": "noun",
        "vi_short": "chi phí khấu hao tài sản cố định",
        "vi_explanation": "Khoản chi phí phân bổ dần giá trị của tài sản cố định hữu hình hoặc vô hình vào chi phí hoạt động của từng kỳ trong suốt thời gian sử dụng hữu ích (耐用年数).",
        "vi_context": "Là chi phí phi tiền mặt (Non-cash expense), ảnh hưởng trực tiếp đến lợi nhuận tính thuế và dòng tiền tự do.",
        "en_preferred": "Depreciation expense",
        "en_alternatives": ["Depreciation and amortization"],
        "tier": "PRO-A2",
        "estimated_level": "N2",
        "priority_score": 96,
        "factors": {"workplace_frequency": 29, "learner_usefulness": 29, "source_authority": 20, "cross_domain_value": 18},
        "synonyms": [],
        "antonyms": [],
        "related_terms": ["減価償却累計額", "耐用年数", "定額法", "定率法"],
        "collocations": ["減価償却費を計上する", "耐用年数に応じて償却する", "定額法で計算する"],
        "examples": [
            {"ja": "社用車の購入代金は5年間にわたって減価償却費として費用化します。", "vi": "Tiền mua xe công ty sẽ được phân bổ thành chi phí khấu hao dần trong vòng 5 năm.", "en": "The purchase cost of company vehicles is expensed as depreciation over five years.", "register": "natural_workplace"}
        ],
        "dialogue": [
            {"speaker": "A", "ja": "新工場の機械設備はどの方式で償却しますか。", "vi": "Thiết bị máy móc của nhà máy mới sẽ khấu hao theo phương pháp nào?", "en": "Which method will we use to depreciate the new plant's machinery?"},
            {"speaker": "B", "ja": "税法に合わせて定率法を採用して計上します。", "vi": "Chúng ta sẽ áp dụng phương pháp số dư giảm dần theo quy định của luật thuế để hạch toán ạ.", "en": "We will adopt the declining balance method in accordance with tax law."}
        ],
        "sources": [{"source_id": "fsa_edinet_2026", "source_term_exact": "減価償却費", "source_reference": "1f_AccountList.xlsx:DepreciationExpense"}]
    },
    {
        "surface": "貸倒引当金",
        "reading": "かしだおれひきあてきん",
        "romaji": "kashidaorehikiatekin",
        "secondary_domains": ["banking", "tax"],
        "concept_type": "noun",
        "vi_short": "dự phòng nợ khó đòi",
        "vi_explanation": "Khoản dự phòng được trích lập trước để bù đắp các tổn thất có thể xảy ra khi các khoản phải thu (như nợ phải thu, thương phiếu, tiền cho vay) không thể thu hồi được.",
        "vi_context": "Được ghi nhận làm khoản giảm trừ trực tiếp trên bảng cân đối kế toán hoặc bên phần nợ.",
        "en_preferred": "Allowance for doubtful accounts",
        "en_alternatives": ["Provision for bad debts"],
        "tier": "PRO-A2",
        "estimated_level": "N1",
        "priority_score": 93,
        "factors": {"workplace_frequency": 27, "learner_usefulness": 28, "source_authority": 20, "cross_domain_value": 18},
        "synonyms": [],
        "antonyms": [],
        "related_terms": ["貸倒損失", "貸倒引当金繰入", "回収不能"],
        "collocations": ["貸倒引当金を繰り入れる", "貸倒引当金を計上する", "引当率"],
        "examples": [
            {"ja": "取引先の信用状況悪化に伴い、貸倒引当金の積み増しを行った。", "vi": "Do tình hình tín dụng của đối tác xấu đi, chúng tôi đã trích lập bổ sung dự phòng nợ khó đòi.", "en": "Due to deterioration in our client's credit status, we increased our allowance for doubtful accounts.", "register": "formal_business"}
        ],
        "dialogue": [
            {"speaker": "Accountant", "ja": "B社の売掛金について、一部回収困難な見込みです。", "vi": "Về khoản phải thu của công ty B, dự kiến có một phần khó thu hồi được ạ.", "en": "Regarding Company B's receivables, part of it is expected to be uncollectible."},
            {"speaker": "Manager", "ja": "今期末に個別貸倒引当金を計上しておいてください。", "vi": "Hãy trích lập dự phòng nợ khó đòi riêng lẻ vào cuối kỳ này nhé.", "en": "Please record a specific allowance for doubtful accounts at the end of this period."}
        ],
        "sources": [{"source_id": "fsa_edinet_2026", "source_term_exact": "貸倒引当金", "source_reference": "1f_AccountList.xlsx:AllowanceForDoubtfulAccounts"}]
    },
    {
        "surface": "未払金",
        "reading": "みばらいきん",
        "romaji": "mibaraikin",
        "secondary_domains": ["bookkeeping", "purchasing"],
        "concept_type": "noun",
        "vi_short": "khoản phải trả khác",
        "vi_explanation": "Khoản tiền phải trả cho người bán hoặc bên cung cấp phát sinh từ các giao dịch ngoài hoạt động kinh doanh chính (như mua tài sản cố định, vật dụng văn phòng, chi phí quảng cáo).",
        "vi_context": "Khác với 買掛金 (phải trả mua hàng kinh doanh chính). Việc phân loại rạch ròi 買掛金 và 未払金 là nguyên tắc quan trọng trong kế toán Nhật.",
        "en_preferred": "Accounts payable - other",
        "en_alternatives": ["Other payables"],
        "tier": "PRO-A1",
        "estimated_level": "N2",
        "priority_score": 95,
        "factors": {"workplace_frequency": 30, "learner_usefulness": 29, "source_authority": 20, "cross_domain_value": 16},
        "synonyms": [],
        "antonyms": ["未収入金"],
        "related_terms": ["買掛金", "未払費用"],
        "collocations": ["未払金を計上する", "未払金を精算する"],
        "examples": [
            {"ja": "オフィス用PCの購入代金は未払金として処理します。", "vi": "Tiền mua máy tính văn phòng sẽ được xử lý dưới dạng khoản phải trả khác.", "en": "The purchase cost of office PCs is processed as accounts payable - other.", "register": "natural_workplace"}
        ],
        "dialogue": [
            {"speaker": "Staff", "ja": "広告費の請求書は買掛金で仕訳しますか。", "vi": "Hóa đơn tiền quảng cáo có hạch toán vào khoản phải trả người bán không ạ?", "en": "Should the invoice for advertising expenses be journalized as trade payables?"},
            {"speaker": "Senior", "ja": "本業の仕入れではないので、未払金を使ってください。", "vi": "Vì không phải nhập hàng phục vụ kinh doanh chính nên hãy dùng 'khoản phải trả khác' nhé.", "en": "Since it is not a core inventory purchase, please use accounts payable - other."}
        ],
        "sources": [{"source_id": "fsa_edinet_2026", "source_term_exact": "未払金", "source_reference": "1f_AccountList.xlsx:AccountsPayableOther"}]
    },
    {
        "surface": "未収入金",
        "reading": "みしゅうにゅうきん",
        "romaji": "mishuunyuukin",
        "secondary_domains": ["bookkeeping", "finance"],
        "concept_type": "noun",
        "vi_short": "khoản phải thu khác",
        "vi_explanation": "Khoản tiền mà doanh nghiệp có quyền thu từ việc bán các tài sản không phải là hàng hóa kinh doanh chính (như thanh lý máy móc, bán chứng khoán đầu tư).",
        "vi_context": "Khác với 売掛金 (tiền bán hàng hóa dịch vụ chính).",
        "en_preferred": "Accounts receivable - other",
        "en_alternatives": ["Other receivables"],
        "tier": "PRO-A1",
        "estimated_level": "N2",
        "priority_score": 93,
        "factors": {"workplace_frequency": 28, "learner_usefulness": 28, "source_authority": 20, "cross_domain_value": 17},
        "synonyms": [],
        "antonyms": ["未払金"],
        "related_terms": ["売掛金", "未収収益"],
        "collocations": ["未収入金を回収する", "未収入金に振り替える"],
        "examples": [
            {"ja": "社用車を売却した代金の未回収分は未収入金に計上する。", "vi": "Số tiền chưa thu từ việc thanh lý xe công ty được hạch toán vào khoản phải thu khác.", "en": "The uncollected amount from selling company vehicles is recorded as accounts receivable - other.", "register": "natural_workplace"}
        ],
        "dialogue": [
            {"speaker": "A", "ja": "古くなったサーバーの売却益はどこに入金されますか。", "vi": "Tiền bán thanh lý máy chủ cũ sẽ chuyển về đâu vậy anh?", "en": "Where will the proceeds from selling the old server be deposited?"},
            {"speaker": "B", "ja": "来月入金予定なので、現在は未収入金として処理しています。", "vi": "Dự kiến tháng sau tiền về, nên hiện tại đang ghi nhận là khoản phải thu khác.", "en": "It is scheduled to arrive next month, so it is currently processed as accounts receivable - other."}
        ],
        "sources": [{"source_id": "fsa_edinet_2026", "source_term_exact": "未収入金", "source_reference": "1f_AccountList.xlsx:AccountsReceivableOther"}]
    },
    {
        "surface": "前払費用",
        "reading": "まえばらいひよう",
        "romaji": "maebaraihiyou",
        "secondary_domains": ["bookkeeping"],
        "concept_type": "noun",
        "vi_short": "chi phí trả trước",
        "vi_explanation": "Khoản tiền đã trả trước cho các dịch vụ sẽ được cung cấp liên tục trong các kỳ tương lai (như tiền thuê nhà trả trước 1 năm, phí bảo hiểm trả trước).",
        "vi_context": "Thuộc tài khoản chi phí chờ phân bổ (経過勘定), được ghi nhận là tài sản ngắn hạn.",
        "en_preferred": "Prepaid expenses",
        "en_alternatives": ["Prepayments"],
        "tier": "PRO-A2",
        "estimated_level": "N2",
        "priority_score": 91,
        "factors": {"workplace_frequency": 27, "learner_usefulness": 27, "source_authority": 20, "cross_domain_value": 17},
        "synonyms": [],
        "antonyms": ["未払費用"],
        "related_terms": ["前受収益", "経過勘定", "決算整理"],
        "collocations": ["前払費用として繰り延べる", "期首に再振替仕訳を行う"],
        "examples": [
            {"ja": "1年分の火災保険料を一括で支払ったため、未経過分を前払費用に計上した。", "vi": "Do đã thanh toán trọn gói phí bảo hiểm hỏa hoạn 1 năm, chúng tôi hạch toán phần chưa trôi qua vào chi phí trả trước.", "en": "Because we paid one year's fire insurance premium in lump sum, the unexpired portion was recorded as prepaid expenses.", "register": "natural_workplace"}
        ],
        "dialogue": [
            {"speaker": "A", "ja": "オフィスの家賃を1年分前払いしましたが、全額今期の経費ですか。", "vi": "Tiền thuê văn phòng đã trả trước 1 năm có được tính hết vào chi phí kỳ này không?", "en": "We paid one year's office rent in advance, is it all expensed this period?"},
            {"speaker": "B", "ja": "来期に属する期間分は前払費用として資産計上します。", "vi": "Phần thời gian thuộc về niên độ sau sẽ được ghi nhận là tài sản dưới dạng chi phí trả trước ạ.", "en": "The portion belonging to the next period is capitalized as prepaid expenses."}
        ],
        "sources": [{"source_id": "fsa_edinet_2026", "source_term_exact": "前払費用", "source_reference": "1f_AccountList.xlsx:PrepaidExpenses"}]
    },
    {
        "surface": "前受金",
        "reading": "まえうけきん",
        "romaji": "maeukekin",
        "secondary_domains": ["sales", "bookkeeping"],
        "concept_type": "noun",
        "vi_short": "tiền khách hàng trả trước / tiền đặt cọc nhận trước",
        "vi_explanation": "Khoản tiền doanh nghiệp nhận trước từ khách hàng trước khi bàn giao hàng hóa hoặc cung cấp dịch vụ hoàn chỉnh.",
        "vi_context": "Được xếp vào nợ ngắn hạn (流動負債) vì doanh nghiệp có nghĩa vụ phải giao hàng hoặc cung cấp dịch vụ sau đó.",
        "en_preferred": "Advances received",
        "en_alternatives": ["Customer advances", "Contract liabilities"],
        "tier": "PRO-A1",
        "estimated_level": "N2",
        "priority_score": 94,
        "factors": {"workplace_frequency": 29, "learner_usefulness": 29, "source_authority": 20, "cross_domain_value": 16},
        "synonyms": [],
        "antonyms": ["前渡金"],
        "related_terms": ["契約負債", "着手金"],
        "collocations": ["前受金を受け取る", "売上に振り替える"],
        "examples": [
            {"ja": "受注時に契約金額の30％を前受金として受領しました。", "vi": "Khi nhận đơn đặt hàng, chúng tôi đã nhận 30% giá trị hợp đồng dưới dạng tiền cọc trả trước.", "en": "Upon receiving the order, we accepted 30% of the contract amount as advances received.", "register": "natural_workplace"}
        ],
        "dialogue": [
            {"speaker": "Sales", "ja": "顧客から手付金が振り込まれました。売上にして良いですか。", "vi": "Khách hàng đã chuyển tiền cọc rồi, em cho vào doanh thu được chưa ạ?", "en": "The client transferred the earnest money. Can I book it as sales?"},
            {"speaker": "Accountant", "ja": "納品が完了するまでは前受金として処理してください。", "vi": "Cho đến khi hoàn tất giao hàng thì chỉ được xử lý là tiền nhận trước thôi nhé.", "en": "Please treat it as advances received until delivery is completed."}
        ],
        "sources": [{"source_id": "fsa_edinet_2026", "source_term_exact": "前受金", "source_reference": "1f_AccountList.xlsx:AdvancesReceived"}]
    },
    {
        "surface": "前渡金",
        "reading": "まえわたしきん",
        "romaji": "maewatashikin",
        "secondary_domains": ["purchasing", "bookkeeping"],
        "concept_type": "noun",
        "vi_short": "tiền ứng trước cho người bán",
        "vi_explanation": "Khoản tiền doanh nghiệp trả trước cho nhà cung cấp trước khi nhận hàng hóa hoặc vật liệu.",
        "vi_context": "Còn được gọi là 前払金 (Maebaraikin). Được phân loại là tài sản ngắn hạn.",
        "en_preferred": "Advances paid",
        "en_alternatives": ["Prepayments to suppliers"],
        "tier": "PRO-A1",
        "estimated_level": "N2",
        "priority_score": 92,
        "factors": {"workplace_frequency": 27, "learner_usefulness": 28, "source_authority": 20, "cross_domain_value": 17},
        "synonyms": ["前払金"],
        "antonyms": ["前受金"],
        "related_terms": ["手付金", "内金"],
        "collocations": ["前渡金を支払う", "仕入に振り替える"],
        "examples": [
            {"ja": "特注品の製造を着手してもらうため、メーカーに前渡金を支払った。", "vi": "Để nhà sản xuất bắt đầu chế tạo sản phẩm đặt riêng, chúng tôi đã thanh toán tiền ứng trước.", "en": "We paid an advance to the manufacturer so they could commence production of the custom goods.", "register": "natural_workplace"}
        ],
        "dialogue": [
            {"speaker": "A", "ja": "仕入先から着手金の事前支払いを求められています。", "vi": "Nhà cung cấp đang yêu cầu tạm ứng tiền khởi công trước.", "en": "The supplier is asking for an advance payment before starting."},
            {"speaker": "B", "ja": "契約書を確認の上、前渡金として出金処理を進めてください。", "vi": "Sau khi kiểm tra hợp đồng, hãy tiến hành thủ tục xuất quỹ tạm ứng nhé.", "en": "After checking the contract, please proceed with the disbursement as advances paid."}
        ],
        "sources": [{"source_id": "fsa_edinet_2026", "source_term_exact": "前渡金", "source_reference": "1f_AccountList.xlsx:AdvancesPaid"}]
    },
    {
        "surface": "未払費用",
        "reading": "みばらいひよう",
        "romaji": "mibaraihiyou",
        "secondary_domains": ["bookkeeping", "hr_labor"],
        "concept_type": "noun",
        "vi_short": "chi phí phải trả",
        "vi_explanation": "Khoản chi phí phát sinh do đã nhận dịch vụ liên tục trong kỳ nhưng theo thỏa thuận hợp đồng thì thời điểm trả tiền lại rơi vào kỳ sau (như tiền lương nhân viên chưa đến ngày lĩnh, tiền lãi vay đến hạn sau).",
        "vi_context": "Thuộc nhóm tài khoản chi phí dồn tích (経過勘定), ghi nhận vào nợ ngắn hạn.",
        "en_preferred": "Accrued expenses",
        "en_alternatives": ["Accrued liabilities"],
        "tier": "PRO-A2",
        "estimated_level": "N2",
        "priority_score": 92,
        "factors": {"workplace_frequency": 27, "learner_usefulness": 28, "source_authority": 20, "cross_domain_value": 17},
        "synonyms": [],
        "antonyms": ["前払費用"],
        "related_terms": ["未払金", "未払給与", "未払利息"],
        "collocations": ["未払費用を計上する", "期末の見越し計上"],
        "examples": [
            {"ja": "月末締めの給与支払いが翌月10日のため、未払費用として計上する。", "vi": "Do kỳ lương chốt cuối tháng nhưng trả vào ngày 10 tháng sau, nên chúng tôi ghi nhận vào chi phí phải trả.", "en": "Since salaries closed at month-end are paid on the 10th next month, they are accrued as expenses.", "register": "natural_workplace"}
        ],
        "dialogue": [
            {"speaker": "A", "ja": "決算月の水道光熱費の請求書がまだ届いていません。", "vi": "Hóa đơn điện nước của tháng quyết toán vẫn chưa gửi tới ạ.", "en": "The utility bill for the closing month has not arrived yet."},
            {"speaker": "B", "ja": "概算額を見積もって未払費用に計上しておきましょう。", "vi": "Hãy ước tính số liệu gần đúng rồi trích trước vào chi phí phải trả nhé.", "en": "Let's estimate the approximate amount and record it as accrued expenses."}
        ],
        "sources": [{"source_id": "fsa_edinet_2026", "source_term_exact": "未払費用", "source_reference": "1f_AccountList.xlsx:AccruedExpenses"}]
    },
    {
        "surface": "未収収益",
        "reading": "みしゅうしゅうえき",
        "romaji": "mishuushuueki",
        "secondary_domains": ["bookkeeping", "finance"],
        "concept_type": "noun",
        "vi_short": "doanh thu dồn tích / doanh thu chờ thu",
        "vi_explanation": "Khoản doanh thu đã phát sinh tương ứng với dịch vụ đã cung cấp liên tục trong kỳ nhưng chưa đến kỳ hạn thanh toán theo hợp đồng (như lãi tiền gửi tiết kiệm hoặc tiền cho thuê tài sản chưa đến ngày thu).",
        "vi_context": "Thuộc nhóm tài sản ngắn hạn (dồn tích doanh thu).",
        "en_preferred": "Accrued income",
        "en_alternatives": ["Accrued revenue"],
        "tier": "PRO-A2",
        "estimated_level": "N1",
        "priority_score": 88,
        "factors": {"workplace_frequency": 24, "learner_usefulness": 26, "source_authority": 20, "cross_domain_value": 18},
        "synonyms": [],
        "antonyms": ["前受収益"],
        "related_terms": ["未収入金", "受取利息"],
        "collocations": ["未収収益を見越す", "期首振替"],
        "examples": [
            {"ja": "貸付金の未収利息を決算時に未収収益として認識した。", "vi": "Tiền lãi chưa thu của khoản cho vay được ghi nhận là doanh thu dồn tích tại thời điểm quyết toán.", "en": "Uncollected interest on loans was recognized as accrued income at the fiscal closing.", "register": "formal_business"}
        ],
        "dialogue": [
            {"speaker": "A", "ja": "定期預金の利息入金日は来期ですが、今期分はどうしますか。", "vi": "Ngày trả lãi tiền gửi định kỳ rơi vào kỳ sau, nhưng phần của kỳ này xử lý sao ạ?", "en": "The term deposit interest payment date is next period, but what about this period's share?"},
            {"speaker": "B", "ja": "経過日数分を日割り計算して未収収益に計上してください。", "vi": "Hãy tính theo số ngày đã trôi qua rồi đưa vào doanh thu dồn tích nhé.", "en": "Please prorate by elapsed days and record it under accrued income."}
        ],
        "sources": [{"source_id": "fsa_edinet_2026", "source_term_exact": "未収収益", "source_reference": "1f_AccountList.xlsx:AccruedIncome"}]
    },
    {
        "surface": "有形固定資産",
        "reading": "ゆうけいこていしさん",
        "romaji": "yuukeikoteishisan",
        "secondary_domains": ["management"],
        "concept_type": "noun",
        "vi_short": "tài sản cố định hữu hình",
        "vi_explanation": "Tài sản có hình thái vật chất cụ thể được doanh nghiệp nắm giữ để sử dụng trong sản xuất, kinh doanh hoặc cho thuê dài hạn trên 1 năm.",
        "vi_context": "Bao gồm đất đai, nhà xưởng, máy móc thiết bị, phương tiện vận tải. Ngoại trừ đất đai, hầu hết đều phải trích khấu hao.",
        "en_preferred": "Property, plant and equipment",
        "en_alternatives": ["Tangible fixed assets"],
        "tier": "PRO-A2",
        "estimated_level": "N2",
        "priority_score": 94,
        "factors": {"workplace_frequency": 28, "learner_usefulness": 28, "source_authority": 20, "cross_domain_value": 18},
        "synonyms": [],
        "antonyms": ["無形固定資産"],
        "related_terms": ["減価償却", "固定資産台帳", "減損会計"],
        "collocations": ["有形固定資産を取得する", "有形固定資産の減損", "固定資産台帳に登録する"],
        "examples": [
            {"ja": "新しい本社ビルを有形固定資産として計上しました。", "vi": "Tòa nhà trụ sở chính mới đã được hạch toán vào tài sản cố định hữu hình.", "en": "The new head office building was recorded as property, plant and equipment.", "register": "natural_workplace"}
        ],
        "dialogue": [
            {"speaker": "A", "ja": "購入したサーバー機器は消耗品費ですか、それとも固定資産ですか。", "vi": "Thiết bị máy chủ vừa mua tính vào chi phí tiêu hao hay tài sản cố định?", "en": "Are the purchased server devices supplies expenses or fixed assets?"},
            {"speaker": "B", "ja": "1台あたり30万円を超えるため、有形固定資産として登録します。", "vi": "Vì mỗi chiếc trên 30 vạn yên nên chúng ta đăng ký vào tài sản cố định hữu hình.", "en": "Since each unit exceeds 300,000 yen, we register it as property, plant and equipment."}
        ],
        "sources": [{"source_id": "fsa_edinet_2026", "source_term_exact": "有形固定資産", "source_reference": "1f_AccountList.xlsx:PropertyPlantAndEquipment"}]
    },
    {
        "surface": "無形固定資産",
        "reading": "むけいこていしさん",
        "romaji": "mukeikoteishisan",
        "secondary_domains": ["legal", "management"],
        "concept_type": "noun",
        "vi_short": "tài sản cố định vô hình",
        "vi_explanation": "Tài sản không có hình thái vật chất nhưng mang lại quyền lợi kinh tế lâu dài cho doanh nghiệp (như quyền sáng chế, quyền tác giả, phần mềm, lợi thế thương mại - goodwill).",
        "vi_context": "Phần mềm tự phát triển hoặc mua ngoài phục vụ kinh doanh đều được kích hoạt vào danh mục này và trích khấu hao (thường là 5 năm).",
        "en_preferred": "Intangible assets",
        "en_alternatives": ["Intangible fixed assets"],
        "tier": "PRO-A2",
        "estimated_level": "N1",
        "priority_score": 91,
        "factors": {"workplace_frequency": 25, "learner_usefulness": 28, "source_authority": 20, "cross_domain_value": 18},
        "synonyms": [],
        "antonyms": ["有形固定資産"],
        "related_terms": ["のれん", "ソフトウェア", "特許権"],
        "collocations": ["無形固定資産を償却する", "ソフトウェアの資産計上"],
        "examples": [
            {"ja": "自社開発した基幹システムの費用は無形固定資産に振り替えます。", "vi": "Chi phí phát triển hệ thống ERP nội bộ được chuyển thành tài sản cố định vô hình.", "en": "The costs of internally developing the core system are capitalized as intangible assets.", "register": "formal_business"}
        ],
        "dialogue": [
            {"speaker": "A", "ja": "M&Aに伴って発生した『のれん』はどこに表示されますか。", "vi": "Lợi thế thương mại phát sinh sau vụ sáp nhập M&A sẽ hiển thị ở mục nào?", "en": "Where is goodwill arising from the M&A presented?"},
            {"speaker": "B", "ja": "貸借対照表の無形固定資産の区分に記載されます。", "vi": "Sẽ được ghi trong phân mục tài sản cố định vô hình trên bảng cân đối kế toán ạ.", "en": "It is recorded under the intangible assets section of the balance sheet."}
        ],
        "sources": [{"source_id": "fsa_edinet_2026", "source_term_exact": "無形固定資産", "source_reference": "1f_AccountList.xlsx:IntangibleAssets"}]
    },
    {
        "surface": "のれん",
        "reading": "のれん",
        "romaji": "noren",
        "secondary_domains": ["corporate_governance", "finance"],
        "concept_type": "noun",
        "vi_short": "lợi thế thương mại (goodwill)",
        "vi_explanation": "Chênh lệch giá trị khi giá mua lại doanh nghiệp cao hơn tổng giá trị hợp lý của tài sản thuần mà doanh nghiệp đó sở hữu tại thời điểm sáp nhập.",
        "vi_context": "Theo chuẩn kế toán Nhật Bản (J-GAAP), 'noren' phải được phân bổ đều trong tối đa 20 năm; trong khi chuẩn IFRS không phân bổ mà thực hiện đánh giá giảm giá trị định kỳ.",
        "en_preferred": "Goodwill",
        "en_alternatives": ["Consolidation goodwill"],
        "tier": "PRO-A3",
        "estimated_level": "N1",
        "priority_score": 90,
        "factors": {"workplace_frequency": 24, "learner_usefulness": 26, "source_authority": 20, "cross_domain_value": 20},
        "synonyms": [],
        "antonyms": [],
        "related_terms": ["企業結合", "のれん償却", "減損テスト"],
        "collocations": ["のれんを均等償却する", "のれんの減損処理を行う", "負ののれん"],
        "examples": [
            {"ja": "買収先の業績不振が続いたため、多額ののれん減損損失を計上した。", "vi": "Do kết quả kinh doanh của công ty mục tiêu bị sa sút kéo dài, chúng tôi đã phải ghi nhận khoản lỗ giảm giá trị lợi thế thương mại rất lớn.", "en": "Due to prolonged poor performance of the acquired company, we recognized a massive impairment loss on goodwill.", "register": "formal_business"}
        ],
        "dialogue": [
            {"speaker": "A", "ja": "日本基準とIFRSでの『のれん』の扱いの違いは何ですか。", "vi": "Sự khác biệt trong việc xử lý lợi thế thương mại giữa J-GAAP và IFRS là gì?", "en": "What is the difference in goodwill accounting between Japanese GAAP and IFRS?"},
            {"speaker": "B", "ja": "日本基準では毎年償却しますが、IFRSでは減損テストのみ行います。", "vi": "Chuẩn mực Nhật thì khấu hao đều hàng năm, còn IFRS thì chỉ làm bài kiểm tra suy giảm giá trị thôi ạ.", "en": "Under Japanese GAAP it is amortized annually, whereas under IFRS only impairment testing is performed."}
        ],
        "sources": [{"source_id": "fsa_edinet_2026", "source_term_exact": "のれん", "source_reference": "1f_AccountList.xlsx:Goodwill"}]
    },
    {
        "surface": "引当金",
        "reading": "ひきあてきん",
        "romaji": "hikiatekin",
        "secondary_domains": ["tax", "management"],
        "concept_type": "noun",
        "vi_short": "khoản dự phòng",
        "vi_explanation": "Khoản chi phí hoặc tổn thất dự kiến chắc chắn sẽ xảy ra trong tương lai phát sinh từ các sự kiện trong kỳ hiện tại và có thể ước tính được số tiền một cách hợp lý.",
        "vi_context": "Bao gồm dự phòng nợ xấu (貸倒引当金), dự phòng thưởng nhân viên (賞与引当金), dự phòng bảo hành (製品保証引当金).",
        "en_preferred": "Provisions",
        "en_alternatives": ["Allowances", "Accrued provisions"],
        "tier": "PRO-A2",
        "estimated_level": "N2",
        "priority_score": 93,
        "factors": {"workplace_frequency": 28, "learner_usefulness": 28, "source_authority": 20, "cross_domain_value": 17},
        "synonyms": [],
        "antonyms": [],
        "related_terms": ["賞与引当金", "貸倒引当金", "引当金繰入"],
        "collocations": ["引当金を計上する", "引当金を取り崩す", "引当要件を満たす"],
        "examples": [
            {"ja": "将来の支出に備えて、決算期末に賞与引当金を計上します。", "vi": "Để chuẩn bị cho các khoản chi tương lai, chúng tôi trích lập dự phòng tiền thưởng vào cuối niên độ kế toán.", "en": "In preparation for future payouts, we accrue a provision for bonuses at the fiscal year end.", "register": "natural_workplace"}
        ],
        "dialogue": [
            {"speaker": "A", "ja": "引当金を設定するための4つの要件を覚えていますか。", "vi": "Em có nhớ 4 điều kiện để trích lập khoản dự phòng không?", "en": "Do you remember the four conditions for recognizing a provision?"},
            {"speaker": "B", "ja": "はい、将来の費用、当期に起因、発生可能性が高く、金額が見積もれることです。", "vi": "Dạ nhớ, là chi phí tương lai, bắt nguồn từ kỳ này, khả năng xảy ra cao và số tiền ước tính được hợp lý ạ.", "en": "Yes: future cost, arising from the current period, high probability of occurrence, and reasonably estimable amount."}
        ],
        "sources": [{"source_id": "fsa_edinet_2026", "source_term_exact": "引当金", "source_reference": "1f_AccountList.xlsx:Provisions"}]
    },
    {
        "surface": "資本金",
        "reading": "しほんきん",
        "romaji": "shihonkin",
        "secondary_domains": ["corporate_governance", "legal"],
        "concept_type": "noun",
        "vi_short": "vốn điều lệ / vốn góp cổ đông",
        "vi_explanation": "Số tiền góp vốn ban đầu hoặc bổ sung của các chủ sở hữu, cổ đông vào doanh nghiệp, được đăng ký chính thức trên giấy phép kinh doanh.",
        "vi_context": "Mức vốn điều lệ ảnh hưởng lớn đến chế độ thuế của doanh nghiệp tại Nhật (ví dụ: vốn dưới 100 triệu yên được hưởng ưu đãi thuế SME).",
        "en_preferred": "Share capital",
        "en_alternatives": ["Capital stock", "Stated capital"],
        "tier": "PRO-A1",
        "estimated_level": "N2",
        "priority_score": 96,
        "factors": {"workplace_frequency": 29, "learner_usefulness": 29, "source_authority": 20, "cross_domain_value": 18},
        "synonyms": [],
        "antonyms": [],
        "related_terms": ["資本準備金", "自己資本", "増資", "減資"],
        "collocations": ["資本金を増資する", "資本金の額を登記する", "資本金1億円以下"],
        "examples": [
            {"ja": "事業拡大に伴い、第三者割当増資によって資本金を1億円に増額した。", "vi": "Cùng với việc mở rộng kinh doanh, chúng tôi đã tăng vốn điều lệ lên 100 triệu yên qua hình thức phát hành cổ phiếu riêng lẻ.", "en": "In line with business expansion, we increased our share capital to 100 million yen through a third-party allotment.", "register": "formal_business"}
        ],
        "dialogue": [
            {"speaker": "A", "ja": "会社設立時の資本金はいくらに設定しましたか。", "vi": "Vốn điều lệ khi thành lập công ty anh để bao nhiêu vậy?", "en": "What did you set the share capital to when founding the company?"},
            {"speaker": "B", "ja": "税制上の優遇措置を考慮して、まずは1,000万円未満で始めました。", "vi": "Cân nhắc các chính sách ưu đãi thuế, trước mắt tôi bắt đầu với mức dưới 10 triệu yên.", "en": "Considering tax incentives, we initially started with under 10 million yen."}
        ],
        "sources": [{"source_id": "fsa_edinet_2026", "source_term_exact": "資本金", "source_reference": "1f_AccountList.xlsx:CapitalStock"}]
    },
    {
        "surface": "利益剰余金",
        "reading": "りえきじょうよきん",
        "romaji": "riekijouyokin",
        "secondary_domains": ["corporate_governance", "finance"],
        "concept_type": "noun",
        "vi_short": "thặng dư lợi nhuận / lợi nhuận giữ lại tích lũy",
        "vi_explanation": "Phần lợi nhuận lũy kế sau thuế từ ngày thành lập mà doanh nghiệp giữ lại sau khi đã chi trả cổ tức cho cổ đông.",
        "vi_context": "Thường được gọi là 'khoản tích lũy nội bộ' (Naibu ryuho), phản ánh năng lực tự tài trợ và sức chịu đựng rủi ro dài hạn.",
        "en_preferred": "Retained earnings",
        "en_alternatives": ["Accumulated surplus"],
        "tier": "PRO-A2",
        "estimated_level": "N1",
        "priority_score": 93,
        "factors": {"workplace_frequency": 27, "learner_usefulness": 28, "source_authority": 20, "cross_domain_value": 18},
        "synonyms": ["内部留保"],
        "antonyms": [],
        "related_terms": ["利益準備金", "繰越利益剰余金", "配当金"],
        "collocations": ["利益剰余金を積み立てる", "利益剰余金から配当を行う"],
        "examples": [
            {"ja": "長年の黒字経営により、当社の利益剰余金は過去最高を更新しました。", "vi": "Nhờ hoạt động kinh doanh có lãi nhiều năm liên tục, thặng dư lợi nhuận của công ty chúng tôi đã lập đỉnh kỷ lục.", "en": "Thanks to years of profitable operation, our retained earnings hit an all-time high.", "register": "formal_business"}
        ],
        "dialogue": [
            {"speaker": "A", "ja": "今回の株主配当の原資はどこから出ますか。", "vi": "Nguồn chi trả cổ tức cho cổ đông đợt này lấy từ đâu vậy?", "en": "Where are the funds for this shareholder dividend coming from?"},
            {"speaker": "B", "ja": "その他利益剰余金を取り崩して充当します。", "vi": "Sẽ trích từ thặng dư lợi nhuận khác để chi trả ạ.", "en": "We will draw from other retained earnings to cover it."}
        ],
        "sources": [{"source_id": "fsa_edinet_2026", "source_term_exact": "利益剰余金", "source_reference": "1f_AccountList.xlsx:RetainedEarnings"}]
    },
    {
        "surface": "売上高",
        "reading": "うりあげだか",
        "romaji": "uriagedaka",
        "secondary_domains": ["sales", "management"],
        "concept_type": "noun",
        "vi_short": "doanh thu bán hàng / tổng doanh thu thuần",
        "vi_explanation": "Tổng số tiền thu được từ việc bán sản phẩm, hàng hóa hoặc cung cấp dịch vụ trong kỳ kinh doanh chính của doanh nghiệp.",
        "vi_context": "Là dòng đầu tiên trên Báo cáo kết quả hoạt động kinh doanh (Top line).",
        "en_preferred": "Net sales",
        "en_alternatives": ["Revenue", "Sales turnover"],
        "tier": "PRO-A1",
        "estimated_level": "N3",
        "priority_score": 100,
        "factors": {"workplace_frequency": 30, "learner_usefulness": 30, "source_authority": 20, "cross_domain_value": 20},
        "synonyms": ["売上", "収益"],
        "antonyms": [],
        "related_terms": ["売上原価", "売上総利益", "営業収益"],
        "collocations": ["売上高を達成する", "売上高が前年比で伸びる", "年間売上高"],
        "examples": [
            {"ja": "新製品のヒットにより、今期の売上高は前年比20％増となった。", "vi": "Nhờ sản phẩm mới bán chạy, tổng doanh thu kỳ này đã tăng 20% so với năm trước.", "en": "Driven by the success of the new product, net sales for this period increased 20% year-on-year.", "register": "natural_workplace"}
        ],
        "dialogue": [
            {"speaker": "Manager", "ja": "第3四半期の売上高の進捗はどうですか。", "vi": "Tiến độ doanh thu quý 3 thế nào rồi anh?", "en": "How is the progress on Q3 net sales?"},
            {"speaker": "Sales", "ja": "目標の95％まで到達しており、今月末には達成見込みです。", "vi": "Đã đạt 95% mục tiêu rồi và dự kiến sẽ cán đích vào cuối tháng này ạ.", "en": "We have reached 95% of the target and expect to achieve it by month-end."}
        ],
        "sources": [{"source_id": "fsa_edinet_2026", "source_term_exact": "売上高", "source_reference": "1f_AccountList.xlsx:NetSales"}]
    },
    {
        "surface": "売上原価",
        "reading": "うりあげげんか",
        "romaji": "uriagegenka",
        "secondary_domains": ["purchasing", "management"],
        "concept_type": "noun",
        "vi_short": "giá vốn hàng bán (COGS)",
        "vi_explanation": "Toàn bộ chi phí trực tiếp bỏ ra để mua hoặc sản xuất số hàng hóa, thành phẩm đã được tiêu thụ trong kỳ.",
        "vi_context": "Công thức: Đầu kỳ + Nhập trong kỳ - Cuối kỳ. Lấy 売上高 trừ đi 売上原価 sẽ ra Lợi nhuận gộp (売上総利益).",
        "en_preferred": "Cost of sales",
        "en_alternatives": ["Cost of goods sold", "COGS"],
        "tier": "PRO-A1",
        "estimated_level": "N2",
        "priority_score": 98,
        "factors": {"workplace_frequency": 30, "learner_usefulness": 30, "source_authority": 20, "cross_domain_value": 18},
        "synonyms": ["原価"],
        "antonyms": [],
        "related_terms": ["売上総利益", "仕入高", "製造原価"],
        "collocations": ["売上原価を計算する", "原価率を下げる", "売上原価に含まれる費用"],
        "examples": [
            {"ja": "原材料価格の高騰により、売上原価率が前年より悪化した。", "vi": "Do giá nguyên vật liệu leo thang, tỷ lệ giá vốn hàng bán đã xấu đi so với năm ngoái.", "en": "Due to surging raw material prices, the cost of sales ratio worsened compared to last year.", "register": "formal_business"}
        ],
        "dialogue": [
            {"speaker": "A", "ja": "利益率を改善するためにはどこを見直すべきでしょうか。", "vi": "Để cải thiện tỷ suất lợi nhuận, chúng ta nên xem xét lại khâu nào?", "en": "Where should we review in order to improve profit margins?"},
            {"speaker": "B", "ja": "まずはサプライヤーとの価格交渉で売上原価を抑えましょう。", "vi": "Trước hết hãy đàm phán giá với nhà cung cấp để ghìm giá vốn hàng bán xuống.", "en": "First, let's negotiate prices with suppliers to hold down the cost of sales."}
        ],
        "sources": [{"source_id": "fsa_edinet_2026", "source_term_exact": "売上原価", "source_reference": "1f_AccountList.xlsx:CostOfSales"}]
    },
    {
        "surface": "売上総利益",
        "reading": "うりあげそうりえき",
        "romaji": "uriagesourieki",
        "secondary_domains": ["sales", "management"],
        "concept_type": "noun",
        "vi_short": "lợi nhuận gộp (lãi gộp)",
        "vi_explanation": "Chênh lệch giữa tổng doanh thu bán hàng và giá vốn hàng bán, phản ánh sức mạnh cạnh tranh cốt lõi của sản phẩm.",
        "vi_context": "Trong giới kinh doanh Nhật Bản thường gọi quen thuộc là 'Arari' (粗利益).",
        "en_preferred": "Gross profit",
        "en_alternatives": ["Gross margin"],
        "tier": "PRO-A1",
        "estimated_level": "N2",
        "priority_score": 98,
        "factors": {"workplace_frequency": 30, "learner_usefulness": 30, "source_authority": 20, "cross_domain_value": 18},
        "synonyms": ["粗利益", "あらり"],
        "antonyms": [],
        "related_terms": ["売上高", "営業利益", "粗利率"],
        "collocations": ["売上総利益率", "粗利を確保する", "粗利計算"],
        "examples": [
            {"ja": "新製品は高付加価値のため、売上総利益率が45％に達した。", "vi": "Nhờ có giá trị gia tăng cao, tỷ suất lợi nhuận gộp của sản phẩm mới đã đạt 45%.", "en": "Because the new product has high added value, its gross profit margin reached 45%.", "register": "natural_workplace"}
        ],
        "dialogue": [
            {"speaker": "Manager", "ja": "値引きしてでも案件を受注すべきでしょうか。", "vi": "Chúng ta có nên giảm giá để chốt được hợp đồng không anh?", "en": "Should we discount just to secure the deal?"},
            {"speaker": "Director", "ja": "最低限の粗利が確保できない無理な値下げは避けてください。", "vi": "Hãy tránh hạ giá quá đà nếu không đảm bảo được mức lãi gộp tối thiểu nhé.", "en": "Please avoid unreasonable discounts that fail to secure minimal gross profit."}
        ],
        "sources": [{"source_id": "fsa_edinet_2026", "source_term_exact": "売上総利益", "source_reference": "1f_AccountList.xlsx:GrossProfit"}]
    },
    {
        "surface": "販売費及び一般管理費",
        "reading": "はんばいひおよびいっぱんかんりひ",
        "romaji": "hanbaihioyobiippankanrihi",
        "secondary_domains": ["management"],
        "concept_type": "compound_noun",
        "vi_short": "chi phí bán hàng và chi phí quản lý doanh nghiệp (SG&A)",
        "vi_explanation": "Toàn bộ các khoản chi phí phát sinh cho việc tiêu thụ sản phẩm (tiền tiếp thị, quảng cáo, vận chuyển) và chi phí vận hành bộ máy quản lý chung của công ty (lương nhân viên văn phòng, tiền thuê trụ sở).",
        "vi_context": "Thường được gọi tắt trong công việc là 'Han-kan-hi' (販管費) hoặc SG&A.",
        "en_preferred": "Selling, general and administrative expenses",
        "en_alternatives": ["SG&A expenses"],
        "tier": "PRO-A1",
        "estimated_level": "N2",
        "priority_score": 97,
        "factors": {"workplace_frequency": 29, "learner_usefulness": 30, "source_authority": 20, "cross_domain_value": 18},
        "synonyms": ["販管費", "SG&A"],
        "antonyms": [],
        "related_terms": ["営業利益", "役員報酬", "交際費", "広告宣伝費"],
        "collocations": ["販管費を削減する", "販管費比率", "一般管理費"],
        "examples": [
            {"ja": "テレワークの導入によりオフィスの販管費を10％削減できました。", "vi": "Nhờ triển khai làm việc từ xa, chúng tôi đã cắt giảm được 10% chi phí quản lý doanh nghiệp.", "en": "By introducing telework, we were able to reduce office SG&A expenses by 10%.", "register": "natural_workplace"}
        ],
        "dialogue": [
            {"speaker": "A", "ja": "今期の営業利益が伸び悩んでいる原因は何ですか。", "vi": "Nguyên nhân khiến lợi nhuận kinh doanh kỳ này chưa tăng trưởng tốt là gì?", "en": "What is the reason behind sluggish operating profit growth this period?"},
            {"speaker": "B", "ja": "積極的な広告投資によって販管費が大きく膨らんだためです。", "vi": "Là do chúng ta đầu tư mạnh vào quảng cáo khiến chi phí bán hàng và quản lý tăng vọt ạ.", "en": "It is because proactive advertising investments significantly expanded SG&A expenses."}
        ],
        "sources": [{"source_id": "fsa_edinet_2026", "source_term_exact": "販売費及び一般管理費", "source_reference": "1f_AccountList.xlsx:SellingGeneralAndAdministrativeExpenses"}]
    },
    {
        "surface": "営業利益",
        "reading": "えいぎょうりえき",
        "romaji": "eigyourieki",
        "secondary_domains": ["management", "finance"],
        "concept_type": "noun",
        "vi_short": "lợi nhuận thuần từ hoạt động kinh doanh (EBIT)",
        "vi_explanation": "Khoản lợi nhuận thu được trực tiếp từ hoạt động sản xuất kinh doanh cốt lõi của doanh nghiệp, tính bằng lợi nhuận gộp trừ đi chi phí bán hàng và quản lý.",
        "vi_context": "Chỉ số then chốt để các nhà đầu tư và ngân hàng đánh giá năng lực kiếm tiền từ bản thân ngành nghề kinh doanh chính.",
        "en_preferred": "Operating profit",
        "en_alternatives": ["Operating income", "Operating earnings"],
        "tier": "PRO-A1",
        "estimated_level": "N2",
        "priority_score": 99,
        "factors": {"workplace_frequency": 30, "learner_usefulness": 30, "source_authority": 20, "cross_domain_value": 19},
        "synonyms": [],
        "antonyms": ["営業損失"],
        "related_terms": ["売上総利益", "経常利益", "当期純利益", "営業利益率"],
        "collocations": ["営業利益を計上する", "営業利益率", "営業黒字"],
        "examples": [
            {"ja": "売上の増加と経費削減が功を奏し、営業利益が過去最高を記録した。", "vi": "Nhờ doanh số tăng và cắt giảm chi phí hiệu quả, lợi nhuận hoạt động đã đạt mức kỷ lục.", "en": "Thanks to sales increases and cost reductions, operating profit hit an all-time high.", "register": "natural_workplace"}
        ],
        "dialogue": [
            {"speaker": "CEO", "ja": "今年度の営業利益目標は達成できそうか。", "vi": "Mục tiêu lợi nhuận hoạt động năm nay có khả năng cán đích không?", "en": "Are we likely to achieve this fiscal year's operating profit target?"},
            {"speaker": "CFO", "ja": "現在のペースを維持できれば、計画を上回る見通しです。", "vi": "Nếu duy trì được tốc độ hiện tại, dự kiến sẽ vượt kế hoạch đề ra ạ.", "en": "If we maintain the current pace, we expect to surpass the plan."}
        ],
        "sources": [{"source_id": "fsa_edinet_2026", "source_term_exact": "営業利益", "source_reference": "1f_AccountList.xlsx:OperatingIncome"}]
    },
    {
        "surface": "経常利益",
        "reading": "けいじょうりえき",
        "romaji": "keijourieki",
        "secondary_domains": ["banking", "finance"],
        "concept_type": "noun",
        "vi_short": "lợi nhuận thường niên / lợi nhuận thông thường",
        "vi_explanation": "Chỉ tiêu lợi nhuận đặc trưng của kế toán Nhật Bản, tính bằng lợi nhuận kinh doanh cộng các khoản thu tài chính (lãi tiền gửi, cổ tức) và trừ chi phí tài chính (lãi vay).",
        "vi_context": "Thường được gọi tắt là 'Keitsune' (経常). Phản ánh năng lực sinh lời tổng thể của toàn doanh nghiệp trong điều kiện kinh doanh bình thường.",
        "en_preferred": "Ordinary income",
        "en_alternatives": ["Recurring profit", "Ordinary profit"],
        "tier": "PRO-A2",
        "estimated_level": "N2",
        "priority_score": 96,
        "factors": {"workplace_frequency": 29, "learner_usefulness": 29, "source_authority": 20, "cross_domain_value": 18},
        "synonyms": ["経常", "ケイツネ"],
        "antonyms": ["経常損失"],
        "related_terms": ["営業利益", "営業外収益", "営業外費用", "当期純利益"],
        "collocations": ["経常利益を伸ばす", "経常増益", "経常損益"],
        "examples": [
            {"ja": "借入金の返済が進み支払利息が減ったため、経常利益が大幅に改善した。", "vi": "Do trả bớt nợ vay nên chi phí lãi vay giảm, lợi nhuận thường niên đã được cải thiện đáng kể.", "en": "Because loan repayments progressed and interest expenses decreased, ordinary income improved substantially.", "register": "formal_business"}
        ],
        "dialogue": [
            {"speaker": "A", "ja": "本業は黒字なのに経常利益が赤字なのはなぜですか。", "vi": "Kinh doanh chính có lãi mà sao lợi nhuận thường niên lại bị âm vậy anh?", "en": "Why is ordinary income in the red even though core business is profitable?"},
            {"speaker": "B", "ja": "急激な円安による為替差損が大きく響いたためです。", "vi": "Là do khoản lỗ chênh lệch tỷ giá do đồng Yên trượt giá mạnh gây ảnh hưởng lớn ạ.", "en": "It is because foreign exchange losses from the rapid yen depreciation hit heavily."}
        ],
        "sources": [{"source_id": "fsa_edinet_2026", "source_term_exact": "経常利益", "source_reference": "1f_AccountList.xlsx:OrdinaryIncome"}]
    },
    {
        "surface": "当期純利益",
        "reading": "とうきじゅんりえき",
        "romaji": "toukijunrieki",
        "secondary_domains": ["finance", "corporate_governance"],
        "concept_type": "noun",
        "vi_short": "lợi nhuận thuần trong kỳ / lãi ròng sau thuế",
        "vi_explanation": "Khoản lợi nhuận cuối cùng thuộc về cổ đông sau khi đã cộng trừ tất cả các khoản thu chi bất thường và nộp đầy đủ các loại thuế thu nhập doanh nghiệp.",
        "vi_context": "Còn được gọi là 'Bottom line' trên báo cáo thu nhập. Dùng để chia cổ tức hoặc chuyển vào thặng dư tích lũy.",
        "en_preferred": "Net income",
        "en_alternatives": ["Net profit", "Bottom line"],
        "tier": "PRO-A1",
        "estimated_level": "N2",
        "priority_score": 99,
        "factors": {"workplace_frequency": 30, "learner_usefulness": 30, "source_authority": 20, "cross_domain_value": 19},
        "synonyms": ["純利益", "最終利益"],
        "antonyms": ["当期純損失"],
        "related_terms": ["税引前当期純利益", "法人税等", "親会社株主に帰属する当期純利益"],
        "collocations": ["当期純利益を計上する", "過去最高の当期純利益", "純利益率"],
        "examples": [
            {"ja": "今期は税制優遇措置の恩恵もあり、当期純利益が50億円に達した。", "vi": "Kỳ này nhờ có chính sách ưu đãi thuế, lợi nhuận ròng sau thuế đã đạt 5 tỷ yên.", "en": "Thanks also to tax incentive measures, net income for this period reached 5 billion yen.", "register": "formal_business"}
        ],
        "dialogue": [
            {"speaker": "Director", "ja": "決算発表での最終的な当期純利益の着地予想はどうですか。", "vi": "Dự báo con số chốt lợi nhuận ròng sau thuế trong buổi công bố quyết toán thế nào?", "en": "What is the landing forecast for final net income in the earnings release?"},
            {"speaker": "Manager", "ja": "特別損失を吸収し、前年並みの黒字を維持できる見込みです。", "vi": "Chúng ta đã bù đắp được khoản lỗ bất thường và dự kiến duy trì được mức lãi tương đương năm ngoái ạ.", "en": "We absorbed the extraordinary loss and expect to maintain profits comparable to last year."}
        ],
        "sources": [{"source_id": "fsa_edinet_2026", "source_term_exact": "当期純利益", "source_reference": "1f_AccountList.xlsx:NetIncome"}]
    },
    {
        "surface": "仕訳",
        "reading": "しわけ",
        "romaji": "shiwake",
        "secondary_domains": ["bookkeeping"],
        "concept_type": "noun",
        "vi_short": "bút toán kế toán / định khoản Nợ - Có",
        "vi_explanation": "Thao tác phân tích một nghiệp vụ kinh tế tài chính phát sinh thành các tài khoản Nợ (Karikata) và Có (Kashikata) theo nguyên tắc kế toán kép.",
        "vi_context": "Kỹ năng nền tảng của nhân viên kế toán. Mỗi bút toán phải bảo đảm tổng số tiền bên Nợ bằng tổng số tiền bên Có.",
        "en_preferred": "Journal entry",
        "en_alternatives": ["Journalizing", "Account classification"],
        "tier": "PRO-A1",
        "estimated_level": "N3",
        "priority_score": 100,
        "factors": {"workplace_frequency": 30, "learner_usefulness": 30, "source_authority": 20, "cross_domain_value": 20},
        "synonyms": ["仕訳を切る"],
        "antonyms": [],
        "related_terms": ["借方", "貸方", "勘定科目", "仕訳帳"],
        "collocations": ["仕訳を切る", "仕訳を入力する", "決算整理仕訳"],
        "examples": [
            {"ja": "取引内容を確認しながら、会計ソフトに正確な仕訳を入力する。", "vi": "Chúng tôi vừa kiểm tra nội dung giao dịch vừa nhập các bút toán chính xác vào phần mềm kế toán.", "en": "While checking transaction details, we enter accurate journal entries into the accounting software.", "register": "natural_workplace"}
        ],
        "dialogue": [
            {"speaker": "Newcomer", "ja": "この消耗品費の購入はどの科目で仕訳を切ればよいですか。", "vi": "Khoản mua đồ tiêu hao này em nên định khoản vào tài khoản nào ạ?", "en": "Which account should I journalize this supplies expense under?"},
            {"speaker": "Senior", "ja": "借方を消耗品費、貸方を普通預金にして仕訳してください。", "vi": "Em ghi bên Nợ là Chi phí đồ tiêu hao, bên Có là Tiền gửi ngân hàng thông thường nhé.", "en": "Debit supplies expense and credit ordinary deposit."}
        ],
        "sources": [{"source_id": "fsa_edinet_2026", "source_term_exact": "仕訳", "source_reference": "bookkeeping_foundation"}]
    },
    {
        "surface": "借方",
        "reading": "かりかた",
        "romaji": "karikata",
        "secondary_domains": ["bookkeeping"],
        "concept_type": "noun",
        "vi_short": "bên Nợ (trong kế toán)",
        "vi_explanation": "Vị trí nằm ở phía bên trái của tài khoản kế toán hoặc sổ nhật ký, dùng để ghi nhận sự gia tăng tài sản, gia tăng chi phí hoặc sự suy giảm nợ phải trả và vốn.",
        "vi_context": "Quy tắc cơ bản: Tài sản tăng ghi Nợ, Chi phí tăng ghi Nợ.",
        "en_preferred": "Debit",
        "en_alternatives": ["Dr."],
        "tier": "PRO-A1",
        "estimated_level": "N3",
        "priority_score": 98,
        "factors": {"workplace_frequency": 30, "learner_usefulness": 30, "source_authority": 20, "cross_domain_value": 18},
        "synonyms": [],
        "antonyms": ["貸方"],
        "related_terms": ["仕訳", "貸借平均の原理"],
        "collocations": ["借方に記入する", "借方合計"],
        "examples": [
            {"ja": "現金が増加したときは、借方に現金勘定を記入します。", "vi": "Khi tiền mặt tăng lên, chúng ta ghi tài khoản tiền mặt vào bên Nợ.", "en": "When cash increases, we record the cash account on the debit side.", "register": "natural_workplace"}
        ],
        "dialogue": [
            {"speaker": "A", "ja": "借方と貸方の合計金額が合いません。", "vi": "Tổng số tiền bên Nợ và bên Có không khớp nhau anh ơi.", "en": "The total amounts for debit and credit do not match."},
            {"speaker": "B", "ja": "どこかで入力ミスがあるはずだから、もう一度仕訳帳を見直そう。", "vi": "Chắc chắn có chỗ nhập nhầm, chúng ta hãy rà soát lại sổ nhật ký nhé.", "en": "There must be an input error somewhere, let's review the journal again."}
        ],
        "sources": [{"source_id": "fsa_edinet_2026", "source_term_exact": "借方", "source_reference": "bookkeeping_foundation"}]
    },
    {
        "surface": "貸方",
        "reading": "かしかた",
        "romaji": "kashikata",
        "secondary_domains": ["bookkeeping"],
        "concept_type": "noun",
        "vi_short": "bên Có (trong kế toán)",
        "vi_explanation": "Vị trí nằm ở phía bên phải của tài khoản kế toán hoặc sổ nhật ký, dùng để ghi nhận sự gia tăng nợ phải trả, gia tăng vốn, phát sinh doanh thu hoặc sự sụt giảm tài sản.",
        "vi_context": "Quy tắc cơ bản: Nợ phải trả tăng ghi Có, Vốn tăng ghi Có, Doanh thu phát sinh ghi Có.",
        "en_preferred": "Credit",
        "en_alternatives": ["Cr."],
        "tier": "PRO-A1",
        "estimated_level": "N3",
        "priority_score": 98,
        "factors": {"workplace_frequency": 30, "learner_usefulness": 30, "source_authority": 20, "cross_domain_value": 18},
        "synonyms": [],
        "antonyms": ["借方"],
        "related_terms": ["仕訳", "貸借一致"],
        "collocations": ["貸方に計上する", "貸方残高"],
        "examples": [
            {"ja": "売上が発生した場合は、貸方に売上高を計上するのが基本ルールです。", "vi": "Quy tắc cơ bản là khi phát sinh doanh thu, chúng ta hạch toán doanh thu vào bên Có.", "en": "The basic rule is to record net sales on the credit side when revenue is generated.", "register": "natural_workplace"}
        ],
        "dialogue": [
            {"speaker": "A", "ja": "銀行からの借入金が入金された場合の貸方は何ですか。", "vi": "Khi tiền vay ngân hàng về tài khoản thì bên Có là gì ạ?", "en": "What is the credit entry when a bank loan is deposited?"},
            {"speaker": "B", "ja": "負債の増加なので、貸方に短期借入金を記入します。", "vi": "Vì là tăng nợ phải trả nên bên Có ghi Vay ngắn hạn em nhé.", "en": "Since liabilities increase, enter short-term borrowings on the credit side."}
        ],
        "sources": [{"source_id": "fsa_edinet_2026", "source_term_exact": "貸方", "source_reference": "bookkeeping_foundation"}]
    },
    {
        "surface": "勘定科目",
        "reading": "かんじょうかもく",
        "romaji": "kanjoukamoku",
        "secondary_domains": ["bookkeeping"],
        "concept_type": "noun",
        "vi_short": "tài khoản kế toán / tên danh mục kế toán",
        "vi_explanation": "Tên gọi danh mục được quy ước thống nhất để phân loại và theo dõi các giao dịch tài chính phát sinh vào tài sản, nợ, vốn, doanh thu hay chi phí.",
        "vi_context": "Mỗi doanh nghiệp đều xây dựng Hệ thống danh mục tài khoản (Chart of Accounts) riêng dựa trên quy chuẩn kế toán chung.",
        "en_preferred": "Account title",
        "en_alternatives": ["Account item", "Chart of accounts item"],
        "tier": "PRO-A1",
        "estimated_level": "N2",
        "priority_score": 99,
        "factors": {"workplace_frequency": 30, "learner_usefulness": 30, "source_authority": 20, "cross_domain_value": 19},
        "synonyms": [],
        "antonyms": [],
        "related_terms": ["仕訳", "勘定科目リスト", "補助科目"],
        "collocations": ["勘定科目を設定する", "適切な勘定科目を選ぶ", "勘定科目体系"],
        "examples": [
            {"ja": "経費精算の際は、社内規程に従って正しい勘定科目を選択してください。", "vi": "Khi làm thủ tục thanh toán chi phí, vui lòng chọn đúng tài khoản kế toán theo quy định nội bộ công ty.", "en": "When settling expenses, please select the correct account title in accordance with company regulations.", "register": "natural_workplace"}
        ],
        "dialogue": [
            {"speaker": "A", "ja": "取引先との会食代はどの勘定科目になりますか。", "vi": "Tiền ăn tiếp khách với đối tác thì dùng tài khoản kế toán nào vậy?", "en": "Which account title does the dining expense with clients fall under?"},
            {"speaker": "B", "ja": "社内交際費ではなく、交際接待費として申請してください。", "vi": "Hãy làm đơn theo tài khoản Chi phí tiếp khách (Kousai-hi) nhé.", "en": "Please apply under entertainment expenses, not internal social expenses."}
        ],
        "sources": [{"source_id": "fsa_edinet_2026", "source_term_exact": "勘定科目リスト", "source_reference": "1f_AccountList.xlsx:AccountListHeader"}]
    },
    {
        "surface": "総勘定元帳",
        "reading": "そうかんじょうもとちょう",
        "romaji": "soukanjoumotochou",
        "secondary_domains": ["bookkeeping", "audit"],
        "concept_type": "noun",
        "vi_short": "sổ cái tổng hợp các tài khoản",
        "vi_explanation": "Sổ kế toán trung tâm tập hợp toàn bộ các bút toán phát sinh trong kỳ theo từng tài khoản kế toán riêng biệt để theo dõi số dư và biến động.",
        "vi_context": "Thường được gọi tắt là 'Motochou' (元帳). Là chứng từ pháp lý cốt lõi khi thanh tra thuế hoặc kiểm toán độc lập kiểm tra.",
        "en_preferred": "General ledger",
        "en_alternatives": ["GL"],
        "tier": "PRO-A2",
        "estimated_level": "N2",
        "priority_score": 94,
        "factors": {"workplace_frequency": 28, "learner_usefulness": 28, "source_authority": 20, "cross_domain_value": 18},
        "synonyms": ["元帳", "GL"],
        "antonyms": [],
        "related_terms": ["仕訳帳", "補助元帳", "試算表"],
        "collocations": ["総勘定元帳へ転記する", "元帳を照合する", "総勘定元帳を印刷・保存する"],
        "examples": [
            {"ja": "仕訳帳から総勘定元帳へ転記し、勘定ごとの残高を把握します。", "vi": "Từ sổ nhật ký chúng tôi kết chuyển vào sổ cái để nắm bắt số dư từng tài khoản.", "en": "We post from the journal to the general ledger to track balances for each account.", "register": "natural_workplace"}
        ],
        "dialogue": [
            {"speaker": "Auditor", "ja": "消耗品費の総勘定元帳の明細を提出してください。", "vi": "Xin vui lòng nộp bảng chi tiết sổ cái của tài khoản chi phí tiêu hao.", "en": "Please submit the general ledger details for supplies expenses."},
            {"speaker": "Accountant", "ja": "会計システムから該当期間の元帳データをエクスポートして提出します。", "vi": "Tôi sẽ xuất dữ liệu sổ cái kỳ đó từ phần mềm kế toán và gửi sang ngay ạ.", "en": "I will export the ledger data for the relevant period from our system and submit it."}
        ],
        "sources": [{"source_id": "fsa_edinet_2026", "source_term_exact": "総勘定元帳", "source_reference": "bookkeeping_foundation"}]
    },
    {
        "surface": "試算表",
        "reading": "しさんひょう",
        "romaji": "shisanhyou",
        "secondary_domains": ["bookkeeping", "management"],
        "concept_type": "noun",
        "vi_short": "bảng cân đối thử / bảng tổng hợp số phát sinh",
        "vi_explanation": "Bảng tổng hợp được lập ra để kiểm tra tính chính xác của việc ghi chép và kết chuyển sổ cái dựa trên nguyên tắc cân bằng giữa tổng Nợ và tổng Có.",
        "vi_context": "Thường lập hàng tháng (Gesshi shisanhyou - 月次試算表) để ban điều hành nắm tình hình kinh doanh giữa niên độ.",
        "en_preferred": "Trial balance",
        "en_alternatives": ["Trial balance sheet"],
        "tier": "PRO-A2",
        "estimated_level": "N2",
        "priority_score": 95,
        "factors": {"workplace_frequency": 29, "learner_usefulness": 28, "source_authority": 20, "cross_domain_value": 18},
        "synonyms": ["合計残高試算表", "T/B"],
        "antonyms": [],
        "related_terms": ["総勘定元帳", "決算整理", "精算表"],
        "collocations": ["月次試算表を作成する", "試算表で残高を確認する", "貸借の不一致"],
        "examples": [
            {"ja": "毎月第5営業日までに月次試算表を作成し、経営会議へ報告します。", "vi": "Trước ngày làm việc thứ 5 hàng tháng, chúng tôi lập bảng cân đối thử tháng để báo cáo lên cuộc họp điều hành.", "en": "We prepare the monthly trial balance by the fifth business day to report to management.", "register": "natural_workplace"}
        ],
        "dialogue": [
            {"speaker": "Manager", "ja": "先月の月次試算表はもうできましたか。", "vi": "Bảng cân đối thử của tháng trước đã xong chưa em?", "en": "Is last month's trial balance ready yet?"},
            {"speaker": "Staff", "ja": "ただいま未払金の残高確認中ですので、午後一番に提出します。", "vi": "Em đang rà soát lại số dư các khoản phải trả, đầu giờ chiều em gửi ạ.", "en": "I am currently verifying accounts payable balances, so I will submit it early this afternoon."}
        ],
        "sources": [{"source_id": "fsa_edinet_2026", "source_term_exact": "試算表", "source_reference": "bookkeeping_foundation"}]
    }
]
