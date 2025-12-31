from cold_strategist.query.confidence import compute_confidence
from cold_strategist.query.provenance import build_provenance
from cold_strategist.query.formatter import phrase_answer


class QueryEngine:
    """
    Hardened query engine.
    Read-only. No side effects.
    """

    def __init__(self, universal_store, book_store):
        self.universal_store = universal_store
        self.book_store = book_store

    def query(self, question: str):
        # 1️⃣ Try universal principles first
        principles = self.universal_store.search(question)

        authority = "universal"

        if not principles:
            principles = self.book_store.search(question)
            authority = "book"

        if not principles:
            return {
                "answer": None,
                "confidence": 0.0,
                "authority": "none",
                "sources": {}
            }

        # 2️⃣ Build provenance
        provenance = build_provenance(principles)

        # 3️⃣ Compute confidence
        confidence = compute_confidence(
            authority=authority,
            unique_books=len(provenance["books"]),
            support_count=len(principles)
        )

        # 4️⃣ Phrase answer (LLM = phrasing only)
        answer = phrase_answer(
            [p["text"] for p in principles]
        )

        return {
            "answer": answer,
            "confidence": confidence,
            "authority": authority,
            "sources": provenance
        }
