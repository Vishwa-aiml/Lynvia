from google.cloud.firestore import Client as FirestoreClient
from app.models.user import User, UserRole
from app.schemas.auth import UserCreate
from datetime import datetime, timezone

def get_user_by_uid(db: FirestoreClient, uid: str, role: UserRole) -> User | None:
    collection_name = "clients" if role == UserRole.CLIENT else "designers"
    doc = db.collection(collection_name).document(uid).get()
    
    if doc.exists:
        data = doc.to_dict()
        data["id"] = doc.id
        data["role"] = role
        return User(**data)
    
    # Check users collection for ADMIN fallback
    if role == UserRole.ADMIN:
        doc = db.collection("users").document(uid).get()
        if doc.exists:
            data = doc.to_dict()
            data["id"] = doc.id
            data["role"] = role
            return User(**data)
            
    return None

def create_user(db: FirestoreClient, uid: str, user_in: UserCreate) -> User:
    role = user_in.role if user_in.role else UserRole.CLIENT
    norm_email = user_in.email.strip().lower()
    
    collection_name = "clients" if role == UserRole.CLIENT else "designers"
    
    user_data = {
        "email": norm_email,
        "full_name": user_in.full_name,
        "accountStatus": "ACTIVE",
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }
    
    # We use the actual Firebase UID as the document ID
    db.collection(collection_name).document(uid).set(user_data)
    
    user_data["id"] = uid
    user_data["role"] = role
    return User(**user_data)
