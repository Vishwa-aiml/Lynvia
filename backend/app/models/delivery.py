from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, Table
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.db.base import Base


class DeliveryStatus(str, enum.Enum):
    PENDING_REVIEW = "pending_review"
    ACCEPTED = "accepted"
    REVISION_REQUESTED = "revision_requested"


class RevisionStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"


# Association table mapping deliveries to their associated files
delivery_files = Table(
    "delivery_files",
    Base.metadata,
    Column("delivery_id", Integer, ForeignKey("deliveries.id", ondelete="CASCADE"), primary_key=True),
    Column("file_metadata_id", Integer, ForeignKey("file_metadata.id", ondelete="CASCADE"), primary_key=True)
)


class Delivery(Base):
    __tablename__ = "deliveries"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    designer_id = Column(Integer, ForeignKey("designer_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    
    version = Column(Integer, nullable=False, default=1)
    message = Column(Text, nullable=True)
    status = Column(Enum(DeliveryStatus), nullable=False, default=DeliveryStatus.PENDING_REVIEW)
    
    submitted_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)

    # Relationships
    project = relationship("Project", back_populates="deliveries")
    designer = relationship("DesignerProfile")
    files = relationship("FileMetadata", secondary=delivery_files, backref="deliveries")
    revisions = relationship("Revision", back_populates="delivery", cascade="all, delete-orphan")


class Revision(Base):
    __tablename__ = "revisions"

    id = Column(Integer, primary_key=True, index=True)
    delivery_id = Column(Integer, ForeignKey("deliveries.id", ondelete="CASCADE"), nullable=False, index=True)
    
    revision_number = Column(Integer, nullable=False, default=1)
    request_reason = Column(String(255), nullable=False)
    client_comment = Column(Text, nullable=False)
    designer_response = Column(Text, nullable=True)
    status = Column(Enum(RevisionStatus), nullable=False, default=RevisionStatus.PENDING)
    
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    delivery = relationship("Delivery", back_populates="revisions")
