from typing import Dict, Any


def summarize_books(scores: Dict[str, float]) -> Dict[str, Any]:
    top = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)
    return {"top_books": top[:10], "count": len(scores)}
