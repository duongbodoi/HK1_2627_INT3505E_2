import logging
from datetime import datetime, timezone

import pytest

import sunset
from app import V1_SUNSET, app


@pytest.fixture
def client():
    return app.test_client()


def fake_clock(monkeypatch, dt):
    monkeypatch.setattr(sunset, "_now", lambda: dt)


def test_before_sunset_200_with_headers(client, monkeypatch):
    fake_clock(monkeypatch, datetime(2026, 11, 18, tzinfo=timezone.utc))
    r = client.get("/api/v1/users/1")
    assert r.status_code == 200
    assert r.headers["Sunset"] == "Thu, 31 Dec 2026 23:59:59 GMT"
    assert r.headers["Deprecation"] == "true"
    assert r.headers["Link"] == '</api/v2/users>; rel="successor-version"'
    assert r.get_json()["full_name"] == "Nguyễn Văn A"


def test_after_sunset_410_gone(client, monkeypatch):
    fake_clock(monkeypatch, datetime(2027, 1, 1, tzinfo=timezone.utc))
    r = client.get("/api/v1/users/1")
    assert r.status_code == 410
    j = r.get_json()
    assert j["error"] == "gone" and j["use_instead"] == "/api/v2/users"


def test_exactly_at_sunset_is_gone(client, monkeypatch):
    fake_clock(monkeypatch, V1_SUNSET)
    assert client.get("/api/v1/users/1").status_code == 410


def test_each_call_logs_warning(client, monkeypatch, caplog):
    fake_clock(monkeypatch, datetime(2026, 11, 18, tzinfo=timezone.utc))
    with caplog.at_level(logging.WARNING, logger="sunset"):
        client.get("/api/v1/users/1")
        client.get("/api/v1/users/2")
    msgs = [r.getMessage() for r in caplog.records if r.name == "sunset"]
    assert len(msgs) == 2 and all("deprecated_call" in m for m in msgs)


def test_no_warning_logged_after_sunset(client, monkeypatch, caplog):
    fake_clock(monkeypatch, datetime(2027, 1, 1, tzinfo=timezone.utc))
    with caplog.at_level(logging.WARNING, logger="sunset"):
        client.get("/api/v1/users/1")
    assert not caplog.records


def test_v2_untouched(client):
    r = client.get("/api/v2/users/1")
    assert r.status_code == 200 and "Sunset" not in r.headers


def test_decorator_preserves_status_code(monkeypatch):
    fake_clock(monkeypatch, datetime(2026, 11, 18, tzinfo=timezone.utc))
    from flask import Flask
    a = Flask("t")

    @a.route("/x")
    @sunset.deprecate_at(V1_SUNSET)
    def x():
        return {"error": "nf"}, 404

    r = a.test_client().get("/x")
    assert r.status_code == 404 and r.headers["Sunset"]
    assert "Link" not in r.headers  # không có replacement
