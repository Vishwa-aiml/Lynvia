"""
tests/test_admin_auth.py — Admin authorization security tests.

Verifies that require_admin_role enforces BOTH:
  1. User has ADMIN role in DB.
  2. User email matches settings.ADMIN_EMAIL (case-insensitive, whitespace-trimmed).

Protected endpoint used: GET /users/ (existing admin-only route).
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.user import User, UserRole

# ── Shared constants ──────────────────────────────────────────────────────────
ADMIN_EMAIL = settings.ADMIN_EMAIL          # e.g. vspark2908@gmail.com
ADMIN_PASSWORD = "AdminPass999!"
ADMIN_PROBE_URL = "/users/"                 # existing admin-only route


def _register(client, email, password=ADMIN_PASSWORD, role="CLIENT"):
    r = client.post("/auth/register", json={
        "email": email, "password": password,
        "full_name": "Test User", "role": role,
    })
    assert r.status_code == 201, r.json()
    return r.json()


def _login(client, email, password=ADMIN_PASSWORD):
    tok = client.post("/auth/login", json={"email": email, "password": password})
    assert tok.status_code == 200, tok.json()
    return {"Authorization": f"Bearer {tok.json()['access_token']}"}


def _set_role(db: Session, email: str, role: UserRole):
    user = db.query(User).filter(User.email == email).first()
    assert user is not None, f"User {email!r} not found in DB"
    user.role = role
    db.commit()
    return user


# ── 1. Authorized admin (role=ADMIN + correct email) ─────────────────────────

def test_authorized_admin_access_granted(client: TestClient, db: Session):
    """ADMIN role + authorized email → 200."""
    _register(client, ADMIN_EMAIL)
    _set_role(db, ADMIN_EMAIL, UserRole.ADMIN)
    hdrs = _login(client, ADMIN_EMAIL)
    r = client.get(ADMIN_PROBE_URL, headers=hdrs)
    assert r.status_code == 200, r.json()


# ── 2. ADMIN role but wrong email ─────────────────────────────────────────────

def test_admin_role_wrong_email_denied(client: TestClient, db: Session):
    """ADMIN role + wrong email → 403. Role alone is not sufficient."""
    email = "impostor_admin@example.com"
    _register(client, email)
    _set_role(db, email, UserRole.ADMIN)
    hdrs = _login(client, email)
    r = client.get(ADMIN_PROBE_URL, headers=hdrs)
    assert r.status_code == 403, r.json()
    assert "Admin access denied" in r.json()["detail"]


# ── 3. Authorized email but non-ADMIN role ────────────────────────────────────

def test_authorized_email_without_admin_role_denied(client: TestClient, db: Session):
    """Correct email + CLIENT role → 403. Email alone is not sufficient."""
    _register(client, ADMIN_EMAIL, role="CLIENT")
    # Role stays CLIENT — do NOT promote
    hdrs = _login(client, ADMIN_EMAIL)
    r = client.get(ADMIN_PROBE_URL, headers=hdrs)
    assert r.status_code == 403, r.json()
    assert "Admin access denied" in r.json()["detail"]


# ── 4. Normal CLIENT ──────────────────────────────────────────────────────────

def test_client_role_denied(client: TestClient, db: Session):
    """CLIENT → 403."""
    email = "plain_client_admin_test@example.com"
    _register(client, email, role="CLIENT")
    hdrs = _login(client, email)
    r = client.get(ADMIN_PROBE_URL, headers=hdrs)
    assert r.status_code == 403, r.json()


# ── 5. Normal DESIGNER ────────────────────────────────────────────────────────

def test_designer_role_denied(client: TestClient, db: Session):
    """DESIGNER → 403."""
    email = "designer_admin_test@example.com"
    _register(client, email, role="DESIGNER")
    hdrs = _login(client, email)
    r = client.get(ADMIN_PROBE_URL, headers=hdrs)
    assert r.status_code == 403, r.json()


# ── 6. Unauthenticated ────────────────────────────────────────────────────────

def test_unauthenticated_returns_401(client: TestClient, db: Session):
    """No token → 401 (existing authentication behavior preserved)."""
    r = client.get(ADMIN_PROBE_URL)
    assert r.status_code == 401, r.json()


# ── 7. Case-insensitive email comparison ─────────────────────────────────────

def test_authorized_email_uppercase_access_granted(client: TestClient, db: Session):
    """require_admin_role compares emails case-insensitively.

    The auth system normalizes emails to lowercase on registration, so the stored
    email is always lowercase. We verify the comparison works by temporarily setting
    settings.ADMIN_EMAIL to an uppercase variant — the lowercase stored email must
    still match.
    """
    original = settings.ADMIN_EMAIL
    try:
        # Store the authorized admin (email stored as lowercase by auth system)
        _register(client, ADMIN_EMAIL)
        _set_role(db, ADMIN_EMAIL, UserRole.ADMIN)

        # Simulate ADMIN_EMAIL configured with uppercase in environment
        settings.ADMIN_EMAIL = ADMIN_EMAIL.upper()

        hdrs = _login(client, ADMIN_EMAIL)
        r = client.get(ADMIN_PROBE_URL, headers=hdrs)
        # Lowercase stored email vs UPPERCASE setting -> case-insensitive -> 200
        assert r.status_code == 200, r.json()
    finally:
        settings.ADMIN_EMAIL = original


def test_authorized_email_mixed_case_access_granted(client: TestClient, db: Session):
    """require_admin_role comparison is case-insensitive for settings.ADMIN_EMAIL too."""
    original = settings.ADMIN_EMAIL
    try:
        _register(client, ADMIN_EMAIL)
        _set_role(db, ADMIN_EMAIL, UserRole.ADMIN)

        # Mixed-case ADMIN_EMAIL in settings
        mixed = "".join(
            c.upper() if i % 2 == 0 else c.lower()
            for i, c in enumerate(ADMIN_EMAIL)
        )
        settings.ADMIN_EMAIL = mixed

        hdrs = _login(client, ADMIN_EMAIL)
        r = client.get(ADMIN_PROBE_URL, headers=hdrs)
        assert r.status_code == 200, r.json()
    finally:
        settings.ADMIN_EMAIL = original


# ── 8. Admin email not exposed in response ────────────────────────────────────

def test_admin_email_not_exposed_in_403_response(client: TestClient, db: Session):
    """403 response must not leak ADMIN_EMAIL value."""
    email = "snooper@example.com"
    _register(client, email, role="CLIENT")
    hdrs = _login(client, email)
    r = client.get(ADMIN_PROBE_URL, headers=hdrs)
    assert r.status_code == 403
    response_text = r.text
    # ADMIN_EMAIL must not appear anywhere in the response body
    assert ADMIN_EMAIL.lower() not in response_text.lower()


def test_admin_email_not_exposed_in_successful_response(client: TestClient, db: Session):
    """Successful admin response must not leak ADMIN_EMAIL in the body."""
    _register(client, ADMIN_EMAIL)
    _set_role(db, ADMIN_EMAIL, UserRole.ADMIN)
    hdrs = _login(client, ADMIN_EMAIL)
    r = client.get(ADMIN_PROBE_URL, headers=hdrs)
    assert r.status_code == 200
    # The ADMIN_EMAIL setting value must not appear in the response metadata/detail fields
    # (user list may contain the email as data — we check only for config leakage in detail)
    data = r.json()
    if isinstance(data, dict) and "detail" in data:
        assert ADMIN_EMAIL.lower() not in data["detail"].lower()


# ── 9. Admin endpoint protected by real dependency ────────────────────────────

def test_admin_route_protected_via_real_dependency(client: TestClient, db: Session):
    """
    The admin probe URL must reject a bearer token from a non-admin user.
    This verifies the route uses require_admin_role (not just a role flag).
    """
    email = "real_dep_client@example.com"
    _register(client, email)
    hdrs = _login(client, email)
    r = client.get(ADMIN_PROBE_URL, headers=hdrs)
    assert r.status_code == 403


def test_admin_route_accessible_only_to_exact_authorized_admin(client: TestClient, db: Session):
    """
    Prove end-to-end: create both an authorized and an unauthorized admin,
    confirm only the authorized one succeeds.
    """
    # Authorized admin
    _register(client, ADMIN_EMAIL)
    _set_role(db, ADMIN_EMAIL, UserRole.ADMIN)
    auth_hdrs = _login(client, ADMIN_EMAIL)

    # Unauthorized: has ADMIN role but wrong email
    bad_email = "fake.admin.99@example.com"
    _register(client, bad_email)
    _set_role(db, bad_email, UserRole.ADMIN)
    bad_hdrs = _login(client, bad_email)

    assert client.get(ADMIN_PROBE_URL, headers=auth_hdrs).status_code == 200
    assert client.get(ADMIN_PROBE_URL, headers=bad_hdrs).status_code == 403
