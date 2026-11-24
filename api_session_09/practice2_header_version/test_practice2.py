import pytest

from app import app


@pytest.fixture
def client():
    return app.test_client()


def test_default_is_newest(client):
    r = client.get("/users/1")
    assert r.status_code == 200
    assert r.headers["X-API-Version-Served"] == "2"
    assert "first_name" in r.get_json()


def test_explicit_v1(client):
    r = client.get("/users/1", headers={"X-API-Version": "1"})
    assert r.headers["X-API-Version-Served"] == "1"
    assert r.get_json() == {"id": 1, "full_name": "Văn Nguyễn"}


def test_dated_version(client):
    r = client.get("/users/1", headers={"X-API-Version": "2024-06-20"})
    assert r.status_code == 200
    assert r.headers["X-API-Version-Served"] == "2024-06-20"
    assert r.get_json()["last_name"] == "Nguyễn"


def test_unsupported_version_400(client):
    r = client.get("/users/1", headers={"X-API-Version": "99"})
    assert r.status_code == 400
    assert r.get_json()["error"] == "unsupported version"
    assert "X-API-Version-Served" not in r.headers


def test_not_found_is_404_with_served_header(client):
    r = client.get("/users/404", headers={"X-API-Version": "1"})
    assert r.status_code == 404
    assert r.headers["X-API-Version-Served"] == "1"


def test_vary_header_present(client):
    assert client.get("/users/1").headers["Vary"] == "X-API-Version"
