# ADR 0003 — Biến thể Gõ câu, điểm và kho từ

**Trạng thái** Accepted cho đặc tả sản phẩm, 19/11/2026. **Chủ sở hữu** Product, Learning và Data.

## Quyết định

- Mode và difficulty là hai trục có ma trận tương thích. MVP mở `default` ở `basic`, `intermediate`, `advanced` và `listen` ở `advanced`. V1 mở `listen_speak` ở `advanced` với phát mẫu, ghi âm cục bộ và tự đánh dấu. Bản publish chứa thứ tự item ổn định theo biến thể. Phiên ghim version, mode và difficulty, hỗ trợ resume chính xác và replay chủ động. Từng độ khó có kết quả riêng, còn prerequisite thuộc curriculum.
- Lưu first-attempt accuracy và terminal score độc lập. Reveal hoàn thành item có trợ giúp với terminal score bằng 0 cho item đó. Mastery áp dụng riêng biến thể đã pass toàn bộ không trợ giúp và accuracy lần đầu từ 80%. Speech tự đánh dấu có completion riêng, điểm và mastery để trống.
- MVP cấp **10 XP** ở lần hoàn tất graded đầu tiên của mỗi bài có đủ item pass không trợ giúp. Retry hợp lệ vẫn có thể đạt XP. Unique nguồn theo learner + lesson bền qua phiên và version. Sprint 03 ghi cùng transaction completion, Sprint 04 đọc. Streak, leaderboard và thành tích nâng cao ở V2.
- Từ Sprint 05, completion graded đưa các nghĩa đã gắn vào item bắt buộc vào kho từ. Lưu nghĩa và ghi danh SRS là hai hành động. Khóa unique learner + meaning, giữ tombstone khi người dùng bỏ từ để completion sau không tự thêm lại. Người học tự chọn nghĩa và chiều để tạo thẻ SRS. Hợp nhất người học, tiến độ và kho trong transaction với backfill lịch sử có ràng buộc.

## Căn cứ và kiểm tra

Quan sát mode, replay, tổng kết, kho từ và XP ở bài mẫu cung cấp bằng chứng sản phẩm. Công thức trong ADR là lựa chọn dự án. Kiểm ma trận, điểm và bất biến duplicate ở [đặc tả engine](../06-exercise-engines.md), [API](../05-api-specification.md), [ERD](../04-database-design.md) và [ma trận parity](../../requirements/06-feature-parity-matrix.md). Xem lại sau khi pilot có số liệu completion, assisted rate và tỷ lệ tự chọn ôn.
