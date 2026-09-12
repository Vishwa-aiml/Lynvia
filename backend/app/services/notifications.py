"""
Notification Service — centralized, channel-agnostic notification creation.

Architecture:
    Domain Event
        │
        ▼
    Existing Service (invitation, workspace, payment…)
        │
        ▼
    create_notification() / create_bulk_notifications()
        │
        ├── Check NotificationPreference.in_app_enabled
        │
        └── INSERT Notification row
                 │
             (Future hooks: WebSocket, Email, Push)

This service never touches HTTP. It is pure DB business logic.
"""
import json
import logging
from datetime import datetime, timezone
from typing import Optional, List, Any

from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.notification import Notification, NotificationType
from app.models.notification_preference import NotificationPreference
from app.schemas.notification import (
    NotificationListResponse,
    NotificationOut,
    UnreadCountResponse,
)

logger = logging.getLogger(__name__)

# ── Pagination limits ─────────────────────────────────────────────────────────
DEFAULT_PAGE_LIMIT = 20
MAX_PAGE_LIMIT = 100


# ── Preference helpers ────────────────────────────────────────────────────────

def get_or_create_preference(
    db: Session,
    user_id: int,
    notification_type: NotificationType,
) -> NotificationPreference:
    """Return existing preference, or create a default-enabled one."""
    pref = db.query(NotificationPreference).filter(
        NotificationPreference.user_id == user_id,
        NotificationPreference.notification_type == notification_type,
    ).first()
    if pref:
        return pref
    pref = NotificationPreference(
        user_id=user_id,
        notification_type=notification_type,
        in_app_enabled=True,
        email_enabled=False,
        push_enabled=False,
    )
    db.add(pref)
    db.flush()  # don't commit — caller decides transaction boundary
    return pref


def get_all_preferences(db: Session, user_id: int) -> List[NotificationPreference]:
    return db.query(NotificationPreference).filter(
        NotificationPreference.user_id == user_id
    ).all()


def update_preference(
    db: Session,
    user_id: int,
    notification_type: NotificationType,
    in_app_enabled: Optional[bool] = None,
    email_enabled: Optional[bool] = None,
    push_enabled: Optional[bool] = None,
) -> NotificationPreference:
    pref = get_or_create_preference(db, user_id, notification_type)
    if in_app_enabled is not None:
        pref.in_app_enabled = in_app_enabled
    if email_enabled is not None:
        pref.email_enabled = email_enabled
    if push_enabled is not None:
        pref.push_enabled = push_enabled
    db.add(pref)
    db.commit()
    db.refresh(pref)
    return pref


def _is_in_app_enabled(
    db: Session,
    user_id: int,
    notification_type: NotificationType,
) -> bool:
    """Check if in-app notifications are enabled for this user+type. Default: True."""
    pref = db.query(NotificationPreference).filter(
        NotificationPreference.user_id == user_id,
        NotificationPreference.notification_type == notification_type,
    ).first()
    if pref is None:
        return True  # default enabled
    return pref.in_app_enabled


# ── Core notification creation ────────────────────────────────────────────────

def create_notification(
    db: Session,
    recipient_id: int,
    notification_type: NotificationType,
    title: str,
    message: str,
    actor_id: Optional[int] = None,
    entity_type: Optional[str] = None,
    entity_id: Optional[int] = None,
    meta_data: Optional[dict] = None,
) -> Optional[Notification]:
    """
    Create a single in-app notification, respecting user preferences.

    Returns the created Notification, or None if preference disabled.
    Does NOT commit — relies on the caller's transaction.
    """
    if not _is_in_app_enabled(db, recipient_id, notification_type):
        logger.debug(
            "Notification suppressed for user=%d type=%s (preference disabled)",
            recipient_id, notification_type,
        )
        return None

    metadata_str = json.dumps(meta_data) if meta_data else None

    notification = Notification(
        recipient_id=recipient_id,
        actor_id=actor_id,
        type=notification_type,
        title=title,
        message=message,
        entity_type=entity_type,
        entity_id=entity_id,
        meta_data=metadata_str,
        is_read=False,
        read_at=None,
    )
    db.add(notification)
    db.flush()
    return notification


def create_bulk_notifications(
    db: Session,
    recipient_ids: List[int],
    notification_type: NotificationType,
    title: str,
    message: str,
    actor_id: Optional[int] = None,
    entity_type: Optional[str] = None,
    entity_id: Optional[int] = None,
    meta_data: Optional[dict] = None,
) -> List[Notification]:
    """Create notifications for multiple recipients, checking each preference."""
    created = []
    for recipient_id in recipient_ids:
        n = create_notification(
            db=db,
            recipient_id=recipient_id,
            notification_type=notification_type,
            title=title,
            message=message,
            actor_id=actor_id,
            entity_type=entity_type,
            entity_id=entity_id,
            meta_data=meta_data,
        )
        if n:
            created.append(n)
    return created


# ── Read state ────────────────────────────────────────────────────────────────

def mark_as_read(
    db: Session,
    notification_id: int,
    user_id: int,
) -> Optional[Notification]:
    """
    Mark a single notification as read (idempotent).
    Returns None if not found or not owned by user.
    """
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.recipient_id == user_id,
    ).first()
    if not notification:
        return None
    if not notification.is_read:
        notification.is_read = True
        notification.read_at = datetime.now(timezone.utc)
        db.add(notification)
        db.commit()
        db.refresh(notification)
    return notification


def mark_all_as_read(db: Session, user_id: int) -> int:
    """
    Mark all unread notifications for a user as read.
    Returns the count of rows updated.
    """
    now = datetime.now(timezone.utc)
    updated = db.query(Notification).filter(
        Notification.recipient_id == user_id,
        Notification.is_read == False,  # noqa: E712
    ).all()
    count = len(updated)
    for n in updated:
        n.is_read = True
        n.read_at = now
        db.add(n)
    db.commit()
    return count


# ── Queries ───────────────────────────────────────────────────────────────────

def get_unread_count(db: Session, user_id: int) -> int:
    """Efficient COUNT query for unread notifications."""
    return db.query(func.count(Notification.id)).filter(
        Notification.recipient_id == user_id,
        Notification.is_read == False,  # noqa: E712
    ).scalar() or 0


def get_notifications(
    db: Session,
    user_id: int,
    page: int = 1,
    limit: int = DEFAULT_PAGE_LIMIT,
) -> NotificationListResponse:
    """
    Paginated list of notifications for a user, ordered by created_at DESC.
    Enforces MAX_PAGE_LIMIT.
    """
    limit = min(limit, MAX_PAGE_LIMIT)
    page = max(page, 1)
    offset = (page - 1) * limit

    total = db.query(func.count(Notification.id)).filter(
        Notification.recipient_id == user_id,
    ).scalar() or 0

    notifications = db.query(Notification).filter(
        Notification.recipient_id == user_id,
    ).order_by(Notification.created_at.desc()).offset(offset).limit(limit).all()

    unread_count = get_unread_count(db, user_id)

    return NotificationListResponse(
        notifications=[NotificationOut.model_validate(n) for n in notifications],
        total=total,
        page=page,
        limit=limit,
        unread_count=unread_count,
    )
