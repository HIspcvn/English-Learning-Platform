# Bàn giao task qua GitHub

## Khi bắt đầu task mới

1. Chạy `git status --short --branch` để kiểm tra nhánh và thay đổi local. Giữ nguyên các thay đổi đang làm và các commit trên nhánh task trước.
2. Chạy `git fetch origin`, chuyển sang `main` bằng `git switch main`, rồi cập nhật bằng `git merge --ff-only origin/main`. Xác nhận `git rev-parse main origin/main` trả về cùng một SHA. Nếu không thể chuyển nhánh an toàn hoặc hai SHA khác nhau, xử lý chênh lệch trước khi bắt đầu task.
3. Tạo nhánh riêng từ `main` đã đồng bộ bằng `git switch -c <ten-nhanh-task> main` trước khi sửa tệp. Chỉ dùng lại nhánh hiện có khi tiếp tục chính task của nhánh đó, ví dụ khi cập nhật PR theo review.

## Khi hoàn thành task

1. Chạy các kiểm tra phù hợp với thay đổi và ghi kết quả thực tế. Chỉ stage và commit các tệp thuộc task, giữ nguyên thay đổi ngoài phạm vi.
2. Đẩy nhánh thực hiện lên `origin` bằng push thông thường. Nếu đang ở `main`, tạo nhánh cho task trước khi đẩy. Nếu remote đã có thay đổi, kiểm tra và tích hợp an toàn trước khi thử lại.
3. Mở pull request từ nhánh đó vào `main`, hoặc cập nhật PR đang mở của nhánh. Tóm tắt thay đổi, cách kiểm tra và các cổng còn chờ. Báo lại URL PR, commit và trạng thái CI đã xác minh.

Mặc định thực hiện push và mở PR ngay khi task đã qua kiểm tra, không cần hỏi lại. Việc merge do người dùng quyết định. Tuân thủ mọi giới hạn Git mà người dùng nêu riêng cho task hiện tại.
