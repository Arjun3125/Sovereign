"""
Phase-1: Whole book → canonical chapters (LLM).

Single LLM call for entire book.
Output: structured chapters with preserved text.
"""

import os
from .llm_client import call_llm, LLMError
from .prompts import phase1_system, phase1_user
from .validators import validate_phase1, ValidationError


def phase1_structure(book_text: str, model: str = None) -> dict:
    """
    Phase-1: Extract canonical chapters from entire book.

    Args:
        book_text: Full book text (single string)
        model: LLM model name (default: env OLLAMA_MODEL)

    Returns:
        {
            "book_title": "string",
            "author": null,
            "chapters": [
                {
                    "chapter_index": 1,
                    "chapter_title": "string",
                    "chapter_text": "string"
                },
                ...
            ]
        }

    Raises:
        LLMError: If LLM call fails
        ValidationError: If output schema invalid
    """
    system_prompt = phase1_system()
    user_prompt = phase1_user(book_text)
    full_prompt = system_prompt + "\n\n" + user_prompt

    # Call LLM
    result = call_llm(full_prompt, model)

    # Validate
    validate_phase1(result)

    return result
