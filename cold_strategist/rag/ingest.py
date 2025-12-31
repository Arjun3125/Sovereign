from rag.schema import KnowledgeChunk, SourceRef
from typing import List


def ingest_book(book_name: str, parsed_sections: List[dict]) -> List[KnowledgeChunk]:
    chunks = []

    for section in parsed_sections:
        chunk = KnowledgeChunk(
            text=section["principle"],  # rewritten insight
            domain=section["domain"],
            source=SourceRef(
                book=book_name,
                principle=section["principle_name"],
                location=section.get("location"),
                confidence=section.get("confidence", 0.7),
            )
        )
        chunks.append(chunk)

    return chunks
