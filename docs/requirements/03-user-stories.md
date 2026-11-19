# User stories và hành trình

**Trạng thái** PROPOSED. Mỗi story có một kết quả quan sát được và đi kèm FR chính. ID dưới đây là mã giao tiếp đến QA và sprint.

| Story | Vai trò, việc và lý do | Khi nào đạt | FR |
| --- | --- | --- | --- |
| US-01 | Là khách, tôi thử một câu để biết cách học trước khi đăng ký. | Có phản hồi tiếng Việt và đăng ký được từ demo. | FR-LAND-001 |
| US-02 | Là người mới, tôi chứng minh quyền truy cập email trước khi đặt tên và mật khẩu, rồi chọn mức học phù hợp. | Register gửi email, verify lập credentials sau token, rồi login. Dashboard mở sau khi chọn CEFR, timezone và locale. Mục tiêu kỳ thi tùy chọn. | FR-AUTH-001 |
| US-03 | Là người học A1, tôi xem lộ trình và vào bài kế để sử dụng thời gian hiệu quả. | Từ dashboard mở đúng bài/resume, có lý do ở bài chưa mở. | FR-CUR-001 |
| US-04 | Là editor, tôi nhập bài, thấy lỗi theo dòng và xin người khác duyệt. | Import sai giữ nháp. Admin xem và publish một version khi pass. | FR-CMS-001 |
| US-05 | Là người học đang gõ, tôi biết từ nào sai và thử lại để sửa lỗi cụ thể. | Gõ bằng bàn phím/touch, nhận text lỗi, reload trả đúng vị trí và phản hồi đã lưu. | FR-TYPE-001 |
| US-06 | Là người học buổi ngắn, tôi biết bài nào đã xong và còn bao nhiêu phút hôm nay. | Progress phản ánh kết quả một lần, đổi ngày theo múi giờ của tôi. | FR-PROG-001 |
| US-07 | Là người học từ mới, tôi lưu đúng nghĩa và xem ví dụ để nhớ cách dùng. | Một sense có một marker. Chọn đưa vào ôn tạo một card cho mỗi chiều. Mở nghĩa và audio khi có. | FR-VOCAB-001 |
| US-08 | Là người học quay lại, tôi ôn từ đến hạn để ghi nhớ lâu hơn. | Lật card, chấm mức nhớ, thấy queue giảm và thời điểm tới hạn kế. | FR-SRS-001 |
| US-09 | Là người hay nhầm thì, tôi đọc giải thích, làm bài và thấy lý do sai. | Dẫn về ví dụ đúng. Bài lý thuyết vẫn đọc được nếu exercise không tải. | FR-GRAM-001 |
| US-10 | Là người đọc gặp cụm lạ, tôi tra cả cụm và nghe giọng mẫu. | Autocomplete dùng được bằng keyboard và kết quả đúng sense/cụm. | FR-DICT-001 |
| US-11 | Là người đang đọc, tôi bật song ngữ theo nhu cầu và tra từ ngay. | Giữ đoạn hiện tại khi đổi chế độ, quay lại đúng từ sau đóng popover. | FR-READ-001 |
| US-12 | Là người dịch bài, tôi muốn thử diễn đạt của mình và xem bài mẫu/rubric sau nộp. | Lịch sử lưu đúng chiều, bản nháp phục hồi và coverage hiển thị. | FR-TRANS-001 |
| US-13 | Là người học nghe, tôi tua từ phụ đề và làm quiz để kiểm tra hiểu. | Cue tua đúng đoạn, phụ đề bật/tắt và kết quả có lời giải. | FR-VIDEO-001 |
| US-14 | Là người nghe chưa kịp, tôi lặp một đoạn rồi gõ để sửa chỗ nghe sai. | Chọn tốc độ, replay, thấy khác biệt, retry không chấm hai lần. | FR-DICTATION-001 |
| US-15 | Là người hay nhầm hai âm, tôi đối chiếu cặp tối thiểu để phân biệt. | Bảng IPA theo accent, bài chọn nghe có giải thích. | FR-IPA-001 |
| US-16 | Là người luyện nói, tôi phát lại bản tự ghi để đối chiếu với mẫu. | Điều khiển rõ tắt mic, bản ghi local và chỉ nghe vẫn dùng được. | FR-SHADOW-001 |
| US-17 | Là người cần chấm diễn đạt, tôi yêu cầu góp ý AI theo tiêu chí rõ. | Có trạng thái chờ, limit và fallback. Điểm tham khảo không thay quyền học. | FR-AI-001 |
| US-18 | Là người đặt động lực nhỏ, tôi biết điều gì được ghi nhận qua XP và streak. | Thấy điều kiện/lịch sử. Hoàn tất trùng không nhân điểm. | FR-GAME-001 |
| US-19 | Là người học thay đổi lịch, tôi chỉnh thiết lập hoặc yêu cầu xuất/xóa dữ liệu của mình. | Form hướng dẫn khi lỗi. Lịch sử ngày giữ đúng. Export/erase yêu cầu nhập lại mật khẩu, erase có xác nhận riêng, export dùng link riêng tư ngắn hạn. | FR-SET-001 |
| US-20 | Là người chủ động kết bạn, tôi kiểm soát chia sẻ tiến độ của mình. | Opt-in, block, giới hạn hồ sơ, và gặp tài khoản ẩn thì không lộ thông tin. | FR-SOC-001 |
| US-21 | Là người gặp lỗi nội dung, tôi báo đúng bài để nhóm xử lý. | Xem số báo cáo, không tự gửi dữ liệu học riêng. | FR-HELP-001 |

## Hành trình có nhánh

**Buổi đầu trong 10 phút** · Landing → demo một câu → gửi email → mở link → đặt tên/mật khẩu và xác minh → đăng nhập → chọn CEFR/kỳ thi tùy chọn/múi giờ/ngôn ngữ → dashboard → roadmap → lesson → play → nộp → feedback → hoàn tất. Nếu email muộn, gửi lại sau cooldown. Nếu mất mạng sau submit, retry với khóa cũ và hiển thị kết quả server. Hoàn tất quay về mục tiêu ngày và bài kế. US-01, US-02, US-03, US-05, US-06.

**Buổi ôn ngắn** · Dashboard có thẻ đến hạn → Review → tự nhớ → lật → rate → card tiếp → empty kèm lần đến hạn. Hai thiết bị cùng card thì thiết bị trễ nhận trạng thái mới. Sau tra từ điển hoặc bài đọc, lưu sense vào cùng kho, rồi đưa vào ôn theo chiều mà không tạo thẻ trùng. US-07, US-08, US-10.

**Từ đọc sang dịch** · Catalog → bài đọc → hiển thị song ngữ → từ ngữ cảnh → chọn chiều → lưu nháp → nộp → phản hồi/lịch sử. Phiên bản V2 cho yêu cầu góp ý ngữ nghĩa từ kết quả. Nếu chưa có bản dịch, bản Anh vẫn đọc được. US-10, US-11, US-12, US-17.

**Nghe và nói** · Video → phụ đề → chọn cue → Dictation, Quiz hoặc Shadowing. Trong IPA, chọn accent → phoneme → minimal pair. Nếu mic không có quyền, giữ mẫu, transcript và tiếp tục nghe. US-13, US-14, US-15, US-16.

**Duyệt một bài** · Import → staging → lỗi theo dòng hoặc nháp hợp lệ → preview → xin duyệt → người khác approve → admin publish → learner truy cập phiên bản mới. Báo lỗi gắn version hiện tại. Đã mở run cũ đi tiếp trên version được pin. US-04, US-21.

**Giá trị học và quyền riêng tư** · Tiến độ → xem mục tiêu/gamification → điều chỉnh mục tiêu ngày từ Sprint 4 hoặc đổi múi giờ trong Settings. Xuất/xóa dữ liệu → nhập lại mật khẩu → xác nhận nếu xóa → theo dõi job khi vẫn có phiên → dùng link riêng tư ngắn hạn nếu xuất. Nếu bật xã hội, chọn giới hạn chia sẻ trước khi kết bạn, có block. US-06, US-18, US-19, US-20.

[Tiêu chí chấp nhận](04-acceptance-criteria.md) · [SRS](02-SRS.md) · [Roadmap sprint](../plans/00-master-roadmap.md)
