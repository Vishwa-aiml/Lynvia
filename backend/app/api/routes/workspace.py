from fastapi import APIRouter, Depends, HTTPException, status
from google.cloud.firestore import Client as FirestoreClient
from typing import List

from app.db.firebase import get_db
from app.api.dependencies import get_current_user
from app.models.user import User
from app.schemas.workspace import (
    ProjectWorkspaceOut,
    MilestoneCreate, MilestoneUpdate, MilestoneOut,
    FileMetadataCreate, FileMetadataOut,
    DeliveryCreate, DeliveryOut,
    RevisionCreate, RevisionOut
)
from app.services import workspace as workspace_service

router = APIRouter()


@router.get("/", response_model=ProjectWorkspaceOut)
def get_workspace(
    project_id: str, 
    db: FirestoreClient = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """Get all workspace data for a project (Milestones, Tasks, Files, Events, Deliveries)."""
    return workspace_service.get_workspace(db, project_id, current_user.id)


# --- MILESTONES ---

@router.post("/milestones", response_model=MilestoneOut, status_code=status.HTTP_201_CREATED)
def create_milestone(
    project_id: str, 
    milestone_in: MilestoneCreate, 
    db: FirestoreClient = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    return workspace_service.create_milestone(db, project_id, current_user.id, milestone_in)


@router.put("/milestones/{milestone_id}", response_model=MilestoneOut)
def update_milestone(
    project_id: str, 
    milestone_id: str, 
    milestone_in: MilestoneUpdate, 
    db: FirestoreClient = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    return workspace_service.update_milestone(db, project_id, milestone_id, current_user.id, milestone_in)


# --- FILES ---

@router.post("/files", response_model=FileMetadataOut, status_code=status.HTTP_201_CREATED)
def add_file(
    project_id: str, 
    file_in: FileMetadataCreate, 
    db: FirestoreClient = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    return workspace_service.add_file(db, project_id, current_user.id, file_in)


# --- DELIVERIES & REVISIONS ---

@router.post("/deliveries", response_model=DeliveryOut, status_code=status.HTTP_201_CREATED)
def submit_delivery(
    project_id: str, 
    delivery_in: DeliveryCreate, 
    db: FirestoreClient = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    return workspace_service.submit_delivery(db, project_id, current_user.id, delivery_in)


@router.post("/deliveries/{delivery_id}/accept", response_model=DeliveryOut)
def accept_delivery(
    project_id: str, 
    delivery_id: str, 
    db: FirestoreClient = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    return workspace_service.accept_delivery(db, project_id, delivery_id, current_user.id)


@router.post("/deliveries/{delivery_id}/revise", response_model=RevisionOut, status_code=status.HTTP_201_CREATED)
def request_revision(
    project_id: str, 
    delivery_id: str, 
    revision_in: RevisionCreate, 
    db: FirestoreClient = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    return workspace_service.request_revision(db, project_id, delivery_id, current_user.id, revision_in)
