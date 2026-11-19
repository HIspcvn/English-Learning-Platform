# Sprint 09 — IPA và shadowing

> PROPOSED · V1 · Các đường dẫn code bên dưới là vị trí dự kiến.

## Mục tiêu và phạm vi

Cho người học nghe mẫu, đọc IPA và tự so sánh bản ghi trong phiên.

- **Phạm vi** Phoneme set, example audio, record/playback, video cue shadowing; chấm phát âm sau.
- **Tiền điều kiện và phụ thuộc** [Sprint 06](sprint-06.md), [Sprint 08](sprint-08.md)
- **Tính năng** FR-IPA-001, FR-SHADOW-001.
- **Đặc tả giao diện** [SRS](../requirements/02-SRS.md), [API](../architecture/05-api-specification.md), [ERD](../architecture/04-database-design.md).

## Công việc theo lớp

| Lớp | Công việc |
|---|---|
| PostgreSQL | Pronunciation examples mapped to assets; local recordings mặc định. |
| Backend | Read IPA corpus, client media capability hints, record progress khi hoàn tất hoạt động. |
| Frontend | IPA chart, phoneme detail, permission denied và reference/speech playback. |
| Nội dung | IPA UK/US có editorial review và recording cùng license. |
| Kiểm thử | Permission deny/allow, duration bound, browser unsupported, cleanup memory. |
| Bảo mật | Xin phép mic khi user bấm, dừng streams khi rời màn, local-only mặc định. |

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

### S09-02 — Ghi âm so sánh shadowing

- **Mục tiêu** Đi hết vòng record/replay bằng browser.
- **Tệp và module** apps/web/features/shadowing, apps/web/tests/e2e, apps/api/app/progress
- **Đầu vào** Active cue, supported MediaRecorder, local consent.
- **Đầu ra** Record state, secured local audio/revoke, completion event.
- **Phụ thuộc** S09-01, S08-02
- **Ưu tiên và ước lượng** P1 · 4–5 ngày developer.
- **Hướng dẫn triển khai** Giới hạn thời lượng, một stream, cleanup object URL; điều hướng hoặc stop đóng tracks.
- **Ca kiểm thử** Denied, no device, permission later, pause source, max duration.
- **Nghiệm thu** Nghe mẫu và bản ghi trên browser được hỗ trợ, có fallback nếu thiết bị từ chối.
- **Commit đề xuất** `feat: add privacy-first shadowing recorder`.

- [ ] Viết ca kiểm thử nêu trên và kiểm tra lỗi đặc trưng trước thay đổi.
- [ ] Hoàn thành đầu ra, chạy ca kiểm thử liên quan và đối chiếu nghiệm thu.
- [ ] Gửi thay đổi và bằng chứng chạy kiểm thử để review.

## Điều kiện hoàn tất

- **Nghiệm thu sprint** Nghe mẫu và phát bản ghi cục bộ; mic bị từ chối vẫn dùng nội dung đọc.
- **Bàn giao** Các task trên đã được review, bản trình diễn staging và bằng chứng kiểm thử đính kèm. Migration có hướng nâng cấp và hướng khôi phục khi sprint thay đổi schema.
- **Rủi ro dự kiến** Khả năng codec/MediaRecorder khác nhau và thu âm ngoài ý muốn.

[Lộ trình và điều kiện phát hành](00-master-roadmap.md) · [Ma trận kiểm thử](../testing/02-test-cases.md)

