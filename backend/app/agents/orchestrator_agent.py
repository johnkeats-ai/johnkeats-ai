"""
Orchestrator Agent. Generates calibration recommendations targeting exact sections.
"""

import json
import os
from typing import Dict, List
from google.genai import Client, types

async def generate_insights(db, baseline: Dict):
    """Generate specific calibration recommendations based on latest baseline + pending signals."""
    
    # Get pending signals
    signal_docs = db.collection("signals").where("status", "==", "pending").stream()
    signals = [doc.to_dict() | {"id": doc.id} for doc in signal_docs]
    
    client = Client(
        vertexai=True,
        project=os.getenv("GOOGLE_CLOUD_PROJECT"),
        location=os.getenv("GOOGLE_CLOUD_LOCATION")
    )
    
    response_schema = {
        "type": "OBJECT",
        "properties": {
            "calibration_notes": {
                "type": "ARRAY",
                "items": {
                    "type": "OBJECT",
                    "properties": {
                        "target": {"type": "STRING", "enum": ["system_prompt", "kb-01", "kb-02", "kb-03", "kb-04"]},
                        "section": {"type": "STRING"},
                        "recommendation": {"type": "STRING"},
                        "evidence": {"type": "STRING"},
                        "confidence": {"type": "NUMBER"}
                    }
                }
            },
            "weight_adjustments": {
                "type": "ARRAY",
                "items": {
                    "type": "OBJECT",
                    "properties": {
                        "dimension": {"type": "STRING"},
                        "current_weight": {"type": "NUMBER"},
                        "recommended_weight": {"type": "NUMBER"},
                        "evidence": {"type": "STRING"}
                    }
                }
            },
            "anonymiser_calibration": {
                "type": "ARRAY",
                "items": {
                    "type": "OBJECT",
                    "properties": {
                        "target": {"type": "STRING"},
                        "recommendation": {"type": "STRING"},
                        "evidence": {"type": "STRING"}
                    }
                }
            },
            "next_priority": {"type": "STRING"}
        },
        "required": ["calibration_notes", "weight_adjustments", "anonymiser_calibration", "next_priority"]
    }

    prompt = (
        "You are an Orchestrator Agent. Read the latest baseline report and pending signals. "
        "Generate specific calibration recommendations targeting exact sections of the system prompt or KB files. "
        "Recommend weight adjustments for scoring dimensions based on engagement correlation evidence. "
        "Recommend anonymiser calibrations if needed. "
        "Return the analysis as JSON."
    )

    contents = [
        prompt,
        "LATEST_BASELINE: " + json.dumps(baseline),
        "PENDING_SIGNALS: " + json.dumps(signals)
    ]

    response = await client.models.generate_content(
        model="gemini-2.0-flash",
        contents=contents,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=response_schema
        )
    )
    
    insights = json.loads(response.text)
    
    # Store raw insights
    db.collection("orchestrator_insights").add(insights | {"created_at": os.getenv("CURRENT_TIME")})
    
    return insights
