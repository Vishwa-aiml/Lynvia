from google.cloud.firestore import Client as FirestoreClient
from app.schemas.portfolio import PortfolioCreate, PortfolioUpdate, MediaCreate
from google.cloud.firestore_v1.base_query import FieldFilter
from datetime import datetime
import uuid

def create_portfolio_item(db: FirestoreClient, designer_id: str, item_in: PortfolioCreate):
    item_data = item_in.dict()
    item_data['designer_id'] = designer_id
    item_data['is_public'] = item_data.get('is_public', True)
    item_data['created_at'] = datetime.utcnow().isoformat()
    item_data['updated_at'] = datetime.utcnow().isoformat()
    
    if item_data.get('media'):
        for idx, m in enumerate(item_data['media']):
            m['id'] = str(uuid.uuid4())
            if m.get('sort_order') is None:
                m['sort_order'] = idx
            m['url'] = str(m['url'])

    doc_ref = db.collection("portfolio_items").document()
    db.collection("portfolio_items").document(doc_ref.id).set(item_data)
    item_data['id'] = doc_ref.id
    return item_data

def get_portfolio_item(db: FirestoreClient, item_id: str):
    doc = db.collection("portfolio_items").document(item_id).get()
    if doc.exists:
        data = doc.to_dict()
        data["id"] = doc.id
        return data
    return None

def list_designer_portfolio(db: FirestoreClient, designer_id: str, public_only: bool = True, limit: int = 20, offset: int = 0):
    query = db.collection("portfolio_items").where(filter=FieldFilter("designer_id", "==", designer_id))
    if public_only:
        query = query.where(filter=FieldFilter("is_public", "==", True))
    
    from google.cloud.firestore import Query
    query = query.order_by("created_at", direction=Query.DESCENDING).offset(offset).limit(limit)
    
    docs = query.stream()
    results = []
    for doc in docs:
        data = doc.to_dict()
        data["id"] = doc.id
        results.append(data)
    return results

def update_portfolio_item(db: FirestoreClient, item_id: str, item_in: PortfolioUpdate):
    item = get_portfolio_item(db, item_id)
    if not item:
        return None
    
    update_data = item_in.dict(exclude_unset=True)
    update_data['updated_at'] = datetime.utcnow().isoformat()
    
    if 'media' in update_data and update_data['media'] is not None:
        for idx, m in enumerate(update_data['media']):
            m['id'] = m.get('id', str(uuid.uuid4()))
            if m.get('sort_order') is None:
                m['sort_order'] = idx
            m['url'] = str(m['url'])
            
    db.collection("portfolio_items").document(item_id).update(update_data)
    item.update(update_data)
    return item

def delete_portfolio_item(db: FirestoreClient, item_id: str) -> bool:
    doc_ref = db.collection("portfolio_items").document(item_id)
    if not doc_ref.get().exists:
        return False
    doc_ref.delete()
    return True

def add_media(db: FirestoreClient, item_id: str, media_in: MediaCreate):
    item = get_portfolio_item(db, item_id)
    if not item:
        raise Exception("Portfolio item not found")
        
    media_data = media_in.dict()
    media_data['id'] = str(uuid.uuid4())
    media_data['url'] = str(media_data['url'])
    
    media_list = item.get('media', [])
    if media_data.get('sort_order') is None:
        media_data['sort_order'] = len(media_list)
        
    media_list.append(media_data)
    db.collection("portfolio_items").document(item_id).update({"media": media_list, "updated_at": datetime.utcnow().isoformat()})
    return media_data

def remove_media(db: FirestoreClient, item_id: str, media_id: str) -> bool:
    item = get_portfolio_item(db, item_id)
    if not item:
        return False
        
    media_list = item.get('media', [])
    new_media_list = [m for m in media_list if m.get('id') != media_id]
    
    if len(media_list) == len(new_media_list):
        return False
        
    db.collection("portfolio_items").document(item_id).update({"media": new_media_list, "updated_at": datetime.utcnow().isoformat()})
    return True
