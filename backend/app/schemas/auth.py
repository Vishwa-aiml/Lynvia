from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from app.models.user import UserRole


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = None
    role: Optional[UserRole] = UserRole.CLIENT


class UserOut(BaseModel):
    id: str
    email: EmailStr
    full_name: Optional[str] = None
    role: UserRole
    is_active: bool

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: Optional[str] = None


class TokenData(BaseModel):
    sub: Optional[str] = None
    role: Optional[str] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
