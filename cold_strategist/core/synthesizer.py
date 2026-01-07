from typing import Any, Dict

class MinisterSynthesizer:
    """Minimal synthesizer interface. Real implementations should subclass/replace this."""
    def __init__(self, llm=None):
        self.llm = llm

    def synthesize(self, minister_name: str, goal: str, context: str, retrieved: Any) -> Dict[str, Any]:
        """
        Should return a dict matching minister output shape or {'silence': True}.
        This is a placeholder deterministic stub that signals silence.
        """
        return {"silence": True}
