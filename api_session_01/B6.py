from flask import Flask, jsonify, request
app = Flask(__name__)
_next = 1
BOOKS = [{"id":1,"title":"Clean Code","author":"R. Martin"}]
def find(bid):
    return next((b for b in BOOKS if b["id"]==bid), None)
# LIST — GET /books
@app.route("/books",methods=["GET"])
def list_books() :
    n = int(request.args.get("limit", 100))
    return jsonify(BOOKS[:n]), 200

# DETAIL — GET /books/<int:id>
@app.route("/books/<int:id>")
def get_book(id):
    book=find(id)
    if book is None:
        return jsonify({"error":"Sách không tồn tại"}),404
    return jsonify(book),200
# CREATE — POST /books
@app.route("/books",methods=["POST","PUT"])
def create_or_update_book():
    global _next
    body=request.get_json(silent=True) or {}
    t,a=body.get("title"),body.get("author")
    if not t or not a :
        return jsonify({"error":"Lỗi request r ní"}),400
    book={"id": _next ,"title":t,"author":a}
    _next+=1
    if request.method=="PUT":
        BOOKS.append(book)
        return jsonify({"mes":"ĐÃ thêm thành công"}),200
    return jsonify(book),201, {"Location":f"/books/{book['id']}"}
# UPDATE — PUT, DELETE — DELETE (xem bên phải)
@app.route("/books/<int:bid>", methods=["PUT", "DELETE"])
def modify_book(bid):
    book = find(bid)
    if not book: return {"error":"not found"}, 404
    if request.method == "PUT":
        book.update(request.get_json(silent=True) or {})
        return jsonify(book), 200
    BOOKS.remove(book)
    return"", 204
if __name__=="__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
