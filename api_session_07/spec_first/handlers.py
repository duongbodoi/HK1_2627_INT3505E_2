# handlers.py
import time
import uuid
import jwt

SECRET = "dev-secret-chi-dung-de-demo-0123456789"   # >= 32 ký tự để PyJWT không cảnh báo

# ---- Dữ liệu giả (thay cho DB) ----
USERS = {
    "duong": {"password": "123456", "scope": "read:posts"},   # có quyền xem bài
    "guest": {"password": "123456", "scope": ""},             # không có scope → demo 403
}
REFRESH_TOKENS = {}   # refreshToken -> username

POSTS = {
    101: {
        "id": 101,
        "authorId": 7,
        "content": "Hôm nay trời đẹp quá!",
        "visibility": "public",
        "likeCount": 12,
        "commentCount": 3,
        "createdAt": "2026-10-26T15:30:00Z",
    },
    # Cố tình thiếu 'visibility', 'createdAt' → demo validate_responses trả 500
    102: {"id": 102, "authorId": 7, "content": "Bài viết lỗi"},
}


# ---- Security: x-tokenInfoFunc ----
def token_info(token):
    """Connexion gọi hàm này với token sau 'Bearer '.
    Trả None → 401. Thiếu scope yêu cầu → connexion tự trả 403."""
    try:
        payload = jwt.decode(token, SECRET, algorithms=["HS256"])
    except jwt.PyJWTError:
        return None
    return {"sub": payload["sub"], "scope": payload.get("scope", "").split()}


def _issue_tokens(username):
    access = jwt.encode(
        {"sub": username, "scope": USERS[username]["scope"], "exp": int(time.time()) + 3600},
        SECRET,
        algorithm="HS256",
    )
    refresh_token = str(uuid.uuid4())
    REFRESH_TOKENS[refresh_token] = username
    return {
        "accessToken": access,
        "refreshToken": refresh_token,
        "tokenType": "Bearer",
        "expiresIn": 3600,
    }


# ---- POST /auth/login ----
def login(body):
    # body đã được connexion validate theo schema Login
    user = USERS.get(body["username"])
    if user is None or user["password"] != body["password"]:
        return {"code": "INVALID_CREDENTIALS",
                "message": "Tên đăng nhập hoặc mật khẩu không đúng."}, 401
    return _issue_tokens(body["username"]), 200


# ---- POST /auth/refresh ----
def refresh(body):
    username = REFRESH_TOKENS.pop(body["refreshToken"], None)   # pop: mỗi refresh token dùng 1 lần
    if username is None:
        return {"code": "INVALID_TOKEN",
                "message": "Refresh token không hợp lệ hoặc đã dùng."}, 401
    return _issue_tokens(username), 200


# ---- GET /posts/{id} ----
def get_post(id, user):
    # id: connexion đã ép kiểu int và kiểm tra minimum: 1
    # user: giá trị 'sub' lấy từ token_info
    post = POSTS.get(id)
    if post is None:
        return {"code": "NOT_FOUND", "message": f"Không tìm thấy bài viết {id}."}, 404
    return post, 200