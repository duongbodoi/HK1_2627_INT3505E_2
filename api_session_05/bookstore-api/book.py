import json
import os
import base64
from flask import Blueprint, request, jsonify, abort
from jsonschema import validate, ValidationError
from sqlalchemy import select, func, tuple_
from models import db, Book, Author, BookAuthor, Category

bp = Blueprint('books', __name__, url_prefix='/api/v1/books')

# Load JSON Schema
schema_path = os.path.join(os.path.dirname(__file__), '../schemas/book.json')
with open(schema_path, 'r') as f:
    BOOK_SCHEMA = json.load(f)

# Whitelist các cột cho phép sắp xếp chống SQL Injection
SORT_FIELDS = {
    "id": Book.id,
    "price": Book.price_vnd,
    "price_vnd": Book.price_vnd,
    "title": Book.title,
    "stock": Book.stock
}

# --- HELPER FUNCTIONS ---

def _encode_cursor(payload: dict) -> str:
    """Mã hóa dictionary thành cursor chuỗi base64 safe-url"""
    return base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip("=")

def _decode_cursor(token: str) -> dict:
    """Giải mã cursor chuỗi base64 thành dictionary"""
    try:
        pad = "=" * (-len(token) % 4)
        return json.loads(base64.urlsafe_b64decode(token + pad))
    except Exception:
        return None

def parse_multi_sort(sort_raw: str):
    """
    Xử lý sort multi-key (VD: "-price,title" -> sắp xếp theo price DESC, title ASC).
    Luôn tự động append tie-break column (id) ở cuối để định thứ tự xác định (deterministic).
    """
    if not sort_raw:
        sort_raw = "-id"

    order_cols = []
    parsed_keys = []
    
    for item in sort_raw.split(","):
        item = item.strip()
        if not item:
            continue
        desc = item.startswith("-")
        key = item.lstrip("-")
        
        if key not in SORT_FIELDS:
            return None, None, f"Cột sắp xếp không hợp lệ: {key}"
            
        col_attr = SORT_FIELDS[key]
        order_cols.append(col_attr.desc() if desc else col_attr.asc())
        parsed_keys.append({"key": key, "desc": desc})

    # Nếu chưa có id trong danh sách sort, thêm id làm tie-break
    if not any(pk["key"] == "id" for pk in parsed_keys):
        # Mặc định chiều của id đi theo chiều của key chính đầu tiên
        primary_desc = parsed_keys[0]["desc"] if parsed_keys else True
        order_cols.append(Book.id.desc() if primary_desc else Book.id.asc())
        parsed_keys.append({"key": "id", "desc": primary_desc})

    return order_cols, parsed_keys, None


# --- ROUTES ---

@bp.get("")
def list_books():
    strategy = request.args.get("strategy", "offset").lower()
    limit = min(request.args.get("limit", 20, type=int), 100)
    genre = request.args.get("genre")  # Filter theo genre/category
    sort_raw = request.args.get("sort", "-id")

    # 1. Parse multi-key sort
    order_cols, parsed_keys, sort_err = parse_multi_sort(sort_raw)
    if sort_err:
        return jsonify({"error": sort_err}), 400

    # 2. Khởi tạo Query & Thêm Filter
    stmt = select(Book)
    if genre:
        # Hỗ trợ filter theo slug category hoặc id
        if genre.isdigit():
            stmt = stmt.where(Book.category_id == int(genre))
        else:
            stmt = stmt.join(Category).where(Category.slug == genre)

    # OFFSET / LIMIT PAGINATION
    if strategy == "offset":
        offset = request.args.get("offset", 0, type=int)
        
        # Đếm tổng số lượng bản ghi thỏa mãn filter
        total_stmt = select(func.count()).select_from(stmt.subquery())
        total = db.session.scalar(total_stmt)

        # Lấy dữ liệu phân trang
        rows_stmt = stmt.order_by(*order_cols).offset(offset).limit(limit)
        books = db.session.scalars(rows_stmt).all()

        return jsonify({
            "data": [b.to_dict() for b in books],
            "pagination": {
                "strategy": "offset",
                "offset": offset,
                "limit": limit,
                "total": total,
                "has_next": (offset + limit) < total
            }
        }), 200

    # ==========================================
    # STRATEGY 2: CURSOR-BASED PAGINATION
    # ==========================================
    elif strategy == "cursor":
        cursor_raw = request.args.get("cursor")
        
        # Áp dụng cursor nếu được truyền lên
        if cursor_raw:
            c_data = _decode_cursor(cursor_raw)
            if not c_data or "v" not in c_data or "s" not in c_data:
                return jsonify({"error": "Mã cursor không hợp lệ"}), 400
            
            # Kiểm tra nếu client đổi cấu hình sort giữa các trang
            if c_data.get("s") != sort_raw:
                return jsonify({"error": "Cấu hình sort đã thay đổi, vui lòng lấy lại trang đầu"}), 400

            primary_key_info = parsed_keys[0]
            p_field = SORT_FIELDS[primary_key_info["key"]]
            p_desc = primary_key_info["desc"]
            
            # Tuple comparison cho composite cursor: (sort_val, id) < (v, i) hoặc > (v, i)
            op = "<" if p_desc else ">"
            stmt = stmt.where(
                tuple_(p_field, Book.id).op(op)((c_data["v"], c_data["i"]))
            )

        # Query thừa 1 item để kiểm tra has_more (limit + 1)
        rows_stmt = stmt.order_by(*order_cols).limit(limit + 1)
        books = db.session.scalars(rows_stmt).all()

        has_more = len(books) > limit
        result_items = books[:limit]

        # Tạo next_cursor từ item cuối cùng
        next_cursor = None
        if result_items and has_more:
            last_item = result_items[-1]
            primary_key_name = parsed_keys[0]["key"]
            sort_val = getattr(last_item, SORT_FIELDS[primary_key_name].key)
            
            next_cursor = _encode_cursor({
                "s": sort_raw,
                "v": sort_val,
                "i": last_item.id
            })

        return jsonify({
            "data": [b.to_dict() for b in result_items],
            "pagination": {
                "strategy": "cursor",
                "limit": limit,
                "has_more": has_more,
                "next_cursor": next_cursor
            }
        }), 200

    else:
        return jsonify({"error": f"Chiến lược phân trang '{strategy}' không được hỗ trợ. Hãy dùng 'offset' hoặc 'cursor'"}), 400


# --- CÁC ROUTE CRUD KHÁC BÌNH THƯỜNG ---

@bp.post("")
def create_book():
    payload = request.get_json(silent=True) or {}
    try:
        validate(payload, BOOK_SCHEMA)
    except ValidationError as e:
        return jsonify({
            "error": "validation_failed",
            "field": list(e.path),
            "message": e.message
        }), 400

    book = Book(
        title=payload["title"],
        isbn=payload.get("isbn"),
        price_vnd=payload.get("price_vnd", 0),
        stock=payload.get("stock", 0),
        category_id=payload.get("category_id")
    )
    db.session.add(book)
    db.session.commit()
    return jsonify(book.to_dict()), 201

@bp.get("/<int:bid>")
def get_book(bid):
    book = Book.query.get_or_404(bid)
    return jsonify(book.to_dict()), 200