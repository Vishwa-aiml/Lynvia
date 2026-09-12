from sqlalchemy.orm import Session
from app.models.service import Service, Skill, Specialization, Availability, designer_skills
from app.schemas.service import (
    ServiceCreate, ServiceUpdate, SpecializationCreate, AvailabilityCreate
)


# Service CRUD
def get_service(db: Session, service_id: int) -> Service | None:
    return db.query(Service).filter(Service.id == service_id).first()


def get_designer_services(db: Session, designer_id: int) -> list[Service]:
    return db.query(Service).filter(Service.designer_id == designer_id, Service.is_active == True).all()


def create_service(db: Session, designer_id: int, service_in: ServiceCreate) -> Service:
    # validate price and delivery_days
    try:
        price = int(service_in.price)
    except Exception:
        raise ValueError("Invalid price; must be integer minor-units")
    if price < 0:
        raise ValueError("Price must be non-negative")

    delivery_days = service_in.delivery_days
    if delivery_days is not None:
        try:
            delivery_days = int(delivery_days)
        except Exception:
            raise ValueError("Invalid delivery_days; must be integer number of days")
        if delivery_days < 1:
            raise ValueError("delivery_days must be at least 1")

    service = Service(
        designer_id=designer_id,
        title=service_in.title,
        description=service_in.description,
        category=service_in.category,
        price=price,
        delivery_days=delivery_days,
    )
    db.add(service)
    db.commit()
    db.refresh(service)
    return service


def update_service(db: Session, service_id: int, service_in: ServiceUpdate) -> Service | None:
    service = get_service(db, service_id)
    if not service:
        return None
    
    update_data = service_in.dict(exclude_unset=True)

    # validate price and delivery_days if present
    if 'price' in update_data and update_data['price'] is not None:
        try:
            p = int(update_data['price'])
        except Exception:
            raise ValueError("Invalid price; must be integer minor-units")
        if p < 0:
            raise ValueError("Price must be non-negative")
        update_data['price'] = p

    if 'delivery_days' in update_data and update_data['delivery_days'] is not None:
        try:
            d = int(update_data['delivery_days'])
        except Exception:
            raise ValueError("Invalid delivery_days; must be integer number of days")
        if d < 1:
            raise ValueError("delivery_days must be at least 1")
        update_data['delivery_days'] = d

    for key, value in update_data.items():
        setattr(service, key, value)
    
    db.add(service)
    db.commit()
    db.refresh(service)
    return service


# Skill CRUD
def get_skill(db: Session, skill_id: int) -> Skill | None:
    return db.query(Skill).filter(Skill.id == skill_id).first()


def get_skill_by_name(db: Session, name: str) -> Skill | None:
    return db.query(Skill).filter(Skill.name == name).first()


def get_all_skills(db: Session) -> list[Skill]:
    return db.query(Skill).all()


def create_skill(db: Session, name: str, description: str | None = None) -> Skill:
    skill = Skill(name=name, description=description)
    db.add(skill)
    db.commit()
    db.refresh(skill)
    return skill


def add_skill_to_designer(db: Session, designer_id: int, skill_id: int) -> None:
    # Check if association already exists to avoid duplicate primary key error
    existing = db.execute(
        designer_skills.select().where(
            designer_skills.c.designer_id == designer_id,
            designer_skills.c.skill_id == skill_id,
        )
    ).first()
    if existing:
        return
    stmt = designer_skills.insert().values(designer_id=designer_id, skill_id=skill_id)
    db.execute(stmt)
    db.commit()


def get_designer_skills(db: Session, designer_id: int) -> list[Skill]:
    return db.query(Skill).join(designer_skills).filter(
        designer_skills.c.designer_id == designer_id
    ).all()


# Specialization CRUD
def get_specialization(db: Session, spec_id: int) -> Specialization | None:
    return db.query(Specialization).filter(Specialization.id == spec_id).first()


def get_designer_specializations(db: Session, designer_id: int) -> list[Specialization]:
    return db.query(Specialization).filter(Specialization.designer_id == designer_id).all()


def create_specialization(db: Session, designer_id: int, spec_in: SpecializationCreate) -> Specialization:
    spec = Specialization(
        designer_id=designer_id,
        name=spec_in.name,
        description=spec_in.description,
    )
    db.add(spec)
    db.commit()
    db.refresh(spec)
    return spec


# Availability CRUD
def get_availability(db: Session, avail_id: int) -> Availability | None:
    return db.query(Availability).filter(Availability.id == avail_id).first()


def get_designer_availability(db: Session, designer_id: int) -> list[Availability]:
    return db.query(Availability).filter(Availability.designer_id == designer_id).all()


def create_availability(db: Session, designer_id: int, avail_in: AvailabilityCreate) -> Availability:
    avail = Availability(
        designer_id=designer_id,
        day_of_week=avail_in.day_of_week,
        is_available=avail_in.is_available,
        hours_per_day=avail_in.hours_per_day,
    )
    db.add(avail)
    db.commit()
    db.refresh(avail)
    return avail


def update_availability(db: Session, avail_id: int, is_available: bool, hours_per_day: int | None = None) -> Availability | None:
    avail = get_availability(db, avail_id)
    if not avail:
        return None
    
    avail.is_available = is_available
    if hours_per_day is not None:
        avail.hours_per_day = hours_per_day
    
    db.add(avail)
    db.commit()
    db.refresh(avail)
    return avail
