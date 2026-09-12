from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List
from datetime import datetime


class MediaCreate(BaseModel):
    filename: str = Field(..., max_length=255)
    url: HttpUrl
    mime_type: Optional[str] = None
    sort_order: Optional[int] = None


class MediaOut(BaseModel):
    id: int
    filename: str
    url: HttpUrl
    mime_type: Optional[str] = None
    sort_order: Optional[int] = None
    created_at: datetime

    class Config:
        orm_mode = True


class PortfolioCreate(BaseModel):
    title: str = Field(..., max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    category: Optional[str] = Field(None, max_length=100)
    project_reference: Optional[str] = Field(None, max_length=255)
    is_public: Optional[bool] = True
    media: Optional[List[MediaCreate]] = []


class PortfolioUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    category: Optional[str] = Field(None, max_length=100)
    project_reference: Optional[str] = Field(None, max_length=255)
    is_public: Optional[bool] = None
    media: Optional[List[MediaCreate]] = None


class PortfolioOut(BaseModel):
    id: int
    designer_id: int
    title: str
    description: Optional[str] = None
    category: Optional[str] = None
    project_reference: Optional[str] = None
    is_public: bool
    media: List[MediaOut] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
