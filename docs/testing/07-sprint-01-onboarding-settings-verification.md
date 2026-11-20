# Bằng chứng S01-03 — Onboarding và settings

**20/11/2026** · Nhánh `codex/s01-03-onboarding-settings`, baseline `9a026ae`. S01-02 đã merge, CI đạt cả trên commit cuối của PR và commit merge. Kiểm thử S01-03 dùng PostgreSQL 17 và Mailpit của project Compose riêng `elp-s0103`. PostgreSQL ở cổng `15433`, API ở `18000`, Next.js ở `13000` và Mailpit ở `18025`. [Kế hoạch](../plans/tasks/S01-03-onboarding-settings.md) · [PR S01-02](https://github.com/HIspcvn/English-Learning-Platform/pull/2) · [CI baseline main](https://github.com/HIspcvn/English-Learning-Platform/actions/runs/44659950108)

## Phạm vi nghiệm thu

- Bốn endpoint `/api/v1/me/profile` và `/api/v1/me/preferences` xác định chủ tài khoản từ cookie phiên hiện có. Các lệnh ghi kiểm `Origin` và CSRF gắn phiên. PostgreSQL lưu profile và preferences riêng theo `user_id`.
- `0004_learner_settings` thêm bio nullable và bảng receipt idempotency. Preferences dùng revision, đặt timestamp hoàn tất ở lần lưu hợp lệ đầu tiên, giữ timestamp qua settings và ghi receipt cùng transaction. Mục tiêu cũ ngoài danh mục được hiển thị như chưa chọn, giữ nguyên giá trị đã lưu khi đọc.
- `/onboarding` khôi phục bản nháp cùng tab khi refresh. `/settings` lưu hồ sơ và tùy chọn riêng. Sau khi hoàn tất, `/dashboard` hiển thị thông tin tài khoản và danh mục học sắp mở. Locale `vi/en` lưu vào tài khoản, phần giao diện S01-03 dùng tiếng Việt. [Hợp đồng API](../architecture/05-api-specification.md#identity-và-tài-khoản--fr-auth-001-fr-set-001)

## Các cổng kiểm thử

| Cổng | Kết quả |
| --- | --- |
| Ca đỏ trước triển khai | **Xác nhận** Test OpenAPI thiếu `/api/v1/me/profile` trên baseline. Playwright trên stack S01-02 thấy `/settings` chưa chuyển guest về `/login`. |
| Ruff | **PASS** `ruff check .` và `ruff format --check .`, 44 tệp đúng format. |
| Alembic | **PASS** `0003_secure_sessions → 0004_learner_settings → 0003_secure_sessions → 0004_learner_settings`. Hai lần `alembic check` không có drift. Ca tích hợp xác nhận dữ liệu preferences cũ còn nguyên sau vòng migration. |
| Pytest | **PASS** 118/118 trên PostgreSQL riêng, gồm hồi quy S01-01/S01-02, validation, Origin/CSRF, isolation, race trên hai phiên, stale revision, replay idempotency và dữ liệu trước migration. JUnit ở `test-results/s0103-api-junit.xml`. Trên Windows dùng `--basetemp` riêng do ACL của thư mục tạm mặc định. |
| OpenAPI và TypeScript | **PASS** Export OpenAPI và `npm run api:types`. Sinh lặp lại cho kết quả giống nhau theo byte. |
| Web lint, typecheck và unit | **PASS** ESLint, Next typegen, `tsc --noEmit`, 13/13 unit tests. |
| Production build | **PASS** `npm run build` trên bản cuối trong Compose Linux. Kiểm tra riêng cho thấy lỗi worker PostCSS của baseline vẫn tái hiện trong sandbox Windows. Bản sao Windows ngoài sandbox build được. [Bằng chứng S01-01](05-sprint-01-email-identity-verification.md) |
| Playwright Chromium | **PASS** 11/11 qua Next và Mailpit, gồm 8 ca hồi quy và 3 ca S01-03. Kiểm tra desktop 1280 px, mobile 390/320 px, bàn phím, lỗi mạng khi lưu, refresh bản nháp, hoàn tất onboarding, lưu settings và khôi phục sau xung đột revision. Báo cáo `apps/web/playwright-report/index.html` có ảnh onboarding desktop và mobile. |
| Docker Compose smoke | **PASS** `config --quiet`, build và khởi động stack. Migration thoát `0`. Readiness trực tiếp và qua Next chuyển `200 → 503 → 200` khi dừng và khởi động lại PostgreSQL. Liveness giữ `200` khi PostgreSQL dừng. |

Các kiểm tra GitHub Actions được đối chiếu theo commit đầu nhánh trong PR vào `main`. [Workflow](../../.github/workflows/ci.yml)

Avatar khác null hiện trả `404` đến khi có media catalog để kiểm tra ownership và trạng thái ready. Rollback `0004_learner_settings` bỏ dữ liệu bio và receipt tạo từ S01-03, giữ nguyên bảng hồ sơ và preferences của S01-02. Sao lưu các trường mới trước khi rollback môi trường có người dùng.
