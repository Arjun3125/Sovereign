"""
Phase-2: Chapter → Doctrine (LLM)

This is the semantic compilation phase. Extracts doctrine with 15-domain classification.
"""
import sys
import threading
import time
from .llm_client import call_llm, LLMError
from .prompts_v2 import phase2_system, phase2_user


def _show_chapter_progress(chapter_idx: int, stop_event):
    """Show progress spinner for chapter processing."""
    spinner = "|/-\\"
    i = 0
    last_print = 0
    while not stop_event.is_set():
        # Only update every 0.5 seconds to reduce output
        if time.time() - last_print >= 0.5:
            sys.stdout.write(f"\r[PHASE-2] Processing chapter {chapter_idx}... {spinner[i % len(spinner)]}")
            sys.stdout.flush()
            i += 1
            last_print = time.time()
        time.sleep(0.1)
    sys.stdout.write("\r" + " " * 60 + "\r")  # Clear line
    sys.stdout.flush()


def phase2_doctrine(chapter: dict, model: str = None) -> dict:
    """
    Extract doctrine from one chapter using LLM.

    Args:
        chapter: Chapter dict with chapter_index, chapter_title, chapter_text
        model: LLM model name (default: env OLLAMA_MODEL)

    Returns:
        {
            "chapter_index": int,
            "chapter_title": str,
            "domains": [str],  # 2-3 domains typically
            "principles": [str],
            "rules": [str],
            "claims": [str],
            "warnings": [str],
            "cross_references": [int]
        }

    Raises:
        LLMError: If LLM call fails
    """
    system = phase2_system()
    user = phase2_user(chapter)
    chapter_idx = chapter.get("chapter_index", "?")

    # Show progress spinner during LLM call
    stop_event = threading.Event()
    spinner_thread = threading.Thread(target=_show_chapter_progress, args=(chapter_idx, stop_event), daemon=True)
    spinner_thread.start()

    try:
        result = call_llm(system, user, model=model)
        stop_event.set()
        spinner_thread.join(timeout=1)
        return result
    except Exception as e:
        stop_event.set()
        spinner_thread.join(timeout=1)
        raise LLMError(f"Phase-2 (doctrine extraction) failed for chapter {chapter_idx}: {e}")

