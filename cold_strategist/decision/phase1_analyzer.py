"""
Phase-1: Strategic Situation Analysis & Decision Synthesis

Consolidated module for analyzing situations, producing structured decisions,
and validating responses through an LLM interface.

Features:
- Schema validation (Decision, ActionItem, Phase1Response)
- LLM-based situation analysis with structured output
- JSON response parsing and validation
- Demo/test harness
"""

import os
import json
import requests
from typing import Optional, List, Dict, Any, Literal
from pydantic import BaseModel, Field


# ======================
# SCHEMA DEFINITIONS
# ======================

class Decision(BaseModel):
    """Structured decision object.

    - action: canonical action name (string); can be empty for NEEDS_CONTEXT/ERROR
    - parameters: optional dict of parameters for the action
    """

    action: str = ""
    parameters: Optional[Dict[str, Any]] = None


class ActionItem(BaseModel):
    """Follow-up action item.

    - type: short action type identifier (e.g., GATHER_INFO, NOTIFY)
    - description: human-friendly description
    - target: optional actor or channel
    """

    type: str
    description: Optional[str] = None
    target: Optional[str] = None


class Phase1Response(BaseModel):
    """Schema for Phase-1 assistant output.

    Fields:
    - status: one of 'OK', 'NEEDS_CONTEXT', or 'ERROR'
    - reasoning: human-readable justification
    - confidence: float between 0.0 and 1.0
    - decision: `Decision` object (optional, may be null on error/needs_context)
    - actions: optional list of `ActionItem`
    - metadata: optional map for additional non-critical info
    """

    status: Literal["OK", "NEEDS_CONTEXT", "ERROR"]
    reasoning: str = Field(..., min_length=1)
    confidence: float = Field(..., ge=0.0, le=1.0)
    decision: Optional[Decision] = None
    actions: Optional[List[ActionItem]] = None
    metadata: Optional[Dict[str, Any]] = None


# ======================
# PROMPT & EXAMPLES
# ======================

PROMPT = """
You are Phase-1 assistant. Your job is to analyze a short `situation` text and produce a concise, structured JSON response matching the specified schema exactly.

Schema (Phase1Response):
- status: one of "OK", "NEEDS_CONTEXT", "ERROR"
- reasoning: short explanation (1-5 sentences)
- confidence: float between 0.0 and 1.0
- decision: object describing the recommended decision and parameters
- actions: optional array of follow-up actions (objects)

REQUIREMENTS:
- Return ONLY a single JSON object and nothing else (no markdown, no backticks, no commentary).
- Fields must exactly match the schema types.
- Use numbers for `confidence` (0.0-1.0).
- If the `situation` is empty or insufficient, set `status` to "NEEDS_CONTEXT" and provide a short `reasoning` explaining what is missing.
- If an internal failure occurs, set `status` to "ERROR" and populate `reasoning`.

EXAMPLES: see `EXAMPLES` variable in this module.
"""

EXAMPLES: List[str] = [
    # 1: Clear actionable situation
    json.dumps({
        "status": "OK",
        "reasoning": "Sufficient details provided and actors identified.",
        "confidence": 0.87,
        "decision": {"action": "engage", "parameters": {"level": "limited"}},
        "actions": [
            {"type": "NOTIFY", "description": "Inform commander of limited engagement", "target": "commander"}
        ],
        "metadata": {"source": "example"}
    }),

    # 2: Missing context
    json.dumps({
        "status": "NEEDS_CONTEXT",
        "reasoning": "Location and timeframe missing; cannot assess urgency.",
        "confidence": 0.0,
        "decision": {"action": "none", "parameters": {}},
        "actions": [{"type": "GATHER_INFO", "description": "Request location and timeframe from reporter"}],
    }),

    # 3: Internal error
    json.dumps({
        "status": "ERROR",
        "reasoning": "Parsing failed due to malformed input.",
        "confidence": 0.0,
        "decision": {"action": "none", "parameters": {}},
    }),

    # 4: Low-confidence, monitoring suggestion
    json.dumps({
        "status": "OK",
        "reasoning": "Some indicators point to potential hostile intent but evidence is weak.",
        "confidence": 0.35,
        "decision": {"action": "monitor", "parameters": {"period": "2h"}},
        "actions": [{"type": "GATHER_INFO", "description": "Increase surveillance for 2 hours"}],
    }),
]


# ======================
# LLM INTERFACE
# ======================

def call_llm(prompt: str, model: Optional[str] = None, timeout: int = 30) -> str:
    """Call a local LLM (Ollama) using environment variables.

    Expects `OLLAMA_URL` and `OLLAMA_MODEL` (or `model` arg) to be set.
    Falls back to raising a RuntimeError with an explanatory message.

    Args:
        prompt: The prompt text to send to the LLM
        model: Optional model name (overrides OLLAMA_MODEL env var)
        timeout: Request timeout in seconds

    Returns:
        The LLM response text

    Raises:
        RuntimeError: If LLM is not configured
        requests.HTTPError: If the API request fails
    """
    ollama_url = os.getenv("OLLAMA_URL")
    ollama_model = model or os.getenv("OLLAMA_MODEL")

    if not ollama_url or not ollama_model:
        raise RuntimeError(
            "No LLM configured. Set OLLAMA_URL and OLLAMA_MODEL environment variables."
        )

    endpoint = ollama_url.rstrip("/") + "/api/generate"
    payload = {
        "model": ollama_model,
        "prompt": prompt,
        "temperature": 0,
        "top_p": 1,
        "top_k": 0,
        "max_tokens": 1024,
    }

    with requests.post(endpoint, json=payload, timeout=timeout, stream=True) as resp:
        resp.raise_for_status()

        # Ollama often streams newline-delimited JSON objects with a 'response' field.
        parts = []
        try:
            for raw_line in resp.iter_lines(decode_unicode=True):
                if not raw_line:
                    continue
                line = raw_line.strip()
                # Some servers send comma-separated chunks; try to parse JSON per line
                try:
                    obj = json.loads(line)
                    if isinstance(obj, dict) and "response" in obj:
                        parts.append(obj.get("response", ""))
                    elif isinstance(obj, dict) and "text" in obj:
                        parts.append(obj.get("text", ""))
                    else:
                        # Unexpected structure: append the raw line
                        parts.append(line)
                except json.JSONDecodeError:
                    # If line isn't JSON, append as-is
                    parts.append(line)
        except Exception:
            # Fallback to full body if streaming iteration fails
            return resp.text

        return "".join(parts)


# ======================
# RESPONSE VALIDATION
# ======================

def validate_response(raw: str) -> Phase1Response:
    """Parse and validate a raw LLM response string.

    Accepts raw string (expected to be JSON). Strips markdown fences if present.
    Raises ValueError on parse error or pydantic.ValidationError on schema mismatch.

    Args:
        raw: Raw response string from LLM

    Returns:
        Phase1Response: Validated response object

    Raises:
        ValueError: If response is not valid JSON
        pydantic.ValidationError: If response doesn't match schema
    """
    # Strip common markdown fences or accidental surrounding text
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        # remove leading fence and optional language tag
        parts = cleaned.split("\n", 1)
        if len(parts) > 1:
            cleaned = parts[1]
        # remove trailing fence
        if cleaned.rfind("```") != -1:
            cleaned = cleaned[: cleaned.rfind("```")]
    cleaned = cleaned.strip()

    try:
        obj = json.loads(cleaned)
    except Exception as e:
        raise ValueError(f"Response is not valid JSON: {e}")

    # Validate using pydantic v2 if available, otherwise v1 compatible parse
    try:
        if hasattr(Phase1Response, "model_validate"):
            validated = Phase1Response.model_validate(obj)
        else:
            validated = Phase1Response.parse_obj(obj)
    except Exception as e:
        # Re-raise for caller to handle; preserve original exception
        raise

    return validated


# ======================
# ANALYSIS FUNCTION
# ======================

def analyze_situation(situation: str, model: Optional[str] = None) -> Phase1Response:
    """Analyze a strategic situation using Phase-1.

    Args:
        situation: The situation text to analyze
        model: Optional LLM model name

    Returns:
        Phase1Response: The structured analysis result

    Raises:
        RuntimeError: If LLM is not configured
        ValueError: If response is invalid
    """
    full_prompt = PROMPT + "\n\nSITUATION:\n" + situation + "\n\nRespond with a single JSON object."
    raw = call_llm(full_prompt, model=model)
    validated = validate_response(raw)
    return validated


# ======================
# DEMO HARNESS
# ======================

def run_demo(situation: str = None):
    """Demo/test harness for Phase-1 analysis.

    Args:
        situation: The situation to analyze (or uses environment variable)
    """
    if situation is None:
        situation = os.getenv("PHASE1_SITUATION", "An escalation in the northern sector with unclear actors.")

    print("=" * 70)
    print("PHASE-1: STRATEGIC SITUATION ANALYSIS")
    print("=" * 70)
    print(f"\nSituation:\n{situation}\n")

    # Build full prompt
    full = PROMPT + "\n\nSITUATION:\n" + situation + "\n\nRespond with a single JSON object."

    try:
        raw = call_llm(full)
        print("=" * 70)
        print("RAW LLM OUTPUT")
        print("=" * 70)
        print(raw)
        print()

        # Validate
        validated = validate_response(raw)
        print("=" * 70)
        print("VALIDATED RESPONSE")
        print("=" * 70)
        
        # Pydantic v1 vs v2 compatibility for JSON output
        try:
            if hasattr(validated, "model_dump_json"):
                print(validated.model_dump_json(indent=2))
            else:
                print(validated.json(indent=2))
        except Exception:
            # Fallback to manual dump
            try:
                data = validated.model_dump() if hasattr(validated, "model_dump") else validated.dict()
            except Exception:
                data = validated.__dict__
            print(json.dumps(data, indent=2, ensure_ascii=False))
        
        print()
        print("=" * 70)
        print(f"Status: {validated.status} | Confidence: {validated.confidence:.2f}")
        print("=" * 70)
        
    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_demo()
