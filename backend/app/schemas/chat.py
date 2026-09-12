"""
Chat Pydantic schemas.
"""
from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel, Field, model_validator
from app.models.chat import MessageType

# ── Conversation ───────────────────────────────────────────────────────────────

class ConversationOut(BaseModel):
    id: int
    project_id: int
    last_message_at: Optional[datetime] = None
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Messages ───────────────────────────────────────────────────────────────────

class MessageCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=4000)
    message_type: MessageType = MessageType.TEXT
    reply_to_message_id: Optional[int] = None


class MessageUpdate(BaseModel):
    content: str = Field(..., min_length=1, max_length=4000)


class MessageOut(BaseModel):
    id: int
    conversation_id: int
    sender_id: Optional[int]
    content: str
    message_type: MessageType
    reply_to_message_id: Optional[int] = None
    is_deleted: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

    @classmethod
    def from_orm_safe(cls, msg: Any) -> "MessageOut":
        """Redact content if message is soft-deleted."""
        obj = cls.model_validate(msg)
        if obj.is_deleted:
            obj.content = "This message was deleted."
        return obj


class MessageListResponse(BaseModel):
    messages: List[MessageOut]
    total: int
    page: int
    limit: int
    has_next: bool


# ── Read state ─────────────────────────────────────────────────────────────────

class ChatUnreadCountResponse(BaseModel):
    unread_count: int


class MarkChatReadResponse(BaseModel):
    updated: bool
