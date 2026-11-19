# S01-01 — Danh tính email và xác minh

## Hiện trạng và phạm vi

Baseline local `main` tại `9574c8776ccad99717ef8f36f74df1e54067a88a` sạch trước khi tạo `feat/sprint-01-auth-onboarding`. FastAPI đã có lifespan, PostgreSQL engine, readiness theo Alembic head, Problem JSON, access log có request ID và export OpenAPI độc lập cấu hình. Revision `0001_sprint_00_baseline` chỉ thiết lập lịch sử. Next.js chuyển tiếp cùng origin và sinh type từ OpenAPI. CI đã có PostgreSQL cô lập, Playwright và Compose. [Sprint 01](../sprint-01.md#s01-01--tạo-danh-tính-và-vòng-đời-token) · [Xác minh Sprint 00](../../testing/04-sprint-00-verification.md)

Phạm vi gồm đăng ký, gửi lại, xác minh, bootstrap CSRF guest, queue giao thư tiếng Việt, migration, contract và kiểm thử. Login, phiên learner, reset, onboarding, màn hình nhận link và triển khai email production thuộc các mốc sau. Link thư dùng `/verify#token=…` theo hợp đồng frontend để token ở fragment. [Frontend](../../architecture/02-frontend-architecture.md)

## Dữ liệu và giao dịch

| Bảng | Bất biến |
| --- | --- |
| `users` | UUID, `email_norm` duy nhất, pending không có hash/verified_at, active có cả hai. Email và credential của tài khoản hiện có giữ nguyên trong register/resend. |
| `user_profiles` | `user_id` vừa là PK vừa là FK. Tạo hồ sơ cùng giao dịch kích hoạt. |
| `auth_tokens` | UUID, digest SHA-256 duy nhất, mục đích, TTL 24 giờ, timestamps consume/supersede và unique partial cho proof mở theo user/mục đích. |
| `jobs` | UUID, dedupe theo loại và token, trạng thái, lease, lần thử, lịch retry. Payload chỉ có ID và mục đích. |
| `auth_mail_secrets` | UUID `job_id` PK/FK, FK user/token, một blob AEAD trên token và index hết hạn. |
| `auth_rate_limits` | Key digest và cửa sổ đếm cố định theo scope. Tăng atomic bằng PostgreSQL upsert, áp dụng chung cho các process. |

`jobs` là hàng đợi transactional của luồng này. Register dùng insert on conflict cho email mới. Resend khóa user trước proof và phát thay thế sau cooldown 60 giây. Issue/retire proof, thay đổi job và ciphertext commit cùng nhau. Verify tìm owner bằng digest, khóa user rồi proof, kiểm lại thời hạn và trạng thái dưới khóa. Sau đó consume, lưu hash Argon2id, tạo profile, kích hoạt và dọn ciphertext trong cùng giao dịch. Rate limit được ghi ở giao dịch riêng để lỗi verify vẫn tính lượt. Migration thêm bảng mới và downgrade chỉ dùng trên DB kiểm thử cô lập. [Thiết kế DB](../../architecture/04-database-design.md)

## API và bảo mật

| Route dưới `/api/v1` | Contract |
| --- | --- |
| `GET /auth/session` | Bootstrap guest trả `{user:null,csrf_token}` và cookie host-only HttpOnly, SameSite=Lax. HTTPS dùng `Secure` và prefix `__Host-`. |
| `POST /auth/register` | `{email}` → `202 {accepted:true}` cho user mới, trùng hoặc đã active. |
| `POST /auth/verification/resend` | `{email}` → cùng `202` cho mọi trạng thái, kể cả cooldown. |
| `POST /auth/verify` | `{token,password,display_name}` → `204`; proof không dùng được → `410`. |

Mutation kiểm `Origin` cấu hình và so sánh constant-time cookie với `X-CSRF-Token`. HTTP chỉ dành cho loopback local/test. Validate email tối đa 254, chuẩn hóa case và miền IDNA, giữ dấu chấm và dấu cộng. Password 12–128 ký tự, display name 1–80 sau trim. Lỗi chuẩn Problem JSON, `403` cho origin/CSRF, `422` cho payload sai, `429` và `503` kèm `Retry-After`. Trong cửa sổ 15 phút, register/resend chung quota 5/email và 20/IP, verify có quota riêng 10/IP. Local Compose dùng IP của peer Next.js cho request qua rewrite. Trước production, TLS ingress cần ghi đè header IP từ caller và cấu hình Uvicorn chỉ tin ingress đó. Auth responses dùng `no-store`. Log giữ metadata tối thiểu. [Hợp đồng API](../../architecture/05-api-specification.md#identity-và-tài-khoản--fr-auth-001-fr-set-001) · [ADR HTTP](../../architecture/adr/0002-http-and-deployment-baseline.md)

## Giao thư

Worker dùng chung image API, chạy process riêng với PostgreSQL và Mailpit trong Compose. AES-256-GCM dùng khóa chỉ qua môi trường local/test, nonce ngẫu nhiên và associated data gắn user, token, mục đích, TTL. Worker claim bằng `SKIP LOCKED`, commit lease và lần thử trước I/O, rồi kiểm lại proof và lease sau SMTP handshake, ngay trước khi chuyển payload. Retry giới hạn với timeout và backoff. Dọn blob khi terminal, hết hạn, bị consume hoặc supersede. Nếu SMTP đã bắt đầu chuyển thư khi resend commit, API từ chối proof cũ. Worker gửi SMTP theo mô hình at-least-once khi mất xác nhận. KMS tách quyền và mail provider là điều kiện triển khai production. [Kiến trúc backend](../../architecture/03-backend-architecture.md) · [Triển khai](../../architecture/07-deployment-architecture.md)

## Trình tự và kiểm thử

1. Ghi tracker toàn dự án và lưu kế hoạch. Phụ thuộc Sprint 00 local, PostgreSQL 17, uv, npm và Docker Compose. Thêm thư viện chuẩn hóa email, Argon2id và AEAD vào lockfile.
2. Viết ca đỏ cho schema và lifecycle. Thêm SQLAlchemy models, revision kế tiếp, fixture schema riêng, kiểm upgrade từ baseline, Alembic check và downgrade.
3. Thêm service và tests cho duplicate, pending, active, concurrent claim, replay, proof hết hạn/superseded, cooldown biên, rollback issue/activate và queue atomic.
4. Kiểm worker thành công, SMTP timeout, retry hữu hạn, lease bị bỏ, proof stale, cleanup và ciphertext bị sửa. Thử giao thư thật vào Mailpit với địa chỉ tổng hợp.
5. Bật REST API, bootstrap CSRF, throttle và Problem JSON. Kiểm `202/204/403/410/422/429`, `Retry-After`, no-store, response đồng nhất và log an toàn. Tái sinh OpenAPI/TypeScript và kiểm diff.
6. Chạy Ruff, pytest PostgreSQL, HTTP end-to-end, lint/typecheck/unit/build web, Playwright, Compose và quét diff/secrets. Ghi bằng chứng vào tài liệu kiểm thử, cập nhật tracker và checkbox Sprint 01. [Ca QA](../../testing/02-test-cases.md#auth-curriculum-và-cms)

Chia commit theo tracker, kế hoạch, schema, lát cắt identity–mail–HTTP có test/contract và bằng chứng. Chỉ commit nhóm nhất quán đã kiểm tra. Definition of Done yêu cầu lifecycle PostgreSQL, race/rollback, SMTP Mailpit thực tế, generated contracts và các cổng local có bằng chứng. Review và cổng hosted được ghi riêng theo kết quả thực tế.
