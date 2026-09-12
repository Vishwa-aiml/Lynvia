from fastapi import APIRouter, Depends, Query
from typing import List, Optional
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.discovery import search_designers
from app.schemas.service import DesignerDiscoveryOut

router = APIRouter()


@router.get("/designers", response_model=List[DesignerDiscoveryOut])
def discover_designers(
    skills: Optional[str] = Query(None, description="Comma-separated skill names"),
    category: Optional[str] = Query(None),
    min_experience: Optional[int] = Query(None, ge=0),
    max_experience: Optional[int] = Query(None, ge=0),
    location: Optional[str] = Query(None),
    min_rate: Optional[int] = Query(None, ge=0),
    max_rate: Optional[int] = Query(None, ge=0),
    available_day: Optional[int] = Query(None, ge=0, le=6),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    sort: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    skills_list = [s.strip() for s in skills.split(",")] if skills else None
    results = search_designers(
        db,
        skills=skills_list,
        category=category,
        min_experience=min_experience,
        max_experience=max_experience,
        location=location,
        min_rate=min_rate,
        max_rate=max_rate,
        available_day=available_day,
        limit=limit,
        offset=offset,
        sort=sort,
    )
    # results are dicts; DesignerDiscoveryOut expects nested objects; rely on ORM objects for services/skills
    return results
