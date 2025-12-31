from collections import defaultdict
from typing import Dict, List, Tuple, Optional
from core.analytics.book_scorer import book_effectiveness


class BookInfluenceTracker:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(BookInfluenceTracker, cls).__new__(cls)
            cls._instance.usage = defaultdict(list)
        return cls._instance

    def record(self, book: str, relevance: float, outcome_score: Optional[float]):
        self.usage[book].append((relevance, outcome_score))

    def record_outcome(self, decision_id: str, outcome_score: float, telemetry_path: str = None):
        """
        Scan telemetry rag_traces for entries matching decision_id and update usage with outcome_score.
        """
        try:
            import json, os
            if telemetry_path is None:
                telemetry_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '..', 'data', 'telemetry', 'rag_traces.jsonl')
            # Best-effort: try common location
            if not os.path.exists(telemetry_path):
                # fallback to workspace-level data/telemetry
                telemetry_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '..', '..', 'data', 'telemetry', 'rag_traces.jsonl')
            if not os.path.exists(telemetry_path):
                return

            with open(telemetry_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        rec = json.loads(line)
                    except Exception:
                        continue
                    if rec.get('decision_id') == decision_id or rec.get('decisionId') == decision_id:
                        book = rec.get('source_book')
                        rel = float(rec.get('relevance_score') or 0.0)
                        self.record(book, rel, outcome_score)
        except Exception:
            pass

    def summarize(self):
        try:
            from core.analytics.book_reports import summarize_books
            scores = {}
            for book, entries in self.usage.items():
                scores[book] = book_effectiveness(entries)
            return summarize_books(scores)
        except Exception:
            return {}
