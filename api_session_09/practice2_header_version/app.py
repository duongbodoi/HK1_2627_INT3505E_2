"""Practice 2 — Header versioning với decorator @api_version."""
from functools import wraps

from flask import Flask, jsonify, request

LATEST = "2"
SUPPORTED = {"1", "2", "2024-06-20"}
USERS = {1: {"f": "Văn", "l": "Nguyễn", "e": "a@vnu.vn"}}

app = Flask(__name__)
app.json.ensure_ascii = False


def api_version(supported=SUPPORTED, default=LATEST):
    def decorate(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            # ① parse X-API-Version — thiếu header thì dùng default (newest stable)
            v = request.headers.get("X-API-Version", default)
            # ④ version lạ -> 400, không fallback
            if v not in supported:
                resp = jsonify(error="unsupported version", requested=v,
                               supported=sorted(supported))
                resp.status_code = 400
                return resp
            result = fn(v, *args, **kwargs)
            body, status = result if isinstance(result, tuple) else (result, 200)
            response = jsonify(body)
            response.status_code = status
            # ② trả X-API-Version-Served để debug
            response.headers["X-API-Version-Served"] = v
            # Cùng URL nhưng nội dung phụ thuộc header -> cache phải biết (slide Header: Vary)
            response.headers["Vary"] = "X-API-Version"
            return response
        return wrapper
    return decorate


@app.route("/users/<int:uid>")
@api_version()
def get_user(version, uid):
    u = USERS.get(uid)
    if not u:
        return {"error": "not found"}, 404
    # ③ mỗi version một shape
    if version == "1":
        return {"id": uid, "full_name": u["f"] + " " + u["l"]}
    # "2" và "2024-06-20" dùng chung shape v2
    return {"id": uid, "first_name": u["f"], "last_name": u["l"], "email": u["e"]}


if __name__ == "__main__":
    app.run(port=5000, debug=True)
