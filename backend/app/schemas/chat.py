"""
Chat Pydantic schemas.
"""
from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum

class MessageType(str, Enum):
    TEXT = "TEXT"
    FILE = "FILE"
    SYSTEM = "SYSTEM"
    MILESTONE_UPDATE = "MILESTONE_UPDATE"

# -- Conversation ---------------------------------------------------------------

class ConversationOut(BaseModel):
    id: str
    projectId: str
    lastMessageAt: Optional[datetime] = None
    createdAt: datetime

    model_config = ConfigDict(from_attributes=True)

# -- Messages -------------------------------------------------------------------

class MessageCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=4000)
    messageType: MessageType = MessageType.TEXT
    replyToMessageId: Optional[str] = None


class MessageUpdate(BaseModel):
    content: str = Field(..., min_length=1, max_length=4000)


class MessageOut(BaseModel):
    id: str
    conversationId: str
    senderId: Optional[str]
    content: str
    messageType: MessageType
    replyToMessageId: Optional[str] = None
    isDeleted: bool
    createdAt: datetime
    updatedAt: datetime

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_orm_safe(cls, msg: Any) -> "MessageOut":
        """Redact content if message is soft-deleted."""
        obj = cls.model_validate(msg)
        if obj.isDeleted:
            obj.content = "This message was deleted."
        return obj


class MessageListResponse(BaseModel):
    messages: List[MessageOut]
    total: int
    page: int
    limit: int
    hasNext: bool


# -- Read state -----------------------------------------------------------------

class ChatUnreadCountResponse(BaseModel):
    unreadCount: int


class MarkChatReadResponse(BaseModel):
    updated: bool

