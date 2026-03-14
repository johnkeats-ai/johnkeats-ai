"""
PII Auditor agent. Independent adversarial review.
Reads ONLY anonymised transcript. Verdicts: CLEAN / FLAGGED / BLOCKED.
"""

import json
import os
from typing import Dict
from google.genai import Client, types

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

    prompt = (
        "You are an adversarial PII auditor. Read ONLY the following anonymised transcript. "
        "Try to find remaining PII that was missed. Check for inference risks: can multiple "
        "anonymised details be combined to identify someone? Check for temporal identifiers. "
        "Verdicts: \n"
        "- BLOCKED: Any critical severity PII (full name, specific address, full credit card).\n"
        "- FLAGGED: Any high severity PII or medium inference risks.\n"
        "- CLEAN: Genuinely clean.\n"
        "When in doubt, flag. False positives are better than missed PII."
    )

    response = await client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[prompt, json.dumps(anonymised_transcript)],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=response_schema
        )
    )
    
    return json.loads(response.text)
