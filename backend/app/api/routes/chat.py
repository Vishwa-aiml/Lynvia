import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect, status
from google.cloud.firestore import Client as FirestoreClient

from app.api.dependencies import get_current_user
from app.db.firebase import get_db
from app.models.user import User
from app.schemas.chat import (
    ConversationOut, MessageCreate, MessageUpdate, MessageOut,
    MessageListResponse, ChatUnreadCountResponse, MarkChatReadResponse,
)
from app.services import chat as chat_svc
from app.utils.security import decode_access_token

logger = logging.getLogger(__name__)
router = APIRouter(tags=["chat"])

def _resolve_project_and_conversation(
    project_id: str,
    db: FirestoreClient,
    current_user: User,
):
    try:
        project_data = chat_svc.check_project_access(db, project_id, current_user.id)
    except HTTPException as exc:
        raise exc
        
    conversation_id = chat_svc.get_or_create_conversation(db, project_id)
    return project_data, conversation_id

# -- REST Endpoints ------------------------------------------------------------

@router.get("/projects/{project_id}/chat", response_model=ConversationOut)
def get_conversation(
    project_id: str,
    db: FirestoreClient = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _, conv_id = _resolve_project_and_conversation(project_id, db, current_user)
    doc = db.collection("conversations").document(conv_id).get()
    return ConversationOut(**doc.to_dict())

@router.get("/projects/{project_id}/chat/messages", response_model=MessageListResponse)
def list_messages(
    project_id: str,
    page: int = Query(1, ge=1),
    limit: int = Query(chat_svc.DEFAULT_LIMIT, ge=1, le=chat_svc.MAX_LIMIT),
    db: FirestoreClient = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _, conv_id = _resolve_project_and_conversation(project_id, db, current_user)
    return chat_svc.get_messages(db, conv_id, page, limit)

@router.post("/projects/{project_id}/chat/messages", response_model=MessageOut, status_code=status.HTTP_201_CREATED)
def send_message(
    project_id: str,
    payload: MessageCreate,
    db: FirestoreClient = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _, conv_id = _resolve_project_and_conversation(project_id, db, current_user)
    msg = chat_svc.send_message(db, conv_id, current_user.id, payload)
    return msg

@router.get("/projects/{project_id}/chat/messages/{message_id}", response_model=MessageOut)
def get_single_message(
    project_id: str,
    message_id: str,
    db: FirestoreClient = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _, conv_id = _resolve_project_and_conversation(project_id, db, current_user)
    msg = chat_svc.get_message(db, message_id, conv_id)
    if not msg:
        raise HTTPException(status_code=404, detail="Message not found")
    return msg

@router.patch("/projects/{project_id}/chat/messages/{message_id}", response_model=MessageOut)
def edit_message(
    project_id: str,
    message_id: str,
    payload: MessageUpdate,
    db: FirestoreClient = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _, conv_id = _resolve_project_and_conversation(project_id, db, current_user)
    try:
        return chat_svc.edit_message(db, message_id, conv_id, current_user.id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc))

@router.delete("/projects/{project_id}/chat/messages/{message_id}", response_model=MessageOut)
def delete_message(
    project_id: str,
    message_id: str,
    db: FirestoreClient = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _, conv_id = _resolve_project_and_conversation(project_id, db, current_user)
    try:
        return chat_svc.delete_message(db, message_id, conv_id, current_user.id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc))

@router.patch("/projects/{project_id}/chat/read", response_model=MarkChatReadResponse)
def mark_chat_read(
    project_id: str,
    db: FirestoreClient = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _, conv_id = _resolve_project_and_conversation(project_id, db, current_user)
    updated = chat_svc.mark_as_read(db, conv_id, current_user.id)
    return MarkChatReadResponse(updated=updated)

@router.get("/projects/{project_id}/chat/unread-count", response_model=ChatUnreadCountResponse)
def unread_count(
    project_id: str,
    db: FirestoreClient = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _, conv_id = _resolve_project_and_conversation(project_id, db, current_user)
    count = chat_svc.get_unread_count(db, conv_id, current_user.id)
    return ChatUnreadCountResponse(unreadCount=count)

# -- WebSocket -----------------------------------------------------------------

@router.websocket("/ws/projects/{project_id}/chat")
async def ws_chat(
    websocket: WebSocket,
    project_id: str,
    token: str,
    db: FirestoreClient = Depends(get_db)
):
    try:
        payload = decode_access_token(token)
        user_id = payload.get("sub")
        if not user_id:
            raise ValueError("Invalid token subject")
    except Exception as exc:
        logger.warning(f"WS auth failed: {exc}")
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    try:
        chat_svc.check_project_access(db, project_id, user_id)
    except HTTPException:
        logger.warning(f"WS access denied: user={user_id} project={project_id}")
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await chat_svc.manager.connect(project_id, user_id, websocket)

    try:
        while True:
            await websocket.receive_text()
            # Just keeping connection alive for MVP
    except WebSocketDisconnect:
        chat_svc.manager.disconnect(project_id, user_id, websocket)
