from google.cloud.firestore import Client as FirestoreClient, Transaction, transactional
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectOut, ProjectStatus, ProjectPhase
from app.schemas.project import ProposalCreate, ProposalOut, ProposalDesignerOut, ProposalStatus
from typing import Optional, List
from datetime import datetime, timezone
import uuid

_VALID_TRANSITIONS = {
    ProjectStatus.DRAFT: {ProjectStatus.OPEN_FOR_PROPOSALS, ProjectStatus.CANCELLED},
    ProjectStatus.OPEN_FOR_PROPOSALS: {ProjectStatus.PROPOSAL_REVIEW, ProjectStatus.CANCELLED},
    ProjectStatus.PROPOSAL_REVIEW: {ProjectStatus.DESIGNER_SELECTED, ProjectStatus.CANCELLED},
    ProjectStatus.DESIGNER_SELECTED: {ProjectStatus.AWAITING_PAYMENT, ProjectStatus.CANCELLED},
    ProjectStatus.AWAITING_PAYMENT: {ProjectStatus.ACTIVE, ProjectStatus.CANCELLED},
    ProjectStatus.ACTIVE: {ProjectStatus.IN_REVIEW, ProjectStatus.DISPUTED, ProjectStatus.CANCELLED},
    ProjectStatus.IN_REVIEW: {ProjectStatus.DELIVERED, ProjectStatus.ACTIVE, ProjectStatus.DISPUTED},
    ProjectStatus.DELIVERED: {ProjectStatus.COMPLETED, ProjectStatus.IN_REVIEW, ProjectStatus.DISPUTED},
    ProjectStatus.COMPLETED: set(),
    ProjectStatus.CANCELLED: set(),
    ProjectStatus.DISPUTED: {ProjectStatus.ACTIVE, ProjectStatus.COMPLETED, ProjectStatus.CANCELLED},
}

def create_project(db: FirestoreClient, client_id: str, project_in: ProjectCreate) -> ProjectOut:
    project_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)
    
    data = {
        "id": project_id,
        "clientId": client_id,
        "designerId": None,
        "selectedProposalId": None,
        "title": project_in.title,
        "category": project_in.category,
        "description": project_in.description,
        "requirements": project_in.requirements,
        "deliverables": project_in.deliverables,
        "referenceFiles": project_in.referenceFiles,
        "budget": project_in.budget,
        "deadline": project_in.deadline,
        "status": ProjectStatus.DRAFT.value,
        "currentPhase": ProjectPhase.DISCOVERY.value,
        "createdAt": now,
        "updatedAt": now,
    }
    
    db.collection("projects").document(project_id).set(data)
    return ProjectOut(**data)


def get_project(db: FirestoreClient, project_id: str) -> Optional[ProjectOut]:
    doc = db.collection("projects").document(project_id).get()
    if not doc.exists:
        return None
    return ProjectOut(**doc.to_dict())


def list_client_projects(db: FirestoreClient, client_id: str, limit: int = 20, offset: int = 0) -> List[ProjectOut]:
    docs = db.collection("projects").where("clientId", "==", client_id).order_by("createdAt", direction="DESCENDING").limit(limit).offset(offset).stream()
    return [ProjectOut(**doc.to_dict()) for doc in docs]


def update_project(db: FirestoreClient, project_id: str, project_in: ProjectUpdate) -> Optional[ProjectOut]:
    doc_ref = db.collection("projects").document(project_id)
    doc = doc_ref.get()
    if not doc.exists:
        return None
        
    current_data = doc.to_dict()
    update_data = project_in.dict(exclude_unset=True)
    
    if "status" in update_data:
        new_status = update_data["status"]
        current_status = ProjectStatus(current_data["status"])
        
        allowed = _VALID_TRANSITIONS.get(current_status, set())
        if new_status not in allowed:
            raise ValueError(f"Cannot transition project from '{current_status.value}' to '{new_status.value}'")
        
        update_data["status"] = new_status.value
        
    if "currentPhase" in update_data:
        update_data["currentPhase"] = update_data["currentPhase"].value
        
    update_data["updatedAt"] = datetime.now(timezone.utc)
    
    doc_ref.update(update_data)
    
    updated_doc = doc_ref.get()
    return ProjectOut(**updated_doc.to_dict())


def submit_proposal(db: FirestoreClient, project_id: str, designer_id: str, proposal_in: ProposalCreate) -> ProposalOut:
    # Check designer approval
    designer_docs = db.collection("designerProfiles").where("userId", "==", designer_id).limit(1).get()
    if not designer_docs or designer_docs[0].to_dict().get("applicationStatus") != "APPROVED":
        raise ValueError("Only APPROVED designers can submit proposals")
        
    project = get_project(db, project_id)
    if not project or project.status != ProjectStatus.OPEN_FOR_PROPOSALS:
        raise ValueError("Project is not open for proposals")
        
    proposal_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)
    
    data = {
        "id": proposal_id,
        "projectId": project_id,
        "designerId": designer_id,
        "proposedPrice": proposal_in.proposedPrice,
        "deliveryDays": proposal_in.deliveryDays,
        "conceptCount": proposal_in.conceptCount,
        "revisionCount": proposal_in.revisionCount,
        "approach": proposal_in.approach,
        "status": ProposalStatus.SUBMITTED.value,
        "submittedAt": now,
        "updatedAt": now,
    }
    
    db.collection("projectProposals").document(proposal_id).set(data)
    return ProposalOut(**data)


def list_project_proposals(db: FirestoreClient, project_id: str, requesting_user_id: str, is_client: bool) -> List:
    docs = db.collection("projectProposals").where("projectId", "==", project_id).stream()
    proposals = []
    
    for doc in docs:
        data = doc.to_dict()
        if is_client:
            # Client sees full proposals
            proposals.append(ProposalOut(**data))
        else:
            # Designer sees own full proposal, sanitized for others
            if data["designerId"] == requesting_user_id:
                proposals.append(ProposalOut(**data))
            else:
                proposals.append(ProposalDesignerOut(**data))
                
    return proposals


@transactional
def atomic_designer_selection(transaction: Transaction, db: FirestoreClient, project_id: str, proposal_id: str, client_id: str):
    project_ref = db.collection("projects").document(project_id)
    project_snap = project_ref.get(transaction=transaction)
    
    if not project_snap.exists:
        raise ValueError("Project not found")
        
    project_data = project_snap.to_dict()
    if project_data["clientId"] != client_id:
        raise ValueError("Unauthorized")
        
    current_status = ProjectStatus(project_data["status"])
    if current_status not in [ProjectStatus.OPEN_FOR_PROPOSALS, ProjectStatus.PROPOSAL_REVIEW]:
        raise ValueError(f"Project status '{current_status.value}' does not allow designer selection")
        
    proposal_ref = db.collection("projectProposals").document(proposal_id)
    proposal_snap = proposal_ref.get(transaction=transaction)
    
    if not proposal_snap.exists:
        raise ValueError("Proposal not found")
        
    proposal_data = proposal_snap.to_dict()
    if proposal_data["projectId"] != project_id:
        raise ValueError("Proposal does not belong to this project")
        
    designer_id = proposal_data["designerId"]
    
    # Update project
    transaction.update(project_ref, {
        "status": ProjectStatus.DESIGNER_SELECTED.value,
        "designerId": designer_id,
        "selectedProposalId": proposal_id,
        "updatedAt": datetime.now(timezone.utc)
    })
    
    # Update selected proposal
    transaction.update(proposal_ref, {
        "status": ProposalStatus.SELECTED.value,
        "updatedAt": datetime.now(timezone.utc)
    })
    
    return True


def select_designer(db: FirestoreClient, project_id: str, proposal_id: str, client_id: str):
    transaction = db.transaction()
    atomic_designer_selection(transaction, db, project_id, proposal_id, client_id)
    
    # Best-effort mark other proposals as NOT_SELECTED
    proposals = db.collection("projectProposals").where("projectId", "==", project_id).where("status", "==", ProposalStatus.SUBMITTED.value).stream()
    batch = db.batch()
    count = 0
    now = datetime.now(timezone.utc)
    for p in proposals:
        if p.id != proposal_id:
            batch.update(p.reference, {"status": ProposalStatus.NOT_SELECTED.value, "updatedAt": now})
            count += 1
            if count == 500:
                batch.commit()
                batch = db.batch()
                count = 0
    if count > 0:
        batch.commit()
        
    # Return updated project
    return get_project(db, project_id)


def accept_project(db: FirestoreClient, project_id: str, designer_id: str):
    project = get_project(db, project_id)
    if not project:
        raise ValueError("Project not found")
        
    if project.designerId != designer_id:
        raise ValueError("Unauthorized")
        
    if project.status != ProjectStatus.DESIGNER_SELECTED:
        raise ValueError("Project is not in DESIGNER_SELECTED state")
        
    db.collection("projects").document(project_id).update({
        "status": ProjectStatus.AWAITING_PAYMENT.value,
        "updatedAt": datetime.now(timezone.utc)
    })
    
    return get_project(db, project_id)
