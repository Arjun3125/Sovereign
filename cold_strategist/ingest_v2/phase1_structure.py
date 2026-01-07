"""
Phase-1: Whole Book → Canonical Chapters (LLM)

This is the structural compilation phase. No doctrine, no interpretation.
Only canonical chapter extraction.
"""
import sys
import threading
import time
from .llm_client import call_llm, LLMError
from .prompts_v2 import phase1_system, phase1_user


def _show_progress_spinner(stop_event):
    """Show a spinner while LLM is processing."""
    spinner = "|/-\\"
    i = 0
    last_print = 0
    while not stop_event.is_set():
        # Only update every 0.5 seconds to reduce output
        if time.time() - last_print >= 0.5:
            sys.stdout.write(f"\r[PHASE-1] Processing... {spinner[i % len(spinner)]} (this may take 1-3 minutes)")
            sys.stdout.flush()
            i += 1
            last_print = time.time()
        time.sleep(0.1)
    sys.stdout.write("\r" + " " * 70 + "\r")  # Clear line
    sys.stdout.flush()


def phase1_structure(book_text: str, model: str = None) -> dict:
    """
    Extract canonical chapters from whole book using LLM.

    Args:
        book_text: Full book text as single string
        model: LLM model name (default: env OLLAMA_MODEL)

    Returns:
        {
            "book_title": str,
            "author": str | null,
            "chapters": [
                {
                    "chapter_index": int,
                    "chapter_title": str,
                    "chapter_text": str
                }
            ]
        }

    Raises:
        LLMError: If LLM call fails
    """
    system = phase1_system()
    user = phase1_user(book_text)

    # Show progress spinner during LLM call
    stop_event = threading.Event()
    spinner_thread = threading.Thread(target=_show_progress_spinner, args=(stop_event,), daemon=True)
    spinner_thread.start()

    try:
        result = call_llm(system, user, model=model)
        stop_event.set()
        spinner_thread.join(timeout=1)
        return result
    except Exception as e:
        stop_event.set()
        spinner_thread.join(timeout=1)
        raise LLMError(f"Phase-1 (book structuring) failed: {e}")

