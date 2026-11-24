import pytest

import gateway
from app import app


@pytest.fixture
def client():
    return app.test_client()


def handler(resp):
    return resp.headers["X-Order-Handler"]


def find_account(pred):
    """Tìm account bình thường (không allow-list) thoả điều kiện bucket."""
    for i in range(100000):
        a = f"user_{i}"
        if pred(gateway.bucket(a)):
            return a


# Case 1: cohort beta -> v2 dù % = 0
def test_case1_cohort_beta_to_v2(client, monkeypatch):
    monkeypatch.setattr(gateway, "V2_PERCENT", 0)
    r = client.post("/orders", json={"account_id": "any"}, headers={"X-Cohort": "beta"})
    assert handler(r) == "v2" and r.status_code == 201
    assert r.get_json()["schema_version"] == 2


def test_case1b_cohort_case_insensitive_and_unknown_cohort(client, monkeypatch):
    monkeypatch.setattr(gateway, "V2_PERCENT", 0)
    assert handler(client.post("/orders", json={"account_id": "x"},
                               headers={"X-Cohort": "INTERNAL"})) == "v2"
    assert handler(client.post("/orders", json={"account_id": "x"},
                               headers={"X-Cohort": "vip"})) == "v1"


# Case 2: acct_42 force -> v2
def test_case2_allow_list(client, monkeypatch):
    monkeypatch.setattr(gateway, "V2_PERCENT", 0)
    assert handler(client.post("/orders", json={"account_id": "acct_42"})) == "v2"
    assert handler(client.post("/orders", json={"account_id": "acct_99"})) == "v2"


# Case 3: account thường -> bucket quyết định, deterministic
def test_case3_bucket_decides_and_is_sticky(client, monkeypatch):
    monkeypatch.setattr(gateway, "V2_PERCENT", 5)
    in_v2 = find_account(lambda b: b < 5)
    in_v1 = find_account(lambda b: b >= 5)
    for _ in range(3):  # gọi lặp lại: luôn cùng kết quả
        assert handler(client.post("/orders", json={"account_id": in_v2})) == "v2"
        assert handler(client.post("/orders", json={"account_id": in_v1})) == "v1"


# Case 4: flip V2_PERCENT = 100 -> tất cả v2 ; 0 -> tất cả v1 (rollback)
def test_case4_flip_to_100_then_rollback(client, monkeypatch):
    monkeypatch.setattr(gateway, "V2_PERCENT", 100)
    for a in ("a", "b", "user_7", "zzz", ""):
        assert handler(client.post("/orders", json={"account_id": a})) == "v2"
    monkeypatch.setattr(gateway, "V2_PERCENT", 0)  # rollback
    for a in ("a", "b", "user_7", "zzz", ""):
        assert handler(client.post("/orders", json={"account_id": a})) == "v1"


# Case 5: sau khi 100% ổn -> v1 trả 200 / v2 trả 201, mỗi bên đúng schema
def test_case5_response_shapes_differ(client, monkeypatch):
    monkeypatch.setattr(gateway, "V2_PERCENT", 0)
    v1 = client.post("/orders", json={"account_id": "q"})
    monkeypatch.setattr(gateway, "V2_PERCENT", 100)
    v2 = client.post("/orders", json={"account_id": "q"})
    assert v1.status_code == 200 and "payment_status" not in v1.get_json()
    assert v2.status_code == 201 and v2.get_json()["payment_status"] == "pending"


# Thống kê: 5% thật sự ~5% và rollout đơn điệu (tăng % không đẩy ai ngược về v1)
def test_bucket_distribution_and_monotonic_rollout():
    accts = [f"acct_{i}" for i in range(20000)]
    share = sum(gateway.bucket(a) < 5 for a in accts) / len(accts)
    assert 0.04 < share < 0.06
    s5 = {a for a in accts if gateway.bucket(a) < 5}
    s20 = {a for a in accts if gateway.bucket(a) < 20}
    assert s5 <= s20


def test_missing_or_invalid_body_does_not_crash(client, monkeypatch):
    monkeypatch.setattr(gateway, "V2_PERCENT", 0)
    r = client.post("/orders", data="not json", content_type="text/plain")
    assert r.status_code == 200 and handler(r) == "v1"
