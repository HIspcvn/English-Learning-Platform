# Phân tích UI và UX AIO English

## Quan sát có bằng chứng

| Thành phần | Desktop và compact | Mobile 390×844 | Phạm vi |
|---|---|---|---|
| Shell | Sidebar với trong nhóm học/thư viện/tài khoản trên tab 1280×720. Player Gõ câu dùng header riêng, back và menu; compact 595×703 không có sidebar chính. | Tabbar cố định cao 69 px, bốn link và nút Menu; dialog mở thêm module. Gõ câu đang chọn có nền xanh nhạt và icon label. | RT-12–18 |
| Header | Gốc đăng nhập và module giữ entry profile/streak ở shell. Player hiển thị tên bài, phần trăm, timer, pause, settings. | Header trang danh mục vẫn có link profile/streak, nội dung rộng đủ viewport. | RT-05, RT-12, RT-14 |
| Typography và spacing | H1/H2 theo module/vùng, điều khiển module có tên đọc được. Dữ liệu đi theo nhãn và giá trị, như accuracy, combo, tiến độ và thanh thời lượng. | Label tabbar một dòng và icon đủ khác nhau. Popup chiếm bề rộng gần viewport, action dưới. | RT-12, RT-15, MV-12 |
| Màu và hình dạng | Màu phản hồi và nhấn nhá có ý nghĩa bên cạnh chữ. Thẻ đề xuất và dialog dùng bo góc. Giao diện có nút theme sáng/tối/hệ thống. | Ảnh thấy nền thanh màu trung tính ấm, tab đang chọn xanh nhạt, nhãn tối. | RT-07, RT-12, RT-15 |
| Cards và nút | Catalog là grid/sections, card chứa CEFR, số bài và tiến độ. Panel setup chọn mode/độ khó bằng button pressed. | Các nhóm danh mục xếp theo chiều dọc khi thu hẹp. Menu đưa các item phụ vào dialog. | RT-12–14, CV-01–03, MV-11 |
| Input và feedback | Typing đặt focus vào ô, xác minh qua Enter, status chính xác/sai. Từ điển autocomplete listbox, dịch/quiz blank disabled. | Không tràn ngang tại viewport kiểm trên catalog. Bàn phím ảo native chưa thử. | RT-15, MV-02, MV-15–16 |
| Modals và empty | Setup/pause/settings, thông báo ứng dụng, dialog card mode/XP, AI, review. Bạn bè/due/Của tôi có empty explicit. | Dialog app có Để sau và Đóng; dialog điều hướng có trạng thái active. | RT-08–12, RT-14, RT-18, CV-02, MV-11 |
| Progress và loading | Progress bar, bộ đếm, % và thời gian. Gõ câu có tổng kết chỉ số, CTA tiếp theo/làm lại/về danh sách và nút thử lại khi tải lỗi. Dịch đoạn có trạng thái đang chấm. | Hai dấu hiệu nav và độ rộng được đo; loading skeleton/toast và screen reader thiết bị thật chưa kiểm. | RT-05, RT-15, RT-19, CV-06, MV-01, MV-07 |

Font family, chính xác giá trị token màu, breakpoint CSS, transition, ARIA audit toàn diện, toast trên nhánh lỗi, tương tác bàn phím ảo và contrast theo từng theme chưa đo. Các nhãn aria đã thấy gồm nút mở menu, progressbar, âm thanh, role tab/button và live status. Khi đổi độ khó A1, chỉ số aria từng còn tổng 49 trong lúc nội dung hiện 24. Kiểm đồng nhất label/counter là ca QA cho thiết kế mới. [Bằng chứng](06-evidence-and-screenshots.md)

## Bố cục quan sát

```text
Desktop danh mục
┌──────────────┬─────────────────────────────────────────┐
│ Sidebar      │ Tên module + hành động bắt đầu         │
│ Các nhóm học │ Gói đề xuất → cards CEFR               │
│ Cài đặt      │ Chủ đề đời sống / công việc            │
└──────────────┴─────────────────────────────────────────┘

Mobile danh mục
┌────────────────────────────────────┐
│ Header · streak · profile         │
│ Tiêu đề và CTA                     │
│ Gói đề xuất → chủ đề               │
│ Các cards và tiến độ               │
├────────────────────────────────────┤
│ Home | Gõ câu | Từ vựng | Ngữ pháp | Menu
└────────────────────────────────────┘

Player bài gõ
┌────────────────────────────────────┐
│ Back · tên bài · timer · settings │
│ Progress · combo · accuracy       │
│ Mode · difficulty                  │
│ Prompt · ô nhập · status           │
│ Audio · đáp án · gửi · tiếp       │
└────────────────────────────────────┘
```

## Hệ quả cho thiết kế mới

Nhận diện riêng và UI mới có thẻ nhỏ gọn, navigation theo việc học và feedback có nghĩa cộng với màu. Trên màn nhỏ, prioritize input/feedback và đảm bảo thanh cố định tránh nội dung/bàn phím. Kiểm live region khi chuyển câu, focus restore sau dialog và chênh lệch số mục ở mode switch. Xem [Design system](../design/01-design-system.md), [screen specs](../design/03-screen-specifications.md) và [React components](../design/04-component-inventory.md).
