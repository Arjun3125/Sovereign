"""
War-Aware RAG Retriever

Wraps the standard retriever to apply War Mode book selection bias.

When mode == "war":
- Retrieves books ranked by WarRAGSelector preference
- Prefers dark/strategic texts
- De-prioritizes moral/harmony texts
- Preserves traceability (book → chapter → principle → advice)

When mode != "war":
- Falls back to standard uniform retrieval
"""

from typing import Dict, List, Any, Optional
from core.knowledge.war_rag_selector import WarRAGSelector
from core.knowledge.book_metadata_loader import BookMetadataLoader
from core.knowledge.minister_retriever import MinisterRetriever


class WarAwareRAGRetriever:
    """
    War-Mode-aware wrapper around the standard MinisterRetriever.
    
    Usage:
        retriever = WarAwareRAGRetriever(
            base_retriever=minister_retriever,
            metadata_loader=loader
        )
        
        # War Mode: uses bias
        results = retriever.retrieve_for_minister(
            minister_name="Power",
            query="how to consolidate control",
            mode="war"
        )
        
        # Standard Mode: uses default ranking
        results = retriever.retrieve_for_minister(
            minister_name="Power",
            query="how to consolidate control",
            mode="standard"
        )
    """

    def __init__(
        self,
        base_retriever: MinisterRetriever,
        metadata_loader: BookMetadataLoader = None
    ):
        """
        Args:
            base_retriever: Standard MinisterRetriever instance
            metadata_loader: BookMetadataLoader instance (loads book metadata YAML)
                           If None, creates a default loader
        """
        self.base_retriever = base_retriever
        self.metadata_loader = metadata_loader or BookMetadataLoader()
        self.war_selector = WarRAGSelector()

    def retrieve_for_minister(
        self,
        minister_name: str,
        query: str,
        mode: str = "standard",
        k: int = 5,
        include_counter: bool = False,
        include_audit: bool = False,
    ) -> Dict[str, Any]:
        """
        Retrieve knowledge chunks for a minister, applying War Mode bias if active.
        
        Args:
            minister_name: Name of minister
            query: Query string
            mode: "war", "standard", or "quick" (affects book ranking)
            k: Number of results per category
            include_counter: Include counter-evidence chunks
            include_audit: Include audit trail showing book scoring
            
        Returns:
            Dict with structure:
                {
                    "support": [chunks with traceability],
                    "counter": [chunks] (if include_counter),
                    "neutral": [chunks],
                    "mode": "war",
                    "book_rankings": [...] (if include_audit),
                }
        """
        # First, get standard retrieval from base retriever
        result = self.base_retriever.retrieve_for_minister(
            minister_name=minister_name,
            query=query,
            k=k,
            include_counter=include_counter
        )

        # If War Mode active, apply book selection bias
        if mode == "war":
            result = self._apply_war_mode_bias(
                result=result,
                minister_name=minister_name,
                mode=mode,
                include_audit=include_audit
            )

        # Add mode to result for transparency
        result["mode"] = mode

        return result

    def _apply_war_mode_bias(
        self,
        result: Dict[str, List[Dict]],
        minister_name: str,
        mode: str,
        include_audit: bool = False
    ) -> Dict[str, Any]:
        """
        Apply War Mode book selection bias to retrieval results.
        
        Algorithm:
        1. Group chunks by book
        2. Score each book using WarRAGSelector
        3. Re-rank books by score
        4. Return top-ranked books' chunks
        5. Preserve all traceability metadata
        
        Args:
            result: Standard retrieval result with chunks
            minister_name: For reference/audit
            mode: "war" or other (for audit)
            include_audit: If True, include book_rankings in result
            
        Returns:
            Modified result with War Mode ranking applied
        """
        # Load all book metadata
        all_books = self.metadata_loader.load_all()

        # Group result chunks by book
        chunks_by_book = {}
        for category in ["support", "counter", "neutral"]:
            if category not in result:
                continue

            for chunk in result.get(category, []):
                book_id = chunk.get("book_id")
                if not book_id:
                    continue

                if book_id not in chunks_by_book:
                    chunks_by_book[book_id] = {
                        "metadata": all_books.get(book_id, {}),
                        "chunks": {
                            "support": [],
                            "counter": [],
                            "neutral": []
                        }
                    }

                chunks_by_book[book_id]["chunks"][category].append(chunk)

        # Score each book, sort by War Mode preference
        books_with_scores = [
            (book_id, data["metadata"], self.war_selector.score(data["metadata"]))
            for book_id, data in chunks_by_book.items()
        ]
        books_with_scores.sort(key=lambda x: x[2], reverse=True)

        # Re-organize result by ranked books (War Mode order)
        war_result = {
            "support": [],
            "counter": [],
            "neutral": []
        }

        audit_rankings = []

        for book_id, book_meta, score in books_with_scores:
            chunks = chunks_by_book[book_id]["chunks"]

            for category in ["support", "counter", "neutral"]:
                war_result[category].extend(chunks[category])

            if include_audit:
                audit = self.war_selector.audit(book_meta, score)
                audit_rankings.append(audit)

        # Update result with War Mode ranking
        result.update(war_result)

        if include_audit:
            result["book_rankings"] = audit_rankings

        return result

    def get_book_audit(self, book_id: str) -> Dict:
        """
        Get detailed audit of why a book scores what it does in War Mode.
        
        Args:
            book_id: Book identifier
            
        Returns:
            Audit dict with scoring breakdown
        """
        metadata = self.metadata_loader.load_one(book_id)
        score = self.war_selector.score(metadata)
        return self.war_selector.audit(metadata, score)
