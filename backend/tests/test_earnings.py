import pytest
from app.models.payment import Payment, PaymentStatus, Transaction, TransactionType, LedgerEntry, DesignerEarning, EarningStatus
from app.models.project import Project
from app.models.user import User, UserRole
from app.services.payment import _process_successful_payment
from app.utils.security import hash_password

@pytest.fixture
def test_user(db):
    user = User(email="earning_client@proj.com", hashed_password=hash_password("secret"), role=UserRole.CLIENT, is_active=True)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def test_ledger_generation_and_commission(db, test_user):
    project = Project(
        client_id=test_user.id,
        assigned_designer_id=1,
        title="Ledger Test",
        budget=100000
    )
    db.add(project)
    db.commit()
    
    payment = Payment(
        project_id=project.id,
        client_id=test_user.id,
        amount=100000,
        provider_order_id="order_ledger_1",
        status=PaymentStatus.CREATED
    )
    db.add(payment)
    db.commit()
    
    _process_successful_payment(db, payment)
    
    tx_payment = db.query(Transaction).filter(Transaction.type == TransactionType.PAYMENT).first()
    assert tx_payment.amount == 100000
    
    tx_commission = db.query(Transaction).filter(Transaction.type == TransactionType.COMMISSION).first()
    assert tx_commission.amount == 12000
    
    tx_earning = db.query(Transaction).filter(Transaction.type == TransactionType.DESIGNER_EARNING).first()
    assert tx_earning.amount == 88000
    
    ledgers = db.query(LedgerEntry).all()
    assert len(ledgers) == 2
    assert ledgers[0].entry_type == "CLIENT_PAYMENT"
    assert ledgers[1].entry_type == "PLATFORM_COMMISSION"
    
    earning = db.query(DesignerEarning).first()
    assert earning.gross_amount == 100000
    assert earning.platform_fee == 12000
    assert earning.net_amount == 88000
    assert earning.status == EarningStatus.PENDING
