from fastapi import APIRouter, Depends, HTTPException, status, Query
from google.cloud.firestore import Client as FirestoreClient
from app.db.firebase import get_db
from app.schemas.project import ProjectCreate, ProjectOut, ProjectUpdate, ProposalCreate, ProposalOut, ProposalDesignerOut
from app.services import project as project_svc
from app.api.dependencies import get_current_user, require_client_role, require_designer_role
from app.models.user import User

router = APIRouter()


@router.post("/", response_model=ProjectOut, status_code=status.HTTP_201_CREATED)
def create_project(
    project_in: ProjectCreate,
    db: FirestoreClient = Depends(get_db),
    current_user: User = Depends(require_client_role),
):
    """Create a new project. Only CLIENTS may create projects."""
    project = project_svc.create_project(db, current_user.id, project_in)
    return project


@router.get("/", response_model=list[ProjectOut])
def list_projects(
    db: FirestoreClient = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """List projects. If client, lists their projects. If designer, could list assigned projects (needs separate implementation, currently defaults to client projects)."""
    if current_user.role.value == "CLIENT":
        projects = project_svc.list_client_projects(db, current_user.id, limit=limit, offset=offset)
        return projects
    else:
        # For simplicity, returning empty list for designers here. 
        # A real implementation would fetch projects where designerId == current_user.id
        return []


@router.get("/{project_id}", response_model=ProjectOut)
def get_project(project_id: str, db: FirestoreClient = Depends(get_db)):
    """Get a project by ID."""
    project = project_svc.get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return project


@router.put("/{project_id}", response_model=ProjectOut)
def update_project(
    project_id: str,
    project_in: ProjectUpdate,
    db: FirestoreClient = Depends(get_db),
    current_user: User = Depends(require_client_role),
):
    """Update a project. Only the owning client may update it."""
    project = project_svc.get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    if project.clientId != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify this project",
        )
    try:
        updated = project_svc.update_project(db, project_id, project_in)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return updated


@router.post("/{project_id}/proposals", response_model=ProposalOut, status_code=status.HTTP_201_CREATED)
def submit_proposal(
    project_id: str,
    proposal_in: ProposalCreate,
    db: FirestoreClient = Depends(get_db),
    current_user: User = Depends(require_designer_role),
):
    """Submit a proposal for a project. Only APPROVED designers can submit."""
    try:
        proposal = project_svc.submit_proposal(db, project_id, current_user.id, proposal_in)
        return proposal
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{project_id}/proposals")
def list_proposals(
    project_id: str,
    db: FirestoreClient = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List proposals for a project. Clients see all details, designers see sanitized competitor details."""
    is_client = current_user.role.value == "CLIENT"
    proposals = project_svc.list_project_proposals(db, project_id, current_user.id, is_client)
    return proposals


@router.post("/{project_id}/proposals/{proposal_id}/select", response_model=ProjectOut)
def select_designer(
    project_id: str,
    proposal_id: str,
    db: FirestoreClient = Depends(get_db),
    current_user: User = Depends(require_client_role),
):
    """Select a designer's proposal for a project. Only the owning client can select."""
    try:
        project = project_svc.select_designer(db, project_id, proposal_id, current_user.id)
        return project
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{project_id}/accept", response_model=ProjectOut)
def accept_project(
    project_id: str,
    db: FirestoreClient = Depends(get_db),
    current_user: User = Depends(require_designer_role),
):
    """Designer accepts the project after being selected. Transitions to AWAITING_PAYMENT."""
    try:
        project = project_svc.accept_project(db, project_id, current_user.id)
        return project
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

