"""
Annotation Validator agent. Independent adversarial review.
Checks emotional weights and substitution labels.
"""

import json
import os
from typing import Dict
from google.genai import Client, types
from agents.prompts import load_prompt

async def validate_annotations(original_transcript: list, anonymised_transcript: list, annotations: list) -> Dict:
    client = Client(
        vertexai=True,
        project=os.getenv("GOOGLE_CLOUD_PROJECT"),
        location=os.getenv("GOOGLE_CLOUD_LOCATION")
    )
    
    response_schema = {
        "type": "OBJECT",
        "properties": {
            "verdict": {"type": "STRING", "enum": ["CONFIRMED", "ADJUSTED", "FLAGGED"]},
            "corrected_annotations": {
                "type": "ARRAY",
                "items": {
                    "type": "OBJECT",
                    "properties": {
                        "turn": {"type": "STRING"},
                        "category": {"type": "STRING"},
                        "emotional_weight_adjustment": {"type": "NUMBER"},
                        "note": {"type": "STRING"}
                    }
                }
            },
            "best_effort": {"type": "ARRAY", "items": {"type": "OBJECT"}},
            "note": {"type": "STRING"}
        },
        "required": ["verdict", "corrected_annotations"]
    }

    prompt = load_prompt("annotation-validator.md")

    contents = [
        prompt,
        "ORIGINAL: " + json.dumps(original_transcript),
        "ANONYMISED: " + json.dumps(anonymised_transcript),
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
    
    return json.loads(response.text)
