"""
Dispute Pydantic schemas.
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from app.models.dispute import DisputeReason, DisputeStatus, ResolutionType


class DisputeCreate(BaseModel):
    reason: DisputeReason
    description: str = Field(..., min_length=10, max_length=5000)
    payment_id: Optional[int] = None


class DisputeOut(BaseModel):
    id: int
    project_id: int
    payment_id: Optional[int] = None
    raised_by_user_id: int
    against_user_id: int
    reason: DisputeReason
    description: str
    status: DisputeStatus
    resolution_type: Optional[ResolutionType] = None
    resolution_amount: Optional[int] = None
    resolution_note: Optional[str] = None
    resolved_by_user_id: Optional[int] = None
    resolved_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class DisputeListResponse(BaseModel):
    disputes: List[DisputeOut]
    total: int


class DisputeStatusUpdate(BaseModel):
    status: DisputeStatus
    note: Optional[str] = Field(None, max_length=1000)


class DisputeResolutionRequest(BaseModel):
    resolution_type: ResolutionType
    resolution_note: str = Field(..., min_length=10, max_length=5000)
    # Required only for PARTIAL_REFUND_TO_CLIENT — in minor units (paise)
    resolution_amount: Optional[int] = Field(None, ge=1)


class DisputeResponseCreate(BaseModel):
    message: str = Field(..., min_length=5, max_length=5000)
    # Optional JSON-serialised list of FileMetadata IDs from the project
    attachment_file_ids: Optional[List[int]] = None


class DisputeResponseOut(BaseModel):
    id: int
    dispute_id: int
    user_id: int
    message: str
    attachment_meta: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class DisputeResponseListResponse(BaseModel):
    responses: List[DisputeResponseOut]
    total: int
