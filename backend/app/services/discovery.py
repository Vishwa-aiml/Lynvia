from google.cloud.firestore import Client as FirestoreClient
from typing import List, Optional

def search_designers(
    db: FirestoreClient,
    skills: Optional[List[str]] = None,
    category: Optional[str] = None,
    min_experience: Optional[int] = None,
    max_experience: Optional[int] = None,
    location: Optional[str] = None,
    min_rate: Optional[int] = None,
    max_rate: Optional[int] = None,
    available_day: Optional[int] = None,
    limit: int = 20,
    offset: int = 0,
    sort: Optional[str] = None,
):
    # Fetch active designers from Firestore
    # We query the "designer_profiles" collection
    query = db.collection("designer_profiles")
    
    if min_experience is not None:
        query = query.where("years_experience", ">=", min_experience)
    if max_experience is not None:
        query = query.where("years_experience", "<=", max_experience)
    if min_rate is not None:
        query = query.where("hourly_rate", ">=", min_rate)
    if max_rate is not None:
        query = query.where("hourly_rate", "<=", max_rate)
    
    if sort == 'rate_asc':
        query = query.order_by("hourly_rate")
    elif sort == 'rate_desc':
        from google.cloud.firestore import Query
        query = query.order_by("hourly_rate", direction=Query.DESCENDING)
    elif sort == 'experience_desc':
        from google.cloud.firestore import Query
        query = query.order_by("years_experience", direction=Query.DESCENDING)
    
    docs = query.limit(100).stream() # fetch a batch to apply in-memory filters for complex queries (skills, location)
    
    profiles = []
    for doc in docs:
        p = doc.to_dict()
        p['id'] = doc.id
        
        # In-memory filtering for location (case-insensitive substring)
        if location and location.lower() not in p.get("location", "").lower():
            continue
            
        # In-memory filtering for skills
        if skills:
            p_skills = [s.lower() for s in p.get("skills", [])]
            if not any(s.lower() in p_skills for s in skills):
                continue
                
        # In-memory filtering for category
        if category and p.get("category") != category:
            continue
            
        # In-memory filtering for availability
        if available_day is not None:
            avail = p.get("availability", [])
            if available_day not in avail:
                continue
                
        profiles.append(p)
        
    # Apply offset and limit
    paginated_profiles = profiles[offset:offset+limit]
    
    results = []
    for p in paginated_profiles:
        # Fetch related data if necessary, or assume it's embedded in the profile document
        results.append({
            'id': p['id'],
            'user_id': p.get('user_id'),
            'headline': p.get('headline'),
            'bio': p.get('bio'),
            'location': p.get('location'),
            'hourly_rate': p.get('hourly_rate'),
            'years_experience': p.get('years_experience'),
            'services': p.get('services', []),
            'skills': p.get('skills', []),
            'specializations': p.get('specializations', []),
            'portfolio_count': p.get('portfolio_count', 0),
        })

    return results

def search_projects(
    db: FirestoreClient,
    category: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
):
    query = db.collection("projects").where("status", "==", "OPEN_FOR_PROPOSALS")
    
    if category:
        query = query.where("category", "==", category)
        
    docs = query.limit(limit).offset(offset).stream()
    
    results = []
    for doc in docs:
        p = doc.to_dict()
        p['id'] = doc.id
        results.append(p)
        
    return results
