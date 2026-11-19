# Hợp đồng dữ liệu nội dung

**PROPOSED** cho FR-CMS-001, FR-CUR-001 và các mô-đun bài tập. Đặc tả này dành cho định dạng nhập, kiểm duyệt và bộ fixture. [Thiết kế PostgreSQL](../architecture/04-database-design.md) quy định kiểu lưu trữ và [API](../architecture/05-api-specification.md) quy định định dạng phục vụ người học.

## Gói nhập JSON

| Trường | Kiểu | Quy tắc |
|---|---|---|
| `schema_version` | integer | Bản đầu là `1`. Phiên bản chưa hỗ trợ bị báo lỗi trước khi tạo bản nháp. |
| `package_key`, `source_release` | string | Khóa ổn định dạng snake_case hoặc chữ thường, số, dấu chấm và gạch ngang, tối đa 120 ký tự. `source_release` do bên tạo gói cấp. Cùng cặp khóa và cùng SHA-256 trả lại đợt nhập hiện có. Cùng cặp khóa với nội dung khác phải dùng release mới. |
| `sources` | mảng provenance | Mỗi nguồn có `key`, `source_url` hoặc định danh kho nội bộ có kiểm soát, `source_version`, `creator`, `license_code`, `license_url` hoặc `contract_ref`, `attribution`, `rights_scope`, `changes` nếu có. Số hóa giấy phép tài sản phái sinh riêng. |
| `assets` | mảng media refs | Mỗi tài sản có `key`, `source_key`, tên tệp an toàn, MIME kỳ vọng, SHA-256, ngôn ngữ, accent nếu áp dụng. Server kiểm tra metadata thực trước khi gắn. `duration_ms` được đo khi xử lý. |
| `courses`, `units`, `lessons` | mảng đối tượng | Khóa độc nhất theo loại trong nguồn. Liên kết bằng khóa, resolve trong gói hoặc dữ liệu đã biết. Thứ tự nguyên dương, duy nhất trong cha. |
| `lexemes` | mảng mục từ | Mỗi lexeme ổn định theo khóa nguồn. Phân biệt nghĩa bằng ID riêng, ghi nguồn theo mục khi bộ dữ liệu có nhiều tác giả. |

`course` gồm `key`, `slug`, `title_vi`, `cefr_level`, `objective_vi`, `source_key`. `unit` gồm `key`, `course_key`, `title_vi`, `objective_vi` và `position`. `lesson` có `key`, `unit_key`, `slug`, `kind`, `title_vi`, `cefr_level`, `position`, `estimated_minutes`, `source_key`, `required_exercise_keys` và các mục nội dung riêng theo **kind**. `prerequisites` của lesson chứa `lesson_key` và `policy` thuộc `recommended` hoặc `required`. Định danh bên ngoài giữ ổn định qua các lần biên tập. Bản import vào môi trường khác nhận ID nội bộ mới và resolve theo khóa. Import bản đã công bố tạo phiên bản nháp mới. Bài học xuất bản đóng băng phiên bản, thứ tự và đáp án.

Lesson typing khai báo `typing_variants:[{mode,difficulty}]` với cặp duy nhất theo [ma trận engine](../architecture/06-exercise-engines.md#mode-difficulty-và-lựa-chọn-item). Tập `required_exercise_keys` xác định candidate trước khi lọc loại prompt và sắp `position`. Validate non-empty cho từng lane, cue/bản dịch dùng trong default và audio ready có quyền cho listen/listen_speak. `vocabulary_target_sense_keys` của exercise là danh sách cặp khóa nguồn `{lexeme_key,sense_key}` được tác giả chọn. Resolver kiểm nghĩa khả dụng và provenance, nối với UUID nghĩa bằng FK trước khi publish. Giữ liên kết theo version, kể cả khi cùng khóa xuất hiện ở nhiều prompt. Mục từ dùng để tra cứu chung có thể vẫn ở `lexeme_keys` và chỉ vào kho từ nếu có target rõ ràng.

## Schema theo loại

| Loại | Trường và quan hệ | Kiểm tra |
|---|---|---|
| Câu và phrase | `key`, `text_en`, `meaning_vi`, `kind` thuộc `word`, `phrase` hoặc `sentence`, `position`, `source_key`, `lexeme_keys`, `vocabulary_target_sense_keys`, `audio_asset_key`, `accepted_answers`. | Tối thiểu một đáp án cho bài graded; tính chuẩn hóa khi xác nhận phiên bản, giữ nguyên biểu diễn gốc. Cảnh báo trùng sau normalize. Cặp target trùng cùng exercise bị từ chối khi nhập. Chấm theo mục tiêu và giới hạn độ dài của engine. |
| Lexeme, nghĩa và bộ từ | `key`, `lemma`, `language`, `pos`, `forms`, `cefr_level`, `topic_keys`, `pronunciations`, `meanings`. Nghĩa gồm `sense_key`, `gloss_vi`, `definition_en`, `examples`, `related_sense_keys` tùy chọn. Bộ từ có khóa, tên, cấp, chủ đề và danh sách sense theo thứ tự. | POS từ danh mục đã chốt, nghĩa tiếng Việt có nội dung, sense ID giữ ổn định. `pronunciations` phân biệt en-US và en-GB và có IPA hoặc audio khi khả dụng. Một lexeme theo locale, lemma đã normalize và POS. Nghĩa đồng hình tách bằng `sense_key`. |
| Grammar | `topic_key`, `cefr_level`, `title_vi`, `objective_vi`, `sections` có heading/text/example, `exercise_keys`. Quiz có `key`, `type`, `position`, prompt, option keys, answer key hoặc alternatives, `explanation_vi`. | Nguồn văn bản có markup giới hạn. Bài trắc nghiệm có ít nhất hai lựa chọn, đáp án tham chiếu đúng mục và có giải thích. Bài điền có ít nhất một đáp án. |
| Reading | `title_en`, `cefr_level`, `segments` gồm `key`, `position`, `text_en`, `translation_vi`, `lexeme_keys`, `comprehension_exercise_keys`, `source_key`. | Mỗi segment cặp EN–VI ở cùng position. Quyền dịch cần nằm trong hồ sơ nguồn. Các quiz liên kết tới segment phiên bản hiện tại. |
| Translation | `source_language`, `target_language`, `prompt`, `references`, `rubric_items`, `explanation_vi`, `source_key`. Mỗi mục rubric có `key`, `kind`, `weight`, `description_vi` và `mandatory`. | Hai ngôn ngữ khác nhau. Tổng trọng số là 100, mục bắt buộc có tiêu chí kiểm chứng và đáp án mẫu. Biến thể được duyệt theo ý nghĩa. Ghim rubric theo phiên bản. |
| Video và transcript | `media_asset_key`, `title_vi`, `cefr_level`, `duration_ms`, `tracks`, `exercise_keys`. Mỗi track có `language`, `kind`, `cues` với khóa, `start_ms`, `end_ms`, `text`, `pair_key` tùy chọn. | Cue dùng đơn vị ms, `0 ≤ start_ms < end_ms ≤ duration_ms`. Cue tăng dần và không chồng thời gian trong một track. Bản dịch đối chiếu theo cặp đã duyệt. Asset, transcript và bài tập có hồ sơ quyền riêng khi khác nguồn. [WebVTT](https://developer.mozilla.org/en-US/docs/Web/API/WebVTT_API/Web_Video_Text_Tracks_Format) |
| Dictation, IPA và shadowing | Dictation gồm `cue_key`, `audio_asset_key` nếu có tệp clip riêng, `accepted_answers` và giải thích. IPA gồm `phoneme`, `accent`, `focus_position`, `minimal_pair_sense_keys`, audio. Shadowing ghim cue, accent, audio tham chiếu và mục tiêu. | Quyền tạo đoạn cần xác nhận, cue resolve trong cùng bản. So khớp từ tối thiểu có đúng âm mục tiêu, IPA gắn nhãn accent. Tệp của người học nằm ở luồng riêng với TTL và quyền riêng tư. |

Tiếng Việt và tiếng Anh dùng UTF-8/NFC. Giữ chữ hoa, dấu câu và dấu tiếng Việt ở cột hiển thị. Bộ chuẩn hóa của engine tính trường dẫn xuất phía server. CEFR là một trong A1, A2, B1, B2, C1, C2 ở những loại được gán cấp. Giáo viên duyệt cấp theo mục tiêu và yêu cầu thực hành. Có thể lưu nội dung nháp thiếu bản dịch hoặc audio, nhưng duyệt xuất bản áp dụng ràng buộc theo kind và trạng thái quyền.

## CSV sử dụng cho biên tập theo lô

Định dạng CSV UTF-8 với header duy nhất và các trường chứa dấu phẩy hoặc xuống dòng được quote. Bản đọc chấp nhận BOM UTF-8 và báo dòng/cột lỗi. Từ chối cột ngoài schema để phát hiện sai tên. Hai hình thức dùng trong MVP:

| Bảng nhập | Cột bắt buộc | Cột tùy chọn |
|---|---|---|
| Sentences | `key,lesson_key,position,kind,text_en,meaning_vi,source_key` | `audio_asset_key`, `accepted_answers_json`, `lexeme_keys_json`, `vocabulary_target_sense_keys_json` |
| Vocabulary | `key,lemma,language,pos,sense_key,gloss_vi,cefr_level,source_key` | `definition_en`, `ipa_en_us`, `ipa_en_gb`, `audio_en_us_asset_key`, `audio_en_gb_asset_key`, `examples_json`, `topic_keys_json` |

Nhập CSV ánh xạ về cùng mô hình kiểm duyệt với JSON. Mode/difficulty được đặt ở metadata lesson. Giá trị bắt đầu bằng ký tự công thức vẫn là text trong mô hình. Chức năng xuất CSV cần escape cho ứng dụng bảng tính để giảm nguy cơ thực thi công thức. Gói thử nghiệm chọn giới hạn khởi đầu 10 MB phần văn bản và 5.000 bản ghi trước khi benchmark, media tải riêng đến khu vực cách ly.

## Fixture nguyên bản để xây MVP

Chủ điểm A1 **Tại quầy cà phê**, source key `original.a1.cafe`, tác giả dùng nhãn nhóm dự án trong fixture, quyền của dữ liệu phát hành phải được xác lập trước công bố. Trong bộ mẫu, audio ID là tài sản minh họa cần tạo.

| Đối tượng | Khóa mẫu | Nội dung kiểm thử |
|---|---|---|
| Course | `a1.everyday` | Mục tiêu gọi món và hỏi giá bằng một câu ngắn. |
| Unit | `a1.everyday.cafe` | Chương 1, gồm typing và một lần ôn vocab. |
| Lesson / typing word | `a1.cafe.order` / `a1.cafe.small` | `small` / “nhỏ”, thứ tự 1, nhãn tính từ, audio en-US khi được sản xuất. |
| Typing phrase | `a1.cafe.small_tea` | `a small tea` / “một ly trà nhỏ”, thứ tự 2. |
| Typing sentence | `a1.cafe.order_tea` | `I would like a small tea.` / “Tôi muốn một ly trà nhỏ.”, thứ tự 3. Target explicit `tea.n.drink` và `small.adj.size`; bản fixture bật listen nâng cao sau khi có audio được phép. |
| Vocabulary sense | `tea.n.drink` | `tea`, danh từ, “trà” trong nghĩa đồ uống, IPA `/tiː/`, ví dụ nguyên bản `My tea is warm.` |
| Vocabulary sense | `small.adj.size` | `small`, tính từ, “nhỏ” theo kích thước. Gắn cùng nghĩa vào prompt từ `a1.cafe.small` để kiểm auto-save trùng. |
| Đầu vào QA | cùng lesson/run | Câu chính xác, đổi hoa và dấu câu, bỏ `small`, thêm `hot`, đổi `small` thành `large`, input rỗng, hai tab submit trùng, đóng và quay lại. |
| Lỗi dữ liệu | cùng package key mới | Hai position trùng, audio không có hồ sơ quyền, thiếu bản dịch, digest bị sai, source key không tồn tại, hai lesson tạo chu kỳ prerequisite. |

Một gói V1 mở rộng cùng trường hợp với reading ngắn “The café opens at seven.”, quiz giờ mở cửa, bài dịch với hai biến thể “Quán cà phê mở cửa lúc bảy giờ.” và “Quán mở vào lúc bảy giờ.”, clip tự thu và cue 0–2.200 ms, cặp phát âm `tea` / `key` nếu giáo viên xác nhận âm đầu được luyện. Bộ mẫu một unit đủ xây luồng xuyên suốt, kiểm thử nhập và trình diễn. Chỉ triển khai rộng sau rà soát tiếng Anh, tiếng Việt, tài sản và độ khó.

[Nguồn và quyền](02-data-sources.md) · [Pipeline CMS](03-content-pipeline.md) · [Bộ máy bài tập](../architecture/06-exercise-engines.md)
