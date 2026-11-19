# Đặc tả REST API

**PROPOSED.** Tất cả route ứng dụng dưới `/api/v1`. Route trong bảng là suffix. Hợp đồng này mô tả API của sản phẩm mới. Sử dụng OpenAPI 3.1, Pydantic discriminated unions và client types tạo từ schema khi Sprint 0 triển khai.

## Quy ước áp dụng cho từng dòng

- JSON UTF-8, timestamp RFC3339 UTC, local date YYYY-MM-DD, UUID canonical, CEFR A1/A2/B1/B2/C1/C2. Hậu tố `?` là optional/nullable theo schema cụ thể. Binary chỉ dùng object storage. Mặc định status 200, tạo 201, queued 202, không body 204. `list<T>` có `{items:T[],next_cursor:string|null}`.
- Quyền `P` công khai, `L` learner đã xác minh và có session, `E` editor, `R` reviewer, `A` admin. Mỗi endpoint quyền `L/E/R/A` mặc định 401 khi session sai, 403 khi role/Origin/CSRF sai; resource riêng không thuộc actor trả 404. Public auth mutation cũng kiểm Origin và guest CSRF token. Rate limit áp dụng 429 + `Retry-After`. `GET` an toàn và không ghi tiến độ. Response authenticated mặc định private, no-store.
- `Key` = header `Idempotency-Key` 16–128 ký tự token URL-safe, buộc với các command tạo trạng thái. SHA-256 từ method, resource IDs và canonical JSON trước khi mutation, key scope actor/operation. 409 `IDEMPOTENCY_CONFLICT` khi cùng key khác body. Replay yêu cầu quyền còn hợp lệ; receipt tối thiểu 7 ngày. `Set` là upsert/set semantics có guard revision nếu mô tả. `Read` có thể retry. Endpoint auth dùng token một lần hoặc rate limiting theo hàng, không cache response phát credential.
- `Cursor`: `limit` mặc định 20 và 1–100, cursor opaque chứa sort key + record ID + filter scope, check scope/signature, 422 nếu sai. SRS dùng ngày giờ snapshot cố định trong cursor để ổn định trang. Search bounded, không full scan bằng wildcard không kiểm soát. Endpoint detail không phân trang trừ nested collection có khai báo.
- Input sai kiểu/range hoặc thiếu trường trả 422 `VALIDATION_ERROR`. 409 cho revision stale/current item sai/state conflict; 423 khi prerequisite đóng; 404 khi missing/unpublished; 413 cho size; 503 với retry khi dependency tạm thời. Error envelope `{type,title,status,detail,instance,code,request_id,errors?:[{field,code,message}]}` làm `application/problem+json`. Các dòng chỉ ghi thêm các lỗi nghiệp vụ cụ thể. Update destructive hoặc quyền cao sinh audit. Negative path test bao phủ common error theo mỗi route.
- View cơ bản: `UserView{id,display_name,locale,timezone,roles[],verified,onboarding_completed}`; `LessonRef{id,slug,title,kind,cefr,version_id,locked,lock_reason?}`; `RunView`, `Feedback`, `CardView`, `JobView` chi tiết bên dưới. Input giới hạn max cho str/array ở từng DTO, từ chối unknown fields trong command. Nội dung do CMS hoặc provider gửi vẫn được validate.
- Proxy bảo toàn `X-Request-Id`, không expose token. `X-CSRF-Token` lấy từ GET auth/session private; session cookie có HttpOnly. Truy vấn public cache theo publication version. ETag chỉ dùng representation công khai hoặc tài nguyên có projection phù hợp.

## Identity và tài khoản — FR-AUTH-001, FR-SET-001

| Method và endpoint | Quyền | Request → Response | Xử lý / DB / lỗi | Idempotency, page, test |
| --- | --- | --- | --- | --- |
| GET `/auth/session` | P | ∅ → `{user:UserView\|null,csrf_token}` | Auth session digest/expiry; người chưa đăng nhập nhận guest CSRF. Cache no-store. | Read. Anonymous, expired cookie, token masking. |
| POST `/auth/register` | P | `{email}` → 202 `{accepted:true}` | Email ≤254. Create pending user chưa có hash, lock theo email unique; phát proof/outbox job mã hóa trong cùng txn. Existing account trả response chung, giữ nguyên profile/hash. | Rate/unique. Existing active và duplicate race không đổi credential, malformed. |
| POST `/auth/verification/resend` | P | `{email}` → 202 `{accepted:true}` | Gửi token mới cho pending user theo cooldown email/IP; supersede token cũ dưới user lock và ghi mail job/ciphertext cùng txn. Response chung, giữ nguyên credential/profile. | Rate. Pending resend, cooldown, old token rejected. |
| POST `/auth/verify` | P | `{token,password,display_name}` → 204 | Name 1–80, password 12–128. Chỉ latest proof đúng digest, pending và còn hạn; atomically consume, lưu Argon2id hash, tạo profile và activate. 410 hết hạn/đã dùng/bị thay thế, không tạo session. | One-use. Race, replay, superseded token, verify fail rollback. |
| POST `/auth/login` | P | `{email,password}` → `{user,csrf_token}` + cookie | Argon2id, rate-limit email+IP; rotate session. 401 credentials hoặc account unavailable theo policy, tránh enumeration. | Rotate. Wrong/valid/CSRF/cookie. |
| POST `/auth/reauth` | L | `{password}` → `{valid_until}` | Verify password + rate limit, đặt auth_sessions.reauthenticated_at theo server clock cho session hiện tại. 401 REAUTH_FAILED nếu mật khẩu sai, giữ phiên hiện tại và không ghi reauthenticated_at. CSRF như mutation learner. | Set. 10 phút, scope đúng session, không kéo dài phiên. |
| POST `/auth/logout` | P | ∅ → 204 + clear cookie | Nếu session tồn tại, authorize rồi revoke; nếu vắng, trả cùng response. CSRF nếu cookie hợp lệ. | Set. Logout twice, cookie replay. |
| POST `/auth/password/forgot` | P | `{email}` → 202 `{accepted:true}` | Ghi digest, supersede reset proof cũ và queue email ciphertext cùng txn nếu account active, response chung. | Rate. Existing/missing same contract. |
| POST `/auth/password/reset` | P | `{token,password}` → 204 | Verify digest, đổi hash, revoke all sessions trong một txn. 410 expired/spent. | One-use. Concurrent reset, session revoked. |
| GET `/me/profile` | L | ∅ → `{display_name,avatar_asset_id?,bio?}` | Read user_profiles theo session. | Read. Owner-only and missing optional. |
| PATCH `/me/profile` | L | `{display_name?,avatar_asset_id?,bio?}` → profile | Validate field allowlist, asset owned/ready, bio ≤500, empty patch 422. | Set. Foreign asset, XSS text. |
| GET `/me/preferences` | L | ∅ → `{locale,timezone,current_cefr,target_kind?,target_code?,exam_date?,default_accent,ai_opt_in,social_opt_in,onboarding_completed_at?,revision}` | Read preferences; onboarding dùng cùng resource. | Read. Defaults and onboarding. |
| PUT `/me/preferences` | L | Pref đầy đủ + `expected_revision` → prefs | Check IANA zone, locale vi/en (mặc định vi), CEFR và mục tiêu thi tùy chọn; Sprint 1 onboarding chỉ hỏi các trường này. Accent AI/social áp theo giai đoạn, mục tiêu thời gian ở endpoint riêng từ Sprint 4. CAS; server set onboarding_completed_at khi lưu đủ lần đầu. 409 stale. Timezone tương lai, opt-out hủy jobs chưa chạy khi khả thi. | Key. Double retry/CAS, change zone. |
| POST `/me/privacy-requests` | L | `{kind:"export"\|"erase"}` → 202 `{job_id,kind,status,requested_at}` | Yêu cầu reauth còn hạn 10 phút trên current session cho cả hai loại; 403 REAUTH_REQUIRED nếu thiếu/hết hạn. Erase cần xác nhận UI rõ ràng. Kiểm fresh trước idempotency lookup, ghi owner-linked privacy_requests và job cùng txn, một job queued/running mỗi owner/kind, audit + retention; revoke toàn bộ session khi worker thực thi erase. | Key. Cả hai loại không qua nếu reauth hết hạn; replay/retry nhất quán. |
| GET `/me/privacy-requests/{job_id}` | L | ∅ → `{job_id,kind,status,requested_at,finished_at?,download_available,error_code?}` | Tìm request qua privacy_requests.user_id và active session; trả trạng thái tối thiểu, không đưa file hay signed URL vào response. | Read. Foreign ID 404, session bị revoke 401, queued/completed/failed. |
| GET `/me/privacy-requests/{job_id}/download` | L | ∅ → 303 với `Location` là URL tải ký ngắn hạn | Chỉ owner export ready, asset private còn TTL; 409 chưa ready, 410 hết hạn, 404 foreign hoặc loại erase. Cache no-store; scrub URL trong logs. | Read. Owner, short expiry, foreign no data, revoke/erasure. |

## Public, curriculum, grammar và reading — FR-LAND-001, FR-CUR-001, FR-GRAM-001, FR-READ-001

| Endpoint | Quyền | Request → Response | Xử lý / DB / lỗi | Idempotency, page, test |
| --- | --- | --- | --- | --- |
| GET `/public/demo` | P | ∅ → `{version,prompts:[DemoPrompt]}` | Snapshot mẫu original, checksum. Chấm demo cục bộ bằng answers đã phát cùng demo. Không lưu attempt. | Read. Public payload only; no auth read. |
| GET `/curriculum/courses` | L | `cefr?,cursor?,limit?` → `list<CourseRef{id,slug,title,cefr}>` | active/published, order cefr,sort,id. | Read Cursor. Level filter, archived invisible. |
| GET `/curriculum/courses/{course_id}` | L | `cursor?,limit?` → `{course,units:list<UnitView{id,title,position,lessons:LessonRef[]}>}` | Load units cho course; bound số lessons/unit ở CMS. Annotate recommendation/required qua progress. | Read Cursor. Same-record sort, lock/preq. |
| GET `/lessons` | L | `kind?,cefr?,unit_id?,cursor?,limit?` → `list<LessonRef>` | `kind` allowed typing/grammar/reading/translation/video/dictation/ipa/shadowing; published pointer join. | Read Cursor. Kind filter, draft leakage. |
| GET `/lessons/{lesson_id}` | L | ∅ → `LessonRef & {objective,estimate_seconds?,modes[],typing_variants?:TypingVariantView[],active_runs:ActiveRunRef[],body:LessonPublicBody}` | Version current, body union: intro/exercise counts, grammar blocks, reading paragraphs hoặc media IDs. Với typing, variants tách mode/difficulty và chỉ liệt kê lane đã bật, đủ điều kiện nội dung. active_runs chỉ ID/lane của owner, gồm cả run đã pin bản cũ còn quyền. Zero private answer keys, locked detail policy. | Read. Lookup variant progress, filter revoked runs, answer excluded. |

## Lesson runs, điểm và tiến độ — FR-TYPE-001, FR-PROG-001, FR-GRAM-001, FR-READ-001, FR-TRANS-001, FR-DICTATION-001, FR-IPA-001, FR-SHADOW-001

### Schema trọng tâm

| Schema | Trường và bất biến |
| --- | --- |
| `StartRun` | `{lesson_id,mode,difficulty?,intent?}`. Với typing, gửi difficulty và mode `default/listen/listen_speak`; intent là `resume/replay`, mặc định resume. Với loại khác, giữ mode của loại đó và không gửi hai trường typing. Server chọn/pin version. |
| `TypingVariantView` | `{mode,difficulty,required_count,active_run_id?,completed_run_id?,mastered:boolean\|null}` cho current version. Difficulty enum `basic/intermediate/advanced`. Mastered tổng hợp từ lane/version đó, null nếu không chấm. `ActiveRunRef{id,lesson_version_id,mode,difficulty:Difficulty\|null}`. |
| `RunView` | `{id,lesson_id,lesson_version_id,mode,difficulty:Difficulty\|null,status,revision,current_item:RunItemView\|null,position,total,terminal_count,resumed,completion?:CompletionReceipt}`. `RunItemView{id,kind,prompt,audio_asset_id?,hint_remaining,can_reveal,attempt_count}`. Chỉ gửi projection của mode; listen/listen_speak không gửi transcript và bản dịch khi đang làm item. |
| `SubmitAttempt` | `{item_id,expected_revision,answer}` với `item_id` là run item ID. Union `{kind:"text",text}` (typing ≤1000 Unicode code points, translation ≤1000 theo pilot), `{kind:"choice",option_id}`, `{kind:"translation_segments",responses:[{segment_id,text}]}` (≤32 segment, ≤1000 tổng code points), `{kind:"practice_ack"}` cho IPA/shadowing và typing listen_speak V1. Server chọn loại đáp án theo lane. Không nhận recording, điểm hoặc expected_text cho listen_speak V1. Control/blank sau normalize ⇒ 422, không ghi. |
| `Feedback` | `{attempt_id,item_id,outcome,passed:boolean\|null,score:number\|null,alignment?:[{op,expected_index?,actual_index?,actual_token?,expected_token?}],ref_disclosed,assisted,explanation?,coverage?:number,can_retry,grading_version}`. `outcome` enum `pass/fail/needs_review/unscored`. Missing/incorrect ref text redacted nếu chưa được reveal; feedback khi pass có thể hiện reference. |
| `HintCommand` | `{item_id,expected_revision,kind:"nudge"\|"reveal"}` → `{hint:{kind,text},run:RunView}`. Nudge hợp lệ đặt assisted và giữ cursor. Reveal typing graded chỉ sau ≥2 lần sai hợp lệ của item; terminal revealed, advance và đánh dấu assisted, không tạo attempt. Typing listen_speak dùng practice_ack, không dùng hai lệnh hint. |
| `TypingMetrics` | `{required_count,graded_count,first_attempt_correct_count,first_attempt_accuracy:number\|null,passed_count,revealed_count,acknowledged_count,terminal_score:number\|null,mastered:boolean\|null}`. Tỷ lệ dựa trên toàn bộ graded_count bắt buộc, làm tròn 2 chữ số, speech có 0 graded và ba trường nullable là null. |
| `CompletionReceipt` | `{run_id,status:"completed",score:number\|null,assisted_count,study_date,completed_at,progress:{first_completed_at,best_score,completed_runs},typing_metrics?:TypingMetrics,reward?:{eligible:boolean,xp_delta:0\|10},vocabulary?:{new_saved_count}}`. Typing trả typing_metrics, top-level score bằng terminal_score cùng reward, kể cả speech (false/0). Vocabulary chỉ có từ Sprint 05 đối với graded completion. Hồ sơ immutable, backfill kho từ không bổ sung trường vào receipt cũ. |
| `ProgressView` | `{timezone,today:{study_date,goal_minutes,active_seconds,completed_lessons,reviewed_cards,xp},recommended:LessonRef\|null,totals:{completed_lessons,reviews,xp},items:list<LessonProgressView>,gamification?}`. completed_lessons là lesson distinct trong phạm vi; completed_runs riêng ở lịch sử/receipt. XP riêng tư từ Sprint 04, không đòi leaderboard hoặc streak. |
| `StudySessionView` | `{id,run_id?,started_at,last_signal_at,ended_at?,active_seconds}`. Signal có monotonic sequence theo session nếu cần; server clamp theo `now`, không tin thời gian client. |

### Contract

| Endpoint | Quyền | Request → Response | Xử lý / DB / lỗi | Idempotency, page, test |
| --- | --- | --- | --- | --- |
| POST `/lesson-runs` | L | StartRun → 201 create hoặc 200 RunView có sẵn | Check current version, prerequisite 423, variant ngoài matrix/phase/content 422 `TYPING_VARIANT_UNAVAILABLE`. Serialize start theo user/lesson/version/mode/difficulty và unique active. Typing resume lấy active hoặc completed mới nhất cùng khóa, tạo mới khi chưa có cả hai. Replay chỉ tạo sau khi có completed cùng khóa và không còn active; 409 `ACTIVE_RUN_EXISTS` hoặc `REPLAY_REQUIRES_COMPLETION`. Non-typing tiếp tục active hoặc tạo như cũ. Materialize ordinal rõ ràng và bất biến. | Key. Active cùng lane không trùng kể cả difficulty null; khác lane độc lập; replay không hủy run. |
| GET `/lesson-runs/{run_id}` | L | ∅ → RunView | Ownership, dùng version/variant đã pin dù current pointer đổi. Completed trả completion snapshot và current_item null. Active pin bị thu hồi quyền trả 410 `LESSON_VERSION_REVOKED`; history đọc được điểm đã tổng hợp mà không trả nội dung đã thu hồi. | Read. Owner, reload pinned older version, same cursor, no expected reference leakage. |
| POST `/lesson-runs/{run_id}/attempts` | L | SubmitAttempt → 201 `{feedback,run}` | Lock run/item, compare revision/current/mode, grade snapshot/policy, ghi assisted từ item tại lần nộp, update cursor/revision trong transaction. Typing fail giữ cursor, pass advance. Speech self_ack terminal, unscored và advance. `needs_review` giữ chính sách hiện có cho dịch. 409 stale/item mismatch/not active, 410 active version bị thu hồi. | Key. Blank, normalization, wrong/missing/extra, nudge race và concurrent keys. |
| GET `/lesson-runs/{run_id}/items/{item_id}/draft` | L | ∅ → `{answer?,draft_revision}` | Owned active translation item, blank when absent or expired. | Read. Cross-run/item, expiry. |
| PUT `/lesson-runs/{run_id}/items/{item_id}/draft` | L | `{answer,expected_draft_revision}` → `{draft_revision,expires_at}` | Validate same answer shape with blank optionally allowed; CAS independent draft revision, no grade, bounded TTL. 409 stale/item terminal. | Set with CAS. Two tabs, timeout refetch, no attempt. |
| GET `/me/translation-attempts` | L | `direction?,cursor?,limit?` → `list<{run_id,attempt_id,lesson_version_id,direction,submitted_at,outcome,score?}>` | Read own attempts for translation types, stable cursor by submitted_at/id; load feedback by attempt path. | Read Cursor. Direction filter, old version, owner scope. |
| POST `/lesson-runs/{run_id}/hints` | L | HintCommand → hint and RunView | Lock run/item, enforce cap/cursor/lane. 409 khi revision cũ, hint không đủ điều kiện hoặc mode không hỗ trợ. 410 với active version bị thu hồi. Ở graded typing reveal là terminal, nudge giữ item hiện tại. | Key. Replay giữ bộ đếm, khóa nhánh không hỗ trợ, kiểm tra quyền trước khi hiện đáp án. |
| GET `/lesson-runs/{run_id}/attempts/{attempt_id}/feedback` | L | ∅ → Feedback | Read persisted result, verify attempt belongs to run/user; historical redaction rule identical to submission snapshot. | Read. Reload final feedback, wrong nested ID. |
| POST `/lesson-runs/{run_id}/complete` | L | `{expected_revision}` → CompletionReceipt | Lock run, validate required terminal theo lane, 409 incomplete/stale, 410 active version bị thu hồi. Completed trả immutable snapshot cả khi key mới, sau kiểm owner/quyền. Atomic receipt, lesson history, daily distinct, 10 XP first qualifying và từ Sprint 05 insert kho từ khi eligible. Không enroll SRS. | Key. Completion race same/different keys/lanes, local day, ledger rollback, tombstone và new_saved_count. |
| GET `/me/progress` | L | `from?,to?,cursor?,limit?` → ProgressView | Date bounds ≤366 days, same scope summary; index date/progress. Recommended computed by ordered published candidates. | Read Cursor. Empty, private/no-store, post-completion read. |
| PUT `/me/daily-goal` | L | `{minutes}` 5–180 → `{minutes,effective_local_date}` | Lock user/day; effective date server chooses from IANA timezone. No retroactive activity edits. | Key. Concurrent same day, DST. |
| POST `/study-sessions` | L | `{run_id?}` → 201 StudySessionView | Run ownership/mode, start explicit when learner engages. Reuse same active session for same run, otherwise 409 active session; stale idle session expires under same transaction. | Key. Foreign run, duplicate, timeout. |
| POST `/study-sessions/{id}/signals` | L | `{kind:"active"\|"pause"\|"finish"}` → StudySessionView | Lock row, clamp elapsed, reject ended except duplicate finish, split cross-day time locally. | Key. Double heartbeat, background tabs, DST, finish after pause. |

## Dictionary, từ vựng và SRS — FR-VOCAB-001, FR-SRS-001, FR-DICT-001

| Schema | Trường |
| --- | --- |
| `EntryView` | `{id,lemma,pos,ipa_uk?,ipa_us?,audio_uk_id?,audio_us_id?,senses:[{id,definition_en?,gloss_vi,examples,cefr?}],attribution}` |
| `CardView` | `{id,meaning_id,direction,state,due_at,revision,prompt}`; hint/answer tự reveal qua Detail khi ứng dụng flashcard hoặc kèm DTO nếu UX tự chấm, không dùng làm điểm proficiency. |
| `ReviewCommand` | `{rating:"again"\|"hard"\|"good"\|"easy",expected_revision}`; server review time. |
| `ReviewReceipt` | `{review_id,card:CardView,previous_due_at,due_at,reviewed_at,algorithm_version,repeat_in_session:boolean}`. |

| Endpoint | Quyền | Request → Response | Xử lý / DB / lỗi | Idempotency, page, test |
| --- | --- | --- | --- | --- |
| GET `/dictionary/entries` | L | `q` 1–80, `cursor?,limit?` → `list<EntrySummary{id,lemma,pos,gloss_vi?,ipa_uk?,ipa_us?}>` | Normalize case/whitespace; exact rồi prefix, tối đa result; query bound/escaped. No-match 200 empty. | Read Cursor. Phrase, prefix, unknown, injection plain text. |
| GET `/dictionary/entries/{entry_id}` | L | ∅ → EntryView | Published entry+senses, attribution, optional assets. | Read. Missing IPA/accent and revoked article. |
| GET `/vocabulary/decks` | L | `scope?,cefr?,cursor?,limit?` → `list<DeckView{id,title,scope,cefr?,word_count}>` | Published or owned; no private leaks. | Read Cursor. Deck membership and counts. |
| POST `/vocabulary/decks` | L | `{title}` 1–100 → 201 DeckView | Create personal deck, server slug normalized; 409 on name collision under owner. | Key. Duplicate/foreign collisions. |
| GET `/vocabulary/decks/{id}` | L | `cursor?,limit?` → `{deck,entries:list<EntrySummary>}` | Read owned/public deck, join meanings and entries. | Read Cursor. Private not visible and empty deck. |
| PUT `/vocabulary/decks/{id}/entries/{meaning_id}` | L | ∅ → 204 | Owner private, UQ member and safe position under row lock; 403 public mutation. | Set. Concurrent add/duplicate. |
| DELETE `/vocabulary/decks/{id}/entries/{meaning_id}` | L | ∅ → 204 | Owner private, detach only. | Set. Repeat no loss of SRS. |
| GET `/vocabulary/saved` | L | `cursor?,limit?` → `list<{meaning_id,saved_at,source,entry:EntrySummary}>` | Owner, chỉ marker chưa bị bỏ và nghĩa còn khả dụng, sort saved_at/meaning_id. | Read Cursor. Stable page, auto-save, empty và tombstone. |
| PUT `/vocabulary/saved/{meaning_id}` | L | ∅ → 204 | Save nghĩa khả dụng, restore tombstone khi learner chủ động lưu. Marker active có sẵn không đổi. Enrollment riêng. | Set. Same sense from typing/dictionary dedup. |
| DELETE `/vocabulary/saved/{meaning_id}` | L | ∅ → 204 | Set tombstone cho mục đã lưu hoặc nghĩa khả dụng mà learner vừa xóa. Các completion sau và backfill không hồi sinh. Giữ review logs/cards. | Set. Race với auto-save, repeat, scheduled card stays. |
| POST `/srs/cards` | L | `{meaning_id,direction}` → 201/200 CardView | Kiểm sense khả dụng từ kho hoặc catalog. Chỉ thao tác enroll tường minh mới upsert theo user/sense/direction, initial due now khi tạo, lịch cũ giữ nguyên. | Key. Same sense across decks, alternate direction. |
| GET `/srs/due` | L | `cursor?,limit?` → `{as_of,due_count,next_due_at?,cards:list<CardView>}` | Rows states not suspended and due_at≤as_of, order due_at,id. Token includes as_of; counts can fluctuate post-mutation. | Read Cursor. Boundary exact instant, other learner excluded, empty. |
| POST `/srs/cards/{card_id}/reviews` | L | ReviewCommand → 201 ReviewReceipt | Lock card/revision, rate, state, due eligibility per engine, append log, update schedule and progress once. 409 suspended/stale/early. | Key. Race, bad rating, due after repeat, replay same receipt. |
| GET `/srs/cards/{card_id}/reviews` | L | `cursor?,limit?` → `list<ReviewReceipt>` | Historical snapshots from immutable log. | Read Cursor. History ownership and order. |

## Video, media, AI và trợ giúp — FR-VIDEO-001, FR-IPA-001, FR-SHADOW-001, FR-AI-001, FR-HELP-001, FR-GAME-001, FR-SOC-001

| Endpoint | Quyền | Request → Response | Xử lý / DB / lỗi | Idempotency, page, test |
| --- | --- | --- | --- | --- |
| GET `/videos/{lesson_id}/transcript` | L | `version_id?,lang?,cursor?,limit?` → `{version_id,available_langs,duration_ms,cues:list<TranscriptCue>}` | `TranscriptCue{id,start_ms,end_ms,track_lang,text,pair_key?}`. `version_id` current or owned pinned run; sort time/position/id. Missing optional track ⇒ empty with available languages. 404 if not video/published. | Read Cursor. Track fallback, cue boundaries, missing old version. |
| GET `/media/assets/{asset_id}/playback` | L | `run_id?` → `{url,expires_at,mime_type,duration_ms?}` | Sprint 03 dùng cho prompt audio. Confirm access from published version/current reference, explicit owned pinned run, or own recording nếu phase cho phép. Short-lived URL; purpose and revoked check. | Read. Expiry, ownership, range, revoked. |
| POST `/media/assets` | E or L for allowed recording | `{purpose,mime_type,bytes,sha256}` → 201 `{asset_id}` | Reserve generated object key; role/purpose cap, only allowed mime/sizes, recording needs consent where AI upload. | Key. Wrong MIME, huge, foreign. |
| POST `/media/assets/{asset_id}/upload-url` | owner or E admin by policy | ∅ → `{url,headers,expires_at}` | Only pending owner or authorized editorial, bound method/key and type. Renew no new row. | Read semantics, POST for privacy. Expired, scoped prefix. |
| POST `/media/assets/{asset_id}/finalize` | owner or authorized E | ∅ → 202 JobView | Stat object and queue one validation job, checksum/sniff/scan/metadata pipeline. 409 missing or wrong state. | Key. Missing, duplicate, scanner reject, Worker retry. |
| POST `/ai/feedback` | L consent | `{kind,attempt_id?,asset_id?}` → 202 `{feedback_id,status}` | Check ownership, policy, lesson and allowed media; reserve quota + job, 403 opt-out/429 budget. | Key. Dedup, cost bound, absent consent, foreign data. |
| POST `/ai/feedback/{feedback_id}/cancel` | L | ∅ → `{id,status}` | Enforce ownership, cancel queued job atomically and release quota. Running job returns 409 if provider call is committed; opt-out stops further sends. | Key. Race with worker claim, quota ledger, foreign job. |
| GET `/ai/feedback/{feedback_id}` | L | ∅ → `{id,status,result?,error_code?,expires_at}` | Query owned request, scrub result and enforce expiry. 410 expired. | Read. Pending/failed/succeeded, output schema. |
| GET `/me/gamification/xp` | L V2 | `cursor?,limit?` → `list<{source_type,amount,earned_at,study_date}>` | Summarize owned ledger in reverse chronological order. | Read Cursor. Duplicate reward prevention and negative correction. |
| GET `/me/gamification` | L V2 | ∅ → `{xp,streak:{current_days,longest_days},achievements:[{code,earned_at}]}` | Read ledger/projection, output badge statuses. | Read. Midnight and dedup. |
| POST `/help/feedback` | L | `{category,message,lesson_version_id?,item_id?}` 1–2000 → 201 `{id,status}` | Save sanitized plain text with quota. Optional lesson version published or owned pinned version; optional item belongs owned run with matching version. No implicit attachments or answer payloads. | Key. Bound, throttled, no external disclosure. |
| GET `/help/feedback/{id}` | L | ∅ → `{id,status,created_at}` | Owner receipt, omit internal assignment. | Read. Foreign ticket absent. |
| GET `/cms/support-feedback` | A | `status?,cursor?,limit?` → `list<{id,category,status,lesson_version_id?,assignee_id?,revision}>` | Admin triage; privacy scope and access audit. | Read Cursor. Role denial, minimized DTO. |
| PATCH `/cms/support-feedback/{id}` | A | `{status,assignee_id?,expected_revision}` → `{id,status,revision}` | Admin recipients only, valid transition and status revision; record audit. | Key. Assignment conflict and unauthorized actor. |
| GET `/social/discover` | L optional | `handle` → `{peer_handle,peer_display}` | Owner and peer both opt in, exact handle match/scope and request throttle. No searchable email. | Read. Privacy unlisted and blocked. |
| GET `/social/friendships` | L optional | `status?,cursor?,limit?` → `list<{id,peer_display,status,shared_progress?}>` | Owner pair, shared progress only accepted and consented. Admin moderation separate. `id` can be opaque signed pair key over canonical IDs. | Read Cursor. Hidden email, blocked user. |
| POST `/social/friendships` | L optional | `{peer_handle}` → 201/200 `{id,status}` | Explicit opt-in, stable handle search limit, canonical unique pair; anti-harassment before launch. | Key. Self/inverse race/blocked. |
| PATCH `/social/friendships/{id}` | L optional | `{action:"accept"\|"decline"\|"disconnect"\|"block"}` → `{id,status}` | Verify role in pair, recipient-only accept, owner block with suppression. 409 invalid transition. | Key. Foreign interaction, duplicate. |

## CMS — FR-CMS-001

### Editorial DTO

`VersionCommand` has `{schema_version,title,cefr,learning_objective,estimated_seconds?,content,exercises,source_and_license:{source_manifest_id,source_keys[]}}`. Typing content khai báo `typing_variants:[{mode,difficulty}]`. Exercise typing liên kết `vocabulary_target_meaning_ids[]` đã resolve trong catalog. Review/publish kiểm matrix, prompt, audio/asset rights, sequence không rỗng và sense id trước khi đóng băng; draft có thể nhận validation report cho trường chưa đủ. VersionView adds `{id,lesson_id,version_no,status,revision,checksum,review?}`; audit view redacts PII. `JobView{id,status:"queued"|"running"|"succeeded"|"failed",next_poll_after?,result?,error_code?}`. ImportReport `{import_id,rows_total,error_total,warning_total,errors:list<{row,field,code,message}>}`.

| Endpoint | Quyền | Request → Response | Xử lý / DB / lỗi | Idempotency, page, test |
| --- | --- | --- | --- | --- |
| POST `/cms/source-manifests` | E/A | `{package_key,source_release,records,evidence_uri?}` → 201 `{id,manifest_sha256,approved_at:null}` | Validate required source/license proof and typed records; immutable once approved. Server canonicalizes and hashes manifest. | Key. Unapproved source, repeated release and changed digest. |
| POST `/cms/source-manifests/{id}/approve` | A | `{expected_sha256}` → `{id,approved_at}` | Check source evidence and checksums, audit issuer. 409 stale hash. | Key. Actor role and hash race. |
| POST `/cms/courses` | E/A | `{slug,title,cefr,sort_order}` → 201 CourseRef | Slug regex 1–80 lowercase ASCII hyphen, UQ, archive via editorial operation. | Key. Duplicate slug, invalid CEFR. |
| POST `/cms/courses/{course_id}/units` | E/A | `{slug,title,position}` → 201 UnitView | Course exists and editable, unique sequence/slug. | Key. Conflicting positions. |
| POST `/cms/units/{unit_id}/lessons` | E/A | `{slug,kind,position}` → 201 `{lesson_id}` | Validate taxonomy/unit scope/uniqueness; unpublished staging. | Key. Non-editor, missing unit. |
| GET `/cms/lessons` | E/R/A | `status?,q?,cursor?,limit?` → `list<{lesson_id,current_version_id?,latest_draft?}>` | Role and assignment policy, issues summary. | Read Cursor. Draft only to staff. |
| POST `/cms/lessons/{lesson_id}/versions` | E/A | VersionCommand → 201 VersionView | Lock lesson/version sequence, validate structural shape/draft permissions. | Key. Concurrent numbering, missing fields draft. |
| GET `/cms/lessons/{lesson_id}/versions/{version_id}` | E/R/A | ∅ → VersionView | Verify version belongs lesson and authorized. Answer key staff only. | Read. Cross-lesson 404, learner 403. |
| PUT `/cms/lessons/{lesson_id}/versions/{version_id}` | E/A | VersionCommand + `expected_revision` → VersionView | Draft only; CAS, content checksum. 409 locked/stale. | Key. Published immutable, editor concurrency. |
| POST `/cms/lessons/{lesson_id}/versions/{version_id}/submit-review` | E/A | `{expected_revision}` → VersionView | Immutable review snapshot, schema/content/license and media checks; state in_review. 422 validation details. | Key. Missing rights, invalid refs, stale. |
| POST `/cms/lessons/{lesson_id}/versions/{version_id}/decisions` | R/A | `{decision:"approve"\|"reject",notes?,expected_revision}` → VersionView | Reviewer distinct from author, append content_reviews + audit, approve/reject transition. | Key. Self-review 403, stale approval. |
| POST `/cms/lessons/{lesson_id}/versions/{version_id}/publish` | A | `{expected_revision,expected_current_version_id}` → `{lesson_id,version_id,checksum,published_at}` | Validate approved exact rev, license/media/DAG/readiness; lock lesson then version; commit status pointer and audit/outbox; publish target course upon first approved lesson publication. 409 stale/head changed, 422 invalid. | Key. Concurrent publishers, repeat same receipt, in-flight old run. |
| POST `/cms/imports` | E/A | `{asset_id,schema_version,package_key,source_release,source_manifest_id}` → 202 `{import_id,job_id,status}` | Owner staged CSV/JSON under size bound; provenance manifest required and identity checked. Dedup same package/release/SHA; 409 same pair different SHA. Queue validation only. | Key. Unsupported schema, malware fail, retry. |
| GET `/cms/imports/{id}` | E/A | `cursor?,limit?` → ImportReport + status | Staff owner/allowed, row errors paginated by row/code, raw inputs redacted. | Read Cursor. CSV bad encoding, report stable. |
| POST `/cms/imports/{id}/apply` | E/A | `{expected_checksum}` → 202 JobView | Verified report no blocking errors; lock import; create drafts atomically by approved batch policy. 409 already changed. | Key. Duplicate IDs, all-or-nothing, no auto publish. |
| POST `/cms/lessons/{lesson_id}/restore-version` | A | `{version_id,expected_current_version_id}` → `{lesson_id,version_id,restored_at}` | Require previously published version and still valid rights/media; lock current pointer; audit/revalidate. 409 mismatched current. | Key. Restore pointer and retain existing run. |
| POST `/cms/lessons/{lesson_id}/versions/{version_id}/revoke-access` | A | `{reason_code,expected_current_version_id}` → `{version_id,blocked_at,current_version_id?}` | Record access block, replace current pointer with eligible published version or null; freeze learning input when pinned item revoked. Audit and asset URL scope. | Key. Pinned access disabled, history retained, competing pointer conflict. |
| GET `/cms/audit` | A/R according to scope | `target_kind?,target_id?,cursor?,limit?` → `list<AuditEntry>` | Sort time/id, audit viewing by admin when necessary, never token/secret dump. | Read Cursor. Filters, actor privacy, access. |

## Bảng truy vết contract

- Run start/attempt/hint/feedback/completion → FR-TYPE-001, [engine](06-exercise-engines.md), `lesson_runs/run_items/exercise_attempts/lesson_completions`.
- Due/review/history → FR-SRS-001, `srs_cards/srs_review_logs`, persistent revision trước review và UTC.
- Progress/session/goal → FR-PROG-001, daily activity, completion transaction, forecast/read policy.
- Dict and vocabulary save → FR-DICT-001/FR-VOCAB-001, normalized lookup and unique user/sense.
- Video transcript → FR-VIDEO-001, `video_lessons/transcript_cues`, cue track versions.
- CMS publish → FR-CMS-001, `lesson_versions/lessons/content_reviews`, version immutable, audit/outbox.
- Routes added beyond MVP remain tagged in roadmap. Integration/e2e/performance gates [test cases](../testing/02-test-cases.md).

## Ví dụ ngắn cho typing

```json
{
  "item_id": "72fa77f5-eab6-4f30-bdd1-30fa78f82bcf",
  "expected_revision": 3,
  "answer": {"kind": "text", "text": "I carry a small bag."}
}
```

Kết quả khi sai có `passed:false`, `score`, danh sách alignment theo thứ tự và `run.revision=4` cho lần thử tiếp. Cùng key/body trả đúng attempt cũ. Đây là response contract, các trường grade chi tiết và thuật toán ở [Exercise engines](06-exercise-engines.md).

