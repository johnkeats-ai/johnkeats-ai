# JohnKeats.AI

JohnKeats.AI is a voice-first AI companion built on the philosophy of negative capability — the 200-year-old idea from the poet John Keats that the ability to hold uncertainty without reaching for premature answers is the most important cognitive skill of the modern age. Unlike every other AI agent that races to solve your problem, Keats sits with you in the question. The visual environment — a single breathing point of light in darkness, audio-reactive to the conversation — creates a space rather than a screen. You don't look at Keats. You listen.

## Live Demo
- **Live URL**: [https://johnkeats.ai](https://johnkeats.ai)
- **Demo Video**: [DEMO VIDEO URL]

## Architecture
![System Architecture](docs/architecture.png)

**Brief Overview:**
- **User (Browser)** ↔ WebSocket ↔ **FastAPI Server (Cloud Run)**
- **FastAPI** ↔ ADK (LiveRequestQueue + Runner) ↔ **Gemini 2.5 Flash Native Audio (Vertex AI Live API)**
- **Gemini** ↔ Function Calling ↔ **Cloud Firestore (Dark Passage)**
- **Frontend**: Audio Stream → Web Audio API → Three.js Orb

## Tech Stack

| Layer | Technology |
|---|---|
| Agent Framework | Google Agent Development Kit (ADK) |
| Model | Gemini 2.5 Flash Native Audio via Vertex AI Live API |
| Backend | Python 3.11, FastAPI, uvicorn |
| Frontend | Vanilla JavaScript, Three.js (r128), Web Audio API |
| Storage | Cloud Firestore |
| Deployment | Docker, Google Cloud Run, Artifact Registry |
| Audio | Bidirectional streaming (16kHz input / 24kHz output) |

## Local Setup

### Step 1: Clone
```bash
git clone https://github.com/johnkeats-ai/johnkeats-ai.git
cd johnkeats-ai
```

### Step 2: Python Environment
```bash
python3.11 -m venv .venv
source .venv/bin/activate
```

### Step 3: Install Dependencies
```bash
cd backend/app
pip install -e .
```

### Step 4: Configure Environment
```bash
cp .env.example .env
# Edit .env with your GCP project details:
#   GOOGLE_GENAI_USE_VERTEXAI=TRUE
#   GOOGLE_CLOUD_PROJECT=your-project-id
#   GOOGLE_CLOUD_LOCATION=us-central1
#   KEATS_MODEL=gemini-live-2.5-flash-native-audio
#   KEATS_VOICE_NAME=Achird
```

### Step 5: SSL Certificates (Required for Vertex AI)
```bash
export SSL_CERT_FILE=$(python -m certifi)
```

### Step 6: Run
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```
Then open [http://localhost:8000](http://localhost:8000).

## Cloud Deployment

Deploy in one command using the provided script at the repo root:
```bash
./deploy.sh
```

## Project Structure

```
johnkeats-ai/
├── backend/app/
│   ├── main.py                 # FastAPI server + WebSocket handler
│   ├── keats_agent/
│   │   ├── agent.py            # Keats agent definition + system prompt
│   │   └── __init__.py
│   ├── tools/
│   │   ├── passage_tools.py    # Firestore tools (save, retrieve, resolve, crisis)
│   │   └── __init__.py
│   └── static/
│       ├── index.html
│       ├── css/styles.css
│       └── js/                 # Orb, audio pipeline, app logic
├── knowledge-base/             # Philosophy, patterns, references, safety
├── docs/architecture.png
├── deploy.sh
├── Dockerfile
└── README.md
```

## Competition
Built for the [Gemini Live Agent Challenge](https://geminiliveagentchallenge.devpost.com/) on Devpost.

## License
MIT
