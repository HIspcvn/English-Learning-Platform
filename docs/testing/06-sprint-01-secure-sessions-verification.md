# Bằng chứng S01-02 — Phiên và quyền truy cập

**19/11/2026** · Nhánh `feat/sprint-01-auth-onboarding`, baseline `a92a9f2b362b`. Pytest và Alembic dùng PostgreSQL 17 riêng tại cổng 25442. Compose dùng một volume PostgreSQL riêng khác ở cổng 25443, Next ở 3302, API ở 8302 và Mailpit ở 8325. Dữ liệu kiểm thử là fixture tổng hợp. [Kế hoạch](../plans/tasks/S01-02-secure-sessions.md)

## Phạm vi đã triển khai

- `GET /api/v1/auth/session` bootstrap guest hoặc trả `UserView` và CSRF gắn phiên. `POST /api/v1/auth/login` xác minh Argon2id, xoay cookie hiện tại và cấp session mới. `POST /api/v1/auth/logout` thu hồi phiên hợp lệ, xóa cookie và trả `204` nhất quán khi lặp lại.
- `POST /api/v1/auth/password/forgot` trả `202` chung, áp dụng ngưỡng thời gian 250 ms cho phản hồi chấp nhận trong điều kiện xử lý bình thường và ghi mail reset cho tài khoản active qua outbox. `POST /api/v1/auth/password/reset` claim proof 30 phút, đổi hash và thu hồi mọi phiên của tài khoản trong một transaction. Phản hồi lỗi dùng Problem Details và `Retry-After` khi bị giới hạn.
- Migration `0003_secure_sessions` thêm `auth_sessions` và `learning_preferences`. Token phiên chỉ lưu digest. Cookie HTTPS có `Secure`, `HttpOnly`, `SameSite=Lax` với tiền tố `__Host-`. HTTP loopback dùng tên cookie riêng. Phiên có idle expiry 14 ngày và hard expiry 30 ngày. Preferences thực quyết định onboarding. Khi chưa có preferences, API trả `vi`, `UTC` và `onboarding_completed=false`.
- Năm trang auth dùng API thật. Link email dùng fragment, được đọc vào bộ nhớ và xóa khỏi URL hiện tại. `/onboarding` và `/dashboard` kiểm phiên server-side và mở thao tác đăng xuất. S01-03 triển khai onboarding và cách lưu preferences. S04-03 triển khai dashboard học tập.
- API local và Compose lấy IP từ socket peer. Next dùng chung bucket IP của proxy. Production cần ingress TLS duy nhất, ghi đè header chuyển tiếp và giới hạn địa chỉ proxy được API tin cậy. [ADR HTTP](../architecture/adr/0002-http-and-deployment-baseline.md#trust-boundary-cho-rate-limiting)

| Phần | Tệp chính |
| --- | --- |
| Migration và model | [0003_secure_sessions.py](../../apps/api/alembic/versions/0003_secure_sessions.py), [models.py](../../apps/api/app/identity/models.py) |
| Phiên, CSRF, rate limit và khôi phục | [routes.py](../../apps/api/app/identity/routes.py), [sessions.py](../../apps/api/app/identity/sessions.py), [csrf.py](../../apps/api/app/identity/csrf.py), [rate_limit.py](../../apps/api/app/identity/rate_limit.py), [recovery.py](../../apps/api/app/identity/recovery.py), [mail.py](../../apps/api/app/worker/mail.py) |
| Web và hợp đồng | [Trang auth](../../apps/web/app/(auth)), [Trang learner](../../apps/web/app/(learn)), [Auth client](../../apps/web/lib/api/auth.ts), [OpenAPI](../../apps/api/openapi.json), [TypeScript schema](../../apps/web/lib/api/schema.d.ts) |
| Kiểm thử và workflow | [Identity pytest](../../apps/api/tests/identity), [Auth unit](../../apps/web/tests/unit/auth-flow.test.ts), [Auth E2E](../../apps/web/tests/e2e/auth.spec.ts), [CI](../../.github/workflows/ci.yml) |

## Các cổng kiểm thử

| Cổng | Kết quả |
| --- | --- |
| Dependency khóa phiên bản | **PASS** `uv sync --locked` và `npm ci --no-audit --no-fund` trong bản frontend sạch. |
| Ruff | **PASS** `ruff check .` và `ruff format --check .`, 37 file đã đúng format. |
| Alembic và PostgreSQL | **PASS** Nâng cấp `0002_email_identity` → `0003_secure_sessions`, `alembic check`, downgrade về `0002`, upgrade và `alembic check` lại. Hai lần check đều không có chênh lệch schema. |
| Pytest | **PASS** 85/85, gồm 50 ca hồi quy baseline S01-01, login, quota, expiry và rotation, Origin/CSRF, logout lặp, reset replay và cạnh tranh, login cạnh tranh với reset, thu hồi toàn bộ phiên và cách ly tài khoản. Baseline S01-01 chạy riêng cũng đạt 50/50. |
| Contract | **PASS** OpenAPI export xác định theo byte. `npm.cmd run api:types` sinh lại đúng file TypeScript đã commit. |
| Frontend lint, typecheck và build | **PASS** ESLint, `npm.cmd run typecheck` và production build Turbopack trong bản sao Windows ở đường dẫn không có khoảng trắng. Build Linux trong Compose cũng đạt. |
| Unit web | **PASS** 9/9. Bao gồm điều hướng onboarding, lấy và xóa fragment, kiểm mật khẩu. |
| Playwright | **PASS** 8/8, gồm 4 ca smoke cũ và 4 ca auth mới. Giao diện 320 px và 390 px, thao tác bàn phím, lỗi mạng, register → Mailpit → verify → login, giữ cookie qua reload và khôi phục browser context, reset → thu hồi phiên → logout. Ca proxy thay forwarded headers nhưng vẫn đạt `429` và `Retry-After` theo bucket IP chung. |
| Compose và Mailpit | **PASS** `config --quiet`, `up --build --detach --wait`, `migrate` thoát 0. Readiness trực tiếp và qua Next chuyển `200 → 503 → 200` khi dừng rồi khởi động lại DB, liveness giữ `200`. Worker dọn ciphertext. Log API, web và worker không chứa proof hoặc mật khẩu fixture. |
| Workflow lint | **PASS** Actionlint 1.7.12 cho cấu hình E2E với Mailpit. |
| Git diff và secret scan | **PASS** `git diff --check` từ baseline S01-01 và Gitleaks 8.30.0 quét lịch sử Git, không phát hiện secret. |
| CI hosted Sprint 00 | **PASS** Workflow Sprint 00 trên `main` tại `ec9be05`. [Run 44495463264](https://github.com/HIspcvn/English-Learning-Platform/actions/runs/44495463264) |
| CI hosted S01-01 | **PASS** PR tại `a92a9f2` và `main` sau merge tại `6e6d1c4`. [Run PR](https://github.com/HIspcvn/English-Learning-Platform/actions/runs/44507218765) · [Run main](https://github.com/HIspcvn/English-Learning-Platform/actions/runs/44508335891) |
| CI hosted S01-02 | **SKIP** Thay đổi ở nhánh local. Chờ review và kết quả GitHub Actions của chính SHA được gửi review. |

Để tái chạy Playwright, dùng stack Compose mới với volume rỗng, đặt `PLAYWRIGHT_BASE_URL` và `PLAYWRIGHT_MAILPIT_URL` theo cổng kiểm thử rồi chạy `npm.cmd run test:e2e`. Ca trust boundary chủ động dùng hết quota reset của IP proxy. [Lệnh chạy](../../README.md#testing--quality-assurance)

## Điều kiện chuyển S01-03

S01-03 dùng guard server-side, `UserView.onboarding_completed` và CSRF hiện tại để lưu preferences và hoàn tất onboarding. Đối chiếu lại hành trình xác minh → đăng nhập → onboarding sau khi đã có form và API preferences thật. Gửi các commit local để review và chạy CI hosted trước khi xác nhận nghiệm thu remote của S01-02. [Checklist Sprint 01](../plans/sprint-01.md#s01-02--phiên-và-quyền-truy-cập)
