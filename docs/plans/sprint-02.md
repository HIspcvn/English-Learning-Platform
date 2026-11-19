# Sprint 02 — Curriculum và CMS

> PROPOSED · MVP · Các đường dẫn code bên dưới là vị trí dự kiến.

## Mục tiêu và phạm vi

Biên tập viên xuất bản một khóa A1 có ngữ liệu phiên bản hóa.

- **Phạm vi** Course/units/lessons, draft–review–approve–publish, nhập CSV/JSON và catalog.
- **Tiền điều kiện và phụ thuộc** [Sprint 01](sprint-01.md)
- **Tính năng** FR-CUR-001, FR-CMS-001.
- **Đặc tả giao diện** [SRS](../requirements/02-SRS.md), [API](../architecture/05-api-specification.md), [ERD](../architecture/04-database-design.md).

## Công việc theo lớp

| Lớp | Công việc |
|---|---|
| PostgreSQL | Course, unit, lesson, version, exercise, asset, import, editorial audit. |
| Backend | Curriculum queries, validation/import, publish atomic, quyền editor/reviewer/publisher. |
| Frontend | Catalog và breadcrumbs; CMS import preview, diff và trạng thái review. |
| Nội dung | Soạn gói A1 tối thiểu, manifest và nguồn bản quyền. |
| Kiểm thử | Seed/import idempotency, publish race, snapshot cũ vẫn đọc. |
| Bảo mật | RBAC từng hành động, escape rich text, file magic and limits, audit. |

## Task có thể review độc lập

### S02-01 — Khung khóa và route catalog

- **Mục tiêu** Đọc cây khóa ổn định với public IDs.
- **Tệp và module** apps/api/app/curriculum, apps/web/app/(learn)/courses, apps/api/alembic/versions
- **Đầu vào** Course/unit/lesson slugs và metadata, release hiện hành.
- **Đầu ra** Catalog, lesson detail, dữ liệu rỗng và pagination có thứ tự.
- **Phụ thuộc** S01-03
- **Ưu tiên và ước lượng** P0 · 3–4 ngày developer.
- **Hướng dẫn triển khai** Mỗi record có khóa duy nhất phù hợp; join active published version, giữ thứ tự xác định.
- **Ca kiểm thử** Draft ẩn, query empty, pagination tránh trùng dưới cùng snapshot.
- **Nghiệm thu** Course và unit có URL trực tiếp, version published được trả.
- **Commit đề xuất** `feat: expose versioned curriculum catalog`.

- [ ] Viết ca kiểm thử nêu trên và kiểm tra lỗi đặc trưng trước thay đổi.
- [ ] Hoàn thành đầu ra, chạy ca kiểm thử liên quan và đối chiếu nghiệm thu.
- [ ] Gửi thay đổi và bằng chứng chạy kiểm thử để review.

### S02-02 — Import draft theo manifest

- **Mục tiêu** Tạo bản nháp dự đoán được từ nguồn đã kiểm.
- **Tệp và module** apps/api/app/cms/imports, apps/web/app/(admin)/cms, apps/api/tests/cms
- **Đầu vào** CSV/JSON, source key, license, hashes media.
- **Đầu ra** Dry-run row errors hoặc draft batch đã audit.
- **Phụ thuộc** S02-01
- **Ưu tiên và ước lượng** P0 · 3–4 ngày developer.
- **Hướng dẫn triển khai** Giới hạn kích thước và MIME, validate quan hệ trước commit, chạy cùng import hash trả lại kết quả.
- **Ca kiểm thử** Row thiếu license, formula-like text, file quá cỡ, replay, DB failure rollback.
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
- **Hướng dẫn triển khai** Lock lesson khi đổi active version; verify trạng thái/asset/license, transaction viết audit cùng publish.
- **Ca kiểm thử** Race hai phiên bản, ID version sai lesson, thiếu quyền, draft bị sửa sau approval.
- **Nghiệm thu** Public query chuyển một lần và khóa nội dung snapshot đã xuất bản.
- **Commit đề xuất** `feat: publish reviewed content atomically`.

- [ ] Viết ca kiểm thử nêu trên và kiểm tra lỗi đặc trưng trước thay đổi.
- [ ] Hoàn thành đầu ra, chạy ca kiểm thử liên quan và đối chiếu nghiệm thu.
- [ ] Gửi thay đổi và bằng chứng chạy kiểm thử để review.

## Điều kiện hoàn tất

- **Nghiệm thu sprint** Người học chỉ thấy published version. Ngữ liệu mẫu đi hết quy trình và publish lặp phát một event.
- **Bàn giao** Các task trên đã được review, bản trình diễn staging và bằng chứng kiểm thử đính kèm. Migration có hướng nâng cấp và hướng khôi phục khi sprint thay đổi schema.
- **Rủi ro dự kiến** Dữ liệu có license thiếu hoặc tiến độ gắn sai ID của phiên bản.

[Lộ trình và điều kiện phát hành](00-master-roadmap.md) · [Ma trận kiểm thử](../testing/02-test-cases.md)

