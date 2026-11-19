# Ma trận ca kiểm thử

**PROPOSED**. Mỗi ca là một assertion có thể chuyển thành test. Kết quả dưới đây dành cho sản phẩm mới. [Hành vi AIO English đã khảo sát](../research/06-evidence-and-screenshots.md)

Mọi API dùng tiền tố `/api/v1`. Với lỗi, xác minh HTTP status, mã lỗi chuẩn ở [hợp đồng API](../architecture/05-api-specification.md), trạng thái UI, và số bản ghi bị thay đổi. Fixtures dùng hai người học, đồng hồ server cố định, một unit A1 và hai version của bài typing. [Đặc tả fixture](../data/01-content-schemas.md)

## Auth, curriculum và CMS

| ID / FR | Tầng | Seed và thao tác | Kết quả cần kiểm tra |
|---|---|---|---|
| QA-LAND-01 / FR-LAND-001 | E2E | Người mới mở trang giới thiệu 390 px, duyệt menu và nhấn CTA học. | Focus/label rõ. CTA qua trang đăng ký và người đã đăng nhập mở dashboard. |
| QA-AUTH-01 / FR-AUTH-001 | API + E2E | Gửi email fixture tới register. Truy cập link từ mail sink, đặt mật khẩu và tên qua `/auth/verify` rồi login. Thử lỗi mật khẩu và vào lại sau logout. | Pending chưa có credentials. Verify hợp lệ đặt hash và kích hoạt tài khoản. Phiên dùng cookie, chuyển onboarding đúng. Lỗi login trả response chung và cookie đã thu hồi bị từ chối. |
| QA-AUTH-02 / FR-AUTH-001 | API | Với guest, gửi từng trường hợp thiếu cookie double-submit, thiếu hoặc sai header. Với learner, gửi HMAC token sai, lấy token từ phiên khác, hoặc dùng Origin ngoài allowlist. Sau đó thử token đúng. | Điều kiện CSRF và Origin sai trả 403 trước khi ghi. Hợp đồng guest và learner độc lập. Token đúng theo session/origin hoạt động. |
| QA-AUTH-03 / FR-AUTH-001 | Integration | Tạo hai phiên cùng learner. Logout một phiên, dùng lại cookie đó. Yêu cầu reset, dùng link hợp lệ rồi replay link. | Logout thu hồi phiên hiện tại. Reset hợp lệ thu hồi cả hai phiên, link chỉ dùng một lần và cookie cũ không truy cập được. |
| QA-AUTH-04 / FR-AUTH-001 | API | Dùng phiên learner B đọc run, feedback, progress hay review card của A qua ID fixture. | Kết quả theo policy tài nguyên không thuộc owner. Không trả nội dung hoặc ghi DB của A. |
| QA-AUTH-05 / FR-AUTH-001 | Integration | Hai claim đồng thời của cùng một token email, sau đó replay, thử token cũ sau resend và gửi register với email active fixture. | Chỉ một claim đặt được credentials. Token đã tiêu thụ hoặc bị thay trả 410. Response register giống trạng thái pending và active. Email active giữ nguyên hash, hồ sơ và session. |
| QA-AUTH-06 / FR-AUTH-001 | Integration | Dùng mail sink, gây lỗi tạm thời một lượt gửi, resend, đặt clock vượt hạn và retry job cũ. Kiểm log, job record và token store qua fixture. | Worker kiểm đúng token/purpose và tình trạng trước khi gửi. Token cũ không gửi. Chỉ giữ blob mã hóa có TTL ở hàng đợi, xóa khi terminal. Không có link secret trong log hoặc payload thường. |
| QA-CUR-01 / FR-CUR-001 | E2E | Hai lesson published, một lesson có prerequisite `required` chưa đạt, một lesson có prerequisite `recommended` chưa đạt và một lesson draft. | Catalog thứ tự ổn định, bài required hiển thị lý do khóa. Bài recommended có thể bắt đầu. Draft vắng mặt. Hoàn thành điều kiện mở lesson theo định nghĩa. |
| QA-CUR-02 / FR-CUR-001 | API | Yêu cầu start lesson cần prerequisite chưa đạt bằng ID fixture. | Backend áp quy tắc khóa, không tạo run dù UI đã cũ. |
| QA-CUR-03 / FR-CUR-001 | DB | Bản import có lesson A yêu cầu B và B yêu cầu A. | Phát hiện chu kỳ trước publish, bản hiện hành giữ nguyên. |
| QA-CMS-01 / FR-CMS-001 | Integration | Nhập CSV hợp lệ rồi lặp cùng `package_key`, release và hash. Thử lại cùng key/release với hash khác. | Cùng file replay, file khác báo conflict, một draft set. |
| QA-CMS-02 / FR-CMS-001 | API + UI | Nhập vật liệu chưa có quyền, position trùng hoặc cue vượt duration. | Lỗi đúng dòng/field. Bản nháp thiếu quyền được xem để sửa. Gói lỗi cấu trúc bị chặn apply. |
| QA-CMS-03 / FR-CMS-001 | API | Editor gọi endpoint publish của draft. Editor có kiêm Reviewer thử tự duyệt. Reviewer khác trả bản về draft. | Admin mới được publish, author không tự duyệt, workflow guard theo trạng thái, phản hồi của reviewer có audit. |
| QA-CMS-04 / FR-CMS-001 | DB | Publish version đã duyệt nhưng trạng thái media/rule quyền đổi trước commit. | Lệnh thất bại và con trỏ published version giữ nguyên, expiring grant không được lưu với trạng thái thành công. |
| QA-CMS-05 / FR-CMS-001 | DB | Hai publisher cạnh tranh cùng lesson. Song song tạo run trong lúc version đổi. | Con trỏ là một version hợp lệ, mọi run ghim nhất quán. Lệnh cùng idempotency key được replay và tranh chấp revision theo contract. |
| QA-CMS-06 / FR-CMS-001 | E2E | Mở preview draft bằng editor rồi cùng URL ở learner. So lại sau publish. | Preview chỉ mở với role được cấp. Learner đọc bản published và media ready theo contract. |
| QA-CMS-07 / FR-CMS-001 | Integration | Gói lỗi ghi giữa apply, hoặc một asset upload sai MIME/checksum. | Batch rollback, file lỗi ở cách ly. Retry đúng asset có đúng một derivative ready. |

## Typing, progress, gamification

Reference fixture là `I would like a small tea.`. Kiểm tra cả grade, alignment, số lần attempt append, cursor và hàm đổi điểm theo [exercise engines](../architecture/06-exercise-engines.md).

| ID / FR | Tầng | Đầu vào và thao tác | Kết quả cần kiểm tra |
|---|---|---|---|
| QA-TYPE-01 / FR-TYPE-001 | Unit + API | Nộp đúng câu mẫu. | Tất cả token match, accepted. Feedback đồng nhất với GET theo attempt đã lưu. |
| QA-TYPE-02 / FR-TYPE-001 | Unit | Đổi `small` thành `large`. | Một substitution báo đúng vị trí, không false pass. |
| QA-TYPE-03 / FR-TYPE-001 | Unit | Bỏ `small` và giữ đoạn còn lại. | Một missing đúng vị trí, các từ sau vẫn khớp. |
| QA-TYPE-04 / FR-TYPE-001 | Unit | Thêm `hot` trước `tea`. | Một extra đúng vị trí, không chain substitution. |
| QA-TYPE-05 / FR-TYPE-001 | Unit | Dùng `I WOULD  LIKE A SMALL TEA!` với NBSP và xuống dòng giữa từ. | Normalize thành cùng token sequence, accepted. Bản raw được giữ theo chính sách. |
| QA-TYPE-06 / FR-TYPE-001 | Unit | `don't` và `don’t`, `re-enter` và `reenter`, Unicode composed/decomposed. | Hai dạng apostrophe chuẩn hóa giống. Dấu nối nội từ giữ nghĩa. NFC làm các biểu diễn tương đương khớp. |
| QA-TYPE-07 / FR-TYPE-001 | API + UI | Input rỗng, chỉ có khoảng trắng hoặc dấu câu bị bỏ qua, và một giá trị vượt giới hạn. | Input rỗng sau normalize bị từ chối. Attempt và progress giữ nguyên, focus vào input. Request lỗi dùng mã validation. |
| QA-TYPE-08 / FR-TYPE-001 | Unit + E2E | Enter khi IME composition và Enter sau khi xác nhận. | Enter lúc IME đang compose không submit. Enter hợp lệ nộp đúng một lần, giữ focus theo bước. |
| QA-TYPE-09 / FR-TYPE-001 | Unit | Ref `we can can go`, user `we can go`. Thử chuỗi nhiều đường edit cùng cost. | Tổng edit distance và tie-break ổn định qua các lần chạy. |
| QA-TYPE-10 / FR-TYPE-001 | API + E2E | Practice: sai một lần, nudge, thử reveal sớm rồi nộp sai lần hai và reveal. Mở exam fixture và thử nudge, sau đó nộp lần hợp lệ đầu. | Một nudge giữ cursor. Reveal bị chặn trước hai lần sai, sau đó terminal assisted. Hints bị từ chối ở exam và lần nộp đầu hợp lệ chuyển item terminal. Attempt và feedback cũ giữ nguyên. |
| QA-TYPE-11 / FR-TYPE-001 | API + E2E | Song song nộp cùng payload và `Idempotency-Key`. Sau commit dùng key đó với payload khác. | Tác dụng phụ đúng một lần. Cùng payload replay response, payload khác conflict. |
| QA-TYPE-12 / FR-TYPE-001 | API + E2E | Hai tab có khác idempotency key và cùng cursor revision. Một lệnh timeout phía client sau commit và retry. | Không bỏ qua cursor. Giao diện đồng bộ lại run, retry giữ key. Số attempt/điểm không bị ghi hai lần bởi timeout. |
| QA-TYPE-13 / FR-TYPE-001 | E2E | Tạo run, nộp item đầu, reload giữa bài và mở cùng lesson ở tab khác. Publish v2 trong lúc thử. | GET run phục hồi trạng thái chuẩn, v1 đã ghim. Cùng learner/lesson/version/mode chỉ có một run active. |
| QA-PROG-01 / FR-PROG-001 | API + DB | Complete khi bỏ mục bắt buộc rồi hoàn thành đủ. Gửi hai lệnh complete cạnh tranh. | Lệnh sớm lỗi trạng thái, lần hợp lệ cập nhật lesson và completion trong cùng giao dịch. Không nhân completion hoặc thưởng. |
| QA-PROG-02 / FR-PROG-001 | E2E | Sau khi hoàn thành mở lại lesson và dashboard. Có hai lesson distinct có activity cùng ngày. | Hiện lịch sử cùng kết quả cũ và đề xuất tiếp theo theo thứ tự. Retry/replay tạo run mới theo contract và không xóa kết quả cũ. |
| QA-PROG-03 / FR-PROG-001 | DB | Gây lỗi sau insert attempt nhưng trước update cursor/session. | Rollback trọn vẹn, retry sau lỗi tạo kết quả đúng một lần. |
| QA-PROG-04 / FR-PROG-001 | Unit + DB | Hai heartbeat chồng lấn, foreground đổi background, user đóng tab. | Thời gian học tính phần hợp lệ theo [NFR](../requirements/05-non-functional-requirements.md) và progress contract. Hai tab không nhân phút. |
| QA-GAME-01 / FR-GAME-001 | DB | Hai giao dịch cùng source reward, UTC qua nửa đêm ở Hà Nội, DST ở New York. | Một bản ghi XP cho source, ngày theo timezone IANA đã ghim theo quy tắc, một ngày đủ điều kiện tăng chuỗi. |
| QA-GAME-02 / FR-GAME-001 | E2E | Người học đạt ngưỡng achievement và refresh. | Achievement trao một lần, lưu ngưỡng và nguồn. Leaderboard phân trang và tôn trọng phạm vi công khai nếu bật. |

## Vocabulary, SRS và các mô-đun V1/V2

| ID / FR | Tầng | Seed và thao tác | Kết quả cần kiểm tra |
|---|---|---|---|
| QA-VOCAB-01 / FR-VOCAB-001 | E2E | Mở deck A1, lật thẻ, chọn một sense của từ nhiều nghĩa, lưu rồi ghi danh SRS hai lần. | Hiện đúng gloss, IPA và audio đã có, không nhân SRS card khi ghi danh cùng sense và chiều. QA-DICT-01 kiểm tra nguồn lưu bổ sung ở V1. |
| QA-VOCAB-02 / FR-VOCAB-001 | E2E | Pronunciation thiếu file en-GB, en-US sẵn. | Chỉ điều khiển được accent sẵn, giữ nghĩa và hiện nhãn dự phòng. |
| QA-SRS-01 / FR-SRS-001 | Unit | Mỗi rating again/hard/good/easy với clock cố định. Một thẻ lapse sau nhiều interval. | Mapping 0/3/4/5. Again đặt lại reps và due +10 phút. Lần Pass đầu/hai cách 1/6 ngày, interval sau tăng theo engine và tối đa 365 ngày, ease tối thiểu 1,30. [Quy tắc engine](../architecture/06-exercise-engines.md) |
| QA-SRS-02 / FR-SRS-001 | API | Đặt thẻ có due đúng thời điểm truy vấn và sau đó 1 ms, GET due hai trang. | Bao gồm thẻ tới hạn, thứ tự ổn định khi tie, cursor không lặp. Thông báo khi hàng đợi rỗng. |
| QA-SRS-03 / FR-SRS-001 | DB + API | Hai tab rate cùng `expected_revision` khác key. Retry key đã commit và cùng payload. | Một interval và log mới, lệnh cũ conflict, replay trả review đã lưu. |
| QA-SRS-04 / FR-SRS-001 | Unit | Due trước/sau đổi giờ mùa hè và đổi timezone tài khoản. | Ôn dài ngày dùng 24h UTC theo engine. Thay timezone áp vào tổng hợp ngày theo policy. |
| QA-GRAM-01 / FR-GRAM-001 | E2E | Lọc level, đọc lý thuyết và trả lời một quiz sai rồi đúng. | Có giải thích sau khi nộp, retry độc lập, progress ghi theo điều kiện hoàn thành. |
| QA-DICT-01 / FR-DICT-001 | API + E2E | Truy vấn từ đơn, cụm từ, nhiều nghĩa và không khớp. Chuyển accent. | Gợi ý và phân trang đúng hợp đồng, giao diện empty có hướng xử lý, source attribution theo sense, accent khả dụng phát được. |
| QA-READ-01 / FR-READ-001 | E2E | Đọc đoạn A1, bật/tắt dịch, chọn mục từ và gửi comprehension answer. | Không mất vị trí đọc, từ đúng context, câu hỏi hiển thị feedback và lưu theo run khi có. |
| QA-TRANS-01 / FR-TRANS-001 | Unit + E2E | Gửi hai reference khác nhau và một câu làm sai giờ mở cửa. | Hai variant hợp lệ nhận feedback nhất quán. Lỗi giờ nhận rubric mục tương ứng hoặc thông báo cần đánh giá theo policy. |
| QA-TRANS-02 / FR-TRANS-001 | API | Mất kết nối trong lúc feedback, retry cùng key. | Trạng thái rõ và không tạo attempt trùng. Rule-based dùng được khi AI chưa bật. |
| QA-VIDEO-01 / FR-VIDEO-001 | E2E + media | Tệp 8 giây với cue hợp lệ, clip riêng và phụ đề hai ngôn ngữ. Seek vào cue, tốc độ 0.75x/1.25x, lặp. | Player seek đúng theo dung sai trong [hồ sơ hiệu năng](03-performance-and-security.md), đồng bộ theo media time. Chọn phụ đề bằng bàn phím. |
| QA-VIDEO-02 / FR-VIDEO-001 | API | Transcript đúng version, signed URL hết hạn, video provider thất bại. | Đúng track và phút, làm mới URL hợp lệ một lần theo policy. Có retry/empty/error, UI không tự báo hoàn thành. |
| QA-DICTATION-01 / FR-DICTATION-001 | E2E | Phát cue, gõ sai, nghe lại, retry đúng, next. | Cùng mode và cue, feedback đúng version, chuyển tiếp theo quyền và chỉ ghi hoàn thành hợp lệ. |
| QA-IPA-01 / FR-IPA-001 | E2E | Chọn phoneme, nhận diện cặp tối thiểu, phát mỗi accent khả dụng. | Âm đang chọn có nhãn và ví dụ rõ. Câu trả lời được xác định theo ID nghĩa chính xác. |
| QA-SHADOW-01 / FR-SHADOW-001 | E2E | Từ chối mic, sau đó ở fixture riêng cấp mic giả lập và ghi âm cue. | App giải thích quyền thiếu, phát lại audio cục bộ khi được phép, chỉ gửi audio khi có đồng ý. |
| QA-SHADOW-02 / FR-SHADOW-001 | Integration | Upload quá size, retry job đang xử lý và TTL hết hạn. | Lỗi có hướng khắc phục, job idempotent, đối tượng hết hạn không truy cập được. |
| QA-AI-01 / FR-AI-001 | Integration + eval | Mock provider timeout, tín hiệu quota và trả dữ liệu ngoài schema. | Báo trạng thái fallback, không có feedback ảo hay ghi đè đánh giá chuẩn, chặn vượt ngân sách. |
| QA-AI-02 / FR-AI-001 | Gold eval | Tập ẩn có paraphrase, thiếu ý, câu ác ý nằm trong input và accent khác nhau. | Bám rubric, nội dung đầu vào chỉ là dữ liệu, không rò giữa learner. Đạt cổng chất lượng theo hồ sơ hiệu năng. |
| QA-SET-01 / FR-SET-001 | E2E | Hoàn thành onboarding bằng CEFR, timezone và locale `vi` mặc định, bỏ qua mục tiêu thi. Đổi sang `en` và reload. Sprint 4 thêm ca đổi phút học và timezone. | Lưu cờ hoàn thành và lựa chọn qua reload. Locale/schema sai hoặc revision stale bị chặn. Mục tiêu phút đúng khoảng 5–180 và lịch sử giữ timezone đã ghi. |
| QA-SET-02 / FR-SET-001 | API + E2E | Learner A gửi export khi chưa reauth rồi reauth đúng và gửi lại. Poll job và tải khi ready. Learner B thử xem status hoặc tải cùng ID. Thử URL đã hết hạn. | Step-up bắt buộc cho export. Retry cùng khóa tạo một job, nội dung giới hạn đúng dữ liệu A, status và grant chỉ cấp cho A. Learner B và URL hết hạn bị từ chối. Không lộ thông tin nhận dạng qua log. |
| QA-SET-03 / FR-SET-001 | Integration + E2E | Erase khi chưa reauth, sai mật khẩu, session khác hoặc bước xác thực đã cũ hơn 10 phút. Bấm hủy xác nhận trong UI. Sau đó reauth đúng, xác nhận erase và gửi lặp cùng key. | Các nhánh reauth sai không tạo job. UI hủy xác nhận không gửi mutation. Phiên vừa xác thực gửi lặp chỉ tạo một job. Worker ghi audit, chạy đúng policy retention và thu hồi phiên của tài khoản khi xử lý erase. |
| QA-SOC-01 / FR-SOC-001 | API + E2E | Nếu bật social, user gửi invite vào tài khoản QA, lặp cùng key, người khác thử accept, rồi đúng người accept. | Một lời mời, người ngoài không có quyền, trạng thái bạn nhất quán, thiết lập opt-out được tôn trọng. |
| QA-HELP-01 / FR-HELP-001 | E2E | Mở Help từ app, duyệt FAQ và mở biểu mẫu nếu có. | Liên kết dùng được, label và error có ngữ cảnh. Biểu mẫu nêu rõ dữ liệu cần nhập và hiển thị trạng thái sau khi gửi vào stub. |

## Chạy hồi quy trên desktop và mobile

| ID | Ca | Bằng chứng |
|---|---|---|
| QA-A11Y-01 | Tab qua dashboard, dialog setup, input, feedback và next. Dùng Escape, quay focus về nút mở dialog. Kiểm tra error/progress live regions. | Trace focus và kiểm tra screen reader, cả zoom 200% và reduced motion. |
| QA-MOB-01 | Viewport 320 px và 390 px, keyboard mở, xoay chiều nếu có video. Mở hint, submit và xem feedback. | Action còn trong vùng thao tác, không cuộn ngang ngoài vùng transcript có chủ đích, chữ và trạng thái dễ đọc. |
| QA-MOB-02 | Chuyển tab và điều hướng history giữa lúc audio đang phát. | Không phát ngoài trải nghiệm đã chọn hoặc giữ mic ngoài luồng đang chạy. Nút play/pause đồng bộ. |
| QA-RST-01 | Restore một bản backup ở staging riêng, chạy login, đọc version, resume run và audit sample. | Kiểm tra timestamp snapshot, tổng row và SHA-256 mẫu đối tượng. Ghi RPO/RTO thực tế với dấu thời gian. |
| QA-SEC-01 | Kiểm tra rate limits, session, authz, CSRF, nội dung hiển thị, asset ACL, config và audit theo cổng bảo mật. | Có kết quả theo owner và bản phát hành, không có test production dùng dữ liệu thật. [Kịch bản bảo mật](03-performance-and-security.md) |

[Chiến lược kiểm thử](01-test-strategy.md) · [Tiêu chí nghiệm thu](../requirements/04-acceptance-criteria.md)
