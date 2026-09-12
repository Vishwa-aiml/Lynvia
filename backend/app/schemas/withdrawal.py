"""
Pydantic schemas for the Withdrawal domain.
"""
from __future__ import annotations
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator
from app.models.withdrawal import WithdrawalStatus


class WalletOut(BaseModel):
    """Designer wallet summary derived from DesignerEarning records."""
    pending_balance: int = Field(..., description="Earnings not yet released (paise)")
    available_balance: int = Field(..., description="Earnings available for withdrawal (paise)")
    processing_balance: int = Field(..., description="Earnings reserved in active withdrawals (paise)")
    withdrawn_balance: int = Field(..., description="Earnings successfully paid out (paise)")
    currency: str = "INR"


class WithdrawalCreate(BaseModel):
    amount: int = Field(..., gt=0, description="Amount to withdraw in minor units (paise)")
    idempotency_key: Optional[str] = Field(None, max_length=255)


class WithdrawalOut(BaseModel):
    id: int
    designer_profile_id: int
    user_id: int
    amount: int
    currency: str
    status: WithdrawalStatus
    payout_reference: Optional[str] = None
    failure_reason: Optional[str] = None
    idempotency_key: Optional[str] = None
    requested_at: datetime
    processing_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    failed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class WithdrawalListResponse(BaseModel):
    withdrawals: List[WithdrawalOut]
    total: int


class WithdrawalProcessRequest(BaseModel):
    """Admin: move withdrawal to PROCESSING with optional provider reference."""
    payout_reference: Optional[str] = None


class WithdrawalCompleteRequest(BaseModel):
    """Admin: mark withdrawal COMPLETED."""
    payout_reference: Optional[str] = None


class WithdrawalFailRequest(BaseModel):
    """Admin: mark withdrawal FAILED with a reason."""
    failure_reason: str = Field(..., min_length=1, max_length=500)
    payout_reference: Optional[str] = None
