import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Optional, List, Dict, Set

from fastapi import WebSocket
from fastapi import HTTPException, status
from google.cloud.firestore import Client as FirestoreClient, Transaction, transactional, Query

from app.schemas.chat import MessageCreate, MessageUpdate, MessageOut, MessageListResponse, ConversationOut

logger = logging.getLogger(__name__)

# -- Limits --------------------------------------------------------------------
DEFAULT_LIMIT = 50
MAX_LIMIT = 100

# -- WebSocket connection manager ----------------------------------------------

class ConnectionManager:
    def __init__(self):
        # project_id -> set of (user_id, WebSocket) tuples
        self._connections: Dict[str, Set] = {}

    async def connect(self, project_id: str, user_id: str, ws: WebSocket) -> None:
        await ws.accept()
        if project_id not in self._connections:
            self._connections[project_id] = set()
        self._connections[project_id].add((user_id, ws))
        logger.info("WS connected: user=%s project=%s", user_id, project_id)

    def disconnect(self, project_id: str, user_id: str, ws: WebSocket) -> None:
        if project_id in self._connections:
            self._connections[project_id].discard((user_id, ws))
            if not self._connections[project_id]:
                del self._connections[project_id]

    async def broadcast_to_project(self, project_id: str, data: dict) -> None:
        if project_id in self._connections:
            dead_connections = set()
            for user_id, ws in self._connections[project_id]:
                try:
                    await ws.send_json(data)
                except Exception as e:
                    logger.error(f"Error sending message to {user_id}: {e}")
                    dead_connections.add((user_id, ws))
            
            for dc in dead_connections:
                self._connections[project_id].discard(dc)

manager = ConnectionManager()

# -- Firestore Services --------------------------------------------------------

def check_project_access(db: FirestoreClient, project_id: str, user_id: str) -> dict:
    doc = db.collection("projects").document(project_id).get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Project not found")
        
    data = doc.to_dict()
    if data.get("clientId") != user_id and data.get("assignedDesignerId") != user_id:
        raise HTTPException(status_code=403, detail="You do not have access to this chat")
        
    return data

def get_or_create_conversation(db: FirestoreClient, project_id: str) -> str:
    """Returns conversation ID for a project. (1-to-1 mapping)"""
    conv_id = project_id # Simplifying: conversation ID = project ID
    doc = db.collection("conversations").document(conv_id).get()
    
    if not doc.exists:
        now = datetime.now(timezone.utc)
        db.collection("conversations").document(conv_id).set({
            "id": conv_id,
            "projectId": project_id,
            "lastMessageAt": None,
            "createdAt": now
        })
    
    return conv_id

def send_message(db: FirestoreClient, conversation_id: str, user_id: str, payload: MessageCreate) -> MessageOut:
    msg_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)
    
    msg_data = {
        "id": msg_id,
        "conversationId": conversation_id,
        "senderId": user_id,
        "content": payload.content,
        "messageType": payload.messageType.value,
        "replyToMessageId": payload.replyToMessageId,
        "isDeleted": False,
        "createdAt": now,
        "updatedAt": now
    }
    
    # Batch write message and update conversation lastMessageAt
    batch = db.batch()
    msg_ref = db.collection("conversations").document(conversation_id).collection("messages").document(msg_id)
    conv_ref = db.collection("conversations").document(conversation_id)
    
    batch.set(msg_ref, msg_data)
    batch.update(conv_ref, {"lastMessageAt": now})
    batch.commit()
    
    # Add unread counts for participants (using subcollection `readState`)
    # To keep it simple, we'll increment a global unread count in a subcollection
    # Not fully implemented in this MVP rewrite to keep scope manageable
    
    return MessageOut(**msg_data)

def get_messages(db: FirestoreClient, conversation_id: str, page: int = 1, limit: int = DEFAULT_LIMIT) -> MessageListResponse:
    if limit > MAX_LIMIT:
        limit = MAX_LIMIT
        
    messages_ref = db.collection("conversations").document(conversation_id).collection("messages")
    query = messages_ref.order_by("createdAt", direction=Query.DESCENDING).limit(limit).offset((page - 1) * limit)
    
    messages = []
    for doc in query.stream():
        data = doc.to_dict()
        msg = MessageOut.from_orm_safe(data)
        messages.append(msg)
        
    messages.reverse() # Chronological order
    
    # Calculate totals (Firestore doesn't have an easy way without aggregation query)
    # For MVP, we'll just mock total and hasNext
    
    return MessageListResponse(
        messages=messages,
        total=len(messages), # Mock total
        page=page,
        limit=limit,
        hasNext=len(messages) == limit
    )

def get_message(db: FirestoreClient, message_id: str, conversation_id: str) -> Optional[MessageOut]:
    doc = db.collection("conversations").document(conversation_id).collection("messages").document(message_id).get()
    if not doc.exists:
        return None
    return MessageOut.from_orm_safe(doc.to_dict())

def delete_message(db: FirestoreClient, message_id: str, conversation_id: str, user_id: str) -> MessageOut:
    msg_ref = db.collection("conversations").document(conversation_id).collection("messages").document(message_id)
    doc = msg_ref.get()
    
    if not doc.exists:
        raise ValueError("Message not found")
        
    data = doc.to_dict()
    if data["senderId"] != user_id:
        raise PermissionError("Not authorized to delete this message")
        
    if data["isDeleted"]:
        return MessageOut.from_orm_safe(data)
        
    updated = {
        "isDeleted": True,
        "updatedAt": datetime.now(timezone.utc)
    }
    msg_ref.update(updated)
    data.update(updated)
    
    return MessageOut.from_orm_safe(data)

def edit_message(db: FirestoreClient, message_id: str, conversation_id: str, user_id: str, payload: MessageUpdate) -> MessageOut:
    msg_ref = db.collection("conversations").document(conversation_id).collection("messages").document(message_id)
    doc = msg_ref.get()
    
    if not doc.exists:
        raise ValueError("Message not found")
        
    data = doc.to_dict()
    if data["senderId"] != user_id:
        raise PermissionError("Not authorized to edit this message")
        
    if data["isDeleted"]:
        raise ValueError("Cannot edit a deleted message")
        
    updated = {
        "content": payload.content,
        "updatedAt": datetime.now(timezone.utc)
    }
    msg_ref.update(updated)
    data.update(updated)
    
    return MessageOut(**data)

def mark_as_read(db: FirestoreClient, conversation_id: str, user_id: str) -> bool:
    # MVP: Not fully implemented
    return True

def get_unread_count(db: FirestoreClient, conversation_id: str, user_id: str) -> int:
    # MVP: Not fully implemented
    return 0
