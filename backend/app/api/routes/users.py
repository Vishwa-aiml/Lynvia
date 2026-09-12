from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.api.dependencies import get_current_user, require_admin_role
from app.models.user import User, UserRole

router = APIRouter()


@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    """Return the authenticated user's profile."""
    return {"id": current_user.id, "email": current_user.email, "role": current_user.role, "is_active": current_user.is_active}


@router.get("/", dependencies=[Depends(require_admin_role)])
def list_users(db: Session = Depends(get_db)):
    # Admin-only: list users (id and email only)
    users = db.query(User.id, User.email, User.role, User.is_active).all()
    return {"users": [dict(id=u.id, email=u.email, role=u.role, is_active=u.is_active) for u in users]}


@router.get("/{user_id}")
def get_user(user_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # allow admin or the user themselves
    if current_user.role != UserRole.ADMIN and current_user.id != user_id:
        # if not admin and not requesting own profile, forbid
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this user")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return {"id": user.id, "email": user.email, "role": user.role, "is_active": user.is_active}
