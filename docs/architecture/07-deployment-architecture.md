# Kiến trúc triển khai và tích hợp

**PROPOSED.** Ưu tiên ít dịch vụ, rollback rõ và dữ liệu có thể phục hồi. Sprint 12 là gate khi đưa MVP, V1 và V2 vào môi trường production.

## Deployment

```mermaid
flowchart TB
  CI["GitHub Actions"]
  REG["Container registry · image digests"]
  User["Trình duyệt"]
  subgraph Host["Production app host · private app network"]
    P["TLS reverse proxy"]
    W["Next.js"]
    A["FastAPI"]
    J["Worker · when needed"]
  end
  DB[("Managed PostgreSQL · PITR")]
  O[("Private object storage")]
  Ext["SMTP / AI / monitoring"]
  CI --> REG
  REG --> W
  REG --> A
  REG --> J
  User -->|HTTPS| P
  P --> W
  P --> A
  A --> DB
  J --> DB
  J --> O
  A --> O
  User -->|Short-lived media URLs| O
  J --> Ext
```

| Môi trường | Thiết kế | Gate |
| --- | --- | --- |
| Local | Docker Compose: postgres, API, Web, worker tùy tính năng, mail capture/object storage emulator khi cần. Seed original và env example không có secret. | Lệnh migrate/start có kiểm tra health, integration dùng cùng Postgres major như production. |
| CI | GitHub Actions lint/typecheck/build/unit, integration với Postgres sạch, Alembic upgrade, e2e fixture. Build/sbom/scan/push immutable digest sau merge ở nhánh bảo vệ. | Không deploy khi test fail hoặc migration incompatibility. Secret chỉ vào job deploy được phê duyệt; không in env. |
| Staging | Cùng topology và schema với production, synthetic data, mail sink, provider test. Focus mobile, media, CMS và concurrency. | Smoke + sample restore trước migration rủi ro, baseline load test và note schema version. |
| Production | Một VPS/application host đầu tiên sau TLS và managed Postgres có backup/WAL. Worker cùng Python image nhưng process riêng. Object bucket private và ACL theo mục đích. Tăng số process/horizontal khi quan sát tải. | Health, alert, restore rehearsal, release config, pinned image, backup hợp lệ, rollback owner. Single app host phải cân nhắc nếu availability đo dưới 99.5%. |

Traefik/Caddy/Nginx chọn một theo hosting. DNS/SSL renewal tự động, origin security headers và CSP cho nguồn media cho phép. API/DB ở mạng private; công khai 443, cổng 80 phục vụ redirect/challenge khi cần. DB bắt buộc TLS phía client và user migration tách khỏi runtime. Secrets từ secret manager/host runner, rotation SMTP/API keys và hạn quyền; KMS tách quyền encrypt của API và decrypt của mail worker, giữ key ID theo thời hạn ciphertext; không commit credentials. Mỗi môi trường dùng bucket, DB, issuer và service account riêng. App tách đích API/gateway cho public hostname và lưu policy CORS chặt ở storage; CDN chỉ cache tài sản được phép và có kiểm revoke.

## Release, migration, rollback

1. CI tạo image digest Web/API/worker và migration report; deploy staging theo digest. Chạy Alembic một job singleton với advisory lock, expand schema trước, verify phiên bản app cũ còn đọc. Backfill batch có checkpoint.
2. Prepare production: xác nhận PostgreSQL snapshot/PITR, image rollback, health, log/alert owner. Apply migration additive tương thích; đổi service image theo thứ tự API/worker rồi Web khi schema contract tương thích. Dùng health gate trước chuyển traffic; smoke register email-only qua mail sink tại staging, verify rồi login, resend hết hạn, reauth và export owner-only, curriculum, typing synthetic account được chỉ định, SRS due, CMS publish preview.
3. Nếu readiness hoặc SLO rớt, tắt feature flag ảnh hưởng, rollback image trước trong window tương thích. Không downgrade phá dữ liệu khi vừa có writes. Restore point-in-time chỉ theo incident playbook và quyết định với dữ liệu bị thiếu sau restore; xác nhận FK/pointer/active run/SRS ledger và reconcile media/outbox trước mở lại.
4. Contract migration chỉ sau khi không còn app cũ, backfill đã verify và backup/restore đáp ứng. Publish nội dung có thể chọn lại version đã duyệt bằng quy trình rollback có audit và access policy, run pin giữ nguyên.

## Media ingestion

```mermaid
sequenceDiagram
  actor E as Editor
  participant A as Media API
  participant O as Private storage
  participant J as Worker
  participant D as PostgreSQL
  E->>A: Reserve asset, size, type, checksum
  A->>D: Pending asset
  A-->>E: Asset ID
  E->>A: Request signed PUT
  A-->>E: Short-lived signed PUT
  E->>O: Upload to staging object
  E->>A: Finalize
  A->>D: Verify presence and queue job
  J->>O: Fetch, sniff, scan, validate checksum and metadata
  J->>D: Ready or rejected with reason
  Note over A,D: Publish only after assets ready and provenance approved
```

API client chưa thấy nội dung mới trước action publish và assets ready. Upload bind size/type/hash và object path riêng; input scanner thực hiện ngoài transaction SQL. Kiểm MIME thực, giới hạn bytes/duration/decode, checksum, malware, cue schema/timebase và license/attribution. Object copied đến final key immutable khi ready, DB ghi metadata; giải phóng staging object bằng idempotent cleanup job. Nếu DB update fail sau copy, retry cùng target checksum hoặc cleanup orphan theo 7 ngày. Revoke asset làm API ngừng phát URL mới, TTL playback ngắn (default 5 phút); CDN purge khi cần. Test HTTP range, expired refresh, cue tại boundary và CORS. Private recordings TTL mặc định 7 ngày khi thử nghiệm có đồng ý, TTL ngắn hơn nếu nhu cầu, tách bucket prefix/no public cache.

## AI/STT/TTS (V2)

```mermaid
sequenceDiagram
  actor L as Learner
  participant A as AI API
  participant D as PostgreSQL
  participant W as Scoped worker
  participant P as Model/Speech provider
  L->>A: Request feedback with consent and owned input
  A->>D: Reserve quota and create deduped job
  A-->>L: 202 with result handle
  W->>D: Claim job lease, read pinned rubric
  W->>P: Minimized permitted payload
  P-->>W: Structured output and usage
  W->>D: Validate, settle quota and persist result/abstain
  L->>A: Poll status
  A-->>L: Owned result or safe fallback
```

Quota theo learner/ngày và cap toàn hệ thống, max tokens/audio seconds, timeout/provider retry theo lỗi. Validate structured output và xử lý như dữ liệu; prompt/learning content không có quyền gọi tool. Gửi ít auth/PII nhất, chỉ provider được duyệt, preference opt-in và audit. Translation fallback compare reference; shadowing fallback playback/reference; chấm cốt lõi không phụ thuộc AI. Hủy queue chưa gửi khi opt-out, xóa dữ liệu theo workflow sở hữu và retention. Trường hợp provider đã nhận nhưng chưa có receipt đưa về trạng thái cần điều tra nếu provider thiếu idempotency. Khi chất lượng hay chi phí vượt ngưỡng, tắt flag theo module, giữ lộ trình học chuẩn.

Gia sư AI là mở rộng sau khi hoàn thành gate feedback. Nếu triển khai, giới hạn phiên và lượt hội thoại theo ngân sách; gắn bối cảnh với lesson đã publish, cho phép xóa lịch sử theo chính sách, lọc nội dung và đánh giá dẫn nguồn trước khi mở cho learner. Lời khuyên của gia sư không thay đổi điểm và tiến độ. Quyết định provider, retention và yêu cầu người dùng nhỏ tuổi chốt ở Sprint 10 trước rollout.

## Vận hành và hiệu năng

- Pilot target 99.5% availability tháng trên luồng xác thực và học chính. RPO ≤15 phút, RTO ≤4 giờ với PITR managed PostgreSQL; restore diễn tập trước mỗi release và sau thay đổi topology. Object versioning và lifecycle; verify mapping DB asset IDs/keys sau restore. Incident owner có sổ chạy và quyền tối thiểu.
- Endpoint read p95 ≤300 ms, typing submit p95 ≤400 ms ở 50 phiên learner đồng thời trên baseline đại diện, trừ latency mạng/browser ngoài metric. First media frame p95 ≤2.5 giây trên cấu hình staging mục tiêu; cue sai lệch ≤250 ms qua seek/rate change trong E2E. Ghi rõ dataset, preload, cache, throttling, pass/fail trước release.
- Metrics p50/p95/p99 + 5xx/429, DB locks/storage, queue age, expired lease, provider spend, publish failure, due queue latency, error correlation ID. Alerts theo SLO, queue lâu hơn ngưỡng và backup failure. Logs JSON scrub IP khi phù hợp, không có payload answer, email/token, signed URLs hoặc audio.
- Backup mã hóa, least privilege, logs/PII retention, access audit. Health/readiness probe qua internal loopback/network. Dùng load test thấy bottleneck trước Redis/CDN/replica. Runbook mô tả degraded media/AI, rollback và restore từng lỗi. Xem [performance và security](../testing/03-performance-and-security.md).

