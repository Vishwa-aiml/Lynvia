"""
Withdrawal models.

Withdrawal — tracks a designer's request to withdraw available earnings.
WithdrawalLedgerEntry — immutable, append-only audit log for withdrawal financial events.
    Kept separate from LedgerEntry because withdrawal events are not project-scoped
    (LedgerEntry.project_id is NOT NULL).

State machine:
    PENDING -> PROCESSING -> COMPLETED
    PENDING -> CANCELLED
    PROCESSING -> FAILED
"""
import enum
from sqlalchemy import (
    Column, Integer, String, BigInteger, DateTime, ForeignKey,
    Enum, Index, UniqueConstraint,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base


class WithdrawalStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class WithdrawalEntryType(str, enum.Enum):
    WITHDRAWAL_RESERVED = "withdrawal_reserved"
    WITHDRAWAL_RELEASED = "withdrawal_released"
    WITHDRAWAL_COMPLETED = "withdrawal_completed"
    WITHDRAWAL_PROCESSING = "withdrawal_processing"


# Valid state machine transitions
VALID_WITHDRAWAL_TRANSITIONS = {
    "pending": ["processing", "cancelled"],
    "processing": ["completed", "failed"],
    "completed": [],
    "failed": [],
    "cancelled": [],
}


class Withdrawal(Base):
    __tablename__ = "withdrawals"

    id = Column(Integer, primary_key=True, index=True)

    designer_profile_id = Column(
        Integer,
        ForeignKey("designer_profiles.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    amount = Column(BigInteger, nullable=False)
    currency = Column(String(3), nullable=False, default="INR")

    status = Column(
        Enum(WithdrawalStatus),
        nullable=False,
        default=WithdrawalStatus.PENDING,
        index=True,
    )

    payout_reference = Column(String(255), nullable=True)
    failure_reason = Column(String(500), nullable=True)
    idempotency_key = Column(String(255), nullable=True)

    requested_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    processing_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    failed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    designer_profile = relationship("DesignerProfile", foreign_keys=[designer_profile_id])
    user = relationship("User", foreign_keys=[user_id])
    ledger_entries = relationship(
        "WithdrawalLedgerEntry", back_populates="withdrawal", cascade="all, delete-orphan"
    )

    __table_args__ = (
        UniqueConstraint("idempotency_key", name="uix_withdrawal_idempotency_key"),
        Index("ix_withdrawals_designer_status", "designer_profile_id", "status"),
    )


class WithdrawalLedgerEntry(Base):
    """Append-only audit log for withdrawal financial events."""
    __tablename__ = "withdrawal_ledger_entries"

    id = Column(Integer, primary_key=True, index=True)
    withdrawal_id = Column(
        Integer,
        ForeignKey("withdrawals.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    designer_profile_id = Column(
        Integer,
        ForeignKey("designer_profiles.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    entry_type = Column(Enum(WithdrawalEntryType), nullable=False)
    amount = Column(BigInteger, nullable=False)
    currency = Column(String(3), nullable=False, default="INR")
    description = Column(String(500), nullable=True)

    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)

    withdrawal = relationship("Withdrawal", back_populates="ledger_entries")
