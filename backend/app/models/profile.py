from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field


class ClientProfileBase(BaseModel):
    user_id: str
    company_name: Optional[str] = None
    bio: Optional[str] = None
    location: Optional[str] = None
    website: Optional[str] = None

class ClientProfile(ClientProfileBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DesignerProfileBase(BaseModel):
    user_id: str
    headline: Optional[str] = None
    bio: Optional[str] = None
    location: Optional[str] = None
    website: Optional[str] = None
    hourly_rate: Optional[int] = None
    years_experience: Optional[int] = None

class DesignerProfile(DesignerProfileBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

