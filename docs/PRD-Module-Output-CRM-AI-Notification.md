
TÀI LIỆU ĐẶC TẢ SẢN PHẨM
PRODUCT REQUIREMENTS DOCUMENT (PRD)

MODULE OUTPUT
CRM Quản lý cho Cán bộ &amp; Hệ thống AI Gửi thông báo tự động
Hệ thống Cảnh báo Thời tiết Thông minh tỉnh Điện Biên (DBWAS)

Mã module:
DBWAS-OUTPUT-001
Phiên bản:
1.0
Ngày tạo:
17/07/2026
Trạng thái:
Draft — Chờ phê duyệt
Thuộc dự án:
DBWAS-2025

Lịch sử phiên bản
Phiên bản
Ngày
Tác giả
Mô tả
1.0
17/07/2026
Ban Dự án
Bản khởi tạo — Đặc tả Output module

Phê duyệt
Họ và tên
Vai trò
Ngày
Chữ ký

Product Owner



Tech Lead



UX Lead



Mục lục
TOC \h \o &quot;1-3&quot;


1. Tổng quan Module Output
1.1. Mục đích
Module Output là tầng phân phối cuối cùng của hệ thống DBWAS, chịu trách nhiệm đưa thông tin cảnh báo thời tiết đến đúng người, đúng kênh, đúng ngôn ngữ và cung cấp công cụ quản lý/giám sát cho cán bộ các cấp. Module gồm hai thành phần chính:
Thành phần 1 — CRM Dashboard: Giao diện quản lý và thống kê dành cho cán bộ cấp xã, huyện, tỉnh — theo dõi tình hình thời tiết, trạng thái gửi thông báo và phản hồi từ cơ sở.
Thành phần 2 — Hệ thống AI gửi thông báo tự động: Phân phối cảnh báo đến người dân, trưởng bản, cán bộ xã qua đa kênh (Zalo, SMS, cuộc gọi tổng đài, file audio loa phát thanh) với nội dung được cá nhân hóa theo dân tộc và vai trò.
1.2. Đối tượng sử dụng
Đối tượng
Thành phần sử dụng
Mô tả
Cán bộ quản lý cấp tỉnh/huyện
CRM Dashboard
Xem tổng quan toàn tỉnh, theo dõi trạng thái gửi tin và phản hồi, xuất thống kê
Cán bộ quản lý cấp xã
CRM Dashboard + Nhận thông báo
Xem chi tiết xã quản lý, nhận thông báo qua Zalo/SMS, phản hồi xác nhận
Trưởng bản
Nhận thông báo + Audio loa
Nhận SMS/Zalo/cuộc gọi + file audio phát loa phát thanh
Người dân
Nhận thông báo
Nhận SMS/Zalo/cuộc gọi tự động bằng tiếng dân tộc
1.3. Phạm vi tài liệu
Tài liệu này đặc tả chi tiết hai thành phần của Module Output bao gồm: các màn hình giao diện CRM, luồng gửi thông báo tự động, quy tắc định danh và phân loại người nhận, chiến lược đa kênh đa ngôn ngữ, và các yêu cầu phi chức năng liên quan. Tài liệu không bao gồm phần thu thập dữ liệu thời tiết (Module Input) và phần xử lý/phân tích rủi ro (Module Processing).

2. CRM Dashboard — Quản lý &amp; Thống kê cho Cán bộ
2.1. Tổng quan CRM Dashboard
CRM Dashboard là giao diện web dành cho cán bộ quản lý các cấp, cung cấp cái nhìn tổng hợp về tình hình thời tiết toàn tỉnh, trạng thái phân phối thông báo và phản hồi từ cơ sở. Dashboard được thiết kế theo nguyên tắc: nhìn tổng thể trước, drill-down chi tiết sau.
2.2. Màn hình Dashboard tổng quan tỉnh
2.2.1. Mô tả chức năng
Hiển thị toàn cảnh tình hình thời tiết và trạng thái phân phối thông báo trên toàn tỉnh Điện Biên. Đây là màn hình mặc định khi cán bộ đăng nhập hệ thống.
2.2.2. Thành phần giao diện

A. Thanh tiêu đề (Header Bar):
Logo hệ thống + tên &quot;DBWAS — Hệ thống Cảnh báo Thời tiết Điện Biên&quot;
Hiển thị thời gian hiện tại và thời điểm cập nhật dữ liệu gần nhất
Tên cán bộ đăng nhập + dropdown đăng xuất
Badge thông báo: số lượng alert chưa xử lý (icon chuông, số đỏ)

B. Bộ thẻ tóm tắt (Summary Cards):
Hàng ngang 4 thẻ lớn hiển thị chỉ số tổng hợp toàn tỉnh:
Thẻ
Nội dung
Màu nền
Hành vi khi click
Tổng xã có cảnh báo
Số xã đang ở cấp Vàng/Cam/Đỏ / Tổng xã
Đỏ nếu có cấp Đỏ, Cam nếu cao nhất là Cam
Scroll xuống bản đồ, filter xã có cảnh báo
Thông báo đã gửi hôm nay
Tổng số tin nhắn (SMS + Zalo + Cuộc gọi) đã gửi trong ngày
Xanh dương
Mở trang Thống kê thông báo
Chưa nhận phản hồi đủ
Số xã đã gửi thông báo nhưng tỷ lệ xác nhận &lt; 50%
Cam cảnh báo
Scroll xuống bản đồ, highlight các xã này
Chờ xử lý
Số alert mới chưa được cán bộ xem/xác nhận
Đỏ nếu &gt; 0
Mở danh sách alert chờ xử lý

C. Bản đồ tỉnh Điện Biên (Map View) — Thành phần trọng tâm:
Bản đồ tương tác hiển thị ranh giới hành chính đến cấp xã, mỗi xã được tô màu và gắn icon theo trạng thái.

Hệ thống mã màu xã theo trạng thái phân phối thông báo:
Màu
Mã hex
Trạng thái
Ý nghĩa
Xanh lá
#27AE60
Đã gửi — Phản hồi đủ
Thông báo đã gửi VÀ ≥ 80% trưởng bản/cán bộ xã đã xác nhận nhận được
Vàng
#F1C40F
Đã gửi — Đang nhận phản hồi
Thông báo đã gửi nhưng tỷ lệ xác nhận mới đạt 30–79%
Cam
#E67E22
Đã gửi — Chưa nhận phản hồi đủ
Thông báo đã gửi nhưng tỷ lệ xác nhận &lt; 30% hoặc quá 30 phút chưa có phản hồi
Đỏ
#E74C3C
Chưa gửi thông báo
Có cảnh báo thời tiết nhưng thông báo chưa được phát hành (lỗi hệ thống hoặc chờ duyệt)
Xám nhạt
#BDC3C7
Không có cảnh báo
Khu vực an toàn, không có alert nào đang active

Hệ thống icon thiên tai trên bản đồ:
Icon
Loại thiên tai
Hiển thị khi
Vị trí trên bản đồ
🌧️ (giọt mưa)
Mưa lớn
Dự báo mưa tích lũy &gt; 30mm/3h
Tâm xã bị ảnh hưởng
⛰️ (núi nứt)
Sạt lở đất
Mưa &gt; 30mm &amp; độ dốc &gt; 30° hoặc cảnh báo thủ công
Tâm xã bị ảnh hưởng
🌊 (sóng nước)
Ngập lụt / Lũ quét
Mực nước vượt ngưỡng hoặc mưa tích lũy &gt; 50mm/3h
Tâm xã bị ảnh hưởng
🌫️ (mây mù)
Sương mù dày
Tầm nhìn &lt; 500m
Tâm xã bị ảnh hưởng
❄️ (bông tuyết)
Sương muối / Rét hại
Nhiệt độ &lt; 8°C &amp; ẩm &gt; 70%
Tâm xã bị ảnh hưởng
💨 (gió)
Gió mạnh
Tốc độ gió &gt; 40 km/h
Tâm xã bị ảnh hưởng

Tương tác với bản đồ:
Zoom in/out: cuộn chuột hoặc pinch trên mobile; mức zoom từ toàn tỉnh → cấp huyện → cấp xã.
Hover lên xã: tooltip hiển thị tên xã, cấp cảnh báo hiện tại, số thông báo đã gửi, tỷ lệ phản hồi.
Click vào xã: mở panel chi tiết xã (xem mục 2.3 bên dưới).
Nhiều icon trên cùng xã: hiển thị chồng icon với badge số lượng loại thiên tai.
Icon nhấp nháy: khi alert ở cấp Đỏ, icon nhấp nháy để thu hút chú ý.
Filter: thanh filter phía trên bản đồ cho phép lọc theo huyện, theo loại thiên tai, theo trạng thái phân phối.

D. Bảng tổng hợp theo huyện (dưới bản đồ):
Huyện
Số xã có cảnh báo
Cấp cao nhất
Thông báo đã gửi
Tỷ lệ phản hồi
Trạng thái
Tủa Chùa
5/12
Đỏ
1.245 tin
72%
Đang xử lý
Mường Nhé
3/8
Cam
856 tin
45%
Cần chú ý
Tuần Giáo
1/10
Vàng
320 tin
91%
Ổn định
(ví dụ)
...
...
...
...
...
Sort: click header để sort theo bất kỳ cột nào; mặc định sort theo cấp cao nhất (Đỏ lên đầu).
Highlight: hàng có tỷ lệ phản hồi &lt; 50% được highlight cam.
Click hàng: mở trang chi tiết huyện (danh sách xã kèm trạng thái).

2.3. Màn hình Chi tiết xã (Commune Detail Panel)
2.3.1. Cách mở
Click vào một xã trên bản đồ → panel trượt ra từ bên phải (slide-in panel, chiếm 40% chiều rộng màn hình desktop). Trên mobile: chuyển sang trang mới full-screen.
2.3.2. Thành phần hiển thị

A. Header xã:
Tên xã + tên huyện
Badge cấp cảnh báo hiện tại (Xanh/Vàng/Cam/Đỏ) — lớn, dễ thấy
Icon loại thiên tai đang active (có thể nhiều icon)
Thời gian cập nhật gần nhất

B. Thông tin thời tiết hiện tại:
Nhiệt độ hiện tại, min/max trong ngày
Lượng mưa tích lũy 3h, 6h, 24h
Tốc độ gió, tầm nhìn, độ ẩm
Biểu đồ mini (sparkline) 24h gần nhất cho nhiệt độ và lượng mưa

C. Trạng thái thông báo tại xã:
Chỉ số
Giá trị mẫu
Ghi chú
Tổng thông báo đã gửi
324 tin
Gồm SMS + Zalo + Cuộc gọi
SMS đã gửi
180 tin (thành công: 172, lỗi: 8)
Hiện % thành công
Zalo đã gửi
120 tin (đã đọc: 95, chưa đọc: 25)
Hiện % đã đọc
Cuộc gọi tổng đài
24 cuộc (nghe máy: 18, không nghe: 6)
Hiện % nghe máy
Trưởng bản đã xác nhận
8/12 thôn bản
Danh sách thôn chưa xác nhận
Cán bộ xã đã xác nhận
2/3 cán bộ
Tên cán bộ chưa xác nhận

D. Danh sách thôn bản trong xã:
Thôn bản
Trưởng bản
Kênh đã gửi
Phản hồi
Loa phát thanh
Hành động
Bản Huổi Lóng
(tên)
SMS ✓ Zalo ✓ Gọi ✓
Đã nhận + Đã phát loa
Đã tải audio
—
Bản Nà Hì
(tên)
SMS ✓ Zalo ✗
Chưa phản hồi
Chưa tải
Gửi lại | Gọi
(ví dụ)
...
...
...
...
...
Nút &quot;Gửi lại&quot;: gửi lại thông báo qua kênh đã lỗi cho thôn bản cụ thể.
Nút &quot;Gọi&quot;: kích hoạt cuộc gọi tổng đài đến trưởng bản của thôn đó.
Highlight hàng đỏ: thôn bản chưa phản hồi sau 30 phút kể từ khi gửi.

2.4. Màn hình Thống kê thông báo
2.4.1. Mô tả
Trang thống kê chi tiết toàn bộ thông báo đã gửi, cho phép lọc theo nhiều chiều: khu vực, thời gian, kênh gửi, nội dung, trạng thái.
2.4.2. Bộ lọc (Filter Bar)
Bộ lọc
Loại control
Giá trị
Mặc định
Thời gian
Date range picker
Từ ngày — Đến ngày
7 ngày gần nhất
Huyện
Multi-select dropdown
Tất cả huyện trong tỉnh
Tất cả
Xã
Multi-select dropdown (lọc theo huyện đã chọn)
Danh sách xã
Tất cả
Kênh gửi
Checkbox group
SMS / Zalo / Cuộc gọi / Audio loa
Tất cả
Trạng thái
Checkbox group
Thành công / Lỗi / Đang chờ / Đã đọc
Tất cả
Loại cảnh báo
Multi-select dropdown
Mưa lớn / Sạt lở / Ngập / Sương muối / ...
Tất cả

2.4.3. Bảng dữ liệu chi tiết
Cột
Mô tả
Sortable
Ghi chú
Thời gian gửi
Timestamp dd/mm/yyyy HH:mm
Có
Mặc định sort giảm dần
Khu vực
Xã — Huyện
Có
Hiện đầy đủ tên xã + huyện
Loại cảnh báo
Mưa lớn / Sạt lở / Ngập / ...
Có
Icon + text
Cấp độ
Vàng / Cam / Đỏ
Có
Badge màu
Nội dung
Text bản tin đã gửi (rút gọn 50 ký tự)
Không
Hover để xem đầy đủ
Kênh
SMS / Zalo / Gọi / Audio
Có
Icon kênh
SĐT / Zalo ID
Số điện thoại hoặc Zalo ID người nhận
Không
Che bớt: 09xx-xxx-456
Trạng thái
Thành công / Lỗi / Đã đọc / Không nghe máy
Có
Badge trạng thái
Phản hồi
Nội dung phản hồi (nếu có): 1/2/3
Có
1=Nhận, 2=Phát loa, 3=Cần hỗ trợ

2.4.4. Biểu đồ thống kê
Biểu đồ cột (Bar chart): Số lượng thông báo theo ngày, phân chia theo kênh (SMS/Zalo/Gọi) — stacked bar.
Biểu đồ tròn (Pie chart): Phân bổ trạng thái: Thành công vs Lỗi vs Đang chờ.
Biểu đồ đường (Line chart): Tỷ lệ phản hồi theo ngày — đường trend.
Bản đồ nhiệt (Heat map): Tỷ lệ gửi thành công theo xã — xã nào hay lỗi nhất.
2.4.5. Xuất dữ liệu
Nút &quot;Xuất Excel&quot;: export toàn bộ dữ liệu đã lọc ra file .xlsx.
Nút &quot;Xuất PDF&quot;: export báo cáo tổng hợp dạng PDF có biểu đồ + bảng.
Nút &quot;In báo cáo&quot;: mở print preview với layout chuẩn A4.

3. Hệ thống AI gửi thông báo tự động
3.1. Tổng quan luồng gửi thông báo
Khi Alert Engine phát hiện vượt ngưỡng và sinh bản tin cảnh báo, Hệ thống AI gửi thông báo tự động thực hiện phân phối theo luồng sau:

Bước 1 — Định danh người nhận: Tra cứu danh sách liên lạc trong vùng bị ảnh hưởng → xác định vai trò (người dân / trưởng bản / cán bộ xã), dân tộc, kênh liên lạc khả dụng.
Bước 2 — Cá nhân hóa nội dung: Chọn template bản tin phù hợp vai trò → dịch sang ngôn ngữ dân tộc (nếu cần) → chuẩn hóa nội dung.
Bước 3 — Phân phối đa kênh: Gửi đồng thời qua tất cả kênh khả dụng cho từng người nhận (Zalo + SMS cho người có smartphone; SMS + Cuộc gọi cho người không biết chữ; Audio loa cho trưởng bản).
Bước 4 — Theo dõi &amp; Escalation: Ghi log delivery → chờ phản hồi → escalation nếu không nhận phản hồi đủ trong 30 phút.

3.2. Định danh người nhận (User Identification)
3.2.1. Thuộc tính định danh
Thuộc tính
Bắt buộc
Mục đích sử dụng
Nguồn dữ liệu
Số điện thoại
Có
Định danh chính (unique key); gửi SMS; gọi tổng đài
Cán bộ xã nhập hoặc import Excel
Họ tên
Có
Hiển thị trên dashboard, trong bản tin (nếu cần)
Cán bộ xã nhập
Vai trò
Có
Quyết định loại bản tin + kênh gửi + nội dung bổ sung
Cán bộ xã phân loại
Dân tộc
Có
Quyết định ngôn ngữ bản tin: Kinh → Việt, Thái → tiếng Thái, Mông → tiếng Mông
Cán bộ xã nhập
Xã / Thôn bản
Có
Quyết định người nhận khi có alert tại khu vực
Cán bộ xã nhập
Zalo ID
Không
Gửi tin Zalo nếu có; nếu không có chỉ gửi SMS
User follow Zalo OA + đăng ký
Khả năng đọc chữ
Không
Nếu không biết chữ → bổ sung cuộc gọi tổng đài bằng tiếng dân tộc
Cán bộ xã đánh dấu

3.2.2. Phân loại vai trò và chiến lược gửi tin
Vai trò
Kênh gửi
Nội dung bản tin
Bổ sung đặc biệt
Người dân (dân tộc Kinh)
SMS + Zalo
Bản tin ngắn gọn tiếng Việt ≤ 50 từ, mệnh lệnh hành động
—
Người dân (dân tộc Thái)
SMS + Zalo + Cuộc gọi tổng đài
Bản tin tiếng Thái; SMS không dấu; Cuộc gọi đọc tiếng Thái
Cuộc gọi tự động bằng tiếng Thái cho người không biết chữ
Người dân (dân tộc Mông)
SMS + Zalo + Cuộc gọi tổng đài
Bản tin tiếng Mông; SMS không dấu; Cuộc gọi đọc tiếng Mông
Cuộc gọi tự động bằng tiếng Mông cho người không biết chữ
Trưởng bản
SMS + Zalo + Cuộc gọi + Audio file
Bản tin cán bộ (chi tiết hơn) + file audio phát loa phát thanh
Nhận file audio MP3 qua Zalo/link để phát loa xã/bản
Cán bộ quản lý cấp xã
SMS + Zalo + Email (nếu có)
Bản tin cán bộ đầy đủ: số liệu + hành động + số liên hệ
Push notification trên CRM Dashboard

3.3. Kênh gửi SMS
3.3.1. Đặc tả kỹ thuật
Hạng mục
Đặc tả
Provider
SpeedSMS hoặc eSMS (primary); VNPT SMS Brandname (fallback)
Brandname
DBWAS hoặc tên đơn vị PCTT được cấp phép
Giới hạn ký tự
≤ 160 ký tự không dấu (GSM-7 encoding) để tối ưu chi phí
Encoding
Không dấu (remove diacritics) cho tất cả SMS — đảm bảo feature phone hiển thị đúng
Tốc độ gửi
Tối đa 100 SMS/batch, chờ 2 giây giữa các batch
Retry
Nếu gửi lỗi → retry 3 lần, cách nhau 30 giây; sau 3 lần → ghi log lỗi
Fallback
Nếu provider chính lỗi liên tiếp 5 tin → auto-switch sang provider phụ

3.3.2. Template SMS theo vai trò

SMS cho người dân (tiếng Việt, không dấu):
[CANH BAO CAM] Mua to tai Tua Chua toi nay. Khong qua suoi. Dat trau ve chuong. Lien he truong ban neu can. Tra loi 1=Da nhan.

SMS cho người dân (tiếng Thái, không dấu — dịch từ template):
[CANH BAO] Phan lon tai Tua Chua khuam. Bok xam nam. Klap huon. Tra loi 1=Da nhan.

SMS cho trưởng bản:
[CANH BAO CAM] Mua 80-120mm/6h tai Tua Chua. (1) Phat loa ngay (2) Kiem tra ho ven suoi (3) San sang so tan. Tra loi 1=Nhan 2=Phat loa 3=Can ho tro.

3.4. Kênh gửi Zalo
3.4.1. Đặc tả kỹ thuật
Hạng mục
Đặc tả
Loại tài khoản
Zalo Official Account (OA) — cần đăng ký doanh nghiệp
Đăng ký nhận tin
User follow OA → nhắn &quot;DANG KY [TÊN XÃ]&quot; → hệ thống lưu Zalo ID + khu vực
Loại tin nhắn
Rich message: banner ảnh + text + button
Banner ảnh
Ảnh nền tự động đổi màu theo cấp cảnh báo: Xanh/Vàng/Cam/Đỏ + icon thiên tai
Nội dung text
Bản tin phù hợp vai trò (ngắn cho dân, đầy đủ cho cán bộ)
Button
&quot;Xem chi tiết&quot; → link web app dự báo; &quot;Xác nhận&quot; → gửi reply xác nhận
Giới hạn
Chỉ gửi được cho người đã follow OA; quota Zalo OA (kiểm tra với Zalo)
Attachment
Gửi file audio MP3 cho trưởng bản kèm tin nhắn

3.4.2. Luồng đăng ký Zalo
Người dùng tìm và follow Zalo OA &quot;DBWAS Điện Biên&quot;.
Zalo OA gửi tin chào mừng: &quot;Chào bạn! Nhắn DANG KY [tên xã] để nhận cảnh báo. Ví dụ: DANG KY TUA CHUA&quot;.
Người dùng nhắn tin đăng ký → hệ thống parse tên xã, lưu Zalo ID + location_id.
Hệ thống gửi xác nhận: &quot;Đã đăng ký nhận cảnh báo khu vực Tủa Chùa. Nhắn HUY để hủy đăng ký.&quot;.
Khi có alert tại khu vực → tự động push rich message đến tất cả Zalo ID đã đăng ký.

3.5. Kênh cuộc gọi tổng đài tự động (Auto-call)
3.5.1. Mục đích
Đây là kênh đặc biệt quan trọng dành cho người dân không biết chữ — đặc biệt đồng bào dân tộc thiểu số ở vùng sâu. Thay vì đọc SMS (không thể đọc) hay xem Zalo (không có smartphone), họ nhận cuộc gọi tự động phát nội dung cảnh báo bằng chính tiếng dân tộc của mình.
3.5.2. Đặc tả kỹ thuật
Hạng mục
Đặc tả
Provider
StringeeX, VBEE, hoặc tổng đài VoIP tương đương hỗ trợ auto-call API
Trigger
Tự động khi: (1) Người nhận được đánh dấu &quot;không biết chữ&quot; HOẶC (2) Alert cấp Đỏ (gọi cho tất cả người dân trong vùng)
Nội dung cuộc gọi
File audio TTS đã sinh sẵn bằng ngôn ngữ dân tộc của người nhận
Thời lượng
15–30 giây; phát 2 lần liên tiếp trong 1 cuộc gọi
Mở đầu
3 giây âm hiệu cảnh báo (alert chime) → nội dung
Nhấn phím xác nhận
Sau khi phát xong: &quot;Nhấn phím 1 nếu đã nghe rõ&quot; → ghi nhận phản hồi DTMF
Không nghe máy
Nếu không nghe → retry sau 5 phút, tối đa 3 lần; sau 3 lần → đánh dấu &quot;không liên lạc được&quot;
Giờ gọi
Chỉ gọi 6:00–22:00; alert Đỏ ban đêm vẫn gọi (khẩn cấp)
Ưu tiên
Gọi người dân không biết chữ trước; sau đó mở rộng nếu cấp Đỏ

3.5.3. Nội dung cuộc gọi mẫu

Tiếng Việt:
[Âm hiệu cảnh báo 3 giây] — Cảnh báo thời tiết khẩn cấp tại xã Tủa Chùa. Tối nay có mưa rất to. Không đi qua suối. Đưa trâu bò về chuồng. Ở trong nhà chắc chắn. — [Lặp lại 1 lần] — Nhấn phím 1 nếu bạn đã nghe rõ.

Tiếng Thái (Tây Bắc) — nội dung tương đương:
[Âm hiệu] — (nội dung tiếng Thái đã được kiểm duyệt từ template dịch) — [Lặp lại] — (hướng dẫn nhấn phím 1 bằng tiếng Thái).

Tiếng Mông — nội dung tương đương:
[Âm hiệu] — (nội dung tiếng Mông đã được kiểm duyệt từ template dịch) — [Lặp lại] — (hướng dẫn nhấn phím 1 bằng tiếng Mông).

3.6. Kênh audio loa phát thanh
3.6.1. Mục đích
Dành riêng cho trưởng bản — nhận file audio MP3 cảnh báo đã được sinh tự động, để phát qua hệ thống loa phát thanh xã/bản. Đây là kênh tiếp cận toàn bộ cộng đồng trong bản mà không phụ thuộc vào điện thoại cá nhân.
3.6.2. Đặc tả
Hạng mục
Đặc tả
Định dạng
MP3, bitrate 128kbps, mono
Dung lượng
&lt; 500KB (phù hợp gửi qua Zalo, download qua 3G chậm)
Thời lượng
20–40 giây
Cấu trúc audio
[Âm hiệu 3s] → [Nội dung cảnh báo] → [Hướng dẫn hành động] → [Repeat nội dung 1 lần]
Giọng đọc
TTS giọng nữ miền Bắc, tốc độ chậm hơn 20% so với chuẩn
Ngôn ngữ
Sinh 3 phiên bản: tiếng Việt, tiếng Thái, tiếng Mông (trưởng bản chọn phiên bản phù hợp)
Phân phối
Gửi kèm tin Zalo (attachment) + link download trong SMS
Tần suất phát loa
Đề nghị phát 3 lần, cách nhau 15–30 phút (hiện text khuyến nghị khi gửi file)

3.6.3. Luồng phân phối audio
Alert Engine kích hoạt cảnh báo tại khu vực X.
AI Bulletin Generator sinh bản tin text cho trưởng bản.
TTS Engine chuyển text → file audio MP3 (3 ngôn ngữ).
Distribution Router gửi file audio cho trưởng bản qua: Zalo (attachment MP3) + SMS (link download ngắn).
Trưởng bản tải file → kết nối điện thoại/USB với loa phát thanh → phát.
Trưởng bản reply xác nhận: &quot;2&quot; = Đã phát loa.

3.7. Quy tắc chuẩn hóa nội dung thông báo
3.7.1. Nguyên tắc chung
Mỗi thông báo phải có cấu trúc cố định để người nhận quen thuộc và nhận diện nhanh.
Không dùng thuật ngữ kỹ thuật (mm, mbar, m/s) trong bản tin cho người dân.
Dùng mệnh lệnh hành động trực tiếp: &quot;Không qua suối&quot;, &quot;Về nhà ngay&quot;, &quot;Dắt trâu về&quot;.
Mỗi bản tin chỉ tập trung 1 thông điệp chính + tối đa 3 hành động.

3.7.2. Cấu trúc chuẩn hóa bản tin
Thành phần
Vị trí
Ví dụ
Bắt buộc
Tag cấp độ
Mở đầu
[CANH BAO CAM] hoặc [CANH BAO DO]
Có
Loại thiên tai
Sau tag
Mua to / Sat lo / Ngap / Suong muoi
Có
Khu vực
Sau loại
tai Tua Chua / tai ban Huoi Long
Có
Thời gian
Sau khu vực
toi nay / sang mai / trong 6 gio toi
Có
Hành động 1
Dòng tiếp theo
Khong qua suoi
Có
Hành động 2
Dòng tiếp theo
Dat trau ve chuong
Tùy chọn
Hành động 3
Dòng tiếp theo
Lien he truong ban
Tùy chọn
Yêu cầu phản hồi
Cuối tin
Tra loi 1=Da nhan
Có (SMS)
3.7.3. Ma trận ngôn ngữ theo dân tộc
Dân tộc người nhận
SMS
Zalo text
Cuộc gọi audio
Audio loa phát thanh
Kinh
Tiếng Việt không dấu
Tiếng Việt có dấu
Tiếng Việt TTS
Tiếng Việt TTS
Thái
Tiếng Thái không dấu (Latin hóa)
Tiếng Thái (chữ Thái nếu hỗ trợ, không thì Latin)
Tiếng Thái TTS / Thu âm
Tiếng Thái TTS / Thu âm
Mông / Hmong
Tiếng Mông không dấu (RPA)
Tiếng Mông (RPA Hmong)
Tiếng Mông TTS / Thu âm
Tiếng Mông TTS / Thu âm
Khác
Tiếng Việt không dấu
Tiếng Việt có dấu
Tiếng Việt TTS
Tiếng Việt TTS

Lưu ý: Khi TTS chưa hỗ trợ chất lượng tốt cho tiếng Thái/Mông, hệ thống sử dụng file audio thu âm sẵn bởi người bản địa cho các template cảnh báo phổ biến nhất (khoảng 20 template). Chỉ dùng TTS khi đã kiểm tra chất lượng đạt yêu cầu.

3.8. Chiến lược gửi đa kênh đồng thời
3.8.1. Nguyên tắc
Gửi đồng thời qua tất cả kênh khả dụng của người nhận, không gửi tuần tự và chờ — lý do: vùng sâu sóng yếu, SMS có thể đến chậm, Zalo cần 3G/4G. Gửi đồng thời đảm bảo ít nhất 1 kênh đến được.

3.8.2. Ma trận kênh theo cấp cảnh báo
Cấp cảnh báo
Người dân
Trưởng bản
Cán bộ xã
Ghi chú
Vàng (Lưu ý)
—
SMS + Zalo
SMS + Zalo + Dashboard
Chỉ gửi cán bộ/trưởng bản, chưa gửi người dân
Cam (Nguy hiểm)
SMS + Zalo
SMS + Zalo + Audio + Gọi
SMS + Zalo + Dashboard
Gửi người dân đã đăng ký; trưởng bản nhận thêm audio loa
Đỏ (Rất nguy hiểm)
SMS + Zalo + Gọi
SMS + Zalo + Audio + Gọi
SMS + Zalo + Dashboard + Gọi
Gọi tất cả; người không biết chữ được gọi bằng tiếng dân tộc

3.8.3. Thứ tự ưu tiên khi hệ thống quá tải
Khi có alert Đỏ ở nhiều khu vực cùng lúc, hệ thống gửi theo thứ tự ưu tiên:
Trưởng bản và cán bộ xã ở vùng Đỏ (họ là relay node — phát loa cho cả cộng đồng).
Người dân ở vùng Đỏ.
Trưởng bản và cán bộ ở vùng Cam.
Người dân ở vùng Cam.
Cán bộ ở vùng Vàng.

4. Yêu cầu phi chức năng
Mã
Hạng mục
Yêu cầu
NFR-01
Thời gian gửi
Từ khi alert kích hoạt đến khi tin nhắn đầu tiên rời hệ thống: ≤ 60 giây
NFR-02
Tỷ lệ gửi thành công
SMS ≥ 95%, Zalo ≥ 90%, Cuộc gọi ≥ 80% (nghe máy)
NFR-03
Throughput
Hỗ trợ gửi ≥ 5.000 tin nhắn/giờ đồng thời (SMS + Zalo + Cuộc gọi)
NFR-04
Dashboard load
Trang dashboard tải ≤ 3 giây; bản đồ render ≤ 5 giây
NFR-05
Real-time
Dashboard cập nhật trạng thái mỗi 30 giây (WebSocket hoặc polling)
NFR-06
Khả dụng
Uptime ≥ 99.5%; SMS gateway có ≥ 2 provider; auto-failover
NFR-07
Bảo mật
SĐT mã hóa at-rest; dashboard yêu cầu login (JWT); phân quyền theo cấp hành chính
NFR-08
Responsive
Dashboard hoạt động trên desktop (1280px+) và tablet (768px+); mobile hiển thị simplified view
NFR-09
Lưu trữ
Log gửi tin và phản hồi lưu tối thiểu 24 tháng; export được
NFR-10
Phân quyền
Cán bộ xã chỉ xem data xã mình; cán bộ huyện xem các xã trong huyện; cấp tỉnh xem tất cả
NFR-11
Audio TTS
File audio sinh ≤ 10 giây; chất lượng nghe rõ qua loa phát thanh ngoài trời
NFR-12
Cuộc gọi đồng thời
Hỗ trợ ≥ 50 cuộc gọi đồng thời; queue khi vượt giới hạn

5. Ma trận phân quyền CRM Dashboard
Chức năng
Cán bộ xã
Cán bộ huyện
Cán bộ tỉnh
Admin
Xem dashboard tổng quan tỉnh
Không
Có (huyện mình)
Có (toàn tỉnh)
Có
Xem bản đồ
Xã mình
Huyện mình
Toàn tỉnh
Toàn tỉnh
Xem chi tiết xã
Xã mình
Các xã trong huyện
Tất cả xã
Tất cả xã
Xem thống kê thông báo
Xã mình
Huyện mình
Toàn tỉnh
Toàn tỉnh
Xuất báo cáo
Xã mình
Huyện mình
Toàn tỉnh
Toàn tỉnh
Gửi thông báo thủ công
Không
Có (xã trong huyện)
Có (toàn tỉnh)
Có
Gửi lại / Gọi lại
Xã mình
Xã trong huyện
Tất cả
Tất cả
Quản lý danh sách liên lạc
Xã mình
Xã trong huyện
Tất cả
Tất cả
Quản lý ngưỡng cảnh báo
Không
Không
Có
Có
Quản lý locations
Không
Không
Có
Có
Duyệt bản dịch
Không
Không
Có
Có
Quản lý tài khoản cán bộ
Không
Không
Không
Có

6. Luồng nghiệp vụ chính (Business Flows)
6.1. Luồng 1 — Gửi thông báo tự động khi có alert
Alert Engine phát hiện chỉ số vượt ngưỡng tại khu vực X → tạo Alert record.
AI Bulletin Generator sinh 3 phiên bản bản tin (dân / trưởng bản / cán bộ) bằng tiếng Việt.
Translation Service dịch bản tin sang tiếng Thái, tiếng Mông (từ template đã duyệt hoặc LLM).
TTS Engine sinh file audio cho: cuộc gọi tổng đài (3 ngôn ngữ) + audio loa phát thanh (3 ngôn ngữ).
Distribution Router truy vấn danh sách contacts thuộc khu vực X → phân loại theo vai trò + dân tộc.
Router quyết định kênh gửi cho từng người (theo ma trận 3.8.2) → đẩy vào message queue.
SMS Sender, Zalo Sender, Auto-call Sender xử lý queue đồng thời → ghi delivery_log.
CRM Dashboard cập nhật real-time: bản đồ đổi màu xã, bảng trạng thái cập nhật.
Hệ thống chờ phản hồi (SMS reply, Zalo reply, DTMF phím 1) → ghi acknowledgment_log.
Sau 30 phút: nếu trưởng bản vùng Cam/Đỏ chưa phản hồi → escalation lên cán bộ huyện.
6.2. Luồng 2 — Cán bộ xem dashboard và can thiệp
Cán bộ đăng nhập CRM Dashboard → thấy bản đồ tỉnh với màu sắc trạng thái.
Nhận thấy xã A có màu Cam (chưa nhận phản hồi đủ) → click vào xã A.
Panel chi tiết xã A mở ra → thấy thôn bản B chưa phản hồi.
Click &quot;Gọi&quot; → hệ thống kích hoạt cuộc gọi tổng đài đến trưởng bản thôn B.
Hoặc click &quot;Gửi lại&quot; → hệ thống gửi lại SMS/Zalo cho thôn B.
Trưởng bản thôn B phản hồi → màu xã A chuyển từ Cam sang Xanh lá trên bản đồ.
6.3. Luồng 3 — Gửi cảnh báo thủ công
Cán bộ PCTT huyện/tỉnh đánh giá cần gửi cảnh báo bổ sung (ví dụ: thông tin sơ tán cụ thể).
Vào CRM Dashboard → chọn &quot;Gửi cảnh báo thủ công&quot;.
Chọn khu vực (huyện/xã), cấp độ, nhập nội dung bản tin tùy chỉnh.
Hệ thống preview bản tin 3 phiên bản + auto-translate → cán bộ xác nhận.
Click &quot;Gửi ngay&quot; → Distribution Router phân phối giống luồng 1.

7. Đặc tả API cho Module Output
Method
Endpoint
Mô tả
Phân quyền
GET
/api/dashboard/summary
Thẻ tóm tắt tổng quan tỉnh (4 cards)
Cán bộ huyện/tỉnh
GET
/api/dashboard/map-data
Dữ liệu bản đồ: danh sách xã + trạng thái + icon thiên tai
Cán bộ huyện/tỉnh
GET
/api/dashboard/districts
Bảng tổng hợp theo huyện
Cán bộ huyện/tỉnh
GET
/api/communes/{id}/detail
Chi tiết xã: thời tiết + trạng thái thông báo + danh sách thôn
Cán bộ xã/huyện/tỉnh
GET
/api/notifications
Danh sách thông báo đã gửi (có filter, pagination)
Cán bộ xã+
GET
/api/notifications/stats
Thống kê: biểu đồ theo ngày/kênh/trạng thái
Cán bộ huyện/tỉnh
GET
/api/notifications/export
Xuất Excel/PDF danh sách thông báo
Cán bộ huyện/tỉnh
POST
/api/notifications/resend
Gửi lại thông báo cho contact cụ thể
Cán bộ xã+
POST
/api/notifications/call
Kích hoạt cuộc gọi tổng đài đến SĐT cụ thể
Cán bộ xã+
POST
/api/alerts/manual
Tạo cảnh báo thủ công + phân phối
Cán bộ huyện/tỉnh
GET
/api/contacts
Danh sách liên lạc (filter theo xã/vai trò/dân tộc)
Cán bộ xã+
POST
/api/contacts/import
Import danh sách liên lạc từ file Excel
Cán bộ xã+
GET
/api/acknowledgments
Danh sách phản hồi + tỷ lệ theo khu vực
Cán bộ xã+
WS
/ws/dashboard
WebSocket real-time cập nhật trạng thái bản đồ + bảng
Cán bộ huyện/tỉnh

8. Tiêu chí nghiệm thu
Mã
Tiêu chí
Điều kiện đạt
AC-01
Bản đồ tỉnh hiển thị đúng
Bản đồ hiện ranh giới xã, tô màu đúng 5 trạng thái, icon thiên tai đúng loại; click xã mở panel chi tiết
AC-02
Gửi SMS tự động
Khi alert kích hoạt, SMS được gửi đến ≥ 95% danh sách trong ≤ 5 phút; nội dung đúng template, đúng ngôn ngữ
AC-03
Gửi Zalo tự động
Rich message có banner đúng màu cấp cảnh báo, nội dung đúng vai trò; button hoạt động
AC-04
Cuộc gọi tổng đài
Người nhận nghe cuộc gọi rõ ràng bằng đúng tiếng dân tộc; nhấn phím 1 ghi nhận phản hồi thành công
AC-05
Audio loa phát thanh
Trưởng bản nhận file audio qua Zalo; phát qua loa nghe rõ ngoài trời; đúng ngôn ngữ
AC-06
Thống kê thông báo
Bảng thống kê hiển thị đúng: khu vực, SĐT, kênh, trạng thái, nội dung; filter hoạt động; export Excel/PDF thành công
AC-07
Phản hồi và Escalation
Reply SMS/Zalo được ghi nhận trong ≤ 30 giây; DTMF phím 1 trong cuộc gọi ghi nhận đúng; escalation kích hoạt đúng thời gian
AC-08
Đa ngôn ngữ
Bản tin tiếng Thái và tiếng Mông hiển thị đúng; được ≥ 1 người bản địa xác nhận nội dung hiểu được
AC-09
Phân quyền
Cán bộ xã không xem được dữ liệu xã khác; cán bộ huyện chỉ xem trong huyện; cấp tỉnh xem tất cả
AC-10
Real-time dashboard
Bản đồ tự đổi màu trong ≤ 30 giây khi trạng thái phân phối thay đổi mà không cần reload

9. Ma trận ưu tiên triển khai
Mã
Tính năng
Độ quan trọng
Độ phức tạp
Phase
OUT-01
Gửi SMS tự động theo vai trò + cấp cảnh báo
Cao
Thấp
MVP
OUT-02
Template bản tin chuẩn hóa tiếng Việt
Cao
Thấp
MVP
OUT-03
Bản đồ tỉnh + mã màu 5 trạng thái
Cao
Trung bình
MVP
OUT-04
Click xã → panel chi tiết
Cao
Trung bình
MVP
OUT-05
Icon thiên tai trên bản đồ
Cao
Thấp
MVP
OUT-06
Bảng tổng hợp theo huyện
Cao
Thấp
MVP
OUT-07
Thống kê thông báo + Filter
Trung bình
Trung bình
MVP
OUT-08
Gửi Zalo OA
Trung bình
Trung bình
Phase 2
OUT-09
Dịch bản tin tiếng Thái / Mông
Cao
Cao
Phase 2
OUT-10
Cuộc gọi tổng đài tự động
Cao
Cao
Phase 2
OUT-11
Audio loa phát thanh (TTS)
Trung bình
Cao
Phase 2
OUT-12
Phân quyền theo cấp hành chính
Trung bình
Trung bình
Phase 2
OUT-13
WebSocket real-time dashboard
Trung bình
Trung bình
Phase 2
OUT-14
Gửi cảnh báo thủ công
Trung bình
Trung bình
Phase 2
OUT-15
Xuất báo cáo Excel/PDF
Thấp
Thấp
Phase 3
OUT-16
Escalation tự động khi thiếu phản hồi
Trung bình
Trung bình
Phase 3


— Hết tài liệu —
