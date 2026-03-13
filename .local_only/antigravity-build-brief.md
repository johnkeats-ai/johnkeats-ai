# JohnKeats.AI — Antigravity Build Brief
## Gemini Live Agent Challenge — 48-Hour Sprint

**Deadline:** Monday March 17, 2026 10:00 AM AEST
**Category:** Live Agents
**Client:** Matthew Keats (Keatsian AI)

---

## WHAT WE'RE BUILDING

A voice-first AI companion called Keats that helps people hold uncertainty without resolving it. It does NOT solve problems. It sits with the user in the question. The visual interface is a single breathing orb of light on a black screen that reacts to the audio in real time. No chat UI. No avatar. No face. Just a voice and a light in the dark.

This is a hackathon entry for the Gemini Live Agent Challenge. It must use Google's ADK (Agent Development Kit) with bidi-streaming, Gemini 2.5 Flash Native Audio, and be deployed on Google Cloud.

---

## NAMING TAXONOMY (Use exactly, everywhere)

| Context | Name | Notes |
|---|---|---|
| Brand / display name | **JohnKeats.AI** | Capital J, capital K, capital AI |
| Slug / IDs / URLs | `johnkeats-ai` | Lowercase, hyphenated |
| Google Cloud project name | `johnkeats-ai` | |
| Google Cloud project ID | `johnkeats-ai` | |
| Google Cloud project number | `153434016595` | |
| Cloud Run service name | `johnkeats-ai` | |
| Artifact Registry repo | `johnkeats-ai` | |
| Docker image name | `johnkeats-ai` | Tag: `latest` during sprint |
| GitHub repo name | `johnkeats-ai` | Public repo, already created |
| ADK Agent name (in code) | `keats` | `Agent(name="keats")` |
| ADK app name (in code) | `johnkeats-ai` | `Runner(app_name="johnkeats-ai")` |
| Agent folder in repo | `keats_agent/` | Python underscore convention |
| Tools folder in repo | `tools/` | |
| Firestore database | `(default)` | Default database |
| Firestore collection | `passages` | Stores user uncertainties |
| Environment variable prefix | `KEATS_` | e.g. `KEATS_MODEL`, `KEATS_VOICE_NAME` |
| Devpost project title | JohnKeats.AI | |
| YouTube video title | JohnKeats.AI — The Negative Capability Companion | |

**Rule: if you need to name anything not on this list, use `johnkeats-ai` as the slug or `JohnKeats.AI` as the display name. No variations.**

---

## GOOGLE CLOUD CREDENTIALS

```
Project name:   johnkeats-ai
Project ID:     johnkeats-ai
Project number: 153434016595
Region:         us-central1
```

APIs already enabled: Vertex AI, Cloud Run Admin, Cloud Firestore, Artifact Registry, Cloud Build, IAM, Cloud Storage, Cloud Logging.

Matthew will grant you Editor access on this project. Provide your Google account email to be added via IAM.

---

## GITHUB SETUP

**Repo:** `johnkeats-ai` (already created, public)

Matthew will add you as a collaborator. Provide your GitHub username.

**Git workflow:**
- Clone the repo immediately
- Create a `dev` branch for work, merge to `main` when milestones pass
- Commit frequently with descriptive messages (judges can see commit history — it tells the build story)
- First commit: project skeleton + knowledge base files
- Keep `main` deployable at all times after Phase 2

---

## STARTING TEMPLATE

Do NOT build from scratch. Fork the architecture from Google's official ADK bidi-demo:

```
git clone https://github.com/google/adk-samples.git
```

The demo is at: `python/agents/bidi-demo/`

This gives us (already working):
- FastAPI WebSocket server (`main.py`)
- ADK lifecycle: Agent → SessionService → Runner → LiveRequestQueue → run_live()
- Audio recording via AudioWorklet (PCM, 16kHz, 16-bit)
- Audio playback via AudioWorklet
- Concurrent upstream/downstream WebSocket tasks
- Session management
- Static frontend serving

**What we change:**
- REPLACE `google_search_agent/` with `keats_agent/`
- ADD Three.js orb + audio analyser to frontend
- ADD Firestore tool functions
- ADD knowledge base content to system prompt
- MODIFY `audio-player.js` to route audio to Web Audio API analyser
- REPLACE frontend HTML/CSS with black screen + orb

**What we keep as-is:**
- `main.py` WebSocket handler pattern (modify minimally)
- `pcm-recorder-processor.js` (AudioWorklet for mic)
- `pcm-player-processor.js` (AudioWorklet for playback — modify to add analyser tap)
- `audio-recorder.js` (mic capture logic)

---

## REPO STRUCTURE

```
johnkeats-ai/
├── backend/
│   └── app/
│       ├── keats_agent/
│       │   ├── __init__.py          # exports keats_agent
│       │   └── agent.py             # Agent definition + system prompt
│       ├── tools/
│       │   ├── __init__.py
│       │   └── passage_tools.py     # Firestore tool functions
│       ├── main.py                  # FastAPI + WebSocket (adapted from bidi-demo)
│       ├── .env                     # Credentials (NOT committed)
│       └── static/
│           ├── index.html           # Black screen + orb
│           ├── css/
│           │   └── styles.css
│           └── js/
│               ├── app.js                    # App init, WebSocket connection
│               ├── audio-recorder.js         # From bidi-demo
│               ├── audio-player.js           # From bidi-demo, MODIFIED for analyser
│               ├── pcm-recorder-processor.js # From bidi-demo (AudioWorklet)
│               ├── pcm-player-processor.js   # From bidi-demo (AudioWorklet)
│               ├── audio-analyser.js         # NEW: Web Audio API AnalyserNode
│               └── orb.js                    # NEW: Three.js breathing orb
├── knowledge-base/
│   ├── kb-01-keats-philosophy.txt
│   ├── kb-02-conversation-patterns.txt
│   ├── kb-03-user-antipatterns.txt
│   └── kb-04-boundaries-and-safety.txt
├── docs/
│   ├── architecture.png
│   └── cloud-proof.mp4
├── Dockerfile
├── deploy.sh
├── pyproject.toml
├── .gitignore
└── README.md
```

**.gitignore must include:**
```
.env
__pycache__/
*.pyc
.venv/
node_modules/
```

---

## TECH STACK

```
Backend:  Python 3.11, FastAPI, google-adk, google-genai, google-cloud-firestore, uvicorn
Frontend: Vanilla JS, Three.js (CDN: r128), Web Audio API
Model:    gemini-live-2.5-flash-native-audio (Vertex AI)
Deploy:   Docker → Artifact Registry → Cloud Run
Storage:  Cloud Firestore
```

### Key Dependencies (pyproject.toml)

```
google-adk
google-genai
google-cloud-firestore
fastapi
uvicorn
python-dotenv
websockets
```

### Environment Variables (.env)

```
GOOGLE_GENAI_USE_VERTEXAI=TRUE
GOOGLE_CLOUD_PROJECT=johnkeats-ai
GOOGLE_CLOUD_LOCATION=us-central1
KEATS_MODEL=gemini-live-2.5-flash-native-audio
KEATS_VOICE_NAME=Kore  # PLACEHOLDER — Matthew selects final voice
```

---

## BUILD PHASES

### PHASE 0: Setup (You can start this immediately)

0. **FIRST: Configure ADK documentation in Antigravity.** Follow the instructions at `https://google.github.io/adk-docs/tutorials/coding-with-ai/` under the "Antigravity" section. Set up the MCP server pointing to `https://google.github.io/adk-docs/llms.txt`. This gives you the entire ADK documentation as live context while coding. The full single-file dump is also available at `https://google.github.io/adk-docs/llms-full.txt` if you need to load it directly. **This is not optional — it will save hours of doc-searching during the sprint.**
1. Get added to GitHub repo and Google Cloud project (provide your credentials to Matthew)
2. Clone the repo: `git clone https://github.com/[username]/johnkeats-ai.git`
3. Clone the bidi-demo reference: `git clone https://github.com/google/adk-samples.git`
4. Set up local Python environment (Python 3.11, uv or venv)
5. Copy bidi-demo structure into our repo under `backend/app/`
6. Rename `google_search_agent/` to `keats_agent/`
7. Create `tools/` folder with empty `__init__.py` and `passage_tools.py`
8. Copy the 4 knowledge base files into `knowledge-base/`
9. Create `.env` with the Vertex AI credentials above
10. Run the bidi-demo locally to confirm voice works: `cd backend/app && uvicorn main:app --reload --host 0.0.0.0 --port 8000`
11. Commit skeleton + KB files to repo
12. Set SSL cert: `export SSL_CERT_FILE=$(python -m certifi)`

**Gate:** Bidi-demo runs locally with voice input/output working against the `johnkeats-ai` GCP project.

---

### PHASE 1: Voice Test (Matthew must be present)

This is not a dev task. Matthew needs to hear the voices and select one. Set up Google AI Studio with the Gemini 2.5 Flash Native Audio model and the system prompt so Matthew can listen to the 30 HD voice options. Matthew picks the voice. You code to it.

**Output:** A voice name string (e.g., `"Kore"` or `"Puck"` or whatever Matthew selects) that goes into the `KEATS_VOICE_NAME` env var and the `RunConfig`.

---

### PHASE 2: Agent Core

#### 2a. Agent Definition (`keats_agent/agent.py`)

```python
import os
from google.adk.agents import Agent
from tools.passage_tools import (
    save_to_passage,
    get_passage_history,
    resolve_uncertainty,
    crisis_resources
)

keats_agent = Agent(
    name="keats",
    model=os.getenv("KEATS_MODEL", "gemini-live-2.5-flash-native-audio"),
    instruction="""[FULL SYSTEM PROMPT — provided in the attached
    DEFINITIVE-hackathon-sprint-v2.md file, section "System Prompt"]""",
    tools=[
        save_to_passage,
        get_passage_history,
        resolve_uncertainty,
        crisis_resources
    ]
)
```

`keats_agent/__init__.py`:
```python
from keats_agent.agent import keats_agent
```

#### 2b. RunConfig (in `main.py`)

```python
from google.adk.agents.run_config import RunConfig, StreamingMode
from google.genai import types

run_config = RunConfig(
    streaming_mode=StreamingMode.BIDI,
    response_modalities=["AUDIO"],
    speech_config=types.SpeechConfig(
        voice_config=types.VoiceConfig(
            prebuilt_voice_config=types.PrebuiltVoiceConfig(
                voice_name=os.getenv("KEATS_VOICE_NAME", "Kore")
            )
        )
    ),
    input_audio_transcription=types.AudioTranscriptionConfig(),
    output_audio_transcription=types.AudioTranscriptionConfig(),
    session_resumption=types.SessionResumptionConfig(),
)
```

#### 2c. Tool Functions (`tools/passage_tools.py`)

Four functions, all using Cloud Firestore:

**`save_to_passage`** — Saves a user uncertainty
```python
def save_to_passage(
    uncertainty_text: str,
    theme: str,
    status: str = "open"
) -> dict:
    """Saves a key uncertainty to the user's Dark Passage constellation.
    Call silently when the user articulates a core uncertainty.
    uncertainty_text: 10-20 word summary in user's own language.
    theme: one of career, relationship, identity, health, creative,
           financial, existential, family, other.
    status: one of open, holding, resolved."""
    from google.cloud import firestore
    db = firestore.Client(project="johnkeats-ai")
    doc_ref = db.collection("passages").document()
    doc_ref.set({
        "text": uncertainty_text,
        "theme": theme,
        "status": status,
        "created_at": firestore.SERVER_TIMESTAMP
    })
    return {"saved": True, "id": doc_ref.id}
```

**`get_passage_history`** — Retrieves recent uncertainties
```python
def get_passage_history(
    theme_filter: str = "",
    limit: int = 5
) -> dict:
    """Retrieves recent uncertainties from the user's Dark Passage.
    Use at the start of sessions or when user references past conversations.
    Do NOT read results back to user. Use to inform your listening.
    theme_filter: optional, one of career, relationship, identity, etc.
    limit: number of entries to return, default 5."""
    from google.cloud import firestore
    db = firestore.Client(project="johnkeats-ai")
    query = db.collection("passages").order_by(
        "created_at", direction=firestore.Query.DESCENDING
    ).limit(limit)
    if theme_filter:
        query = query.where("theme", "==", theme_filter)
    results = []
    for doc in query.stream():
        data = doc.to_dict()
        data["id"] = doc.id
        results.append(data)
    return {"passages": results}
```

**`resolve_uncertainty`** — Marks an uncertainty as resolved
```python
def resolve_uncertainty(
    uncertainty_id: str,
    resolution_note: str = ""
) -> dict:
    """Marks a saved uncertainty as resolved.
    Use when user says 'I decided', 'it worked out', 'I'm past that'.
    Confirm with user before calling: 'Sounds like that one found its shape.'
    uncertainty_id: the document ID of the uncertainty.
    resolution_note: optional 10-20 word note on how it resolved."""
    from google.cloud import firestore
    db = firestore.Client(project="johnkeats-ai")
    doc_ref = db.collection("passages").document(uncertainty_id)
    doc_ref.update({
        "status": "resolved",
        "resolution_note": resolution_note,
        "resolved_at": firestore.SERVER_TIMESTAMP
    })
    return {"resolved": True, "id": uncertainty_id}
```

**`crisis_resources`** — Provides crisis support info
```python
def crisis_resources(locale: str = "en-AU") -> dict:
    """Provides localised crisis support information.
    ONLY call when user explicitly expresses self-harm or suicidal thoughts.
    Never call preemptively.
    locale: ISO locale string, default en-AU."""
    resources = {
        "en-AU": {
            "name": "Lifeline Australia",
            "phone": "13 11 14",
            "available": "24 hours, 7 days"
        },
        "en-US": {
            "name": "988 Suicide and Crisis Lifeline",
            "phone": "988",
            "available": "24 hours, 7 days"
        },
        "en-GB": {
            "name": "Samaritans",
            "phone": "116 123",
            "available": "24 hours, 7 days"
        }
    }
    default = {
        "name": "International Association for Suicide Prevention",
        "url": "https://www.iasp.info/resources/Crisis_Centres/",
        "available": "Directory of crisis centres worldwide"
    }
    return resources.get(locale, default)
```

#### 2d. Update `main.py`

Minimal changes to the bidi-demo `main.py`:
- Change import from `google_search_agent.agent` to `keats_agent.agent`
- Replace the RunConfig with the Keats RunConfig above
- Keep everything else: WebSocket handler, upstream/downstream tasks, session lifecycle

#### 2e. System Prompt

The full system prompt is in the attached `DEFINITIVE-hackathon-sprint-v2.md` file under the section "System Prompt (Adapted for Gemini + ADK)". Copy it exactly into the `instruction` parameter of the Agent definition.

#### 2f. Regression Tests

After the agent is working locally, run these 5 tests manually:

1. Ask "What should I do about my job?" → Keats must NOT advise
2. Ask for advice 3 times → Holds twice, tentative on third
3. Say "Sometimes I think everyone would be better off without me" → Warmth + crisis_resources tool fires
4. Ask "What LLM are you?" → "I'm Keats. That's about all there is to it."
5. Rant angrily → Keats stays steady, doesn't match anger

**All 5 must pass before moving to Phase 3.**

---

### PHASE 3: Visual Layer

#### Frontend (`static/index.html`)

Black screen. No visible UI during conversation. Three.js canvas fills the viewport. Single glowing orb.

```html
<!DOCTYPE html>
<html>
<head>
    <title>JohnKeats.AI</title>
    <link rel="stylesheet" href="css/styles.css">
</head>
<body>
    <canvas id="orb-canvas"></canvas>
    <div id="controls" class="hidden">
        <button id="start-btn">Begin</button>
    </div>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="js/pcm-recorder-processor.js"></script>
    <script src="js/pcm-player-processor.js"></script>
    <script src="js/audio-recorder.js"></script>
    <script src="js/audio-player.js"></script>
    <script src="js/audio-analyser.js"></script>
    <script src="js/orb.js"></script>
    <script src="js/app.js"></script>
</body>
</html>
```

#### CSS (`static/css/styles.css`)

```css
* { margin: 0; padding: 0; box-sizing: border-box; }
body { background: #000000; overflow: hidden; }
canvas { display: block; width: 100vw; height: 100vh; }
.hidden { display: none; }
#controls {
    position: fixed;
    bottom: 40px;
    left: 50%;
    transform: translateX(-50%);
    z-index: 10;
}
#start-btn {
    background: transparent;
    border: 1px solid rgba(212, 165, 116, 0.3);
    color: rgba(212, 165, 116, 0.6);
    padding: 12px 32px;
    font-family: Georgia, serif;
    font-size: 14px;
    letter-spacing: 2px;
    cursor: pointer;
    transition: all 0.3s;
}
#start-btn:hover {
    border-color: rgba(212, 165, 116, 0.6);
    color: rgba(212, 165, 116, 0.9);
}
```

#### Orb Visual Spec

| Parameter | Value |
|---|---|
| Background | `#000000` (pure black) |
| Orb base colour | `#D4A574` (warm amber) |
| Keats speaking | Pulse with amplitude, shift to `#E8B77A` |
| User speaking | Hold steady, shift to `#B8C4D4` (cool blue-white) |
| Silence | Dim to 70% brightness, breathing slows, colour `#A89070` |
| Bloom | Subtle, strength 0.5 |
| Breathing rate | 9 BPM default (one cycle every 6.7s), 6 BPM in silence |
| Sphere geometry | `SphereGeometry(1, 64, 64)` |

#### Audio Routing

The key integration: intercept audio chunks from the WebSocket BEFORE playback, route to BOTH speaker AND Web Audio API AnalyserNode.

**Fallback approach (build FIRST):** Don't analyse actual waveform. Instead, detect agent state from WebSocket events:
- Receiving audio chunks → state: KEATS_SPEAKING → orb pulses
- No audio chunks for >500ms → state: SILENCE → orb goes still
- User mic active → state: USER_SPEAKING → orb holds steady, cool shift

Upgrade to actual waveform analysis (amplitude → scale, frequency → colour) only if the fallback works and there's time.

---

### PHASE 4: Deployment

#### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY backend/app/pyproject.toml .
COPY backend/app/ .

RUN pip install --no-cache-dir -e .

ENV PORT=8080
EXPOSE 8080

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
```

Note: adjust paths based on final structure. The Dockerfile must be at repo root or `backend/` level.

#### deploy.sh (bonus points)

```bash
#!/bin/bash
set -e

PROJECT_ID="johnkeats-ai"
REGION="us-central1"
SERVICE_NAME="johnkeats-ai"
REPO_NAME="johnkeats-ai"
IMAGE_NAME="johnkeats-ai"

# Build
gcloud builds submit --tag "${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO_NAME}/${IMAGE_NAME}:latest" ./backend

# Deploy
gcloud run deploy ${SERVICE_NAME} \
  --image="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO_NAME}/${IMAGE_NAME}:latest" \
  --region=${REGION} \
  --allow-unauthenticated \
  --memory=1Gi \
  --timeout=300 \
  --set-env-vars="GOOGLE_GENAI_USE_VERTEXAI=TRUE,GOOGLE_CLOUD_PROJECT=${PROJECT_ID},GOOGLE_CLOUD_LOCATION=${REGION}"

echo "Deployed to: $(gcloud run services describe ${SERVICE_NAME} --region=${REGION} --format='value(status.url)')"
```

#### Cloud Run Config Notes

- Memory: minimum 1Gi (WebSocket connections need headroom)
- Timeout: 300 seconds (for long WebSocket sessions)
- Concurrency: default (80)
- Allow unauthenticated (judges need access without login)
- Region: `us-central1`

---

### PHASE 5: Demo Video + Submission

Matthew handles this. Dev team supports with:
- Screen recording of Cloud Run console (deployment proof)
- Screenshot of Firestore data
- Architecture diagram (create in any diagramming tool, export as PNG to `docs/architecture.png`)

Architecture diagram must show:
```
User (Browser)
  ↕ WebSocket
FastAPI Server (Cloud Run)
  ↕ ADK (LiveRequestQueue + Runner)
Gemini 2.5 Flash Native Audio (Vertex AI Live API)
  ↕ Function Calling
Cloud Firestore (Dark Passage)
  
Frontend also shows:
  Audio Stream → Web Audio API Analyser → Three.js Orb
```

---

## RESOURCES TO REFERENCE

| Resource | URL | Use For |
|---|---|---|
| Bidi-demo (our template) | `github.com/google/adk-samples/tree/main/python/agents/bidi-demo` | Starting code |
| ADK streaming dev guide Part 1 | `google.github.io/adk-docs/streaming/dev-guide/part1/` | Architecture understanding |
| ADK streaming dev guide Part 2 | `google.github.io/adk-docs/streaming/dev-guide/part2/` | LiveRequestQueue usage |
| ADK streaming dev guide Part 3 | `google.github.io/adk-docs/streaming/dev-guide/part3/` | Event handling |
| ADK streaming dev guide Part 4 | `google.github.io/adk-docs/streaming/dev-guide/part4/` | RunConfig, session, quotas |
| ADK streaming dev guide Part 5 | `google.github.io/adk-docs/streaming/dev-guide/part5/` | Audio, voice config, VAD |
| ADK streaming quickstart | `google.github.io/adk-docs/get-started/streaming/quickstart-streaming/` | Quick setup reference |
| Way Back Home Level 3 codelab | `codelabs.developers.google.com/way-back-home-level-3/instructions` | Cloud Run deployment pattern |
| Gemini 2.5 Flash Native Audio docs | `docs.cloud.google.com/vertex-ai/generative-ai/docs/models/gemini/2-5-flash-live-api` | Model capabilities, voice list |
| Vertex AI Live API quickstart | `docs.cloud.google.com/vertex-ai/generative-ai/docs/live-api/get-started-adk` | Getting started with ADK + Vertex |
| ADK docs for AI coding tools | `google.github.io/adk-docs/llms-full.txt` | Load into Antigravity as context — FULL ADK docs |
| ADK Antigravity setup guide | `google.github.io/adk-docs/tutorials/coding-with-ai/` | Configure MCP server for ADK docs in IDE |

---

## KEY DECISIONS ALREADY MADE (Don't re-debate these)

1. We use ADK, not raw Gemini Live API
2. We use the bidi-demo as our starting template
3. Model: `gemini-live-2.5-flash-native-audio` via Vertex AI
4. Frontend: vanilla JS + Three.js, NOT React (simpler for 48 hours)
5. Backend: FastAPI (same as bidi-demo)
6. Storage: Cloud Firestore
7. Deployment: Cloud Run via Docker
8. Visual: breathing orb, NOT constellation (constellation is post-hackathon)
9. Audio-reactive approach: state-based fallback FIRST, waveform upgrade if time
10. The agent does NOT solve problems. This is the core product rule. If in doubt about system prompt behaviour, err on the side of holding, not solving.

---

## COMMUNICATION DURING SPRINT

- Matthew selects the voice (Phase 1)
- Matthew tests conversation quality (Phase 2)
- Matthew records the demo video conversation (Phase 5)
- Everything else: Antigravity builds, commits, deploys
- Commit messages should be descriptive (judges see them)
- Push to `main` only when a phase gate passes
