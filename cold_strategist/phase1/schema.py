from pydantic import BaseModel, Field
from typing import Literal, Optional, List, Dict, Any


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
