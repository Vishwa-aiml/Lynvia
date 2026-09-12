"""
Dispute models — project-scoped dispute and resolution system.

State machine:
    OPEN → UNDER_REVIEW → WAITING_FOR_CLIENT / WAITING_FOR_DESIGNER → UNDER_REVIEW → RESOLVED / REJECTED
    OPEN / UNDER_REVIEW → CANCELLED (by creator or admin)
"""
from sqlalchemy import (
    Column, Integer, BigInteger, String, Text, DateTime,
    ForeignKey, Enum, Index,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base
import enum


class DisputeReason(str, enum.Enum):
    DELIVERY_QUALITY = "delivery_quality"
    REQUIREMENT_MISMATCH = "requirement_mismatch"
    MISSED_DEADLINE = "missed_deadline"
    OUT_OF_SCOPE_REQUEST = "out_of_scope_request"
    REFUND_REQUEST = "refund_request"
    PAYMENT_ISSUE = "payment_issue"
    NON_RESPONSIVE_PARTY = "non_responsive_party"
    OTHER = "other"


class DisputeStatus(str, enum.Enum):
    OPEN = "open"
    UNDER_REVIEW = "under_review"
    WAITING_FOR_CLIENT = "waiting_for_client"
    WAITING_FOR_DESIGNER = "waiting_for_designer"
    RESOLVED = "resolved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


class ResolutionType(str, enum.Enum):
    RELEASE_TO_DESIGNER = "release_to_designer"
    FULL_REFUND_TO_CLIENT = "full_refund_to_client"
    PARTIAL_REFUND_TO_CLIENT = "partial_refund_to_client"
    NO_REFUND = "no_refund"
    MUTUAL_RESOLUTION = "mutual_resolution"


# Valid status transitions (from -> {allowed tos})
VALID_TRANSITIONS: dict = {
    DisputeStatus.OPEN: {
        DisputeStatus.UNDER_REVIEW,
        DisputeStatus.CANCELLED,
    },
    DisputeStatus.UNDER_REVIEW: {
        DisputeStatus.WAITING_FOR_CLIENT,
        DisputeStatus.WAITING_FOR_DESIGNER,
        DisputeStatus.RESOLVED,
        DisputeStatus.REJECTED,
        DisputeStatus.CANCELLED,
    },
    DisputeStatus.WAITING_FOR_CLIENT: {
        DisputeStatus.UNDER_REVIEW,
        DisputeStatus.RESOLVED,
        DisputeStatus.REJECTED,
        DisputeStatus.CANCELLED,
    },
    DisputeStatus.WAITING_FOR_DESIGNER: {
        DisputeStatus.UNDER_REVIEW,
        DisputeStatus.RESOLVED,
        DisputeStatus.REJECTED,
        DisputeStatus.CANCELLED,
    },
    # Terminal states — no further transitions
    DisputeStatus.RESOLVED: set(),
    DisputeStatus.REJECTED: set(),
    DisputeStatus.CANCELLED: set(),
}


class Dispute(Base):
    __tablename__ = "disputes"

    id = Column(Integer, primary_key=True, index=True)

    project_id = Column(
        Integer, ForeignKey("projects.id", ondelete="RESTRICT"),
        nullable=False, index=True,
    )
    # Optional link to the specific payment being disputed
    payment_id = Column(
        Integer, ForeignKey("payments.id", ondelete="RESTRICT"),
        nullable=True, index=True,
    )

    # User who raised the dispute (client or designer user)
    raised_by_user_id = Column(
        Integer, ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False, index=True,
    )
    # The other party (client or designer user)
    against_user_id = Column(
        Integer, ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False, index=True,
    )

    reason = Column(Enum(DisputeReason), nullable=False)
    description = Column(Text, nullable=False)

    status = Column(Enum(DisputeStatus), nullable=False, default=DisputeStatus.OPEN)

    # Populated only when resolved
    resolution_type = Column(Enum(ResolutionType), nullable=True)
    # Minor-unit amount (paise) for PARTIAL_REFUND
    resolution_amount = Column(BigInteger, nullable=True)
    resolution_note = Column(Text, nullable=True)
    resolved_by_user_id = Column(
        Integer, ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=True,
    )
    resolved_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    __table_args__ = (
        Index("ix_disputes_project_id_status", "project_id", "status"),
    )

    # Relationships
    project = relationship("Project")
    payment = relationship("Payment")
    raised_by = relationship("User", foreign_keys=[raised_by_user_id])
    against = relationship("User", foreign_keys=[against_user_id])
    resolved_by = relationship("User", foreign_keys=[resolved_by_user_id])
    responses = relationship(
        "DisputeResponse", back_populates="dispute",
        cascade="all, delete-orphan",
        order_by="DisputeResponse.created_at",
    )


class DisputeResponse(Base):
    __tablename__ = "dispute_responses"

    id = Column(Integer, primary_key=True, index=True)
    dispute_id = Column(
        Integer, ForeignKey("disputes.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False, index=True,
    )
    message = Column(Text, nullable=False)
    # JSON-encoded list of file metadata references (reuses existing FileMetadata ids)
    attachment_meta = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)

    # Responses are immutable — no updated_at

    # Relationships
    dispute = relationship("Dispute", back_populates="responses")
    user = relationship("User")
