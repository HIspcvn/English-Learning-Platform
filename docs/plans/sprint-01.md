# Sprint 01 — Xác thực và onboarding

> MVP · S01-01 và S01-02 đã đạt CI hosted. S01-03 đạt nghiệm thu local. [Tiến độ thực thi](implementation-status.md)

## Mục tiêu và phạm vi

Người học tạo và khôi phục tài khoản, onboarding vào dashboard với hồ sơ riêng.

- **Phạm vi** Landing cơ bản, xác minh rồi thiết lập mật khẩu, phiên và reset, onboarding, thiết lập cơ bản và yêu cầu xuất/xóa dữ liệu.
- **Tiền điều kiện và phụ thuộc** [Sprint 00](sprint-00.md)
- **Tính năng** FR-AUTH-001, FR-SET-001, FR-LAND-001.
- **Đặc tả giao diện** [SRS](../requirements/02-SRS.md), [API](../architecture/05-api-specification.md), [ERD](../architecture/04-database-design.md).

## Công việc theo lớp

| Lớp | Công việc |
|---|---|
| PostgreSQL | User pending/active, profile, digest token, session, preferences, worker jobs và yêu cầu quyền riêng tư. |
| Backend | Register, verify, resend, login/logout, reset, step-up, profile/preferences và export/erase. Cookie phiên và CSRF cùng origin. |
| Frontend | Form email, xác minh và tạo mật khẩu, onboarding tiếng Việt, thiết lập và yêu cầu quyền dữ liệu. |
| Nội dung | Email giao dịch vi-VN và nội dung công khai nguyên gốc. |
| Kiểm thử | Account isolation, claim token đồng thời, mất phiên, CSRF, step-up hết hạn, export/erase bằng dữ liệu test. |
| Bảo mật | Cookie Secure/HttpOnly/SameSite, chống enumeration, AEAD cho link gửi qua worker, reauth trước khi yêu cầu quyền dữ liệu. |

## Task có thể review độc lập

### S01-01 — Tạo danh tính và vòng đời token

- **Mục tiêu** Cấp danh tính có email xác minh độc lập.
- **Tệp và module** `apps/api/app/identity/`, `apps/api/app/worker/`, `apps/api/alembic/versions/`, `apps/api/tests/identity/`
- **Đầu vào** Email chuẩn hoá, sau đó là token proof, display_name và password hợp lệ.
- **Đầu ra** User pending không có credential, rồi active với mật khẩu băm sau khi xác minh email. Token được gửi qua transactional outbox.
- **Phụ thuộc** S00-03
- **Ưu tiên và ước lượng** P0 · 3–4 ngày developer.
- **Hướng dẫn triển khai** POST /auth/register nhận email. POST /auth/verify nhận token, display_name và password. Claim một lần trong cùng giao dịch, với Argon2id và không sửa tài khoản active từ form khách. Worker chỉ mở token AEAD gắn mục đích trong job, bỏ qua token hết hạn/bị thay và xóa ciphertext sau kết thúc.
- **Ca kiểm thử** Concurrent verify chỉ thắng một lần, replay token 410, resend làm token cũ hết hiệu lực, đăng ký trùng email active, SMTP timeout và dọn ciphertext. Kiểm thư local qua Mailpit.
- **Nghiệm thu** Hai lần đăng ký cùng email không tạo hai user hoặc thay thông tin đăng nhập. Chỉ link hợp lệ chứng minh email mới thiết lập được credential lần đầu.
- **Commit đề xuất** `feat: add email identity lifecycle`.

- [x] Viết ca kiểm thử nêu trên và kiểm tra lỗi đặc trưng trước thay đổi.
- [x] Hoàn thành đầu ra, chạy ca kiểm thử liên quan và đối chiếu nghiệm thu.
- [x] Bàn giao commit local và [bằng chứng chạy kiểm thử](../testing/05-sprint-01-email-identity-verification.md) để review.

### S01-02 — Phiên và quyền truy cập

- **Mục tiêu** Đưa cùng-origin session vào web/API.
- **Tệp và module** `apps/api/app/identity/`, `apps/web/app/(auth)/`, `apps/web/features/auth/`, `apps/api/tests/identity/`
- **Đầu vào** User xác minh, phiên opaque, CSRF.
- **Đầu ra** Session mới sau login, guard, logout, thu hồi khi reset.
- **Phụ thuộc** S01-01
- **Ưu tiên và ước lượng** P0 · 3–4 ngày developer.
- **Hướng dẫn triển khai** Rotate session khi login. Guest dùng double-submit CSRF, learner dùng header HMAC gắn phiên. Kiểm Origin cho mutation và coi phiên bị thu hồi như guest.
- **Ca kiểm thử** Unauthorized/expired/forged CSRF, fixation, logout retry, reset thu hồi.
- **Nghiệm thu** Request ghi thiếu CSRF bị chặn và mọi lỗi phiên về form login thân thiện.
- **Commit đề xuất** `feat: secure session and auth routes`.

- [x] Viết ca kiểm thử và xác nhận lỗi đặc trưng trước khi có endpoint và trước bản sửa timing.
- [x] Hoàn thành đầu ra, chạy PostgreSQL riêng, Playwright qua Compose và đối chiếu nghiệm thu.
- [x] Bàn giao commit local và bằng chứng chạy kiểm thử để review. [Kế hoạch](tasks/S01-02-secure-sessions.md) · [Bằng chứng](../testing/06-sprint-01-secure-sessions-verification.md)
- [x] PR #2 đã merge. CI hosted đạt trên `8a4b05f` và `9a026ae` trên `main`. [CI PR](https://github.com/HIspcvn/English-Learning-Platform/actions/runs/44659079262) · [CI main](https://github.com/HIspcvn/English-Learning-Platform/actions/runs/44659950108)

### S01-03 — Onboarding và settings an toàn

- **Mục tiêu** Lưu mục tiêu và thiết lập lần đầu.
- **Tệp và module** `apps/web/app/(learn)/onboarding/`, `apps/web/features/auth/`, `apps/api/app/identity/`, `apps/web/tests/e2e/`
- **Đầu vào** Tài khoản có phiên, CEFR tự chọn, mục tiêu kỳ thi tùy chọn, locale và IANA timezone.
- **Đầu ra** Hồ sơ tối thiểu và phân nhánh tiếp tục onboarding.
- **Phụ thuộc** S01-02
- **Ưu tiên và ước lượng** P0 · 2–3 ngày developer.
- **Hướng dẫn triển khai** Tách dữ liệu public/private, validate IANA, dùng locale vi/en mặc định vi. PUT /me/preferences hoàn tất onboarding khi đủ trường. Mục tiêu phút/ngày dùng endpoint Progress từ Sprint 04.
- **Ca kiểm thử** Refresh giữa onboarding, timezone lỗi, cách ly tài khoản, xung đột revision, thao tác bàn phím.
- **Nghiệm thu** Đăng ký đến onboarding đến dashboard thành công trên desktop/mobile.
- **Commit đề xuất** `feat: add learner onboarding and settings`.

- [x] Xác nhận ca đỏ của hợp đồng API và guard settings trên baseline trước thay đổi.
- [x] Hoàn thành đầu ra, chạy 118 pytest, 13 unit web và 11 Playwright trên stack riêng.
- [x] Bàn giao nhánh riêng và bằng chứng kiểm thử cho PR vào `main`. [Kế hoạch](tasks/S01-03-onboarding-settings.md) · [Bằng chứng](../testing/07-sprint-01-onboarding-settings-verification.md)

### S01-04 — Yêu cầu xuất và xóa dữ liệu

- **Mục tiêu** Cho chủ tài khoản thực thi quyền dữ liệu qua quy trình có audit.
- **Tệp và module** `apps/api/app/identity/`, `apps/api/app/worker/`, `apps/api/alembic/versions/`, `apps/web/app/(learn)/settings/`, `apps/web/features/settings/`, `apps/api/tests/identity/`
- **Đầu vào** Phiên learner, mật khẩu hiện tại, yêu cầu export hoặc erase đã xác nhận.
- **Đầu ra** Cấp step-up 10 phút, receipt job, trạng thái chủ tài khoản và link tải ngắn hạn sau export.
- **Phụ thuộc** S01-01, S01-02 và S01-03.
- **Ưu tiên và ước lượng** P0 · 3–5 ngày developer.
- **Hướng dẫn triển khai** POST /auth/reauth đánh dấu session hiện tại. POST /me/privacy-requests kiểm step-up và idempotency. Worker chỉ xử lý dữ liệu chủ tài khoản, dọn file export theo TTL, thu hồi phiên khi thực thi xóa và audit metadata tối thiểu.
- **Ca kiểm thử** Sai mật khẩu, step-up hết hạn, CSRF, replay, khác chủ, file hết hạn và worker retry. Chạy một export và một erase trên fixture.
- **Nghiệm thu** Người dùng có thể hoàn tất export và yêu cầu erase sau xác minh. Tài khoản khác không xem trạng thái/tải file và phiên cũ mất quyền khi erase được thực thi.
- **Commit đề xuất** `feat: process private data rights requests`.

- [ ] Viết ca kiểm thử nêu trên và kiểm tra lỗi đặc trưng trước thay đổi.
- [ ] Hoàn thành đầu ra, chạy ca kiểm thử liên quan và đối chiếu nghiệm thu.
- [ ] Gửi thay đổi và bằng chứng chạy kiểm thử để review.

## Điều kiện hoàn tất

- **Nghiệm thu sprint** Người dùng mới từ landing vào dashboard sau khi xác minh email và thiết lập mật khẩu. Refresh giữ phiên hợp lệ, logout thu hồi phiên. Export và erase fixture chạy qua job có audit.
- **Bàn giao** Các task trên đã được review, bản trình diễn staging và bằng chứng kiểm thử đính kèm. Migration có hướng nâng cấp và hướng khôi phục khi sprint thay đổi schema.
- **Rủi ro dự kiến** SMTP deliverability, TTL token, thay đổi chính sách email.

[Lộ trình và điều kiện phát hành](00-master-roadmap.md) · [Ma trận kiểm thử](../testing/02-test-cases.md)

