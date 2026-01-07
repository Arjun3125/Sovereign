"""Centralized retry controller for LLM calls and other transient ops."""
import time
from typing import Callable, Any


def retry(func: Callable[..., Any], retries: int = 2, delay: float = 0.5):
    """Retry decorator that wraps a function with retry logic.
    
    Args:
        func: Function to retry
        retries: Number of retry attempts (default: 2)
        delay: Delay between retries in seconds (default: 0.5)
    
    Returns:
        Wrapped function that retries on exception
    """
    def wrapper(*args, **kwargs):
        last_exc = None
        for i in range(retries + 1):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_exc = e
                if i < retries:  # Don't sleep on last attempt
                    time.sleep(delay)
        raise last_exc
    return wrapper
