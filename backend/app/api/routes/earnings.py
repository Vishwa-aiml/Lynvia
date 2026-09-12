from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.api.dependencies import get_current_user
from app.models.user import User, UserRole
from app.models.payment import DesignerEarning, EarningStatus
from app.models.profile import DesignerProfile
from app.schemas.payment import DesignerEarningOut, EarningSummaryOut
from sqlalchemy import func

router = APIRouter()

@router.get("/designer/earnings", response_model=List[DesignerEarningOut])
def get_designer_earnings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != UserRole.DESIGNER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only designers can view earnings")
        
    profile = db.query(DesignerProfile).filter(DesignerProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Designer profile not found")
        
    earnings = db.query(DesignerEarning).filter(DesignerEarning.designer_id == profile.id).all()
    return earnings

@router.get("/designer/earnings/summary", response_model=EarningSummaryOut)
def get_earnings_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != UserRole.DESIGNER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only designers can view earnings")
        
    profile = db.query(DesignerProfile).filter(DesignerProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Designer profile not found")
        
    pending = db.query(func.sum(DesignerEarning.net_amount)).filter(
        DesignerEarning.designer_id == profile.id,
        DesignerEarning.status == EarningStatus.PENDING
    ).scalar() or 0
    
    available = db.query(func.sum(DesignerEarning.net_amount)).filter(
        DesignerEarning.designer_id == profile.id,
        DesignerEarning.status == EarningStatus.AVAILABLE
    ).scalar() or 0
    
    return EarningSummaryOut(
        total_pending=int(pending),
        total_available=int(available),
        currency="INR"
    )
