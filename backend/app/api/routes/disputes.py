"""
Dispute routes.

REST:
    POST   /projects/{project_id}/disputes          — create dispute
    GET    /projects/{project_id}/disputes          — list project disputes
    GET    /disputes/{dispute_id}                   — get dispute detail
    PATCH  /disputes/{dispute_id}/status            — change status (admin or cancel)
    POST   /disputes/{dispute_id}/responses         — add response
    GET    /disputes/{dispute_id}/responses         — list responses
    POST   /disputes/{dispute_id}/resolve           — resolve (admin only)
    POST   /disputes/{dispute_id}/reject            — reject (admin only)
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, require_admin_role
from app.db.session import get_db
from app.models.user import User, UserRole
from app.schemas.dispute import (
    DisputeCreate, DisputeOut, DisputeListResponse,
    DisputeStatusUpdate, DisputeResolutionRequest,
    DisputeResponseCreate, DisputeResponseOut, DisputeResponseListResponse,
)
from app.services import disputes as dispute_svc
from app.models.dispute import DisputeStatus

router = APIRouter(tags=["disputes"])


def _get_dispute_or_404(dispute_id: int, db: Session):
    try:
        return dispute_svc.get_dispute(db, dispute_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


def _assert_participant_or_admin(dispute, user: User):
    is_admin = user.role == UserRole.ADMIN
    if not is_admin and user.id not in (dispute.raised_by_user_id, dispute.against_user_id):
        raise HTTPException(status_code=403, detail="You are not authorized to access this dispute")


# ── Create dispute ────────────────────────────────────────────────────────────

@router.post("/projects/{project_id}/disputes", response_model=DisputeOut, status_code=201)
def create_dispute(
    project_id: int,
    payload: DisputeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        dispute = dispute_svc.create_dispute(db, project_id, current_user.id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return dispute


# ── List project disputes ─────────────────────────────────────────────────────

@router.get("/projects/{project_id}/disputes", response_model=DisputeListResponse)
def list_project_disputes(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Verify project participant or admin
    try:
        project = dispute_svc.get_project_or_404(db, project_id)
        if current_user.role != UserRole.ADMIN:
            dispute_svc.check_project_participant(db, project, current_user.id)
    except ValueError as exc:
        raise HTTPException(status_code=403, detail=str(exc))

    return dispute_svc.list_project_disputes(db, project_id)


# ── Get dispute detail ────────────────────────────────────────────────────────

@router.get("/disputes/{dispute_id}", response_model=DisputeOut)
def get_dispute(
    dispute_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    dispute = _get_dispute_or_404(dispute_id, db)
    _assert_participant_or_admin(dispute, current_user)
    return dispute


# ── Change status ─────────────────────────────────────────────────────────────

@router.patch("/disputes/{dispute_id}/status", response_model=DisputeOut)
def change_dispute_status(
    dispute_id: int,
    payload: DisputeStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    dispute = _get_dispute_or_404(dispute_id, db)
    _assert_participant_or_admin(dispute, current_user)

    is_admin = current_user.role == UserRole.ADMIN
    try:
        dispute = dispute_svc.change_status(
            db, dispute, payload.status, current_user.id,
            note=payload.note, is_admin=is_admin,
        )
    except (ValueError, PermissionError) as exc:
        code = 403 if isinstance(exc, PermissionError) else 400
        raise HTTPException(status_code=code, detail=str(exc))
    return dispute


# ── Responses ─────────────────────────────────────────────────────────────────

@router.post("/disputes/{dispute_id}/responses", response_model=DisputeResponseOut, status_code=201)
def add_response(
    dispute_id: int,
    payload: DisputeResponseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    dispute = _get_dispute_or_404(dispute_id, db)
    is_admin = current_user.role == UserRole.ADMIN
    try:
        response = dispute_svc.add_response(db, dispute, current_user.id, payload, is_admin=is_admin)
    except (ValueError, PermissionError) as exc:
        code = 403 if isinstance(exc, PermissionError) else 400
        raise HTTPException(status_code=code, detail=str(exc))
    return response


@router.get("/disputes/{dispute_id}/responses", response_model=DisputeResponseListResponse)
def list_responses(
    dispute_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    dispute = _get_dispute_or_404(dispute_id, db)
    _assert_participant_or_admin(dispute, current_user)
    return dispute_svc.list_responses(db, dispute_id)


# ── Admin resolution ──────────────────────────────────────────────────────────

@router.post("/disputes/{dispute_id}/resolve", response_model=DisputeOut)
def resolve_dispute(
    dispute_id: int,
    payload: DisputeResolutionRequest,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin_role),  # admin-only
    current_user: User = Depends(get_current_user),
):
    dispute = _get_dispute_or_404(dispute_id, db)
    try:
        dispute = dispute_svc.resolve_dispute(db, dispute, current_user.id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return dispute


@router.post("/disputes/{dispute_id}/reject", response_model=DisputeOut)
def reject_dispute(
    dispute_id: int,
    payload: DisputeStatusUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin_role),
    current_user: User = Depends(get_current_user),
):
    dispute = _get_dispute_or_404(dispute_id, db)
    try:
        dispute = dispute_svc.reject_dispute(db, dispute, current_user.id, payload.note or "Rejected by admin")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return dispute
