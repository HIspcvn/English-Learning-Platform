# Sprint 05 — Từ vựng và ôn giãn cách

> PROPOSED · MVP · Các đường dẫn code bên dưới là vị trí dự kiến.

## Mục tiêu và phạm vi

Học deck gốc và ôn từ đến hạn với lịch nhất quán.

- **Phạm vi** Deck, word details, flashcards, lưu từ và SRS bốn mức.
- **Tiền điều kiện và phụ thuộc** [Sprint 02](sprint-02.md) mở đường cho deck và scheduler. Tích hợp vào dashboard sau [Sprint 04](sprint-04.md), trước cổng MVP.
- **Tính năng** FR-VOCAB-001, FR-SRS-001.
- **Đặc tả giao diện** [SRS](../requirements/02-SRS.md), [API](../architecture/05-api-specification.md), [ERD](../architecture/04-database-design.md).

## Công việc theo lớp

| Lớp | Công việc |
|---|---|
| PostgreSQL | Entries/senses/decks/cards/review logs, unique learner+meaning+direction, due index. |
| Backend | Deck queries, save, due queue, rate and reschedule transaction. |
| Frontend | Catalog, word detail, flip/rate, empty due, stats. |
| Nội dung | Deck A1, ngữ nghĩa VI, IPA và audio có provenance. |
| Kiểm thử | Concurrent review, backfill, due boundary, streak integration khi có. |
| Bảo mật | Card ownership, cap list, same card stale revision trả conflict. |

## Task có thể review độc lập

### S05-01 — Danh mục từ và thẻ cá nhân

- **Mục tiêu** Dùng chung lexical entry từ deck đến dictionary tương lai.
- **Tệp và module** apps/api/app/vocabulary, apps/web/app/(learn)/vocabulary, apps/api/alembic/versions
- **Đầu vào** Manifest entry/sense/audio và deck ordering.
- **Đầu ra** Deck view, word details, lưu nghĩa idempotent và ghi danh ôn theo chiều đã chọn.
- **Phụ thuộc** S02-03
- **Ưu tiên và ước lượng** P0 · 3–4 ngày developer.
- **Hướng dẫn triển khai** Chuẩn hoá lexical identity và tách senses; gắn danh sách lưu với meaning_id và ghi danh ôn bằng command riêng.
- **Ca kiểm thử** Một từ nhiều nghĩa, thiếu audio, save lặp, request owner sai.
- **Nghiệm thu** Cùng learner, nghĩa và chiều dùng chung một thẻ khi xuất phát từ nhiều màn hình.
- **Commit đề xuất** `feat: add vocabulary decks and saved cards`.

- [ ] Viết ca kiểm thử nêu trên và kiểm tra lỗi đặc trưng trước thay đổi.
- [ ] Hoàn thành đầu ra, chạy ca kiểm thử liên quan và đối chiếu nghiệm thu.
- [ ] Gửi thay đổi và bằng chứng chạy kiểm thử để review.

### S05-02 — Scheduler và hàng đợi

- **Mục tiêu** Dời lịch sau rating có lưu lịch sử.
- **Tệp và module** apps/api/app/srs, apps/api/tests/srs, apps/api/alembic/versions
- **Đầu vào** Card state, rating, expected revision và command idempotency.
- **Đầu ra** Due query + append-only review log + next due.
- **Phụ thuộc** S05-01
- **Ưu tiên và ước lượng** P0 · 3–4 ngày developer.
- **Hướng dẫn triển khai** Dùng SM-2 đã chọn trong engine spec, lock card, đánh giá server time, giữ ngưỡng due UTC.
- **Ca kiểm thử** 4 ratings, lapse, stale double click, due biên, first card, no due.
- **Nghiệm thu** Kết quả rating tái lập và replays trả receipt cũ.
- **Commit đề xuất** `feat: schedule spaced vocabulary reviews`.

- [ ] Viết ca kiểm thử nêu trên và kiểm tra lỗi đặc trưng trước thay đổi.
- [ ] Hoàn thành đầu ra, chạy ca kiểm thử liên quan và đối chiếu nghiệm thu.
- [ ] Gửi thay đổi và bằng chứng chạy kiểm thử để review.

### S05-03 — Giao diện ôn tập

- **Mục tiêu** Cho người học flip/rate và trở về summary.
- **Tệp và module** apps/web/features/srs, apps/web/app/(learn)/vocabulary, apps/web/tests/e2e
- **Đầu vào** Due page và review response.
- **Đầu ra** Flashcard state/summary với âm thanh và trạng thái rỗng.
- **Phụ thuộc** S05-02
- **Ưu tiên và ước lượng** P0 · 2–3 ngày developer.
- **Hướng dẫn triển khai** Rating chỉ sau reveal, prevent duplicate while pending, lỗi mạng giữ card và retry đúng key.
- **Ca kiểm thử** Tab/Enter, double tap, empty state, hết batch, failed review.
- **Nghiệm thu** Mobile hoàn thành lượt ôn và dashboard có số due sau reload.
- **Commit đề xuất** `feat: guide vocabulary recall sessions`.

- [ ] Viết ca kiểm thử nêu trên và kiểm tra lỗi đặc trưng trước thay đổi.
- [ ] Hoàn thành đầu ra, chạy ca kiểm thử liên quan và đối chiếu nghiệm thu.
- [ ] Gửi thay đổi và bằng chứng chạy kiểm thử để review.

## Điều kiện hoàn tất

- **Nghiệm thu sprint** Review hợp lệ tạo một log, due mới phản ánh ngay, reload không nhân đôi hoặc mất kết quả.
- **Bàn giao** Các task trên đã được review, bản trình diễn staging và bằng chứng kiểm thử đính kèm. Migration có hướng nâng cấp và hướng khôi phục khi sprint thay đổi schema.
- **Rủi ro dự kiến** Deck có từ đa nghĩa, learner bị nợ ôn quá nhiều và dữ liệu trùng.

[Lộ trình và điều kiện phát hành](00-master-roadmap.md) · [Ma trận kiểm thử](../testing/02-test-cases.md)

