# Sprint 12 — Kiểm thử, tối ưu và triển khai

> PROPOSED · Gate MVP, V1 và V2 · Các đường dẫn code bên dưới là vị trí dự kiến.

## Mục tiêu và phạm vi

Đưa lát cắt đã hoàn thành lên production với bằng chứng khôi phục và quan sát.

- **Phạm vi** Chạy cổng S12 cho từng release và mở rộng test matrix để bao phủ các module vừa thêm vào V1 hoặc V2.
- **Tiền điều kiện và phụ thuộc** MVP sau [Sprint 04](sprint-04.md) và [Sprint 05](sprint-05.md). V1 thêm [Sprint 07](sprint-07.md) và [Sprint 09](sprint-09.md). V2 thêm [Sprint 10](sprint-10.md) và [Sprint 11](sprint-11.md).
- **Tính năng** FR-AUTH-001, FR-CMS-001, FR-TYPE-001, FR-PROG-001, FR-SRS-001.
- **Đặc tả giao diện** [SRS](../requirements/02-SRS.md), [API](../architecture/05-api-specification.md), [ERD](../architecture/04-database-design.md).

## Công việc theo lớp

| Lớp | Công việc |
|---|---|
| PostgreSQL | Migration dry-run, backup encrypted và restore drill. |
| Backend | Readiness/observability, private DB, security configuration, load testing. |
| Frontend | Mobile/accessibility/CWV, E2E staging, error boundary và rollback. |
| Nội dung | Rà nguồn, public manifests và quyền sử dụng trước promote. |
| Kiểm thử | Contracts, restored data, e2e, concurrency, performance, accessibility. |
| Bảo mật | TLS, secrets, audit, monitoring/PagerDuty thích hợp, privacy/abuse and backups. |

## Task có thể review độc lập

### S12-01 — Release gates theo phiên bản

- **Mục tiêu** Cố định tiêu chí promotion và bằng chứng.
- **Tệp và module** .github/workflows, apps/api/tests, apps/web/tests
- **Đầu vào** Release scope, NFR, QA cases, representative content.
- **Đầu ra** Test matrix có threshold và kết quả trên artifacts.
- **Phụ thuộc** S04-03 và S05-03 cho MVP. V1 thêm S07-03 và S09-02. V2 thêm S10-03 và S11-02.
- **Ưu tiên và ước lượng** P0 · 3–5 ngày developer.
- **Hướng dẫn triển khai** Chạy contract/migration/product journeys, verify license, accessible keyboard and performance budgets.
- **Ca kiểm thử** Simulate regressions, duplicate commands, 390px, WebKit media, AI feature toggle.
- **Nghiệm thu** Green cho nhóm phiên bản hiện hành và blocker có owner.
- **Commit đề xuất** `test: enforce versioned release gates`.

- [ ] Viết ca kiểm thử nêu trên và kiểm tra lỗi đặc trưng trước thay đổi.
- [ ] Hoàn thành đầu ra, chạy ca kiểm thử liên quan và đối chiếu nghiệm thu.
- [ ] Gửi thay đổi và bằng chứng chạy kiểm thử để review.

### S12-02 — Production và rollback

- **Mục tiêu** Triển khai stack với chứng cứ phục hồi thật.
- **Tệp và module** infra, .github/workflows, runbooks, apps/api/app/health
- **Đầu vào** Staging snapshot vô danh, approved immutable images và migrations.
- **Đầu ra** Production deploy plan, telemetry, rollback runbook and restore drill receipt.
- **Phụ thuộc** S12-01
- **Ưu tiên và ước lượng** P0 · 4–6 ngày developer.
- **Hướng dẫn triển khai** Expand/contract schema, image tags immutable, point-in-time restore, rollout smoke và theo dõi worker/job failures.
- **Ca kiểm thử** Migration rollback decision, expired secrets, restore measure, killed app restart.
- **Nghiệm thu** Chạy smoke trước/sau rollback, ghi RPO/RTO đạt đã chốt.
- **Commit đề xuất** `ops: verify deployment rollback and data restore`.

- [ ] Viết ca kiểm thử nêu trên và kiểm tra lỗi đặc trưng trước thay đổi.
- [ ] Hoàn thành đầu ra, chạy ca kiểm thử liên quan và đối chiếu nghiệm thu.
- [ ] Gửi thay đổi và bằng chứng chạy kiểm thử để review.

## Điều kiện hoàn tất

- **Nghiệm thu sprint** Checklist release ký bởi người phụ trách, staging smoke pass, khôi phục thử và rollback được diễn tập.
- **Bàn giao** Các task trên đã được review, bản trình diễn staging và bằng chứng kiểm thử đính kèm. Migration có hướng nâng cấp và hướng khôi phục khi sprint thay đổi schema.
- **Rủi ro dự kiến** Migration không tương thích, outage provider hoặc không đủ DB restore windows.

[Lộ trình và điều kiện phát hành](00-master-roadmap.md) · [Ma trận kiểm thử](../testing/02-test-cases.md)

