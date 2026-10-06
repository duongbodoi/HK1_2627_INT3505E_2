# Ví dụ bộ api album trong webApi sprotify
| API | URL | 05. Error response có cấu trúc | 06. Pagination rõ ràng |
| :--- | :--- | :--- | :--- |
| Get Album |GET /albums/{id} |Không|Có|
| Get Several Albums |GET /albums |Không|Có|
| Get Album Tracks |GET /albums/{id}/tracks|Không|Có|
| Get User's Saved Albums |GET /me/albums |Không|Có|
| Save Albums for Current User |PUT /me/albums |Không|-|
| Remove Users' Saved Albums |DELETE /me/albums |Không|-|
| Check User's Saved Albums |GET /me/albums/contains |Không|Có|
| Get New Releases |GET /browse/new-releases |Không|Có|
# Tiêu chí 5
- Nhận xét: Mặc dù API có trả về một cấu trúc lỗi rõ ràng (structured error), nhưng nó **không tuân thủ chuẩn RFC 7807** như tiêu chí 05 đã đề ra. Nó thiếu hoàn toàn các trường định danh cơ bản của RFC 7807 là `type`, `title`, `detail`, và `instance`.
=> Kết luận không đạt
- VD:
![alt text](image-7.png)
# Tiêu chí 6
- Pagination rõ ràng, API đã triển khai cơ chế Offset-based Pagination (Phân trang theo offset) rất chuẩn mực và đầy đủ thông tin cho collection. Ngoài ra còn có limit để giới hạn số trang, total tổng số lượng, hết hợp href, prev,next thể hiện các url nghiệp vụ tương ứng
- VD:
![alt text](image-8.png)