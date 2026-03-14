"""
Listener agent for structured scoring of Keats's attunement quality.
6 attunement dimensions + 1 self-monitoring dimension.
"""

import json
import os
from typing import Dict, List
from google.genai import Client, types

def compute_deterministic_metrics(transcript: List[Dict]) -> Dict:
    """Python computes deterministic signals."""
    metrics = {
        "user_turns": 0,
        "keats_turns": 0,
        "avg_user_turn_length": 0,
        "silence_count": 0,
        "repetition_flags": []
    }
    
    user_texts = []
    keats_texts = []
    
    for entry in transcript:
        text = entry.get("text", "")
        if entry.get("role") == "user":
            metrics["user_turns"] += 1
            user_texts.append(text)
        else:
            metrics["keats_turns"] += 1
            keats_texts.append(text)
            
            # Simple repetition check
            if any(text == prev for prev in keats_texts[:-1]):
                metrics["repetition_flags"].append(f"Repeated full response: {text[:50]}...")
    
    if user_texts:
        metrics["avg_user_turn_length"] = sum(len(t) for t in user_texts) / len(user_texts)
        
    return metrics

async def score_conversation(db, conversation: Dict):
    """Structured emotional attunement scoring with annotation weighting."""
    session_id = conversation.get("id")
    transcript = conversation.get("transcript", [])
    annotations = conversation.get("annotations", [])
    
    deterministic = compute_deterministic_metrics(transcript)
    
    client = Client(
        vertexai=True,
        project=os.getenv("GOOGLE_CLOUD_PROJECT"),
        location=os.getenv("GOOGLE_CLOUD_LOCATION")
    )
    
    response_schema = {
        "type": "OBJECT",
        "properties": {
            "emotional_match": {"type": "NUMBER"},
            "curiosity": {"type": "NUMBER"},
            "silence_quality": {"type": "NUMBER"},
            "solution_resistance": {"type": "NUMBER"},
            "image_quality": {"type": "NUMBER"},
            "conversation_arc": {"type": "NUMBER"},
            "repetition_score": {"type": "NUMBER"},
            "overall_score": {"type": "NUMBER"},
            "qualitative_summary": {"type": "STRING"},
            "best_moment": {"type": "STRING"},
            "worst_moment": {"type": "STRING"}
        },
        "required": ["emotional_match", "curiosity", "silence_quality", "solution_resistance", "image_quality", "conversation_arc", "repetition_score", "overall_score", "qualitative_summary"]
    }

    prompt = (
        "You are a Listener agent evaluating Keats's attunement quality. "
        "Score from 0.0 to 1.0 on: \n"
        "- EMOTIONAL_MATCH: How well Keats matched user state. Weight turns with emotional annotations > 0.5 as 2x.\n"
        "- CURIOSITY: Count specific vs generic questions.\n"
        "- SILENCE_QUALITY: Assessment of productive silence.\n"
        "- SOLUTION_RESISTANCE: Did Keats resist giving advice or solutions?\n"
        "- IMAGE_QUALITY: Specificity and grounding of imagery.\n"
        "- CONVERSATION_ARC: Organic flow vs forced shifts.\n"
        "- REPETITION: Qualitative detection of repeated moves.\n"
        "Return the scores and a qualitative summary as JSON."
    )

    contents = [
        prompt,
        "TRANSCRIPT: " + json.dumps(transcript),
        "ANNOTATIONS: " + json.dumps(annotations),
        "DETERMINISTIC_METRICS: " + json.dumps(deterministic)
    ]

    response = await client.models.generate_content(
        model="gemini-2.0-flash",
        contents=contents,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=response_schema
        )
    )
    
    scores = json.loads(response.text)
    
    # Write scores to Firestore
    score_ref = db.collection("conversation_scores").document(session_id)
    score_ref.set({
        "session_id": session_id,
        "emotional_match": scores["emotional_match"],
        "curiosity": scores["curiosity"],
        "silence_quality": scores["silence_quality"],
        "solution_resistance": scores["solution_resistance"],
        "image_quality": scores["image_quality"],
        "conversation_arc": scores["conversation_arc"],
        "keats_repetition": scores["repetition_score"],
        "overall_score": scores["overall_score"],
        "repetition_flags": deterministic["repetition_flags"],
        "qualitative_summary": scores["qualitative_summary"],
        "best_moment": scores.get("best_moment"),
        "worst_moment": scores.get("worst_moment"),
        "created_at": conversation.get("ended_at") or os.getenv("CURRENT_TIME")
    })
    
    return scores
