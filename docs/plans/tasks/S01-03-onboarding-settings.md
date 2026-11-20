# S01-03 — Onboarding và settings an toàn

**Mục tiêu** Người học đã xác minh có thể lưu hồ sơ học tập, vào `/dashboard` và cập nhật riêng dữ liệu tài khoản của mình tại `/settings`.

**Baseline** `main` và `origin/main` tại `9a026ae`, nhánh `codex/s01-03-onboarding-settings` tách mới từ commit này. S01-02 đã merge và CI đạt trên commit cuối `8a4b05f`. [PR #2](https://github.com/HIspcvn/English-Learning-Platform/pull/2) · [GitHub Actions](https://github.com/HIspcvn/English-Learning-Platform/actions/runs/44659079262)

## Backend và dữ liệu

- Giữ quy trình đăng ký, xác minh, login, reset và cookie hiện tại. Dùng danh tính learner từ phiên để truy vấn `user_id`. Mutation kiểm `Origin` và HMAC CSRF gắn với phiên. Trả dữ liệu riêng với `Cache-Control: private, no-store` và dùng `application/problem+json` cho lỗi.
- `GET /api/v1/me/profile` đọc `user_profiles`. `PATCH` nhận các trường `display_name`, `bio`, `avatar_asset_id` theo allowlist. Dùng bộ kiểm tra tên 1–80 ký tự của identity, tiểu sử tối đa 500 ký tự và từ chối patch rỗng. Thêm cột `bio` nullable qua Alembic. ID avatar chưa thể xác minh ownership và trạng thái ready trước khi có media catalog, nên ID khác null trả `404`. Profile dùng patch theo trường.
- `GET /api/v1/me/preferences` đọc bảng đã có từ `0003_secure_sessions`. Tài khoản chưa lưu nhận `vi`, `UTC`, CEFR null, accent `system`, opt-in false, timestamp null và revision `0`. Cơ sở dữ liệu giữ CEFR bắt buộc trên hàng đã lưu. Dùng `zoneinfo` để kiểm timezone IANA và kiểm locale `vi/en`, CEFR `A1`–`C2` và accent `uk/us/system` với Pydantic.
- `PUT /api/v1/me/preferences` nhận preference đầy đủ và `expected_revision`. Các lựa chọn mục tiêu là để trống, `general` hoặc `exam`. Mục tiêu `exam` dùng mã `ielts` hoặc `toeic` và ngày thi tùy chọn. UI chỉ chỉnh các trường được mở ở Sprint 01. AI và social chưa cho bật mới.
- Kiểm revision khi ghi, khởi tạo từ revision `0` và trả `409` với bản sao cũ. Server đặt `onboarding_completed_at` ở lần lưu hợp lệ đầu tiên và giữ timestamp qua các lần sửa. Session bootstrap tiếp tục đọc cờ từ timestamp. Dùng `Idempotency-Key` 16–128 ký tự, receipt riêng theo chủ tài khoản và thao tác, giữ ít nhất 7 ngày. Ghi preference và receipt trong cùng transaction. Replay cùng key/body nhận lại kết quả, cùng key khác body trả `409`.
- Alembic bổ sung schema trên dữ liệu hiện tại và rollback về `0003_secure_sessions`. Kiểm upgrade, dữ liệu cũ, `alembic check` và downgrade trên PostgreSQL dùng riêng. Xuất OpenAPI và sinh lại types ở commit API.

## Frontend

- `/onboarding` dùng giao diện tiếng Việt, nhóm CEFR, mục tiêu học, kỳ thi khi chọn ôn thi, timezone và ngôn ngữ. Hiển thị tải, lỗi và trạng thái lưu. Giữ bản nháp trên tab theo user và revision khi refresh. Sau khi lưu thành công, mở `/dashboard` qua guard hiện tại.
- `/settings` dùng hai form lưu riêng cho hồ sơ và sở thích học, có chỉnh accent. Giữ giá trị người dùng nhập khi lỗi. Khi revision xung đột, cho tải lại bản đã lưu trước khi thử lại. Thiết lập ngôn ngữ lưu vi/en để các module dùng về sau.
- `/dashboard` hiển thị thông tin tài khoản, đường vào Settings và các khu học tập theo lộ trình. Tài khoản thiếu onboarding đi tới `/onboarding`. Tài khoản đã hoàn tất mở onboarding sẽ về `/dashboard`. Người chưa đăng nhập đi tới `/login`. Các màn hình dùng form native, nhãn và legend, thông báo trạng thái, focus thấy rõ và bố cục phù hợp màn hình nhỏ.
- S01-04 phụ trách quyền dữ liệu. S04-03 phụ trách dashboard tiến độ và mục tiêu phút/ngày. [SRS](../../requirements/02-SRS.md) · [Đặc tả màn hình](../../design/03-screen-specifications.md)

## Ca kiểm thử và thứ tự commit

| Commit | Phạm vi | Bằng chứng cần có |
| --- | --- | --- |
| `docs: plan S01-03` | Baseline, hợp đồng, dữ liệu, UI và phụ thuộc. | Đối chiếu PRD, SRS, API, ERD và Design System. |
| `feat(api): implement learner profile and preferences` | DTO, route, PostgreSQL, migration và schema client. | Quyền learner, Origin/CSRF, validation, ownership, CAS và idempotency. |
| `feat(web): implement learner onboarding` | Guard, form onboarding và dashboard tài khoản. | Login đến onboarding, refresh giữa form rồi hoàn tất, chuyển hướng sau lưu và login lại. |
| `feat(web): add account settings` | Form hồ sơ, preference và accent. | Profile/prefs tồn tại sau refresh, stale revision, trạng thái lưu và lỗi. |
| `test: cover onboarding and access control` | Unit, PostgreSQL integration, Playwright và hồi quy S01-01/S01-02. | Anonymous, owner isolation, profile/timezone/CEFR/optional exam, race giữa hai phiên, desktop/mobile và bàn phím. |
| `docs: record S01-03 verification` | Kết quả thực tế, implementation tracker, checklist Sprint 01. | Ghi kết quả từng cổng và trạng thái PR/CI đã xác minh. |

Chạy ca kiểm thử thiếu tính năng trước khi triển khai. Sau khi cập nhật, chạy Ruff lint/format, pytest với PostgreSQL riêng, Alembic upgrade/check/downgrade, OpenAPI export, TypeScript generation, web lint/typecheck/unit/build, Playwright qua Compose và Mailpit, Docker Compose smoke. Bàn giao bằng push thường và PR vào `main`. [Chiến lược kiểm thử](../../testing/01-test-strategy.md) · [Quy trình bàn giao](../../../AGENT.md)
