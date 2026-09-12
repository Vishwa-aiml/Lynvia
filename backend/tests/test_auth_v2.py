"""Auth tests using conftest fixtures (SQLite in-memory).

NOTE: The original version of this file had a hard-coded database password
and a broken os.getenv() call. Both have been removed. Tests now use the
shared SQLite in-memory DB from conftest.py.
"""
import pytest
from app.models.user import User, UserRole
from app.utils.security import hash_password, create_access_token


@pytest.fixture
def test_user(db):
    user = User(
        email="alice@example.com",
        full_name="Alice",
        hashed_password=hash_password("secret123"),
        role=UserRole.CLIENT,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def auth_header(test_user):
    token = create_access_token(subject=test_user.id, role=UserRole.CLIENT.value)
    return {"Authorization": f"Bearer {token}"}


def test_register(client):
    resp = client.post(
        "/auth/register",
        json={"email": "bob@example.com", "password": "secret123", "full_name": "Bob"},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["email"] == "bob@example.com"


def test_register_duplicate_email(client, test_user):
    resp = client.post("/auth/register", json={"email": "alice@example.com", "password": "secret123"})
    assert resp.status_code == 400


def test_register_short_password(client):
    resp = client.post("/auth/register", json={"email": "bob@example.com", "password": "short"})
    assert resp.status_code == 422


def test_login(client, test_user):
    resp = client.post("/auth/login", json={"email": "alice@example.com", "password": "secret123"})
    assert resp.status_code == 200
    assert "access_token" in resp.json()


def test_login_wrong_password(client, test_user):
    resp = client.post("/auth/login", json={"email": "alice@example.com", "password": "wrong"})
    assert resp.status_code == 401


def test_login_nonexistent_user(client):
    resp = client.post("/auth/login", json={"email": "nonexistent@example.com", "password": "secret123"})
    assert resp.status_code == 401
