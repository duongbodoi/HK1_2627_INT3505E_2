import sqlite3
from flask import Flask, request, jsonify, make_response, g

app = Flask(__name__)
DATABASE = 'database.db'

# 1. Hàm khởi tạo và lấy kết nối database
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        # Thiết lập row_factory để cursor trả về dữ liệu dạng dict thay vì tuple
        db.row_factory = sqlite3.Row
    return db

# 2. Tự động đóng database sau khi xử lý xong mỗi request
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# 3. Tạo bảng tự động khi chạy app nếu bảng chưa tồn tại
def init_db():
    with app.app_context():
        db = get_db()
        db.execute('''
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                author TEXT NOT NULL
            )
        ''')
        db.commit()

# Gọi hàm khởi tạo bảng
init_db()

# ─── GET /books —— trả danh sách
@app.route("/books", methods=["GET"])
def list_books():
    db = get_db()
    cursor = db.execute('SELECT id, title, author FROM books')
    # Ép kiểu dữ liệu sqlite3.Row thành dict để JSONify
    books = [dict(row) for row in cursor.fetchall()]
    
    return jsonify({
        "data": books,
        "total": len(books)
    }), 200

# ─── Bổ sung: GET /books/<oid> —— lấy thông tin 1 phần tử
@app.route("/books/<int:oid>", methods=["GET"])
def get_book(oid):
    db = get_db()
    cursor = db.execute('SELECT id, title, author FROM books WHERE id = ?', (oid,))
    row = cursor.fetchone()
    
    if row is None:
        return jsonify({"error": "Book not found"}), 404
        
    return jsonify(dict(row)), 200

# ─── POST /books —— tạo mới
@app.route("/books", methods=["POST"])
def create_book():
    if not request.is_json:
        return jsonify({"error":"expected JSON"}), 415 

    body = request.get_json(silent=True) or {}
    title = body.get("title", "").strip()
    author = body.get("author", "").strip()
    
    if not title or not author:
        return jsonify({"error":"Bạn cần nhập title và author"}), 422 
        
    db = get_db()
    # Sử dụng query parameters (?) để chống SQL Injection
    cursor = db.execute(
        'INSERT INTO books (title, author) VALUES (?, ?)',
        (title, author)
    )
    db.commit()
    
    # Lấy ID của record vừa được insert
    new_id = cursor.lastrowid
    
    book = {
        "id": new_id,
        "title": title,
        "author": author
    }
    
    resp = make_response(jsonify(book), 201)
    resp.headers["Location"] = f"/books/{new_id}"
    return resp

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)