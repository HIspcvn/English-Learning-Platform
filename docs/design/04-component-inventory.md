# Component inventory — React / Next.js

**Trạng thái** PROPOSED. Dùng App Router, Server Components cho khung/trang tải initial data khi có lợi. Client Components cho phần tương tác, audio, form, editor. UI primitives theo Tailwind và shadcn/ui cho các thành phần đã audit. TanStack Query quản lý cache dữ liệu người học và mutation replay. Zustand chỉ cân nhắc khi nhiều vùng cùng cần chia sẻ state giao diện cục bộ, ví dụ media clock. Progress, quyền, điểm, phiên bản và due lấy từ server.

| Component / owner | Data hoặc state | Props / boundaries | Kiểm tra |
| --- | --- | --- | --- |
| AppShell, NavigationRail, MobileNav · shell | Route, nguồn session đã lọc, quyền và phase flags | Nhận view model, handle responsive và focus, không phân quyền thay server | Skip link, current nav, Esc, 320 px |
| PublicShell, DemoPanel · marketing | Prompt public, mode demo | Thực thi policy demo riêng, CTA auth | Enter, blank, mobile |
| FormField, PasswordField, FieldErrorSummary · shared | Label, errors, describedBy | Field binding, auto-complete, submit state | Screen reader, lỗi và focus |
| RegistrationEmailForm, VerificationSetupForm · auth | Email, trạng thái đã gửi, link token, tên và mật khẩu | Register gửi email. Verify nhận tên/mật khẩu và chỉ hoàn thành sau xác minh token. | Email trùng, token hết hạn, replay, autofill |
| PageState, PendingIndicator, StatusBanner, ToastRegion · shared | Enum loading/empty/error/success, retry | Một live channel theo khu vực | Không spam trong typing |
| Button, IconButton, Dialog, Drawer, Popover, Tabs · shared | Các trạng thái primitive | Shadcn/Radix khi phù hợp, label cho icon | Keyboard, touch target, return focus |
| FiltersToolbar, EntityGrid, CursorPager · catalog | Search, filters, result count/cursor | Request scope theo keys, giữ URL filter hợp lệ | No matches, clear, nhanh đổi query |
| CourseMap, UnitList, LessonPreview · curriculum | Course, units, lesson status, availableVersion | Server view model, prop progress. Link đến lesson đủ quyền | Khóa, version withdrawn, empty CEFR |
| NextActionPanel, DailyGoalMeter, ActivityHistory · progress | Hôm nay, streak flag, bài tiếp, history | Read model. Meter có số tuyệt đối và nhãn | 0/goal, midnight, stale |
| ExerciseShell, ExercisePrompt, ExerciseStepper, RunSummary · learn | Pinned run, item, result | Điều phối renderer trực tiếp theo type/version. Render thông tin hoàn tất | Resume, completion, version mismatch |
| TypingInput, FeedbackDiff, HintControls · typing | Local input, IME, feedback server | Không chấm authoritative trong browser. Hint/reveal theo quyền server. Giữ input khi lỗi | composition, Enter, căn thiếu/thừa, retry |
| MediaPlayer, PlaybackControls, TranscriptCueList · media | Playback time, speeds, cues, activeCue | Time update throttled. Seek theo timestamp, highlight cue. Cleanup media | Seek, caption, lỗi object, mobile |
| VocabDeckCard, WordDetail, SaveWordControl · vocabulary | Deck, lexeme/sense, saved control | Tách save sense và enrollment theo chiều, invalidate đúng scope | Duplicate save, audio lỗi |
| Flashcard, ReviewRatingBar, ReviewQueueSummary · review | Card/due, flipped, version | Mặt sau có hành động rõ, rating sau flip, conflict reload | Keyboard, due inclusive, stale |
| GrammarArticle, QuestionForm, ExplanationBlock · grammar | Nội dung safe blocks, exercise/results | Renderer nội dung versioned, explanation sau submit | Dữ liệu lạ, retry, đọc bằng SR |
| DictionaryCombobox, SensePanel, PronunciationButtons · dictionary | Query, suggestions, lexeme | ARIA combobox, abort stale request, sense ID canonical | Enter/Esc, empty, multiword |
| ParallelText, WordAnnotation, ParagraphToolbar · reading | Passages, anchors, language | Toggle song ngữ giữ vị trí, popover tra/từ điển | lang, focus, offset, mobile |
| TranslationDraft, RubricResult, AttemptHistory · translation | Draft text, dirty/saved, result | Autosave định kỳ và blur, status read-only, source coverage | Reopen, quota, no authority client |
| VideoModePicker, DictationPanel, QuizPanel · videos | Mode, run, resources | Shared MediaPlayer, tách UI quiz/dictation, deep-link mode validate | Unavailable mode, aria radios |
| IpaChart, MinimalPairPicker, RecordingPanel · pronunciation | Accent, phoneme, local mic | Xử lý media lifecycle, local records V1, trạng thái quyền | Denial fallback, release mic |
| AiFeedbackStatus, ConsentPanel · AI | jobId, opt-in, queued/running/failed | Poll khi hiển thị với backoff, render validated result text | Timeout/cancel, budget cap, ownership |
| PreferenceForm, PrivacyControls, StepUpDialog, PrivacyJobStatus · settings | Preference revision, timezone, job status, step-up theo phiên | Field whitelist, xử lý conflict, xác thực lại 10 phút, xác nhận erase, link export riêng tư ngắn hạn | Timezone, locale, tab cũ, xác thực hết hạn, job người khác, link hết hạn |
| ContactReport, FaqList · help | Field states, receipt | Nội dung người học text escaped, stable receipt on replay | Rỗng, lỗi/throttled |
| AchievementGrid, SocialScopeForm · game/social | Ledger view, selection, invites | Opt-in. Controls chỉ phản ánh quyền server | Scope, block, duplicate |
| ImportReport, DraftEditor, PublishDialog, ReviewQueue · CMS | Import state, draft edit version, rights and reviewers | Server auth and CAS. Hiện preview draft nhãn rõ, validate lỗi theo dòng | Lost update, license, no self-review |

Tên component là proposal giao tiếp. Biên frontend feature đặt cạnh route/use case, không đưa UI riêng module vào shared chỉ vì có thể tái dùng. [Kiến trúc frontend](../architecture/02-frontend-architecture.md) · [Design system](01-design-system.md)
