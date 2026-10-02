from flask import Flask, request, jsonify

app = Flask(__name__)
#database
orders = [
    {
        "id": 1,
        "customer_id": 101,
        "status": "paid",
        "total": 120.5
    },
    {
        "id": 2,
        "customer_id": 102,
        "status": "pending",
        "total": 80.0
    },
    {
        "id": 3,
        "customer_id": 101,
        "status": "paid",
        "total": 250.0
    },
    {
        "id": 4,
        "customer_id": 103,
        "status": "cancelled",
        "total": 50.0
    },
    {
        "id": 5,
        "customer_id": 104,
        "status": "paid",
        "total": 300.0
    },
    {
        "id": 6,
        "customer_id": 102,
        "status": "paid",
        "total": 150.0
    },
    {
        "id": 7,
        "customer_id": 105,
        "status": "pending",
        "total": 90.0
    },
    {
        "id": 8,
        "customer_id": 101,
        "status": "paid",
        "total": 500.0
    },
    {
        "id": 9,
        "customer_id": 106,
        "status": "cancelled",
        "total": 70.0
    },
    {
        "id": 10,
        "customer_id": 104,
        "status": "paid",
        "total": 200.0
    }
]
#exception
class ProblemError(Exception):
    def __init__(self, status, title, detail):
        self.status = status
        self.title = title
        self.detail = detail
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
    return jsonify(payload)

@app.get("/orders")
def get_orders():
    # 1. Lấy query parameters
    cursor = request.args.get("cursor") # điểm lọc
    limit = request.args.get("limit", default=5, type=int) # limit item trong 1 trang

    status = request.args.get("status") #filter
    customer_id = request.args.get("customer_id") #filter

    sort = request.args.get("sort", "id") #sort

    fields = request.args.get("fields") # trường trả về
    # xử lý cursor
    if cursor is not None :
        try :
            cursor=int(cursor)
        except ValueError:
            raise ProblemError(400,"Bad request","cursor phải là số nguyên")
    # xử lí limiit
    if limit <=0:
        raise ProblemError(400,"Bad request","limit phải là số dương >0")
    # filter
    result=orders.copy()
    if status :
        result=[order for order in result
                if order["status"]==status]
    if customer_id:
        try :
            customer_id=int(customer_id)
        except(ValueError):
            raise ProblemError(400,"Bad request","customer_id phải là số nguyên")
        result=[order for order in result
                if order["customer_id"]==customer_id]
    # sort
    allowed_sort = {
        "id",
        "total",
        "customer_id"
    }
    descending = sort.startswith("-")
    sort_field = sort[1:] if descending else sort
    if sort_field not in allowed_sort:
        raise ProblemError(400,"Bad request","Trường sắp xếp ko tồn tại/ko cho phép")
    result.sort(
        key=lambda order: order[sort_field],
        reverse=descending
    )
    if cursor is None:
        result = orders[:limit]
    else :
        result=[order for order in result
                if order["id"]>cursor]
        
    # limit
    has_next=len(result) > limit
    page = result[:limit]
    # fields
    if fields:
        request_fields=fields.split(",")
        allowed_fields = {
            "id",
            "customer_id",
            "status",
            "total"
        }
        for field in request_fields:
            if field not in allowed_fields:
                raise ProblemError(400,"Bad request","Trường trả về ko tồn tại/ko cho phép")
        page=[
            {
                field:order[field]
                for field in request_fields
            }
            for order in page
        ]    
    # next cursor
    
    if has_next:
        next_cursor = page[-1]["id"]
        return jsonify({
                "data": page,
                "next_cursor": next_cursor
            })
    return jsonify({
            "data": page,
        })
    
        
        

if __name__=="__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)