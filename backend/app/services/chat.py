"""
Chat service — project-scoped messaging business logic.

All database operations are here; route handlers only call these.
WebSocket connections are managed by the in-process ConnectionManager.
"""
import json
import logging
from datetime import datetime, timezone
from typing import Optional, List, Dict, Set

from fastapi import WebSocket
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.chat import Conversation, ConversationParticipant, Message, MessageType
from app.models.project import Project
from app.models.profile import DesignerProfile
from app.models.notification import NotificationType
from app.schemas.chat import MessageCreate, MessageUpdate, MessageOut, MessageListResponse

logger = logging.getLogger(__name__)

# ── Limits ────────────────────────────────────────────────────────────────────
DEFAULT_LIMIT = 50
MAX_LIMIT = 100


# ── WebSocket connection manager ──────────────────────────────────────────────

class ConnectionManager:
    """In-process WebSocket manager keyed by project_id.

    Design is intentionally simple (no Redis) — replace broadcast() with a
    pub/sub publisher in a future horizontal-scaling phase.
    """

    def __init__(self):
        # project_id -> set of (user_id, WebSocket) tuples
        self._connections: Dict[int, Set] = {}

    async def connect(self, project_id: int, user_id: int, ws: WebSocket) -> None:
        await ws.accept()
        if project_id not in self._connections:
            self._connections[project_id] = set()
        self._connections[project_id].add((user_id, ws))
        logger.info("WS connected: user=%d project=%d", user_id, project_id)

    def disconnect(self, project_id: int, user_id: int, ws: WebSocket) -> None:
        if project_id in self._connections:
            self._connections[project_id].discard((user_id, ws))
            if not self._connections[project_id]:
                del self._connections[project_id]
        logger.info("WS disconnected: user=%d project=%d", user_id, project_id)

    async def broadcast_to_project(self, project_id: int, data: dict) -> None:
        """Send JSON event to all connected sockets for this project."""
        text = json.dumps(data, default=str)
        dead = []
        for uid, ws in list(self._connections.get(project_id, [])):
            try:
                await ws.send_text(text)
            except Exception:
                dead.append((uid, ws))
        # Clean up broken connections
        for entry in dead:
            self._connections.get(project_id, set()).discard(entry)


# Singleton manager — shared across all requests in the process
manager = ConnectionManager()


# ── Authorization helpers ─────────────────────────────────────────────────────

def _get_project_or_403(db: Session, project_id: int):
    """Return project or raise ValueError if not found."""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise ValueError(f"Project {project_id} not found")
    return project


def _get_designer_user_id(db: Session, designer_profile_id: int) -> Optional[int]:
    """Resolve DesignerProfile.id -> User.id."""
    profile = db.query(DesignerProfile).filter(DesignerProfile.id == designer_profile_id).first()
    return profile.user_id if profile else None


def check_project_access(db: Session, project_id: int, user_id: int) -> Project:
    """
    Verify user is either the project client OR the assigned designer.
    Returns the project on success; raises ValueError on failure.
    """
    project = _get_project_or_403(db, project_id)
    if project.client_id == user_id:
        return project
    if project.assigned_designer_id is not None:
        designer_user_id = _get_designer_user_id(db, project.assigned_designer_id)
        if designer_user_id == user_id:
            return project
    raise ValueError("Not authorized to access this project's chat")


# ── Conversation management ───────────────────────────────────────────────────

def get_or_create_conversation(db: Session, project: Project) -> Conversation:
    """
    Return the existing conversation for this project, or create one with
    the client + assigned designer as participants.
    """
    conv = db.query(Conversation).filter(Conversation.project_id == project.id).first()
    if conv:
        return conv

    conv = Conversation(project_id=project.id)
    db.add(conv)
    db.flush()  # need conv.id for participants

    # Add client
    _add_participant(db, conv.id, project.client_id)

    # Add designer if assigned
    if project.assigned_designer_id:
        designer_user_id = _get_designer_user_id(db, project.assigned_designer_id)
        if designer_user_id:
            _add_participant(db, conv.id, designer_user_id)

    db.commit()
    db.refresh(conv)
    return conv


def _add_participant(db: Session, conversation_id: int, user_id: int) -> ConversationParticipant:
    existing = db.query(ConversationParticipant).filter(
        ConversationParticipant.conversation_id == conversation_id,
        ConversationParticipant.user_id == user_id,
    ).first()
    if existing:
        return existing
    p = ConversationParticipant(conversation_id=conversation_id, user_id=user_id)
    db.add(p)
    db.flush()
    return p


def _get_participant(db: Session, conversation_id: int, user_id: int) -> Optional[ConversationParticipant]:
    return db.query(ConversationParticipant).filter(
        ConversationParticipant.conversation_id == conversation_id,
        ConversationParticipant.user_id == user_id,
    ).first()


# ── Message operations ────────────────────────────────────────────────────────

def send_message(
    db: Session,
    conversation: Conversation,
    sender_id: int,
    payload: MessageCreate,
) -> Message:
    """
    Validate and persist a new message; fire a NEW_MESSAGE notification to
    all other participants. Returns the saved Message.
    """
    # Validate reply
    if payload.reply_to_message_id is not None:
        ref = db.query(Message).filter(
            Message.id == payload.reply_to_message_id,
            Message.conversation_id == conversation.id,
        ).first()
        if not ref:
            raise ValueError("reply_to_message_id does not exist in this conversation")
        if ref.is_deleted:
            raise ValueError("Cannot reply to a deleted message")

    msg = Message(
        conversation_id=conversation.id,
        sender_id=sender_id,
        content=payload.content.strip(),
        message_type=payload.message_type,
        reply_to_message_id=payload.reply_to_message_id,
    )
    db.add(msg)

    # Update conversation.last_message_at
    conversation.last_message_at = datetime.now(timezone.utc)
    db.add(conversation)
    db.flush()

    # Notify other participants (lazy import avoids circular)
    try:
        from app.services import notifications as notif_svc
        participants = db.query(ConversationParticipant).filter(
            ConversationParticipant.conversation_id == conversation.id,
            ConversationParticipant.user_id != sender_id,
        ).all()
        for p in participants:
            notif_svc.create_notification(
                db=db,
                recipient_id=p.user_id,
                actor_id=sender_id,
                notification_type=NotificationType.NEW_MESSAGE,
                title="New message",
                message="You have a new message in your project chat.",
                entity_type="conversation",
                entity_id=conversation.id,
                meta_data={"project_id": conversation.project_id},
            )
    except Exception:
        logger.warning("Failed to create NEW_MESSAGE notifications; continuing", exc_info=True)

    db.commit()
    db.refresh(msg)
    return msg


def get_messages(
    db: Session,
    conversation_id: int,
    page: int = 1,
    limit: int = DEFAULT_LIMIT,
) -> MessageListResponse:
    """Paginated message history, oldest-to-newest."""
    limit = min(max(limit, 1), MAX_LIMIT)
    page = max(page, 1)
    offset = (page - 1) * limit

    total = db.query(func.count(Message.id)).filter(
        Message.conversation_id == conversation_id,
    ).scalar() or 0

    messages = (
        db.query(Message)
        .filter(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    return MessageListResponse(
        messages=[MessageOut.from_orm_safe(m) for m in messages],
        total=total,
        page=page,
        limit=limit,
        has_next=(offset + limit) < total,
    )


def get_message(db: Session, message_id: int, conversation_id: int) -> Optional[Message]:
    return db.query(Message).filter(
        Message.id == message_id,
        Message.conversation_id == conversation_id,
    ).first()


def delete_message(db: Session, message_id: int, conversation_id: int, user_id: int) -> Message:
    """Soft-delete a message. Only the sender may delete."""
    msg = get_message(db, message_id, conversation_id)
    if not msg:
        raise ValueError("Message not found")
    if msg.sender_id != user_id:
        raise PermissionError("You can only delete your own messages")
    if msg.is_deleted:
        return msg  # idempotent
    msg.is_deleted = True
    msg.deleted_at = datetime.now(timezone.utc)
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg


def edit_message(db: Session, message_id: int, conversation_id: int, user_id: int, payload: MessageUpdate) -> Message:
    """Edit a message's content. Only the sender may edit; cannot edit deleted messages."""
    msg = get_message(db, message_id, conversation_id)
    if not msg:
        raise ValueError("Message not found")
    if msg.sender_id != user_id:
        raise PermissionError("You can only edit your own messages")
    if msg.is_deleted:
        raise ValueError("Cannot edit a deleted message")
    msg.content = payload.content.strip()
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg


# ── Read receipts ─────────────────────────────────────────────────────────────

def mark_as_read(db: Session, conversation_id: int, user_id: int) -> bool:
    """
    Update the participant's last_read_message_id to the most recent message.
    Returns True if updated.
    """
    participant = _get_participant(db, conversation_id, user_id)
    if not participant:
        return False

    latest = (
        db.query(Message)
        .filter(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.desc())
        .first()
    )
    if not latest:
        return False

    participant.last_read_message_id = latest.id
    participant.last_read_at = datetime.now(timezone.utc)
    db.add(participant)
    db.commit()
    return True


def get_unread_count(db: Session, conversation_id: int, user_id: int) -> int:
    """
    Count messages after the participant's last read position.
    """
    participant = _get_participant(db, conversation_id, user_id)
    if not participant:
        return 0

    query = db.query(func.count(Message.id)).filter(
        Message.conversation_id == conversation_id,
        Message.sender_id != user_id,
    )
    if participant.last_read_message_id is not None:
        # Only messages after their last read point
        last_read_msg = db.query(Message).filter(
            Message.id == participant.last_read_message_id
        ).first()
        if last_read_msg:
            query = query.filter(Message.created_at > last_read_msg.created_at)

    return query.scalar() or 0
