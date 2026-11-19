# Tiến độ triển khai English Learning Platform

**Mốc đối chiếu 19/11/2026** · `main` tại `9574c8776cca` (`origin/main` cùng commit theo ref local) · Worktree sạch khi bắt đầu. Nhánh triển khai hiện tại là `feat/sprint-01-auth-onboarding`.

Ở mốc đối chiếu, ứng dụng có khung Next.js, FastAPI, PostgreSQL/Alembic và workflow CI của Sprint 00. Các đặc tả nghiệp vụ, API và ERD ở các sprint tính năng là đầu vào triển khai. Tiến độ nghiệm thu được ghi theo từng task bên dưới. [Lộ trình dự án](00-master-roadmap.md) · [Bằng chứng Sprint 00](../testing/04-sprint-00-verification.md)

## Quy ước cập nhật

- `NOT_STARTED` — Chưa bắt đầu triển khai task. Phụ thuộc kỹ thuật ghi ở từng dòng.
- `IN_PROGRESS` — Đang triển khai hoặc chạy nghiệm thu. Ghi commit, lệnh đã chạy và kết quả khi có.
- `BLOCKED` — Một bước bắt buộc đang chờ điều kiện bên ngoài. Ghi phần đã đạt và điều kiện gỡ chặn.
- `DONE` — Đầu ra trong repository đã được nghiệm thu bằng bằng chứng thực tế. S00-01 có đầu ra là ADR và hợp đồng đã review. Task tính năng cần code, migration nếu thay đổi schema và kết quả kiểm thử.

## S00–S05 · MVP

| Task và sprint plan | Phụ thuộc trực tiếp | Trạng thái | Nhánh, commit và bằng chứng |
|---|---|---|---|
| [S00-01](sprint-00.md#s00-01--chốt-adr-và-hợp-đồng) Chốt ADR và hợp đồng | Blueprint | DONE | `main`, `1496fa1`. Kiểm 49 tài liệu Markdown, 618 liên kết nội bộ, 49 dòng parity, 73 mã QA. [Bằng chứng](../testing/04-sprint-00-verification.md) |
| [S00-02](sprint-00.md#s00-02--khởi-tạo-môi-trường-chạy) Khởi tạo môi trường chạy | S00-01 | DONE | `main`, `08eecc2`. Clone sạch, Compose healthy, PostgreSQL 17 upgrade/check/downgrade và readiness phục hồi sau khi khởi động lại DB. [Bằng chứng](../testing/04-sprint-00-verification.md) |
| [S00-03](sprint-00.md#s00-03--dựng-ci-và-test-harness) Dựng CI và test harness | S00-02 | BLOCKED | `main`, `9526ba2`. Local đạt 10 API, 4 unit web, 4 Playwright cùng kiểm tra OpenAPI, Actionlint và Gitleaks. Cổng GitHub Actions còn chờ bằng chứng hosted. Nghiệm thu local đáp ứng điều kiện mở S01-01. [Bằng chứng](../testing/04-sprint-00-verification.md) |
| [S01-01](sprint-01.md#s01-01--tạo-danh-tính-và-vòng-đời-token) Danh tính email và xác minh | S00-03 (nền local) | DONE | `feat/sprint-01-auth-onboarding`, schema `69c1209`, identity/worker `c5b75d6`, API `859965e`, Compose/CI `c766827`. 50 pytest, 4 unit web, 4 Playwright, HTTP/Mailpit và Compose đạt. [Bằng chứng](../testing/05-sprint-01-email-identity-verification.md) |
| [S01-02](sprint-01.md#s01-02--phiên-và-quyền-truy-cập) Phiên và quyền truy cập | S01-01 | NOT_STARTED | — |
| [S01-03](sprint-01.md#s01-03--onboarding-và-settings-an-toàn) Onboarding và settings | S01-02 | NOT_STARTED | — |
| [S01-04](sprint-01.md#s01-04--yêu-cầu-xuất-và-xóa-dữ-liệu) Xuất và xóa dữ liệu | S01-01, S01-02, S01-03 | NOT_STARTED | — |
| [S02-01](sprint-02.md#s02-01--khung-khóa-và-route-catalog) Khung khóa và catalog | S01-03 | NOT_STARTED | — |
| [S02-02](sprint-02.md#s02-02--import-draft-theo-manifest) Import draft | S02-01 | NOT_STARTED | — |
| [S02-03](sprint-02.md#s02-03--review-và-publish-phiên-bản) Review và publish | S02-02 | NOT_STARTED | — |
| [S03-01](sprint-03.md#s03-01--chấm-câu-và-phản-hồi-token) Chấm câu và phản hồi token | S02-03 | NOT_STARTED | — |
| [S03-02](sprint-03.md#s03-02--run-attempt-và-completion) Run, attempt và completion | S03-01 | NOT_STARTED | — |
| [S03-03](sprint-03.md#s03-03--giao-diện-bài-tập-và-demo) Giao diện bài tập và demo | S03-02 | NOT_STARTED | — |
| [S04-01](sprint-04.md#s04-01--chiếu-tiến-độ-và-resume) Tiến độ và resume | S03-02 | NOT_STARTED | — |
| [S04-02](sprint-04.md#s04-02--đo-study-time-và-mục-tiêu) Study time và mục tiêu | S04-01 | NOT_STARTED | — |
| [S04-03](sprint-04.md#s04-03--dashboard-và-điều-hướng-học-tiếp) Dashboard và học tiếp | S04-01, S04-02 | NOT_STARTED | — |
| [S05-01](sprint-05.md#s05-01--danh-mục-từ-và-thẻ-cá-nhân) Danh mục từ và thẻ cá nhân | S02-03 cho catalog, S03-02 cho auto-save và backfill | NOT_STARTED | — |
| [S05-02](sprint-05.md#s05-02--scheduler-và-hàng-đợi) Scheduler và hàng đợi SRS | S05-01 | NOT_STARTED | — |
| [S05-03](sprint-05.md#s05-03--giao-diện-ôn-tập) Giao diện ôn tập | S05-02 | NOT_STARTED | — |

## S06–S09 · V1

| Task và sprint plan | Phụ thuộc trực tiếp | Trạng thái | Nhánh, commit và bằng chứng |
|---|---|---|---|
| [S06-01](sprint-06.md#s06-01--bài-ngữ-pháp-và-bài-tập) Ngữ pháp và bài tập | S02-03, S03-02 | NOT_STARTED | — |
| [S06-02](sprint-06.md#s06-02--tra-cứu-chi-tiết-và-lưu-từ) Tra cứu và lưu từ | S05-01 | NOT_STARTED | — |
| [S07-01](sprint-07.md#s07-01--bài-đọc-song-ngữ-và-câu-hỏi) Đọc song ngữ và câu hỏi | S06-02, S03-02 | NOT_STARTED | — |
| [S07-02](sprint-07.md#s07-02--chấm-dịch-có-tham-chiếu) Chấm dịch có tham chiếu | S07-01, S03-02 | NOT_STARTED | — |
| [S07-03](sprint-07.md#s07-03--kênh-góp-ý-riêng-tư) Góp ý riêng tư | S01-02, S02-03 | NOT_STARTED | — |
| [S08-01](sprint-08.md#s08-01--media-pipeline-và-transcript) Media pipeline và transcript | S02-03 | NOT_STARTED | — |
| [S08-02](sprint-08.md#s08-02--player-subtitle-và-luyện-nghe) Player, phụ đề và luyện nghe | S08-01, S03-02 | NOT_STARTED | — |
| [S09-01](sprint-09.md#s09-01--bảng-ipa-và-bài-mẫu) Bảng IPA và bài mẫu | S06-02, S08-01 | NOT_STARTED | — |
| [S09-02](sprint-09.md#s09-02--ghi-âm-cục-bộ-cho-shadowing-và-nghe--nói) Ghi âm cục bộ cho shadowing và Nghe & nói | S03-02, S09-01, S08-02 | NOT_STARTED | — |

## S10–S12 · V2 và công việc phát hành

| Task và sprint plan | Phụ thuộc trực tiếp | Trạng thái | Nhánh, commit và bằng chứng |
|---|---|---|---|
| [S10-01](sprint-10.md#s10-01--consent-queue-và-budget) Consent, queue và ngân sách | S07-02, S09-02 | NOT_STARTED | — |
| [S10-02](sprint-10.md#s10-02--phản-hồi-dịch-và-đánh-giá-ai) Phản hồi dịch và đánh giá AI | S10-01 | NOT_STARTED | — |
| [S10-03](sprint-10.md#s10-03--stttts-và-tutor-giới-hạn) STT/TTS và tutor | S10-01, S09-02 | NOT_STARTED | — |
| [S11-01](sprint-11.md#s11-01--xp-streak-và-huy-hiệu) XP, streak và huy hiệu | S04-02, S05-02 | NOT_STARTED | — |
| [S11-02](sprint-11.md#s11-02--gợi-ý-và-social-tùy-chọn) Gợi ý và social tùy chọn | S11-01 | NOT_STARTED | — |
| [S12-01](sprint-12.md#s12-01--release-gates-theo-phiên-bản) Release gates | MVP: S04-03, S05-03. V1 thêm S07-03, S09-02. V2 thêm S10-03, S11-02. | NOT_STARTED | — |
| [S12-02](sprint-12.md#s12-02--production-và-rollback) Production và rollback | S12-01 theo release | NOT_STARTED | — |

## Cổng phát hành

Chạy S12-01 và S12-02 cho từng release. Ghi kết quả và lệnh rollback đã xác minh trước khi phát hành. [Tiêu chí đầy đủ](00-master-roadmap.md#cổng-theo-phiên-bản) · [Kế hoạch Sprint 12](sprint-12.md) · [Chiến lược QA](../testing/01-test-strategy.md)

| Release | Trạng thái | Điều kiện và bằng chứng cần lưu |
|---|---|---|
| MVP · S00–S05 + S12 | NOT_STARTED | Hành trình từ landing qua xác minh/onboarding đến bài A1, gõ, resume/replay theo lane, tiến độ, XP một lần, kho từ/backfill và ghi danh SRS. Publish có review. Lưu E2E desktop/mobile, kiểm quyền/session/CSRF/export/erase, race DB, idempotency, quyền học liệu, WCAG và biên bản restore. |
| V1 · S06–S09 + S12 | NOT_STARTED | Chạy lại MVP. Nghiệm thu ngữ pháp/từ điển, đọc/dịch, clip song ngữ, dictation, IPA, shadowing và Gõ câu Nghe & nói Nâng cao. Lưu QA-TYPE-17, ma trận thiết bị, cue/audio, phụ đề, quyền media, fallback mic/mạng, cleanup bản ghi và baseline tải. |
| V2 · S10–S11 + S12 | NOT_STARTED | Chạy lại V1. Nghiệm thu streak, leaderboard, thành tích và cá nhân hóa. AI qua cổng privacy/consent, chi phí, eval và fallback. Lưu gold eval, cost/cap, stress concurrency, bằng chứng thu hồi quyền và trạng thái feature flag. Social tùy chọn cần phê duyệt opt-in và owner vận hành. |

## Blocker và bước tiếp theo

- **S00-03 hosted** — Cần lần chạy GitHub Actions thực tế để xác nhận cổng PR. Kiểm tra connector cho commit nền trả về danh sách PR workflow và commit status rỗng. Kết quả local của Sprint 00 đã được lưu. [Workflow](../../.github/workflows/ci.yml) · [Bằng chứng](../testing/04-sprint-00-verification.md#cổng-bàn-giao)
- **Staging và production** — Trước pilot cần chốt hosting, vùng dữ liệu, domain, ngân sách, backup/restore và điều kiện privacy. Trước gửi thư staging cần chốt nhà cung cấp email và sender DNS. [Các quyết định cần chốt](00-master-roadmap.md#các-quyết-định-cần-chốt) · [ADR HTTP và triển khai](../architecture/adr/0002-http-and-deployment-baseline.md)
- **Hiện tại** — S01-01 đã đạt nghiệm thu local. Commit và bằng chứng sẵn sàng review. [Bằng chứng](../testing/05-sprint-01-email-identity-verification.md)
- **Next task** — S01-02 có thể bắt đầu với user active, Argon2id và bootstrap CSRF guest. Tiếp tục S01-03 và S01-04 theo phụ thuộc. [Kế hoạch phiên và quyền truy cập](sprint-01.md#s01-02--phiên-và-quyền-truy-cập)
