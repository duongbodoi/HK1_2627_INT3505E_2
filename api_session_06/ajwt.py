from flask import Flask, request, jsonify
from flask_jwt_extended import (
    JWTManager, create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity, get_jwt
)
import bcrypt
import os

app = Flask(__name__)

# 1. Cấu hình ứng dụng và JWT
app.config.update(
    SECRET_KEY=os.environ.get("FLASK_SECRET_KEY", "flask-secret-key-default"),
    JWT_SECRET_KEY=os.environ.get("JWT_SECRET_KEY", "jwt-secret-key-default"),
    JWT_ACCESS_TOKEN_EXPIRES=900,         # Access token sống 15 phút (900s)
    JWT_REFRESH_TOKEN_EXPIRES=2592000,    # Refresh token sống 30 ngày
    JWT_ALGORITHM="HS256"                 # Thuật toán mã hóa HS256
)

jwt = JWTManager(app)

# Giả lập CSDL users
# Mật khẩu gốc cho user này là: "secret123"
_hashed_password = bcrypt.hashpw(b"secret123", bcrypt.gensalt())
_users_db = {
    "an@vnu.edu.vn": {
        "id": 1,
        "email": "an@vnu.edu.vn",
        "pwd_hash": _hashed_password
    }
}

# Giả lập hàm lấy quyền hạn từ DB
def load_permissions(user_id):
    return {
        "roles": ["user"],
        "scopes": ["orders:read", "orders:write"]
    }

# Giả lập hàm lấy dữ liệu đơn hàng
def orders_by_owner(user_id):
    return [
        {"order_id": 101, "item": "Laptop Dell", "owner_id": user_id},
        {"order_id": 102, "item": "Bàn phím cơ", "owner_id": user_id}
    ]


# 2. API Đăng nhập (/api/auth/login)
@app.post("/api/auth/login")
def login():
    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password", "").encode()

    user = _users_db.get(email)
    
    # Kiểm tra user và mật khẩu
    if not user or not bcrypt.checkpw(password, user["pwd_hash"]):
        return jsonify(error="invalid_credentials"), 401

    claims = load_permissions(user["id"])
    uid = str(user["id"])

    # Cấp access token và refresh token
    return jsonify(
        access=create_access_token(identity=uid, additional_claims=claims),
        refresh=create_refresh_token(identity=uid, additional_claims=claims)
    ), 200


# 3. API Bảo vệ tài nguyên (/api/orders)
@app.get("/api/orders")
@jwt_required()  # Bắt buộc đính kèm Access Token
def list_orders():
    uid = get_jwt_identity()
    claims = get_jwt()

    # Kiểm tra quyền "orders:read" trong claims
    if "orders:read" not in claims.get("scopes", []):
        return jsonify(error="insufficient_scope"), 403

    return jsonify(orders_by_owner(uid)), 200


# 4. API Gia hạn Token (/api/auth/refresh)
@app.post("/api/auth/refresh")
@jwt_required(refresh=True)  # Bắt buộc đính kèm Refresh Token
def refresh():
    current_user_id = get_jwt_identity()
    claims = load_permissions(current_user_id)

    # Cấp lại Access Token mới
    new_access_token = create_access_token(
        identity=current_user_id, additional_claims=claims
    )
    return jsonify(access=new_access_token), 200


if __name__ == "__main__":
    app.run(debug=True, port=5000)