"""LAB 1 — add your five tests here. Do not delete the smoke tests.

A. GET /books, empty database -> HTTP 200 and []
B. GET /books/9999 -> HTTP 404, JSON code == NOT_FOUND
C. POST /books with only author -> HTTP 400, errors contains title
D. POST valid book, DELETE it, GET same id -> HTTP 404
BONUS. Validate a Book response using JSON Schema; add an unknown
       field to a *copy* of the response and assert ValidationError.

Useful imports:
    from jsonschema import validate, ValidationError
    import pytest
    from tools import get_book_schema

Do not depend on test execution order. Fixtures: client, app, sample_book.
"""
import copy
import pytest
from jsonschema import ValidationError, validate
from models import Book, db
from tools import get_book_schema

# A. DB rỗng -> 200 + [] (không phải null / {})
def test_list_books_empty_returns_empty_array(client):
    r = client.get("/books")
    assert r.status_code == 200
    assert r.content_type == "application/json"
    assert r.get_json() == []

# B. id không tồn tại -> 404 + code NOT_FOUND
def test_get_unknown_book_returns_404_not_found(client):
    r = client.get("/books/9999")
    assert r.status_code == 404
    assert r.get_json()["code"] == "NOT_FOUND"

# C. POST thiếu title -> 400 + errors chứa field "title"
def test_create_book_missing_title_returns_400(client):
    r = client.post("/books", json={"author": "X"})
    assert r.status_code == 400
    fields = {e["field"] for e in r.get_json()["errors"]}
    assert "title" in fields

# D. POST -> DELETE -> GET cùng id => 404
def test_deleted_book_is_gone(client):
    created = client.post("/books", json={"title": "T", "author": "A"})
    assert created.status_code == 201
    book_id = created.get_json()["id"]
    assert client.delete(f"/books/{book_id}").status_code == 204
    assert client.get(f"/books/{book_id}").status_code == 404

# BONUS: thêm field lạ vào BẢN SAO response -> jsonschema phải báo lỗi
def test_response_extra_field_blocked(client, app):
    with app.app_context():
        db.session.add(Book(title="T", author="A", year=2021, isbn="9781617295850"))
        db.session.commit()
    schema = get_book_schema()
    body = client.get("/books").get_json()[0]
    validate(body, schema)                     # response thật phải hợp lệ

    leaked = copy.deepcopy(body)
    leaked["password_hash"] = "abc123"
    with pytest.raises(ValidationError):
        validate(leaked, schema)