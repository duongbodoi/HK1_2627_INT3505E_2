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
    title,author=body.get("title").strip(),body.get("author").strip()
    if not title or not author :
        return jsonify({"error":"Bạn cần nhập title và author"}),422 # thiếu field
    book={
            "id":next_id,
            "title":title,
            "author":author
         }
    BOOKS.append(book);next_id+=1
    resp = make_response(jsonify(book), 201)
    resp.headers["Location"] = f"/books/{book['id']}"
    return resp


      


if __name__=="__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)