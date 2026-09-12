"""
Chat routes — project-scoped messaging.

REST:
    GET    /projects/{project_id}/chat                         — conversation info
    GET    /projects/{project_id}/chat/messages                — paginated history
    POST   /projects/{project_id}/chat/messages                — send message
    GET    /projects/{project_id}/chat/messages/{message_id}   — single message
    PATCH  /projects/{project_id}/chat/messages/{message_id}   — edit message
    DELETE /projects/{project_id}/chat/messages/{message_id}   — soft-delete
    PATCH  /projects/{project_id}/chat/read                    — mark conversation read
    GET    /projects/{project_id}/chat/unread-count            — unread count

WebSocket:
    WS /ws/projects/{project_id}/chat?token=<JWT>              — real-time channel
"""
import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.chat import (
    ConversationOut, MessageCreate, MessageUpdate, MessageOut,
    MessageListResponse, ChatUnreadCountResponse, MarkChatReadResponse,
)
from app.services import chat as chat_svc
from app.utils.security import decode_access_token

logger = logging.getLogger(__name__)

router = APIRouter(tags=["chat"])


# ── Shared authorization dependency ───────────────────────────────────────────

def _resolve_project_and_conversation(
    project_id: int,
    db: Session,
    current_user: User,
):
    """Authenticate project access and return (project, conversation)."""
    try:
        project = chat_svc.check_project_access(db, project_id, current_user.id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
    conversation = chat_svc.get_or_create_conversation(db, project)
    return project, conversation


# ── REST endpoints ─────────────────────────────────────────────────────────────

@router.get("/projects/{project_id}/chat", response_model=ConversationOut)
def get_conversation(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return (or lazily create) the conversation for this project."""
    _, conversation = _resolve_project_and_conversation(project_id, db, current_user)
    return conversation


@router.get("/projects/{project_id}/chat/messages", response_model=MessageListResponse)
def list_messages(
    project_id: int,
    page: int = Query(1, ge=1),
    limit: int = Query(chat_svc.DEFAULT_LIMIT, ge=1, le=chat_svc.MAX_LIMIT),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Paginated message history (oldest to newest)."""
    _, conversation = _resolve_project_and_conversation(project_id, db, current_user)
    return chat_svc.get_messages(db, conversation.id, page=page, limit=limit)


@router.post("/projects/{project_id}/chat/messages", response_model=MessageOut, status_code=201)
def send_message(
    project_id: int,
    payload: MessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Send a new message in the project conversation."""
    _, conversation = _resolve_project_and_conversation(project_id, db, current_user)
    try:
        msg = chat_svc.send_message(db, conversation, current_user.id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    # Broadcast over WebSocket to any connected peers (non-blocking)
    import asyncio
    event = {
        "type": "message.created",
        "message": MessageOut.from_orm_safe(msg).model_dump(),
    }
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            loop.create_task(chat_svc.manager.broadcast_to_project(project_id, event))
    except Exception:
        pass  # WS broadcast failure must never fail the REST response

    return MessageOut.from_orm_safe(msg)


@router.get("/projects/{project_id}/chat/messages/{message_id}", response_model=MessageOut)
def get_single_message(
    project_id: int,
    message_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _, conversation = _resolve_project_and_conversation(project_id, db, current_user)
    msg = chat_svc.get_message(db, message_id, conversation.id)
    if not msg:
        raise HTTPException(status_code=404, detail="Message not found")
    return MessageOut.from_orm_safe(msg)


@router.patch("/projects/{project_id}/chat/messages/{message_id}", response_model=MessageOut)
def edit_message(
    project_id: int,
    message_id: int,
    payload: MessageUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _, conversation = _resolve_project_and_conversation(project_id, db, current_user)
    try:
        msg = chat_svc.edit_message(db, message_id, conversation.id, current_user.id, payload)
    except (ValueError, PermissionError) as exc:
        code = 400 if isinstance(exc, ValueError) else 403
        raise HTTPException(status_code=code, detail=str(exc))
    return MessageOut.from_orm_safe(msg)


@router.delete("/projects/{project_id}/chat/messages/{message_id}", response_model=MessageOut)
def delete_message(
    project_id: int,
    message_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _, conversation = _resolve_project_and_conversation(project_id, db, current_user)
    try:
        msg = chat_svc.delete_message(db, message_id, conversation.id, current_user.id)
    except (ValueError, PermissionError) as exc:
        code = 400 if isinstance(exc, ValueError) else 403
        raise HTTPException(status_code=code, detail=str(exc))
    return MessageOut.from_orm_safe(msg)


@router.patch("/projects/{project_id}/chat/read", response_model=MarkChatReadResponse)
def mark_chat_read(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _, conversation = _resolve_project_and_conversation(project_id, db, current_user)
    updated = chat_svc.mark_as_read(db, conversation.id, current_user.id)
    return MarkChatReadResponse(updated=updated)


@router.get("/projects/{project_id}/chat/unread-count", response_model=ChatUnreadCountResponse)
def unread_count(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _, conversation = _resolve_project_and_conversation(project_id, db, current_user)
    count = chat_svc.get_unread_count(db, conversation.id, current_user.id)
    return ChatUnreadCountResponse(unread_count=count)


# ── WebSocket endpoint ─────────────────────────────────────────────────────────

@router.websocket("/ws/projects/{project_id}/chat")
async def ws_chat(
    project_id: int,
    websocket: WebSocket,
    token: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """
    Real-time chat via WebSocket.

    Authentication: pass JWT as ?token=<access_token> query parameter.
    After connecting:
        - Client sends: {"content": "...", "message_type": "text"}
        - Server broadcasts: {"type": "message.created", "message": {...}}
    """
    # --- Authenticate ---
    if not token:
        await websocket.close(code=4001, reason="Missing token")
        logger.warning("WS rejected (no token): project=%d", project_id)
        return

    payload = decode_access_token(token)
    if not payload:
        await websocket.close(code=4001, reason="Invalid or expired token")
        logger.warning("WS rejected (invalid token): project=%d", project_id)
        return

    try:
        user_id = int(payload.get("sub", ""))
    except (ValueError, TypeError):
        await websocket.close(code=4001, reason="Invalid token payload")
        return

    from app.models.user import User as UserModel
    user = db.query(UserModel).filter(UserModel.id == user_id, UserModel.is_active == True).first()  # noqa: E712
    if not user:
        await websocket.close(code=4003, reason="User not found or inactive")
        return

    # --- Authorize project access ---
    try:
        project = chat_svc.check_project_access(db, project_id, user_id)
    except ValueError as exc:
        await websocket.close(code=4003, reason=str(exc))
        logger.warning("WS rejected (auth): user=%d project=%d reason=%s", user_id, project_id, exc)
        return

    # --- Get or create conversation ---
    conversation = chat_svc.get_or_create_conversation(db, project)

    # --- Accept connection ---
    await chat_svc.manager.connect(project_id, user_id, websocket)

    try:
        while True:
            raw = await websocket.receive_text()
            try:
                data = MessageCreate.model_validate_json(raw)
            except Exception as exc:
                await websocket.send_text(
                    '{"type":"error","detail":"Invalid message payload"}'
                )
                logger.debug("WS bad payload from user=%d: %s", user_id, exc)
                continue

            try:
                msg = chat_svc.send_message(db, conversation, user_id, data)
            except ValueError as exc:
                await websocket.send_text(
                    f'{{"type":"error","detail":"{exc}"}}'
                )
                continue

            event = {
                "type": "message.created",
                "message": MessageOut.from_orm_safe(msg).model_dump(),
            }
            await chat_svc.manager.broadcast_to_project(project_id, event)

    except WebSocketDisconnect:
        chat_svc.manager.disconnect(project_id, user_id, websocket)
    except Exception as exc:
        logger.exception("WS error: user=%d project=%d: %s", user_id, project_id, exc)
        chat_svc.manager.disconnect(project_id, user_id, websocket)
