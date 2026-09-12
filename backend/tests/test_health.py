from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root():
    res = client.get("/")
    assert res.status_code == 200
    assert "Lynvia API" in res.json().get("message", "")


def test_health_ready():
    res = client.get("/health/ready")
    assert res.status_code == 200
    assert res.json().get("status") == "ready"
