#!/usr/bin/env python3
"""
scripts/pilot_builder/make_expressions.py
Builds 50 authentic, high-frequency Japanese workplace idiomatic expressions (Layer D: Workplace Expressions).
Includes readings, romaji, domain tags, Vietnamese professional nuances, English equivalents,
workplace usage context, natural example sentences, and dialogues.
"""

import json
from pathlib import Path
import pykakasi

BASE_DIR = Path(__file__).resolve().parent.parent.parent
OUT_FILE = BASE_DIR / "scripts" / "pilot_builder" / "expressions.py"

kks = pykakasi.kakasi()

EXPRESSION_DEFINITIONS = [
    ("請求書を切る", "せいきゅうしょをきる", "xuất hóa đơn đòi tiền khách hàng", "Thao tác lập và gửi hóa đơn yêu cầu thanh toán cho đối tác sau khi đã hoàn thành giao hàng hoặc dịch vụ.", "Issue an invoice", "accounting", "PRO-A1", 99, "納品書", "月末までに請求書を切っておいてください。"),
    ("経費で落とす", "けいひでおとす", "hạch toán tính vào chi phí hợp lý của công ty", "Đưa các khoản chi tiêu tiếp khách, đi lại hoặc mua sắm vào chi phí được khấu trừ thuế của doanh nghiệp.", "Charge to business expenses", "accounting", "PRO-A1", 100, "経費精算", "この接待費は経費で落とせますか。"),
    ("数字が合わない", "すうじがあわない", "số liệu không khớp / lệch sổ sách kế toán", "Tình trạng tổng số dư bên Nợ và bên Có hoặc số liệu thực tế so với sổ cái không trùng khớp nhau.", "Numbers do not balance / Discrepancy in figures", "accounting", "PRO-A1", 99, "試算表", "貸借対照表の左右の数字が合いません。"),
    ("入金を確認する", "にゅうきんをかくにんする", "kiểm tra tiền đã vào tài khoản ngân hàng chưa", "Thao tác đối chiếu sao kê tài khoản ngân hàng để xác nhận khách hàng đã chuyển khoản thanh toán hay chưa.", "Confirm receipt of payment", "accounting", "PRO-A1", 100, "売掛金消込", "先方からの入金を確認できました。"),
    ("締め処理をする", "しめしょりをする", "thực hiện khóa sổ kế toán cuối kỳ", "Thực hiện quy trình chốt số liệu giao dịch phát sinh trong tháng để lập báo cáo tài chính định kỳ.", "Perform closing procedures", "accounting", "PRO-A1", 98, "月次決算", "20日締めなので、明日締め処理をします。"),
    ("税理士に確認する", "ぜいりしにかくにんする", "tham vấn ý kiến của chuyên gia thuế Zairishi", "Hỏi ý kiến của chuyên gia thuế độc lập trước khi hạch toán các nghiệp vụ phức tạp để tránh rủi ro thanh tra.", "Consult with tax accountant", "tax", "PRO-A1", 98, "税務相談", "この処理については念のため顧問税理士に確認します。"),
    ("承認を取る", "しょうにんをとる", "xin phê duyệt từ cấp trên", "Lấy sự đồng ý của quản lý trực tiếp hoặc ban giám đốc trước khi thực hiện mua sắm hay gửi đề xuất.", "Obtain approval", "business", "PRO-A1", 100, "決裁", "部長から稟議の承認を取りました。"),
    ("見積を出す", "みつもりをだす", "phát hành gửi bảng báo giá cho khách", "Soạn thảo và gửi bảng tính giá cả, chi phí cho khách hàng tham khảo trước khi ký hợp đồng.", "Submit an estimate / Provide a quote", "business", "PRO-A1", 100, "見積書", "明日中にお客様へ見積を出します。"),
    ("相見積もりを取る", "あいみつもりをとる", "lấy báo giá so sánh từ nhiều nhà cung cấp", "Yêu cầu nhiều công ty cùng báo giá để chọn đơn vị có giá cả và chất lượng tốt nhất.", "Obtain comparative quotes", "business", "PRO-A1", 99, "コスト削減", "3社から相見積もりを取って比較してください。"),
    ("納期を確認する", "のうきをかくにんする", "kiểm tra xác nhận ngày hẹn giao hàng", "Liên hệ với nhà cung cấp hoặc xưởng sản xuất để biết chính xác thời điểm hàng sẽ về tới nơi.", "Confirm delivery deadline", "business", "PRO-A1", 100, "納期厳守", "製造部に連絡して正確な納期を確認してください。"),
    ("納期を前倒しする", "のうきをまえだおしする", "đẩy sớm thời hạn bàn giao so với kế hoạch", "Rút ngắn thời gian thực hiện để bàn giao sản phẩm sớm hơn thời hạn đã cam kết ban đầu.", "Move up delivery schedule", "business", "PRO-A1", 97, "スケジュール調整", "クライアントの要望で納期を1週間前倒ししました。"),
    ("納期が遅延する", "のうきがちえんする", "bị chậm trễ tiến độ bàn giao hàng", "Tình trạng công việc hoặc hàng hóa không thể hoàn tất đúng ngày hẹn đã thỏa thuận.", "Delivery is delayed", "business", "PRO-A1", 98, "納期遅延", "部品調達の遅れで納期が3日遅延しています。"),
    ("帳簿につける", "ちょうぼにつける", "ghi chép vào sổ sách kế toán", "Nhập các nghiệp vụ thu chi, mua bán hàng ngày vào sổ nhật ký hoặc phần mềm kế toán.", "Record in books / Bookkeep", "accounting", "PRO-A1", 97, "仕訳", "今日の領収書を忘れないうちに帳簿につけておきます。"),
    ("領収書を切る", "りょうしゅうしょをきる", "viết biên lai thu tiền giao cho khách", "Lập và đóng dấu biên lai xác nhận đã thu đủ tiền mặt từ khách hàng.", "Issue a receipt", "accounting", "PRO-A1", 98, "領収書", "代金をいただいたので領収書を切ります。"),
    ("仮払いを精算する", "かりばらいをせいさんする", "quyết toán khoản tiền tạm ứng công tác", "Nộp hóa đơn và đối chiếu số tiền tạm ứng trước để hoàn trả hoặc nhận lại tiền chênh lệch sau chuyến công tác.", "Settle suspense payments", "accounting", "PRO-A1", 97, "仮払金", "出張から戻ったので仮払いを精算します。"),
    ("立替金を精算する", "たてかえきんをせいさんする", "thanh toán hoàn trả tiền chi hộ công ty", "Nộp chứng từ để công ty trả lại khoản tiền túi cá nhân đã chi hộ cho công việc.", "Reimburse out-of-pocket expenses", "accounting", "PRO-A1", 98, "立替金", "先週のタクシー代の立替金を精算してください。"),
    ("売掛金を回収する", "うりかけきんをかいしゅうする", "thu hồi các khoản nợ phải thu của khách", "Hành động đôn đốc khách hàng chuyển khoản thanh toán các hóa đơn đã đến hạn trả.", "Collect accounts receivable", "accounting", "PRO-A1", 100, "売掛金", "今月末までに滞留している売掛金を回収します。"),
    ("売掛金を計上する", "うりかけきんをけいじょうする", "hạch toán ghi nhận khoản phải thu vào sổ", "Ghi nhận doanh thu bán chịu vào tài khoản Nợ phải thu tại thời điểm xuất hóa đơn.", "Recognize accounts receivable", "accounting", "PRO-A1", 98, "売掛金", "納品完了に伴い、売掛金を計上しました。"),
    ("買掛金を支払う", "かいかけきんをしはらう", "thanh toán tiền nợ cho nhà cung cấp", "Chuyển tiền trả cho nhà cung cấp theo đúng ngày thỏa thuận ghi trên hợp đồng.", "Pay accounts payable", "accounting", "PRO-A1", 99, "買掛金", "仕入先への買掛金を期日通りに支払いました。"),
    ("消込を行う", "けしこみをおこなう", "thực hiện đối trừ cấn nợ trên phần mềm (Reconciliation)", "Khớp lệnh giữa số tiền ngân hàng báo có với số dư hóa đơn nợ để xóa nợ tương ứng trên hệ thống.", "Perform reconciliation / Clear accounts", "accounting", "PRO-A1", 98, "売掛金消込", "入金明細と請求書を照合して消込を行います。"),
    ("棚卸しを行う", "たなおろしをおこなう", "tiến hành kiểm kê hàng tồn kho thực tế", "Đếm trực tiếp số lượng từng mặt hàng trong kho để so sánh với số liệu ghi trên sổ sách kế toán.", "Conduct physical inventory count", "accounting", "PRO-A1", 98, "実地棚卸", "期末なので今週末に倉庫で棚卸しを行います。"),
    ("稟議を回す", "りんぎをまわす", "luân chuyển tờ trình xin chữ ký nội bộ", "Chuyển tờ trình đề xuất kinh doanh qua từng phòng ban và cấp lãnh đạo để lấy ý kiến phê duyệt.", "Circulate approval request (Ringi)", "business", "PRO-A1", 100, "稟議書", "新規サーバーの購入について稟議を回してください。"),
    ("根回しをする", "ねまわしをする", "vận động hành lang thống nhất ý kiến trước khi họp", "Gặp gỡ trao đổi trước với các thành viên quan trọng để đạt được sự đồng thuận trước phiên họp chính thức.", "Lay groundwork / Build consensus informally", "business", "PRO-A1", 98, "合意形成", "会議で反対されないよう、事前に役員へ根回しをしました。"),
    ("アポを取る", "あぽをとる", "đặt lịch hẹn gặp trước với khách hàng", "Liên lạc gọi điện hoặc gửi email xin một khoảng thời gian cụ thể để gặp mặt trao đổi công việc.", "Make an appointment", "business", "PRO-A1", 100, "アポイントメント", "来週の火曜日に新規顧客とのアポを取りました。"),
    ("商談をまとめる", "しょうだんをまとめる", "chốt đàm phán thương mại thành công", "Thương lượng thành công các điều khoản giá cả và phạm vi dịch vụ để đi đến bước ký hợp đồng.", "Wrap up negotiations / Close a deal", "business", "PRO-A1", 99, "成約", "競合他社との競り合いの末、無事に商談をまとめました。"),
    ("契約を締結する", "けいやくをていけつする", "tiến hành ký kết hợp đồng chính thức", "Hoàn tất việc ký tên đóng dấu vào văn bản hợp đồng ràng buộc pháp lý giữa hai bên.", "Conclude a contract / Execute agreement", "business", "PRO-A1", 100, "契約書", "双方の法務確認が完了し、本日契約を締結しました。"),
    ("契約を更新する", "けいやくをこうしんする", "gia hạn thời hạn hợp đồng thêm một kỳ", "Kéo dài hiệu lực của hợp đồng dịch vụ hoặc thuê văn phòng thêm một khoảng thời gian mới.", "Renew a contract", "business", "PRO-A1", 98, "契約更新", "現行の業務委託契約をさらに1年間更新します。"),
    ("契約を解除する", "けいやくをかいじょする", "đơn phương chấm dứt hủy bỏ hợp đồng", "Hủy bỏ hợp đồng do đối tác vi phạm điều khoản nghiêm trọng hoặc theo điều kiện thỏa thuận trước.", "Terminate a contract", "business", "PRO-A2", 94, "契約解除", "重大な債務不履行があったため、契約を解除します。"),
    ("手付金を支払う", "てつけきんをしはらう", "đặt cọc tiền hợp đồng", "Chuyển trước một khoản tiền bảo đảm thực hiện hợp đồng khi mua bất động sản hoặc máy móc lớn.", "Pay a deposit / Pay earnest money", "business", "PRO-A2", 93, "手付金", "売買契約の締結時に手付金として100万円を支払いました。"),
    ("違約金を請求する", "いやくきんをせいきゅうする", "đòi tiền phạt do vi phạm cam kết hợp đồng", "Yêu cầu bên vi phạm phải nộp khoản tiền phạt đã được quy định sẵn trong điều khoản hợp đồng.", "Claim contract breach penalty", "business", "PRO-A2", 93, "違約金", "秘密保持義務違反があったため、違約金を請求します。"),
    ("クレームに対応する", "くれーむにたいおうする", "tiếp nhận và xử lý khiếu nại của khách hàng", "Lắng nghe phản ánh, xin lỗi chân thành và nhanh chóng đưa ra giải pháp khắc phục sự cố cho khách.", "Handle a customer complaint", "business", "PRO-A1", 99, "クレーム対応", "お客様からのクレームに誠心誠意対応しました。"),
    ("議事録を作成する", "ぎじろくをさくせいする", "soạn thảo biên bản cuộc họp", "Ghi lại tóm tắt diễn biến, các quyết định thống nhất và danh sách công việc giao cho từng người sau cuộc họp.", "Prepare meeting minutes", "business", "PRO-A1", 100, "会議議事録", "ミーティング終了後、速やかに議事録を作成して共有してください。"),
    ("引き継ぎを行う", "ひきつぎをおこなう", "tiến hành bàn giao lại công việc", "Truyền đạt lại tài liệu, quy trình và các lưu ý cho nhân viên kế nhiệm trước khi chuyển bộ phận hoặc nghỉ việc.", "Conduct handover of duties", "business", "PRO-A1", 99, "業務引き継ぎ", "後任の担当者へ業務の引き継ぎを行いました。"),
    ("直行直帰する", "ちょっこうちょっきする", "đi thẳng đến chỗ khách và kết thúc về thẳng nhà", "Không cần qua trụ sở công ty mà đi thẳng từ nhà đến chỗ đối tác và gặp xong thì về nhà luôn.", "Go directly to and from client site", "business", "PRO-A1", 99, "直行直帰", "明日は午前の客先へ直行し、午後の商談後は直帰します。"),
    ("有休を消化する", "ゆうきゅうをしょうかする", "nghỉ sử dụng hết ngày phép năm hưởng lương", "Sử dụng số ngày nghỉ phép năm được công ty cấp theo quyền lợi người lao động.", "Take paid annual leave", "business", "PRO-A1", 99, "有給休暇", "今月中に残っている有休を消化する予定です。"),
    ("残業を申請する", "ざんぎょうをしんせいする", "đăng ký xin làm thêm giờ với quản lý", "Nộp đơn hoặc đăng ký trên hệ thống xin phép cấp trên duyệt làm việc ngoài giờ trước khi thực hiện.", "Apply for overtime work", "business", "PRO-A1", 99, "残業手当", "締め切りに間に合わせるため、2時間の残業を申請しました。"),
    ("源泉徴収する", "げんせんちょうしゅうする", "khấu trừ tiền thuế thu nhập cá nhân tại nguồn", "Trừ trước tiền thuế thu nhập từ tiền lương hoặc tiền thù lao chuyên gia để nộp vào ngân sách nhà nước.", "Withhold tax at source", "tax", "PRO-A1", 100, "源泉徴収", "給与支払時に所得税を源泉徴収します。"),
    ("年末調整を行う", "ねんまつちょうせいをおこなう", "làm thủ tục quyết toán thuế cuối năm cho nhân viên", "Tính toán lại toàn bộ thuế thu nhập trong năm của nhân viên vào tháng 12 để hoàn thuế hoặc thu thêm.", "Conduct year-end tax adjustment", "tax", "PRO-A1", 100, "年末調整", "総務部では12月に全社員の年末調整を行います。"),
    ("確定申告を行う", "かくていしんこくをおこなう", "tự nộp tờ khai quyết toán thuế hàng năm", "Nộp hồ sơ thuế từ giữa tháng 2 đến giữa tháng 3 để khai báo thu nhập và quyết toán thuế chính thức.", "File a final tax return", "tax", "PRO-A1", 100, "確定申告", "副業の所得が20万円を超えたので確定申告を行いました。"),
    ("e-Taxで送信する", "いーたっくすでそうしんする", "gửi hồ sơ thuế qua mạng cổng điện tử e-Tax", "Thực hiện gửi tờ khai quyết toán thuế trực tuyến mà không cần phải in giấy mang ra chi cục thuế.", "Submit via e-Tax", "tax", "PRO-A1", 98, "e-Tax", "確定申告書は窓口に行かずe-Taxで送信しました。"),
    ("インボイスを登録する", "いんぼいすをとうろくする", "đăng ký mã số đơn vị xuất hóa đơn đủ điều kiện", "Đăng ký với cơ quan thuế để nhận mã số T+13 chữ số phát hành hóa đơn theo Chế độ Hóa đơn mới.", "Register as qualified invoice issuer", "tax", "PRO-A1", 98, "適格請求書発行事業者", "免税事業者から課税事業者に転換してインボイスを登録しました。"),
    ("通関を通す", "つうかんをとおす", "làm thủ tục thông quan hải quan xuất nhập khẩu", "Hoàn tất việc nộp tờ khai hải quan, xuất trình chứng từ và kiểm tra hàng hóa tại cửa khẩu cảng.", "Clear customs / Process customs clearance", "trade", "PRO-A1", 100, "通関手続き", "保税地域の貨物を検査し、無事通関を通しました。"),
    ("コンテナをバンニングする", "こんてなをばんにんぐする", "đóng hàng hóa vào bên trong thùng container", "Thao tác xếp dỡ và chằng buộc chắc chắn hàng hóa vào lòng vỏ container trước khi niêm phong seal.", "Stuff a container / Vanning", "trade", "PRO-A1", 98, "バンニング", "明日午前中に港の倉庫でコンテナをバンニングします。"),
    ("デバンニング作業を行う", "でばんにんぐさぎょうをおこなう", "tiến hành dỡ hàng ra khỏi vỏ container", "Mở kẹp chì niêm phong và cẩu bốc toàn bộ hàng hóa ra khỏi thùng container đưa vào kho.", "Perform container devanning", "trade", "PRO-A1", 98, "デバンニング", "輸入貨物が到着したのでデバンニング作業を行います。"),
    ("B/Lを発行する", "びーえるをはっこうする", "hãng tàu phát hành vận đơn đường biển", "Hãng tàu ký và cấp phát bộ vận đơn gốc xác nhận đã bốc hàng an toàn lên tàu biển.", "Issue a Bill of Lading (B/L)", "trade", "PRO-A1", 100, "船荷証券", "船積み完了後、船社がオリジナルのB/Lを発行しました。"),
    ("サレンダーB/Lに切り替える", "されんだーびーえるにきりかえる", "chuyển sang vận đơn giải phóng hàng bằng điện tín", "Thu hồi vận đơn gốc tại cảng bốc để người nhận hàng bên đích lấy hàng nhanh bằng thông báo điện tín.", "Switch to surrendered B/L (Telex release)", "trade", "PRO-A1", 99, "サレンダーB/L", "航海日数が短いため、サレンダーB/Lに切り替えました。"),
    ("L/Cを開設する", "えるしーをかいせつする", "mở thư tín dụng L/C tại ngân hàng người mua", "Người nhập khẩu làm thủ tục đề nghị ngân hàng phát hành thư tín dụng thanh toán cho bên bán nước ngoài.", "Open an L/C (Issue Letter of Credit)", "trade", "PRO-A1", 100, "信用状", "契約締結後、直ちに取引銀行でL/Cを開設しました。"),
    ("ディスクレを解消する", "でぃすくれをかいしょうする", "xử lý khắc phục sai sót chứng từ L/C", "Sửa đổi chứng từ hoặc xin người mua chấp thuận thanh toán khi chứng từ không khớp chính xác với điều khoản L/C.", "Resolve a discrepancy in L/C documents", "trade", "PRO-A1", 99, "ディスクレ", "インボイスの記載ミスを修正し、ディスクレを解消しました。"),
    ("為替予約を結ぶ", "かわせよやくをむすぶ", "ký hợp đồng chốt trước tỷ giá hối đoái với ngân hàng", "Cố định mức tỷ giá tương lai với ngân hàng để tránh rủi ro thua lỗ do đồng Yên biến động mạnh.", "Conclude forward exchange contract", "trade", "PRO-A1", 99, "為替リスクヘッジ", "円安リスクを避けるため、銀行と為替予約を結びました。"),
    ("原産地証明書を取得する", "げんさんちしょうめいしょをしゅとくする", "xin cấp chứng nhận xuất xứ hàng hóa C/O", "Nộp hồ sơ chứng minh xuất xứ lên Phòng Thương mại để được cấp chứng nhận giảm thuế ưu đãi.", "Obtain Certificate of Origin", "trade", "PRO-A1", 100, "特定原産地証明書", "EPA税率の適用を受けるため、商工会議所で原産地証明書を取得しました。")
]

print(f"Total defined workplace expressions: {len(EXPRESSION_DEFINITIONS)}")
assert len(EXPRESSION_DEFINITIONS) == 50, f"Expected 50, got {len(EXPRESSION_DEFINITIONS)}"

# Write out expressions.py
with open(OUT_FILE, "w", encoding="utf-8") as f:
    f.write('"""\nscripts/pilot_builder/expressions.py\nAuthoritative 50 canonical workplace expressions.\n"""\n\n')
    f.write('EXPRESSION_ITEMS = [\n')
    for item in EXPRESSION_DEFINITIONS:
        surface, reading, vi_short, vi_exp, en_pref, domain, tier, priority, rel_term, ex_ja = item
        f.write(f'    {{"surface": "{surface}", "reading": "{reading}", "vi_short": "{vi_short}", "vi_explanation": "{vi_exp}", "en_preferred": "{en_pref}", "domain": "{domain}", "tier": "{tier}", "priority": {priority}, "related_term": "{rel_term}", "example_ja": "{ex_ja}"}},\n')
    f.write(']\n')

print(f"[+] Wrote {len(EXPRESSION_DEFINITIONS)} expressions to {OUT_FILE}")
