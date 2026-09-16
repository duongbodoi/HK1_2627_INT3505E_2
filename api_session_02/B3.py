from flask import Flask,request,jsonify,make_response
app=Flask(__name__)
BOOKS=[
  {
    "id": 1,
    "title": "Clean Code",
    "author": "Robert C. Martin",
    "genre": "Software Engineering",
    "price": 32.99,
    "published_year": 2008,
    "rating": 4.7
  },
  {
    "id": 2,
    "title": "The Clean Coder",
    "author": "Robert C. Martin",
    "genre": "Software Engineering",
    "price": 28.50,
    "published_year": 2011,
    "rating": 4.6
  },
  {
    "id": 3,
    "title": "Design Patterns Clean",
    "author": "Erich Gamma",
    "genre": "Software Architecture",
    "price": 45.00,
    "published_year": 1994,
    "rating": 4.8
  },
  {
    "id": 4,
    "title": "Refactoring",
    "author": "Martin Fowler",
    "genre": "Software Engineering",
    "price": 39.99,
    "published_year": 1999,
    "rating": 4.7
  },
  {
    "id": 5,
    "title": "Pragmatic Programmer",
    "author": "Andrew Hunt",
    "genre": "Career & Practice",
    "price": 41.25,
    "published_year": 1999,
    "rating": 4.9
  },
  {
    "id": 6,
    "title": "Designing Data-Intensive Applications",
    "author": "Martin Kleppmann",
    "genre": "System Design",
    "price": 49.99,
    "published_year": 2017,
    "rating": 4.9
  },
  {
    "id": 7,
    "title": "You Don't Know JS Yet",
    "author": "Kyle Simpson",
    "genre": "JavaScript",
    "price": 25.00,
    "published_year": 2020,
    "rating": 4.5
  },
  {
    "id": 8,
    "title": "Head First Design Patterns",
    "author": "Eric Freeman",
    "genre": "Software Architecture",
    "price": 35.50,
    "published_year": 2004,
    "rating": 4.6
  }
]
     

next_id=1
# ─── tham số phân trang
DEFAULT_SIZE, MAX_SIZE = 20, 100
# app.py — GET /books nâng cấp với pagination + filter + HATEOAS
@app.route("/books",methods=["GET"])
def list_books():
    try:
        page=int(request.args.get("page",1))
        size=int(request.args.get("size",DEFAULT_SIZE))
    except ValueError:
        return jsonify({"error":"page và size phải là số nguyên"}),400
    page=max(page,1)
    size=max(min(size,MAX_SIZE),1)
    # filter: author chính xác, q tìm trong title
    filter=BOOKS
    a=request.args.get("author")
    if a:
        filter=[b for b in filter if b["author"].lower()==a.lower()]
    q=request.args.get("q")
    if q:
            filter=[b for b in filter if q in b["title"].lower()]
    # paginate
    total = len(filter); start=(page-1)*size; end=start+size # bản chất phân trang tức là dựa vào size để tiến hành phân trang sao cho mỗi trang có n=size phần từ
    items = filter[start:end]; last=(total+size-1)//size
    # HATEOAS links
    def u(p): return f"/books?page={p}&size={size}"
    links={"self":{"href":u(page)},
            "first":{"href":u(1)},
            "last":{"href":u(max(page,1))}
        }
    if page > 1:
        links["prev"]={"href":u(page-1)}
    if end < total :
            links["next"]={"href":u(page+1)}
    
    body = {"data":items,
    "pagination":{"page":page,"size":size,"total":total,"total_pages":last}, 
    "_links":links}
    resp = make_response(jsonify(body), 200)
    resp.headers["Cache-Control"]="public, max-age=30"
    return resp


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