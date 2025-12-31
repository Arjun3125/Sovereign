"""Simple retry helper used by ingest_v2 components.

Offers a tiny `retry` wrapper that returns a callable which will
attempt the target function up to `retries` times.
"""
from typing import Callable
import time


def retry(func: Callable, retries: int = 1, delay: float = 0.1) -> Callable:
    """Return a callable that runs `func` with simple retry semantics.

    The returned callable will raise the last exception if all retries fail.
    """

    def _runner():
        last_exc = None
        for attempt in range(max(1, retries)):
            try:
                return func()
            except Exception as exc:
                last_exc = exc
                time.sleep(delay)
        if last_exc:
            raise last_exc

    return _runner
"""Centralized retry controller for LLM calls and other transient ops."""
import time
from typing import Callable, Any


def retry(func: Callable[..., Any], retries: int = 2, delay: float = 0.5):
    def wrapper(*args, **kwargs):
        last_exc = None
        for i in range(retries + 1):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_exc = e
                time.sleep(delay)
        raise last_exc
    return wrapper
