"""FastAPI application demonstrating ADK Gemini Live API Toolkit with WebSocket."""

import asyncio
import base64
import json
import logging
import os
import uuid
import warnings
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from google.adk.agents.live_request_queue import LiveRequestQueue
from google.adk.agents.run_config import RunConfig, StreamingMode
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

# Load environment variables from env_file BEFORE importing agent
env_path = Path(__file__).parent.absolute() / "env_file"
load_dotenv(str(env_path))

# Import agent after loading environment variables
# pylint: disable=wrong-import-position
from keats_agent.agent import keats_agent

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Suppress Pydantic serialization warnings
warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")

# Application name constant
APP_NAME = "johnkeats-ai"

# ========================================
# Phase 1: Application Initialization (once at startup)
# ========================================

app = FastAPI()

# Mount static files
static_dir = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Define your session service
session_service = InMemorySessionService()

# Define your runner
runner = Runner(app_name=APP_NAME, agent=keats_agent, session_service=session_service)

# ========================================
# HTTP Endpoints
# ========================================


@app.get("/")
async def root():
    """Serve the index.html page."""
    return FileResponse(Path(__file__).parent / "static" / "index.html")


# ========================================
# WebSocket Endpoint
# ========================================


@app.websocket("/ws/{user_id}/{session_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    user_id: str,
    session_id: str,
    proactivity: bool = False,
    affective_dialog: bool = False,
) -> None:
    """WebSocket endpoint for bidirectional streaming with ADK."""
    
    # Bug 3: Generate unique session ID to prevent context leak between users
    effective_session_id = f"{session_id}-{uuid.uuid4().hex[:8]}"
    
    logger.debug(
        f"WebSocket connection request: user_id={user_id}, session_id={session_id}, "
        f"effective_session_id={effective_session_id}, "
        f"proactivity={proactivity}, affective_dialog={affective_dialog}"
    )
    await websocket.accept()
    logger.debug(f"WebSocket connection accepted for session: {effective_session_id}")

    # ========================================
    # Phase 2: Session Initialization (once per streaming session)
    # ========================================

    # Automatically determine response modality based on model architecture
    # Native audio models (containing "native-audio" in name)
    # ONLY support AUDIO response modality.
    model_name = keats_agent.model
    is_native_audio = "native-audio" in model_name.lower()

    if is_native_audio:
        # Native audio models require AUDIO response modality
        run_config = RunConfig(
            streaming_mode=StreamingMode.BIDI,
            response_modalities=["AUDIO"],
            speech_config=types.SpeechConfig(
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(
                        voice_name=os.getenv("KEATS_VOICE_NAME", "Achird")
                    )
                )
            ),
            input_audio_transcription=types.AudioTranscriptionConfig(),
            output_audio_transcription=types.AudioTranscriptionConfig(),
            session_resumption=types.SessionResumptionConfig(),
        )
        logger.debug(
            f"Native audio model detected: {model_name}, "
            f"using AUDIO response modality with voice: {os.getenv('KEATS_VOICE_NAME')}"
        )
    else:
        # Half-cascade models support TEXT response modality
        # for faster performance
        response_modalities = ["TEXT"]
        run_config = RunConfig(
            streaming_mode=StreamingMode.BIDI,
            response_modalities=response_modalities,
            input_audio_transcription=None,
            output_audio_transcription=None,
            session_resumption=types.SessionResumptionConfig(),
        )
        logger.debug(
            f"Half-cascade model detected: {model_name}, "
            "using TEXT response modality"
        )
        # Warn if user tried to enable native-audio-only features
        if proactivity or affective_dialog:
            logger.warning(
                f"Proactivity and affective dialog are only supported on native "
                f"audio models. Current model: {model_name}. "
                f"These settings will be ignored."
            )
    logger.debug(f"RunConfig created: {run_config}")

    # Get or create session (handles both new sessions and reconnections)
    session = await session_service.get_session(
        app_name=APP_NAME, user_id=user_id, session_id=effective_session_id
    )
    if not session:
        await session_service.create_session(
            app_name=APP_NAME, user_id=user_id, session_id=effective_session_id
        )

    live_request_queue = LiveRequestQueue()

    # ========================================
    # Phase 3: Active Session (concurrent bidirectional communication)
    # ========================================

    async def upstream_task() -> None:
        """Receives messages from WebSocket and sends to LiveRequestQueue."""
        logger.debug("upstream_task started")
        try:
            while True:
                # Receive message from WebSocket (text or binary)
                message = await websocket.receive()

                # Handle binary frames (audio data)
                if "bytes" in message:
                    audio_data = message["bytes"]
                    logger.debug(f"Received binary audio chunk: {len(audio_data)} bytes")

                    audio_blob = types.Blob(
                        mime_type="audio/pcm;rate=16000", data=audio_data
                    )
                    live_request_queue.send_realtime(audio_blob)

                # Handle text frames (JSON messages)
                elif "text" in message:
                    text_data = message["text"]
                    logger.debug(f"Received text message: {text_data[:100]}...")

                    json_message = json.loads(text_data)

                    # Extract text from JSON and send to LiveRequestQueue
                    if json_message.get("type") == "text":
                        logger.debug(f"Sending text content: {json_message['text']}")
                        content = types.Content(
                            parts=[types.Part(text=json_message["text"])]
                        )
                        live_request_queue.send_content(content)

                    # Handle image data
                    elif json_message.get("type") == "image":
                        logger.debug("Received image data")

                        # Decode base64 image data
                        image_data = base64.b64decode(json_message["data"])
                        mime_type = json_message.get("mimeType", "image/jpeg")

                        logger.debug(
                            f"Sending image: {len(image_data)} bytes, " f"type: {mime_type}"
                        )

                        # Send image as blob
                        image_blob = types.Blob(mime_type=mime_type, data=image_data)
                        live_request_queue.send_realtime(image_blob)
        except (RuntimeError, WebSocketDisconnect):
            logger.info(f"Browser disconnected for session {effective_session_id}")
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"Error in upstream_task: {e}", exc_info=True)

    async def downstream_task() -> None:
        """Receives Events from run_live() and sends to WebSocket."""
        logger.debug(f"downstream_task started for session {effective_session_id}")
        max_retries = 3
        retries = 0
        try:
            while retries < max_retries:
                try:
                    async for event in runner.run_live(
                        user_id=user_id,
                        session_id=effective_session_id,
                        live_request_queue=live_request_queue,
                        run_config=run_config,
                    ):
                        # Reset retries on any successful event
                        retries = 0
                        event_json = event.model_dump_json(exclude_none=True, by_alias=True)
                        logger.debug(f"[SERVER] Event: {event_json}")
                        await websocket.send_text(event_json)
                    
                    # If generator finishes normally, exit the loop
                    break
                    
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.info(f"Gemini session ended/interrupted for {effective_session_id}: {e}")
                    
                    # Check for transitory close (code 1000 is common for timeouts)
                    # We attempt to resume regardless of error type up to max_retries
                    retries += 1
                    if retries < max_retries:
                        logger.info(f"Attempting session resumption ({retries}/{max_retries})...")
                        try:
                            await websocket.send_text(json.dumps({"type": "reconnecting"}))
                        except Exception:
                            # If browser WebSocket is also closed, stop retrying
                            break
                        
                        # Small backoff before recreating session
                        await asyncio.sleep(1)
                    else:
                        logger.error(f"Max retries reached for session {effective_session_id}")
        finally:
            logger.debug(f"downstream_task finished for {effective_session_id}")

    # Bug 1: Replace asyncio.gather with managed task lifecycles
    upstream = asyncio.create_task(upstream_task())
    downstream = asyncio.create_task(downstream_task())
    
    try:
        done, pending = await asyncio.wait(
            [upstream, downstream],
            return_when=asyncio.FIRST_COMPLETED
        )
        for task in pending:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
    except Exception as e:
        logger.error(f"Unexpected error in managed tasks: {e}", exc_info=True)
    finally:
        # ========================================
        # Phase 4: Session Termination
        # ========================================

        # Always close the queue, even if exceptions occurred
        logger.debug("Closing live_request_queue")
        live_request_queue.close()
