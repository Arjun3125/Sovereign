import json
from typing import Optional, Dict, List, Any
from ollama import chat, embeddings


# Model routing for specialized tasks
MODEL_MAP = {
    "reason": "huihui_ai/deepseek-r1-abliterated:8b",  # Tribunal / Cold analysis
    "code": "qwen2.5-coder:7b",                          # Coding tasks
    "challenge": "dolphin-mistral:7b",                   # Devil's advocate / adversarial
    "embed": "nomic-embed-text",                         # RAG / memory embeddings
    # Backwards compatibility
    "domain_classification": "huihui_ai/deepseek-r1-abliterated:8b",
    "memory_extraction": "huihui_ai/deepseek-r1-abliterated:8b",
}

# Single source of truth - Windows host, local Ollama
OLLAMA_BASE_URL = "http://127.0.0.1:11434"


class OllamaClient:
    def __init__(self, model: Optional[str] = None, timeout: int = 300, base_url: str = OLLAMA_BASE_URL):
        self.model = model
        self.timeout = timeout
        self.base_url = base_url.rstrip("/")

    def generate(self, model: str = None, prompt: str = "", task: str = None, stream: bool = True) -> str:
        """Generate text using Ollama native API with model routing."""
        # Resolve model name from task mapping, explicit model, or instance default
        model_name = MODEL_MAP.get(task, model or self.model)
        if not model_name:
            raise ValueError("Model not specified and no task mapping found")

        response = chat(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
        )
        
        result = response["message"]["content"].strip()
        if not result:
            raise RuntimeError("Ollama returned empty response")
        return result

    def reason(self, prompt: str) -> str:
        """Deep reasoning (Tribunal / Cold analysis)."""
        response = chat(
            model=MODEL_MAP["reason"],
            messages=[{"role": "user", "content": prompt}],
        )
        return response["message"]["content"]

    def code(self, prompt: str) -> str:
        """Code generation task."""
        response = chat(
            model=MODEL_MAP["code"],
            messages=[{"role": "user", "content": prompt}],
        )
        return response["message"]["content"]

    def challenge(self, prompt: str) -> str:
        """Devil's advocate / adversarial analysis."""
        response = chat(
            model=MODEL_MAP["challenge"],
            messages=[{"role": "user", "content": prompt}],
        )
        return response["message"]["content"]

    def embed(self, text: str) -> List[float]:
        """Generate embeddings for RAG / memory operations."""
        response = embeddings(
            model=MODEL_MAP["embed"],
            prompt=text
        )
        return response["embedding"]


# Backwards-compatible alias expected by other modules
OllamaLLM = OllamaClient


