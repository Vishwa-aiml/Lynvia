from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Any
from datetime import datetime
from enum import Enum

class NotificationType(str, Enum):
    PROJECT_CREATED = "PROJECT_CREATED"
    PROPOSAL_RECEIVED = "PROPOSAL_RECEIVED"
    PROPOSAL_ACCEPTED = "PROPOSAL_ACCEPTED"
    PROPOSAL_REJECTED = "PROPOSAL_REJECTED"
    PAYMENT_RECEIVED = "PAYMENT_RECEIVED"
    MILESTONE_CREATED = "MILESTONE_CREATED"
    MILESTONE_COMPLETED = "MILESTONE_COMPLETED"
    DELIVERY_SUBMITTED = "DELIVERY_SUBMITTED"
    REVISION_REQUESTED = "REVISION_REQUESTED"
    DELIVERY_ACCEPTED = "DELIVERY_ACCEPTED"
    NEW_MESSAGE = "NEW_MESSAGE"
    DISPUTE_OPENED = "DISPUTE_OPENED"
    SYSTEM_ALERT = "SYSTEM_ALERT"

class NotificationOut(BaseModel):
    id: str
    recipientId: str
    actorId: Optional[str]
    type: NotificationType
    title: str
    message: str
    entityType: Optional[str]
    entityId: Optional[str]
    metaData: Optional[str]  # JSON string; callers can parse if needed
    isRead: bool
    readAt: Optional[datetime]
    createdAt: datetime

    model_config = ConfigDict(from_attributes=True)


class NotificationListResponse(BaseModel):
    notifications: List[NotificationOut]
    total: int
    page: int
    limit: int
    unreadCount: int


class UnreadCountResponse(BaseModel):
    count: int


class MarkReadResponse(BaseModel):
    success: bool
    message: str


class PreferenceOut(BaseModel):
    id: str
    userId: str
    notificationType: NotificationType
    inAppEnabled: bool
    emailEnabled: bool
    pushEnabled: bool
    createdAt: datetime
    updatedAt: datetime

    model_config = ConfigDict(from_attributes=True)


class PreferenceUpdate(BaseModel):
    inAppEnabled: Optional[bool] = None
    emailEnabled: Optional[bool] = None
    pushEnabled: Optional[bool] = None
