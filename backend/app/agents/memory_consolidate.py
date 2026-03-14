"""
Memory Consolidate agent. Finds cross-conversation patterns and generates Signals.
"""

import json
import os
from typing import List, Dict
from google.genai import Client, types
from google.cloud import firestore

async def consolidate_memories(db):
    """Triggered after 3+ new scored conversations. Finds cross-conversation connections."""
    
    # Read unconsolidated raw memories
    docs = db.collection("memories").document("raw").collection("records") \
             .where("consolidated", "==", False).stream()
    
    unconsolidated = [doc.to_dict() | {"id": doc.id} for doc in docs]
    
    if len(unconsolidated) < 3:
        return {"status": "skipped", "reason": "not enough memories to consolidate"}

    client = Client(
        vertexai=True,
        project=os.getenv("GOOGLE_CLOUD_PROJECT"),
        location=os.getenv("GOOGLE_CLOUD_LOCATION")
    )
    
    response_schema = {
        "type": "OBJECT",
        "properties": {
            "connections": {
                "type": "ARRAY",
                "items": {
                    "type": "OBJECT",
                    "properties": {
                        "memory_a": {"type": "STRING"},
                        "memory_b": {"type": "STRING"},
                        "relationship": {"type": "STRING"}
                    }
                }
            },
            "signals": {
                "type": "ARRAY",
                "items": {
                    "type": "OBJECT",
                    "properties": {
                        "target": {"type": "STRING", "enum": ["system_prompt", "kb-01", "kb-02", "kb-03", "kb-04", "scoring_weights"]},
                        "section": {"type": "STRING"},
                        "finding": {"type": "STRING"},
                        "confidence": {"type": "NUMBER"},
                        "recommendation": {"type": "STRING"}
                    }
                }
            }
        },
        "required": ["connections", "signals"]
    }

    prompt = (
        "You are a memory consolidation agent. Read the following raw memory records from multiple conversations. "
        "Find cross-conversation connections and patterns: \n"
        "- Which imagery domains correlate with engagement?\n"
        "- Which moves correlate with longer conversations?\n"
        "- Which patterns precede drop-offs?\n"
        "Generate Signals targeting specific prompt/KB sections for improvement. "
        "Return the analysis as JSON."
    )

    response = await client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[prompt, json.dumps(unconsolidated)],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=response_schema
        )
    )
    
    result = json.loads(response.text)
    
    # Write Signals and mark memories as consolidated
    batch = db.batch()
    for sig in result["signals"]:
        sig_ref = db.collection("signals").document()
        batch.set(sig_ref, sig | {"status": "pending", "created_at": firestore.SERVER_TIMESTAMP})
        
    for mem in unconconsolidated:
        mem_ref = db.collection("memories").document("raw").collection("records").document(mem["id"])
        batch.update(mem_ref, {"consolidated": True})
        
    await batch.commit()
    
    return result
