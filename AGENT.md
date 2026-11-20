# Bàn giao task qua GitHub

Khi hoàn thành một task trong repository này:

1. Chạy các kiểm tra phù hợp với thay đổi và ghi kết quả thực tế. Chỉ stage và commit các tệp thuộc task, giữ nguyên thay đổi ngoài phạm vi.
2. Đẩy nhánh thực hiện lên `origin` bằng push thông thường. Nếu đang ở `main`, tạo nhánh cho task trước khi đẩy. Nếu remote đã có thay đổi, kiểm tra và tích hợp an toàn trước khi thử lại.
3. Mở pull request từ nhánh đó vào `main`, hoặc cập nhật PR đang mở của nhánh. Tóm tắt thay đổi, cách kiểm tra và các cổng còn chờ. Báo lại URL PR, commit và trạng thái CI đã xác minh.

Mặc định thực hiện push và mở PR ngay khi task đã qua kiểm tra, không cần hỏi lại. Việc merge do người dùng quyết định. Tuân thủ mọi giới hạn Git mà người dùng nêu riêng cho task hiện tại.
