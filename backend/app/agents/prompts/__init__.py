import os

PROMPT_DIR = os.path.dirname(__file__)

def load_prompt(filename: str) -> str:
    """Loads a prompt from a markdown file in the prompts directory."""
    path = os.path.join(PROMPT_DIR, filename)
    if not os.path.exists(path):
        # Fallback for common extensions
        if not path.endswith(".md"):
            path += ".md"
    
    try:
        with open(path, "r") as f:
            return f.read()
    except FileNotFoundError:
        # Log error or return placeholder if missing
        return f"Prompt file {filename} not found."
