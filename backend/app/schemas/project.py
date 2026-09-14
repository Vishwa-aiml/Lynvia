from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class ProjectStatus(str, Enum):
    DRAFT = "DRAFT"
    OPEN_FOR_PROPOSALS = "OPEN_FOR_PROPOSALS"
    PROPOSAL_REVIEW = "PROPOSAL_REVIEW"
    DESIGNER_SELECTED = "DESIGNER_SELECTED"
    AWAITING_PAYMENT = "AWAITING_PAYMENT"
    ACTIVE = "ACTIVE"
    IN_REVIEW = "IN_REVIEW"
    DELIVERED = "DELIVERED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    DISPUTED = "DISPUTED"


class ProjectPhase(str, Enum):
    DISCOVERY = "DISCOVERY"
    CONCEPT = "CONCEPT"
    REFINEMENT = "REFINEMENT"
    PRODUCTION = "PRODUCTION"
    DELIVERY = "DELIVERY"


class ProposalStatus(str, Enum):
    SUBMITTED = "SUBMITTED"
    WITHDRAWN = "WITHDRAWN"
    SHORTLISTED = "SHORTLISTED"
    SELECTED = "SELECTED"
    NOT_SELECTED = "NOT_SELECTED"
    REJECTED = "REJECTED"


class ProjectCreate(BaseModel):
    title: str = Field(..., max_length=255)
    category: str = Field(..., max_length=100)
    description: Optional[str] = Field(None, max_length=4000)
    requirements: Optional[str] = Field(None, max_length=8000)
    deliverables: Optional[List[str]] = None
    referenceFiles: Optional[List[str]] = None
    budget: Optional[int] = Field(None, ge=0)
    deadline: Optional[datetime] = None


class ProjectUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=255)
    category: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = Field(None, max_length=4000)
    requirements: Optional[str] = Field(None, max_length=8000)
    deliverables: Optional[List[str]] = None
    referenceFiles: Optional[List[str]] = None
    budget: Optional[int] = Field(None, ge=0)
    deadline: Optional[datetime] = None
    status: Optional[ProjectStatus] = None
    currentPhase: Optional[ProjectPhase] = None


class ProjectOut(BaseModel):
    id: str  # Firestore uses string UUIDs
    clientId: str
    designerId: Optional[str] = None
    selectedProposalId: Optional[str] = None
    title: str
    category: str
    description: Optional[str] = None
    requirements: Optional[str] = None
    deliverables: Optional[List[str]] = None
    referenceFiles: Optional[List[str]] = None
    budget: Optional[int] = None
    deadline: Optional[datetime] = None
    status: ProjectStatus
    currentPhase: Optional[ProjectPhase] = None
    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True


class ProposalCreate(BaseModel):
    proposedPrice: int = Field(..., ge=0)  # in paise
    deliveryDays: int = Field(..., ge=1)
    conceptCount: int = Field(..., ge=0)
    revisionCount: int = Field(..., ge=0)
    approach: str = Field(..., max_length=4000)


class ProposalOut(BaseModel):
    id: str
    projectId: str
    designerId: str
    proposedPrice: int
    deliveryDays: int
    conceptCount: int
    revisionCount: int
    approach: str
    status: ProposalStatus
    submittedAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True


class ProposalDesignerOut(BaseModel):
    """Sanitized view for competing designers (price hidden)."""
    id: str
    projectId: str
    designerId: str
    # proposedPrice is deliberately omitted
    deliveryDays: int
    conceptCount: int
    revisionCount: int
    approach: str
    status: ProposalStatus
    submittedAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True

