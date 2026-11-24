"""Practice 3 — Sunset middleware (RFC 8594): @deprecate_at(date)."""
import logging
from datetime import datetime, timezone
from email.utils import format_datetime
from functools import wraps

from flask import jsonify, request

log = logging.getLogger("sunset")


def http_date(dt):
    return format_datetime(dt, usegmt=True)


def _now():
    # tách ra để test có thể thay thế "đồng hồ"
    return datetime.now(timezone.utc)


def deprecate_at(sunset_date, replacement=None):
    def wrap(fn):
        @wraps(fn)
        def inner(*a, **kw):
            # Sau sunset -> 410 Gone (không phải 404: phải rõ "đã bị gỡ")
            if _now() >= sunset_date:
                resp = jsonify({"error": "gone",
                                "sunset": http_date(sunset_date),
                                "use_instead": replacement})
                resp.status_code = 410
                return resp

            result = fn(*a, **kw)
            body, status = result if isinstance(result, tuple) else (result, 200)
            r = jsonify(body)
            r.status_code = status
            r.headers["Sunset"] = http_date(sunset_date)
            r.headers["Deprecation"] = "true"
            if replacement:
                r.headers["Link"] = f'<{replacement}>; rel="successor-version"'
            log.warning("deprecated_call %s %s", request.path, request.remote_addr)
            return r
        return inner
    return wrap
