from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.profile import ClientProfileCreate, ClientProfileUpdate, ClientProfileOut
from app.services import profile as profile_service
from app.api.dependencies import get_current_user, require_client_role
from app.models.user import User

router = APIRouter()


@router.post("/client", response_model=ClientProfileOut, status_code=status.HTTP_201_CREATED)
def create_client_profile(
    profile_in: ClientProfileCreate,
    current_user: User = Depends(require_client_role),
    db: Session = Depends(get_db),
):
    existing = profile_service.get_client_profile(db, current_user.id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Profile already exists"
        )
    return profile_service.create_client_profile(db, current_user.id, profile_in)


@router.get("/client/{user_id}", response_model=ClientProfileOut)
def get_client_profile(user_id: int, db: Session = Depends(get_db)):
    profile = profile_service.get_client_profile(db, user_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    return profile


@router.put("/client/{user_id}", response_model=ClientProfileOut)
def update_client_profile(
    user_id: int,
    profile_in: ClientProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify this profile"
        )
    profile = profile_service.update_client_profile(db, user_id, profile_in)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    return profile
