"""
Pydantic schemas for the Withdrawal domain.
"""
from __future__ import annotations
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum


class WithdrawalStatus(str, Enum):
    REQUESTED = "REQUESTED"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class WalletOut(BaseModel):
    """Designer wallet summary derived from DesignerEarning records."""
    pendingBalance: int = Field(..., description="Earnings not yet released (paise)")
    availableBalance: int = Field(..., description="Earnings available for withdrawal (paise)")
    processingBalance: int = Field(..., description="Earnings reserved in active withdrawals (paise)")
    withdrawnBalance: int = Field(..., description="Earnings successfully paid out (paise)")
    currency: str = "INR"


class WithdrawalCreate(BaseModel):
    amount: int = Field(..., gt=0, description="Amount to withdraw in minor units (paise)")
    idempotencyKey: Optional[str] = Field(None, max_length=255)


class WithdrawalOut(BaseModel):
    id: str
    designerProfileId: str
    userId: str
    amount: int
    currency: str
    status: WithdrawalStatus
    payoutReference: Optional[str] = None
    failureReason: Optional[str] = None
    idempotencyKey: Optional[str] = None
    requestedAt: datetime
    processingAt: Optional[datetime] = None
    completedAt: Optional[datetime] = None
    failedAt: Optional[datetime] = None
    createdAt: datetime
    updatedAt: datetime

    model_config = ConfigDict(from_attributes=True)


class WithdrawalListResponse(BaseModel):
    withdrawals: List[WithdrawalOut]
    total: int


class WithdrawalProcessRequest(BaseModel):
    payoutReference: str


class WithdrawalCompleteRequest(BaseModel):
    payoutReference: str


class WithdrawalFailRequest(BaseModel):
    failureReason: str
