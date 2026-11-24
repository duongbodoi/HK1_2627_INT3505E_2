from flask import Flask, jsonify, request

from gateway import dispatch

app = Flask(__name__)
app.json.ensure_ascii = False


@app.route("/orders", methods=["POST"])
def create_order():
    which, result = dispatch(request.get_json(silent=True) or {})
    resp = jsonify(result)
    resp.headers["X-Order-Handler"] = which
    return resp, (201 if which == "v2" else 200)


if __name__ == "__main__":
    app.run(port=5000, debug=True)
