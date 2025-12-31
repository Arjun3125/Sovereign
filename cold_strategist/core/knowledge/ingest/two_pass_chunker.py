"""
Two-Pass Semantic Chunking for Books

Pass 1: Structural (offline)
  - Split by chapter/section
  - Split by semantic label (story, principle, warning, etc.)
  - Preserve story narrative with principle mapping

Pass 2: Semantic (LLM-assisted, optional)
  - Map stories to principles
  - Extract application_space
  - Create principle-centric chunks

Result: Each chunk has:
  - principle: Core actionable insight
  - pattern: Recurring observation
  - application_space: Where this applies
  - supporting_story: Narrative that illustrates the principle
  - source: Full traceability (book, chapter, page)
"""

from typing import List, Dict, Any, Optional, Callable
import hashlib


class TwoPassSemanticChunker:
    """
    Chunks book text while preserving stories and mapping them to principles.
    
    Philosophy:
    - Stories are NOT noise; they illustrate principles
    - Each chunk should be principle-centric with supporting narrative
    - Traceability ALWAYS preserved (book → chapter → page → principle)
    """

    def __init__(
        self,
        llm_call: Optional[Callable[[str], str]] = None,
        max_principle_chars: int = 500,
    ):
        """
        Args:
            llm_call: LLM function for semantic mapping (optional)
            max_principle_chars: Max chars for principle statement (usually short)
        """
        self.llm_call = llm_call
        self.max_principle_chars = max_principle_chars

    def process_section(
        self,
        section_text: str,
        book_id: str,
        chapter_title: str,
        chapter_num: int = 0,
        page_start: int = 0,
    ) -> List[Dict[str, Any]]:
        """
        Process a chapter/section into principle-centric chunks.
        
        Args:
            section_text: Raw text of chapter
            book_id: Book identifier
            chapter_title: Chapter name/title
            chapter_num: Chapter number (for ordering)
            page_start: Starting page number
            
        Returns:
            List of chunks, each with structure:
                {
                    "chunk_id": "art_of_seduction_ch3_p112_principle1",
                    "principle": "Charm disarms resistance before desire forms.",
                    "pattern": "Low-pressure presence increases attraction.",
                    "application_space": ["courtship", "influence", "negotiation"],
                    "supporting_story": "In the story of The Rake...",
                    "semantic_label": "principle",
                    "source": {
                        "book_id": "art_of_seduction",
                        "chapter_title": "The Art of Charm",
                        "chapter_num": 3,
                        "page_start": 112,
                        "page_end": 118,
                    },
                    "text": "Full verbatim section text",
                    "start_char": 0,
                    "end_char": 1200,
                }
        """
        chunks = []

        # Pass 1: Structural slicing
        # Split by semantic patterns (principle, story, warning, etc.)
        structural_chunks = self._structural_split(
            text=section_text,
            book_id=book_id,
            chapter_title=chapter_title,
            chapter_num=chapter_num,
            page_start=page_start,
        )

        # Pass 2: Semantic enrichment (if LLM available)
        if self.llm_call:
            for chunk in structural_chunks:
                enriched = self._enrich_with_principle(chunk)
                chunks.append(enriched)
        else:
            chunks = structural_chunks

        return chunks

    def _structural_split(
        self,
        text: str,
        book_id: str,
        chapter_title: str,
        chapter_num: int,
        page_start: int,
    ) -> List[Dict[str, Any]]:
        """
        Structural Pass: Split by obvious semantic boundaries.
        
        Looks for patterns like:
        - "The principle is: ..."
        - "Example: ..."
        - "In the story of X, ..."
        - "Warning: ..."
        """
        chunks = []

        # For now, simple heuristic: split on major paragraphs
        # In practice, could use more sophisticated detection

        paragraphs = text.split("\n\n")
        char_pos = 0

        for para in paragraphs:
            if not para.strip():
                char_pos += len(para) + 2
                continue

            # Detect semantic label
            label = self._detect_label(para)

            chunk = {
                "chunk_id": self._make_chunk_id(
                    book_id, chapter_num, page_start, len(chunks)
                ),
                "principle": None,  # Will be filled in Pass 2
                "pattern": None,
                "application_space": [],
                "supporting_story": None,
                "semantic_label": label,
                "source": {
                    "book_id": book_id,
                    "chapter_title": chapter_title,
                    "chapter_num": chapter_num,
                    "page_start": page_start,
                    "page_end": page_start + (len(text[:char_pos]) // 250),  # Rough estimate
                },
                "text": para.strip(),
                "start_char": char_pos,
                "end_char": char_pos + len(para),
            }

            chunks.append(chunk)
            char_pos += len(para) + 2

        return chunks

    def _detect_label(self, paragraph: str) -> str:
        """
        Detect semantic label from paragraph content.
        
        Returns one of: "principle", "story", "warning", "example", "pattern", "context"
        """
        text_lower = paragraph.lower()

        if any(p in text_lower for p in ["principle is", "the rule is", "always"]):
            return "principle"

        if any(p in text_lower for p in ["for example", "for instance", "like when"]):
            return "example"

        if any(p in text_lower for p in ["warning", "never", "avoid", "dangerous"]):
            return "warning"

        if any(
            p in text_lower
            for p in [
                "in the story",
                "consider",
                "take",
                "imagine",
                "suppose",
            ]
        ):
            return "story"

        if any(p in text_lower for p in ["pattern", "tends to", "often", "usually"]):
            return "pattern"

        return "context"

    def _enrich_with_principle(self, chunk: Dict[str, Any]) -> Dict[str, Any]:
        """
        Pass 2: Use LLM to extract/map principle from story/example.
        
        If label is "story" or "example", ask LLM:
        - What principle does this illustrate?
        - What's the pattern?
        - Where would this apply?
        """
        if chunk["semantic_label"] not in ["story", "example", "context"]:
            # Already has structure, just clean up
            if chunk["semantic_label"] == "principle":
                chunk["principle"] = chunk["text"]
            elif chunk["semantic_label"] == "pattern":
                chunk["pattern"] = chunk["text"]

            return chunk

        # For story/example/context, ask LLM to extract principle
        if not self.llm_call:
            return chunk

        prompt = f"""
You are a PRINCIPLE EXTRACTOR.

Given this excerpt from a book:
---
{chunk['text']}
---

Extract (or infer) the underlying PRINCIPLE in one sentence.
Then list 2-3 domains where this principle applies.

Output format (STRICT):
principle|<one sentence principle>
pattern|<one sentence pattern/observation>
application|<domain1>,<domain2>,<domain3>

Do NOT summarize the story. Extract the ACTIONABLE INSIGHT.
"""

        try:
            response = self.llm_call(prompt)
            chunk = self._parse_enrichment_response(response, chunk)
        except Exception as e:
            print(f"Warning: LLM enrichment failed: {e}")
            # Fallback: treat text as principle if it's short
            if len(chunk["text"]) < self.max_principle_chars:
                chunk["principle"] = chunk["text"]
            else:
                chunk["supporting_story"] = chunk["text"]

        return chunk

    def _parse_enrichment_response(
        self, response: str, chunk: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Parse LLM enrichment response."""
        lines = response.strip().split("\n")

        for line in lines:
            if "|" not in line:
                continue

            parts = line.split("|", 1)
            key = parts[0].lower().strip()
            value = parts[1].strip()

            if key == "principle":
                chunk["principle"] = value
            elif key == "pattern":
                chunk["pattern"] = value
            elif key == "application":
                chunk["application_space"] = [
                    d.strip() for d in value.split(",")
                ]

        # If no principle extracted, treat original text as supporting story
        if not chunk["principle"]:
            chunk["supporting_story"] = chunk["text"]

        return chunk

    def _make_chunk_id(
        self, book_id: str, chapter_num: int, page_start: int, chunk_index: int
    ) -> str:
        """Generate deterministic chunk ID."""
        base = f"{book_id}_ch{chapter_num}_p{page_start}_c{chunk_index}"
        return base

    @staticmethod
    def chunk_to_retrieval_format(chunk: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert principle-centric chunk to retrieval-friendly format.
        
        Used when returning chunks to LLM/minister for advice generation.
        """
        return {
            "chunk_id": chunk["chunk_id"],
            "principle": chunk.get("principle"),
            "pattern": chunk.get("pattern"),
            "application_space": chunk.get("application_space", []),
            "source": chunk["source"],
            "source_text": chunk["text"],  # Full verbatim for reference
        }
