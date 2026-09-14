from fastapi import APIRouter, Depends
from google.cloud.firestore import Client as FirestoreClient
from app.db.firebase import get_db
from app.api.dependencies import require_admin_role
from app.models.user import User

router = APIRouter(tags=["admin"])

@router.get("/admin/stats")
def get_platform_stats(
    db: FirestoreClient = Depends(get_db),
    admin_user: User = Depends(require_admin_role)
):
    """Get high-level platform statistics for the admin dashboard."""
    # MVP: Basic aggregation by counting documents.
    # In production, use Firebase aggregations or a scheduled cloud function
    # to maintain counters instead of reading all documents.
    
    users_count = len(list(db.collection("users").stream()))
    projects_count = len(list(db.collection("projects").stream()))
    disputes_count = len(list(db.collection("disputes").where("status", "==", "OPEN").stream()))
    withdrawals_count = len(list(db.collection("withdrawals").where("status", "==", "REQUESTED").stream()))
    
    return {
        "totalUsers": users_count,
        "totalProjects": projects_count,
        "openDisputes": disputes_count,
        "pendingWithdrawals": withdrawals_count
    }
