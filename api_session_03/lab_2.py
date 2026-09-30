import logging
from flask import Flask, request, jsonify
from werkzeug.exceptions import HTTPException

app = Flask(__name__)
# Cấu hình log cơ bản
logging.basicConfig(level=logging.ERROR)

# 1. Định nghĩa ProblemError ngắn gọn
class ProblemError(Exception):
    def __init__(self, status, title, detail):
        self.status = status
        self.title = title
        self.detail = detail

# 2. Xử lý ProblemError
@app.errorhandler(ProblemError)
def handle_problem(e):
    payload = {
        "type": "about:blank",
        "title": e.title,
        "status": e.status,
        "detail": e.detail,
        "instance": request.path
    }
    # Trả về JSON
    return jsonify(payload), e.status, {'Content-Type': 'application/problem+json'}

# 3. Fallback cho HTTPException (Lỗi 404, 405 của Flask...)
@app.errorhandler(HTTPException)
def handle_http_exception(e):
    payload = {
        "type": "about:blank",
        "title": e.name,
        "status": e.code,
        "detail": e.description,
        "instance": request.path
    }
    return jsonify(payload), e.code, {'Content-Type': 'application/problem+json'}

# 4. Bắt các Exception chưa lường trước (Lỗi 500)
@app.errorhandler(Exception)
def handle_exception(e):
    # Dùng logging.exception để tự động ghi log lỗi kèm stack trace trên server
    logging.exception("Unhandled Exception:") 
    
    payload = {
        "type": "about:blank",
        "title": "Internal Server Error",
        "status": 500,
        "detail": "Lỗi hệ thống máy chủ.",
        "instance": request.path
    }
    return jsonify(payload), 500, {'Content-Type': 'application/problem+json'}

# --- Route kiểm thử ---
@app.route('/resources/<int:id>')
def get_resource(id):
    raise ProblemError(404, "Not Found", f"Không tìm thấy resource {id}")

if __name__ == '__main__':
    app.run(debug=True)