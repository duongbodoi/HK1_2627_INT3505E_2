#2xx Mã ok
    #200 Get/Put/Patch thành công
    #201 Post thành công
    #204 Delete thành công
#4xx lỗi client
    #400 bad request : json body lỗi 
    #404 not found : không có body
    #409 conflict state xung đột
    #422 unprocessable : logic sai
    #429 Too many : Rate limit
#5xx Lỗi server
    #500 Internal : Lỗi không rõ 
    #503 Unavailable: Bảo trì
from flask import Flask,jsonify,request
app=Flask("__name__")
ORDERS = {
    "1": {"status": "shipped"},
    "2": {"status": "shipped"},
    "3": {"status": "None"}
}
    
#Nghiệp vụ được mô tả liên quan tới các thao tác xoá 1 đơn hàng. Các vấn đề cần xử lí là nếu không có thì sao? Nếu đang vận chuyển rồi thì sao?Nếu thành công thì sao
@app.route("/orders/<id>",methods=["DELETE"])
def delete_order(id):
    order=ORDERS.get(id)
    #Not found
    if order is None:
        return jsonify({"error":"Làm gì có mà xoá ??"}),404
    # conflict
    if order["status"] in ("shipped","delivered"):
        return jsonify({"error:":"Conflict"}),409
    ORDERS.pop(id,None)
    return jsonify({"text":"Quá tốt rồi"}),204

if __name__=="__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)