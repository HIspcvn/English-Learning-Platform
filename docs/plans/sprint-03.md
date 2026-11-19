# Sprint 03 — Bộ máy và luồng Gõ câu

> PROPOSED · MVP · Các đường dẫn code bên dưới là vị trí dự kiến.

## Mục tiêu và phạm vi

Người học làm bài Gõ câu, nhận phản hồi và hoàn tất qua hợp đồng nhất quán.

- **Phạm vi** Demo khách, Mặc định ba độ khó, Nghe Nâng cao, resume và replay theo từng tổ hợp, completion có điểm và XP cơ bản. Nghe & nói Nâng cao ở S9. Tự lưu từ và ghi danh ôn ở S5.
- **Tiền điều kiện và phụ thuộc** [Sprint 02](sprint-02.md)
- **Tính năng** FR-TYPE-001, FR-LAND-001, FR-PROG-001, FR-GAME-001 phần XP cơ bản.
- **Đặc tả giao diện** [SRS](../requirements/02-SRS.md), [API](../architecture/05-api-specification.md), [ERD](../architecture/04-database-design.md).

## Công việc theo lớp

| Lớp | Công việc |
|---|---|
| PostgreSQL | Run active unique theo learner/lesson/version/mode/difficulty. Attempt và hint append-only, terminal state, completion receipt, tiến độ theo tổ hợp và XP ledger theo learner/lesson. |
| Backend | Scorer token, xác thực tổ hợp và prerequisite, snapshot READY, resume/replay, hoàn tất nguyên tử và XP idempotent. |
| Frontend | Hai bộ chọn mode/difficulty, audio/Enter, feedback, retry, resume đúng run và summary có giải thích. |
| Nội dung | Audio có quyền và READY cho Nghe, nội dung gốc, đáp án, mục bắt buộc và thứ tự theo tổ hợp. |
| Kiểm thử | Ma trận 3×3, READY, version pin, API conflict, điểm/lần đầu/mastery, XP race xuyên tổ hợp, 390 px và IME. |
| Bảo mật | Giới hạn chiều dài và thao tác, answer key chỉ sau hint hoặc feedback thích hợp. |

## Task có thể review độc lập

### S03-01 — Chấm câu và phản hồi token

- **Mục tiêu** Tạo scorer tất định dùng lại được trong dictation.
- **Tệp và module** apps/api/app/exercises/typing, apps/api/tests/exercises
- **Đầu vào** User text và references trong snapshot.
- **Đầu ra** Score, matched reference nội bộ và match/substitute/missing/extra spans.
- **Phụ thuộc** S02-03
- **Ưu tiên và ước lượng** P0 · 2–3 ngày developer.
- **Hướng dẫn triển khai** Áp dụng đúng normalize và tie-break trong engine spec, giữ display spans và không tiết lộ reference bất ngờ.
- **Ca kiểm thử** NFC, apostrophe, whitespace, missing/extra, tie, dài quá limit.
- **Nghiệm thu** Cùng input/version cho cùng feedback và blank bị từ chối bởi API.
- **Commit đề xuất** `feat: add deterministic typing feedback`.

- [ ] Viết ca kiểm thử nêu trên và kiểm tra lỗi đặc trưng trước thay đổi.
- [ ] Hoàn thành đầu ra, chạy ca kiểm thử liên quan và đối chiếu nghiệm thu.
- [ ] Gửi thay đổi và bằng chứng chạy kiểm thử để review.

### S03-02 — Run, attempt và completion

- **Mục tiêu** Lưu lượt theo đúng tổ hợp và cấp phần thưởng cơ bản nguyên tử.
- **Tệp và module** apps/api/app/learning, apps/api/app/exercises, apps/api/alembic/versions, apps/api/tests/learning
- **Đầu vào** Lesson, mode, difficulty, intent, version và manifest đã publish, item ID/answer/revision/idempotency key.
- **Đầu ra** Run ghim version và thứ tự, feedback, cursor, completion receipt bất biến có typing metrics và delta XP.
- **Phụ thuộc** S03-01
- **Ưu tiên và ước lượng** P0 · 4–5 ngày developer.
- **Hướng dẫn triển khai** Xác thực whitelist mode/difficulty, phase, prerequisite và READY. Tạo snapshot từ danh sách mục bắt buộc có ordinal của đúng version/tổ hợp. Resume mặc định trả active hoặc completion cùng tổ hợp, replay yêu cầu lệnh tường minh. Khóa run và item khi cập nhật. Completion kết toán điểm lần đầu, điểm cuối, trợ giúp, mastery và XP trong giao dịch. Lần đủ điều kiện đầu của một lesson cấp 10 XP, unique qua mode/difficulty/version. Bảng kho từ và SRS triển khai ở S5, có backfill từ lịch sử run của S3.
- **Ca kiểm thử** Tất cả tổ hợp, version cũ, đổi tổ hợp, thiếu audio, prerequisite chưa đạt, hai tab tranh revision, replay cùng key, lộ thông tin chủ khác, rollback. Sai rồi sửa đúng không trợ giúp đủ điều kiện XP. Nudge/reveal không đủ điều kiện; hai lượt đủ điều kiện của hai version đồng thời chỉ cấp một lần.
- **Nghiệm thu** Một receipt trên mỗi run và tối đa 10 XP cơ bản trên mỗi user/lesson. Điểm, mastery và completion của tổ hợp này không cấp cho tổ hợp khác. Run mở lại giữ cursor, nội dung và kết quả đã ghim.
- **Commit đề xuất** `feat: persist idempotent lesson runs`.

- [ ] Viết ca kiểm thử nêu trên và kiểm tra lỗi đặc trưng trước thay đổi.
- [ ] Hoàn thành đầu ra, chạy ca kiểm thử liên quan và đối chiếu nghiệm thu.
- [ ] Gửi thay đổi và bằng chứng chạy kiểm thử để review.

### S03-03 — Giao diện bài tập và demo

- **Mục tiêu** Đưa player nhập liệu tới desktop/mobile.
- **Tệp và module** apps/web/app/(learn)/lessons, apps/web/app/(learn)/learn, apps/web/features/typing, apps/web/tests/e2e
- **Đầu vào** `typing_variants`, `active_runs`, run view, feedback spans, audio asset, bộ demo tự biên.
- **Đầu ra** Bộ chọn hai chiều với lý do disabled, thao tác nhập/retry, summary, lỗi/khôi phục và nút Làm lại tường minh.
- **Phụ thuộc** S03-02
- **Ưu tiên và ước lượng** P0 · 3–5 ngày developer.
- **Hướng dẫn triển khai** Hiện tổ hợp READY từ API. Mở run của tổ hợp tương ứng và có lối tới run cũ còn quyền. Enter gửi một lần sau khi IME đã commit. Giữ draft client khi lỗi, đọc lại cursor từ server trên reload. Summary tách điểm đúng lần đầu, điểm cuối, trợ giúp, mastery và XP. Chỉ hiển thị CTA kho từ khi capability S5 có.
- **Ca kiểm thử** IME, 390 px, submit nhanh, lỗi audio, vào lại đúng item, review summary trước replay, thao tác replay qua nút riêng.
- **Nghiệm thu** Người học hoàn thành một bài, demo không cần tài khoản và nhận nội dung mẫu độc lập.
- **Commit đề xuất** `feat: deliver accessible typing practice`.

- [ ] Viết ca kiểm thử nêu trên và kiểm tra lỗi đặc trưng trước thay đổi.
- [ ] Hoàn thành đầu ra, chạy ca kiểm thử liên quan và đối chiếu nghiệm thu.
- [ ] Gửi thay đổi và bằng chứng chạy kiểm thử để review.

## Điều kiện hoàn tất

- **Nghiệm thu sprint** Hai chiều được chọn và lưu độc lập. Cùng run giữ phiên bản, thứ tự và cursor qua refresh. Một command lặp tạo một attempt, một run sở hữu một completion và learner chỉ nhận một award cơ bản trên mỗi lesson.
- **Bàn giao** Các task trên đã được review, bản trình diễn staging và bằng chứng kiểm thử đính kèm. Migration có hướng nâng cấp và hướng khôi phục khi sprint thay đổi schema.
- **Rủi ro dự kiến** Đánh dấu lỗi khó đọc trên màn nhỏ và khả năng để lộ answer key.

[Lộ trình và điều kiện phát hành](00-master-roadmap.md) · [Ma trận kiểm thử](../testing/02-test-cases.md)

