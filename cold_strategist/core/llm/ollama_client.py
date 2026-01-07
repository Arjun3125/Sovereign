import json
from typing import Optional, Dict, List, Any
import requests
from ollama import chat, embeddings


# Default model to use for all clients (enable Claude Haiku 4.5)
DEFAULT_MODEL = "claude/haiku-4.5"


# Model routing for specialized tasks (use DEFAULT_MODEL unless task needs special model)
MODEL_MAP = {
    "reason": DEFAULT_MODEL,  # Tribunal / Cold analysis
    "code": DEFAULT_MODEL,    # Coding tasks
    "challenge": DEFAULT_MODEL,  # Devil's advocate / adversarial
    "embed": "nomic-embed-text",     # RAG / memory embeddings - use Nomic embeddings
    # Backwards compatibility
    "domain_classification": DEFAULT_MODEL,
    "memory_extraction": DEFAULT_MODEL,
}

# Single source of truth - Windows host, local Ollama
OLLAMA_BASE_URL = "http://127.0.0.1:11434"


class OllamaClient:
    def __init__(self, model: Optional[str] = None, timeout: int = 300, base_url: str = OLLAMA_BASE_URL):
        self.model = model
        self.timeout = timeout
        self.base_url = base_url.rstrip("/")

    def generate(
        self,
        model: str = None,
        prompt: str = "",
        task: str = None,
        stream: bool = False,
        *,
        temperature: float = None,
        max_tokens: int = None,
        top_p: float = None,
        system: str = None,
        debug_dump: str = None,
    ) -> str:
        """Generate text using Ollama native API with model routing.

        Accepts optional generation kwargs (`system`, `temperature`, `max_tokens`) and
        resolves the model from explicit `model`, `task` mapping, or the instance default.
        """
        # Resolve model name from task mapping, explicit model, or instance default
        model_name = MODEL_MAP.get(task, model or self.model or DEFAULT_MODEL)
        if not model_name:
            raise ValueError("Model not specified and no task mapping found")

        # Build messages list; include optional system prompt if provided
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        # Forward supported kwargs to the backend chat call using `options`
        chat_kwargs = {"model": model_name, "messages": messages}
        if stream is not None:
            chat_kwargs["stream"] = stream

        options: Dict[str, Any] = {}
        if temperature is not None:
            options["temperature"] = temperature
        if max_tokens is not None:
            options["max_tokens"] = max_tokens
        if top_p is not None:
            options["top_p"] = top_p
        if options:
            chat_kwargs["options"] = options

        response = chat(**chat_kwargs)

        # If streaming, chat may return a generator; ensure we have a final response object
        if hasattr(response, "__iter__") and not isinstance(response, (dict, list)):
            parts = list(response)
            if not parts:
                raise RuntimeError("Ollama returned empty stream")
            response = parts[-1]

        # Extract content robustly (support dicts and pydantic models)
        content = ""
        # dict-like
        if isinstance(response, dict):
            content = response.get("message", {}).get("content", "")
        else:
            # try attribute access
            msg = getattr(response, "message", None)
            if isinstance(msg, dict):
                content = msg.get("content", "")
            elif msg is not None:
                content = getattr(msg, "content", "")
            else:
                # fallback to top-level content attr or model_dump
                content = getattr(response, "content", "")
                if not content and hasattr(response, "model_dump"):
                    try:
                        dumped = response.model_dump()
                        content = dumped.get("message", {}).get("content", "")
                    except Exception:
                        content = ""

        result = (content or "").strip()

        # If caller requested a debug dump, write raw response repr for inspection
        if debug_dump:
            try:
                with open(debug_dump, "w", encoding="utf-8") as fd:
                    fd.write("MODEL_NAME: %s\n" % model_name)
                    fd.write("RAW_RESPONSE_REPR:\n")
                    fd.write(repr(response))
                    fd.write("\n\nEXTRACTED_CONTENT:\n")
                    fd.write(result)
            except Exception:
                pass

        if not result:
            if debug_dump:
                # When debug_dump is provided, return empty result (caller will inspect file)
                return result
            raise RuntimeError("Ollama returned empty response")
        return result

    def generate_raw(
        self,
        *,
        prompt: str,
        system: str = "",
        model: Optional[str] = None,
        temperature: float = 0.0,
        max_tokens: int = 512,
        top_p: float = 1.0,
        stream: bool = False,
        debug_dump: str = None,
    ) -> str:
        """Raw deterministic generation via Ollama /api/generate.

        This MUST be used for ingestion / Phase-1 / Phase-2 where raw
        text output (not chat objects) is required.
        """
        model_name = model or self.model or DEFAULT_MODEL
        if not model_name:
            raise ValueError("Model not specified for raw generation")

        payload = {
            "model": model_name,
            "prompt": (system + "\n\n" + prompt).strip(),
            "stream": False if not stream else True,
            "options": {
                "temperature": float(temperature),
                "top_p": float(top_p),
                "num_predict": int(max_tokens),
            },
        }

        url = f"{self.base_url}/api/generate"

        try:
            r = requests.post(url, json=payload, timeout=self.timeout)
            r.raise_for_status()
            data = r.json()
        except Exception as exc:
            raise RuntimeError(f"Ollama /api/generate failed: {exc}")

        # Ollama /api/generate typically returns {'response': '...'}
        text = (data.get("response") or "").strip()

        if debug_dump:
            try:
                with open(debug_dump, "w", encoding="utf-8") as fd:
                    fd.write(f"MODEL: {model_name}\n")
                    fd.write("RAW_JSON:\n")
                    fd.write(json.dumps(data, indent=2, ensure_ascii=False))
                    fd.write("\n\nEXTRACTED_TEXT:\n")
                    fd.write(text)
            except Exception:
                pass

        if not text:
            raise RuntimeError("Ollama /api/generate returned empty text")

        return text

    def reason(self, prompt: str, **kwargs) -> str:
        """Deep reasoning (Tribunal / Cold analysis)."""
        return self.generate(prompt=prompt, task="reason", **kwargs)

    def code(self, prompt: str, **kwargs) -> str:
        """Code generation task."""
        return self.generate(prompt=prompt, task="code", **kwargs)

    def challenge(self, prompt: str, **kwargs) -> str:
        """Devil's advocate / adversarial analysis."""
        return self.generate(prompt=prompt, task="challenge", **kwargs)

    def embed(self, text: str) -> List[float]:
        """Generate embeddings for RAG / memory operations."""
        response = embeddings(
            model=MODEL_MAP["embed"],
            prompt=text
        )
        return response["embedding"]


# Backwards-compatible alias expected by other modules
OllamaLLM = OllamaClient


