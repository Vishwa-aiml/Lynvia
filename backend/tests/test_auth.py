"""Basic auth smoke test — kept for backward compatibility.

Uses conftest fixtures (see conftest.py for DB setup).
"""
import pytest


def test_register_and_login(client):
    # register — expects 201
    resp = client.post(
        "/auth/register",
        json={"email": "alice@example.com", "password": "secret123", "full_name": "Alice"},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["email"] == "alice@example.com"

    # login
    resp = client.post("/auth/login", json={"email": "alice@example.com", "password": "secret123"})
    assert resp.status_code == 200
    tok = resp.json()
    assert "access_token" in tok
