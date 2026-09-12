from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, BigInteger
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base
import enum


class ProjectStatus(str, enum.Enum):
    DRAFT = "draft"
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False, index=True)
    assigned_designer_id = Column(Integer, ForeignKey("designer_profiles.id", ondelete="SET NULL"), nullable=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    requirements = Column(Text, nullable=True)
    budget = Column(BigInteger, nullable=True)  # stored in minor units
    deadline = Column(DateTime(timezone=True), nullable=True)
    status = Column(Enum(ProjectStatus), nullable=False, default=ProjectStatus.DRAFT)
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    client = relationship("User", foreign_keys=[client_id], backref="projects")
    assigned_designer = relationship("DesignerProfile", foreign_keys=[assigned_designer_id])
    
    # Workspace Relationships
    milestones = relationship("Milestone", back_populates="project", cascade="all, delete-orphan", order_by="Milestone.order")
    files = relationship("FileMetadata", back_populates="project", cascade="all, delete-orphan")
    events = relationship("ProjectEvent", back_populates="project", cascade="all, delete-orphan", order_by="desc(ProjectEvent.created_at)")
    deliveries = relationship("Delivery", back_populates="project", cascade="all, delete-orphan", order_by="desc(Delivery.version)")
