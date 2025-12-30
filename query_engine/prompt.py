from typing import List, Dict


def build_prompt(question: str, chapters: List[Dict]) -> str:
    blocks = []

    for ch in chapters:
        blocks.append(
            f"""
CHAPTER {ch['chapter_index']} — {ch['chapter_title']}
Principles: {ch.get('principles', [])}
Claims: {ch.get('claims', [])}
Rules: {ch.get('rules', [])}
Warnings: {ch.get('warnings', [])}
"""
        )

    context = "\n".join(blocks)

    return f"""
You are a reasoning engine.

RULES:
- Use ONLY the provided chapters
- Do NOT invent information
- If doctrine is insufficient, say so
- Cite chapter indices explicitly

QUESTION:
{question}

DOCTRINE:
{context}

Return a clear, cold answer with citations.
"""
