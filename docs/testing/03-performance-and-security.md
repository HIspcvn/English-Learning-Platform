# Hiệu năng, bảo mật và vận hành

**PROPOSED**. Chủ sản phẩm và kỹ thuật chốt ngưỡng production ở [NFR](../requirements/05-non-functional-requirements.md) cùng topology [triển khai](../architecture/07-deployment-architecture.md). Các giá trị bên dưới là profile kiểm thử và đề xuất khởi đầu cho staging.

## Hồ sơ tải và cách đo

| Tín hiệu | Cách kiểm tra | Mục tiêu đề xuất |
|---|---|---|
| Dashboard, catalog, progress, due | Dataset QA 10.000 learner, 500 lesson đang publish, 1 triệu attempt phân bố không đều, 50 learner sessions đồng thời. Ramp 5 phút, steady state 15 phút, ba lần. Cố định vùng, build, browser, pool và warmup. | p95 API đọc ≤300 ms và lỗi ngoài dự kiến dưới 1% trong profile. |
| Typing submit và complete | Cùng 50 session. Mỗi learner có nhịp nộp có độ trễ người dùng, gồm lượt nhập sai, retry, lặp key, xung đột cursor và hoàn thành. | p95 nộp ≤400 ms. Không mất, bỏ qua hoặc nhân attempt, completion và reward. Ghi p99 và thời gian giữ lock. |
| Media | Thiết bị thật hoặc staging ở profile băng thông cố định, file mẫu trong object storage/CDN, start, seek và đổi playback rate. Đo thời gian đến first frame rồi cue hiển thị và audio sync. | Cue active lệch ≤250 ms trong đường test ổn định, mục tiêu first frame p95 ≤2,5 giây sau thao tác Play trong profile 10 Mbps và RTT 80 ms. API app chỉ phục vụ metadata và quyền truy cập theo architecture. |
| Frontend | Landing, dashboard và typing với mobile viewport, thiết bị đại diện, profile lạnh và cache ấm. Lighthouse lab để tìm hồi quy, RUM lấy p75 theo route, device và mạng. | LCP ≤2,5 s, INP ≤200 ms, CLS ≤0,1 tại p75 với đủ mẫu. Lab không thay cho INP field metric. [Core Web Vitals](https://web.dev/articles/vitals) |
| Job và CMS | Import gói mặc định tối đa 5.000 bản ghi và xử lý media song song lúc learner load. Ghi thời gian chờ của bản ghi cũ nhất, retry, băng thông và DB lock. | Tải học vẫn trong gate chính. Publish chỉ hiện bản đầy đủ, retry không nhân kết quả và backlog giảm khi lượt nhập kết thúc. |

Ba lần chạy, mỗi lần ghi đếm request, percentile, tỷ lệ lỗi và trace đại diện ở từng route. Tách 4xx cố ý khỏi lỗi ngoài mong đợi. Dùng access log đã ẩn danh và ID tương quan, query timings, PostgreSQL wait/locks, pool saturation, CPU, memory và CDN hit để giải thích. Khi baseline vượt tải, thử theo từng mức 25/50/100 session trong giới hạn staging để tìm điểm bão hòa. Đối chiếu số row theo fixture và execution plan của các truy vấn chậm. Chốt SLO theo tier launch trước chạy kiểm định, báo cáo sai lệch kèm owner.

## Bảo mật và quyền riêng tư

| Mặt kiểm tra | Yêu cầu triển khai và bằng chứng |
|---|---|
| Phiên và auth | Cookie phiên opaque đặt Secure, HttpOnly, SameSite theo auth contract và scope tối thiểu. Rotate sau auth và thay quyền, hạn dùng server-side, thu hồi sau sự kiện bảo mật. Kiểm tra cookie không còn truy cập được sau logout/expired, đăng nhập dùng lỗi chung và token reset chỉ sử dụng một lần. |
| CSRF và origin | Lệnh sửa trạng thái dùng cùng origin và token CSRF. Kiểm tra request không có token hoặc origin không được phép bị từ chối trước tác dụng DB, headers CORS ở môi trường phòng thử theo đúng allowlist. |
| Authz | Kiểm tra chủ sở hữu và role tại boundary/service, lặp với run, attempt, SRS, profile, asset, CMS, job và báo cáo import. Fixture gồm hai learner và ba role CMS, bất kể hai tài khoản dùng cùng role. |
| Rate limiting | Cấu hình theo endpoint, tài khoản và IP phù hợp. Tách login/reset, AI/STT, media grants, upload với đọc thường. Test ngay dưới, ở trên và sau cửa sổ. API trả 429 theo contract và hướng dẫn retry, dashboard không gửi trùng. |
| Input, SQL và XSS | Pydantic validate length, enum, pagination, ID, datetime. SQLAlchemy bind values, whitelist sort. Escape output UI, sanitize markup CMS, render cue và AI output như text hoặc allowlist. Kiểm tra dữ liệu hiển thị ở learner, review và các màn hình báo cáo. |
| Media và upload | Bucket riêng, staged upload, checksum, giới hạn size và MIME theo bytes. Tên tệp user không làm object path. Dùng allowlist codec và hạn mức xử lý. Ký URL đã kiểm tra quyền với TTL. Kiểm tra truy cập khi version draft, expired, revoked hoặc thuộc learner khác. |
| Bí mật và hạ tầng | HTTPS, cấu hình secure headers, HSTS sau khi ổn định, DB ngoài public access, credential riêng theo môi trường, quyền IAM tối thiểu. Secrets từ cơ chế runtime, có quy trình rotate. CI scan dependency và bí mật, production role migration tách quyền app. |
| Audit và giám sát | Ghi actor, hành động, target, revision, kết quả, thời điểm và request ID cho auth nhạy cảm, role, publish/revoke và tác vụ dữ liệu. Append-only trong quyền ghi dự kiến. Đặt cảnh báo cho lỗi 5xx, auth burst, media backlog, SRS lỗi và AI runaway. Kiểm tra log không chứa cookie, mật khẩu, audio hay thông tin nhận dạng thừa. |
| Dữ liệu cá nhân | Vẽ data map cho mục đích, người xử lý, thời hạn, vị trí và luồng bên thứ ba. Tách thông tin nhận dạng và dữ liệu học khi phù hợp. Thiết kế yêu cầu truy cập/xuất/sửa/xóa, thời hạn backup và xử lý giọng nói có consent. Pháp lý xác nhận Luật 91/2025/QH15, nghị định hướng dẫn, người học chưa thành niên và chuyển dữ liệu trước khi bật thị trường hoặc provider. [Luật 91/2025/QH15](https://vbpl.moj.gov.vn/bocongan/Pages/vbpq-van-ban-goc.aspx?ItemID=179252), [Nghị định 356/2025/NĐ-CP](https://vbpl.moj.gov.vn/bocongan/Pages/vbpq-thuoctinh.aspx?ItemID=187276) |
| AI opt-in và cost | Feature flag default off, dự toán cost trước call, hard budget per user và per month, max tokens/audio bytes, rate limit, timeout và circuit breaker. Telemetry ghi model/version, latency, outcome và cost ước lượng/đã tính. Không đưa thông tin định danh không cần thiết, hạn chế chuỗi giữ dữ liệu tại provider. |

Chọn controls OWASP ASVS theo mức rủi ro của sản phẩm, chỉ định owner và bằng chứng, chạy lại khi đổi auth, upload, SDK, CDN hoặc phiên bản runtime. Các kiểm thử dùng tài khoản và dữ liệu staging. [OWASP ASVS](https://asvs.owasp.org/)

## Backup, phục hồi và vận hành sự cố

1. Lưu bản sao PostgreSQL và media metadata, bật PITR khi production sử dụng, phối hợp versioning của object storage và retention audit. Bản backup mã hóa, quyền truy xuất hạn chế, sao lưu tách khỏi production runtime. Xác minh dấu thời gian và kiểm tra backup mới tự động.
2. Khi release schema, tạo chứng cứ restore trước migration rủi ro. Chạy khôi phục vào mạng cách ly, xác minh sample checksum, quan hệ media, assertion progress và nội dung ghim. Đo RPO và RTO thực tế theo [NFR](../requirements/05-non-functional-requirements.md). Tập khôi phục sau thay đổi lớn và theo lịch vận hành.
3. Alert theo error rate, critical p95, DB pool, job backlog, mất backup, cost và expired privileges. Mỗi alert có owner, dashboard và runbook. Trong sự cố, bảo toàn request ID, giảm tải hoặc tắt feature flag, restore có điểm dừng và verify sau khôi phục.
4. Diễn tập xoay credential, vô hiệu hóa AI, rollback app/version nội dung và drain job đang chạy. Kiểm tra tương thích nếu DB đã migrate. Bản sửa không thể đảo ngược cần kế hoạch roll forward và đủ backup.

## Đánh giá AI trước phát hành

| Hạng mục | Cách lấy mẫu | Cổng đề xuất bản V2 |
|---|---|---|
| Feedback dịch | Gold set tối thiểu 120 bài, cân bằng EN→VI/VI→EN và lỗi thiếu ý, paraphrase, đáp án ngắn, từ đa nghĩa. Hai giám khảo chấm độc lập trên rubric, người thứ ba giải xung đột. | ≥85% feedback đồng ý với giám khảo ở cấp đạt/chưa đạt. Không có lỗi nghiêm trọng trong tập an toàn đã duyệt. Lưu sai lệch theo lớp dữ liệu cần khắc phục. |
| ASR và shadowing | Âm thanh được cấp quyền, nhiều accent, giọng và mức tạp âm. Ghim chuẩn tham chiếu, đo WER và bỏ sót từ mục tiêu theo cohort. | Ngưỡng WER theo cohort xác lập từ baseline. UI thể hiện độ không chắc chắn và cung cấp nghe lại khi confidence thấp. |
| Tutor | Bộ thao tác hội thoại dùng để kiểm tra đáp ứng mục tiêu, dẫn giải, bám ngữ cảnh, tiếng Việt, lỗi provider và rò dữ liệu. | Không có trường hợp vượt quyền hoặc rò dữ liệu trong tập gate. Human review ở mẫu trở ngại có tác động cao, tắt theo cohort khi chất lượng tụt. |
| Hồi quy, latency, cost | Version hóa model, prompt, rubric, tokenizer, fixtures và cấu hình. Replay golden set trước đổi provider, so p95 và mức chi phí theo tác vụ. | Không phát hành khi vượt hard budget hoặc khi tỷ lệ lỗi và latency vượt NFR. Fallback có thông điệp hữu ích, kết quả rule-based vẫn hoạt động. |

Bộ gold và voice fixture tách hẳn dữ liệu tài khoản thật. Chỉ bật gọi provider ở môi trường có cấu hình quyền và chi phí. Lưu báo cáo version, tiêu chí đạt, fail và người duyệt, tránh lưu nội dung nhạy cảm ở telemetry.

[Chiến lược kiểm thử](01-test-strategy.md) · [Ma trận ca](02-test-cases.md)
