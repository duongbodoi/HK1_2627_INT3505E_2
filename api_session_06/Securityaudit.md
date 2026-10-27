# Security Audit – API social-network

**Sinh viên:** Nguyễn Tùng Dương – 24021443

| # | Điểm có thể lộ | Endpoint | Mức độ | Khắc phục |
|---|---|---|---|---|
| 1 | **Brute-force mật khẩu**: thử liên tục nhiều mật khẩu | `POST /auth/login` | Cao | Rate limit, trả `429`; khóa tạm tài khoản sau nhiều lần sai |
| 2 | **User enumeration**: thông báo lỗi khác nhau làm lộ username tồn tại | `POST /auth/login` | Trung bình | Dùng chung lỗi `INVALID_CREDENTIALS` cho sai username và sai mật khẩu |
| 3 | **IDOR**: đổi `id` trên URL để xem bài `private` của người khác | `GET /posts/{id}` | Cao | Server kiểm tra `visibility` và quyền sở hữu; không đủ quyền trả `404` |
| 4 | **Refresh token bị đánh cắp và dùng lại** | `POST /auth/refresh` | Cao | Rotation (cấp token mới, hủy token cũ); lưu trong cookie `HttpOnly` |
| 5 | **JWT yếu**: chấp nhận `alg: none`, secret ngắn, hạn dùng dài | Endpoint cần token | Cao | Cố định thuật toán, secret mạnh, access token hạn ngắn |
| 6 | **Không kiểm tra scope**: token thiếu `read:posts` vẫn đọc được bài | `GET /posts/{id}` | Trung bình | Middleware kiểm tra scope, thiếu thì trả `403` |
| 7 | **Lộ thông tin qua lỗi 500**: trả stack trace, câu SQL | Mọi endpoint | Trung bình | Chỉ trả `ErrorResponse` chung, chi tiết ghi vào log nội bộ |
| 8 | **Lộ mật khẩu/token qua đường truyền và log** | Mọi endpoint | Cao | Bắt buộc HTTPS; che `password`, `token` trong log |