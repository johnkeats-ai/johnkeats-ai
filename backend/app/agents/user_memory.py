"""
User Memory agent. Path 1: save/retrieve/decay per-user memory (PII retained).
Sealed space, isolated per user.
"""

import os
from datetime import datetime
from google.cloud import firestore

async def save_user_memory(db, user_id: str, session_id: str, transcript: list, start_time: datetime):
    """Save full conversation to user's personal memory space. PII retained."""
    doc_ref = db.collection("users").document(user_id)\
                .collection("memories").document(session_id)
    doc_ref.set({
        "transcript": transcript,
        "started_at": start_time,
        "ended_at": firestore.SERVER_TIMESTAMP,
        "duration_seconds": int((datetime.now() - start_time).total_seconds()) if start_time else 0,
        "topics": [],
        "emotional_summary": ""
    })
    
    # Update user profile
    profile_ref = db.collection("users").document(user_id)\
                    .collection("profile").document("info")
    profile_ref.set({
        "last_seen": firestore.SERVER_TIMESTAMP,
        "sessions_count": firestore.Increment(1)
    }, merge=True)

async def get_user_context(db, user_id: str, limit: int = 3):
    """Retrieve recent conversations for this user. PII intact."""
    memories = db.collection("users").document(user_id)\
                 .collection("memories")\
                 .order_by("started_at", direction=firestore.Query.DESCENDING)\
                 .limit(limit)\
                 .stream()
    return [doc.to_dict() for doc in memories]
