import os
from dotenv import load_dotenv
from google.genai import Client
from google.adk.agents import Agent
from google.adk.runners import Runner

load_dotenv()

print(f"GOOGLE_GENAI_USE_VERTEXAI: {os.getenv('GOOGLE_GENAI_USE_VERTEXAI')}")
print(f"GOOGLE_CLOUD_PROJECT: {os.getenv('GOOGLE_CLOUD_PROJECT')}")

try:
    client = Client(
        vertexai=True,
        project=os.getenv("GOOGLE_CLOUD_PROJECT"),
        location=os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
    )
    print("Successfully initialized google-genai Client for Vertex AI.")
    
    # Try a simple models.get to verify auth
    model = client.models.get(model=os.getenv("DEMO_AGENT_MODEL", "gemini-live-2.5-flash-native-audio"))
    print(f"Successfully retrieved model: {model.name}")
    
except Exception as e:
    print(f"Error during diagnostic: {e}")
