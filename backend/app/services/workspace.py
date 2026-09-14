import uuid
from typing import List, Optional
from datetime import datetime, timezone
from fastapi import HTTPException, status
from google.cloud.firestore import Client as FirestoreClient, Transaction, transactional

from app.schemas.workspace import (
    MilestoneCreate, MilestoneUpdate, MilestoneOut,
    TaskCreate, TaskUpdate, TaskOut,
    FileMetadataCreate, FileMetadataOut, ProjectEventCreate, ProjectEventOut,
    DeliveryCreate, DeliveryOut, RevisionCreate, RevisionOut,
    ProjectWorkspaceOut, MilestoneStatus, TaskStatus, DeliveryStatus, RevisionStatus, ProjectEventType
)
from app.schemas.project import ProjectStatus

def verify_workspace_access(db: FirestoreClient, project_id: str, user_id: str) -> dict:
    doc = db.collection("projects").document(project_id).get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Project not found")
        
    data = doc.to_dict()
    if data.get("clientId") != user_id and data.get("assignedDesignerId") != user_id:
        raise HTTPException(status_code=403, detail="You do not have access to this workspace")
        
    return data

def check_project_active(project_data: dict):
    if project_data.get("status") in [ProjectStatus.CANCELLED.value, ProjectStatus.COMPLETED.value]:
        raise HTTPException(status_code=400, detail="Cannot modify workspace for this project status")

def _log_event(transaction: Transaction, db: FirestoreClient, project_id: str, author_id: str, event_type: str, content: str = None):
    now = datetime.now(timezone.utc)
    event_id = str(uuid.uuid4())
    ref = db.collection("projects").document(project_id).collection("events").document(event_id)
    transaction.set(ref, {
        "id": event_id,
        "projectId": project_id,
        "authorId": author_id,
        "eventType": event_type,
        "content": content,
        "createdAt": now
    })

# --- MILESTONES ---

def create_milestone(db: FirestoreClient, project_id: str, user_id: str, milestone_in: MilestoneCreate) -> MilestoneOut:
    project_data = verify_workspace_access(db, project_id, user_id)
    check_project_active(project_data)
    
    @transactional
    def _create(transaction):
        milestone_id = str(uuid.uuid4())
        ref = db.collection("projects").document(project_id).collection("milestones").document(milestone_id)
        now = datetime.now(timezone.utc)
        data = milestone_in.model_dump()
        data.update({
            "id": milestone_id,
            "projectId": project_id,
            "createdAt": now,
            "updatedAt": now
        })
        if "dueDate" in data and data["dueDate"]:
            data["dueDate"] = data["dueDate"]
            
        transaction.set(ref, data)
        _log_event(transaction, db, project_id, user_id, ProjectEventType.MILESTONE_CREATED.value, f"Milestone '{data['title']}' created")
        return data
        
    return MilestoneOut(**_create(db.transaction()))

def update_milestone(db: FirestoreClient, project_id: str, milestone_id: str, user_id: str, milestone_in: MilestoneUpdate) -> MilestoneOut:
    verify_workspace_access(db, project_id, user_id)
    
    @transactional
    def _update(transaction):
        ref = db.collection("projects").document(project_id).collection("milestones").document(milestone_id)
        doc = ref.get(transaction=transaction)
        if not doc.exists:
            raise HTTPException(status_code=404, detail="Milestone not found")
            
        update_data = milestone_in.model_dump(exclude_unset=True)
        update_data["updatedAt"] = datetime.now(timezone.utc)
        
        transaction.update(ref, update_data)
        _log_event(transaction, db, project_id, user_id, ProjectEventType.MILESTONE_UPDATED.value, "Milestone updated")
        
        doc_updated = ref.get(transaction=transaction).to_dict()
        return doc_updated
        
    return MilestoneOut(**_update(db.transaction()))

# --- DELIVERIES ---

def submit_delivery(db: FirestoreClient, project_id: str, user_id: str, delivery_in: DeliveryCreate) -> DeliveryOut:
    project_data = verify_workspace_access(db, project_id, user_id)
    check_project_active(project_data)
    
    if project_data.get("assignedDesignerId") != user_id:
        raise HTTPException(status_code=403, detail="Only the assigned designer can submit deliveries")
        
    @transactional
    def _submit(transaction):
        # Get next version
        deliveries_ref = db.collection("projects").document(project_id).collection("deliveries")
        existing = list(deliveries_ref.get(transaction=transaction))
        version = len(existing) + 1
        
        delivery_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc)
        
        data = {
            "id": delivery_id,
            "projectId": project_id,
            "designerId": user_id,
            "version": version,
            "status": DeliveryStatus.SUBMITTED.value,
            "submittedAt": now,
            "message": delivery_in.message,
            "fileIds": delivery_in.fileIds,
            "revisions": []
        }
        transaction.set(deliveries_ref.document(delivery_id), data)
        _log_event(transaction, db, project_id, user_id, ProjectEventType.DELIVERY_SUBMITTED.value, f"Delivery v{version} submitted")
        return data
        
    return DeliveryOut(**_submit(db.transaction()))

def accept_delivery(db: FirestoreClient, project_id: str, delivery_id: str, user_id: str) -> DeliveryOut:
    project_data = verify_workspace_access(db, project_id, user_id)
    if project_data.get("clientId") != user_id:
        raise HTTPException(status_code=403, detail="Only the client can accept deliveries")
        
    @transactional
    def _accept(transaction):
        d_ref = db.collection("projects").document(project_id).collection("deliveries").document(delivery_id)
        doc = d_ref.get(transaction=transaction)
        if not doc.exists:
            raise HTTPException(status_code=404, detail="Delivery not found")
            
        d_data = doc.to_dict()
        if d_data["status"] != DeliveryStatus.SUBMITTED.value:
            raise HTTPException(status_code=400, detail="Only submitted deliveries can be accepted")
            
        transaction.update(d_ref, {"status": DeliveryStatus.ACCEPTED.value})
        
        # Complete project
        p_ref = db.collection("projects").document(project_id)
        transaction.update(p_ref, {"status": ProjectStatus.COMPLETED.value})
        
        # Release Escrow Funds (Earnings PENDING -> AVAILABLE)
        earnings_query = db.collection("designerEarnings").where("projectId", "==", project_id).where("status", "==", EarningStatus.PENDING.value).get(transaction=transaction)
        
        for e in earnings_query:
            transaction.update(e.reference, {
                "status": EarningStatus.AVAILABLE.value,
                "updatedAt": datetime.now(timezone.utc)
            })
        
        _log_event(transaction, db, project_id, user_id, ProjectEventType.DELIVERY_ACCEPTED.value, "Delivery accepted. Funds released and project complete.")
        
        d_data["status"] = DeliveryStatus.ACCEPTED.value
        return d_data
        
    return DeliveryOut(**_accept(db.transaction()))

def request_revision(db: FirestoreClient, project_id: str, delivery_id: str, user_id: str, revision_in: RevisionCreate) -> RevisionOut:
    project_data = verify_workspace_access(db, project_id, user_id)
    if project_data.get("clientId") != user_id:
        raise HTTPException(status_code=403, detail="Only the client can request revisions")
        
    @transactional
    def _revise(transaction):
        d_ref = db.collection("projects").document(project_id).collection("deliveries").document(delivery_id)
        doc = d_ref.get(transaction=transaction)
        if not doc.exists:
            raise HTTPException(status_code=404, detail="Delivery not found")
            
        d_data = doc.to_dict()
        if d_data["status"] != DeliveryStatus.SUBMITTED.value:
            raise HTTPException(status_code=400, detail="Revisions can only be requested on submitted deliveries")
            
        rev_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc)
        revisions = d_data.get("revisions", [])
        rev_num = len(revisions) + 1
        
        rev_data = {
            "id": rev_id,
            "deliveryId": delivery_id,
            "revisionNumber": rev_num,
            "requestReason": revision_in.requestReason,
            "clientComment": revision_in.clientComment,
            "designerResponse": None,
            "status": RevisionStatus.REQUESTED.value,
            "createdAt": now,
            "updatedAt": now
        }
        
        revisions.append(rev_data)
        transaction.update(d_ref, {
            "status": DeliveryStatus.IN_REVISION.value,
            "revisions": revisions
        })
        
        _log_event(transaction, db, project_id, user_id, ProjectEventType.REVISION_REQUESTED.value, "Revision requested")
        return rev_data
        
    return RevisionOut(**_revise(db.transaction()))

# --- FULL WORKSPACE FETCH ---

def get_workspace(db: FirestoreClient, project_id: str, user_id: str) -> ProjectWorkspaceOut:
    verify_workspace_access(db, project_id, user_id)
    
    p_ref = db.collection("projects").document(project_id)
    
    milestones = [MilestoneOut(**m.to_dict()) for m in p_ref.collection("milestones").stream()]
    tasks = [TaskOut(**t.to_dict()) for t in p_ref.collection("tasks").stream()]
    files = [FileMetadataOut(**f.to_dict()) for f in p_ref.collection("files").stream()]
    events = [ProjectEventOut(**e.to_dict()) for e in p_ref.collection("events").stream()]
    deliveries = [DeliveryOut(**d.to_dict()) for d in p_ref.collection("deliveries").stream()]
    
    return ProjectWorkspaceOut(
        projectId=project_id,
        milestones=milestones,
        tasks=tasks,
        files=files,
        events=events,
        deliveries=deliveries
    )
