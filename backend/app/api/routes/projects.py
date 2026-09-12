from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.project import ProjectCreate, ProjectOut, ProjectUpdate
from app.services import project as project_svc
from app.api.dependencies import get_current_user, require_client_role
from app.models.user import User

router = APIRouter()


@router.post("/", response_model=ProjectOut, status_code=status.HTTP_201_CREATED)
def create_project(
    project_in: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_client_role),
):
    """Create a new project. Only CLIENTS may create projects."""
    project = project_svc.create_project(db, current_user.id, project_in)
    return project


@router.get("/", response_model=list[ProjectOut])
def list_projects(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_client_role),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """List all projects owned by the authenticated client."""
    projects = project_svc.list_client_projects(db, current_user.id, limit=limit, offset=offset)
    return projects


@router.get("/{project_id}", response_model=ProjectOut)
def get_project(project_id: int, db: Session = Depends(get_db)):
    """Get a project by ID. Publicly accessible."""
    project = project_svc.get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return project


@router.put("/{project_id}", response_model=ProjectOut)
def update_project(
    project_id: int,
    project_in: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_client_role),
):
    """Update a project. Only the owning client may update it."""
    project = project_svc.get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    if project.client_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify this project",
        )
    try:
        updated = project_svc.update_project(db, project_id, project_in)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return updated
