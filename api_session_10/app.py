from flask import Flask, jsonify

app = Flask(__name__)

@app.get("/healthz")
def healthz():
    return jsonify(status="ok"), 200

@app.get("/hello")
def hello():
    return jsonify(message="Xin chào từ trong container!")
