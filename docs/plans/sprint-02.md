# Sprint 02 — Curriculum và CMS

> PROPOSED · MVP · Các đường dẫn code bên dưới là vị trí dự kiến.

## Mục tiêu và phạm vi

Biên tập viên xuất bản một khóa A1 có ngữ liệu phiên bản hóa.

- **Phạm vi** Course, units, lessons, snapshot, nhập và duyệt nội dung. Catalog chuẩn bị lane Gõ câu và identity nghĩa để Sprint 03 ghim snapshot và Sprint 05 tự lưu từ.
- **Tiền điều kiện và phụ thuộc** [Sprint 01](sprint-01.md)
- **Tính năng** FR-CUR-001, FR-CMS-001.
- **Đặc tả giao diện** [SRS](../requirements/02-SRS.md), [API](../architecture/05-api-specification.md), [ERD](../architecture/04-database-design.md).

## Công việc theo lớp

| Lớp | Công việc |
|---|---|
| PostgreSQL | Course, unit, lesson, version, exercise, asset, typing_variants, vocabulary_entries/meanings ở mức biên tập, exercise_vocabulary_targets, import và editorial audit. |
| Backend | Curriculum queries, validation/import, publish atomic, quyền editor/reviewer/publisher. |
| Frontend | Catalog và breadcrumbs; CMS import preview, diff và trạng thái review. |
| Nội dung | Soạn gói A1 tối thiểu, manifest và nguồn bản quyền. |
| Kiểm thử | Seed/import idempotency, publish race, snapshot cũ vẫn đọc. |
| Bảo mật | RBAC từng hành động, escape rich text, file magic and limits, audit. |

## Task có thể review độc lập

### S02-01 — Khung khóa và route catalog

- **Mục tiêu** Đọc cây khóa ổn định với public IDs.
- **Tệp và module** `apps/api/app/curriculum/`, `apps/web/app/(learn)/roadmap/`, `apps/web/app/(learn)/lessons/[lessonId]/`, `apps/api/alembic/versions/`
- **Đầu vào** Course/unit/lesson slugs và metadata, release hiện hành.
- **Đầu ra** Catalog, lesson detail, dữ liệu rỗng và pagination có thứ tự.
- **Phụ thuộc** S01-03
- **Ưu tiên và ước lượng** P0 · 3–4 ngày developer.
- **Hướng dẫn triển khai** Mỗi record có khóa duy nhất phù hợp; join active published version, giữ thứ tự xác định.
- **Ca kiểm thử** Draft ẩn, query empty, pagination tránh trùng dưới cùng snapshot.
- **Nghiệm thu** Lộ trình duyệt theo khóa và chương. Lesson detail có URL trực tiếp và chỉ trả version published còn quyền.
- **Commit đề xuất** `feat: expose versioned curriculum catalog`.

- [ ] Viết ca kiểm thử nêu trên và kiểm tra lỗi đặc trưng trước thay đổi.
- [ ] Hoàn thành đầu ra, chạy ca kiểm thử liên quan và đối chiếu nghiệm thu.
- [ ] Gửi thay đổi và bằng chứng chạy kiểm thử để review.

### S02-02 — Import draft theo manifest

- **Mục tiêu** Tạo bản nháp dự đoán được từ nguồn đã kiểm.
- **Tệp và module** `apps/api/app/cms/imports`, `apps/api/app/vocabulary/`, `apps/api/alembic/versions/`, `apps/web/app/(admin)/cms/`, `apps/api/tests/cms/`
- **Đầu vào** CSV/JSON, source key, license, hashes media.
- **Đầu ra** Dry-run row errors hoặc draft batch đã audit.
- **Phụ thuộc** S02-01
- **Ưu tiên và ước lượng** P0 · 3–4 ngày developer.
- **Hướng dẫn triển khai** Giới hạn kích thước/MIME và validate quan hệ trước commit. Resolve lexeme_key/sense_key về UUID nghĩa ổn định, nhập schema typing_variants và gắn nghĩa được tác giả chọn vào exercise. Cùng import hash trả kết quả cũ. Kho learner, thẻ và review được thêm ở Sprint 05.
- **Ca kiểm thử** Row thiếu license, formula-like text, quá cỡ, target trỏ nghĩa không khả dụng, cặp mode/difficulty trùng, replay và DB rollback.
- **Nghiệm thu** Dry-run an toàn và batch invalid không tạo draft từng phần.
- **Commit đề xuất** `feat: validate and stage content imports`.

- [ ] Viết ca kiểm thử nêu trên và kiểm tra lỗi đặc trưng trước thay đổi.
- [ ] Hoàn thành đầu ra, chạy ca kiểm thử liên quan và đối chiếu nghiệm thu.
- [ ] Gửi thay đổi và bằng chứng chạy kiểm thử để review.

### S02-03 — Review và publish phiên bản

- **Mục tiêu** Đảm bảo bản đã duyệt được phát hành nguyên tử.
- **Tệp và module** apps/api/app/cms/publishing, apps/web/app/(admin)/cms, apps/api/tests/cms
- **Đầu vào** Version draft, reviewer feedback, publisher permission.
- **Đầu ra** Published pointer, immutable version, audit và cache refresh.
- **Phụ thuộc** S02-02
- **Ưu tiên và ước lượng** P0 · 3–4 ngày developer.
- **Hướng dẫn triển khai** Lock khi đổi active version. Kiểm trạng thái, quyền asset, audio ready cho lane nghe, candidate sequence non-empty, target sense hợp lệ và prerequisite. Đóng băng vị trí item, lane khai báo và liên kết nghĩa cùng snapshot. Audit cùng transaction publish.
- **Ca kiểm thử** Race hai phiên bản, version sai lesson, thiếu quyền, lane rỗng hoặc audio thiếu, target không hợp lệ, draft đổi sau approval.
- **Nghiệm thu** Public query chuyển một lần. Lane, thứ tự và mục từ của phiên bản đã đăng bất biến. [Schema nội dung](../data/01-content-schemas.md)
- **Commit đề xuất** `feat: publish reviewed content atomically`.

- [ ] Viết ca kiểm thử nêu trên và kiểm tra lỗi đặc trưng trước thay đổi.
- [ ] Hoàn thành đầu ra, chạy ca kiểm thử liên quan và đối chiếu nghiệm thu.
- [ ] Gửi thay đổi và bằng chứng chạy kiểm thử để review.

## Điều kiện hoàn tất

- **Nghiệm thu sprint** Người học chỉ thấy published version. Ngữ liệu mẫu đi hết quy trình và publish lặp phát một event.
- **Bàn giao** Các task trên đã được review, bản trình diễn staging và bằng chứng kiểm thử đính kèm. Migration có hướng nâng cấp và hướng khôi phục khi sprint thay đổi schema.
- **Rủi ro dự kiến** Dữ liệu có license thiếu hoặc tiến độ gắn sai ID của phiên bản.

[Lộ trình và điều kiện phát hành](00-master-roadmap.md) · [Ma trận kiểm thử](../testing/02-test-cases.md)

