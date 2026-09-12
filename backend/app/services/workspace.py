from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime, timezone

from app.models.project import Project, ProjectStatus
from app.models.milestone import Milestone
from app.models.task import Task
from app.models.file import FileMetadata
from app.models.workspace import ProjectEvent, ProjectEventType
from app.models.delivery import Delivery, DeliveryStatus, Revision, RevisionStatus
from app.models.payment import DesignerEarning, EarningStatus, LedgerEntry, EntryDirection
from app.schemas.workspace import (
    MilestoneCreate, MilestoneUpdate,
    TaskCreate, TaskUpdate,
    FileMetadataCreate, ProjectEventCreate,
    DeliveryCreate, RevisionCreate
)
from app.models.notification import NotificationType
import app.services.notifications as notif_svc


def verify_workspace_access(db: Session, project_id: int, user_id: int) -> Project:
    """
    Verify that the user is either the client or assigned designer for the project.
    Returns the project if authorized, raises 403 otherwise.
    Raises 404 if project doesn't exist.
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    # The user must be the client who created the project, or the assigned designer.
    # Note: Designer profiles have the same ID as their User account in this schema.
    if project.client_id != user_id and project.assigned_designer_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this project's workspace"
        )
        
    return project


def check_project_active(project: Project):
    """Raise error if project is cancelled or completed (prevent edits)."""
    if project.status in [ProjectStatus.CANCELLED, ProjectStatus.COMPLETED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot modify workspace items for a {project.status.value} project"
        )


# --- MILESTONES ---

def create_milestone(db: Session, project_id: int, milestone_in: MilestoneCreate) -> Milestone:
    db_obj = Milestone(
        project_id=project_id,
        title=milestone_in.title,
        description=milestone_in.description,
        order=milestone_in.order,
        status=milestone_in.status,
        due_date=milestone_in.due_date
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)

    # Notify: project participants — milestone created
    try:
        project = db.query(Project).filter(Project.id == project_id).first()
        if project:
            recipients = [r for r in {project.client_id, project.assigned_designer_id} if r]
            notif_svc.create_bulk_notifications(
                db=db,
                recipient_ids=recipients,
                notification_type=NotificationType.MILESTONE_CREATED,
                title="Milestone created",
                message=f"Milestone '{db_obj.title}' was added to the project.",
                entity_type="milestone",
                entity_id=db_obj.id,
                meta_data={"project_id": project_id, "milestone_id": db_obj.id},
            )
            db.commit()
    except Exception:
        pass

    return db_obj


def update_milestone(db: Session, milestone_id: int, milestone_in: MilestoneUpdate) -> Milestone:
    db_obj = db.query(Milestone).filter(Milestone.id == milestone_id).first()
    if not db_obj:
        raise HTTPException(status_code=404, detail="Milestone not found")
        
    update_data = milestone_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)
        
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)

    # Notify: milestone updated
    try:
        project = db.query(Project).filter(Project.id == db_obj.project_id).first()
        if project:
            recipients = [r for r in {project.client_id, project.assigned_designer_id} if r]
            notif_svc.create_bulk_notifications(
                db=db,
                recipient_ids=recipients,
                notification_type=NotificationType.MILESTONE_UPDATED,
                title="Milestone updated",
                message=f"Milestone '{db_obj.title}' was updated.",
                entity_type="milestone",
                entity_id=db_obj.id,
                meta_data={"project_id": db_obj.project_id, "milestone_id": db_obj.id},
            )
            db.commit()
    except Exception:
        pass

    return db_obj


def delete_milestone(db: Session, milestone_id: int) -> None:
    db_obj = db.query(Milestone).filter(Milestone.id == milestone_id).first()
    if not db_obj:
        raise HTTPException(status_code=404, detail="Milestone not found")
    db.delete(db_obj)
    db.commit()


# --- TASKS ---

def validate_task_assignment(project: Project, assigned_user_id: Optional[int]):
    if assigned_user_id is not None:
        if assigned_user_id not in [project.client_id, project.assigned_designer_id]:
            raise HTTPException(status_code=400, detail="Assigned user must be the project client or assigned designer")


def create_task(db: Session, project_id: int, task_in: TaskCreate) -> Task:
    # Validate milestone belongs to project
    milestone = db.query(Milestone).filter(Milestone.id == task_in.milestone_id, Milestone.project_id == project_id).first()
    if not milestone:
        raise HTTPException(status_code=404, detail="Milestone not found in this project")
        
    validate_task_assignment(milestone.project, task_in.assigned_user_id)
        
    db_obj = Task(
        milestone_id=task_in.milestone_id,
        title=task_in.title,
        description=task_in.description,
        status=task_in.status,
        priority=task_in.priority,
        assigned_user_id=task_in.assigned_user_id,
        due_date=task_in.due_date
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)

    # Notify assigned user about new task
    try:
        if db_obj.assigned_user_id:
            notif_svc.create_notification(
                db=db,
                recipient_id=db_obj.assigned_user_id,
                notification_type=NotificationType.TASK_ASSIGNED,
                title="Task assigned to you",
                message=f"You have been assigned task '{db_obj.title}'.",
                entity_type="task",
                entity_id=db_obj.id,
                meta_data={"project_id": project_id, "task_id": db_obj.id},
            )
            db.commit()
    except Exception:
        pass

    return db_obj


def update_task(db: Session, project_id: int, task_id: int, task_in: TaskUpdate) -> Task:
    # Join with Milestone to ensure task belongs to this project
    db_obj = db.query(Task).join(Milestone).filter(Task.id == task_id, Milestone.project_id == project_id).first()
    if not db_obj:
        raise HTTPException(status_code=404, detail="Task not found")
        
    if task_in.assigned_user_id is not None:
        validate_task_assignment(db_obj.milestone.project, task_in.assigned_user_id)
        
    update_data = task_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)
        
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def delete_task(db: Session, project_id: int, task_id: int) -> None:
    db_obj = db.query(Task).join(Milestone).filter(Task.id == task_id, Milestone.project_id == project_id).first()
    if not db_obj:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(db_obj)
    db.commit()


# --- FILES ---

def create_file_metadata(db: Session, project_id: int, uploader_id: int, file_in: FileMetadataCreate) -> FileMetadata:
    db_obj = FileMetadata(
        project_id=project_id,
        uploader_id=uploader_id,
        filename=file_in.filename,
        storage_key=file_in.storage_key,
        file_url=file_in.file_url,
        mime_type=file_in.mime_type,
        file_size=file_in.file_size
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)

    # Notify the opposite project participant about file upload
    try:
        project = db.query(Project).filter(Project.id == project_id).first()
        if project:
            # Notify the OTHER party (not the uploader)
            notify_ids = [
                r for r in {project.client_id, project.assigned_designer_id}
                if r and r != uploader_id
            ]
            if notify_ids:
                notif_svc.create_bulk_notifications(
                    db=db,
                    recipient_ids=notify_ids,
                    notification_type=NotificationType.FILE_UPLOADED,
                    title="New file uploaded",
                    message=f"A file '{db_obj.filename}' was uploaded to the project.",
                    actor_id=uploader_id,
                    entity_type="file",
                    entity_id=db_obj.id,
                    meta_data={"project_id": project_id, "file_id": db_obj.id},
                )
                db.commit()
    except Exception:
        pass

    return db_obj

def create_project_event(db: Session, project_id: int, author_id: int, event_in: ProjectEventCreate) -> ProjectEvent:
    db_obj = ProjectEvent(
        project_id=project_id,
        author_id=author_id,
        event_type=event_in.event_type,
        content=event_in.content
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


# --- DELIVERABLES ---

from app.models.profile import DesignerProfile

def submit_delivery(db: Session, project: Project, user_id: int, delivery_in: DeliveryCreate) -> Delivery:
    check_project_active(project)
    
    designer_profile = db.query(DesignerProfile).filter(DesignerProfile.user_id == user_id).first()
    if not designer_profile:
        raise HTTPException(status_code=400, detail="Designer profile not found")
    
    # Calculate version (max current version + 1)
    current_deliveries = db.query(Delivery).filter(Delivery.project_id == project.id).all()
    version = len(current_deliveries) + 1
    
    # Validate files exist and belong to project
    files = []
    if delivery_in.file_ids:
        files = db.query(FileMetadata).filter(
            FileMetadata.id.in_(delivery_in.file_ids),
            FileMetadata.project_id == project.id
        ).all()
        if len(files) != len(delivery_in.file_ids):
            raise HTTPException(status_code=400, detail="Some files are invalid or do not belong to this project")

    db_obj = Delivery(
        project_id=project.id,
        designer_id=designer_profile.id,
        version=version,
        message=delivery_in.message,
        status=DeliveryStatus.PENDING_REVIEW
    )
    
    # Associate files
    for file in files:
        db_obj.files.append(file)
        
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)

    # Log event
    create_project_event(db, project.id, user_id, ProjectEventCreate(
        event_type=ProjectEventType.DELIVERY_SUBMITTED,
        content=f"Delivery version {version} submitted."
    ))

    # Notify client: delivery submitted
    try:
        notif_svc.create_notification(
            db=db,
            recipient_id=project.client_id,
            notification_type=NotificationType.DELIVERY_SUBMITTED,
            title="Delivery submitted",
            message=f"A new delivery (v{version}) has been submitted for your review.",
            actor_id=user_id,
            entity_type="delivery",
            entity_id=db_obj.id,
            meta_data={"project_id": project.id, "delivery_id": db_obj.id, "version": version},
        )
        db.commit()
    except Exception:
        pass

    return db_obj


def accept_delivery(db: Session, project: Project, delivery_id: int, client_id: int) -> Delivery:
    check_project_active(project)
    
    delivery = db.query(Delivery).filter(Delivery.id == delivery_id, Delivery.project_id == project.id).first()
    if not delivery:
        raise HTTPException(status_code=404, detail="Delivery not found")
        
    if delivery.status != DeliveryStatus.PENDING_REVIEW:
        raise HTTPException(status_code=400, detail=f"Cannot accept delivery in {delivery.status.value} status")
        
    delivery.status = DeliveryStatus.ACCEPTED
    db.add(delivery)
    
    # Financial: Release pending earnings to the designer
    earnings = db.query(DesignerEarning).filter(
        DesignerEarning.project_id == project.id,
        DesignerEarning.status == EarningStatus.PENDING
    ).all()
    
    for earning in earnings:
        earning.status = EarningStatus.AVAILABLE
        earning.available_at = datetime.now(timezone.utc)
        db.add(earning)
        
        # Log ledger entry for the designer credit
        ledger_credit = LedgerEntry(
            project_id=project.id,
            payment_id=earning.payment_id,
            user_id=earning.designer_id,
            entry_type="DESIGNER_EARNING_RELEASE",
            amount=earning.net_amount,
            currency=earning.currency,
            direction=EntryDirection.CREDIT,
            description=f"Earnings released for accepted delivery version {delivery.version}"
        )
        db.add(ledger_credit)
        
    db.commit()

    # Log event
    create_project_event(db, project.id, client_id, ProjectEventCreate(
        event_type=ProjectEventType.DELIVERY_ACCEPTED,
        content=f"Delivery version {delivery.version} accepted."
    ))

    # Notify designer: delivery accepted
    try:
        designer_user_id = None
        if delivery.designer_id:
            from app.models.profile import DesignerProfile
            dp = db.query(DesignerProfile).filter(DesignerProfile.id == delivery.designer_id).first()
            if dp:
                designer_user_id = dp.user_id
        if designer_user_id:
            notif_svc.create_notification(
                db=db,
                recipient_id=designer_user_id,
                notification_type=NotificationType.DELIVERY_ACCEPTED,
                title="Delivery accepted",
                message=f"Your delivery (v{delivery.version}) was accepted by the client.",
                actor_id=client_id,
                entity_type="delivery",
                entity_id=delivery.id,
                meta_data={"project_id": project.id, "delivery_id": delivery.id},
            )
            # Notify designer: earnings released
            for earning in earnings:
                notif_svc.create_notification(
                    db=db,
                    recipient_id=designer_user_id,
                    notification_type=NotificationType.EARNINGS_RELEASED,
                    title="Earnings released",
                    message=f"Your earnings of {earning.net_amount} {earning.currency} are now available.",
                    entity_type="earning",
                    entity_id=earning.id,
                    meta_data={"project_id": project.id, "earning_id": earning.id, "net_amount": earning.net_amount},
                )
            db.commit()
    except Exception:
        pass

    return delivery


def request_revision(db: Session, project: Project, delivery_id: int, client_id: int, revision_in: RevisionCreate) -> Revision:
    check_project_active(project)
    
    delivery = db.query(Delivery).filter(Delivery.id == delivery_id, Delivery.project_id == project.id).first()
    if not delivery:
        raise HTTPException(status_code=404, detail="Delivery not found")
        
    if delivery.status != DeliveryStatus.PENDING_REVIEW:
        raise HTTPException(status_code=400, detail=f"Cannot request revision for delivery in {delivery.status.value} status")
        
    delivery.status = DeliveryStatus.REVISION_REQUESTED
    
    revision_num = len(delivery.revisions) + 1
    
    rev_obj = Revision(
        delivery_id=delivery.id,
        revision_number=revision_num,
        request_reason=revision_in.request_reason,
        client_comment=revision_in.client_comment,
        status=RevisionStatus.PENDING
    )
    
    db.add(delivery)
    db.add(rev_obj)
    db.commit()
    db.refresh(rev_obj)

    # Log event
    create_project_event(db, project.id, client_id, ProjectEventCreate(
        event_type=ProjectEventType.REVISION_REQUESTED,
        content=f"Revision requested for delivery version {delivery.version}: {revision_in.request_reason}"
    ))

    # Notify designer: revision requested
    try:
        from app.models.profile import DesignerProfile
        dp = db.query(DesignerProfile).filter(DesignerProfile.id == delivery.designer_id).first()
        if dp:
            notif_svc.create_notification(
                db=db,
                recipient_id=dp.user_id,
                notification_type=NotificationType.REVISION_REQUESTED,
                title="Revision requested",
                message=f"The client has requested a revision for delivery v{delivery.version}: {revision_in.request_reason}",
                actor_id=client_id,
                entity_type="delivery",
                entity_id=delivery.id,
                meta_data={"project_id": project.id, "delivery_id": delivery.id, "revision_id": rev_obj.id},
            )
            db.commit()
    except Exception:
        pass

    return rev_obj
