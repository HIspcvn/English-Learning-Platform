# Bằng chứng S01-01 — Danh tính email

**19/11/2026** · Baseline `9574c8776cca` trên `main` · Nhánh `feat/sprint-01-auth-onboarding`. Backend chạy trên PostgreSQL 17.12 cô lập ở cổng 25432. Smoke dùng project Compose riêng `elp-s01-verify`, volume mới và Mailpit v1.27.10. Frontend được cài từ lockfile và build trong thư mục sạch. [Kế hoạch](../plans/tasks/S01-01-email-identity.md)

## Kết quả thực thi

| Cổng | Kết quả |
| --- | --- |
| Dependency | `uv sync --locked`, `npm ci`, build image API và web từ lockfile đạt. |
| Ruff và migration | Ruff lint/format đạt. Alembic lên `0001_sprint_00_baseline` rồi `0002_email_identity`. `alembic check` không thấy chênh model/schema. Pytest chạy upgrade, downgrade và kiểm sáu bảng có UUID primary key trong schema riêng. |
| Backend | **50 pytest đạt**. Bao gồm duplicate và claim cạnh tranh, rollback, TTL 24 giờ, resend cooldown, bảo vệ account active, Argon2id, giới hạn IP/email, CSRF/Origin, lỗi validation và database unavailable. Worker tests có SMTP socket timeout thật, retry, lease cạnh tranh, resend trong handshake, tampering AEAD và cleanup khi terminal. |
| HTTP và Mailpit | Bootstrap cho guest qua Next.js, thử `403` và `422`, register trả `202` và user pending chưa có hash. Mailpit nhận thư tiếng Việt với link fragment trong 24 giờ. Job thành công và ciphertext được dọn. Verify trả `204`, replay trả `410`, PostgreSQL có profile và hash Argon2id của user active. Register/resend account active trả cùng `202`, giới hạn trả `429` và `Retry-After`. Nhật ký dịch vụ không có email, mật khẩu và proof của fixture. |
| OpenAPI và TypeScript | Hai lần export OpenAPI cho cùng bytes với JSON đã lưu. TypeScript sinh từ nguồn và đối chiếu bytes với file được theo dõi. Common errors và hai header mutation được kiểm trong contract test. |
| Frontend và trình duyệt | ESLint, TypeScript và Turbopack production build đạt trên bản frontend cô lập. **4/4** unit tests và **4/4** Playwright smoke đạt. Build Docker Linux đạt. |
| Compose và DB outage | `config --quiet` và `up --build --detach --wait` đạt. Migrate thoát 0. Khi dừng DB kiểm thử, readiness trực tiếp và qua Next trả `503`, liveness giữ `200`. Readiness trả `200` sau khi DB chạy lại. |
| Workflow và secret scan | Actionlint 1.7.12 đạt cho workflow cập nhật. Gitleaks 8.30.0 quét source S01-01 và không phát hiện secret. |

Trong thư mục Windows hiện tại, Turbopack gặp lỗi worker PostCSS ngay trên baseline. Production build mặc định đạt khi chạy trên bản frontend sạch ở đường dẫn không có khoảng trắng và trong Compose Linux. Pytest chạy với thư mục tạm mới vì thư mục mặc định trên máy có ACL chặn test export OpenAPI.

## Tái chạy local

Tạo khóa mã hóa thư local và chạy stack theo [README](../../README.md#getting-started). Đặt `DATABASE_URL` và `TEST_DATABASE_URL` tới PostgreSQL dùng cho nghiệm thu, trong đó DB test dành riêng cho fixtures. Từ `apps/api` chạy:

```powershell
uv sync --locked
uv run --locked ruff check .
uv run --locked ruff format --check .
uv run --locked alembic upgrade head
uv run --locked alembic check
$elpPytestTemp = Join-Path ([IO.Path]::GetTempPath()) "elp-s01-pytest-$(New-Guid)"
uv run --locked python -m pytest --basetemp $elpPytestTemp
uv run --locked python -m app.export_openapi --output openapi.json
```

Từ root chạy các cổng web và Compose. Dùng cùng `WEB_PORT` cho Playwright và browser origin.

```powershell
npm.cmd ci --no-audit --no-fund
npm.cmd run api:types
git diff --exit-code -- apps/api/openapi.json apps/web/lib/api/schema.d.ts
npm.cmd run lint
npm.cmd run typecheck
npm.cmd run test:web
npm.cmd run build
docker compose config --quiet
docker compose up --build --detach --wait
$env:PLAYWRIGHT_BASE_URL = 'http://127.0.0.1:3000'
npm.cmd run test:e2e
git diff --check
```

Smoke HTTP cần giữ cookie từ `GET /api/v1/auth/session`. Gửi `POST /api/v1/auth/register` với địa chỉ tổng hợp và hai header `Origin`, `X-CSRF-Token`. Lấy token từ fragment trong Mailpit rồi gửi `POST /api/v1/auth/verify` với `password` và `display_name`. Không ghi giá trị fixture hoặc response chứa CSRF vào báo cáo.

## Bàn giao

S01-01 đạt nghiệm thu local. S01-02 dùng danh tính active và bootstrap guest để triển khai phiên. GitHub Actions `verify` đã PASS cho SHA `a92a9f2`. PR #1 được merge vào `main` tại `6e6d1c4` và workflow sau merge cũng PASS. SMTP production và cổng phát hành còn chờ các mốc tương ứng. [Tracker](../plans/implementation-status.md) · [Run PR](https://github.com/HIspcvn/English-Learning-Platform/actions/runs/44507218765) · [Run main](https://github.com/HIspcvn/English-Learning-Platform/actions/runs/44508335891)
