from pydantic import BaseModel, HttpUrl, Field
from typing import List, Optional
from datetime import datetime

from app.models.milestone import MilestoneStatus
from app.models.task import TaskStatus, TaskPriority
from app.models.workspace import ProjectEventType
from app.models.delivery import DeliveryStatus, RevisionStatus
from app.schemas.auth import UserOut


# --- MILESTONE SCHEMAS ---

class MilestoneBase(BaseModel):
    title: str = Field(..., max_length=255)
    description: Optional[str] = None
    order: Optional[int] = 0
    status: Optional[MilestoneStatus] = MilestoneStatus.PENDING
    due_date: Optional[datetime] = None


class MilestoneCreate(MilestoneBase):
    pass


class MilestoneUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    order: Optional[int] = None
    status: Optional[MilestoneStatus] = None
    due_date: Optional[datetime] = None


class MilestoneOut(MilestoneBase):
    id: int
    project_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


# --- TASK SCHEMAS ---

class TaskBase(BaseModel):
    title: str = Field(..., max_length=255)
    description: Optional[str] = None
    status: Optional[TaskStatus] = TaskStatus.TODO
    priority: Optional[TaskPriority] = TaskPriority.MEDIUM
    assigned_user_id: Optional[int] = None
    due_date: Optional[datetime] = None


class TaskCreate(TaskBase):
    milestone_id: int


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    assigned_user_id: Optional[int] = None
    due_date: Optional[datetime] = None


class TaskOut(TaskBase):
    id: int
    milestone_id: int
    created_at: datetime
    updated_at: datetime
    assigned_user: Optional[UserOut] = None

    class Config:
        orm_mode = True


# --- FILE SCHEMAS ---

class FileMetadataBase(BaseModel):
    filename: str = Field(..., max_length=255)
    storage_key: Optional[str] = Field(None, max_length=1024)
    file_url: str = Field(..., max_length=2048)
    mime_type: Optional[str] = Field(None, max_length=128)
    file_size: Optional[int] = None


class FileMetadataCreate(FileMetadataBase):
    pass


class FileMetadataOut(FileMetadataBase):
    id: int
    project_id: int
    uploader_id: Optional[int] = None
    created_at: datetime
    uploader: Optional[UserOut] = None

    class Config:
        orm_mode = True


# --- EVENT SCHEMAS ---

class ProjectEventBase(BaseModel):
    event_type: ProjectEventType
    content: Optional[str] = None


class ProjectEventCreate(ProjectEventBase):
    pass


class ProjectEventOut(ProjectEventBase):
    id: int
    project_id: int
    author_id: Optional[int] = None
    created_at: datetime
    author: Optional[UserOut] = None

    class Config:
        orm_mode = True


# --- DELIVERY & REVISION SCHEMAS ---

class RevisionBase(BaseModel):
    request_reason: str = Field(..., max_length=255)
    client_comment: str


class RevisionCreate(RevisionBase):
    pass


class RevisionOut(RevisionBase):
    id: int
    delivery_id: int
    revision_number: int
    designer_response: Optional[str] = None
    status: RevisionStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class DeliveryBase(BaseModel):
    message: Optional[str] = None


class DeliveryCreate(DeliveryBase):
    file_ids: List[int] = []


class DeliveryOut(DeliveryBase):
    id: int
    project_id: int
    designer_id: int
    version: int
    status: DeliveryStatus
    submitted_at: datetime
    files: List[FileMetadataOut] = []
    revisions: List[RevisionOut] = []

    class Config:
        orm_mode = True


# --- WORKSPACE AGGREGATE SCHEMA ---

class ProjectWorkspaceOut(BaseModel):
    project_id: int
    milestones: List[MilestoneOut] = []
    tasks: List[TaskOut] = []
    files: List[FileMetadataOut] = []
    events: List[ProjectEventOut] = []
    deliveries: List[DeliveryOut] = []

    class Config:
        orm_mode = True
