"""
Handshake processor. Scheduled batch pipeline for learning loop (Path 2).
"""

import asyncio
import logging
import os
import json
from pathlib import Path
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
env_path = Path(__file__).parent.parent.absolute() / ".env"
load_dotenv(str(env_path), override=True)

# Ensure correct project is targeted globally
os.environ["GOOGLE_CLOUD_PROJECT"] = "johnkeats-ai"
os.environ["GOOGLE_CLOUD_LOCATION"] = "us-central1"
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "TRUE"

from google.cloud import firestore
db = firestore.Client(project=os.environ["GOOGLE_CLOUD_PROJECT"])
from agents.anonymiser import anonymise_transcript
from agents.pii_auditor import audit_pii
from agents.annotation_validator import validate_annotations
from agents.anonymiser_gate import gate_decision
from agents.listener_agent import score_conversation
from agents.memory_ingest import ingest_conversation
from agents.memory_consolidate import consolidate_memories
from agents.baseline_agent import generate_baseline
from agents.orchestrator_agent import generate_insights
from agents.policy_gate import filter_recommendations


async def handshake():
    db = firestore.Client(project="johnkeats-ai")
    
    # --- PHASE 1: New Transcripts ---
    pending = list(db.collection("pending_analysis")\
                .where("retry_count", "<", 3)\
                .stream())
                
    print(f"Phase 1: Found {len(pending)} new pending documents.")
                
    for doc in pending:
        data = doc.to_dict()
        sid = doc.id
        raw_transcript = data["transcript"]
        
        try:
            # Stage 1-3: Anonymisation & Annotation
            anon_result = await anonymise_transcript(raw_transcript)
            pii_result = await audit_pii(anon_result["anonymised_transcript"])
            val_result = await validate_annotations(raw_transcript, anon_result["anonymised_transcript"], anon_result["annotations"])
            
            # Stage 4: Gate
            decision, payload = gate_decision(pii_result, val_result, data.get("retry_count", 0))
            
            if decision == "proceed":
                # Save to conversations first
                db.collection("conversations").document(sid).set({
                    "transcript": anon_result["anonymised_transcript"],
                    "annotations": payload["annotations"],
                    "annotation_uncertain": payload["uncertain"],
                    "duration_seconds": data.get("duration_seconds"),
                    "started_at": data.get("started_at"),
                    "ended_at": data.get("ended_at"),
                    "analysed": False
                })
                print(f"Anonymised session: {sid}")
            elif decision == "quarantine":
                db.collection("quarantine").document(sid).set({
                    "reason": payload["reason"],
                    "transcript": anon_result["anonymised_transcript"],
                    "created_at": firestore.SERVER_TIMESTAMP
                })
                print(f"Quarantined session: {sid}")
            
            # If we proceeded or quarantined, we can remove from pending
            if decision in ["proceed", "quarantine"]:
                doc.reference.delete()
            elif decision == "re_anonymise":
                doc.reference.update({"retry_count": firestore.Increment(1)})

        except Exception as e:
            print(f"Handshake Phase 1 error for {sid}: {e}")
            import traceback
            traceback.print_exc()
            logger.error(f"Handshake Phase 1 failed for {sid}: {e}", exc_info=True)
            try:
                doc.reference.update({"retry_count": firestore.Increment(1)})
            except:
                pass

    # --- PHASE 2: Scoring & Ingest ---
    unanalysed = list(db.collection("conversations")\
                 .where("analysed", "==", False)\
                 .stream())
    
    print(f"Phase 2: Found {len(unanalysed)} sessions to score/ingest.")
    
    for doc in unanalysed:
        sid = doc.id
        data = doc.to_dict()
        try:
            print(f"Scoring session: {sid}")
            data["id"] = sid
            await score_conversation(db, data)
            
            print(f"Ingesting memory for: {sid}")
            await ingest_conversation(db, data | {"sid": sid})
            
            # Mark as analysed
            doc.reference.update({"analysed": True})
            print(f"Completed analysis for: {sid}")

        except Exception as e:
            print(f"Handshake Phase 2 error for {sid}: {e}")
            logger.error(f"Handshake Phase 2 failed for {sid}: {e}", exc_info=True)

    # --- PHASE 3: Consolidation & Orchestration ---
    try:
        print("Checking for memory consolidation...")
        consolidation_result = await consolidate_memories(db)
        print(f"Consolidation result: {consolidation_result}")
        
        print("Generating baseline stats and trends...")
        baseline = await generate_baseline(db)
        print(f"Baseline generated: {baseline.get('avg_overall_score', 'N/A')}")
        
        print("Generating orchestrator insights...")
        insights = await generate_insights(db, baseline)
        
        print("Applying policy gate...")
        filtered = filter_recommendations(insights)
        print(f"Policy Gate: {filtered['approved_count']} approved, {filtered['rejected_count']} rejected.")
        
        # Write filtered recommendations to Firestore
        batch = db.batch()
        for note in filtered['approved_for_review']:
            note['status'] = 'pending'
            note['created_at'] = firestore.SERVER_TIMESTAMP
            db.collection('orchestrator_insights').add(note)
            
        for note in filtered['policy_rejected']:
            note['status'] = 'policy_rejected'
            note['created_at'] = firestore.SERVER_TIMESTAMP
            db.collection('orchestrator_insights').add(note)
            
        print("Full consolidation + baseline + orchestrator complete.")

    except Exception as e:
        print(f"Consolidation/Orchestration failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(handshake())
