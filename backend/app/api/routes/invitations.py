from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.invitation import InvitationCreate, InvitationOut
from app.api.dependencies import get_current_user, require_client_role, require_designer_role
from app.services import invitation as inv_svc
from app.models.user import User

router = APIRouter()


@router.post("/projects/{project_id}/invite", response_model=InvitationOut, status_code=status.HTTP_201_CREATED)
def invite_designer(project_id: int, invite_in: InvitationCreate, current_user: User = Depends(require_client_role), db: Session = Depends(get_db)):
    try:
        inv = inv_svc.create_invitation(db, current_user.id, project_id, invite_in.designer_id, invite_in.message)
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return inv


@router.get("/invitations/me", response_model=list[InvitationOut])
def my_invitations(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # return invitations relevant to the current user: if designer -> incoming, if client -> sent
    from app.models.user import UserRole
    if current_user.role == UserRole.DESIGNER:
        items = inv_svc.list_invitations_for_designer(db, current_user.id)
    else:
        items = inv_svc.list_invitations_for_client(db, current_user.id)
    return items


@router.post("/invitations/{invitation_id}/accept", response_model=InvitationOut)
def accept_inv(invitation_id: int, current_user: User = Depends(require_designer_role), db: Session = Depends(get_db)):
    try:
        inv = inv_svc.accept_invitation(db, invitation_id, current_user.id)
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return inv


@router.post("/invitations/{invitation_id}/reject", response_model=InvitationOut)
def reject_inv(invitation_id: int, current_user: User = Depends(require_designer_role), db: Session = Depends(get_db)):
    try:
        inv = inv_svc.reject_invitation(db, invitation_id, current_user.id)
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return inv
