"""Security utilities: password hashing and JWT token operations.

Uses PyJWT for JWT and bcrypt directly for password hashing.

NOTE: passlib has a known incompatibility with bcrypt >= 4.0 (it tries to detect
a bcrypt wrap bug using an internal API that no longer exists). We use bcrypt
directly to avoid this issue.
"""
import bcrypt
from datetime import datetime, timedelta, timezone
from typing import Optional
import jwt
from app.core.config import settings

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 1 day


def hash_password(password: str) -> str:
    """Hash a plaintext password using bcrypt."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against a bcrypt hash."""
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except Exception:
        return False


def create_access_token(
    subject: int | str,
    role: Optional[str] = None,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Create a JWT access token.

    Args:
        subject: The user ID (stored as string in 'sub' claim).
        role: Optional role string to embed in the token.
        expires_delta: Optional custom expiry. Defaults to ACCESS_TOKEN_EXPIRE_MINUTES.

    Returns:
        Encoded JWT string.
    """
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode: dict = {"sub": str(subject), "exp": expire}
    if role is not None:
        to_encode["role"] = role
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> Optional[dict]:
    """Decode and validate a JWT token.

    Returns:
        The decoded payload dict on success, or None if the token is invalid/expired.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
