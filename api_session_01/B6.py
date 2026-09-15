from flask import Flask, jsonify, request
app = Flask(__name__)
_next = 1
BOOKS = [{"id":1,"title":"Clean Code","author":"R. Martin"}]
def find(bid):
    return next((b for b in BOOKS if b["id"]==bid), None)
# LIST — GET /books
@app.route("/books",methods=["GET"])
def list_books() :
    #BTVN a) GET /books?q=...
    books_return=BOOKS.copy()
    q=request.args.get("q")
    sort_by=request.args.get("sort")
    if q:
        books_return.clear()
        for book in BOOKS:
            if q.lower() in book["title"].lower():
                books_return.append(book)
    #b)sort theo ?sort=title
    if sort_by =="title":
        books_return=sorted(books_return,key=lambda x: x["title"].lower())
    return jsonify(books_return),200




# DETAIL — GET /books/<int:id>
@app.route("/books/<int:id>")
def get_book(id):
    book=find(id)
    if book is None:
        return jsonify({"error":"Sách không tồn tại"}),404
    return jsonify(book),200
# CREATE — POST /books
@app.route("/books",methods=["POST"])
def create_book():
    global _next
    body=request.get_json(silent=True) or {}
    t,a=body.get("title"),body.get("author")
    year=body.get("year")
    if not t or not a or not year:
        return jsonify({"error":"Lỗi request r ní"}),404
    # bắt buộc field year là số ≥ 1900
    if not isinstance(year,int):
        return jsonify({"error":"year bắt buộc phải là số"}),400
    if year<=1900 :
        return jsonify({"error":"year phải lớn hơn 1900"}),400
    _next+=1
    book={"id": _next ,"title":t,"author":a}
    BOOKS.append(book)
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
