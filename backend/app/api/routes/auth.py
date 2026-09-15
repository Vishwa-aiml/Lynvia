from fastapi import APIRouter, Depends, HTTPException, status
from google.cloud.firestore import Client as FirestoreClient
from app.db.firebase import get_db
from app.schemas.auth import UserCreate, UserOut
from app.services import auth as auth_service
from app.models.user import UserRole, User
from app.api.dependencies import get_current_user, get_firebase_user
import firebase_admin.auth as fb_auth

router = APIRouter()

@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(
    user_in: UserCreate, 
    payload: dict = Depends(get_firebase_user),
    db: FirestoreClient = Depends(get_db)
):
    """Register the user in Firestore using their Firebase Auth UID."""
    
    # Block ADMIN registration via the public API
    if user_in.role == UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot register as ADMIN via this endpoint",
        )

    uid = payload.get("uid")
    if not uid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

    # Check if they already exist in the target collection
    existing = auth_service.get_user_by_uid(db, uid, user_in.role)
    if existing:
        return existing

    # Create the user in the database
    user = auth_service.create_user(db, uid, user_in)
    
    # Set the custom claim in Firebase Auth so the next token refresh has the role
    fb_auth.set_custom_user_claims(uid, {"role": user_in.role.value})
    
    return user


@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    """Returns the profile of the current user based on their token and database."""
    return current_user
