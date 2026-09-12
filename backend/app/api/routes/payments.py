from fastapi import APIRouter, Depends, Request, Header
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.api.dependencies import get_current_user
from app.models.user import User, UserRole
from app.schemas.payment import PaymentOut, PaymentVerificationReq
from app.services.payment import create_payment_order, verify_and_process_payment, process_razorpay_webhook
from app.integrations.razorpay.webhooks import verify_webhook_signature
from fastapi import HTTPException, status

router = APIRouter()


@router.post("/projects/{project_id}/payments", response_model=PaymentOut, status_code=status.HTTP_201_CREATED)
def create_payment(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new payment order for a project."""
    if current_user.role != UserRole.CLIENT:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only clients can initiate payments")
    return create_payment_order(db, project_id, current_user.id)


@router.post("/payments/{payment_id}/verify", response_model=PaymentOut)
def verify_payment(
    payment_id: int,
    req: PaymentVerificationReq,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Verify a payment signature after client checkout."""
    if current_user.role != UserRole.CLIENT:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only clients can verify payments")
    return verify_and_process_payment(db, payment_id, current_user.id, req)


@router.post("/payments/webhook/razorpay", status_code=status.HTTP_200_OK)
async def razorpay_webhook(
    request: Request,
    x_razorpay_signature: str = Header(None),
    db: Session = Depends(get_db)
):
    """Handle incoming Razorpay webhooks."""
    if not x_razorpay_signature:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing signature")
        
    body = await request.body()
    is_valid = verify_webhook_signature(body, x_razorpay_signature)
    
    if not is_valid:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid signature")
        
    payload = await request.json()
    process_razorpay_webhook(db, payload)
    return {"status": "ok"}
