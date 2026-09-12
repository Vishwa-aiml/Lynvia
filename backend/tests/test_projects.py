"""Project CRUD and ownership tests."""
import pytest
from app.models.user import User, UserRole
from app.models.profile import DesignerProfile
from app.utils.security import hash_password, create_access_token


@pytest.fixture
def client_user(db):
    user = User(
        email="client@proj.com",
        hashed_password=hash_password("secret123"),
        role=UserRole.CLIENT,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def client_headers(client_user):
    token = create_access_token(subject=client_user.id, role=UserRole.CLIENT.value)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def designer_user(db):
    user = User(
        email="designer@proj.com",
        hashed_password=hash_password("secret123"),
        role=UserRole.DESIGNER,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def designer_headers(designer_user):
    token = create_access_token(subject=designer_user.id, role=UserRole.DESIGNER.value)
    return {"Authorization": f"Bearer {token}"}


# ---------------------------------------------------------------------------
# Project creation
# ---------------------------------------------------------------------------

def test_create_project(client, client_headers):
    resp = client.post(
        "/projects/",
        json={"title": "Website Redesign", "description": "Full redesign", "budget": 500000},
        headers=client_headers,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "Website Redesign"
    assert data["status"] == "draft"
    assert data["assigned_designer_id"] is None


def test_create_project_no_auth(client):
    resp = client.post("/projects/", json={"title": "Unauthorized"})
    assert resp.status_code == 401  # get_current_user raises 401 when no credentials


def test_designer_cannot_create_project(client, designer_headers):
    resp = client.post(
        "/projects/",
        json={"title": "Hack Project"},
        headers=designer_headers,
    )
    assert resp.status_code == 403


# ---------------------------------------------------------------------------
# Project listing and retrieval
# ---------------------------------------------------------------------------

def test_list_projects(client, client_user, client_headers):
    client.post("/projects/", json={"title": "P1"}, headers=client_headers)
    client.post("/projects/", json={"title": "P2"}, headers=client_headers)
    resp = client.get("/projects/", headers=client_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 2


def test_get_project_by_id(client, client_headers):
    r = client.post("/projects/", json={"title": "Findable"}, headers=client_headers)
    project_id = r.json()["id"]
    resp = client.get(f"/projects/{project_id}")
    assert resp.status_code == 200
    assert resp.json()["title"] == "Findable"


def test_get_nonexistent_project(client):
    resp = client.get("/projects/999999")
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# Project update and ownership
# ---------------------------------------------------------------------------

def test_update_project_title(client, client_headers):
    r = client.post("/projects/", json={"title": "Old Title"}, headers=client_headers)
    project_id = r.json()["id"]
    resp = client.put(
        f"/projects/{project_id}",
        json={"title": "New Title"},
        headers=client_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["title"] == "New Title"


def test_client_cannot_update_other_clients_project(client, db):
    """A second client must not be able to update another client's project."""
    c1 = User(email="c1@test.com", hashed_password=hash_password("secret123"), role=UserRole.CLIENT, is_active=True)
    c2 = User(email="c2@test.com", hashed_password=hash_password("secret123"), role=UserRole.CLIENT, is_active=True)
    db.add_all([c1, c2])
    db.commit()
    db.refresh(c1)
    db.refresh(c2)

    t1 = create_access_token(subject=c1.id, role=UserRole.CLIENT.value)
    t2 = create_access_token(subject=c2.id, role=UserRole.CLIENT.value)

    r = client.post("/projects/", json={"title": "C1 Project"}, headers={"Authorization": f"Bearer {t1}"})
    project_id = r.json()["id"]

    resp = client.put(
        f"/projects/{project_id}",
        json={"title": "Hijacked"},
        headers={"Authorization": f"Bearer {t2}"},
    )
    assert resp.status_code == 403


def test_invalid_status_transition(client, client_headers):
    """Cannot jump from DRAFT directly to COMPLETED."""
    r = client.post("/projects/", json={"title": "State Test"}, headers=client_headers)
    project_id = r.json()["id"]
    resp = client.put(
        f"/projects/{project_id}",
        json={"status": "completed"},
        headers=client_headers,
    )
    assert resp.status_code == 400
