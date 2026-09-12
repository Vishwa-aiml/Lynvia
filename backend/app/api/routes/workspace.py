from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.api.dependencies import get_db, get_current_user
from app.models.user import User
from app.schemas.workspace import (
    ProjectWorkspaceOut,
    MilestoneCreate, MilestoneUpdate, MilestoneOut,
    TaskCreate, TaskUpdate, TaskOut,
    FileMetadataCreate, FileMetadataOut,
    ProjectEventCreate, ProjectEventOut,
    DeliveryCreate, DeliveryOut,
    RevisionCreate, RevisionOut
)
from app.services import workspace as workspace_service

router = APIRouter()


def verify_access(project_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Dependency to verify user has workspace access and return the project."""
    return workspace_service.verify_workspace_access(db, project_id, current_user.id)


@router.get("/", response_model=ProjectWorkspaceOut)
def get_workspace(project_id: int, project=Depends(verify_access)):
    """Get all workspace data for a project (Milestones, Tasks, Files, Events, Deliveries)."""
    return {
        "project_id": project.id,
        "milestones": project.milestones,
        "tasks": [task for m in project.milestones for task in m.tasks],
        "files": project.files,
        "events": project.events,
        "deliveries": project.deliveries
    }


# --- MILESTONES ---

@router.post("/milestones", response_model=MilestoneOut, status_code=status.HTTP_201_CREATED)
def create_milestone(project_id: int, milestone_in: MilestoneCreate, project=Depends(verify_access), db: Session = Depends(get_db)):
    workspace_service.check_project_active(project)
    return workspace_service.create_milestone(db, project.id, milestone_in)


@router.put("/milestones/{milestone_id}", response_model=MilestoneOut)
def update_milestone(project_id: int, milestone_id: int, milestone_in: MilestoneUpdate, project=Depends(verify_access), db: Session = Depends(get_db)):
    workspace_service.check_project_active(project)
    return workspace_service.update_milestone(db, milestone_id, milestone_in)


@router.delete("/milestones/{milestone_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_milestone(project_id: int, milestone_id: int, project=Depends(verify_access), db: Session = Depends(get_db)):
    workspace_service.check_project_active(project)
    workspace_service.delete_milestone(db, milestone_id)
    return None


# --- TASKS ---

@router.post("/tasks", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
def create_task(project_id: int, task_in: TaskCreate, project=Depends(verify_access), db: Session = Depends(get_db)):
    workspace_service.check_project_active(project)
    return workspace_service.create_task(db, project.id, task_in)


@router.put("/tasks/{task_id}", response_model=TaskOut)
def update_task(project_id: int, task_id: int, task_in: TaskUpdate, project=Depends(verify_access), db: Session = Depends(get_db)):
    workspace_service.check_project_active(project)
    return workspace_service.update_task(db, project.id, task_id, task_in)


@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(project_id: int, task_id: int, project=Depends(verify_access), db: Session = Depends(get_db)):
    workspace_service.check_project_active(project)
    workspace_service.delete_task(db, project.id, task_id)
    return None


# --- FILES ---

@router.post("/files", response_model=FileMetadataOut, status_code=status.HTTP_201_CREATED)
def create_file(project_id: int, file_in: FileMetadataCreate, project=Depends(verify_access), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    workspace_service.check_project_active(project)
    return workspace_service.create_file_metadata(db, project.id, current_user.id, file_in)


# --- COLLABORATION ---

@router.post("/events", response_model=ProjectEventOut, status_code=status.HTTP_201_CREATED)
def create_event(project_id: int, event_in: ProjectEventCreate, project=Depends(verify_access), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return workspace_service.create_project_event(db, project.id, current_user.id, event_in)


# --- DELIVERABLES ---

@router.post("/deliveries", response_model=DeliveryOut, status_code=status.HTTP_201_CREATED)
def submit_delivery(project_id: int, delivery_in: DeliveryCreate, project=Depends(verify_access), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if project.assigned_designer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the assigned designer can submit deliveries")
    return workspace_service.submit_delivery(db, project, current_user.id, delivery_in)


@router.post("/deliveries/{delivery_id}/accept", response_model=DeliveryOut)
def accept_delivery(project_id: int, delivery_id: int, project=Depends(verify_access), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if project.client_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the client can accept deliveries")
    return workspace_service.accept_delivery(db, project, delivery_id, current_user.id)


@router.post("/deliveries/{delivery_id}/revisions", response_model=RevisionOut, status_code=status.HTTP_201_CREATED)
def request_revision(project_id: int, delivery_id: int, revision_in: RevisionCreate, project=Depends(verify_access), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if project.client_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the client can request revisions")
    return workspace_service.request_revision(db, project, delivery_id, current_user.id, revision_in)
