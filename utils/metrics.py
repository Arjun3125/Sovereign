"""Ingest metrics tracking (crash-safe, append-only style).

Tracks progress across ingest runs:
- total_chunks
- completed_chunks
- start_time
- last_update
- percent_complete (computed)
- eta_seconds (computed)
- rate_chunks_per_sec (computed)
"""

import json
import time
from pathlib import Path
from threading import Lock
from typing import Optional
from utils.eta import compute_progress

METRICS_FILE = Path("cold_strategist/state/ingest_metrics.json")


class MetricsCollector:
    """Thread-safe metrics collector that persists a simple JSON file.

    Provides `init`, `update`, `read`, and `reset` operations while
    guarding concurrent access with a Lock.
    """

    def __init__(self, path: Optional[Path] = None):
        self._file = path or METRICS_FILE
        self._lock = Lock()

    def init(self, total_chunks: int) -> None:
        self._file.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "total_chunks": total_chunks,
            "completed_chunks": 0,
            "start_time": time.time(),
            "last_update": time.time(),
            "percent_complete": 0.0,
            "eta_seconds": None,
            "rate_chunks_per_sec": 0.0,
        }
        with self._lock:
            self._file.write_text(json.dumps(data, indent=2))

    def update(self, chunks_just_done: int = 0) -> None:
        if not self._file.exists():
            return
        with self._lock:
            try:
                data = json.loads(self._file.read_text())
            except Exception:
                return

            data["completed_chunks"] = data.get("completed_chunks", 0) + chunks_just_done
            progress = compute_progress(data)
            data.update(progress)
            data["last_update"] = time.time()
            self._file.write_text(json.dumps(data, indent=2))

    def read(self) -> dict:
        if not self._file.exists():
            return {}
        with self._lock:
            try:
                return json.loads(self._file.read_text())
            except Exception:
                return {}

    def reset(self) -> None:
        with self._lock:
            try:
                if self._file.exists():
                    self._file.unlink()
            except Exception:
                pass


# Module-level singleton for convenience & backwards compatibility
_collector = MetricsCollector()


def init_metrics(total_chunks: int) -> None:
    return _collector.init(total_chunks)


def update_metrics(chunks_just_done: int = 0) -> None:
    return _collector.update(chunks_just_done)


def read_metrics() -> dict:
    return _collector.read()
