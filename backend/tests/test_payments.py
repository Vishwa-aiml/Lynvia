import pytest
from unittest.mock import patch
from app.models.payment import Payment, PaymentStatus
from app.models.project import Project
from app.models.user import User, UserRole
from app.utils.security import hash_password, create_access_token

@pytest.fixture
def mock_razorpay_order():
    with patch("app.services.payment.create_order") as mock:
        mock.return_value = {"id": "order_test123"}
        yield mock

@pytest.fixture
def mock_razorpay_verify():
    with patch("app.services.payment.verify_payment_signature") as mock:
        mock.return_value = True
        yield mock

@pytest.fixture
def test_user(db):
    user = User(email="payment_client@proj.com", hashed_password=hash_password("secret"), role=UserRole.CLIENT, is_active=True)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@pytest.fixture
def test_headers(test_user):
    token = create_access_token(subject=test_user.id, role=UserRole.CLIENT.value)
    return {"Authorization": f"Bearer {token}"}

def test_create_payment_order(client, test_headers, db, test_user, mock_razorpay_order):
    project = Project(
        client_id=test_user.id,
        assigned_designer_id=1,
        title="Payment Test",
        budget=100000,
        status="in_progress"
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    
    response = client.post(
        f"/projects/{project.id}/payments",
        headers=test_headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["amount"] == 100000
    assert data["status"] == "created"
    assert data["provider_order_id"] == "order_test123"

def test_verify_payment(client, test_headers, db, test_user, mock_razorpay_verify):
    project = Project(
        client_id=test_user.id,
        assigned_designer_id=1,
        title="Verify Test",
        budget=50000,
    )
    db.add(project)
    db.commit()
    
    payment = Payment(
        project_id=project.id,
        client_id=test_user.id,
        amount=50000,
        provider_order_id="order_test_456",
        status=PaymentStatus.CREATED
    )
    db.add(payment)
    db.commit()
    
    req_data = {
        "razorpay_order_id": "order_test_456",
        "razorpay_payment_id": "pay_test_789",
        "razorpay_signature": "valid_signature"
    }
    
    response = client.post(
        f"/payments/{payment.id}/verify",
        headers=test_headers,
        json=req_data
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "succeeded"
    assert data["provider_payment_id"] == "pay_test_789"
