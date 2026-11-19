# SRS — Đặc tả yêu cầu phần mềm

**Trạng thái** PROPOSED · 19/11/2026

Mọi FR bên dưới là yêu cầu của nền tảng mới. Nghiên cứu ghi lượt quan sát OBSERVED, diễn giải INFERRED và phần cần xác minh tại [inventory](../research/02-feature-inventory.md) và [evidence](../research/06-evidence-and-screenshots.md). Tham chiếu MV/CV hoặc khu vực nghiên cứu là động lực thiết kế. Quy tắc nghiệp vụ dưới đây thuộc quyết định sản phẩm mới.

**Actor** Guest, Learner, Editor, Reviewer, Admin, Worker. Browser gửi định danh và ý định thao tác. Server quyết định quyền, bản phát hành, chấm, thứ tự và hiệu ứng. Staff có quyền theo vai trò. Learner chỉ truy cập dữ liệu thuộc tài khoản của mình. Ưu tiên P0 là MVP, P1 là V1, P2 là V2. Mỗi mã có luồng, điều kiện, đầu vào/ra, lưu dữ liệu, lỗi, tiêu chí và phụ thuộc. Xem [API](../architecture/05-api-specification.md), [ERD](../architecture/04-database-design.md), [AC](04-acceptance-criteria.md), [NFR](05-non-functional-requirements.md) và [screen](../design/03-screen-specifications.md).

## Điều kiện chung

- Đọc catalog và lịch sử theo cursor do server cấp khi có phân trang API. Bỏ dữ liệu response cũ khi query đổi, dùng stable ID khi nối thêm và có clear filter.
- Tạo run dùng content version đang công khai, pin version bất biến. Constraint chỉ cho một run đang hoạt động trên cùng learner, lesson, version và mode. Thứ tự item do server định nghĩa. Trạng thái lỗi có thể phục hồi mà không tạo hiệu ứng thứ hai.
- Mutation học tập có idempotency theo actor, thao tác, khóa và canonical request hash. Payload cũ khớp được trả lại cùng kết quả, payload khác xung đột. Update cùng resource dùng expected version và row lock theo hợp đồng API. Server kiểm quyền trước đọc/ghi tài nguyên.
- Một bài chỉ hoàn tất khi các item bắt buộc đạt trạng thái cuối hợp lệ. Khi publish mới, run đang ghim bản cũ tiếp tục trừ phiên bản bị thu hồi vì lý do quyền hoặc an toàn. UI luôn cho biết lỗi có retry được.
- Câu nhập và nội dung người dùng được hiển thị dạng text. Các trường văn bản dài có giới hạn theo hợp đồng, normalize rõ và phản hồi lỗi theo field. Feedback có text bên cạnh ký hiệu/màu và trạng thái thuần đọc cho screen reader.

## Yêu cầu theo module

### FR-LAND-001 · Demo và giới thiệu

**Ưu tiên và kế hoạch** P0 · S0/S3

- **Actor, điều kiện và kích hoạt** Guest mở trang chủ và chọn Thử một câu.
- **Luồng chính** Chọn demo tự biên, nhập câu, nộp và xem phản hồi, sau đó có thể đăng ký. Người đã đăng nhập có đường về dashboard.
- **Luồng thay thế và lỗi** Keyboard và touch cùng luồng. Rỗng báo tại ô, mất kết nối có Retry, demo cạn bài có Làm lại.
- **Input, output, validation và UI states** Nhận snapshot gồm câu và đáp án mẫu từ GET /public/demo. Chấm normalized matching cục bộ, giao diện ẩn đáp án đến khi có phản hồi. Trạng thái giới thiệu, nhập, chấm, feedback, hoàn tất.
- **Business rules, persistence và phụ thuộc** Phiên demo trong bộ nhớ, chỉ dùng snapshot mẫu công khai. Giới hạn truy vấn tại edge. Phụ thuộc chính sách normalization và nội dung demo.
- **Chấp nhận** Khách nộp đúng 1 câu bằng Enter, thấy giải thích, đi tới đăng ký. Dữ liệu dùng thử vắng ở tiến độ tài khoản mới.
- **Evidence và xác minh** PROPOSED. Landing và demo, nghiên cứu site. [RT-01](../research/06-evidence-and-screenshots.md#rt-01)

### FR-AUTH-001 · Email, phiên và onboarding

**Ưu tiên và kế hoạch** P0 · S1

- **Actor, điều kiện và kích hoạt** Guest đăng ký, xác minh, đăng nhập, khôi phục hoặc vào lại sau khi phiên hết hạn. Learner lần đầu mở onboarding.
- **Luồng chính** Nhập email vào POST /auth/register để nhận link một lần. Mở link và gửi token, tên hiển thị, mật khẩu qua POST /auth/verify. Server xác thực token trước khi thiết lập credentials. Sau đó người học đăng nhập, chọn CEFR, mục tiêu kỳ thi tùy chọn, múi giờ IANA và locale vi/en mặc định vi. Đăng xuất thu hồi phiên. Phục hồi bằng token một lần.
- **Luồng thay thế và lỗi** Guest gửi lại cùng email nhận phản hồi chung và không ghi đè tên/mật khẩu. Login sai và yêu cầu reset tránh lộ trạng thái tài khoản. Token hết hạn hoặc đã dùng có hướng gửi lại đúng flow và cooldown. Tiếp tục trang hợp lệ sau khi xác thực.
- **Input, output, validation và UI states** Register chỉ nhận email. Verify nhận token hợp lệ, tên hiển thị và mật khẩu 12–128 ký tự. Onboarding kiểm tra CEFR, mã mục tiêu kỳ thi nếu cung cấp, timezone IANA và locale vi/en. Login trả phiên same-origin cookie, JS nhận CSRF token và trạng thái onboarding.
- **Business rules, persistence và phụ thuộc** Tiêu thụ token một lần và thiết lập tên/mật khẩu hash trong cùng giao dịch. Lưu hash token/phiên và lifecycle. Cookie Secure HttpOnly SameSite, CSRF cho mutation. Phụ thuộc email và account.
- **Chấp nhận** Token replay thất bại, đăng ký guest trùng không đổi credentials đã thiết lập. Hoàn tất onboarding vào dashboard khi các trường bắt buộc hợp lệ, mục tiêu kỳ thi có thể bỏ trống. Lần sau mở đúng tuyến nội bộ. Các tab khác nhận phiên đã thu hồi khi request kế.
- **Evidence và xác minh** PROPOSED. Điều hướng auth và dashboard nghiên cứu. Flow xác minh/khôi phục là đề xuất. [RT-02](../research/06-evidence-and-screenshots.md#rt-02) · [RT-03](../research/06-evidence-and-screenshots.md#rt-03)

### FR-CUR-001 · Khóa, chương, roadmap và bài

**Ưu tiên và kế hoạch** P0 · S2

- **Actor, điều kiện và kích hoạt** Learner đã xác thực mở roadmap và chọn bài đã xuất bản.
- **Luồng chính** Hiện khóa theo CEFR, chương theo thứ tự, trạng thái bài và đề xuất kế. Chọn bài để xem thành phần, độ dài và tiến độ.
- **Luồng thay thế và lỗi** Xem lại bài đủ quyền hoặc tiếp tục run. Báo empty khi cấp chưa có nội dung. Stale/withdrawn có thông báo và đường tới bài thay thế.
- **Input, output, validation và UI states** Nhận khóa/chương hoặc lessonId. Trả metadata, phiên bản hoạt động, khả năng bắt đầu, và dữ liệu progress của chính người học.
- **Business rules, persistence và phụ thuộc** Lưu version bài, quan hệ curriculum và enrollment nếu đã chọn. Cổng máy chủ xác nhận availability. Phụ thuộc CMS và Progress.
- **Chấp nhận** Mở lesson đủ quyền từ roadmap. Bài draft/unpublished không hiện trong API learner. Version đang làm được ghim khi có phát hành mới.
- **Evidence và xác minh** PROPOSED. Lộ trình và dashboard trong nghiên cứu. [RT-13](../research/06-evidence-and-screenshots.md#rt-13) · [CV-09](../research/06-evidence-and-screenshots.md#cv-09)

### FR-CMS-001 · Nhập, duyệt và xuất bản

**Ưu tiên và kế hoạch** P0 · S2

- **Actor, điều kiện và kích hoạt** Editor, Reviewer hoặc Admin đã xác thực vào CMS.
- **Luồng chính** Editor tạo nháp hoặc nạp CSV/JSON staging, sửa lỗi theo dòng và xin duyệt. Reviewer khác tác giả duyệt. Admin publish bản đã duyệt hợp lệ.
- **Luồng thay thế và lỗi** Import lỗi giữ staging và bản public. Approve có thể yêu cầu sửa với lý do. Content bị thu hồi xử lý độc lập với cập nhật version mới.
- **Input, output, validation và UI states** Schema, charset, locale, CEFR, media, rights, thứ tự bài, đáp án, edit version hợp lệ. Trả báo cáo lỗi, revision và trạng thái kiểm duyệt.
- **Business rules, persistence và phụ thuộc** Lưu import, draft, review, published version bất biến, license và audit. Publish transaction, optimistic edit version và replay an toàn. Phụ thuộc import/media.
- **Chấp nhận** Import có lỗi dòng kèm lý do, không publish. Reviewer khác tác giả approve. Hai publish đồng thời chỉ tạo một version active.
- **Evidence và xác minh** PROPOSED. CMS gốc tùy quyền, cần xem giới hạn nghiên cứu.

### FR-TYPE-001 · Gõ từ, cụm và câu

**Ưu tiên và kế hoạch** P0 · S3

- **Actor, điều kiện và kích hoạt** Learner mở bài Gõ, lesson đã phát hành và được phép truy cập.
- **Luồng chính** Bắt đầu/tiếp tục run, chọn điều khiển audio, đọc prompt, nhập và nộp, xem căn chỉnh từ, thử lại hoặc đi câu tiếp, hoàn tất rồi xem kết quả.
- **Luồng thay thế và lỗi** Gợi ý ngắn tối đa 1. Trong practice xem đáp án sau ít nhất 2 lần sai hợp lệ, item kết thúc dạng assisted. Nếu lỗi mạng giữ text, retry cùng khóa. Khi reload lấy lại vị trí và phản hồi server.
- **Input, output, validation và UI states** Input text và item/version expected hợp lệ, rejection khi rỗng. Dùng policy normalization của version. Trả feedback đúng/sai/thiếu/thừa, trạng thái attempt, cursor và progress.
- **Business rules, persistence và phụ thuộc** Giữ kết quả lần nộp, hint/reveal, run pin version, completion idempotent. Phụ thuộc Catalog, audio và Progress.
- **Chấp nhận** Ca thường, sai/thiếu/thừa từ, chữ hoa/dấu, rỗng, Enter, reload, complete/reopen có kết quả trong test matrix. Phát sinh đúng một completion.
- **Evidence và xác minh** PROPOSED. Thực nghiệm Gõ câu trong nghiên cứu và [engine](../architecture/06-exercise-engines.md). [RT-14](../research/06-evidence-and-screenshots.md#rt-14) · [RT-15](../research/06-evidence-and-screenshots.md#rt-15) · [RT-16](../research/06-evidence-and-screenshots.md#rt-16) · [RT-17](../research/06-evidence-and-screenshots.md#rt-17) · [RT-19](../research/06-evidence-and-screenshots.md#rt-19)

### FR-PROG-001 · Tiến độ, buổi học và mục tiêu

**Ưu tiên và kế hoạch** P0 · S4

- **Actor, điều kiện và kích hoạt** Learner vào /dashboard hoặc /progress sau khi học, hoặc sửa mục tiêu tại thiết lập.
- **Luồng chính** Hiển thị bài kế, lịch sử, bài xong, phút hôm nay, mục tiêu và số đến hạn khi SRS sẵn sàng. Từ Sprint 4, mục tiêu phút/ngày có thể cập nhật ở dashboard hoặc Settings. Mở thẻ để vào đúng module.
- **Luồng thay thế và lỗi** Tài khoản mới có metric 0 và CTA. Không tính idle/thời gian từ client chưa được xác thực. Lỗi từng thẻ có retry riêng, thông báo trạng thái khi muộn.
- **Input, output, validation và UI states** Input thành quả server hoặc mục tiêu đã xác thực, timezone IANA. Trả ngày kỳ vọng, minutes/completion còn thiếu, resume và trend.
- **Business rules, persistence và phụ thuộc** Hiệu ứng unique theo sự kiện, ghi ngày local tại thời điểm phát sinh, không tính lại quá khứ khi đổi timezone. Phụ thuộc run, account, lịch SRS.
- **Chấp nhận** Hai request complete trùng chỉ có một effect. Qua nửa đêm sai khác theo zone đúng. Resume đi đúng run.
- **Evidence và xác minh** PROPOSED. Dashboard, roadmap và progress quan sát được. [RT-05](../research/06-evidence-and-screenshots.md#rt-05) · [RT-06](../research/06-evidence-and-screenshots.md#rt-06) · [RT-19](../research/06-evidence-and-screenshots.md#rt-19)

### FR-VOCAB-001 · Bộ từ và danh sách đã lưu

**Ưu tiên và kế hoạch** P0 · S5

- **Actor, điều kiện và kích hoạt** Learner mở bộ từ, chi tiết từ hoặc dùng lưu từ ngữ cảnh khi Dictionary phát hành.
- **Luồng chính** Duyệt bộ theo chủ đề hoặc cấp, mở sense, nghĩa Việt, IPA, ví dụ và audio nếu có. Thêm vào danh sách hoặc bộ cá nhân. Chọn Đưa vào ôn và chiều ôn để tạo card.
- **Luồng thay thế và lỗi** Lưu lại idempotent. Chưa có từ thì mẫu empty với lối quay về catalog. Audio hỏng có nhãn thử lại, nghĩa vẫn sẵn.
- **Input, output, validation và UI states** Input deckId, lexeme/sense ID hợp lệ và quyền nội dung. Trả thẻ, count và trạng thái đã lưu.
- **Business rules, persistence và phụ thuộc** Lưu marker người học/sense và thành viên bộ cá nhân. Bỏ lưu hoặc gỡ khỏi bộ giữ thẻ và lịch sử ôn. SRS sở hữu lịch học. Phụ thuộc Catalog, media, Dictionary khi có.
- **Chấp nhận** Lưu cùng sense hai lần chỉ có một marker. Đưa vào ôn cùng sense và chiều chỉ tạo một card cho người học. Empty có lối thêm từ.
- **Evidence và xác minh** PROPOSED. Khảo sát Từ vựng và modal từ điển MV-17. [CV-01](../research/06-evidence-and-screenshots.md#cv-01) · [CV-03](../research/06-evidence-and-screenshots.md#cv-03) · [CV-04](../research/06-evidence-and-screenshots.md#cv-04) · [MV-17](../research/06-evidence-and-screenshots.md#mv-17)

### FR-SRS-001 · Ôn giãn cách

**Ưu tiên và kế hoạch** P0 · S5

- **Actor, điều kiện và kích hoạt** Learner chọn đưa sense đã lưu hoặc được xuất bản vào ôn theo chiều Anh–Việt/Việt–Anh, hoặc mở Review với card đến hạn.
- **Luồng chính** Hiện mặt trước, người học cố nhớ, lật để xem đáp án, chọn Again/Hard/Good/Easy. Server cập nhật due và trả thẻ tiếp theo cùng count.
- **Luồng thay thế và lỗi** Empty nếu hết hạn, có thời điểm tiếp theo. Hai tab stale được nhắc tải trạng thái. Mạng rớt giữ trạng thái nút và retry đúng khóa.
- **Input, output, validation và UI states** Nhận cardId, version và rating enum. Due được so UTC kể cả bằng thời gian hiện tại. Trả interval, dueAt và status.
- **Business rules, persistence và phụ thuộc** Lưu card version, due, lịch review bất biến với scheduler version. Không tạo thêm review từ replay. Phụ thuộc Vocabulary.
- **Chấp nhận** Hai thiết bị review đồng thời xử lý một lượt hợp lệ, ghi due theo scheduler và có giao diện khi hết queue.
- **Evidence và xác minh** PROPOSED. CV nhóm từ vựng, công thức scheduler là PROPOSED. [CV-02](../research/06-evidence-and-screenshots.md#cv-02) · [CV-05](../research/06-evidence-and-screenshots.md#cv-05)

### FR-GRAM-001 · Bài ngữ pháp và bài tập

**Ưu tiên và kế hoạch** P1 · S6

- **Actor, điều kiện và kích hoạt** Learner mở chủ đề từ roadmap hoặc tra cứu thư viện.
- **Luồng chính** Đọc hướng dẫn Việt, ví dụ Anh, bắt đầu item trắc nghiệm/điền từ, nộp, xem lý do và thử lại.
- **Luồng thay thế và lỗi** Có thể xem lý thuyết trước/sau. Bài chưa có quiz có thông báo, lỗi phiên bản hướng về lesson.
- **Input, output, validation và UI states** Nhận lessonId và answer đúng schema item, trả lựa chọn/gaps, lời giải, trạng thái bài. Tách học xong lý thuyết và đạt bài tập.
- **Business rules, persistence và phụ thuộc** Nội dung versioned, attempts và tiến độ chung. Cần renderer block và Exercise Engine.
- **Chấp nhận** Với item sai, giải thích chỉ ra lỗi và retry được. Item đúng tiến một bước, reload phản hồi giữ.
- **Evidence và xác minh** PROPOSED. Khảo sát bài Ngữ pháp. [CV-06](../research/06-evidence-and-screenshots.md#cv-06) · [CV-07](../research/06-evidence-and-screenshots.md#cv-07) · [CV-08](../research/06-evidence-and-screenshots.md#cv-08)

### FR-DICT-001 · Từ điển song ngữ

**Ưu tiên và kế hoạch** P1 · S6

- **Actor, điều kiện và kích hoạt** Learner đã xác thực tìm từ tiếng Anh hoặc lưu một sense.
- **Luồng chính** Debounce tìm từ/cụm, đề xuất có keyboard, mở entry, chọn từ loại/sense, nghe UK/US và lưu từ.
- **Luồng thay thế và lỗi** Không có kết quả giải thích và gợi ý sửa. Server hạn chế query quá dài. Audio lỗi báo riêng, dữ liệu nghĩa vẫn sử dụng.
- **Input, output, validation và UI states** Input query chuẩn Unicode, filter top results. Output lemma, meaning/sense, định nghĩa English, Việt, IPA/dialect, audio, example, relations tùy entry.
- **Business rules, persistence và phụ thuộc** Dữ liệu từ nguồn có phép, lưu tài khoản qua Vocabulary. Cache public theo version. Phụ thuộc content license, media.
- **Chấp nhận** Tra cụm và từ đơn có kết quả. Query rỗng/không khớp có empty state. Không tự sinh nghĩa khi catalog thiếu.
- **Evidence và xác minh** PROPOSED. MV-16/17. [MV-16](../research/06-evidence-and-screenshots.md#mv-16) · [MV-17](../research/06-evidence-and-screenshots.md#mv-17)

### FR-READ-001 · Đọc song ngữ và tra ngữ cảnh

**Ưu tiên và kế hoạch** P1 · S7

- **Actor, điều kiện và kích hoạt** Learner chọn bài theo CEFR/chủ đề, nội dung đã phát hành.
- **Luồng chính** Đọc theo đoạn và chuyển Anh/Song ngữ, mở chú thích từ/cụm, vào từ điển hoặc chế độ dịch.
- **Luồng thay thế và lỗi** Thiếu bản dịch có nhãn trạng thái. Bài không có quyền/licensing bị ẩn hoặc từ chối. Popover đóng bằng Esc và trả focus.
- **Input, output, validation và UI states** Input lessonId, locale và display mode. Trả passage, paragraphs, anchors và linked sense đã được review.
- **Business rules, persistence và phụ thuộc** Lưu phiên bản passage. Display preference theo account hoặc thiết bị. Phụ thuộc Catalog và Dictionary.
- **Chấp nhận** Chuyển mode giữ vị trí, word popover hoạt động bằng keyboard, bản dịch dùng đúng version bài.
- **Evidence và xác minh** PROPOSED. MV-05/06/09. [MV-05](../research/06-evidence-and-screenshots.md#mv-05) · [MV-06](../research/06-evidence-and-screenshots.md#mv-06) · [MV-09](../research/06-evidence-and-screenshots.md#mv-09)

### FR-TRANS-001 · Luyện dịch và lịch sử

**Ưu tiên và kế hoạch** P1 · S7

- **Actor, điều kiện và kích hoạt** Learner chọn bài/chiều đã được biên soạn và tạo run.
- **Luồng chính** Nhập câu hoặc đoạn, lưu nháp, nộp, so sánh bản mẫu và biến thể hoặc xem trạng thái cần review. Có lịch sử attempt theo chiều.
- **Luồng thay thế và lỗi** Rỗng báo lỗi. Dịch khác đáp án mẫu có thể thuộc Needs review. Giữ bài, giải thích mức tự tin. V2 mới dùng góp ý ngữ nghĩa async nếu bật.
- **Input, output, validation và UI states** Input text, chiều, item/version, khóa. Trả coverage, verdict/rubric theo rule, chú thích và bản mẫu sau nộp.
- **Business rules, persistence và phụ thuộc** Lưu draft/task, attempt, rule version. Submission lặp trả kết quả cũ. Phụ thuộc Reading và Exercise Engine, AI ở V2.
- **Chấp nhận** Bản đúng thay thế được chấp nhận nếu editorial cấu hình. Bài thiếu câu có coverage thấp. Lịch sử mở lại đúng version.
- **Evidence và xác minh** PROPOSED. MV-02..08. Luồng chấm và ngưỡng của nền tảng mới là đề xuất. [MV-02](../research/06-evidence-and-screenshots.md#mv-02) · [MV-03](../research/06-evidence-and-screenshots.md#mv-03) · [MV-04](../research/06-evidence-and-screenshots.md#mv-04) · [MV-07](../research/06-evidence-and-screenshots.md#mv-07) · [MV-08](../research/06-evidence-and-screenshots.md#mv-08)

### FR-VIDEO-001 · Thư viện video, phụ đề và quiz

**Ưu tiên và kế hoạch** P1 · S8

- **Actor, điều kiện và kích hoạt** Learner có quyền xem media đã cấp phép và mở video.
- **Luồng chính** Lọc, chọn mode, play/pause, timeline seek theo cue, điều chỉnh tốc độ, bật lớp phụ đề. Chọn Quiz nếu có bộ câu hỏi.
- **Luồng thay thế và lỗi** Phụ đề mất hoặc URL hết hạn hiển thị lỗi phù hợp/tải lại. Thiết bị không autoplay thì hiện play. Quiz chấm từng item và hiện kết quả chung khi đủ item bắt buộc.
- **Input, output, validation và UI states** Input lessonId, version, cue/timestamp và mode. Trả metadata media chuẩn, cues hoặc quiz view. Không lấy embed từ URL tùy ý.
- **Business rules, persistence và phụ thuộc** Media object, cue, license và trạng thái học server. Tính tiến độ watch theo giới hạn session. Phụ thuộc Storage, Catalog, Exercise.
- **Chấp nhận** Click cue để seek đúng đoạn trong tolerance test, caption động, quiz chặn nộp khi chưa chọn, feedback có lời giải cho item đã trả, receipt chỉ khi đủ điều kiện.
- **Evidence và xác minh** PROPOSED. MV-11/13/15. [MV-11](../research/06-evidence-and-screenshots.md#mv-11) · [MV-13](../research/06-evidence-and-screenshots.md#mv-13) · [MV-15](../research/06-evidence-and-screenshots.md#mv-15)

### FR-DICTATION-001 · Nghe chép từng đoạn

**Ưu tiên và kế hoạch** P1 · S8

- **Actor, điều kiện và kích hoạt** Learner chọn Dictation trên video có đoạn đã biên soạn.
- **Luồng chính** Nghe, replay/loop/speed, nhập, nộp, đọc khác biệt, tiếp tục đến hết hoặc resume.
- **Luồng thay thế và lỗi** Transcript lời giải ẩn trước phép reveal. Không đủ audio vẫn cho báo lỗi và trở lại video, không biến thành thành công giả.
- **Input, output, validation và UI states** Input cue/version, answer, khóa request. Cùng engine typing, trả alignment và trạng thái cue.
- **Business rules, persistence và phụ thuộc** Attempt và progress server theo run. Không trả reference cho cue chưa chấm. Phụ thuộc Video và Typing Engine.
- **Chấp nhận** Một câu sai có retry, câu đúng tăng progress một lần. Đổi tab/chế độ rồi quay lại khôi phục run theo contract.
- **Evidence và xác minh** PROPOSED. MV-12. Resume bền vững là đề xuất. [MV-12](../research/06-evidence-and-screenshots.md#mv-12)

### FR-IPA-001 · Tra và luyện âm IPA

**Ưu tiên và kế hoạch** P1 · S9

- **Actor, điều kiện và kích hoạt** Learner chọn accent, phoneme và bài đã xuất bản.
- **Luồng chính** Hiển thị bảng IPA theo nhóm, hướng dẫn vị trí âm, từ mẫu và minimal pairs. Mở bài nghe phân biệt, nghe, chọn và xem giải thích.
- **Luồng thay thế và lỗi** Thiếu âm mẫu vẫn đọc được hướng dẫn. Audio fail không tính đáp án tự động. Danh mục có CTA để tiếp tục.
- **Input, output, validation và UI states** Input soundId, dialect, lựa chọn. Output mô tả, audio/caption, phản hồi, state.
- **Business rules, persistence và phụ thuộc** Lưu phiên bản phoneme/prompt, completion nghe phân biệt. Phụ thuộc Media/Exercise.
- **Chấp nhận** Trả lời đúng một item và thấy phản hồi chữ. Đổi UK/US trả đúng tập dữ liệu đã xuất bản. Quiz không cần mic.
- **Evidence và xác minh** PROPOSED. MV-18/19. [MV-18](../research/06-evidence-and-screenshots.md#mv-18) · [MV-19](../research/06-evidence-and-screenshots.md#mv-19)

### FR-SHADOW-001 · Shadowing nghe và đối chiếu

**Ưu tiên và kế hoạch** P1 · S9

- **Actor, điều kiện và kích hoạt** Learner đã mở mode, chọn ghi âm qua thao tác rõ ràng nếu môi trường hỗ trợ.
- **Luồng chính** Nghe mẫu, ghi một đoạn ngắn, dừng, phát lại local, tự đánh dấu đã luyện.
- **Luồng thay thế và lỗi** Từ chối mic, nền tảng không hỗ trợ hoặc thiết bị mất giữ khả năng nghe/đọc. Nút dừng luôn hiện khi đang thu.
- **Input, output, validation và UI states** Input cueId và audio buffer trong RAM trình duyệt. Output trình phát local và trạng thái hoàn thành thao tác.
- **Business rules, persistence và phụ thuộc** V1 lưu mốc tự đánh dấu, recording ở RAM, giải phóng track sau dừng/thoát. Server AI dùng thỏa thuận riêng khi bật V2.
- **Chấp nhận** Từ chối quyền không kẹt UI. Chuyển màn/đóng dừng track. Không yêu cầu mic khi chỉ nghe.
- **Evidence và xác minh** PROPOSED. MV-14. Playback, quyền và an toàn là PROPOSED. [RT-20](../research/06-evidence-and-screenshots.md#rt-20) · [MV-14](../research/06-evidence-and-screenshots.md#mv-14)

### FR-AI-001 · Góp ý AI bất đồng bộ

**Ưu tiên và kế hoạch** P2 · S10

- **Actor, điều kiện và kích hoạt** Learner đủ quota, opt-in theo feature và đã nộp bài hỗ trợ.
- **Luồng chính** Yêu cầu feedback, xem queued/running, nhận feedback theo schema và rubric/source. Hủy khi chính sách cho phép hoặc đọc điểm rule-based.
- **Luồng thay thế và lỗi** Timeout, trùng, model từ chối, lỗi format và hết quota có trạng thái hữu ích, giữ attempt. Không lấy điểm AI để sinh achievement mặc định.
- **Input, output, validation và UI states** Input attemptId và consent/policy tùy tác vụ. Output jobId, rubric version, feedback/citation nội bộ, sai lệch mức tin cậy.
- **Business rules, persistence và phụ thuộc** Lưu job, provider/model/prompt version, trạng thái, chi phí và thời hạn. Báo hiệu lỗi trên queue, ownership trước truy cập.
- **Chấp nhận** Double click một job, provider lỗi fallback, dữ liệu bị xóa chặn phát lại, test đánh giá bao phủ dịch thiếu nhiều và prompt injection.
- **Evidence và xác minh** PROPOSED. MV-03/07 minh họa nhu cầu, kiến trúc nhà cung cấp là đề xuất. [MV-03](../research/06-evidence-and-screenshots.md#mv-03) · [MV-07](../research/06-evidence-and-screenshots.md#mv-07)

### FR-GAME-001 · XP, streak và thành tích

**Ưu tiên và kế hoạch** P2 · S11

- **Actor, điều kiện và kích hoạt** Learner hoàn tất hoạt động đủ điều kiện.
- **Luồng chính** Server ghi XP theo event, tính streak theo ngày địa phương và gắn thành tích có nguồn sự kiện. Dashboard mở lịch sử và điều kiện.
- **Luồng thay thế và lỗi** Hiển thị zero, ngày đứt chuỗi với cách bắt đầu lại. Retry và sửa lỗi không cộng thêm XP ngoài event policy.
- **Input, output, validation và UI states** Input domain event chuẩn, timezone snapshot. Output ledger summary, ngày liên tiếp và achievement.
- **Business rules, persistence và phụ thuộc** Ledger append-only, event key unique, quy tắc có phiên bản. Phụ thuộc Progress.
- **Chấp nhận** Trùng hoàn thành không nhân XP, hai khóa ngày liên tiếp đúng theo múi giờ, badge chỉ cấp một lần.
- **Evidence và xác minh** PROPOSED. Dashboard/xếp hạng/streak nghiên cứu. [RT-05](../research/06-evidence-and-screenshots.md#rt-05) · [RT-10](../research/06-evidence-and-screenshots.md#rt-10)

### FR-SET-001 · Thiết lập và quyền riêng tư

**Ưu tiên và kế hoạch** P0 · S1/S4 và cổng S12. Tùy chọn AI mở ở S10.

- **Actor, điều kiện và kích hoạt** Learner mở /settings và sửa một lựa chọn.
- **Luồng chính** Đọc và đổi locale vi/en, múi giờ và default_accent UK/US/system. Mục tiêu phút/ngày xuất hiện từ S4. Privacy mô tả dữ liệu thu và nhận yêu cầu xuất/xóa. Nhập lại mật khẩu để có xác thực nâng quyền 10 phút, xác nhận riêng khi xóa, rồi tạo job. Settings theo dõi trạng thái trong khi phiên có hiệu lực và hiển thị link xuất riêng tư ngắn hạn khi sẵn sàng.
- **Luồng thay thế và lỗi** Chặn giá trị sai và stale update, nêu múi giờ ảnh hưởng kỳ sau. Nếu xác thực nâng quyền hết 10 phút, trình bày lại bước nhập mật khẩu. Khi xóa có hiệu lực và phiên bị thu hồi, chuyển sang thông báo công khai tối thiểu. Jobs có trạng thái chờ, đang xử lý, sẵn sàng hoặc lỗi.
- **Input, output, validation và UI states** Input preference whitelist theo revision, mật khẩu hiện tại ở bước xác thực lại và lựa chọn export/erase. Output preference, job ID, trạng thái, link tải riêng tư ngắn hạn khi sẵn sàng.
- **Business rules, persistence và phụ thuộc** Lưu preferences, xác thực nâng quyền giới hạn theo phiên và job theo chính sách lưu giữ. Kiểm ownership khi xem job hoặc tải link. Audit thao tác nhạy cảm. Phụ thuộc Auth/Progress và privacy worker.
- **Chấp nhận** Đổi múi giờ giữ nguyên ngày đã chốt. Chặn export/erase khi thiếu xác thực mới và chặn erase khi chưa xác nhận. Retry cùng khóa tạo một job. Link tải riêng tư hết hạn và job người khác không truy cập được. Focus ở lỗi trường đầu.
- **Evidence và xác minh** PROPOSED. Thiết lập quan sát trong audit. [RT-07](../research/06-evidence-and-screenshots.md#rt-07) · [RT-08](../research/06-evidence-and-screenshots.md#rt-08)

### FR-SOC-001 · Bạn bè và phạm vi hiển thị

**Ưu tiên và kế hoạch** P2 có điều kiện · S11

- **Actor, điều kiện và kích hoạt** Learner opt-in, moderation đã vận hành và vai trò hỗ trợ có công cụ.
- **Luồng chính** Tìm theo định danh cho phép, gửi/nhận yêu cầu, chấp nhận, thấy tiến độ chia sẻ hoặc hủy kết nối.
- **Luồng thay thế và lỗi** Đã chặn hoặc pending có trạng thái kín đáo. Không hiển thị profile private hoặc thông tin cá nhân ngoài phạm vi đồng ý.
- **Input, output, validation và UI states** Input public handle và trạng thái hợp lệ. Output connection/aggregate opt-in, hạn mức và lỗi quyền.
- **Business rules, persistence và phụ thuộc** Lưu relationship với cặp định danh canonical, moderation và audit. Phụ thuộc Auth, Progress và chính sách privacy.
- **Chấp nhận** Hai lời mời trùng không tạo hai relation. Người dùng bị block không xem được thông tin chia sẻ.
- **Evidence và xác minh** PROPOSED. Tiến độ & Bạn bè nghiên cứu. Triển khai phụ thuộc moderation. [RT-09](../research/06-evidence-and-screenshots.md#rt-09)

### FR-HELP-001 · FAQ và báo lỗi học liệu

**Ưu tiên và kế hoạch** P1 · S7/S12

- **Actor, điều kiện và kích hoạt** Guest xem FAQ, Learner gửi báo lỗi từ màn có nội dung hợp lệ.
- **Luồng chính** Đọc trợ giúp, chọn loại vấn đề, nhập mô tả, xác nhận gửi rồi thấy mã báo cáo. Staff lọc và phân công.
- **Luồng thay thế và lỗi** Rỗng/quá dài báo tại trường, rate limit có retry. Không tự kèm bài trả lời/audio/tokens. Báo đội editorial theo phiên bản nội dung.
- **Input, output, validation và UI states** Input loại, text, optional content reference. Output receipt và state. Guest chỉ FAQ công khai.
- **Business rules, persistence và phụ thuộc** Lưu report theo TTL, kiểm quyền staff và access audit. Phụ thuộc CMS/Auth.
- **Chấp nhận** Bấm lặp chỉ có một báo cáo. Người học thấy mã và không truy cập ticket của người khác.
- **Evidence và xác minh** PROPOSED. FAQ, Yêu cầu tính năng và trợ giúp nghiên cứu. [RT-01](../research/06-evidence-and-screenshots.md#rt-01) · [RT-11](../research/06-evidence-and-screenshots.md#rt-11)

## Biên giao diện

[Catalog UI và route](../design/02-sitemap.md) có bước vào chính của từng FR. [Flow của engine](../architecture/06-exercise-engines.md) mô tả scoring, retry và versioning. [QA](../testing/02-test-cases.md) có evidence thực thi cần có khi triển khai. Các hạng P2 có cổng đánh giá và chủ sở hữu vận hành trước khi cấp quyền cho pilot.
