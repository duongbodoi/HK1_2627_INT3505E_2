"""Hai implementation của POST /orders (slide không cho sẵn nên tự định nghĩa)."""
import itertools

_v1_ids = itertools.count(1)
_v2_ids = itertools.count(1)


def v1_create_order(body):
    """v1: schema cũ — trả về order tối giản."""
    return {"order_id": f"o1-{next(_v1_ids)}",
            "account_id": body.get("account_id"),
            "status": "created"}


def v2_create_order(body):
    """v2: schema mới — thêm schema_version và tách status/payment_status."""
    return {"order_id": f"o2-{next(_v2_ids)}",
            "account_id": body.get("account_id"),
            "status": "created",
            "payment_status": "pending",
            "schema_version": 2}
