# Sprint 09 — IPA và shadowing

> PROPOSED · V1 · Các đường dẫn code bên dưới là vị trí dự kiến.

## Mục tiêu và phạm vi

Cho người học nghe mẫu, đọc IPA và tự so sánh bản ghi trong phiên. Mở tổ hợp Nghe & nói Nâng cao của Gõ câu ở V1.

- **Phạm vi** IPA, phát mẫu, ghi/phát cục bộ, shadowing theo cue và Gõ câu `listen_speak/advanced` với `practice_ack`. Chấm tự động là lựa chọn V2.
- **Tiền điều kiện và phụ thuộc** [Sprint 03](sprint-03.md) cho run và lane Gõ câu, [Sprint 06](sprint-06.md) cho từ điển, [Sprint 08](sprint-08.md) cho player và cue.
- **Tính năng** FR-IPA-001, FR-SHADOW-001, FR-TYPE-001 (Nghe & nói).
- **Đặc tả giao diện** [SRS](../requirements/02-SRS.md), [API](../architecture/05-api-specification.md), [ERD](../architecture/04-database-design.md).

## Công việc theo lớp

| Lớp | Công việc |
|---|---|
| PostgreSQL | IPA và audio tham chiếu theo asset; run Nghe & nói dùng snapshot cùng lane model S03. |
| Backend | Đọc IPA, mở lane Nghe & nói ở Nâng cao, chấp nhận self-ack theo item/revision và completion unscored. |
| Frontend | IPA chart, phoneme detail, permission denied và reference/speech playback. |
| Nội dung | IPA UK/US có editorial review và recording cùng license. |
| Kiểm thử | Permission deny/allow, thời lượng, thiết bị, cleanup, quyền run và QA-TYPE-17. |
| Bảo mật | Xin phép mic khi người học bấm, dừng stream khi rời màn. Bản ghi ở lại thiết bị. |

## Task có thể review độc lập

### S09-01 — Bảng IPA và bài mẫu

- **Mục tiêu** Tạo đường dẫn từ IPA đến ví dụ được duyệt.
- **Tệp và module** apps/api/app/pronunciation, apps/web/features/pronunciation, apps/api/tests/pronunciation
- **Đầu vào** Phoneme, IPA symbol, accent, example, asset availability.
- **Đầu ra** IPA chart và trang chi tiết, fallback audio.
- **Phụ thuộc** S06-02, S08-01
- **Ưu tiên và ước lượng** P1 · 2–4 ngày developer.
- **Hướng dẫn triển khai** Gắn language attribute đúng, phát theo user gesture, accent chỉ khi có nguồn.
- **Ca kiểm thử** IPA combining chars, audio unavailable, navigation keyboard.
- **Nghiệm thu** Biểu tượng có nhãn đọc được và chọn qua desktop/mobile.
- **Commit đề xuất** `feat: present curated pronunciation practice`.

- [ ] Viết ca kiểm thử nêu trên và kiểm tra lỗi đặc trưng trước thay đổi.
- [ ] Hoàn thành đầu ra, chạy ca kiểm thử liên quan và đối chiếu nghiệm thu.
- [ ] Gửi thay đổi và bằng chứng chạy kiểm thử để review.

### S09-02 — Ghi âm cục bộ cho shadowing và Nghe & nói

- **Mục tiêu** Nghe mẫu và so sánh bản ghi trên browser hỗ trợ, giữ luồng tự luyện khi mic bị từ chối.
- **Tệp và module** `apps/web/features/shadowing/`, `apps/web/features/typing/`, `apps/web/app/(learn)/learn/[runId]/`, `apps/web/tests/e2e/`, `apps/api/app/learning/`
- **Đầu vào** Cue hoặc item Gõ câu, audio tham chiếu đã duyệt, capability MediaRecorder và consent cục bộ.
- **Đầu ra** Ghi/phát/revoke cục bộ và self-ack từng item Nghe & nói. Completion hiển thị tiến độ thực hành, điểm/mastery null và XP 0.
- **Phụ thuộc** S03-02, S09-01, S08-02
- **Ưu tiên và ước lượng** P1 · 4–5 ngày developer.
- **Hướng dẫn triển khai** Giới hạn thời lượng, một stream, cleanup object URL. Dừng tracks khi stop/rời trang. Lane Nghe & nói chỉ có Nâng cao, API nhận lệnh `practice_ack` có item/revision/key. Learner có thể nghe và tự xác nhận khi thiếu mic.
- **Ca kiểm thử** QA-TYPE-17. Kiểm deny/no-device, xin lại quyền, dừng nguồn, chạm giới hạn thời lượng, nộp lại key và tiến độ vẫn giữ khi reload.
- **Nghiệm thu** Cả hai luồng phát audio đã duyệt và có fallback mic. Nghe & nói hoàn tất bằng self-ack, không upload bản ghi, không cấp XP hoặc lưu từ tự động.
- **Commit đề xuất** `feat: add privacy-first shadowing recorder`.

- [ ] Viết ca kiểm thử nêu trên và kiểm tra lỗi đặc trưng trước thay đổi.
- [ ] Hoàn thành đầu ra, chạy ca kiểm thử liên quan và đối chiếu nghiệm thu.
- [ ] Gửi thay đổi và bằng chứng chạy kiểm thử để review.

## Điều kiện hoàn tất

- **Nghiệm thu sprint** Người học replay mẫu/bản ghi cục bộ và hoàn tất Nghe & nói Nâng cao nhờ tự xác nhận. Khi từ chối mic, audio mẫu và self-ack vẫn hoạt động. [Ca kiểm thử theo feature](../testing/02-test-cases.md)
- **Bàn giao** Các task trên đã được review, bản trình diễn staging và bằng chứng kiểm thử đính kèm. Migration có hướng nâng cấp và hướng khôi phục khi sprint thay đổi schema.
- **Rủi ro dự kiến** Khả năng codec/MediaRecorder khác nhau và thu âm ngoài ý muốn.

[Lộ trình và điều kiện phát hành](00-master-roadmap.md) · [Ma trận kiểm thử](../testing/02-test-cases.md)

