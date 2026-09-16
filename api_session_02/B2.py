from flask import Flask,request,jsonify,make_response
app=Flask(__name__)
BOOKS=[]
next_id=1
# ─── GET /books —— trả danh sách
@app.route("/books",methods=["GET"])
def list_books():
        return jsonify(
            {
                "data":BOOKS,
                "total":len(BOOKS)
            }
        ),200
# ─── POST /books —— tạo mới
@app.route("/books",methods=["POST"])
def create_book() :
    global next_id
    if not request.is_json:
        return jsonify({"error":"expected JSON"}),415 # Thiếu context type
    body=request.get_json(silent=True) or {}
    title,author,price=body.get("title").strip(),body.get("author").strip(),body.get("price").strip()
    if not title or not author :
        return jsonify({"error":"Bạn cần nhập title và author"}),422 # thiếu field
    book={
            "id":next_id,
            "title":title,
            "author":author,
            "price":price
         }
    BOOKS.append(book);next_id+=1
    resp = make_response(jsonify(book), 201)
    resp.headers["Location"] = f"/books/{book['id']}"
    return resp




## Bài 2
# ─── GET /books/<id> ─── cache 60s
@app.route("/books/<int:bid>",methods=["GET"])
def fetch(bid):
    i = next((k for k,b in enumerate(BOOKS) if b["id"]==bid), None)
    if i is None:
        return jsonify({"error":"Not found"}),404
    resp = make_response(jsonify(BOOKS[i]),200)
    resp.headers["Cache-Control"]="max-age=60"
    return resp
# ─── PUT ─── thay toàn bộ, title+author bắt buộc
@app.route("/books/<int:bid>",methods=["PUT"])
def put(bid):
    i = next((k for k,b in enumerate(BOOKS) if b["id"]==bid), None)
    if i is None:
        return jsonify({"error":"Not found"}),404
    body=request.get_json(silent=True) or {}
    title,author=body.get("title").strip(),body.get("author").strip()
    if not title or not author :
        return jsonify({"error":"Bạn cần nhập title và author"}),422 # thiếu field
    BOOKS[i]={
            "id":bid,
            "title":title,
            "author":author,
            "price":body.get("price")
        }
    return jsonify(BOOKS[i]),200
# ─── PATCH ─── chỉ cập nhật field có trong body
@app.patch("/books/<int:bid>")
def patch(bid):
    i = next((k for k,b in enumerate(BOOKS) if b["id"]==bid), None)
    if i is None:
        return jsonify({"error":"Not found"}),404
    body=request.get_json(silent=True) or {}
    for k in "id title author price".split():
        if k in body:
            BOOKS[i][k]=body[k]
    return jsonify(BOOKS[i]),200
# ─── DELETE ─── idempotent, trả 204
@app.delete("/books/<int:bid>")
def delete(bid):
    i = next((k for k,b in enumerate(BOOKS) if b["id"]==bid), None)
    if i is None:
        return jsonify({"error":"Not found"}),404
    BOOKS.pop(i)
    return jsonify({"sucess":"Xoá thành công"}),204    

      


if __name__=="__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)