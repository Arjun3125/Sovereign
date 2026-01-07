"""
Progress tracking for Ingestion v2.

Calculates and displays: (completed_units / total_units) * 100
"""


class Progress:
    """
    Progress tracker for two-phase ingestion.

    Total units = 1 (Phase-1) + N (chapters in Phase-2)
    """

    def __init__(self, total_chapters: int):
        """
        Initialize progress tracker.

        Args:
            total_chapters: Number of chapters (determined after Phase-1)
        """
        self.total_chapters = total_chapters
        self.total_units = 1 + total_chapters  # 1 for Phase-1, 1 per chapter for Phase-2
        self.completed_units = 0

    def phase1_complete(self) -> None:
        """Mark Phase-1 as complete."""
        self.completed_units = 1
        self._print("Phase-1 (Book Structuring): COMPLETE")

    def chapter_ingested(self, chapter_index: int, chapter_title: str) -> None:
        """
        Mark one chapter as complete.

        Args:
            chapter_index: Chapter number
            chapter_title: Chapter name
        """
        self.completed_units += 1
        pct = self._percentage()
        chapters_done = self.completed_units - 1  # Subtract Phase-1 unit
        print(
            f"[INGESTION] Phase-2: {chapters_done}/{self.total_chapters} chapters | "
            f"Overall: {pct}%"
        )

    def _percentage(self) -> int:
        """Calculate percentage completed."""
        return int((self.completed_units / self.total_units) * 100)

    def _print(self, label: str) -> None:
        """Print progress with label and percentage."""
        pct = self._percentage()
        print(f"[INGESTION] {label} | {pct}%")

    def complete(self) -> None:
        """Mark entire ingestion as complete."""
        self.completed_units = self.total_units
        print(f"[INGESTION] Complete | 100%")
