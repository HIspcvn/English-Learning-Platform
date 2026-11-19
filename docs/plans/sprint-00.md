# Sprint 00 — Chốt yêu cầu và dựng môi trường

> Nền tảng MVP · Các quyết định local đã chốt trong ADR. Xem [bằng chứng thực thi](../testing/04-sprint-00-verification.md) để biết cổng nào đã chạy.

## Mục tiêu và phạm vi

Tạo baseline để developer clone và chạy một quy trình kiểm tra lặp lại được.

- **Phạm vi** Chốt ADR, cấu trúc monorepo, môi trường và CI tối thiểu.
- **Tiền điều kiện và phụ thuộc** Workspace có quyền ghi và bộ blueprint đã được đọc.
- **Tính năng** FR-LAND-001, FR-AUTH-001, FR-CUR-001, FR-TYPE-001.
- **Đặc tả giao diện** [SRS](../requirements/02-SRS.md), [API](../architecture/05-api-specification.md), [ERD](../architecture/04-database-design.md), [parity](../requirements/06-feature-parity-matrix.md).

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
- **Hướng dẫn triển khai** Chốt session, CSRF, nền local và ranh giới MVP. Gán người phụ trách và hạn cho các quyết định hosting, vùng dữ liệu, email và chi phí production. [ADR toolchain](../architecture/adr/0001-local-toolchain-and-monorepo.md) · [ADR HTTP](../architecture/adr/0002-http-and-deployment-baseline.md) · [ADR Gõ câu](../architecture/adr/0003-learning-variants-rewards-vocabulary.md)
- **Ca kiểm thử** Review trace FR→DB/API→QA và kiểm tra các ID duy nhất.
- **Nghiệm thu** Sprint 1 có thể cho ra contract tests ngay.
- **Commit đề xuất** `docs: approve initial platform decisions`.

- [x] Đối chiếu 49 nhóm nghiên cứu, yêu cầu, API, ERD và QA.
- [x] Chốt ADR local và giữ danh sách Open Decision production.
- [x] Rà soát hợp đồng và liên kết với kế hoạch các sprint.

### S00-02 — Khởi tạo môi trường chạy

- **Mục tiêu** Cho dịch vụ web và API chạy ổn định trên máy mới.
- **Tệp và module** apps/web, apps/api, compose.yaml, .env.example
- **Đầu vào** ADR, bản runtime chốt và lockfile.
- **Đầu ra** Next/FastAPI/PostgreSQL chạy bằng Compose và health endpoint.
- **Phụ thuộc** S00-01
- **Ưu tiên và ước lượng** P0 · 2–3 ngày developer.
- **Hướng dẫn triển khai** Khoá dependency bằng npm và uv. Compose chờ DB rồi chạy revision nền trước khi mở API. Check readiness đối chiếu revision Alembic thực tế. Next gọi API qua cùng origin.
- **Ca kiểm thử** Compose mới báo healthy, DB ngắt thì readiness báo lỗi và liveness còn hoạt động.
- **Nghiệm thu** Checkout sạch phục hồi đầy đủ từ README mới của Sprint 0.
- **Commit đề xuất** `chore: bootstrap modular platform`.

- [x] Chạy ca red cho API, trang chủ và liveness parser trước triển khai.
- [x] Build và chạy Compose từ clone sạch, đối chiếu migration, liveness và readiness khi dừng DB.
- [x] Ghi quy trình chạy và bằng chứng đã thực thi.

### S00-03 — Dựng CI và test harness

- **Mục tiêu** Biến gate phát hành thành bước chạy được.
- **Tệp và module** .github/workflows, apps/api/tests, apps/web/tests
- **Đầu vào** Dịch vụ S00-02 và migrations nền.
- **Đầu ra** Lint, typecheck, pytest, Playwright smoke và artifacts fail.
- **Phụ thuộc** S00-02
- **Ưu tiên và ước lượng** P0 · 2–3 ngày developer.
- **Hướng dẫn triển khai** Tách DB mỗi job, migration thật, dùng role ít quyền và fixtures độc lập thời gian.
- **Ca kiểm thử** Bẻ health hoặc schema khiến pipeline đỏ, khôi phục thì xanh.
- **Nghiệm thu** Chạy lint, format, typecheck, migration và smoke từ checkout sạch. Workflow cung cấp cùng các kiểm tra trên GitHub. Để xác nhận ở cấp PR, cần có repository remote và lần chạy GitHub Actions thực tế.
- **Commit đề xuất** `ci: enforce reproducible quality checks`.

- [x] Chạy đủ lint, format, typecheck, unit, integration và browser smoke.
- [x] Kiểm schema sinh lại, Actionlint và quét Git bằng Gitleaks.
- [ ] Xác nhận cổng hosted ở lần chạy GitHub Actions đầu tiên.

## Điều kiện hoàn tất

- **Nghiệm thu local** ADR chốt toolchain, hợp đồng auth, tenancy và DB. Lint, typecheck, tests, migration và smoke vận hành trên checkout sạch. README và bằng chứng kiểm thử nằm trong repository.
- **Nghiệm thu hosted** Chạy workflow trên GitHub trước khi dựa vào trạng thái PR. Môi trường staging/production theo quyết định hosting trước pilot.
- **Bàn giao** Review và đối chiếu bằng chứng với từng task. Migration có hướng upgrade và downgrade được thử trên PostgreSQL cô lập.
- **Rủi ro dự kiến** Lệch phiên bản runtime và lockfile giữa CI với máy developer.

[Lộ trình và điều kiện phát hành](00-master-roadmap.md) · [Ma trận kiểm thử](../testing/02-test-cases.md)

