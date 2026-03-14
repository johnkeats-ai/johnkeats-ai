"""
Run the full analysis pipeline manually for testing.
"""

import asyncio
import os
import json
from google.cloud import firestore
from agents.memory_ingest import ingest_conversation
from agents.listener_agent import score_conversation
from agents.baseline_agent import generate_baseline
from agents.orchestrator_agent import generate_insights
from agents.policy_gate import filter_recommendations

async def run():
    db = firestore.Client(project="johnkeats-ai")
    
    # Find unanalysed conversations in Path 2 (anonymised)
    # For testing, we might need to manually trigger ingest/score for new documents
    convos = db.collection("conversations").where("analysed", "==", False).stream()
    conversation_list = [doc.to_dict() | {"id": doc.id} for doc in convos]
    print(f"Found {len(conversation_list)} unanalysed conversations")
    
    for conv in conversation_list:
        sid = conv["id"]
        
        # Memory Ingest
        print(f"  [{sid}] Ingesting...")
        await ingest_conversation(db, conv)
        
        # Listener scoring
        print(f"  [{sid}] Scoring...")
        scores = await score_conversation(db, conv)
        print(f"  [{sid}] Overall Score: {scores['overall_score']}")
        
        # Mark as analysed
        db.collection("conversations").document(sid).update({"analysed": True})
    
    # Run Downstream if enough conversations
    if len(conversation_list) >= 0: # Threshold 3 in production, 0 for testing
        print("\nGenerating Baseline...")
        baseline = await generate_baseline(db)
        
        print("\nGenerating Orchestrator Insights...")
        insights = await generate_insights(db, baseline)
        
        print("\nApplying Policy Gate...")
        filtered = filter_recommendations(insights)
        print(f"Approved: {filtered['approved_count']}, Rejected: {filtered['rejected_count']}")
        
        # Write approved to Firestore
        for note in filtered["approved_for_review"]:
            db.collection("calibration_queue").add(note | {"created_at": firestore.SERVER_TIMESTAMP})

if __name__ == "__main__":
    asyncio.run(run())
