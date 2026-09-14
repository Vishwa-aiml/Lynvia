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
from google.cloud.firestore import Client as FirestoreClient

from app.api.dependencies import get_current_user, require_admin_role, require_designer_role
from app.db.firebase import get_db
from app.models.user import User
from app.schemas.withdrawal import (
    WalletOut, WithdrawalCreate, WithdrawalOut, WithdrawalListResponse,
    WithdrawalProcessRequest, WithdrawalCompleteRequest, WithdrawalFailRequest,
)
from app.services import withdrawals as w_svc

router = APIRouter(tags=["withdrawals"])

@router.get("/designer/wallet", response_model=WalletOut)
def get_wallet(
    db: FirestoreClient = Depends(get_db),
    current_user: User = Depends(require_designer_role),
):
    try:
        # Assuming current_user.id is the designerProfileId for simplicity, or look it up
        designer_docs = db.collection("designerProfiles").where("userId", "==", current_user.id).limit(1).get()
        if not designer_docs:
            raise ValueError("Designer profile not found")
        designer_profile_id = designer_docs[0].id
        return w_svc.get_wallet_balance(db, designer_profile_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))

@router.post("/designer/withdrawals", response_model=WithdrawalOut, status_code=201)
def create_withdrawal(
    payload: WithdrawalCreate,
    db: FirestoreClient = Depends(get_db),
    current_user: User = Depends(require_designer_role),
):
    try:
        designer_docs = db.collection("designerProfiles").where("userId", "==", current_user.id).limit(1).get()
        if not designer_docs:
            raise ValueError("Designer profile not found")
        designer_profile_id = designer_docs[0].id
        return w_svc.request_withdrawal(db, current_user.id, designer_profile_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

@router.post("/admin/withdrawals/{withdrawal_id}/process", response_model=WithdrawalOut)
def admin_process_withdrawal(
    withdrawal_id: str,
    req: WithdrawalProcessRequest,
    db: FirestoreClient = Depends(get_db),
    _: User = Depends(require_admin_role),
):
    try:
        return w_svc.process_withdrawal(db, withdrawal_id, req.payoutReference)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

@router.post("/admin/withdrawals/{withdrawal_id}/complete", response_model=WithdrawalOut)
def admin_complete_withdrawal(
    withdrawal_id: str,
    req: WithdrawalCompleteRequest,
    db: FirestoreClient = Depends(get_db),
    _: User = Depends(require_admin_role),
):
    try:
        return w_svc.complete_withdrawal(db, withdrawal_id, req.payoutReference)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

@router.post("/admin/withdrawals/{withdrawal_id}/fail", response_model=WithdrawalOut)
def admin_fail_withdrawal(
    withdrawal_id: str,
    req: WithdrawalFailRequest,
    db: FirestoreClient = Depends(get_db),
    _: User = Depends(require_admin_role),
):
    try:
        return w_svc.fail_withdrawal(db, withdrawal_id, req.failureReason)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
