# ADR 0002 — API cùng origin và cấu hình môi trường

**Trạng thái** Accepted cho local và CI, 19/11/2026. **Chủ sở hữu** Engineering và Platform.

## Quyết định

- Trình duyệt gọi URL tương đối. Next chuyển tiếp `/api/v1/:path*`, `/health/live` và `/health/ready` tới API trong local. `API_INTERNAL_URL` là origin nội bộ cấu hình khi build/dev start. Compose dùng `http://api:8000`. Native dev và CI dùng mặc định `http://127.0.0.1:8000`. Biên production dùng TLS reverse proxy cùng origin.
- FastAPI công bố OpenAPI 3.1 dưới `/api/v1/openapi.json`. Các endpoint sức khỏe vận hành nằm ngoài tiền tố nghiệp vụ. Liveness kiểm tiến trình. Readiness kiểm truy vấn thật và revision Alembic đúng head, trả 503 dạng `application/problem+json` khi chưa sẵn sàng. JSON logs giữ request ID, method, status và duration. Tiến trình API/web container chạy bằng tài khoản thường.
- Export schema từ app bằng `uv run --locked python -m app.export_openapi --output openapi.json` trong `apps/api`. `npm run api:types` ở root tạo `apps/web/lib/api/schema.d.ts`. Commit cả hai và kiểm diff trong CI. Code web lấy kiểu health từ schema đã sinh.
- `DATABASE_URL` là DSN SQLAlchemy `postgresql+psycopg://` cho API/Alembic. `TEST_DATABASE_URL` chỉ trỏ vào PostgreSQL dùng một lần cho test có migration. Root `.env.example` là mẫu Compose với dữ liệu dev. Các giá trị thật đi qua env/secret store, không đưa về browser hoặc commit. Port mở trên loopback local.
- Hợp đồng Sprint 01 dùng cookie `__Host-elp_session` opaque, Secure, HttpOnly, SameSite=Lax. Mutation kiểm Origin và CSRF. Guest dùng double-submit, learner dùng header HMAC gắn phiên. OpenAPI thể hiện request/response trước khi tạo client. Các chuẩn này triển khai theo [hợp đồng auth](../05-api-specification.md).

## Open Decision

| Quyết định | Chủ trì | Hạn và tiêu chí chốt |
|---|---|---|
| Hosting production, vùng lưu dữ liệu, domain và ngân sách | Chủ dự án + Platform | Trước triển khai pilot. Đối chiếu yêu cầu lưu trữ, RPO/RTO, TTL, forecast và chi phí. Local dùng Compose. |
| Nhà cung cấp email và sender DNS | Chủ dự án + Identity | Trước gửi thư staging. SMTP thử bằng mail sink, chốt DPA, SPF/DKIM, quota và cảnh báo. |
| Điều kiện độ tuổi, retention, quyền dữ liệu và thị trường pilot | Chủ dự án + Legal | Trước thu dữ liệu thật. Dùng tài khoản và nội dung tổng hợp khi test. |
| Tên thương hiệu và bộ nội dung A1 có quyền sử dụng | Chủ dự án + Nội dung | Trước Sprint 02 publish cho pilot. Duyệt tên, ngữ liệu và attribution theo manifest. |

Chạy nền local và CI bằng dữ liệu cô lập. Chủ dự án duyệt lựa chọn có chi phí trước khi tạo tài nguyên production. Xem [roadmap](../../plans/00-master-roadmap.md).
