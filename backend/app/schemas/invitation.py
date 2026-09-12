from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class InvitationStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


class InvitationCreate(BaseModel):
    designer_id: int
    message: Optional[str] = None


class InvitationOut(BaseModel):
    id: int
    project_id: int
    designer_id: int
    client_id: int
    message: Optional[str] = None
    status: InvitationStatus
    created_at: datetime
    responded_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class InvitationAction(BaseModel):
    # no body needed for accept/reject currently, placeholder
    pass
