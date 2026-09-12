"""
Dispute service — business logic for the Lynvia dispute and resolution system.

Financial resolution goes through the existing payment/ledger architecture:
  - FULL_REFUND_TO_CLIENT    → Payment -> REFUNDED, reversal ledger entries
  - PARTIAL_REFUND_TO_CLIENT → Payment -> PARTIALLY_REFUNDED, partial reversal ledger entries
  - RELEASE_TO_DESIGNER      → DesignerEarning -> AVAILABLE (finalise held earnings)
  - NO_REFUND                → Record decision; payment state unchanged
  - MUTUAL_RESOLUTION        → Record decision; no financial adjustment
"""
import json
import logging
from datetime import datetime, timezone
from typing import Optional, List

from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.dispute import (
    Dispute, DisputeResponse, DisputeReason, DisputeStatus,
    ResolutionType, VALID_TRANSITIONS,
)
from app.models.project import Project
from app.models.profile import DesignerProfile
from app.models.payment import (
    Payment, PaymentStatus, Transaction, TransactionType,
    TransactionStatus, LedgerEntry, EntryDirection,
    DesignerEarning, EarningStatus,
)
from app.models.workspace import ProjectEvent, ProjectEventType
from app.models.file import FileMetadata
from app.models.notification import NotificationType
from app.models.user import User, UserRole
from app.schemas.dispute import (
    DisputeCreate, DisputeResolutionRequest, DisputeResponseCreate,
    DisputeOut, DisputeResponseOut, DisputeListResponse, DisputeResponseListResponse,
)
import app.services.notifications as notif_svc

logger = logging.getLogger(__name__)


# ── Authorization helpers ────────────────────────────────────────────────────

def _get_designer_user_id(db: Session, designer_profile_id: int) -> Optional[int]:
    profile = db.query(DesignerProfile).filter(DesignerProfile.id == designer_profile_id).first()
    return profile.user_id if profile else None


def get_project_or_404(db: Session, project_id: int) -> Project:
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise ValueError(f"Project {project_id} not found")
    return project


def check_project_participant(db: Session, project: Project, user_id: int) -> str:
    """
    Verify user is the client or assigned designer.
    Returns 'client' or 'designer'. Raises ValueError if not a participant.
    """
    if project.client_id == user_id:
        return "client"
    if project.assigned_designer_id is not None:
        d_uid = _get_designer_user_id(db, project.assigned_designer_id)
        if d_uid == user_id:
            return "designer"
    raise ValueError("You are not a participant in this project")


def get_opposing_user_id(db: Session, project: Project, raiser_id: int) -> int:
    """Return the other party's user ID."""
    if project.client_id == raiser_id:
        # Raiser is client → opposing is designer
        d_uid = _get_designer_user_id(db, project.assigned_designer_id)
        if not d_uid:
            raise ValueError("No assigned designer to raise dispute against")
        return d_uid
    # Raiser is designer → opposing is client
    return project.client_id


# ── Project event helper ──────────────────────────────────────────────────────

def _log_event(db: Session, project_id: int, author_id: int, event_type: ProjectEventType, content: str):
    event = ProjectEvent(
        project_id=project_id,
        author_id=author_id,
        event_type=event_type,
        content=content,
    )
    db.add(event)
    db.flush()


# ── Core dispute operations ───────────────────────────────────────────────────

def create_dispute(db: Session, project_id: int, raiser_id: int, payload: DisputeCreate) -> Dispute:
    """
    Create a dispute. Only the project client or assigned designer may raise one.
    Prevents duplicate OPEN/UNDER_REVIEW disputes on the same project.
    """
    project = get_project_or_404(db, project_id)
    check_project_participant(db, project, raiser_id)  # raises if not participant

    opposing_id = get_opposing_user_id(db, project, raiser_id)

    # Sanity: cannot raise dispute against oneself (shouldn't happen but be explicit)
    if opposing_id == raiser_id:
        raise ValueError("Cannot raise a dispute against yourself")

    # Validate payment_id belongs to this project
    if payload.payment_id is not None:
        payment = db.query(Payment).filter(
            Payment.id == payload.payment_id,
            Payment.project_id == project_id,
        ).first()
        if not payment:
            raise ValueError("Payment not found or does not belong to this project")

    # Prevent duplicate active disputes
    active = db.query(Dispute).filter(
        Dispute.project_id == project_id,
        Dispute.status.in_([DisputeStatus.OPEN, DisputeStatus.UNDER_REVIEW,
                             DisputeStatus.WAITING_FOR_CLIENT, DisputeStatus.WAITING_FOR_DESIGNER]),
    ).first()
    if active:
        raise ValueError(f"An active dispute (#{active.id}) already exists for this project. "
                         "Resolve or cancel it before opening a new one.")

    dispute = Dispute(
        project_id=project_id,
        payment_id=payload.payment_id,
        raised_by_user_id=raiser_id,
        against_user_id=opposing_id,
        reason=payload.reason,
        description=payload.description,
        status=DisputeStatus.OPEN,
    )
    db.add(dispute)
    db.flush()

    # Project event
    _log_event(db, project_id, raiser_id, ProjectEventType.DISPUTE_CREATED,
               json.dumps({"dispute_id": dispute.id, "reason": payload.reason.value}))

    # Notify opposing party
    try:
        notif_svc.create_notification(
            db=db,
            recipient_id=opposing_id,
            actor_id=raiser_id,
            notification_type=NotificationType.DISPUTE_CREATED,
            title="Dispute raised",
            message="A dispute has been raised against you for this project.",
            entity_type="dispute",
            entity_id=dispute.id,
            meta_data={"project_id": project_id, "dispute_id": dispute.id},
        )
    except Exception:
        logger.warning("Failed to send DISPUTE_CREATED notification", exc_info=True)

    db.commit()
    db.refresh(dispute)
    return dispute


def get_dispute(db: Session, dispute_id: int) -> Dispute:
    d = db.query(Dispute).filter(Dispute.id == dispute_id).first()
    if not d:
        raise ValueError(f"Dispute {dispute_id} not found")
    return d


def check_dispute_access(db: Session, dispute: Dispute, user_id: int, is_admin: bool = False):
    """Allow access only to the two parties or an admin. Raises ValueError otherwise."""
    if is_admin:
        return
    if user_id not in (dispute.raised_by_user_id, dispute.against_user_id):
        raise ValueError("You are not authorized to access this dispute")


def list_project_disputes(db: Session, project_id: int) -> DisputeListResponse:
    disputes = db.query(Dispute).filter(Dispute.project_id == project_id).order_by(Dispute.created_at.desc()).all()
    return DisputeListResponse(
        disputes=[DisputeOut.model_validate(d) for d in disputes],
        total=len(disputes),
    )


# ── Status transitions ────────────────────────────────────────────────────────

def change_status(
    db: Session,
    dispute: Dispute,
    new_status: DisputeStatus,
    changed_by_id: int,
    note: Optional[str] = None,
    is_admin: bool = False,
) -> Dispute:
    """
    Apply a status transition. Admin-only transitions are enforced.
    """
    allowed = VALID_TRANSITIONS.get(dispute.status, set())
    if new_status not in allowed:
        raise ValueError(
            f"Cannot transition dispute from '{dispute.status.value}' to '{new_status.value}'"
        )

    # Non-admins may only cancel their own dispute (if OPEN)
    if not is_admin:
        if new_status == DisputeStatus.CANCELLED:
            if dispute.raised_by_user_id != changed_by_id:
                raise PermissionError("Only the dispute creator can cancel it")
        else:
            raise PermissionError("Only admins can change dispute status")

    dispute.status = new_status
    db.add(dispute)

    _log_event(db, dispute.project_id, changed_by_id, ProjectEventType.DISPUTE_STATUS_CHANGED,
               json.dumps({"dispute_id": dispute.id, "new_status": new_status.value, "note": note}))

    # Notify both parties on any admin-driven status change
    recipients = {dispute.raised_by_user_id, dispute.against_user_id} - {changed_by_id}
    for recipient_id in recipients:
        try:
            notif_svc.create_notification(
                db=db,
                recipient_id=recipient_id,
                actor_id=changed_by_id,
                notification_type=NotificationType.DISPUTE_STATUS_CHANGED,
                title="Dispute status updated",
                message=f"Your dispute status has changed to '{new_status.value}'.",
                entity_type="dispute",
                entity_id=dispute.id,
                meta_data={"project_id": dispute.project_id, "dispute_id": dispute.id, "new_status": new_status.value},
            )
        except Exception:
            logger.warning("Failed to send DISPUTE_STATUS_CHANGED notification", exc_info=True)

    db.commit()
    db.refresh(dispute)
    return dispute


# ── Responses ─────────────────────────────────────────────────────────────────

def add_response(
    db: Session,
    dispute: Dispute,
    user_id: int,
    payload: DisputeResponseCreate,
    is_admin: bool = False,
) -> DisputeResponse:
    """Add a response to a dispute. Only the two parties or admin may respond."""
    if not is_admin and user_id not in (dispute.raised_by_user_id, dispute.against_user_id):
        raise PermissionError("You are not authorized to respond to this dispute")

    if dispute.status in (DisputeStatus.RESOLVED, DisputeStatus.REJECTED, DisputeStatus.CANCELLED):
        raise ValueError(f"Cannot respond to a {dispute.status.value} dispute")

    # Validate file attachments belong to the project
    attachment_meta = None
    if payload.attachment_file_ids:
        validated_files = []
        for file_id in payload.attachment_file_ids:
            fm = db.query(FileMetadata).filter(
                FileMetadata.id == file_id,
                FileMetadata.project_id == dispute.project_id,
            ).first()
            if not fm:
                raise ValueError(f"File {file_id} not found or does not belong to this project")
            validated_files.append({"id": fm.id, "filename": fm.filename, "file_type": fm.file_type})
        attachment_meta = json.dumps(validated_files)

    response = DisputeResponse(
        dispute_id=dispute.id,
        user_id=user_id,
        message=payload.message,
        attachment_meta=attachment_meta,
    )
    db.add(response)
    db.flush()

    _log_event(db, dispute.project_id, user_id, ProjectEventType.DISPUTE_RESPONSE_ADDED,
               json.dumps({"dispute_id": dispute.id, "response_id": response.id}))

    # Notify the other party
    recipients = {dispute.raised_by_user_id, dispute.against_user_id} - {user_id}
    for recipient_id in recipients:
        try:
            notif_svc.create_notification(
                db=db,
                recipient_id=recipient_id,
                actor_id=user_id,
                notification_type=NotificationType.DISPUTE_RESPONSE,
                title="New dispute response",
                message="A response has been added to your dispute.",
                entity_type="dispute",
                entity_id=dispute.id,
                meta_data={"project_id": dispute.project_id, "dispute_id": dispute.id},
            )
        except Exception:
            logger.warning("Failed to send DISPUTE_RESPONSE notification", exc_info=True)

    db.commit()
    db.refresh(response)
    return response


def list_responses(db: Session, dispute_id: int) -> DisputeResponseListResponse:
    responses = db.query(DisputeResponse).filter(
        DisputeResponse.dispute_id == dispute_id
    ).order_by(DisputeResponse.created_at.asc()).all()
    return DisputeResponseListResponse(
        responses=[DisputeResponseOut.model_validate(r) for r in responses],
        total=len(responses),
    )


# ── Resolution (admin-only) ───────────────────────────────────────────────────

def resolve_dispute(
    db: Session,
    dispute: Dispute,
    admin_id: int,
    payload: DisputeResolutionRequest,
) -> Dispute:
    """
    Admin-only. Apply a financial resolution and close the dispute.
    All financial adjustments go through the existing ledger architecture.
    """
    if dispute.status in (DisputeStatus.RESOLVED, DisputeStatus.REJECTED, DisputeStatus.CANCELLED):
        raise ValueError(f"Dispute is already {dispute.status.value}; cannot resolve again")

    _apply_financial_resolution(db, dispute, admin_id, payload)

    dispute.resolution_type = payload.resolution_type
    dispute.resolution_note = payload.resolution_note
    dispute.resolved_by_user_id = admin_id
    dispute.resolved_at = datetime.now(timezone.utc)

    if payload.resolution_type == ResolutionType.MUTUAL_RESOLUTION:
        # Record resolution amount if provided for partial refund-like mutual resolution
        if payload.resolution_amount is not None:
            dispute.resolution_amount = payload.resolution_amount
    elif payload.resolution_type == ResolutionType.PARTIAL_REFUND_TO_CLIENT:
        dispute.resolution_amount = payload.resolution_amount

    dispute.status = DisputeStatus.RESOLVED
    db.add(dispute)

    event_type = ProjectEventType.DISPUTE_RESOLVED
    _log_event(db, dispute.project_id, admin_id, event_type,
               json.dumps({
                   "dispute_id": dispute.id,
                   "resolution_type": payload.resolution_type.value,
                   "note": payload.resolution_note,
               }))

    # Notify both parties
    for recipient_id in (dispute.raised_by_user_id, dispute.against_user_id):
        try:
            notif_svc.create_notification(
                db=db,
                recipient_id=recipient_id,
                actor_id=admin_id,
                notification_type=NotificationType.DISPUTE_RESOLVED,
                title="Dispute resolved",
                message=f"Your dispute has been resolved: {payload.resolution_type.value}.",
                entity_type="dispute",
                entity_id=dispute.id,
                meta_data={"project_id": dispute.project_id, "dispute_id": dispute.id,
                           "resolution_type": payload.resolution_type.value},
            )
        except Exception:
            logger.warning("Failed to send DISPUTE_RESOLVED notification", exc_info=True)

    db.commit()
    db.refresh(dispute)
    return dispute


def reject_dispute(db: Session, dispute: Dispute, admin_id: int, note: str) -> Dispute:
    """Admin rejects the dispute without financial adjustment."""
    if dispute.status in (DisputeStatus.RESOLVED, DisputeStatus.REJECTED, DisputeStatus.CANCELLED):
        raise ValueError(f"Dispute is already {dispute.status.value}")

    dispute.status = DisputeStatus.REJECTED
    dispute.resolution_note = note
    dispute.resolved_by_user_id = admin_id
    dispute.resolved_at = datetime.now(timezone.utc)
    db.add(dispute)

    _log_event(db, dispute.project_id, admin_id, ProjectEventType.DISPUTE_REJECTED,
               json.dumps({"dispute_id": dispute.id, "note": note}))

    for recipient_id in (dispute.raised_by_user_id, dispute.against_user_id):
        try:
            notif_svc.create_notification(
                db=db,
                recipient_id=recipient_id,
                actor_id=admin_id,
                notification_type=NotificationType.DISPUTE_RESOLVED,
                title="Dispute rejected",
                message="Your dispute has been rejected by the admin.",
                entity_type="dispute",
                entity_id=dispute.id,
                meta_data={"project_id": dispute.project_id, "dispute_id": dispute.id},
            )
        except Exception:
            logger.warning("Failed to send DISPUTE_REJECTED notification", exc_info=True)

    db.commit()
    db.refresh(dispute)
    return dispute


# ── Financial resolution ──────────────────────────────────────────────────────

def _apply_financial_resolution(
    db: Session,
    dispute: Dispute,
    admin_id: int,
    payload: DisputeResolutionRequest,
) -> None:
    """
    Route to the correct financial adjustment based on resolution_type.
    All amounts are integer minor units (paise). Never float.
    """
    rt = payload.resolution_type

    if rt == ResolutionType.NO_REFUND:
        # No financial change — just record the decision
        return

    if rt == ResolutionType.MUTUAL_RESOLUTION:
        # Typically no automated financial change at MVP level
        return

    if rt == ResolutionType.RELEASE_TO_DESIGNER:
        _release_to_designer(db, dispute, admin_id)
        return

    if rt == ResolutionType.FULL_REFUND_TO_CLIENT:
        _full_refund(db, dispute, admin_id)
        return

    if rt == ResolutionType.PARTIAL_REFUND_TO_CLIENT:
        if not payload.resolution_amount or payload.resolution_amount <= 0:
            raise ValueError("resolution_amount must be positive for PARTIAL_REFUND_TO_CLIENT")
        _partial_refund(db, dispute, admin_id, payload.resolution_amount)
        return


def _get_succeeded_payment(db: Session, dispute: Dispute) -> Optional[Payment]:
    """Return the SUCCEEDED payment for the project (or the specific payment_id if set)."""
    q = db.query(Payment).filter(
        Payment.project_id == dispute.project_id,
        Payment.status.in_([PaymentStatus.SUCCEEDED, PaymentStatus.PARTIALLY_REFUNDED]),
    )
    if dispute.payment_id:
        q = q.filter(Payment.id == dispute.payment_id)
    return q.first()


def _reverse_designer_earning(db: Session, payment: Payment) -> Optional[DesignerEarning]:
    """Mark the earning REVERSED if it is still PENDING/AVAILABLE/HELD. Idempotent."""
    earning = db.query(DesignerEarning).filter(
        DesignerEarning.payment_id == payment.id,
        DesignerEarning.status.notin_([EarningStatus.REVERSED]),
    ).first()
    if earning:
        earning.status = EarningStatus.REVERSED
        db.add(earning)
        db.flush()
    return earning


def _create_refund_ledger_entries(
    db: Session,
    project_id: int,
    payment: Payment,
    refund_amount: int,
    platform_refund: int,
    designer_refund: int,
    description_suffix: str,
) -> None:
    """Append reversal/refund ledger entries. Never modifies existing entries."""
    # Refund debit from platform (money leaving the platform back to client)
    tx_refund = Transaction(
        project_id=project_id,
        payment_id=payment.id,
        type=TransactionType.REFUND,
        amount=refund_amount,
        currency=payment.currency,
        status=TransactionStatus.COMPLETED,
    )
    db.add(tx_refund)
    db.flush()

    db.add(LedgerEntry(
        project_id=project_id,
        payment_id=payment.id,
        transaction_id=tx_refund.id,
        user_id=payment.client_id,
        entry_type="CLIENT_REFUND",
        amount=refund_amount,
        currency=payment.currency,
        direction=EntryDirection.DEBIT,
        description=f"Refund to client — {description_suffix}",
    ))

    if platform_refund > 0:
        tx_rev_comm = Transaction(
            project_id=project_id,
            payment_id=payment.id,
            type=TransactionType.REVERSAL,
            amount=platform_refund,
            currency=payment.currency,
            status=TransactionStatus.COMPLETED,
        )
        db.add(tx_rev_comm)
        db.flush()
        db.add(LedgerEntry(
            project_id=project_id,
            payment_id=payment.id,
            transaction_id=tx_rev_comm.id,
            entry_type="COMMISSION_REVERSAL",
            amount=platform_refund,
            currency=payment.currency,
            direction=EntryDirection.CREDIT,
            description=f"Commission reversal — {description_suffix}",
        ))

    if designer_refund > 0:
        tx_rev_earning = Transaction(
            project_id=project_id,
            payment_id=payment.id,
            type=TransactionType.REVERSAL,
            amount=designer_refund,
            currency=payment.currency,
            status=TransactionStatus.COMPLETED,
        )
        db.add(tx_rev_earning)
        db.flush()
        db.add(LedgerEntry(
            project_id=project_id,
            payment_id=payment.id,
            transaction_id=tx_rev_earning.id,
            entry_type="DESIGNER_EARNING_REVERSAL",
            amount=designer_refund,
            currency=payment.currency,
            direction=EntryDirection.CREDIT,
            description=f"Designer earning reversal — {description_suffix}",
        ))

    db.flush()


def _full_refund(db: Session, dispute: Dispute, admin_id: int) -> None:
    payment = _get_succeeded_payment(db, dispute)
    if not payment:
        raise ValueError("No eligible payment found for refund")

    from app.core.config import settings
    commission_rate = settings.PLATFORM_COMMISSION_RATE
    platform_fee = int(round(payment.amount * commission_rate))
    designer_amount = payment.amount - platform_fee

    # Reverse designer earning (idempotent)
    _reverse_designer_earning(db, payment)

    _create_refund_ledger_entries(
        db=db,
        project_id=dispute.project_id,
        payment=payment,
        refund_amount=payment.amount,
        platform_refund=platform_fee,
        designer_refund=designer_amount,
        description_suffix=f"dispute #{dispute.id} full refund",
    )

    payment.status = PaymentStatus.REFUNDED
    db.add(payment)

    _log_event(db, dispute.project_id, admin_id, ProjectEventType.DISPUTE_PAYMENT_ADJUSTED,
               json.dumps({"dispute_id": dispute.id, "type": "full_refund", "amount": payment.amount}))
    db.flush()


def _partial_refund(db: Session, dispute: Dispute, admin_id: int, refund_amount: int) -> None:
    payment = _get_succeeded_payment(db, dispute)
    if not payment:
        raise ValueError("No eligible payment found for partial refund")

    if refund_amount > payment.amount:
        raise ValueError(
            f"Refund amount ({refund_amount}) exceeds payment amount ({payment.amount})"
        )

    from app.core.config import settings
    commission_rate = settings.PLATFORM_COMMISSION_RATE
    # Pro-rate the platform fee and designer reversal
    platform_refund = int(round(refund_amount * commission_rate))
    designer_refund = refund_amount - platform_refund

    # Reverse the designer earning proportionally (just mark REVERSED at MVP)
    _reverse_designer_earning(db, payment)

    _create_refund_ledger_entries(
        db=db,
        project_id=dispute.project_id,
        payment=payment,
        refund_amount=refund_amount,
        platform_refund=platform_refund,
        designer_refund=designer_refund,
        description_suffix=f"dispute #{dispute.id} partial refund",
    )

    payment.status = PaymentStatus.PARTIALLY_REFUNDED
    db.add(payment)

    _log_event(db, dispute.project_id, admin_id, ProjectEventType.DISPUTE_PAYMENT_ADJUSTED,
               json.dumps({"dispute_id": dispute.id, "type": "partial_refund", "amount": refund_amount}))
    db.flush()


def _release_to_designer(db: Session, dispute: Dispute, admin_id: int) -> None:
    """Finalise pending designer earnings — makes them AVAILABLE."""
    payment = _get_succeeded_payment(db, dispute)
    if not payment:
        raise ValueError("No eligible payment found to release")

    earning = db.query(DesignerEarning).filter(
        DesignerEarning.payment_id == payment.id,
        DesignerEarning.status == EarningStatus.PENDING,
    ).first()

    if not earning:
        # Already available or reversed — idempotent, log and move on
        logger.info("release_to_designer: earning already processed for payment %d", payment.id)
        return

    earning.status = EarningStatus.AVAILABLE
    earning.available_at = datetime.now(timezone.utc)
    db.add(earning)

    # Create the DESIGNER_EARNING ledger entry (held back since initial payment)
    tx_earning_release = Transaction(
        project_id=dispute.project_id,
        payment_id=payment.id,
        type=TransactionType.DESIGNER_EARNING,
        amount=earning.net_amount,
        currency=earning.currency,
        status=TransactionStatus.COMPLETED,
    )
    db.add(tx_earning_release)
    db.flush()

    db.add(LedgerEntry(
        project_id=dispute.project_id,
        payment_id=payment.id,
        transaction_id=tx_earning_release.id,
        user_id=earning.designer_id,
        entry_type="DESIGNER_EARNING_RELEASED",
        amount=earning.net_amount,
        currency=earning.currency,
        direction=EntryDirection.CREDIT,
        description=f"Designer earning released — dispute #{dispute.id}",
    ))

    _log_event(db, dispute.project_id, admin_id, ProjectEventType.DISPUTE_PAYMENT_ADJUSTED,
               json.dumps({"dispute_id": dispute.id, "type": "release_to_designer", "amount": earning.net_amount}))
    db.flush()
