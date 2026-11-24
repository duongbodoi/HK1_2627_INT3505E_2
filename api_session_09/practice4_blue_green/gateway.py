"""Practice 4 — Blue-Green routing 3 tầng: cohort > allow-list > hash bucket %."""
import hashlib
import logging

from flask import request

from handlers import v1_create_order, v2_create_order

# Config: flip V2_PERCENT qua dashboard (ở đây là biến module, test có thể set)
V2_PERCENT = 5
V2_COHORTS = {"beta", "internal"}
V2_FORCE_ACCOUNTS = {"acct_42", "acct_99"}

log = logging.getLogger("gateway")


def bucket(account_id: str) -> int:
    """Bucket 0..99, deterministic: cùng account luôn rơi vào cùng bucket."""
    return int(hashlib.md5(account_id.encode()).hexdigest(), 16) % 100


def route_to_v2(body) -> bool:
    # 1. Explicit cohort có ưu tiên cao nhất
    cohort = request.headers.get("X-Cohort", "").lower()
    if cohort in V2_COHORTS:
        return True

    # 2. Account nằm trong allow-list
    acct = (body or {}).get("account_id", "")
    if acct in V2_FORCE_ACCOUNTS:
        return True

    # 3. Bucket theo % (deterministic)
    if V2_PERCENT <= 0:
        return False
    return bucket(acct) < V2_PERCENT


def dispatch(body):
    if route_to_v2(body):
        log.info("route v2 account=%s", (body or {}).get("account_id"))
        return "v2", v2_create_order(body or {})
    return "v1", v1_create_order(body or {})
