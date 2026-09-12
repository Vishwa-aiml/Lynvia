from sqlalchemy.orm import Session
from app.models.portfolio import PortfolioItem, PortfolioMedia
from app.schemas.portfolio import PortfolioCreate, PortfolioUpdate, MediaCreate


def create_portfolio_item(db: Session, designer_id: int, item_in: PortfolioCreate) -> PortfolioItem:
    item = PortfolioItem(
        designer_id=designer_id,
        title=item_in.title,
        description=item_in.description,
        category=item_in.category,
        project_reference=item_in.project_reference,
        is_public=item_in.is_public if item_in.is_public is not None else True,
    )
    db.add(item)
    db.commit()
    db.refresh(item)

    # add media if provided
    if item_in.media:
        for idx, m in enumerate(item_in.media):
            media = PortfolioMedia(
                portfolio_id=item.id,
                filename=m.filename,
                url=str(m.url),
                mime_type=m.mime_type,
                sort_order=m.sort_order if m.sort_order is not None else idx,
            )
            db.add(media)
        db.commit()
        db.refresh(item)
    return item


def get_portfolio_item(db: Session, item_id: int) -> PortfolioItem | None:
    return db.query(PortfolioItem).filter(PortfolioItem.id == item_id).first()


def list_designer_portfolio(db: Session, designer_id: int, public_only: bool = True, limit: int = 20, offset: int = 0) -> list[PortfolioItem]:
    q = db.query(PortfolioItem).filter(PortfolioItem.designer_id == designer_id)
    if public_only:
        q = q.filter(PortfolioItem.is_public == True)
    return q.order_by(PortfolioItem.created_at.desc()).limit(limit).offset(offset).all()


def update_portfolio_item(db: Session, item_id: int, item_in: PortfolioUpdate) -> PortfolioItem | None:
    item = get_portfolio_item(db, item_id)
    if not item:
        return None
    update_data = item_in.dict(exclude_unset=True)
    # handle media separately if provided (replace behavior)
    media_list = update_data.pop('media', None)
    for key, value in update_data.items():
        setattr(item, key, value)
    db.add(item)
    db.commit()
    db.refresh(item)
    if media_list is not None:
        # delete existing media and add new set
        db.query(PortfolioMedia).filter(PortfolioMedia.portfolio_id == item.id).delete()
        db.commit()
        for idx, m in enumerate(media_list):
            media = PortfolioMedia(
                portfolio_id=item.id,
                filename=m.filename,
                url=str(m.url),
                mime_type=m.mime_type,
                sort_order=m.sort_order if m.sort_order is not None else idx,
            )
            db.add(media)
        db.commit()
        db.refresh(item)
    return item


def delete_portfolio_item(db: Session, item_id: int) -> bool:
    item = get_portfolio_item(db, item_id)
    if not item:
        return False
    db.delete(item)
    db.commit()
    return True


def add_media(db: Session, item_id: int, media_in: MediaCreate) -> PortfolioMedia:
    media = PortfolioMedia(
        portfolio_id=item_id,
        filename=media_in.filename,
        url=str(media_in.url),
        mime_type=media_in.mime_type,
        sort_order=media_in.sort_order,
    )
    db.add(media)
    db.commit()
    db.refresh(media)
    return media


def remove_media(db: Session, media_id: int) -> bool:
    media = db.query(PortfolioMedia).filter(PortfolioMedia.id == media_id).first()
    if not media:
        return False
    db.delete(media)
    db.commit()
    return True
