# S01-02 — Phiên và quyền truy cập

## Phạm vi và phụ thuộc

- Baseline `a92a9f2b362b64c8100414c1484ea800fbece01d`, nhánh `feat/sprint-01-auth-onboarding`, worktree sạch. GitHub Actions chạy workflow nền và hồi quy S01-01 tại chính SHA này, job `verify` thành công. [Run 44507218765](https://github.com/HIspcvn/English-Learning-Platform/actions/runs/44507218765)
- Dùng danh tính active, Argon2id, double-submit CSRF và transactional outbox từ S01-01. Giữ register và resend `202` chung, verify `204` cho proof hợp lệ và `410` khi hết hiệu lực. Verify tiếp tục yêu cầu login sau khi kích hoạt. [Bằng chứng S01-01](../../testing/05-sprint-01-email-identity-verification.md)
- Triển khai năm endpoint và năm màn hình S01-02. `/onboarding` và `/dashboard` chỉ xác nhận trạng thái phiên và cho phép đăng xuất ở mốc này. S01-03 phụ trách form onboarding và ghi preferences. S04-03 phụ trách dashboard học tập.

## Quyết định thiết kế

- Cookie opaque 32 byte CSPRNG, lưu SHA-256 digest. Cookie HTTPS dùng `__Host-elp_session`, `Secure`, `HttpOnly`, `SameSite=Lax`, `Path=/`; HTTP loopback dùng `elp_session_local`. Idle 14 ngày, hard expiry 30 ngày. Cookie cũ mất quyền khi login xoay phiên hiện tại, khi logout hoặc khi reset mật khẩu. [Kiến trúc backend](../../architecture/03-backend-architecture.md#http-và-quyền)
- Bootstrap trả `UserView` hoặc guest và CSRF proof tương ứng, `private, no-store`. Learner dùng HMAC-SHA256 theo ID phiên với secret CSRF độc lập. Guest dùng double-submit S01-01. Mọi mutation kiểm đúng một Origin trùng cấu hình. Logout với phiên hợp lệ kiểm HMAC, còn giao dịch lặp lại có cùng `204` sau khi cookie đã mất quyền.
- Login và reset đồng bộ trên cùng khóa hàng user. Login xác minh Argon2id với hash thật hoặc dummy và chỉ cấp phiên nếu credential kiểm tra vẫn hiện hành. Reset dùng proof digest theo mục đích, hết hạn sau 30 phút, claim một lần, đổi hash và thu hồi toàn bộ phiên trong một giao dịch. Worker chỉ mở payload AEAD đúng loại, còn hạn, và xóa ciphertext khi kết thúc.
- Next.js local chuyển tiếp cùng origin. Uvicorn local lấy IP từ socket peer, bỏ qua forwarded headers, nên Next dùng chung bucket IP của proxy và vẫn có quota theo email. Ở biên TLS production, route `/api/v1` thẳng tới API qua ingress riêng; nếu bật proxy headers, ingress phải ghi đè `X-Forwarded-For` từ kết nối thực, API chỉ tin địa chỉ của đúng ingress và không được truy cập từ Internet hay peer không tin cậy. [ADR HTTP](../../architecture/adr/0002-http-and-deployment-baseline.md)
- Link email đưa proof vào fragment. Trang xác minh và reset đọc fragment vào bộ nhớ, thay URL hiện tại và giữ referrer policy `no-referrer`. Guards đọc phiên server-side từ API có `no-store` trước khi hiển thị route learner; redirect sau login dùng cờ onboarding từ API.

## Subtask và lịch sử Git

| Thứ tự commit | Phạm vi | Tiêu chí kiểm tra |
| --- | --- | --- |
| `docs: plan S01-02` | Kế hoạch, baseline, hợp đồng và trust boundary. | Đối chiếu API, ERD, NFR và S01-01. |
| `feat(db): add secure session models` | SQLAlchemy và Alembic, `auth_sessions` và dữ liệu đọc `learning_preferences`. Giữ user, token và job hiện tại. | Upgrade từ 0002, `alembic check`, downgrade và upgrade lại trên PostgreSQL riêng. |
| `feat(auth): implement login and session lifecycle` | Login/session/logout, HMAC, cookie, quota và cấu hình tin cậy proxy. | Wrong/pending/unknown cùng `401`; rotate, hết hạn, revoke, Origin và CSRF theo phiên; Next giữ bucket peer. |
| `feat(auth): implement password recovery` | Forgot/reset, reuse proof và outbox, mail tiếng Việt, worker. | `202` chung, reset `410` khi replay, race một lần thắng, revoke toàn bộ phiên của đúng user. |
| `feat(web): build authentication pages` | `(auth)`, `(learn)`, client typed, trạng thái và điều hướng. | Form vi-VN, bàn phím, trường mật khẩu, network/expired, bootstrap và guard server-side. |
| `test(auth): add session and security regression tests` | TDD cho API/worker, isolation PostgreSQL, Playwright desktop/mobile qua Next và Mailpit. | Ca đỏ cho hành vi mới, ca xanh cùng hồi quy S01-01 và QA-AUTH liên quan. |
| `docs: record S01-02 verification` | Tracker, checklist và biên bản cổng kiểm thử. | Từng cổng có `PASS`, `FAIL` hoặc `SKIP`, kèm bằng chứng và điều kiện tới S01-03. |

Sau khi chốt model, có thể làm UI, test và phần proxy song song dựa trên API spec. Recovery phụ thuộc khóa user và hàm thu hồi phiên từ backend. Export OpenAPI và sinh types sau khi ổn định năm endpoint, rồi kiểm diff tái sinh.

## Cổng bàn giao

- Dùng duy nhất PostgreSQL/Compose disposable và Mailpit local cho nghiệm thu. Chạy Ruff, Alembic upgrade/check và rollback, pytest, export OpenAPI, sinh TypeScript, lint/typecheck/build, unit, Playwright, Compose smoke, Git diff và secret scan.
- Ghi lại SHA, kết quả và lỗi còn lại. Review local và gửi thay đổi để có hosted CI cho chính SHA S01-02 là bước kế tiếp trước khi nâng trạng thái nghiệm thu remote. S01-03 có thể dùng `UserView.onboarding_completed`, guards và phiên đã nghiệm thu local.
