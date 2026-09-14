from fastapi import APIRouter, Depends, HTTPException, status, Query
from google.cloud.firestore import Client as FirestoreClient
from typing import List

from app.db.firebase import get_db
from app.api.dependencies import get_current_user
from app.models.user import User
from app.schemas.notification import (
    NotificationListResponse,
    UnreadCountResponse,
    MarkReadResponse,
    PreferenceOut,
    PreferenceUpdate,
    NotificationType
)
import app.services.notifications as notif_svc

router = APIRouter(tags=["notifications"])


@router.get("/notifications", response_model=NotificationListResponse)
def get_notifications(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: FirestoreClient = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return notif_svc.get_notifications(db, current_user.id, page, limit)


@router.get("/notifications/unread-count", response_model=UnreadCountResponse)
def get_unread_count(
    db: FirestoreClient = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    count = notif_svc.get_unread_count(db, current_user.id)
    return UnreadCountResponse(count=count)


@router.patch("/notifications/{notification_id}/read", response_model=MarkReadResponse)
def mark_notification_as_read(
    notification_id: str,
    db: FirestoreClient = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        success = notif_svc.mark_as_read(db, current_user.id, notification_id)
        msg = "Notification marked as read" if success else "Notification already read"
        return MarkReadResponse(success=success, message=msg)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.patch("/notifications/read-all", response_model=MarkReadResponse)
def mark_all_notifications_as_read(
    db: FirestoreClient = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    count = notif_svc.mark_all_as_read(db, current_user.id)
    return MarkReadResponse(success=True, message=f"{count} notifications marked as read")


@router.get("/notifications/preferences", response_model=List[PreferenceOut])
def get_notification_preferences(
    db: FirestoreClient = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return notif_svc.get_all_preferences(db, current_user.id)


@router.patch("/notifications/preferences/{notification_type}", response_model=PreferenceOut)
def update_notification_preference(
    notification_type: str,
    updates: PreferenceUpdate,
    db: FirestoreClient = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        # Validate enum
        enum_val = NotificationType(notification_type)
        return notif_svc.update_preference(db, current_user.id, enum_val.value, updates)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid notification type")
