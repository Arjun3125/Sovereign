from typing import List


def build_trace(chunks: List) -> List[dict]:
    return [
        {
            "book": c.source.book,
            "principle": c.source.principle,
            "location": c.source.location,
            "confidence": c.source.confidence
        }
        for c in chunks
    ]
