# BÁO CÁO BÀI TẬP: AUDIT PUBLIC API 
**Đối tượng Audit:** Stripe API (`https://api.stripe.com/v1`)  
**Tài liệu tham khảo:** Stripe API Reference  

---

## I. TỔNG QUAN
Stripe API cung cấp giao diện tích hợp thanh toán cho các ứng dụng. API này được thiết kế dựa trên kiến trúc REST, định hướng theo tài nguyên (resource-oriented), sử dụng mã trạng thái HTTP tiêu chuẩn và xác thực qua Basic Auth. 

Dưới đây là phần kiểm toán (audit) 5 endpoint liên quan đến tài nguyên `customers` (Khách hàng).

---

## II. CHI TIẾT AUDIT ENDPOINTS

### 1. Tạo mới một khách hàng (Create a Customer)
* **Endpoint:** `/v1/customers`
* **Method:** `POST`
* **Headers tiêu chuẩn:**
  * `Authorization: Bearer <API_SECRET_KEY>`
  * `Content-Type: application/x-www-form-urlencoded`
* **Status Code:**
  * `200 OK`: Tạo thành công (Stripe trả về 200 thay vì 201).
  * `400 Bad Request`: Thiếu tham số bắt buộc hoặc sai định dạng.
  * `401 Unauthorized`: API key không hợp lệ.
* **Đánh giá tính RESTful:** **Khá RESTful nhưng có ngoại lệ.** 
  * *Điểm chuẩn:* Sử dụng danh từ số nhiều `/customers` làm tài nguyên và `POST` để tạo mới. 
  * *Điểm chưa chuẩn:* Theo chuẩn REST nghiêm ngặt, việc tạo tài nguyên mới nên trả về HTTP Status `201 Created`, tuy nhiên Stripe chọn việc làm phẳng (flatten) các mã thành công về `200 OK`.

### 2. Truy xuất thông tin một khách hàng (Retrieve a Customer)
* **Endpoint:** `/v1/customers/{customer_id}`
* **Method:** `GET`
* **Headers tiêu chuẩn:**
  * `Authorization: Bearer <API_SECRET_KEY>`
* **Status Code:**
  * `200 OK`: Trả về JSON chứa thông tin chi tiết của customer.
  * `404 Not Found`: Không tìm thấy `customer_id` tương ứng.
* **Đánh giá tính RESTful:** **Hoàn toàn RESTful.**
  * Định danh tài nguyên rõ ràng qua URI path variable (`{customer_id}`).
  * Method `GET` đảm bảo tính an toàn (safe) và không trạng thái (idempotent), không gây thay đổi dữ liệu trên server.

### 3. Cập nhật thông tin khách hàng (Update a Customer)
* **Endpoint:** `/v1/customers/{customer_id}`
* **Method:** `POST`
* **Headers tiêu chuẩn:**
  * `Authorization: Bearer <API_SECRET_KEY>`
  * `Content-Type: application/x-www-form-urlencoded`
* **Status Code:**
  * `200 OK`: Cập nhật thành công.
  * `400 Bad Request`: Tham số cập nhật không hợp lệ.
* **Đánh giá tính RESTful:** **Vi phạm nguyên tắc RESTful.**
  * *Phân tích:* Theo chuẩn HTTP/REST, để cập nhật một phần tài nguyên, method phù hợp nhất là `PATCH` (hoặc `PUT` nếu thay thế toàn bộ). Tuy nhiên, đặc thù thiết kế của Stripe là **chỉ sử dụng GET, POST và DELETE**. Họ dùng `POST` cho cả việc tạo mới và cập nhật. Dù điều này mang lại sự đơn giản cho các hệ thống cũ không hỗ trợ `PATCH/PUT`, nhưng xét theo lý thuyết REST, đây là một điểm không tuân thủ.

### 4. Xóa một khách hàng (Delete a Customer)
* **Endpoint:** `/v1/customers/{customer_id}`
* **Method:** `DELETE`
* **Headers tiêu chuẩn:**
  * `Authorization: Bearer <API_SECRET_KEY>`
* **Status Code:**
  * `200 OK`: Xóa thành công (trả về JSON xác nhận: `{"id": "cus_123", "deleted": true}`).
  * `404 Not Found`: Khách hàng không tồn tại để xóa.
* **Đánh giá tính RESTful:** **Gần chuẩn RESTful.**
  * Sử dụng đúng HTTP verb `DELETE` cho hành động xóa tài nguyên.
  * *Điểm đáng lưu ý:* Nhiều RESTful API tiêu chuẩn thích trả về `204 No Content` khi xóa thành công. Stripe trả về `200 OK` kèm theo một object báo hiệu trạng thái `deleted: true`. Cách tiếp cận này mang tính thực tiễn cao nhưng hơi lệch so với sách giáo khoa REST.

### 5. Lấy danh sách khách hàng (List all Customers)
* **Endpoint:** `/v1/customers`
* **Method:** `GET`
* **Headers tiêu chuẩn:**
  * `Authorization: Bearer <API_SECRET_KEY>`
* **Status Code:**
  * `200 OK`: Trả về một object danh sách (list) chứa mảng các khách hàng.
* **Đánh giá tính RESTful:** **Hoàn toàn RESTful.**
  * Endpoint đại diện cho collection of resources (`/customers`).
  * Hỗ trợ phân trang, lọc và sắp xếp thông qua Query Parameters (ví dụ: `?limit=3&email=test@example.com`), đúng với nguyên tắc kiến trúc đồng nhất (Uniform Interface) của REST.

---

## III. KẾT LUẬN VỀ KIẾN TRÚC API
Stripe là một API mang tính thực tiễn (Pragmatic REST) thay vì tuân thủ cứng nhắc (Pure REST). Mặc dù có những điểm vi phạm về mặt lý thuyết như việc sử dụng `POST` thay cho `PATCH/PUT` hoặc chuẩn hóa mọi phản hồi thành công thành `200 OK`, thiết kế này đảm bảo sự ổn định, dễ đoán và dễ tích hợp cho mọi nền tảng backend hiện nay.