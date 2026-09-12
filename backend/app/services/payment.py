import json
import uuid
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from fastapi import HTTPException, status

from app.models.payment import (
    Payment, PaymentStatus, Transaction, TransactionType,
    TransactionStatus, LedgerEntry, EntryDirection, DesignerEarning, EarningStatus,
    WebhookEvent
)
from app.models.project import Project
from app.schemas.payment import PaymentVerificationReq
from app.integrations.razorpay.payments import create_order, verify_payment_signature
from app.core.config import settings

def create_payment_order(db: Session, project_id: int, client_id: int) -> Payment:
    project = db.query(Project).filter(Project.id == project_id, Project.client_id == client_id).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found or unauthorized")
    
    if not project.budget:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Project budget not set")
    
    if not project.assigned_designer_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No designer assigned to this project yet")
    
    # Check if a successful payment already exists
    existing_payment = db.query(Payment).filter(
        Payment.project_id == project_id,
        Payment.status == PaymentStatus.SUCCEEDED
    ).first()
    
    if existing_payment:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Payment already completed for this project")
    
    amount = project.budget
    currency = "INR"
    receipt = f"rcptid_{project_id}_{int(datetime.now(timezone.utc).timestamp())}"
    
    try:
        # Request order from Razorpay
        order = create_order(amount=amount, currency=currency, receipt=receipt)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to create payment order: {str(e)}")

    payment = Payment(
        project_id=project_id,
        client_id=client_id,
        amount=amount,
        currency=currency,
        provider="razorpay",
        provider_order_id=order.get("id"),
        status=PaymentStatus.CREATED
    )
    
    db.add(payment)
    db.commit()
    db.refresh(payment)
    return payment

def verify_and_process_payment(db: Session, payment_id: int, client_id: int, req: PaymentVerificationReq):
    payment = db.query(Payment).filter(Payment.id == payment_id, Payment.client_id == client_id).first()
    if not payment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found")
        
    if payment.status == PaymentStatus.SUCCEEDED:
        return payment # Idempotent return
        
    if payment.provider_order_id != req.razorpay_order_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Order ID mismatch")

    is_valid = verify_payment_signature(req.razorpay_order_id, req.razorpay_payment_id, req.razorpay_signature)
    
    if not is_valid:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid payment signature")
    
    payment.provider_payment_id = req.razorpay_payment_id
    
    return _process_successful_payment(db, payment)

def process_razorpay_webhook(db: Session, payload: dict):
    event_id = payload.get("id")
    event_type = payload.get("event")
    
    if not event_id or not event_type:
        return
        
    # Idempotency Check
    existing_event = db.query(WebhookEvent).filter(
        WebhookEvent.provider == "razorpay",
        WebhookEvent.event_id == event_id
    ).first()
    
    if existing_event:
        return # Already processed
    
    webhook_event = WebhookEvent(
        provider="razorpay",
        event_id=event_id,
        event_type=event_type,
        payload=json.dumps(payload),
        processed=0
    )
    db.add(webhook_event)
    db.commit()
    
    if event_type == "order.paid":
        order_entity = payload.get("payload", {}).get("order", {}).get("entity", {})
        provider_order_id = order_entity.get("id")
        
        payment = db.query(Payment).filter(Payment.provider_order_id == provider_order_id).first()
        if payment and payment.status != PaymentStatus.SUCCEEDED:
            payment.provider_payment_id = payload.get("payload", {}).get("payment", {}).get("entity", {}).get("id")
            _process_successful_payment(db, payment)
            
    # Mark as processed
    webhook_event.processed = 1
    webhook_event.processed_at = datetime.now(timezone.utc)
    db.commit()

def _process_successful_payment(db: Session, payment: Payment) -> Payment:
    """Core Ledger Generation logic. This handles commission breakdown and creates immutable ledger records."""
    if payment.status == PaymentStatus.SUCCEEDED:
        return payment # Ensure double execution is impossible
        
    payment.status = PaymentStatus.SUCCEEDED
    payment.paid_at = datetime.now(timezone.utc)
    
    project = db.query(Project).filter(Project.id == payment.project_id).first()
    
    # 1. Main Payment Transaction
    tx_payment = Transaction(
        project_id=payment.project_id,
        payment_id=payment.id,
        type=TransactionType.PAYMENT,
        amount=payment.amount,
        currency=payment.currency,
        status=TransactionStatus.COMPLETED
    )
    db.add(tx_payment)
    db.flush() # flush to get tx_payment.id
    
    ledger_client = LedgerEntry(
        project_id=project.id,
        payment_id=payment.id,
        transaction_id=tx_payment.id,
        user_id=payment.client_id,
        entry_type="CLIENT_PAYMENT",
        amount=payment.amount,
        currency=payment.currency,
        direction=EntryDirection.CREDIT,
        description="Client payment for project"
    )
    db.add(ledger_client)
    
    # 2. Commission Calculation
    commission_rate = settings.PLATFORM_COMMISSION_RATE
    platform_fee = int(round(payment.amount * commission_rate))
    net_designer_amount = payment.amount - platform_fee
    
    tx_commission = Transaction(
        project_id=payment.project_id,
        payment_id=payment.id,
        type=TransactionType.COMMISSION,
        amount=platform_fee,
        currency=payment.currency,
        status=TransactionStatus.COMPLETED
    )
    db.add(tx_commission)
    db.flush()
    
    ledger_commission = LedgerEntry(
        project_id=project.id,
        payment_id=payment.id,
        transaction_id=tx_commission.id,
        entry_type="PLATFORM_COMMISSION",
        amount=platform_fee,
        currency=payment.currency,
        direction=EntryDirection.DEBIT,
        description="Platform fee deducted"
    )
    db.add(ledger_commission)
    
    # 3. Designer Earning Registration
    tx_earning = Transaction(
        project_id=payment.project_id,
        payment_id=payment.id,
        type=TransactionType.DESIGNER_EARNING,
        amount=net_designer_amount,
        currency=payment.currency,
        status=TransactionStatus.COMPLETED
    )
    db.add(tx_earning)
    db.flush()
    
    designer_earning = DesignerEarning(
        designer_id=project.assigned_designer_id,
        project_id=project.id,
        payment_id=payment.id,
        gross_amount=payment.amount,
        platform_fee=platform_fee,
        net_amount=net_designer_amount,
        currency=payment.currency,
        status=EarningStatus.PENDING
    )
    db.add(designer_earning)
    
    # Note: We do NOT add a ledger entry for the designer yet, because the money is held in escrow.
    # The ledger will be credited to the designer when the project delivery is accepted.
    
    db.commit()
    db.refresh(payment)

    # Notify client: payment successful
    try:
        from app.models.notification import NotificationType
        import app.services.notifications as notif_svc
        notif_svc.create_notification(
            db=db,
            recipient_id=payment.client_id,
            notification_type=NotificationType.PAYMENT_SUCCESS,
            title="Payment successful",
            message=f"Payment of {payment.amount} {payment.currency} for project '{project.title}' was successful.",
            entity_type="payment",
            entity_id=payment.id,
            meta_data={"project_id": project.id, "payment_id": payment.id},
        )
        db.commit()
    except Exception:
        pass

    return payment
