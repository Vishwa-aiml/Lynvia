import json
import uuid
from datetime import datetime, timezone
from fastapi import HTTPException, status
from google.cloud.firestore import Client as FirestoreClient, Transaction, transactional

from app.schemas.payment import (
    PaymentStatus, TransactionType, TransactionStatus, EntryDirection, 
    EarningStatus, PaymentVerificationReq, PaymentOut
)
from app.schemas.project import ProjectStatus
from app.integrations.razorpay.payments import create_order, verify_payment_signature
from app.core.config import settings
from app.services.project import get_project


def create_payment_order(db: FirestoreClient, project_id: str, client_id: str) -> PaymentOut:
    project = get_project(db, project_id)
    if not project or project.clientId != client_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found or unauthorized")
    
    if not project.budget:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Project budget not set")
    
    if not project.designerId:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No designer assigned to this project yet")
    
    if project.status != ProjectStatus.AWAITING_PAYMENT:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Project is not in AWAITING_PAYMENT state")
    
    # Check if a successful payment already exists
    existing_payments = db.collection("payments").where("projectId", "==", project_id).where("status", "==", PaymentStatus.SUCCEEDED.value).limit(1).get()
    
    if existing_payments:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Payment already completed for this project")
    
    amount = project.budget
    currency = "INR"
    receipt = f"rcptid_{project_id}_{int(datetime.now(timezone.utc).timestamp())}"
    
    try:
        order = create_order(amount=amount, currency=currency, receipt=receipt)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to create payment order: {str(e)}")

    payment_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)
    
    data = {
        "id": payment_id,
        "projectId": project_id,
        "clientId": client_id,
        "amount": amount,
        "currency": currency,
        "provider": "razorpay",
        "providerOrderId": order.get("id"),
        "status": PaymentStatus.CREATED.value,
        "paidAt": None,
        "createdAt": now,
        "updatedAt": now
    }
    
    db.collection("payments").document(payment_id).set(data)
    return PaymentOut(**data)


def verify_and_process_payment(db: FirestoreClient, payment_id: str, client_id: str, req: PaymentVerificationReq):
    payment_doc = db.collection("payments").document(payment_id).get()
    if not payment_doc.exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found")
        
    payment_data = payment_doc.to_dict()
    if payment_data["clientId"] != client_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found")
        
    if payment_data["status"] == PaymentStatus.SUCCEEDED.value:
        return PaymentOut(**payment_data)
        
    if payment_data["providerOrderId"] != req.razorpay_order_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Order ID mismatch")

    is_valid = verify_payment_signature(req.razorpay_order_id, req.razorpay_payment_id, req.razorpay_signature)
    
    if not is_valid:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid payment signature")
    
    return _process_successful_payment(db, payment_id, req.razorpay_payment_id)


def process_razorpay_webhook(db: FirestoreClient, payload: dict):
    event_id = payload.get("id")
    event_type = payload.get("event")
    
    if not event_id or not event_type:
        return
        
    # Idempotency Check
    webhook_ref = db.collection("webhookEvents").document(f"razorpay_{event_id}")
    if webhook_ref.get().exists:
        return
    
    now = datetime.now(timezone.utc)
    webhook_ref.set({
        "provider": "razorpay",
        "eventId": event_id,
        "eventType": event_type,
        "payload": json.dumps(payload),
        "processed": True,
        "processedAt": now,
        "createdAt": now
    })
    
    if event_type == "order.paid":
        order_entity = payload.get("payload", {}).get("order", {}).get("entity", {})
        provider_order_id = order_entity.get("id")
        provider_payment_id = payload.get("payload", {}).get("payment", {}).get("entity", {}).get("id")
        
        payments = db.collection("payments").where("providerOrderId", "==", provider_order_id).limit(1).get()
        if payments:
            payment_doc = payments[0]
            if payment_doc.to_dict().get("status") != PaymentStatus.SUCCEEDED.value:
                _process_successful_payment(db, payment_doc.id, provider_payment_id)


def _process_successful_payment(db: FirestoreClient, payment_id: str, provider_payment_id: str) -> PaymentOut:
    transaction = db.transaction()
    return _atomic_process_successful_payment(transaction, db, payment_id, provider_payment_id)


@transactional
def _atomic_process_successful_payment(transaction: Transaction, db: FirestoreClient, payment_id: str, provider_payment_id: str) -> PaymentOut:
    payment_ref = db.collection("payments").document(payment_id)
    payment_doc = payment_ref.get(transaction=transaction)
    
    if not payment_doc.exists:
        raise ValueError("Payment not found")
        
    payment_data = payment_doc.to_dict()
    if payment_data["status"] == PaymentStatus.SUCCEEDED.value:
        return PaymentOut(**payment_data)
        
    project_id = payment_data["projectId"]
    project_ref = db.collection("projects").document(project_id)
    project_doc = project_ref.get(transaction=transaction)
    
    if not project_doc.exists:
        raise ValueError("Project not found")
        
    project_data = project_doc.to_dict()
    
    now = datetime.now(timezone.utc)
    amount = payment_data["amount"]
    currency = payment_data["currency"]
    
    # 1. Update Payment
    updated_payment = {
        "status": PaymentStatus.SUCCEEDED.value,
        "providerPaymentId": provider_payment_id,
        "paidAt": now,
        "updatedAt": now
    }
    transaction.update(payment_ref, updated_payment)
    payment_data.update(updated_payment)
    
    # 2. Update Project Status to ACTIVE
    transaction.update(project_ref, {
        "status": ProjectStatus.ACTIVE.value,
        "updatedAt": now
    })
    
    # 3. Main Payment Transaction & Ledger
    tx_payment_id = str(uuid.uuid4())
    transaction.set(db.collection("transactions").document(tx_payment_id), {
        "id": tx_payment_id,
        "projectId": project_id,
        "paymentId": payment_id,
        "type": TransactionType.PAYMENT.value,
        "amount": amount,
        "currency": currency,
        "status": TransactionStatus.COMPLETED.value,
        "createdAt": now
    })
    
    ledger_client_id = str(uuid.uuid4())
    transaction.set(db.collection("ledger").document(ledger_client_id), {
        "id": ledger_client_id,
        "projectId": project_id,
        "paymentId": payment_id,
        "transactionId": tx_payment_id,
        "userId": payment_data["clientId"],
        "entryType": "CLIENT_PAYMENT",
        "amount": amount,
        "currency": currency,
        "direction": EntryDirection.CREDIT.value,
        "description": "Client payment for project",
        "createdAt": now
    })
    
    # 4. Commission Calculation
    commission_rate = settings.PLATFORM_COMMISSION_RATE
    platform_fee = int(round(amount * commission_rate))
    net_designer_amount = amount - platform_fee
    
    tx_commission_id = str(uuid.uuid4())
    transaction.set(db.collection("transactions").document(tx_commission_id), {
        "id": tx_commission_id,
        "projectId": project_id,
        "paymentId": payment_id,
        "type": TransactionType.COMMISSION.value,
        "amount": platform_fee,
        "currency": currency,
        "status": TransactionStatus.COMPLETED.value,
        "createdAt": now
    })
    
    ledger_commission_id = str(uuid.uuid4())
    transaction.set(db.collection("ledger").document(ledger_commission_id), {
        "id": ledger_commission_id,
        "projectId": project_id,
        "paymentId": payment_id,
        "transactionId": tx_commission_id,
        "entryType": "PLATFORM_COMMISSION",
        "amount": platform_fee,
        "currency": currency,
        "direction": EntryDirection.DEBIT.value,
        "description": "Platform fee deducted",
        "createdAt": now
    })
    
    # 5. Designer Earning Registration (Held in escrow, marked PENDING)
    tx_earning_id = str(uuid.uuid4())
    transaction.set(db.collection("transactions").document(tx_earning_id), {
        "id": tx_earning_id,
        "projectId": project_id,
        "paymentId": payment_id,
        "type": TransactionType.DESIGNER_EARNING.value,
        "amount": net_designer_amount,
        "currency": currency,
        "status": TransactionStatus.COMPLETED.value,
        "createdAt": now
    })
    
    earning_id = str(uuid.uuid4())
    transaction.set(db.collection("designerEarnings").document(earning_id), {
        "id": earning_id,
        "designerId": project_data["designerId"],
        "projectId": project_id,
        "paymentId": payment_id,
        "grossAmount": amount,
        "commissionAmount": platform_fee,
        "netAmount": net_designer_amount,
        "currency": currency,
        "status": EarningStatus.PENDING.value,
        "availableAt": None,
        "createdAt": now,
        "updatedAt": now
    })
    
    return PaymentOut(**payment_data)

