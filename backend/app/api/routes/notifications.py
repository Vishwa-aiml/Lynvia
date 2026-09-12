from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.api.dependencies import get_current_user
from app.models.user import User
from app.models.notification import NotificationType
from app.schemas.notification import (
    NotificationListResponse,
    UnreadCountResponse,
    MarkReadResponse,
    PreferenceOut,
    PreferenceUpdate,
)
import app.services.notifications as notif_svc

router = APIRouter()


@router.get("/notifications", response_model=NotificationListResponse)
def get_notifications(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a paginated list of notifications for the current user."""
    return notif_svc.get_notifications(db, current_user.id, page, limit)


@router.get("/notifications/unread-count", response_model=UnreadCountResponse)
def get_unread_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get the total count of unread notifications for the current user."""
    count = notif_svc.get_unread_count(db, current_user.id)
    return UnreadCountResponse(count=count)


@router.patch("/notifications/{notification_id}/read", response_model=MarkReadResponse)
def mark_notification_as_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark a specific notification as read."""
    notification = notif_svc.mark_as_read(db, notification_id, current_user.id)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    return MarkReadResponse(success=True, message="Notification marked as read")


@router.patch("/notifications/read-all", response_model=MarkReadResponse)
def mark_all_notifications_as_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark all unread notifications as read for the current user."""
    count = notif_svc.mark_all_as_read(db, current_user.id)
    return MarkReadResponse(success=True, message=f"{count} notifications marked as read")


@router.get("/notifications/preferences", response_model=List[PreferenceOut])
def get_notification_preferences(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all notification preferences for the current user."""
    return notif_svc.get_all_preferences(db, current_user.id)


@router.patch("/notifications/preferences/{notification_type}", response_model=PreferenceOut)
def update_notification_preference(
    notification_type: NotificationType,
    pref_in: PreferenceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a specific notification preference."""
    pref = notif_svc.update_preference(
        db=db,
        user_id=current_user.id,
        notification_type=notification_type,
        in_app_enabled=pref_in.in_app_enabled,
        email_enabled=pref_in.email_enabled,
        push_enabled=pref_in.push_enabled,
    )
    return pref
