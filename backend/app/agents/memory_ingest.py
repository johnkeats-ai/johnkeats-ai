"""
Memory Ingest agent. Extracts emotional markers and writes raw memory records.
"""

import json
import os
from typing import Dict
from google.genai import Client, types

async def ingest_conversation(db, conversation: Dict):
    """Extract emotional markers and write raw memory records."""
    session_id = conversation.get("id")
    transcript = conversation.get("transcript", [])
    annotations = conversation.get("annotations", [])
    
    client = Client(
        vertexai=True,
        project=os.getenv("GOOGLE_CLOUD_PROJECT"),
        location=os.getenv("GOOGLE_CLOUD_LOCATION")
    )
    
    response_schema = {
        "type": "OBJECT",
        "properties": {
            "summary": {"type": "STRING"},
            "emotional_arc": {"type": "ARRAY", "items": {"type": "STRING"}},
            "topics": {"type": "ARRAY", "items": {"type": "STRING"}},
            "keats_moves": {"type": "ARRAY", "items": {"type": "STRING"}},
            "silence_moments": {"type": "INTEGER"},
            "importance_rating": {"type": "NUMBER"}
        },
        "required": ["summary", "emotional_arc", "topics", "keats_moves", "silence_moments", "importance_rating"]
    }

    prompt = (
        "You are a memory ingest agent. Analyze the following anonymised transcript and its annotations. "
        "Extract: \n"
        "- Emotional arc (user emotional states across conversation)\n"
        "- Topics discussed\n"
        "- Keats moves used (tag them: curiosity, imagery, reframe, etc.)\n"
        "- Silence moments (estimate from timestamps if provided, or transcript flow)\n"
        "- Importance rating (informed by emotional weight in annotations)\n"
        "Return the analysis as JSON."
    )

    contents = [
        prompt,
        "TRANSCRIPT: " + json.dumps(transcript),
        "ANNOTATIONS: " + json.dumps(annotations)
    ]

    response = await client.models.generate_content(
        model="gemini-2.5-flash",
        contents=contents,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=response_schema
        )
    )
    
    analysis = json.loads(response.text)
    
    # Write to Firestore
    memory_ref = db.collection("memories").document("raw").collection("records").document(session_id)
    memory_ref.set({
        "session_id": session_id,
        "summary": analysis["summary"],
        "emotional_arc": analysis["emotional_arc"],
        "topics": analysis["topics"],
        "keats_moves": analysis["keats_moves"],
        "silence_count": analysis["silence_moments"],
        "importance": analysis["importance_rating"],
        "consolidated": False,
        "created_at": conversation.get("ended_at") or os.getenv("CURRENT_TIME")
    })
    
    return analysis
