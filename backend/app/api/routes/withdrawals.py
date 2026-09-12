"""
Withdrawal routes.

Designer endpoints:
    GET  /designer/wallet                              — wallet summary
    POST /designer/withdrawals                         — create withdrawal
    GET  /designer/withdrawals                         — list own withdrawals
    GET  /designer/withdrawals/{id}                    — get withdrawal detail
    POST /designer/withdrawals/{id}/cancel             — cancel own withdrawal

Admin endpoints:
    GET  /admin/withdrawals                            — list all withdrawals
    GET  /admin/withdrawals/{id}                       — inspect any withdrawal
    POST /admin/withdrawals/{id}/process               — move to PROCESSING
    POST /admin/withdrawals/{id}/complete              — mark COMPLETED
    POST /admin/withdrawals/{id}/fail                  — mark FAILED
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, require_admin_role, require_designer_role
from app.db.session import get_db
from app.models.user import User
from app.schemas.withdrawal import (
    WalletOut, WithdrawalCreate, WithdrawalOut, WithdrawalListResponse,
    WithdrawalProcessRequest, WithdrawalCompleteRequest, WithdrawalFailRequest,
)
from app.services import withdrawals as w_svc

router = APIRouter(tags=["withdrawals"])


def _get_withdrawal_or_404(withdrawal_id: int, db: Session):
    try:
        return w_svc.get_withdrawal(db, withdrawal_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


# ── Designer routes ───────────────────────────────────────────────────────────

@router.get("/designer/wallet", response_model=WalletOut)
def get_wallet(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_designer_role),
):
    try:
        return w_svc.get_wallet(db, current_user)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.post("/designer/withdrawals", response_model=WithdrawalOut, status_code=201)
def create_withdrawal(
    payload: WithdrawalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_designer_role),
):
    try:
        return w_svc.create_withdrawal(db, current_user, payload)
    except ValueError as exc:
        msg = str(exc)
        # Profile not found -> 404, everything else -> 400
        code = 404 if "profile not found" in msg.lower() else 400
        raise HTTPException(status_code=code, detail=msg)


@router.get("/designer/withdrawals", response_model=WithdrawalListResponse)
def list_my_withdrawals(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_designer_role),
):
    try:
        profile = w_svc._get_designer_profile(db, current_user)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    return w_svc.list_withdrawals(db, profile.id, page=page, limit=limit)


@router.get("/designer/withdrawals/{withdrawal_id}", response_model=WithdrawalOut)
def get_my_withdrawal(
    withdrawal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_designer_role),
):
    withdrawal = _get_withdrawal_or_404(withdrawal_id, db)
    # IDOR prevention: only owner can access
    if withdrawal.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    return withdrawal


@router.post("/designer/withdrawals/{withdrawal_id}/cancel", response_model=WithdrawalOut)
def cancel_withdrawal(
    withdrawal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_designer_role),
):
    withdrawal = _get_withdrawal_or_404(withdrawal_id, db)
    if withdrawal.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    try:
        return w_svc.cancel_withdrawal(db, withdrawal, current_user)
    except (ValueError, PermissionError) as exc:
        code = 403 if isinstance(exc, PermissionError) else 400
        raise HTTPException(status_code=code, detail=str(exc))


# ── Admin routes ──────────────────────────────────────────────────────────────

@router.get("/admin/withdrawals", response_model=WithdrawalListResponse)
def admin_list_withdrawals(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    _: User = Depends(require_admin_role),
):
    return w_svc.list_all_withdrawals(db, page=page, limit=limit)


@router.get("/admin/withdrawals/{withdrawal_id}", response_model=WithdrawalOut)
def admin_get_withdrawal(
    withdrawal_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin_role),
):
    return _get_withdrawal_or_404(withdrawal_id, db)


@router.post("/admin/withdrawals/{withdrawal_id}/process", response_model=WithdrawalOut)
def admin_process_withdrawal(
    withdrawal_id: int,
    req: WithdrawalProcessRequest,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin_role),
):
    withdrawal = _get_withdrawal_or_404(withdrawal_id, db)
    try:
        return w_svc.process_withdrawal(db, withdrawal, req)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/admin/withdrawals/{withdrawal_id}/complete", response_model=WithdrawalOut)
def admin_complete_withdrawal(
    withdrawal_id: int,
    req: WithdrawalCompleteRequest,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin_role),
):
    withdrawal = _get_withdrawal_or_404(withdrawal_id, db)
    try:
        return w_svc.complete_withdrawal(db, withdrawal, req)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/admin/withdrawals/{withdrawal_id}/fail", response_model=WithdrawalOut)
def admin_fail_withdrawal(
    withdrawal_id: int,
    req: WithdrawalFailRequest,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin_role),
):
    withdrawal = _get_withdrawal_or_404(withdrawal_id, db)
    try:
        return w_svc.fail_withdrawal(db, withdrawal, req)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
