from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Any
from datetime import datetime
from app.models.notification import NotificationType


class NotificationOut(BaseModel):
    id: int
    recipient_id: int
    actor_id: Optional[int]
    type: NotificationType
    title: str
    message: str
    entity_type: Optional[str]
    entity_id: Optional[int]
    meta_data: Optional[str]  # JSON string; callers can parse if needed
    is_read: bool
    read_at: Optional[datetime]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class NotificationListResponse(BaseModel):
    notifications: List[NotificationOut]
    total: int
    page: int
    limit: int
    unread_count: int


class UnreadCountResponse(BaseModel):
    count: int


class MarkReadResponse(BaseModel):
    success: bool
    message: str


class PreferenceOut(BaseModel):
    id: int
    user_id: int
    notification_type: NotificationType
    in_app_enabled: bool
    email_enabled: bool
    push_enabled: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PreferenceUpdate(BaseModel):
    in_app_enabled: Optional[bool] = None
    email_enabled: Optional[bool] = None
    push_enabled: Optional[bool] = None
