from core.rag.minister_shelves import MINISTER_SHELVES
from core.knowledge.war_rag_bias import WAR_RAG_BIAS


class MinisterRAGSelector:
    def select(self, minister_name, books, mode):
        shelf_tags = set(MINISTER_SHELVES.get(minister_name, []))

        # 1) Filter to minister shelf
        candidates = [
            b for b in books
            if shelf_tags.intersection(set(b.get("shelves", [])))
        ]

        # If filtering removed everything, fall back to all books
        if not candidates:
            candidates = list(books)

        # 2) Score (mode-aware)
        if mode == "war":
            return self._score_war(candidates)
        return self._score_standard(candidates)

    def _score_war(self, books):
        scored = []
        for b in books:
            score = 0.0
            for d in b.get("domains", []):
                if d in WAR_RAG_BIAS.get("preferred_domains", []):
                    score += 2.0
            for t in b.get("tones", []):
                if t in WAR_RAG_BIAS.get("preferred_tones", []):
                    score += 1.5
            score *= b.get("priority", {}).get("war", 0.5)
            scored.append((score, b))
        return [b for _, b in sorted(scored, key=lambda x: x[0], reverse=True)]

    def _score_standard(self, books):
        return sorted(
            books,
            key=lambda b: b.get("priority", {}).get("standard", 0.5),
            reverse=True
        )
