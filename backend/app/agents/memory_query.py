"""
Memory Query agent. Retrieves personal + system context.
"""

from typing import List, Dict

async def get_conversation_context(db, user_id: str):
    """Called at conversation start. Returns personal + system context."""
    
    # Path 1: Personal context (what does Keats know about THIS person?)
    # For now, return recent memory summaries
    memories = db.collection("users").document(user_id) \
                 .collection("memories") \
                 .order_by("started_at", direction="DESCENDING") \
                 .limit(3).stream()
    
    personal_context = [doc.to_dict().get("summary", "No summary available") for doc in memories]
    
    # Path 2: System context (what has the system learned about attunement?)
    insights = db.collection("signals") \
                 .where("status", "==", "accepted") \
                 .order_by("confidence", direction="DESCENDING") \
                 .limit(5).stream()
                 
    system_insights = [doc.to_dict().get("recommendation") for doc in insights]
    
    return {
        "personal": personal_context,
        "system": system_insights
    }
