from sqlalchemy.orm import Session
from app.models.project import Project, ProjectStatus
from app.schemas.project import ProjectCreate, ProjectUpdate


# Valid state transitions for a project
_VALID_TRANSITIONS: dict[ProjectStatus, set[ProjectStatus]] = {
    ProjectStatus.DRAFT: {ProjectStatus.OPEN, ProjectStatus.CANCELLED},
    ProjectStatus.OPEN: {ProjectStatus.IN_PROGRESS, ProjectStatus.CANCELLED},
    ProjectStatus.IN_PROGRESS: {ProjectStatus.COMPLETED, ProjectStatus.CANCELLED},
    ProjectStatus.COMPLETED: set(),
    ProjectStatus.CANCELLED: set(),
}


def create_project(db: Session, client_id: int, project_in: ProjectCreate) -> Project:
    project = Project(
        client_id=client_id,
        title=project_in.title,
        description=project_in.description,
        requirements=project_in.requirements,
        budget=project_in.budget,
        deadline=project_in.deadline,
        status=ProjectStatus.DRAFT,
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


def get_project(db: Session, project_id: int) -> Project | None:
    return db.query(Project).filter(Project.id == project_id).first()


def list_client_projects(db: Session, client_id: int, limit: int = 20, offset: int = 0) -> list[Project]:
    return (
        db.query(Project)
        .filter(Project.client_id == client_id)
        .order_by(Project.created_at.desc())
        .limit(limit)
        .offset(offset)
        .all()
    )


def update_project(db: Session, project_id: int, project_in: ProjectUpdate) -> Project | None:
    project = get_project(db, project_id)
    if not project:
        return None

    update_data = project_in.dict(exclude_unset=True)

    # Validate status transition if status is being changed
    if "status" in update_data:
        new_status_str = update_data["status"]
        # Pydantic may return enum or string depending on version
        if isinstance(new_status_str, str):
            new_status = ProjectStatus(new_status_str)
        else:
            new_status = new_status_str
        current_status = project.status
        allowed = _VALID_TRANSITIONS.get(current_status, set())
        if new_status not in allowed:
            raise ValueError(
                f"Cannot transition project from '{current_status.value}' to '{new_status.value}'"
            )
        update_data["status"] = new_status

    for key, value in update_data.items():
        setattr(project, key, value)

    db.add(project)
    db.commit()
    db.refresh(project)
    return project
