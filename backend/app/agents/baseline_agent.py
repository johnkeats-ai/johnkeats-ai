"""
Baseline Agent. Cross-conversation pattern detection and anonymiser health monitoring.
Runs aggregate stats (Python) followed by trend analysis (Gemini).
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List
from google.genai import Client, types

def compute_aggregate_stats(scores: List[Dict]) -> Dict:
    """Deterministic stats computation in Python."""
    if not scores:
        return {}
        
    count = len(scores)
    stats = {
        "conversations_analysed": count,
        "avg_overall_score": sum(s["overall_score"] for s in scores) / count,
        "dimension_averages": {
            "emotional_match": sum(s["emotional_match"] for s in scores) / count,
            "curiosity": sum(s["curiosity"] for s in scores) / count,
            "silence_quality": sum(s["silence_quality"] for s in scores) / count,
            "solution_resistance": sum(s["solution_resistance"] for s in scores) / count,
            "image_quality": sum(s["image_quality"] for s in scores) / count,
            "conversation_arc": sum(s["conversation_arc"] for s in scores) / count,
        }
    }
    return stats

async def generate_baseline(db):
    """Aggregate stats and trend analysis."""
    
    # Get recent scores (e.g., last 30 days)
    # For hackathon, just get all current scores
    docs = db.collection("conversation_scores").stream()
    scores = [doc.to_dict() | {"id": doc.id} for doc in docs]
    
    if not scores:
        return {"status": "skipped", "reason": "no scores found"}
        
    stats = compute_aggregate_stats(scores)
    
    client = Client(
        vertexai=True,
        project=os.getenv("GOOGLE_CLOUD_PROJECT"),
        location=os.getenv("GOOGLE_CLOUD_LOCATION")
    )
    
    response_schema = {
        "type": "OBJECT",
        "properties": {
            "trend_directions": {"type": "OBJECT"},
            "top_strengths": {"type": "ARRAY", "items": {"type": "STRING"}},
            "top_weaknesses": {"type": "ARRAY", "items": {"type": "STRING"}},
            "anonymiser_health_note": {"type": "STRING"},
            "recommendations": {"type": "ARRAY", "items": {"type": "STRING"}}
        },
        "required": ["trend_directions", "top_strengths", "top_weaknesses", "anonymiser_health_note", "recommendations"]
    }

    prompt = (
        "You are a Baseline Agent. Analyze the following aggregate statistics from Keats's conversation scores. "
        "Identify: \n"
        "- Trend direction per dimension (improving / stable / degrading)\n"
        "- Top 3 strengths and top 3 weaknesses in Keats's attunement\n"
        "- Narrative interpretation of the data\n"
        "- Initial recommendations for the Orchestrator\n"
        "Return the analysis as JSON."
    )

    response = await client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[prompt, json.dumps(stats)],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=response_schema
        )
    )
    
    analysis = json.loads(response.text)
    
    baseline_record = stats | analysis | {"generated_at": datetime.now().isoformat()}
    db.collection("baselines").add(baseline_record)
    
    return baseline_record
