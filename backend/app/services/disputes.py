import uuid
from datetime import datetime, timezone
from typing import Optional, List
from fastapi import HTTPException
from google.cloud.firestore import Client as FirestoreClient, Transaction, transactional, Query

from app.schemas.dispute import (
    DisputeCreate, DisputeOut, DisputeStatusUpdate,
    DisputeResolutionRequest, DisputeResponseCreate, DisputeResponseOut,
    DisputeStatus, ResolutionType, DisputeListResponse, DisputeResponseListResponse
)
from app.schemas.project import ProjectStatus
from app.schemas.workspace import ProjectEventType
from app.schemas.payment import EarningStatus

def get_project_or_404(db: FirestoreClient, project_id: str) -> dict:
    doc = db.collection("projects").document(project_id).get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Project not found")
    return doc.to_dict()

def check_project_participant(project: dict, user_id: str) -> str:
    if project.get("clientId") == user_id:
        return "CLIENT"
    if project.get("assignedDesignerId") == user_id:
        return "DESIGNER"
    raise HTTPException(status_code=403, detail="Not a participant of this project")

def get_opposing_user_id(project: dict, raiser_id: str) -> str:
    return project.get("assignedDesignerId") if project.get("clientId") == raiser_id else project.get("clientId")

def _log_event(transaction: Transaction, db: FirestoreClient, project_id: str, author_id: str, event_type: str, content: str):
    event_id = str(uuid.uuid4())
    ref = db.collection("projects").document(project_id).collection("events").document(event_id)
    now = datetime.now(timezone.utc)
    transaction.set(ref, {
        "id": event_id,
        "projectId": project_id,
        "authorId": author_id,
        "eventType": event_type,
        "content": content,
        "createdAt": now
    })

def create_dispute(db: FirestoreClient, project_id: str, raiser_id: str, payload: DisputeCreate) -> DisputeOut:
    project = get_project_or_404(db, project_id)
    check_project_participant(project, raiser_id)
    
    if project.get("status") in [ProjectStatus.COMPLETED.value, ProjectStatus.CANCELLED.value]:
        raise HTTPException(status_code=400, detail="Cannot open dispute on a completed or cancelled project")
        
    opposing_id = get_opposing_user_id(project, raiser_id)
    
    @transactional
    def _create(transaction):
        # Freeze project
        p_ref = db.collection("projects").document(project_id)
        transaction.update(p_ref, {"status": ProjectStatus.FROZEN.value})
        
        _log_event(transaction, db, project_id, raiser_id, ProjectEventType.DISPUTE_OPENED.value, f"Dispute opened: {payload.reason.value}")
        
        dispute_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc)
        data = {
            "id": dispute_id,
            "projectId": project_id,
            "paymentId": payload.paymentId,
            "raisedByUserId": raiser_id,
            "againstUserId": opposing_id,
            "reason": payload.reason.value,
            "description": payload.description,
            "status": DisputeStatus.OPEN.value,
            "resolutionType": None,
            "resolutionAmount": None,
            "resolutionNote": None,
            "resolvedByUserId": None,
            "resolvedAt": None,
            "createdAt": now,
            "updatedAt": now
        }
        
        d_ref = db.collection("disputes").document(dispute_id)
        transaction.set(d_ref, data)
        return data
        
    return DisputeOut(**_create(db.transaction()))

def get_dispute(db: FirestoreClient, dispute_id: str) -> DisputeOut:
    doc = db.collection("disputes").document(dispute_id).get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Dispute not found")
    return DisputeOut(**doc.to_dict())

def check_dispute_access(dispute: DisputeOut, user_id: str, is_admin: bool = False):
    if is_admin:
        return
    if user_id not in [dispute.raisedByUserId, dispute.againstUserId]:
        raise HTTPException(status_code=403, detail="Not authorized to view this dispute")

def list_project_disputes(db: FirestoreClient, project_id: str) -> DisputeListResponse:
    query = db.collection("disputes").where("projectId", "==", project_id).get()
    disputes = [DisputeOut(**d.to_dict()) for d in query]
    return DisputeListResponse(disputes=disputes, total=len(disputes))

def change_status(db: FirestoreClient, dispute_id: str, user_id: str, payload: DisputeStatusUpdate) -> DisputeOut:
    # MVP: Admin only route
    @transactional
    def _update(transaction):
        ref = db.collection("disputes").document(dispute_id)
        doc = ref.get(transaction=transaction)
        if not doc.exists:
            raise HTTPException(status_code=404, detail="Dispute not found")
            
        transaction.update(ref, {
            "status": payload.status.value,
            "updatedAt": datetime.now(timezone.utc)
        })
        
        return ref.get(transaction=transaction).to_dict()
    
    return DisputeOut(**_update(db.transaction()))

def add_response(db: FirestoreClient, dispute_id: str, user_id: str, payload: DisputeResponseCreate) -> DisputeResponseOut:
    dispute = get_dispute(db, dispute_id)
    check_dispute_access(dispute, user_id)
    
    if dispute.status in [DisputeStatus.RESOLVED.value, DisputeStatus.CLOSED_UNRESOLVED.value]:
        raise HTTPException(status_code=400, detail="Dispute is closed")
        
    resp_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)
    
    data = {
        "id": resp_id,
        "disputeId": dispute_id,
        "userId": user_id,
        "message": payload.message,
        "attachmentMeta": None,
        "createdAt": now
    }
    
    db.collection("disputes").document(dispute_id).collection("responses").document(resp_id).set(data)
    return DisputeResponseOut(**data)

def list_responses(db: FirestoreClient, dispute_id: str) -> DisputeResponseListResponse:
    query = db.collection("disputes").document(dispute_id).collection("responses").order_by("createdAt").get()
    responses = [DisputeResponseOut(**r.to_dict()) for r in query]
    return DisputeResponseListResponse(responses=responses, total=len(responses))

def resolve_dispute(db: FirestoreClient, dispute_id: str, admin_id: str, payload: DisputeResolutionRequest) -> DisputeOut:
    dispute = get_dispute(db, dispute_id)
    
    if dispute.status in [DisputeStatus.RESOLVED.value, DisputeStatus.CLOSED_UNRESOLVED.value]:
        raise HTTPException(status_code=400, detail="Dispute is already closed")
        
    @transactional
    def _resolve(transaction):
        # 1. Update dispute
        d_ref = db.collection("disputes").document(dispute_id)
        now = datetime.now(timezone.utc)
        transaction.update(d_ref, {
            "status": DisputeStatus.RESOLVED.value,
            "resolutionType": payload.resolutionType.value,
            "resolutionNote": payload.resolutionNote,
            "resolutionAmount": payload.resolutionAmount,
            "resolvedByUserId": admin_id,
            "resolvedAt": now,
            "updatedAt": now
        })
        
        # 2. Update project
        p_ref = db.collection("projects").document(dispute.projectId)
        transaction.update(p_ref, {"status": ProjectStatus.CANCELLED.value}) # Standard resolution cancels project
        
        # 3. Financials (simplified MVP: mark earning as cancelled or available)
        earnings = db.collection("designerEarnings").where("projectId", "==", dispute.projectId).where("status", "==", EarningStatus.PENDING.value).get(transaction=transaction)
        
        for earning in earnings:
            new_status = EarningStatus.CANCELLED.value
            if payload.resolutionType == ResolutionType.FUNDS_RELEASED_TO_DESIGNER:
                new_status = EarningStatus.AVAILABLE.value
            # Partial refund not fully implemented in ledger for MVP, defaulting to cancelled
                
            transaction.update(earning.reference, {
                "status": new_status,
                "updatedAt": now
            })
            
        _log_event(transaction, db, dispute.projectId, admin_id, ProjectEventType.DISPUTE_RESOLVED.value, f"Dispute resolved via {payload.resolutionType.value}")
        return d_ref.get(transaction=transaction).to_dict()
        
    return DisputeOut(**_resolve(db.transaction()))
