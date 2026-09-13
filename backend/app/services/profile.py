from google.cloud.firestore import Client as FirestoreClient
from app.schemas.profile import ClientProfileCreate, ClientProfileUpdate, DesignerProfileCreate, DesignerProfileUpdate
from google.cloud.firestore_v1.base_query import FieldFilter

def get_client_profile(db: FirestoreClient, user_id: str):
    docs = db.collection("client_profiles").where(filter=FieldFilter("user_id", "==", user_id)).limit(1).stream()
    for doc in docs:
        data = doc.to_dict()
        data["id"] = doc.id
        return data
    return None

def create_client_profile(db: FirestoreClient, user_id: str, profile_in: ClientProfileCreate):
    profile_data = profile_in.dict()
    profile_data["user_id"] = user_id
    doc_ref = db.collection("client_profiles").document()
    db.collection("client_profiles").document(doc_ref.id).set(profile_data)
    profile_data["id"] = doc_ref.id
    return profile_data

def update_client_profile(db: FirestoreClient, user_id: str, profile_in: ClientProfileUpdate):
    profile = get_client_profile(db, user_id)
    if not profile:
        return None
    
    update_data = profile_in.dict(exclude_unset=True)
    if update_data:
        db.collection("client_profiles").document(profile["id"]).update(update_data)
        profile.update(update_data)
    return profile

def get_designer_profile(db: FirestoreClient, user_id: str):
    docs = db.collection("designer_profiles").where(filter=FieldFilter("user_id", "==", user_id)).limit(1).stream()
    for doc in docs:
        data = doc.to_dict()
        data["id"] = doc.id
        return data
    return None

def create_designer_profile(db: FirestoreClient, user_id: str, profile_in: DesignerProfileCreate):
    profile_data = profile_in.dict()
    profile_data["user_id"] = user_id
    doc_ref = db.collection("designer_profiles").document()
    db.collection("designer_profiles").document(doc_ref.id).set(profile_data)
    profile_data["id"] = doc_ref.id
    return profile_data

def update_designer_profile(db: FirestoreClient, user_id: str, profile_in: DesignerProfileUpdate):
    profile = get_designer_profile(db, user_id)
    if not profile:
        return None
    
    update_data = profile_in.dict(exclude_unset=True)
    if update_data:
        db.collection("designer_profiles").document(profile["id"]).update(update_data)
        profile.update(update_data)
    return profile
