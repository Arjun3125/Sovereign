"""
CLI utilities for source traceability inspection.

Enables --why, --show-source, --open-book flags to drill into knowledge origins.
"""

from typing import Dict, Any


class SourceInspector:
    """
    Inspect and display knowledge sources from retrieval results.
    
    Supports:
      --why chunk_id           → Show why this chunk was retrieved
      --show-source chunk_id   → Display full chunk with context
      --open-book book_id      → Show book metadata and contents
    """
    
    def __init__(self, retrieval_result: Dict[str, Any]):
        """
        Initialize with result from MinisterRetriever.retrieve_with_traceability().
        """
        self.result = retrieval_result
        self.all_chunks = retrieval_result.get("_all_chunks", {})
        self.minister = retrieval_result.get("_minister")
        self.query = retrieval_result.get("_query")
    
    def show_source(self, chunk_id: str) -> str:
        """Display full chunk with metadata."""
        chunk = self.all_chunks.get(chunk_id)
        if not chunk:
            return f"ERROR: Chunk {chunk_id} not found"
        
        lines = [
            f"CHUNK: {chunk_id}",
            f"BOOK: {chunk['book_id']}",
            f"CHAPTER: {chunk['chapter_title']}",
            f"LABEL: {chunk['label']}",
            f"POSITION: chars {chunk['start']}-{chunk['end']}",
            "---",
            chunk['text'],
            "---",
            f"ALLOWED FOR: {', '.join(chunk.get('allowed_ministers', []))}",
            f"DOMAINS: {', '.join(chunk.get('domains', []))}",
        ]
        return "\n".join(lines)
    
    def why(self, chunk_id: str) -> str:
        """Explain why chunk was retrieved."""
        chunk = self.all_chunks.get(chunk_id)
        if not chunk:
            return f"ERROR: Chunk {chunk_id} not found"
        
        # Determine category
        category = None
        for cat in ["support", "counter", "neutral"]:
            if any(c["chunk_id"] == chunk_id for c in self.result.get(cat, [])):
                category = cat
                break
        
        lines = [
            f"WHY RETRIEVED: {category or 'unknown'}",
            f"MINISTER: {self.minister}",
            f"QUERY: {self.query}",
            f"SEMANTIC LABEL: {chunk['label']}",
            f"JUSTIFICATION: This chunk is labeled '{chunk['label']}', which is ",
            f"  {'supporting evidence' if category == 'support' else 'counter-evidence' if category == 'counter' else 'context'},",
            f"  retrieved to inform {self.minister}'s advice.",
        ]
        return "\n".join(lines)
    
    def open_book(self, book_id: str) -> str:
        """Display book metadata and all chunks from that book."""
        # Find all chunks from this book
        book_chunks = [
            c for c in self.all_chunks.values()
            if c.get("book_id") == book_id
        ]
        
        if not book_chunks:
            return f"ERROR: No chunks from book {book_id}"
        
        # Group by chapter
        by_chapter = {}
        for c in book_chunks:
            ch = c.get("chapter_title", "unknown")
            if ch not in by_chapter:
                by_chapter[ch] = []
            by_chapter[ch].append(c)
        
        lines = [
            f"BOOK: {book_id}",
            f"CHAPTERS USED: {', '.join(by_chapter.keys())}",
            f"TOTAL CHUNKS: {len(book_chunks)}",
            "---",
        ]
        
        for chapter, chunks in by_chapter.items():
            lines.append(f"\n{chapter}:")
            for c in chunks:
                lines.append(f"  [{c['chunk_id'][:8]}...] {c['label']}")
        
        return "\n".join(lines)
    
    def summarize(self) -> str:
        """Print summary of all retrieval categories."""
        support = self.result.get("support", [])
        counter = self.result.get("counter", [])
        neutral = self.result.get("neutral", [])
        
        lines = [
            f"RETRIEVAL SUMMARY",
            f"MINISTER: {self.minister}",
            f"QUERY: {self.query}",
            f"",
            f"SUPPORT ({len(support)} chunks):",
        ]
        
        for c in support:
            lines.append(f"  + [{c['chunk_id'][:8]}...] {c['chapter_title']}")
        
        if counter:
            lines.append(f"\nCOUNTER ({len(counter)} chunks):")
            for c in counter:
                lines.append(f"  - [{c['chunk_id'][:8]}...] {c['chapter_title']}")
        
        if neutral:
            lines.append(f"\nNEUTRAL ({len(neutral)} chunks):")
            for c in neutral:
                lines.append(f"  ~ [{c['chunk_id'][:8]}...] {c['chapter_title']}")
        
        return "\n".join(lines)
