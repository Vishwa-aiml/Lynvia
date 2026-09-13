from google.cloud.firestore import Client as FirestoreClient
from app.schemas.service import (
    ServiceCreate, ServiceUpdate, SpecializationCreate, AvailabilityCreate
)
from google.cloud.firestore_v1.base_query import FieldFilter
import uuid

# Service CRUD
def get_service(db: FirestoreClient, service_id: str):
    doc = db.collection("services").document(service_id).get()
    if doc.exists:
        data = doc.to_dict()
        data["id"] = doc.id
        return data
    return None

def get_designer_services(db: FirestoreClient, designer_id: str):
    docs = db.collection("services").where(filter=FieldFilter("designer_id", "==", designer_id)).where(filter=FieldFilter("is_active", "==", True)).stream()
    results = []
    for doc in docs:
        data = doc.to_dict()
        data["id"] = doc.id
        results.append(data)
    return results

def create_service(db: FirestoreClient, designer_id: str, service_in: ServiceCreate):
    price = int(service_in.price)
    if price < 0:
        raise ValueError("Price must be non-negative")

    delivery_days = service_in.delivery_days
    if delivery_days is not None:
        delivery_days = int(delivery_days)
        if delivery_days < 1:
            raise ValueError("delivery_days must be at least 1")

    service_data = {
        "designer_id": designer_id,
        "title": service_in.title,
        "description": service_in.description,
        "category": service_in.category,
        "price": price,
        "delivery_days": delivery_days,
        "is_active": True
    }
    
    doc_ref = db.collection("services").document()
    db.collection("services").document(doc_ref.id).set(service_data)
    service_data["id"] = doc_ref.id
    
    # Also update designer profile to embed services
    update_designer_embedded_data(db, designer_id)
    return service_data

def update_service(db: FirestoreClient, service_id: str, service_in: ServiceUpdate):
    service = get_service(db, service_id)
    if not service:
        return None
    
    update_data = service_in.dict(exclude_unset=True)
    if update_data:
        db.collection("services").document(service_id).update(update_data)
        service.update(update_data)
        update_designer_embedded_data(db, service["designer_id"])
    return service


# Skill CRUD
def get_skill(db: FirestoreClient, skill_id: str):
    doc = db.collection("skills").document(skill_id).get()
    if doc.exists:
        data = doc.to_dict()
        data["id"] = doc.id
        return data
    return None

def get_skill_by_name(db: FirestoreClient, name: str):
    docs = db.collection("skills").where(filter=FieldFilter("name", "==", name)).limit(1).stream()
    for doc in docs:
        data = doc.to_dict()
        data["id"] = doc.id
        return data
    return None

def get_all_skills(db: FirestoreClient):
    docs = db.collection("skills").stream()
    results = []
    for doc in docs:
        data = doc.to_dict()
        data["id"] = doc.id
        results.append(data)
    return results

def create_skill(db: FirestoreClient, name: str, description: str | None = None):
    existing = get_skill_by_name(db, name)
    if existing:
        return existing
        
    skill_data = {"name": name, "description": description}
    doc_ref = db.collection("skills").document()
    db.collection("skills").document(doc_ref.id).set(skill_data)
    skill_data["id"] = doc_ref.id
    return skill_data

def add_skill_to_designer(db: FirestoreClient, designer_id: str, skill_id: str) -> None:
    skill = get_skill(db, skill_id)
    if not skill:
        return
        
    doc_ref = db.collection("designer_skills").document(f"{designer_id}_{skill_id}")
    doc_ref.set({"designer_id": designer_id, "skill_id": skill_id})
    update_designer_embedded_data(db, designer_id)

def get_designer_skills(db: FirestoreClient, designer_id: str):
    docs = db.collection("designer_skills").where(filter=FieldFilter("designer_id", "==", designer_id)).stream()
    skill_ids = [doc.to_dict()["skill_id"] for doc in docs]
    
    skills = []
    for skill_id in skill_ids:
        skill = get_skill(db, skill_id)
        if skill:
            skills.append(skill)
    return skills


# Specialization CRUD
def get_specialization(db: FirestoreClient, spec_id: str):
    doc = db.collection("specializations").document(spec_id).get()
    if doc.exists:
        data = doc.to_dict()
        data["id"] = doc.id
        return data
    return None

def get_designer_specializations(db: FirestoreClient, designer_id: str):
    docs = db.collection("specializations").where(filter=FieldFilter("designer_id", "==", designer_id)).stream()
    results = []
    for doc in docs:
        data = doc.to_dict()
        data["id"] = doc.id
        results.append(data)
    return results

def create_specialization(db: FirestoreClient, designer_id: str, spec_in: SpecializationCreate):
    spec_data = {
        "designer_id": designer_id,
        "name": spec_in.name,
        "description": spec_in.description
    }
    doc_ref = db.collection("specializations").document()
    db.collection("specializations").document(doc_ref.id).set(spec_data)
    spec_data["id"] = doc_ref.id
    update_designer_embedded_data(db, designer_id)
    return spec_data


# Availability CRUD
def get_availability(db: FirestoreClient, avail_id: str):
    doc = db.collection("availabilities").document(avail_id).get()
    if doc.exists:
        data = doc.to_dict()
        data["id"] = doc.id
        return data
    return None

def get_designer_availability(db: FirestoreClient, designer_id: str):
    docs = db.collection("availabilities").where(filter=FieldFilter("designer_id", "==", designer_id)).stream()
    results = []
    for doc in docs:
        data = doc.to_dict()
        data["id"] = doc.id
        results.append(data)
    return results

def create_availability(db: FirestoreClient, designer_id: str, avail_in: AvailabilityCreate):
    avail_data = {
        "designer_id": designer_id,
        "day_of_week": avail_in.day_of_week,
        "is_available": avail_in.is_available,
        "hours_per_day": avail_in.hours_per_day
    }
    doc_ref = db.collection("availabilities").document()
    db.collection("availabilities").document(doc_ref.id).set(avail_data)
    avail_data["id"] = doc_ref.id
    update_designer_embedded_data(db, designer_id)
    return avail_data

def update_availability(db: FirestoreClient, avail_id: str, is_available: bool, hours_per_day: int | None = None):
    avail = get_availability(db, avail_id)
    if not avail:
        return None
    
    update_data = {"is_available": is_available}
    if hours_per_day is not None:
        update_data["hours_per_day"] = hours_per_day
        
    db.collection("availabilities").document(avail_id).update(update_data)
    avail.update(update_data)
    update_designer_embedded_data(db, avail["designer_id"])
    return avail


def update_designer_embedded_data(db: FirestoreClient, designer_id: str):
    """Sync services, skills, specializations directly into the designer_profile document for easier discovery querying"""
    services = get_designer_services(db, designer_id)
    skills = [s['name'] for s in get_designer_skills(db, designer_id)]
    specializations = [s['name'] for s in get_designer_specializations(db, designer_id)]
    availabilities = [a['day_of_week'] for a in get_designer_availability(db, designer_id) if a.get('is_available')]
    
    db.collection("designer_profiles").document(designer_id).update({
        "services": services,
        "skills": skills,
        "specializations": specializations,
        "availability": availabilities
    })
