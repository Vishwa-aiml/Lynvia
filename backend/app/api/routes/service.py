from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.service import (
    ServiceCreate, ServiceUpdate, ServiceOut,
    SkillCreate, SkillOut,
    SpecializationCreate, SpecializationOut,
    AvailabilityCreate, AvailabilityOut,
)
from app.services import service as service_svc
from app.services import profile as profile_svc
from app.api.dependencies import get_current_user, require_designer_role
from app.models.user import User

router = APIRouter()


@router.post("/", response_model=ServiceOut, status_code=status.HTTP_201_CREATED)
def create_service(
    service_in: ServiceCreate,
    current_user: User = Depends(require_designer_role),
    db: Session = Depends(get_db),
):
    # Ensure the designer has a profile and use its id as designer_id
    designer_profile = profile_svc.get_designer_profile(db, current_user.id)
    if not designer_profile:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Designer profile not found")
    return service_svc.create_service(db, designer_profile.id, service_in)


@router.get("/designers/{designer_id}/services", response_model=list[ServiceOut])
def list_designer_services(designer_id: int, db: Session = Depends(get_db)):
    services = service_svc.get_designer_services(db, designer_id)
    return services


@router.get("/skills", response_model=list[SkillOut])
def list_skills(db: Session = Depends(get_db)):
    return service_svc.get_all_skills(db)


@router.post("/skills", response_model=SkillOut, status_code=status.HTTP_201_CREATED)
def create_skill(skill_in: SkillCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Create a skill and, if the caller is a designer, associate it to their profile."""
    from app.models.user import UserRole

    existing = service_svc.get_skill_by_name(db, skill_in.name)
    if existing:
        # if caller is a designer, ensure association exists
        if current_user and current_user.role == UserRole.DESIGNER:
            designer_profile = profile_svc.get_designer_profile(db, current_user.id)
            if designer_profile:
                service_svc.add_skill_to_designer(db, designer_profile.id, existing.id)
        return existing

    skill = service_svc.create_skill(db, skill_in.name, skill_in.description)
    if current_user and current_user.role == UserRole.DESIGNER:
        designer_profile = profile_svc.get_designer_profile(db, current_user.id)
        if designer_profile:
            service_svc.add_skill_to_designer(db, designer_profile.id, skill.id)
    return skill


@router.post("/specializations", response_model=SpecializationOut, status_code=status.HTTP_201_CREATED)
def create_specialization(
    spec_in: SpecializationCreate,
    current_user: User = Depends(require_designer_role),
    db: Session = Depends(get_db),
):
    designer_profile = profile_svc.get_designer_profile(db, current_user.id)
    if not designer_profile:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Designer profile not found")
    return service_svc.create_specialization(db, designer_profile.id, spec_in)


@router.get("/designers/{designer_id}/specializations", response_model=list[SpecializationOut])
def list_designer_specializations(designer_id: int, db: Session = Depends(get_db)):
    return service_svc.get_designer_specializations(db, designer_id)


@router.post("/availability", response_model=AvailabilityOut, status_code=status.HTTP_201_CREATED)
def create_availability(
    avail_in: AvailabilityCreate,
    current_user: User = Depends(require_designer_role),
    db: Session = Depends(get_db),
):
    designer_profile = profile_svc.get_designer_profile(db, current_user.id)
    if not designer_profile:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Designer profile not found")
    return service_svc.create_availability(db, designer_profile.id, avail_in)


@router.get("/designers/{designer_id}/availability", response_model=list[AvailabilityOut])
def list_designer_availability(designer_id: int, db: Session = Depends(get_db)):
    return service_svc.get_designer_availability(db, designer_id)


@router.put("/{service_id}", response_model=ServiceOut)
def update_service(
    service_id: int,
    service_in: ServiceUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Allow the service owner (designer) or ADMIN to update a service."""
    service = service_svc.get_service(db, service_id)
    if not service:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service not found")

    # resolve current user's designer_profile id
    from app.services.profile import get_designer_profile as _get_designer_profile
    designer_profile = _get_designer_profile(db, current_user.id)

    # allow ADMIN or owner
    from app.models.user import UserRole
    if current_user.role != UserRole.ADMIN:
        if not designer_profile or service.designer_id != designer_profile.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to modify this service")

    try:
        updated = service_svc.update_service(db, service_id, service_in)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    return updated
