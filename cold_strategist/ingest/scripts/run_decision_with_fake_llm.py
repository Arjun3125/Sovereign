import json
from cold_strategist.core.decision_engine import decide
from cold_strategist.core.ministers import load_all_ministers

QUESTION = "Should I aggressively expand my project now, or consolidate and wait?"
BOOK_CONTEXT = [
    "Commitment precedes constraint.",
    "Expansion increases exposure.",
    "Timing asymmetry matters.",
    "Early dominance vs premature lock-in."
]


class FakeLLM:
    """Return deterministic, minister-specific structured outputs matching schema."""

    def generate(self, prompt: str):
        # Extract minister id from prompt header
        minister_line = [l for l in prompt.splitlines() if l.strip().startswith("You are the Minister of")]
        if minister_line:
            header = minister_line[0]
            # header like: You are the Minister of STRATEGY.
            parts = header.split()
            minister = parts[-1].strip().strip('.').lower()
        else:
            minister = "unknown"

        # Predefined content per minister
        if minister == "strategy":
            content = {
                "trajectory": "Aggressive expansion now locks the system into a growth trajectory before internal constraints are stabilized.",
                "strategic_risk": "Early expansion reduces adaptability and amplifies future correction costs.",
                "irreversibility": "Public expansion creates path dependency and reputational commitment.",
                "confidence": 0.78,
                "proceed": False,
            }
            return {"content": content}

        if minister == "risk":
            content = {
                "failure_mode": "Overextension before stability increases probability of cascading failure.",
                "ruin_threshold": "Expansion that consumes core operational bandwidth risks total system stall.",
                "confidence": 0.82,
                "catastrophic_risk": True,
                "proceed": False,
            }
            return {"content": content}

        if minister == "optionality":
            content = {
                "exit_routes": "Waiting preserves the option to expand later without reputational damage.",
                "option_loss_risk": "Expanding now collapses multiple future paths into a single commitment.",
                "confidence": 0.75,
                "proceed": False,
            }
            return {"content": content}

        if minister == "timing":
            content = {
                "timing_window": "No external forcing function currently requires immediate expansion.",
                "delay_risk": "Delay cost is low relative to premature commitment cost.",
                "confidence": 0.70,
                "proceed": False,
            }
            return {"content": content}

        if minister == "operations":
            content = {
                "execution_constraints": "Current system complexity suggests consolidation is incomplete.",
                "failure_points": "Scaling before operational discipline increases error propagation.",
                "confidence": 0.72,
                "proceed": False,
            }
            return {"content": content}

        # Others signal silence
        return {"content": {"silence": True}}


if __name__ == "__main__":
    llm = FakeLLM()
    ministers = load_all_ministers()
    result = decide(QUESTION, BOOK_CONTEXT, ministers, llm, mode="FAST_READ_ONLY")
    print(json.dumps(result, indent=2))
