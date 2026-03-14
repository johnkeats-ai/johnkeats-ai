"""
Memory Ingest agent. Extracts emotional markers and writes raw memory records.
"""

import json
import os
from typing import Dict
from google.genai import Client, types
from agents.prompts import load_prompt

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

    prompt = load_prompt("memory-ingest.md")

    contents = [
        prompt,
        "TRANSCRIPT: " + json.dumps(transcript),
        "ANNOTATIONS: " + json.dumps(annotations)
    ]

    response = await client.aio.models.generate_content(
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
