# Design system — Nhịp Anh

**Trạng thái** PROPOSED. Tên làm việc. Giao diện mới phạm vi học tiếng Anh cho người Việt. Landing hướng tới hành động thử bài. Hệ học tập hướng tới thao tác thường xuyên, nội dung dễ đọc và điểm tập trung là prompt/phản hồi. Kiểu chữ, bố cục và icon dưới đây là thiết kế riêng.

## Nền và token

| Token | Giá trị thiết kế | Cách áp dụng |
| --- | --- | --- |
| Canvas | `#F7FAFC` | Nền workspace nền sáng |
| Surface | `#FFFFFF` | Panel, nội dung, dialog |
| Ink | `#14243A` | Tiêu đề, body, text nút màu lime |
| Muted ink | `#44566C` | Metadata/caption có ích |
| Border | `#CCD6E2` | Viền phân vùng trang trí, dùng token Strong border cho control cần nhận diện |
| Strong border | `#667C94` | Viền form và control |
| Brand action | `#0A5B56` | Nút chính chữ trắng, link có underline trong body |
| Accent | `#C2F279` | Điểm nhấn trên nền ink hoặc nhãn ink trên lime |
| Focus | `#155BC4` | Vòng 3 px, offset 2 px. Thêm lớp trắng khi đặt trên nền đậm |
| Success | `#14603E` trên `#E9F6EF` | Icon check, văn bản và cụm đúng |
| Error | `#A6223A` trên `#FFF1F4` | Icon/lỗi theo field và từ thay thế |
| Caution | `#7D3D10` trên `#FFF4DF` | Gợi ý, assisted, lỗi lưu tạm |
| Info | `#1D52A4` trên `#EEF4FC` | Trạng thái queued, lưu và data chưa sẵn |

Tỉ lệ tương phản tính từ token là Ink/Canvas 14,92:1, Muted ink/Canvas 7,17:1, chữ trắng trên Brand action 7,94:1, Strong border/Surface 4,31:1 và Focus/Surface 6,31:1. Bốn cặp semantic nằm trong 6,57–7,56:1. Kiểm tra WCAG 2.2 AA khi dựng component và kiểm trạng thái disabled/hover thực tế. Label, icon, trạng thái sử dụng chữ hoặc hình dạng khác nhau và có độ tương phản. Không dùng pastel làm chữ nhỏ. Error summary có text. Feedback màu trên token chỉ bổ trợ.

## Kiểu chữ và lưới

- **Kiểu chữ** Be Vietnam Pro cho tiếng Việt/English UI với font fallback system sans, font tự host có giấy phép. IPA dùng fallback Noto Sans với glyph đầy đủ. Mã task hoặc cue time dùng số tabular.
- **Scale** H1 32/40 mobile, 44/52 desktop. H2 24/32. H3 20/28. Body 16/25. Bài đọc 18/30. Label 14/20. Caption 13/18. Mức tiêu đề theo cấu trúc HTML. Hỗ trợ zoom tới 200% và reflow 320 CSS px.
- **Spacing** 4, 8, 12, 16, 24, 32, 48, 64 px. Card radius 12, form 8, dialog 16. Shadow nhẹ cho popover và dialog. Card phân vùng có viền. Không chồng nhiều cấp card khi một vùng nội dung đủ.
- **Grid** Workspace max 1280 px, content đọc 56–72 ký tự mỗi dòng. Desktop ≥1024 dùng header chung, lưới 8+4 trong màn dashboard/catalog/workspace và siderail 220px khi có lợi cho điều hướng. Tablet 768–1023 ưu tiên panel chính, side nội dung trong disclosure. Dưới 768 dùng một cột. Nav chuyển thành menu rõ ràng, điều khiển exercise nằm gần input.
- **Hình ảnh và icon** Sơ đồ và biểu tượng line cùng hệ. Mẫu UI ưu tiên content thật, ảnh chỉ khi có nguồn quyền hoặc do nhóm tự sản xuất. Video giữ thumbnail theo quyền. Icon độc lập có accessible name. Favicon và wordmark mới được thiết kế sau khi duyệt tên.

## Component và hành vi

| Pattern | Quy tắc |
| --- | --- |
| Header / navigation | Skip link đầu trang. Current page dùng `aria-current`. Menu hẹp đóng khi chọn hoặc Esc, focus trả trigger nếu thoát. Heading và breadcrumb khi độ sâu cần định hướng. |
| Button / CTA | Một hành động chính trên màn. Nút secondary có label động từ. Disabled khi input chưa có, có mô tả lý do khi cần. Touch hit area chọn ≥44×44 px. |
| Input / validation | Label luôn nhìn được. Field error cạnh trường và summary khi submit dài. Không xóa dữ liệu khi lỗi. `autocomplete`, input mode, instruction yên tĩnh ở form đăng nhập. |
| Feedback / diff | Mỗi trạng thái đúng/thiếu/thừa/sai có icon hoặc text, token HTML đọc theo thứ tự. Live region lịch sự báo kết quả gọn. Với thiếu từ dùng placeholder có text ẩn hỗ trợ. |
| Modal / sheet / popover | Dialog trap focus, có tên, mô tả và nút thoát, trả focus. Modal tiết chế tới chọn chiều/mode/xác nhận. Từ vựng popover hoặc sheet điện thoại có neo ngữ cảnh. |
| Loading / empty / error | Skeleton kích thước gần nội dung, một live status. Empty giải thích bước tiếp. Error cho retry theo vùng và giữ query/draft. Feedback lưu có timestamp nếu phù hợp. |
| Progress / status | Dùng <progress> với nhãn, text x/y và cảm nhận tiến độ. Không dùng percent khi mẫu số chưa biết. Success có CTA kế tiếp. Không đưa toast liên tục mỗi lần gõ. |
| Player / audio | Playback chỉ sau thao tác rõ. Caption có thể mở bằng keyboard, seek button chứa timestamp, speed và volume có nhãn. Giữ đọc được khi media lỗi. |
| Motion | Chuyển trạng thái 120–180 ms, giữ focus. Tắt shimmer/chuyển động qua `prefers-reduced-motion`. Không xoay màn bắt buộc. |

## Responsive và acceptance

Test 320/390/768/1024/1440 CSS px và 200% zoom. Kiểm tra tiếng Việt dài ≥40 ký tự nút, nguồn song ngữ dài, IPA, đoạn sai nhiều từ, bàn phím iOS/Android, safe area, theme system và media. Dùng chiều cao linh hoạt để CTA không che nội dung khi bàn phím ảo hiện. Có viewport desktop/mobile trên [QA](../testing/02-test-cases.md) và contract chi tiết tại [screen spec](03-screen-specifications.md). Bảng màu là nguyên mẫu, brand/legal phải duyệt trước phát hành.
