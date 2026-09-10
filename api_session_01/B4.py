from flask import Flask,request,jsonify
app=Flask(__name__)
# /books/<id> — id là string
@app.route("/books/<id>",methods=["GET"])
def get_book(id) :
    book = find_by_id(id)
    if book is None:
        return jsonify({"error":"Tiêng rất ách, ko có đâu"},), 404
    
    return jsonify(book), 200

# Ép kiểu int ngay từ URL
@app.route("/items/<int:item>")
def get_item(item):
    if item == 3: # Đoạn này có thể viết thẳng vì bản chát item đã là int nên so sánh bình thường
        return jsonify({"item_id":item}), 200
    return jsonify({"error":"Điền 3 là ngon nhe :)"}), 404

#demo trước hàm find id bản chất là phải duyệt trong list hoặc database
def find_by_id(id):
    if id=="1":   #bỏi id lấy ra đang là string
        return {"name":"Như ngày hôm qua đã từng"}
    elif id=="2":
        return {"name":"Vẽ em bằng màu nỗi nhớ"}
    return None


if __name__=="__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
    