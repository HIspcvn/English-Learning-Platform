# Sprint 07 — Đọc và dịch

> PROPOSED · V1 · Các đường dẫn code bên dưới là vị trí dự kiến.

## Mục tiêu và phạm vi

Người học hiểu đoạn A1–B1 và luyện dịch với phản hồi có thể giải nghĩa.

- **Phạm vi** Bài đọc song ngữ, từ trong ngữ cảnh, câu hỏi, dịch câu/đoạn theo hợp đồng. Góp ý riêng tư tối thiểu.
- **Tiền điều kiện và phụ thuộc** [Sprint 03](sprint-03.md) cho run và [Sprint 06](sprint-06.md) cho tra từ trong ngữ cảnh.
- **Tính năng** FR-READ-001, FR-TRANS-001, FR-HELP-001.
- **Đặc tả giao diện** [SRS](../requirements/02-SRS.md), [API](../architecture/05-api-specification.md), [ERD](../architecture/04-database-design.md).

## Công việc theo lớp

| Lớp | Công việc |
|---|---|
| PostgreSQL | Passage/segments/localizations, references/rubrics, attempt type, feedback records. |
| Backend | Content queries, deterministic rubric, history and private feedback intake. |
| Frontend | Bilingual reader, popup từ, dịch, history và form trợ giúp. |
| Nội dung | Đoạn gốc, bản dịch được duyệt, rubric đa đáp án và nguồn. |
| Kiểm thử | Word boundary, accepted alternative, unknown answer, draft recovery. |
| Bảo mật | Escape văn bản, giới hạn length, kiểm tra owner, hạn chế dữ liệu form. |

## Task có thể review độc lập

### S07-01 — Bài đọc song ngữ và câu hỏi

- **Mục tiêu** Đọc theo đoạn có liên kết tra từ.
- **Tệp và module** apps/api/app/reading, apps/web/features/reading, apps/api/tests/reading
- **Đầu vào** Passage version, segment IDs, translations và lexical links.
- **Đầu ra** Reader, VI toggle, context lookup, quiz run.
- **Phụ thuộc** S06-02, S03-02
- **Ưu tiên và ước lượng** P1 · 3–5 ngày developer.
- **Hướng dẫn triển khai** Dùng segment stable keys, giấu bản dịch bằng trạng thái truy cập được, không ghi event cho mỗi hover.
- **Ca kiểm thử** Toggle vẫn giữ scroll, word button focus, đoạn không có bản dịch, quiz reload.
- **Nghiệm thu** Có thể dùng toàn bộ luồng qua bàn phím ở mobile/desktop.
- **Commit đề xuất** `feat: add bilingual reading workspace`.

- [ ] Viết ca kiểm thử nêu trên và kiểm tra lỗi đặc trưng trước thay đổi.
- [ ] Hoàn thành đầu ra, chạy ca kiểm thử liên quan và đối chiếu nghiệm thu.
- [ ] Gửi thay đổi và bằng chứng chạy kiểm thử để review.

### S07-02 — Chấm dịch có tham chiếu

- **Mục tiêu** Tách exact match, rubric và feedback còn cần đánh giá.
- **Tệp và module** apps/api/app/translation, apps/web/features/translation, apps/api/tests/translation
- **Đầu vào** Câu vi→en/en→vi, reference alternatives và version rubric.
- **Đầu ra** Attempt receipt, feedback theo tiêu chí, history.
- **Phụ thuộc** S07-01, S03-02
- **Ưu tiên và ước lượng** P1 · 4–5 ngày developer.
- **Hướng dẫn triển khai** Tie outcome tới rubric version. Xử lý phương án chưa biết theo engine, không gán đúng sai giả định.
- **Ca kiểm thử** Reference thay thế, khác dấu, blank, gửi lại, ref cũ sau publish.
- **Nghiệm thu** Đọc lại được nhận xét gắn đúng attempt, có retry minh bạch.
- **Commit đề xuất** `feat: assess translation with versioned rubrics`.

- [ ] Viết ca kiểm thử nêu trên và kiểm tra lỗi đặc trưng trước thay đổi.
- [ ] Hoàn thành đầu ra, chạy ca kiểm thử liên quan và đối chiếu nghiệm thu.
- [ ] Gửi thay đổi và bằng chứng chạy kiểm thử để review.

### S07-03 — Kênh góp ý riêng tư

- **Mục tiêu** Cho người học báo lỗi gắn bài và phần tử.
- **Tệp và module** apps/api/app/support, apps/web/features/feedback, apps/api/tests/support
- **Đầu vào** Category, nội dung tối thiểu, optional lesson reference.
- **Đầu ra** Ticket receipt cho người gửi và triage trên CMS.
- **Phụ thuộc** S01-02, S02-03
- **Ưu tiên và ước lượng** P1 · 2–3 ngày developer.
- **Hướng dẫn triển khai** Không public nội dung góp ý. Loại metadata nhận dạng không cần và phân quyền staff.
- **Ca kiểm thử** Spam, cross-user, submit lặp, reference sai.
- **Nghiệm thu** Gửi và đọc trạng thái đúng chủ thể; ticket có audit truy cập cần thiết.
- **Commit đề xuất** `feat: accept private learner feedback`.

- [ ] Viết ca kiểm thử nêu trên và kiểm tra lỗi đặc trưng trước thay đổi.
- [ ] Hoàn thành đầu ra, chạy ca kiểm thử liên quan và đối chiếu nghiệm thu.
- [ ] Gửi thay đổi và bằng chứng chạy kiểm thử để review.

## Điều kiện hoàn tất

- **Nghiệm thu sprint** Hoàn thành bài đọc và dịch mẫu, lịch sử truy xuất được; nội dung chưa khớp trả điều cần review.
- **Bàn giao** Các task trên đã được review, bản trình diễn staging và bằng chứng kiểm thử đính kèm. Migration có hướng nâng cấp và hướng khôi phục khi sprint thay đổi schema.
- **Rủi ro dự kiến** Dịch đúng nhưng khác câu mẫu, nội dung bài báo thiếu quyền.

[Lộ trình và điều kiện phát hành](00-master-roadmap.md) · [Ma trận kiểm thử](../testing/02-test-cases.md)

