# Sprint 03 — Bộ máy và luồng Gõ câu

> PROPOSED · MVP · Các đường dẫn code bên dưới là vị trí dự kiến.

## Mục tiêu và phạm vi

Người học làm bài Gõ câu, nhận phản hồi và hoàn tất qua hợp đồng nhất quán.

- **Phạm vi** Demo anonymous; bài mặc định và nghe với từ/cụm/câu theo độ khó; luyện nói ở Sprint 9.
- **Tiền điều kiện và phụ thuộc** [Sprint 02](sprint-02.md)
- **Tính năng** FR-TYPE-001, FR-LAND-001, FR-PROG-001.
- **Đặc tả giao diện** [SRS](../requirements/02-SRS.md), [API](../architecture/05-api-specification.md), [ERD](../architecture/04-database-design.md).

## Công việc theo lớp

| Lớp | Công việc |
|---|---|
| PostgreSQL | Lesson runs, append-only attempts, hint events, item state, idempotency. |
| Backend | Normalization, token alignment, run commands và completion contract. |
| Frontend | Workspace bài học, audio, Enter, feedback, retry, resume và summary. |
| Nội dung | Audio và câu gốc, đáp án, segmentation và mapping độ khó. |
| Kiểm thử | Case/dấu/khoảng trắng, ba loại lỗi, submit lặp, reload, stale item. |
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

- **Mục tiêu** Lưu phiên, retry và tiến độ nguyên tử.
- **Tệp và module** apps/api/app/learning, apps/api/app/exercises, apps/api/alembic/versions
- **Đầu vào** Version/mode và item ID/answer/idempotency key.
- **Đầu ra** Run, attempt, cursor và completion receipt có thể replay.
- **Phụ thuộc** S03-01
- **Ưu tiên và ước lượng** P0 · 4–5 ngày developer.
- **Hướng dẫn triển khai** POST /lesson-runs và mutation con khoá run, kiểm tra item hiện tại, trình tự ghi theo API. Khác body cùng key trả conflict.
- **Ca kiểm thử** Two tabs race, wrong owner, key replay, crash rollback, ảnh hưởng version mới.
- **Nghiệm thu** Hoàn tất không làm mất trace theo item và tạo duy nhất một completion.
- **Commit đề xuất** `feat: persist idempotent lesson runs`.

- [ ] Viết ca kiểm thử nêu trên và kiểm tra lỗi đặc trưng trước thay đổi.
- [ ] Hoàn thành đầu ra, chạy ca kiểm thử liên quan và đối chiếu nghiệm thu.
- [ ] Gửi thay đổi và bằng chứng chạy kiểm thử để review.

### S03-03 — Giao diện bài tập và demo

- **Mục tiêu** Đưa player nhập liệu tới desktop/mobile.
- **Tệp và module** apps/web/app/(learn)/lessons, apps/web/features/typing, apps/web/tests/e2e
- **Đầu vào** Run state, feedback spans, audio asset, bộ demo tự biên.
- **Đầu ra** Answer controls, audio replay, retry, summary, error/recovery.
- **Phụ thuộc** S03-02
- **Ưu tiên và ước lượng** P0 · 3–5 ngày developer.
- **Hướng dẫn triển khai** Enter làm submit một lần và không can thiệp lúc IME composing; giữ draft client vừa đủ, fetch authoritative cursor ở reload.
- **Ca kiểm thử** IME, 390px, submit nhanh, audio không tải, vào lại đúng item.
- **Nghiệm thu** Người học hoàn thành một bài, demo không cần tài khoản và nhận nội dung mẫu độc lập.
- **Commit đề xuất** `feat: deliver accessible typing practice`.

- [ ] Viết ca kiểm thử nêu trên và kiểm tra lỗi đặc trưng trước thay đổi.
- [ ] Hoàn thành đầu ra, chạy ca kiểm thử liên quan và đối chiếu nghiệm thu.
- [ ] Gửi thay đổi và bằng chứng chạy kiểm thử để review.

## Điều kiện hoàn tất

- **Nghiệm thu sprint** Cùng run giữ phiên bản và cursor qua refresh. Một command lặp tạo một attempt. Hoàn tất theo item hợp lệ.
- **Bàn giao** Các task trên đã được review, bản trình diễn staging và bằng chứng kiểm thử đính kèm. Migration có hướng nâng cấp và hướng khôi phục khi sprint thay đổi schema.
- **Rủi ro dự kiến** Đánh dấu lỗi khó đọc trên màn nhỏ và khả năng để lộ answer key.

[Lộ trình và điều kiện phát hành](00-master-roadmap.md) · [Ma trận kiểm thử](../testing/02-test-cases.md)

