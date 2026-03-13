# JohnKeats.AI

A philosophical voice companion that implements **Negative Capability**.

## Overview

JohnKeats.AI is not here to solve your problems. Inspired by the poet John Keats, it helps users hold uncertainty, mystery, and doubt without an "irritable reaching after fact and reason."

Built using the **ADK (Agent Development Kit)** and **Gemini Live API**, Keats provides a warm, unhurried, and deeply reflective conversational experience.

## Core Features

- **Negative Capability Core**: A custom agent logic designed to mirror, reframe, and sit with user uncertainty rather than resolving it.
- **The Breathing Orb**: A minimalist Three.js frontend reflecting the agent's emotional and conversational state.
- **Passage State Management**: Firestore-backed tracking of user uncertainties across sessions.
- **Safety First**: Integrated crisis support and character boundaries.

## Architecture

- **Backend**: Python 3.12, ADK, FastAPI.
- **Frontend**: Vanilla JS, Three.js, Web Audio API.
- **Database**: Google Cloud Firestore.
- **LLM**: Gemini 2.5 Flash (Native Audio) via Vertex AI.

## Local Development

1. **Environment Setup**:
   ```bash
   pip install -e .
   ```
2. **Environment Variables**:
   Create an `env_file` with:
   - `GOOGLE_CLOUD_PROJECT`
   - `GOOGLE_CLOUD_LOCATION`
   - `KEATS_VOICE_NAME=Achird`

3. **Run**:
   ```bash
   uvicorn main:app --reload
   ```

## Deployment

Deployment is handled via Google Cloud Run:
```bash
./deploy.sh
```

## Credits

Part of the Antigravity Code Hackathon.
Built with ❤️ and Negative Capability.
