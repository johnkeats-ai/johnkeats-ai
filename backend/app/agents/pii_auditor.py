"""
PII Auditor agent. Independent adversarial review.
Reads ONLY anonymised transcript. Verdicts: CLEAN / FLAGGED / BLOCKED.
"""

import json
import os
from typing import Dict
from google.genai import Client, types
from agents.prompts import load_prompt

async def audit_pii(anonymised_transcript: list) -> Dict:
    client = Client(
        vertexai=True,
        project=os.getenv("GOOGLE_CLOUD_PROJECT"),
        location=os.getenv("GOOGLE_CLOUD_LOCATION")
    )
    
    response_schema = {
        "type": "OBJECT",
        "properties": {
            "verdict": {"type": "STRING", "enum": ["CLEAN", "FLAGGED", "BLOCKED"]},
            "remaining_pii": {
                "type": "ARRAY",
                "items": {
                    "type": "OBJECT",
                    "properties": {
                        "text": {"type": "STRING"},
                        "type": {"type": "STRING"},
                        "severity": {"type": "STRING", "enum": ["critical", "high", "medium", "low"]}
                    }
                }
            },
            "inference_risks": {"type": "ARRAY", "items": {"type": "STRING"}},
            "note": {"type": "STRING"}
        },
        "required": ["verdict", "remaining_pii", "inference_risks"]
    }

    prompt = load_prompt("pii-auditor.md")

    response = await client.aio.models.generate_content(
        model="gemini-2.5-flash",
        contents=[prompt, json.dumps(anonymised_transcript)],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=response_schema
        )
    )
    
    return json.loads(response.text)
