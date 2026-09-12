import pytest
from fastapi.testclient import TestClient
from app.db.session import get_db
from app.models.user import User, UserRole
from app.models.profile import ClientProfile, DesignerProfile
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


def test_create_client_profile(client, test_user, auth_header):
    resp = client.post(
        "/profiles/client",
        json={"company_name": "Acme Inc", "bio": "Design agency", "location": "NYC", "website": "acme.com"},
        headers=auth_header,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["company_name"] == "Acme Inc"
    assert data["user_id"] == test_user.id


def test_create_client_profile_no_auth(client, test_user):
    resp = client.post(
        "/profiles/client",
        json={"company_name": "Acme Inc", "bio": "Design agency"},
    )
    assert resp.status_code in (401, 403)  # HTTPBearer returns 403 when no credentials


def test_create_client_profile_duplicate(client, test_user, auth_header, db):
    client.post(
        "/profiles/client",
        json={"company_name": "Acme Inc"},
        headers=auth_header,
    )
    resp = client.post(
        "/profiles/client",
        json={"company_name": "Acme Inc 2"},
        headers=auth_header,
    )
    assert resp.status_code == 400


def test_get_client_profile(client, test_user, auth_header):
    client.post(
        "/profiles/client",
        json={"company_name": "Acme Inc", "bio": "Design agency"},
        headers=auth_header,
    )
    resp = client.get(f"/profiles/client/{test_user.id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["company_name"] == "Acme Inc"


def test_update_client_profile_unauthorized(client, test_user, auth_header):
    client.post(
        "/profiles/client",
        json={"company_name": "Acme Inc"},
        headers=auth_header,
    )
    # Token for a non-existent user ID — dependency returns 401
    bob_token = create_access_token(subject=99999, role=UserRole.CLIENT.value)
    bob_headers = {"Authorization": f"Bearer {bob_token}"}

    resp = client.put(
        f"/profiles/client/{test_user.id}",
        json={"company_name": "Hacked"},
        headers=bob_headers,
    )
    assert resp.status_code == 401  # user not found in DB


def test_create_designer_profile(client, db):
    """Only DESIGNER role users can create a designer profile."""
    designer = User(
        email="designer@profiles.com",
        full_name="Designer One",
        hashed_password=hash_password("secret123"),
        role=UserRole.DESIGNER,
        is_active=True,
    )
    db.add(designer)
    db.commit()
    db.refresh(designer)

    designer_token = create_access_token(subject=designer.id, role=UserRole.DESIGNER.value)
    designer_header = {"Authorization": f"Bearer {designer_token}"}

    resp = client.post(
        "/profiles/designer",
        json={"headline": "Logo Designer", "bio": "Expert", "hourly_rate": 50000, "years_experience": 5},
        headers=designer_header,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["headline"] == "Logo Designer"
    assert data["user_id"] == designer.id


def test_client_cannot_create_designer_profile(client, test_user, auth_header):
    """A CLIENT must be rejected when trying to create a designer profile."""
    resp = client.post(
        "/profiles/designer",
        json={"headline": "Designer", "hourly_rate": 50000},
        headers=auth_header,
    )
    assert resp.status_code == 403


def test_designer_profile_rate_validation(client, db):
    """Negative hourly_rate should fail Pydantic validation."""
    designer = User(
        email="d_rate@profiles.com",
        hashed_password=hash_password("secret123"),
        role=UserRole.DESIGNER,
        is_active=True,
    )
    db.add(designer)
    db.commit()
    db.refresh(designer)
    token = create_access_token(subject=designer.id, role=UserRole.DESIGNER.value)
    headers = {"Authorization": f"Bearer {token}"}

    resp = client.post(
        "/profiles/designer",
        json={"headline": "Designer", "hourly_rate": -100},
        headers=headers,
    )
    assert resp.status_code == 422
