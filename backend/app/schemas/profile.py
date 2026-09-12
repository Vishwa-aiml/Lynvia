from pydantic import BaseModel, Field, HttpUrl, validator
from typing import Optional


class ClientProfileCreate(BaseModel):
    company_name: Optional[str] = Field(None, max_length=255)
    bio: Optional[str] = Field(None, max_length=2000)
    location: Optional[str] = Field(None, max_length=255)
    website: Optional[str] = Field(None, max_length=255)


class ClientProfileUpdate(BaseModel):
    company_name: Optional[str] = Field(None, max_length=255)
    bio: Optional[str] = Field(None, max_length=2000)
    location: Optional[str] = Field(None, max_length=255)
    website: Optional[str] = Field(None, max_length=255)


class ClientProfileOut(BaseModel):
    id: int
    user_id: int
    company_name: Optional[str] = None
    bio: Optional[str] = None
    location: Optional[str] = None
    website: Optional[str] = None

    class Config:
        orm_mode = True


class DesignerProfileCreate(BaseModel):
    headline: Optional[str] = Field(None, max_length=255)
    bio: Optional[str] = Field(None, max_length=2000)
    location: Optional[str] = Field(None, max_length=255)
    website: Optional[str] = Field(None, max_length=255)
    hourly_rate: Optional[int] = Field(None, ge=0, le=999999)
    years_experience: Optional[int] = Field(None, ge=0, le=100)


class DesignerProfileUpdate(BaseModel):
    headline: Optional[str] = Field(None, max_length=255)
    bio: Optional[str] = Field(None, max_length=2000)
    location: Optional[str] = Field(None, max_length=255)
    website: Optional[str] = Field(None, max_length=255)
    hourly_rate: Optional[int] = Field(None, ge=0, le=999999)
    years_experience: Optional[int] = Field(None, ge=0, le=100)


class DesignerProfileOut(BaseModel):
    id: int
    user_id: int
    headline: Optional[str] = None
    bio: Optional[str] = None
    location: Optional[str] = None
    website: Optional[str] = None
    hourly_rate: Optional[int] = None
    years_experience: Optional[int] = None

    class Config:
        orm_mode = True
