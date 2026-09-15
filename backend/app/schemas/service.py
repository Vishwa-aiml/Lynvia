from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class SkillCreate(BaseModel):
    name: str = Field(..., max_length=100)
    description: Optional[str] = Field(None, max_length=1000)


class SkillOut(BaseModel):
    id: str
    name: str
    description: Optional[str] = None

    class Config:
        from_attributes = True


class ServiceCreate(BaseModel):
    title: str = Field(..., max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    category: str = Field(..., max_length=100)
    price: int = Field(..., ge=0, le=99999999)
    delivery_days: Optional[int] = Field(None, ge=1, le=365)


class ServiceUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    category: Optional[str] = Field(None, max_length=100)
    price: Optional[int] = Field(None, ge=0, le=99999999)
    delivery_days: Optional[int] = Field(None, ge=1, le=365)
    is_active: Optional[bool] = None


class ServiceOut(BaseModel):
    id: str
    designer_id: str
    title: str
    description: Optional[str] = None
    category: str
    price: int
    delivery_days: Optional[int] = None
    is_active: bool

    class Config:
        from_attributes = True


class SpecializationCreate(BaseModel):
    name: str = Field(..., max_length=255)
    description: Optional[str] = Field(None, max_length=2000)


class SpecializationOut(BaseModel):
    id: str
    designer_id: str
    name: str
    description: Optional[str] = None

    class Config:
        from_attributes = True


class AvailabilityCreate(BaseModel):
    day_of_week: int = Field(..., ge=0, le=6)
    is_available: bool = True
    hours_per_day: Optional[int] = Field(None, ge=1, le=24)


class AvailabilityOut(BaseModel):
    id: str
    designer_id: str
    day_of_week: int
    is_available: bool
    hours_per_day: Optional[int] = None

    class Config:
        from_attributes = True


class DesignerDiscoveryOut(BaseModel):
    """Designer profile with skills and services for discovery."""
    id: str
    user_id: str
    headline: Optional[str] = None
    bio: Optional[str] = None
    location: Optional[str] = None
    hourly_rate: Optional[int] = None
    years_experience: Optional[int] = None
    services: List[ServiceOut] = []
    skills: List[SkillOut] = []
    specializations: List[SpecializationOut] = []
    portfolio_count: int = 0

    class Config:
        from_attributes = True
