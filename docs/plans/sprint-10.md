# Sprint 10 — Các tính năng AI

> PROPOSED · V2 · Các đường dẫn code bên dưới là vị trí dự kiến.

## Mục tiêu và phạm vi

Mở phản hồi AI opt-in có ngân sách, lưu provenance và rubric ổn định.

- **Phạm vi** Worker job, feedback dịch, STT/TTS opt-in, tutor theo feature flag sau eval.
- **Tiền điều kiện và phụ thuộc** [Sprint 07](sprint-07.md), [Sprint 09](sprint-09.md)
- **Tính năng** FR-AI-001, FR-TRANS-001, FR-IPA-001.
- **Đặc tả giao diện** [SRS](../requirements/02-SRS.md), [API](../architecture/05-api-specification.md), [ERD](../architecture/04-database-design.md).

## Công việc theo lớp

| Lớp | Công việc |
|---|---|
| PostgreSQL | AI jobs, result, rubric version, cost quota và timestamps. |
| Backend | Provider adapter, retry/deadline, consent, replay, cancel and fallback. |
| Frontend | AI request states, structured feedback, disclosure and timeout. |
| Nội dung | Tập đánh giá song ngữ và adversarial mô phỏng. |
| Kiểm thử | Schema validation, quality agreement, prompt injection treatment, timeout and budget. |
| Bảo mật | Consent explicit, input redaction, egress bounded và retention policy. |

## Task có thể review độc lập

### S10-01 — Consent, queue và budget

- **Mục tiêu** Chạy tác vụ không khóa luồng người học.
- **Tệp và module** apps/api/app/ai, apps/api/app/worker, apps/api/alembic/versions
- **Đầu vào** Consent scope, rubric/version, request idempotency key, cost cap.
- **Đầu ra** Job receipt và queued/running/succeeded/failed/cancelled statuses.
- **Phụ thuộc** S07-02, S09-02
- **Ưu tiên và ước lượng** P1 · 4–5 ngày developer.
- **Hướng dẫn triển khai** Postgres queue/worker, claim lease, isolate provider timeouts, reserve quota trước khi work.
- **Ca kiểm thử** Consent revoked, concurrent claim, over-budget, timeout, malformed payload.
- **Nghiệm thu** Một request tạo một job và không vượt ngày budget config.
- **Commit đề xuất** `feat: queue consented AI work within quota`.

- [ ] Viết ca kiểm thử nêu trên và kiểm tra lỗi đặc trưng trước thay đổi.
- [ ] Hoàn thành đầu ra, chạy ca kiểm thử liên quan và đối chiếu nghiệm thu.
- [ ] Gửi thay đổi và bằng chứng chạy kiểm thử để review.

### S10-02 — Phản hồi dịch và đánh giá AI

- **Mục tiêu** Yêu cầu provider trả kết quả theo schema.
- **Tệp và module** apps/api/app/ai/evaluation, apps/web/features/translation, evaluation fixtures
- **Đầu vào** Version rubric, redacted answer, calibrated dataset.
- **Đầu ra** Feedback có evidence spans, fallback và report metrics.
- **Phụ thuộc** S10-01
- **Ưu tiên và ước lượng** P1 · 4–6 ngày developer.
- **Hướng dẫn triển khai** Dùng structured schema, reject advice vượt rubric, lưu model/version và kiểm threshold trước rollout.
- **Ca kiểm thử** Known alternatives, bilingual rubrics, harmful instructions trong answer, invalid JSON.
- **Nghiệm thu** Feedback chiến thắng chỉ khi qua quality gate; lỗi hiện fallback.
- **Commit đề xuất** `feat: evaluate structured translation feedback`.

- [ ] Viết ca kiểm thử nêu trên và kiểm tra lỗi đặc trưng trước thay đổi.
- [ ] Hoàn thành đầu ra, chạy ca kiểm thử liên quan và đối chiếu nghiệm thu.
- [ ] Gửi thay đổi và bằng chứng chạy kiểm thử để review.

### S10-03 — STT/TTS và tutor giới hạn

- **Mục tiêu** Thử voice/tutor với cờ theo đối tượng chấp thuận.
- **Tệp và module** apps/api/app/ai/speech, apps/api/app/ai/tutor, apps/web/features/ai
- **Đầu vào** Opt-in, approved audio constraints, approved teaching corpus.
- **Đầu ra** Async speech/tutor result và kill switch, V2 candidate.
- **Phụ thuộc** S10-01, S09-02
- **Ưu tiên và ước lượng** P1 · 4–6 ngày developer.
- **Hướng dẫn triển khai** Nếu duyệt speech V2, dùng opt-in riêng và audio có TTL. Kết quả speech là phản hồi tham khảo, giữ nguyên completion, điểm và eligibility của lượt tự luyện V1. Tutor chỉ dùng nội dung đã cấp quyền và trả hướng dẫn trong cuộc hội thoại.
- **Ca kiểm thử** Audio too long, denied consent, quota, unsafe output, hidden feature flag.
- **Nghiệm thu** File audio có TTL và UI fallback, tutor chỉ mở sau eval riêng.
- **Commit đề xuất** `feat: pilot bounded speech and tutor features`.

- [ ] Viết ca kiểm thử nêu trên và kiểm tra lỗi đặc trưng trước thay đổi.
- [ ] Hoàn thành đầu ra, chạy ca kiểm thử liên quan và đối chiếu nghiệm thu.
- [ ] Gửi thay đổi và bằng chứng chạy kiểm thử để review.

## Điều kiện hoàn tất

- **Nghiệm thu sprint** Chạy offline eval đạt gate; khi provider hỏng vẫn đọc/typing bình thường.
- **Bàn giao** Các task trên đã được review, bản trình diễn staging và bằng chứng kiểm thử đính kèm. Migration có hướng nâng cấp và hướng khôi phục khi sprint thay đổi schema.
- **Rủi ro dự kiến** Một score có thể dao động giữa model/provider và PII có thể xuất hiện trong input.

[Lộ trình và điều kiện phát hành](00-master-roadmap.md) · [Ma trận kiểm thử](../testing/02-test-cases.md)

