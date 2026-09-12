"""Tests for designer services (services, skills, specializations, availability)."""
import pytest
from app.models.user import User, UserRole
from app.models.profile import DesignerProfile
from app.utils.security import create_access_token


@pytest.fixture
def designer_user(db):
    """Create a test designer user."""
    user = User(
        email="designer@example.com",
        full_name="Designer Name",
        hashed_password="hashed_secret",
        role=UserRole.DESIGNER,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def designer_profile(db, designer_user):
    """Create a test designer profile."""
    profile = DesignerProfile(
        user_id=designer_user.id,
        headline="Professional Designer",
        bio="Experienced in branding",
        hourly_rate=50000,
        years_experience=5,
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


@pytest.fixture
def designer_headers(designer_user):
    """Create auth headers for designer."""
    token = create_access_token(subject=designer_user.id, role=UserRole.DESIGNER.value)
    return {"Authorization": f"Bearer {token}"}


def test_create_service(client, designer_profile, designer_headers):
    """Test creating a service."""
    resp = client.post(
        "/services/",
        json={
            "title": "Logo Design",
            "description": "Professional logo design",
            "category": "logo",
            "price": 50000,
            "delivery_days": 7,
        },
        headers=designer_headers,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "Logo Design"
    assert data["designer_id"] == designer_profile.id


def test_create_service_no_auth(client):
    """Test creating a service without auth."""
    resp = client.post(
        "/services/",
        json={"title": "Logo Design", "category": "logo", "price": 50000},
    )
    assert resp.status_code == 401


def test_get_designer_services(client, designer_profile, designer_headers):
    """Test listing designer's services."""
    # Create a service
    client.post(
        "/services/",
        json={"title": "Logo Design", "category": "logo", "price": 50000, "delivery_days": 7},
        headers=designer_headers,
    )
    # List services
    resp = client.get(f"/services/designers/{designer_profile.id}/services")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) > 0
    assert data[0]["title"] == "Logo Design"


def test_list_skills(client):
    """Test listing all skills."""
    resp = client.get("/services/skills")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)


def test_create_skill(client, designer_user):
    """Test creating a skill."""
    token = create_access_token(subject=designer_user.id, role=UserRole.DESIGNER.value)
    headers = {"Authorization": f"Bearer {token}"}
    
    resp = client.post(
        "/services/skills",
        json={"name": "UI Design", "category": "design"},
        headers=headers,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "UI Design"
