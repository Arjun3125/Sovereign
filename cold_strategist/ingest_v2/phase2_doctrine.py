"""
Phase-2: Each chapter → doctrine (LLM).

Per-chapter LLM call.
Output: 15-domain classification, principles, rules, claims, warnings, cross-refs.
"""

from .llm_client import call_llm, LLMError
from .prompts import phase2_system, phase2_user
from .validators import validate_phase2, ValidationError


def phase2_doctrine(chapter: dict, model: str = None) -> dict:
    """
    Phase-2: Extract doctrine from one chapter.

    Args:
        chapter: {
            "chapter_index": int,
            "chapter_title": str,
            "chapter_text": str (entire chapter)
        }
        model: LLM model name (default: env OLLAMA_MODEL)

    Returns:
        {
            "chapter_index": int,
            "chapter_title": str,
            "domains": [list of domain strings],
            "principles": [list of principle strings],
            "rules": [list of rule strings],
            "claims": [list of claim strings],
            "warnings": [list of warning strings],
            "cross_references": [list of chapter indices]
        }

    Raises:
        LLMError: If LLM call fails
        ValidationError: If output schema invalid
    """
    system_prompt = phase2_system()
    user_prompt = phase2_user(chapter)
    full_prompt = system_prompt + "\n\n" + user_prompt

    # Call LLM
    result = call_llm(full_prompt, model)

    # Validate
    validate_phase2(result)

    return result
