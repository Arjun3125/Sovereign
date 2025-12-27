from typing import List, Dict, Any
from core.knowledge.minister_binding import MINISTER_RAG_BINDING


class MinisterRetriever:
    def __init__(self, rag_index, embed_fn):
        self.index = rag_index
        self.embed_fn = embed_fn

    def retrieve_for_minister(
        self,
        minister_name: str,
        query: str,
        k: int = 5,
        include_counter: bool = False
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Retrieve knowledge chunks for a minister, enforcing domain/book permissions.
        
        Returns structured result with support/counter/neutral categorization.
        Each chunk includes full traceability: chunk_id, book_id, chapter_title, text.

        Args:
            minister_name: Name of minister (must exist in MINISTER_RAG_BINDING)
            query: Query string to search
            k: Number of results to retrieve per category
            include_counter: If True, also retrieve counter-evidence (default False)

        Raises:
            ValueError if minister has no binding.

        Returns:
            Dict with keys 'support', 'counter', 'neutral', each containing list of
            chunks with full traceability metadata:
              - chunk_id
              - book_id
              - chapter_title
              - text (verbatim)
              - label (semantic type)
              - start, end (char positions)
              - domains, allowed_ministers (permissions)
        """
        if minister_name not in MINISTER_RAG_BINDING:
            raise ValueError(f"Minister {minister_name} has no RAG access")

        binding = MINISTER_RAG_BINDING[minister_name]

        # Retrieve from vector index
        q_emb = self.embed_fn(query)
        all_results = self.index.search(q_emb, k=k * 3)  # Get more to filter + categorize

        # HARD FILTER: domain and book permissions
        allowed_domains = set(binding.get("domains", []))
        allowed_books = set(binding.get("books", []))

        filtered = [
            r for r in all_results
            if r.get("domains") and any(d in allowed_domains for d in r.get("domains", []))
            and r.get("book_id") in allowed_books
        ]

        # Categorize by semantic label
        support = [
            c for c in filtered
            if c.get("label") in {"principle", "story", "example"}
        ][:k]

        counter = [
            c for c in filtered
            if c.get("label") in {"warning", "failure_case"}
        ][:k] if include_counter else []

        neutral = [
            c for c in filtered
            if c.get("label") in {"analogy", "context"}
        ][:k]

        return {
            "support": support,
            "counter": counter,
            "neutral": neutral,
        }

    def retrieve_with_traceability(
        self,
        minister_name: str,
        query: str,
        k: int = 5
    ) -> Dict[str, Any]:
        """
        Retrieve chunks with full source inspection capabilities.
        
        Result includes helper methods for CLI:
          - get_chunk(chunk_id) → full chunk
          - get_source(chunk_id) → (book_id, chapter_title, text)
          - open_book(book_id) → book metadata
        """
        result = self.retrieve_for_minister(minister_name, query, k=k, include_counter=True)
        
        # Flatten for source lookup
        all_chunks = {}
        for category in ["support", "counter", "neutral"]:
            for chunk in result[category]:
                all_chunks[chunk["chunk_id"]] = chunk
        
        result["_all_chunks"] = all_chunks
        result["_minister"] = minister_name
        result["_query"] = query
        
        return result
