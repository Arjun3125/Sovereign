import time
from typing import Dict


class ProgressTracker:
    def __init__(self, total: int):
        self.total = int(total)
        self.started: Dict[int, float] = {}
        self.completed: Dict[int, float] = {}
        self.start_time = time.time()

    def mark_start(self, chapter_index: int) -> None:
        self.started[int(chapter_index)] = time.time()
        self.print_status()

    def mark_done(self, chapter_index: int) -> None:
        self.completed[int(chapter_index)] = time.time()
        self.print_status()

    def estimate_eta(self) -> str:
        if not self.completed:
            return "estimating..."

        durations = [self.completed[i] - self.started.get(i, self.start_time) for i in self.completed]
        avg = sum(durations) / len(durations)
        remaining = max(self.total - len(self.completed), 0)
        return f"{int(avg * remaining)} sec"

    def print_status(self) -> None:
        print(
            f"[PROGRESS] {len(self.completed)}/{self.total} completed | ETA: {self.estimate_eta()}"
        )
