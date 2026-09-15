"""
Single authoritative authentication and authorisation dependencies for all routes.

Usage:
    from app.api.dependencies import get_current_user, require_client_role, require_designer_role, require_admin_role
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from google.cloud.firestore import Client as FirestoreClient
from app.db.firebase import get_db
import firebase_admin.auth as fb_auth
from app.models.user import User, UserRole
from app.core.config import settings

# OAuth2-compatible bearer token extractor
_bearer = HTTPBearer(auto_error=False)


def get_firebase_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
    db: FirestoreClient = Depends(get_db),
) -> dict:
    """Extract and verify the Firebase ID Token; return the authenticated User."""
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    try:
        payload = fb_auth.verify_id_token(token)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired Firebase token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("uid")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return payload

def get_current_user(
    payload: dict = Depends(get_firebase_user),
    db: FirestoreClient = Depends(get_db),
) -> User:
    """Check database and custom claims to return the full User model."""
    user_id = payload.get("uid")

    # First check custom claims for role
    role_str = payload.get("role")
    
    user_doc = None
    role = None
    
    if role_str == UserRole.CLIENT.value:
        user_doc = db.collection("clients").document(user_id).get()
        role = UserRole.CLIENT
    elif role_str == UserRole.DESIGNER.value:
        user_doc = db.collection("designers").document(user_id).get()
        role = UserRole.DESIGNER
    elif role_str == UserRole.ADMIN.value:
        user_doc = db.collection("users").document(user_id).get() # Admins still in users for now
        role = UserRole.ADMIN
    else:
        # Fallback if no custom claims are set yet
        user_doc = db.collection("clients").document(user_id).get()
        if user_doc.exists:
            role = UserRole.CLIENT
        else:
            user_doc = db.collection("designers").document(user_id).get()
            if user_doc.exists:
                role = UserRole.DESIGNER

    if not user_doc or not user_doc.exists:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found in database",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_data = user_doc.to_dict()
    user_data["id"] = user_id
    user_data["role"] = role
    
    # We map back to the universal User model for compatibility across backend
    user = User(**user_data)

    # If the user model tracks account status, we check it
    if hasattr(user, "accountStatus") and user.accountStatus != "ACTIVE":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is inactive or suspended",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


def require_client_role(current_user: User = Depends(get_current_user)) -> User:
    """Assert the authenticated user has the CLIENT role."""
    if current_user.role != UserRole.CLIENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Client role required",
        )
    return current_user


def require_designer_role(current_user: User = Depends(get_current_user)) -> User:
    """Assert the authenticated user has the DESIGNER role."""
    if current_user.role != UserRole.DESIGNER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Designer role required",
        )
    return current_user


def require_admin_role(current_user: User = Depends(get_current_user)) -> User:
    """
    Assert the authenticated user:
      1. Has the ADMIN role.
      2. Has an email that matches the configured ADMIN_EMAIL (case-insensitive).

    Both conditions must be true; failing either returns HTTP 403.
    The error message is generic to avoid leaking configuration details.
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access denied",
        )

    # Normalized case-insensitive, whitespace-trimmed email comparison
    if current_user.email.strip().lower() != settings.ADMIN_EMAIL.strip().lower():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access denied",
        )

    return current_user
