# English Learning Platform

Bộ tài liệu nghiên cứu AIO English và monorepo của nền tảng web học tiếng Anh dành cho người nói tiếng Việt. Sprint 00 cung cấp ứng dụng Next.js, API FastAPI, PostgreSQL, migration nền và kiểm tra CI. Tên sản phẩm làm việc là Nhịp Anh.

## Chạy từ checkout mới

Yêu cầu Docker Engine với Compose v2+, Node.js 24 với npm 11, Python 3.13 và uv 0.12.7. Mở terminal tại thư mục repo. Các lệnh PowerShell dùng `npm.cmd`; trên Linux/macOS dùng `npm`.

```powershell
if (!(Test-Path .env)) { Copy-Item .env.example .env }
docker compose config --quiet
docker compose up --build --detach --wait
Invoke-RestMethod http://127.0.0.1:3000/health/live
Invoke-RestMethod http://127.0.0.1:3000/health/ready
```

Mở [Web local](http://127.0.0.1:3000/) và [OpenAPI local](http://127.0.0.1:3000/api/v1/openapi.json). Compose chờ PostgreSQL, chạy Alembic một lần, rồi mở API và Web. Các cổng host mặc định DB 15432, API 8000 và Web 3000 cấu hình được trong `.env`. API kết nối các service qua cổng nội bộ Compose. Dùng mật khẩu thuần URL-safe trong Compose local. Giá trị mẫu chỉ dành cho máy dev hoặc CI.

### Chạy kiểm tra

```powershell
npm.cmd ci
npm.cmd run lint
npm.cmd run typecheck
npm.cmd run test:web
npm.cmd run build
npm.cmd exec --workspace @elp/web -- playwright install chromium
$env:PLAYWRIGHT_BASE_URL = 'http://127.0.0.1:3000'
npm.cmd run test:e2e
```

Với cấu hình Compose mặc định, tạo một DB test riêng tên `elp_test` một lần rồi chạy lệnh backend sau. Khi đổi thông tin hoặc cổng PostgreSQL local, sửa các DSN tương ứng. Chỉ dùng `TEST_DATABASE_URL` với DB test cô lập vì bộ kiểm tra chạy migration lên và xuống.

```powershell
docker compose exec -T db createdb -U elp elp_test
$env:DATABASE_URL = 'postgresql+psycopg://elp:elp_local_only@127.0.0.1:15432/elp'
$env:TEST_DATABASE_URL = 'postgresql+psycopg://elp:elp_local_only@127.0.0.1:15432/elp_test'
Push-Location apps/api
uv sync --locked
uv run --locked ruff check .
uv run --locked ruff format --check .
uv run --locked alembic upgrade head
uv run --locked alembic check
uv run --locked python -m pytest
uv run --locked python -m app.export_openapi --output openapi.json
Pop-Location
npm.cmd run api:types
git diff --exit-code -- apps/api/openapi.json apps/web/lib/api/schema.d.ts
```

Để chuyển từ Compose sang hai process dev trực tiếp, chạy `docker compose stop web api` để giải phóng cổng, rồi giữ PostgreSQL với `docker compose up --detach --wait db` và chạy migration ở trên. Terminal API trong `apps/api` chạy `uv run --locked uvicorn app.main:app --host 127.0.0.1 --port 8000 --no-access-log` sau khi đặt `DATABASE_URL`. Terminal frontend chạy `npm.cmd run dev` ở root. Nếu cổng API khác 8000, đặt `API_INTERNAL_URL` trước khi chạy Next dev hoặc build. Dừng stack bằng `docker compose down`, volume PostgreSQL giữ dữ liệu local.

[Bằng chứng chạy Sprint 00](docs/testing/04-sprint-00-verification.md) · [Cấu hình CI](.github/workflows/ci.yml)

## Bắt đầu đọc

1. Mở [Tổng quan khảo sát](docs/research/01-site-exploration.md) để xem số trang, khu vực, tính năng và giới hạn nghiên cứu.
2. Đọc [PRD](docs/requirements/01-PRD.md) để nắm đối tượng, mục tiêu học tập và phạm vi MVP/V1/V2. Dùng [SRS](docs/requirements/02-SRS.md) và [Tiêu chí nghiệm thu](docs/requirements/04-acceptance-criteria.md) để định nghĩa hành vi cần xây.
3. Mở [Lộ trình tổng](docs/plans/00-master-roadmap.md), [Sprint 00](docs/plans/sprint-00.md) và [Sprint 01](docs/plans/sprint-01.md). Dùng API, ERD, thiết kế giao diện và QA làm chuẩn đối chiếu ở mỗi task.

## Cách đọc bằng chứng

| Nhãn | Ý nghĩa |
|---|---|
| **OBSERVED** | Ghi nhận giao diện, thao tác hoặc kết quả trực tiếp tại URL và điều kiện đã nêu trong sổ bằng chứng. Phạm vi quan sát nằm ở từng mục. |
| **INFERRED** | Suy luận có căn cứ, với giải thích và bằng chứng tham chiếu. Cần thử thêm để xác định hành vi trong các điều kiện chưa thấy. |
| **PROPOSED** | Quyết định đề xuất cho sản phẩm mới, gồm mô hình dữ liệu, API, công nghệ, thuật toán và các ca kiểm thử tương lai. |
| **UNVERIFIED** | Trạng thái kiểm chứng của câu hỏi còn mở, chẳng hạn thiếu quyền, điều kiện dữ liệu, quyền mic, kết quả không quan sát được hoặc ngoài phạm vi thao tác. |

Mã bằng chứng dẫn về sổ khảo sát. Mã `FR-…` nối SRS với nghiệm thu và các sprint. Mã `QA-…` định danh ca kiểm thử của sản phẩm mới. Kiến trúc đề xuất dựa trên nhu cầu xây dựng và các bất biến đã ghi trong đặc tả. Số liệu, tài khoản và bối cảnh của AIO English chỉ được mô tả ở mức cần để hiểu hành vi. Thiết kế và fixture mới dùng nhận diện, ngôn ngữ và nội dung riêng.

## Mục lục tài liệu

### Khảo sát

1. [Phạm vi, phương pháp và kết quả khảo sát](docs/research/01-site-exploration.md)
2. [Danh mục chức năng](docs/research/02-feature-inventory.md)
3. [Kiểm kê từng trang](docs/research/03-page-by-page-audit.md)
4. [Luồng người dùng](docs/research/04-user-flows.md)
5. [Phân tích giao diện và trải nghiệm](docs/research/05-ui-ux-analysis.md)
6. [Bằng chứng và ảnh chụp](docs/research/06-evidence-and-screenshots.md)
7. [Hạng mục chưa xác minh](docs/research/07-unverified-features.md)

### Yêu cầu

1. [PRD](docs/requirements/01-PRD.md)
2. [SRS và functional requirements](docs/requirements/02-SRS.md)
3. [User stories](docs/requirements/03-user-stories.md)
4. [Tiêu chí nghiệm thu](docs/requirements/04-acceptance-criteria.md)
5. [Yêu cầu phi chức năng](docs/requirements/05-non-functional-requirements.md)
6. [Ma trận đối chiếu 49 nhóm chức năng](docs/requirements/06-feature-parity-matrix.md)

### Kiến trúc

1. [Kiến trúc hệ thống](docs/architecture/01-system-architecture.md)
2. [Kiến trúc frontend](docs/architecture/02-frontend-architecture.md)
3. [Kiến trúc backend](docs/architecture/03-backend-architecture.md)
4. [Thiết kế PostgreSQL và ERD](docs/architecture/04-database-design.md)
5. [Hợp đồng REST API](docs/architecture/05-api-specification.md)
6. [Bộ máy bài tập](docs/architecture/06-exercise-engines.md)
7. [Kiến trúc triển khai](docs/architecture/07-deployment-architecture.md)
8. [ADR 0001 — Monorepo và toolchain](docs/architecture/adr/0001-local-toolchain-and-monorepo.md)
9. [ADR 0002 — HTTP, local và các quyết định production còn mở](docs/architecture/adr/0002-http-and-deployment-baseline.md)
10. [ADR 0003 — Biến thể, điểm và kho từ](docs/architecture/adr/0003-learning-variants-rewards-vocabulary.md)

### Thiết kế sản phẩm

1. [Design system](docs/design/01-design-system.md)
2. [Sitemap và định tuyến](docs/design/02-sitemap.md)
3. [Đặc tả màn hình và wireframe](docs/design/03-screen-specifications.md)
4. [Danh mục component React](docs/design/04-component-inventory.md)

### Dữ liệu nội dung

1. [Schema nhập và dữ liệu mẫu](docs/data/01-content-schemas.md)
2. [Nguồn dữ liệu và giấy phép](docs/data/02-data-sources.md)
3. [Quy trình biên soạn, duyệt và xuất bản](docs/data/03-content-pipeline.md)

### Kế hoạch

1. [Lộ trình, phụ thuộc và cổng phát hành](docs/plans/00-master-roadmap.md)
2. [Sprint 00 — Chốt yêu cầu và nền tảng](docs/plans/sprint-00.md)
3. [Sprint 01 — Xác thực và onboarding](docs/plans/sprint-01.md)
4. [Sprint 02 — Curriculum và CMS](docs/plans/sprint-02.md)
5. [Sprint 03 — Gõ câu](docs/plans/sprint-03.md)
6. [Sprint 04 — Tiến độ và dashboard](docs/plans/sprint-04.md)
7. [Sprint 05 — Từ vựng và SRS](docs/plans/sprint-05.md)
8. [Sprint 06 — Ngữ pháp và từ điển](docs/plans/sprint-06.md)
9. [Sprint 07 — Đọc và dịch](docs/plans/sprint-07.md)
10. [Sprint 08 — Video và dictation](docs/plans/sprint-08.md)
11. [Sprint 09 — IPA và shadowing](docs/plans/sprint-09.md)
12. [Sprint 10 — AI](docs/plans/sprint-10.md)
13. [Sprint 11 — Gamification và cá nhân hóa](docs/plans/sprint-11.md)
14. [Sprint 12 — Kiểm thử, tối ưu và triển khai](docs/plans/sprint-12.md)

### Kiểm thử và bảo mật

1. [Chiến lược kiểm thử theo tầng](docs/testing/01-test-strategy.md)
2. [Ma trận ca kiểm thử](docs/testing/02-test-cases.md)
3. [Hiệu năng, bảo mật và vận hành](docs/testing/03-performance-and-security.md)
4. [Bằng chứng kiểm chứng Sprint 00](docs/testing/04-sprint-00-verification.md)

Mở README bằng trình đọc Markdown hoặc trình duyệt repository để đi theo liên kết. Muốn xem sơ đồ, dùng trình đọc hỗ trợ Mermaid.
