"""
DEBATE SYNTHESIZER — Format minister positions into auditable debate transcript

Uses Ollama ONLY as a formatter + reasoning narrator. 
NO new doctrine introduced. NO decisions made.

Key constraint: Temperature = 0 (deterministic)
"""

import requests
import json

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3.1:8b-instruct-q4_0"

SYSTEM_PROMPT = """You are the Sovereign Council Scribe.

STRICT RULES:
1. Do NOT invent facts
2. Do NOT add strategies or advice
3. Do NOT moralize
4. Use ONLY the provided minister positions and doctrine references
5. Surface disagreements clearly
6. Highlight contradictions
7. Do NOT resolve the debate
8. Your job is to RECORD the debate, not decide

Output a structured council debate transcript where each minister speaks based on their retrieved doctrines."""

def synthesize_debate(question: str, council_outputs: dict) -> str:
    """
    Synthesize council positions into a debate transcript.
    
    Args:
        question: user query
        council_outputs: dict of {minister: {position, doctrine_ids, confidence}}
    
    Returns:
        Formatted debate transcript (read-only, audit trail)
    """
    
    # Build formatted positions for Ollama
    positions_text = "MINISTER POSITIONS:\n\n"
    for minister, output in council_outputs.items():
        positions_text += f"{minister}:\n"
        positions_text += f"  Position: {output['position']}\n"
        positions_text += f"  Doctrines: {', '.join(output['doctrine_ids'])}\n"
        positions_text += f"  Confidence: {output['confidence']:.0%}\n\n"

    prompt = f"""QUESTION FOR COUNCIL:
{question}

{positions_text}

TASK: Produce a structured council debate transcript.

Rules:
- Each minister speaks once, using ONLY their listed doctrines
- Reference specific doctrine IDs in brackets [DOC_ID]
- Explicitly note where ministers disagree
- Surface logical contradictions
- Do NOT add new arguments
- End with: "Debate concluded. Tribunal review required."

Format: Natural dialogue where ministers explain their doctrine-grounded positions."""

    payload = {
        "model": MODEL,
        "system": SYSTEM_PROMPT,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.0,  # Deterministic
            "top_p": 1.0
        }
    }

    try:
        r = requests.post(OLLAMA_URL, json=payload, timeout=120)
        r.raise_for_status()
        return r.json()["response"]
    except Exception as e:
        return f"[DEBATE SYNTHESIS ERROR: {str(e)}]"


def extract_disagreements(council_outputs: dict) -> list:
    """
    Extract high-disagreement minister pairs (confidence spread > 0.3).
    
    Returns:
        List of (minister1, minister2, spread) tuples
    """
    ministers = list(council_outputs.items())
    disagreements = []
    
    for i, (m1, out1) in enumerate(ministers):
        for m2, out2 in ministers[i+1:]:
            spread = abs(out1["confidence"] - out2["confidence"])
            if spread > 0.30:  # Significant disagreement
                disagreements.append((m1, m2, spread))
    
    return sorted(disagreements, key=lambda x: x[2], reverse=True)
