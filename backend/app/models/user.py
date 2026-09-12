import enum
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field

class UserRole(str, enum.Enum):
    CLIENT = "CLIENT"
    DESIGNER = "DESIGNER"
    ADMIN = "ADMIN"

class UserBase(BaseModel):
    email: str
    full_name: Optional[str] = None
    role: UserRole = UserRole.CLIENT
    is_active: bool = True

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: str
    hashed_password: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
