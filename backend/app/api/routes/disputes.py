from fastapi import APIRouter, Depends, HTTPException, status
from google.cloud.firestore import Client as FirestoreClient

from app.api.dependencies import get_current_user, require_admin_role
from app.db.firebase import get_db
from app.models.user import User, UserRole
from app.schemas.dispute import (
    DisputeCreate, DisputeOut, DisputeListResponse,
    DisputeStatusUpdate, DisputeResolutionRequest,
    DisputeResponseCreate, DisputeResponseOut, DisputeResponseListResponse,
)
from app.services import disputes as dispute_svc

router = APIRouter(tags=["disputes"])

def _assert_participant_or_admin(dispute: DisputeOut, user: User):
    is_admin = user.role == UserRole.ADMIN
    dispute_svc.check_dispute_access(dispute, user.id, is_admin)

@router.post("/projects/{project_id}/disputes", response_model=DisputeOut, status_code=status.HTTP_201_CREATED)
def create_dispute(
    project_id: str,
    payload: DisputeCreate,
    db: FirestoreClient = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return dispute_svc.create_dispute(db, project_id, current_user.id, payload)


@router.get("/projects/{project_id}/disputes", response_model=DisputeListResponse)
def list_project_disputes(
    project_id: str,
    db: FirestoreClient = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Verify project participation before returning disputes
    project = dispute_svc.get_project_or_404(db, project_id)
    if current_user.role != UserRole.ADMIN:
        dispute_svc.check_project_participant(project, current_user.id)
    return dispute_svc.list_project_disputes(db, project_id)


@router.get("/disputes/{dispute_id}", response_model=DisputeOut)
def get_dispute(
    dispute_id: str,
    db: FirestoreClient = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    dispute = dispute_svc.get_dispute(db, dispute_id)
    _assert_participant_or_admin(dispute, current_user)
    return dispute


@router.patch("/disputes/{dispute_id}/status", response_model=DisputeOut)
def change_dispute_status(
    dispute_id: str,
    payload: DisputeStatusUpdate,
    db: FirestoreClient = Depends(get_db),
    admin_user: User = Depends(require_admin_role)
):
    return dispute_svc.change_status(db, dispute_id, admin_user.id, payload)


@router.post("/disputes/{dispute_id}/responses", response_model=DisputeResponseOut, status_code=status.HTTP_201_CREATED)
def add_dispute_response(
    dispute_id: str,
    payload: DisputeResponseCreate,
    db: FirestoreClient = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return dispute_svc.add_response(db, dispute_id, current_user.id, payload)


@router.get("/disputes/{dispute_id}/responses", response_model=DisputeResponseListResponse)
def list_dispute_responses(
    dispute_id: str,
    db: FirestoreClient = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    dispute = dispute_svc.get_dispute(db, dispute_id)
    _assert_participant_or_admin(dispute, current_user)
    return dispute_svc.list_responses(db, dispute_id)


@router.post("/disputes/{dispute_id}/resolve", response_model=DisputeOut)
def resolve_dispute(
    dispute_id: str,
    payload: DisputeResolutionRequest,
    db: FirestoreClient = Depends(get_db),
    admin_user: User = Depends(require_admin_role)
):
    return dispute_svc.resolve_dispute(db, dispute_id, admin_user.id, payload)
