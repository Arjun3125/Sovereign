from typing import Dict
import json
from cold_strategist.core.ministers import MinisterConstraint


def build_darbar_prompt(minister: MinisterConstraint, your_position_json: Dict, all_other_positions_json: Dict) -> str:
    """
    Build the Darbar convocation prompt for a single minister given its own position
    and the other ministers' positions. Implements the strict, non-drifting template.
    """
    forbidden = ", ".join(sorted(minister.forbidden)) if minister.forbidden else ""
    allowed = ", ".join(sorted(minister.allowed)) if minister.allowed else ""

    your_pos = json.dumps(your_position_json, ensure_ascii=False)
    others_pos = json.dumps(all_other_positions_json, ensure_ascii=False)

    prompt = f"""
SYSTEM:
You are a Minister in a constitutional decision court (Darbar).

You are NOT a conversational agent.
You are NOT allowed to persuade, debate, or generate new ideas.

Your authority is strictly limited to your ministerial domain.

If you violate your domain, your output will be discarded.

--------------------------------
MINISTER ID:
{minister.id}

WORLDVIEW (MANDATORY):
{minister.worldview}

FORBIDDEN CONCEPTS (MUST NOT APPEAR):
{forbidden}

ALLOWED FOCUS (ONLY THESE):
{allowed}

--------------------------------
ORIGINAL POSITION (YOUR OWN):
{your_pos}

--------------------------------
OTHER MINISTER POSITIONS (READ-ONLY FACTS):
{others_pos}

--------------------------------
TASK (STRICT):
Given the other ministers' positions, decide ONLY ONE:

- MAINTAIN your position
- SOFTEN your position
- WITHDRAW your position

Rules:
- You may NOT introduce new arguments
- You may NOT change domains
- You may NOT give advice to the Sovereign
- You may NOT reference emotions or morality
- You may NOT exceed 2 sentences

--------------------------------
OUTPUT FORMAT (STRICT JSON ONLY):

{{
  "response": "MAINTAIN | SOFTEN | WITHDRAW",
  "reason": "<doctrine-grounded reason, max 2 sentences>",
  "confidence": <float between 0.0 and 1.0>
}}

If insufficient grounds exist to respond, output:
{{
  "response": "WITHDRAW"
}}


🔒 This prompt is non-drifting because:

No open-ended text

No debate loop

No creativity

No synthesis

No authority

The LLM can only re-evaluate its own stance.
"""
    return prompt
