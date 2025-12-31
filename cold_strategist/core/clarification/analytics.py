from datetime import datetime
from typing import Any, Dict
import json
from pathlib import Path


class ClarificationEvent:
    def __init__(self, question: str, answer: str, owner: str, reason: str):
        self.question = question
        self.answer = answer
        self.owner = owner
        self.reason = reason
        self.timestamp = datetime.utcnow().isoformat()
        self.impact: Dict[str, Any] = {}


class ClarificationAnalytics:
    def __init__(self):
        self.events = []

    def log(self, event: ClarificationEvent):
        self.events.append(event)

    def attach_impact(self, event: ClarificationEvent, impact: Dict[str, Any]):
        event.impact = impact

    def to_dict(self, event: ClarificationEvent) -> Dict[str, Any]:
        return {
            "question": event.question,
            "answer": event.answer,
            "owner": event.owner,
            "reason": event.reason,
            "timestamp": event.timestamp,
            "impact": event.impact,
        }

    def persist(self, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "a", encoding="utf-8") as f:
            for e in self.events:
                f.write(json.dumps(self.to_dict(e), ensure_ascii=False) + "\n")
        # keep in-memory as well; caller may clear if desired
