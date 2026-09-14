import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Optional, List, Dict

from google.cloud.firestore import Client as FirestoreClient, Transaction, transactional, Query
from app.schemas.notification import (
    NotificationOut, PreferenceOut, PreferenceUpdate, NotificationType, NotificationListResponse
)

logger = logging.getLogger(__name__)

# -- Preferences ---------------------------------------------------------------

def get_or_create_preference(db: FirestoreClient, user_id: str, notif_type: str) -> PreferenceOut:
    prefs_ref = db.collection("users").document(user_id).collection("notificationPreferences")
    query = prefs_ref.where("notificationType", "==", notif_type).limit(1).get()
    
    if query:
        return PreferenceOut(**query[0].to_dict())
        
    pref_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)
    data = {
        "id": pref_id,
        "userId": user_id,
        "notificationType": notif_type,
        "inAppEnabled": True,
        "emailEnabled": True,
        "pushEnabled": False,
        "createdAt": now,
        "updatedAt": now
    }
    prefs_ref.document(pref_id).set(data)
    return PreferenceOut(**data)

def get_all_preferences(db: FirestoreClient, user_id: str) -> List[PreferenceOut]:
    prefs_ref = db.collection("users").document(user_id).collection("notificationPreferences")
    return [PreferenceOut(**doc.to_dict()) for doc in prefs_ref.stream()]

def update_preference(db: FirestoreClient, user_id: str, notif_type: str, updates: PreferenceUpdate) -> PreferenceOut:
    pref = get_or_create_preference(db, user_id, notif_type)
    update_data = updates.model_dump(exclude_unset=True)
    
    if not update_data:
        return pref
        
    update_data["updatedAt"] = datetime.now(timezone.utc)
    db.collection("users").document(user_id).collection("notificationPreferences").document(pref.id).update(update_data)
    
    doc = db.collection("users").document(user_id).collection("notificationPreferences").document(pref.id).get()
    return PreferenceOut(**doc.to_dict())

def _is_in_app_enabled(db: FirestoreClient, user_id: str, notif_type: str) -> bool:
    pref = get_or_create_preference(db, user_id, notif_type)
    return pref.inAppEnabled

# -- Notifications -------------------------------------------------------------

def create_notification(
    db: FirestoreClient,
    recipient_id: str,
    notification_type: NotificationType,
    title: str,
    message: str,
    actor_id: Optional[str] = None,
    entity_type: Optional[str] = None,
    entity_id: Optional[str] = None,
    meta_data: Optional[dict] = None,
) -> Optional[NotificationOut]:
    if not _is_in_app_enabled(db, recipient_id, notification_type.value):
        return None
        
    notif_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)
    data = {
        "id": notif_id,
        "recipientId": recipient_id,
        "actorId": actor_id,
        "type": notification_type.value,
        "title": title,
        "message": message,
        "entityType": entity_type,
        "entityId": entity_id,
        "metaData": json.dumps(meta_data) if meta_data else None,
        "isRead": False,
        "readAt": None,
        "createdAt": now
    }
    
    db.collection("users").document(recipient_id).collection("notifications").document(notif_id).set(data)
    return NotificationOut(**data)

def create_bulk_notifications(
    db: FirestoreClient,
    recipient_ids: List[str],
    notification_type: NotificationType,
    title: str,
    message: str,
    actor_id: Optional[str] = None,
    entity_type: Optional[str] = None,
    entity_id: Optional[str] = None,
    meta_data: Optional[dict] = None,
) -> int:
    created = 0
    batch = db.batch()
    now = datetime.now(timezone.utc)
    
    for r_id in recipient_ids:
        if not _is_in_app_enabled(db, r_id, notification_type.value):
            continue
            
        notif_id = str(uuid.uuid4())
        data = {
            "id": notif_id,
            "recipientId": r_id,
            "actorId": actor_id,
            "type": notification_type.value,
            "title": title,
            "message": message,
            "entityType": entity_type,
            "entityId": entity_id,
            "metaData": json.dumps(meta_data) if meta_data else None,
            "isRead": False,
            "readAt": None,
            "createdAt": now
        }
        
        ref = db.collection("users").document(r_id).collection("notifications").document(notif_id)
        batch.set(ref, data)
        created += 1
        
        # Batch limit in firestore is 500, if needed we can chunk it
    
    if created > 0:
        batch.commit()
    return created

def mark_as_read(db: FirestoreClient, user_id: str, notification_id: str) -> bool:
    ref = db.collection("users").document(user_id).collection("notifications").document(notification_id)
    doc = ref.get()
    if not doc.exists:
        raise ValueError("Notification not found")
        
    if doc.to_dict()["isRead"]:
        return False
        
    ref.update({
        "isRead": True,
        "readAt": datetime.now(timezone.utc)
    })
    return True

def mark_all_as_read(db: FirestoreClient, user_id: str) -> int:
    query = db.collection("users").document(user_id).collection("notifications").where("isRead", "==", False).get()
    
    if not query:
        return 0
        
    batch = db.batch()
    now = datetime.now(timezone.utc)
    count = 0
    
    for doc in query:
        batch.update(doc.reference, {"isRead": True, "readAt": now})
        count += 1
        
    if count > 0:
        batch.commit()
    return count

def get_unread_count(db: FirestoreClient, user_id: str) -> int:
    # MVP: using len of query instead of aggregation for simplicity
    query = db.collection("users").document(user_id).collection("notifications").where("isRead", "==", False).get()
    return len(query)

def get_notifications(db: FirestoreClient, user_id: str, page: int = 1, limit: int = 50) -> NotificationListResponse:
    if limit > 100:
        limit = 100
        
    notifs_ref = db.collection("users").document(user_id).collection("notifications")
    query = notifs_ref.order_by("createdAt", direction=Query.DESCENDING).limit(limit).offset((page - 1) * limit)
    
    notifications = [NotificationOut(**doc.to_dict()) for doc in query.stream()]
    unread_count = get_unread_count(db, user_id)
    
    return NotificationListResponse(
        notifications=notifications,
        total=len(notifications), # Mocking total
        page=page,
        limit=limit,
        unreadCount=unread_count
    )
