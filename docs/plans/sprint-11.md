# Sprint 11 — Gamification và cá nhân hóa

> PROPOSED · V2 · Các đường dẫn code bên dưới là vị trí dự kiến.

## Mục tiêu và phạm vi

Khuyến khích duy trì nhịp học bằng tiến độ, mục tiêu và thưởng chống ghi trùng.

- **Phạm vi** Mở rộng ledger XP cơ bản đã có từ S3 bằng quy tắc thưởng đã duyệt. Thêm streak, achievements, next recommendation và leaderboard opt-in nếu qua duyệt riêng tư/vận hành.
- **Tiền điều kiện và phụ thuộc** [Sprint 03](sprint-03.md) cho ledger MVP, [Sprint 04](sprint-04.md) cho dữ liệu tiến độ và [Sprint 05](sprint-05.md) cho sự kiện ôn.
- **Tính năng** FR-GAME-001, FR-PROG-001, FR-SOC-001.
- **Đặc tả giao diện** [SRS](../requirements/02-SRS.md), [API](../architecture/05-api-specification.md), [ERD](../architecture/04-database-design.md).

## Công việc theo lớp

| Lớp | Công việc |
|---|---|
| PostgreSQL | Dùng ledger MVP, thêm achievement grants, local-day activity và friendship nếu bật. |
| Backend | Derive rewards from completion events; ranking and privacy gates if authorized. |
| Frontend | XP, streak và achievements có nhãn; đề xuất lộ trình; social optional. |
| Nội dung | Minh bạch quy tắc thưởng và thông báo quyền riêng tư. |
| Kiểm thử | Replay, backdate, streak DST, private account excluded, opt-in respected. |
| Bảo mật | Không thưởng bởi client, không công khai mặc định, rate limit social. |

## Task có thể review độc lập

### S11-01 — XP, streak và huy hiệu

- **Mục tiêu** Phát thưởng theo sự kiện đã xác minh.
- **Tệp và module** apps/api/app/gamification, apps/web/features/progress, apps/api/tests/gamification
- **Đầu vào** Eligible completion/review, local study date, rule ID.
- **Đầu ra** XP ledger row, derived streak và achievement grants.
- **Phụ thuộc** S04-02, S05-02
- **Ưu tiên và ước lượng** P1 · 3–5 ngày developer.
- **Hướng dẫn triển khai** Khóa nguồn theo event và rule của các thưởng V2, giữ nguyên award Gõ câu 10 XP từ ledger MVP. Tính streak theo ngày liên tiếp với IANA snapshot đã ghim. Dedupe khi reprocess.
- **Ca kiểm thử** Dup event, race, future date, DST and rule version.
- **Nghiệm thu** Replaying backfill leaves totals and achievements unchanged.
- **Commit đề xuất** `feat: award learning milestones idempotently`.

- [ ] Viết ca kiểm thử nêu trên và kiểm tra lỗi đặc trưng trước thay đổi.
- [ ] Hoàn thành đầu ra, chạy ca kiểm thử liên quan và đối chiếu nghiệm thu.
- [ ] Gửi thay đổi và bằng chứng chạy kiểm thử để review.

### S11-02 — Gợi ý và social tùy chọn

- **Mục tiêu** Sắp xếp việc học tiếp theo từ dữ liệu tối thiểu.
- **Tệp và module** apps/api/app/recommendations, apps/web/features/recommendations, apps/api/app/social
- **Đầu vào** Current level, due count, last run, opt-in if social pilot.
- **Đầu ra** Explainable next action. Optional invitation/friends after rollout review.
- **Phụ thuộc** S11-01
- **Ưu tiên và ước lượng** P1 · 3–5 ngày developer.
- **Hướng dẫn triển khai** Ưu tiên tiếp tục bài → đến hạn → lesson tiếp theo; social flag mặc định tắt và tránh tên người khác trong event log.
- **Ca kiểm thử** Due queue empty, publication retired, timezone, private account, invite abuse.
- **Nghiệm thu** Gợi ý có lý do rõ và trạng thái hidden an toàn khi flag tắt.
- **Commit đề xuất** `feat: personalize next learning actions`.

- [ ] Viết ca kiểm thử nêu trên và kiểm tra lỗi đặc trưng trước thay đổi.
- [ ] Hoàn thành đầu ra, chạy ca kiểm thử liên quan và đối chiếu nghiệm thu.
- [ ] Gửi thay đổi và bằng chứng chạy kiểm thử để review.

## Điều kiện hoàn tất

- **Nghiệm thu sprint** Mỗi nguồn thưởng ghi một lần, streak vùng giờ đúng; basic flows hoạt động khi social off.
- **Bàn giao** Các task trên đã được review, bản trình diễn staging và bằng chứng kiểm thử đính kèm. Migration có hướng nâng cấp và hướng khôi phục khi sprint thay đổi schema.
- **Rủi ro dự kiến** Pressure từ leaderboard hoặc account spam, reset khi đổi timezone.

[Lộ trình và điều kiện phát hành](00-master-roadmap.md) · [Ma trận kiểm thử](../testing/02-test-cases.md)

