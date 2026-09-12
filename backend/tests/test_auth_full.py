"""Authentication tests: registration, login, JWT, role enforcement."""
import pytest
from app.models.user import User, UserRole
from app.utils.security import hash_password, create_access_token


# ---------------------------------------------------------------------------
# Registration tests
# ---------------------------------------------------------------------------

def test_register_client(client):
    resp = client.post(
        "/auth/register",
        json={"email": "alice@example.com", "password": "secret123", "full_name": "Alice", "role": "CLIENT"},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["email"] == "alice@example.com"
    assert data["role"] == "CLIENT"
    assert data["is_active"] is True


def test_register_designer(client):
    resp = client.post(
        "/auth/register",
        json={"email": "bob@example.com", "password": "secret123", "role": "DESIGNER"},
    )
    assert resp.status_code == 201
    assert resp.json()["role"] == "DESIGNER"


def test_register_default_role_is_client(client):
    resp = client.post(
        "/auth/register",
        json={"email": "default@example.com", "password": "secret123"},
    )
    assert resp.status_code == 201
    assert resp.json()["role"] == "CLIENT"


def test_register_admin_blocked(client):
    """Public API must not allow ADMIN registration."""
    resp = client.post(
        "/auth/register",
        json={"email": "admin@example.com", "password": "secret123", "role": "ADMIN"},
    )
    assert resp.status_code == 403


def test_register_duplicate_email(client):
    client.post("/auth/register", json={"email": "dup@example.com", "password": "secret123"})
    resp = client.post("/auth/register", json={"email": "dup@example.com", "password": "secret123"})
    assert resp.status_code == 400


def test_register_short_password(client):
    resp = client.post(
        "/auth/register",
        json={"email": "short@example.com", "password": "abc"},
    )
    assert resp.status_code == 422


# ---------------------------------------------------------------------------
# Login tests
# ---------------------------------------------------------------------------

def test_login_success(client):
    client.post("/auth/register", json={"email": "login@example.com", "password": "secret123"})
    resp = client.post("/auth/login", json={"email": "login@example.com", "password": "secret123"})
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client):
    client.post("/auth/register", json={"email": "wrongpw@example.com", "password": "secret123"})
    resp = client.post("/auth/login", json={"email": "wrongpw@example.com", "password": "wrong"})
    assert resp.status_code == 401


def test_login_nonexistent_user(client):
    resp = client.post("/auth/login", json={"email": "nobody@example.com", "password": "secret123"})
    assert resp.status_code == 401


def test_login_inactive_user(client, db):
    """Inactive users must not be able to log in."""
    user = User(
        email="inactive@example.com",
        hashed_password=hash_password("secret123"),
        role=UserRole.CLIENT,
        is_active=False,
    )
    db.add(user)
    db.commit()
    resp = client.post("/auth/login", json={"email": "inactive@example.com", "password": "secret123"})
    assert resp.status_code == 401


# ---------------------------------------------------------------------------
# JWT / /auth/me tests
# ---------------------------------------------------------------------------

def test_get_me_success(client, db):
    """Valid token returns current user info."""
    user = User(
        email="me@example.com",
        hashed_password=hash_password("secret123"),
        role=UserRole.DESIGNER,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    token = create_access_token(subject=user.id, role=UserRole.DESIGNER.value)
    resp = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["email"] == "me@example.com"
    assert data["role"] == "DESIGNER"


def test_get_me_invalid_token(client):
    resp = client.get("/auth/me", headers={"Authorization": "Bearer invalidtoken"})
    assert resp.status_code == 401


def test_get_me_missing_token(client):
    resp = client.get("/auth/me")
    assert resp.status_code == 401  # get_current_user raises 401 when credentials absent


def test_get_me_expired_token(client, db):
    """Expired tokens must return 401."""
    from datetime import timedelta
    user = User(
        email="expired@example.com",
        hashed_password=hash_password("secret123"),
        role=UserRole.CLIENT,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    expired_token = create_access_token(
        subject=user.id,
        expires_delta=timedelta(seconds=-1),
    )
    resp = client.get("/auth/me", headers={"Authorization": f"Bearer {expired_token}"})
    assert resp.status_code == 401


# ---------------------------------------------------------------------------
# Role authorization tests
# ---------------------------------------------------------------------------

def test_client_cannot_create_designer_profile(client):
    client.post("/auth/register", json={"email": "clt@example.com", "password": "secret123", "role": "CLIENT"})
    r = client.post("/auth/login", json={"email": "clt@example.com", "password": "secret123"})
    token = r.json()["access_token"]
    resp = client.post(
        "/profiles/designer",
        json={"headline": "Hack"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 403


def test_designer_cannot_create_client_profile(client):
    client.post("/auth/register", json={"email": "dsgn@example.com", "password": "secret123", "role": "DESIGNER"})
    r = client.post("/auth/login", json={"email": "dsgn@example.com", "password": "secret123"})
    token = r.json()["access_token"]
    resp = client.post(
        "/profiles/client",
        json={"company_name": "Hack"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 403


def test_designer_cannot_create_project(client):
    client.post("/auth/register", json={"email": "d2@example.com", "password": "secret123", "role": "DESIGNER"})
    r = client.post("/auth/login", json={"email": "d2@example.com", "password": "secret123"})
    token = r.json()["access_token"]
    resp = client.post(
        "/projects/",
        json={"title": "Hack Project"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 403
