from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime
from app.models.payment import PaymentStatus, TransactionType, TransactionStatus, EntryDirection, EarningStatus


class PaymentVerificationReq(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str


class PaymentOut(BaseModel):
    id: int
    project_id: int
    client_id: int
    amount: int
    currency: str
    provider: str
    provider_order_id: Optional[str]
    provider_payment_id: Optional[str]
    status: PaymentStatus
    paid_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TransactionOut(BaseModel):
    id: int
    payment_id: Optional[int]
    project_id: int
    type: TransactionType
    amount: int
    currency: str
    status: TransactionStatus
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LedgerEntryOut(BaseModel):
    id: int
    project_id: int
    payment_id: Optional[int]
    transaction_id: Optional[int]
    user_id: Optional[int]
    entry_type: str
    amount: int
    currency: str
    direction: EntryDirection
    description: Optional[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DesignerEarningOut(BaseModel):
    id: int
    designer_id: int
    project_id: int
    payment_id: Optional[int]
    gross_amount: int
    platform_fee: int
    net_amount: int
    currency: str
    status: EarningStatus
    available_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EarningSummaryOut(BaseModel):
    total_pending: int
    total_available: int
    currency: str = "INR"
