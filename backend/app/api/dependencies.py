"""
Single authoritative authentication and authorisation dependencies for all routes.

Usage:
    from app.api.dependencies import get_current_user, require_client_role, require_designer_role, require_admin_role
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from google.cloud.firestore import Client as FirestoreClient
from app.db.firebase import get_db
from app.utils.security import decode_access_token
from app.models.user import User, UserRole
from app.core.config import settings

# OAuth2-compatible bearer token extractor
_bearer = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
    db: FirestoreClient = Depends(get_db),
) -> User:
    """Extract and verify the JWT Bearer token; return the authenticated User."""
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id_str = payload.get("sub")
    if not user_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # In Firestore, document IDs are strings, so we don't need to cast to int.
    user_id = user_id_str

    user_doc = db.collection("users").document(user_id).get()
    if not user_doc.exists:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_data = user_doc.to_dict()
    user_data["id"] = user_id
    user = User(**user_data)

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is inactive",
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
