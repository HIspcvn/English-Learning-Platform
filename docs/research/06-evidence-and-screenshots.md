# Bằng chứng khảo sát và ảnh chụp

Ngày 19/11/2026, múi giờ Asia/Saigon. Trình duyệt tích hợp ChatGPT, tài khoản người học đã có phiên. URL tương đối thuộc aioenglish.com. Giá trị cá nhân được lược bỏ, và `{session}` thay mã phiên luyện của tài khoản.

## Ảnh đã lưu

![RT-12 — Điều hướng đáy trong module Gõ câu ở viewport 390×844](screenshots/RT-12-mobile-navigation.jpg)

RT-12 ghi thanh điều hướng đáy sau khi đóng thông báo. Ảnh được cắt để chỉ giữ thanh điều hướng. Hình ảnh và nội dung gốc được giữ làm chứng cứ nghiên cứu.

![RT-19 — Ba chỉ số hiển thị sau khi hoàn tất Gõ câu](screenshots/RT-19-typing-completion.jpg)

RT-19 ghi phần số liệu trong màn tổng kết của bài đã hoàn tất. Các câu cuối được làm sau khi xem đáp án mẫu. Ảnh giữ nguyên nhãn Chính xác 0%, Combo 5 và +30 XP như hiển thị.

## Chỉ mục thao tác

<a id="rt-01"></a>

### RT-01 — Trang giới thiệu và lối vào demo

- **URL** `/`
- **Điều kiện** Khách (lần render đầu).
- **Thao tác và kết quả OBSERVED** Mở URL gốc; thấy sáu mô tả module, CTA login/register, app stores, FAQ, skip link và tile 6 câu demo không cần tài khoản. Hydration chuyển sang dashboard của phiên đã đăng nhập.
- **Phạm vi và giới hạn** Tile và lời giới thiệu quan sát được; vòng demo anonymous chưa chạy, số catalog chỉ là số hiển thị.

<a id="rt-02"></a>

### RT-02 — Biểu mẫu đăng nhập

- **URL** `/auth/login`
- **Điều kiện** Khách hoặc mở route trong phiên hiện có.
- **Thao tác và kết quả OBSERVED** Mở trang đăng nhập; thấy email/mật khẩu, điều khiển hiển thị mật khẩu, OAuth Google, khôi phục, điều khoản và đăng ký.
- **Phạm vi và giới hạn** Chỉ quan sát UI. Không nộp credentials, không khởi chạy OAuth.

<a id="rt-03"></a>

### RT-03 — Đăng ký và yêu cầu đặt lại

- **URL** `/auth/register`, `/auth/forgot`
- **Điều kiện** Khách hoặc mở route trong phiên hiện có.
- **Thao tác và kết quả OBSERVED** Mở hai trang. Đăng ký có email, mật khẩu và lặp mật khẩu, liên kết pháp lý và nút disabled khi trống. Quên mật khẩu có email và nút gửi link.
- **Phạm vi và giới hạn** Không tạo tài khoản, gửi email hay kiểm OTP/token.

<a id="rt-04"></a>

### RT-04 — Tra cứu điều khoản và quyền riêng tư

- **URL** `/phap-ly`, `/phap-ly/dieu-khoan`, `/phap-ly/quyen-rieng-tu`
- **Điều kiện** Khách/learner.
- **Thao tác và kết quả OBSERVED** Mở index và hai trang tiếng Việt. Điều khoản có mục dịch vụ miễn phí; privacy có mục xử lý giọng, AI, lưu trữ và xóa tài khoản. Index có link EN.
- **Phạm vi và giới hạn** Điều khoản là nội dung công bố. Checkout, gói hoặc quyền truy cập dựa trên subscription chưa thấy.

<a id="rt-05"></a>

### RT-05 — Dashboard lộ trình và kế hoạch ngày

- **URL** `/`
- **Điều kiện** Learner.
- **Thao tác và kết quả OBSERVED** Thấy menu module, điểm danh, 7 mục liên module có link bài, thanh phút và mục tiêu; chapter/progress/kiểm tra lên cấp và XP tháng. Ban đầu hiện 0/7 bài, 0/180 phút; trong khảo sát hiện 2/180 phút.
- **Phạm vi và giới hạn** Không tác động điểm danh hoặc tùy chọn bài. Chưa tách nguồn thời gian giữa các tab.

<a id="rt-06"></a>

### RT-06 — Mở chỉnh mục tiêu ngày

- **URL** `/`
- **Điều kiện** Learner.
- **Thao tác và kết quả OBSERVED** Mở nút mục tiêu từ dashboard → nút expanded; cửa sổ mục tiêu có lựa chọn phút/ngày được đối chiếu từ Roadmap/CV-09.
- **Phạm vi và giới hạn** Giữ nguyên mục tiêu 180 phút trong phiên; chưa thử ghi.

<a id="rt-07"></a>

### RT-07 — Hồ sơ và tùy chọn học/giao diện

- **URL** `/cai-dat`
- **Điều kiện** Learner.
- **Thao tác và kết quả OBSERVED** Đọc các vùng Hồ sơ, Bạn bè, Trình độ, Mục tiêu, Giọng và Giao diện; thấy tên/đổi ảnh, TOEIC/IELTS, 30–180 phút, phím nghe Anh–Anh/Anh–Mỹ, theme/motion. Nội dung riêng tư được lược khỏi tài liệu.
- **Phạm vi và giới hạn** Chưa sửa hồ sơ, mục tiêu, theme, tạo link mời hay lưu tùy chọn.

<a id="rt-08"></a>

### RT-08 — Điều khiển riêng tư và tài khoản

- **URL** `/cai-dat`
- **Điều kiện** Learner.
- **Thao tác và kết quả OBSERVED** Thấy các switch gửi dữ liệu cho AI, ẩn khỏi leaderboard, ẩn online; nút tải dữ liệu, đăng xuất thiết bị khác, đăng xuất, xóa tài khoản.
- **Phạm vi và giới hạn** Chỉ quan sát điều khiển. Không thao tác dữ liệu cá nhân, phiên hoặc tài khoản.

<a id="rt-09"></a>

### RT-09 — Bạn bè, ID tìm kiếm và lời mời

- **URL** `/ban-be`
- **Điều kiện** Learner.
- **Thao tác và kết quả OBSERVED** Vào phần Bạn bè. Trang có tìm theo ID/nút Tìm disabled khi rỗng, danh sách rỗng, copy link mời và gợi ý kết bạn.
- **Phạm vi và giới hạn** Không tìm người dùng thật, gửi lời mời hoặc tạo link mới.

<a id="rt-10"></a>

### RT-10 — XP, cấp, streak và thống kê tuần

- **URL** `/ban-be`, `/`
- **Điều kiện** Learner.
- **Thao tác và kết quả OBSERVED** Dashboard thấy tabs Tất cả/Bạn bè cho XP tháng. Mở tổng XP ở trang tiến độ → dialog Cách nhận XP; có chuỗi, số phút tuần, mục tiêu theo ngày và XP tới cấp sau. Tại một thời điểm hiển thị 1 XP.
- **Phạm vi và giới hạn** Giá trị thay đổi theo hoạt động đã thử. Quy tắc thưởng và tất cả mốc chưa thực nghiệm.

<a id="rt-11"></a>

### RT-11 — Bảng góp ý và ý tưởng của mình

- **URL** `/yeu-cau-tinh-nang`
- **Điều kiện** Learner.
- **Thao tác và kết quả OBSERVED** Thấy form tên/mô tả, gửi disabled khi trống, lọc trạng thái và hai tab xếp hạng. Chuyển Mới nhất và Của tôi → vùng Ý tưởng của tôi, thông báo trống.
- **Phạm vi và giới hạn** Không gửi, bình chọn, bình luận. Chưa kiểm duyệt hỗ trợ hoặc ticket riêng.

<a id="rt-12"></a>

### RT-12 — Điều hướng màn nhỏ và tiện ích nổi

- **URL** `/go-cau`, `/`
- **Điều kiện** Learner.
- **Thao tác và kết quả OBSERVED** Ở 390×844 danh mục có bốn link và Menu ở đáy, không tràn ngang. Đóng popup thông báo bằng Để sau. Mở Menu → dialog tới Phát âm/Từ điển/Tiến độ/Góp ý/Cài đặt. Mở Tiện ích thấy nút Từ điển nhanh.
- **Phạm vi và giới hạn** Ứng dụng web, không mô phỏng thiết bị iOS/Android thật. Popup tra cứu nhanh chưa xác minh kết quả.

<a id="rt-13"></a>

### RT-13 — Thư viện gói câu và mục lục

- **URL** `/go-cau`, `/go-cau/lo-trinh-a1`, `/go-cau/du-lich`
- **Điều kiện** Learner.
- **Thao tác và kết quả OBSERVED** Mở gói A1 → tiến độ 0/84 bài, chapter accordion và bài có badge độ khó; mở Du lịch → 36 bài, nhóm A1–B2 và danh sách theo nhóm. Catalog có lộ trình A1–C1, chủ đề đời sống và môi trường công việc.
- **Phạm vi và giới hạn** Chọn hai gói, chưa chạy mọi bài/chủ đề.

<a id="rt-14"></a>

### RT-14 — Thiết lập mode và phân tầng bài Gõ câu

- **URL** `/go-cau/lo-trinh-a1`, `/go-cau/lo-trinh-a1/crs_c9ac3ba0d8ae726835`, `/go-cau/du-lich/crs_de6b8251568427d00a`
- **Điều kiện** Learner.
- **Thao tác và kết quả OBSERVED** Mở bộ chọn ở danh mục và trong bài. Mặc định có Cơ bản (từ/mảnh/câu), Trung cấp (từ/câu), Nâng cao (câu). Bắt đầu A1 Cơ bản 49 mục, A1 Nâng cao 24 câu, Du lịch Trung cấp 83 mục. Chọn Nghe hoặc Nghe & nói thì Cơ bản/Trung cấp disabled.
- **Phạm vi và giới hạn** Danh mục hiển thị ba tầng; đã mở prompt từ/câu, chưa tới mảnh câu trong lượt thử.

<a id="rt-15"></a>

### RT-15 — Nộp đáp án và chấm tại chỗ

- **URL** `/go-cau/lo-trinh-a1/crs_c9ac3ba0d8ae726835`
- **Điều kiện** Learner.
- **Thao tác và kết quả OBSERVED** Đúng từ bằng Enter, đúng câu khác hoa/dấu, thử sai một từ/thừa/thiếu, rồi sửa với khoảng trắng. Trạng thái Chính xác hoặc Sai, thử lại; sai giữ cursor và ô đáp án, đúng tăng Đã làm. Xem ma trận ở 04-user-flows.
- **Phạm vi và giới hạn** Một vài mẫu đủ xác định quan sát này. Công thức điểm, stopword và Unicode toàn diện chưa xác minh. Ô trống bị auto-review chặn.

<a id="rt-16"></a>

### RT-16 — Đáp án, phản hồi theo từ và chuyển bước

- **URL** `/go-cau/lo-trinh-a1/crs_c9ac3ba0d8ae726835`
- **Điều kiện** Learner.
- **Thao tác và kết quả OBSERVED** Bấm Đáp án khi sai → lộ từng từ cùng IPA/POS và nút phát âm từ. Sau câu đúng, Câu tiếp mở bước đọc lại câu với Làm lại/Tiếp tục; sau đó prompt mới. Sửa tại ô và gửi lại được.
- **Phạm vi và giới hạn** Các token render riêng. Màu/thuật toán đánh dấu missing/extra và giá XP khi reveal chưa chốt; không đồng nhất nhãn transient ở mọi bước.

<a id="rt-17"></a>

### RT-17 — Âm thanh, cài đặt luyện và phím tắt

- **URL** `/go-cau/lo-trinh-a1/crs_c9ac3ba0d8ae726835`, `/go-cau/du-lich/crs_de6b8251568427d00a`
- **Điều kiện** Learner.
- **Thao tác và kết quả OBSERVED** Mở Cài đặt luyện tập: 0.8×/1×/1.2×, tự phát, phím/hiệu ứng, IPA/POS, font và reset. Bấm Phát âm ở Luyện nghe, thấy replay và hướng dẫn nghe viết. Desktop Du lịch lộ nhãn Ctrl, Alt, Ctrl+Alt, Enter.
- **Phạm vi và giới hạn** Đã kích hoạt control; môi trường không kiểm chứng âm thanh nghe được, timing và phím tắt ngoài Enter.

<a id="rt-18"></a>

### RT-18 — Tạm dừng và bộ đếm phiên

- **URL** `/go-cau/du-lich/crs_de6b8251568427d00a`, `/go-cau/lo-trinh-a1/crs_c9ac3ba0d8ae726835`
- **Điều kiện** Learner.
- **Thao tác và kết quả OBSERVED** Bấm Tạm dừng ở Du lịch → dialog Đã tạm dừng với Tiếp tục học. Thanh tiến độ, thời gian, combo và chính xác phản ánh trạng thái phiên; AX label tổng từng còn 49 ngay sau chuyển sang Nâng cao 24.
- **Phạm vi và giới hạn** Chưa đo idle, exact timer, combo formula hoặc đi hết phiên.

<a id="rt-19"></a>

### RT-19 — Khôi phục tiến độ, hoàn tất và mở lại bài

- **URL** `/go-cau/lo-trinh-a1/crs_c9ac3ba0d8ae726835`, `/go-cau/lo-trinh-a1`, `/tu-vung?tab=cua-toi`
- **Điều kiện** Learner.
- **Thao tác và kết quả OBSERVED** Reload sau 2 đúng → màn chọn mode, counter 0/24 tạm thời. Bắt đầu Nghe Nâng cao → Câu 2/24, Đã làm 2. Tab mới mở gói → bài 1 8%, gói 0% hoàn thành. Trong lượt sau, đổi mode một lần gặp Không tải được khoá học. Bấm Thử lại khôi phục Cơ bản ở 1/49. Chọn Mặc định Nâng cao khôi phục 2/24. Tiếp tục bằng nút Đáp án để đọc mẫu, nhập và gửi các mục còn lại đến 24/24, sau đó Tiếp tục → tổng kết +30 XP, +8 từ, lên cấp 2, combo 5 và Chính xác 0%. Về danh sách → 1/84, 1%, badge Trọn bộ có nhãn Nâng cao tính đủ ba độ khó. Chọn lại bài mở setup với Nâng cao. Kho từ sau đó hiển thị 8/8 từ và hết từ đến hạn hôm nay.
- **Phạm vi và giới hạn** Đã xác minh truy xuất UI sau reload, đi hết và mở lại bài tới setup. Một lần tổng kết có sử dụng đáp án mẫu nên không suy ra công thức chính xác, combo, XP hoặc thời điểm SRS đến hạn. Không khởi chạy lượt làm lại.

<a id="rt-20"></a>

### RT-20 — Luyện nghe và nói

- **URL** `/go-cau/lo-trinh-a1/crs_c9ac3ba0d8ae726835`
- **Điều kiện** Learner.
- **Thao tác và kết quả OBSERVED** Chọn Nghe & nói Nâng cao → ẩn nghĩa, Phát lại, Bắt đầu ghi âm, gợi ý Enter để nói và Nghe lại bản ghi disabled khi chưa ghi.
- **Phạm vi và giới hạn** Không cấp quyền mic. Nhận giọng, điểm và lỗi khi ghi chưa xác minh.

<a id="cv-01"></a>

### CV-01 — Thư viện bộ từ

- **URL** https://aioenglish.com/tu-vung
- **Điều kiện** Learner.
- **Thao tác và kết quả OBSERVED** Catalog từ vựng có bộ của bạn, Oxford, chủ đề A1–C1, IELTS/TOEIC, mở rộng (phrasal verbs/collocations/thành ngữ/AWL). Thẻ hiển thị số từ, phạm vi CEFR và tiến độ khi có.
- **Phạm vi và giới hạn** OBSERVED

<a id="cv-02"></a>

### CV-02 — Kho cá nhân, trạng thái đến hạn và tạo bộ

- **URL** https://aioenglish.com/tu-vung?tab=cua-toi
- **Điều kiện** Learner.
- **Thao tác và kết quả OBSERVED** Nhấn Từ vựng của tôi. “Chưa có từ đến hạn”; kho bản thân 0 từ/0% với tổng/chưa thuộc/đã thuộc; kho SRS tách và có empty CTA tới bộ đề xuất. Mở rồi hủy tạo danh sách inline. Mở Tạo từ vựng: dialog AI có chủ đề/đoạn văn/ảnh, chọn trình độ, nút Soạn bộ từ disabled khi trống; đóng.
- **Phạm vi và giới hạn** OBSERVED giao diện, UNVERIFIED ghi/lưu, trùng, favorites/khó, review bền vững

<a id="cv-03"></a>

### CV-03 — Bộ từ theo cấp và chủ đề

- **URL** https://aioenglish.com/tu-vung/oxford-3000 và https://aioenglish.com/tu-vung/oxford-3000?cap=a2
- **Điều kiện** Learner.
- **Thao tác và kết quả OBSERVED** Oxford 3000 A1–B2 có chủ đề/counter; tab A2 cập nhật URL, mục đã chọn và số nhóm (A1 21/A2 20). Quay A1, mở Con người & Quan hệ; dialog Nạp sâu (mặc định) hoặc Nạp nhanh bằng flashcard.
- **Phạm vi và giới hạn** OBSERVED

<a id="cv-04"></a>

### CV-04 — Nạp sâu và cấu trúc thẻ

- **URL** https://aioenglish.com/tu-vung/oxford-3000/vset_8ebfa3f8a626e3190f/hoc
- **Điều kiện** Learner.
- **Thao tác và kết quả OBSERVED** Bắt đầu Nạp sâu. Bỏ qua/Học/Biết rồi (1/2/3), mục tiêu chọn 5. Thẻ có từ, từ loại, một dạng IPA, nghĩa Việt, định nghĩa VI/EN, ví dụ/song ngữ, nút đọc/phát âm. Bấm nghe, chưa đo âm, UK/US chưa xác minh. Cài đặt cỡ chữ và tự đọc, đóng không đổi. Nhấn Học 5 lần, màn gõ chép bước 1/25 với Kiểm tra và Enter. Review tự động từ chối gõ/nộp cố ý sai vì có thể ghi attempt.
- **Phạm vi và giới hạn** OBSERVED luồng/step, UNVERIFIED chấm, kho SRS và hoàn thành

<a id="cv-05"></a>

### CV-05 — Lật flashcard, mức ghi nhớ và tổng kết sớm

- **URL** https://aioenglish.com/tu-vung/oxford-3000/vset_8ebfa3f8a626e3190f/hoc?mode=nhanh
- **Điều kiện** Learner.
- **Thao tác và kết quả OBSERVED** Chọn Nạp nhanh. Mặc định EN→VI, đảo VI→EN, hiện đáp án (Space được ghi), thấy IPA/song ngữ. Các nút hiển thị Quên rồi · 1 phút, Mơ hồ · 5 phút, Đã nhớ · 10 phút, Quá dễ · Đã biết; Bỏ qua, bộ đếm nạp/lặp. Kết thúc chưa chấm → tổng kết 0 từ, 35 giây, +0 XP; Hoàn tất.
- **Phạm vi và giới hạn** OBSERVED, UNVERIFIED thời điểm thực sự đến hạn/lịch bền vững

<a id="cv-06"></a>

### CV-06 — Danh mục theo lộ trình/cốt lõi

- **URL** https://aioenglish.com/ngu-phap
- **Điều kiện** Learner.
- **Thao tác và kết quả OBSERVED** Mở danh mục. Hai tab Theo lộ trình và Ngữ pháp cốt lõi, chọn cốt lõi và quay lại. Theo lộ trình có chương, trạng thái điểm ngữ pháp, tiến độ chung và A1–C2.
- **Phạm vi và giới hạn** OBSERVED

<a id="cv-07"></a>

### CV-07 — Mastery và khóa các cấp luyện

- **URL** https://aioenglish.com/ngu-phap/a1-to-be và https://aioenglish.com/ngu-phap/tai-lieu/dong-tu-be-have-got?node=a1-to-be
- **Điều kiện** Learner.
- **Thao tác và kết quả OBSERVED** Bài với thang 0/3: làm quen sau hướng dẫn, đã nắm sau bài ngắn 20 câu có gợi ý, thuần thục sau bài đầy đủ 20 câu không gợi ý. Luyện tập khóa trước khi xong hướng dẫn. Bấm Đọc tài liệu: tiêu đề, mục lục, quay lại bài.
- **Phạm vi và giới hạn** OBSERVED cho giao diện

<a id="cv-08"></a>

### CV-08 — Bài hướng dẫn và câu chọn đáp án

- **URL** https://aioenglish.com/ngu-phap/a1-to-be/hoc?mode=guided
- **Điều kiện** Learner.
- **Thao tác và kết quả OBSERVED** Bài hướng dẫn có bốn quy tắc, ví dụ song ngữ, lỗi hay mắc, làm mẫu viết lại câu, phần cuối mô tả 5 câu không gợi ý. Bấm Tiếp tục từ ví dụ sang chọn một trong ba từ điền, có Gợi ý và Bài trước. Review tự động từ chối mở gợi ý kèm nộp câu đúng có thể ghi attempt/tiến độ.
- **Phạm vi và giới hạn** OBSERVED bước đầu, UNVERIFIED chấm, retry, hoàn thành, mastery bền vững

<a id="cv-09"></a>

### CV-09 — Chương học, đổi cấp và mục tiêu

- **URL** https://aioenglish.com/lo-trinh và https://aioenglish.com/ngu-phap/a1-to-be-negative
- **Điều kiện** Learner.
- **Thao tác và kết quả OBSERVED** Có bài tiếp, dự báo, % mục tiêu, phút/ngày, bài/từ đã học, tab chương. Chọn Chương 2 khi Chương 1 đang học và 0/127; mở được bài ngữ pháp chưa học ở chương sau, có Bắt đầu. Sửa mục tiêu hiển thị phút/ngày và lựa chọn kỳ thi, lưu disabled khi không đổi; hủy. Đổi A2 mở modal A1–C1, mô tả giữ lịch sử và tính lại kế hoạch; hủy.
- **Phạm vi và giới hạn** OBSERVED nhảy một chương/bài; UNVERIFIED quyền mọi bài, lưu đổi cấp/mục tiêu

<a id="cv-10"></a>

### CV-10 — Tổng quan kiểm tra lên cấp

- **URL** https://aioenglish.com/lo-trinh/kiem-tra
- **Điều kiện** Learner.
- **Thao tác và kết quả OBSERVED** Tổng quan A1: 36 câu/40 phút (12 từ vựng + 12 ngữ pháp + 12 đọc), công bố ≥29 tổng và ≥7 mỗi phần. Mốc 80% là khuyến nghị; Bắt đầu hiển thị ở 0%. UI mô tả tính lượt ngay, đồng hồ chạy khi rời, cooldown 24h/3 ngày/7 ngày. Không bắt đầu lượt.
- **Phạm vi và giới hạn** OBSERVED tổng quan; UNVERIFIED thực thi chặn/mở/tính giờ/chấm

<a id="mv-01"></a>

### MV-01 — Hub đọc, dịch và lịch sử

- **URL** `/luyen-dich-thuat`
- **Điều kiện** Learner.
- **Thao tác và kết quả OBSERVED** Hub chia dịch từng câu (ngẫu nhiên A1 với 612 câu, theo bài), dịch đoạn theo chủ đề (đề xuất kế tiếp, số từ, tiến độ), báo song ngữ theo nhà xuất bản, bài riêng, lịch sử gần đây. Sidebar có /tu-dien và /phat-am.
- **Phạm vi và giới hạn** Các số là snapshot giao diện.

<a id="mv-02"></a>

### MV-02 — Dịch câu ngẫu nhiên và gợi ý

- **URL** `/luyen-dich-thuat/tung-cau/ngau-nhien`
- **Điều kiện** Learner.
- **Thao tác và kết quả OBSERVED** A1, Việt→Anh. Ô nhập auto-focus, Kiểm tra/Làm lại disabled khi rỗng. Gợi ý tăng 0/2→1/2 và hiện từ song ngữ. Nộp bản đúng bằng Enter → Chính xác!, tô từng từ, bản chấp nhận và bản mẫu, ghi chú, nút phát âm/làm lại/câu tiếp. Sidebar lượt 0→1 đã dịch/đúng/đúng liền. Câu tiếp đổi đề và reset hint.
- **Phạm vi và giới hạn** Vẫn có control hiện đáp án và nhãn phím Alt/Ctrl nhưng chưa test mọi phím.

<a id="mv-03"></a>

### MV-03 — Chấm sai và chấm lại bản dịch

- **URL** `/luyen-dich-thuat/tung-cau/ngau-nhien`
- **Điều kiện** Learner.
- **Thao tác và kết quả OBSERVED** Nộp câu khác nghĩa → Chưa đúng, số từ khác, Sửa lại hoặc Bản dịch của tôi cũng đúng. Bấm chấm lại → disabled trong khi chờ, sau đó giải thích khác nghĩa, đáp án/3 biến thể và Câu tiếp theo. Lượt hiển thị 2 đã dịch, 1 đúng, 0 đúng liền sau test.
- **Phạm vi và giới hạn** Thuật toán, điều kiện quota, model và tính bền vững của bộ đếm riêng chưa xác minh.

<a id="mv-04"></a>

### MV-04 — Dịch theo bài và chọn câu

- **URL** `/luyen-dich-thuat/tung-cau/theo-bai`
- **Điều kiện** Learner.
- **Thao tác và kết quả OBSERVED** Card theo bài vào thẳng bài kế tiếp Nắng, mây và gió, 15 câu; progressbar và danh sách câu. Chọn Câu 2 → Câu 2/15 và chỉ dấu đang làm chuyển.
- **Phạm vi và giới hạn** Chưa làm hết bài, chưa suy ra quy tắc mở khóa.

<a id="mv-05"></a>

### MV-05 — Lọc bài dịch theo chủ đề và CEFR

- **URL** `/luyen-dich-thuat/chu-de` → `/luyen-dich-thuat/chu-de/du-lich`
- **Điều kiện** Learner.
- **Thao tác và kết quả OBSERVED** Điều hướng tới chủ đề đang chọn, trình độ A1 mặc định. Danh mục bên cạnh, nút Tất cả/A1–C1; chọn A2 đổi khu vực nội dung Du lịch · A2. Mỗi mục có đường sang /luyen-dich-thuat/tung-cau/{text-id}.
- **Phạm vi và giới hạn** Chưa mở các chủ đề còn lại.

<a id="mv-06"></a>

### MV-06 — Đọc song ngữ và tra từ theo ngữ cảnh

- **URL** `/luyen-dich-thuat` → `/luyen-dich-thuat/lam-bai/{session}`
- **Điều kiện** Learner.
- **Thao tác và kết quả OBSERVED** Bấm Dịch bài này → modal Chỉ đọc, Anh→Việt, Việt→Anh. Bắt đầu Chỉ đọc → bài thực tế, lớp Song ngữ/Chỉ tiếng Anh, vocab/phrase panel, đánh dấu từ. Click từ → nghĩa ngữ cảnh, nút nghe và mở Từ điển chuyên sâu. Chuyển Chỉ tiếng Anh, trang báo kế tiếp giữ lựa chọn; đã khôi phục Song ngữ. Bắt đầu dịch → modal chọn chiều.
- **Phạm vi và giới hạn** Quyền dùng đọc không xác thực và đọc hiểu dạng câu hỏi chưa kiểm chứng.

<a id="mv-07"></a>

### MV-07 — Chấm đoạn và rubric kết quả

- **URL** `/luyen-dich-thuat/lam-bai/{session}` → `/luyen-dich-thuat/ket-qua/{session}`
- **Điều kiện** Learner.
- **Thao tác và kết quả OBSERVED** Anh→Việt: bài gốc/ô bản dịch hai cột; rỗng không chấm được. 19 từ/84 ký tự → xác nhận chấm → chờ có nhãn có thể rời trang → 88/100, 4 tiêu chí, nhận xét còn thiếu phần lớn đoạn. Có bài gốc, bản mẫu, bản người học, làm lại. Xem các lần làm mở Lần 1, số góp ý, ngày, điểm; ghi chỉ tính bài dịch cả đoạn.
- **Phạm vi và giới hạn** Thực nghiệm nộp hai câu của 14 câu; số điểm cao dù thiếu cho thấy phải đọc cùng rubric, chưa suy ra công thức.

<a id="mv-08"></a>

### MV-08 — Lưu bản dịch và mở lịch sử kết quả

- **URL** `/luyen-dich-thuat`, hai route MV-07
- **Điều kiện** Learner.
- **Thao tác và kết quả OBSERVED** Từ hub sau quay lại thấy lịch sử 1/1, TB 88, link về kết quả 88; chủ đề Du lịch 0/28→1/28. Vào lại route làm bài thấy nội dung 19 từ khôi phục và Đã lưu; link lịch sử mở route kết quả.
- **Phạm vi và giới hạn** Một lần làm cả đoạn và kết quả đã được thêm vào tài khoản. Card theo bài 0/42→1/42 và số phụ 0→2 sau các thử nghiệm nhưng nguyên nhân cụ thể và đơn vị của số phụ chưa kiểm chứng.

<a id="mv-09"></a>

### MV-09 — Danh mục báo và bài báo song ngữ

- **URL** `/luyen-dich-thuat/bao/the-guardian` → `/luyen-dich-thuat/bao/the-guardian/tex_fa636f0f6e60aa89af`
- **Điều kiện** Learner.
- **Thao tác và kết quả OBSERVED** Danh mục The Guardian có tìm kiếm, bộ lọc chủ đề và phân trang. Mở bài đầu thấy lớp song ngữ/Anh, vocab/patterns, và CTA Luyện dịch bài này. Lựa chọn tiếng Anh từ MV-06 còn hiệu lực, đổi lại Song ngữ.
- **Phạm vi và giới hạn** The Conversation và The Atlantic xác nhận có link từ hub, chưa mở riêng.

<a id="mv-10"></a>

### MV-10 — Form tạo bài riêng từ URL, văn bản hoặc AI

- **URL** `/luyen-dich-thuat`
- **Điều kiện** Learner.
- **Thao tác và kết quả OBSERVED** Mở 3 modal đầu vào: thêm URL giới hạn 3 nguồn được nêu với bài riêng tư; dán văn bản có giới hạn UI 3.000 ký tự; tạo bằng AI có chủ đề, trình độ/độ dài.
- **Phạm vi và giới hạn** Chụp cấu trúc form, không tạo bài riêng, chưa kiểm tra validation backend, lỗi hoặc quota.

<a id="mv-11"></a>

### MV-11 — Danh mục video, filter và chọn mode

- **URL** `/video`
- **Điều kiện** Learner.
- **Thao tác và kết quả OBSERVED** Search video/kênh, gợi ý bắt đầu, carousel, theo kênh, Video của tôi, link ngẫu nhiên và dán YouTube. Mở filter, chọn A1–A2 và thoát filter → kết quả, mức CEFR và phân trang. Mở video A2 → modal Dictation/Shadowing/Quiz/Subtitles với Dictation mặc định.
- **Phạm vi và giới hạn** Luồng thêm URL, ngẫu nhiên, tìm kiếm và lịch sử video chưa chạy.

<a id="mv-12"></a>

### MV-12 — Nghe chép, seek, loop và sửa đáp án

- **URL** `/video/english-listening-practice-for-beginners-my-weekend-a1-a2-1b136b?mode=dictation`
- **Điều kiện** Learner.
- **Thao tác và kết quả OBSERVED** Player YouTube nhúng, play/pause, thanh tua, tốc độ .8/1/1.2×, replay đoạn, câu trước/sau, loop. Chọn .8 và loop → pressed; chọn mốc 00:08 → Câu đang chép số 2, vị trí player cập nhật và cue tương ứng. Ô có phím Enter; nhập sai → Chưa đúng, thử lại; hiện toàn câu có bản dịch và nút tra nghĩa; nhập đúng → Đã gõ đúng cả câu, 0→1/164. Thấy công tắc tự sang câu.
- **Phạm vi và giới hạn** Dữ liệu đồng bộ kiểm tại 1 mốc, không đo drift. Câu đúng là thay đổi trong lượt; đổi sang chế độ khác và quay lại Dictation 0/164. Tiến độ server/hoàn thành video/điểm tổng chưa xác minh. Khôi phục 1×, tắt loop và dừng.

<a id="mv-13"></a>

### MV-13 — Transcript, phụ đề song ngữ và IPA

- **URL** Cùng slug video, `?mode=chill`
- **Điều kiện** Learner.
- **Thao tác và kết quả OBSERVED** Chọn Subtitles ở nav mode → transcript và cue thời gian, ẩn/thu gọn phụ đề, toggle Bản dịch checked→off, IPA off→checked. Bản dịch và IPA giữ khi đổi mode; đã khôi phục.
- **Phạm vi và giới hạn** Chưa đo độ đúng với tiếng nghe hoặc thiết bị khác.

<a id="mv-14"></a>

### MV-14 — Điều khiển Shadowing và chọn micro

- **URL** Cùng slug video, `?mode=shadowing`
- **Điều kiện** Learner.
- **Thao tác và kết quả OBSERVED** Chọn Shadowing → player phát câu, tốc độ, nút Bắt đầu ghi âm và combobox Chọn micro.
- **Phạm vi và giới hạn** Chưa cấp quyền mic, ghi âm, phát lại hoặc chấm.

<a id="mv-15"></a>

### MV-15 — Trắc nghiệm video và lời giải

- **URL** Cùng slug video, `?mode=quiz`
- **Điều kiện** Learner.
- **Thao tác và kết quả OBSERVED** Quiz 20 câu radio, trước chọn thì Nộp bài (0/20) disabled. Chọn 1 câu sai → Nộp bài (1/20), nộp thiếu được → 0/20 đúng, lời giải bằng tiếng Việt và Làm lại. Mở được modal Cài đặt bài học, có thiết lập tự chuyển sau 3 giây.
- **Phạm vi và giới hạn** Điểm quiz xuất hiện trong lượt; chưa xác minh lưu qua reload, XP hoặc thống kê tài khoản.

<a id="mv-16"></a>

### MV-16 — Gợi ý, từ đơn, cụm từ và chi tiết

- **URL** `/tu-dien`
- **Điều kiện** Learner.
- **Thao tác và kết quả OBSERVED** Entry mẫu, combobox Tìm kiếm từ. Nhập wind → listbox gợi ý có mục từ và nghĩa Việt, nhiều kết quả theo tiền tố, cả cụm. Enter → entry wind, CEFR/từ loại, nghĩa Việt, định nghĩa Anh, ví dụ song ngữ, diễn giải, IPA UK/US, hai nút audio, các mục họ từ, kết hợp, đồng/trái nghĩa. Click audio Anh–Anh có focus/tooltip. Tra break the ice → mục thành ngữ riêng; collocation có link /tu-dien?q=....
- **Phạm vi và giới hạn** Nghe được âm thanh hay độ chính xác phát âm chưa xác minh bằng môi trường thu âm. Từ không có kết quả, so sánh hai từ, hạn mức AI chưa thử.

<a id="mv-17"></a>

### MV-17 — Modal lưu mục từ

- **URL** `/tu-dien`
- **Điều kiện** Learner.
- **Thao tác và kết quả OBSERVED** Bấm Lưu vào danh sách từ → modal điền sẵn cụm, IPA, từ loại, nghĩa, ví dụ/bản dịch; Tự điền, combobox danh sách đích, Tạo danh sách mới và nút Lưu. Nút Tạo danh sách disabled khi tên trống.
- **Phạm vi và giới hạn** Chưa bấm Lưu/ Tạo, chưa xác minh card SRS được sinh.

<a id="mv-18"></a>

### MV-18 — Bảng âm UK/US, chi tiết và cặp tối thiểu

- **URL** `/phat-am` → `/phat-am/i-long`
- **Điều kiện** Learner.
- **Thao tác và kết quả OBSERVED** Module có tiếp tục, 3 nhóm khó, chỉ số đã luyện; bảng Nguyên âm, Nguyên âm đôi, Phụ âm. UK 50 → US 46 qua selector; lựa chọn còn thấy sau quay lại, đã khôi phục UK. Bài /iː/ có nút giọng, mẫu âm/từ, cặp tối thiểu, cách đọc, link 3 phần Thử thách nghe 10/Cụm từ 6/Câu 6.
- **Phạm vi và giới hạn** Accents là số theo kho site. Các nhánh cụm/câu có CTA, chưa làm.

<a id="mv-19"></a>

### MV-19 — Thử thách phân biệt âm

- **URL** `/phat-am/i-long/luyen?phan=thu-thach`
- **Điều kiện** Learner.
- **Thao tác và kết quả OBSERVED** Thử thách nghe có progress, Cách đọc, Bỏ qua, phím 1/2. Bấm Nghe, chọn đáp án → Đúng rồi, cho nghe lại hai từ; Tiếp tục → câu mới. Ra catalog vẫn 0 âm đã luyện.
- **Phạm vi và giới hạn** Hoàn tất một âm, ngưỡng đạt, lưu chính xác từng bước, thử nói và lỗi mic chưa xác minh.

## Tác động tài khoản trong phiên khảo sát

| Phạm vi | Dấu hiệu quan sát | Giới hạn quy kết |
|---|---|---|
| Gõ câu | A1 Cơ bản có một từ đúng. A1 Nâng cao thử ba đáp án sai mẫu rồi hoàn tất 24/24 với trợ giúp ở phần sau, +30 XP, cấp 2, gói lên 1/84. Kho từ có 8/8 sau khi tổng kết báo +8 từ. Học Du lịch tới màn nhập và tạm dừng. | XP là thưởng hiển thị tại màn tổng kết, còn tổng tháng gồm các hoạt động khác. Rule SRS chưa xác minh. |
| Dashboard và XP | Dashboard lúc đầu 0/180 phút, sau tương tác snapshot văn bản hiển thị 2/180. Trang XP từng hiển thị 1 XP và bộ tóm tắt mobile sau đó hiển thị 21 XP tháng. | Các tab cùng tài khoản. Số XP và thời gian cuối phiên có thể gồm nhiều module. |
| Từ vựng và ngữ pháp | Chọn Học 5 từ trong Nạp sâu. Flashcard đóng sớm hiển thị 0 từ, 35 giây, +0 XP. Ngữ pháp chuyển từ làm mẫu tới câu hỏi. | Chưa thấy ghi SRS/mastery bền vững. Hai thao tác tự động bị chặn như CV-04/CV-08. |
| Đọc & dịch | Dịch câu đúng/sai đổi bộ đếm phiên. Nộp một bản dịch đoạn chưa trọn, lưu điểm 88/100, 1 dòng lịch sử, 1/28 ở chủ đề. Nội dung 19 từ còn khi mở lại. Song ngữ khôi phục sau phép thử. | Không suy luận công thức điểm hay chính xác nguồn các số phụ. |
| Video và IPA | Dictation sai rồi đúng 1/164, trở về 0/164 khi đổi mode. Quiz video có kết quả 0/20. IPA trả lời đúng một câu, catalog vẫn 0 âm hoàn tất. Khôi phục phụ đề/tốc độ/loop và giọng IPA đã thử. | Không xác minh lưu điểm quiz/IPA hay gọi mic. |

[Luồng thực nghiệm](04-user-flows.md) · [Các phép thử còn mở](07-unverified-features.md)
