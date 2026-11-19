# Kiến trúc frontend

**PROPOSED.** Next.js App Router + React + TypeScript, Tailwind với semantic token và component shadcn/ui được điều chỉnh cho nhận diện riêng. Các phân đoạn URL dưới đây là route sản phẩm mới.

## Cấu trúc dự kiến

```text
apps/web/
  app/(public)/                  landing, demo, legal
  app/(auth)/                    login, register, verify, recover
  app/(learner)/                 dashboard, curriculum, lesson, library, settings
  app/(editor)/cms/              import, editor, review, audit
  features/                      auth, curriculum, lesson-run, progress, vocab, grammar,
                                 dictionary, reading, media, pronunciation, cms
  components/ui/                 primitives, dialog, field, icon button, notice
  components/shell/              desktop nav, mobile nav, breadcrumb, page boundary
  lib/api/                       client, problem decoder, generated contract types
  lib/telemetry/                 allowlisted events
```

| Luồng | Route nhóm | Đọc/ghi | Kết quả |
| --- | --- | --- | --- |
| Public và preview | `/`, `/demo`, `/legal/*` | Dùng snapshot công khai và demo đã biên soạn | Demo không tạo kết quả người học; chạy bằng sample original. |
| Auth & onboarding | `/login`, `/register`, `/verify`, `/recover`, `/onboarding` | Auth API và `PUT /me/preferences` | Đăng ký chỉ nhập email. Link xác minh mở form mật khẩu và tên hiển thị, sau thành công chuyển tới login. Onboarding chọn CEFR, mục tiêu thi tùy chọn, locale vi/en mặc định vi và múi giờ IANA; thiết lập thời gian/ngày mở Sprint 4. Loader kiểm session, return path chỉ cùng origin. |
| Học | `/dashboard`, `/roadmap`, `/lessons/[lessonId]`, `/learn/[runId]` | Curriculum, lesson-runs, progress | Mở bản xuất bản, tạo hoặc resume run, vào mode theo loại. |
| Từ vựng | `/vocabulary`, `/vocabulary/[deckId]`, `/review`, `/dictionary` | Decks/cards/entries/reviews | Truy vấn due theo cursor và lưu mục từ từ tra cứu. |
| Kỹ năng | `/grammar`, `/grammar/[lessonId]`, `/reading`, `/reading/[lessonId]`, `/videos`, `/videos/[lessonId]`, `/pronunciation`, `/pronunciation/[soundId]` | Danh mục lesson theo kind, media, transcript | Danh mục theo trình độ; trang detail kỹ năng dùng cùng LessonRef, phiên thi/luyện mở tại `/learn/[runId]`. Video detail có query `mode` đồng bộ với bộ điều khiển. `soundId` là lesson ID của bài IPA đã công bố. |
| Cá nhân | `/progress`, `/settings`, `/help`, `/social` sau V2 | User scoped API | Progress, mục tiêu, tùy chọn, feedback, gamification khi bật. |
| CMS | `/cms`, `/cms/imports/[importId]`, `/cms/lessons/[id]`, `/cms/review` | CMS scope, import và publish | Read-only preview theo quyền và version, validation gắn dòng/field. |

## Sơ đồ frontend

```mermaid
flowchart LR
  R["App Router · layouts/loading/error"]
  SSR["Server Components · public/read initial"]
  C["Client Components · lesson/media/forms"]
  URL["URL params · filter/page"]
  Query["TanStack Query · server state"]
  Local["Reducer/form · draft and transient state"]
  API["Shared typed API client"]
  R --> SSR
  R --> C
  URL --> SSR
  URL --> C
  C --> Query
  C --> Local
  Query --> API
  SSR --> API
```

### Tổ chức và dữ liệu

- Route giữ layout, loading/error boundary, metadata. Feature folder giữ cách phối hợp query/command, reducer và component của nghiệp vụ. API client generated types từ OpenAPI; mapping DTO → view model chỉ khi cần biến đổi.
- Learner server route gửi cookie đến API nội bộ qua wrapper allowlist headers và dùng `cache: no-store`. Protect bằng redirect UI cho UX; API vẫn xác thực, phân quyền và kiểm ownership. CMS link được ẩn theo quyền, quyết định cấp quyền thực thi tại API.
- Query key convention `[resource, userScope, filters]` cho dữ liệu riêng, thêm `runId` hoặc `lessonId/versionId` đúng phạm vi. Clear toàn bộ cache private khi đổi session. Public snapshot cache theo version; bản current pointer có TTL hoặc revalidate khi publish.
- Filter/search/selected tab được quản trong URL nếu có ý nghĩa chia sẻ hoặc back. Text draft giữ theo run/item trong memory đối với typing. Bản nháp dịch V1 dùng API theo run/item và revision riêng, không giữ lâu sau khi submit hoặc hoàn tất. Chỉ xem xét `sessionStorage` có TTL với dữ liệu học tối thiểu, dọn khi logout. Zustand chỉ khi có trạng thái trình phát hoặc shell dùng xuyên route mà React context cục bộ không đủ.
- Typing và grammar gõ bằng controlled form; Enter submit nếu IME đã commit và textarea ở mode có Enter submit. Một lần submit dùng cùng key khi timeout/retry, key mới khi sửa nội dung. Giữ draft khi 503/network. Chặn double click để UX gọn, API kiểm tra duplicate riêng.
- Chuyển trạng thái trên client: `loading → ready → submitting → feedback → next|complete`. 409 stale revision: refetch run rồi hiển thị item thực, giữ nháp cũ để người học sao chép nếu phù hợp. 422 hiển thị lỗi ngay tại trường, không tăng attempt. 401 đưa về đăng nhập và giữ return path nội bộ; 403 yêu cầu quay lại danh mục. Loading skeleton, empty rõ nguyên nhân và CTA.
- Không optimistic score/completion. Learning UI dùng server receipt cho next item, feedback và thống kê. Review chỉ rút card khỏi queue sau response, không bù điểm bằng đồng hồ client.
- Audio dùng native audio/video control hoặc accessible controls; URL media hết hạn → làm mới URL một lần. Transcript dùng cue bắt đầu/kết thúc theo ms, active cue theo media currentTime, người học có thể tắt auto-scroll. Caption song ngữ bố trí hai dòng độc lập; playback, transcript, review state tách rời.
- AI job poll có backoff theo `Retry-After`; pending/timeout hiển thị thông tin, cho quay lại bài. Không chèn HTML model/biên tập thô vào DOM. Text format từ schema và allowlisted markup qua sanitizer.
- Privacy settings yêu cầu nhập lại mật khẩu cho cả export/erase, với thời hạn 10 phút của session. Xác nhận xóa rõ ràng trước khi tạo job; theo dõi trạng thái qua API riêng. Chỉ nút Tải dữ liệu của export hoàn tất mới xin URL riêng tư ngắn hạn. Link xác minh/reset mang token trong fragment; nhập vào state bộ nhớ rồi xóa fragment khỏi URL. Đặt Referrer-Policy: no-referrer cho hai màn hình. Giữ token email, mật khẩu và URL ký sẵn ngoài telemetry và logs.
- CMS dùng tải signed PUT riêng, preview hiện trạng thái checksum/media. Download báo lỗi CSV là tệp do server sinh, tránh formula injection. Publish cần xác nhận version và quyền, show errors theo field và giữ sửa nháp.

## Thiết bị và trợ năng

Desktop có sidebar, content hierarchy và thanh tiến độ bài. Mobile có điều hướng compact, một cột và thao tác chính cố định nếu không che keyboard. Transcript/media và điều khiển đánh giá xuống dưới hoặc đổi thứ tự phù hợp với viewport. Tập trung focus vào heading sau nav và giữ focus giữa input/feedback. Cho phép replay trực quan, `aria-live` feedback vừa đủ, thông báo lỗi liên kết field, phím skip, tab order ở dialog. Font và ngôn ngữ EN/VI truyền đúng `lang`; chỉnh 200% zoom, chiều ngang 320 CSS px và reduced-motion. Xác nhận chống tràn với input dài, không phá dòng giữa glyph/ký tự IPA. Xem [đặc tả màn hình](../design/03-screen-specifications.md) và [NFR](../requirements/05-non-functional-requirements.md).

