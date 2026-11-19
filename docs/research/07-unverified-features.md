# Hạng mục chưa xác minh

**UNVERIFIED** chỉ nói về nhánh hoặc cơ chế trong cột còn mở. Các hành vi đã quan sát ở cùng module tiếp tục có bằng chứng riêng. Các kiểm tra sau cần dữ liệu hoặc quyền ghi thích hợp.

| Mã | Phạm vi | Điều còn mở | Vì sao và ca tái kiểm | Bằng chứng liên quan |
|---|---|---|---|---|
| UV-AUTH-01 | Đăng nhập/onboarding/khôi phục | Credentials hợp lệ/sai, OAuth, xác minh email, reset link, MFA, onboarding, token/expiry và guard từng route. Demo guest hết 6 câu. | Đã dùng phiên sẵn và xem form. Tái kiểm bằng tài khoản test và phiên khách riêng, mở form rồi làm đủ luồng. | RT-01–03 |
| UV-TY-01 | Gõ câu blank và IME | Enter trên ô trống, composition, phím Ctrl/Alt/Ctrl+Alt và lỗi input dài. | Auto-review từ chối Enter trống, vì có thể tạo attempt. Chờ xác nhận cụ thể hoặc dùng tài khoản test; table 04 giữ kết quả trống. | RT-15, RT-17 |
| UV-TY-02 | Gõ câu sau hoàn thành | Hành vi khi Start lượt làm lại, thưởng lặp, trường hợp hoàn tất độ khó thấp, mảnh câu trong Cơ bản, resume liên thiết bị. | Đã thấy tổng kết 24/24, gói 1/84 và mở setup của bài Trọn bộ. Tái kiểm bằng tài khoản test trước/sau replay và qua thiết bị thứ hai. | RT-13–20 |
| UV-TY-03 | Highlight và thuật toán | Cách gắn màu/tokens khi thiếu/thừa/sai, apo/hyphen, exact scoring, nhiều đáp án, thời gian/accuracy. | Chỉ có chuỗi phản hồi và một số token. Re-test có screenshot đúng thời điểm và assertion từng token. | RT-15–18 |
| UV-AUDIO-01 | Audio, mic, speech | Nghe thực tế, lựa chọn giọng, tốc độ quan sát bằng thời lượng, thiết bị không mic, ghi/phát lại và scoring nhận dạng. | Có control nhưng mic không được cấp, âm thanh chưa được đo. Chạy trên thiết bị test có quyền mic phù hợp. | RT-17, RT-20, MV-12, MV-14, MV-16, MV-19 |
| UV-VOC-01 | Từ vựng cá nhân | Tạo/lưu danh sách, yêu thích, từ khó, cross-flow Dictionary → card, chấm deep mode và ngưỡng hoàn tất. | Form mở/hủy; nộp vocab deep có chủ đích sai bị auto-review chặn vì có thể ghi attempt. Retest trong tài khoản test với bộ 1–5 từ. | CV-02, CV-04, MV-17 |
| UV-SRS-01 | Review theo thời gian | Rating thật, thời điểm đến hạn, vòng ôn lại, thuật toán, retention, reminder và mapping từ mới sang thẻ. | Sau Gõ câu xác nhận 8 từ vào kho và vẫn hết từ đến hạn hôm nay. Bốn lựa chọn thấy trên thẻ chưa chấm. Chạy ca có dữ liệu đến hạn và mốc thời gian đã kiểm soát. | CV-02, CV-05, RT-19 |
| UV-GRAM-01 | Ngữ pháp | Chấm đúng/sai, giải thích sau lỗi, retry, unlock mastery, saved progress. | Mở tới choice; lượt gợi ý+nộp bị auto-review chặn vì có thể ghi tiến độ. Tái kiểm thao tác đã xác nhận trong tài khoản test. | CV-07, CV-08 |
| UV-ROAD-01 | Lộ trình, kiểm tra, goal | Ràng buộc mọi chương, Start ở 0%, timer khi thoát, streak check-in, thay goal/level, cooldown thực tế. | Chương 2 mở thử; CTA test chưa kích hoạt vì tiêu thụ lượt, không ghi goal. Theo dõi trạng thái trước/sau trong test. | RT-05–06, CV-09–10 |
| UV-READ-01 | Đọc/dịch và AI | Hai nguồn báo, câu hỏi đọc hiểu độc lập, bài riêng, lỗi/quota và bài đi hết, mô hình/chấm, hành vi nhiều phiên. | Một đoạn chấm và lưu đã xác minh; bài riêng dừng trước submit. Thử 2 bản đủ/thiếu với cùng bài và consent hợp lệ. | MV-01–10 |
| UV-VID-01 | Video | Hoàn thành, XP, retention qua reload, media lỗi, drift đồng bộ, speech capture, custom YouTube. | Một cue seek tốt về UI; quá trình phát/đồng bộ chưa đo; mic không cấp. So lại waveform/timestamp trên mẫu có nguồn và thiết bị test. | MV-11–15 |
| UV-DICT-01 | Từ điển | Từ không kết quả, AI suggestions/so sánh, lưu xong vào danh sách và tra nhanh. | Tested từ/cụm/ví dụ có mặt, modal save dừng trước mutation. Thử từ giả và save idempotency trong tài khoản test. | RT-12, MV-16–17 |
| UV-IPA-01 | Luyện IPA | Phần cụm/câu, đủ câu, ngưỡng đạt và stats bền, âm thiếu dữ liệu. | Một câu nghe trả lời đúng, catalog vẫn 0. Chạy trọn 3 bài của một âm. | MV-18–19 |
| UV-SOC-01 | Bạn bè, XP, thành tích | Gửi/nhận yêu cầu, leaderboard bạn bè, các mốc, lịch sử check-in và XP chính xác. | Có UI and modal, tránh gửi và check-in. Cần 2 tài khoản test, sự kiện có timestamp và kiểm sau reload. | RT-05, RT-09–10 |
| UV-SET-01 | Settings/privacy/feedback | Đổi hồ sơ, lưu preference, báo lỗi sau gửi, export, xóa, thiết bị khác, comments, moderation. | Quan sát điều khiển và góp ý trống. Thao tác cần account test; xóa, gửi cho người khác và thay credentials nằm ngoài lần khảo sát này. | RT-07–08, RT-11 |
| UV-ADMIN-01 | CMS/Admin và subscription | Vai trò quản trị/biên tập, pipeline nội bộ, paywall/pricing/checkout, gói. | Không thấy entry với learner, pháp lý công bố dịch vụ miễn phí. Cần quyền admin rõ ràng hoặc route công khai do site cung cấp; không suy diễn quyền nội bộ. | RT-04, RT-07, RT-12 |
| UV-UI-01 | Responsive và lỗi | Mọi route trên mobile, device keyboard/mic, landscape, dark/zoom, WCAG flow, server offline/error rates và hiệu năng. | Đã đo shell catalog 390×844 và desktop; dùng ma trận thiết bị, các tài khoản và môi trường mô phỏng lỗi phù hợp. | RT-12, RT-18, MV-07 |

## Trạng thái từ auto-review

Ba thao tác bị từ chối ở bước thực hiện vì có thể tạo lịch sử hoạt động trên tài khoản. Gõ câu là gửi trống bằng Enter. Từ vựng là nộp có chủ đích sai ở Nạp sâu. Ngữ pháp là mở gợi ý kèm nộp câu đúng trong guided. Phép thử độc lập và bình thường đã tiếp tục. Các mục trên có hướng tái kiểm bằng tài khoản test hoặc quyền hành động cụ thể.

[Quay về tổng quan](01-site-exploration.md) · [Sổ bằng chứng](06-evidence-and-screenshots.md)
