from sqlalchemy.orm import Session
from datetime import datetime, timezone
from app.models.invitation import ProjectInvitation, InvitationStatus
from app.models.project import Project, ProjectStatus
from app.services.profile import get_designer_profile
from app.models.user import User
from app.models.notification import NotificationType
import app.services.notifications as notif_svc


def create_invitation(
    db: Session,
    client_user_id: int,
    project_id: int,
    designer_id: int,
    message: str | None = None,
) -> ProjectInvitation:
    # verify project exists and is owned by client
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise ValueError("Project not found")
    if project.client_id != client_user_id:
        raise PermissionError("Not owner of project")
    if project.status in (ProjectStatus.CANCELLED, ProjectStatus.COMPLETED):
        raise ValueError("Cannot invite to a cancelled or completed project")

    # Resolve designer profile — accept designer profile id directly
    from app.models.profile import DesignerProfile
    designer = db.query(DesignerProfile).filter(DesignerProfile.id == designer_id).first()
    if not designer:
        raise ValueError("Designer profile not found")

    # Prevent duplicate invitations (unique constraint will also catch this, but give a friendly message)
    existing = db.query(ProjectInvitation).filter(
        ProjectInvitation.project_id == project_id,
        ProjectInvitation.designer_id == designer.id,
    ).first()
    if existing:
        raise ValueError("Designer has already been invited to this project")

    inv = ProjectInvitation(
        project_id=project_id,
        designer_id=designer.id,
        client_id=client_user_id,
        message=message,
    )
    db.add(inv)
    db.commit()
    db.refresh(inv)

    # Notify designer about the new invitation
    try:
        notif_svc.create_notification(
            db=db,
            recipient_id=designer.user_id,
            notification_type=NotificationType.PROJECT_INVITATION,
            title="New project invitation",
            message=f"You have been invited to project '{project.title}'.",
            actor_id=client_user_id,
            entity_type="project",
            entity_id=project_id,
            meta_data={"project_id": project_id, "invitation_id": inv.id},
        )
        db.commit()
    except Exception:
        pass  # Notification failure must never break the invitation flow

    return inv


def get_invitation(db: Session, invitation_id: int) -> ProjectInvitation | None:
    return db.query(ProjectInvitation).filter(ProjectInvitation.id == invitation_id).first()


def list_invitations_for_designer(db: Session, designer_user_id: int) -> list[ProjectInvitation]:
    """Return all invitations where the current user is the invited designer."""
    designer = get_designer_profile(db, designer_user_id)
    if not designer:
        return []
    return db.query(ProjectInvitation).filter(ProjectInvitation.designer_id == designer.id).all()


def list_invitations_for_client(db: Session, client_user_id: int) -> list[ProjectInvitation]:
    return db.query(ProjectInvitation).filter(ProjectInvitation.client_id == client_user_id).all()


def accept_invitation(db: Session, invitation_id: int, designer_user_id: int) -> ProjectInvitation:
    inv = get_invitation(db, invitation_id)
    if not inv:
        raise ValueError("Invitation not found")

    # Ensure the caller is the invited designer
    designer = get_designer_profile(db, designer_user_id)
    if not designer or designer.id != inv.designer_id:
        raise PermissionError("Not authorized to accept this invitation")
    if inv.status != InvitationStatus.PENDING:
        raise ValueError("Invitation already responded")

    # Verify project is still open/draft
    project = db.query(Project).filter(Project.id == inv.project_id).first()
    if not project:
        raise ValueError("Project not found")
    if project.status in (ProjectStatus.CANCELLED, ProjectStatus.COMPLETED):
        raise ValueError("Cannot accept invitation for a cancelled or completed project")

    # Accept invitation and assign designer to project
    inv.status = InvitationStatus.ACCEPTED
    inv.responded_at = datetime.now(timezone.utc)

    project.assigned_designer_id = inv.designer_id
    project.status = ProjectStatus.IN_PROGRESS

    db.add(inv)
    db.add(project)
    db.commit()
    db.refresh(inv)
    db.refresh(project)

    # Notify client: designer accepted
    try:
        notif_svc.create_notification(
            db=db,
            recipient_id=project.client_id,
            notification_type=NotificationType.PROJECT_INVITATION_ACCEPTED,
            title="Invitation accepted",
            message=f"A designer accepted your invitation for project '{project.title}'.",
            actor_id=designer.user_id,
            entity_type="project",
            entity_id=project.id,
            meta_data={"project_id": project.id, "invitation_id": inv.id},
        )
        # Notify both parties: project assigned
        notif_svc.create_bulk_notifications(
            db=db,
            recipient_ids=[project.client_id, designer.user_id],
            notification_type=NotificationType.PROJECT_ASSIGNED,
            title="Project assigned",
            message=f"Project '{project.title}' is now in progress.",
            entity_type="project",
            entity_id=project.id,
            meta_data={"project_id": project.id},
        )
        db.commit()
    except Exception:
        pass

    return inv


def reject_invitation(db: Session, invitation_id: int, designer_user_id: int) -> ProjectInvitation:
    inv = get_invitation(db, invitation_id)
    if not inv:
        raise ValueError("Invitation not found")
    designer = get_designer_profile(db, designer_user_id)
    if not designer or designer.id != inv.designer_id:
        raise PermissionError("Not authorized to reject this invitation")
    if inv.status != InvitationStatus.PENDING:
        raise ValueError("Invitation already responded")

    inv.status = InvitationStatus.REJECTED
    inv.responded_at = datetime.now(timezone.utc)
    db.add(inv)
    db.commit()
    db.refresh(inv)

    # Notify client: designer declined
    try:
        project = db.query(Project).filter(Project.id == inv.project_id).first()
        notif_svc.create_notification(
            db=db,
            recipient_id=inv.client_id,
            notification_type=NotificationType.PROJECT_INVITATION_DECLINED,
            title="Invitation declined",
            message=f"A designer declined your invitation{(' for project ' + project.title) if project else ''}.",
            actor_id=designer.user_id,
            entity_type="project",
            entity_id=inv.project_id,
            meta_data={"project_id": inv.project_id, "invitation_id": inv.id},
        )
        db.commit()
    except Exception:
        pass

    return inv
