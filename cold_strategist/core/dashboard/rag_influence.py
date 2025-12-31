from typing import Dict, Any, List
from core.memory.memory_store import MemoryStore


def rag_influence_for_advice(advice_id: str) -> Dict[str, Any]:
    """Return RAG trace for a specific advice item (best-effort).

    Looks up any stored rag_trace entries in MemoryStore (if implemented).
    """
    store = MemoryStore()

    try:
        # Best-effort: MemoryStore may expose a method to query rag traces; otherwise return empty
        traces = store.db.get_rag_trace(advice_id)
    except Exception:
        traces = None

    if not traces:
        return {"advice_id": advice_id, "trace": None, "note": "No RAG trace available"}

    # Normalize trace into view
    return {"advice_id": advice_id, "trace": traces}
