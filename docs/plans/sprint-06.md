# Sprint 06 — Ngữ pháp và từ điển

> PROPOSED · V1 · Các đường dẫn code bên dưới là vị trí dự kiến.

## Mục tiêu và phạm vi

Người học chuyển liền mạch giữa quy tắc ngữ pháp, bài áp dụng và nghĩa trong ngữ cảnh.

- **Phạm vi** Bài lý thuyết và luyện có lời giải. Lookup từ/cụm từ, UK/US nếu có, lưu về SRS.
- **Tiền điều kiện và phụ thuộc** [Sprint 02](sprint-02.md), [Sprint 03](sprint-03.md), [Sprint 05](sprint-05.md)
- **Tính năng** FR-GRAM-001, FR-DICT-001.
- **Đặc tả giao diện** [SRS](../requirements/02-SRS.md), [API](../architecture/05-api-specification.md), [ERD](../architecture/04-database-design.md).

## Công việc theo lớp

| Lớp | Công việc |
|---|---|
| PostgreSQL | Grammar references, exercise payloads, lexical senses/search and source metadata. |
| Backend | Read grammar version, grade exercise, ranked dictionary lookup. |
| Frontend | Catalog/lesson/quiz, search debounce và word detail. |
| Nội dung | A1 grammar units, examples, lexicon, accent audio rights. |
| Kiểm thử | Grading, no hit, accent fallback, simultaneous save, keyboard. |
| Bảo mật | Chống XSS rich text, validate query length và giới hạn suggestions. |

## Task có thể review độc lập

### S06-01 — Bài ngữ pháp và bài tập

- **Mục tiêu** Mô hình hóa lý thuyết và kiểm tra hiểu.
- **Tệp và module** apps/api/app/grammar, apps/web/features/grammar, apps/api/tests/grammar
- **Đầu vào** Version content blocks, lựa chọn hoặc câu có tham chiếu.
- **Đầu ra** Bài hướng dẫn, attempt có giải thích và retry.
- **Phụ thuộc** S02-03, S03-02
- **Ưu tiên và ước lượng** P1 · 4–5 ngày developer.
- **Hướng dẫn triển khai** Tái dùng lesson-run. Trả explanation sau chấm, progress phản ánh quy tắc trong published version.
- **Ca kiểm thử** Câu trả lời sai, gate chưa đủ, retry, bản mới khi bài cũ đang chạy.
- **Nghiệm thu** Luồng học → áp dụng → giải thích hoàn chỉnh.
- **Commit đề xuất** `feat: add guided grammar practice`.

- [ ] Viết ca kiểm thử nêu trên và kiểm tra lỗi đặc trưng trước thay đổi.
- [ ] Hoàn thành đầu ra, chạy ca kiểm thử liên quan và đối chiếu nghiệm thu.
- [ ] Gửi thay đổi và bằng chứng chạy kiểm thử để review.

### S06-02 — Tra cứu, chi tiết và lưu từ

- **Mục tiêu** Kết nối lexical entry dùng lại từ SRS.
- **Tệp và module** apps/api/app/dictionary, apps/web/features/dictionary, apps/api/tests/dictionary
- **Đầu vào** Query từ/cụm và variant UK/US hợp lệ.
- **Đầu ra** Suggestions, senses, assets và liên kết save.
- **Phụ thuộc** S05-01
- **Ưu tiên và ước lượng** P1 · 3–5 ngày developer.
- **Hướng dẫn triển khai** Xếp exact lemma/phrase trước prefix, giữ tách POS/sense. Reuse card save đơn nhất.
- **Ca kiểm thử** Query rỗng, phrase, miss, dấu nháy cong, thiếu UK, save lặp.
- **Nghiệm thu** Lookup no-hit dễ hiểu và không sinh thẻ duplicate.
- **Commit đề xuất** `feat: connect dictionary lookup to vocabulary`.

- [ ] Viết ca kiểm thử nêu trên và kiểm tra lỗi đặc trưng trước thay đổi.
- [ ] Hoàn thành đầu ra, chạy ca kiểm thử liên quan và đối chiếu nghiệm thu.
- [ ] Gửi thay đổi và bằng chứng chạy kiểm thử để review.

## Điều kiện hoàn tất

- **Nghiệm thu sprint** Mở bài, làm quiz, đọc giải thích, tra cụm và lưu đúng entry.
- **Bàn giao** Các task trên đã được review, bản trình diễn staging và bằng chứng kiểm thử đính kèm. Migration có hướng nâng cấp và hướng khôi phục khi sprint thay đổi schema.
- **Rủi ro dự kiến** Mơ hồ khi lemma có nhiều POS hoặc nghĩa Việt chưa đủ.

[Lộ trình và điều kiện phát hành](00-master-roadmap.md) · [Ma trận kiểm thử](../testing/02-test-cases.md)

