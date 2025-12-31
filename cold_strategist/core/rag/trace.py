from core.telemetry.store import TelemetryStore
from core.telemetry.models import RAGTrace
from core.telemetry.ids import uid

telemetry = TelemetryStore()


def log_rag_trace(decision_id, book, chapter, principle, interp, score):
    try:
        telemetry.append(
            "rag_traces",
            RAGTrace(
                id=uid(),
                decision_id=decision_id,
                source_book=book,
                chapter=chapter or "",
                principle=principle or "",
                minister_interpretation=interp or "",
                relevance_score=float(score or 0.0),
            ),
        )
        # Also record initial book usage for analytics (outcome to be filled later)
        try:
            from core.analytics.book_tracker import BookInfluenceTracker
            BookInfluenceTracker().record(book, float(score or 0.0), None)
        except Exception:
            pass
    except Exception:
        # Telemetry must not break retrieval
        pass
