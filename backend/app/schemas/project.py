from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class ProjectStatus(str, Enum):
    draft = "draft"
    open = "open"
    in_progress = "in_progress"
    completed = "completed"
    cancelled = "cancelled"


class ProjectCreate(BaseModel):
    title: str = Field(..., max_length=255)
    description: Optional[str] = Field(None, max_length=4000)
    requirements: Optional[str] = Field(None, max_length=8000)
    budget: Optional[int] = Field(None, ge=0)
    deadline: Optional[datetime] = None


class ProjectUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = Field(None, max_length=4000)
    requirements: Optional[str] = Field(None, max_length=8000)
    budget: Optional[int] = Field(None, ge=0)
    deadline: Optional[datetime] = None
    status: Optional[ProjectStatus] = None


class ProjectOut(BaseModel):
    id: int
    client_id: int
    assigned_designer_id: Optional[int] = None
    title: str
    description: Optional[str] = None
    requirements: Optional[str] = None
    budget: Optional[int] = None
    deadline: Optional[datetime] = None
    status: ProjectStatus

    class Config:
        orm_mode = True
