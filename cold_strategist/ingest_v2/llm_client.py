"""
LLM client for Ingestion v2.

Handles Ollama calls with JSON extraction.
Uses the Python ollama library for compatibility.
Deterministic: temp=0, top_p=1.
"""
import os
import json
import time

try:
    from ollama import chat
except ImportError:
    # Fallback to HTTP if ollama library not available
    import requests
    chat = None


OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "huihui_ai/deepseek-r1-abliterated:8b")
TIMEOUT = 600


class LLMError(Exception):
    """LLM call failed after retries."""
    pass


def call_llm(system_prompt: str, user_prompt: str, model: str = None) -> dict:
    """
    Call Ollama LLM and extract JSON response.

    Args:
        system_prompt: System prompt
        user_prompt: User prompt
        model: Model name (default: env OLLAMA_MODEL)

    Returns:
        Parsed JSON dict from LLM response

    Raises:
        LLMError: On JSON parsing or HTTP failure
    """
    if model is None:
        model = OLLAMA_MODEL

    # Combine prompts for models that don't support system messages
    full_prompt = f"{system_prompt}\n\n{user_prompt}"

    for attempt in range(2):
        try:
            if chat is not None:
                # Use Python ollama library
                response = chat(
                    model=model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    options={
                        "temperature": 0,
                        "top_p": 1,
                        "top_k": 0,
                        "seed": 42
                    }
                )
                text = response["message"]["content"]
            else:
                # Fallback to HTTP API
                import requests
                payload = {
                    "model": model,
                    "prompt": full_prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0,
                        "top_p": 1,
                        "top_k": 0
                    }
                }
                r = requests.post("http://127.0.0.1:11434/api/generate", json=payload, timeout=TIMEOUT)
                r.raise_for_status()
                text = r.json().get("response", "")

            # Debug: log response if it's suspicious
            if len(text) < 50 or "{" not in text:
                print(f"\n[DEBUG] LLM response suspicious:")
                print(f"  Length: {len(text)}")
                print(f"  First 500 chars: {text[:500]}")
                print(f"  Contains '{{': {'{' in text}")
            
            # Extract JSON from markdown fences if needed
            if "```" in text:
                start = text.index("```") + 3
                if text[start:start+4] == "json":
                    start += 4
                end = text.rindex("```")
                text = text[start:end].strip()

            # Find JSON object - handle cases where it might not exist
            if "{" not in text:
                print(f"\n[ERROR] No JSON found in LLM response")
                print(f"Response length: {len(text)}")
                print(f"Response preview: {text[:500]}")
                raise ValueError(f"No JSON found in LLM response")
            
            start = text.index("{")
            if "}" not in text[start:]:
                print(f"\n[ERROR] Incomplete JSON in response")
                print(f"Response from '{{' onwards: {text[start:start+500]}")
                raise ValueError(f"Incomplete JSON in LLM response")
            
            end = text.rindex("}") + 1
            try:
                return json.loads(text[start:end])
            except json.JSONDecodeError as je:
                print(f"\n[ERROR] JSON parse failed: {je}")
                print(f"Attempted to parse: {text[start:end][:500]}")
                raise ValueError(f"Invalid JSON from LLM: {je}")

        except Exception as e:
            if attempt == 1:
                raise LLMError(f"LLM call failed: {e}")
            time.sleep(5)

