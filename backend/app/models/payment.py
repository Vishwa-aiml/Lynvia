from sqlalchemy import Column, Integer, String, BigInteger, DateTime, ForeignKey, Enum, Numeric, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from app.db.base import Base


class PaymentStatus(str, enum.Enum):
    CREATED = "created"
    PENDING = "pending"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"
    PARTIALLY_REFUNDED = "partially_refunded"


class TransactionType(str, enum.Enum):
    PAYMENT = "payment"
    COMMISSION = "commission"
    DESIGNER_EARNING = "designer_earning"
    REFUND = "refund"
    REVERSAL = "reversal"


class TransactionStatus(str, enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"


class EarningStatus(str, enum.Enum):
    PENDING = "pending"
    AVAILABLE = "available"
    HELD = "held"
    REVERSED = "reversed"
    WITHDRAWAL_PENDING = "withdrawal_pending"  # reserved for an in-flight withdrawal
    PAID = "paid"                              # payout completed successfully


class EntryDirection(str, enum.Enum):
    CREDIT = "credit"
    DEBIT = "debit"


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="RESTRICT"), nullable=False, index=True)
    client_id = Column(Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True)
    
    amount = Column(BigInteger, nullable=False) # stored in minor units (paise)
    currency = Column(String(3), nullable=False, default="INR")
    
    provider = Column(String(50), nullable=False, default="razorpay")
    provider_order_id = Column(String(255), nullable=True, unique=True, index=True)
    provider_payment_id = Column(String(255), nullable=True, unique=True, index=True)
    
    status = Column(Enum(PaymentStatus), nullable=False, default=PaymentStatus.CREATED)
    
    paid_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    project = relationship("Project", backref="payments")
    client = relationship("User", foreign_keys=[client_id])
    transactions = relationship("Transaction", back_populates="payment", cascade="all, delete-orphan")


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    payment_id = Column(Integer, ForeignKey("payments.id", ondelete="RESTRICT"), nullable=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="RESTRICT"), nullable=False, index=True)
    
    type = Column(Enum(TransactionType), nullable=False)
    amount = Column(BigInteger, nullable=False)
    currency = Column(String(3), nullable=False, default="INR")
    status = Column(Enum(TransactionStatus), nullable=False, default=TransactionStatus.PENDING)
    
    provider_reference = Column(String(255), nullable=True)
    metadata_json = Column(String, nullable=True) # JSON string if needed
    
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)

    # Relationships
    payment = relationship("Payment", back_populates="transactions")
    project = relationship("Project")


class LedgerEntry(Base):
    __tablename__ = "ledger_entries"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="RESTRICT"), nullable=False, index=True)
    payment_id = Column(Integer, ForeignKey("payments.id", ondelete="RESTRICT"), nullable=True, index=True)
    transaction_id = Column(Integer, ForeignKey("transactions.id", ondelete="RESTRICT"), nullable=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=True, index=True)
    
    entry_type = Column(String(50), nullable=False) # e.g. "CLIENT_PAYMENT", "PLATFORM_COMMISSION", "DESIGNER_EARNING"
    amount = Column(BigInteger, nullable=False)
    currency = Column(String(3), nullable=False, default="INR")
    direction = Column(Enum(EntryDirection), nullable=False)
    description = Column(String(255), nullable=True)
    
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)

    # Note: Immutable, append-only.


class DesignerEarning(Base):
    __tablename__ = "designer_earnings"

    id = Column(Integer, primary_key=True, index=True)
    designer_id = Column(Integer, ForeignKey("designer_profiles.id", ondelete="RESTRICT"), nullable=False, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="RESTRICT"), nullable=False, index=True)
    payment_id = Column(Integer, ForeignKey("payments.id", ondelete="RESTRICT"), nullable=True, index=True)
    
    gross_amount = Column(BigInteger, nullable=False)
    platform_fee = Column(BigInteger, nullable=False)
    net_amount = Column(BigInteger, nullable=False)
    currency = Column(String(3), nullable=False, default="INR")
    
    status = Column(Enum(EarningStatus), nullable=False, default=EarningStatus.PENDING)
    
    available_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False)


class WebhookEvent(Base):
    __tablename__ = "webhook_events"

    id = Column(Integer, primary_key=True, index=True)
    provider = Column(String(50), nullable=False)
    event_id = Column(String(255), nullable=False)
    event_type = Column(String(255), nullable=False)
    
    payload = Column(String, nullable=True) # Text/JSON
    processed = Column(Integer, default=0, nullable=False) # 0=False, 1=True
    processed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)

    __table_args__ = (
        UniqueConstraint('provider', 'event_id', name='uix_provider_event_id'),
    )
