import os
import requests

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
MODEL = os.getenv(
    "TRIBUNAL_MODEL",
    "huihui_ai/deepseek-r1-abliterated:8b"
)


def synthesize_verdict(debate_records, question):
    """Synthesize a structured verdict from minister positions.
    
    Rules:
    - Uses ONLY minister inputs
    - Does NOT add new doctrine
    - Exposes conflicts clearly
    - States uncertainties explicitly
    - Does NOT give final advice (human retains authority)
    
    Args:
        debate_records: List of {minister, opinion} dicts.
        question: Original question being debated.
        
    Returns:
        Structured synthesis highlighting agreements, disagreements, risks, uncertainties.
    """
    blocks = []
    for r in debate_records:
        blocks.append(
            f"{r['minister']}:\n{r['opinion']}\n"
        )

    prompt = f"""
You are the Tribunal Synthesizer.

RULES:
- Use ONLY minister inputs
- Do NOT add new doctrine
- Expose conflicts clearly
- If uncertainty exists, state it
- DO NOT give final advice

QUESTION:
{question}

MINISTER POSITIONS:
{''.join(blocks)}

Return a structured synthesis highlighting:
- Agreements
- Disagreements
- Risks
- Open uncertainties
"""

    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.0,
            "top_p": 1
        }
    }

    r = requests.post(OLLAMA_URL, json=payload, timeout=120)
    r.raise_for_status()
    return r.json()["response"]
