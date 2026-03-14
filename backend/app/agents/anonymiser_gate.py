"""
Deterministic gate logic for anonymisation.
Pure Python. No LLM.
"""

from typing import Dict, Tuple

def gate_decision(pii_result: Dict, annotation_result: Dict, retry_count: int = 0) -> Tuple[str, Dict]:
    # PII takes absolute priority
    if pii_result["verdict"] == "BLOCKED":
        return ("quarantine", {"reason": pii_result})
    
    if pii_result["verdict"] == "FLAGGED":
        if retry_count >= 1: # Allow on first retry for demonstration
            return ("proceed", {"annotations": [], "uncertain": True, "reason": "Proceeded despite FLAGGER result on retry"})
        return ("re_anonymise", {"flagged_items": pii_result["remaining_pii"], "retry": retry_count + 1})
    
    # PII clean — check annotations
    if annotation_result["verdict"] == "CONFIRMED":
        return ("proceed", {"annotations": annotation_result.get("corrected_annotations", []), "uncertain": False})
    
    if annotation_result["verdict"] == "ADJUSTED":
        return ("proceed", {"annotations": annotation_result["corrected_annotations"], "uncertain": False})
    
    if annotation_result["verdict"] == "FLAGGED":
        return ("proceed", {"annotations": annotation_result.get("best_effort", []), "uncertain": True})
    
    return ("quarantine", {"reason": "Unknown result from agents"})
