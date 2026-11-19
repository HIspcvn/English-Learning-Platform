# Chiến lược kiểm thử và cổng phát hành

**PROPOSED** cho nền tảng mới. Mỗi PR muốn thay đổi nghiệp vụ phải cập nhật đối chiếu FR, hợp đồng và bộ test theo phạm vi. Hồ sơ kiểm thử dùng fixture nguyên bản, PostgreSQL thật trong kiểm thử tích hợp và đồng hồ có thể đóng băng.

## Các tầng kiểm thử

| Tầng | Công cụ dự kiến | Phạm vi và điều kiện đạt |
|---|---|---|
| Unit backend | pytest, parametrization và Hypothesis cho bất biến | Unicode/IME UIs có test riêng, chuẩn hóa và alignment typing, state transitions run, điều kiện hoàn thành, thứ tự ngày, SM-2, rubric, cue lookup, xác định quyền. Deterministic theo cùng version và input. |
| Unit UI | Vitest, React Testing Library | Trạng thái loading/empty/error, gửi/retry và disabled, focus, keyboard, skip link, toast, media controls và CSRF client. Assertion theo hành vi nhìn thấy. |
| Database / integration | pytest, PostgreSQL cùng major production dưới Compose/CI, Alembic | Upgrade từ bản gần nhất, FK/unique/check, hai connection độc lập cho race, transaction rollback, nội dung ghim, tác dụng phụ đúng một lần. Kiểm tra schema trống và snapshot giả lập dữ liệu cũ. |
| API / contract | pytest với FastAPI, OpenAPI diff, client types tạo từ schema đã commit khi có code | Happy path, request/schema, pagination, lỗi chuẩn, cookie+CSRF, quyền từng tài nguyên, idempotency, stale review, 429, media access. CI phát hiện API thay đổi phá vỡ đã công bố. |
| E2E | Playwright Chromium/WebKit/Firefox theo mức ưu tiên | Learner đi từ landing tới học và resume, review đến hạn, editor → reviewer → publisher, browser bị mất mạng. Chromium smoke trên PR, ma trận browser/điện thoại ở staging. |
| Tiếp cận | axe-core, bàn phím, NVDA + Chromium/Firefox và VoiceOver + Safari | WCAG 2.2 AA, focus nhìn thấy, target size, label/error, input và trạng thái bằng chữ, transcript cho media, thao tác khi zoom 200% và giảm chuyển động. Mức nghiêm trọng cao của axe bằng 0 và tất cả luồng chủ chốt qua kiểm tra thủ công. [WCAG 2.2](https://www.w3.org/TR/WCAG22/) |
| Hiệu năng | k6 hoặc Locust cho API, Lighthouse/WebPageTest và RUM | Kịch bản đọc, nộp bài, media, writer concurrency và tải CMS nền. Mỗi kịch bản khóa dataset, topology, profile và percentile theo [hồ sơ hiệu năng](03-performance-and-security.md). |
| Bảo mật và riêng tư | kiểm thử quyền pytest, dependency audit, secret scan và kiểm tra cấu hình CI, thủ công theo OWASP ASVS | Kiểm thử tài khoản chéo, CSRF, XSS, session, upload/media, rate limit, backup, audit, yêu cầu dữ liệu và IAM. Báo cáo phát hành nêu owner và cách xử lý từng phát hiện. [OWASP ASVS](https://asvs.owasp.org/) |
| AI evaluation | Bộ gold versioned, replay với mock deterministic và đánh giá blind của biên tập viên | Đánh giá riêng nghe nói, dịch, tutor, tiếng Việt và timeout/cost. Chạy CI offline với stub, chạy provider staging có ngân sách và cổng human rubric trước bật. |

## Dữ liệu và môi trường

- Sử dụng fixture A1 tại quầy cà phê, hai learner có vai trò giống nhau, editor/reviewer/admin tách tài khoản, một account bị thu hồi phiên, một draft, hai version published và asset ở ba trạng thái ready, pending, revoked. [Fixture nội dung](../data/01-content-schemas.md)
- Seed thời điểm UTC cố định, kiểm tra qua ngày `Asia/Ho_Chi_Minh` và DST với `America/New_York`. Tách mốc ngày mục tiêu khỏi thời điểm due UTC của SRS. API kiểm tra clock do server quản lý.
- Mỗi run test có namespace và tài khoản riêng. Hai thao tác song song trong concurrency test dùng barrier tại tài nguyên thật. Cấu hình tái chạy từ seed cố định, commit/infra/browser versions và dữ liệu giả lập. Dùng Mailpit hoặc email stub, object storage tương thích S3, provider stub và audio/video nguyên bản ngắn.
- Giữ kết quả JUnit, trace lỗi E2E, ảnh đáp ứng, OpenAPI diff, báo cáo WCAG, metrics và mã phiên bản. Giới hạn retention theo cấu hình CI. Không lưu cookie, token hoặc dữ liệu nhận dạng thật trong trace, video hay console.

## Cổng qua sprint và release

| Mốc | Cổng được yêu cầu |
|---|---|
| PR | Lint/typecheck sau khi repo có code, unit, contract, và các integration bị ảnh hưởng. Thay đổi DB chạy upgrade, rollback theo kế hoạch migration và test version pin nếu liên quan. |
| Sprint 0–2 | Quy ước contract, auth/role/CSRF và khả năng local chạy một kịch bản hoàn chỉnh. CMS lỗi giữa apply/publish rollback. Reviewer mở bản preview bằng đúng quyền. |
| Sprint 3–5, MVP | Luồng đăng nhập, chọn A1, typing, reload/resume, hoàn thành, xem tiến độ, vocab và SRS due. Nộp lặp không nhân kết quả. Kiểm tra 320/390 px với bàn phím hiện, smoke tải, sao lưu/khôi phục và kiểm tra bảo mật đi kèm Sprint 12. |
| Sprint 6–9, V1 | Grammar và dictionary, reading/dịch, playback, cue, dictation, IPA/shadowing. Kiểm tra audio không có, Safari/iOS, permission mic bị từ chối, stale transcript và retry. Lặp gate MVP và Sprint 12. |
| Sprint 10–11, V2 | Eval AI theo cohort, budget, timeout và opt-in. Kiểm thử lặp XP, ngày chuyển giờ, riêng tư leaderboard và social nếu bật. Lặp gate Sprint 12 với dữ liệu đại diện. |
| Trước triển khai hoặc rollback | Báo cáo test/metrics và thay đổi schema. Staging restore thành công, xác minh job retry, rollout health, người trực và cách tắt feature flags. Giữ bản kết quả theo commit phát hành. |

NFR và các tiêu chí nghiệm thu định ngưỡng phát hành. Mọi ngoại lệ đã biết cần owner, người duyệt và thời hạn. Rò dữ liệu, mất tiến độ, lỗi phân quyền, nhân đôi kết quả, bước học chính không thực hiện bằng bàn phím và không khôi phục được dữ liệu là lỗi chặn release.

[Ma trận ca kiểm thử](02-test-cases.md) · [Hiệu năng và bảo mật](03-performance-and-security.md) · [Roadmap](../plans/00-master-roadmap.md)
