from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.db.base import Base


class ProjectEventType(str, enum.Enum):
    COMMENT = "comment"
    MILESTONE_UPDATE = "milestone_update"
    TASK_UPDATE = "task_update"
    FILE_UPLOAD = "file_upload"
    DELIVERY_SUBMITTED = "delivery_submitted"
    DELIVERY_ACCEPTED = "delivery_accepted"
    REVISION_REQUESTED = "revision_requested"
    DISPUTE_CREATED = "dispute_created"
    DISPUTE_STATUS_CHANGED = "dispute_status_changed"
    DISPUTE_RESPONSE_ADDED = "dispute_response_added"
    DISPUTE_RESOLVED = "dispute_resolved"
    DISPUTE_REJECTED = "dispute_rejected"
    DISPUTE_PAYMENT_ADJUSTED = "dispute_payment_adjusted"


class ProjectEvent(Base):
    __tablename__ = "project_events"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    author_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    event_type = Column(Enum(ProjectEventType), nullable=False)
    content = Column(Text, nullable=True) # Store comment text or JSON payload for other events
    
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)

    # Relationships
    project = relationship("Project", back_populates="events")
    author = relationship("User")
