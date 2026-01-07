"""
Progress tracking for Ingestion v2 two-phase compiler.

Tracks progress as percentage: (completed_units / (N + 1)) * 100
where N = number of chapters

Shows detailed progress for each phase and step.
"""
from typing import Optional


class Progress:
    """
    Progress tracker for two-phase ingestion.

    Total units = 1 (Phase-1) + N (Phase-2 chapters)
    """
    def __init__(self, num_chapters: int):
        """
        Initialize progress tracker.

        Args:
            num_chapters: Number of chapters (determined after Phase-1)
        """
        self.num_chapters = num_chapters
        self.total_units = num_chapters + 1  # 1 for Phase-1, N for Phase-2
        self.completed_units = 0
        self.phase1_done = False
        self.phase2_completed = 0

    def phase1_start(self):
        """Mark Phase-1 as starting."""
        print(f"\n[PHASE-1] Book Structuring")
        print(f"[PHASE-1] Processing whole book...")

    def phase1_complete(self):
        """Mark Phase-1 as complete."""
        self.completed_units = 1
        self.phase1_done = True
        percent = int((self.completed_units / self.total_units) * 100)
        print(f"[PHASE-1] [OK] Complete | {percent}% overall")
        print(f"[PHASE-1] Found {self.num_chapters} chapters")

    def phase2_start(self):
        """Mark Phase-2 as starting."""
        print(f"\n[PHASE-2] Doctrine Extraction")
        print(f"[PHASE-2] Processing {self.num_chapters} chapters...")

    def chapter_ingested(self, chapter_index: int, chapter_title: str):
        """Mark one chapter as ingested."""
        self.completed_units += 1
        self.phase2_completed += 1
        
        # Phase-2 progress
        phase2_percent = int((self.phase2_completed / self.num_chapters) * 100)
        
        # Overall progress
        overall_percent = int((self.completed_units / self.total_units) * 100)
        
        print(f"[PHASE-2] Chapter {chapter_index}/{self.num_chapters}: {chapter_title[:50]}... | Phase-2: {phase2_percent}% | Overall: {overall_percent}%")

    def chapter_skipped(self, chapter_index: int, chapter_title: str):
        """Mark one chapter as skipped (already exists)."""
        self.completed_units += 1
        self.phase2_completed += 1
        
        phase2_percent = int((self.phase2_completed / self.num_chapters) * 100)
        overall_percent = int((self.completed_units / self.total_units) * 100)
        
        print(f"[PHASE-2] Chapter {chapter_index}/{self.num_chapters}: {chapter_title[:50]}... [SKIPPED] | Phase-2: {phase2_percent}% | Overall: {overall_percent}%")

    def complete(self):
        """Mark ingestion as 100% complete."""
        self.completed_units = self.total_units
        self.phase2_completed = self.num_chapters
        print(f"\n[PHASE-2] [OK] Complete | 100%")
        print(f"[INGESTION] All phases complete | 100% overall")
