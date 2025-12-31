from collections import Counter


class EmbedStats:
    def __init__(self):
        self.counter = Counter()

    def log(self, reason: str):
        """
        reason:
          - NEW_BOOK_PRINCIPLE
          - NEW_UNIVERSAL_PRINCIPLE
          - SKIPPED_EXISTING
        """
        self.counter[reason] += 1

    def snapshot(self):
        return dict(self.counter)


def dump_stats(embed_stats: EmbedStats):
    print("[EMBED STATS]")
    for k, v in embed_stats.snapshot().items():
        print(f"  {k}: {v}")
