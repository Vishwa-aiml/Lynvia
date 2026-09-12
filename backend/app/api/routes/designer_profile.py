from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.profile import DesignerProfileCreate, DesignerProfileUpdate, DesignerProfileOut
from app.services import profile as profile_service
from app.api.dependencies import get_current_user, require_designer_role
from app.models.user import User

router = APIRouter()


@router.post("/designer", response_model=DesignerProfileOut, status_code=status.HTTP_201_CREATED)
def create_designer_profile(
    profile_in: DesignerProfileCreate,
    current_user: User = Depends(require_designer_role),
    db: Session = Depends(get_db),
):
    """Create a designer profile. Only DESIGNER-role users may call this."""
    existing = profile_service.get_designer_profile(db, current_user.id)
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Profile already exists")
    return profile_service.create_designer_profile(db, current_user.id, profile_in)


@router.get("/designer/{user_id}", response_model=DesignerProfileOut)
def get_designer_profile(user_id: int, db: Session = Depends(get_db)):
    profile = profile_service.get_designer_profile(db, user_id)
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")
    return profile


@router.put("/designer/{user_id}", response_model=DesignerProfileOut)
def update_designer_profile(
    user_id: int,
    profile_in: DesignerProfileUpdate,
    current_user: User = Depends(require_designer_role),
    db: Session = Depends(get_db),
):
    """Update a designer profile. Only the owning DESIGNER may update their own profile."""
    if current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to modify this profile")
    profile = profile_service.update_designer_profile(db, user_id, profile_in)
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")
    return profile
