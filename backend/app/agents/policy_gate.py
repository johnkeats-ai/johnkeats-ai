"""
Policy gate for orchestrator recommendations.
Deterministic rules. No LLM. Rejects recommendations that violate behavioural policy.
"""

from typing import Dict, List

# Prohibited recommendation patterns
PROHIBITED_PATTERNS = {
    "dependency_seeking": [
        "increase emotional intensity",
        "encourage longer sessions",
        "make the user feel they need",
        "create attachment",
        "increase reliance",
    ],
    "diagnostic_framing": [
        "diagnose", "clinical", "disorder", "condition",
        "symptoms", "treatment", "therapy",
        "depression", "anxiety disorder",  # as diagnostic labels, not as emotional states
    ],
    "manipulative_escalation": [
        "escalate emotional",
        "deepen vulnerability",
        "exploit",
        "leverage their",
        "maximize engagement",
        "optimize for retention",
    ],
    "persona_drift": [
        "be more cheerful",
        "be more upbeat",
        "sound more helpful",
        "assistant-like",
        "offer solutions more",
        "be more proactive",
    ],
    "certainty_overreach": [
        "the user needs",
        "the user wants",
        "users like this always",
        "this type of person",
        "people with this problem",
    ],
}

def check_recommendation(recommendation: Dict) -> Dict:
    """
    Check a single recommendation against policy rules.
    Returns: {passed: bool, violations: list, recommendation: dict}
    """
    text = (
        recommendation.get("recommendation", "") + " " +
        recommendation.get("evidence", "")
    ).lower()
    
    violations = []
    for category, patterns in PROHIBITED_PATTERNS.items():
        for pattern in patterns:
            if pattern.lower() in text:
                violations.append({
                    "category": category,
                    "pattern": pattern,
                    "severity": "blocked"
                })
    
    return {
        "passed": len(violations) == 0,
        "violations": violations,
        "recommendation": recommendation
    }

def filter_recommendations(orchestrator_output: Dict) -> Dict:
    """
    Filter all orchestrator recommendations through policy.
    Returns only policy-compliant recommendations for human review.
    """
    approved = []
    rejected = []
    
    for note in orchestrator_output.get("calibration_notes", []):
        result = check_recommendation(note)
        if result["passed"]:
            note["status"] = "pending"  # ready for human review
            approved.append(note)
        else:
            note["status"] = "policy_rejected"
            note["violations"] = result["violations"]
            rejected.append(note)
    
    # Weight adjustments also pass through policy
    for adj in orchestrator_output.get("weight_adjustments", []):
        if adj.get("recommended_weight", 0) <= 0 or adj.get("recommended_weight", 0) > 0.4:
            adj["status"] = "policy_rejected"
            adj["violations"] = [{"category": "weight_bounds", "pattern": "weight <= 0 or > 0.4"}]
            rejected.append(adj)
        else:
            adj["status"] = "pending"
            approved.append(adj)
    
    return {
        "approved_for_review": approved,
        "policy_rejected": rejected,
        "approved_count": len(approved),
        "rejected_count": len(rejected)
    }
