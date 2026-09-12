from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base
import enum


class InvitationStatus(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


class ProjectInvitation(Base):
    __tablename__ = "project_invitations"
    __table_args__ = (
        # Prevent duplicate invitations for the same project+designer
        UniqueConstraint("project_id", "designer_id", name="uq_invitation_project_designer"),
    )

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    designer_id = Column(Integer, ForeignKey("designer_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    client_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    message = Column(Text, nullable=True)
    status = Column(Enum(InvitationStatus), nullable=False, default=InvitationStatus.PENDING)
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    responded_at = Column(DateTime(timezone=True), nullable=True)

    project = relationship("Project", backref="invitations")
    designer = relationship("DesignerProfile", backref="invitations")
    client = relationship("User", backref="sent_invitations")
