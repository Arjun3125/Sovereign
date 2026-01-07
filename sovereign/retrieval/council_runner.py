from .minister_retriever import retrieve_for_minister
from ..config.ministers import MINISTER_DOMAINS

def minister_position(minister: str, doctrines: list, question: str) -> str:
    """Format minister position from retrieved doctrines."""
    if not doctrines:
        return f"No doctrine available on this topic for {minister}."
    
    doctrine_refs = ", ".join([d["doctrine_id"] for d in doctrines])
    avg_conf = sum(d["confidence"] for d in doctrines) / len(doctrines)
    
    return f"Based on doctrines {doctrine_refs} (avg confidence {avg_conf:.0%}), the posture is informed by these principles."

def run_council(question: str, ministers: list = None) -> dict:
    """Run query across all (or selected) ministers."""
    if ministers is None:
        ministers = list(MINISTER_DOMAINS.keys())
    
    outputs = {}

    for m in ministers:
        doctrines = retrieve_for_minister(m, question, top_k=3)
        avg_conf = (
            sum(d["confidence"] for d in doctrines) / max(len(doctrines), 1)
        )
        position = minister_position(m, doctrines, question)
        
        outputs[m] = {
            "minister": m,
            "position": position,
            "confidence": avg_conf,
            "doctrine_ids": [d["doctrine_id"] for d in doctrines],
            "doctrines": doctrines,
            "count": len(doctrines)
        }

    return outputs
