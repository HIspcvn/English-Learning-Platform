# Bằng chứng kiểm chứng Sprint 00

**Ngày kiểm tra** 19/11/2026, Windows với Docker Desktop Engine 29.7.2. Nhánh local `main`. Kiểm tra clone sạch từ commit ứng dụng `08eecc2`, với project Compose và volume PostgreSQL riêng. [Cách chạy](../../README.md) · [Kế hoạch Sprint 00](../plans/sprint-00.md)

## Kết quả thực thi

| Hạng mục | Lệnh hoặc thao tác | Kết quả đã thấy |
|---|---|---|
| Cài đặt khóa từ clone sạch | `npm ci` và `uv sync --locked --project apps/api` với cache đã cài | Cài thành công cả dependency frontend lẫn 33 package Python trên Windows. Container thực hiện cài đặt từ các lockfile tương ứng. |
| Lint, format và build | ESLint với `--max-warnings=0`, `npm run typecheck`, `npm run build`, `ruff check` và `ruff format --check` | Đạt trên clone sạch. Next.js build tuyến App Router `/`. Ruff xác nhận 12 tệp đã đúng format. |
| Compose và migration sạch | `docker compose config --quiet`, `docker compose up --build --detach --wait`, `alembic check` | PostgreSQL 17, API và web healthy. Migrate exit 0. Revision `0001_sprint_00_baseline`. Alembic xác nhận không có thao tác nâng cấp mới. Ảnh chạy API và web được xác minh UID 10001 và 1000. |
| Backend | `uv run --locked python -m pytest` với `TEST_DATABASE_URL` trỏ vào DB test riêng | 10 đạt, 0 lỗi, 0 skip ở workspace và clone sạch. PostgreSQL thật kiểm schema trống, upgrade, revision sai, downgrade và phân biệt readiness/liveness. |
| Frontend unit | `npm run test:web` | 4 đạt ở workspace và clone sạch. Kiểm liveness schema hợp lệ, HTTP lỗi, trạng thái khác và body JSON sai. |
| Browser E2E | `npm run test:e2e` với URL web Compose thật | 4 đạt ở workspace và clone sạch. Kiểm viewport 390 px, gọi API cùng origin, thử lại sau network failure, readiness và OpenAPI có phiên bản. |
| PostgreSQL dừng và phục hồi | Dừng đúng dịch vụ DB của project test, lấy raw HTTP trực tiếp và qua Next, sau đó khởi động lại DB | Readiness 503 dạng `application/problem+json`, mã `SERVICE_NOT_READY` có request ID. Liveness qua web 200. Readiness trở lại 200 khi DB healthy. Clone vẫn sạch. |
| OpenAPI | Chạy export Python và `npm run api:types`, sau đó kiểm diff hai tệp sinh | Nội dung OpenAPI JSON và kiểu TypeScript khớp commit. FastAPI cung cấp `/api/v1/openapi.json` qua URL web. |
| Workflow và secrets | Actionlint 1.7.12 kiểm workflow. Gitleaks 8.30.0 quét lịch sử Git local trong container chỉ đọc, tắt mạng | Workflow hợp lệ qua kiểm tra tĩnh. Gitleaks không phát hiện leak trong lịch sử đã quét. |

Các ca red trước triển khai xác nhận probe FastAPI trả 404, Playwright chưa tìm được tiêu đề trang và unit probe chưa nhận response hợp lệ. Ở lượt lỗi DB thật, PowerShell trả body Problem dưới dạng `Byte[]`. Đọc raw HTTP và giải mã UTF-8 rồi kiểm lại cùng điều kiện xác nhận API và proxy giữ đúng status, header và body.

Kiểm tra tĩnh đối chiếu 49 tài liệu Markdown, 618 liên kết nội bộ, 49 dòng parity và 73 mã QA trong blueprint. Các mã QA mô tả cả những ca sẽ triển khai ở các sprint sau.

## Cổng bàn giao

- **Local đạt**. Repository có README, code, lockfile và quy trình tái lập. Ma trận parity phủ 49 nhóm quan sát. Thiết kế Gõ câu, điểm, XP và kho từ được chốt cho các sprint tính năng. `docs/research/` đối chiếu nguyên vẹn với commit nền `2663795`.
- **Hosted đang chờ lần chạy đầu**. Repo GitHub private đã tạo và gắn `origin`. Các commit hiện ở local. GitHub Actions mới được kiểm tra tĩnh và qua các bước tương đương ở local. [Workflow](../../.github/workflows/ci.yml)
- **Sprint 01 có thể bắt đầu ở local** dựa trên ADR và hợp đồng xác thực. Hosting, email production, ngân sách, vùng dữ liệu và chính sách pilot được ghi cùng người phụ trách. [ADR và Open Decision](../architecture/adr/0002-http-and-deployment-baseline.md)
