from flask import Blueprint
from .users_data import get_user
bp = Blueprint("v1", __name__, url_prefix="/users")
@bp.route("/<int:uid>")
def get(uid):
    u = get_user(uid)
    if not u: return {"error": "nf"}, 404
    return {"id": uid,
    "full_name": f"{u['first_name']} {u['last_name']}",
    "email": u["email"]}
from datetime import datetime, timezone
from email.utils import format_datetime

V1_SUNSET = datetime(2026, 12, 31, 23, 59, 59, tzinfo=timezone.utc)

@bp.after_request
def add_sunset_headers(resp):
    resp.headers["Sunset"] = format_datetime(V1_SUNSET, usegmt=True)
    resp.headers["Deprecation"] = "true"
    resp.headers["Link"] = '</api/v2/users>; rel="successor-version"'
    return resp