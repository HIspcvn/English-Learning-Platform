# Đặc tả bộ máy bài tập

**PROPOSED.** Các chính sách dưới đây là hợp đồng sản phẩm mới. Khảo sát gõ câu và flashcard cho biết các hành vi mà người học nhìn thấy; thuật toán gốc của AIO English chưa được xác minh. Xem [SRS](../requirements/02-SRS.md), [run API](05-api-specification.md) và [test cases](../testing/02-test-cases.md).

## Nền tảng dùng chung

`ExerciseSpec(version,exercise_id,kind,prompt,policy,private_grader_config)` được pin bằng lesson version. `RunItem(item_id,ordinal,revision,counters,status)` nhận đáp án từ learner đang ở cursor. Pure engine nhận revision nội dung, answer DTO và scoring config. Trả `Grade(outcome,passed?,score?,feedback,grading_version)`; `null` cho trường hợp không có điểm xác định. Service giữ ownership, transaction và idempotency; engine không gọi API/DB. Đáp án chuẩn, rubric và secret ở server. Gửi lại có cùng key dùng grade đã lưu, không chấm theo policy mới.

```mermaid
sequenceDiagram
  participant U as Lesson Player
  participant A as Learning API
  participant E as Pure grading engine
  participant D as PostgreSQL
  U->>A: Start or resume lesson run
  A->>D: Pin version and materialize sequence
  A-->>U: Current item and revision
  U->>A: Submit answer with revision and key
  A->>D: Verify ownership, lock run, read pinned item
  A->>E: Grade bounded answer with private reference
  E-->>A: Alignment and verdict
  A->>D: Commit append-only attempt, revision, cursor
  A-->>U: Feedback and updated RunView
  U->>A: Complete after last required item
  A->>D: Completion + progress + eligible XP + saved vocabulary
  A-->>U: Completion receipt
```

## Typing: FR-TYPE-001

### Mode, difficulty và lựa chọn item

| Practice mode | Cơ bản `basic` | Trung cấp `intermediate` | Nâng cao `advanced` |
| --- | --- | --- | --- |
| Mặc định `default` | MVP · từ, cụm, câu | MVP · từ, câu | MVP · câu |
| Nghe `listen` | Không hỗ trợ | Không hỗ trợ | MVP · câu, phát audio, gõ lại |
| Nghe và nói `listen_speak` | Không hỗ trợ | Không hỗ trợ | V1 · câu, nghe mẫu, tự xác nhận đã luyện. Chấm tự động thuộc quyết định V2. |

- Tác giả đánh dấu `typing_variants` trong phiên bản, gắn `word/phrase/sentence` cho từng prompt và sắp `exercises.position`. Với lane được phase hỗ trợ, lọc exercise typing `required=true` theo loại prompt của ma trận, sắp theo position tăng dần, ghim ordinal 1..N trong `run_items` khi bắt đầu. Optional item không tham gia typing run. Không bốc ngẫu nhiên hay chọn bài từ dữ liệu người học. CMS báo lỗi lane rỗng, loại nội dung thiếu dữ liệu hoặc license/audio chưa đủ, giữ lane đóng đến khi bản hợp lệ được publish.
- Default cho thấy cue/bản dịch đã duyệt và chỉ công bố reference sau khi được phép. Listen dùng audio mẫu hợp lệ và ẩn lời/bản dịch đến lúc phản hồi đủ điều kiện. Listen_speak dùng audio mẫu, ghi và phát lại cục bộ nếu người học cấp quyền, tự xác nhận `practice_ack` cho từng mục và thu hồi tài nguyên ghi ngay khi rời. Người học có thể nghe và tự xác nhận khi không cấp mic. V1 gửi duy nhất lệnh tự xác nhận, gồm item, revision và kind. Khi audio lỗi, giữ lại cursor và hướng dẫn thử lại hoặc chọn lane khác. Lỗi tải audio không tính attempt, pass hoặc completion.
- Identity một lane là learner + lesson + phiên bản + mode + difficulty. Chọn lane tạo hoặc tiếp tục theo khóa đó. Reload và ngắt kết nối lấy run ID, revision, terminal count và cursor từ server. Đổi mode hoặc difficulty điều hướng về chọn lane rồi mở run khác. Lượt đang làm vẫn giữ nguyên để mở lại. Khi publish bản mới, lượt mới lấy phiên bản current; run cũ còn quyền tiếp tục qua ID. Replay là thao tác riêng khi đã hoàn tất lane, không ghi đè lượt đang làm hoặc kết quả cũ.
- Điều kiện mở bài thuộc `lesson_prerequisites`. Prerequisite `recommended` cho phép đi tiếp, `required` cần có completion hợp lệ của bài trước, không cần mastery. Với bài đã mở, mọi lane đủ điều kiện nội dung và phase được chọn ngay. Hoàn thành ở một lane/version chỉ ghi thành tích lane/version đó và progress lesson identity, không đánh dấu các lane khác hoàn tất. Khi version mất quyền, chặn làm tiếp và vẫn cho xem kết quả tổng hợp đã ghi.

### Chuẩn hóa và token

1. Kiểm JSON sớm. Nhận tối đa 1000 Unicode code point và 128 token. Từ chối control char không phải whitespace được phép (`tab`, newline), Unicode bidi control và zero-width formatting. Prompt kỳ vọng không rỗng, phải qua validate CMS trước publish. Dùng Unicode NFC, chuẩn hóa U+2018/U+2019 thành apostrophe thẳng và U+2010/U+2011 thành hyphen `-`; English lowercasing, không lệ thuộc locale máy người dùng. Collapse whitespace Unicode thành dấu cách, trim.
2. Token là chuỗi Unicode letter/mark/digit có apostrophe/hyphen khi chúng nằm giữa hai đoạn token. Dấu câu ngoài token là separator. Vì vậy `Wait, now!` và `wait now` tương đương; `don't` khác `dont`, `re-enter` khác `re enter`, `12.5` thành `12` và `5` trong mode này. Decimal/định dạng số và dấu có nghĩa đặc biệt cần reference do editor khai báo, hoặc một exercise mode theo format với policy riêng.
3. Giữ cả raw input đã validate và mapping token → span trên input cho màn feedback; normalize một token có thể đổi độ dài và nhiều code point. Index trong response là thứ tự token, không dùng offset byte làm vị trí JS.
4. Các dạng rút gọn, số viết chữ, chính tả UK/US và dấu thanh không tự hợp nhất. Editor thêm reference alternative khi hợp lệ. Dùng cùng normalization trên expected và actual. Answer chỉ dấu câu/whitespace → 422 và không tạo attempt. Từ chối input vượt giới hạn ngay tại validation.

### Căn chỉnh và điểm

- Levenshtein trên token: match cost 0; substitute, delete expected (missing), insert actual (extra) cost 1. Dynamic programming với traceback từ cuối, tie priority theo hướng traceback `match → substitute → missing → extra`. Ma trận `(n+1)*(m+1)` với cap 128 để thời gian/bộ nhớ O(nm), ổn định cả lặp token. Thứ tự kết quả sau reverse là theo chuỗi.
- Chạy từng reference (tối đa 10), chọn distance nhỏ nhất rồi reference theo thứ tự biên soạn. Alignment ops `match/wrong/missing/extra` chứa index expected/actual phù hợp. UI dùng chữ/ký hiệu và màu cùng lúc. Không trả `expected_token` cho wrong/missing trước reveal; nêu vị trí và loại lỗi. Các token learner đã gõ an toàn để echo dưới dạng plain text. `passed` nếu distance=0; `score=round_half_up(100 × max(0,1-distance/max(n,m,1)),2)`.
- Thành công hoàn toàn đưa item vào passed và advance cursor; UI giữ feedback tới khi chọn Tiếp tục, rồi render current item đã được server xác nhận. Sai để nguyên item, hiện lý do, cho retry. Submits trùng được ràng buộc theo request key/revision theo API. Kể cả mới thay key, một revision/cursor cũ không tạo điểm kép.
- Nudge tối đa một lần/item trong graded mode khi có nội dung hint đã duyệt, có thể cho độ dài hoặc ngữ cảnh. Nudge đặt item assisted và giữ cursor. Lần nộp sau nudge hoặc trợ giúp tương đương có `assisted=true`; bản ghi lần nộp trước đó giữ cờ trước thời điểm hỗ trợ. Reveal chỉ có sau ít nhất hai lần thử sai hợp lệ ở cùng item. Reveal phát nội dung mẫu, đặt assisted và terminal `revealed`, advance cursor, không chèn attempt. Listener speech không dùng nudge/reveal. Blank, validation, stale revision và replay cùng key không tăng bộ đếm.

### Completion, điểm và thưởng

| Chỉ số | Quy tắc cho typing |
| --- | --- |
| First Attempt Accuracy | `100 × first_attempt_correct_count / graded_count` trên toàn bộ mục graded bắt buộc. Tử số chỉ tính lần nộp hợp lệ đầu pass và unassisted. Fail lần đầu, first attempt assisted, reveal hoặc chưa nộp đóng góp 0. Nếu không có mục graded thì null. |
| Final Completion | Run chuyển completed khi tất cả required items đã terminal và learner gửi complete. Graded terminal là passed hoặc revealed. Speech terminal là self_ack. Đây là trạng thái tiến độ, độc lập với accuracy hoặc kết quả chấm. |
| Assisted attempts và reveal | Báo riêng `assisted_count` là số required items dùng trợ giúp, `revealed_count` là số mục kết thúc bằng đáp án. Cờ `Feedback.assisted` mô tả đúng attempt, không đổi khi item được hỗ trợ về sau. |
| Terminal Score | `100 × passed_count / graded_count`. Pass do retry hoặc sau nudge vẫn tính 1, reveal tính 0. Không lấy trung bình điểm alignment của từng lượt nộp. Speech trả null. |
| Mastery | Một completion graded đạt mastery khi mọi required item passed unassisted và first-attempt accuracy thực ≥80%. So bằng số đếm trước khi làm tròn UI. Giá trị đọc per lane/version giữ lịch sử đã đạt, còn kết quả từng run giữ nguyên. Speech trả null. |
| XP eligibility | Run typing graded hoàn tất và mọi required item kết thúc passed unassisted. Retry được tính nếu không dùng trợ giúp. Eligibility không cần mastery. +10 XP cho completion đầu đủ điều kiện theo learner + lesson, qua mọi mode, difficulty và version. Sau đó receipt vẫn phản ánh eligibility, `xp_delta=0`. Speech, reveal hoặc nudge không đủ điều kiện. |

Các giá trị phần trăm làm tròn half-up 2 chữ số chỉ sau khi kiểm ngưỡng. Báo required/graded/passed/revealed/self_ack và lần đầu đúng qua `TypingMetrics`. Speech không tạo grade number; self_ack là thực hành đã ghi nhận. Điểm terminal của typing là `CompletionReceipt.score`. Các loại bài khác tiếp tục dùng policy riêng. Công thức +10 và cách tính mastery là quyết định sản phẩm mới, theo dõi phản ứng pilot qua nhật ký riêng tư; streak, leaderboard và thành tích mở rộng thuộc V2.

### Nối kho từ và SRS

1. Content editor chọn từng `meaning_id` từ catalog để nối với exercise trong snapshot. Chỉ lấy nghĩa còn khả dụng từ required items được materialize của graded run, kể cả revealed. Các target trùng collapse theo identity nghĩa; ví dụ hai từ đồng hình khác sense vẫn là hai mục.
2. Sprint 03 commit completion + progress + XP đúng một lần. Sprint 04 đọc XP cá nhân. Sprint 05 thêm insert kho từ trong cùng completion transaction và backfill những graded completion trước cutover theo [ERD](04-database-design.md).
3. Mỗi learner/meaning có một marker kho từ. Auto-save dùng insert-if-absent, giữ nguyên marker active đã có và tombstone do learner bỏ lưu. Explicit save có thể restore, lịch ôn giữ độc lập. Nếu kho từ thay đổi tại completion, `new_saved_count` là số row vừa tạo và được ghi cùng immutable receipt.
4. Learner có thể chọn nghĩa và hướng ôn để gọi enroll. Khóa learner/meaning/direction tạo một thẻ cho cùng hướng và preserve lịch khi enroll lại. Hoàn thành hoặc làm lại bài typing không tạo thẻ đến hạn, không cập nhật trạng thái ghi nhớ và không tăng số lượt ôn.

```text
grade_typing(raw, references):
  actual = normalize_and_tokenize_validated(raw)
  require 1 <= len(actual) <= 128
  candidates = [(distance_and_trace(expected, actual), order)
                for each approved reference in author order]
  align, selected = choose by (distance, author order)
  score = round_half_up(max(0, 100 * (1 - distance / max(lengths, 1))), 2)
  passed = distance == 0
  return redact_as_needed(grade(passed, score, align, grading_version))

submit(run, cmd, key):
  in one transaction:
    replay or reserve key
    lock run and validate owner/state/revision/current_item and pinned lane
    grade using run's published immutable version
    append attempt with assistance snapshot
    apply mode terminal/retry policy and increment revision
    write receipt
  return receipt

complete(run, expected_revision, key):
  in one transaction:
    replay or reserve key; lock owned run
    if already completed: return stored receipt
    require revision matches and every required item is terminal for the lane
    calculate grading metrics from required items and first valid attempts
    lock lesson progress, upsert one run outcome and apply daily distinct counts
    xp_delta = insert_first_eligible_xp_grant_if_absent()
    if vocabulary integration enabled and lane is graded:
      new_saved_count = insert_missing_authored_meanings_for_required_items()
    mark run completed and persist receipt with progress, XP and vocabulary snapshot
  return receipt
```

| Test | Input với reference “I carry a small bag.” nếu không ghi khác | Kết quả |
| --- | --- | --- |
| ENG-T01 | `i CARRY  a small bag!` | Pass 100, năm match; caps/space/punctuation chuẩn hóa. |
| ENG-T02 | `I carry a red bag.` | 1 wrong, score 80, không gửi `small` trước reveal. |
| ENG-T03 | `I carry small bag` / `I carry a very small bag` | 1 missing, 80 / 1 extra, 83.33. |
| ENG-T04 | whitespace, `...`, IME composition, control chars, > caps | 422 không tạo attempt cho server invalid; IME không tự submit ở UI. |
| ENG-T05 | ref `don't re-enter` và actual `don’t re‑enter` / `dont re enter` | Pass biến thể unicode hợp lệ; mismatch dạng bỏ apostrophe/hyphen. |
| ENG-T06 | reference `a a b`, input `a b` và alt bằng điểm | Trace cố định; author order quyết định alt tie. Traceback implementation được snapshot test. |
| ENG-T07 | Submit accepted rồi timeout, retry same key; đổi body cùng key | Same attempt id, không double; 409 body conflict. |
| ENG-T08 | Hai tabs cùng revision, hint và submit; giới hạn reveal; reload sau pass | Một command chuyển revision, stale 409; không lộ answer trước policy; cursor sau reload theo server. |
| ENG-T09 | Publish mới khi có run; input theo bản cũ | Chấm version đã pin; run mới lấy version mới. |
| ENG-T10 | Default ba difficulty, listen basic, listen_speak trước/sau V1 | Sequence đúng loại và order theo ma trận. Lane không hợp lệ 422. Fixture lane nghe audio thiếu không publish. |
| ENG-T11 | Hai request Start khác key, cùng lane, và Start lane khác | Cùng lane trả một active run, khác lane khác run. Lượt non-typing có difficulty null cũng chỉ một active theo mode. |
| ENG-T12 | Resume đã completed, replay khi active, tiếp tục bản cũ | Default trả completed receipt, replay conflict nếu còn active, replay sau complete giữ lịch sử. Bản cũ còn quyền resume qua ID. |
| ENG-T13 | Hai mục pass lần đầu unassisted, một pass sau retry, một pass sau nudge, một reveal | Completion 5/5; first-attempt 40%, terminal 80%, assisted 2, revealed 1, mastery false, XP 0. |
| ENG-T14 | Bốn mục pass lần đầu unassisted và một pass sau retry | First-attempt 80%, terminal 100%, mastery true. Một run 3/4 lần đầu và mọi mục pass unassisted vẫn đủ XP dù mastery false. |
| ENG-T15 | Đồng thời hoàn tất hai lane/version đủ điều kiện cùng lesson trong một ngày | Hai completion receipt hợp lệ, lesson/day count tăng một, XP tổng tăng +10, không grant trùng khi replay. |
| ENG-T16 | Speech người học từ chối mic rồi tự xác nhận mọi mục | Có completion, không có dạng số cho accuracy/terminal, mastery null, XP 0, kho từ không đổi. |
| ENG-T17 | Hai exercise trùng nghĩa, nghĩa manual đã lưu, tombstone, optional và speech | Graded auto-save chỉ insert các target khả dụng mới từ required; không thay đổi manual/tombstone; không có SRS card hoặc due khi chưa enroll. |
| ENG-T18 | Rớt transaction sau khi chuẩn bị XP/kho từ, backfill restart sau mất kết nối | Rollback không để side effect, retry chỉ materialize một lần. Backfill có checkpoint, giữ receipt cũ, tombstone, lịch ôn, history và XP. |

## Vocabulary và ôn: FR-VOCAB-001, FR-SRS-001

Stock do card sở hữu key `(learner, meaning, direction)` và tách dấu saved. Đề xuất MVP flashcard recall tự chấm để quay lại thường xuyên. Học sâu nhiều dạng bài, AI tạo bộ từ và tự auto-enroll sau bài được ưu tiên sau khi có bằng chứng về giá trị. Deck lồng theo CEFR/tag; mất membership không xóa review logs. Hai chiều prompt là card khác nhau. UI có front, revealed, rating_pending, confirmed, retryable, empty và complete. Space flip và dãy 1–4 chỉ active khi focus phù hợp. Khi no due, hiện học thêm hoặc ngày ôn tiếp; không tự chấm thẻ chưa lật.

### Quy tắc lịch

- SM-2 biến thể dễ giải thích, `algorithm_version=sm2-elp-v1`. State `new/learning/review/suspended`, `repetitions`, `interval_days`, `ease` khởi tạo 2.50, lower bound 1.30, max interval 365 ngày. Map again→0, hard→3, good→4, easy→5.
- Update `ease=round_half_up(max(1.30, oldEase+0.10-(5-q)*(0.08+(5-q)*0.02)),2)`. Again reset reps=0, interval=0, learning, due_at=server UTC now +10 phút, repeat_in_session=true. Ngay sau khi chấm lần nữa server chỉ chấp nhận khi due; mode tự học ngoài SRS có thể luyện lại mà không đổi lịch.
- Với q≥3, reps mới là old+1. Reps=1 → 1 ngày, reps=2 → 6, reps≥3 → max(previous+1, rounded previous*oldEase), cap 365; state review. due_at = now UTC + n×24h, không trượt DST. Trong pilot Hard/Good/Easy đầu cùng khoảng và phân biệt Ease; UI hiển thị dự kiến theo thuật toán thực. Xu hướng ease và retention xem lại sau đủ dữ liệu. SRS không dùng các nhãn phút đo từ website tham khảo.
- Timestamp authoritative lấy từ server. Scheduler thuần có clock injectable. Due query inclusive `due_at<=as_of`. Worker không bắt buộc để query due. Bản ghi cũ giữ algorithm_version khi đổi thuật toán; migration chỉ opt-in trên cohort đã chọn. Revision trước khi chấm duy nhất để nhận race sau TTL idempotency.
- Một phiên kết thúc khi queue đã chọn hết hoặc người học dừng, hiển thị số thẻ đã chấm, lại trong phiên và còn đến hạn; chỉ item đã commit tính số. Không suy luận đã thuộc lâu dài từ một self-rating.

```mermaid
sequenceDiagram
  actor U as Người học
  participant V as Review API
  participant D as PostgreSQL
  U->>V: GET /srs/due
  V->>D: Read cards at fixed as_of
  V-->>U: Due page and revisions
  Note over U: Recall, flip, rate
  U->>V: POST card review rating + revision + key
  V->>D: Lock card, insert review log, update due + daily
  V-->>U: ReviewReceipt, updated due and revision
```

```text
next_review(card, rating, server_now):
  require card is not suspended and due_at <= server_now
  q = {again:0, hard:3, good:4, easy:5}[rating]
  new_ease = clamp_and_round_ease(card.ease, q)
  if q == 0: return learning(reps=0, days=0, ease=new_ease,
                             due=server_now + 10 minutes)
  reps = card.reps + 1
  interval = (1 if reps==1; 6 if reps==2;
              min(365, max(card.interval+1, round_half_up(card.interval*card.ease))) otherwise)
  return review(reps, interval, new_ease, server_now + interval*24h)
```

| Test | Kỳ vọng |
| --- | --- |
| ENG-S01 New + good | Reps=1, ease=2.50, due sau 24h UTC; lần good tiếp sau 6 ngày. |
| ENG-S02 Review + again | Reps=0, interval=0, ease min 1.30, đến hạn +10 phút; cấm early durable chấm. |
| ENG-S03 Hard/easy | Rating cập nhật ease theo công thức và cap; đủ 365 không tăng. |
| ENG-S04 Due boundary | 1 ms trước due bị từ chối; thời điểm bằng due được chấp nhận; UTC qua DST không đổi elapsed. |
| ENG-S05 Duplicate | Retried key nhận same review; key khác trên revision cũ 409; log/daily chỉ một. |
| ENG-S06 Enrollment | Cùng sense ở hai deck không nhân card cùng hướng; hướng khác được tạo. |

## Translation: FR-TRANS-001 và FR-AI-001

- Version giữ `source_lang, target_lang, source_text, references[], rubric_version, rubric`. Reference tác giả chấp thuận có nguồn và rationale ngắn. Rubric đánh giá fidelity/coverage, grammar, naturalness theo 0–4 mỗi chiều; báo lỗi theo `span,category,severity,explanation_vi,suggestion`. Chỉ gán lỗi khi rubric và bằng chứng giải thích được khác biệt về nội dung/ngữ pháp. Với dấu thanh tiếng Việt, NFC + case/whitespace đủ, giữ dấu trong token.
- V1 normalize và exact match qua mọi references đã phê duyệt. Bài nhiều đoạn cho mỗi đoạn nguồn một segment ID; coverage = số required segments có đáp án không rỗng / số required segments. Coverage chỉ đo phần được trả lời, không đo đầy đủ ý. Tất cả phân đoạn đầy đủ và mỗi đoạn match nhận pass; không match thì trả `needs_review` + phản hồi tham chiếu khi learner chọn xem. Alignment có thể hiển thị khác biệt nhưng không quy đồng là lỗi. Missing/unclear không cho điểm sai tự động trong yêu cầu cần dịch tự do. Completion translation practice cho terminal after learner ack bằng reveal; lưu trạng thái assisted/no grade khi không matched. Dùng multiple-choice/rule-based với đáp án xác định riêng nếu cần bài đánh giá.
- V2, opt-in gửi source, answer, rubric và bộ references tối thiểu đến LLM as data. Ràng buộc structured schema, check enum, field length, score và span; nếu output không đúng/thiếu confidence hoặc có ambiguity thì trả `needs_review` với message trung lập. Model không gọi tool hay tiết lộ prompt/secret. Một lần fallback parse/repair nếu rơi trong budget; lỗi provider → manual comparison, không đổi lịch học. Không ghi đè accuracy/proficiency dựa chỉ trên model. Tách evaluation dataset version có chấm người và so sánh giữa phiên bản.
- Input tất cả phân đoạn rỗng, segment trùng/foreign, vượt giới hạn hoặc unsafe Unicode controls: 422. Nháp per run/item dùng revision riêng, có TTL và xóa khi terminal; lịch sử từ attempt theo chiều và snapshot pin. Ví dụ nhãn trạng thái gồm “Accepted reference match”, “Compare with two sample translations”, “AI pending” theo loại. Store original answer encrypted at rest theo hạ tầng, giữ theo retention; logs chỉ grade metadata.
  
```text
assess_translation(answer, version, want_ai):
  normalized, coverage = normalize_answer_by_segment(answer, version)
  if coverage == 1 and each submitted segment matches an approved reference:
    return exact_match_pass()
  feedback = needs_review_with_optional_reference_reveal(coverage)
  if want_ai and consent and allowed_budget:
    enqueue_job_with_pinned_rubric_and_attempt()
  return feedback
```

| Test | Kỳ vọng |
| --- | --- |
| ENG-X01 Exact approved alternative | Pass ngay với khác case/spacing theo quy tắc; không cần provider. |
| ENG-X02 Diễn đạt đúng khác reference | Needs review, giải thích so sánh, không gán sai tuyệt đối. |
| ENG-X06 Dịch hai trong ba đoạn required | Coverage 2/3, needs_review; không tự xem là hai đoạn đúng hoàn toàn. |
| ENG-X03 Từ phủ định/đơn vị/số quan trọng bị thay | Bộ kiểm định có nhãn critical; AI phải làm nổi mâu thuẫn khi trả valid, chưa đủ tin thì human review. |
| ENG-X04 Prompt injection trong user input / model JSON sai | Xử lý như text; validator từ chối output, không có side effects hoặc lời gợi ý nguy hiểm. |
| ENG-X05 Opt-out / expiry / timeout | Không queue nếu opt-out; expired không phục hồi dữ liệu; fallback compare. |

## Grammar, đọc, dictation và phát âm

- Grammar/đọc chọn một: option IDs versioned, required exactly one; khi submit compare server key và giải thích. Rewrite/điền dùng typing policy riêng cho exercise; mark explanation/hint allowed theo lesson mode. Sau khi xuất bản pin blocks/rules.
- Dictation dùng grader typing và expected versioned cue, prompt không expose transcript trước feedback, tốc độ replay quản ngay tại player. Audio lỗi có retry/alternative text tùy mục tiêu, không trừ điểm vì lỗi tải.
- IPA/shadowing V1 dùng model audio có quyền, IPA và loop; learner tự xác nhận practice_ack khi mode cho phép. Speech score V2 chỉ formative, tách voice retention và consent. Không suy từ transcript STT rằng phát âm mọi phoneme sai/đúng.

## Exercise analytics

| Metric | Nguồn, mẫu số và quy tắc |
| --- | --- |
| First-attempt accuracy | Typing dùng first_attempt_correct_count / graded_count trên tập required graded đã chọn. No-attempt và assisted đóng góp 0. Tách mode/difficulty và version; báo cỡ mẫu. Những engine khác dùng định nghĩa theo bài. |
| Attempts per item | Tổng attempts accepted / số item có attempt. Validation, replay và hint không tăng. |
| Completion rate | Distinct completed runs / active runs đã bắt đầu trong window cố định và có follow-up tối thiểu, tách mode. Theo dõi abandon và thời gian theo cohort. |
| Response time | Elapsed giữa item visible/server start và submit, có idle policy, báo p50/p95, client mốc dùng cho analytics allowlisted, không tin dùng cấp điểm. |
| Progress | Distinct lessons đã completion theo version policy / eligible lessons trong published program, last/best không cộng lại idempotent. |
| Recall | Good/easy trong first durable review sau ≥24h / first durable reviewed eligible cards; self-report, tách sample size, state new/learning/review. |
| Quality | Alignment wrong/missing/extra theo nhóm và AI abstention/safety/rubric agreement; không đưa raw answer/audio vào analytics chung. |

Mọi thống kê day/streak dùng local date server. Test một activity đổi timezone giữa ngày, qua midnight, DST và retry. Tách cohort khi đổi grading_version/algorithm_version để kiểm tra hồi quy.

