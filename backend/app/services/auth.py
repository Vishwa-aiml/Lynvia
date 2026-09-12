from google.cloud.firestore import Client as FirestoreClient
from app.models.user import User, UserRole
from app.schemas.auth import UserCreate
from app.utils.security import hash_password, verify_password
from datetime import datetime, timezone
import uuid


def get_user_by_email(db: FirestoreClient, email: str) -> User | None:
    norm = email.strip().lower()
    users_ref = db.collection("users").where(field_path="email", op_string="==", value=norm).limit(1).stream()
    for doc in users_ref:
        data = doc.to_dict()
        data["id"] = doc.id
        return User(**data)
    return None


def create_user(db: FirestoreClient, user_in: UserCreate) -> User:
    role = user_in.role if user_in.role else UserRole.CLIENT
    norm_email = user_in.email.strip().lower()
    
    # Generate a unique ID (Firestore document ID)
    user_id = str(uuid.uuid4())
    
    user_data = {
        "email": norm_email,
        "full_name": user_in.full_name,
        "role": role.value,
        "hashed_password": hash_password(user_in.password),
        "is_active": True,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }
    
    db.collection("users").document(user_id).set(user_data)
    
    user_data["id"] = user_id
    user_data["role"] = role
    return User(**user_data)


def authenticate_user(db: FirestoreClient, email: str, password: str) -> User | None:
    """Return the user if credentials are valid and account is active, else None."""
    user = get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    if not user.is_active:
        return None
    return user
