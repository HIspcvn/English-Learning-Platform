# Khảo sát AIO English

Khảo sát ngày **19/11/2026** bằng trình duyệt tích hợp, từ phiên người học đã đăng nhập. Đã mở **39 đường dẫn trang cụ thể thuộc 14 khu vực**, ghi nhận **49 nhóm chức năng OBSERVED**. Đếm URL theo pathname sau điều hướng. Các query mode, tab, hash, popup và redirect alias không tính thêm. Hai màn landing/dashboard dùng chung `/`. Bài làm và kết quả với mã cá nhân được ẩn dưới mẫu `{session}`. Số đường dẫn là mẫu khảo sát, không phải tổng URL của site.

| Khu vực | Đường dẫn trang trong mẫu | Bằng chứng |
|---|---:|---|
| Landing, demo entry và pháp lý | 4 | RT-01, RT-04 |
| Xác thực | 3 | RT-02–03 |
| Dashboard và tiến độ | 0, dùng chung `/` và `/ban-be` | RT-05–06, RT-10 |
| Profile và cài đặt | 1 | RT-07–08 |
| Lộ trình và kiểm tra lên cấp | 2 | CV-09–10 |
| Gõ câu | 5 | RT-13–20 |
| Từ vựng và SRS | 3 | CV-01–05 |
| Ngữ pháp | 5, gồm hai bài cùng mẫu | CV-06–09 |
| Đọc và dịch | 8 | MV-01–10 |
| Video, Dictation và Shadowing | 2 | MV-11–15 |
| Từ điển và tiện ích tra nhanh | 1 | MV-16–17, RT-12 |
| IPA | 3 | MV-18–19 |
| Bạn bè, XP và điểm danh | 1 | RT-09–10 |
| Góp ý và yêu cầu tính năng | 1 | RT-11 |
| **Tổng** | **39** | **49 nhóm định danh** |

## Kết quả có ảnh hưởng tới thiết kế

1. Gõ câu tách **chế độ** và **độ khó**. Nghe/nghe nói chỉ hiện Nâng cao. Đã mở hai bài ở A1 và Du lịch, dùng prompt từ và câu. Hoàn tất bài A1 ở mức Nâng cao sau khi dùng đáp án mẫu ở phần còn lại. Tổng kết báo **+30 XP**, **+8 từ mới vào kho** và **lên cấp 2**. Danh mục lên **1/84 bài** và đánh dấu riêng bài này **Trọn bộ**, với nhãn Nâng cao được tính đủ ba độ khó. [RT-14–20](06-evidence-and-screenshots.md#rt-14)
2. Một case mẫu chấp nhận khác chữ hoa/dấu câu, một case chấp nhận khoảng trắng khác. Sai, thiếu và thừa từ đã bị chấm sai. Lần reload mở setup, sau Start lấy lại hai câu đã làm. Xem [ma trận Gõ câu](04-user-flows.md#ma-trận-gõ-câu).
3. Thẻ từ vựng có Nạp sâu và Nạp nhanh. Bốn nhãn tự đánh giá cùng các mốc thời gian hiện trên flashcard, trong khi kho đến hạn đang rỗng. Xem [CV-02–05](06-evidence-and-screenshots.md#cv-02).
4. Roadmap cho vào một bài ở chương tiếp theo khi chương trước chưa hoàn tất. Ngữ pháp lại có gate nội bộ giữa bài hướng dẫn và luyện có/không gợi ý. Xem [CV-07–10](06-evidence-and-screenshots.md#cv-07).
5. Bài dịch cả đoạn có rubric, nội dung tự lưu và history; một bản chưa hoàn chỉnh hiển thị 88/100 cùng phản hồi yêu cầu bổ sung. Video có bốn chế độ; seek theo cue, lặp và dictation đã thử trực tiếp. Xem [MV-06–15](06-evidence-and-screenshots.md#mv-06).
6. Desktop 1280×720 hiện sidebar. Viewport 390×844 hiện tabbar bốn link và một Menu, với dialog điều hướng mở rộng. Mobile đã đo trên danh mục Gõ câu. Xem [RT-12 và ảnh](06-evidence-and-screenshots.md#rt-12).

## Kỹ thuật và giới hạn

- Đi từ navigation chính, từ catalog sang detail và player. Dùng accessibility tree và snapshot DOM hiển thị. Lưu hai ảnh, gồm điều hướng mobile và số liệu tổng kết Gõ câu. Cài đặt, popup, truy vấn mode và trạng thái thử lại được ghi vào audit.
- Tài khoản learner cho phép thực hành thông thường. Không cấp quyền microphone, thực hiện tác vụ quản trị, mua hàng hay gửi góp ý. Xem [tác động tiến độ](06-evidence-and-screenshots.md#tác-động-tài-khoản-trong-phiên-khảo-sát).
- **OBSERVED** mô tả giao diện/hành vi trực tiếp. **INFERRED** dùng cho diễn giải có chứng cứ. **PROPOSED** áp dụng cho hệ thống mới. **UNVERIFIED** giữ các nhánh chưa thử/không đủ dữ liệu. Cộng nhóm có bằng chứng quan sát, không cộng các giả thuyết hoặc nhánh chưa xác minh.
- Chi tiết [kiểm kê trang](03-page-by-page-audit.md), [danh mục chức năng](02-feature-inventory.md), [hạng mục chưa xác minh](07-unverified-features.md).
