"""
Chat models — project-scoped messaging.

Architecture:
    Project
      └── Conversation (1 per project, unique)
            ├── ConversationParticipant (client + assigned designer)
            └── Message (TEXT / FILE / SYSTEM, soft-deletable)
"""
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, ForeignKey,
    Boolean, Enum, Index, UniqueConstraint,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base
import enum


class MessageType(str, enum.Enum):
    TEXT = "text"
    FILE = "file"
    SYSTEM = "system"


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    # One conversation per project — enforced at DB level
    project_id = Column(
        Integer, ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False, unique=True, index=True,
    )
    last_message_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    project = relationship("Project")
    participants = relationship(
        "ConversationParticipant", back_populates="conversation",
        cascade="all, delete-orphan",
    )
    messages = relationship(
        "Message", back_populates="conversation",
        cascade="all, delete-orphan",
        order_by="desc(Message.created_at)",
    )


class ConversationParticipant(Base):
    __tablename__ = "conversation_participants"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(
        Integer, ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    # Tracks which message the user last read — used for unread count
    last_read_message_id = Column(
        Integer, ForeignKey("messages.id", ondelete="SET NULL"),
        nullable=True,
    )
    last_read_at = Column(DateTime(timezone=True), nullable=True)
    joined_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)

    __table_args__ = (
        UniqueConstraint("conversation_id", "user_id", name="uq_conversation_participant"),
    )

    # Relationships
    conversation = relationship("Conversation", back_populates="participants")
    user = relationship("User")
    last_read_message = relationship("Message", foreign_keys=[last_read_message_id])


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(
        Integer, ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    sender_id = Column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True, index=True,
    )
    content = Column(Text, nullable=False)
    message_type = Column(Enum(MessageType), nullable=False, default=MessageType.TEXT)

    # Reply threading
    reply_to_message_id = Column(
        Integer, ForeignKey("messages.id", ondelete="SET NULL"),
        nullable=True, index=True,
    )

    # JSON blob for file references (stored as text for cross-DB compat)
    meta_data = Column(Text, nullable=True)

    # Soft deletion
    is_deleted = Column(Boolean, nullable=False, default=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False)

    __table_args__ = (
        Index("ix_messages_conversation_created_at", "conversation_id", "created_at"),
    )

    # Relationships
    conversation = relationship("Conversation", back_populates="messages")
    sender = relationship("User", foreign_keys=[sender_id])
    reply_to = relationship("Message", foreign_keys=[reply_to_message_id], remote_side=[id])
