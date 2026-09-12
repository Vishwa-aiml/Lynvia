from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime, ForeignKey, Enum, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base
import enum


class NotificationType(str, enum.Enum):
    # Invitation flow
    PROJECT_INVITATION = "project_invitation"
    PROJECT_INVITATION_ACCEPTED = "project_invitation_accepted"
    PROJECT_INVITATION_DECLINED = "project_invitation_declined"

    # Project lifecycle
    PROJECT_ASSIGNED = "project_assigned"

    # Milestones
    MILESTONE_CREATED = "milestone_created"
    MILESTONE_UPDATED = "milestone_updated"

    # Tasks
    TASK_ASSIGNED = "task_assigned"
    TASK_UPDATED = "task_updated"

    # Files
    FILE_UPLOADED = "file_uploaded"
    FILE_UPDATED = "file_updated"

    # Delivery & revision
    DELIVERY_SUBMITTED = "delivery_submitted"
    REVISION_REQUESTED = "revision_requested"
    DELIVERY_ACCEPTED = "delivery_accepted"

    # Payments
    PAYMENT_CREATED = "payment_created"
    PAYMENT_SUCCESS = "payment_success"
    PAYMENT_FAILED = "payment_failed"

    # Earnings
    EARNINGS_RELEASED = "earnings_released"

    # System / catch-all
    SYSTEM = "system"

    # Chat messaging
    NEW_MESSAGE = "new_message"

    # Disputes
    DISPUTE_CREATED = "dispute_created"
    DISPUTE_RESPONSE = "dispute_response"
    DISPUTE_STATUS_CHANGED = "dispute_status_changed"
    DISPUTE_RESOLVED = "dispute_resolved"

    # Withdrawals
    WITHDRAWAL_REQUESTED = "withdrawal_requested"
    WITHDRAWAL_PROCESSING = "withdrawal_processing"
    WITHDRAWAL_COMPLETED = "withdrawal_completed"
    WITHDRAWAL_FAILED = "withdrawal_failed"
    WITHDRAWAL_CANCELLED = "withdrawal_cancelled"


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    recipient_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    actor_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    type = Column(Enum(NotificationType), nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)

    # Entity reference (e.g. entity_type="project", entity_id=42)
    entity_type = Column(String(50), nullable=True)
    entity_id = Column(Integer, nullable=True)

    # JSON metadata stored as text for cross-DB compatibility
    meta_data = Column(Text, nullable=True)

    is_read = Column(Boolean, nullable=False, default=False)
    read_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)

    # Relationships
    recipient = relationship("User", foreign_keys=[recipient_id], backref="notifications")
    actor = relationship("User", foreign_keys=[actor_id])

    __table_args__ = (
        # Composite indexes for common query patterns
        Index("ix_notifications_recipient_is_read", "recipient_id", "is_read"),
        Index("ix_notifications_recipient_created_at", "recipient_id", "created_at"),
    )
