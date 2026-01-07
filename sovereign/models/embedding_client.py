import requests

OLLAMA_URL = "http://localhost:11434/api/embeddings"
MODEL = "nomic-embed-text"

def embed_text(text: str) -> list:
    """Embed text via local Ollama."""
    payload = {
        "model": MODEL,
        "prompt": text
    }
    r = requests.post(OLLAMA_URL, json=payload, timeout=60)
    r.raise_for_status()
    return r.json()["embedding"]
