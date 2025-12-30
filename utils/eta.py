"""ETA and progress computation from ingest metrics.

Deterministic, crash-safe, resume-safe.
"""

import time


def compute_progress(metrics: dict) -> dict:
    """Compute percentage complete, ETA, and throughput rate.
    
    Args:
        metrics: Dict with keys:
            - completed_chunks: int
            - total_chunks: int
            - start_time: float (unix timestamp)
    
    Returns:
        Dict with:
            - percent_complete: float [0.0, 100.0]
            - eta_seconds: int or None
            - rate_chunks_per_sec: float
    """
    completed = metrics.get("completed_chunks", 0)
    total = metrics.get("total_chunks", 1)
    start = metrics.get("start_time", time.time())

    now = time.time()
    elapsed = max(now - start, 1e-6)  # avoid div by zero and tiny intervals

    # Defensive clamps
    total = max(int(total), 0)
    completed = max(int(completed), 0)
    if total == 0:
        return {"percent_complete": 100.0, "eta_seconds": 0, "rate_chunks_per_sec": 0.0}

    percent = (completed / total * 100)
    percent = max(0.0, min(100.0, percent))

    rate = completed / elapsed  # chunks per second

    if rate > 0:
        remaining = max(total - completed, 0)
        eta_seconds = int(remaining / rate) if remaining > 0 else 0
    else:
        eta_seconds = None

    return {
        "percent_complete": round(percent, 2),
        "eta_seconds": eta_seconds,
        "rate_chunks_per_sec": round(rate, 3),
    }


def format_eta(eta_seconds: int) -> str:
    """Format ETA seconds to human-readable string.
    
    Args:
        eta_seconds: Remaining seconds (None = calculating)
        
    Returns:
        Formatted string like "5m 30s" or "calculating..."
    """
    if eta_seconds is None:
        return "calculating..."
    if eta_seconds == 0:
        return "< 1s"
    
    mins = eta_seconds // 60
    secs = eta_seconds % 60
    
    if mins > 0:
        return f"{mins}m {secs}s"
    return f"{secs}s"
