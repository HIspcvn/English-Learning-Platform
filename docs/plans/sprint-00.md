# Sprint 00 — Chốt yêu cầu và dựng môi trường

> PROPOSED · Nền tảng MVP · Các đường dẫn code bên dưới là vị trí dự kiến.

## Mục tiêu và phạm vi

Tạo baseline để developer clone và chạy một quy trình kiểm tra lặp lại được.

- **Phạm vi** Chốt ADR, cấu trúc monorepo, môi trường và CI tối thiểu.
- **Tiền điều kiện và phụ thuộc** Workspace có quyền ghi và bộ blueprint đã được đọc.
- **Tính năng** FR-LAND-001, FR-AUTH-001, FR-CUR-001, FR-TYPE-001.
- **Đặc tả giao diện** [SRS](../requirements/02-SRS.md), [API](../architecture/05-api-specification.md), [ERD](../architecture/04-database-design.md).

## Công việc theo lớp

| Lớp | Công việc |
|---|---|
| PostgreSQL | Khởi động PostgreSQL trống và Alembic. |
| Backend | Khung FastAPI, endpoints health/readiness và chuẩn lỗi. |
| Frontend | Khung Next.js, cấu hình API cùng origin, kiểm tra build. |
| Nội dung | Đặt chủ sở hữu và manifest mẫu có giấy phép. |
| Kiểm thử | Smoke local/CI, migration up trên DB riêng. |
| Bảo mật | Secrets chỉ qua env, secret scan và ảnh container không chạy root. |

## Task có thể review độc lập

### S00-01 — Chốt ADR và hợp đồng

- **Mục tiêu** Đóng quyết định có tác động liên module.
- **Tệp và module** docs/architecture, docs/requirements, docs/plans
- **Đầu vào** Blueprint này, người phụ trách dữ liệu và chi phí.
- **Đầu ra** ADR theo chủ đề, người ký, ngưỡng và tiêu chí đảo quyết định.
- **Phụ thuộc** Blueprint
- **Ưu tiên và ước lượng** P0 · 1–2 ngày developer.
- **Hướng dẫn triển khai** Chốt session, CSRF, miền ứng dụng, vị trí dữ liệu và ranh giới MVP. Gán hạn cho vấn đề còn mở.
- **Ca kiểm thử** Review trace FR→DB/API→QA và kiểm tra các ID duy nhất.
- **Nghiệm thu** Sprint 1 có thể cho ra contract tests ngay.
- **Commit đề xuất** `docs: approve initial platform decisions`.

- [ ] Viết ca kiểm thử nêu trên và kiểm tra lỗi đặc trưng trước thay đổi.
- [ ] Hoàn thành đầu ra, chạy ca kiểm thử liên quan và đối chiếu nghiệm thu.
- [ ] Gửi thay đổi và bằng chứng chạy kiểm thử để review.

### S00-02 — Khởi tạo môi trường chạy

- **Mục tiêu** Cho dịch vụ web và API chạy ổn định trên máy mới.
- **Tệp và module** apps/web, apps/api, compose.yaml, .env.example
- **Đầu vào** ADR, bản runtime chốt và lockfile.
- **Đầu ra** Next/FastAPI/PostgreSQL chạy bằng Compose và health endpoint.
- **Phụ thuộc** S00-01
- **Ưu tiên và ước lượng** P0 · 2–3 ngày developer.
- **Hướng dẫn triển khai** Khoá dependency trực tiếp và chuyển tiếp, chuẩn hoá cấu hình dev/test/prod, readiness kiểm tra DB.
- **Ca kiểm thử** Compose mới báo healthy, DB ngắt thì readiness báo lỗi và liveness còn hoạt động.
- **Nghiệm thu** Checkout sạch phục hồi đầy đủ từ README mới của Sprint 0.
- **Commit đề xuất** `chore: bootstrap modular platform`.

- [ ] Viết ca kiểm thử nêu trên và kiểm tra lỗi đặc trưng trước thay đổi.
- [ ] Hoàn thành đầu ra, chạy ca kiểm thử liên quan và đối chiếu nghiệm thu.
- [ ] Gửi thay đổi và bằng chứng chạy kiểm thử để review.

### S00-03 — Dựng CI và test harness

- **Mục tiêu** Biến gate phát hành thành bước chạy được.
- **Tệp và module** .github/workflows, apps/api/tests, apps/web/tests
- **Đầu vào** Dịch vụ S00-02 và migrations nền.
- **Đầu ra** Lint, typecheck, pytest, Playwright smoke và artifacts fail.
- **Phụ thuộc** S00-02
- **Ưu tiên và ước lượng** P0 · 2–3 ngày developer.
- **Hướng dẫn triển khai** Tách DB mỗi job, migration thật, dùng role ít quyền và fixtures độc lập thời gian.
- **Ca kiểm thử** Bẻ health hoặc schema khiến pipeline đỏ, khôi phục thì xanh.
- **Nghiệm thu** Một PR có kết quả bắt buộc cho web, API, migration và smoke.
- **Commit đề xuất** `ci: enforce reproducible quality checks`.

- [ ] Viết ca kiểm thử nêu trên và kiểm tra lỗi đặc trưng trước thay đổi.
- [ ] Hoàn thành đầu ra, chạy ca kiểm thử liên quan và đối chiếu nghiệm thu.
- [ ] Gửi thay đổi và bằng chứng chạy kiểm thử để review.

## Điều kiện hoàn tất

- **Nghiệm thu sprint** CI chạy lint, typecheck, tests và smoke trên checkout sạch. ADR chốt auth, hosting, tenancy và DB được review.
- **Bàn giao** Các task trên đã được review, bản trình diễn staging và bằng chứng kiểm thử đính kèm. Migration có hướng nâng cấp và hướng khôi phục khi sprint thay đổi schema.
- **Rủi ro dự kiến** Lệch phiên bản runtime và lockfile giữa CI với máy developer.

[Lộ trình và điều kiện phát hành](00-master-roadmap.md) · [Ma trận kiểm thử](../testing/02-test-cases.md)

