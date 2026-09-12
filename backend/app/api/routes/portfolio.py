from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.schemas.portfolio import PortfolioCreate, PortfolioOut, PortfolioUpdate, MediaOut, MediaCreate
from app.services import portfolio as portfolio_svc
from app.api.dependencies import get_current_user, require_designer_role
from app.services.profile import get_designer_profile
from app.models.user import User

router = APIRouter()


@router.post("/", response_model=PortfolioOut, status_code=status.HTTP_201_CREATED)
def create_portfolio(
    item_in: PortfolioCreate,
    current_user: User = Depends(require_designer_role),
    db: Session = Depends(get_db),
):
    # ensure designer has a profile
    dp = get_designer_profile(db, current_user.id)
    if not dp:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Designer profile not found")
    item = portfolio_svc.create_portfolio_item(db, dp.id, item_in)
    return item


@router.get("/designer/{designer_id}", response_model=List[PortfolioOut])
def list_designer_portfolio(
    designer_id: int,
    public_only: bool = Query(True),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    items = portfolio_svc.list_designer_portfolio(db, designer_id, public_only=public_only, limit=limit, offset=offset)
    return items


@router.get("/{item_id}", response_model=PortfolioOut)
def get_portfolio_item(item_id: int, db: Session = Depends(get_db)):
    item = portfolio_svc.get_portfolio_item(db, item_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio item not found")
    return item


@router.put("/{item_id}", response_model=PortfolioOut)
def update_portfolio_item(
    item_id: int,
    item_in: PortfolioUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    item = portfolio_svc.get_portfolio_item(db, item_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio item not found")
    # verify ownership: current_user's designer_profile.id must match
    dp = get_designer_profile(db, current_user.id)
    from app.models.user import UserRole
    if current_user.role != UserRole.ADMIN:
        if not dp or item.designer_id != dp.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to modify this portfolio item")
    try:
        updated = portfolio_svc.update_portfolio_item(db, item_id, item_in)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return updated


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_portfolio_item(item_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    item = portfolio_svc.get_portfolio_item(db, item_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio item not found")
    dp = get_designer_profile(db, current_user.id)
    from app.models.user import UserRole
    if current_user.role != UserRole.ADMIN:
        if not dp or item.designer_id != dp.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this portfolio item")
    ok = portfolio_svc.delete_portfolio_item(db, item_id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete")
    return None


@router.post("/{item_id}/media", response_model=MediaOut, status_code=status.HTTP_201_CREATED)
def add_media(item_id: int, media_in: MediaCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    item = portfolio_svc.get_portfolio_item(db, item_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio item not found")
    dp = get_designer_profile(db, current_user.id)
    from app.models.user import UserRole
    if current_user.role != UserRole.ADMIN:
        if not dp or item.designer_id != dp.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to add media")
    media = portfolio_svc.add_media(db, item_id, media_in)
    return media


@router.delete("/media/{media_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_media(media_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # load media and verify owner
    from app.models.portfolio import PortfolioMedia
    media = db.query(PortfolioMedia).filter(PortfolioMedia.id == media_id).first()
    if not media:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Media not found")
    item = portfolio_svc.get_portfolio_item(db, media.portfolio_id)
    dp = get_designer_profile(db, current_user.id)
    from app.models.user import UserRole
    if current_user.role != UserRole.ADMIN:
        if not dp or item.designer_id != dp.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to remove media")
    ok = portfolio_svc.remove_media(db, media_id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to remove media")
    return None
