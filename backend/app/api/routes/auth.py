from fastapi import APIRouter, Depends, HTTPException, status
from google.cloud.firestore import Client as FirestoreClient
from app.db.firebase import get_db
from app.schemas.auth import UserCreate, Token, LoginRequest, UserOut
from app.services import auth as auth_service
from app.utils.security import create_access_token, hash_password
from app.models.user import UserRole, User
from app.api.dependencies import get_current_user
from pydantic import BaseModel
from typing import Optional
import requests as http_requests
import os

GOOGLE_CLIENT_ID = "488343505027-ga55geta6m947eu1lu43g10nlhsubav4.apps.googleusercontent.com"

router = APIRouter()


class GoogleAuthRequest(BaseModel):
    token: str
    role: Optional[str] = "CLIENT"


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, db: FirestoreClient = Depends(get_db)):
    # Block ADMIN registration via the public API
    if user_in.role == UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot register as ADMIN via this endpoint",
        )

    existing = auth_service.get_user_by_email(db, user_in.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    user = auth_service.create_user(db, user_in)
    return user


@router.post("/login", response_model=Token)
def login(req: LoginRequest, db: FirestoreClient = Depends(get_db)):
    user = auth_service.authenticate_user(db, req.email, req.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    role_value = user.role.value if getattr(user, "role", None) is not None else None
    token = create_access_token(subject=user.id, role=role_value)
    return {"access_token": token, "token_type": "bearer", "role": role_value}


@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/google", response_model=Token)
def google_auth(req: GoogleAuthRequest, db: FirestoreClient = Depends(get_db)):
    """Verify a Google ID token, then sign up or log in the user."""
    try:
        resp = http_requests.get(
            f"https://oauth2.googleapis.com/tokeninfo?id_token={req.token}",
            timeout=10,
        )
        info = resp.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Failed to verify Google token")

    if resp.status_code != 200 or info.get("aud") != GOOGLE_CLIENT_ID:
        raise HTTPException(status_code=401, detail="Invalid Google token")

    email = info.get("email", "").strip().lower()
    if not email:
        raise HTTPException(status_code=400, detail="Google account has no email")

    role_str = (req.role or "CLIENT").upper()
    try:
        role = UserRole[role_str]
    except KeyError:
        role = UserRole.CLIENT

    user = auth_service.get_user_by_email(db, email)
    if not user:
        full_name = info.get("name") or info.get("given_name", "")
        import secrets
        user_in = UserCreate(
            email=email,
            password=secrets.token_urlsafe(32),
            full_name=full_name,
            role=role,
        )
        user = auth_service.create_user(db, user_in)

    role_value = user.role.value if user.role else None
    token = create_access_token(subject=user.id, role=role_value)
    return {"access_token": token, "token_type": "bearer"}


class GoogleUserInfoRequest(BaseModel):
    email: str
    full_name: Optional[str] = ""
    google_sub: Optional[str] = ""
    role: Optional[str] = "CLIENT"


@router.post("/google-userinfo", response_model=Token)
def google_userinfo_auth(req: GoogleUserInfoRequest, db: FirestoreClient = Depends(get_db)):
    """
    Accept verified Google user info (email + name) from the frontend
    after it fetches from Google's /userinfo endpoint using an access token.
    Find or create the user, return a Lynvia JWT.
    """
    email = req.email.strip().lower()
    if not email:
        raise HTTPException(status_code=400, detail="Email is required")

    role_str = (req.role or "CLIENT").upper()
    try:
        role = UserRole[role_str]
    except KeyError:
        role = UserRole.CLIENT

    user = auth_service.get_user_by_email(db, email)
    if not user:
        import secrets
        user_in = UserCreate(
            email=email,
            password=secrets.token_urlsafe(32),
            full_name=req.full_name or "",
            role=role,
        )
        user = auth_service.create_user(db, user_in)

    role_value = user.role.value if user.role else None
    token = create_access_token(subject=user.id, role=role_value)
    # Return role alongside token so frontend doesn't need extra /me call
    return {"access_token": token, "token_type": "bearer", "role": role_value}

