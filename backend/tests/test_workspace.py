import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.project import Project, ProjectStatus
from app.models.milestone import MilestoneStatus
from app.models.task import TaskStatus, TaskPriority
from app.models.user import User, UserRole
from app.models.profile import DesignerProfile
from app.utils.security import hash_password, create_access_token
from app.models.delivery import DeliveryStatus
from app.models.workspace import ProjectEventType

# Fixtures for test data

@pytest.fixture
def client_user(db):
    user = User(email="client_ws@proj.com", hashed_password=hash_password("secret"), role=UserRole.CLIENT, is_active=True)
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
    user = User(email="designer_ws@proj.com", hashed_password=hash_password("secret"), role=UserRole.DESIGNER, is_active=True)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@pytest.fixture
def designer_headers(designer_user):
    token = create_access_token(subject=designer_user.id, role=UserRole.DESIGNER.value)
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def designer_profile(db, designer_user):
    profile = DesignerProfile(user_id=designer_user.id, headline="Test Designer", bio="Bio", hourly_rate=50)
    db.add(profile)
    db.commit()
    return profile

@pytest.fixture
def active_project(client, client_headers, db: Session, client_user, designer_user, designer_profile):
    """Creates an active project with an assigned designer."""
    resp = client.post("/projects/", json={
        "title": "Workspace Test Project",
        "description": "Test",
        "budget": 50000,
        "requirements": "Need a workspace"
    }, headers=client_headers)
    assert resp.status_code == 201
    project_id = resp.json()["id"]
    
    # Assign designer and open project
    project = db.query(Project).get(project_id)
    project.assigned_designer_id = designer_user.id
    project.status = ProjectStatus.IN_PROGRESS
    db.commit()
    return project

@pytest.fixture
def other_client_user(db):
    import uuid
    email = f"other_{uuid.uuid4().hex[:6]}@example.com"
    user = User(email=email, hashed_password=hash_password("secret"), role=UserRole.CLIENT, is_active=True)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@pytest.fixture
def other_client_headers(other_client_user):
    token = create_access_token(subject=other_client_user.id, role=UserRole.CLIENT.value)
    return {"Authorization": f"Bearer {token}"}

# Tests

def test_unauthorized_workspace_access(client, active_project, other_client_headers):
    resp = client.get(f"/projects/{active_project.id}/workspace/", headers=other_client_headers)
    assert resp.status_code == 403

def test_get_empty_workspace(client, active_project, client_headers):
    resp = client.get(f"/projects/{active_project.id}/workspace/", headers=client_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["project_id"] == active_project.id
    assert data["milestones"] == []
    assert data["tasks"] == []

def test_milestone_crud(client, active_project, client_headers):
    # Create
    resp = client.post(f"/projects/{active_project.id}/workspace/milestones", json={
        "title": "Phase 1: Design",
        "description": "Initial mockups",
        "order": 1
    }, headers=client_headers)
    assert resp.status_code == 201
    milestone_id = resp.json()["id"]
    assert resp.json()["status"] == MilestoneStatus.PENDING.value

    # Update
    resp = client.put(f"/projects/{active_project.id}/workspace/milestones/{milestone_id}", json={
        "status": MilestoneStatus.IN_PROGRESS.value
    }, headers=client_headers)
    assert resp.status_code == 200
    assert resp.json()["status"] == MilestoneStatus.IN_PROGRESS.value

    # Delete
    resp = client.delete(f"/projects/{active_project.id}/workspace/milestones/{milestone_id}", headers=client_headers)
    assert resp.status_code == 204

def test_task_crud_and_assignment(client, active_project, client_headers, designer_user, other_client_headers):
    # Need a milestone first
    milestone_resp = client.post(f"/projects/{active_project.id}/workspace/milestones", json={"title": "M1"}, headers=client_headers)
    milestone_id = milestone_resp.json()["id"]

    # Create task assigned to designer
    resp = client.post(f"/projects/{active_project.id}/workspace/tasks", json={
        "milestone_id": milestone_id,
        "title": "Wireframes",
        "assigned_user_id": designer_user.id
    }, headers=client_headers)
    assert resp.status_code == 201
    task_id = resp.json()["id"]

    # Try assigning to someone not in project
    resp = client.put(f"/projects/{active_project.id}/workspace/tasks/{task_id}", json={
        "assigned_user_id": 9999
    }, headers=client_headers)
    assert resp.status_code == 400
    assert "must be the project client or assigned designer" in resp.json()["detail"]

    # Delete task
    resp = client.delete(f"/projects/{active_project.id}/workspace/tasks/{task_id}", headers=client_headers)
    assert resp.status_code == 204

def test_delivery_lifecycle(client, active_project, client_headers, designer_headers, designer_user, db):
    # Designer uploads a file
    file_resp = client.post(f"/projects/{active_project.id}/workspace/files", json={
        "filename": "logo.png",
        "file_url": "https://example.com/logo.png"
    }, headers=designer_headers)
    assert file_resp.status_code == 201
    file_id = file_resp.json()["id"]

    # Client tries to submit delivery (should fail, only designer can)
    resp = client.post(f"/projects/{active_project.id}/workspace/deliveries", json={
        "message": "Here is my work",
        "file_ids": [file_id]
    }, headers=client_headers)
    assert resp.status_code == 403

    # Designer submits delivery
    resp = client.post(f"/projects/{active_project.id}/workspace/deliveries", json={
        "message": "Here is my work",
        "file_ids": [file_id]
    }, headers=designer_headers)
    assert resp.status_code == 201
    delivery_id = resp.json()["id"]
    assert resp.json()["version"] == 1
    assert resp.json()["status"] == DeliveryStatus.PENDING_REVIEW.value

    # Designer tries to accept (should fail, only client can)
    resp = client.post(f"/projects/{active_project.id}/workspace/deliveries/{delivery_id}/accept", headers=designer_headers)
    assert resp.status_code == 403

    # Client requests revision
    resp = client.post(f"/projects/{active_project.id}/workspace/deliveries/{delivery_id}/revisions", json={
        "request_reason": "Changes needed",
        "client_comment": "Make it pop"
    }, headers=client_headers)
    assert resp.status_code == 201

    # Client accepts delivery (should fail, it's not pending_review anymore)
    resp = client.post(f"/projects/{active_project.id}/workspace/deliveries/{delivery_id}/accept", headers=client_headers)
    assert resp.status_code == 400

    # Designer submits V2
    resp = client.post(f"/projects/{active_project.id}/workspace/deliveries", json={
        "message": "Fixed it"
    }, headers=designer_headers)
    assert resp.status_code == 201
    delivery_id_v2 = resp.json()["id"]
    assert resp.json()["version"] == 2

    # Client accepts V2
    resp = client.post(f"/projects/{active_project.id}/workspace/deliveries/{delivery_id_v2}/accept", headers=client_headers)
    assert resp.status_code == 200
    assert resp.json()["status"] == DeliveryStatus.ACCEPTED.value

def test_collaboration_events(client, active_project, client_headers):
    resp = client.post(f"/projects/{active_project.id}/workspace/events", json={
        "event_type": ProjectEventType.COMMENT.value,
        "content": "Looking forward to working together!"
    }, headers=client_headers)
    assert resp.status_code == 201

    # Check aggregation
    ws_resp = client.get(f"/projects/{active_project.id}/workspace/", headers=client_headers)
    assert ws_resp.status_code == 200
    events = ws_resp.json()["events"]
    assert len(events) >= 1
    assert any(e["event_type"] == ProjectEventType.COMMENT.value for e in events)

def test_completed_project_restrictions(client, active_project, client_headers, db):
    # Complete the project
    active_project.status = ProjectStatus.COMPLETED
    db.commit()

    # Try to add a milestone
    resp = client.post(f"/projects/{active_project.id}/workspace/milestones", json={"title": "M1"}, headers=client_headers)
    assert resp.status_code == 400
    assert "completed" in resp.json()["detail"]
