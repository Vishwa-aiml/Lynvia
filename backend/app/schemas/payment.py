from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime
from enum import Enum


class PaymentStatus(str, Enum):
    CREATED = "CREATED"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    REFUNDED = "REFUNDED"


class TransactionType(str, Enum):
    PAYMENT = "PAYMENT"
    COMMISSION = "COMMISSION"
    DESIGNER_EARNING = "DESIGNER_EARNING"
    WITHDRAWAL = "WITHDRAWAL"
    REFUND = "REFUND"


class TransactionStatus(str, Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class EntryDirection(str, Enum):
    CREDIT = "CREDIT"
    DEBIT = "DEBIT"


class EarningStatus(str, Enum):
    PENDING = "PENDING"
    AVAILABLE = "AVAILABLE"
    WITHDRAWN = "WITHDRAWN"


class PaymentVerificationReq(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str


class PaymentOut(BaseModel):
    id: str
    projectId: str
    clientId: str
    amount: int
    currency: str
    provider: str
    providerOrderId: Optional[str] = None
    providerPaymentId: Optional[str] = None
    status: PaymentStatus
    paidAt: Optional[datetime] = None
    createdAt: datetime
    updatedAt: datetime

    model_config = ConfigDict(from_attributes=True)


class TransactionOut(BaseModel):
    id: str
    paymentId: Optional[str] = None
    projectId: str
    type: TransactionType
    amount: int
    currency: str
    status: TransactionStatus
    createdAt: datetime

    model_config = ConfigDict(from_attributes=True)


class LedgerEntryOut(BaseModel):
    id: str
    projectId: str
    paymentId: Optional[str] = None
    transactionId: Optional[str] = None
    userId: Optional[str] = None
    entryType: str
    amount: int
    currency: str
    direction: EntryDirection
    description: Optional[str] = None
    createdAt: datetime

    model_config = ConfigDict(from_attributes=True)


class DesignerEarningOut(BaseModel):
    id: str
    designerId: str
    projectId: str
    paymentId: Optional[str] = None
    grossAmount: int
    commissionAmount: int
    netAmount: int
    currency: str
    status: EarningStatus
    availableAt: Optional[datetime] = None
    createdAt: datetime
    updatedAt: datetime

    model_config = ConfigDict(from_attributes=True)


class EarningSummaryOut(BaseModel):
    total_pending: int
    total_available: int
    currency: str = "INR"

