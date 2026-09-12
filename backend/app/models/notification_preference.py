from sqlalchemy import Column, Integer, Boolean, DateTime, ForeignKey, Enum, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base
from app.models.notification import NotificationType


class NotificationPreference(Base):
    __tablename__ = "notification_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    notification_type = Column(Enum(NotificationType), nullable=False)

    # Current phase: only in_app_enabled is enforced
    in_app_enabled = Column(Boolean, nullable=False, default=True)

    # Future-ready channels — stored now, not yet active
    email_enabled = Column(Boolean, nullable=False, default=False)
    push_enabled = Column(Boolean, nullable=False, default=False)

    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    user = relationship("User", backref="notification_preferences")

    __table_args__ = (
        UniqueConstraint("user_id", "notification_type", name="uq_pref_user_type"),
    )
