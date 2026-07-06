from app.utils import utcnow

def log_activity(db, user_id, activity_type, meta=None):
    db["activities"].insert_one({
        "user_id": user_id,
        "type": activity_type,
        "meta": meta or {},
        "created_at": utcnow(),
    })
