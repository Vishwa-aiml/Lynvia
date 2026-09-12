from sqlalchemy.orm import Session
from app.models.profile import ClientProfile, DesignerProfile
from app.schemas.profile import ClientProfileCreate, ClientProfileUpdate, DesignerProfileCreate, DesignerProfileUpdate


def get_client_profile(db: Session, user_id: int) -> ClientProfile | None:
    return db.query(ClientProfile).filter(ClientProfile.user_id == user_id).first()


def create_client_profile(db: Session, user_id: int, profile_in: ClientProfileCreate) -> ClientProfile:
    profile = ClientProfile(
        user_id=user_id,
        company_name=profile_in.company_name,
        bio=profile_in.bio,
        location=profile_in.location,
        website=profile_in.website,
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


def update_client_profile(db: Session, user_id: int, profile_in: ClientProfileUpdate) -> ClientProfile | None:
    profile = get_client_profile(db, user_id)
    if not profile:
        return None
    
    update_data = profile_in.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(profile, key, value)
    
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


def get_designer_profile(db: Session, user_id: int) -> DesignerProfile | None:
    return db.query(DesignerProfile).filter(DesignerProfile.user_id == user_id).first()


def create_designer_profile(db: Session, user_id: int, profile_in: DesignerProfileCreate) -> DesignerProfile:
    profile = DesignerProfile(
        user_id=user_id,
        headline=profile_in.headline,
        bio=profile_in.bio,
        location=profile_in.location,
        website=profile_in.website,
        hourly_rate=profile_in.hourly_rate,
        years_experience=profile_in.years_experience,
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


def update_designer_profile(db: Session, user_id: int, profile_in: DesignerProfileUpdate) -> DesignerProfile | None:
    profile = get_designer_profile(db, user_id)
    if not profile:
        return None
    
    update_data = profile_in.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(profile, key, value)
    
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile
