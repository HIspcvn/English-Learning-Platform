# Sprint 08 — Video và dictation

> PROPOSED · V1 · Các đường dẫn code bên dưới là vị trí dự kiến.

## Mục tiêu và phạm vi

Phát video có transcript đồng bộ và tạo bài nghe chép lại từ nguồn đã cấp quyền.

- **Phạm vi** Catalog/video/player, caption song ngữ, click-to-seek/loop/speed, luyện dictation.
- **Tiền điều kiện và phụ thuộc** [Sprint 02](sprint-02.md) cho publish và media readiness, [Sprint 03](sprint-03.md) cho engine và run.
- **Tính năng** FR-VIDEO-001, FR-DICTATION-001.
- **Đặc tả giao diện** [SRS](../requirements/02-SRS.md), [API](../architecture/05-api-specification.md), [ERD](../architecture/04-database-design.md).

## Công việc theo lớp

| Lớp | Công việc |
|---|---|
| PostgreSQL | Video assets, transcript cues, versioned dictation exercises. |
| Backend | Manifest/transcript queries, signed URLs và reuse typing scorer. |
| Frontend | Player HTML5, keyboard controls, timeline, transcript và dictation. |
| Nội dung | Nội dung video tự sở hữu, VTT segment, source licenses. |
| Kiểm thử | Playback, cue boundary, loop, transcript lỗi, progress offline retry. |
| Bảo mật | URL ký hết hạn, asset scope, MIME/sniff, không tải media của bên thứ ba trái quyền. |

## Task có thể review độc lập

### S08-01 — Media pipeline và transcript

- **Mục tiêu** Giữ metadata/cue có thể kiểm trước khi xuất bản.
- **Tệp và module** apps/api/app/media, apps/api/app/video, apps/api/tests/media
- **Đầu vào** Video có license, object key, VTT/cues, timebase.
- **Đầu ra** Ready media manifest và GET /videos/{lesson_id}/transcript.
- **Phụ thuộc** S02-03
- **Ưu tiên và ước lượng** P1 · 3–5 ngày developer.
- **Hướng dẫn triển khai** Normalize millisecond cues, validate monotonic bounds, kiểm tra upload một lần và manifest scope.
- **Ca kiểm thử** Bad range, overlap ngoài quy tắc, encoding, signed URL hết hạn.
- **Nghiệm thu** CMS không publish nếu asset/cue chưa ready; transcript order ổn định.
- **Commit đề xuất** `feat: version video cues and media manifests`.

- [ ] Viết ca kiểm thử nêu trên và kiểm tra lỗi đặc trưng trước thay đổi.
- [ ] Hoàn thành đầu ra, chạy ca kiểm thử liên quan và đối chiếu nghiệm thu.
- [ ] Gửi thay đổi và bằng chứng chạy kiểm thử để review.

### S08-02 — Player, subtitle và luyện nghe

- **Mục tiêu** Đồng bộ controls và bài dictation.
- **Tệp và module** apps/web/features/video, apps/api/app/exercises, apps/web/tests/e2e
- **Đầu vào** Signed video, cue list, dictation run contract.
- **Đầu ra** Player check trạng thái media, cue select/repeat và correct/wrong feedback.
- **Phụ thuộc** S08-01, S03-02
- **Ưu tiên và ước lượng** P1 · 4–6 ngày developer.
- **Hướng dẫn triển khai** Dùng events native player và cue IDs, giữ tốc độ giữa seek, không gửi answer key từ transcript restricted mode trước hint.
- **Ca kiểm thử** Seek đầu/cuối, playback fail, tốc độ, mobile inline, dictation retry/reload.
- **Nghiệm thu** Người học tìm và replay cue, sau đó hoàn thành dictation.
- **Commit đề xuất** `feat: deliver transcript-driven video practice`.

- [ ] Viết ca kiểm thử nêu trên và kiểm tra lỗi đặc trưng trước thay đổi.
- [ ] Hoàn thành đầu ra, chạy ca kiểm thử liên quan và đối chiếu nghiệm thu.
- [ ] Gửi thay đổi và bằng chứng chạy kiểm thử để review.

## Điều kiện hoàn tất

- **Nghiệm thu sprint** Seek theo câu, luyện và tiếp tục sau refresh; video mất kết nối vẫn có transcript nếu được phép.
- **Bàn giao** Các task trên đã được review, bản trình diễn staging và bằng chứng kiểm thử đính kèm. Migration có hướng nâng cấp và hướng khôi phục khi sprint thay đổi schema.
- **Rủi ro dự kiến** Cue drift và lỗi seek trên Safari mobile.

[Lộ trình và điều kiện phát hành](00-master-roadmap.md) · [Ma trận kiểm thử](../testing/02-test-cases.md)

