# Sprint 04 — Tiến độ và dashboard

> PROPOSED · MVP · Các đường dẫn code bên dưới là vị trí dự kiến.

## Mục tiêu và phạm vi

Hiển thị tiến độ đáng tin và giúp người học quay lại bài đang làm.

- **Phạm vi** Continue, dashboard, mục tiêu, thời gian học có giới hạn và lịch sử gần đây.
- **Tiền điều kiện và phụ thuộc** [Sprint 03](sprint-03.md)
- **Tính năng** FR-PROG-001, FR-CUR-001, FR-SET-001.
- **Đặc tả giao diện** [SRS](../requirements/02-SRS.md), [API](../architecture/05-api-specification.md), [ERD](../architecture/04-database-design.md).

## Công việc theo lớp

| Lớp | Công việc |
|---|---|
| PostgreSQL | Aggregates/progress, study sessions, local day và goal effective date. |
| Backend | GET /me/progress, daily goals, activity intervals và truy vấn resumable. |
| Frontend | Dashboard ngày, progressbar, skeleton/empty, chỉnh mục tiêu. |
| Nội dung | Biên tập nhãn hướng dẫn và safe empty state. |
| Kiểm thử | Ngày địa phương, DST, hai tab, idle, goal update và resume. |
| Bảo mật | Chủ tài khoản, giảm telemetry, chặn client tự khai duration dài. |

## Task có thể review độc lập

### S04-01 — Chiếu tiến độ và resume

- **Mục tiêu** Trả trạng thái mà dashboard và catalog dùng chung.
- **Tệp và module** apps/api/app/progress, apps/api/tests/progress, apps/api/alembic/versions
- **Đầu vào** Completion receipt và eligible run.
- **Đầu ra** Aggregate per learner/lesson và /me/progress.
- **Phụ thuộc** S03-02
- **Ưu tiên và ước lượng** P0 · 3–4 ngày developer.
- **Hướng dẫn triển khai** Approval completion transaction ghi summary cùng source event. Tách activity gần đây theo cursor.
- **Ca kiểm thử** Hai completion đồng thời, attempt chưa hoàn thành, version mới, cross-user.
- **Nghiệm thu** Đọc lại phản ánh đúng completion; retry không thêm bản ghi.
- **Commit đề xuất** `feat: project atomic learning progress`.

- [ ] Viết ca kiểm thử nêu trên và kiểm tra lỗi đặc trưng trước thay đổi.
- [ ] Hoàn thành đầu ra, chạy ca kiểm thử liên quan và đối chiếu nghiệm thu.
- [ ] Gửi thay đổi và bằng chứng chạy kiểm thử để review.

### S04-02 — Đo study time và mục tiêu

- **Mục tiêu** Tính phút ngày có thể tái lập.
- **Tệp và module** apps/api/app/progress/study, apps/web/features/study-session, apps/api/tests/progress
- **Đầu vào** Visibility/activity heartbeat có server time, timezone, goal.
- **Đầu ra** Daily rollup và target hiệu lực theo chính sách.
- **Phụ thuộc** S04-01
- **Ưu tiên và ước lượng** P0 · 3–4 ngày developer.
- **Hướng dẫn triển khai** Cap heartbeat và idle, gộp khoảng trùng; đóng date bucket theo IANA và giữ attribution của ngày đã ghi.
- **Ca kiểm thử** Overlap hai tab, heartbeat trễ, DST, vượt midnight, timezone đổi.
- **Nghiệm thu** Không cộng hai lần và lịch sử bền qua đổi timezone.
- **Commit đề xuất** `feat: track bounded study time and goals`.

- [ ] Viết ca kiểm thử nêu trên và kiểm tra lỗi đặc trưng trước thay đổi.
- [ ] Hoàn thành đầu ra, chạy ca kiểm thử liên quan và đối chiếu nghiệm thu.
- [ ] Gửi thay đổi và bằng chứng chạy kiểm thử để review.

### S04-03 — Dashboard và điều hướng học tiếp

- **Mục tiêu** Đưa người học từ trạng thái hiện tại đến việc tiếp theo.
- **Tệp và module** apps/web/app/(learn)/dashboard, apps/web/features/progress, apps/web/tests/e2e
- **Đầu vào** Progress/goal, published curriculum, run cũ.
- **Đầu ra** Dashboard có retry, next learning path và chỉnh goal.
- **Phụ thuộc** S04-01, S04-02
- **Ưu tiên và ước lượng** P0 · 2–4 ngày developer.
- **Hướng dẫn triển khai** Giữ CTA duy nhất ở empty state, update ngay sau mutation success, retry không phá các vùng đã tải.
- **Ca kiểm thử** Người mới, API lỗi một phần, hoàn tất xong thiếu mạng, screen reader progress.
- **Nghiệm thu** Rời bài và quay lại đúng vị trí từ dashboard.
- **Commit đề xuất** `feat: surface learner progress and next steps`.

- [ ] Viết ca kiểm thử nêu trên và kiểm tra lỗi đặc trưng trước thay đổi.
- [ ] Hoàn thành đầu ra, chạy ca kiểm thử liên quan và đối chiếu nghiệm thu.
- [ ] Gửi thay đổi và bằng chứng chạy kiểm thử để review.

## Điều kiện hoàn tất

- **Nghiệm thu sprint** Hoàn tất bài cập nhật đúng một lần. Mục tiêu và thời gian theo ngày IANA và giữ lịch sử.
- **Bàn giao** Các task trên đã được review, bản trình diễn staging và bằng chứng kiểm thử đính kèm. Migration có hướng nâng cấp và hướng khôi phục khi sprint thay đổi schema.
- **Rủi ro dự kiến** Tab nền hoặc tab mở đồng thời làm phồng thời gian.

[Lộ trình và điều kiện phát hành](00-master-roadmap.md) · [Ma trận kiểm thử](../testing/02-test-cases.md)

