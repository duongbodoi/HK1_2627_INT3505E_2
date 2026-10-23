from flask import Flask, jsonify, request
from flask_httpauth import HTTPBasicAuth
import bcrypt

app = Flask(__name__)
auth = HTTPBasicAuth()

# KHÔNG BAO GIỜ lưu plaintext – hash khi khởi tạo
_users = {
    "an@vnu.edu.vn": bcrypt.hashpw(
        b"correct horse battery staple", bcrypt.gensalt())
}

@auth.verify_password
def verify_password(username, password):
    if username not in _users:
        return False
    stored = _users[username]
    pwd = (password.encode()
           if isinstance(password, str) else password)
    # Xác minh hash bằng thư viện
    return username if bcrypt.checkpw(pwd, stored) else None

# --- BỔ SUNG ROUTE ĐỂ TEST TRÊN POSTMAN ---

@app.route('/api/orders', methods=['GET'])
@auth.login_required  # Yêu cầu phải đi qua bước verify_password ở trên
def get_orders():
    # Lấy thông tin user hiện tại vừa xác thực thành công
    current_user = auth.current_user() 
    return jsonify({
        "status": "success",
        "message": f"Xin chào {current_user}, bạn đã truy cập tài nguyên bảo vệ thành công!",
        "data": [
            {"id": 1, "item": "Laptop", "price": 1500},
            {"id": 2, "item": "Mouse", "price": 25}
        ]
    }), 200

if __name__ == '__main__':
    # Chạy app ở chế độ Debug trên port 5000
    app.run(debug=True, port=5000)