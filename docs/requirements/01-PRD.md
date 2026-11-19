# PRD — Nhịp Anh

**Trạng thái** PROPOSED · 19/11/2026 · Tên làm việc Nhịp Anh

## Tầm nhìn và vấn đề

Giúp người Việt trình độ A1–A2 hình thành thói quen thực hành tiếng Anh có chủ đích. Mỗi lượt học bắt đầu bằng một việc vừa sức, trả phản hồi có thể sửa ngay và cho biết khi nào cần ôn. Mở rộng B1–C1 khi nhóm biên soạn có đủ bài được thẩm định.

Người mới thường tìm được nhiều tài liệu nhưng khó chọn bài tiếp theo, phân biệt lỗi gõ với lỗ hổng ngôn ngữ và duy trì ôn sau buổi đầu. Cần một vòng lặp có thứ tự mặc định và quyền chủ động chọn lại bài, phản hồi dễ hiểu, tiến độ đáng tin cậy và bài ngắn dùng được trên điện thoại.

## Đối tượng

| Persona giả định | Hoàn cảnh và mục tiêu | Lựa chọn sản phẩm |
| --- | --- | --- |
| Người đi làm mất gốc | 10 phút trên điện thoại, cần mẫu dùng ngay | Tiếng Việt, bắt đầu từ A1, tiếp tục đúng bài, chọn mục tiêu thời gian |
| Người học A2 tự học | Biết nghĩa nhưng gõ/sử dụng chưa chắc | Gõ chủ động, phân biệt từ thừa/thiếu/sai, ôn theo hạn |
| Người học nâng lên B1 | Muốn hiểu bài đọc và nghe nguồn thật | V1 có tài liệu có phép, phụ đề, luyện theo đoạn và từ ngữ cảnh |
| Biên tập viên | Cần sửa bài đã phát hành và giữ lịch sử | Môi trường nháp, đối chiếu lỗi theo bản ghi, review và bản phát hành bất biến |

## Trải nghiệm học

1. Khách chọn demo có nội dung tự biên, thử một câu và thấy phản hồi trước khi tạo tài khoản.
2. Người học gửi email để nhận link xác minh. Sau khi chứng minh quyền truy cập email, họ đặt tên hiển thị và mật khẩu rồi đăng nhập. Onboarding chọn CEFR, mục tiêu kỳ thi tùy chọn, múi giờ IANA và ngôn ngữ Việt/Anh, mặc định tiếng Việt. Dashboard hiển thị một hành động chính. Từ Sprint 4, người học đặt mục tiêu phút/ngày tại dashboard hoặc Settings.
3. Lộ trình có khóa học theo CEFR, chương, bài và trạng thái. Đề xuất thứ tự mặc định, cho xem lại bài công khai trong cấp đã có. Bài hết quyền truy cập hoặc bị thu hồi có lý do cụ thể.
4. Gõ từ → cụm → câu khi đội nội dung đã biên soạn cả ba phần. Gợi ý mở từng phần, phản hồi hiện dạng văn bản, giữ bản nháp khi gặp lỗi mạng.
5. Kết thúc lượt hợp lệ cập nhật mục tiêu và tiến độ một lần. Từ lưu chủ động vào kho. Người học chọn Đưa vào ôn và chiều ôn trước khi tạo thẻ. Bài đến hạn xuất hiện trên dashboard có lý do và số lượng.

AIO English đã đưa tám từ vào kho khi bài Gõ câu mẫu hoàn tất. MVP đề xuất lưu và đưa vào ôn theo lựa chọn của người học để họ kiểm soát khối lượng ôn ban đầu. [RT-19](../research/06-evidence-and-screenshots.md#rt-19)
6. Bản phát hành sau mở thêm giáo trình đọc, video, chính tả, IPA, rồi thêm góp ý AI theo quyền riêng tư.

[User stories](03-user-stories.md) · [SRS](02-SRS.md) · [Bản đồ hành trình và màn hình](../design/02-sitemap.md)

## Phạm vi và giá trị phát hành

| Mốc | Phạm vi | Điều kiện qua mốc |
| --- | --- | --- |
| MVP, Sprint 00–05 và cổng 12 | Landing/demo. Email auth, xác minh, phục hồi, onboarding. Roadmap A1, CMS với nhập nháp/duyệt/xuất bản. Typing từ/cụm/câu. Resume, tiến độ, mục tiêu ngày, bộ từ và ôn SRS bốn mức. Thiết lập cơ bản và yêu cầu tải/xóa dữ liệu với xác thực lại bằng mật khẩu | Từ demo tới bài thật và review chạy E2E trên desktop/mobile. Mỗi tài liệu đã có quyền và audio thiết yếu phát được. Hai lần gửi/retry tạo một hiệu ứng. Staff khác vai trò mới publish. |
| V1, Sprint 06–09 và cổng 12 | Ngữ pháp, từ điển, đọc song ngữ, dịch theo đáp án/rubric quy tắc, video/phụ đề/quiz, dictation, IPA nghe phân biệt, shadowing nghe và tự đối chiếu, hỗ trợ | Có luồng fallback khi lỗi media/quyền mic, tìm kiếm có empty state, phản hồi có căn cứ, có phủ A2 do editorial xác nhận. |
| V2, Sprint 10–11 và cổng 12 | Chấm dịch ngữ nghĩa và tác vụ AI bất đồng bộ, có ngân sách và kiểm duyệt, XP/streak/achievement, gợi ý cá nhân hóa. Bạn bè chỉ triển khai khi có chủ sở hữu moderation | Đạt chuẩn đánh giá AI, ghi nhận xóa dữ liệu, opt-in xã hội, giới hạn chi phí, khóa vùng sai lệch. |

Gói trả phí, thi cấp chứng chỉ, xếp hạng công khai mặc định, nhắn tin giữa người dùng, app native, marketplace nội dung, nhập báo/YouTube tùy ý và chấm điểm giọng nói tự động nằm ngoài cam kết. Bộ bài cùng logo, ảnh, nội dung, nhạc hoặc typography mang nhận diện AIO English cần nguồn quyền sử dụng riêng. Sản phẩm dùng tài sản tự biên hoặc có cấp phép.

## KPI đề xuất

Ngưỡng dưới đây là mục tiêu pilot, cần đo baseline trước khi cam kết. Báo theo cohort bắt đầu tuần, mức tự chọn và thiết bị khi đủ mẫu. Dedupe theo người dùng và sự kiện server. Loại staff, demo ẩn danh khỏi cohort học thật và loại phiên test.

| Chỉ số | Định nghĩa | Mục tiêu pilot |
| --- | --- | --- |
| Activation 24h | Tài khoản xác minh hoàn tất bài gõ đầu tiên trong 24h / tài khoản mới xác minh và đã đủ 24h quan sát | ≥ 45% |
| D7 learning retention | Tài khoản đã activation có ít nhất một lần nộp hợp lệ hoặc review vào ngày địa phương thứ 7 / cohort đã đủ 7 ngày | ≥ 25% |
| Typing completion | Lượt typing hoàn tất / lượt đã khởi động, trong 7 ngày, theo phiên bản bài và chế độ | ≥ 70% |
| FCR | Câu đúng ở lần nộp đầu, trước khi xem đáp án / câu có lần nộp đầu, theo bài và cùng chế độ | Theo dõi baseline · Không dùng để xếp hạng cá nhân |
| SRS recall | Review có Good hoặc Easy / review đã chấm, tách nhóm card đến hạn và khoảng giữa hai lượt | ≥ 75% theo nhóm pilot |
| Chất lượng nội dung | Bản phát hành có license, review ngôn ngữ và bộ mẫu kiểm tra / tổng bản phát hành | 100% |
| An toàn vận hành | P95, lỗi 5xx, kiểm thử restore, a11y và privacy | [Ngưỡng kỹ thuật](05-non-functional-requirements.md) |

Sự kiện server tối thiểu gồm xác minh tài khoản, bắt đầu/hoàn tất run, chấm attempt hợp lệ, chấm review, xuất bản version. Thuộc tính dùng ID nội bộ, thời gian, version và kết quả tổng hợp. Bài trả lời, recording và email không thuộc telemetry sản phẩm. Báo chất lượng chấm chạy trên dữ liệu gán nhãn tách riêng.

## Rủi ro sản phẩm

| Rủi ro | Hệ quả | Quyết định |
| --- | --- | --- |
| Gõ lại được hiểu là gõ chính tả tuyệt đối | Người học nhầm lỗi dấu câu với mất nghĩa | Định nghĩa policy chấm trên từng bài. Hiển thị chỗ sửa và gợi ý tiếng Việt. |
| Hạn chế từ vựng/nội dung chất lượng | Lộ trình dài nhưng thiếu bài thật | Cổng biên tập license, CEFR do người duyệt, phát hành A1 theo đợt nhỏ. |
| Điểm AI cao dù thiếu nhiều nội dung | Số điểm làm sai lệch học tập | Rubric tách coverage, prompt version, bảng so mẫu gán nhãn và fallback thủ công. MV-07. |
| Cạnh tranh hoặc chuỗi gây áp lực | Người học bỏ cuộc, lộ dữ liệu | Mục tiêu riêng mặc định. Khi có streak và xã hội thì opt-in và nêu cách tắt. |
| Kết nối yếu hoặc thiếu mic | Rơi lượt học | Trạng thái lưu riêng, retry cùng khóa idempotency, caption và cách học nghe/đọc. |
| Người học chia sẻ dữ liệu cá nhân với AI | Xử lý ngoài kỳ vọng | Giữ tính năng tùy chọn, giảm dữ liệu gửi, nêu mục đích, TTL, hủy và giải quyết yêu cầu xóa. |
| Múi giờ và giờ mùa hè | Tính trùng tiến độ/mục tiêu | Ngày địa phương được chốt tại thời điểm sự kiện. Mục tiêu hiển thị múi giờ đang áp dụng. |

## Các quyết định cần chốt trước khi code

- Chủ sở hữu nội dung, giọng UK/US khởi đầu, giấy phép và khối lượng bài A1 đạt chuẩn để pilot.
- Provider email, tên miền và hạ tầng có phương án backup/restore. Chính sách retention và thị trường pháp lý do chủ sản phẩm chốt.
- Quy tắc CEFR cho đầu vào, cách đo tiến bộ trong pilot và khả năng dùng tên Nhịp Anh.
- Trước Sprint 10, chốt provider, sampling eval, ngân sách, xử lý recording và trợ giúp khi AI lỗi. Trước triển khai xã hội, chốt moderation/báo cáo và nhân sự thực hiện.

[Chấp nhận](04-acceptance-criteria.md) · [Kế hoạch phát hành](../plans/00-master-roadmap.md) · [Nghiên cứu AIO English](../research/01-site-exploration.md)
