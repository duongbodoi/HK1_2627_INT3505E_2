from flask import Flask,jsonify,request
from uuid import uuid4
app=Flask(__name__)
STUDENTS=[] # giả lập 1 database :))
#Tạo 1 api tới endpoint /students , method post, lấy ra cái name từ body request, rồi tạo 1 thằng student từ name đó rồi thêm vào database

@app.route("/students",methods=["POST"])
def create_student():
    body=request.get_json(silent=True) or {}
    name = body.get("name")
    if not name :
        return jsonify({"error":"Name là bắt buộc"})
    student = {
        "id" : str(uuid4()),
        "name":name,
        "gpa" : body.get("gpa",0.0)
    }
    STUDENTS.append(student)


    return jsonify(student)

if __name__=="__main__":
    app.run(host="127.0.0.1",port=5000,debug=True)
