from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from app.models.profile import DesignerProfile
from app.models.service import Service, Skill, Specialization, designer_skills
from app.models.user import User, UserRole
from app.models.portfolio import PortfolioItem
from app.services.service import get_designer_skills


def search_designers(
    db: Session,
    skills: Optional[List[str]] = None,
    category: Optional[str] = None,
    min_experience: Optional[int] = None,
    max_experience: Optional[int] = None,
    location: Optional[str] = None,
    min_rate: Optional[int] = None,
    max_rate: Optional[int] = None,
    available_day: Optional[int] = None,
    limit: int = 20,
    offset: int = 0,
    sort: Optional[str] = None,  # e.g., 'rate_asc', 'rate_desc', 'experience_desc'
):
    # Base query: designer profiles joined to active users with DESIGNER role
    q = db.query(DesignerProfile).join(User, DesignerProfile.user_id == User.id).filter(
        User.role == UserRole.DESIGNER,
        User.is_active == True,
    )

    if min_experience is not None:
        q = q.filter(DesignerProfile.years_experience >= min_experience)
    if max_experience is not None:
        q = q.filter(DesignerProfile.years_experience <= max_experience)
    if location:
        q = q.filter(func.lower(DesignerProfile.location).like(f"%{location.lower()}%"))
    if min_rate is not None:
        q = q.filter(DesignerProfile.hourly_rate >= min_rate)
    if max_rate is not None:
        q = q.filter(DesignerProfile.hourly_rate <= max_rate)

    # skill filter via association table
    if skills:
        skill_names = [s.strip().lower() for s in skills if s.strip()]
        skill_ids = [r[0] for r in db.query(Skill.id).filter(func.lower(Skill.name).in_(skill_names)).all()]
        if skill_ids:
            ds_subq = db.query(designer_skills.c.designer_id).filter(
                designer_skills.c.skill_id.in_(skill_ids)
            ).distinct().subquery()
            q = q.filter(DesignerProfile.id.in_(ds_subq))
        else:
            # no matching skills -> return empty
            return []

    if category:
        q = q.join(Service, DesignerProfile.id == Service.designer_id)
        q = q.filter(Service.category == category, Service.is_active == True)

    if available_day is not None:
        from app.models.service import Availability as Av
        q = q.join(Av, DesignerProfile.id == Av.designer_id)
        q = q.filter(Av.day_of_week == available_day, Av.is_available == True)

    # sorting
    if sort == 'rate_asc':
        q = q.order_by(DesignerProfile.hourly_rate.asc().nulls_last())
    elif sort == 'rate_desc':
        q = q.order_by(DesignerProfile.hourly_rate.desc().nulls_last())
    elif sort == 'experience_desc':
        q = q.order_by(DesignerProfile.years_experience.desc().nulls_last())
    else:
        q = q.order_by(DesignerProfile.created_at.desc())

    q = q.distinct().limit(limit).offset(offset)

    results = []
    profiles = q.all()
    for p in profiles:
        services = db.query(Service).filter(Service.designer_id == p.id, Service.is_active == True).all()
        designer_skills_list = get_designer_skills(db, p.id)
        specializations = db.query(Specialization).filter(Specialization.designer_id == p.id).all()
        portfolio_count = db.query(PortfolioItem).filter(
            PortfolioItem.designer_id == p.id,
            PortfolioItem.is_public == True,
        ).count()
        results.append({
            'id': p.id,
            'user_id': p.user_id,
            'headline': p.headline,
            'bio': p.bio,
            'location': p.location,
            'hourly_rate': p.hourly_rate,
            'years_experience': p.years_experience,
            'services': services,
            'skills': designer_skills_list,
            'specializations': specializations,
            'portfolio_count': portfolio_count,
        })

    return results
