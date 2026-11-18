from flask import Blueprint
from .users_data import get_user
bp = Blueprint("v2", __name__, url_prefix="/users")
@bp.route("/<int:uid>")
def get(uid):
    u = get_user(uid)
    if not u: return {"error": "nf"}, 404
    return {"id": uid,
            "first_name": u["first_name"],
            "last_name": u["last_name"],
            "email": u["email"]}
@bp.route("", methods=["POST"])
def create():
    body = request.get_json(silent=True) or {}
    missing = [k for k in ("first_name", "last_name", "email")
               if not isinstance(body.get(k), str) or not body[k].strip()]
    if missing:
        return {"error": "validation_failed", "missing_or_invalid": missing}, 422
    uid, u = create_user(body["first_name"].strip(), body["last_name"].strip(),
                         body["email"].strip())
    return {"id": uid, **u}, 201, {"Location": f"/api/v2/users/{uid}"}