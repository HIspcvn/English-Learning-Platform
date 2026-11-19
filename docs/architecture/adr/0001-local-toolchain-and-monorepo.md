# ADR 0001 — Monorepo và công cụ Sprint 00

**Trạng thái** Accepted cho nền tảng mới, 19/11/2026. **Chủ sở hữu** Engineering.

## Quyết định

- Một repo private, nhánh mặc định `main`. Hai workspace triển khai độc lập dưới `apps/web` và `apps/api`. Cấu hình dev và cổng kiểm tra đặt ở root, blueprint trong `docs/`.
- Web dùng Node.js 24 LTS, npm 11 qua workspaces và một `package-lock.json` ở root. Dùng `npm ci` trên máy mới và CI. Next App Router + React + TypeScript strict + Tailwind. Route groups `(public)`, `(auth)`, `(learn)`, `(admin)` chỉ tạo khi có route thật. URL học tiêu chuẩn là `/roadmap`, `/lessons/[lessonId]` và `/learn/[runId]`. Nghiệp vụ UI nằm ở `apps/web/features/`, schema ở `apps/web/lib/api/`, smoke ở `apps/web/tests/e2e/`.
- API dùng Python 3.13, uv 0.12.7, `pyproject.toml` và `uv.lock` dưới `apps/api`. Chạy `uv sync --locked`. Entry point `app.main:app`, module domain trực tiếp dưới `apps/api/app/`. Dùng FastAPI, Pydantic, SQLAlchemy 2 sync với psycopg 3 và PostgreSQL 17.
- Alembic config ở `apps/api/alembic.ini`, các revision ở `apps/api/alembic/versions/`. Duy trì một head, tên mô tả, chạy upgrade trên DB rỗng và kiểm `alembic check`. Cân nhắc downgrade ở môi trường dùng thử, production rollback theo chính sách expand/contract và khôi phục trong [ADR triển khai](../07-deployment-architecture.md). Revision gốc chỉ tạo metadata Alembic. Thêm bảng theo migration từng sprint.
- Tên Python thống nhất theo biên kiến trúc và task. `identity` giữ auth, `cms` giữ import/publish, `curriculum` giữ thứ tự và version, `learning` giữ run/attempt, `exercises` giữ grader thuần, `progress` giữ mục tiêu/ledger, `vocabulary` giữ từ đã lưu, `srs` giữ lịch ôn. `support`, `gamification`, `social` có biên riêng khi triển khai.

## Kiểm tra và đánh đổi

Tách cài đặt npm và uv giữ lockfile theo hệ sinh thái. Một PostgreSQL và hai app đủ cho luồng từ clone đến smoke. Kiểm cài đặt, lint, format Python, typecheck, production build, migration, API, browser và secret scan trong CI. Xem lại nếu chi phí CI hoặc deployment cho thấy hai workspace phải có vòng phát hành riêng.
