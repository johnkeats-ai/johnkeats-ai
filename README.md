# JohnKeats.AI

> The first AI agent designed not to solve your problem, but to sit with you in it.

A voice-first philosophical companion built on John Keats' 200-year-old idea of **negative capability** — the ability to hold uncertainty without reaching for premature answers. Unlike every other AI agent that races to solve your problem, Keats sits with you in the question.

The visual environment is a single breathing point of light in darkness, audio-reactive to the conversation. You don't look at Keats. You listen. The darkness is the product.

**Built for the Gemini Live Agent Challenge.**

## Live Demo

[johnkeats.ai](https://johnkeats.ai)

## Demo Video

[YouTube — coming soon]

## Architecture

![Architecture](docs/architecture.png)

**Backend:** FastAPI server on Cloud Run handles WebSocket connections. The Google ADK manages bidirectional audio streaming with the Gemini model. Four Firestore tools handle the user's "Dark Passage" — a constellation of saved uncertainties.

**Model:** Gemini 2.5 Flash Native Audio via the Vertex AI Live API. Native audio means the model hears tone, pace, and hesitation — not just transcribed words. This enables affective dialogue: Keats slows down when you sound anxious, stays steady when you're angry, comes closer when you're numb.

**Frontend:** Vanilla JavaScript and Three.js render a breathing orb on a black screen. The orb's state is driven by the conversation: it pulses when Keats speaks, shifts cool when you speak, and dims into slow breathing during silence.

## Tech Stack

- **Backend:** Python 3.11, FastAPI, Google ADK, google-genai, google-cloud-firestore
- **Model:** Gemini 2.5 Flash Native Audio (Vertex AI Live API)
- **Frontend:** Vanilla JS, Three.js (r128), Web Audio API
- **Storage:** Google Cloud Firestore
- **Deployment:** Docker → Artifact Registry → Google Cloud Run
- **Streaming:** WebSocket bidirectional audio (ADK bidi-streaming)

## Local Development

1. Clone the repo:
   ```bash
   git clone https://github.com/johnkeats-ai/johnkeats-ai.git
   cd johnkeats-ai
   ```

2. Set up Python 3.11 environment:
   ```bash
   python3.11 -m venv .venv
   source .venv/bin/activate
   ```

3. Copy the example environment file and fill in your values:
   ```bash
   cp .env.example backend/app/.env
   ```

   Required variables:
   - `GOOGLE_CLOUD_PROJECT=johnkeats-ai`
   - `GOOGLE_CLOUD_LOCATION=us-central1`
   - `GOOGLE_GENAI_USE_VERTEXAI=TRUE`
   - `KEATS_VOICE_NAME=Achird`

4. Install dependencies:
   ```bash
   cd backend/app
   pip install -e .
   ```

5. Set SSL certificate path:
   ```bash
   export SSL_CERT_FILE=$(python -m certifi)
   ```

6. Run the server:
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

7. Open [http://localhost:8000](http://localhost:8000) in your browser.

## Cloud Deployment

Requires a GCP project with Vertex AI, Firestore, Cloud Run, and Artifact Registry APIs enabled.

```bash
./deploy.sh
```

## Project Structure

```
johnkeats-ai/
├── backend/app/
│   ├── keats_agent/
│   │   ├── __init__.py
│   │   └── agent.py          # Agent definition + system prompt
│   ├── tools/
│   │   ├── __init__.py
│   │   └── passage_tools.py  # Firestore tools
│   ├── static/
│   │   ├── css/style.css
│   │   ├── js/
│   │   │   ├── app.js         # WebSocket + state machine
│   │   │   ├── orb.js         # Three.js breathing orb
│   │   │   ├── audio-player.js
│   │   │   ├── audio-recorder.js
│   │   │   └── ...
│   │   └── index.html
│   ├── main.py                # FastAPI + WebSocket handler
│   └── pyproject.toml
├── knowledge-base/
│   ├── kb-01-keats-philosophy.txt
│   ├── kb-02-conversation-patterns.txt
│   ├── kb-03-user-antipatterns.txt
│   └── kb-04-boundaries-and-safety.txt
├── docs/
│   └── architecture.png
├── deploy.sh
├── Dockerfile
├── .env.example
└── README.md
```

## Knowledge Base

The `knowledge-base/` directory contains four reference documents:

- **kb-01:** Keats' philosophical framework — negative capability, the Mansion of Many Apartments, the vale of soul-making
- **kb-02:** Conversation patterns — signature moves, emotional matching, conversation closings
- **kb-03:** User anti-patterns — ten common certainty-seeking patterns with reframe directions
- **kb-04:** Boundaries and safety — crisis protocol, therapy boundaries, hostility handling, character integrity

## Tools

Four Firestore-backed tools power the agent's memory:

- **save_to_passage** — silently saves a user's core uncertainty when they articulate it
- **get_passage_history** — retrieves recent uncertainties to inform listening (never read back to user)
- **resolve_uncertainty** — marks an uncertainty as resolved when the user indicates closure
- **crisis_resources** — provides localised crisis support information (fires only on explicit self-harm or suicidal expression)

## Blog Post

[Coming soon — dev.to]

## License

MIT
