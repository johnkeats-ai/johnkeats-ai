"""
Anonymiser agent for Path 2.
3-pass anonymisation: Regex (Python), Contextual PII (Gemini), Emotional Weight Annotations (Gemini).
"""

import json
import logging
import re
import os
from typing import List, Dict, Tuple
from google.genai import Client, types

logger = logging.getLogger(__name__)

PII_PATTERNS = {
    "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
    "phone": r'\b(\+?\d{1,3}[-.\s]?)?\(?\d{2,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,4}\b',
    "address": r'\b\d{1,5}\s[A-Z][a-z]+\s(?:Street|St|Road|Rd|Avenue|Ave|Drive|Dr|Lane|Ln|Boulevard|Blvd|Way|Court|Ct|Place|Pl)\b',
}

def regex_anonymise(transcript: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
    """First pass: strip obvious PII with regex. Fast, cheap, catches the basics."""
    substitutions = []
    anonymised_transcript = [dict(entry) for entry in transcript]
    
    for entry in anonymised_transcript:
        turn_text = entry.get("text", "")
        for pii_type, pattern in PII_PATTERNS.items():
            matches = re.findall(pattern, turn_text)
            for match in matches:
                turn_text = turn_text.replace(str(match), f"[{pii_type.upper()}]")
                substitutions.append({
                    "turn": entry.get("timestamp"), # Use timestamp as turn ID if turn number not available
                    "type": pii_type,
                    "original_snippet": str(match) # Be careful with original PII in logs
                })
        entry["text"] = turn_text
    return anonymised_transcript, substitutions

async def contextual_anonymise(transcript: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
    """Second and Third Pass: Gemini Flash for contextual PII and emotional annotations."""
    
    # Load prompt from file (Task 4 Step 10 requirement)
    # For now, inline until Step 10, but the spec says "Python files should import their prompts"
    # Actually I should create the prompt files now to be cleaner.
    
    client = Client(
        vertexai=True,
        project=os.getenv("GOOGLE_CLOUD_PROJECT"),
        location=os.getenv("GOOGLE_CLOUD_LOCATION")
    )
    
    # Define expected response schema
    response_schema = {
        "type": "OBJECT",
        "properties": {
            "anonymised_transcript": {
                "type": "ARRAY",
                "items": {
                    "type": "OBJECT",
                    "properties": {
                        "role": {"type": "STRING"},
                        "text": {"type": "STRING"},
                        "timestamp": {"type": "STRING"}
                    }
                }
            },
            "annotations": {
                "type": "ARRAY",
                "items": {
                    "type": "OBJECT",
                    "properties": {
                        "turn": {"type": "STRING"},
                        "category": {"type": "STRING", "enum": ["bereavement", "relationship", "health", "professional", "family", "financial", "identity", "neutral"]},
                        "specificity": {"type": "STRING", "enum": ["named_individual", "named_place", "specific_date", "general"]},
                        "recency": {"type": "STRING", "enum": ["acute_recent", "recent", "past", "distant", "unknown"]},
                        "emotional_weight_adjustment": {"type": "NUMBER"},
                        "note": {"type": "STRING"}
                    }
                }
            }
        },
        "required": ["anonymised_transcript", "annotations"]
    }

    prompt = (
        "You are an anonymization expert. Read the following transcript and replace all contextual PII "
        "(names in context, workplaces, institutions, locations, specific dates) with bracketed labels like [NAME], [LOCATION], [INSTITUTION], [DATE]. "
        "Also, for every substitution made (including any already marked as [EMAIL], [PHONE], [ADDRESS]), generate emotional weight annotations. "
        "The goal is to preserve the emotional context while removing identifiable details. "
        "Return the fully anonymised transcript and the list of annotations in the specified JSON format."
    )

    response = await client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[prompt, json.dumps(transcript)],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=response_schema
        )
    )
    
    result = json.loads(response.text)
    return result["anonymised_transcript"], result["annotations"]

async def anonymise_transcript(transcript: List[Dict]) -> Dict:
    """Full anonymisation pipeline."""
    # Pass 1
    anonymised, regex_subs = regex_anonymise(transcript)
    
    # Pass 2 & 3
    final_anonymised, annotations = await contextual_anonymise(anonymised)
    
    return {
        "anonymised_transcript": final_anonymised,
        "annotations": annotations,
        "regex_substitutions": regex_subs
    }
