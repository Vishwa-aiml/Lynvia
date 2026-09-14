from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum

class DisputeReason(str, Enum):
    NON_DELIVERY = "NON_DELIVERY"
    UNRESPONSIVE = "UNRESPONSIVE"
    QUALITY_ISSUE = "QUALITY_ISSUE"
    SCOPE_CREEP = "SCOPE_CREEP"
    OTHER = "OTHER"

class DisputeStatus(str, Enum):
    OPEN = "OPEN"
    UNDER_REVIEW = "UNDER_REVIEW"
    WAITING_ON_CLIENT = "WAITING_ON_CLIENT"
    WAITING_ON_DESIGNER = "WAITING_ON_DESIGNER"
    RESOLVED = "RESOLVED"
    CLOSED_UNRESOLVED = "CLOSED_UNRESOLVED"

class ResolutionType(str, Enum):
    FULL_REFUND_TO_CLIENT = "FULL_REFUND_TO_CLIENT"
    PARTIAL_REFUND_TO_CLIENT = "PARTIAL_REFUND_TO_CLIENT"
    FUNDS_RELEASED_TO_DESIGNER = "FUNDS_RELEASED_TO_DESIGNER"
    MUTUAL_CANCELLATION = "MUTUAL_CANCELLATION"


class DisputeCreate(BaseModel):
    reason: DisputeReason
    description: str = Field(..., min_length=10, max_length=5000)
    paymentId: Optional[str] = None


class DisputeOut(BaseModel):
    id: str
    projectId: str
    paymentId: Optional[str] = None
    raisedByUserId: str
    againstUserId: str
    reason: DisputeReason
    description: str
    status: DisputeStatus
    resolutionType: Optional[ResolutionType] = None
    resolutionAmount: Optional[int] = None
    resolutionNote: Optional[str] = None
    resolvedByUserId: Optional[str] = None
    resolvedAt: Optional[datetime] = None
    createdAt: datetime
    updatedAt: datetime

    model_config = ConfigDict(from_attributes=True)


class DisputeListResponse(BaseModel):
    disputes: List[DisputeOut]
    total: int


class DisputeStatusUpdate(BaseModel):
    status: DisputeStatus
    note: Optional[str] = Field(None, max_length=1000)


class DisputeResolutionRequest(BaseModel):
    resolutionType: ResolutionType
    resolutionNote: str = Field(..., min_length=10, max_length=5000)
    # Required only for PARTIAL_REFUND_TO_CLIENT - in minor units (paise)
    resolutionAmount: Optional[int] = Field(None, ge=1)


class DisputeResponseCreate(BaseModel):
    message: str = Field(..., min_length=5, max_length=5000)
    # Optional JSON-serialised list of FileMetadata IDs from the project
    attachmentFileIds: Optional[List[str]] = None


class DisputeResponseOut(BaseModel):
    id: str
    disputeId: str
    userId: str
    message: str
    attachmentMeta: Optional[str] = None
    createdAt: datetime

    model_config = ConfigDict(from_attributes=True)


class DisputeResponseListResponse(BaseModel):
    responses: List[DisputeResponseOut]
    total: int
