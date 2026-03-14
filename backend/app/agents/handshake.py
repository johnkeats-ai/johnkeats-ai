"""
Handshake processor. Scheduled batch pipeline for learning loop (Path 2).
"""

import asyncio
import logging
from google.cloud import firestore
from agents.anonymiser import anonymise_transcript
from agents.pii_auditor import audit_pii
from agents.annotation_validator import validate_annotations
from agents.anonymiser_gate import gate_decision
from agents.memory_ingest import ingest_conversation
from agents.listener_agent import score_conversation

logger = logging.getLogger(__name__)

async def handshake():
    db = firestore.Client(project="johnkeats-ai")
    
    # Pick up pending transcripts
    pending = db.collection("pending_analysis")\
                .where("retry_count", "<", 3)\
                .stream()
                
    for doc in pending:
        data = doc.to_dict()
        sid = doc.id
        raw_transcript = data["transcript"]
        
        try:
            # Stage 1-3: Anonymisation & Annotation
            anon_result = await anonymise_transcript(raw_transcript)
            
            # Stage 2: PII Audit
            pii_result = await audit_pii(anon_result["anonymised_transcript"])
            
            # Stage 3: Annotation Validation
            val_result = await validate_annotations(raw_transcript, anon_result["anonymised_transcript"], anon_result["annotations"])
            
            # Stage 4: Gate
            decision, payload = gate_decision(pii_result, val_result, data.get("retry_count", 0))
            
            if decision == "proceed":
                # Save anonymised version
                db.collection("conversations").document(sid).set({
                    "transcript": anon_result["anonymised_transcript"],
                    "annotations": payload["annotations"],
                    "annotation_uncertain": payload["uncertain"],
                    "duration_seconds": data.get("duration_seconds"),
                    "started_at": data.get("started_at"),
                    "ended_at": data.get("ended_at"),
                    "analysed": False
                })
                # Mark staging as done
                doc.reference.delete()
                logger.info(f"Handshake processed session: {sid}")
            elif decision == "quarantine":
                db.collection("quarantine").document(sid).set({
                    "reason": payload["reason"],
                    "transcript": anon_result["anonymised_transcript"],
                    "created_at": firestore.SERVER_TIMESTAMP
                })
                doc.reference.delete()
                logger.warning(f"Handshake quarantined session: {sid}")
            elif decision == "re_anonymise":
                doc.reference.update({"retry_count": firestore.Increment(1)})
                
        except Exception as e:
            logger.error(f"Handshake failed for {sid}: {e}", exc_info=True)
            doc.reference.update({"retry_count": firestore.Increment(1)})

if __name__ == "__main__":
    asyncio.run(handshake())
