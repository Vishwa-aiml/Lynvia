from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import datetime
from enum import Enum

# --- ENUMS ---

class MilestoneStatus(str, Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"

class TaskStatus(str, Enum):
    TODO = "TODO"
    IN_PROGRESS = "IN_PROGRESS"
    IN_REVIEW = "IN_REVIEW"
    DONE = "DONE"

class TaskPriority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    URGENT = "URGENT"

class ProjectEventType(str, Enum):
    MILESTONE_CREATED = "MILESTONE_CREATED"
    MILESTONE_UPDATED = "MILESTONE_UPDATED"
    MILESTONE_COMPLETED = "MILESTONE_COMPLETED"
    TASK_CREATED = "TASK_CREATED"
    TASK_UPDATED = "TASK_UPDATED"
    TASK_COMPLETED = "TASK_COMPLETED"
    FILE_UPLOADED = "FILE_UPLOADED"
    DELIVERY_SUBMITTED = "DELIVERY_SUBMITTED"
    REVISION_REQUESTED = "REVISION_REQUESTED"
    DELIVERY_ACCEPTED = "DELIVERY_ACCEPTED"
    GENERAL = "GENERAL"

class DeliveryStatus(str, Enum):
    SUBMITTED = "SUBMITTED"
    IN_REVISION = "IN_REVISION"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"

class RevisionStatus(str, Enum):
    REQUESTED = "REQUESTED"
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"

# --- MILESTONE SCHEMAS ---

class MilestoneBase(BaseModel):
    title: str = Field(..., max_length=255)
    description: Optional[str] = None
    order: Optional[int] = 0
    status: Optional[MilestoneStatus] = MilestoneStatus.PENDING
    dueDate: Optional[datetime] = None

class MilestoneCreate(MilestoneBase):
    pass

class MilestoneUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    order: Optional[int] = None
    status: Optional[MilestoneStatus] = None
    dueDate: Optional[datetime] = None

class MilestoneOut(MilestoneBase):
    id: str
    projectId: str
    createdAt: datetime
    updatedAt: datetime
    model_config = ConfigDict(from_attributes=True)

# --- TASK SCHEMAS ---

class TaskBase(BaseModel):
    title: str = Field(..., max_length=255)
    description: Optional[str] = None
    status: Optional[TaskStatus] = TaskStatus.TODO
    priority: Optional[TaskPriority] = TaskPriority.MEDIUM
    assignedUserId: Optional[str] = None
    dueDate: Optional[datetime] = None

class TaskCreate(TaskBase):
    milestoneId: str

class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    assignedUserId: Optional[str] = None
    dueDate: Optional[datetime] = None

class TaskOut(TaskBase):
    id: str
    milestoneId: str
    createdAt: datetime
    updatedAt: datetime
    model_config = ConfigDict(from_attributes=True)

# --- FILE SCHEMAS ---

class FileMetadataBase(BaseModel):
    filename: str = Field(..., max_length=255)
    storageKey: Optional[str] = Field(None, max_length=1024)
    fileUrl: str = Field(..., max_length=2048)
    mimeType: Optional[str] = Field(None, max_length=128)
    fileSize: Optional[int] = None

class FileMetadataCreate(FileMetadataBase):
    pass

class FileMetadataOut(FileMetadataBase):
    id: str
    projectId: str
    uploaderId: Optional[str] = None
    createdAt: datetime
    model_config = ConfigDict(from_attributes=True)

# --- EVENT SCHEMAS ---

class ProjectEventBase(BaseModel):
    eventType: ProjectEventType
    content: Optional[str] = None

class ProjectEventCreate(ProjectEventBase):
    pass

class ProjectEventOut(ProjectEventBase):
    id: str
    projectId: str
    authorId: Optional[str] = None
    createdAt: datetime
    model_config = ConfigDict(from_attributes=True)

# --- DELIVERY & REVISION SCHEMAS ---

class RevisionBase(BaseModel):
    requestReason: str = Field(..., max_length=255)
    clientComment: str

class RevisionCreate(RevisionBase):
    pass

class RevisionOut(RevisionBase):
    id: str
    deliveryId: str
    revisionNumber: int
    designerResponse: Optional[str] = None
    status: RevisionStatus
    createdAt: datetime
    updatedAt: datetime
    model_config = ConfigDict(from_attributes=True)

class DeliveryBase(BaseModel):
    message: Optional[str] = None

class DeliveryCreate(DeliveryBase):
    fileIds: List[str] = []

class DeliveryOut(DeliveryBase):
    id: str
    projectId: str
    designerId: str
    version: int
    status: DeliveryStatus
    submittedAt: datetime
    files: List[FileMetadataOut] = []
    revisions: List[RevisionOut] = []
    model_config = ConfigDict(from_attributes=True)

# --- WORKSPACE AGGREGATE SCHEMA ---

class ProjectWorkspaceOut(BaseModel):
    projectId: str
    milestones: List[MilestoneOut] = []
    tasks: List[TaskOut] = []
    files: List[FileMetadataOut] = []
    events: List[ProjectEventOut] = []
    deliveries: List[DeliveryOut] = []
    model_config = ConfigDict(from_attributes=True)
