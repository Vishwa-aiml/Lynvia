"""
Withdrawal service — business logic for designer payouts.

Money rules:
- All amounts in integer minor units (paise). No float arithmetic.
- DesignerEarning.net_amount is the canonical amount for balance calculation.
- Ledger entries are append-only; never update or delete.
- Earning status AVAILABLE -> WITHDRAWAL_PENDING on reserve.
- Earning status WITHDRAWAL_PENDING -> PAID on completion.
- Earning status WITHDRAWAL_PENDING -> AVAILABLE on release (fail/cancel).

Balance derivation from DesignerEarning (by designer_profile_id):
    pending_balance    = SUM(net_amount) WHERE status=PENDING
    available_balance  = SUM(net_amount) WHERE status=AVAILABLE
    processing_balance = SUM(net_amount) WHERE status=WITHDRAWAL_PENDING
    withdrawn_balance  = SUM(net_amount) WHERE status=PAID
"""
from __future__ import annotations
import logging
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.payment import DesignerEarning, EarningStatus
from app.models.profile import DesignerProfile
from app.models.user import User, UserRole
from app.models.withdrawal import (
    Withdrawal, WithdrawalStatus, WithdrawalLedgerEntry, WithdrawalEntryType,
    VALID_WITHDRAWAL_TRANSITIONS,
)
from app.schemas.withdrawal import (
    WalletOut, WithdrawalCreate, WithdrawalOut,
    WithdrawalListResponse, WithdrawalProcessRequest,
    WithdrawalCompleteRequest, WithdrawalFailRequest,
)

logger = logging.getLogger(__name__)


# ── Internal helpers ──────────────────────────────────────────────────────────

def _get_designer_profile(db: Session, user: User) -> DesignerProfile:
    profile = db.query(DesignerProfile).filter(DesignerProfile.user_id == user.id).first()
    if not profile:
        raise ValueError("Designer profile not found")
    return profile


def _sum_earnings(db: Session, designer_profile_id: int, status: EarningStatus) -> int:
    result = db.query(
        func.coalesce(func.sum(DesignerEarning.net_amount), 0)
    ).filter(
        DesignerEarning.designer_id == designer_profile_id,
        DesignerEarning.status == status,
    ).scalar()
    return int(result)


def _append_ledger(
    db: Session,
    withdrawal: Withdrawal,
    entry_type: WithdrawalEntryType,
    amount: int,
    currency: str,
    description: str,
) -> WithdrawalLedgerEntry:
    entry = WithdrawalLedgerEntry(
        withdrawal_id=withdrawal.id,
        designer_profile_id=withdrawal.designer_profile_id,
        entry_type=entry_type,
        amount=amount,
        currency=currency,
        description=description,
    )
    db.add(entry)
    db.flush()
    return entry


def _notify_designer(
    db: Session,
    user_id: int,
    notification_type,
    title: str,
    message: str,
    withdrawal_id: int,
    amount: int,
    currency: str,
) -> None:
    try:
        import app.services.notifications as notif_svc
        notif_svc.create_notification(
            db=db,
            recipient_id=user_id,
            notification_type=notification_type,
            title=title,
            message=message,
            entity_type="withdrawal",
            entity_id=withdrawal_id,
            meta_data={"withdrawal_id": withdrawal_id, "amount": amount, "currency": currency},
        )
    except Exception:
        logger.exception("Failed to create withdrawal notification for user=%d", user_id)


# ── Public API ────────────────────────────────────────────────────────────────

def calculate_wallet_balance(db: Session, designer_profile_id: int) -> WalletOut:
    """Derive wallet balances from DesignerEarning records."""
    return WalletOut(
        pending_balance=_sum_earnings(db, designer_profile_id, EarningStatus.PENDING),
        available_balance=_sum_earnings(db, designer_profile_id, EarningStatus.AVAILABLE),
        processing_balance=_sum_earnings(db, designer_profile_id, EarningStatus.WITHDRAWAL_PENDING),
        withdrawn_balance=_sum_earnings(db, designer_profile_id, EarningStatus.PAID),
        currency=settings.WITHDRAWAL_CURRENCY,
    )


def get_wallet(db: Session, user: User) -> WalletOut:
    profile = _get_designer_profile(db, user)
    return calculate_wallet_balance(db, profile.id)


def create_withdrawal(db: Session, user: User, payload: WithdrawalCreate) -> Withdrawal:
    """
    Atomically create a withdrawal request.

    Flow:
    1. Resolve designer profile.
    2. If idempotency_key provided, check for duplicate.
    3. Validate amount >= MINIMUM_WITHDRAWAL_AMOUNT.
    4. Validate currency.
    5. Lock and sum AVAILABLE earnings.
    6. Validate amount <= available_balance.
    7. Reserve AVAILABLE earnings -> WITHDRAWAL_PENDING (with row-level update).
    8. Create Withdrawal record.
    9. Append ledger entry.
    10. Notify designer.
    """
    profile = _get_designer_profile(db, user)

    # Idempotency check
    if payload.idempotency_key:
        existing = db.query(Withdrawal).filter(
            Withdrawal.idempotency_key == payload.idempotency_key,
            Withdrawal.designer_profile_id == profile.id,
        ).first()
        if existing:
            return existing

    # Validate minimum
    if payload.amount < settings.MINIMUM_WITHDRAWAL_AMOUNT:
        raise ValueError(
            f"Minimum withdrawal amount is {settings.MINIMUM_WITHDRAWAL_AMOUNT} "
            f"{settings.WITHDRAWAL_CURRENCY} (in minor units)"
        )

    # Validate currency (currently INR-only)
    currency = settings.WITHDRAWAL_CURRENCY

    # Lock AVAILABLE earnings for this designer and compute total
    available_earnings = (
        db.query(DesignerEarning)
        .filter(
            DesignerEarning.designer_id == profile.id,
            DesignerEarning.status == EarningStatus.AVAILABLE,
        )
        .with_for_update()  # row-level lock to prevent concurrent over-withdrawal
        .all()
    )
    available_balance = sum(e.net_amount for e in available_earnings)

    if payload.amount > available_balance:
        raise ValueError(
            f"Insufficient available balance. Requested: {payload.amount}, "
            f"Available: {available_balance} {currency}"
        )

    # Reserve earnings greedily (largest-first to minimise row count)
    available_earnings.sort(key=lambda e: e.net_amount, reverse=True)
    to_reserve: list[DesignerEarning] = []
    running_total = 0
    for earning in available_earnings:
        if running_total >= payload.amount:
            break
        to_reserve.append(earning)
        running_total += earning.net_amount

    for earning in to_reserve:
        earning.status = EarningStatus.WITHDRAWAL_PENDING
        db.add(earning)

    db.flush()

    # Create withdrawal record
    withdrawal = Withdrawal(
        designer_profile_id=profile.id,
        user_id=user.id,
        amount=payload.amount,
        currency=currency,
        status=WithdrawalStatus.PENDING,
        idempotency_key=payload.idempotency_key,
        requested_at=datetime.now(timezone.utc),
    )
    db.add(withdrawal)
    db.flush()

    # Append ledger entry
    _append_ledger(
        db, withdrawal, WithdrawalEntryType.WITHDRAWAL_RESERVED,
        payload.amount, currency,
        f"Withdrawal requested by designer (profile_id={profile.id})",
    )

    db.commit()
    db.refresh(withdrawal)

    # Notify (after commit, non-blocking)
    try:
        from app.models.notification import NotificationType
        _notify_designer(
            db=db,
            user_id=user.id,
            notification_type=NotificationType.WITHDRAWAL_REQUESTED,
            title="Withdrawal requested",
            message=f"Your withdrawal request of {payload.amount} {currency} has been submitted.",
            withdrawal_id=withdrawal.id,
            amount=payload.amount,
            currency=currency,
        )
        db.commit()
    except Exception:
        logger.exception("Failed to notify on withdrawal creation withdrawal_id=%d", withdrawal.id)

    return withdrawal


def list_withdrawals(
    db: Session,
    designer_profile_id: int,
    page: int = 1,
    limit: int = 20,
) -> WithdrawalListResponse:
    limit = min(limit, 100)
    offset = (max(page, 1) - 1) * limit

    total = db.query(func.count(Withdrawal.id)).filter(
        Withdrawal.designer_profile_id == designer_profile_id,
    ).scalar() or 0

    withdrawals = (
        db.query(Withdrawal)
        .filter(Withdrawal.designer_profile_id == designer_profile_id)
        .order_by(Withdrawal.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    return WithdrawalListResponse(
        withdrawals=[WithdrawalOut.model_validate(w) for w in withdrawals],
        total=total,
    )


def list_all_withdrawals(db: Session, page: int = 1, limit: int = 20) -> WithdrawalListResponse:
    limit = min(limit, 100)
    offset = (max(page, 1) - 1) * limit

    total = db.query(func.count(Withdrawal.id)).scalar() or 0
    withdrawals = (
        db.query(Withdrawal)
        .order_by(Withdrawal.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    return WithdrawalListResponse(
        withdrawals=[WithdrawalOut.model_validate(w) for w in withdrawals],
        total=total,
    )


def get_withdrawal(db: Session, withdrawal_id: int) -> Withdrawal:
    w = db.query(Withdrawal).filter(Withdrawal.id == withdrawal_id).first()
    if not w:
        raise ValueError(f"Withdrawal {withdrawal_id} not found")
    return w


def _assert_valid_transition(withdrawal: Withdrawal, target: WithdrawalStatus) -> None:
    current = withdrawal.status.value if hasattr(withdrawal.status, "value") else withdrawal.status
    allowed = VALID_WITHDRAWAL_TRANSITIONS.get(current, [])
    target_val = target.value if hasattr(target, "value") else target
    if target_val not in allowed:
        raise ValueError(
            f"Invalid transition: {current} -> {target_val}. "
            f"Allowed: {allowed}"
        )


def process_withdrawal(
    db: Session, withdrawal: Withdrawal, req: WithdrawalProcessRequest
) -> Withdrawal:
    """Admin: move withdrawal to PROCESSING and optionally set provider reference."""
    _assert_valid_transition(withdrawal, WithdrawalStatus.PROCESSING)

    withdrawal.status = WithdrawalStatus.PROCESSING
    withdrawal.processing_at = datetime.now(timezone.utc)
    if req.payout_reference:
        withdrawal.payout_reference = req.payout_reference
    db.add(withdrawal)
    db.flush()

    _append_ledger(
        db, withdrawal, WithdrawalEntryType.WITHDRAWAL_PROCESSING,
        withdrawal.amount, withdrawal.currency,
        "Payout initiated with provider",
    )
    db.commit()
    db.refresh(withdrawal)

    try:
        from app.models.notification import NotificationType
        _notify_designer(
            db=db, user_id=withdrawal.user_id,
            notification_type=NotificationType.WITHDRAWAL_PROCESSING,
            title="Withdrawal processing",
            message=f"Your withdrawal of {withdrawal.amount} {withdrawal.currency} is being processed.",
            withdrawal_id=withdrawal.id, amount=withdrawal.amount, currency=withdrawal.currency,
        )
        db.commit()
    except Exception:
        pass

    return withdrawal


def complete_withdrawal(
    db: Session, withdrawal: Withdrawal, req: WithdrawalCompleteRequest
) -> Withdrawal:
    """Admin: mark withdrawal COMPLETED and transition reserved earnings to PAID."""
    _assert_valid_transition(withdrawal, WithdrawalStatus.COMPLETED)

    withdrawal.status = WithdrawalStatus.COMPLETED
    withdrawal.completed_at = datetime.now(timezone.utc)
    if req.payout_reference:
        withdrawal.payout_reference = req.payout_reference
    db.add(withdrawal)

    # Advance WITHDRAWAL_PENDING earnings to PAID (idempotent check)
    earnings = db.query(DesignerEarning).filter(
        DesignerEarning.designer_id == withdrawal.designer_profile_id,
        DesignerEarning.status == EarningStatus.WITHDRAWAL_PENDING,
    ).all()
    for e in earnings:
        e.status = EarningStatus.PAID
        db.add(e)

    db.flush()

    _append_ledger(
        db, withdrawal, WithdrawalEntryType.WITHDRAWAL_COMPLETED,
        withdrawal.amount, withdrawal.currency,
        f"Payout confirmed. Reference: {withdrawal.payout_reference or 'N/A'}",
    )
    db.commit()
    db.refresh(withdrawal)

    try:
        from app.models.notification import NotificationType
        _notify_designer(
            db=db, user_id=withdrawal.user_id,
            notification_type=NotificationType.WITHDRAWAL_COMPLETED,
            title="Withdrawal completed",
            message=f"Your withdrawal of {withdrawal.amount} {withdrawal.currency} has been paid.",
            withdrawal_id=withdrawal.id, amount=withdrawal.amount, currency=withdrawal.currency,
        )
        db.commit()
    except Exception:
        pass

    return withdrawal


def fail_withdrawal(
    db: Session, withdrawal: Withdrawal, req: WithdrawalFailRequest
) -> Withdrawal:
    """Admin: mark withdrawal FAILED and release reserved earnings back to AVAILABLE."""
    _assert_valid_transition(withdrawal, WithdrawalStatus.FAILED)

    withdrawal.status = WithdrawalStatus.FAILED
    withdrawal.failure_reason = req.failure_reason
    withdrawal.failed_at = datetime.now(timezone.utc)
    if req.payout_reference:
        withdrawal.payout_reference = req.payout_reference
    db.add(withdrawal)

    # Release WITHDRAWAL_PENDING earnings back to AVAILABLE
    earnings = db.query(DesignerEarning).filter(
        DesignerEarning.designer_id == withdrawal.designer_profile_id,
        DesignerEarning.status == EarningStatus.WITHDRAWAL_PENDING,
    ).all()
    for e in earnings:
        e.status = EarningStatus.AVAILABLE
        db.add(e)

    db.flush()

    _append_ledger(
        db, withdrawal, WithdrawalEntryType.WITHDRAWAL_RELEASED,
        withdrawal.amount, withdrawal.currency,
        f"Payout failed: {req.failure_reason}. Funds released back to available balance.",
    )
    db.commit()
    db.refresh(withdrawal)

    try:
        from app.models.notification import NotificationType
        _notify_designer(
            db=db, user_id=withdrawal.user_id,
            notification_type=NotificationType.WITHDRAWAL_FAILED,
            title="Withdrawal failed",
            message=f"Your withdrawal of {withdrawal.amount} {withdrawal.currency} failed: {req.failure_reason}",
            withdrawal_id=withdrawal.id, amount=withdrawal.amount, currency=withdrawal.currency,
        )
        db.commit()
    except Exception:
        pass

    return withdrawal


def cancel_withdrawal(db: Session, withdrawal: Withdrawal, user: User) -> Withdrawal:
    """
    Cancel a PENDING withdrawal.
    Designer can cancel their own; admin can cancel any.
    Cannot cancel once PROCESSING or beyond.
    """
    _assert_valid_transition(withdrawal, WithdrawalStatus.CANCELLED)

    # Authorization: must be owner or admin
    is_admin = user.role == UserRole.ADMIN
    if not is_admin and withdrawal.user_id != user.id:
        raise PermissionError("You can only cancel your own withdrawals")

    withdrawal.status = WithdrawalStatus.CANCELLED
    db.add(withdrawal)

    # Release WITHDRAWAL_PENDING earnings back to AVAILABLE
    earnings = db.query(DesignerEarning).filter(
        DesignerEarning.designer_id == withdrawal.designer_profile_id,
        DesignerEarning.status == EarningStatus.WITHDRAWAL_PENDING,
    ).all()
    for e in earnings:
        e.status = EarningStatus.AVAILABLE
        db.add(e)

    db.flush()

    _append_ledger(
        db, withdrawal, WithdrawalEntryType.WITHDRAWAL_RELEASED,
        withdrawal.amount, withdrawal.currency,
        "Withdrawal cancelled. Funds released back to available balance.",
    )
    db.commit()
    db.refresh(withdrawal)

    try:
        from app.models.notification import NotificationType
        _notify_designer(
            db=db, user_id=withdrawal.user_id,
            notification_type=NotificationType.WITHDRAWAL_CANCELLED,
            title="Withdrawal cancelled",
            message=f"Your withdrawal of {withdrawal.amount} {withdrawal.currency} has been cancelled.",
            withdrawal_id=withdrawal.id, amount=withdrawal.amount, currency=withdrawal.currency,
        )
        db.commit()
    except Exception:
        pass

    return withdrawal
