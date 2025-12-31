from typing import List, Dict, Any, Optional
from core.knowledge.minister_binding import MINISTER_RAG_BINDING


class MinisterRetriever:
    def __init__(self, rag_index: Optional[object] = None, embed_fn: Optional[callable] = None):
        # rag_index may be a VectorIndex or our RAGIndex; prefer RAGIndex if it has books
        self.index = rag_index
        self.embed_fn = embed_fn

    def retrieve_for_minister(
        self,
        minister_name: str,
        query: str,
        k: int = 5,
        include_counter: bool = False,
        decision_id: str = None,
        mode: str = "standard",
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
        # If a RAGIndex (persisted books) is available, use shelf-based retrieval
        try:
            from core.rag.index import RAGIndex
            from core.rag.shelves import ShelfBuilder
            from core.rag.retriever import RAGRetriever
            # If self.index is None or not a RAGIndex, try to load one from default location
            rag_idx = None
            if hasattr(self.index, "books") and isinstance(self.index.books, dict):
                rag_idx = self.index
            else:
                try:
                    rag_idx = RAGIndex().load()
                except Exception:
                    rag_idx = None

            if rag_idx and getattr(rag_idx, "books", {}):
                builder = ShelfBuilder(rag_idx)
                shelves = builder.build_for_minister(minister_name, war=(mode == "war"))
                retr = RAGRetriever(shelves)
                results = retr.retrieve(query, minister_name, top_k=k, decision_id=decision_id)
                # Convert results into support/counter/neutral simple buckets
                return {"support": results, "counter": [], "neutral": []}
        except Exception:
            # fallback to vector retrieval below
            pass

        # Fallback: vector-index based retrieval if embed_fn and index provide search
        if self.embed_fn is None or self.index is None:
            raise ValueError("No retrieval backend available: provide rag_index or embed_fn+vector index")

        binding = MINISTER_RAG_BINDING.get(minister_name)
        if binding is None:
            raise ValueError(f"Minister {minister_name} has no RAG access")

        q_emb = self.embed_fn(query)
        all_results = self.index.search(q_emb, k=k * 3)

        allowed_domains = set(binding.get("domains", []))
        allowed_books = set(binding.get("books", []))

        filtered = [
            r for r in all_results
            if r.get("domains") and any(d in allowed_domains for d in r.get("domains", []))
            and r.get("book_id") in allowed_books
        ]

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
