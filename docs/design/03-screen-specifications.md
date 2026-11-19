# Screen specifications — Nhịp Anh

**Trạng thái** PROPOSED. Dùng [sitemap](02-sitemap.md) cho route và quyền, [design system](01-design-system.md) cho token, [SRS](../requirements/02-SRS.md) cho quy tắc và [API](../architecture/05-api-specification.md) cho schema. Các màn minh họa bằng wireframe chữ để kỹ sư có thể bắt đầu từ layout và bản đồ focus. Ngôn ngữ giao diện mặc định tiếng Việt, người học có thể chọn tiếng Anh. Đoạn tiếng Anh khai báo lang=en. ID UI dưới đây phục vụ kiểm tra coverage.

## Wireframe bố cục

### W01 · Dashboard

```text
≥1024
┌────────────────── Top app header ───────────────────────┐
│ Nhịp Anh       Học  Thư viện  Tiến độ            Hồ sơ   │
├──────────────────────────────┬──────────────────────────┤
│ Tiếp tục học                 │ Mục tiêu hôm nay  8/15  │
│ A1  ›  Chapter 1  ›  Bài 2   │ [======       ]         │
│ [Tiếp tục · câu 3/8]          │ [Đổi mục tiêu]          │
│                              │                          │
│ Lộ trình / Hàng ôn           │ Từ đến hạn  6            │
│ Danh sách và trạng thái      │ [Ôn từ]                   │
└──────────────────────────────┴──────────────────────────┘
<768  [Menu   Nhịp Anh   Hồ sơ] → Tiếp tục → Mục tiêu → Đến hạn → Lộ trình
```

### W02 · Run học Gõ

```text
≥1024
┌── Quay lại ── Bài 2 ── Từ → Cụm → Câu ── 3/8 ── Đã lưu ┐
│ Prompt, locale, chỉ dẫn                  Danh sách item │
│ [Nghe]  [1×]   [Gợi ý]                   1 ✓  2 ✓  3 •  │
│ Ô gõ phản hồi                       [Kiểm tra / Tiếp]   │
│ Phản hồi chữ + căn chỉnh từ                             │
└─────────────────────────────────────────────────────────┘
<768  Quay lại + tiến độ → prompt → audio → ô gõ → Kiểm tra → phản hồi → Tiếp
```

Giữ cùng vị trí cho Kiểm tra/Tiếp khi bàn phím ảo hiện. Focus vào ô nhập sau khi sang item theo thao tác người dùng. Submit khi Enter và IME đã commit. Nếu có nhiều phần, bộ bước có text, chỉ vùng phần đang làm nhận focus. Kết quả có số câu đúng ngay, assisted, thời gian đã ghi nhận và liên kết về học tiếp. Sau attempt terminal, server trả cursor mới cùng feedback. Nút Tiếp hiển thị item đã được cấp, dùng request hoàn tất riêng khi toàn bộ item bắt buộc ở trạng thái cuối.

### W03 · Bài đọc và dịch

```text
≥1024  [Quay lại • Tiêu đề • Song ngữ/Anh • Từ vựng mở/đóng]
       [Văn bản/câu có từ neo  8 cột] [Từ ngữ cảnh  4 cột]
       [Chọn chiều →] mở modal, cùng route vào run sau start
       [Đoạn nguồn]          [Bản dịch của bạn | Đang lưu]
       [Khi đã nộp: coverage | tiêu chí | mẫu | lịch sử]
<768   Tiêu đề → toggle → từng đoạn → popover/sheet → form → kết quả
```

### W04 · Media workspace

```text
≥1024  [Quay lại • Tiêu đề • Phụ đề | Chép | Shadowing | Quiz]
       [Video + seek + tốc độ]     [Danh sách cue timestamp]
       [Panel chế độ luyện]       [Cue đang phát và lớp dịch]
<768   Video giữ tỷ lệ → mode → điều khiển → bài tập/caption dạng biến thể
```

Khi video không tải hoặc bị pause theo chính sách trình duyệt, thông báo cạnh player và thời gian tham chiếu còn thấy. Cue và câu hỏi hiện theo quyền mode. Dictation nghe được từ cue. Nếu dữ liệu thiếu, thông báo và link quay về. Shadowing hiển thị recording indicator và stop rõ ngay khi thu.

### W05 · Flashcards SRS

```text
      [Review]                 [Còn 6]
      ┌──────────── Từ hoặc cụm ──────────┐
      │ IPA     |   [Nghe]               │
      │ [Lật thẻ] → nghĩa, ví dụ, ghi chú│
      └──────────────────────────────────┘
      [Again]   [Hard]   [Good]   [Easy]
```

Nút rating chỉ xuất hiện khi thẻ lật. Phiên hẹp dùng lưới 2×2, mỗi nút có nhãn Việt và phụ chú thời gian nếu scheduler đã có preview. Tab qua audio và nút lật theo thứ tự. Chính sách đổi nghĩa/phiên bản và SRS conflict do API quyết định.

## Màn public và tài khoản

| ID và route | Mục tiêu, hierarchy, components và navigation | Data, tương tác và lỗi | Reflow và accessibility |
| --- | --- | --- | --- |
| UI-01 · `/`, `/demo` | PublicShell → H1 giá trị luyện ngắn → Thử một câu → demo → auth hoặc dashboard. FAQ/link pháp lý ở footer. | Demo prompt tự biên, nhận snapshot có đáp án mẫu để chấm tại máy, chỉ hiển thị đáp án ở giai đoạn phản hồi, không lấy lịch sử người học. Kiểm tra phản hồi, disabled khi trống, lỗi mạng giữ text, hoàn tất có CTA. | Hero 2 cột → CTA rồi demo 1 cột. Tránh auto-focus khi vừa tới landing. Demo có role status và label trường. |
| UI-02 · `/login`, `/register` | AuthShell → H1 → /register chỉ email và thông báo kiểm tra hộp thư. /login nhận email/mật khẩu và link khôi phục. | Field validation, thông điệp register chung, pending/cooldown, lỗi login dạng chung. Nếu có URL quay lại, chỉ nội bộ hợp lệ. | Form 400–480 px max, một cột. Password visibility và autocomplete đúng ở login. |
| UI-03 · `/verify`, `/recover` | Từ link xác minh, /verify hiện trường tên hiển thị và mật khẩu 12–128 ký tự. /recover gồm yêu cầu email và đặt mật khẩu mới theo link. Cả hai dẫn về login sau thành công. | Server kiểm token trước khi thiết lập credentials. Có trạng thái hết hạn/đã dùng, gửi lại/cooldown và generic message. | Tập trung heading sau transition. Password field gắn nhãn và dùng new-password. |
| UI-04 · `/onboarding` | Header gọn → CEFR → mục tiêu kỳ thi tùy chọn → múi giờ IANA và locale vi/en → Xác nhận → dashboard. | Mặc định vi và cho đổi sau. Các lựa chọn kỳ thi có thể bỏ trống. Mục tiêu phút/ngày đặt ở dashboard/Settings từ Sprint 4. | Nhóm lựa chọn dùng fieldset, có Back và submit. Trường lỗi giữ giá trị. |

## Màn học tập và thư viện

| ID và route | Mục tiêu, hierarchy, components và navigation | Data, tương tác và lỗi | Reflow và accessibility |
| --- | --- | --- | --- |
| UI-05 · `/dashboard` | W01. NextActionPanel là hành động đầu, mục tiêu/review có CTA riêng, link roadmap/progress. | Read model gồm next lesson, run, due, daily goal và phase. Mới học thấy bắt đầu. Lỗi riêng thẻ giữ các thẻ khác. | Desktop 8+4, mobile 1 cột. Progress aria-label, heading rõ, callback không mở modal ngoài ý. |
| UI-06 · `/roadmap`, `/lessons/[lessonId]` | Route map chọn CEFR → UnitList → LessonPreview có mục tiêu, số item, thời lượng, bắt đầu/tiếp tục. | Catalog, quyền, trạng thái, version. Empty cấp chưa có bài. Lộ lý do khóa. Withdrawn điều hướng bài thay. | Accordion mobile vẫn có heading. List button khác link. Khóa mô tả bằng text. |
| UI-07 · `/learn/[runId]` nhập và feedback | W02. ExerciseShell, prompt, audio, input, clue, feedback, tiến độ, status. Câu kế hoặc resume. | Pinned version và current item server. Gợi ý enable theo quyền, reveal gated. Lỗi mạng giữ input trong phiên hiện tại. Reload dùng vị trí và phản hồi đã ghi nhận của server. 409 đối chiếu item mới, quyền hết dẫn login. | Cỡ nhập ≥16 px mobile, screen reader đọc trật tự diff. Enter có guard IME. Không nhảy focus khi status lưu. |
| UI-08 · `/learn/[runId]` kết thúc | RunSummary → số item đúng/assisted → phản hồi → CTA Lộ trình hoặc Ôn từ khi có. | Completion và metrics authoritative, loading khi server xác nhận, đã hoàn tất mở lại summary. Không tự đánh complete khi lỗi. | Một CTA đầu. Progress kết thúc có nhãn mô tả. Heading được focus sau nộp cuối. |
| UI-09 · `/progress` | DailyGoalMeter → lịch hoạt động → filter khoảng → ngày chi tiết. V2 thêm XP/streak/achievement. | YYYY-MM-DD theo local date event, durations/attempts server, timezone label. Empty có giải thích. Cache không nối hai timezone. | Bảng có tiêu đề cột, phiên hẹp thành list theo ngày. Chart nếu có kèm giá trị text và focus. |
| UI-10 · `/vocabulary`, `/vocabulary/[deckId]` | Catalog bộ từ → WordDetail/Bộ đã lưu → CTA bắt đầu Review. | Deck, senses, phiên âm, audio có thể thiếu, trạng thái saved. Lưu nghĩa và đưa vào ôn theo chiều là hai hành động độc lập, replay an toàn. | Grid→list, word row tách CTA audio/save. Dictation không dùng chung phím khi trong form. |
| UI-11 · `/review` | W05. Queue đến hạn, flashcard, bốn mức, trạng thái hết lượt và đến hạn tiếp. | cardId/version/due, review transition, stale và retry. Mặt sau theo thao tác rõ. | Rating 2×2 mobile, có số còn lại dạng live polite. Keyboard có hướng dẫn, không chấm bằng Space khi mới lật. |
| UI-12 · `/grammar`, `/grammar/[lessonId]` | Catalog, bài cấu trúc theo H2 → giải thích, ví dụ, mục lục → dùng đúng exercise mode. | Versioned safe blocks, mô tả, examples, item types. Khi thiếu quiz tiếp tục đọc. | TOC bung/gập, code/formula wrap. Radio labels hoặc fieldset được mô tả. |
| UI-13 · `/dictionary` | DictionaryCombobox ở đầu → entry → các sense → collocations, refs, save. | Suggestions và cancellation stale, query length cap, IPA/audio, trạng thái no matches và thử lại. Tra và lưu cần tài khoản đã xác thực. | Dùng ARIA combobox, mũi tên/Enter/Esc, vocab popover không che form. |
| UI-14 · `/reading`, `/reading/[lessonId]` | Catalog theo CEFR/chủ đề → W03 đọc → song ngữ/Anh → popover hoặc panel từ → CTA dịch. | Passage blocks, anchors, license/source/locale, no translation fallback. Route giữ vị trí khi mode đổi. | Dịch theo sau đoạn tương ứng khi hẹp. Toggle aria-pressed, đoạn lang phù hợp. |
| UI-15 · `/learn/[runId]` dịch | W03 sau chọn chiều. Draft, số từ, lưu nháp, nộp, summary/rubric/mẫu/history và yêu cầu AI khi V2. | Empty/limit tại field, conflict, autosave, needs review, rubric coverage. Bản mẫu chỉ sau nộp. Worker panel queued/running/error/success. | Trình tự keyboard source→input→submit→summary. Paste thường hỗ trợ. Màn hẹp có anchor về nguồn. |
| UI-16 · `/videos`, `/videos/[lessonId]` | Catalog filter → mode picker → W04. Transcript, captions, seek, speed, quiz. | Versioned cues, visibility policy, poster/audio, chưa có mode thì giải thích. Trạng thái tải media, lỗi object và replay. | Transcript và player dùng nhãn riêng. Không tự phát, cue button có thời gian và text, keyboard nhập bình thường. |
| UI-17 · `/videos/[lessonId]?mode=dictation` hoặc run | W04 + exercise. Nghe/tốc độ/lặp → nhập → kết quả → câu tiếp. | Request chứa cue/version. Khi lỗi giữ input, chưa giải thì ẩn đáp án đúng, resume từ server. | Điều khiển ở trên ô nhập, không bắt cuộn hai panel cùng lúc. |
| UI-18 · `/pronunciation`, `/pronunciation/[soundId]` | Accent → IPA chart → phoneme detail → minh họa vị trí và minimal pairs → quiz. | Danh mục theo giọng, mẫu audio và mô tả, quiz version. Thiếu âm/mạng có fallback mô tả. | Nhóm IPA có heading, mỗi biểu tượng có accessible name và từ mẫu. |
| UI-19 · `/videos/[lessonId]?mode=shadowing` | Player/cue → nghe mẫu → bật mic khi chủ động → record/playback local → đánh dấu luyện. | Unsupported/denied/lost device, clip RAM, trạng thái thu rõ. Cleanup track khi thoát. | Nút mic có text, trạng thái live nhưng tránh nhắc từng khung. Màn hẹp giữ nút Dừng đủ lớn. |
| UI-20 · `/videos/[lessonId]?mode=quiz` | Player → radiogroup item hiện tại → nộp → phản hồi → tiếp tục/thử lại → receipt khi hoàn tất. | Tiến độ server theo điều kiện hoàn thành của item. Chưa chọn thì chặn nộp, thiếu quiz thì xem phụ đề. API lỗi giữ lựa chọn. | Fieldset/legend, sau nộp focus summary. Câu chưa trả lời không dựa chỉ vào màu. |

## Thiết lập, hỗ trợ và CMS

| ID và route | Mục tiêu, hierarchy, components và navigation | Data, tương tác và lỗi | Reflow và accessibility |
| --- | --- | --- | --- |
| UI-21 · `/settings` | Nhóm hồ sơ, preference, mục tiêu phút/ngày từ S4, phiên và quyền dữ liệu. Chọn Xuất hoặc Xóa → nhập lại mật khẩu (hiệu lực 10 phút) → xác nhận riêng cho Xóa → xem trạng thái job khi phiên còn hiệu lực. | Kiểm revision, quyền và IANA. Lỗi giữ form preference để so, mật khẩu hỗ trợ nhập lại. Khi export sẵn sàng hiển thị link riêng tư ngắn hạn. Khi erase có hiệu lực và phiên bị thu hồi, trả thông báo tối thiểu. | Focus lỗi đầu và trả focus sau dialog. Nút tải/xóa có nhãn riêng, tiến độ job có status text. Form một cột. |
| UI-22 · `/help` | FAQ mở rộng → form báo lỗi context (nếu đủ quyền) → receipt. | Type/text giới hạn, ticket ID, không tự gửi câu học/dữ liệu nhạy cảm, retry/rate limit. | Accordion button, confirmation status đọc được, label và enum rõ. |
| UI-23 · `/social` | V2 opt-in → phạm vi → tìm handle/đã kết nối/chờ → block/báo cáo. | Kiểm quyền và visibility server. Tìm kiếm giới hạn, state private và empty, disabled nếu cờ feature off. | Action có text và confirm cho thay đổi phạm vi. Mobile không ẩn nút quyền riêng tư. |
| UI-24 · `/cms`, `/cms/imports/[importId]` | Staff → Queue, Import staging → chọn file, xem tổng quan/lỗi dòng, tạo nháp hợp lệ. | Import schema, uploader, lỗi từng dòng, phân trang, job pending. Giữ report trên refresh. | Bảng lỗi có column headers và danh sách thay thế trên mobile, trạng thái tiến trình. |
| UI-25 · `/cms/lessons/[id]`, `/cms/review` | Draft editor → preview → request review → approve/request changes → publish confirmation. | Content/rights/published versions, edit version, role và differing reviewer. Mismatch giữ bản local và tóm tắt field xung đột. | Tabs đúng keyboard, modal xác nhận kèm version và tác động. Focus trả lại nút, button disabled có lý do khi không có quyền. |

**Biên QA giao diện** Chạy E2E từ demo đến lesson completion và một lượt review trên desktop cùng mobile. Chạy kiểm thử thủ công cho SR, IME, mic denied, phụ đề keyboard, popup từ link interop và zoom. Nếu có dữ liệu mẫu 0, 1, nhiều, lỗi quyền, mạng và version cũ, chụp bằng chứng ở route có UI ID. [Tiêu chí chấp nhận](../requirements/04-acceptance-criteria.md) · [Component inventory](04-component-inventory.md)
